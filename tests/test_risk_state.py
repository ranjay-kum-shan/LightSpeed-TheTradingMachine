import sqlite3
from contextlib import closing
from dataclasses import replace
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from pathlib import Path
from typing import Any

import pytest

from trading_bot.risk import (
    RiskHaltState,
    RiskState,
    RiskStateConflictError,
    RiskStateError,
    RiskStateNotFoundError,
    SQLiteRiskStateStore,
)
from trading_bot.risk.models import RiskReason
from trading_bot.storage import SQLiteTransaction

NOW = datetime(2026, 9, 1, 14, 0, tzinfo=UTC)
PROFILE_HASH = "a" * 64


def make_store(path: Path) -> SQLiteRiskStateStore:
    return SQLiteRiskStateStore(
        path,
        profile_hash=PROFILE_HASH,
        max_daily_loss=Decimal("1000"),
        max_drawdown_from_peak=Decimal("0.25"),
    )


def make_state(**changes: Any) -> RiskState:
    values: dict[str, Any] = {
        "scope_id": "scope-1",
        "session_id": "2026-09-01",
        "session_start_equity": Decimal("100000"),
        "current_risk_equity": Decimal("100000"),
        "high_water_equity": Decimal("100000"),
        "net_external_flow": Decimal(0),
        "halt_state": RiskHaltState.CLEAR,
        "halt_reason": None,
        "revision": 1,
        "updated_at_utc": NOW,
    }
    values.update(changes)
    return RiskState(**values)


def test_restart_preserves_daily_loss_halt_after_equity_recovers(tmp_path: Path) -> None:
    database_path = tmp_path / "state" / "trading.sqlite"
    store = make_store(database_path)
    assert store.migrate() == (1,)
    store.initialize(
        scope_id="paper-account:strategy-1",
        session_id="2026-09-01",
        session_start_equity=Decimal("100000"),
        high_water_equity=Decimal("100000"),
        reconciliation_id="recon-init",
        recorded_at_utc=NOW,
    )

    breached = store.record_equity(
        "paper-account:strategy-1",
        Decimal("99000"),
        NOW + timedelta(minutes=1),
    )
    reopened = make_store(database_path)
    assert reopened.migrate() == ()
    loaded = reopened.load("paper-account:strategy-1")
    recovered = reopened.record_equity(
        "paper-account:strategy-1",
        Decimal("99900"),
        NOW + timedelta(minutes=2),
    )

    assert breached.halt_state is RiskHaltState.LOSS_HALTED
    assert loaded == breached
    assert recovered.halt_state is RiskHaltState.LOSS_HALTED
    assert recovered.halt_reason is RiskReason.DAILY_LOSS
    assert recovered.daily_loss == Decimal("100")


def test_drawdown_takes_precedence_and_survives_new_session(tmp_path: Path) -> None:
    database_path = tmp_path / "state.sqlite"
    store = make_store(database_path)
    store.migrate()
    store.initialize(
        scope_id="scope-1",
        session_id="2026-09-01",
        session_start_equity=Decimal("100000"),
        high_water_equity=Decimal("120000"),
        reconciliation_id="recon-init",
        recorded_at_utc=NOW,
    )

    halted = store.record_equity(
        "scope-1",
        Decimal("90000"),
        NOW + timedelta(minutes=1),
    )
    closed = store.close_session(
        "scope-1",
        current_risk_equity=Decimal("121000"),
        reconciliation_id="recon-2026-09-01",
        recorded_at_utc=NOW + timedelta(minutes=2),
    )
    next_session = store.start_session(
        "scope-1",
        session_id="2026-09-02",
        session_start_equity=Decimal("121000"),
        reconciliation_id="recon-2026-09-02",
        recorded_at_utc=NOW + timedelta(days=1),
    )

    assert halted.halt_state is RiskHaltState.HARD_HALTED
    assert halted.halt_reason is RiskReason.DRAWDOWN
    assert halted.daily_loss == Decimal("10000")
    assert halted.drawdown == Decimal("0.25")
    assert closed.high_water_equity == Decimal("121000")
    assert next_session.halt_state is RiskHaltState.HARD_HALTED
    assert next_session.halt_reason is RiskReason.DRAWDOWN


