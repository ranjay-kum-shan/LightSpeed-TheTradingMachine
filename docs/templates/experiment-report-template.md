# Experiment Report Template

<details open>
<summary><b>Contents</b></summary>

- [Identity](#identity)
- [Registered Question](#registered-question)
- [Reproducibility](#reproducibility)
- [Execution Status](#execution-status)
- [Deviations](#deviations)
- [Data and Method](#data-and-method)
- [Results](#results)
  - [Primary Metrics](#primary-metrics)
  - [Cost Sensitivity](#cost-sensitivity)
  - [Robustness](#robustness)
- [Sanity and Control Results](#sanity-and-control-results)
- [Promotion Evaluation](#promotion-evaluation)
- [Interpretation](#interpretation)
- [Limitations and Invalidations](#limitations-and-invalidations)
- [Artefacts](#artefacts)
- [Review](#review)

</details>

---

**Run ID:** `TBD`  
**Candidate ID and version:** `TBD`  
**Registration hash:** `TBD`  
**Evidence class:** `TBD`  
**Run UTC:** `TBD`  
**Status:** `NOT_RUN`

## Identity

| Field | Value |
|---|---|
| Strategy and version | `TBD` |
| Trial-family ID | `TBD` |
| Trial ordinal after this run | `TBD` |
| Owner | `TBD` |
| Engine version | `TBD` |
| Report schema version | `TBD` |

## Registered Question

Link the immutable strategy registration and restate its falsifiable question without editing it after results are known.

**Registration reference:** `TBD`  
**Question:** `TBD`

## Reproducibility

| Input | Identity |
|---|---|
| Git revision | `TBD` |
| Worktree state | `CLEAN`, `DIRTY_RESEARCH_ONLY`, or `TBD` |
| Environment lock hash | `TBD` |
| Configuration hash | `TBD` |
| Data manifest IDs and hashes | `TBD` |
| Calendar and action-policy versions | `TBD` |
| Random generator and seed | `TBD` |
| Platform details relevant to canonical output | `TBD` |

**Deterministic repeat result:** `PASS`, `FAIL`, or `NOT_RUN`

## Execution Status

Select one:

- `COMPLETED`: valid run eligible for its registered evidence class.
- `FAILED`: execution did not complete; still counted as a trial.
- `INVALID`: completed output cannot answer the question because a contract broke.
- `CANCELED`: deliberately stopped; still retained with reason.

**Selected status:** `TBD`  
**Reason code and explanation:** `TBD`

## Deviations

| Registered item | Actual behavior | Reason | Effect on evidence class |
|---|---|---|---|
| `TBD` | `TBD` | `TBD` | `NONE`, `EXPLORATORY_ONLY`, or `INVALID` |

Use `None` only after comparing code, configuration, data, periods, parameters, costs, and metrics with the registration hash.

## Data and Method

- Universe and membership rule: `TBD`
- Effective history and fold boundaries: `TBD`
- Purge and embargo: `TBD`
- Decision and earliest-fill timeline: `TBD`
- Position sizing and risk profile: `TBD`
- Order and fill model: `TBD`
- Cost model: `TBD`
- Benchmark: `TBD`
- Independent-observation method: `TBD`
- Known data limitations: `TBD`

## Results

### Primary Metrics

| Metric | Gross | Net baseline | Registered threshold | Uncertainty | Result |
|---|---|---|---|---|---|
| Annualized return | `TBD` | `TBD` | Diagnostic | `TBD` | `TBD` |
| Annualized volatility | `TBD` | `TBD` | Diagnostic | `TBD` | `TBD` |
| Annualized Sharpe | `TBD` | `TBD` | At least 0.7 net OOS | `TBD` | `PASS` or `FAIL` |
| Deflated Sharpe Ratio | Not applicable | `TBD` | Positive at 95% confidence | Trial count `TBD` | `PASS` or `FAIL` |
| Maximum drawdown | `TBD` | `TBD` | At most registered limit | `TBD` | `PASS` or `FAIL` |
| Independent trades | `TBD` | `TBD` | At least 100 | Method `TBD` | `PASS` or `FAIL` |
| Expectancy per trade | `TBD` | `TBD` | Diagnostic | `TBD` | `TBD` |
| Turnover | `TBD` | `TBD` | Diagnostic | `TBD` | `TBD` |
| Capacity as percent ADV | `TBD` | `TBD` | At most 1% | `TBD` | `PASS` or `FAIL` |

Report train, validation, and concatenated out-of-sample values separately. Promotion rows use out-of-sample only.

### Cost Sensitivity

| Scenario | Net return | Sharpe | Maximum drawdown | Total variable cost | Promotion implication |
|---|---|---|---|---|---|
| Baseline | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` |
| Doubled variable cost | `TBD` | `TBD` | `TBD` | `TBD` | Sharpe must remain above zero |
| Quadrupled variable cost | `TBD` | `TBD` | `TBD` | `TBD` | Stress diagnostic |

Confirm gross minus net equals the cost ledger under each scenario: `TBD`.

### Robustness

| Check | Registered rule | Observed result | Pass |
|---|---|---|---|
| Parameter plateau | `TBD` | `TBD` | `TBD` |
| Fold dispersion | `TBD` | `TBD` | `TBD` |
| Subperiod behavior | `TBD` | `TBD` | `TBD` |
| Universe perturbation | `TBD` | `TBD` | `TBD` |
| Execution perturbation | `TBD` | `TBD` | `TBD` |
| Leave-one-instrument-out | `TBD` | `TBD` | `TBD` |

Attach the complete tested surface, including failed and unattractive points.

## Sanity and Control Results

| Control | Engine result | Expected | Pass |
|---|---|---|---|
| Deterministic repeat | `TBD` | Byte-identical canonical result | `TBD` |
| Buy and hold | `TBD` | Independent benchmark within tolerance | `TBD` |
| Random signal | `TBD` | Mean net result near negative modeled costs | `TBD` |
| Shuffled returns | `TBD` | Registered temporal edge disappears | `TBD` |
| Future-close access | `TBD` | Rejected | `TBD` |
| Same-bar fill | `TBD` | Rejected | `TBD` |
| Cost identity | `TBD` | Exact ledger reconciliation | `TBD` |
| Corporate actions | `TBD` | Position and value reconcile | `TBD` |
| Partial fill and reject | `TBD` | Orders cash positions and fees reconcile | `TBD` |
| No trade | `TBD` | No phantom activity | `TBD` |

Any failed applicable control makes the strategy result `INVALID`.

## Promotion Evaluation

| Mandatory criterion | Observed | Threshold | Result | Evidence |
|---|---|---|---|---|
| Net annualized Sharpe | `TBD` | At least 0.7 using out-of-sample returns | `TBD` | `TBD` |
| Sharpe at doubled assumed variable costs | `TBD` | Greater than 0 | `TBD` | `TBD` |
| Independent out-of-sample trades | `TBD` | At least 100 | `TBD` | `TBD` |
| Deflated Sharpe Ratio | `TBD` | Positive at 95% confidence | `TBD` | `TBD` |
| Maximum drawdown | `TBD` | At most 25% and at most twice worst in-sample | `TBD` | `TBD` |
| Parameter behavior | `TBD` | Registered plateau rule passes | `TBD` | `TBD` |
| Economic thesis | `TBD` | Predates test and remains plausible | `TBD` | `TBD` |
| Capacity | `TBD` | At most 1% median daily volume | `TBD` | `TBD` |
| Backtester controls | `TBD` | All mandatory sanity tests pass on the exact engine version | `TBD` | `TBD` |
| Data eligibility | `TBD` | All inputs are `PUBLISHED` for the claim | `TBD` | `TBD` |

**Mechanical decision:** `PROMOTED`, `REJECTED`, or `INVALID`  
**Manual override permitted:** `NO`

## Interpretation

Explain what the evidence does and does not support. Lead with uncertainty, effect size after costs, comparison with the registered thesis, and plausible alternative explanations. Do not write a causal claim from a backtest alone.

**Interpretation:** `TBD`

## Limitations and Invalidations

| Limitation or defect | Bias direction | Material | Affected evidence | Action |
|---|---|---|---|---|
| `TBD` | `TBD` | `YES` or `NO` | `TBD` | `TBD` |

List any later data revision, engine defect, cost change, or trial-family discovery that supersedes or invalidates the report.

## Artefacts

| Artefact | Content hash or immutable reference |
|---|---|
| Registration | `TBD` |
| Canonical result JSON | `TBD` |
| Human report | `TBD` |
| Equity and drawdown series | `TBD` |
| Trades and cost ledger | `TBD` |
| Parameter surface | `TBD` |
| Fold results | `TBD` |
| Control suite | `TBD` |
| Environment manifest | `TBD` |

## Review

| Role | Name | Decision | Date |
|---|---|---|---|
| Research owner | `TBD` | `ACCEPT_REPORT`, `REJECT_REPORT`, or `INVALIDATE` | `TBD` |
| Independent review where available | `TBD` | `REVIEWED` or `NOT_AVAILABLE` | `TBD` |

**Next permitted action:** `TBD`
