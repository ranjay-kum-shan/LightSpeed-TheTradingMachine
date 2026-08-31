# Master Task Tracker

<details open>
<summary><b>Contents</b></summary>

- [Control Panel](#control-panel)
- [How This Tracker Works](#how-this-tracker-works)
- [Status Model](#status-model)
- [Current Baseline](#current-baseline)
  - [Completed Subtasks](#completed-subtasks)
- [Parallelization Map](#parallelization-map)
- [Active Claims](#active-claims)
- [Integration Queue](#integration-queue)
- [Blockers and Decisions](#blockers-and-decisions)
- [Task Register](#task-register)
  - [Stage Zero and Coordination](#stage-zero-and-coordination)
  - [Work Package One Foundation](#work-package-one-foundation)
  - [Work Package Two Risk and Control](#work-package-two-risk-and-control)
  - [Work Package Three Data](#work-package-three-data)
  - [Work Package Four Backtesting](#work-package-four-backtesting)
  - [Work Package Five Execution](#work-package-five-execution)
  - [Work Package Six Recovery and Operations](#work-package-six-recovery-and-operations)
  - [Later Stages](#later-stages)
- [Completed Work](#completed-work)
- [Evidence Ledger](#evidence-ledger)
- [Coordinator Update Checklist](#coordinator-update-checklist)
- [Change Log](#change-log)

</details>

---

**Tracker version:** 1.0  
**Last reconciled:** 31 August 2026  
**Coordinator:** `GitHub Copilot (sequential session only)`  
**Current authorization:** `PAPER_ONLY`  
**Current gate:** Stage 0 not passed  
**Requirement state:** 58 `SPECIFIED`, 3 `IMPLEMENTED`, 0 `VERIFIED`  
**Parallel execution state:** `BASELINE_SYNCED_COORDINATOR_APPOINTMENT_REQUIRED`

## Control Panel

| Measure | Current value | Authority |
| --- | --- | --- |
| Total registered tasks | 41 | Task Register below |
| `DONE` | 8 | Completed Work below |
| `IN_PROGRESS` | 0 | Active Claims below |
| `READY` | 5 | Parallelization Map below |
| `BLOCKED` | 9 | Blockers and Decisions below |
| `BACKLOG` | 18 | Dependency sequencing below |
| Active claims | 0 | `coordination/claims/` plus Active Claims below |
| Items in review | 1 | Integration Queue below |
| Open incidents | 0 | Incident records |
| Baseline commit | `4ba5111d53c33343112d97af1c492b7ac087dee4` | Reviewed and integrated baseline |
| Git remote | `https://github.com/ranjay-kum-shan/LightSpeed-TheTradingMachine.git` | Git configuration |

This file is the master task index, not the requirement authority. Requirement
status belongs to the [Requirements Traceability Matrix](docs/14-requirements-traceability.md),
and safety constraints belong to [CHARTER.md](CHARTER.md). A task marked `DONE`
does not make a requirement `VERIFIED`.

## How This Tracker Works

1. The coordinator is the only role that edits task status, summary counts,
   Active Claims, Integration Queue, Completed Work, or the Change Log here.
2. A worker selects only a `READY` task and creates a proposed claim from the
   task-claim template under `coordination/claims/TB-NNNN.md`.
3. The coordinator checks dependencies and write-scope overlap, approves the
   claim, records it here, and changes the task to `CLAIMED`.
4. The worker creates `coordination/tasks/TB-NNNN.md` from the task-record
   template and works on branch `task/TB-NNNN-short-name` from the recorded base
   commit.
5. Workers update only their task record, claim heartbeat, and files inside the
   approved write scope. They do not edit this master tracker.
6. When acceptance evidence is ready, the worker changes the task record to
   `IN_REVIEW` and creates `coordination/handoffs/TB-NNNN.md`.
7. A reviewer reruns the evidence. The coordinator alone marks the master task
   `DONE`, updates traceability where justified, and releases the claim.

The full process is defined in the [Parallel Work Protocol](docs/15-parallel-work-protocol.md).

## Status Model

| Status | Meaning | Who may set it |
| --- | --- | --- |
| `BACKLOG` | Defined, but one or more internal dependencies are unfinished | Coordinator |
| `READY` | Dependencies are satisfied, acceptance is clear, and no external blocker exists | Coordinator |
| `CLAIMED` | One approved worker holds an active lease but has not started changes | Coordinator |
| `IN_PROGRESS` | The approved worker is implementing within the declared scope | Coordinator from worker update |
| `BLOCKED` | Progress requires an external decision, credential, provider, or unresolved incident | Coordinator |
| `IN_REVIEW` | Implementation and handoff are complete; independent validation is pending | Coordinator |
| `DONE` | Acceptance evidence passed and the coordinator closed the task | Coordinator only |
| `CANCELLED` | Work is intentionally stopped with rationale and evidence impact recorded | Coordinator only |

Allowed transitions are `BACKLOG -> READY -> CLAIMED -> IN_PROGRESS -> IN_REVIEW -> DONE`.
Any active state may move to `BLOCKED`; resolved blocked work returns to the
appropriate prior state. Reopened work moves from `DONE` to `IN_REVIEW` or
`IN_PROGRESS` with a new claim and a change-log entry.

## Current Baseline

- Local `main` tracks the personal repository and is synchronized with the
  collaboration baseline through commit `3fbc9a1`; the reviewed working baseline
  is now `4ba5111` and is not yet pushed.
- GitHub CLI is authenticated as `ranjay-kum-shan`; repository write permission
  and a normal fast-forward push were verified under the personal account.
- Parallel claims still require the project owner to appoint an ongoing
  coordinator. Until then one agent holds both the implementer and coordinator
  roles, so master-tracker edits appear inside worker commits; this is disclosed
  in each affected handoff.
- The uploadable tree contains source, configuration, documentation, and tests;
  generated environments and caches are absent.
- The last complete validation passed Ruff, strict mypy across 28 files, and 378
  tests at 100% statement and branch coverage.
- The implemented code covers fail-closed configuration, the configuration CLI,
  canonical order values, UTC time normalization with clock and exchange-calendar
  ports, canonical market-data schemas for instruments, bars, corporate actions,
  and dataset manifests, the pure risk engine, operator kill assessment, and
  atomic heartbeat health.
- `DATA-003`, `RISK-002`, and `NFR-MNT-004` are marked `IMPLEMENTED`. No
  requirement is marked `VERIFIED` and no stage gate has passed.
- No data ingestion, hashing, publication, broker adapter, credential,
  network-order path, or real-money capability exists.

### Completed Subtasks

#### TB-1001 - Repository and toolchain foundation

- [x] Create Python package metadata and `src/` layout.
- [x] Lock development and runtime dependencies with uv.
- [x] Configure Ruff, strict mypy, pytest, EditorConfig, and Git attributes.
- [x] Add a least-privilege Windows GitHub Actions workflow.
- [x] Remove generated artefacts and validate the exact Git upload candidate.

#### TB-1002 - Fail-closed configuration and CLI

- [x] Define explicit `BACKTEST`, `PAPER`, `RECOVERY`, and `HALTED` modes.
- [x] Reject missing, malformed, duplicate-key, unknown, and `LIVE` config.
- [x] Add a redacted `trading-bot config-check` command.
- [x] Cover valid and invalid configuration behavior with tests.

#### TB-2001 - Coherent pre-trade risk engine

- [x] Define immutable positions, pending orders, liquidity, limits, and snapshot.
- [x] Enforce every named hard limit with no capital-dependent defaults.
- [x] Include pending orders in projected exposure.
- [x] Prevent projected short positions and leverage above the profile.
- [x] Add boundary, stale-input, loss, drawdown, allowlist, and property tests.

#### TB-2002 - Operator kill and heartbeat primitives

- [x] Assess missing, present, and unreadable operator kill state fail-closed.
- [x] Write heartbeat records atomically.
- [x] Validate missing, malformed, stale, and future heartbeat records.
- [x] Keep automatic position flattening absent.

## Parallelization Map

These tasks can proceed concurrently only after `TB-0006` establishes a shared
baseline commit. Each row has a non-overlapping primary write scope. Changes to
shared exports, package metadata, CI, master documents, or cross-cutting schemas
must be handed to the coordinator for integration.

| Task | Lane | Primary write scope | Required coordination |
| --- | --- | --- | --- |
| TB-1005 | Audit | `src/trading_bot/audit/**`, matching tests | Do not log arbitrary config or SDK objects |
| TB-1006 | Storage | `src/trading_bot/storage/**`, matching tests | Own SQLite migrations and atomic persistence contracts |
| TB-2004 | Watchdog | `src/trading_bot/operations/watchdog.py`, matching tests | No broker calls; use a cancellation port and fake only |
| TB-2005 | Quality | Import-boundary and performance tests | Coordinate any production-code change separately |
| TB-3003 | Calendar data | `src/trading_bot/data/calendars/**`, matching tests | Build on the delivered `ExchangeCalendar` port; `src/trading_bot/data/__init__.py` is now shared |
| TB-5001 | Execution port | `src/trading_bot/execution/ports.py`, fakes, tests | No Alpaca SDK or credentials |

TB-1004 delivered its time contracts into `src/trading_bot/domain/time.py`,
`src/trading_bot/adapters/`, and `src/trading_bot/data/` rather than the
previously listed `src/trading_bot/time/**`, because the
[architecture module boundaries](docs/02-architecture.md) assign clocks to
`adapters` and calendars to `data`. TB-3003 builds real calendar data on the
delivered `ExchangeCalendar` port.

## Active Claims

| Task | Claimant | Branch or worktree | Write scope | Lease expires UTC | Last heartbeat UTC | State |
| --- | --- | --- | --- | --- | --- | --- |
| None | - | - | - | - | - | No active claims |

An entry here is a summary of an approved claim file, not a substitute for it.
If this table and a claim file disagree, stop work and ask the coordinator to
reconcile them before editing.

## Integration Queue

| Order | Task | Branch or PR | Reviewer | Validation status | Conflict notes | Decision |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | TB-1005 | `main` (sequential) | Independent review agent | Cycle one `CHANGES_REQUESTED` on two Critical redaction escapes; after remediation Ruff pass, strict mypy over 32 files, 543 tests, 100% statement and branch coverage, wheel built | New package; no shared file except the tracker | `PENDING_REVIEW` |

The coordinator orders integration by dependency and shared-file risk, not by
completion time. Downstream branches rebase or merge from the newly integrated
baseline and rerun affected validation.

## Blockers and Decisions

| Blocker | Affected tasks | Owner | Resolution evidence | Status |
| --- | --- | --- | --- | --- |
| BLK-001 Stage 0 owner decisions are unsigned | TB-0001 through TB-0005 | Project owner | Signed charter rows and accepted decision records | `OPEN` |
| BLK-002 Personal GitHub authentication and baseline publication | TB-0006 | Project owner | Personal account authenticated; fast-forward push verified | `CLOSED` |
| BLK-003 ETF and data provider are unselected | TB-3001 and TB-3004 | Project owner | Qualified provider and reference instrument decision | `OPEN` |
| BLK-004 Alpaca eligibility and terms are unconfirmed | TB-5003 | Project owner | Current account and API eligibility evidence | `OPEN` |
| BLK-005 Secret, alert, backup, and runtime providers are unselected | TB-0005 and TB-6003 | Project owner | Accepted provider decisions | `OPEN` |

Workers may prepare deterministic fakes where a task explicitly allows it, but
must not bypass an external blocker or introduce real credentials.

## Task Register

### Stage Zero and Coordination

| ID | Task | Requirements or decisions | Depends on | Status | Owner | Next acceptance boundary |
| --- | --- | --- | --- | --- | --- | --- |
| TB-0001 | Approve market, horizon, time budget, and base currency | DEC-011, DEC-016, DEC-017 | Owner decision | `BLOCKED` | Unassigned | Signed charter values |
| TB-0002 | Select reference ETF and market-data source | DATA-001, DEC-024 | TB-0001 | `BLOCKED` | Unassigned | Instrument decision and source qualification |
| TB-0003 | Confirm Alpaca paper eligibility and terms | EXEC-001, DEC-012 | Owner and broker | `BLOCKED` | Unassigned | Current eligibility evidence |
| TB-0004 | Set paper reference equity and risk values | RISK-002 | TB-0001 | `BLOCKED` | Unassigned | Owner-approved paper profile |
| TB-0005 | Select secrets, alerts, backup, retention, and runtime paths | NFR-SEC-002, AUD-004 | Owner decisions | `BLOCKED` | Unassigned | Accepted operational provider records |
| TB-0006 | Establish approved baseline commit and collaboration remote | Coordination protocol | Personal GitHub push authentication | `DONE` | GitHub Copilot | EV-0010 |

### Work Package One Foundation

| ID | Task | Requirements | Depends on | Status | Owner | Next acceptance boundary |
| --- | --- | --- | --- | --- | --- | --- |
| TB-1001 | Repository, package, lockfile, quality tools, and CI | NFR-SEC-003, NFR-MNT-002 | None | `DONE` | Initial implementation | EV-0001 and EV-0002 |
| TB-1002 | Fail-closed runtime config and redacted CLI | NFR-SAFE-001, NFR-MNT-002, RISK-006 | TB-1001 | `DONE` | Initial implementation | Config and CLI tests pass |
| TB-1003 | Complete canonical domain values and reason-code registry | NFR-MNT-004 | TB-1002 | `DONE` | GitHub Copilot (sequential) | EV-0007 through EV-0009 |
| TB-1004 | UTC clock port and deterministic test clock | DATA-003, EXEC-006 | TB-1001 | `DONE` | GitHub Copilot (sequential) | EV-0012 and EV-0013 |
| TB-1005 | Structured audit schema and redaction boundary | AUD-001, NFR-SEC-004 | TB-1002 | `IN_REVIEW` | GitHub Copilot (sequential) | EV-0023; awaiting review cycle two |
| TB-1006 | SQLite migrations, transaction boundary, and atomic storage | STATE-001, NFR-REP-002 | TB-1001 | `READY` | Unassigned | Replayable migration and commit-failure tests |

### Work Package Two Risk and Control

| ID | Task | Requirements | Depends on | Status | Owner | Next acceptance boundary |
| --- | --- | --- | --- | --- | --- | --- |
| TB-2001 | Coherent snapshot, projected exposure, and all hard limits | RISK-001, RISK-002, RISK-003 | TB-1002 | `DONE` | Initial implementation | RISK-002 marked implemented |
| TB-2002 | Operator kill assessment and atomic heartbeat health | RISK-004 | TB-1002 | `DONE` | Initial implementation | Primitive control tests pass |
| TB-2003 | Durable sticky halt, daily-loss, and drawdown state | RISK-004, NFR-SAFE-001 | TB-1006, TB-2001 | `BACKLOG` | Unassigned | Restart cannot clear a halt |
| TB-2004 | Independent watchdog policy, cancellation port, and fake | RISK-004, NFR-REL-003 | TB-2002 | `READY` | Unassigned | Stale heartbeat alerts and cancels known orders only |
| TB-2005 | Risk bypass, import-boundary, mutation, and latency checks | RISK-005, NFR-PERF-002 | TB-2001 | `READY` | Unassigned | No adapter path and risk p95 under target |

### Work Package Three Data

| ID | Task | Requirements | Depends on | Status | Owner | Next acceptance boundary |
| --- | --- | --- | --- | --- | --- | --- |
| TB-3001 | Qualify historical and current data providers | DATA-001, DATA-006 | TB-0002 | `BLOCKED` | Unassigned | Approved source qualification record |
| TB-3002 | Canonical instrument, bar, action, and manifest schemas | DATA-001, DATA-003, DATA-004 | TB-1003 | `DONE` | GitHub Copilot (sequential) | EV-0014 through EV-0019 |
| TB-3003 | Exchange calendar, holidays, half-days, and DST fixtures | DATA-002, DATA-003 | TB-1004 | `READY` | Unassigned | Calendar boundary suite passes |
| TB-3004 | Provider-specific availability and current-data freshness rule | DATA-007 | TB-3001, TB-3003 | `BLOCKED` | Unassigned | `available_at_utc` policy approved |
| TB-3005 | Implement DV-001 through DV-012 | DATA-005 | TB-3002, TB-3003 | `BACKLOG` | Unassigned | One isolated failing fixture per rule |
| TB-3006 | Immutable snapshots, canonical hashes, and revision detection | DATA-004, DATA-006, NFR-REP-003 | TB-3005 | `BACKLOG` | Unassigned | Stable unchanged pull and preserved revision |

### Work Package Four Backtesting

| ID | Task | Requirements | Depends on | Status | Owner | Next acceptance boundary |
| --- | --- | --- | --- | --- | --- | --- |
| TB-4001 | Deterministic event loop and next-session execution | BT-001, BT-002 | TB-3006 | `BACKLOG` | Unassigned | Same-bar fill rejected; replay identical |
| TB-4002 | Simulated broker and canonical order-state transitions | BT-004, EXEC-003 | TB-4001, TB-5001 | `BACKLOG` | Unassigned | Reject, partial, cancel, fill, and expiry fixtures |
| TB-4003 | Ledger, explicit costs, cash, actions, and marks | BT-003, BT-004, BT-006 | TB-3002, TB-4002 | `BACKLOG` | Unassigned | Accounting and cost identities pass |
| TB-4004 | Machinery-only moving-average strategy | BT-001 | TB-4001, TB-4003 | `BACKLOG` | Unassigned | End-to-end result with no promotion claim |
| TB-4005 | Canonical report and mandatory sanity suite | BT-002, BT-005, BT-007 | TB-4004 | `BACKLOG` | Unassigned | All negative controls and byte replay pass |

### Work Package Five Execution

| ID | Task | Requirements | Depends on | Status | Owner | Next acceptance boundary |
| --- | --- | --- | --- | --- | --- | --- |
| TB-5001 | Broker port and deterministic fake adapter | NFR-MNT-001 | Architecture contracts | `READY` | Unassigned | Reusable adapter contract suite starts green |
| TB-5002 | Durable intent journal and deterministic client order IDs | EXEC-002, STATE-001 | TB-1006, TB-5001 | `BACKLOG` | Unassigned | Retry and restart produce one logical ID |
| TB-5003 | Alpaca paper adapter and environment/account guard | EXEC-001 | TB-0003, TB-5001 | `BLOCKED` | Unassigned | Wrong endpoint/account submits nothing |
| TB-5004 | Unknown outcomes, partial fills, cancel races, and reconnect | EXEC-003 through EXEC-006 | TB-5002, TB-5003 | `BACKLOG` | Unassigned | Full adapter contract suite passes |
| TB-5005 | Startup reconciliation and recovery | STATE-002 through STATE-005 | TB-5002, TB-5004 | `BACKLOG` | Unassigned | Broker/internal domains reconcile before strategy |

### Work Package Six Recovery and Operations

| ID | Task | Requirements | Depends on | Status | Owner | Next acceptance boundary |
| --- | --- | --- | --- | --- | --- | --- |
| TB-6001 | Session orchestrator, recovery states, and single-writer lock | STATE-006, NFR-REL-001 | TB-5005 | `BACKLOG` | Unassigned | Startup cannot skip recovery |
| TB-6002 | Alert/report ports, daily report schema, and deterministic fakes | AUD-001, AUD-003, AUD-004 | TB-1005 | `BACKLOG` | Unassigned | No-trade and alert-routing tests pass |
| TB-6003 | Select and integrate real alert providers | AUD-004, NFR-SEC-002 | TB-0005, TB-6002 | `BLOCKED` | Unassigned | Two-channel canary delivery passes |
| TB-6004 | Backup, restore, release manifest, and rollback | NFR-REL-003, NFR-REP-002 | TB-1006, TB-6001 | `BACKLOG` | Unassigned | Isolated restore and state-forward rollback pass |
| TB-6005 | Crash injection and Stage 1 gate exercise | NFR-REL-003 | TB-2004, TB-6001 through TB-6004 | `BACKLOG` | Unassigned | Kill-and-recover bundle accepted |

### Later Stages

| ID | Task | Requirements | Depends on | Status | Owner | Next acceptance boundary |
| --- | --- | --- | --- | --- | --- | --- |
| TB-7001 | Honest backtesting, experiments, walk-forward, and statistics | Stage 2 requirements | TB-6005 | `BACKLOG` | Unassigned | Stage 2 gate bundle |
| TB-7002 | Pre-registered strategy research and promotion | RES-001 through RES-005 | TB-7001 | `BACKLOG` | Unassigned | One candidate passes or honest rejection recorded |
| TB-7003 | Three-month unattended paper observation | AUD-004, AUD-005, NFR-REL-001 through NFR-REL-003 | TB-7002 | `BACKLOG` | Unassigned | Stage 4 evidence bundle |

## Completed Work

| Task | Closed date | Acceptance evidence | Requirement effect |
| --- | --- | --- | --- |
| TB-1001 | 31 August 2026 | `pyproject.toml`, `uv.lock`, CI workflow, upload audit | No requirement promoted to verified |
| TB-1002 | 31 August 2026 | `tests/test_config.py`, `tests/test_cli.py` | Supports fail-closed controls |
| TB-2001 | 31 August 2026 | `tests/test_risk_engine.py` and EV-0001 | RISK-002 marked `IMPLEMENTED` |
| TB-2002 | 31 August 2026 | `tests/test_operations_controls.py` and EV-0001 | RISK-004 remains specified until watchdog integration |
| TB-1003 | 31 August 2026 | Independent approval, EV-0007, EV-0008, commit `84e869e` | NFR-MNT-004 marked `IMPLEMENTED` |
| TB-0006 | 31 August 2026 | Personal authentication, baseline adoption, and fast-forward push in EV-0010 | Parallel Git baseline established |
| TB-1004 | 31 August 2026 | Independent review reproduction in EV-0013 and worker evidence EV-0012 | DATA-003 marked `IMPLEMENTED`; EXEC-006 unchanged |
| TB-3002 | 31 August 2026 | Three independent review cycles closed by EV-0019 at commit `4ba5111` | No requirement promoted; DATA-001 and DATA-004 stay `SPECIFIED` pending TB-3005 and TB-3006 |

## Evidence Ledger

| Evidence | Date | Scope | Result | Reproducible command or record |
| --- | --- | --- | --- | --- |
| EV-0001 | 31 August 2026 | Python source quality | Ruff pass, strict mypy pass, 68 tests pass | Commands in `README.md` |
| EV-0002 | 31 August 2026 | Pre-coordination GitHub upload baseline | 52 files, no secrets/private paths, no ignored artefacts, ready | Upload audit summary in session history |
| EV-0003 | 31 August 2026 | Package build | Wheel and sdist built; wheel smoke test passed | `UV_LINK_MODE=copy uv build` plus clean install |
| EV-0004 | 31 August 2026 | Pre-coordination documentation integrity | 26 Markdown files with valid navigation and links | Repository documentation audit |
| EV-0005 | 31 August 2026 | Parallel coordination baseline | 41 unique tasks, dependency-consistent queue, coordination documents valid | Master/protocol/template validator |
| EV-0006 | 31 August 2026 | TB-1003 domain contracts | Ruff pass, strict mypy pass across 18 files, 77 tests pass | `coordination/handoffs/TB-1003.md` |
| EV-0007 | 31 August 2026 | TB-1003 compatibility repair | Distinct risk-only enum restored; Ruff and mypy pass; 79 tests pass; wheel contains contract modules | `coordination/handoffs/TB-1003.md` |
| EV-0008 | 31 August 2026 | TB-1003 independent re-review | `APPROVE`; cycle-one findings resolved; command reproduction unavailable | `coordination/handoffs/TB-1003.md` |
| EV-0009 | 31 August 2026 | TB-1003 local integration | Commit `84e869e27e9a5210fe3360494ace250530250a2e` created above remote baseline | Local Git history |
| EV-0010 | 31 August 2026 | Personal GitHub synchronization | Active personal account and admin permission verified; `main` synchronized through `2c0bf4d`; CI run 33379734390 passed | `coordination/handoffs/TB-0006.md` |
| EV-0011 | 31 August 2026 | Review remediation | `py.typed` marker shipped in wheel; supported range proven on Python 3.12 and 3.14; boundary-validator tests added; Ruff pass, strict mypy pass across 19 files, 156 tests pass at 100% statement and branch coverage | Commands in `README.md` |
| EV-0012 | 31 August 2026 | TB-1004 UTC clock and calendar ports | Ruff pass, strict mypy pass across 26 files, 211 tests pass at 100% statement and branch coverage; wheel contains the new time, clock, and calendar modules; unanchored `data/` ignore rule proven and repaired | `coordination/handoffs/TB-1004.md` |
| EV-0013 | 31 August 2026 | TB-1004 independent review reproduction | `APPROVE`; sync, Ruff, strict mypy over 26 files, 211 tests at 100% statement and branch coverage, wheel contents, and the ignore-rule repair all reproduced from a clean sync | `coordination/handoffs/TB-1004.md` |
| EV-0014 | 31 August 2026 | TB-3002 canonical data schemas | Ruff pass, strict mypy pass across 28 files, 316 tests pass at 100% statement and branch coverage; wheel contains `trading_bot/data/models.py`; the `DV-*` rule boundary is pinned by an explicit test | `coordination/handoffs/TB-3002.md` |
| EV-0015 | 31 August 2026 | TB-3002 independent review cycle one | `CHANGES_REQUESTED`; 0 Critical, 4 Major, 10 Minor; all declared gates reproduced; the `NORMALIZED` before `VALIDATING` boundary upheld, its stated discriminator rejected, and an undeclared master-tracker edit found | `coordination/handoffs/TB-3002.md` |
| EV-0016 | 31 August 2026 | TB-3002 remediation | Nine findings fixed in code and tests, five disclosed as records or follow-ups; Ruff pass, strict mypy pass across 28 files, 347 tests pass at 100% statement and branch coverage; wheel rebuilt | `coordination/handoffs/TB-3002.md` |
| EV-0017 | 31 August 2026 | TB-3002 independent review cycle two | `CHANGES_REQUESTED`; 0 Critical, 3 Major, 10 Minor; behavioural probes and mutation controls proved the cycle-one secret-guard fix was a net security regression and the rewritten boundary claim was false | `coordination/handoffs/TB-3002.md` |
| EV-0018 | 31 August 2026 | TB-3002 cycle-two remediation | Secret guard rebuilt with an allowlist and restored fragments; two unsound rules removed rather than retuned; boundary claim replaced by an audited enumeration; Ruff pass, strict mypy pass across 28 files, 377 tests pass at 100% statement and branch coverage; wheel rebuilt | `coordination/handoffs/TB-3002.md` |
| EV-0019 | 31 August 2026 | TB-3002 independent review cycle three | `APPROVE`; 0 Critical, 0 Major, 4 Minor; 38 credential-name probes all rejected, 59 benign-name probes with one known-open rejection, 6 of 7 mutations killed, tree restored and re-verified; final gate 378 tests at 100% statement and branch coverage | `coordination/handoffs/TB-3002.md` |
| EV-0020 | 31 August 2026 | TB-1005 audit schema and redaction boundary | Ruff pass, strict mypy pass across 32 files, 493 tests pass at 100% statement and branch coverage; wheel contains the three audit modules; canaries proven absent across mapping, array, URL, header, and multiline carriers | `coordination/handoffs/TB-1005.md` |
| EV-0021 | 31 August 2026 | Published baseline verification | Commits through `678fdf5` pushed to `origin/main`; CI run 33413279087 completed with conclusion `success` | GitHub Actions run 33413279087 |
| EV-0022 | 31 August 2026 | TB-1005 independent review cycle one | `CHANGES_REQUESTED`; 2 Critical, 7 Major, 6 Minor; adversarial probes showed quoted and JSON-shaped text was never redacted and eight authorization schemes rendered the redaction marker beside an intact credential; all six planted mutations were killed and the tree was restored clean | `coordination/handoffs/TB-1005.md` |
| EV-0023 | 31 August 2026 | TB-1005 cycle-one remediation | Credential-field scanner replaces the pair pattern; every identity field redacted; input length, nesting depth, and non-finite numbers refused; decision identity and reason-code rules widened; non-ASCII names treated as hostile. Ruff pass, strict mypy pass across 32 files, 543 tests pass at 100% statement and branch coverage; a twenty-carrier escape probe found no escape and scan time is linear | `coordination/handoffs/TB-1005.md` |

Evidence records summarize a result; task records and handoffs must preserve the
exact command, exit code, affected test names, and artefact identity needed for
review.

## Coordinator Update Checklist

- [ ] Reconcile proposed claim files with Active Claims.
- [ ] Reject overlapping write scopes before approving either claim.
- [ ] Verify dependency and blocker state before changing a task to `READY`.
- [ ] Update status counts in the same change as any task status.
- [ ] Check claim heartbeat and expire abandoned leases deliberately.
- [ ] Order the Integration Queue by dependency and shared-file risk.
- [ ] Require a handoff and independent validation before `DONE`.
- [ ] Update requirement traceability only when its own evidence standard is met.
- [ ] Record decisions, incidents, invalidated evidence, and reopened tasks.
- [ ] Keep Stage 0 and `PAPER_ONLY` constraints visible in every coordination cycle.

## Change Log

| Date | Change | Coordinator | Evidence |
| --- | --- | --- | --- |
| 31 August 2026 | Created master tracker and seeded 41 tasks from the delivery roadmap | Initial setup | Roadmap, traceability, source tree, and validation baseline |
| 31 August 2026 | Added claim, task, handoff, lease, write-scope, review, and integration mechanism | Initial setup | EV-0005 |
| 31 August 2026 | Started TB-1003 in documented pre-baseline sequential mode; no parallel claim asserted | GitHub Copilot | Owner directive and `coordination/tasks/TB-1003.md` |
| 31 August 2026 | Submitted TB-1003 for independent review; integration remains blocked by BLK-002 | GitHub Copilot | EV-0006 |
| 31 August 2026 | Returned TB-1003 to implementation after independent compatibility review | GitHub Copilot | `coordination/handoffs/TB-1003.md` |
| 31 August 2026 | Resubmitted TB-1003 after restoring the legacy risk enum surface and exhaustive emitted-value tests | GitHub Copilot | EV-0007 |
| 31 August 2026 | Recorded independent approval for TB-1003; kept task in review pending baseline integration | GitHub Copilot | EV-0008 and BLK-002 |
| 31 August 2026 | Configured origin and adopted user-created remote baseline without changing worktree content | GitHub Copilot | Baseline commit and 63-file manifest verification |
| 31 August 2026 | Integrated and closed TB-1003 locally; unlocked TB-3002 | GitHub Copilot | EV-0009 |
| 31 August 2026 | Authenticated the personal GitHub owner, fast-forwarded origin/main, and closed TB-0006 | GitHub Copilot | EV-0010 |
| 31 August 2026 | Reviewed, integrated, and closed TB-1004; promoted TB-3003 to `READY`; moved DATA-003 to `IMPLEMENTED` | GitHub Copilot | EV-0013 |
| 31 August 2026 | Started and submitted TB-3002 in documented sequential mode; no parallel claim asserted | GitHub Copilot | EV-0014 |
| 31 August 2026 | Returned TB-3002 to implementation after independent review, then resubmitted it after remediation | GitHub Copilot | EV-0015 and EV-0016 |
| 31 August 2026 | Recorded that this session holds both the implementer and coordinator roles, so master-tracker edits accompany worker commits until an ongoing coordinator is appointed | GitHub Copilot | TB-3002 review finding M3 |
| 31 August 2026 | Returned TB-3002 to implementation a second time after an independent security regression finding, then resubmitted it | GitHub Copilot | EV-0017 and EV-0018 |
| 31 August 2026 | Approved, integrated, and closed TB-3002 at commit `4ba5111`; recorded NEW-1 and NEW-4 as known-open; promoted no requirement | GitHub Copilot | EV-0019 |
| 31 August 2026 | Published the reviewed baseline to `origin/main` and confirmed CI success on Python 3.12 and 3.14 | GitHub Copilot | EV-0021 |
| 31 August 2026 | Started and submitted TB-1005 in documented sequential mode; no parallel claim asserted | GitHub Copilot | EV-0020 |
| 31 August 2026 | Returned TB-1005 to implementation after two Critical redaction escapes, then resubmitted it after remediation | GitHub Copilot | EV-0022 and EV-0023 |