def test_initialization_persists_an_already_crossed_drawdown(tmp_path: Path) -> None:
    database_path = tmp_path / "state.sqlite"
    store = make_store(database_path)
    store.migrate()

    initialized = store.initialize(
        scope_id="scope-1",
        session_id="2026-09-01",
        session_start_equity=Decimal("75000"),
        high_water_equity=Decimal("100000"),
        reconciliation_id="recon-init",
        recorded_at_utc=NOW,
    )

    assert initialized.halt_state is RiskHaltState.HARD_HALTED
    assert initialized.halt_reason is RiskReason.DRAWDOWN
    assert make_store(database_path).load("scope-1") == initialized


def test_new_session_clears_daily_halt_only_after_reconciled_close(tmp_path: Path) -> None:
    store = make_store(tmp_path / "state.sqlite")
    store.migrate()
    store.initialize(
        scope_id="scope-1",
        session_id="2026-09-01",
        session_start_equity=Decimal("100000"),
        high_water_equity=Decimal("100000"),
        reconciliation_id="recon-init",
        recorded_at_utc=NOW,
    )
    store.record_equity("scope-1", Decimal("99000"), NOW + timedelta(minutes=1))

    with pytest.raises(RiskStateConflictError, match="must be closed"):
        store.start_session(
            "scope-1",
            session_id="2026-09-02",
            session_start_equity=Decimal("100500"),
            reconciliation_id="recon-2",
            recorded_at_utc=NOW + timedelta(days=1),
        )

    closed = store.close_session(
        "scope-1",
        current_risk_equity=Decimal("100500"),
        reconciliation_id="recon-1",
        recorded_at_utc=NOW + timedelta(minutes=2),
    )
    started = store.start_session(
        "scope-1",
        session_id="2026-09-02",
        session_start_equity=Decimal("100500"),
        reconciliation_id="recon-2",
        recorded_at_utc=NOW + timedelta(days=1),
    )

    assert closed.halt_state is RiskHaltState.LOSS_HALTED
    assert closed.high_water_equity == Decimal("100500")
    assert started.halt_state is RiskHaltState.CLEAR
    assert started.halt_reason is None
    assert started.net_external_flow == 0


@pytest.mark.parametrize(
    ("scope_id", "opening_equity", "flow_id", "opening_flow", "expected_high_water"),
    [
        ("deposit", Decimal("125000"), "deposit-1", Decimal("25000"), Decimal("125000")),
        ("withdrawal", Decimal("75000"), "withdrawal-1", Decimal("-25000"), Decimal("75000")),
    ],
)
def test_documented_opening_flow_adjusts_high_water_without_creating_pnl(
    tmp_path: Path,
    scope_id: str,
    opening_equity: Decimal,
    flow_id: str,
    opening_flow: Decimal,
    expected_high_water: Decimal,
) -> None:
    store = make_store(tmp_path / "state.sqlite")
    store.migrate()
    store.initialize(
        scope_id=scope_id,
        session_id="2026-09-01",
        session_start_equity=Decimal("100000"),
        high_water_equity=Decimal("100000"),
        reconciliation_id=f"recon-init-{scope_id}",
        recorded_at_utc=NOW,
    )
    store.close_session(
        scope_id,
        current_risk_equity=Decimal("100000"),
        reconciliation_id=f"recon-close-{scope_id}",
        recorded_at_utc=NOW + timedelta(minutes=1),
    )

    started = store.start_session(
        scope_id,
        session_id="2026-09-02",
        session_start_equity=opening_equity,
        reconciliation_id=f"recon-start-{scope_id}",
        recorded_at_utc=NOW + timedelta(days=1),
        opening_flow_id=flow_id,
        opening_external_flow=opening_flow,
    )

    assert started.high_water_equity == expected_high_water
    assert started.daily_pnl == 0
    assert started.drawdown == 0
    assert started.halt_state is RiskHaltState.CLEAR


