from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from trading_bot.config import OperatingMode
from trading_bot.operations import (
    HeartbeatHealth,
    HeartbeatRecord,
    KillHealth,
    assess_heartbeat,
    assess_operator_kill,
    write_heartbeat,
)
from trading_bot.risk import TradingState

NOW = datetime(2026, 8, 31, 14, 0, tzinfo=UTC)


def make_heartbeat(**changes: object) -> HeartbeatRecord:
    values: dict[str, object] = {
        "schema_version": "1",
        "process_instance": "paper-process-1",
        "session_id": "paper-2026-08-31",
        "mode": OperatingMode.PAPER,
        "state": TradingState.READY,
        "written_at_utc": NOW,
        "last_reconciliation_id": "recon-1",
    }
    values.update(changes)
    return HeartbeatRecord.model_validate(values)


def test_missing_operator_kill_is_clear(tmp_path: Path) -> None:
    assessment = assess_operator_kill(tmp_path / "KILL")

    assert assessment.health is KillHealth.CLEAR
    assert assessment.safe_to_trade
    assert assessment.reason_code == "CONTROL_KILL_CLEAR"


def test_present_operator_kill_is_active_and_is_not_deleted(tmp_path: Path) -> None:
    kill_path = tmp_path / "KILL"
    kill_path.write_text("operator requested halt\n", encoding="utf-8")

    assessment = assess_operator_kill(kill_path)

    assert assessment.health is KillHealth.ACTIVE
    assert not assessment.safe_to_trade
    assert assessment.reason_code == "CONTROL_KILL_PRESENT"
    assert kill_path.read_text(encoding="utf-8") == "operator requested halt\n"


def test_unreadable_operator_kill_state_fails_closed(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    kill_path = tmp_path / "KILL"

    def fail_stat(self: Path) -> None:
        raise PermissionError("denied")

    monkeypatch.setattr(Path, "stat", fail_stat)

    assessment = assess_operator_kill(kill_path)

    assert assessment.health is KillHealth.UNKNOWN
    assert not assessment.safe_to_trade
    assert assessment.reason_code == "CONTROL_KILL_UNKNOWN"


def test_heartbeat_round_trip_is_atomic_and_normalizes_utc(tmp_path: Path) -> None:
    heartbeat_path = tmp_path / "run" / "heartbeat"
    offset_time = datetime(2026, 8, 31, 15, 0, tzinfo=UTC)
    record = make_heartbeat(written_at_utc=offset_time)

    write_heartbeat(heartbeat_path, record)
    assessment = assess_heartbeat(
        heartbeat_path,
        offset_time,
        max_age=timedelta(seconds=30),
        max_future_offset=timedelta(seconds=1),
    )

    assert assessment.health is HeartbeatHealth.HEALTHY
    assert assessment.healthy
    assert assessment.record == record
    assert assessment.age == timedelta(0)
    assert list(heartbeat_path.parent.glob(".*.tmp")) == []
    assert heartbeat_path.read_bytes().endswith(b"\n")


@pytest.mark.parametrize(
    ("content", "expected_health", "expected_reason"),
    [
        (None, HeartbeatHealth.MISSING, "CONTROL_HEARTBEAT_MISSING"),
        ("not-json", HeartbeatHealth.INVALID, "CONTROL_HEARTBEAT_INVALID"),
        (
            '{"schema_version":"2"}',
            HeartbeatHealth.INVALID,
            "CONTROL_HEARTBEAT_INVALID",
        ),
    ],
)
def test_missing_or_invalid_heartbeat_fails_closed(
    tmp_path: Path,
    content: str | None,
    expected_health: HeartbeatHealth,
    expected_reason: str,
) -> None:
    heartbeat_path = tmp_path / "heartbeat"
    if content is not None:
        heartbeat_path.write_text(content, encoding="utf-8")

    assessment = assess_heartbeat(
        heartbeat_path,
        NOW,
        max_age=timedelta(seconds=30),
        max_future_offset=timedelta(seconds=1),
    )

    assert assessment.health is expected_health
    assert not assessment.healthy
    assert assessment.reason_code == expected_reason


@pytest.mark.parametrize(
    ("written_at", "expected_health", "expected_reason"),
    [
        (
            NOW - timedelta(seconds=30),
            HeartbeatHealth.HEALTHY,
            "CONTROL_HEARTBEAT_HEALTHY",
        ),
        (
            NOW - timedelta(seconds=31),
            HeartbeatHealth.STALE,
            "CONTROL_HEARTBEAT_STALE",
        ),
        (
            NOW + timedelta(seconds=1),
            HeartbeatHealth.HEALTHY,
            "CONTROL_HEARTBEAT_HEALTHY",
        ),
        (
            NOW + timedelta(seconds=2),
            HeartbeatHealth.FUTURE,
            "CONTROL_HEARTBEAT_FUTURE",
        ),
    ],
)
def test_heartbeat_age_boundaries(
    tmp_path: Path,
    written_at: datetime,
    expected_health: HeartbeatHealth,
    expected_reason: str,
) -> None:
    heartbeat_path = tmp_path / "heartbeat"
    write_heartbeat(heartbeat_path, make_heartbeat(written_at_utc=written_at))

    assessment = assess_heartbeat(
        heartbeat_path,
        NOW,
        max_age=timedelta(seconds=30),
        max_future_offset=timedelta(seconds=1),
    )

    assert assessment.health is expected_health
    assert assessment.reason_code == expected_reason


@pytest.mark.parametrize(
    ("now_utc", "max_age", "max_future_offset"),
    [
        (datetime(2026, 8, 31, 14, 0), timedelta(seconds=30), timedelta(seconds=1)),
        (NOW, timedelta(0), timedelta(seconds=1)),
        (NOW, timedelta(seconds=30), timedelta(seconds=-1)),
    ],
)
def test_invalid_heartbeat_assessment_parameters_are_rejected(
    tmp_path: Path,
    now_utc: datetime,
    max_age: timedelta,
    max_future_offset: timedelta,
) -> None:
    with pytest.raises(ValueError):
        assess_heartbeat(tmp_path / "heartbeat", now_utc, max_age, max_future_offset)