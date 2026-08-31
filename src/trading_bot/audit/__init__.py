"""Structured audit evidence and the redaction boundary."""

from trading_bot.audit.events import (
    AUDIT_SCHEMA_VERSION,
    AuditEvent,
    Severity,
    serialize_event,
)
from trading_bot.audit.redaction import (
    REDACTED,
    PayloadValue,
    RedactionFailure,
    Redactor,
    ScanBudget,
    is_secret_name,
)

__all__ = [
    "AUDIT_SCHEMA_VERSION",
    "REDACTED",
    "AuditEvent",
    "PayloadValue",
    "RedactionFailure",
    "Redactor",
    "ScanBudget",
    "Severity",
    "is_secret_name",
    "serialize_event",
]