def test_unexplained_opening_equity_gap_remains_subject_to_drawdown(tmp_path: Path) -> None:
    store = make_store(tmp_path / "state.sqlite")
    store.migrate()
    store.initialize(
        scope_id="scope-1",
        session_id="2026-09-01",
        session_start_equity=Decimal("100000"),
        high_water_equity=Decimal("100000"),
        reconciliation_id="recon-init",
        recorded_at_utc=NOW,
    )
    store.close_session(
        "scope-1",
        current_risk_equity=Decimal("100000"),
        reconciliation_id="recon-close",
        recorded_at_utc=NOW + timedelta(minutes=1),
    )

    started = store.start_session(
        "scope-1",
        session_id="2026-09-02",
        session_start_equity=Decimal("50000"),
        reconciliation_id="recon-start",
        recorded_at_utc=NOW + timedelta(days=1),
    )

    assert started.daily_pnl == 0
    assert started.drawdown == Decimal("0.5")
    assert started.halt_state is RiskHaltState.HARD_HALTED
    assert started.halt_reason is RiskReason.DRAWDOWN


@pytest.mark.parametrize(
    ("flow_id", "amount", "match"),
    [
        ("flow-without-amount", Decimal(0), "requires a nonzero"),
        (None, Decimal("1"), "requires opening_flow_id"),
        ("flow-1", Decimal("NaN"), "must be finite"),
    ],
)
def test_opening_flow_requires_complete_finite_identity(
    tmp_path: Path,
    flow_id: str | None,
    amount: Decimal,
    match: str,
) -> None:
    store = make_store(tmp_path / "state.sqlite")

    with pytest.raises(ValueError, match=match):
        store.start_session(
            "scope-1",
            session_id="2026-09-02",
            session_start_equity=Decimal("100000"),
            reconciliation_id="recon-start",
            recorded_at_utc=NOW,
            opening_flow_id=flow_id,
            opening_external_flow=amount,
        )


def test_capital_flows_are_neutral_idempotent_and_append_only(tmp_path: Path) -> None:
    database_path = tmp_path / "state.sqlite"
    store = make_store(database_path)
    store.migrate()
    store.initialize(
        scope_id="scope-1",
        session_id="2026-09-01",
        session_start_equity=Decimal("100000"),
        high_water_equity=Decimal("100000"),
        reconciliation_id="recon-init",
        recorded_at_utc=NOW,
    )

    deposited = store.record_capital_flow(
        "scope-1",
        flow_id="deposit-1",
        amount=Decimal("10000"),
        current_risk_equity=Decimal("110000"),
        reconciliation_id="recon-deposit",
        recorded_at_utc=NOW + timedelta(minutes=1),
    )
    duplicate = store.record_capital_flow(
        "scope-1",
        flow_id="deposit-1",
        amount=Decimal("10000.0"),
        current_risk_equity=Decimal("110000.00"),
        reconciliation_id="recon-deposit",
        recorded_at_utc=NOW + timedelta(minutes=1),
    )
    withdrawn = store.record_capital_flow(
        "scope-1",
        flow_id="withdrawal-1",
        amount=Decimal("-20000"),
        current_risk_equity=Decimal("90000"),
        reconciliation_id="recon-withdrawal",
        recorded_at_utc=NOW + timedelta(minutes=2),
    )

    assert deposited.daily_pnl == 0
    assert deposited.drawdown == 0
    assert duplicate == deposited
    assert withdrawn.daily_pnl == 0
    assert withdrawn.drawdown == 0
    assert withdrawn.high_water_equity == Decimal("90000")
    assert withdrawn.net_external_flow == Decimal("-10000")
    assert withdrawn.halt_state is RiskHaltState.CLEAR
    with closing(sqlite3.connect(database_path)) as connection:
        event_count = connection.execute("SELECT COUNT(*) FROM risk_state_events").fetchone()
        flow_count = connection.execute("SELECT COUNT(*) FROM risk_capital_flows").fetchone()
    assert event_count == (3,)
    assert flow_count == (2,)


