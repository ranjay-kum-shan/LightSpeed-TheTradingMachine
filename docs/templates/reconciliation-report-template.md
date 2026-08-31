# Reconciliation Report Template

<details open>
<summary><b>Contents</b></summary>

- [Identity](#identity)
- [Trigger and Scope](#trigger-and-scope)
- [Source Evidence](#source-evidence)
- [Account Verification](#account-verification)
- [Position Comparison](#position-comparison)
- [Cash and Equity Comparison](#cash-and-equity-comparison)
- [Order Comparison](#order-comparison)
- [Fill Comparison](#fill-comparison)
- [Unknown Outcomes](#unknown-outcomes)
- [Discrepancies](#discrepancies)
- [Resolution Events](#resolution-events)
- [Final Result](#final-result)
- [Review](#review)

</details>

---

**Reconciliation ID:** `RECON-TBD`  
**Triggered at UTC:** `TBD`  
**Mode:** `PAPER`  
**Session ID:** `TBD`  
**Status:** `NOT_RUN`  
**Initial reconciliation status:** `NOT_RUN`  
**New strategy orders are denied until reconciliation passes:** `YES`

> This template stores normalized and redacted comparison evidence. Do not paste credentials, authorization data, full account numbers, or unredacted broker payloads.

## Identity

| Field | Value |
|---|---|
| Process or recovery instance | `TBD` |
| Release ID and git revision | `TBD` |
| Effective configuration hash | `TBD` |
| Account fingerprint | `TBD` |
| Broker adapter version | `TBD` |
| Internal schema version | `TBD` |
| Owner or automated initiator | `TBD` |

## Trigger and Scope

Select all applicable triggers:

- [ ] Startup before strategy evaluation
- [ ] Reconnect or stream gap
- [ ] Unknown submission or cancel outcome
- [ ] Partial fill or unexpected reject
- [ ] Before or after recovery action
- [ ] Session close
- [ ] Operator request

**Covered broker query interval with overlap:** `TBD`  
**Pagination completed:** `TBD`  
**Included domains:** account, positions, cash, orders, and fills unless a documented non-trading scope applies.

## Source Evidence

| Source | As-of or retrieval UTC | Immutable or restricted reference | Hash or cursor |
|---|---|---|---|
| Internal intent and order journal | `TBD` | `TBD` | `TBD` |
| Internal fill journal | `TBD` | `TBD` | `TBD` |
| Internal ledger checkpoint and replay | `TBD` | `TBD` | `TBD` |
| Broker account response | `TBD` | `TBD` | `TBD` |
| Broker positions | `TBD` | `TBD` | `TBD` |
| Broker open and historical orders | `TBD` | `TBD` | `TBD` |
| Broker fills or activities | `TBD` | `TBD` | `TBD` |

## Account Verification

| Field | Approved or internal | Broker | Match | Action |
|---|---|---|---|---|
| Environment | `PAPER` | `TBD` | `TBD` | `TBD` |
| Account fingerprint | `TBD` | `TBD` | `TBD` | `TBD` |
| Account status | `TBD` | `TBD` | `TBD` | `TBD` |
| Base or account currency | `TBD` | `TBD` | `TBD` | `TBD` |
| Relevant trading permissions | `TBD` | `TBD` | `TBD` | `TBD` |

Any account or environment mismatch produces a hard halt.

## Position Comparison

| Instrument ID | Symbol | Internal quantity | Broker quantity | Tolerance | Difference | Result |
|---|---|---|---|---|---|---|
| `TBD` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` |

**Unexpected broker-only positions:** `TBD`  
**Unexpected internal-only positions:** `TBD`

## Cash and Equity Comparison

| Currency or measure | Internal | Broker | Tolerance | Difference | Explanation | Result |
|---|---|---|---|---|---|---|
| Cash `TBD` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` |
| Net liquidation value | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` |
| Buying power or approved equivalent | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` |

Differences from settlement, FX, rounding, or broker marks require an explicit approved tolerance and evidence; they are not silently ignored.

## Order Comparison

| Client order ID | Broker order ID | Internal state | Broker state | Total | Filled | Remaining | Terms match | Result |
|---|---|---|---|---|---|---|---|---|
| `TBD` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` |

**Broker-only orders:** `TBD`  
**Internal-only submitted orders:** `TBD`  
**Unknown broker statuses:** `TBD`

## Fill Comparison

| Broker fill ID | Client order ID | Internal quantity and price | Broker quantity and price | Fees | Duplicate or missing | Result |
|---|---|---|---|---|---|---|
| `TBD` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` |

**Broker fills missing internally:** `TBD`  
**Internal fills missing at broker:** `TBD`

## Unknown Outcomes

| Intent or attempt ID | Client order ID | Ambiguous event | Queries performed | Resolution | Blocking |
|---|---|---|---|---|---|
| `TBD` | `TBD` | `TBD` | Client ID, overlapping orders, and fills | `TBD` | `YES` |

Every unknown outcome must resolve before reconciliation can pass.

## Discrepancies

| Discrepancy ID | Domain | Internal fact | Broker fact | Severity | Reason code | Status |
|---|---|---|---|---|---|---|
| `DISC-TBD` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` | `OPEN` |

Do not mutate either historical view to remove a discrepancy. Corrections are new linked events.

## Resolution Events

| Discrepancy ID | Resolution action | Actor | UTC time | Evidence | Regression required |
|---|---|---|---|---|---|
| `TBD` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` |

Manual broker actions, statement corrections, mapping changes, and internal correction events are all recorded.

## Final Result

| Domain | Result | Unresolved count |
|---|---|---|
| Account and environment | `NOT_RUN` | `TBD` |
| Positions | `NOT_RUN` | `TBD` |
| Cash and equity | `NOT_RUN` | `TBD` |
| Orders | `NOT_RUN` | `TBD` |
| Fills | `NOT_RUN` | `TBD` |
| Unknown outcomes | `NOT_RUN` | `TBD` |

**Overall result:** `NOT_RUN`  
**Required runtime state:** `RECOVERY` until overall result is `PASS`  
**New strategy orders permitted:** `NO`

## Review

| Role | Name or component | Decision | UTC time |
|---|---|---|---|
| Reconciler | `TBD` | `PASS` or `FAIL` | `TBD` |
| Owner for any discrepancy | `TBD` | `ACKNOWLEDGE`, `REMAIN_HALTED`, or `APPROVE_CORRECTION` | `TBD` |

**Report hash:** `TBD`
