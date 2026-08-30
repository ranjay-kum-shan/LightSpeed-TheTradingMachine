"""Deterministic pre-trade risk evaluation."""

from collections import defaultdict
from datetime import timedelta
from decimal import Decimal
from zoneinfo import ZoneInfo

from trading_bot.domain import OrderIntent, Side
from trading_bot.risk.models import (
    RiskDecision,
    RiskLimits,
    RiskReason,
    RiskSnapshot,
    TradingState,
)


class RiskEngine:
    """Apply every hard limit to a coherent snapshot before submission."""

    def __init__(self, limits: RiskLimits) -> None:
        self._limits = limits
        self._exchange_timezone = ZoneInfo(limits.exchange_timezone)

    def evaluate(
        self,
        intent: OrderIntent | None,
        snapshot: RiskSnapshot | None,
    ) -> RiskDecision:
        if intent is None or snapshot is None:
            return RiskDecision(False, (RiskReason.INPUT_MISSING,))

        reasons: list[RiskReason] = []

        if snapshot.trading_state is not TradingState.RUNNING:
            reasons.append(RiskReason.MODE_NOT_RUNNING)
        if snapshot.internal_halt:
            reasons.append(RiskReason.INTERNAL_HALT)
        if snapshot.operator_kill:
            reasons.append(RiskReason.OPERATOR_KILL)
        if not snapshot.watchdog_healthy:
            reasons.append(RiskReason.WATCHDOG_UNHEALTHY)
        if not snapshot.is_reconciled:
            reasons.append(RiskReason.NOT_RECONCILED)
        if snapshot.has_unknown_orders:
            reasons.append(RiskReason.UNKNOWN_ORDER)
        if abs(snapshot.clock_offset) > self._limits.max_clock_offset:
            reasons.append(RiskReason.CLOCK_OFFSET)

        local_time = snapshot.as_of_utc.astimezone(self._exchange_timezone).time()
        if not self._limits.allowed_order_start <= local_time <= self._limits.allowed_order_end:
            reasons.append(RiskReason.SESSION_CLOSED)
        if intent.created_at_utc > snapshot.as_of_utc:
            reasons.append(RiskReason.INTENT_IN_FUTURE)

        data_age = snapshot.as_of_utc - snapshot.market_data_as_of_utc
        if data_age < timedelta(0):
            reasons.append(RiskReason.DATA_FUTURE)
        elif data_age > self._limits.max_data_age:
            reasons.append(RiskReason.DATA_STALE)

        if intent.symbol not in self._limits.allowed_symbols:
            reasons.append(RiskReason.SYMBOL_NOT_ALLOWED)
        if intent.order_type not in self._limits.allowed_order_types:
            reasons.append(RiskReason.ORDER_TYPE_NOT_ALLOWED)
        if intent.time_in_force not in self._limits.allowed_time_in_force:
            reasons.append(RiskReason.TIME_IN_FORCE_NOT_ALLOWED)

        order_notional = intent.quantity * intent.conservative_price
        if intent.quantity > self._limits.max_order_quantity:
            reasons.append(RiskReason.ORDER_QUANTITY)
        if order_notional > self._limits.max_order_notional:
            reasons.append(RiskReason.ORDER_NOTIONAL)
        if snapshot.orders_last_minute + 1 > self._limits.max_orders_per_minute:
            reasons.append(RiskReason.ORDER_RATE)

        quantities: defaultdict[str, Decimal] = defaultdict(Decimal)
        prices: dict[str, Decimal] = {}
        for position in snapshot.positions:
            quantities[position.symbol] += position.quantity
            prices[position.symbol] = position.mark_price
        for pending_order in snapshot.pending_orders:
            direction = Decimal(1) if pending_order.side is Side.BUY else Decimal(-1)
            quantities[pending_order.symbol] += direction * pending_order.remaining_quantity
            prices[pending_order.symbol] = max(
                prices.get(pending_order.symbol, Decimal(0)),
                pending_order.conservative_price,
            )

        intent_direction = Decimal(1) if intent.side is Side.BUY else Decimal(-1)
        quantities[intent.symbol] += intent_direction * intent.quantity
        prices[intent.symbol] = max(
            prices.get(intent.symbol, Decimal(0)),
            intent.conservative_price,
        )

        projected_notionals = {
            symbol: abs(quantity) * prices[symbol]
            for symbol, quantity in quantities.items()
            if quantity != 0
        }
        projected_position_quantity = quantities[intent.symbol]
        projected_gross_exposure = sum(projected_notionals.values(), start=Decimal(0))
        projected_net_exposure = sum(
            (quantity * prices[symbol] for symbol, quantity in quantities.items()),
            start=Decimal(0),
        )
        projected_leverage = projected_gross_exposure / snapshot.current_equity

        if (
            any(
                quantity != 0 and symbol not in self._limits.allowed_symbols
                for symbol, quantity in quantities.items()
            )
            and RiskReason.SYMBOL_NOT_ALLOWED not in reasons
        ):
            reasons.append(RiskReason.SYMBOL_NOT_ALLOWED)
        if not self._limits.allow_short and any(quantity < 0 for quantity in quantities.values()):
            reasons.append(RiskReason.SHORT_POSITION)
        if any(
            notional > self._limits.max_position_notional_per_symbol
            for notional in projected_notionals.values()
        ):
            reasons.append(RiskReason.POSITION_NOTIONAL)
        if any(
            notional / snapshot.current_equity > self._limits.max_position_pct_equity
            for notional in projected_notionals.values()
        ):
            reasons.append(RiskReason.POSITION_CONCENTRATION)
        if projected_gross_exposure > self._limits.max_gross_exposure:
            reasons.append(RiskReason.GROSS_EXPOSURE)
        if abs(projected_net_exposure) > self._limits.max_net_exposure:
            reasons.append(RiskReason.NET_EXPOSURE)
        if projected_leverage > self._limits.max_leverage:
            reasons.append(RiskReason.LEVERAGE)
        if len(projected_notionals) > self._limits.max_open_positions:
            reasons.append(RiskReason.OPEN_POSITIONS)

        liquidity_by_symbol = {item.symbol: item for item in snapshot.liquidity}
        for symbol, quantity in quantities.items():
            if quantity == 0:
                continue
            liquidity = liquidity_by_symbol.get(symbol)
            if liquidity is None:
                if RiskReason.LIQUIDITY_MISSING not in reasons:
                    reasons.append(RiskReason.LIQUIDITY_MISSING)
                continue
            if (
                abs(quantity) / liquidity.median_daily_volume
                > self._limits.max_position_pct_adv
                and RiskReason.ADV not in reasons
            ):
                reasons.append(RiskReason.ADV)

        daily_loss = max(
            Decimal(0),
            snapshot.session_start_equity - snapshot.current_equity,
        )
        if daily_loss >= self._limits.max_daily_loss:
            reasons.append(RiskReason.DAILY_LOSS)

        drawdown = max(
            Decimal(0),
            (snapshot.high_water_equity - snapshot.current_equity)
            / snapshot.high_water_equity,
        )
        if drawdown >= self._limits.max_drawdown_from_peak:
            reasons.append(RiskReason.DRAWDOWN)

        return RiskDecision(
            approved=not reasons,
            reason_codes=tuple(reasons),
            projected_position_quantity=projected_position_quantity,
            projected_gross_exposure=projected_gross_exposure,
            projected_net_exposure=projected_net_exposure,
            projected_leverage=projected_leverage,
        )
