from dataclasses import replace
from datetime import UTC, datetime, time, timedelta
from decimal import Decimal
from typing import Any

import pytest
from hypothesis import given
from hypothesis import strategies as st

from trading_bot.domain import OrderIntent, OrderType, Side, TimeInForce
from trading_bot.risk import (
    Liquidity,
    PendingOrder,
    Position,
    RiskEngine,
    RiskLimits,
    RiskReason,
    RiskSnapshot,
    TradingState,
)

NOW = datetime(2026, 8, 31, 14, 0, tzinfo=UTC)


def make_limits() -> RiskLimits:
    return RiskLimits(
        allowed_symbols=frozenset({"SPY"}),
        allowed_order_types=frozenset({OrderType.MARKET}),
        allowed_time_in_force=frozenset({TimeInForce.DAY}),
        exchange_timezone="America/New_York",
        allowed_order_start=time(9, 30),
        allowed_order_end=time(16, 0),
        max_order_notional=Decimal("25000"),
        max_order_quantity=Decimal("100"),
        max_position_notional_per_symbol=Decimal("50000"),
        max_position_pct_equity=Decimal("0.50"),
        max_gross_exposure=Decimal("100000"),
        max_net_exposure=Decimal("100000"),
        max_leverage=Decimal("1"),
        max_open_positions=5,
        max_orders_per_minute=10,
        max_daily_loss=Decimal("1000"),
        max_drawdown_from_peak=Decimal("0.25"),
        max_position_pct_adv=Decimal("0.01"),
        max_data_age=timedelta(days=3),
        max_clock_offset=timedelta(seconds=1),
        allow_short=False,
        allow_margin=False,
    )


def make_snapshot() -> RiskSnapshot:
    return RiskSnapshot(
        as_of_utc=NOW,
        market_data_as_of_utc=NOW - timedelta(days=1),
        positions=(),
        pending_orders=(),
        liquidity=(Liquidity("SPY", Decimal("1000000")),),
        current_equity=Decimal("100000"),
        session_start_equity=Decimal("100000"),
        high_water_equity=Decimal("100000"),
        orders_last_minute=0,
        trading_state=TradingState.RUNNING,
        is_reconciled=True,
        has_unknown_orders=False,
        internal_halt=False,
        operator_kill=False,
        watchdog_healthy=True,
        clock_offset=timedelta(0),
    )


@pytest.fixture
def limits() -> RiskLimits:
    return make_limits()


@pytest.fixture
def snapshot() -> RiskSnapshot:
    return make_snapshot()


def make_intent(**changes: object) -> OrderIntent:
    values: dict[str, Any] = {
        "symbol": "SPY",
        "side": Side.BUY,
        "quantity": Decimal("10"),
        "order_type": OrderType.MARKET,
        "time_in_force": TimeInForce.DAY,
        "conservative_price": Decimal("500"),
        "created_at_utc": NOW,
    }
    values.update(changes)
    return OrderIntent(**values)


def assert_rejected(decision_reasons: tuple[RiskReason, ...], reason: RiskReason) -> None:
    assert reason in decision_reasons


def test_safe_long_only_order_is_approved(limits: RiskLimits, snapshot: RiskSnapshot) -> None:
    decision = RiskEngine(limits).evaluate(make_intent(), snapshot)

    assert decision.approved
    assert decision.reason_codes == ()
    assert decision.projected_position_quantity == Decimal("10")
    assert decision.projected_gross_exposure == Decimal("5000")
    assert decision.projected_net_exposure == Decimal("5000")
    assert decision.projected_leverage == Decimal("0.05")


@pytest.mark.parametrize("missing", ["intent", "snapshot"])
def test_missing_risk_input_fails_closed(
    limits: RiskLimits,
    snapshot: RiskSnapshot,
    missing: str,
) -> None:
    intent = None if missing == "intent" else make_intent()
    risk_snapshot = None if missing == "snapshot" else snapshot

    decision = RiskEngine(limits).evaluate(intent, risk_snapshot)

    assert not decision.approved
    assert decision.reason_codes == (RiskReason.INPUT_MISSING,)


