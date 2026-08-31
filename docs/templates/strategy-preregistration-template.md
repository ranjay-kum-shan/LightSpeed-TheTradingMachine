# Strategy Preregistration Template

<details open>
<summary><b>Contents</b></summary>

- [Identity](#identity)
- [Research Question](#research-question)
- [Economic Thesis](#economic-thesis)
- [Falsification Conditions](#falsification-conditions)
- [Evidence Class](#evidence-class)
- [Universe and Data](#universe-and-data)
- [Information Timeline](#information-timeline)
- [Signal Definition](#signal-definition)
- [Portfolio and Position Sizing](#portfolio-and-position-sizing)
- [Order and Fill Policy](#order-and-fill-policy)
- [Risk Profile](#risk-profile)
- [Cost Assumptions](#cost-assumptions)
- [Train Validation and Test Design](#train-validation-and-test-design)
- [Parameters and Trial Family](#parameters-and-trial-family)
- [Metrics and Promotion Thresholds](#metrics-and-promotion-thresholds)
- [Robustness Plan](#robustness-plan)
- [Known Limitations](#known-limitations)
- [Registration Lock](#registration-lock)
- [Approval](#approval)

</details>

---

**Candidate ID:** `EXP-TBD`  
**Strategy ID and version:** `TBD`  
**Family:** `TBD`  
**Author:** `TBD`  
**Registration UTC:** `TBD`  
**Status:** `DRAFT`  
**Evidence class:** `EXPLORATORY` until locked

## Identity

| Field | Value |
|---|---|
| Candidate name | `TBD` |
| Parent candidate or prior trial family | `TBD` |
| Repository revision | `TBD` |
| Strategy configuration hash | `TBD` |
| Planned engine version | `TBD` |
| Owner | `TBD` |

## Research Question

State one falsifiable question. Example structure: "Does `[predefined signal]` applied to `[point-in-time universe]` at `[decision time]` produce positive out-of-sample expectancy after `[complete cost model]` over `[frozen period and walk-forward design]`?"

## Economic Thesis

Describe before testing:

- The risk premium, structural constraint, or behavioral mechanism.
- Who or what is plausibly on the other side of the trade.
- Why that counterparty may continue accepting the transfer.
- Why the effect should survive realistic costs.
- Why the selected horizon and universe fit the mechanism.
- Published or primary evidence used only as context, not proof.

**Thesis:** `TBD`

## Falsification Conditions

List observations that would make the thesis wrong or unusable, not merely make one backtest unattractive.

| Condition | Measurement | Required response |
|---|---|---|
| `TBD` | `TBD` | Reject, revise into a new candidate, or gather specified evidence |
| `TBD` | `TBD` | `TBD` |

## Evidence Class

Select exactly one planned class:

- `MACHINERY`: engine behavior only; never promotion evidence.
- `EXPLORATORY`: may guide a new frozen registration.
- `CONFIRMATORY_OOS`: eligible for a promotion decision if every contract passes.

**Selected class:** `TBD`  
**Why this class is valid:** `TBD`

## Universe and Data

| Field | Registered value |
|---|---|
| Instrument universe | `TBD` |
| Membership rule and known-at semantics | `TBD` |
| Inclusion and exclusion filters | `TBD` |
| Data provider and product | `TBD` |
| Dataset manifest IDs or frozen selection rule | `TBD` |
| Calendar and version | `TBD` |
| Corporate-action policy and version | `TBD` |
| Raw versus adjusted fields by use | `TBD` |
| Data quality state required | `PUBLISHED` unless explicitly machinery-only |
| Survivorship and revision limitations | `TBD` |

## Information Timeline

| Event | Registered timestamp rule |
|---|---|
| Feature input available | `TBD` |
| Decision time | `TBD` |
| Earliest order eligibility | `TBD` |
| Earliest fill eligibility | No earlier than the next eligible session for a complete daily-bar signal |
| Rebalance or evaluation schedule | `TBD` |
| Maximum tolerated data age | `TBD` |

Explain how the design prevents same-bar fills, future constituents, restated inputs, and cross-sectional publication leakage: `TBD`.

## Signal Definition

Provide formulas or pseudocode detailed enough for independent implementation:

```text
inputs: TBD
warm-up: TBD
transformations: TBD
signal: TBD
missing-input behavior: reject or no-trade under TBD rule
```

State whether each feature is fitted and where fitting occurs: `TBD`.

## Portfolio and Position Sizing

| Field | Registered value |
|---|---|
| Long or short eligibility | `TBD` |
| Target construction | `TBD` |
| Sizing method | `TBD` |
| Volatility lookback and timing | `TBD` |
| Gross and net target | `TBD` |
| Concentration rule | `TBD` |
| Cash treatment | `TBD` |
| Rebalance threshold | `TBD` |

Sizing cannot rely on information later than the decision cutoff.

## Order and Fill Policy

| Field | Registered value |
|---|---|
| Order type | `TBD` |
| Time in force | `TBD` |
| Submission window | `TBD` |
| Fill model and version | `TBD` |
| Spread model | `TBD` |
| Slippage and impact model | `TBD` |
| Participation cap | At most 1% of median daily volume for promotion |
| Partial-fill policy | `TBD` |
| Reject cancel and expiry policy | `TBD` |

## Risk Profile

**Risk profile ID and hash:** `TBD`

Confirm the profile covers symbol and order allowlists, order and position size, gross and net exposure, leverage, open positions, order rate, daily loss, drawdown, ADV, session hours, stale data, kill controls, and reconciliation.

Strategy-specific risk hypothesis or stop condition: `TBD`.

## Cost Assumptions

| Cost | Baseline | Source and as-of date | Doubled and quadrupled treatment |
|---|---|---|---|
| Spread | `TBD` | `TBD` | `TBD` |
| Commission and minimum | `TBD` | `TBD` | `TBD` |
| Slippage and impact | `TBD` | `TBD` | `TBD` |
| Venue and regulatory fees | `TBD` | `TBD` | `TBD` |
| Transaction tax | `TBD` | `TBD` | `TBD` |
| Financing or borrow | `TBD` | `TBD` | `TBD` |
| FX conversion | `TBD` | `TBD` | `TBD` |
| Fixed data and infrastructure | `TBD` | `TBD` | Reported separately |

An explicit zero requires a reason and applicability source.

## Train Validation and Test Design

| Segment or rule | Registered value |
|---|---|
| Training period | `TBD` |
| Validation period | `TBD` |
| Final test period | `TBD` |
| Rolling or anchored windows | `TBD` |
| Purge length | `TBD` |
| Embargo length | `TBD` |
| Label and holding overlap | `TBD` |
| Fold count and schedule | `TBD` |
| Final out-of-sample concatenation rule | `TBD` |

State why the final test remains unseen and how preprocessing is fitted inside each training window: `TBD`.

## Parameters and Trial Family

| Parameter | Fixed value or complete grid | Economic range rationale |
|---|---|---|
| `TBD` | `TBD` | `TBD` |

| Trial field | Registered value |
|---|---|
| Related prior trial IDs | `TBD` |
| Honest prior trial count | `TBD` |
| Planned new combinations | `TBD` |
| Multiple-testing family | `TBD` |
| Correction method | `TBD` |
| Plateau rule | `TBD` |

Renaming a strategy does not reset its trial family.

## Metrics and Promotion Thresholds

| Criterion | Registered threshold | Primary or diagnostic |
|---|---|---|
| Net annualized Sharpe | At least 0.7 using out-of-sample returns | Mandatory |
| Sharpe at doubled assumed variable costs | Greater than 0 | Mandatory |
| Independent out-of-sample trades | At least 100 | Mandatory |
| Deflated Sharpe Ratio | Positive at 95% confidence | Mandatory |
| Maximum drawdown | At most 25% and at most twice worst in-sample drawdown | Mandatory |
| Parameter behavior | Registered plateau rule passes | Mandatory |
| Economic thesis | Still plausible after blind result review | Mandatory |
| Capacity | Position at most 1% of median daily volume | Mandatory |
| Backtester controls | All mandatory sanity tests pass on the exact engine version | Mandatory |
| Data eligibility | All inputs are `PUBLISHED` for the claim | Mandatory |
| Additional metric | `TBD` | `TBD` |

State the risk-free rate, uncertainty estimator, effective sample method, benchmark, and any secondary metrics: `TBD`.

## Robustness Plan

- Full parameter surface: `TBD`
- Fold and subperiod dispersion: `TBD`
- Leave-one-instrument-out or universe perturbation: `TBD`
- Cost and execution perturbation: `TBD`
- Alternative reasonable data or action treatment: `TBD`
- Negative controls and engine sanity version: `TBD`
- Predefined regime descriptions that do not drive selection: `TBD`

No unregistered robustness result can be presented as confirmatory without a new frozen record.

## Known Limitations

| Limitation | Direction of likely bias | Could reverse conclusion | Treatment |
|---|---|---|---|
| `TBD` | `Optimistic`, `pessimistic`, or `unknown` | `YES` or `NO` | `TBD` |

Any limitation that could reverse the conclusion blocks promotion unless resolved before the run.

## Registration Lock

Before changing status to `LOCKED`:

- [ ] Every mandatory field is complete.
- [ ] Dataset selection and period boundaries are frozen.
- [ ] Parameters and trial count are frozen.
- [ ] Costs, metrics, thresholds, and robustness rules are frozen.
- [ ] Code and configuration identities are recorded.
- [ ] The registration is canonicalized and content-hashed.
- [ ] No result from the confirmatory period has been viewed by the decision maker.

**Registration hash:** `TBD`  
**Locked at UTC:** `TBD`  
**Locked status:** `DRAFT`

## Approval

| Role | Name | Decision | Date |
|---|---|---|---|
| Research owner | `TBD` | `LOCK` or `REJECT` | `TBD` |
| Independent implementation review where available | `TBD` | `REVIEWED` or `NOT_AVAILABLE` | `TBD` |

**Authorized next action:** `None until LOCKED`
