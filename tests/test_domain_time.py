from datetime import UTC, date, datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo

import pytest

from trading_bot.domain import ExchangeSession, SessionType, ensure_utc

ET = ZoneInfo("America/New_York")


def make_session(
    day: date,
    open_local: time = time(9, 30),
    close_local: time = time(16, 0),
    session_type: SessionType = SessionType.REGULAR,
) -> ExchangeSession:
    return ExchangeSession(
        session_date=day,
        open_utc=datetime.combine(day, open_local, tzinfo=ET),
        close_utc=datetime.combine(day, close_local, tzinfo=ET),
        session_type=session_type,
    )


def test_ensure_utc_rejects_naive_timestamp() -> None:
    with pytest.raises(ValueError, match="observed_at must be timezone-aware"):
        ensure_utc(datetime(2026, 3, 5, 14, 30), "observed_at")


def test_ensure_utc_converts_offset_to_utc() -> None:
    converted = ensure_utc(
        datetime(2026, 3, 5, 9, 30, tzinfo=timezone(timedelta(hours=-5))),
        "observed_at",
    )

    assert converted == datetime(2026, 3, 5, 14, 30, tzinfo=UTC)
    assert converted.tzinfo is UTC


def test_ensure_utc_preserves_an_already_utc_instant() -> None:
    original = datetime(2026, 3, 5, 14, 30, tzinfo=UTC)

    assert ensure_utc(original, "observed_at") == original


def test_ensure_utc_resolves_ambiguous_local_time_by_fold() -> None:
    # 01:30 occurs twice on the US fall-back date; fold selects which instant is meant.
    first = ensure_utc(datetime(2026, 11, 1, 1, 30, tzinfo=ET, fold=0), "observed_at")
    second = ensure_utc(datetime(2026, 11, 1, 1, 30, tzinfo=ET, fold=1), "observed_at")

    assert first == datetime(2026, 11, 1, 5, 30, tzinfo=UTC)
    assert second == datetime(2026, 11, 1, 6, 30, tzinfo=UTC)
    assert second - first == timedelta(hours=1)


def test_session_normalizes_local_bounds_to_utc_before_dst() -> None:
    session = make_session(date(2026, 3, 5))

    assert session.open_utc == datetime(2026, 3, 5, 14, 30, tzinfo=UTC)
    assert session.close_utc == datetime(2026, 3, 5, 21, 0, tzinfo=UTC)


def test_session_shifts_one_hour_after_spring_forward() -> None:
    session = make_session(date(2026, 3, 9))

    assert session.open_utc == datetime(2026, 3, 9, 13, 30, tzinfo=UTC)
    assert session.close_utc == datetime(2026, 3, 9, 20, 0, tzinfo=UTC)


def test_session_shifts_back_one_hour_after_fall_back() -> None:
    before = make_session(date(2026, 10, 30))
    after = make_session(date(2026, 11, 2))

    assert before.open_utc == datetime(2026, 10, 30, 13, 30, tzinfo=UTC)
    assert after.open_utc == datetime(2026, 11, 2, 14, 30, tzinfo=UTC)


def test_session_retains_exchange_local_date_identity() -> None:
    session = make_session(date(2026, 3, 9))

    assert session.session_date == date(2026, 3, 9)
    assert session.open_utc.date() == date(2026, 3, 9)


@pytest.mark.parametrize("field", ["open_utc", "close_utc"])
def test_session_rejects_naive_bounds(field: str) -> None:
    bounds = {
        "open_utc": datetime(2026, 3, 5, 14, 30, tzinfo=UTC),
        "close_utc": datetime(2026, 3, 5, 21, 0, tzinfo=UTC),
    }
    bounds[field] = bounds[field].replace(tzinfo=None)

    with pytest.raises(ValueError, match=f"{field} must be timezone-aware"):
        ExchangeSession(
            session_date=date(2026, 3, 5),
            session_type=SessionType.REGULAR,
            **bounds,
        )


@pytest.mark.parametrize("close_hour", [14, 13])
def test_session_rejects_close_at_or_before_open(close_hour: int) -> None:
    with pytest.raises(ValueError, match="open_utc must be before close_utc"):
        ExchangeSession(
            session_date=date(2026, 3, 5),
            open_utc=datetime(2026, 3, 5, 14, 30, tzinfo=UTC),
            close_utc=datetime(2026, 3, 5, close_hour, 30, tzinfo=UTC),
            session_type=SessionType.REGULAR,
        )


@pytest.mark.parametrize(
    ("instant", "expected"),
    [
        (datetime(2026, 3, 5, 14, 29, 59, tzinfo=UTC), False),
        (datetime(2026, 3, 5, 14, 30, tzinfo=UTC), True),
        (datetime(2026, 3, 5, 17, 0, tzinfo=UTC), True),
        (datetime(2026, 3, 5, 20, 59, 59, tzinfo=UTC), True),
        (datetime(2026, 3, 5, 21, 0, tzinfo=UTC), False),
        (datetime(2026, 3, 5, 21, 0, 1, tzinfo=UTC), False),
    ],
)
def test_session_contains_is_half_open(instant: datetime, expected: bool) -> None:
    assert make_session(date(2026, 3, 5)).contains(instant) is expected


def test_session_contains_rejects_naive_instant() -> None:
    with pytest.raises(ValueError, match="instant must be timezone-aware"):
        make_session(date(2026, 3, 5)).contains(datetime(2026, 3, 5, 17, 0))


def test_early_close_session_ends_before_the_regular_close() -> None:
    half_day = make_session(
        date(2026, 11, 27),
        close_local=time(13, 0),
        session_type=SessionType.EARLY_CLOSE,
    )

    assert half_day.session_type is SessionType.EARLY_CLOSE
    assert half_day.close_utc == datetime(2026, 11, 27, 18, 0, tzinfo=UTC)
    assert not half_day.contains(datetime(2026, 11, 27, 18, 30, tzinfo=UTC))