@pytest.mark.parametrize(
    ("changes", "reason"),
    [
        ({"trading_state": TradingState.HALTED}, RiskReason.MODE_NOT_RUNNING),
        ({"internal_halt": True}, RiskReason.INTERNAL_HALT),
        ({"operator_kill": True}, RiskReason.OPERATOR_KILL),
        ({"watchdog_healthy": False}, RiskReason.WATCHDOG_UNHEALTHY),
        ({"is_reconciled": False}, RiskReason.NOT_RECONCILED),
        ({"has_unknown_orders": True}, RiskReason.UNKNOWN_ORDER),
        ({"clock_offset": timedelta(seconds=2)}, RiskReason.CLOCK_OFFSET),
    ],
)
def test_global_control_failure_rejects_order(
    limits: RiskLimits,
    snapshot: RiskSnapshot,
    changes: dict[str, Any],
    reason: RiskReason,
) -> None:
    decision = RiskEngine(limits).evaluate(make_intent(), replace(snapshot, **changes))

    assert not decision.approved
    assert_rejected(decision.reason_codes, reason)


@pytest.mark.parametrize(
    ("changes", "reason"),
    [
        ({"as_of_utc": datetime(2026, 8, 31, 13, 0, tzinfo=UTC)}, RiskReason.SESSION_CLOSED),
        (
            {"market_data_as_of_utc": NOW - timedelta(days=4)},
            RiskReason.DATA_STALE,
        ),
        (
            {"market_data_as_of_utc": NOW + timedelta(seconds=1)},
            RiskReason.DATA_FUTURE,
        ),
    ],
)
def test_time_or_data_failure_rejects_order(
    limits: RiskLimits,
    snapshot: RiskSnapshot,
    changes: dict[str, Any],
    reason: RiskReason,
) -> None:
    decision = RiskEngine(limits).evaluate(make_intent(), replace(snapshot, **changes))

    assert not decision.approved
    assert_rejected(decision.reason_codes, reason)


@pytest.mark.parametrize(
    ("intent", "reason"),
    [
        (make_intent(symbol="QQQ"), RiskReason.SYMBOL_NOT_ALLOWED),
        (make_intent(order_type=OrderType.LIMIT), RiskReason.ORDER_TYPE_NOT_ALLOWED),
        (make_intent(time_in_force=TimeInForce.GTC), RiskReason.TIME_IN_FORCE_NOT_ALLOWED),
        (make_intent(quantity=Decimal("101")), RiskReason.ORDER_QUANTITY),
        (
            make_intent(quantity=Decimal("51"), conservative_price=Decimal("500")),
            RiskReason.ORDER_NOTIONAL,
        ),
        (
            make_intent(created_at_utc=NOW + timedelta(seconds=1)),
            RiskReason.INTENT_IN_FUTURE,
        ),
    ],
)
def test_order_rule_failure_rejects_order(
    limits: RiskLimits,
    snapshot: RiskSnapshot,
    intent: OrderIntent,
    reason: RiskReason,
) -> None:
    decision = RiskEngine(limits).evaluate(intent, snapshot)

    assert not decision.approved
    assert_rejected(decision.reason_codes, reason)


@pytest.mark.parametrize(
    ("limit_changes", "reason"),
    [
        ({"max_position_notional_per_symbol": Decimal("4999")}, RiskReason.POSITION_NOTIONAL),
        ({"max_position_pct_equity": Decimal("0.049")}, RiskReason.POSITION_CONCENTRATION),
        ({"max_gross_exposure": Decimal("4999")}, RiskReason.GROSS_EXPOSURE),
        ({"max_net_exposure": Decimal("4999")}, RiskReason.NET_EXPOSURE),
        ({"max_leverage": Decimal("0.049")}, RiskReason.LEVERAGE),
        ({"max_position_pct_adv": Decimal("0.000009")}, RiskReason.ADV),
    ],
)
def test_each_projected_exposure_limit_rejects_order(
    limits: RiskLimits,
    snapshot: RiskSnapshot,
    limit_changes: dict[str, Any],
    reason: RiskReason,
) -> None:
    constrained_limits = replace(limits, **limit_changes)

    decision = RiskEngine(constrained_limits).evaluate(make_intent(), snapshot)

    assert not decision.approved
    assert_rejected(decision.reason_codes, reason)


def test_open_position_limit_includes_new_symbol(
    limits: RiskLimits,
    snapshot: RiskSnapshot,
) -> None:
    constrained_limits = replace(
        limits,
        allowed_symbols=frozenset({"QQQ", "SPY"}),
        max_open_positions=1,
    )
    existing_snapshot = replace(
        snapshot,
        positions=(Position("QQQ", Decimal("1"), Decimal("400")),),
        liquidity=(
            Liquidity("QQQ", Decimal("1000000")),
            Liquidity("SPY", Decimal("1000000")),
        ),
    )

    decision = RiskEngine(constrained_limits).evaluate(make_intent(), existing_snapshot)

    assert not decision.approved
    assert_rejected(decision.reason_codes, RiskReason.OPEN_POSITIONS)


