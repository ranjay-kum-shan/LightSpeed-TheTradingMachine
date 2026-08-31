# Stage Gate Review Template

<details open>
<summary><b>Contents</b></summary>

- [Review Identity](#review-identity)
- [Requested Transition](#requested-transition)
- [Evidence Identities](#evidence-identities)
- [Prerequisites](#prerequisites)
- [Requirements Coverage](#requirements-coverage)
- [Quantitative Criteria](#quantitative-criteria)
- [Safety Security and Operations](#safety-security-and-operations)
- [External Confirmations](#external-confirmations)
- [Open Incidents and Limitations](#open-incidents-and-limitations)
- [Evidence Validity](#evidence-validity)
- [Decision](#decision)
- [Clock and Next Action](#clock-and-next-action)
- [Approvals](#approvals)

</details>

---

**Gate review ID:** `GATE-TBD`  
**Current stage:** `TBD`  
**Requested stage:** `TBD`  
**Review date:** `TBD`  
**Status:** `DRAFT`  
**Current authorization:** `PAPER_ONLY`  
**Default gate result:** `REMAIN`  
**No gate pass is recorded:** `YES`

## Review Identity

| Field | Value |
|---|---|
| Project charter version | `TBD` |
| Gate criteria version | `TBD` |
| Owner | `TBD` |
| Evidence cutoff UTC | `TBD` |
| Candidate or strategy if applicable | `TBD` |
| Account fingerprint if applicable | `TBD` |

## Requested Transition

State the exact requested transition and capability. A gate pass authorizes only that scope.

**Request:** `TBD`  
**Explicit exclusions:** `TBD`  
**Requested effective window or expiry:** `TBD`

## Evidence Identities

| Evidence | Immutable identity or hash | Validated |
|---|---|---|
| Source release manifest | `TBD` | `TBD` |
| Environment lock | `TBD` | `TBD` |
| Effective configuration | `TBD` | `TBD` |
| Strategy and risk profiles | `TBD` | `TBD` |
| Data manifests and calendar | `TBD` | `TBD` |
| Test and fault-exercise bundle | `TBD` | `TBD` |
| Research or paper reports | `TBD` | `TBD` |
| Reconciliation reports | `TBD` | `TBD` |
| Security dependency and backup evidence | `TBD` | `TBD` |

## Prerequisites

| Prerequisite | Required evidence | Result | Blocking gap |
|---|---|---|---|
| Prior gate signed | `TBD` | `NOT_MET` | `TBD` |
| Required owner decisions accepted | `TBD` | `NOT_MET` | `TBD` |
| Applicable documentation current | `TBD` | `NOT_MET` | `TBD` |
| Required external access and terms verified | `TBD` | `NOT_MET` | `TBD` |
| No unresolved kill halt or reconciliation state | `TBD` | `NOT_MET` | `TBD` |

## Requirements Coverage

| Requirement group | Applicable rows | Verified rows | Invalid or blocked rows | Result |
|---|---|---|---|---|
| Market data | `TBD` | `TBD` | `TBD` | `NOT_MET` |
| Backtesting and research | `TBD` | `TBD` | `TBD` | `NOT_MET` |
| Risk and execution | `TBD` | `TBD` | `TBD` | `NOT_MET` |
| State and audit | `TBD` | `TBD` | `TBD` | `NOT_MET` |
| Nonfunctional | `TBD` | `TBD` | `TBD` | `NOT_MET` |

Link the exact release-specific traceability snapshot: `TBD`.

## Quantitative Criteria

Copy every mandatory criterion for the requested gate without renaming or omitting rows.

| Criterion | Threshold fixed before observation | Observed | Uncertainty or duration | Result |
|---|---|---|---|---|
| `TBD` | `TBD` | `TBD` | `TBD` | `NOT_MET` |

One `NOT_MET`, `INVALID`, or blank mandatory row prevents a pass. Weighted scoring and manual compensation are prohibited.

## Safety Security and Operations

| Control | Required result | Evidence | Result |
|---|---|---|---|
| Fail-closed mode and endpoint guard | Passing | `TBD` | `NOT_MET` |
| Hard risk limits and kill controls | Passing | `TBD` | `NOT_MET` |
| Idempotency and unknown-outcome recovery | Passing | `TBD` | `NOT_MET` |
| Startup and close reconciliation | Passing | `TBD` | `NOT_MET` |
| Heartbeat watchdog and alerts | Passing | `TBD` | `NOT_MET` |
| Secret redaction and credential review | Passing | `TBD` | `NOT_MET` |
| Backup restore and rollback | Passing | `TBD` | `NOT_MET` |
| Required runbooks exercised | Passing | `TBD` | `NOT_MET` |

## External Confirmations

| Confirmation | Required for this gate | Reviewer or protected reference | As-of or expiry | Result |
|---|---|---|---|---|
| Broker eligibility terms and account status | `TBD` | `TBD` | `TBD` | `NOT_MET` |
| Market-data rights | `TBD` | `TBD` | `TBD` | `NOT_MET` |
| UK tax and recordkeeping advice | `TBD` | `TBD` | `TBD` | `NOT_MET` |
| Owner capital and loss approval | `TBD` | `TBD` | `TBD` | `NOT_MET` |

Professional and protected personal details are referenced, not copied into this report.

## Open Incidents and Limitations

| Incident limitation or discrepancy | Severity | Affected evidence | Blocking | Resolution |
|---|---|---|---|---|
| `TBD` | `TBD` | `TBD` | `YES` or `NO` | `TBD` |

Explain why each non-blocking item cannot reverse the decision or create unsafe exposure.

## Evidence Validity

- Data revisions since evidence creation: `TBD`
- Engine or adapter defects since evidence creation: `TBD`
- Strategy, parameter, cost, execution, or risk changes: `TBD`
- Trial-family or multiple-testing changes: `TBD`
- Sessions or runs invalidated: `TBD`
- Required evidence regenerated: `TBD`

**Evidence remains valid:** `NO` until reviewed.

## Decision

Select exactly one result appropriate to the gate:

- `PASS`: every mandatory row passes for the defined scope.
- `REMAIN`: evidence is incomplete or a criterion failed without requiring demotion.
- `RESET_CLOCK`: observation must restart after correction.
- `DEMOTE`: an earlier capability or evidence layer must be revalidated.
- `ABANDON`: a charter stop condition applies.
- `INVALID`: the evidence cannot answer the gate question.

**Mechanical criterion result:** `NOT_MET`  
**Final decision:** `REMAIN`  
**Authorized capability:** `NONE_ADDED`  
**Decision rationale:** `TBD`

## Clock and Next Action

| Field | Value |
|---|---|
| Observation clock action | Continue, reset, stop, or not applicable |
| Effective clock start | `TBD` |
| Next blocking action | `TBD` |
| Owner | `TBD` |
| Due or review date | `TBD` |
| Demoted or invalidated release if applicable | `TBD` |

## Approvals

| Role | Name or protected reference | Decision | Date |
|---|---|---|---|
| Project owner | `TBD` | `APPROVE_DECISION` or `REJECT_DECISION` | `TBD` |
| Required technical or professional reviewer | `TBD` | `REVIEWED`, `APPROVE`, `REJECT`, or `NOT_APPLICABLE` | `TBD` |

**Immutable review hash:** `TBD`  
**Supersedes:** `None`
