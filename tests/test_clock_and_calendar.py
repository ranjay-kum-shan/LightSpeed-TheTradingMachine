from datetime import UTC, date, datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo

import pytest

from trading_bot.adapters import ManualClock, SystemClock
from trading_bot.data import StaticExchangeCalendar
from trading_bot.domain import Clock, ExchangeCalendar, ExchangeSession, SessionType

ET = ZoneInfo("America/New_York")

REGULAR_OPEN = time(9, 30)
REGULAR_CLOSE = time(16, 0)


def make_session(
    day: date,
    close_local: time = REGULAR_CLOSE,
    session_type: SessionType = SessionType.REGULAR,
) -> ExchangeSession:
    return ExchangeSession(
        session_date=day,
        open_utc=datetime.combine(day, REGULAR_OPEN, tzinfo=ET),
        close_utc=datetime.combine(day, close_local, tzinfo=ET),
        session_type=session_type,
    )


# Thanksgiving week 2026: Thursday is a holiday and Friday is an early close.
WEDNESDAY = make_session(date(2026, 11, 25))
FRIDAY_HALF_DAY = make_session(date(2026, 11, 27), time(13, 0), SessionType.EARLY_CLOSE)
MONDAY = make_session(date(2026, 11, 30))


def make_calendar() -> StaticExchangeCalendar:
    return StaticExchangeCalendar(
        "XNYS",
        "2026.1",
        (MONDAY, WEDNESDAY, FRIDAY_HALF_DAY),
    )


def test_system_clock_returns_aware_utc() -> None:
    clock: Clock = SystemClock()

    first = clock.now_utc()
    second = clock.now_utc()

    assert first.tzinfo is UTC
    assert second >= first


def test_manual_clock_satisfies_the_clock_port() -> None:
    clock: Clock = ManualClock(datetime(2026, 11, 25, 14, 30, tzinfo=UTC))

    assert clock.now_utc() == datetime(2026, 11, 25, 14, 30, tzinfo=UTC)


def test_manual_clock_rejects_naive_start() -> None:
    with pytest.raises(ValueError, match="start must be timezone-aware"):
        ManualClock(datetime(2026, 11, 25, 14, 30))


def test_manual_clock_normalizes_offset_start_to_utc() -> None:
    clock = ManualClock(datetime(2026, 11, 25, 9, 30, tzinfo=timezone(timedelta(hours=-5))))

    assert clock.now_utc() == datetime(2026, 11, 25, 14, 30, tzinfo=UTC)


def test_manual_clock_does_not_move_on_its_own() -> None:
    clock = ManualClock(datetime(2026, 11, 25, 14, 30, tzinfo=UTC))

    assert clock.now_utc() == clock.now_utc()


@pytest.mark.parametrize("delta", [timedelta(0), timedelta(minutes=30), timedelta(days=2)])
def test_manual_clock_advances_forward(delta: timedelta) -> None:
    clock = ManualClock(datetime(2026, 11, 25, 14, 30, tzinfo=UTC))

    returned = clock.advance(delta)

    assert returned == datetime(2026, 11, 25, 14, 30, tzinfo=UTC) + delta
    assert clock.now_utc() == returned


def test_manual_clock_rejects_negative_advance() -> None:
    clock = ManualClock(datetime(2026, 11, 25, 14, 30, tzinfo=UTC))

    with pytest.raises(ValueError, match="delta must not be negative"):
        clock.advance(timedelta(seconds=-1))


def test_manual_clock_sets_to_a_later_instant() -> None:
    clock = ManualClock(datetime(2026, 11, 25, 14, 30, tzinfo=UTC))

    returned = clock.set_to(datetime(2026, 11, 25, 21, 0, tzinfo=UTC))

    assert returned == datetime(2026, 11, 25, 21, 0, tzinfo=UTC)
    assert clock.now_utc() == returned


def test_manual_clock_rejects_backwards_movement() -> None:
    clock = ManualClock(datetime(2026, 11, 25, 14, 30, tzinfo=UTC))

    with pytest.raises(ValueError, match="clock must not move backwards"):
        clock.set_to(datetime(2026, 11, 25, 14, 29, tzinfo=UTC))


def test_manual_clock_rejects_naive_set_to() -> None:
    clock = ManualClock(datetime(2026, 11, 25, 14, 30, tzinfo=UTC))

    with pytest.raises(ValueError, match="instant must be timezone-aware"):
        clock.set_to(datetime(2026, 11, 25, 21, 0))


