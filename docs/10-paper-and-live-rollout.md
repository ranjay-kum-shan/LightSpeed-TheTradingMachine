# Paper and Future Live Rollout Plan

<details open>
<summary><b>Contents</b></summary>

- [Purpose](#purpose)
- [Promotion Principle](#promotion-principle)
- [Environment Ladder](#environment-ladder)
- [Stage Gates](#stage-gates)
  - [Stage Zero Decision Gate](#stage-zero-decision-gate)
  - [Stage One Vertical Slice Gate](#stage-one-vertical-slice-gate)
  - [Stage Two Honest Backtest Gate](#stage-two-honest-backtest-gate)
  - [Stage Three Research Gate](#stage-three-research-gate)
  - [Stage Four Paper Gate](#stage-four-paper-gate)
  - [Stage Five Tiny Live Gate](#stage-five-tiny-live-gate)
- [Paper Tracking Plan](#paper-tracking-plan)
- [Tiny Live Activation Controls](#tiny-live-activation-controls)
- [Scaling Rules](#scaling-rules)
- [Demotion and Clock Reset](#demotion-and-clock-reset)
- [Rollback and Emergency Stop](#rollback-and-emergency-stop)
- [Abandon Criteria](#abandon-criteria)
- [Gate Evidence Bundle](#gate-evidence-bundle)
- [Open Decisions](#open-decisions)

</details>

---

**Version:** 1.0  
**Date:** 30 August 2026  
**Status:** Proposed baseline; current authorization remains `PAPER_ONLY`  
**Current authorization:** `PAPER_ONLY`  
**Stage 5 status:** Separately gated and currently unauthorized  
**Related:** [Project Charter](../CHARTER.md) | [Research Protocol](05-backtesting-and-research.md) | [Operations Runbook](08-operations-and-observability.md)

## Purpose

This plan defines evidence-based promotion from planning to research, paper trading, and a separately approved future tiny-live experiment. Time spent in a stage does not grant promotion. Every gate is conjunctive: all required criteria must pass.

## Promotion Principle

- Engineering completion and financial evidence are different outcomes.
- The first strategy validates machinery and is not presumed promotable.
- A stage begins only after the prior gate has a dated owner decision and immutable evidence bundle.
- A failed gate produces `REMAIN`, `DEMOTE`, `RESET_CLOCK`, or `ABANDON`; there is no conditional pass that hides a mandatory failure.
- Thresholds are fixed before results are observed and are never relaxed to promote a current candidate.
- Backtest, paper, and future live results remain separately labeled and compared rather than spliced.
- Any ambiguity about exposure, state, permission, data, or evidence denies promotion.

## Environment Ladder

| Environment | Capital | External order capability | Evidence purpose | Entry control |
|---|---|---|---|---|
| Offline unit and simulation | None | None | Rule and invariant correctness | Source and test configuration |
| Historical backtest | None | None | Research evidence and negative controls | Published data plus registered run |
| Fake broker system test | None | Deterministic local fake only | End-to-end order and recovery behavior | Test harness |
| Paper sandbox smoke | Simulated | Verified paper endpoint only | Adapter contract | Protected explicit command |
| Unattended paper | Simulated | Approved paper account | Operational and tracking evidence | Stage 3 gate plus paper release |
| Tiny live | Owner-approved loss-tolerant allocation only | Separate real account capability | Real fill and behavior evidence | Stage 4 gate plus separate Stage 5 approval |

Movement down the ladder is always allowed for safety. Movement up requires a gate decision.

## Stage Gates

### Stage Zero Decision Gate

Required before implementation assumptions are treated as approved:

- Initial market, universe, daily horizon, long-only and unleveraged scope approved.
- Weekly time budget approved.
- Paper broker eligibility and terms confirmed by the owner.
- Base reporting currency approved.
- Abandon criteria accepted.
- Charter status changed from draft through a dated owner sign-off.
- Live capital and loss fields may remain `TBD`; that keeps Stage 5 blocked and does not block safe paper development.

**Decision:** `PASS_STAGE_0` or `REMAIN_STAGE_0`.

### Stage One Vertical Slice Gate

Required executable evidence:

- One approved ETF has a ten-year immutable daily dataset, manifest, and all twelve data checks passing.
- A simple machinery strategy produces a deterministic backtest with next-session execution and explicit costs.
- Every hard risk limit has a passing denial test before external submission exists.
- Internal halt, operator kill, heartbeat, and independent watchdog paths work.
- The paper environment and account guard pass and reject wrong-mode cases.
- One logical paper order appears exactly once in local state and broker evidence.
- Reject, partial-fill simulation, disconnect, and unknown-outcome paths are exercised.
- Startup compares account, positions, cash, orders, and fills before strategy evaluation.
- Killing the process at critical lifecycle points produces no duplicate order and returns through `RECOVERY`.
- Structured logs and a daily or exercise report contain code, config, data, and session identity without secrets.

**Decision:** `PASS_STAGE_1`, `REMAIN_STAGE_1`, or `DEMOTE_TO_STAGE_0` if scope assumptions are invalid.

### Stage Two Honest Backtest Gate

- Raw and adjusted data and corporate-action accounting reconcile for the declared scope.
- Cost model has no silent default and reports baseline, doubled, and quadrupled scenarios.
- Walk-forward fitting, purge, embargo, and out-of-sample concatenation pass temporal tests.
- Every run, including invalid, failed, and unattractive runs, enters the experiment store.
- Same inputs produce byte-identical canonical results.
- Buy-and-hold, random, shuffled, future-close, same-bar, zero-cost, no-trade, and action sanity tests pass.
- Trial counting, multiple-testing correction, Sharpe uncertainty, and Deflated Sharpe reference cases pass.
- Known data limitations are strong enough for the intended claim or explicitly bar promotion.

**Decision:** `PASS_STAGE_2`, `REMAIN_STAGE_2`, or `INVALIDATE_ENGINE_EVIDENCE`.

### Stage Three Research Gate

At least one frozen pre-registered candidate must pass every row:

| Criterion | Threshold |
|---|---|
| Out-of-sample annualized Sharpe after costs | At least 0.7 |
| Sharpe under doubled variable costs | Greater than 0 |
| Independent out-of-sample trades | At least 100 |
| Deflated Sharpe Ratio | Positive at 95% confidence |
| Maximum drawdown | At most 25% and at most twice worst in-sample drawdown |
| Parameter response | Pre-registered plateau rule passes |
| Economic thesis | Predates the test and remains plausible |
| Capacity | Projected position at most 1% of median daily volume |
| Data and engine | Eligible published data and all engine controls pass |

The candidate package freezes strategy source, parameters, data eligibility, decision time, order policy, costs, risk profile, and expected paper tolerances.

**Decision:** `PROMOTE_TO_PAPER`, `CONTINUE_REGISTERED_RESEARCH`, or `ABANDON` under the charter criteria.

### Stage Four Paper Gate

The qualifying observation window begins only after the promoted release is deployed unattended. All must pass:

| Criterion | Threshold |
|---|---|
| Consecutive qualifying duration | At least three months |
| Unexplained reconciliation breaks | Zero |
| Paper Sharpe versus frozen backtest | Within one estimated standard error |
| Median paper slippage versus modeled | No greater than twice modeled slippage |
| Market-hours availability | At least 99% |
| Induced recovery exercises | At least five successful exercises |
| Daily expected-session reports | 100%, including no-trade sessions |
| Unknown logical orders | Zero unresolved |
| Tax and recordkeeping rehearsal | Complete on paper records |
| Material strategy changes | None during qualifying window |

An unexplained discrepancy or material strategy, data, execution, or risk change resets the qualifying clock after correction and regression evidence.

**Decision:** `PAPER_ACCEPTED`, `RESET_PAPER_CLOCK`, `DEMOTE_TO_RESEARCH`, or `ABANDON`. `PAPER_ACCEPTED` does not itself enable real-money capability.

### Stage Five Tiny Live Gate

This gate is future-only and remains blocked until a separate activation review confirms all of the following:

- Stage 4 has a signed `PAPER_ACCEPTED` evidence bundle.
- The owner states an exact capital allocation that can be lost completely without affecting any life decision.
- Absolute and percentage daily-loss, drawdown, order, position, exposure, and leverage limits are approved in one base currency.
- Initial values are no greater than half the accepted paper risk values and leverage remains disabled unless a later charter change separately approves it.
- Broker account eligibility, permissions, protection status, execution terms, and emergency support are reverified.
- A qualified UK tax professional confirms the intended instrument and recordkeeping treatment.
- Market-data rights cover the intended operation.
- Live credentials, account, configuration, state, reports, alerts, approvals, and deployment are separate from paper.
- Security threat model, incident response, backup, restore, and owner emergency procedures pass review.
- A no-order read-only dress rehearsal and a minimum-size controlled order rehearsal are approved and witnessed.
- The activation has an expiry time and automatically returns to denied state if not used as approved.

**Decision:** `AUTHORIZE_TINY_LIVE_FOR_DEFINED_RELEASE`, `REMAIN_PAPER_ONLY`, or `ABANDON`. The current project has no such authorization.

## Paper Tracking Plan

For each paper decision, link the frozen backtest expectation to the actual paper path:

| Comparison | Measure |
|---|---|
| Signal | Expected direction or target versus paper decision from identical as-of input |
| Eligibility | Expected decision and order time versus actual data and scheduler time |
| Order | Expected type, quantity, and terms versus submitted canonical order |
| Fill | Modeled price and time versus paper fill and slippage in basis points |
| Cost | Modeled spread, fees, and FX versus broker-observed fields where available |
| Position | Expected post-fill quantity versus reconciled broker quantity |
| PnL | Frozen backtest replay of realized paper dates versus paper ledger |
| Operations | Expected session completion versus uptime, alerts, and report delivery |

Tracking tolerances are registered before the qualifying period. The headline set includes decision match rate, fill slippage distribution, cost error, position mismatch count, daily return tracking error, and cumulative PnL divergence with confidence bounds.

Paper fills are not evidence of real queue priority or market impact. Their value is operational verification and measurement of simulation-to-broker divergence.

## Tiny Live Activation Controls

If Stage 5 is eventually approved, activation must require more than configuration editing:

1. Select the exact approved release manifest.
2. Verify the separate account fingerprint and credentials through a read-only call.
3. Verify all owner and professional sign-offs are current and hashes match.
4. Verify the exact capital deposit and no unexplained account positions or orders.
5. Load the immutable tiny-live risk profile; deny inherited paper values.
6. Confirm operator kill, watchdog, primary and secondary alerts, backup, and broker emergency access.
7. Run startup recovery and full reconciliation with order capability still disabled.
8. Require an explicit short-lived owner activation token or equivalent local approval action.
9. Permit only the defined strategy, symbols, order types, windows, and allocation.
10. Expire capability after the approved window and require a fresh reconciliation before any renewal.

The system remains fail-closed if one control is missing, stale, mismatched, or unverifiable.

## Scaling Rules

- Do not change the strategy during the first three months of a future tiny-live observation unless safety requires immediate stop.
- Require at least six months of qualifying operation before any capital increase.
- Compare backtest, paper, and real fills as three distinct evidence series.
- Scale no more than two times the prior allocation in one approved step.
- Recalculate absolute order, position, loss, drawdown, ADV, spread, slippage, and FX exposure for each step; do not auto-scale limits.
- Re-run capacity analysis and broker or market-data cost review.
- A scale change starts a new labeled observation segment and can require a fresh clock if execution behavior materially changes.
- Reduce or remove capital immediately when safety requires; demotion does not wait for a review window.

## Demotion and Clock Reset

| Trigger | Minimum response |
|---|---|
| Unexplained reconciliation break | Halt, investigate, reset paper observation clock after fix |
| Duplicate or unknown logical order | Hard halt and demote to Stage 1 recovery testing |
| Backtest control defect | Invalidate affected research, paper comparison, and promotion evidence |
| Material data revision | Identify affected runs; rerun or invalidate before continuation |
| Strategy or parameter change | New candidate version and research gate |
| Execution or cost-model change | Repeat affected Stage 2 controls and reset comparison baseline |
| Risk limit relaxation | New approval and affected safety tests; reset qualifying window if material |
| Credential exposure | Halt, rotate, security review, and fresh paper preflight |
| Availability below threshold | Reset qualifying paper clock if observation integrity is affected |
| Owner intervention in strategy decisions | Mark period non-qualifying and restart unchanged observation |

Clock resets are not punishments. They protect the meaning of a continuous unattended sample.

## Rollback and Emergency Stop

- The operator kill and broker emergency access are available at every broker-connected stage.
- Emergency response prioritizes stopping new exposure, identifying working orders, reconciling positions, and preserving evidence.
- Code rollback never restores an old database over newer broker facts.
- A rollback release must understand or safely reject the current state schema.
- If compatibility is uncertain, remain halted and use a dedicated recovery tool or broker interface under owner control.
- Any emergency broker action is recorded and reconciled before automation resumes.
- A future real-money incident exceeding the approved daily loss due to software triggers the charter stop criterion until root cause and regression evidence exist.

## Abandon Criteria

Stop and write a retrospective when any charter condition occurs:

1. No strategy passes research promotion within eighteen months of Stage 0 approval.
2. Future real-money drawdown reaches the lower of the owner-approved limit or 25%.
3. Two consecutive qualifying quarters fall outside paper confidence bounds without explanation.
4. More than 800 hours are invested without a paper candidate.
5. The owner no longer finds the project worth continuing.
6. A software loss exceeds the daily limit; stop at least until root cause and regression proof exist.
7. Required data, broker access, legal eligibility, tax handling, or controls cannot be sustained.

No strategy or sunk engineering cost overrides an abandon condition.

## Gate Evidence Bundle

Every gate review includes:

- Gate ID, date, owner, requested decision, and applicable charter version.
- Exact source, dependency, strategy, config, risk, data, calendar, and environment identities.
- Requirement and test traceability status.
- Required reports and quantitative thresholds with observed values.
- Open incidents, discrepancies, known limitations, and invalidated evidence.
- Security, secret, dependency, backup, restore, and alert status where applicable.
- Owner decisions and professional confirmations required by the gate.
- Final result with no blank mandatory criterion.
- Expiry or next review date.

Evidence is immutable after decision. A correction creates a superseding bundle linked to the original.

## Open Decisions

| Decision | Needed by | Blocking effect |
|---|---|---|
| Approve Stage 0 charter rows | Stage 0 | Blocks formal project start |
| Define paper tracking-error tolerances | Before Stage 4 clock | Blocks qualifying paper measurement |
| Define material-change rules for clock reset | Before Stage 4 clock | Blocks consistent observation policy |
| Define paper reference equity and limits | Paper deployment | Blocks realistic risk configuration |
| Choose minimum-size future real-order rehearsal policy | Stage 5 review only | Blocks any future activation |
| Set exact future capital and loss boundaries | Stage 5 review only | Keeps real-money mode denied |
