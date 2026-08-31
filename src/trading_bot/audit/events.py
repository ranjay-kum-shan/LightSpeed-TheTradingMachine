"""Structured audit event schema and canonical JSON Lines serialization."""

import json
import re
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from typing import Final

from trading_bot.audit.redaction import PayloadValue, Redactor, is_secret_name
from trading_bot.config import OperatingMode
from trading_bot.domain.reasons import ReasonCode
from trading_bot.domain.time import ensure_utc

AUDIT_SCHEMA_VERSION: Final = "1"

# Stable dotted name, at least two segments, for example "decision.order.rejected".
_EVENT_TYPE = re.compile(r"^[a-z][a-z0-9]*(\.[a-z0-9]+)+$")
_DECISION_PREFIX: Final = "decision."


class Severity(StrEnum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


def _require_text(value: str, field_name: str) -> str:
    if not value or value != value.strip():
        raise ValueError(f"{field_name} must be a non-empty trimmed value")
    return value


@dataclass(frozen=True, slots=True)
class AuditEvent:
    """One append-only evidence record under the structured event contract."""

    event_id: str
    event_type: str
    occurred_at_utc: datetime
    recorded_at_utc: datetime
    severity: Severity
    mode: OperatingMode
    component: str
    payload: Mapping[str, PayloadValue]
    schema_version: str = AUDIT_SCHEMA_VERSION
    session_id: str | None = None
    run_id: str | None = None
    correlation_id: str | None = None
    reason_code: ReasonCode | None = None
    git_revision: str | None = None
    config_hash: str | None = None
    data_hash: str | None = None
    strategy_id: str | None = None
    account_fingerprint: str | None = None

    def __post_init__(self) -> None:
        _require_text(self.schema_version, "schema_version")
        _require_text(self.event_id, "event_id")
        _require_text(self.component, "component")
        if not _EVENT_TYPE.fullmatch(self.event_type):
            raise ValueError("event_type must be a stable dotted lowercase name")
        for field_name, field_value in (
            ("session_id", self.session_id),
            ("run_id", self.run_id),
            ("correlation_id", self.correlation_id),
            ("git_revision", self.git_revision),
            ("config_hash", self.config_hash),
            ("data_hash", self.data_hash),
            ("strategy_id", self.strategy_id),
            ("account_fingerprint", self.account_fingerprint),
        ):
            if field_value is not None:
                _require_text(field_value, field_name)
        object.__setattr__(
            self, "occurred_at_utc", ensure_utc(self.occurred_at_utc, "occurred_at_utc")
        )
        object.__setattr__(
            self, "recorded_at_utc", ensure_utc(self.recorded_at_utc, "recorded_at_utc")
        )
        if self.recorded_at_utc < self.occurred_at_utc:
            raise ValueError("recorded_at_utc must not precede occurred_at_utc")
        for key in self.payload:
            if is_secret_name(key):
                raise ValueError(f"payload must not carry secret key {key!r}")
        self._require_scope_identity()
        self._require_decision_completeness()

    @property
    def is_decision(self) -> bool:
        return self.event_type.startswith(_DECISION_PREFIX)

    def _require_scope_identity(self) -> None:
        if self.mode is OperatingMode.BACKTEST and self.run_id is None:
            raise ValueError("run_id is required for backtest events")
        if (
            self.mode in (OperatingMode.PAPER, OperatingMode.RECOVERY)
            and self.session_id is None
        ):
            raise ValueError("session_id is required for session-scoped events")

    def _require_decision_completeness(self) -> None:
        if not self.is_decision:
            return
        # AUD-001: a decision that cannot be traced back to its inputs is not evidence.
        required = (
            ("strategy_id", self.strategy_id),
            ("git_revision", self.git_revision),
            ("config_hash", self.config_hash),
            ("data_hash", self.data_hash),
        )
        for field_name, field_value in required:
            if field_value is None:
                raise ValueError(f"{field_name} is required for a decision event")
        if self.reason_code is None:
            raise ValueError("reason_code is required for a decision event")
        if not self.payload:
            raise ValueError("payload is required for a decision event")


def serialize_event(event: AuditEvent, redactor: Redactor) -> str:
    """Render one redacted JSON Lines record, failing closed on a surviving secret."""
    record: dict[str, PayloadValue] = {
        "schema_version": event.schema_version,
        "event_id": redactor.redact_text(event.event_id),
        "event_type": event.event_type,
        "occurred_at_utc": event.occurred_at_utc.isoformat(),
        "recorded_at_utc": event.recorded_at_utc.isoformat(),
        "severity": event.severity.value,
        "mode": event.mode.value,
        "session_id": event.session_id,
        "run_id": event.run_id,
        "correlation_id": event.correlation_id,
        "component": event.component,
        "reason_code": None if event.reason_code is None else event.reason_code.value,
        "git_revision": event.git_revision,
        "config_hash": event.config_hash,
        "data_hash": event.data_hash,
        "strategy_id": event.strategy_id,
        "account_fingerprint": (
            None
            if event.account_fingerprint is None
            else redactor.redact_text(event.account_fingerprint)
        ),
        "payload": redactor.redact(event.payload),
    }
    rendered = json.dumps(record, separators=(",", ":"), ensure_ascii=False)
    redactor.assert_clean(rendered)
    return rendered