def test_delayed_exact_flow_retry_is_idempotent_after_new_session(tmp_path: Path) -> None:
    database_path = tmp_path / "state.sqlite"
    store = make_store(database_path)
    store.migrate()
    store.initialize(
        scope_id="scope-1",
        session_id="2026-09-01",
        session_start_equity=Decimal("100000"),
        high_water_equity=Decimal("100000"),
        reconciliation_id="recon-init",
        recorded_at_utc=NOW,
    )
    store.record_capital_flow(
        "scope-1",
        flow_id="deposit-1",
        amount=Decimal("1000"),
        current_risk_equity=Decimal("101000"),
        reconciliation_id="recon-flow",
        recorded_at_utc=NOW + timedelta(minutes=1),
    )
    store.close_session(
        "scope-1",
        current_risk_equity=Decimal("101000"),
        reconciliation_id="recon-close",
        recorded_at_utc=NOW + timedelta(minutes=2),
    )
    current = store.start_session(
        "scope-1",
        session_id="2026-09-02",
        session_start_equity=Decimal("101000"),
        reconciliation_id="recon-start",
        recorded_at_utc=NOW + timedelta(days=1),
    )

    duplicate = store.record_capital_flow(
        "scope-1",
        flow_id="deposit-1",
        amount=Decimal("1000.00"),
        current_risk_equity=Decimal("101000.0"),
        reconciliation_id="recon-flow",
        recorded_at_utc=NOW + timedelta(minutes=1),
    )

    assert duplicate == current
    with closing(sqlite3.connect(database_path)) as connection:
        flow_count = connection.execute("SELECT COUNT(*) FROM risk_capital_flows").fetchone()
    assert flow_count == (1,)


def test_conflicting_flow_and_reused_session_identity_fail_closed(tmp_path: Path) -> None:
    store = make_store(tmp_path / "state.sqlite")
    store.migrate()
    store.initialize(
        scope_id="scope-1",
        session_id="2026-09-01",
        session_start_equity=Decimal("100000"),
        high_water_equity=Decimal("100000"),
        reconciliation_id="recon-init",
        recorded_at_utc=NOW,
    )
    store.record_capital_flow(
        "scope-1",
        flow_id="flow-1",
        amount=Decimal("100"),
        current_risk_equity=Decimal("100100"),
        reconciliation_id="recon-flow",
        recorded_at_utc=NOW + timedelta(minutes=1),
    )

    with pytest.raises(RiskStateConflictError, match="conflicting facts"):
        store.record_capital_flow(
            "scope-1",
            flow_id="flow-1",
            amount=Decimal("200"),
            current_risk_equity=Decimal("100200"),
            reconciliation_id="recon-flow",
            recorded_at_utc=NOW + timedelta(minutes=1),
        )

    store.close_session(
        "scope-1",
        current_risk_equity=Decimal("100100"),
        reconciliation_id="recon-1",
        recorded_at_utc=NOW + timedelta(minutes=2),
    )
    with pytest.raises(RiskStateConflictError, match="already been used"):
        store.start_session(
            "scope-1",
            session_id="2026-09-01",
            session_start_equity=Decimal("100100"),
            reconciliation_id="recon-reused",
            recorded_at_utc=NOW + timedelta(days=1),
        )


def test_opening_flow_identity_cannot_reuse_an_existing_flow(tmp_path: Path) -> None:
    store = make_store(tmp_path / "state.sqlite")
    store.migrate()
    store.initialize(
        scope_id="scope-1",
        session_id="2026-09-01",
        session_start_equity=Decimal("100000"),
        high_water_equity=Decimal("100000"),
        reconciliation_id="recon-init",
        recorded_at_utc=NOW,
    )
    store.record_capital_flow(
        "scope-1",
        flow_id="flow-1",
        amount=Decimal("100"),
        current_risk_equity=Decimal("100100"),
        reconciliation_id="recon-flow",
        recorded_at_utc=NOW + timedelta(minutes=1),
    )
    store.close_session(
        "scope-1",
        current_risk_equity=Decimal("100100"),
        reconciliation_id="recon-close",
        recorded_at_utc=NOW + timedelta(minutes=2),
    )

    with pytest.raises(RiskStateConflictError, match="opening flow identity"):
        store.start_session(
            "scope-1",
            session_id="2026-09-02",
            session_start_equity=Decimal("100200"),
            reconciliation_id="recon-start",
            recorded_at_utc=NOW + timedelta(days=1),
            opening_flow_id="flow-1",
            opening_external_flow=Decimal("100"),
        )


