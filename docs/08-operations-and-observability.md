# Operations and Observability Runbook

<details open>
<summary><b>Contents</b></summary>

- [Purpose](#purpose)
- [Operational Objectives](#operational-objectives)
- [Structured Event Contract](#structured-event-contract)
- [Reason Codes](#reason-codes)
- [Metrics](#metrics)
- [Alerts](#alerts)
- [Heartbeat and Watchdog](#heartbeat-and-watchdog)
- [Daily Report](#daily-report)
- [Runbooks](#runbooks)
  - [Start a Paper Session](#start-a-paper-session)
  - [Respond to a Risk Halt](#respond-to-a-risk-halt)
  - [Respond to a Reconciliation Break](#respond-to-a-reconciliation-break)
  - [Respond to Stale or Invalid Data](#respond-to-stale-or-invalid-data)
  - [Respond to Broker Disconnect](#respond-to-broker-disconnect)
  - [Recover After Process Failure](#recover-after-process-failure)
- [Scheduling and Session Calendar](#scheduling-and-session-calendar)
- [Backup and Restore](#backup-and-restore)
- [Release and Configuration Deployment](#release-and-configuration-deployment)
- [Retention and Review](#retention-and-review)
- [Operational Acceptance](#operational-acceptance)
- [Open Decisions](#open-decisions)

</details>

---

**Version:** 1.0  
**Date:** 30 August 2026  
**Status:** Proposed baseline  
**Related:** [Architecture](02-architecture.md) | [Risk Specification](03-risk-and-safety.md) | [Execution Specification](06-execution-and-reconciliation.md) | [Security Specification](07-security-and-secrets.md)

## Purpose

This runbook defines how the owner can tell whether the trading system is healthy, what it did, why it stopped, and how to recover without creating duplicate orders or concealing a mismatch. Every normal session produces positive evidence; absence of output is never interpreted as success.

## Operational Objectives

| Objective | Paper target | Measurement |
|---|---|---|
| Market-hours availability | At least 99% during the qualifying Stage 4 window | Eligible scheduled minutes minus unavailable minutes |
| Unexplained reconciliation breaks | Zero | Persisted reconciliation outcomes |
| Daily report delivery | 100% of expected sessions, including no-trade days | Delivery acknowledgement |
| Heartbeat detection | Within two missed heartbeat intervals plus alert transport time | Watchdog event timestamps |
| Duplicate logical orders | Zero | Client-order and intent reconciliation |
| Stale-data trades | Zero | Data-freshness decisions joined to orders |
| Recovery exercises | At least five successful induced failures before paper promotion | Exercise reports |
| Audit lineage | 100% of decisions identify code, config, data, and session | Schema validation |

Targets are service indicators, not permission to ignore one severe incident. Any unexplained order, fill, position, or credential event is blocking regardless of aggregate uptime.

## Structured Event Contract

Logs are JSON Lines written as one complete event per line under a versioned schema.

| Field | Requirement |
|---|---|
| `schema_version` | Required event schema version |
| `event_id` | Globally unique immutable identity |
| `event_type` | Stable dotted event name |
| `occurred_at_utc` | Source occurrence time |
| `recorded_at_utc` | Local durable-record time |
| `severity` | `DEBUG`, `INFO`, `WARNING`, `ERROR`, or `CRITICAL` |
| `mode` | `BACKTEST`, `PAPER`, `RECOVERY`, `HALTED`, or future approved value |
| `session_id` | Required for session-scoped events |
| `run_id` | Required for research or backtest events |
| `correlation_id` | Connects decision, risk, intent, order, fill, and report |
| `component` | Stable emitting component |
| `reason_code` | Required for decisions, rejections, transitions, and alerts |
| `git_revision` | Source revision identity |
| `config_hash` | Effective redacted configuration hash |
| `data_hash` | Decision dataset identity where applicable |
| `strategy_id` | Strategy and version where applicable |
| `account_fingerprint` | Redacted approved account identity where applicable |
| `payload` | Schema-specific allowlisted non-secret object |

Events are append-only. Corrections reference the original event and explain the correction; they do not mutate historical log lines. Event writing failure before an external side effect blocks that side effect.

## Reason Codes

Reason codes are stable machine-readable identifiers with separate human messages.

| Family | Examples | Use |
|---|---|---|
| `MODE_*` | `MODE_PAPER_VERIFIED`, `MODE_LIVE_DENIED` | Environment and approval guards |
| `DATA_*` | `DATA_STALE`, `DATA_REVISION_DETECTED` | Readiness and validation |
| `TIME_*` | `TIME_SESSION_CLOSED`, `TIME_CLOCK_OFFSET` | Clock and calendar decisions |
| `RISK_*` | `RISK_ORDER_NOTIONAL`, `RISK_DAILY_LOSS` | Pre-trade and halt decisions |
| `ORDER_*` | `ORDER_ACCEPTED`, `ORDER_OUTCOME_UNKNOWN` | Order lifecycle |
| `RECON_*` | `RECON_POSITION_MISMATCH`, `RECON_PASSED` | State comparison |
| `BROKER_*` | `BROKER_DISCONNECTED`, `BROKER_THROTTLED` | Provider health |
| `CONTROL_*` | `CONTROL_KILL_PRESENT`, `CONTROL_HEARTBEAT_LOST` | Independent controls |
| `SECURITY_*` | `SECURITY_REDACTION_FAILURE`, `SECURITY_ACCOUNT_MISMATCH` | Security events |
| `REPORT_*` | `REPORT_NO_TRADE`, `REPORT_DELIVERY_FAILED` | Operational evidence |

Messages may improve without changing automation. Removing or changing the meaning of a reason code is a schema-versioned breaking change.

## Metrics

| Metric | Type | Dimensions kept small | Alert relevance |
|---|---|---|---|
| `session_last_success_utc` | Gauge | mode | Missing session evidence |
| `heartbeat_age_seconds` | Gauge | process role | Dead-man control |
| `data_age_seconds` | Gauge | dataset type, provider | Stale data |
| `clock_offset_seconds` | Gauge | clock source | Unsafe timing |
| `reconciliation_status` | Gauge | domain | Any mismatch |
| `open_orders` | Gauge | strategy | Unexpected working orders |
| `open_positions` | Gauge | strategy | Exposure tracking |
| `gross_exposure` and `net_exposure` | Gauge | currency | Limit proximity |
| `daily_pnl` and `drawdown` | Gauge | currency | Loss controls |
| `risk_rejections_total` | Counter | reason family | Loop or config defect |
| `order_submissions_total` | Counter | terminal outcome | Activity and reject tracking |
| `unknown_order_outcomes` | Gauge | strategy | Immediate halt condition |
| `broker_request_latency_seconds` | Histogram | operation class | Degradation |
| `broker_disconnects_total` | Counter | provider | Reliability |
| `slippage_bps` | Distribution in report store | strategy, instrument | Backtest-to-paper tracking |
| `report_delivery_status` | Gauge | report type, channel | Silence detection |
| `disk_free_bytes` | Gauge | volume | Durable-write safety |

Account IDs, order IDs, symbols across a broad universe, and exception messages are not metric labels. High-cardinality evidence belongs in structured events and reports.

## Alerts

| Severity | Condition | Initial response | Acknowledgement target |
|---|---|---|---|
| `CRITICAL` | Unknown order outcome, account mismatch, reconciliation break, kill control, heartbeat loss with exposure, drawdown halt, suspected credential leak | Stop new risk, preserve evidence, inspect broker through trusted path | Immediate owner notification on both channels |
| `HIGH` | Daily loss halt, stale data near order window, sustained broker disconnect, durable-write failure, paper report absent | Halt applicable session and investigate | Before next eligible order window |
| `MEDIUM` | Repeated risk rejection, provider revision, backup failure, clock drift below hard limit, degraded latency | Review and correct before unattended continuation if persistent | Same day |
| `LOW` | Non-blocking maintenance or approaching retention and capacity thresholds | Schedule review | Weekly review |

An alert contains mode, UTC time, session, reason code, impact, current safe state, correlation ID, and the first runbook action. It excludes secrets and unnecessary account data.

Alert delivery is monitored. Primary-channel failure routes to a configured secondary channel. A `CRITICAL` condition does not clear because alert delivery failed.

## Heartbeat and Watchdog

The trading process atomically replaces a heartbeat record containing schema version, process instance, session, mode, state, UTC time, and last successful reconciliation ID. It contains no credential.

The independent watchdog:

1. Uses its own scheduler and process.
2. Knows expected session windows from a pinned calendar.
3. Validates heartbeat format, monotonic progress, age, mode, and session.
4. Avoids false recovery action outside expected operation while still detecting an overdue daily report.
5. On expiry, alerts, verifies the paper account, enumerates approved working orders, and requests idempotent cancellation under policy.
6. Never opens or enlarges a position.
7. Records every observation and broker response separately from the trading process.

The heartbeat interval, expiry threshold, watchdog cadence, and alert deadline are configured with units and tested under delayed filesystem writes and host time shifts.

## Daily Report

Every expected exchange session produces a report with:

- Mode, session date, process version, effective config hash, data hash, calendar version, and account fingerprint.
- Preflight, data-readiness, watchdog, and start and end reconciliation outcomes.
- Strategy decision and reason, including `NO_TRADE`.
- Risk decisions and current effective limits.
- Orders, fills, rejects, partial fills, cancels, and unknown outcomes.
- Start and end positions, cash, equity, daily PnL, drawdown, and exposure.
- Modeled versus broker-observed costs and slippage.
- Data age, broker connectivity, uptime, and heartbeat status.
- Alerts and unresolved actions.
- Delivery time and acknowledgement state.

A no-trade report explains whether the cause was strategy neutrality, closed market, invalid data, risk rejection, halt, or other stable reason. Backtest, paper, and future live values are never combined into one unlabeled curve.

## Runbooks

### Start a Paper Session

1. Confirm the scheduler release ID and expected exchange session.
2. Verify no maintenance, unresolved incident, operator kill, or stale approval blocks operation.
3. Start in `HALTED`; validate paper mode, endpoint, credential namespace, account fingerprint, clock, disk, and alert channels.
4. Acquire the single-writer lock and start or verify the independent watchdog.
5. Enter `RECOVERY`, replay durable state, query broker facts, and complete reconciliation.
6. Verify the published current dataset, actions, calendar, and freshness.
7. Enter `READY`; allow `RUNNING` only for the configured decision and order window.
8. Confirm the session event and heartbeat are visible.

### Respond to a Risk Halt

1. Do not restart to clear the condition.
2. Read the risk reason code, effective limit, coherent input snapshot, and pending orders.
3. Inspect broker positions and working orders through the normal reconciliation path.
4. For a daily-loss halt, keep new exposure disabled for the session; use only approved risk-reducing actions.
5. For a drawdown or control halt, activate or preserve the operator kill and require owner review.
6. Identify whether the cause is market movement, configuration, stale input, duplicate intent, or software defect.
7. Document resolution and add a regression test for defects.
8. Clear only through the explicit reset command and retain the original halt event.

### Respond to a Reconciliation Break

1. Keep the system in `RECOVERY` or `HARD_HALTED` and stop strategy orders.
2. Preserve both normalized views and raw broker evidence references.
3. Re-query with pagination and a wider overlap to exclude transient or boundary omissions.
4. Compare account, positions, cash, orders, and fills independently.
5. Resolve unknown order outcomes by client order ID before any correction.
6. Propose a correction event; do not edit historical journal rows.
7. Require owner acknowledgement for any unexplained broker fact or manual broker action.
8. Add a provider mapping or software regression test, rerun full reconciliation, then reset explicitly.

### Respond to Stale or Invalid Data

1. Stop the decision cycle before intent creation.
2. Identify the failed validation or freshness code and affected instruments and sessions.
3. Check provider status and source timestamps without overwriting the last published snapshot.
4. Pull into a new raw capture, validate, compare revisions, and publish only if every required rule passes.
5. If history changed, open a revision review and identify affected runs.
6. Do not forward-fill or manually patch a promotable dataset without a new manifest and evidence.
7. Resume only with a published hash and fresh readiness check.

### Respond to Broker Disconnect

1. Stop new submissions and mark in-flight outcomes conservatively.
2. Preserve original client order IDs and attempt times.
3. Use bounded reconnect for reads; do not generic-retry order creation.
4. Query orders and fills over an overlap and resolve every unknown outcome.
5. Fetch positions and cash, then run full reconciliation.
6. Resume only when connection health, event continuity, and reconciliation pass.
7. Record outage duration and whether paper-versus-backtest tracking was affected.

### Recover After Process Failure

1. Confirm watchdog alert and cancellation evidence; inspect the paper broker directly if evidence is incomplete.
2. Keep the operator kill present while assessing exposure.
3. Preserve the failed process logs, state, release ID, and last heartbeat.
4. Start the same or corrected approved release in `RECOVERY`, never directly in `RUNNING`.
5. Replay intents and events; query broker orders, fills, positions, and cash over a safe overlap.
6. Resolve ambiguous lifecycle states and complete reconciliation.
7. Run the relevant crash-point regression test if a defect was found.
8. Issue an explicit owner reset, then complete normal preflight and data readiness.

## Scheduling and Session Calendar

- Windows Task Scheduler is the initial scheduler for bounded jobs.
- Tasks run under a dedicated non-administrator account where practical.
- The exchange calendar generates expected session dates and windows; weekday-only schedules are prohibited.
- Data retrieval runs after the provider-specific publication delay.
- The decision job has a bounded latest-start and latest-submit time. Missing it produces a no-trade report rather than a late order.
- The watchdog schedule is independent of the trading process task.
- A report-verifier task checks that each expected daily report arrived.
- Overlapping task instances are denied by both scheduler settings and an application lock.
- Task definitions are exported, versioned without secrets, and included in release review.

## Backup and Restore

Back up the intent, order, fill, ledger, experiment, approval, manifest, audit, and report stores according to sensitivity and retention requirements. Published content-addressed market data may use incremental backup.

Restore exercise:

1. Select a known backup and verify its encryption and integrity metadata.
2. Restore to an isolated non-runtime directory with no broker credential access.
3. Run database integrity checks and event replay.
4. Verify referenced configs, data hashes, and report artefacts exist.
5. Rebuild derived ledger and experiment views and compare known checkpoints.
6. Record recovery point and recovery duration.
7. Delete the isolated sensitive copy under the retention procedure.

A restore test does not contact a broker. Broker reconciliation is a separate paper recovery exercise after local restoration is accepted.

## Release and Configuration Deployment

Each paper release manifest records:

- Release ID and UTC build time.
- Source revision and clean or dirty state.
- Python and dependency lock identity.
- Configuration schema and approved effective config hash.
- Strategy, risk profile, data schema, calendar, and adapter versions.
- Required state migration and rollback compatibility.
- Offline test, security scan, adapter contract, and paper smoke-test outcomes.
- Owner approval and expiry or review date where applicable.

Deployment stops the scheduler, confirms no in-flight order, takes a state backup, installs into a versioned directory, validates configuration without submitting, runs recovery and reconciliation, then re-enables the next eligible session. Rollback never rolls state backward past broker events; it restores code compatibility and replays current facts.

## Retention and Review

- Retention periods are defined by record type, provider terms, tax needs, and incident value before any separately approved Stage 5 operation.
- Order, fill, fee, FX, approval, reconciliation, and tax evidence receives the longest applicable period.
- Debug logs with no unique audit value are minimized and expire sooner.
- Deletion is logged by record class and date without retaining deleted sensitive content.
- Weekly paper review covers alerts, risk rejections, revisions, backups, and upcoming calendar exceptions.
- Monthly review compares backtest and paper decisions, fills, slippage, costs, uptime, and unresolved events.
- Annual or pre-live review revalidates broker terms, market-data licensing, tax assumptions, dependency support, credentials, and all owner approvals.

## Operational Acceptance

- Structured event schemas validate normal, no-trade, reject, partial-fill, halt, and recovery sessions.
- Primary and secondary alerts are delivered with canary events and no secret leakage.
- Heartbeat loss is detected and watchdog cancellation behavior is proven safely in paper.
- Every runbook is exercised as a tabletop; critical ones are also induced against the paper path.
- A daily report is delivered for each synthetic expected-session outcome.
- Scheduler overlap and missed-run behavior are tested.
- Backup integrity and isolated restore pass.
- A release can be deployed and rolled back without losing broker-derived facts.
- Five induced failure recoveries pass before Stage 4 completion.

## Open Decisions

| Decision | Needed by | Blocking effect |
|---|---|---|
| Choose primary and secondary alert channels | Watchdog implementation | Blocks alert acceptance |
| Set heartbeat and expiry intervals | Vertical-slice operations | Blocks timing tests |
| Define provider publication delay and order window | Paper scheduling | Blocks task schedule |
| Select runtime host and dedicated OS account | Unattended paper start | Blocks deployment hardening |
| Approve retention periods by record class | Persistent paper operation | Blocks purge configuration |
| Set backup location encryption and cadence | Stateful paper acceptance | Blocks restore gate |
