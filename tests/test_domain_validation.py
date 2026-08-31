from datetime import UTC, datetime, timedelta, timezone
from decimal import Decimal
from typing import Any

import pytest
from pydantic import ValidationError

from trading_bot.config import OperatingMode
from trading_bot.domain import OrderIntent, OrderType, Side, TimeInForce
from trading_bot.operations import HeartbeatRecord
from trading_bot.risk import (
    Liquidity,
    PendingOrder,
    Position,
    RiskDecision,
    RiskReason,
    TradingState,
)

NOW = datetime(2026, 8, 31, 14, 0, tzinfo=UTC)


def make_intent(**overrides: Any) -> OrderIntent:
    values: dict[str, Any] = {
        "symbol": "SPY",
        "side": Side.BUY,
        "quantity": Decimal("10"),
        "order_type": OrderType.MARKET,
        "time_in_force": TimeInForce.DAY,
        "conservative_price": Decimal("500"),
        "created_at_utc": NOW,
    }
    values.update(overrides)
    return OrderIntent(**values)


def make_heartbeat(**overrides: Any) -> HeartbeatRecord:
    values: dict[str, Any] = {
        "schema_version": "1",
        "process_instance": "process-1",
        "session_id": "session-1",
        "mode": OperatingMode.PAPER,
        "state": TradingState.READY,
        "written_at_utc": NOW,
        "last_reconciliation_id": None,
    }
    values.update(overrides)
    return HeartbeatRecord.model_validate(values)


@pytest.mark.parametrize("symbol", ["", " ", "spy", " SPY", "SPY ", "Spy"])
def test_order_intent_rejects_noncanonical_symbol(symbol: str) -> None:
    with pytest.raises(ValueError, match="symbol"):
        make_intent(symbol=symbol)


@pytest.mark.parametrize("quantity", [Decimal("0"), Decimal("-1")])
def test_order_intent_rejects_nonpositive_quantity(quantity: Decimal) -> None:
    with pytest.raises(ValueError, match="quantity"):
        make_intent(quantity=quantity)


@pytest.mark.parametrize("price", [Decimal("0"), Decimal("-0.01")])
def test_order_intent_rejects_nonpositive_conservative_price(price: Decimal) -> None:
    with pytest.raises(ValueError, match="conservative_price"):
        make_intent(conservative_price=price)


def test_order_intent_rejects_naive_timestamp() -> None:
    with pytest.raises(ValueError, match="timezone-aware"):
        make_intent(created_at_utc=datetime(2026, 8, 31, 14, 0))


def test_order_intent_normalizes_offset_timestamp_to_utc() -> None:
    intent = make_intent(
        created_at_utc=datetime(2026, 8, 31, 10, 0, tzinfo=timezone(timedelta(hours=-4)))
    )

    assert intent.created_at_utc == NOW
    assert intent.created_at_utc.tzinfo is UTC


@pytest.mark.parametrize("symbol", ["", "spy", " SPY "])
def test_position_rejects_noncanonical_symbol(symbol: str) -> None:
    with pytest.raises(ValueError, match="symbol"):
        Position(symbol, Decimal("1"), Decimal("500"))


@pytest.mark.parametrize("quantity", [Decimal("NaN"), Decimal("Infinity")])
def test_position_rejects_nonfinite_quantity(quantity: Decimal) -> None:
    with pytest.raises(ValueError, match="finite"):
        Position("SPY", quantity, Decimal("500"))


@pytest.mark.parametrize("mark_price", [Decimal("0"), Decimal("-1"), Decimal("NaN")])
def test_position_rejects_nonpositive_mark_price(mark_price: Decimal) -> None:
    with pytest.raises(ValueError, match="mark_price"):
        Position("SPY", Decimal("1"), mark_price)


def test_position_allows_negative_quantity_for_short_representation() -> None:
    position = Position("SPY", Decimal("-5"), Decimal("500"))

    assert position.quantity == Decimal("-5")


@pytest.mark.parametrize("symbol", ["", "spy", "SPY "])
def test_pending_order_rejects_noncanonical_symbol(symbol: str) -> None:
    with pytest.raises(ValueError, match="symbol"):
        PendingOrder(symbol, Side.BUY, Decimal("1"), Decimal("500"))


@pytest.mark.parametrize("quantity", [Decimal("0"), Decimal("-1"), Decimal("Infinity")])
def test_pending_order_rejects_nonpositive_remaining_quantity(quantity: Decimal) -> None:
    with pytest.raises(ValueError, match="remaining_quantity"):
        PendingOrder("SPY", Side.BUY, quantity, Decimal("500"))


@pytest.mark.parametrize("price", [Decimal("0"), Decimal("-1")])
def test_pending_order_rejects_nonpositive_conservative_price(price: Decimal) -> None:
    with pytest.raises(ValueError, match="conservative_price"):
        PendingOrder("SPY", Side.BUY, Decimal("1"), price)


@pytest.mark.parametrize("symbol", ["", "spy"])
def test_liquidity_rejects_noncanonical_symbol(symbol: str) -> None:
    with pytest.raises(ValueError, match="symbol"):
        Liquidity(symbol, Decimal("1000"))


@pytest.mark.parametrize("volume", [Decimal("0"), Decimal("-1"), Decimal("NaN")])
def test_liquidity_rejects_nonpositive_median_daily_volume(volume: Decimal) -> None:
    with pytest.raises(ValueError, match="median_daily_volume"):
        Liquidity("SPY", volume)


def test_risk_decision_rejects_approval_with_reasons() -> None:
    with pytest.raises(ValueError, match="approved"):
        RiskDecision(approved=True, reason_codes=(RiskReason.DATA_STALE,))


def test_risk_decision_rejects_rejection_without_reasons() -> None:
    with pytest.raises(ValueError, match="approved"):
        RiskDecision(approved=False, reason_codes=())


@pytest.mark.parametrize("field", ["process_instance", "session_id"])
@pytest.mark.parametrize("value", ["", " ", " process-1", "process-1 "])
def test_heartbeat_rejects_untrimmed_or_empty_identity(field: str, value: str) -> None:
    with pytest.raises(ValidationError):
        make_heartbeat(**{field: value})


@pytest.mark.parametrize("value", ["", " recon-1", "recon-1 "])
def test_heartbeat_rejects_untrimmed_or_empty_reconciliation_id(value: str) -> None:
    with pytest.raises(ValidationError):
        make_heartbeat(last_reconciliation_id=value)


def test_heartbeat_rejects_naive_written_at() -> None:
    with pytest.raises(ValidationError):
        make_heartbeat(written_at_utc=datetime(2026, 8, 31, 14, 0))


def test_heartbeat_normalizes_offset_written_at_to_utc() -> None:
    record = make_heartbeat(
        written_at_utc=datetime(2026, 8, 31, 16, 0, tzinfo=timezone(timedelta(hours=2)))
    )

    assert record.written_at_utc == NOW
