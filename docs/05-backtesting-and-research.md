# Backtesting and Research Protocol

<details open>
<summary><b>Contents</b></summary>

- [Purpose](#purpose)
- [Evidence Classes](#evidence-classes)
- [Simulation Time Model](#simulation-time-model)
- [Portfolio Accounting](#portfolio-accounting)
- [Order and Fill Model](#order-and-fill-model)
- [Cost Model](#cost-model)
- [Strategy Preregistration](#strategy-preregistration)
- [Data Splitting and Walk Forward](#data-splitting-and-walk-forward)
- [Statistical Evaluation](#statistical-evaluation)
  - [Core Metrics](#core-metrics)
  - [Estimation Uncertainty](#estimation-uncertainty)
  - [Multiple Testing](#multiple-testing)
- [Parameter Robustness](#parameter-robustness)
- [Mandatory Sanity Tests](#mandatory-sanity-tests)
- [Promotion Decision](#promotion-decision)
- [Backtest Report Contract](#backtest-report-contract)
- [Initial Strategy Protocol](#initial-strategy-protocol)
- [Known Limitations](#known-limitations)
- [Acceptance Evidence](#acceptance-evidence)

</details>

---

**Version:** 1.0  
**Date:** 30 August 2026  
**Status:** Proposed baseline  
**Related:** [Requirements](01-requirements.md) | [Data Specification](04-data-specification.md) | [Risk Specification](03-risk-and-safety.md)

## Purpose

This protocol defines how hypotheses are registered, simulated, measured, challenged, and promoted. Its purpose is not to produce attractive equity curves; it is to make incorrect assumptions and weak evidence difficult to hide.

## Evidence Classes

| Class | Meaning | Allowed claim |
|---|---|---|
| `MACHINERY` | Synthetic, deliberately simple, or deliberately broken scenario | The engine behaves as specified |
| `EXPLORATORY` | Research that influenced feature, parameter, universe, or period choices | A hypothesis is worth a fresh test, not that an edge exists |
| `CONFIRMATORY_OOS` | Pre-registered evaluation on unseen, eligible data | Input to a promotion decision |
| `PAPER` | Live data and broker simulation | Operational and tracking evidence |
| `LIVE` | Real-money fills under approved tiny-live controls | Realized evidence, still uncertain |

Evidence classes never upgrade automatically. Viewing a confirmatory result and then changing the strategy turns the changed candidate into a new exploratory candidate requiring a fresh test.

## Simulation Time Model

The engine is an event loop with an explicit clock. Vectorized calculations may prepare features, but they may not determine execution order or expose future rows.

For a complete daily-bar strategy, the canonical event order is:

1. Advance to the next exchange event using the pinned calendar.
2. Apply effective corporate actions and scheduled cash events under the declared policy.
3. At session open, process orders that became eligible from prior decisions using raw execution prices.
4. Process fills, fees, cash, positions, and order states in deterministic tie-break order.
5. Mark the portfolio under the declared price policy.
6. When session data reaches `available_at_utc`, expose the completed bar to the strategy.
7. Compute features and a decision using only the as-of view.
8. Create and risk-check any order intent.
9. Queue accepted intent for its earliest eligible future session.
10. Record events, marks, and lineage before advancing time.

A signal based on session $t$ cannot fill at session $t$ close. Its earliest normal fill is session $t+1$ under the configured order policy. A test strategy that attempts same-bar execution must fail.

Events with equal timestamps use a documented stable priority and sequence number. Random behavior uses an explicit recorded seed and a defined pseudorandom generator.

## Portfolio Accounting

The simulated ledger uses double-entry-style invariants even if implemented in a compact form:

- Cash changes only through fills, fees, taxes, financing, dividends, approved external flows, and explicit corrections.
- Position quantity changes only through fills and effective corporate actions.
- Every fill links one order, one instrument, one side, one quantity, one price, and all applicable costs.
- Realized PnL follows one declared lot or average-cost policy and is tested independently of tax-lot export.
- Unrealized PnL uses raw tradable marks, not adjusted prices.
- Splits change quantity and unit basis without creating economic PnL.
- Dividends enter cash and total return under the declared action policy.
- Base-currency reporting records both local-currency values and the FX rate used.

At every event:

$$
\text{equity} = \text{cash} + \sum_i \text{position}_{i} \times \text{mark}_{i} - \text{accrued liabilities}
$$

The ledger must reconcile independently calculated positions and cash from the fill journal. Rounding rules are explicit by currency and never depend on display formatting.

## Order and Fill Model

The Stage 1 model intentionally supports a narrow set of declared semantics:

| Concept | Baseline behavior |
|---|---|
| Direction | Long-only |
| Order intent | Target quantity or side and quantity converted once into a logical order |
| Initial order type | One approved daily-bar-compatible type, selected before implementation acceptance |
| Earliest execution | Next eligible session after the decision |
| Price | Raw market price plus side-aware spread and slippage |
| Participation | Order quantity capped by a configured fraction of observed volume |
| Partial fill | Deterministic policy based on available modeled volume; explicitly scenario-tested |
| Reject | Triggered by risk, cash, session, unsupported type, or test scenario |
| Cancel | Effective only when the simulated broker acknowledges it before fill priority |
| Time in force | Explicit, never inferred |

Daily OHLCV cannot reveal queue position or the true path within a bar. The simulator therefore must not claim realistic passive limit-order fills from bar extremes alone. If a strategy depends on whether the high or low occurred first, daily bars are insufficient and the result is ineligible for promotion.

Fill-model parameters are versioned and sensitivity-tested. A more favorable fill assumption cannot be selected after seeing strategy results without opening a new trial.

## Cost Model

Every applicable field is required, including an explicit zero with rationale. No global zero-cost default exists.

| Cost | Required model |
|---|---|
| Bid-ask spread | Side-aware half-spread or executable-price estimate by instrument and date |
| Commission | Per share, per order, percent notional, and minimum or maximum rules as applicable |
| Slippage | Directional adverse adjustment with volume participation and stress multipliers |
| Market impact | Declared function of order size relative to ADV when material |
| Regulatory and venue fees | Side and venue-specific where applicable |
| SDRT or transaction tax | Instrument and buy-side applicability; US-listed baseline explicitly records zero UK SDRT assumption for review |
| Financing and margin | Daily accrual when applicable; initial unleveraged cash profile records non-applicability |
| Short borrow | Availability and annualized fee when applicable; initial long-only profile records non-applicability |
| FX conversion | Rate source, spread or fee, and conversion timing for non-base-currency activity |
| Market data and infrastructure | Reported as fixed project costs outside per-trade PnL and included in economic viability reporting |
| Tax on gains | Separate after-tax scenario, never mixed into execution cost without a defined account and jurisdiction policy |

Each formal report includes baseline, $2\times$, and $4\times$ variable-cost scenarios. The multiplier applies to uncertain execution costs under a documented map; it does not incorrectly multiply fixed subscription costs or statutory rates without a scenario rationale.

The identity test for modeled variable costs is:

$$
\text{gross PnL} - \text{net PnL} = \sum \text{modeled variable costs}
$$

## Strategy Preregistration

Before the first confirmatory run, record:

- Candidate and strategy-family IDs.
- Versioned economic thesis identifying a risk premium, structural counterparty, or behavioral mechanism.
- Why that mechanism might persist and what would invalidate it.
- Instrument universe and point-in-time eligibility rule.
- Signal formula, feature timing, rebalance schedule, and execution policy.
- Complete parameter values or the full parameter grid.
- Training, validation, embargo, and final test boundaries.
- Cost model and all sensitivity scenarios.
- Position sizing and risk profile.
- Primary metric, secondary metrics, and every promotion threshold.
- Expected trade count and a power or precision discussion.
- Benchmark and negative-control expectations.
- Prior related trials included in the multiple-testing family.
- Stop conditions and planned robustness checks.

The registration is immutable and content-hashed. Corrections create a new candidate version. A timestamped registration after results exist is not pre-registration.

## Data Splitting and Walk Forward

- Select boundaries before confirmatory results are produced.
- Train or choose parameters only on the training segment.
- Use validation segments for permitted model selection and record every selection trial.
- Keep the final test segment untouched until the candidate is frozen.
- For rolling walk-forward evaluation, train on `[t-k, t)`, apply purge and embargo, test on `[t, t+m)`, then advance without retrospective tuning.
- Set purge and embargo at least as long as the maximum information overlap from feature lookback, label horizon, and holding period.
- Fit scalers, winsorization bounds, missing-value rules, and universe screens inside each training window.
- Concatenate untouched out-of-sample returns chronologically and calculate promotion metrics from that sequence only.
- Preserve in-sample output for debugging but label it prominently and exclude it from promotion.

Overlapping positions reduce effective independence. Trade count, bar count, and effective sample size are reported separately.

## Statistical Evaluation

### Core Metrics

Every confirmatory report includes:

- Total and annualized gross and net return.
- Annualized volatility and Sharpe ratio with the declared risk-free rate treatment.
- Sortino and Calmar ratios as secondary, sample-sensitive measures.
- Maximum drawdown, duration, and recovery time.
- Trade count, effective independent observation estimate, hit rate, payoff ratio, and expectancy per trade.
- Turnover, average holding period, exposure, concentration, and ADV participation.
- Gross and net profit by year and declared regime slices.
- Benchmark-relative return, beta, and correlation where meaningful.
- Cost decomposition and baseline, $2\times$, and $4\times$ sensitivity.
- Parameter-surface stability and result dispersion across walk-forward folds.

No single metric decides promotion. In particular, hit rate without payoff and cost is not evidence of edge.

### Estimation Uncertainty

For approximately independent returns measured at one frequency, a starting approximation is:

$$
SE(\widehat{SR}) \approx \sqrt{\frac{1 + \widehat{SR}^2 / 2}{N}}
$$

Serial correlation, overlapping positions, heteroskedasticity, skew, and fat tails make naive uncertainty too optimistic. The implementation must use an autocorrelation-aware or appropriately resampled estimator for formal reports and state all assumptions.

Confidence intervals are reported for the primary return and risk statistics. A short sample is described as uncertain even when the point estimate exceeds a threshold. Calendar duration and independent observations are both shown.

### Multiple Testing

- Log every attempted run automatically, including crashes, rejected configurations, and unattractive results.
- Define related candidate families before correction where possible.
- Treat parameter combinations, universe variants, feature variants, periods, and selective report slices as trials when they influenced selection.
- Report the honest trial count and apply the registered false-discovery or family-wise method.
- Calculate Deflated Sharpe Ratio using a reviewed reference implementation or independently verified formula with golden tests for sample size, skew, kurtosis, and number of trials.
- Never reset the trial count by renaming a strategy.

A positive unadjusted Sharpe with a failed corrected result is a rejection, not a near pass.

## Parameter Robustness

A candidate must show a broad economically plausible region, not an isolated best point.

The robustness artefact includes:

- Full tested grid with no omitted failures.
- Heatmap or equivalent surface for net out-of-sample performance.
- Trade count and turnover alongside performance so sparse points are visible.
- Local perturbations around the registered candidate.
- Fold-by-fold and subperiod results.
- Leave-one-instrument-out results for a multi-instrument strategy.
- Cost and execution assumption perturbations.
- A stated plateau rule established before inspection.

Selecting a point because it is the maximum opens a new exploratory trial. A robust default or center of a plateau is preferred over the empirical peak.

## Mandatory Sanity Tests

| Test | Expected result | Failure implication |
|---|---|---|
| Same config, code, data, and seed twice | Byte-identical canonical result | Nondeterminism or incomplete lineage |
| Buy and hold reference | Matches independently sourced return within declared cost and action tolerance | Data, action, or accounting defect |
| Random signal | Mean net result near negative modeled costs over many seeded runs | Fill, cost, or selection defect |
| Shuffled return sequence | Registered temporal edge disappears within statistical tolerance | Leakage or accounting defect |
| Deliberate future-close strategy | Temporal guard rejects access or promotion immediately | Look-ahead defense absent |
| Same-bar fill attempt | Order cannot fill on signal bar | Execution chronology defect |
| Zero versus baseline costs | PnL difference equals cost ledger exactly | Cost-accounting defect |
| Baseline versus doubled variable costs | Difference equals the declared incremental cost | Sensitivity defect |
| Split and dividend scenario | Economic value and position accounting reconcile | Corporate-action defect |
| Reject and partial-fill scenario | Orders, cash, positions, fees, and risk exposure reconcile | Order-state defect |
| No-trade strategy | Flat positions and only declared fixed economic costs | Phantom fill or cash defect |
| Impossible price sequence | Dataset is quarantined before simulation | Validation bypass |

Sanity tests are release gates for the engine. A strategy result produced while any applicable sanity test fails is invalidated.

## Promotion Decision

A candidate passes research-to-paper promotion only when every condition below passes on eligible confirmatory out-of-sample evidence:

| Criterion | Threshold |
|---|---|
| Net annualized Sharpe | At least 0.7 |
| Sharpe at doubled assumed variable costs | Greater than 0 |
| Independent out-of-sample trades | At least 100 |
| Deflated Sharpe Ratio | Positive at 95% confidence |
| Maximum drawdown | At most 25% and at most twice worst in-sample drawdown |
| Parameter behavior | Registered plateau rule passes |
| Economic thesis | Written before test and still plausible after result review |
| Capacity | Projected position at most 1% of median daily volume |
| Backtester controls | All sanity tests pass on the exact engine version |
| Data eligibility | All inputs are `PUBLISHED` for the claim being made |

The evaluator returns `PROMOTED`, `REJECTED`, or `INVALID`. `INVALID` means the evidence cannot answer the question because a contract was broken. No manual weighted score can compensate for one failed mandatory row.

## Backtest Report Contract

Each report contains or links:

1. Run ID, candidate ID and version, evidence class, and run status.
2. Git commit, dirty-worktree indicator, environment lock hash, config hash, and random seed.
3. Dataset and manifest IDs, calendar and adjustment versions, and data limitations.
4. Decision, order, fill, sizing, and risk policies.
5. Complete cost configuration and cost ledger.
6. Train, validation, purge, embargo, test, and walk-forward boundaries.
7. Gross, net, benchmark, and out-of-sample-only equity curves with no visual splicing.
8. Core metrics, uncertainty, effective observations, and trial count.
9. Baseline, doubled, and quadrupled cost scenarios.
10. Parameter surface and robustness evidence.
11. Sanity-test engine version and outcomes.
12. Every promotion criterion with observed value, threshold, and pass state.
13. Machine-readable canonical result JSON and human-readable report.

Canonical JSON uses a versioned schema and stable numeric serialization. Display rounding never changes the stored decision value.

## Initial Strategy Protocol

The first moving-average crossover is a `MACHINERY` strategy. Its purpose is to exercise data, feature timing, next-session execution, costs, positions, risk, reports, and paper orders. It is not eligible for promotion based on a favorable result discovered during implementation.

After the machinery gate, first formal candidates may come from:

- Time-series trend following.
- Cross-sectional momentum, only with point-in-time eligible universe data.
- Short-horizon mean reversion on liquid instruments.

Each candidate gets a separate pre-registration. Published literature is used for implementation sanity checks, not as proof that the local net-of-cost result will persist.

## Known Limitations

- Daily bars do not identify intrabar path, queue position, spread at decision time, or passive-order fill probability.
- A single ETF produces few independent observations and weak statistical power for modest edges.
- Vendor-adjusted data can embed revisions not known historically.
- Paper fills may not represent real queue priority, impact, borrow, or behavioral response.
- Historical costs and FX conversion may be approximated where primary records are unavailable.
- Regime labels selected after observing performance are descriptive, not confirmatory.
- Statistical correction reduces but does not remove model-selection bias.

Each report states which limitations are material to its claim. A limitation that can reverse the conclusion blocks promotion rather than becoming a footnote.

## Acceptance Evidence

- Event chronology tests prove information and fill eligibility boundaries.
- Accounting invariants pass generated sequences of fills, costs, actions, and cash flows.
- All mandatory sanity tests pass on the reference engine.
- Repeated canonical runs are byte-identical.
- A deliberately incomplete cost configuration is rejected.
- A deliberately unregistered confirmatory run is rejected and still logged as attempted.
- Walk-forward fixtures prove fitting occurs only inside each training window.
- Trial-count and Deflated Sharpe golden cases are independently checked.
- A candidate failing any promotion row is mechanically rejected.