def test_unexpected_existing_position_fails_symbol_allowlist(
    limits: RiskLimits,
    snapshot: RiskSnapshot,
) -> None:
    unexpected_snapshot = replace(
        snapshot,
        positions=(Position("QQQ", Decimal("1"), Decimal("400")),),
        liquidity=(
            Liquidity("QQQ", Decimal("1000000")),
            Liquidity("SPY", Decimal("1000000")),
        ),
    )

    decision = RiskEngine(limits).evaluate(make_intent(), unexpected_snapshot)

    assert not decision.approved
    assert_rejected(decision.reason_codes, RiskReason.SYMBOL_NOT_ALLOWED)


@pytest.mark.parametrize(
    "snapshot_changes",
    [
        {"clock_offset": timedelta(seconds=1)},
        {"market_data_as_of_utc": NOW - timedelta(days=3)},
        {"as_of_utc": datetime(2026, 8, 31, 13, 30, tzinfo=UTC)},
        {"as_of_utc": datetime(2026, 8, 31, 20, 0, tzinfo=UTC)},
    ],
)
def test_inclusive_time_and_freshness_boundaries_are_accepted(
    limits: RiskLimits,
    snapshot: RiskSnapshot,
    snapshot_changes: dict[str, Any],
) -> None:
    boundary_snapshot = replace(snapshot, **snapshot_changes)
    intent = make_intent(created_at_utc=boundary_snapshot.as_of_utc)

    decision = RiskEngine(limits).evaluate(intent, boundary_snapshot)

    assert decision.approved


def test_order_quantity_and_notional_limits_are_inclusive(
    limits: RiskLimits,
    snapshot: RiskSnapshot,
) -> None:
    decision = RiskEngine(limits).evaluate(
        make_intent(quantity=Decimal("50"), conservative_price=Decimal("500")),
        snapshot,
    )

    assert decision.approved


def test_sell_cannot_project_a_short_position(
    limits: RiskLimits,
    snapshot: RiskSnapshot,
) -> None:
    intent = make_intent(side=Side.SELL, quantity=Decimal("11"))
    held_snapshot = replace(
        snapshot,
        positions=(Position("SPY", Decimal("10"), Decimal("500")),),
    )

    decision = RiskEngine(limits).evaluate(intent, held_snapshot)

    assert not decision.approved
    assert_rejected(decision.reason_codes, RiskReason.SHORT_POSITION)


def test_pending_orders_are_included_in_projected_exposure(
    limits: RiskLimits,
    snapshot: RiskSnapshot,
) -> None:
    pending_snapshot = replace(
        snapshot,
        pending_orders=(PendingOrder("SPY", Side.BUY, Decimal("90"), Decimal("500")),),
    )

    decision = RiskEngine(limits).evaluate(make_intent(quantity=Decimal("11")), pending_snapshot)

    assert not decision.approved
    assert decision.projected_position_quantity == Decimal("101")
    assert_rejected(decision.reason_codes, RiskReason.POSITION_NOTIONAL)
    assert_rejected(decision.reason_codes, RiskReason.POSITION_CONCENTRATION)


@pytest.mark.parametrize(
    ("changes", "reason"),
    [
        ({"orders_last_minute": 10}, RiskReason.ORDER_RATE),
        (
            {"current_equity": Decimal("99000")},
            RiskReason.DAILY_LOSS,
        ),
        (
            {
                "current_equity": Decimal("75000"),
                "session_start_equity": Decimal("75000"),
            },
            RiskReason.DRAWDOWN,
        ),
        ({"liquidity": ()}, RiskReason.LIQUIDITY_MISSING),
    ],
)
def test_rate_loss_drawdown_or_liquidity_failure_rejects_order(
    limits: RiskLimits,
    snapshot: RiskSnapshot,
    changes: dict[str, Any],
    reason: RiskReason,
) -> None:
    decision = RiskEngine(limits).evaluate(make_intent(), replace(snapshot, **changes))

    assert not decision.approved
    assert_rejected(decision.reason_codes, reason)


def test_risk_limits_have_no_capital_dependent_defaults() -> None:
    with pytest.raises(TypeError):
        RiskLimits()  # type: ignore[call-arg]


