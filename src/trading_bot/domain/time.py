"""Canonical UTC time values, exchange-session identity, and time ports."""

from dataclasses import dataclass
from datetime import UTC, date, datetime
from enum import StrEnum
from typing import Protocol


def ensure_utc(value: datetime, field_name: str) -> datetime:
    """Reject a naive timestamp and normalize an aware one to UTC."""
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{field_name} must be timezone-aware")
    return value.astimezone(UTC)


class SessionType(StrEnum):
    REGULAR = "REGULAR"
    EARLY_CLOSE = "EARLY_CLOSE"


@dataclass(frozen=True, slots=True)
class ExchangeSession:
    """One trading session: UTC bounds plus the exchange-local date that names it."""

    session_date: date
    open_utc: datetime
    close_utc: datetime
    session_type: SessionType

    def __post_init__(self) -> None:
        object.__setattr__(self, "open_utc", ensure_utc(self.open_utc, "open_utc"))
        object.__setattr__(self, "close_utc", ensure_utc(self.close_utc, "close_utc"))
        if self.open_utc >= self.close_utc:
            raise ValueError("open_utc must be before close_utc")

    def contains(self, instant: datetime) -> bool:
        # Half-open: the closing instant is already outside the session.
        moment = ensure_utc(instant, "instant")
        return self.open_utc <= moment < self.close_utc


class Clock(Protocol):
    """Supplies the current instant as an aware UTC timestamp."""

    def now_utc(self) -> datetime: ...


class ExchangeCalendar(Protocol):
    """Answers session identity and trading eligibility for an instant."""

    @property
    def calendar_name(self) -> str: ...

    @property
    def calendar_version(self) -> str: ...

    def session_at(self, instant: datetime) -> ExchangeSession | None: ...

    def is_open(self, instant: datetime) -> bool: ...
