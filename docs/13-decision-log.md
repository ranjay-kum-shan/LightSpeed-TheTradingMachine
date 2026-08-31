# Project Decision Log

<details open>
<summary><b>Contents</b></summary>

- [Purpose](#purpose)
- [Decision Statuses](#decision-statuses)
- [Decision Process](#decision-process)
- [Recorded Decisions](#recorded-decisions)
  - [Accepted Constraints](#accepted-constraints)
  - [Proposed Defaults](#proposed-defaults)
  - [Blocked Decisions](#blocked-decisions)
- [Open Decision Queue](#open-decision-queue)
- [Superseding a Decision](#superseding-a-decision)
- [Decision Evidence](#decision-evidence)
- [Maintenance](#maintenance)

</details>

---

**Version:** 1.0  
**Date:** 30 August 2026  
**Status:** Active register  
**Template:** [Decision Record Template](templates/decision-record-template.md)  
**Authority:** [Project Charter](../CHARTER.md)

## Purpose

This log records decisions that constrain architecture, evidence, safety, external providers, or owner exposure. It prevents important choices from disappearing into code, chat, or unstated defaults.

The log distinguishes accepted safety constraints from working defaults that still require owner confirmation. Creating documentation does not silently approve the proposed rows.

## Decision Statuses

| Status | Meaning |
|---|---|
| `PROPOSED` | A recommended choice awaiting the named approval or evidence |
| `ACCEPTED` | Approved and currently authoritative |
| `BLOCKED` | No choice may be applied until required owner or external evidence exists |
| `REJECTED` | Considered and explicitly not selected |
| `SUPERSEDED` | Replaced by a later decision that links back to it |
| `EXPIRED` | Time-limited approval ended and must not be used |

Only `ACCEPTED` decisions may authorize implementation assumptions. A `PROPOSED` row may guide a reversible prototype if its gate explicitly permits that, but it cannot enable external risk.

## Decision Process

Create a standalone decision record when a choice:

- Changes market, broker, asset, bar frequency, order policy, leverage, or account mode.
- Changes risk limits, capital, promotion thresholds, or abandon criteria.
- Introduces a service, language, database, deployment target, or irreversible data format.
- Changes point-in-time, timestamp, cost, statistical, or accounting meaning.
- Changes credential, endpoint, watchdog, backup, retention, tax, or compliance controls.
- Invalidates prior research, paper, or release evidence.

The record states context, options, evidence, decision, consequences, rollback, affected requirements, and approvals. The summary row below is updated only after the record is complete.

## Recorded Decisions

### Accepted Constraints

| ID | Decision | Status | Rationale and effect | Source |
|---|---|---|---|---|
| DEC-001 | Profitability is evidence-driven and never assumed. | `ACCEPTED` | Research and engineering success remain separate; no favorable backtest bypasses gates. | Reviewed plan and charter |
| DEC-002 | Current broker-connected authorization is paper-only. | `ACCEPTED` | Real-money capability remains absent until a separately approved Stage 5 decision. | Charter and rollout plan |
| DEC-003 | Hard risk checks, kill controls, durable intent, and reconciliation precede broker order submission. | `ACCEPTED` | No strategy-to-broker bypass is permitted. | Requirements and architecture |
| DEC-004 | A signal based on daily bar `t` cannot fill before the next eligible session. | `ACCEPTED` | Prevents same-bar look-ahead and establishes simulator chronology. | Data and research specifications |
| DEC-005 | The system fails closed on missing, stale, ambiguous, or unreconciled state. | `ACCEPTED` | Ambiguity cannot create new exposure. | Risk specification |
| DEC-006 | Published data and result artefacts are immutable and content-addressed. | `ACCEPTED` | Revisions create new identities and preserve replay. | Data specification |
| DEC-007 | A broker timeout is an unknown outcome, not proof of failure. | `ACCEPTED` | Query by stable client order ID before any controlled retry. | Execution specification |
| DEC-008 | Watchdog default action is alert plus cancellation of known working orders, not blind position flattening. | `ACCEPTED` | Automatic flattening can worsen risk under stale or disconnected conditions. | Risk and architecture specifications |
| DEC-009 | The first strategy is machinery evidence only. | `ACCEPTED` | A moving-average result produced during engine development is ineligible for promotion. | Research protocol |
| DEC-010 | HFT, FPGA, co-location, distributed services, autonomous discovery, leverage, shorting, and derivatives are outside initial scope. | `ACCEPTED` | Protects iteration speed and risk boundary. | Charter |

### Proposed Defaults

| ID | Decision | Status | Approval needed | Effect if accepted |
|---|---|---|---|---|
| DEC-011 | Begin with one liquid US-listed broad-market ETF using daily bars and a 2 to 20 day horizon. | `PROPOSED` | Owner Stage 0 approval | Fixes reference instrument and calendar scope |
| DEC-012 | Use Alpaca paper as the first broker adapter. | `PROPOSED` | Owner eligibility and terms confirmation | Enables paper adapter work only |
| DEC-013 | Use Python 3.12 or newer in one process. | `PROPOSED` | Owner Stage 0 approval | Establishes runtime and package scaffold |
| DEC-014 | Use Parquet plus DuckDB for analytical data and SQLite for experiments and state. | `PROPOSED` | Implementation spike and owner acceptance | Establishes local persistence baseline |
| DEC-015 | Use Polars for canonical analytical transformations. | `PROPOSED` | Small data-pipeline spike | Establishes dataframe semantics |
| DEC-016 | Use GBP as the reporting base currency. | `PROPOSED` | Owner approval | Establishes FX and report denominator |
| DEC-017 | Plan around 8 to 10 focused hours each week. | `PROPOSED` | Owner approval | Establishes roadmap capacity only |
| DEC-018 | Use Windows Task Scheduler on a dedicated non-administrator account for initial unattended paper jobs. | `PROPOSED` | Host and account decision | Establishes scheduling topology |

### Blocked Decisions

| ID | Decision | Status | Blocking evidence | Safety effect |
|---|---|---|---|---|
| DEC-019 | Tiny-live capital allocation | `BLOCKED` | Owner states an amount that can be lost completely without affecting life decisions | Stage 5 remains denied |
| DEC-020 | Maximum total daily and drawdown loss values | `BLOCKED` | Owner approval in base currency and percent | Stage 5 remains denied |
| DEC-021 | Any leverage or shorting | `BLOCKED` | New charter scope, risk design, broker and professional review | Initial profiles remain long-only and unleveraged |
| DEC-022 | Tax calculation and retention policy | `BLOCKED` | Current qualified UK professional confirmation | Stage 5 and automated deletion remain denied |
| DEC-023 | Automatic emergency flattening | `BLOCKED` | Scenario analysis, per-instrument policy, price protection, tests, and owner approval | Watchdog remains cancel-and-alert only |
| DEC-024 | Broad cross-sectional universe | `BLOCKED` | Point-in-time membership, delistings, actions, and licensing | Broad-universe results remain non-promotable |

## Open Decision Queue

| Priority | Decision | Owner | Needed by | Input required |
|---|---|---|---|---|
| 1 | Approve or revise initial market, horizon, weekly capacity, and base currency | Owner | Stage 0 | Charter review |
| 2 | Select the exact reference ETF | Owner | Data implementation | Liquidity, currency, listing, and strategy scope |
| 3 | Confirm Alpaca account eligibility and automated paper terms | Owner | Adapter implementation | Current broker documentation and account check |
| 4 | Select daily-bar and corporate-action provider | Owner after spike | Data publication | Coverage, availability semantics, terms, revision behavior, cost |
| 5 | Select local secret provider and runtime directory | Owner | Broker authentication | Windows security and scheduling fit |
| 6 | Set paper reference equity and risk values | Owner | Paper deployment | Realistic hypothetical allocation and risk policy |
| 7 | Choose initial paper order type and submission window | Owner after simulation evidence | Broker vertical slice | Fill honesty and operational timing |
| 8 | Choose primary and secondary alerts and backup technology | Owner | Unattended paper | Delivery, encryption, restore, and cost |
| 9 | Define paper tracking-error tolerances before observation | Owner | Stage 4 start | Frozen backtest distribution and operational evidence |

Owner-dependent financial and personal values are never inferred from previous examples or broker defaults.

## Superseding a Decision

1. Keep the old ID and record unchanged.
2. Create a new decision record with a new ID and `supersedes` link.
3. Explain the new evidence and why the old choice no longer applies.
4. Mark the old summary row `SUPERSEDED` and link the new ID.
5. Identify affected requirements, code, configuration, tests, data, releases, and gate evidence.
6. Invalidate or rerun prior evidence when semantics changed.
7. Require the same or stronger approval level as the superseded choice.

Never edit an accepted decision in place to make a later implementation appear compliant.

## Decision Evidence

Each accepted record must include:

- Stable ID, title, date, owner, status, and decision scope.
- Context and the measurable problem being solved.
- Considered options, including retaining the current state.
- Selection criteria and evidence.
- Explicit decision and effective boundary.
- Positive and negative consequences.
- Safety, security, data, statistical, operational, cost, and compliance effects.
- Rollout, rollback, expiry, and review trigger.
- Affected requirements, documents, tests, migrations, and evidence.
- Owner and any required professional approval.

Secrets, personal tax details, and full account numbers are referenced through protected evidence, not copied into the decision record.

## Maintenance

- Review this register at every stage gate and monthly during unattended paper operation.
- Resolve or re-date proposed decisions whose needed-by stage is approaching.
- Treat stale external assumptions as expired until reverified.
- Add each accepted record to the release or gate evidence bundle it controls.
- Keep IDs immutable and sequential; deletion is prohibited.
- Ensure the project index links this register and its template.
