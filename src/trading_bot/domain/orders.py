"""Canonical order intent values."""

from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal
from enum import StrEnum


class Side(StrEnum):
    BUY = "BUY"
    SELL = "SELL"


class OrderType(StrEnum):
    MARKET = "MARKET"
    LIMIT = "LIMIT"


class TimeInForce(StrEnum):
    DAY = "DAY"
    GTC = "GTC"


@dataclass(frozen=True, slots=True)
class OrderIntent:
    symbol: str
    side: Side
    quantity: Decimal
    order_type: OrderType
    time_in_force: TimeInForce
    conservative_price: Decimal
    created_at_utc: datetime

    def __post_init__(self) -> None:
        if not self.symbol or self.symbol != self.symbol.strip().upper():
            raise ValueError("symbol must be a non-empty canonical uppercase value")
        if self.quantity <= 0:
            raise ValueError("quantity must be positive")
        if self.conservative_price <= 0:
            raise ValueError("conservative_price must be positive")
        if self.created_at_utc.tzinfo is None or self.created_at_utc.utcoffset() is None:
            raise ValueError("created_at_utc must be timezone-aware")
        object.__setattr__(self, "created_at_utc", self.created_at_utc.astimezone(UTC))
