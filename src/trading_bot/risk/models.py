"""Immutable values consumed and produced by the risk engine."""

from dataclasses import dataclass
from datetime import UTC, datetime, time, timedelta
from decimal import Decimal
from enum import StrEnum
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from trading_bot.domain import OrderType, ReasonCode, Side, TimeInForce


class TradingState(StrEnum):
    RECOVERY = "RECOVERY"
    READY = "READY"
    RUNNING = "RUNNING"
    LOSS_HALTED = "LOSS_HALTED"
    HARD_HALTED = "HARD_HALTED"
    HALTED = "HALTED"


class RiskReason(StrEnum):
    """Backward-compatible risk-only view backed by canonical reason values."""

    APPROVED = ReasonCode.RISK_APPROVED.value
    INPUT_MISSING = ReasonCode.RISK_INPUT_MISSING.value
    MODE_NOT_RUNNING = ReasonCode.MODE_NOT_RUNNING.value
    INTERNAL_HALT = ReasonCode.INTERNAL_HALT.value
    OPERATOR_KILL = ReasonCode.OPERATOR_KILL.value
    WATCHDOG_UNHEALTHY = ReasonCode.WATCHDOG_UNHEALTHY.value
    NOT_RECONCILED = ReasonCode.NOT_RECONCILED.value
    UNKNOWN_ORDER = ReasonCode.UNKNOWN_ORDER.value
    CLOCK_OFFSET = ReasonCode.CLOCK_OFFSET.value
    SESSION_CLOSED = ReasonCode.SESSION_CLOSED.value
    INTENT_IN_FUTURE = ReasonCode.INTENT_IN_FUTURE.value
    DATA_FUTURE = ReasonCode.DATA_FUTURE.value
    DATA_STALE = ReasonCode.DATA_STALE.value
    LIQUIDITY_MISSING = ReasonCode.LIQUIDITY_MISSING.value
    SYMBOL_NOT_ALLOWED = ReasonCode.SYMBOL_NOT_ALLOWED.value
    ORDER_TYPE_NOT_ALLOWED = ReasonCode.ORDER_TYPE_NOT_ALLOWED.value
    TIME_IN_FORCE_NOT_ALLOWED = ReasonCode.TIME_IN_FORCE_NOT_ALLOWED.value
    ORDER_QUANTITY = ReasonCode.ORDER_QUANTITY_LIMIT.value
    ORDER_NOTIONAL = ReasonCode.ORDER_NOTIONAL_LIMIT.value
    SHORT_POSITION = ReasonCode.SHORT_NOT_ALLOWED.value
    POSITION_NOTIONAL = ReasonCode.POSITION_NOTIONAL_LIMIT.value
    POSITION_CONCENTRATION = ReasonCode.POSITION_CONCENTRATION_LIMIT.value
    GROSS_EXPOSURE = ReasonCode.GROSS_EXPOSURE_LIMIT.value
    NET_EXPOSURE = ReasonCode.NET_EXPOSURE_LIMIT.value
    LEVERAGE = ReasonCode.LEVERAGE_LIMIT.value
    OPEN_POSITIONS = ReasonCode.OPEN_POSITIONS_LIMIT.value
    ADV = ReasonCode.ADV_LIMIT.value
    ORDER_RATE = ReasonCode.ORDER_RATE_LIMIT.value
    DAILY_LOSS = ReasonCode.DAILY_LOSS_LIMIT.value
    DRAWDOWN = ReasonCode.DRAWDOWN_LIMIT.value


def _as_utc(value: datetime, field_name: str) -> datetime:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{field_name} must be timezone-aware")
    return value.astimezone(UTC)


def _require_positive(value: Decimal, field_name: str) -> None:
    if not value.is_finite() or value <= 0:
        raise ValueError(f"{field_name} must be finite and positive")


def _require_fraction(value: Decimal, field_name: str) -> None:
    _require_positive(value, field_name)
    if value > 1:
        raise ValueError(f"{field_name} must be no greater than one")


@dataclass(frozen=True, slots=True)
class Position:
    symbol: str
    quantity: Decimal
    mark_price: Decimal

    def __post_init__(self) -> None:
        if not self.symbol or self.symbol != self.symbol.strip().upper():
            raise ValueError("symbol must be a non-empty canonical uppercase value")
        if not self.quantity.is_finite():
            raise ValueError("quantity must be finite")
        _require_positive(self.mark_price, "mark_price")


@dataclass(frozen=True, slots=True)
class PendingOrder:
    symbol: str
    side: Side
    remaining_quantity: Decimal
    conservative_price: Decimal

    def __post_init__(self) -> None:
        if not self.symbol or self.symbol != self.symbol.strip().upper():
            raise ValueError("symbol must be a non-empty canonical uppercase value")
        _require_positive(self.remaining_quantity, "remaining_quantity")
        _require_positive(self.conservative_price, "conservative_price")