def test_calendar_satisfies_the_exchange_calendar_port() -> None:
    calendar: ExchangeCalendar = make_calendar()

    assert calendar.calendar_name == "XNYS"
    assert calendar.calendar_version == "2026.1"


@pytest.mark.parametrize(
    ("instant", "expected"),
    [
        (datetime(2026, 11, 25, 14, 29, 59, tzinfo=UTC), False),
        (datetime(2026, 11, 25, 14, 30, tzinfo=UTC), True),
        (datetime(2026, 11, 25, 18, 0, tzinfo=UTC), True),
        (datetime(2026, 11, 25, 20, 59, 59, tzinfo=UTC), True),
        (datetime(2026, 11, 25, 21, 0, tzinfo=UTC), False),
    ],
)
def test_calendar_session_boundaries_are_half_open(instant: datetime, expected: bool) -> None:
    assert make_calendar().is_open(instant) is expected


def test_calendar_reports_a_holiday_as_closed() -> None:
    calendar = make_calendar()
    thanksgiving_midday = datetime(2026, 11, 26, 17, 0, tzinfo=UTC)

    assert calendar.session_at(thanksgiving_midday) is None
    assert not calendar.is_open(thanksgiving_midday)


def test_calendar_closes_early_on_a_half_day() -> None:
    calendar = make_calendar()

    assert calendar.is_open(datetime(2026, 11, 27, 17, 0, tzinfo=UTC))
    assert not calendar.is_open(datetime(2026, 11, 27, 18, 0, tzinfo=UTC))
    assert not calendar.is_open(datetime(2026, 11, 27, 20, 0, tzinfo=UTC))


def test_calendar_reports_an_unscheduled_gap_as_closed() -> None:
    calendar = make_calendar()

    assert not calendar.is_open(datetime(2026, 11, 28, 17, 0, tzinfo=UTC))
    assert not calendar.is_open(datetime(2026, 11, 24, 17, 0, tzinfo=UTC))
    assert not calendar.is_open(datetime(2026, 12, 1, 17, 0, tzinfo=UTC))


def test_calendar_returns_the_owning_session_identity() -> None:
    session = make_calendar().session_at(datetime(2026, 11, 27, 17, 0, tzinfo=UTC))

    assert session is not None
    assert session.session_date == date(2026, 11, 27)
    assert session.session_type is SessionType.EARLY_CLOSE


def test_calendar_orders_sessions_supplied_out_of_order() -> None:
    calendar = make_calendar()

    assert calendar.is_open(datetime(2026, 11, 25, 17, 0, tzinfo=UTC))
    assert calendar.is_open(datetime(2026, 11, 30, 17, 0, tzinfo=UTC))


def test_calendar_rejects_naive_instant() -> None:
    with pytest.raises(ValueError, match="instant must be timezone-aware"):
        make_calendar().session_at(datetime(2026, 11, 25, 17, 0))


@pytest.mark.parametrize("name", ["", " ", " XNYS", "XNYS "])
def test_calendar_rejects_noncanonical_name(name: str) -> None:
    with pytest.raises(ValueError, match="name must be a non-empty trimmed value"):
        StaticExchangeCalendar(name, "2026.1", (WEDNESDAY,))


@pytest.mark.parametrize("version", ["", " ", " 2026.1", "2026.1 "])
def test_calendar_rejects_noncanonical_version(version: str) -> None:
    with pytest.raises(ValueError, match="version must be a non-empty trimmed value"):
        StaticExchangeCalendar("XNYS", version, (WEDNESDAY,))


def test_calendar_rejects_empty_sessions() -> None:
    with pytest.raises(ValueError, match="sessions must not be empty"):
        StaticExchangeCalendar("XNYS", "2026.1", ())


def test_calendar_rejects_duplicate_session_dates() -> None:
    duplicate = make_session(date(2026, 11, 25), time(15, 0))

    with pytest.raises(ValueError, match="at most one row per session date"):
        StaticExchangeCalendar("XNYS", "2026.1", (WEDNESDAY, duplicate))


def test_calendar_rejects_overlapping_sessions() -> None:
    overlapping = ExchangeSession(
        session_date=date(2026, 11, 26),
        open_utc=datetime(2026, 11, 25, 20, 0, tzinfo=UTC),
        close_utc=datetime(2026, 11, 26, 21, 0, tzinfo=UTC),
        session_type=SessionType.REGULAR,
    )

    with pytest.raises(ValueError, match="sessions must not overlap"):
        StaticExchangeCalendar("XNYS", "2026.1", (WEDNESDAY, overlapping))
