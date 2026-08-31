import json
from datetime import UTC, datetime, timedelta
from pathlib import Path

from trading_bot.config import OperatingMode, load_runtime_config
from trading_bot.domain import (
    DOMAIN_CONTRACT_VERSION,
    OrderPurpose,
    OrderStatus,
    ReasonCode,
    ReasonFamily,
)
from trading_bot.operations import (
    HeartbeatRecord,
    assess_heartbeat,
    assess_operator_kill,
    write_heartbeat,
)
from trading_bot.risk import RiskReason, TradingState

EXPECTED_RISK_REASON_VALUES = {
    "APPROVED": "RISK_APPROVED",
    "INPUT_MISSING": "STATE_RISK_INPUT_MISSING",
    "MODE_NOT_RUNNING": "MODE_NOT_RUNNING",
    "INTERNAL_HALT": "KILL_INTERNAL_HALT",
    "OPERATOR_KILL": "KILL_OPERATOR_CONTROL",
    "WATCHDOG_UNHEALTHY": "CONTROL_WATCHDOG_UNHEALTHY",
    "NOT_RECONCILED": "STATE_NOT_RECONCILED",
    "UNKNOWN_ORDER": "STATE_UNKNOWN_ORDER",
    "CLOCK_OFFSET": "TIME_CLOCK_OFFSET",
    "SESSION_CLOSED": "TIME_SESSION_CLOSED",
    "INTENT_IN_FUTURE": "TIME_INTENT_IN_FUTURE",
    "DATA_FUTURE": "DATA_FUTURE",
    "DATA_STALE": "DATA_STALE",
    "LIQUIDITY_MISSING": "DATA_LIQUIDITY_MISSING",
    "SYMBOL_NOT_ALLOWED": "ORDER_SYMBOL_NOT_ALLOWED",
    "ORDER_TYPE_NOT_ALLOWED": "ORDER_TYPE_NOT_ALLOWED",
    "TIME_IN_FORCE_NOT_ALLOWED": "ORDER_TIME_IN_FORCE_NOT_ALLOWED",
    "ORDER_QUANTITY": "ORDER_QUANTITY_LIMIT",
    "ORDER_NOTIONAL": "ORDER_NOTIONAL_LIMIT",
    "SHORT_POSITION": "EXPOSURE_SHORT_NOT_ALLOWED",
    "POSITION_NOTIONAL": "EXPOSURE_POSITION_NOTIONAL_LIMIT",
    "POSITION_CONCENTRATION": "EXPOSURE_POSITION_CONCENTRATION_LIMIT",
    "GROSS_EXPOSURE": "EXPOSURE_GROSS_LIMIT",
    "NET_EXPOSURE": "EXPOSURE_NET_LIMIT",
    "LEVERAGE": "EXPOSURE_LEVERAGE_LIMIT",
    "OPEN_POSITIONS": "EXPOSURE_OPEN_POSITIONS_LIMIT",
    "ADV": "EXPOSURE_ADV_LIMIT",
    "ORDER_RATE": "CONTROL_ORDER_RATE_LIMIT",
    "DAILY_LOSS": "LOSS_DAILY_LIMIT",
    "DRAWDOWN": "LOSS_DRAWDOWN_LIMIT",
}

EXPECTED_DIRECT_REASON_VALUES = {
    ReasonCode.CONFIG_MISSING: "MODE_CONFIG_MISSING",
    ReasonCode.CONFIG_INVALID: "MODE_CONFIG_INVALID",
    ReasonCode.LIVE_DENIED: "MODE_LIVE_DENIED",
    ReasonCode.KILL_CLEAR: "CONTROL_KILL_CLEAR",
    ReasonCode.KILL_UNKNOWN: "CONTROL_KILL_UNKNOWN",
    ReasonCode.KILL_PRESENT: "CONTROL_KILL_PRESENT",
    ReasonCode.HEARTBEAT_MISSING: "CONTROL_HEARTBEAT_MISSING",
    ReasonCode.HEARTBEAT_UNREADABLE: "CONTROL_HEARTBEAT_UNREADABLE",
    ReasonCode.HEARTBEAT_INVALID: "CONTROL_HEARTBEAT_INVALID",
    ReasonCode.HEARTBEAT_FUTURE: "CONTROL_HEARTBEAT_FUTURE",
    ReasonCode.HEARTBEAT_STALE: "CONTROL_HEARTBEAT_STALE",
    ReasonCode.HEARTBEAT_HEALTHY: "CONTROL_HEARTBEAT_HEALTHY",
}


def test_domain_contract_version_is_explicit() -> None:
    assert DOMAIN_CONTRACT_VERSION == "1"


