"""Durable, capital-flow-aware loss and drawdown state."""

import json
import sqlite3
from dataclasses import dataclass, replace
from datetime import datetime
from decimal import Decimal
from hashlib import sha256
from pathlib import Path

from trading_bot.domain import ensure_utc
from trading_bot.risk.models import (
    RiskHaltState,
    RiskReason,
    RiskSnapshot,
    TradingState,
)
from trading_bot.storage import Migration, SQLiteDatabase, SQLiteTransaction

RISK_STATE_MIGRATIONS = (
    Migration(
        version=1,
        name="create_risk_state",
        statements=(
            """
            CREATE TABLE risk_state_current (
                scope_id TEXT PRIMARY KEY,
                session_id TEXT NOT NULL,
                session_start_equity TEXT NOT NULL,
                current_risk_equity TEXT NOT NULL,
                high_water_equity TEXT NOT NULL,
                net_external_flow TEXT NOT NULL,
                halt_state TEXT NOT NULL CHECK (
                    halt_state IN ('CLEAR', 'LOSS_HALTED', 'HARD_HALTED')
                ),
                halt_reason TEXT,
                revision INTEGER NOT NULL CHECK (revision > 0),
                updated_at_utc TEXT NOT NULL,
                CHECK (
                    (halt_state = 'CLEAR' AND halt_reason IS NULL)
                    OR (halt_state <> 'CLEAR' AND halt_reason IS NOT NULL)
                )
            ) STRICT
            """,
            """
            CREATE TABLE risk_state_profiles (
                scope_id TEXT PRIMARY KEY,
                profile_hash TEXT NOT NULL CHECK (length(profile_hash) = 64),
                FOREIGN KEY (scope_id) REFERENCES risk_state_current (scope_id)
            ) STRICT
            """,
            """
            CREATE TABLE risk_capital_flows (
                scope_id TEXT NOT NULL,
                flow_id TEXT NOT NULL,
                session_id TEXT NOT NULL,
                amount TEXT NOT NULL,
                current_risk_equity TEXT NOT NULL,
                reconciliation_id TEXT NOT NULL,
                occurred_at_utc TEXT NOT NULL,
                PRIMARY KEY (scope_id, flow_id),
                FOREIGN KEY (scope_id) REFERENCES risk_state_current (scope_id)
            ) STRICT
            """,
            """
            CREATE TABLE risk_state_events (
                scope_id TEXT NOT NULL,
                revision INTEGER NOT NULL CHECK (revision > 0),
                event_type TEXT NOT NULL CHECK (
                    event_type IN (
                        'INITIALIZED',
                        'EQUITY_MARK',
                        'CAPITAL_FLOW',
                        'HARD_HALT',
                        'SESSION_STARTED',
                        'SESSION_CLOSED'
                    )
                ),
                session_id TEXT NOT NULL,
                session_start_equity TEXT NOT NULL,
                current_risk_equity TEXT NOT NULL,
                net_external_flow TEXT NOT NULL,
                high_water_equity TEXT NOT NULL,
                halt_state TEXT NOT NULL,
                halt_reason TEXT,
                flow_id TEXT,
                flow_amount TEXT,
                reconciliation_id TEXT,
                occurred_at_utc TEXT NOT NULL,
                previous_event_hash TEXT,
                event_hash TEXT NOT NULL CHECK (length(event_hash) = 64),
                PRIMARY KEY (scope_id, revision),
                FOREIGN KEY (scope_id) REFERENCES risk_state_current (scope_id),
                CHECK (
                    (revision = 1 AND previous_event_hash IS NULL)
                    OR (revision > 1 AND length(previous_event_hash) = 64)
                )
            ) STRICT
            """,
        ),
    ),
)

type RiskStateParameter = bytes | float | int | str | None
_HASH_CHARACTERS = frozenset("0123456789abcdef")


class RiskStateError(RuntimeError):
    """Base error for invalid or unavailable durable risk state."""


