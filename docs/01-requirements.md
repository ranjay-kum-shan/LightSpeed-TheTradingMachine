# Trading Bot Requirements Specification

<details open>
<summary><b>Contents</b></summary>

- [Purpose](#purpose)
- [Product Boundary](#product-boundary)
- [Users and Operating Modes](#users-and-operating-modes)
- [Functional Requirements](#functional-requirements)
  - [Market Data](#market-data)
  - [Backtesting](#backtesting)
  - [Strategy Research](#strategy-research)
  - [Risk Control](#risk-control)
  - [Broker Execution](#broker-execution)
  - [State and Reconciliation](#state-and-reconciliation)
  - [Audit and Reporting](#audit-and-reporting)
- [Nonfunctional Requirements](#nonfunctional-requirements)
  - [Safety and Reliability](#safety-and-reliability)
  - [Reproducibility](#reproducibility)
  - [Security](#security)
  - [Performance](#performance)
  - [Maintainability](#maintainability)
- [Constraints and Assumptions](#constraints-and-assumptions)
- [Acceptance Outcomes](#acceptance-outcomes)
- [Requirements Change Control](#requirements-change-control)
- [Open Decisions](#open-decisions)

</details>

---

**Version:** 1.0  
**Date:** 30 August 2026  
**Status:** Baseline draft  
**Authority:** [Project Charter](../CHARTER.md)

## Purpose

This specification converts the reviewed trading-system plan into testable product requirements. It defines what the first complete system must do without prescribing every class or function.

The words **must**, **should**, and **may** are normative:

- **Must** means required for the applicable stage gate.
- **Should** means expected unless a decision record explains the exception.
- **May** means optional and must not delay a gate.

## Product Boundary

The initial product is a single-owner, single-process Python system for liquid US-listed ETFs using daily bars. It covers historical data, deterministic backtesting, disciplined research, hard risk controls, Alpaca paper execution, state recovery, reconciliation, and audit reporting.

The first release does not include live trading, leverage, shorting, derivatives, intraday strategies, machine learning, multi-broker routing, or distributed services. Live support is a later, separately approved operating mode and not an implicit extension of paper trading.

## Users and Operating Modes

| Actor or mode | Definition | Permissions |
|---|---|---|
| Owner-researcher | The sole person who configures, runs, reviews, and approves the system | Research, paper operation, approvals, incident response |
| Historical data vendor | External source of bars, actions, and calendar inputs | Read-only inbound data |
| Paper broker | External authority for paper cash, positions, orders, and fills | Paper orders only |
| `BACKTEST` | Offline deterministic simulation | No network broker access |
| `PAPER` | Broker-connected simulated trading | Paper endpoint and paper credentials only |
| `RECOVERY` | Startup or reconciliation-repair mode | Read broker state; cancel only under approved recovery policy; no new strategy orders |
| `HALTED` | Fail-closed mode | No new or replacement orders; approved cancel and alert actions only |
| `LIVE` | Future real-money mode | Prohibited until the charter and rollout gates are explicitly approved |

Mode selection must be explicit. Missing, invalid, or conflicting mode configuration must resolve to `HALTED`, never to `PAPER` or `LIVE`.

## Functional Requirements

### Market Data

| ID | Requirement | Acceptance evidence |
|---|---|---|
| DATA-001 | The system must ingest raw and adjusted daily OHLCV bars for an allowlisted symbol and requested date range. | A build for the reference ETF produces a schema-valid Parquet snapshot. |
| DATA-002 | The system must use an exchange calendar, not weekday arithmetic, for expected sessions. | Holiday and half-day fixtures pass. |
| DATA-003 | Every internal timestamp must be timezone-aware and normalized to UTC while retaining exchange-session identity. | Naive timestamps are rejected. |
| DATA-004 | Every immutable dataset snapshot must record provider, retrieval time, request parameters, schema version, content hash, and corporate-action treatment. | Manifest is present and hash verification passes. |
| DATA-005 | All twelve validation rules in the data specification must fail the build when violated. | One negative fixture per rule fails with a stable error code. |
| DATA-006 | Re-pulling a historical window with changed content must create a new snapshot and a revision alert; it must not overwrite prior data. | Revision simulation preserves both hashes. |
| DATA-007 | The system must detect stale or incomplete current-session data before signal evaluation. | A stale-bar fixture moves the session to `HALTED`. |

### Backtesting

| ID | Requirement | Acceptance evidence |
|---|---|---|
| BT-001 | A signal based on bar `t` must not fill before bar `t+1` open. | A same-bar fill attempt is rejected by a temporal-invariant test. |
| BT-002 | The engine must process events in deterministic timestamp and tie-break order. | Repeated runs produce byte-identical canonical results. |
| BT-003 | Costs must be explicit and required: spread, commission, slippage, financing, borrow, tax or fee treatment, and FX conversion where applicable. | A missing applicable cost field fails configuration validation. |
| BT-004 | The simulator must support rejects, partial fills, cancels, cash, positions, and mark-to-market equity. | Scenario fixtures reconcile orders, fills, positions, cash, and PnL. |
| BT-005 | Results must separate in-sample and out-of-sample periods and report promotion metrics from concatenated out-of-sample returns only. | Report labels and metric inputs are asserted. |
| BT-006 | Every run must support one-times, two-times, and four-times cost sensitivity. | Report contains all three scenarios. |
| BT-007 | Benchmark, random-signal, shuffled-return, look-ahead, and zero-cost sanity scenarios must be available. | Expected behavior tests pass. |

### Strategy Research

| ID | Requirement | Acceptance evidence |
|---|---|---|
| RES-001 | Every candidate must have a pre-registered thesis, universe, parameters, periods, cost assumptions, and success threshold before results are generated. | Runner refuses an unregistered candidate ID. |
| RES-002 | Every attempted run, including failures and rejected ideas, must be logged automatically. | Trial count includes unsuccessful and non-promoted runs. |
| RES-003 | Parameter evaluation must retain the full tested surface, not only the best point. | Sensitivity artefact is attached to the candidate report. |
| RES-004 | Multiple-testing correction and Deflated Sharpe Ratio must use the honest trial count. | Promotion report shows trial count, method, and corrected result. |
| RES-005 | No candidate may be promoted unless every charter research threshold passes. | A single failed threshold yields `REJECTED`. |

### Risk Control

| ID | Requirement | Acceptance evidence |
|---|---|---|
| RISK-001 | Every order intent must pass all applicable hard limits immediately before broker submission. | One test per limit proves rejection and no adapter call. |
| RISK-002 | Risk checks must include order size, position size, gross and net exposure, leverage, order rate, daily loss, drawdown, open positions, percent of average daily volume, symbol allowlist, and session hours. | Configuration and test trace include each named check. |
| RISK-003 | Missing or stale inputs to a risk calculation must reject the order. | Stale price, equity, ADV, and position fixtures fail closed. |
| RISK-004 | Internal, operator-triggered, and independent heartbeat kill paths must be available and tested. | Each path reaches `HALTED` within its stated deadline. |
| RISK-005 | Risk limits may not be bypassed by strategy code or broker-adapter retries. | Architecture dependency test and retry scenario pass. |
| RISK-006 | Live risk configuration must require explicit owner-approved values and may not inherit paper defaults. | `LIVE` validation fails when any approval or value is absent. |

### Broker Execution

| ID | Requirement | Acceptance evidence |
|---|---|---|
| EXEC-001 | The adapter must target an allowlisted paper endpoint and verify the account identity and environment at startup. | Wrong endpoint or account mode halts before order submission. |
| EXEC-002 | Every logical order must have a deterministic unique client order ID used for idempotent retries. | Retry returns or adopts the original order and never creates a second logical order. |
| EXEC-003 | The system must represent accepted, rejected, partially filled, filled, pending-cancel, canceled, expired, and unknown order states. | State-transition contract tests pass. |
| EXEC-004 | Timeout or disconnect after submission must be treated as an unknown outcome and resolved by query, not blind resubmission. | Ambiguous-submit fixture produces one broker order. |
| EXEC-005 | Broker rate limits must be respected with bounded retry and jitter for retry-safe reads only. | Throttle fixture does not exceed configured request rate. |
| EXEC-006 | Strategy orders outside the configured session must be rejected locally. | Exchange calendar boundary tests pass. |

### State and Reconciliation

| ID | Requirement | Acceptance evidence |
|---|---|---|
| STATE-001 | Order intent must be durably recorded before external submission. | Crash-point test can identify and resolve an in-flight intent. |
| STATE-002 | On every startup, the broker must be queried and reconciled before strategy evaluation begins. | Startup remains in `RECOVERY` until reconciliation passes. |
| STATE-003 | Broker positions, cash, open orders, and fills must be compared with internal state using explicit tolerances. | Matching fixture passes; each mismatch type halts. |
| STATE-004 | A mismatch must halt new trading and alert; the system must not silently mutate internal state to hide it. | Reconciliation-break test preserves discrepancy evidence. |
| STATE-005 | Working orders from an earlier process must be adopted or canceled according to a documented policy. | Restart fixtures cover both approved paths. |
| STATE-006 | Strategy state must be durably persisted or deterministically reconstructable from immutable data. | Clean reconstruction matches pre-crash state. |

### Audit and Reporting

| ID | Requirement | Acceptance evidence |
|---|---|---|
| AUD-001 | Each decision log must include UTC time, run or session ID, strategy ID, code revision, configuration hash, data hash, inputs, decision, and reason code. | JSON schema validation passes. |
| AUD-002 | Each order and fill record must include broker and client identifiers, symbol, side, quantity, prices, fees, taxes, FX rate, and strategy ID where applicable. | Recordkeeping export contains required fields. |
| AUD-003 | A daily report must be emitted even when no trade occurs. | No-trade fixture produces a report with an explicit reason. |
| AUD-004 | Alerts must cover heartbeat loss, risk rejection, daily or drawdown halt, stale data, broker disconnect, and reconciliation break. | Alert-routing tests cover every event type. |
| AUD-005 | Reports must distinguish backtest, paper, and live evidence and must not merge their PnL curves. | Report schema and labels are validated. |

## Nonfunctional Requirements

### Safety and Reliability

| ID | Requirement | Target |
|---|---|---|
| NFR-SAFE-001 | Failure behavior | Fail closed on ambiguity, stale input, missing configuration, or broken reconciliation |
| NFR-SAFE-002 | Duplicate logical orders | Zero across retry and restart tests |
| NFR-REL-001 | Paper market-hours availability | At least 99% during the Stage 4 observation window |
| NFR-REL-002 | Reconciliation breaks | Zero unexplained breaks before promotion |
| NFR-REL-003 | Recovery exercises | At least five successful induced failures before paper promotion completes |

### Reproducibility

| ID | Requirement | Target |
|---|---|---|
| NFR-REP-001 | Canonical repeated output | Byte-identical for the same code, config, data, and seed |
| NFR-REP-002 | Input lineage | 100% of decision and result artefacts identify code, config, and data |
| NFR-REP-003 | Data mutability | Published snapshots are append-only and never overwritten |

### Security

| ID | Requirement | Target |
|---|---|---|
| NFR-SEC-001 | Secret exposure | Zero secrets in repository, logs, errors, reports, fixtures, or support bundles |
| NFR-SEC-002 | Credential privilege | Paper-only and minimum privilege for initial stages |
| NFR-SEC-003 | Dependency integrity | Locked versions, reviewed updates, and automated vulnerability checks |
| NFR-SEC-004 | Sensitive logging | Allowlisted fields with mandatory redaction tests |

### Performance

| ID | Requirement | Target |
|---|---|---|
| NFR-PERF-001 | Daily decision completion | Complete comfortably before the approved order window; initial target under 60 seconds for the allowlist |
| NFR-PERF-002 | Pre-trade risk evaluation | Initial target under 100 milliseconds locally, measured but not optimized prematurely |
| NFR-PERF-003 | Reference backtest | Initial target under 5 minutes for ten years of daily data and the Stage 1 universe |

Performance targets protect operating deadlines. They are not a reason to introduce a second language or distributed system without profiling evidence.

### Maintainability

| ID | Requirement | Target |
|---|---|---|
| NFR-MNT-001 | Direction of dependencies | Strategy depends on domain ports, never concrete broker or storage clients |
| NFR-MNT-002 | Configuration | Typed, schema-versioned, and validated at process start |
| NFR-MNT-003 | Behavioral change | Documentation and automated tests updated together |
| NFR-MNT-004 | Public contracts | Stable reason codes and schemas versioned explicitly |

## Constraints and Assumptions

- Python 3.12 or newer and a single process are the default through tiny-live operation.
- Parquet and DuckDB hold analytical data; SQLite may hold experiments and durable local state.
- The initial market is liquid US-listed ETFs and the initial strategy is long-only and unleveraged.
- The broker paper environment is authoritative after an order reaches it.
- Daily bars are complete only after the documented vendor publication time, not merely at exchange close.
- Free historical data may be unsuitable for broad cross-sectional claims because of survivorship and revision bias.
- UK legal, tax, account-eligibility, and market-data terms remain external constraints that require owner verification before live use.
- No requirement implies that a profitable strategy exists.

## Acceptance Outcomes

| Stage | Required outcome |
|---|---|
| Stage 0 | Charter decisions and loss boundaries are explicitly approved. |
| Stage 1 | One immutable dataset, one simple strategy, one deterministic backtest, one paper order, risk checks, kill paths, restart recovery, and reconciliation work end to end. |
| Stage 2 | Cost sensitivity, point-in-time limitations, walk-forward evaluation, deterministic replay, experiment logging, and backtester sanity tests are demonstrated. |
| Stage 3 | At least one pre-registered candidate passes every research promotion threshold, or the project records an honest no-promotion result. |
| Stage 4 | Three qualifying months of unattended paper operation meet all paper gates. |
| Stage 5 | Separately approved tiny-live operation meets six-month operational and statistical criteria. |

## Requirements Change Control

1. Assign every new requirement a stable category ID.
2. Record the reason, affected stage, safety impact, and acceptance evidence.
3. Update the architecture and the requirements traceability matrix where ownership changes.
4. Add or update a test before marking a behavioral requirement implemented.
5. Require owner approval for market, broker, instrument, leverage, live-capital, risk-limit, or promotion-threshold changes.
6. Never weaken a gate merely because current results fail it.

## Open Decisions

| Decision | Owner | Needed by | Blocking effect |
|---|---|---|---|
| Approve weekly time budget and initial market | Owner | Stage 0 completion | Blocks Stage 0 |
| Choose initial ETF and data provider | Owner with implementation evidence | Data implementation | Blocks reference dataset |
| Confirm Alpaca UK account eligibility and terms | Owner | Broker integration | Blocks paper broker acceptance |
| Approve base reporting currency | Owner | Cost and reporting implementation | Blocks canonical PnL reporting |
| Define paper reference equity and proportional limits | Owner | Paper configuration | Blocks realistic risk profile |
| Set loss-tolerant live capital and all live limits | Owner | Stage 5 planning | Blocks `LIVE` mode |
| Confirm tax treatment and record retention with a professional | Owner | Stage 5 planning | Blocks `LIVE` mode |
