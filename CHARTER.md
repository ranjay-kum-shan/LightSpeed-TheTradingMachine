# Trading Bot Project Charter

<details open>
<summary><b>Contents</b></summary>

- [Purpose](#purpose)
- [Product Statement](#product-statement)
- [Project Decisions](#project-decisions)
  - [Working Defaults](#working-defaults)
  - [Owner Decisions Required](#owner-decisions-required)
- [Scope](#scope)
  - [In Scope](#in-scope)
  - [Conditional Scope](#conditional-scope)
  - [Out of Scope](#out-of-scope)
- [Constraints](#constraints)
- [Success Criteria](#success-criteria)
  - [Engineering Success](#engineering-success)
  - [Research Success](#research-success)
  - [Paper Trading Success](#paper-trading-success)
  - [Live Trading Success](#live-trading-success)
- [Loss and Safety Boundaries](#loss-and-safety-boundaries)
- [Abandon Criteria](#abandon-criteria)
- [Governance](#governance)
- [Stage Zero Sign Off](#stage-zero-sign-off)

</details>

---

**Version:** 1.0  
**Date:** 30 August 2026  
**Status:** Draft - Stage 0 is not yet approved  
**Operating mode:** `PAPER_ONLY`

> This project is for engineering and research. It is not financial, tax, or investment advice, and it makes no promise of profitability.

## Purpose

Build a small, reproducible, and safety-first systematic trading platform that can test trading hypotheses honestly, trade one liquid market in a paper account, and produce enough evidence to support a deliberate stop or a tightly controlled tiny-live trial.

The project optimizes for learning, correctness, and controlled risk. Profitability is evidence-driven and must never be assumed.

## Product Statement

For a single owner-researcher who wants to evaluate systematic trading ideas, the product is a Python trading system that acquires point-in-time-aware market data, runs reproducible net-of-cost backtests, enforces hard pre-trade risk limits, places paper orders through one broker, reconciles broker state, and records every decision for replay and audit.

Unlike a signal notebook or discretionary trading interface, the system must fail closed, distinguish research results from financial evidence, and require measurable gates before paper or live promotion.

## Project Decisions

### Working Defaults

These defaults are adopted from the reviewed development plan and may be changed only through a recorded decision:

| Decision | Working default | Reason |
| --- | --- | --- |
| Initial market | Liquid US-listed ETFs | High liquidity, broad exposure, no UK SDRT on US shares |
| Initial universe | A small allowlist, beginning with one broad-market ETF | Limits data and operational complexity |
| Bar frequency | Daily | Keeps latency and market microstructure out of the first system |
| Holding horizon | 2 to 20 trading days | Matches daily data and manageable turnover |
| Initial strategy | Simple moving-average crossover used only to validate machinery | No profitability claim is attached to the first strategy |
| Signal timing | Compute after bar `t`; earliest fill is bar `t+1` open | Prevents same-bar look-ahead |
| Broker | Alpaca paper environment | Lowest-friction API-first paper path |
| Long-term broker candidate | Interactive Brokers | Broader UK-accessible market coverage, subject to later review |
| Runtime | Python 3.12 or newer, single process | Research iteration speed is the binding constraint |
| Storage | Parquet plus DuckDB; SQLite for metadata and state | Reproducible local operation without service overhead |
| Time standard | UTC internally with an exchange calendar for session rules | Avoids timezone and daylight-saving ambiguity |
| Stage 1 exposure | Long-only, unleveraged, paper-only | Reduces first-release risk and complexity |
| Development capacity | 8 to 10 focused hours per week | Planning assumption from the reviewed plan |

### Owner Decisions Required

The owner must fill and approve these values before Stage 0 can pass. Until then, live-order capability must remain disabled by configuration and broker credentials.

| Decision | Required value | Current state |
| --- | --- | --- |
| Weekly time budget | Hours per week | Proposed: 8 to 10 hours; not approved |
| Paper account provider | Alpaca or approved alternative | Proposed: Alpaca; not approved |
| Currency for project reporting | One base currency | Proposed: GBP; not approved |
| Tiny-live capital allocation | Amount that can be lost completely without affecting any life decision | `TBD`; mandatory before Stage 5 |
| Maximum total project loss | Absolute currency amount | `TBD`; mandatory before any live order |
| Maximum daily live loss | Absolute amount and percent of allocated capital | `TBD`; mandatory before any live order |
| Maximum live drawdown | Percent of allocated capital, no greater than 25% | `TBD`; mandatory before any live order |
| Broker and account eligibility | Confirm UK residency, product access, and account terms | `TBD`; mandatory before broker integration is approved |
| Tax treatment | Confirm with a qualified UK tax professional for selected instruments | `TBD`; mandatory before Stage 5 |

## Scope

### In Scope

- One owner and one deployment.
- Liquid US-listed ETFs on daily bars.
- A deliberately small symbol allowlist.
- Historical data ingestion, validation, hashing, and immutable snapshots.
- A simple event-loop backtester with explicit costs and next-bar execution.
- Reproducible experiment tracking.
- Hard pre-trade risk checks, kill switches, heartbeat monitoring, and reconciliation.
- One paper broker adapter.
- Structured logs, daily reports, alerts, backups, and restart recovery.
- Two or three evidence-backed strategy families after the vertical slice is validated.
- Paper trading followed by a separately approved tiny-live stage only after all gates pass.

### Conditional Scope

The following require the measured entry conditions in the roadmap:

- A second strategy or portfolio engine after Strategy 1 has at least six months of live evidence.
- Machine learning after a validated non-ML baseline and sufficient independent observations exist.
- Regime detection after a stable regime-dependent performance difference is measured.
- Intraday data after daily research is exhausted and data cost is approved.
- Execution algorithms after measured slippage is a material fraction of edge.
- A second broker or asset class after the first complete path is operationally stable.
- Performance-oriented rewrites only after profiling identifies a binding Python bottleneck.

### Out of Scope

- High-frequency trading, co-location, direct exchange feeds, kernel bypass, and FPGA work.
- Options market making and order-book microstructure strategies.
- Autonomous or genetic strategy discovery.
- Distributed microservices, Kafka, and cluster infrastructure.
- Custody of third-party money, trading for other people, or investment advice.
- Any strategy that requires unavailable point-in-time data or cannot be represented honestly in the simulator.
- Leverage, short selling, CFDs, spread betting, futures, options, and crypto in the first implementation.

## Constraints

- Safety controls are implemented before broker order submission.
- Every order path is paper-only until Stage 5 approval is recorded.
- No secret may be committed, printed, included in an exception, or stored in an artefact.
- No backtest may run without an explicit cost model.
- Every result records configuration, code revision, data hash, and random seed.
- Every signal uses only information available at its recorded decision time.
- Any broker-state mismatch halts trading and requires investigation; it is never silently repaired.
- The broker is the authority for positions, cash, fills, and open orders after restart.
- Regulatory, broker, market-data, and tax assumptions must be revalidated before live use.
- The owner may pause the project at any time; sunk effort is not a reason to continue.

## Success Criteria

### Engineering Success

- One command can run a deterministic backtest and produce a signed result artefact.
- One command can run the paper loop with hard risk checks and reconciliation.
- Killing and restarting the process with paper positions or working orders causes no duplicate order and restores a reconciled state.
- Every documented data, risk, order-state, and recovery invariant has an automated test.
- The system can replay and explain any trading decision from retained inputs and logs.

Engineering success is valuable even if no strategy is promoted.

### Research Success

A strategy is eligible for paper promotion only when all of the following are true:

| Criterion | Minimum threshold |
| --- | --- |
| Out-of-sample annualized Sharpe after costs | At least 0.7 |
| Sharpe at twice assumed costs | Greater than 0 |
| Independent out-of-sample trades | At least 100 |
| Deflated Sharpe Ratio | Positive at 95% confidence |
| Maximum drawdown | No more than 25% and no more than twice the worst in-sample drawdown |
| Parameter response | A stable plateau rather than an isolated optimum |
| Economic thesis | Written before testing and identifies the likely counterparty or compensated risk |
| Capacity | Position no greater than 1% of median daily volume |

### Paper Trading Success

- At least three consecutive months of unattended operation.
- Zero unexplained reconciliation breaks.
- Paper Sharpe within one estimated standard error of the backtest expectation.
- Median realized slippage no greater than twice modeled slippage.
- At least 99% availability during applicable market hours.
- At least five successful induced-failure recovery exercises.
- A tested tax and recordkeeping process using paper fills.

Any unexplained discrepancy resets the observation clock after its root cause is fixed and regression-tested.

### Live Trading Success

- Tiny-live operation is separately approved and uses only the loss-tolerant capital stated in this charter.
- Risk limits begin at no more than half their approved paper values.
- Six months pass without an unresolved operational incident.
- Live fills, costs, and performance stay within pre-registered tolerances of paper results.
- The observed trade count is sufficient for the claimed statistical conclusion.
- Any scale increase is no greater than two times the previous allocation and requires a fresh approval.

## Loss and Safety Boundaries

The numeric live boundaries are intentionally unresolved because only the owner can decide what can be lost without consequence. This is a blocking state, not permission to rely on defaults.

Until every live boundary is approved:

- Runtime mode must be `PAPER_ONLY`.
- Production broker credentials must not exist in the runtime environment.
- The live broker endpoint must be denied by configuration validation.
- Any request to enable live trading must fail with a message naming the missing approvals.

Independent of owner-selected values, the system must enforce limits for order notional, per-symbol position, gross and net exposure, leverage, orders per minute, daily loss, drawdown, open positions, percent of average daily volume, symbol allowlist, and allowed session hours.

## Abandon Criteria

Any one of these conditions triggers a project stop and a written retrospective:

1. Eighteen months pass after Stage 0 approval without a strategy passing the research promotion gate.
2. Live drawdown reaches the lower of 25% or the owner-approved maximum.
3. Two consecutive quarters of live results fall outside the confidence interval of paper results without an evidence-backed explanation.
4. More than 800 hours are invested without a strategy entering paper trading.
5. The project ceases to be worth the time or becomes an unwanted obligation.
6. A software incident loses more than the daily loss limit; work remains stopped until root cause, remediation, and a passing regression test are documented.
7. Required market data, broker access, legal eligibility, or tax recordkeeping cannot be obtained at a sustainable cost.

Stopping because no durable edge exists is a valid research result, not an engineering failure.

## Governance

- This charter is the highest-level project constraint. A conflicting lower-level document must be changed or rejected.
- Changes to scope, market, broker, instrument, leverage, capital, or promotion thresholds require a dated decision record.
- Promotion decisions require evidence links and explicit owner approval; elapsed time alone never promotes a stage.
- Safety limits may be tightened immediately. Relaxing a safety limit requires review, rationale, and a test update.
- Documentation and automated tests must change in the same work item when a behavioral contract changes.
- Regulatory, tax, broker, and market-data assumptions are reviewed before live launch and at least annually thereafter.

## Stage Zero Sign Off

Stage 0 remains **not passed** until all rows below are complete.

| Gate question | Required answer | Status |
| --- | --- | --- |
| What is being traded? | Liquid US-listed ETFs, daily bars, long-only | Proposed; owner approval required |
| Why might a researched strategy earn a return? | A pre-registered behavioral, structural, or risk-premium thesis specific to that strategy | Not satisfied by the machinery-only SMA strategy |
| How much can be lost before stopping? | Approved currency amount and drawdown limit | `TBD` |
| How much time is available? | Approved weekly hours | `TBD` |
| Is paper broker access eligible and acceptable? | Broker and account confirmation | `TBD` |
| Are abandon criteria accepted? | Owner approval | `TBD` |

**Owner:** Ranjay  
**Owner approval date:** `TBD`  
**Approved version:** `TBD`