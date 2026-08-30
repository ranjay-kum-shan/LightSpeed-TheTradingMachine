"""Fail-closed file controls for operator kill and process heartbeat state."""

import os
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from enum import StrEnum
from pathlib import Path
from typing import Literal, Self
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, ValidationError, field_validator

from trading_bot.config import OperatingMode
from trading_bot.risk import TradingState


class KillHealth(StrEnum):
    CLEAR = "CLEAR"
    ACTIVE = "ACTIVE"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True, slots=True)
class KillAssessment:
    health: KillHealth
    reason_code: str

    @property
    def safe_to_trade(self) -> bool:
        return self.health is KillHealth.CLEAR


class HeartbeatHealth(StrEnum):
    HEALTHY = "HEALTHY"
    MISSING = "MISSING"
    INVALID = "INVALID"
    FUTURE = "FUTURE"
    STALE = "STALE"


class HeartbeatRecord(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    schema_version: Literal["1"]
    process_instance: str
    session_id: str
    mode: OperatingMode
    state: TradingState
    written_at_utc: datetime
    last_reconciliation_id: str | None

    @field_validator("process_instance", "session_id")
    @classmethod
    def validate_identity(cls, value: str) -> str:
        if not value or value != value.strip():
            raise ValueError("heartbeat identities must be non-empty and trimmed")
        return value

    @field_validator("last_reconciliation_id")
    @classmethod
    def validate_reconciliation_id(cls, value: str | None) -> str | None:
        if value is not None and (not value or value != value.strip()):
            raise ValueError("last_reconciliation_id must be non-empty and trimmed")
        return value

    @field_validator("written_at_utc")
    @classmethod
    def normalize_written_at(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("written_at_utc must be timezone-aware")
        return value.astimezone(UTC)

    def as_json(self) -> str:
        return self.model_dump_json(exclude_none=False)

    @classmethod
    def from_json(cls, value: str) -> Self:
        return cls.model_validate_json(value)


@dataclass(frozen=True, slots=True)
class HeartbeatAssessment:
    health: HeartbeatHealth
    reason_code: str
    record: HeartbeatRecord | None = None
    age: timedelta | None = None

    @property
    def healthy(self) -> bool:
        return self.health is HeartbeatHealth.HEALTHY


def assess_operator_kill(path: Path) -> KillAssessment:
    try:
        path.stat()
    except FileNotFoundError:
        return KillAssessment(KillHealth.CLEAR, "CONTROL_KILL_CLEAR")
    except OSError:
        return KillAssessment(KillHealth.UNKNOWN, "CONTROL_KILL_UNKNOWN")
    return KillAssessment(KillHealth.ACTIVE, "CONTROL_KILL_PRESENT")


def _write_text_atomically(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = path.with_name(f".{path.name}.{uuid4().hex}.tmp")
    try:
        with temporary_path.open("x", encoding="utf-8", newline="\n") as output:
            output.write(content)
            output.write("\n")
            output.flush()
            os.fsync(output.fileno())
        os.replace(temporary_path, path)
    finally:
        temporary_path.unlink(missing_ok=True)


def write_heartbeat(path: Path, record: HeartbeatRecord) -> None:
    _write_text_atomically(path, record.as_json())


def assess_heartbeat(
    path: Path,
    now_utc: datetime,
    max_age: timedelta,
    max_future_offset: timedelta,
) -> HeartbeatAssessment:
    if now_utc.tzinfo is None or now_utc.utcoffset() is None:
        raise ValueError("now_utc must be timezone-aware")
    if max_age <= timedelta(0):
        raise ValueError("max_age must be positive")
    if max_future_offset < timedelta(0):
        raise ValueError("max_future_offset must not be negative")
    now_utc = now_utc.astimezone(UTC)

    try:
        content = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return HeartbeatAssessment(HeartbeatHealth.MISSING, "CONTROL_HEARTBEAT_MISSING")
    except OSError:
        return HeartbeatAssessment(HeartbeatHealth.INVALID, "CONTROL_HEARTBEAT_UNREADABLE")

    try:
        record = HeartbeatRecord.from_json(content)
    except ValidationError:
        return HeartbeatAssessment(HeartbeatHealth.INVALID, "CONTROL_HEARTBEAT_INVALID")

    age = now_utc - record.written_at_utc
    if age < -max_future_offset:
        return HeartbeatAssessment(
            HeartbeatHealth.FUTURE,
            "CONTROL_HEARTBEAT_FUTURE",
            record,
            age,
        )
    if age > max_age:
        return HeartbeatAssessment(
            HeartbeatHealth.STALE,
            "CONTROL_HEARTBEAT_STALE",
            record,
            age,
        )
    return HeartbeatAssessment(
        HeartbeatHealth.HEALTHY,
        "CONTROL_HEARTBEAT_HEALTHY",
        record,
        age,
    )