class RiskStateNotFoundError(RiskStateError):
    """Raised when a required durable risk scope does not exist."""


class RiskStateConflictError(RiskStateError):
    """Raised when an identity or transition conflicts with durable history."""


def _require_identity(value: str, field_name: str) -> None:
    if not value or value != value.strip():
        raise ValueError(f"{field_name} must be non-empty and trimmed")


def _require_hash(value: str, field_name: str) -> None:
    if len(value) != 64 or any(character not in _HASH_CHARACTERS for character in value):
        raise ValueError(f"{field_name} must be 64 lowercase hexadecimal characters")


def _require_positive(value: Decimal, field_name: str) -> None:
    if not value.is_finite() or value <= 0:
        raise ValueError(f"{field_name} must be finite and positive")


def _decimal_text(value: Decimal) -> str:
    text = format(value, "f")
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    return "0" if value == 0 else text


def _event_hash(
    previous_event_hash: str | None,
    event_values: tuple[RiskStateParameter, ...],
) -> str:
    canonical = json.dumps(
        {
            "event": event_values,
            "previous_event_hash": previous_event_hash,
        },
        ensure_ascii=True,
        separators=(",", ":"),
    )
    return sha256(canonical.encode("utf-8")).hexdigest()


def _timestamp_text(value: datetime) -> str:
    return ensure_utc(value, "timestamp").isoformat(timespec="microseconds").replace(
        "+00:00",
        "Z",
    )


@dataclass(frozen=True, slots=True)
class RiskState:
    """One validated durable view of loss controls for an account scope."""

    scope_id: str
    session_id: str
    session_start_equity: Decimal
    current_risk_equity: Decimal
    high_water_equity: Decimal
    net_external_flow: Decimal
    halt_state: RiskHaltState
    halt_reason: RiskReason | None
    revision: int
    updated_at_utc: datetime

    def __post_init__(self) -> None:
        _require_identity(self.scope_id, "scope_id")
        _require_identity(self.session_id, "session_id")
        _require_positive(self.session_start_equity, "session_start_equity")
        _require_positive(self.current_risk_equity, "current_risk_equity")
        _require_positive(self.high_water_equity, "high_water_equity")
        if not self.net_external_flow.is_finite():
            raise ValueError("net_external_flow must be finite")
        if self.revision < 1:
            raise ValueError("revision must be positive")
        object.__setattr__(
            self,
            "updated_at_utc",
            ensure_utc(self.updated_at_utc, "updated_at_utc"),
        )
        if (self.halt_state is RiskHaltState.CLEAR) != (self.halt_reason is None):
            raise ValueError("halt_reason must be present exactly when state is halted")
        if (
            self.halt_state is RiskHaltState.LOSS_HALTED
            and self.halt_reason is not RiskReason.DAILY_LOSS
        ):
            raise ValueError("LOSS_HALTED requires the daily-loss reason")
        if (
            self.halt_state is RiskHaltState.HARD_HALTED
            and self.halt_reason in (RiskReason.APPROVED, RiskReason.DAILY_LOSS)
        ):
            raise ValueError("HARD_HALTED requires a hard rejection reason")

    @property
    def daily_pnl(self) -> Decimal:
        return self.current_risk_equity - self.session_start_equity - self.net_external_flow

    @property
    def daily_loss(self) -> Decimal:
        return max(Decimal(0), -self.daily_pnl)

    @property
    def drawdown(self) -> Decimal:
        return max(
            Decimal(0),
            (self.high_water_equity - self.current_risk_equity) / self.high_water_equity,
        )

    def enforce_snapshot(self, snapshot: RiskSnapshot) -> RiskSnapshot:
        """Overlay all durable loss facts and force the corresponding halt state."""

        if snapshot.as_of_utc < self.updated_at_utc:
            raise RiskStateError("risk snapshot predates durable risk state")
        runtime_state = snapshot.trading_state
        if self.halt_state is RiskHaltState.LOSS_HALTED:
            runtime_state = TradingState.LOSS_HALTED
        elif self.halt_state is RiskHaltState.HARD_HALTED:
            runtime_state = TradingState.HARD_HALTED
        return replace(
            snapshot,
            current_equity=self.current_risk_equity,
            session_start_equity=self.session_start_equity,
            high_water_equity=self.high_water_equity,
            net_external_flow=self.net_external_flow,
            trading_state=runtime_state,
            durable_halt_state=self.halt_state,
            durable_halt_reason=self.halt_reason,
            internal_halt=(
                snapshot.internal_halt or self.halt_state is not RiskHaltState.CLEAR
            ),
        )