def test_missing_stale_and_closed_state_events_fail_closed(tmp_path: Path) -> None:
    store = make_store(tmp_path / "state.sqlite")
    store.migrate()
    with pytest.raises(RiskStateNotFoundError, match="missing"):
        store.load("missing-scope")
    store.initialize(
        scope_id="scope-1",
        session_id="2026-09-01",
        session_start_equity=Decimal("100000"),
        high_water_equity=Decimal("100000"),
        reconciliation_id="recon-init",
        recorded_at_utc=NOW,
    )
    with pytest.raises(RiskStateError, match="advance event time"):
        store.record_equity("scope-1", Decimal("99999"), NOW)
    store.close_session(
        "scope-1",
        current_risk_equity=Decimal("100000"),
        reconciliation_id="recon-1",
        recorded_at_utc=NOW + timedelta(minutes=1),
    )
    with pytest.raises(RiskStateConflictError, match="closed session"):
        store.record_equity(
            "scope-1",
            Decimal("100001"),
            NOW + timedelta(minutes=2),
        )


@pytest.mark.parametrize(
    ("changes", "match"),
    [
        ({"scope_id": ""}, "scope_id"),
        ({"session_id": " padded "}, "session_id"),
        ({"session_start_equity": Decimal(0)}, "session_start_equity"),
        ({"current_risk_equity": Decimal("NaN")}, "current_risk_equity"),
        ({"high_water_equity": Decimal(-1)}, "high_water_equity"),
        ({"net_external_flow": Decimal("Infinity")}, "net_external_flow"),
        ({"revision": 0}, "revision"),
        ({"updated_at_utc": datetime(2026, 9, 1, 14, 0)}, "updated_at_utc"),
        (
            {"halt_state": RiskHaltState.CLEAR, "halt_reason": RiskReason.DAILY_LOSS},
            "present exactly",
        ),
        (
            {
                "halt_state": RiskHaltState.LOSS_HALTED,
                "halt_reason": RiskReason.ORDER_RATE,
            },
            "LOSS_HALTED requires",
        ),
        (
            {
                "halt_state": RiskHaltState.LOSS_HALTED,
                "halt_reason": RiskReason.DRAWDOWN,
            },
            "LOSS_HALTED requires",
        ),
        (
            {
                "halt_state": RiskHaltState.HARD_HALTED,
                "halt_reason": RiskReason.DAILY_LOSS,
            },
            "HARD_HALTED requires",
        ),
        (
            {
                "halt_state": RiskHaltState.HARD_HALTED,
                "halt_reason": RiskReason.APPROVED,
            },
            "HARD_HALTED requires",
        ),
    ],
)
def test_risk_state_rejects_invalid_values(changes: dict[str, Any], match: str) -> None:
    with pytest.raises(ValueError, match=match):
        replace(make_state(), **changes)


@pytest.mark.parametrize(
    ("daily_loss", "drawdown", "match"),
    [
        (Decimal(0), Decimal("0.25"), "max_daily_loss"),
        (Decimal("1000"), Decimal("1.01"), "no greater than one"),
    ],
)
def test_store_rejects_invalid_limits(
    tmp_path: Path,
    daily_loss: Decimal,
    drawdown: Decimal,
    match: str,
) -> None:
    with pytest.raises(ValueError, match=match):
        SQLiteRiskStateStore(
            tmp_path / "state.sqlite",
            profile_hash=PROFILE_HASH,
            max_daily_loss=daily_loss,
            max_drawdown_from_peak=drawdown,
        )


@pytest.mark.parametrize("profile_hash", ["", "A" * 64, "g" * 64, "a" * 63])
def test_store_rejects_invalid_profile_hash(tmp_path: Path, profile_hash: str) -> None:
    with pytest.raises(ValueError, match="64 lowercase hexadecimal"):
        SQLiteRiskStateStore(
            tmp_path / "state.sqlite",
            profile_hash=profile_hash,
            max_daily_loss=Decimal("1000"),
            max_drawdown_from_peak=Decimal("0.25"),
        )


