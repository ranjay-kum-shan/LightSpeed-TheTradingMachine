# Monthly Paper Trading Report Template

<details open>
<summary><b>Contents</b></summary>

- [Reporting Period](#reporting-period)
- [Qualification Status](#qualification-status)
- [Release and Change Control](#release-and-change-control)
- [Session Completeness](#session-completeness)
- [Performance Comparison](#performance-comparison)
- [Decision Tracking](#decision-tracking)
- [Execution Quality](#execution-quality)
- [Risk and Exposure](#risk-and-exposure)
- [Reconciliation and Incidents](#reconciliation-and-incidents)
- [Availability and Recovery](#availability-and-recovery)
- [Costs and Economic Viability](#costs-and-economic-viability)
- [Data Quality and Revisions](#data-quality-and-revisions)
- [Stage Four Gate Tracking](#stage-four-gate-tracking)
- [Clock Reset Assessment](#clock-reset-assessment)
- [Actions](#actions)
- [Review](#review)

</details>

---

**Report ID:** `MONTHLY-PAPER-TBD`  
**Mode:** `PAPER`  
**Period:** `TBD`  
**Status:** `DRAFT`  
**Generated at UTC:** `TBD`

## Reporting Period

| Field | Value |
|---|---|
| First expected exchange session | `TBD` |
| Last expected exchange session | `TBD` |
| Calendar and version | `TBD` |
| Strategy and frozen candidate version | `TBD` |
| Paper account fingerprint | `TBD` |
| Observation clock start | `TBD` |
| Prior qualifying months | `TBD` |

## Qualification Status

**Current month qualifies:** `NO` until every criterion is reviewed.  
**Qualifying observation remains continuous:** `TBD`  
**Current authorization remains:** `PAPER_ONLY`

Reason summary: `TBD`.

## Release and Change Control

| Release or config | Effective sessions | Approved identity | Material change | Evidence impact |
|---|---|---|---|---|
| `TBD` | `TBD` | `TBD` | `TBD` | `TBD` |

List changes to strategy, parameters, data, calendar, corporate actions, fill policy, costs, broker adapter, risk, scheduling, credentials, alerts, or state schemas. Any unregistered strategy change makes affected sessions non-qualifying.

## Session Completeness

| Measure | Expected | Observed | Missing or failed | Result |
|---|---|---|---|---|
| Exchange sessions | `TBD` | `TBD` | `TBD` | `TBD` |
| Daily reports | 100% of expected sessions | `TBD` | `TBD` | `TBD` |
| Startup reconciliations | One per operated session | `TBD` | `TBD` | `TBD` |
| Close reconciliations | One per operated session | `TBD` | `TBD` | `TBD` |
| No-trade explanations | Every no-trade session | `TBD` | `TBD` | `TBD` |

## Performance Comparison

| Metric | Frozen backtest expectation | Paper observed | Uncertainty or tolerance | Difference | Result |
|---|---|---|---|---|---|
| Net return | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` |
| Annualized Sharpe to date | `TBD` | `TBD` | Within one estimated standard error at gate | `TBD` | `TBD` |
| Maximum drawdown | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` |
| Daily return tracking error | `TBD` | `TBD` | Pre-registered | `TBD` | `TBD` |
| Cumulative PnL divergence | `TBD` | `TBD` | Pre-registered confidence bound | `TBD` | `TBD` |
| Trade count | `TBD` | `TBD` | Expected range | `TBD` | `TBD` |
| Turnover | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` |

Paper PnL is simulated broker evidence and is not described as realized financial return.

## Decision Tracking

| Measure | Count or rate | Target | Exceptions | Result |
|---|---|---|---|---|
| Expected decisions | `TBD` | `TBD` | `TBD` | `TBD` |
| Exact signal or target matches | `TBD` | Pre-registered tolerance | `TBD` | `TBD` |
| Scheduler or data timing deviations | `TBD` | Zero unexplained | `TBD` | `TBD` |
| Risk-denied decisions | `TBD` | Explained | `TBD` | `TBD` |
| Owner strategy interventions | `TBD` | Zero in qualifying period | `TBD` | `TBD` |

## Execution Quality

| Measure | Modeled | Paper observed | Tolerance | Result |
|---|---|---|---|---|
| Median slippage basis points | `TBD` | `TBD` | No greater than twice modeled at gate | `TBD` |
| Slippage distribution tails | `TBD` | `TBD` | Pre-registered | `TBD` |
| Fill rate | `TBD` | `TBD` | `TBD` | `TBD` |
| Partial fills | `TBD` | `TBD` | Explained | `TBD` |
| Rejects | `TBD` | `TBD` | Explained | `TBD` |
| Cancels and expires | `TBD` | `TBD` | Explained | `TBD` |
| Unknown outcomes | Zero | `TBD` | Zero unresolved | `TBD` |
| Duplicate logical orders | Zero | `TBD` | Zero | `TBD` |

Attach per-fill differences and distribution artefacts; averages alone can hide tail failures.

## Risk and Exposure

| Measure | Observed maximum or minimum | Limit | Breaches | Result |
|---|---|---|---|---|
| Order notional | `TBD` | `TBD` | `TBD` | `TBD` |
| Position concentration | `TBD` | `TBD` | `TBD` | `TBD` |
| Gross exposure | `TBD` | `TBD` | `TBD` | `TBD` |
| Net exposure | `TBD` | `TBD` | `TBD` | `TBD` |
| Leverage | `TBD` | At most 1.0 in Stage 1 through Stage 4 | `TBD` | `TBD` |
| ADV participation | `TBD` | At most approved profile and promotion ceiling | `TBD` | `TBD` |
| Daily loss | `TBD` | `TBD` | `TBD` | `TBD` |
| Drawdown | `TBD` | `TBD` | `TBD` | `TBD` |
| Order rate | `TBD` | `TBD` | `TBD` | `TBD` |

List every halt, reset, or limit change and its approval.

## Reconciliation and Incidents

| Measure | Observed | Stage 4 target | Result |
|---|---|---|---|
| Reconciliations run | `TBD` | All required triggers | `TBD` |
| Explained temporary mismatches | `TBD` | Documented and regression-tested where needed | `TBD` |
| Unexplained reconciliation breaks | `TBD` | Zero | `TBD` |
| Incidents by severity | `TBD` | No unresolved blocking incident | `TBD` |
| Credential or environment events | `TBD` | Zero exposure and all resolved | `TBD` |

| Incident or discrepancy ID | Sessions affected | Evidence impact | Resolution | Clock action |
|---|---|---|---|---|
| `TBD` | `TBD` | `TBD` | `TBD` | `TBD` |

## Availability and Recovery

| Measure | Observed | Target | Result |
|---|---|---|---|
| Market-hours availability | `TBD` | At least 99% | `TBD` |
| Missed or late decision windows | `TBD` | Zero unexplained | `TBD` |
| Broker disconnect duration | `TBD` | Explained and reconciled | `TBD` |
| Heartbeat losses | `TBD` | Explained and exercised safely | `TBD` |
| Daily report delivery | `TBD` | 100% | `TBD` |
| Induced recovery exercises completed to date | `TBD` | At least five before gate | `TBD` |
| Backup and restore status | `TBD` | Current and passing | `TBD` |

## Costs and Economic Viability

| Cost | Backtest assumption | Paper observed or current schedule | Difference | Action |
|---|---|---|---|---|
| Spread and slippage | `TBD` | `TBD` | `TBD` | `TBD` |
| Commission and fees | `TBD` | `TBD` | `TBD` | `TBD` |
| FX conversion | `TBD` | `TBD` | `TBD` | `TBD` |
| Data and infrastructure | `TBD` | `TBD` | `TBD` | `TBD` |

Report whether current realistic fixed and variable costs leave a plausible positive net result without treating paper performance as proof.

## Data Quality and Revisions

| Measure | Result | Affected sessions or evidence | Action |
|---|---|---|---|
| Daily validation and freshness | `TBD` | `TBD` | `TBD` |
| Historical provider revisions | `TBD` | `TBD` | `TBD` |
| Corporate-action updates | `TBD` | `TBD` | `TBD` |
| Calendar or availability-rule changes | `TBD` | `TBD` | `TBD` |
| Dataset hashes used by session | `TBD` | `TBD` | `TBD` |

## Stage Four Gate Tracking

**Default status for every Stage 4 gate criterion:** `NOT_MET`

| Criterion | Observed to date | Threshold | Status |
|---|---|---|---|
| Consecutive qualifying duration | `TBD` | At least three months | `NOT_MET` |
| Unexplained reconciliation breaks | `TBD` | Zero | `NOT_MET` |
| Paper Sharpe versus frozen backtest | `TBD` | Within one estimated standard error | `NOT_MET` |
| Median paper slippage versus modeled | `TBD` | No greater than twice modeled | `NOT_MET` |
| Market-hours availability | `TBD` | At least 99% | `NOT_MET` |
| Induced recovery exercises | `TBD` | At least five successful exercises | `NOT_MET` |
| Daily expected-session reports | `TBD` | 100%, including no-trade sessions | `NOT_MET` |
| Unknown logical orders | `TBD` | Zero unresolved; duplicate logical orders also zero | `NOT_MET` |
| Tax and recordkeeping rehearsal | `TBD` | Complete on paper records | `NOT_MET` |
| Material strategy changes | `TBD` | None in qualifying window | `NOT_MET` |

No partial score creates a pass.

## Clock Reset Assessment

| Reset trigger | Occurred | Sessions affected | Decision and evidence |
|---|---|---|---|
| Unexplained reconciliation break | `TBD` | `TBD` | `TBD` |
| Duplicate or unknown order | `TBD` | `TBD` | `TBD` |
| Backtest or data-control defect | `TBD` | `TBD` | `TBD` |
| Material strategy data execution cost or risk change | `TBD` | `TBD` | `TBD` |
| Availability below threshold | `TBD` | `TBD` | `TBD` |
| Owner intervention | `TBD` | `TBD` | `TBD` |

**Clock decision:** `CONTINUE`, `RESET_AFTER_FIX`, `DEMOTE`, or `TBD`  
**New clock start if reset:** `TBD`

## Actions

| Action ID | Description | Owner | Due | Blocking | Status |
|---|---|---|---|---|---|
| `ACT-TBD` | `TBD` | `TBD` | `TBD` | `TBD` | `OPEN` |

## Review

| Role | Name | Decision | Date |
|---|---|---|---|
| Paper operations owner | `TBD` | `ACCEPT_REPORT`, `CORRECT`, `RESET_CLOCK`, `DEMOTE`, or `ABANDON` | `TBD` |

**Final month qualification:** `NO` until approved  
**Report hash:** `TBD`  
**Next review:** `TBD`