@dataclass(frozen=True, slots=True)
class Liquidity:
    symbol: str
    median_daily_volume: Decimal

    def __post_init__(self) -> None:
        if not self.symbol or self.symbol != self.symbol.strip().upper():
            raise ValueError("symbol must be a non-empty canonical uppercase value")
        _require_positive(self.median_daily_volume, "median_daily_volume")


@dataclass(frozen=True, slots=True)
class RiskLimits:
    allowed_symbols: frozenset[str]
    allowed_order_types: frozenset[OrderType]
    allowed_time_in_force: frozenset[TimeInForce]
    exchange_timezone: str
    allowed_order_start: time
    allowed_order_end: time
    max_order_notional: Decimal
    max_order_quantity: Decimal
    max_position_notional_per_symbol: Decimal
    max_position_pct_equity: Decimal
    max_gross_exposure: Decimal
    max_net_exposure: Decimal
    max_leverage: Decimal
    max_open_positions: int
    max_orders_per_minute: int
    max_daily_loss: Decimal
    max_drawdown_from_peak: Decimal
    max_position_pct_adv: Decimal
    max_data_age: timedelta
    max_clock_offset: timedelta
    allow_short: bool
    allow_margin: bool

    def __post_init__(self) -> None:
        if not self.allowed_symbols or any(
            not symbol or symbol != symbol.strip().upper() for symbol in self.allowed_symbols
        ):
            raise ValueError("allowed_symbols must contain canonical uppercase values")
        if not self.allowed_order_types:
            raise ValueError("allowed_order_types must not be empty")
        if not self.allowed_time_in_force:
            raise ValueError("allowed_time_in_force must not be empty")
        try:
            ZoneInfo(self.exchange_timezone)
        except ZoneInfoNotFoundError as error:
            raise ValueError("exchange_timezone must be a valid IANA timezone") from error
        if self.allowed_order_start >= self.allowed_order_end:
            raise ValueError("allowed order window must not cross midnight")

        for field_name in (
            "max_order_notional",
            "max_order_quantity",
            "max_position_notional_per_symbol",
            "max_position_pct_equity",
            "max_gross_exposure",
            "max_net_exposure",
            "max_leverage",
            "max_daily_loss",
            "max_drawdown_from_peak",
            "max_position_pct_adv",
        ):
            value = getattr(self, field_name)
            _require_positive(value, field_name)

        _require_fraction(self.max_position_pct_equity, "max_position_pct_equity")
        _require_fraction(self.max_drawdown_from_peak, "max_drawdown_from_peak")
        _require_fraction(self.max_position_pct_adv, "max_position_pct_adv")
        if self.max_open_positions <= 0:
            raise ValueError("max_open_positions must be positive")
        if self.max_orders_per_minute <= 0:
            raise ValueError("max_orders_per_minute must be positive")
        if self.max_data_age <= timedelta(0):
            raise ValueError("max_data_age must be positive")
        if self.max_clock_offset < timedelta(0):
            raise ValueError("max_clock_offset must not be negative")
        if not self.allow_margin and self.max_leverage > 1:
            raise ValueError("max_leverage cannot exceed one when margin is disabled")


@dataclass(frozen=True, slots=True)
class RiskSnapshot:
    as_of_utc: datetime
    market_data_as_of_utc: datetime
    positions: tuple[Position, ...]
    pending_orders: tuple[PendingOrder, ...]
    liquidity: tuple[Liquidity, ...]
    current_equity: Decimal
    session_start_equity: Decimal
    high_water_equity: Decimal
    orders_last_minute: int
    trading_state: TradingState
    is_reconciled: bool
    has_unknown_orders: bool
    internal_halt: bool
    operator_kill: bool
    watchdog_healthy: bool
    clock_offset: timedelta

    def __post_init__(self) -> None:
        object.__setattr__(self, "as_of_utc", _as_utc(self.as_of_utc, "as_of_utc"))
        object.__setattr__(
            self,
            "market_data_as_of_utc",
            _as_utc(self.market_data_as_of_utc, "market_data_as_of_utc"),
        )
        _require_positive(self.current_equity, "current_equity")
        _require_positive(self.session_start_equity, "session_start_equity")
        _require_positive(self.high_water_equity, "high_water_equity")
        if self.orders_last_minute < 0:
            raise ValueError("orders_last_minute must not be negative")

        position_symbols = [position.symbol for position in self.positions]
        if len(position_symbols) != len(set(position_symbols)):
            raise ValueError("positions must contain at most one row per symbol")
        liquidity_symbols = [item.symbol for item in self.liquidity]
        if len(liquidity_symbols) != len(set(liquidity_symbols)):
            raise ValueError("liquidity must contain at most one row per symbol")


@dataclass(frozen=True, slots=True)
class RiskDecision:
    approved: bool
    reason_codes: tuple[RiskReason, ...]
    projected_position_quantity: Decimal | None = None
    projected_gross_exposure: Decimal | None = None
    projected_net_exposure: Decimal | None = None
    projected_leverage: Decimal | None = None

    def __post_init__(self) -> None:
        if self.approved == bool(self.reason_codes):
            raise ValueError("approved decisions must have no rejection reasons")