def test_duplicate_scope_initialization_fails_closed(tmp_path: Path) -> None:
    store = make_store(tmp_path / "state.sqlite")
    store.migrate()
    arguments: dict[str, Any] = {
        "scope_id": "scope-1",
        "session_id": "2026-09-01",
        "session_start_equity": Decimal("100000"),
        "high_water_equity": Decimal("100000"),
        "reconciliation_id": "recon-init",
        "recorded_at_utc": NOW,
    }
    store.initialize(**arguments)

    with pytest.raises(RiskStateConflictError, match="already initialized"):
        store.initialize(**arguments)


def test_reopen_with_different_risk_profile_fails_closed(tmp_path: Path) -> None:
    database_path = tmp_path / "state.sqlite"
    store = make_store(database_path)
    store.migrate()
    store.initialize(
        scope_id="scope-1",
        session_id="2026-09-01",
        session_start_equity=Decimal("100000"),
        high_water_equity=Decimal("100000"),
        reconciliation_id="recon-init",
        recorded_at_utc=NOW,
    )
    changed_profile = SQLiteRiskStateStore(
        database_path,
        profile_hash="b" * 64,
        max_daily_loss=Decimal("2000"),
        max_drawdown_from_peak=Decimal("0.5"),
    )

    with pytest.raises(RiskStateConflictError, match="different risk profile"):
        changed_profile.load("scope-1")


@pytest.mark.parametrize("amount", [Decimal(0), Decimal("NaN")])
def test_invalid_capital_flow_is_rejected(tmp_path: Path, amount: Decimal) -> None:
    store = make_store(tmp_path / "state.sqlite")

    with pytest.raises(ValueError, match="finite and nonzero"):
        store.record_capital_flow(
            "scope-1",
            flow_id="flow-1",
            amount=amount,
            current_risk_equity=Decimal("100000"),
            reconciliation_id="recon-flow",
            recorded_at_utc=NOW,
        )


def test_withdrawal_cannot_make_high_water_nonpositive(tmp_path: Path) -> None:
    database_path = tmp_path / "state.sqlite"
    store = make_store(database_path)
    store.migrate()
    store.initialize(
        scope_id="scope-1",
        session_id="2026-09-01",
        session_start_equity=Decimal("100000"),
        high_water_equity=Decimal("100000"),
        reconciliation_id="recon-init",
        recorded_at_utc=NOW,
    )

    with pytest.raises(ValueError, match="capital-flow-adjusted"):
        store.record_capital_flow(
            "scope-1",
            flow_id="withdrawal-all",
            amount=Decimal("-100000"),
            current_risk_equity=Decimal("1"),
            reconciliation_id="recon-withdrawal",
            recorded_at_utc=NOW + timedelta(minutes=1),
        )

    with closing(sqlite3.connect(database_path)) as connection:
        flow_count = connection.execute("SELECT COUNT(*) FROM risk_capital_flows").fetchone()
    assert flow_count == (0,)
    assert store.load("scope-1") == make_state()


@pytest.mark.parametrize("history_change", ["DELETE", "INSERT"])
def test_noncontiguous_event_history_fails_closed(
    tmp_path: Path,
    history_change: str,
) -> None:
    database_path = tmp_path / "state.sqlite"
    store = make_store(database_path)
    store.migrate()
    store.initialize(
        scope_id="scope-1",
        session_id="2026-09-01",
        session_start_equity=Decimal("100000"),
        high_water_equity=Decimal("100000"),
        reconciliation_id="recon-init",
        recorded_at_utc=NOW,
    )
    store.record_equity("scope-1", Decimal("99999"), NOW + timedelta(minutes=1))
    store.record_equity("scope-1", Decimal("99998"), NOW + timedelta(minutes=2))
    with closing(sqlite3.connect(database_path)) as connection:
        if history_change == "DELETE":
            connection.execute(
                "DELETE FROM risk_state_events WHERE scope_id = ? AND revision = 2",
                ("scope-1",),
            )
        else:
            connection.execute(
                """
                INSERT INTO risk_state_events (
                    scope_id, revision, event_type, session_id,
                    session_start_equity, current_risk_equity,
                    net_external_flow, high_water_equity, halt_state,
                    halt_reason, flow_id, flow_amount, reconciliation_id,
                    occurred_at_utc, previous_event_hash, event_hash
                )
                SELECT scope_id, 4, 'EQUITY_MARK', session_id,
                       session_start_equity, current_risk_equity,
                       net_external_flow, high_water_equity, halt_state,
                       halt_reason, NULL, NULL, NULL, occurred_at_utc,
                       event_hash, printf('%064d', 0)
                FROM risk_state_events
                WHERE scope_id = ? AND revision = 3
                """,
                ("scope-1",),
            )
        connection.commit()

    with pytest.raises(RiskStateError, match="history is not contiguous"):
        store.load("scope-1")