def test_order_purposes_match_execution_contract() -> None:
    assert {purpose.value for purpose in OrderPurpose} == {
        "RECOVERY",
        "RISK_REDUCTION",
        "STRATEGY",
    }


def test_order_statuses_match_execution_state_machine() -> None:
    assert {status.value for status in OrderStatus} == {
        "ACCEPTED",
        "CANCELED",
        "EXPIRED",
        "FILLED",
        "INTENT_RECORDED",
        "PARTIALLY_FILLED",
        "PENDING_CANCEL",
        "READY_TO_SUBMIT",
        "REJECTED",
        "RISK_REJECTED",
        "SUBMITTING",
        "UNKNOWN",
    }


def test_reason_registry_values_are_unique_and_namespaced() -> None:
    values = [reason.value for reason in ReasonCode]

    assert len(values) == len(set(values))
    assert all(reason.family in ReasonFamily for reason in ReasonCode)


def test_every_existing_risk_reason_is_registry_compatible() -> None:
    assert {name: reason.value for name, reason in RiskReason.__members__.items()} == (
        EXPECTED_RISK_REASON_VALUES
    )
    assert {ReasonCode(reason.value) for reason in RiskReason} <= set(ReasonCode)


def test_directly_emitted_reason_values_are_locked() -> None:
    assert {reason: reason.value for reason in EXPECTED_DIRECT_REASON_VALUES} == (
        EXPECTED_DIRECT_REASON_VALUES
    )


def test_config_reason_outputs_preserve_registry_values() -> None:
    results = (
        load_runtime_config(None),
        load_runtime_config({"schema_version": "2", "mode": "BACKTEST"}),
        load_runtime_config({"schema_version": "1", "mode": "LIVE"}),
    )

    assert {
        ReasonCode(reason)
        for result in results
        for reason in result.reason_codes
    } == {
        ReasonCode.CONFIG_INVALID,
        ReasonCode.CONFIG_MISSING,
        ReasonCode.LIVE_DENIED,
    }


def test_operator_kill_reason_outputs_preserve_registry_values(tmp_path: Path) -> None:
    kill_path = tmp_path / "KILL"
    clear = assess_operator_kill(kill_path)
    kill_path.touch()
    present = assess_operator_kill(kill_path)

    assert ReasonCode(clear.reason_code) is ReasonCode.KILL_CLEAR
    assert ReasonCode(present.reason_code) is ReasonCode.KILL_PRESENT


def test_heartbeat_reason_outputs_preserve_registry_values(tmp_path: Path) -> None:
    heartbeat_path = tmp_path / "heartbeat"
    now = datetime(2026, 8, 31, 12, tzinfo=UTC)
    missing = assess_heartbeat(
        heartbeat_path,
        now,
        max_age=timedelta(seconds=30),
        max_future_offset=timedelta(seconds=1),
    )
    record = HeartbeatRecord(
        schema_version="1",
        process_instance="process-1",
        session_id="session-1",
        mode=OperatingMode.PAPER,
        state=TradingState.READY,
        written_at_utc=now,
        last_reconciliation_id=None,
    )
    write_heartbeat(heartbeat_path, record)
    healthy = assess_heartbeat(
        heartbeat_path,
        now,
        max_age=timedelta(seconds=30),
        max_future_offset=timedelta(seconds=1),
    )

    assert ReasonCode(missing.reason_code) is ReasonCode.HEARTBEAT_MISSING
    assert ReasonCode(healthy.reason_code) is ReasonCode.HEARTBEAT_HEALTHY


def test_unreadable_heartbeat_output_preserves_registry_value(tmp_path: Path) -> None:
    heartbeat_directory = tmp_path / "heartbeat"
    heartbeat_directory.mkdir()

    unreadable = assess_heartbeat(
        heartbeat_directory,
        datetime(2026, 8, 31, 12, tzinfo=UTC),
        max_age=timedelta(seconds=30),
        max_future_offset=timedelta(seconds=1),
    )

    assert unreadable.reason_code is ReasonCode.HEARTBEAT_UNREADABLE


def test_str_enums_serialize_as_stable_strings() -> None:
    assert f"{ReasonCode.ORDER_OUTCOME_UNKNOWN}" == "ORDER_OUTCOME_UNKNOWN"
    assert f"{OrderPurpose.RISK_REDUCTION}" == "RISK_REDUCTION"
    assert f"{OrderStatus.PARTIALLY_FILLED}" == "PARTIALLY_FILLED"
    assert json.dumps([ReasonCode.LIVE_DENIED]) == '["MODE_LIVE_DENIED"]'