class SQLiteRiskStateStore:
    """Persist sticky loss controls through the shared SQLite boundary."""

    def __init__(
        self,
        path: Path,
        *,
        profile_hash: str,
        max_daily_loss: Decimal,
        max_drawdown_from_peak: Decimal,
    ) -> None:
        _require_hash(profile_hash, "profile_hash")
        _require_positive(max_daily_loss, "max_daily_loss")
        _require_positive(max_drawdown_from_peak, "max_drawdown_from_peak")
        if max_drawdown_from_peak > 1:
            raise ValueError("max_drawdown_from_peak must be no greater than one")
        self._database = SQLiteDatabase(path, RISK_STATE_MIGRATIONS)
        self._profile_hash = profile_hash
        self._max_daily_loss = max_daily_loss
        self._max_drawdown_from_peak = max_drawdown_from_peak

    def migrate(self) -> tuple[int, ...]:
        return self._database.migrate()

    def initialize(
        self,
        *,
        scope_id: str,
        session_id: str,
        session_start_equity: Decimal,
        high_water_equity: Decimal,
        reconciliation_id: str,
        recorded_at_utc: datetime,
    ) -> RiskState:
        _require_identity(reconciliation_id, "reconciliation_id")
        state = RiskState(
            scope_id=scope_id,
            session_id=session_id,
            session_start_equity=session_start_equity,
            current_risk_equity=session_start_equity,
            high_water_equity=high_water_equity,
            net_external_flow=Decimal(0),
            halt_state=RiskHaltState.CLEAR,
            halt_reason=None,
            revision=1,
            updated_at_utc=recorded_at_utc,
        )
        state = self._with_halt(state, state, reset_daily_loss=False)
        try:
            with self._database.transaction() as transaction:
                transaction.execute(
                    """
                    INSERT INTO risk_state_current (
                        scope_id, session_id, session_start_equity,
                        current_risk_equity, high_water_equity, net_external_flow,
                        halt_state, halt_reason, revision, updated_at_utc
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    self._state_parameters(state),
                )
                transaction.execute(
                    """
                    INSERT INTO risk_state_profiles (scope_id, profile_hash)
                    VALUES (?, ?)
                    """,
                    (scope_id, self._profile_hash),
                )
                self._insert_event(
                    transaction,
                    state,
                    "INITIALIZED",
                    reconciliation_id=reconciliation_id,
                )
        except sqlite3.IntegrityError as error:
            raise RiskStateConflictError("durable risk scope is already initialized") from error
        return state

    def load(self, scope_id: str) -> RiskState:
        _require_identity(scope_id, "scope_id")
        with self._database.transaction() as transaction:
            return self._load(transaction, scope_id)

    def record_equity(
        self,
        scope_id: str,
        current_risk_equity: Decimal,
        recorded_at_utc: datetime,
    ) -> RiskState:
        _require_identity(scope_id, "scope_id")
        _require_positive(current_risk_equity, "current_risk_equity")
        recorded_at_utc = ensure_utc(recorded_at_utc, "recorded_at_utc")
        with self._database.transaction() as transaction:
            previous = self._load(transaction, scope_id)
            self._require_open_session(transaction, previous)
            self._require_later_time(previous, recorded_at_utc)
            state = self._assess_equity(previous, current_risk_equity, recorded_at_utc)
            self._replace_current(transaction, state)
            self._insert_event(transaction, state, "EQUITY_MARK")
        return state

    def record_capital_flow(
        self,
        scope_id: str,
        *,
        flow_id: str,
        amount: Decimal,
        current_risk_equity: Decimal,
        reconciliation_id: str,
        recorded_at_utc: datetime,
    ) -> RiskState:
        """Record one reconciled signed deposit or withdrawal exactly once."""

        _require_identity(scope_id, "scope_id")
        _require_identity(flow_id, "flow_id")
        _require_identity(reconciliation_id, "reconciliation_id")
        if not amount.is_finite() or amount == 0:
            raise ValueError("amount must be finite and nonzero")
        _require_positive(current_risk_equity, "current_risk_equity")
        recorded_at_utc = ensure_utc(recorded_at_utc, "recorded_at_utc")
        with self._database.transaction() as transaction:
            previous = self._load(transaction, scope_id)
            existing = transaction.fetch_one(
                """
                  SELECT session_id, amount, current_risk_equity,
                      reconciliation_id, occurred_at_utc
                FROM risk_capital_flows
                WHERE scope_id = ? AND flow_id = ?
                """,
                (scope_id, flow_id),
            )
            expected = (
                _decimal_text(amount),
                _decimal_text(current_risk_equity),
                reconciliation_id,
                _timestamp_text(recorded_at_utc),
            )
            if existing is not None:
                if existing[1:] == expected:
                    return previous
                raise RiskStateConflictError("capital-flow identity has conflicting facts")
            self._require_open_session(transaction, previous)
            self._require_later_time(previous, recorded_at_utc)
            adjusted_high_water = previous.high_water_equity + amount
            _require_positive(adjusted_high_water, "capital-flow-adjusted high_water_equity")
            candidate = RiskState(
                scope_id=previous.scope_id,
                session_id=previous.session_id,
                session_start_equity=previous.session_start_equity,
                current_risk_equity=current_risk_equity,
                high_water_equity=adjusted_high_water,
                net_external_flow=previous.net_external_flow + amount,
                halt_state=previous.halt_state,
                halt_reason=previous.halt_reason,
                revision=previous.revision + 1,
                updated_at_utc=recorded_at_utc,
            )
            state = self._with_halt(candidate, previous, reset_daily_loss=False)
            transaction.execute(
                """
                INSERT INTO risk_capital_flows (
                    scope_id, flow_id, session_id, amount,
                    current_risk_equity, reconciliation_id, occurred_at_utc
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    scope_id,
                    flow_id,
                    state.session_id,
                    _decimal_text(amount),
                    _decimal_text(current_risk_equity),
                    reconciliation_id,
                    _timestamp_text(recorded_at_utc),
                ),
            )
            self._replace_current(transaction, state)
            self._insert_event(
                transaction,
                state,
                "CAPITAL_FLOW",
                flow_id=flow_id,
                flow_amount=amount,
                reconciliation_id=reconciliation_id,
            )
        return state

    def close_session(
        self,
        scope_id: str,
        *,
        current_risk_equity: Decimal,
        reconciliation_id: str,
        recorded_at_utc: datetime,
    ) -> RiskState:
        """Persist one reconciled close and advance high water when justified."""

        _require_identity(scope_id, "scope_id")
        _require_identity(reconciliation_id, "reconciliation_id")
        _require_positive(current_risk_equity, "current_risk_equity")
        recorded_at_utc = ensure_utc(recorded_at_utc, "recorded_at_utc")
        with self._database.transaction() as transaction:
            previous = self._load(transaction, scope_id)
            self._require_open_session(transaction, previous)
            self._require_later_time(previous, recorded_at_utc)
            assessed = self._assess_equity(previous, current_risk_equity, recorded_at_utc)
            state = RiskState(
                scope_id=assessed.scope_id,
                session_id=assessed.session_id,
                session_start_equity=assessed.session_start_equity,
                current_risk_equity=assessed.current_risk_equity,
                high_water_equity=max(
                    assessed.high_water_equity,
                    assessed.current_risk_equity,
                ),
                net_external_flow=assessed.net_external_flow,
                halt_state=assessed.halt_state,
                halt_reason=assessed.halt_reason,
                revision=assessed.revision,
                updated_at_utc=assessed.updated_at_utc,
            )
            self._replace_current(transaction, state)
            self._insert_event(
                transaction,
                state,
                "SESSION_CLOSED",
                reconciliation_id=reconciliation_id,
            )
        return state

    def start_session(
        self,
        scope_id: str,
        *,
        session_id: str,
        session_start_equity: Decimal,
        reconciliation_id: str,
        recorded_at_utc: datetime,
        opening_flow_id: str | None = None,
        opening_external_flow: Decimal = Decimal(0),
    ) -> RiskState:
        """Start a unique session with any documented between-session flow."""

        _require_identity(scope_id, "scope_id")
        _require_identity(session_id, "session_id")
        _require_identity(reconciliation_id, "reconciliation_id")
        _require_positive(session_start_equity, "session_start_equity")
        if not opening_external_flow.is_finite():
            raise ValueError("opening_external_flow must be finite")
        if opening_external_flow == 0 and opening_flow_id is not None:
            raise ValueError("opening_flow_id requires a nonzero opening_external_flow")
        if opening_external_flow != 0:
            if opening_flow_id is None:
                raise ValueError("nonzero opening_external_flow requires opening_flow_id")
            _require_identity(opening_flow_id, "opening_flow_id")
        recorded_at_utc = ensure_utc(recorded_at_utc, "recorded_at_utc")
        with self._database.transaction() as transaction:
            previous = self._load(transaction, scope_id)
            if not self._session_is_closed(transaction, previous):
                raise RiskStateConflictError("current session must be closed before a new one")
            existing_session = transaction.fetch_one(
                """
                SELECT 1 FROM risk_state_events
                WHERE scope_id = ? AND session_id = ?
                LIMIT 1
                """,
                (scope_id, session_id),
            )
            if existing_session is not None:
                raise RiskStateConflictError("session identity has already been used")
            if opening_flow_id is not None:
                existing_flow = transaction.fetch_one(
                    """
                    SELECT 1 FROM risk_capital_flows
                    WHERE scope_id = ? AND flow_id = ?
                    """,
                    (scope_id, opening_flow_id),
                )
                if existing_flow is not None:
                    raise RiskStateConflictError("opening flow identity has already been used")
            self._require_later_time(previous, recorded_at_utc)
            adjusted_high_water = previous.high_water_equity + opening_external_flow
            _require_positive(adjusted_high_water, "opening-flow-adjusted high_water_equity")
            candidate = RiskState(
                scope_id=previous.scope_id,
                session_id=session_id,
                session_start_equity=session_start_equity,
                current_risk_equity=session_start_equity,
                high_water_equity=adjusted_high_water,
                net_external_flow=Decimal(0),
                halt_state=previous.halt_state,
                halt_reason=previous.halt_reason,
                revision=previous.revision + 1,
                updated_at_utc=recorded_at_utc,
            )
            state = self._with_halt(candidate, previous, reset_daily_loss=True)
            if opening_flow_id is not None:
                transaction.execute(
                    """
                    INSERT INTO risk_capital_flows (
                        scope_id, flow_id, session_id, amount,
                        current_risk_equity, reconciliation_id, occurred_at_utc
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        scope_id,
                        opening_flow_id,
                        session_id,
                        _decimal_text(opening_external_flow),
                        _decimal_text(session_start_equity),
                        reconciliation_id,
                        _timestamp_text(recorded_at_utc),
                    ),
                )
            self._replace_current(transaction, state)
            self._insert_event(
                transaction,
                state,
                "SESSION_STARTED",
                flow_id=opening_flow_id,
                flow_amount=(
                    None if opening_flow_id is None else opening_external_flow
                ),
                reconciliation_id=reconciliation_id,
            )
        return state

    def set_hard_halt(
        self,
        scope_id: str,
        *,
        reason: RiskReason,
        recorded_at_utc: datetime,
    ) -> RiskState:
        """Persist a hard halt that no API in this task can clear."""

        _require_identity(scope_id, "scope_id")
        if reason in (RiskReason.APPROVED, RiskReason.DAILY_LOSS):
            raise ValueError("hard halt requires a non-daily rejection reason")
        recorded_at_utc = ensure_utc(recorded_at_utc, "recorded_at_utc")
        with self._database.transaction() as transaction:
            previous = self._load(transaction, scope_id)
            self._require_later_time(previous, recorded_at_utc)
            state = RiskState(
                scope_id=previous.scope_id,
                session_id=previous.session_id,
                session_start_equity=previous.session_start_equity,
                current_risk_equity=previous.current_risk_equity,
                high_water_equity=previous.high_water_equity,
                net_external_flow=previous.net_external_flow,
                halt_state=RiskHaltState.HARD_HALTED,
                halt_reason=(
                    previous.halt_reason
                    if previous.halt_state is RiskHaltState.HARD_HALTED
                    else reason
                ),
                revision=previous.revision + 1,
                updated_at_utc=recorded_at_utc,
            )
            self._replace_current(transaction, state)
            self._insert_event(transaction, state, "HARD_HALT")
        return state

    def _assess_equity(
        self,
        previous: RiskState,
        current_risk_equity: Decimal,
        recorded_at_utc: datetime,
    ) -> RiskState:
        candidate = RiskState(
            scope_id=previous.scope_id,
            session_id=previous.session_id,
            session_start_equity=previous.session_start_equity,
            current_risk_equity=current_risk_equity,
            high_water_equity=previous.high_water_equity,
            net_external_flow=previous.net_external_flow,
            halt_state=previous.halt_state,
            halt_reason=previous.halt_reason,
            revision=previous.revision + 1,
            updated_at_utc=recorded_at_utc,
        )
        return self._with_halt(candidate, previous, reset_daily_loss=False)

    def _with_halt(
        self,
        candidate: RiskState,
        previous: RiskState,
        *,
        reset_daily_loss: bool,
    ) -> RiskState:
        if previous.halt_state is RiskHaltState.HARD_HALTED:
            halt_state = RiskHaltState.HARD_HALTED
            halt_reason = previous.halt_reason
        elif candidate.drawdown >= self._max_drawdown_from_peak:
            halt_state = RiskHaltState.HARD_HALTED
            halt_reason = RiskReason.DRAWDOWN
        elif (
            (previous.halt_state is RiskHaltState.LOSS_HALTED and not reset_daily_loss)
            or candidate.daily_loss >= self._max_daily_loss
        ):
            halt_state = RiskHaltState.LOSS_HALTED
            halt_reason = RiskReason.DAILY_LOSS
        else:
            halt_state = RiskHaltState.CLEAR
            halt_reason = None
        return RiskState(
            scope_id=candidate.scope_id,
            session_id=candidate.session_id,
            session_start_equity=candidate.session_start_equity,
            current_risk_equity=candidate.current_risk_equity,
            high_water_equity=candidate.high_water_equity,
            net_external_flow=candidate.net_external_flow,
            halt_state=halt_state,
            halt_reason=halt_reason,
            revision=candidate.revision,
            updated_at_utc=candidate.updated_at_utc,
        )

    @staticmethod
    def _require_later_time(previous: RiskState, recorded_at_utc: datetime) -> None:
        if recorded_at_utc <= previous.updated_at_utc:
            raise RiskStateError("durable risk events must advance event time")

    def _require_open_session(
        self,
        transaction: SQLiteTransaction,
        state: RiskState,
    ) -> None:
        if self._session_is_closed(transaction, state):
            raise RiskStateConflictError("closed session cannot accept another event")

    @staticmethod
    def _session_is_closed(
        transaction: SQLiteTransaction,
        state: RiskState,
    ) -> bool:
        row = transaction.fetch_one(
            """
            SELECT 1 FROM risk_state_events
            WHERE scope_id = ? AND session_id = ? AND event_type = 'SESSION_CLOSED'
            LIMIT 1
            """,
            (state.scope_id, state.session_id),
        )
        return row is not None

    def _load(self, transaction: SQLiteTransaction, scope_id: str) -> RiskState:
        row = transaction.fetch_one(
            """
            SELECT scope_id, session_id, session_start_equity,
                   current_risk_equity, high_water_equity, net_external_flow,
                   halt_state, halt_reason, revision, updated_at_utc
            FROM risk_state_current
            WHERE scope_id = ?
            """,
            (scope_id,),
        )
        if row is None:
            raise RiskStateNotFoundError("durable risk state is missing")
        profile_row = transaction.fetch_one(
            "SELECT profile_hash FROM risk_state_profiles WHERE scope_id = ?",
            (scope_id,),
        )
        if profile_row != (self._profile_hash,):
            raise RiskStateConflictError("durable risk state uses a different risk profile")
        try:
            halt_reason = None if row[7] is None else RiskReason(str(row[7]))
            state = RiskState(
                scope_id=str(row[0]),
                session_id=str(row[1]),
                session_start_equity=Decimal(str(row[2])),
                current_risk_equity=Decimal(str(row[3])),
                high_water_equity=Decimal(str(row[4])),
                net_external_flow=Decimal(str(row[5])),
                halt_state=RiskHaltState(str(row[6])),
                halt_reason=halt_reason,
                revision=int(str(row[8])),
                updated_at_utc=datetime.fromisoformat(str(row[9]).replace("Z", "+00:00")),
            )
        except (ArithmeticError, TypeError, ValueError) as error:
            raise RiskStateError("durable risk state is invalid") from error
        events = transaction.fetch_all(
            """
            SELECT scope_id, revision, event_type, session_id,
                   session_start_equity, current_risk_equity,
                   net_external_flow, high_water_equity, halt_state,
                   halt_reason, flow_id, flow_amount, reconciliation_id,
                   occurred_at_utc, previous_event_hash, event_hash
            FROM risk_state_events
            WHERE scope_id = ?
            ORDER BY revision
            """,
            (state.scope_id,),
        )
        if len(events) != state.revision:
            raise RiskStateError("durable risk event history is not contiguous")
        previous_event_hash: str | None = None
        for expected_revision, event in enumerate(events, start=1):
            if event[0] != state.scope_id or event[1] != expected_revision:
                raise RiskStateError("durable risk event history is not contiguous")
            event_values = event[:14]
            if (
                event[14] != previous_event_hash
                or event[15] != _event_hash(previous_event_hash, event_values)
            ):
                raise RiskStateError("durable risk event hash chain is invalid")
            previous_event_hash = str(event[15])
        flow_summary = transaction.fetch_one(
            """
            SELECT
                (SELECT COUNT(*) FROM risk_capital_flows WHERE scope_id = ?),
                (SELECT COUNT(*) FROM risk_state_events
                 WHERE scope_id = ? AND flow_id IS NOT NULL),
                (SELECT COUNT(*)
                 FROM risk_state_events AS event
                 JOIN risk_capital_flows AS flow
                   ON flow.scope_id = event.scope_id
                  AND flow.flow_id = event.flow_id
                  AND flow.session_id = event.session_id
                  AND flow.amount = event.flow_amount
                  AND flow.current_risk_equity = event.current_risk_equity
                  AND flow.reconciliation_id = event.reconciliation_id
                  AND flow.occurred_at_utc = event.occurred_at_utc
                 WHERE event.scope_id = ?)
            """,
            (state.scope_id, state.scope_id, state.scope_id),
        )
        if flow_summary is None or len(set(flow_summary)) != 1:
            raise RiskStateError("capital-flow ledger disagrees with durable events")
        latest_event = events[-1]
        expected_event = (
            state.session_id,
            _decimal_text(state.session_start_equity),
            _decimal_text(state.current_risk_equity),
            _decimal_text(state.high_water_equity),
            _decimal_text(state.net_external_flow),
            state.halt_state.value,
            None if state.halt_reason is None else state.halt_reason.value,
            _timestamp_text(state.updated_at_utc),
        )
        actual_event = (
            latest_event[3],
            latest_event[4],
            latest_event[5],
            latest_event[7],
            latest_event[6],
            latest_event[8],
            latest_event[9],
            latest_event[13],
        )
        if actual_event != expected_event:
            raise RiskStateError("current risk state disagrees with durable event history")
        return state

    def _replace_current(
        self,
        transaction: SQLiteTransaction,
        state: RiskState,
    ) -> None:
        transaction.execute(
            """
            UPDATE risk_state_current
            SET session_id = ?, session_start_equity = ?,
                current_risk_equity = ?, high_water_equity = ?,
                net_external_flow = ?, halt_state = ?, halt_reason = ?,
                revision = ?, updated_at_utc = ?
            WHERE scope_id = ?
            """,
            (
                state.session_id,
                _decimal_text(state.session_start_equity),
                _decimal_text(state.current_risk_equity),
                _decimal_text(state.high_water_equity),
                _decimal_text(state.net_external_flow),
                state.halt_state.value,
                None if state.halt_reason is None else state.halt_reason.value,
                state.revision,
                _timestamp_text(state.updated_at_utc),
                state.scope_id,
            ),
        )

    @staticmethod
    def _state_parameters(state: RiskState) -> tuple[RiskStateParameter, ...]:
        return (
            state.scope_id,
            state.session_id,
            _decimal_text(state.session_start_equity),
            _decimal_text(state.current_risk_equity),
            _decimal_text(state.high_water_equity),
            _decimal_text(state.net_external_flow),
            state.halt_state.value,
            None if state.halt_reason is None else state.halt_reason.value,
            state.revision,
            _timestamp_text(state.updated_at_utc),
        )

    def _insert_event(
        self,
        transaction: SQLiteTransaction,
        state: RiskState,
        event_type: str,
        *,
        flow_id: str | None = None,
        flow_amount: Decimal | None = None,
        reconciliation_id: str | None = None,
    ) -> None:
        previous_event_hash: str | None = None
        if state.revision > 1:
            previous_row = transaction.fetch_one(
                """
                SELECT event_hash FROM risk_state_events
                WHERE scope_id = ? AND revision = ?
                """,
                (state.scope_id, state.revision - 1),
            )
            if previous_row is None:
                raise RiskStateError("previous durable risk event is missing")
            previous_event_hash = str(previous_row[0])
        event_values: tuple[RiskStateParameter, ...] = (
            state.scope_id,
            state.revision,
            event_type,
            state.session_id,
            _decimal_text(state.session_start_equity),
            _decimal_text(state.current_risk_equity),
            _decimal_text(state.net_external_flow),
            _decimal_text(state.high_water_equity),
            state.halt_state.value,
            None if state.halt_reason is None else state.halt_reason.value,
            flow_id,
            None if flow_amount is None else _decimal_text(flow_amount),
            reconciliation_id,
            _timestamp_text(state.updated_at_utc),
        )
        transaction.execute(
            """
            INSERT INTO risk_state_events (
                scope_id, revision, event_type, session_id,
                session_start_equity, current_risk_equity,
                net_external_flow, high_water_equity,
                halt_state, halt_reason, flow_id, flow_amount,
                reconciliation_id, occurred_at_utc,
                previous_event_hash, event_hash
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (*event_values, previous_event_hash, _event_hash(previous_event_hash, event_values)),
        )