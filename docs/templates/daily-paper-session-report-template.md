# Daily Paper Session Report Template

<details open>
<summary><b>Contents</b></summary>

- [Session Identity](#session-identity)
- [Release and Lineage](#release-and-lineage)
- [Preflight](#preflight)
- [Data Readiness](#data-readiness)
- [Strategy Decision](#strategy-decision)
- [Risk Decisions](#risk-decisions)
- [Orders and Fills](#orders-and-fills)
- [Positions Cash and Performance](#positions-cash-and-performance)
- [Costs and Slippage](#costs-and-slippage)
- [Operational Health](#operational-health)
- [Alerts and Incidents](#alerts-and-incidents)
- [Reconciliation](#reconciliation)
- [Session Result](#session-result)
- [Delivery](#delivery)

</details>

---

**Report ID:** `DAILY-TBD`  
**Exchange session date:** `TBD`  
**Mode:** `PAPER`  
**Status:** `NOT_RUN`  
**Generated at UTC:** `TBD`

## Session Identity

| Field | Value |
|---|---|
| Session ID | `TBD` |
| Exchange and calendar version | `TBD` |
| Expected session type | Regular, half-day, holiday, or `TBD` |
| Account fingerprint | `TBD` |
| Strategy and version | `TBD` |
| Process and watchdog instances | `TBD` |

## Release and Lineage

| Input | Identity |
|---|---|
| Release manifest | `TBD` |
| Git revision | `TBD` |
| Environment lock | `TBD` |
| Effective configuration | `TBD` |
| Risk profile | `TBD` |
| Dataset manifest and content hash | `TBD` |
| Instrument registry | `TBD` |

## Preflight

| Check | Result | Evidence or reason code |
|---|---|---|
| Explicit paper mode | `NOT_RUN` | `TBD` |
| Exact endpoint and account | `NOT_RUN` | `TBD` |
| Credential namespace | `NOT_RUN` | `TBD` |
| Single-writer lock | `NOT_RUN` | `TBD` |
| Operator kill clear | `NOT_RUN` | `TBD` |
| Watchdog healthy | `NOT_RUN` | `TBD` |
| Clock offset acceptable | `NOT_RUN` | `TBD` |
| Disk and durable state writable | `NOT_RUN` | `TBD` |
| Startup reconciliation | `NOT_RUN` | `TBD` |

Any failed mandatory preflight keeps the session out of `RUNNING`.

## Data Readiness

| Check | Observed | Threshold or expected | Result |
|---|---|---|---|
| Expected latest session present | `TBD` | `TBD` | `NOT_RUN` |
| Data available at UTC | `TBD` | Before decision cutoff | `NOT_RUN` |
| Data age | `TBD` | `TBD` | `NOT_RUN` |
| Twelve validation rules | `TBD` | All pass | `NOT_RUN` |
| Corporate actions current | `TBD` | Through next order boundary | `NOT_RUN` |
| Provider revision | `TBD` | None unresolved | `NOT_RUN` |

## Strategy Decision

| Field | Value |
|---|---|
| Decision ID and UTC | `TBD` |
| As-of cutoff | `TBD` |
| Input feature identity | `TBD` |
| Current signal or target | `TBD` |
| Prior target | `TBD` |
| Decision | `BUY`, `SELL`, `HOLD`, `NO_TRADE`, or `NOT_RUN` |
| Reason code | `TBD` |
| Earliest order eligibility | `TBD` |

A no-trade day must identify strategy neutrality, closed market, invalid data, risk denial, halt, or another stable reason.

## Risk Decisions

| Risk decision ID | Intent | Result | Binding rule | Observed | Limit | Snapshot as-of |
|---|---|---|---|---|---|---|
| `TBD` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` |

| Session risk measure | Start | End or current | Limit | Status |
|---|---|---|---|---|
| Gross exposure | `TBD` | `TBD` | `TBD` | `TBD` |
| Net exposure | `TBD` | `TBD` | `TBD` | `TBD` |
| Daily PnL | `TBD` | `TBD` | `TBD` | `TBD` |
| Drawdown | `TBD` | `TBD` | `TBD` | `TBD` |
| Orders in rolling window | `TBD` | `TBD` | `TBD` | `TBD` |

## Orders and Fills

| Logical and client order IDs | Symbol | Side and quantity | Type and terms | Broker state | Filled | Average price | Reason |
|---|---|---|---|---|---|---|---|
| `TBD` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` |

| Fill ID | UTC time | Quantity | Price | Fees | FX | Slippage basis points |
|---|---|---|---|---|---|---|
| `TBD` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` |

**Unknown outcomes:** `TBD`  
**Rejects partial fills cancels or expires:** `TBD`

## Positions Cash and Performance

| Measure | Session start | Session end | Change | Broker reconciled |
|---|---|---|---|---|
| Cash by currency | `TBD` | `TBD` | `TBD` | `TBD` |
| Net liquidation value | `TBD` | `TBD` | `TBD` | `TBD` |
| Daily PnL | `TBD` | `TBD` | `TBD` | `TBD` |

| Instrument | Start quantity | End quantity | End mark | Unrealized PnL | Realized PnL |
|---|---|---|---|---|---|
| `TBD` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` |

## Costs and Slippage

| Measure | Modeled | Paper observed | Difference | Tolerance | Status |
|---|---|---|---|---|---|
| Fill price | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` |
| Spread and slippage | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` |
| Commission and fees | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` |
| FX conversion | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` |

## Operational Health

| Indicator | Observed | Target | Result |
|---|---|---|---|
| Eligible market-hours uptime | `TBD` | At least 99% over qualifying period | `TBD` |
| Heartbeat maximum age | `TBD` | `TBD` | `TBD` |
| Broker disconnects and duration | `TBD` | `TBD` | `TBD` |
| Data retrieval duration | `TBD` | `TBD` | `TBD` |
| Decision completion time | `TBD` | Before latest-submit cutoff | `TBD` |
| Disk and backup status | `TBD` | Healthy | `TBD` |

## Alerts and Incidents

| Alert or incident ID | Severity | Reason code | UTC time | Safe-state action | Status |
|---|---|---|---|---|---|
| `TBD` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` |

**Unacknowledged critical alerts:** `TBD`

## Reconciliation

Both startup reconciliation and close reconciliation are mandatory for an operated paper session.

| Trigger | Reconciliation ID | Account | Positions | Cash | Orders | Fills | Overall |
|---|---|---|---|---|---|---|---|
| Startup | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` |
| Session close | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` |

**Unexplained breaks:** `TBD`

## Session Result

| Outcome | Value |
|---|---|
| Final runtime state | `TBD` |
| Expected session report complete | `NO` until every mandatory section is populated |
| Qualifies for Stage 4 observation | `NO` until evaluated |
| Clock-reset trigger | `TBD` |
| Open action | `TBD` |

**Overall status:** `NOT_RUN`  
**Next permitted action:** `TBD`

## Delivery

| Channel | Sent at UTC | Acknowledged | Result |
|---|---|---|---|
| Primary | `TBD` | `TBD` | `TBD` |
| Secondary if required | `TBD` | `TBD` | `TBD` |

**Canonical report hash:** `TBD`