@given(
    held_quantity=st.integers(min_value=0, max_value=120),
    order_quantity=st.integers(min_value=1, max_value=120),
    side=st.sampled_from([Side.BUY, Side.SELL]),
)
def test_approved_order_never_projects_short_or_over_leverage(
    held_quantity: int,
    order_quantity: int,
    side: Side,
) -> None:
    limits = make_limits()
    positions = (
        (Position("SPY", Decimal(held_quantity), Decimal("500")),)
        if held_quantity
        else ()
    )
    snapshot = replace(make_snapshot(), positions=positions)
    intent = make_intent(side=side, quantity=Decimal(order_quantity))

    decision = RiskEngine(limits).evaluate(intent, snapshot)

    if decision.approved:
        assert decision.projected_position_quantity is not None
        assert decision.projected_gross_exposure is not None
        assert decision.projected_leverage is not None
        assert decision.projected_position_quantity >= 0
        assert decision.projected_gross_exposure <= limits.max_gross_exposure
        assert decision.projected_leverage <= limits.max_leverage


@pytest.mark.parametrize(
    ("changes", "match"),
    [
        ({"allowed_symbols": frozenset()}, "allowed_symbols"),
        ({"allowed_symbols": frozenset({"spy"})}, "allowed_symbols"),
        ({"allowed_order_types": frozenset()}, "allowed_order_types"),
        ({"allowed_time_in_force": frozenset()}, "allowed_time_in_force"),
        ({"exchange_timezone": "Not/AZone"}, "exchange_timezone"),
        ({"allowed_order_start": time(16, 0)}, "must not cross midnight"),
        ({"allowed_order_end": time(9, 30)}, "must not cross midnight"),
        ({"max_order_notional": Decimal("0")}, "max_order_notional"),
        ({"max_order_quantity": Decimal("-1")}, "max_order_quantity"),
        ({"max_gross_exposure": Decimal("NaN")}, "max_gross_exposure"),
        ({"max_position_pct_equity": Decimal("1.5")}, "no greater than one"),
        ({"max_drawdown_from_peak": Decimal("0")}, "max_drawdown_from_peak"),
        ({"max_position_pct_adv": Decimal("2")}, "no greater than one"),
        ({"max_open_positions": 0}, "max_open_positions"),
        ({"max_orders_per_minute": 0}, "max_orders_per_minute"),
        ({"max_data_age": timedelta(0)}, "max_data_age"),
        ({"max_clock_offset": timedelta(seconds=-1)}, "max_clock_offset"),
        ({"max_leverage": Decimal("2")}, "margin is disabled"),
    ],
)
def test_risk_limits_reject_invalid_configuration(
    changes: dict[str, Any],
    match: str,
) -> None:
    with pytest.raises(ValueError, match=match):
        replace(make_limits(), **changes)


def test_risk_limits_allow_leverage_above_one_only_with_margin() -> None:
    limits = replace(make_limits(), allow_margin=True, max_leverage=Decimal("2"))

    assert limits.max_leverage == Decimal("2")


@pytest.mark.parametrize(
    ("changes", "match"),
    [
        ({"as_of_utc": datetime(2026, 8, 31, 14, 0)}, "as_of_utc"),
        ({"market_data_as_of_utc": datetime(2026, 8, 30, 14, 0)}, "market_data_as_of_utc"),
        ({"current_equity": Decimal("0")}, "current_equity"),
        ({"session_start_equity": Decimal("-1")}, "session_start_equity"),
        ({"high_water_equity": Decimal("NaN")}, "high_water_equity"),
        ({"orders_last_minute": -1}, "orders_last_minute"),
        (
            {
                "positions": (
                    Position("SPY", Decimal("1"), Decimal("500")),
                    Position("SPY", Decimal("2"), Decimal("500")),
                )
            },
            "at most one row per symbol",
        ),
        (
            {
                "liquidity": (
                    Liquidity("SPY", Decimal("1000")),
                    Liquidity("SPY", Decimal("2000")),
                )
            },
            "at most one row per symbol",
        ),
    ],
)
def test_risk_snapshot_rejects_invalid_state(changes: dict[str, Any], match: str) -> None:
    with pytest.raises(ValueError, match=match):
        replace(make_snapshot(), **changes)


def test_missing_liquidity_is_reported_once_for_multiple_symbols() -> None:
    snapshot = replace(
        make_snapshot(),
        positions=(Position("QQQ", Decimal("1"), Decimal("400")),),
        liquidity=(),
    )

    decision = RiskEngine(make_limits()).evaluate(make_intent(), snapshot)

    assert not decision.approved
    assert decision.reason_codes.count(RiskReason.LIQUIDITY_MISSING) == 1