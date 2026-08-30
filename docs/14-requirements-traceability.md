# Requirements Traceability Matrix

<details open>
<summary><b>Contents</b></summary>

- [Purpose](#purpose)
- [Status Legend](#status-legend)
- [Functional Traceability](#functional-traceability)
  - [Market Data Requirements](#market-data-requirements)
  - [Backtesting Requirements](#backtesting-requirements)
  - [Strategy Research Requirements](#strategy-research-requirements)
  - [Risk Requirements](#risk-requirements)
  - [Execution Requirements](#execution-requirements)
  - [State Requirements](#state-requirements)
  - [Audit Requirements](#audit-requirements)
- [Nonfunctional Traceability](#nonfunctional-traceability)
  - [Safety and Reliability Requirements](#safety-and-reliability-requirements)
  - [Reproducibility Requirements](#reproducibility-requirements)
  - [Security Requirements](#security-requirements)
  - [Performance Requirements](#performance-requirements)
  - [Maintainability Requirements](#maintainability-requirements)
- [Stage Gate Coverage](#stage-gate-coverage)
- [Current Coverage Gaps](#current-coverage-gaps)
- [Maintenance Rules](#maintenance-rules)

</details>

---

**Version:** 1.0  
**Date:** 30 August 2026  
**Status:** Specification coverage complete; implementation in progress  
**Source:** [Requirements Specification](01-requirements.md)

## Purpose

This matrix maps every product requirement to its owning specification, planned executable evidence, and applicable gate. It currently proves documentation coverage only. No row marked `SPECIFIED` should be mistaken for implemented or tested behavior.

## Status Legend

| Status | Meaning |
|---|---|
| `SPECIFIED` | Requirement and acceptance intent are documented |
| `IMPLEMENTED` | Owning behavior exists but all verification may not yet pass |
| `VERIFIED` | Required automated checks or operational exercises pass for a named release |
| `BLOCKED` | External decision or dependency prevents implementation or verification |
| `NOT_APPLICABLE` | Excluded by an accepted scoped decision with a linked rationale |

**Current matrix state:** 60 requirements are `SPECIFIED`, RISK-002 is `IMPLEMENTED`, and none is `VERIFIED`. Verification remains reserved for a named release and gate evidence bundle.

## Functional Traceability

### Market Data Requirements

| Requirement | Owning specification | Planned verification | Gate | Status |
|---|---|---|---|---|
| DATA-001 | [Market Data Specification](04-data-specification.md) | `T-DATA-INGEST-001` reference ETF schema and Parquet build | Stage 1 | `SPECIFIED` |
| DATA-002 | [Market Data Specification](04-data-specification.md) | `T-DATA-CALENDAR-002` holidays and half-days | Stage 1 | `SPECIFIED` |
| DATA-003 | [Market Data Specification](04-data-specification.md) | `T-DATA-TIME-003` naive rejection UTC and DST fixtures | Stage 1 | `SPECIFIED` |
| DATA-004 | [Market Data Specification](04-data-specification.md) | `T-DATA-MANIFEST-004` complete lineage and hash reload | Stage 1 | `SPECIFIED` |
| DATA-005 | [Market Data Specification](04-data-specification.md) | `T-DATA-DV-005` isolated failure for each `DV-001` through `DV-012` | Stage 1 | `SPECIFIED` |
| DATA-006 | [Market Data Specification](04-data-specification.md) | `T-DATA-REVISION-006` immutable changed overlap | Stage 2 | `SPECIFIED` |
| DATA-007 | [Market Data Specification](04-data-specification.md) | `T-DATA-FRESHNESS-007` stale current view halts | Stage 1 | `SPECIFIED` |

### Backtesting Requirements

| Requirement | Owning specification | Planned verification | Gate | Status |
|---|---|---|---|---|
| BT-001 | [Backtesting Protocol](05-backtesting-and-research.md) | `T-BT-TEMPORAL-001` next-session and same-bar denial | Stage 1 | `SPECIFIED` |
| BT-002 | [Backtesting Protocol](05-backtesting-and-research.md) | `T-BT-DETERMINISM-002` byte-identical canonical replay | Stage 2 | `SPECIFIED` |
| BT-003 | [Backtesting Protocol](05-backtesting-and-research.md) | `T-BT-COST-CONFIG-003` missing applicable field rejected | Stage 2 | `SPECIFIED` |
| BT-004 | [Backtesting Protocol](05-backtesting-and-research.md) | `T-BT-ORDER-004` reject partial cancel cash position PnL | Stage 1 | `SPECIFIED` |
| BT-005 | [Backtesting Protocol](05-backtesting-and-research.md) | `T-BT-OOS-005` report metric provenance | Stage 2 | `SPECIFIED` |
| BT-006 | [Backtesting Protocol](05-backtesting-and-research.md) | `T-BT-COST-SENS-006` baseline doubled quadrupled identity | Stage 2 | `SPECIFIED` |
| BT-007 | [Backtesting Protocol](05-backtesting-and-research.md) | `T-BT-SANITY-007` complete negative-control suite | Stage 2 | `SPECIFIED` |

### Strategy Research Requirements

| Requirement | Owning specification | Planned verification | Gate | Status |
|---|---|---|---|---|
| RES-001 | [Backtesting Protocol](05-backtesting-and-research.md) | `T-RES-REGISTER-001` unregistered confirmatory run denied | Stage 3 | `SPECIFIED` |
| RES-002 | [Backtesting Protocol](05-backtesting-and-research.md) | `T-RES-TRIAL-002` failed and rejected attempts counted | Stage 2 | `SPECIFIED` |
| RES-003 | [Backtesting Protocol](05-backtesting-and-research.md) | `T-RES-SURFACE-003` full parameter surface retained | Stage 3 | `SPECIFIED` |
| RES-004 | [Backtesting Protocol](05-backtesting-and-research.md) | `T-RES-MULTIPLE-004` correction and DSR golden cases | Stage 3 | `SPECIFIED` |
| RES-005 | [Backtesting Protocol](05-backtesting-and-research.md) | `T-RES-PROMOTE-005` each single failed criterion rejects | Stage 3 | `SPECIFIED` |

### Risk Requirements

| Requirement | Owning specification | Planned verification | Gate | Status |
|---|---|---|---|---|
| RISK-001 | [Risk Specification](03-risk-and-safety.md) | `T-RISK-PRETRADE-001` rejection causes zero adapter calls | Stage 1 | `SPECIFIED` |
| RISK-002 | [Risk Specification](03-risk-and-safety.md) | [Risk engine tests](../tests/test_risk_engine.py) cover every named limit and generated long-only and leverage invariants | Stage 1 | `IMPLEMENTED` |
| RISK-003 | [Risk Specification](03-risk-and-safety.md) | `T-RISK-FRESHNESS-003` missing and stale snapshots fail closed | Stage 1 | `SPECIFIED` |
| RISK-004 | [Risk Specification](03-risk-and-safety.md) | `T-RISK-KILL-004` internal operator and watchdog paths | Stage 1 | `SPECIFIED` |
| RISK-005 | [Architecture](02-architecture.md) and [Risk Specification](03-risk-and-safety.md) | `T-RISK-BYPASS-005` dependency and retry-path enforcement | Stage 1 | `SPECIFIED` |
| RISK-006 | [Risk Specification](03-risk-and-safety.md) | `T-RISK-LIVE-DENY-006` absent approvals and limits deny mode | Stage 5 | `SPECIFIED` |

### Execution Requirements

| Requirement | Owning specification | Planned verification | Gate | Status |
|---|---|---|---|---|
| EXEC-001 | [Execution Specification](06-execution-and-reconciliation.md) | `T-EXEC-ENV-001` endpoint account and mode mismatch denial | Stage 1 | `SPECIFIED` |
| EXEC-002 | [Execution Specification](06-execution-and-reconciliation.md) | `T-EXEC-IDEMPOTENCY-002` retry and restart create one order | Stage 1 | `SPECIFIED` |
| EXEC-003 | [Execution Specification](06-execution-and-reconciliation.md) | `T-EXEC-STATES-003` allowed and forbidden transition suite | Stage 1 | `SPECIFIED` |
| EXEC-004 | [Execution Specification](06-execution-and-reconciliation.md) | `T-EXEC-UNKNOWN-004` timeout before and after acceptance | Stage 1 | `SPECIFIED` |
| EXEC-005 | [Execution Specification](06-execution-and-reconciliation.md) | `T-EXEC-RATE-005` bounded read retry and write protection | Stage 1 | `SPECIFIED` |
| EXEC-006 | [Execution Specification](06-execution-and-reconciliation.md) | `T-EXEC-SESSION-006` calendar boundary denial | Stage 1 | `SPECIFIED` |

### State Requirements

| Requirement | Owning specification | Planned verification | Gate | Status |
|---|---|---|---|---|
| STATE-001 | [Execution Specification](06-execution-and-reconciliation.md) | `T-STATE-INTENT-001` crash around durable intent boundary | Stage 1 | `SPECIFIED` |
| STATE-002 | [Execution Specification](06-execution-and-reconciliation.md) | `T-STATE-STARTUP-002` strategy blocked until reconciliation | Stage 1 | `SPECIFIED` |
| STATE-003 | [Execution Specification](06-execution-and-reconciliation.md) | `T-STATE-DOMAINS-003` position cash order fill comparison | Stage 1 | `SPECIFIED` |
| STATE-004 | [Execution Specification](06-execution-and-reconciliation.md) | `T-STATE-MISMATCH-004` halt and preserve both views | Stage 1 | `SPECIFIED` |
| STATE-005 | [Execution Specification](06-execution-and-reconciliation.md) | `T-STATE-WORKING-005` adopt and cancel policy fixtures | Stage 1 | `SPECIFIED` |
| STATE-006 | [Architecture](02-architecture.md) | `T-STATE-STRATEGY-006` persisted or deterministic reconstruction | Stage 1 | `SPECIFIED` |

### Audit Requirements

| Requirement | Owning specification | Planned verification | Gate | Status |
|---|---|---|---|---|
| AUD-001 | [Operations Runbook](08-operations-and-observability.md) | `T-AUD-DECISION-001` event schema and lineage | Stage 1 | `SPECIFIED` |
| AUD-002 | [Recordkeeping Plan](11-recordkeeping-and-compliance.md) | `T-AUD-FILL-002` complete order and fill export | Stage 1 | `SPECIFIED` |
| AUD-003 | [Operations Runbook](08-operations-and-observability.md) | `T-AUD-DAILY-003` no-trade daily report | Stage 1 | `SPECIFIED` |
| AUD-004 | [Operations Runbook](08-operations-and-observability.md) | `T-AUD-ALERT-004` each required event and two channels | Stage 4 | `SPECIFIED` |
| AUD-005 | [Rollout Plan](10-paper-and-live-rollout.md) | `T-AUD-EVIDENCE-005` separate backtest paper and future series | Stage 4 | `SPECIFIED` |

## Nonfunctional Traceability

### Safety and Reliability Requirements

| Requirement | Owning specification | Planned verification | Gate | Status |
|---|---|---|---|---|
| NFR-SAFE-001 | [Risk Specification](03-risk-and-safety.md) | `T-NFR-FAILCLOSED-001` ambiguity matrix | Stage 1 | `SPECIFIED` |
| NFR-SAFE-002 | [Execution Specification](06-execution-and-reconciliation.md) | `T-NFR-DUPLICATE-002` generated retry and restart sequences | Stage 1 | `SPECIFIED` |
| NFR-REL-001 | [Operations Runbook](08-operations-and-observability.md) | `E-NFR-UPTIME-001` qualifying paper availability report | Stage 4 | `SPECIFIED` |
| NFR-REL-002 | [Rollout Plan](10-paper-and-live-rollout.md) | `E-NFR-RECON-002` zero unexplained break report | Stage 4 | `SPECIFIED` |
| NFR-REL-003 | [Testing Strategy](09-testing-and-quality.md) | `E-NFR-RECOVERY-003` five induced exercise reports | Stage 4 | `SPECIFIED` |

### Reproducibility Requirements

| Requirement | Owning specification | Planned verification | Gate | Status |
|---|---|---|---|---|
| NFR-REP-001 | [Backtesting Protocol](05-backtesting-and-research.md) | `T-NFR-CANONICAL-001` byte-identical result | Stage 2 | `SPECIFIED` |
| NFR-REP-002 | [Operations Runbook](08-operations-and-observability.md) | `T-NFR-LINEAGE-002` 100% artefact identity scan | Stage 2 | `SPECIFIED` |
| NFR-REP-003 | [Market Data Specification](04-data-specification.md) | `T-NFR-IMMUTABLE-003` overwrite denial and revision preservation | Stage 2 | `SPECIFIED` |

### Security Requirements

| Requirement | Owning specification | Planned verification | Gate | Status |
|---|---|---|---|---|
| NFR-SEC-001 | [Security Specification](07-security-and-secrets.md) | `T-NFR-SECRETS-001` canary redaction and repository scan | Stage 1 | `SPECIFIED` |
| NFR-SEC-002 | [Security Specification](07-security-and-secrets.md) | `T-NFR-PRIVILEGE-002` paper namespace and OS permission check | Stage 1 | `SPECIFIED` |
| NFR-SEC-003 | [Security Specification](07-security-and-secrets.md) | `T-NFR-DEPENDENCY-003` lock inventory and vulnerability policy | Stage 1 | `SPECIFIED` |
| NFR-SEC-004 | [Security Specification](07-security-and-secrets.md) | `T-NFR-REDACTION-004` nested payload and exception canaries | Stage 1 | `SPECIFIED` |

### Performance Requirements

| Requirement | Owning specification | Planned verification | Gate | Status |
|---|---|---|---|---|
| NFR-PERF-001 | [Requirements Specification](01-requirements.md) | `B-NFR-DECISION-001` reference allowlist under 60 seconds | Stage 1 | `SPECIFIED` |
| NFR-PERF-002 | [Requirements Specification](01-requirements.md) | `B-NFR-RISK-002` local risk p95 under 100 milliseconds | Stage 1 | `SPECIFIED` |
| NFR-PERF-003 | [Requirements Specification](01-requirements.md) | `B-NFR-BACKTEST-003` ten-year reference under 5 minutes | Stage 1 | `SPECIFIED` |

Performance checks are initial operating budgets, not optimization mandates. Measured correctness and safety remain gating.

### Maintainability Requirements

| Requirement | Owning specification | Planned verification | Gate | Status |
|---|---|---|---|---|
| NFR-MNT-001 | [Architecture](02-architecture.md) | `T-NFR-DEPENDENCY-001` module import-boundary test | Stage 1 | `SPECIFIED` |
| NFR-MNT-002 | [Requirements Specification](01-requirements.md) | `T-NFR-CONFIG-002` version unknown-key and missing-field tests | Stage 1 | `SPECIFIED` |
| NFR-MNT-003 | [Delivery Roadmap](12-delivery-roadmap.md) | `E-NFR-CHANGE-003` work-item documentation and test checklist | Every release | `SPECIFIED` |
| NFR-MNT-004 | [Operations Runbook](08-operations-and-observability.md) | `T-NFR-SCHEMA-004` reason-code and schema compatibility tests | Stage 1 | `SPECIFIED` |

## Stage Gate Coverage

| Gate | Requirement groups | Additional evidence |
|---|---|---|
| Stage 0 | Charter decisions rather than implementation requirements | Owner sign-off and external feasibility checks |
| Stage 1 | DATA-001 through DATA-005 and DATA-007; BT-001 and BT-004; all RISK, EXEC, and STATE except future activation; AUD-001 through AUD-003; applicable NFR rows | Kill, watchdog, paper order, crash, reconciliation, report |
| Stage 2 | DATA-006; BT-002 through BT-003 and BT-005 through BT-007; RES-002; reproducibility NFR rows | Full sanity, cost, walk-forward, experiment evidence |
| Stage 3 | RES-001 and RES-003 through RES-005 | Candidate registration and quantitative promotion bundle |
| Stage 4 | AUD-004 through AUD-005 and reliability observation rows | Three qualifying months and five recovery exercises |
| Stage 5 | RISK-006 plus refreshed security, operations, recordkeeping, and owner approvals | Separate activation decision; no current verification claimed |

## Current Coverage Gaps

Documentation coverage is complete for the current 61 requirements. Implementation has begun with fail-closed mode configuration, the pure pre-trade risk engine, operator kill assessment, and heartbeat health. Only RISK-002 is marked implemented because the broader startup, broker, reconciliation, and release evidence required by other rows is not complete. External blockers are:

- Owner approval of Stage 0 scope, weekly capacity, and base currency.
- Exact ETF and market-data provider selection.
- Broker eligibility and API terms confirmation.
- Paper reference equity and capital-dependent paper risk values.
- Secret provider, runtime directory, alerts, backup, and retention decisions.
- Point-in-time broad-universe data before promotable cross-sectional research.
- Qualified UK tax confirmation and exact owner loss boundaries before Stage 5.

These gaps remain visible in the charter and decision log; they are not filled with guessed defaults.

## Maintenance Rules

1. Add a matrix row in the same change as each new requirement.
2. Keep requirement IDs stable when wording is clarified; create a new ID for materially different behavior.
3. Link actual test or exercise artefacts when implemented rather than replacing planned IDs silently.
4. Change status to `VERIFIED` only for a named release whose evidence passes.
5. Demote status and identify affected releases when a defect invalidates evidence.
6. Review every row at each stage gate and reject blank or inherited statuses.
7. Keep future Stage 5 requirements specified but clearly unverified and unauthorized.
