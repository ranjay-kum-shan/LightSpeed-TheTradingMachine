# Incident Report Template

<details open>
<summary><b>Contents</b></summary>

- [Incident Identity](#incident-identity)
- [Summary](#summary)
- [Current Safe State](#current-safe-state)
- [Impact](#impact)
- [Timeline](#timeline)
- [Detection](#detection)
- [Evidence Preserved](#evidence-preserved)
- [Technical Analysis](#technical-analysis)
- [Root Cause](#root-cause)
- [Response and Recovery](#response-and-recovery)
- [Broker and State Reconciliation](#broker-and-state-reconciliation)
- [Corrective Actions](#corrective-actions)
- [Regression Evidence](#regression-evidence)
- [Evidence Invalidation](#evidence-invalidation)
- [Resume Criteria](#resume-criteria)
- [Review and Closure](#review-and-closure)

</details>

---

**Incident ID:** `INC-TBD`  
**Detected at UTC:** `TBD`  
**Mode:** `TBD`  
**Severity:** `TBD`  
**Status:** `OPEN`  
**Current incident status:** `OPEN`  
**Owner:** `TBD`

> Do not place credentials, authorization headers, full account numbers, personal tax data, or unredacted provider payloads in this report. Link protected evidence by hash or restricted reference.

## Incident Identity

| Field | Value |
|---|---|
| Incident type | `ORDER`, `RISK`, `RECONCILIATION`, `DATA`, `SECURITY`, `OPERATIONS`, `EVIDENCE`, or `TBD` |
| First affected session or run | `TBD` |
| First affected release | `TBD` |
| Detection source | `TBD` |
| Correlation IDs | `TBD` |
| Broker account fingerprint if applicable | `TBD` |
| Operator kill activated | `YES`, `NO`, or `NOT_APPLICABLE` |

## Summary

In plain language, state what happened, how it was detected, the maximum credible impact, and whether exposure or evidence remains uncertain.

**Summary:** `TBD`

## Current Safe State

| Control | State | Verified at UTC | Evidence |
|---|---|---|---|
| New strategy orders | `DENIED` or `TBD` | `TBD` | `TBD` |
| Working orders | `TBD` | `TBD` | `TBD` |
| Positions | `TBD` | `TBD` | `TBD` |
| Broker connectivity | `TBD` | `TBD` | `TBD` |
| Reconciliation | `PASS`, `FAIL`, or `UNKNOWN` | `TBD` | `TBD` |
| Operator kill | `PRESENT`, `CLEAR`, or `TBD` | `TBD` | `TBD` |
| Credentials | `VALID`, `ROTATED`, `REVOKED`, `SUSPECT`, or `TBD` | `TBD` | `TBD` |

If any broker fact is unknown, the incident remains open and operation remains halted.

## Impact

| Area | Actual impact | Worst credible impact | Confidence |
|---|---|---|---|
| Orders and fills | `TBD` | `TBD` | `TBD` |
| Positions and exposure | `TBD` | `TBD` | `TBD` |
| Cash PnL and costs | `TBD` | `TBD` | `TBD` |
| Data integrity | `TBD` | `TBD` | `TBD` |
| Research or paper evidence | `TBD` | `TBD` | `TBD` |
| Credential or personal data | `TBD` | `TBD` | `TBD` |
| Availability | `TBD` | `TBD` | `TBD` |

Report currencies, mark times, and uncertainty explicitly. Do not describe simulated paper loss as real financial loss.

## Timeline

Use UTC and separate event occurrence from discovery.

| UTC time | Actor or component | Event | Evidence ID |
|---|---|---|---|
| `TBD` | `TBD` | `TBD` | `TBD` |

Include last known good state, first bad event, detection, halt, broker inspection, recovery actions, reconciliation, and closure decision.

## Detection

- Expected detector: `TBD`
- Actual detector: `TBD`
- Detection delay: `TBD`
- Alert delivery and acknowledgement: `TBD`
- Why earlier controls did or did not detect it: `TBD`

## Evidence Preserved

| Evidence | Immutable or restricted reference | Hash | Access |
|---|---|---|---|
| Audit events | `TBD` | `TBD` | `TBD` |
| Intent order fill and ledger state | `TBD` | `TBD` | `TBD` |
| Broker queries or statements | `TBD` | `TBD` | Restricted |
| Config and release manifest | `TBD` | `TBD` | `TBD` |
| Dataset and calendar | `TBD` | `TBD` | `TBD` |
| Watchdog and alert events | `TBD` | `TBD` | `TBD` |
| Crash or error evidence after redaction | `TBD` | `TBD` | Restricted |

Preservation must not spread exposed secrets. Rotate first where necessary and store only sanitized evidence in normal reports.

## Technical Analysis

Describe the expected control flow, actual event sequence, violated invariant, and why defenses allowed or contained it.

```text
expected: TBD
actual: TBD
first invariant violation: TBD
containment behavior: TBD
```

## Root Cause

Separate causes:

| Category | Finding | Evidence |
|---|---|---|
| Direct technical cause | `TBD` | `TBD` |
| Contributing design or process cause | `TBD` | `TBD` |
| Detection gap | `TBD` | `TBD` |
| Recovery gap | `TBD` | `TBD` |

Avoid "human error" as a root cause. Explain what system condition made the action unsafe or undetectable.

## Response and Recovery

| Action | Owner | UTC time | Result | Evidence |
|---|---|---|---|---|
| Stop new exposure | `TBD` | `TBD` | `TBD` | `TBD` |
| Inspect or cancel working orders | `TBD` | `TBD` | `TBD` | `TBD` |
| Reconcile broker and internal state | `TBD` | `TBD` | `TBD` | `TBD` |
| Rotate or revoke credentials if applicable | `TBD` | `TBD` | `TBD` | `TBD` |
| Preserve evidence | `TBD` | `TBD` | `TBD` | `TBD` |
| Restore or repair | `TBD` | `TBD` | `TBD` | `TBD` |

Manual broker actions are first-class events and must appear in reconciliation.

## Broker and State Reconciliation

| Domain | Internal view | Broker view | Difference | Resolution event |
|---|---|---|---|---|
| Account and mode | `TBD` | `TBD` | `TBD` | `TBD` |
| Positions | `TBD` | `TBD` | `TBD` | `TBD` |
| Cash and equity | `TBD` | `TBD` | `TBD` | `TBD` |
| Orders | `TBD` | `TBD` | `TBD` | `TBD` |
| Fills | `TBD` | `TBD` | `TBD` | `TBD` |

**Final reconciliation result:** `PASS`, `FAIL`, or `UNKNOWN`  
**Final reconciliation ID:** `TBD`

## Corrective Actions

| Action ID | Action | Type | Owner | Due | Blocking | Status |
|---|---|---|---|---|---|---|
| `CA-TBD` | `TBD` | Code, test, config, documentation, provider, process, or credential | `TBD` | `TBD` | `YES` or `NO` | `OPEN` |

Correct the owning abstraction and add defense in depth where proportional. Do not close on a workaround that leaves the violated invariant possible.

## Regression Evidence

| Test or exercise | Reproduces original failure | Proves correction | Result | Artefact |
|---|---|---|---|---|
| `TBD` | `TBD` | `TBD` | `TBD` | `TBD` |

Include the focused regression, affected component suite, relevant fault injection, and release gates.

## Evidence Invalidation

| Evidence set | Affected range | Decision | Reason | Replacement |
|---|---|---|---|---|
| Backtests | `TBD` | Keep, rerun, or invalidate | `TBD` | `TBD` |
| Research promotion | `TBD` | Keep, review, or revoke | `TBD` | `TBD` |
| Paper observation | `TBD` | Keep, exclude, or reset clock | `TBD` | `TBD` |
| Release acceptance | `TBD` | Keep or revoke | `TBD` | `TBD` |

## Resume Criteria

Reconciliation must pass before any resume decision. An unresolved or unknown broker state keeps operation halted.

- [ ] New exposure remains blocked until all blocking actions close.
- [ ] Broker account orders fills positions and cash fully reconcile.
- [ ] Credentials are safe or rotated and old credentials are revoked.
- [ ] Focused regression and affected release gates pass.
- [ ] Required evidence has been invalidated or regenerated.
- [ ] Runbooks and specifications reflect learned provider or system behavior.
- [ ] Operator kill reset is explicit and audited.
- [ ] Owner approves the exact paper release and next session.

Additional incident-specific criteria: `TBD`.

## Review and Closure

| Role | Name | Decision | Date |
|---|---|---|---|
| Incident owner | `TBD` | `CLOSE`, `REMAIN_OPEN`, or `ABANDON` | `TBD` |
| Project owner | `TBD` | `RESUME_PAPER`, `REMAIN_HALTED`, `DEMOTE`, or `ABANDON` | `TBD` |

**Closed at UTC:** `TBD`  
**Superseding decision or release:** `TBD`