def test_equal_count_revision_gap_fails_closed(tmp_path: Path) -> None:
    database_path = tmp_path / "state.sqlite"
    store = make_store(database_path)
    store.migrate()
    store.initialize(
        scope_id="scope-1",
        session_id="2026-09-01",
        session_start_equity=Decimal("100000"),
        high_water_equity=Decimal("100000"),
        reconciliation_id="recon-init",
        recorded_at_utc=NOW,
    )
    store.record_equity("scope-1", Decimal("99999"), NOW + timedelta(minutes=1))
    with closing(sqlite3.connect(database_path)) as connection:
        connection.execute(
            "UPDATE risk_state_events SET revision = 3 WHERE scope_id = ? AND revision = 2",
            ("scope-1",),
        )
        connection.commit()

    with pytest.raises(RiskStateError, match="history is not contiguous"):
        store.load("scope-1")


def test_corrupt_current_state_fails_closed(tmp_path: Path) -> None:
    database_path = tmp_path / "state.sqlite"
    store = make_store(database_path)
    store.migrate()
    store.initialize(
        scope_id="scope-1",
        session_id="2026-09-01",
        session_start_equity=Decimal("100000"),
        high_water_equity=Decimal("100000"),
        reconciliation_id="recon-init",
        recorded_at_utc=NOW,
    )

    with closing(sqlite3.connect(database_path)) as connection:
        connection.execute(
            "UPDATE risk_state_current SET current_risk_equity = 'NaN' WHERE scope_id = ?",
            ("scope-1",),
        )
        connection.commit()

    with pytest.raises(RiskStateError, match="state is invalid"):
        store.load("scope-1")


def test_earlier_event_hash_tamper_fails_closed(tmp_path: Path) -> None:
    database_path = tmp_path / "state.sqlite"
    store = make_store(database_path)
    store.migrate()
    store.initialize(
        scope_id="scope-1",
        session_id="2026-09-01",
        session_start_equity=Decimal("100000"),
        high_water_equity=Decimal("100000"),
        reconciliation_id="recon-init",
        recorded_at_utc=NOW,
    )
    store.record_equity("scope-1", Decimal("99999"), NOW + timedelta(minutes=1))
    with closing(sqlite3.connect(database_path)) as connection:
        connection.execute(
            """
            UPDATE risk_state_events
            SET current_risk_equity = '99999'
            WHERE scope_id = ? AND revision = 1
            """,
            ("scope-1",),
        )
        connection.commit()

    with pytest.raises(RiskStateError, match="hash chain is invalid"):
        store.load("scope-1")


@pytest.mark.parametrize("ledger_change", ["DELETE", "UPDATE"])
def test_capital_flow_ledger_divergence_fails_closed(
    tmp_path: Path,
    ledger_change: str,
) -> None:
    database_path = tmp_path / "state.sqlite"
    store = make_store(database_path)
    store.migrate()
    store.initialize(
        scope_id="scope-1",
        session_id="2026-09-01",
        session_start_equity=Decimal("100000"),
        high_water_equity=Decimal("100000"),
        reconciliation_id="recon-init",
        recorded_at_utc=NOW,
    )
    store.record_capital_flow(
        "scope-1",
        flow_id="deposit-1",
        amount=Decimal("1000"),
        current_risk_equity=Decimal("101000"),
        reconciliation_id="recon-flow",
        recorded_at_utc=NOW + timedelta(minutes=1),
    )
    with closing(sqlite3.connect(database_path)) as connection:
        if ledger_change == "DELETE":
            connection.execute(
                "DELETE FROM risk_capital_flows WHERE scope_id = ?",
                ("scope-1",),
            )
        else:
            connection.execute(
                "UPDATE risk_capital_flows SET amount = '999' WHERE scope_id = ?",
                ("scope-1",),
            )
        connection.commit()

    with pytest.raises(RiskStateError, match="ledger disagrees"):
        store.load("scope-1")


def test_current_state_disagreement_fails_closed(tmp_path: Path) -> None:
    database_path = tmp_path / "state.sqlite"
    store = make_store(database_path)
    store.migrate()
    store.initialize(
        scope_id="scope-1",
        session_id="2026-09-01",
        session_start_equity=Decimal("100000"),
        high_water_equity=Decimal("100000"),
        reconciliation_id="recon-init",
        recorded_at_utc=NOW,
    )
    with closing(sqlite3.connect(database_path)) as connection:
        connection.execute(
            "UPDATE risk_state_current SET current_risk_equity = '99999' WHERE scope_id = ?",
            ("scope-1",),
        )
        connection.commit()

    with pytest.raises(RiskStateError, match="disagrees with durable event history"):
        store.load("scope-1")


def test_missing_predecessor_during_append_rolls_back(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    database_path = tmp_path / "state.sqlite"
    store = make_store(database_path)
    store.migrate()
    initial = store.initialize(
        scope_id="scope-1",
        session_id="2026-09-01",
        session_start_equity=Decimal("100000"),
        high_water_equity=Decimal("100000"),
        reconciliation_id="recon-init",
        recorded_at_utc=NOW,
    )
    load = store._load

    def load_then_remove_predecessor(
        transaction: SQLiteTransaction,
        scope_id: str,
    ) -> RiskState:
        state = load(transaction, scope_id)
        transaction.execute(
            "DELETE FROM risk_state_events WHERE scope_id = ? AND revision = ?",
            (scope_id, state.revision),
        )
        return state

    monkeypatch.setattr(store, "_load", load_then_remove_predecessor)

    with pytest.raises(RiskStateError, match="previous durable risk event is missing"):
        store.record_equity(
            "scope-1",
            Decimal("99999"),
            NOW + timedelta(minutes=1),
        )

    monkeypatch.undo()
    assert store.load("scope-1") == initial


def test_generic_hard_halt_is_sticky_and_preserves_original_reason(tmp_path: Path) -> None:
    database_path = tmp_path / "state.sqlite"
    store = make_store(database_path)
    store.migrate()
    store.initialize(
        scope_id="scope-1",
        session_id="2026-09-01",
        session_start_equity=Decimal("100000"),
        high_water_equity=Decimal("100000"),
        reconciliation_id="recon-init",
        recorded_at_utc=NOW,
    )

    halted = store.set_hard_halt(
        "scope-1",
        reason=RiskReason.NOT_RECONCILED,
        recorded_at_utc=NOW + timedelta(minutes=1),
    )
    reopened = make_store(database_path)
    improved = reopened.record_equity(
        "scope-1",
        Decimal("101000"),
        NOW + timedelta(minutes=2),
    )
    repeated = reopened.set_hard_halt(
        "scope-1",
        reason=RiskReason.WATCHDOG_UNHEALTHY,
        recorded_at_utc=NOW + timedelta(minutes=3),
    )

    assert halted.halt_state is RiskHaltState.HARD_HALTED
    assert reopened.load("scope-1") == repeated
    assert improved.halt_reason is RiskReason.NOT_RECONCILED
    assert repeated.halt_reason is RiskReason.NOT_RECONCILED


@pytest.mark.parametrize("reason", [RiskReason.APPROVED, RiskReason.DAILY_LOSS])
def test_hard_halt_refuses_non_hard_reasons(tmp_path: Path, reason: RiskReason) -> None:
    store = make_store(tmp_path / "state.sqlite")

    with pytest.raises(ValueError, match="non-daily rejection"):
        store.set_hard_halt("scope-1", reason=reason, recorded_at_utc=NOW)