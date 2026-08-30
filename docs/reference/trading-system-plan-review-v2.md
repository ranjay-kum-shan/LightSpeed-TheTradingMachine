# Advanced Trading System — Plan Review and Revised Development Plan

<details open>
<summary><b>Contents</b></summary>

- [0. How to read this document](#0-how-to-read-this-document)
- [Part I — Review and Revised Plan](#part-i--review-and-revised-plan)
- [1. Verdict](#1-verdict)
- [2. What v1.0 gets right (keep these verbatim)](#2-what-v10-gets-right-keep-these-verbatim)
- [3. The ten structural problems](#3-the-ten-structural-problems)
  - [3.1 No working artefact until Phase 16](#31-no-working-artefact-until-phase-16)
  - [3.2 Deliverables are documents, not running systems](#32-deliverables-are-documents-not-running-systems)
  - [3.3 Risk controls arrive nine phases too late](#33-risk-controls-arrive-nine-phases-too-late)
  - [3.4 The scope is a fund's roadmap, not a person's](#34-the-scope-is-a-funds-roadmap-not-a-persons)
  - [3.5 Phase 11 (low-latency / HFT) is not economically accessible](#35-phase-11-low-latency--hft-is-not-economically-accessible)
  - [3.6 No cost model, no capital model, no tax model](#36-no-cost-model-no-capital-model-no-tax-model)
  - [3.7 No statistical power analysis and no abandon criterion](#37-no-statistical-power-analysis-and-no-abandon-criterion)
  - [3.8 The technology stack is over-engineered for a single user](#38-the-technology-stack-is-over-engineered-for-a-single-user)
  - [3.9 Missing engineering concerns that actually break live systems](#39-missing-engineering-concerns-that-actually-break-live-systems)
  - [3.10 No time budget, no sequencing of learning, no definition of "enough"](#310-no-time-budget-no-sequencing-of-learning-no-definition-of-enough)
- [4. Revised roadmap](#4-revised-roadmap)
  - [Stage 0 — Decision and constraints (1–2 weeks)](#stage-0--decision-and-constraints-12-weeks)
  - [Stage 1 — Vertical slice (4–6 weeks)](#stage-1--vertical-slice-46-weeks)
  - [Stage 2 — Honest backtesting (6–10 weeks)](#stage-2--honest-backtesting-610-weeks)
  - [Stage 3 — Strategy research with discipline (8–16 weeks)](#stage-3--strategy-research-with-discipline-816-weeks)
  - [Stage 4 — Paper trading (minimum 3 months, non-negotiable)](#stage-4--paper-trading-minimum-3-months-non-negotiable)
  - [Stage 5 — Tiny live (minimum 6 months)](#stage-5--tiny-live-minimum-6-months)
  - [Stage 6 — Conditional deepening (year 2 and later)](#stage-6--conditional-deepening-year-2-and-later)
  - [4.8 Mapping from v1.0 phases](#48-mapping-from-v10-phases)
  - [4.9 The twelve data validation checks](#49-the-twelve-data-validation-checks)
- [5. Gates, criteria and abandon rules](#5-gates-criteria-and-abandon-rules)
  - [5.1 Strategy promotion criteria (research to paper)](#51-strategy-promotion-criteria-research-to-paper)
  - [5.2 Paper to live criteria](#52-paper-to-live-criteria)
  - [5.3 Abandon criteria — the most important section in this document](#53-abandon-criteria--the-most-important-section-in-this-document)
  - [5.4 What honest success looks like](#54-what-honest-success-looks-like)
- [6. Revised technology stack](#6-revised-technology-stack)
  - [6.1 Recommended stack (Stage 1–5)](#61-recommended-stack-stage-15)
  - [6.2 Deferred technologies and their entry conditions](#62-deferred-technologies-and-their-entry-conditions)
- [7. Cost, capital and tax — the missing chapter](#7-cost-capital-and-tax--the-missing-chapter)
  - [7.1 The full cost stack](#71-the-full-cost-stack)
  - [7.2 Minimum viable capital](#72-minimum-viable-capital)
  - [7.3 The FCA regulatory environment (UK retail)](#73-the-fca-regulatory-environment-uk-retail)
  - [7.4 UK tax treatment — three different regimes](#74-uk-tax-treatment--three-different-regimes)
  - [7.5 Record keeping from day one](#75-record-keeping-from-day-one)
- [8. Risk and safety engineering (moved to Stage 1)](#8-risk-and-safety-engineering-moved-to-stage-1)
  - [8.1 Hard limits — enforced in code, before every order](#81-hard-limits--enforced-in-code-before-every-order)
  - [8.2 The three kill switches](#82-the-three-kill-switches)
  - [8.3 Reconciliation](#83-reconciliation)
  - [8.4 Restart semantics](#84-restart-semantics)
- [9. Statistical validation with actual numbers](#9-statistical-validation-with-actual-numbers)
  - [9.1 How much data do you need?](#91-how-much-data-do-you-need)
  - [9.2 Multiple testing](#92-multiple-testing)
  - [9.3 Deflated Sharpe Ratio](#93-deflated-sharpe-ratio)
  - [9.4 Walk-forward, properly](#94-walk-forward-properly)
  - [9.5 Sanity tests to run against your own backtester](#95-sanity-tests-to-run-against-your-own-backtester)
- [10. Engineering failure modes checklist](#10-engineering-failure-modes-checklist)
- [Part II — Trading Fundamentals](#part-ii--trading-fundamentals)
- [11. How markets actually work](#11-how-markets-actually-work)
    - [11.1 The order book](#111-the-order-book)
    - [11.2 Order types](#112-order-types)
    - [11.3 Liquidity, impact and capacity](#113-liquidity-impact-and-capacity)
    - [11.4 Who is on the other side?](#114-who-is-on-the-other-side)
- [12. Returns, risk and the arithmetic that matters](#12-returns-risk-and-the-arithmetic-that-matters)
    - [12.1 Returns](#121-returns)
    - [12.2 Volatility and scaling](#122-volatility-and-scaling)
    - [12.3 Performance metrics](#123-performance-metrics)
    - [12.4 Position sizing](#124-position-sizing)
- [13. Strategy families](#13-strategy-families)
- [14. The ways backtests lie](#14-the-ways-backtests-lie)
- [15. Instruments and leverage](#15-instruments-and-leverage)
    - [15.1 Leverage — the honest version](#151-leverage--the-honest-version)
- [16. Glossary](#16-glossary)
- [17. Reading list, ordered](#17-reading-list-ordered)
- [Appendix A — First 30 days, concrete](#appendix-a--first-30-days-concrete)
- [Appendix B — Summary of changes from v1.0](#appendix-b--summary-of-changes-from-v10)

</details>

---

**Version 2.0 | 30 August 2026**
**Supersedes:** *Advanced Trading System — Master Development Plan v1.0*
**Status:** Review + revision. Part I is the critique and revised roadmap. Part II is a self-contained trading fundamentals primer.

> **Disclaimer.** This document is engineering and research planning, not financial, tax, or investment advice. Tax and regulatory figures cited are current as of August 2026 and change frequently — verify against HMRC/FCA primary sources and a qualified accountant before acting on them. Nothing here is a prediction that any strategy will be profitable.

---

## 0. How to read this document

| Section | Purpose |
|---|---|
| §1–2 | Verdict on v1.0 — what to keep, what to cut |
| §3 | The ten structural problems, each with a concrete fix |
| §4 | Revised roadmap: stages, executable deliverables, hard gates |
| §5 | Gate criteria and abandon criteria (numbers, not adjectives) |
| §6 | Revised technology stack |
| §7 | Cost, capital and tax model — the chapter v1.0 is missing |
| §8 | Risk and safety engineering, moved to day one |
| §9 | Statistical validation with actual formulas |
| §10 | Engineering failure modes checklist |
| **Part II** | Trading fundamentals primer + glossary + reading list |
| §Appendix | First 30 days, concrete |

---

## Part I — Review and Revised Plan

## 1. Verdict

v1.0 is a **well-written description of what a quantitative hedge fund looks like**. It is not a development plan for one person. Its principles are sound and its vocabulary is correct — it knows about point-in-time data, walk-forward validation, implementation shortfall, and survivorship bias, which already puts it ahead of most retail trading content.

But it has one structural flaw that makes it non-executable, and that flaw generates most of the others:

> **The plan produces no working software for its first sixteen phases.** Every deliverable from Phase 0 to Phase 15 is a *specification*, *framework*, or *architecture*. The first thing that touches a live market is Phase 16.

This is a waterfall plan for a domain where the entire value is in the feedback loop. You will not know whether your backtester lies to you until you paper trade against it. You will not know whether your data has silent revisions until you compare a live snapshot against a historical pull. You will not know whether your edge survives costs until you pay them. Every one of those discoveries invalidates earlier specification work — so specifying sixteen layers before validating one is the maximally expensive ordering.

The realistic outcome of executing v1.0 as written: you spend four to eight months writing documents, your enthusiasm decays, and the project is abandoned in Phase 3 or 4 with zero trades placed and zero knowledge gained about whether any of it works.

**Revised approach:** build a deliberately unimpressive but *complete* end-to-end system in six weeks — one asset, one strategy, one broker, real risk limits, real logging, paper money. Then deepen each layer only where measurement shows it is the binding constraint.

---

## 2. What v1.0 gets right (keep these verbatim)

Do not throw the document away. These parts are correct and unusually disciplined for a first draft:

1. **"Profitability is evidence-driven, not assumed."** Keep as the top-line principle.
2. **Separating engineering success from financial success** (§11 of v1.0). This is the single most valuable idea in the document.
3. **Point-in-time data and look-ahead bias** as first-class concerns.
4. **Walk-forward and out-of-sample validation as mandatory.**
5. **Paper trading before capital; tiny capital before scaling.**
6. **Predicting expected return / volatility / probability rather than BUY/SELL labels** (Phase 6). This is a genuinely sophisticated point that most people get wrong.
7. **The anti-overfitting framework (§8)** — conceptually right, needs teeth (see §9 here).
8. **"Maximum validated edge per unit of risk"** as the objective function.
9. **Rejecting the "best trading bot in the world" framing** in favour of measurable targets.
10. **Research memory — recording failed experiments.** Rare and valuable discipline.

---

## 3. The ten structural problems

### 3.1 No working artefact until Phase 16

**Problem.** Sixteen phases of documents. The plan explicitly forbids code: *"Do not write production trading code yet"* (Phase 0) and *"No production trading system should be built until that specification is agreed"* (§13).

**Why it is wrong.** In trading systems the specification is not the hard part — the hard part is the gap between what you specify and what the market actually does. That gap is only measurable by running something. A backtester whose fill model you have never validated against a real fill is a random number generator with good UX.

**Fix.** Invert it. Ship a **vertical slice** first: one instrument → one signal → one backtest → one paper order → one risk check → one log line → one reconciliation. Ugly is fine. Then widen each layer against measured need. See §4, Stage 1.

---

### 3.2 Deliverables are documents, not running systems

**Problem.** "Deliverable: Backtesting engine design and validation methodology." A design is not a deliverable — it is a promise of one.

**Fix.** Every stage in the revised plan has a deliverable you can *execute* and a gate you can *measure*. Replace "specification" with a command:

| v1.0 deliverable | Revised deliverable |
|---|---|
| "Reproducible, validated historical dataset architecture" | `python -m data.build --symbol SPY --start 2010` produces a Parquet file that passes 12 named validation checks |
| "Backtesting engine design and validation methodology" | `python -m backtest.run --config configs/sma.yaml` emits a signed result JSON with run ID, git SHA, data hash |
| "Risk-control specification with failure scenarios" | A `RiskEngine` class with unit tests that reject 15 named bad-order cases |
| "Paper-trading validation report" | 60 consecutive sessions of automated reconciliation, zero unexplained breaks |

---

### 3.3 Risk controls arrive nine phases too late

**Problem.** The Risk Engine is Phase 9; reconciliation is Phase 9; the kill switch is Phase 9. Paper trading is Phase 16 — but any code that can talk to a broker API can send an order, and the most common catastrophic retail-algo failure is a loop bug that fires 4,000 orders in ninety seconds.

**Fix.** Risk limits, the kill switch, and reconciliation are **Stage 1, week one** — before the first order object is ever constructed, even in paper. They are cheap to build in their simple form (a few hundred lines) and they are the only thing standing between a bug and your capital. See §8.

**Additional gap:** v1.0's kill switch assumes the bot is alive to trip it. The dangerous state is the bot being *dead* with open positions. You need a broker-side or external dead-man's switch, not just an internal one.

---

### 3.4 The scope is a fund's roadmap, not a person's

**Problem.** Nine asset classes, eight strategy families, deep learning, FPGA acceleration, kernel-bypass networking, co-location, distributed microservices, autonomous research agents, genetic strategy discovery. This is a headcount of 20–50 engineers and researchers over 5+ years.

**Reality check on hours.** Assume a demanding full-time job and a realistic 8–10 hours/week of focused side project time, i.e. ~450 hours/year. v1.0's Phase 14 alone (distributed infrastructure with message buses, time-series DBs, observability, deployment automation and DR) is a 6-month full-time project for a competent team.

**Fix.** Explicitly split the plan into **In Scope**, **Conditional**, and **Out of Scope** and put the last category in writing so it stops consuming planning energy:

| Bucket | Contents |
|---|---|
| **In scope (year 1)** | One asset class (liquid US/UK equities or ETFs, or FX). Two to three strategy families. Daily or hourly bars. Single-process Python. Paper → tiny live. |
| **Conditional (year 2+, only if gated evidence exists)** | ML models, multi-strategy portfolio, second asset class, intraday bars, execution algorithms |
| **Out of scope (delete from the plan)** | FPGA, co-location, kernel bypass, custom NIC work, autonomous strategy discovery via genetic search, Kafka, distributed services, options market making, order-book microstructure |

The "out of scope" list is not a permanent judgement — it is a statement that these cannot be justified until something much simpler has been shown to work.

---

### 3.5 Phase 11 (low-latency / HFT) is not economically accessible

**Problem.** v1.0 devotes a whole phase to exchange protocols, kernel bypass, NUMA, lock-free structures, specialised NICs, FPGA and co-location economics.

**Why it is wrong.** The latency-sensitive tier of the market is a capital-intensive, membership-gated business. Realistic annual cost floor for a participant competing on latency: exchange co-location racks, direct feed licences, cross-connects, clearing memberships, and a compliance function — comfortably six figures per year per venue before a single line of code. You cannot compete on speed against firms with FPGA-in-the-NIC and a wire-to-wire path measured in tens of nanoseconds using a colocated VPS and Rust.

If you have a firmware and embedded systems background this phase is *seductive* — it is the part you would most enjoy and would be genuinely good at. That is exactly why it needs to be explicitly fenced off. It has no relationship to whether the project makes money and it will absorb unlimited time.

**Fix.** Delete Phase 11 from the roadmap. If low-latency engineering is interesting for its own sake, make it a **separate, clearly labelled learning project** with no dependency on the trading system. Never let it block a trading milestone.

---

### 3.6 No cost model, no capital model, no tax model

**Problem.** v1.0 says "model realistic costs" nine times but never states what they are or does the arithmetic. There is no mention of tax anywhere in the document — for a UK-based individual this is a first-order omission, not a detail.

**Why it matters.** Costs are the difference between most retail strategies working and not working. A round trip on a small UK share position can easily exceed 100 basis points once you count spread, commission and 0.5% stamp duty on the buy. At 100 round trips a year that is a ~100% annual cost drag on the traded notional. No signal survives that.

**Fix.** §7 of this document is the missing chapter: full cost stack, minimum-viable-capital arithmetic, UK tax treatment (SDRT, CGT, spread betting), and the FCA regulatory environment.

---

### 3.7 No statistical power analysis and no abandon criterion

**Problem.** v1.0 requires "statistical significance and multiple-testing safeguards" and says to "track the number of experiments," but gives no method and no numbers. More importantly, there is **no stopping rule.** The plan can only ever conclude "keep going."

**Why it matters.** The key number nobody wants to hear:

> The standard error of an annualised Sharpe ratio is approximately **1 / √(years of data)**.

So a strategy showing an annualised Sharpe of 1.0 over two years of daily data has a standard error of ~0.71. A 95% confidence interval runs roughly from −0.4 to +2.4. You cannot distinguish it from noise. To be confident a Sharpe of 0.5 is real you need on the order of **16 years** of independent data — or a much higher-frequency strategy generating far more independent observations.

**Fix.** §9 gives the formulas and required sample sizes. §5.3 gives explicit abandon criteria — the conditions under which you stop, write up what you learned, and reclaim your evenings.

---

### 3.8 The technology stack is over-engineered for a single user

**Problem.** Rust core, C++ reference implementations, ClickHouse, Kafka/Redpanda, PostgreSQL, Prometheus/Grafana, Docker, PyTorch, FPGA.

**Why it is wrong.** Every one of those is a defensible choice at scale, and every one is a liability at n=1. The bottleneck in a solo quant project is **research iteration speed** — how many hypotheses you can honestly test per week. Rust makes execution fast and iteration slow. Kafka gives you delivery guarantees you do not need between two functions in the same process. ClickHouse solves a data volume problem you will not have for years.

Ten years of daily OHLCV for the entire US equity universe is roughly **1–2 GB in Parquet**. It fits in RAM. DuckDB queries it in milliseconds. You do not need a cluster.

**Fix.** See §6 for the revised stack and the specific evidence that would justify each deferred technology.

---

### 3.9 Missing engineering concerns that actually break live systems

v1.0 covers strategy and statistics well but omits the mundane failures that cause most real incidents:

- **Time.** Timezones, DST transitions, exchange holiday calendars, half-days, clock drift, whether a bar timestamp means open or close. This is the single largest source of silent backtest bugs.
- **Corporate actions.** Splits, dividends, symbol changes, delistings, mergers. An unadjusted split looks like a −50% return and will make any mean-reversion strategy look brilliant.
- **Idempotency and order deduplication.** Network retry sends the order twice. What stops the fill happening twice?
- **Restart semantics.** The bot dies at 14:31 holding three positions and two working orders. What happens at 14:35 when it restarts?
- **Partial fills and rejects.** Handling paths that only exercise in live trading.
- **Broker/API rate limits and outages.** IBKR permits roughly 50 order messages/second; the interesting question is behaviour when you are throttled or disconnected mid-order.
- **Data feed staleness.** A quote that stopped updating looks identical to a quiet market.
- **Secrets handling.** API keys must never reach a repo, a log line, or an exception traceback.
- **Cost of being wrong about the above** — none of it appears in a backtest.

**Fix.** §10 is a checklist. Every item becomes a test.

---

### 3.10 No time budget, no sequencing of learning, no definition of "enough"

**Problem.** Phase 1 asks you to learn market mechanics, probability, statistics, regression, hypothesis testing, Bayesian reasoning, time-series analysis, stationarity, autocorrelation, cointegration, portfolio theory, risk metrics and position sizing — *before writing code*. That is a taught master's module. Gating all implementation behind it guarantees the project dies in the reading phase.

**Fix.** Interleave. Learn each concept at the moment you need it to make a decision, which is when it will actually stick. The revised plan attaches specific learning to specific stages, and Part II of this document front-loads the minimum you need to start.

---

## 4. Revised roadmap

Six stages replace eighteen phases. Each stage has a **goal**, an **executable deliverable**, a **gate** you must pass to proceed, and a **realistic time estimate** at ~8–10 focused hours per week.

The v1.0 phases are not deleted — they are redistributed. The mapping is in §4.8.

---

### Stage 0 — Decision and constraints (1–2 weeks)

**Goal.** Decide what you are actually building and write down what would make you stop.

**Do:**
- Pick **one** market and one time horizon. Recommendation for a first system: **liquid US equities or ETFs, daily bars, holding period 2–20 days.** Reasons: cleanest free-ish data, no stamp duty on US shares, generous liquidity, slow enough that latency and microstructure are irrelevant, fast enough to generate a usable number of trades.
- State your capital budget as a number you can lose entirely without changing any life decision. Write it down.
- State your weekly time budget honestly.
- Open an **Alpaca paper account** (US equities, free, API-first, no deposit required) and/or an **IBKR** account. Alpaca is the lower-friction path to a first paper order; IBKR is the broader, more serious long-term option for a UK resident wanting multi-asset and global access.
- Write the abandon criteria from §5.3 into the repo README, before you are emotionally invested.

**Deliverable.** A one-page `CHARTER.md` in the repo: market, horizon, capital, time budget, success criteria, abandon criteria.

**Gate.** You can answer, in one sentence each: *What am I trading? Who is on the other side of my trade and why are they willing to lose to me? How much am I prepared to lose before I stop?*

If you cannot answer the second question for a strategy, that strategy has no thesis — only a backtest.

---

### Stage 1 — Vertical slice (4–6 weeks)

**Goal.** One complete loop, end to end, ugly, working. This is the single most important stage in the plan.

**Build, in this order:**

1. **Risk engine first.** Before any order code exists. Hard limits: max position size, max notional exposure, max order size, max orders per minute, max daily loss, max open positions. Every one is a hard fail that raises, not a warning that logs. Unit tests for each violation. (§8)
2. **Kill switch + dead-man's switch.** A file or flag that halts all trading; a heartbeat such that if the process stops writing it, an external watchdog flattens or alerts. Test both by killing the process while a position is open.
3. **Data layer.** One symbol, ten years, daily bars, saved to Parquet. Write the twelve validation checks (§4.9) and make them fail loudly. Store a hash of the dataset with every run.
4. **Backtester.** Deliberately simple: a loop over bars, no vectorised cleverness, explicit next-bar execution, explicit costs. The rule that prevents the most common catastrophic bug: **a signal computed from bar *t* may only be executed at bar *t+1*'s open, never *t*'s close.**
5. **One strategy.** A moving-average crossover or a 5-day mean reversion. You expect it not to work. That is the point — you are testing the *machinery*, not the idea.
6. **Paper broker adapter.** Send a real order to a paper account. Handle the reject. Handle the partial fill. Handle the disconnect.
7. **Reconciliation job.** Every morning, compare your internal view of positions/cash against the broker's. Any mismatch stops trading. This runs from day one, not Phase 9.
8. **Logging.** Structured JSON, one line per decision, with run ID, git SHA, data hash, timestamp in UTC, and the inputs that produced the decision. You must be able to replay any decision six months later.

**Deliverable.** `make backtest && make paper` runs the whole loop. A paper order appears in the broker UI. A reconciliation report appears in `reports/`.

**Gate.** Kill the process mid-session while holding a position. Restart it. It recovers to a correct, reconciled state without human intervention and without duplicating an order.

**What you will learn here** is worth more than the next four phases of v1.0's documents.

---

### Stage 2 — Honest backtesting (6–10 weeks)

**Goal.** Make the backtester stop lying to you.

**Do:**
- **Cost model.** Explicit spread, commission (including per-order minimums), slippage assumption, financing/borrow, and taxes. Make costs a required config field with no default — you should have to consciously state them.
- **Sensitivity harness.** Re-run every result at 1×, 2× and 4× your assumed costs. If the edge vanishes at 2×, it does not exist.
- **Corporate actions.** Split and dividend adjustment, delisted symbols included. If your universe only contains companies that exist today, your backtest is measuring survivorship, not skill.
- **Survivorship-free universe.** This is where free data (`yfinance`) fails hard. Either accept the bias explicitly and only trade a fixed, liquid, pre-selected universe, or budget for a point-in-time dataset (Norgate, Sharadar, or similar) — a few hundred pounds a year. There is no free correct option.
- **Walk-forward harness.** Rolling train/test windows, no peeking. Report out-of-sample only.
- **Deterministic replay.** Same config + same data hash + same seed → byte-identical results. Assert it in CI.
- **Experiment log.** Every run recorded automatically: config, data hash, git SHA, results. This is v1.0's "research memory" and it is genuinely important — but it should be a database table written by the runner, not a discipline you maintain by hand.

**Deliverable.** A backtest report that includes: net-of-cost equity curve, out-of-sample-only metrics, cost sensitivity table, number of independent trades, Sharpe with its standard error, and turnover.

**Gate.** Run a **deliberately broken strategy** (e.g. one using tomorrow's close) and confirm your look-ahead detector catches it. Run a random-signal strategy and confirm it produces a net-negative result of roughly the size of your cost assumption. If a coin flip makes money in your backtester, your backtester is broken.

---

### Stage 3 — Strategy research with discipline (8–16 weeks)

**Goal.** Test real hypotheses without fooling yourself.

**Do:**
- Work through 2–3 strategy families: **cross-sectional momentum**, **time-series trend following**, **short-horizon mean reversion**. These are the best-documented and most robust families in the public literature, which means you can compare your results against published ones — a rare and valuable sanity check.
- For each: write the **economic thesis first**, before the backtest. Who is on the other side? Is it a risk premium (you are being paid to hold something uncomfortable), a structural constraint (someone must trade regardless of price), or a behavioural bias? If you cannot name it, you are curve fitting.
- Pre-register: parameters, universe, test period, and success threshold — *written down before running*.
- Count every backtest you run. That count is your multiple-testing burden and feeds directly into §9's deflated Sharpe calculation.
- Parameter sensitivity: plot performance across the parameter grid. A real edge is a *plateau*; an artefact is a *spike*.

**Deliverable.** A ranked candidate list, each with: thesis, out-of-sample metrics net of 2× costs, parameter sensitivity plot, trade count, Sharpe standard error, and deflated Sharpe.

**Gate.** At least one strategy passes §5.1's promotion criteria. If none does after 16 weeks — that is a legitimate and informative result. See §5.3.

---

### Stage 4 — Paper trading (minimum 3 months, non-negotiable)

**Goal.** Measure the gap between your simulation and reality.

**Do:**
- Run the promoted strategy live-data/paper-money, fully automated, unattended, every session.
- Log **every** divergence: your expected fill price vs actual, expected signal vs actual, expected position vs reconciled position.
- Track the **backtest-vs-paper tracking error** as the headline metric. This number is the honest measure of how much your backtest can be trusted.
- Deliberately induce failures: kill the network mid-order, feed stale data, send a duplicate order, restart mid-session, run through an exchange holiday, run through a DST transition.

**Deliverable.** A monthly paper report: realised vs expected P&L, slippage distribution, uptime, number of unexplained events (target: zero).

**Gate.** Three months of unattended operation, zero unexplained reconciliation breaks, and paper P&L within a pre-stated tolerance of backtest expectation. Any unexplained discrepancy resets the clock. This gate is where most projects should — and do — stop.

---

### Stage 5 — Tiny live (minimum 6 months)

**Goal.** Find out what paper trading was still hiding: real fills, real queue position, real financing, real tax, real emotions.

**Do:**
- Deploy the capital you defined in Stage 0 — **and treat it as already spent.** Ideally 1–5% of what you might eventually consider.
- Halve every risk limit relative to the paper configuration.
- Do not touch the strategy for the first three months. Every intervention destroys the sample.
- Track live vs paper vs backtest as three separate curves. The gaps are the interesting data.
- Keep records for tax from day one (§7.4) — retrospective reconstruction of a year of trades is genuinely painful.

**Gate to scale.** Six months live, results within tolerance of paper, no operational incidents, and — critically — a trade count large enough that the result is statistically meaningful (§9). Scale in steps of no more than 2× at a time.

---

### Stage 6 — Conditional deepening (year 2 and later)

Only unlock these against specific measured evidence. Each has an entry condition:

| Capability | Entry condition |
|---|---|
| Second strategy family / portfolio engine | Strategy 1 has 6+ months of live evidence and you can measure its correlation to a candidate strategy 2 |
| Machine learning | You have a validated non-ML baseline to beat, and enough independent observations that an ML model cannot trivially memorise them |
| Regime detection | You have measured that your strategy's performance actually differs across measured regimes |
| Execution algorithms (slicing, VWAP) | Measured slippage is a material fraction of your edge — i.e. your orders are moving the market |
| Intraday / higher frequency | Daily-horizon research is exhausted, and you have priced intraday data |
| Rust / performance work | Profiling shows compute time is the binding constraint on research throughput |
| AI research assistant | You have ≥50 logged experiments for it to learn from and a validation gate it cannot bypass |
| Low latency / FPGA / co-location | **Never, within this project.** See §3.5. |

---

### 4.8 Mapping from v1.0 phases

| v1.0 | Revised location | Change |
|---|---|---|
| Phase 0 | Stage 0 | Kept, compressed to one page, abandon criteria added |
| Phase 1 | Distributed across all stages + Part II | No longer a blocking gate |
| Phase 2 | Stage 1 (minimal) + Stage 2 (full) | Split; PIT data deferred until needed |
| Phase 3 | Stage 2 | Experiment tracking automated, not manual |
| Phase 4 | Stage 1 (simple) + Stage 2 (honest) | Split; validation tests added |
| Phase 5 | Stage 3 | Narrowed to 3 families; economic thesis required first |
| Phase 6 (ML) | Stage 6, conditional | Deferred behind a baseline requirement |
| Phase 7 (regime) | Stage 6, conditional | Deferred behind measurement |
| Phase 8 (portfolio) | Stage 6, conditional | Deferred until 2 live strategies exist |
| Phase 9 (risk) | **Stage 1, week 1** | Moved to the front — the most important change |
| Phase 10 (execution) | Stage 6, conditional | Deferred until slippage is measured as material |
| Phase 11 (low latency) | **Deleted** | Not economically accessible; see §3.5 |
| Phase 12 (AI research) | Stage 6, conditional | Deferred behind experiment volume |
| Phase 13 (auto discovery) | **Deleted** | Overfitting accelerator at this data scale |
| Phase 14 (distributed) | **Deleted** | Single process is correct for n=1 |
| Phase 15 (security/ops) | Stage 1 (secrets, logs) + Stage 4 (failure testing) | Split and pulled forward |
| Phase 16 (paper) | Stage 4 | Kept, given a hard 3-month minimum |
| Phase 17 (tiny live) | Stage 5 | Kept, given a hard 6-month minimum |
| Phase 18 (continuous) | Ongoing from Stage 5 | Kept |

---

### 4.9 The twelve data validation checks

Run these on every dataset build. Each must fail loudly, not warn.

1. No duplicate timestamps per symbol.
2. No gaps on expected trading days (against an exchange calendar, not a weekday rule).
3. All timestamps timezone-aware and stored in UTC.
4. `low ≤ open, close ≤ high` for every bar.
5. No non-positive prices or volumes where they are impossible.
6. No single-bar return exceeding a plausible bound (e.g. ±50%) without a corresponding corporate action record.
7. Adjusted and unadjusted series both present and reconcilable.
8. Volume not identically zero for a supposedly liquid symbol.
9. No NaNs in required fields after the documented warm-up period.
10. Row count within tolerance of expected trading days.
11. Dataset content hash recorded and stored with every backtest run.
12. Re-pulling the same historical window produces identical data — **vendors silently revise history**, and if you do not detect it, your "reproducible" backtest is not.

---

## 5. Gates, criteria and abandon rules

v1.0's "Definition of Done" is a list of adjectives. Here are numbers. Adjust them to your own risk appetite — but set them *before* you see results, and write them down.

### 5.1 Strategy promotion criteria (research to paper)

A strategy may be promoted only if **all** hold:

| Criterion | Threshold | Why |
|---|---|---|
| Out-of-sample annualised Sharpe, net of costs | ≥ 0.7 | Below this, costs and estimation error dominate |
| Sharpe at 2× assumed costs | Still > 0 | Your cost estimate is optimistic. It always is. |
| Independent trades in the OOS period | ≥ 100 | Fewer and the result is anecdote |
| Deflated Sharpe ratio (§9.3) | > 0 at 95% | Corrects for how many things you tried |
| Max drawdown | ≤ 25%, and ≤ 2× the worst in-sample DD | You will not survive worse in live trading |
| Parameter sensitivity | Plateau, not spike | A spike is an artefact |
| Economic thesis | Written, one paragraph, names the counterparty | No thesis = no trade |
| Capacity | Position size ≤ 1% of the instrument's median daily volume | Otherwise you are your own adversary |

### 5.2 Paper to live criteria

| Criterion | Threshold |
|---|---|
| Unattended paper trading duration | ≥ 3 months |
| Unexplained reconciliation breaks | 0 |
| Paper Sharpe vs backtest Sharpe | Within 1 standard error |
| Median slippage vs modelled slippage | Within 2× |
| System uptime during market hours | ≥ 99% |
| Recovery from induced failure | Automatic, tested at least 5 times |
| Tax and record-keeping process | Documented and tested on paper trades |

### 5.3 Abandon criteria — the most important section in this document

v1.0 has no stopping rule. Add these. Any single one triggers a full stop and a written retrospective:

1. **18 months** from Stage 0 with no strategy passing §5.1.
2. **Live drawdown exceeds 25%** of allocated capital, or your pre-stated maximum loss is hit.
3. **Two consecutive quarters** where live results fall outside the confidence interval of paper results, and you cannot explain why.
4. **Total time invested exceeds 800 hours** with no strategy in paper trading.
5. **The project stops being interesting** and becomes an obligation — sunk cost is not a reason to continue a negative-expectancy activity.
6. **Any live incident** that loses more than your daily loss limit due to a software bug, until root cause is found and a regression test exists.

Stopping is a legitimate, information-rich outcome. Most people who build a trading system find no durable edge; the ones who benefit are those who learn a great deal about data engineering, statistics and their own psychology, and who stop *deliberately* rather than through slow attrition or a blown account.

### 5.4 What honest success looks like

Be explicit about the base rate. FCA-mandated disclosures on UK retail leveraged trading platforms consistently show that a large majority of retail accounts lose money — figures in the 65–76% range are typical across major brokers. That is the population you are joining. Your engineering background is a genuine advantage on the *systems* half of the problem, and no advantage at all on the *edge* half.

Reasonable definitions of success, ranked by realism:

1. **You build a reliable, correct, well-tested trading system and learn a large amount of applied statistics and data engineering.** Very achievable. Genuinely transferable — data pipelines, validation, reproducibility, and live-system reliability are marketable skills in their own right.
2. **You find a small, real, capacity-constrained edge that pays for the data and beats a savings account after tax.** Achievable but uncommon; expect years, not months.
3. **You generate meaningful investment income.** Rare. Requires either significant capital or an unusual and durable edge.
4. **You beat professional quant funds.** No.

Optimise for #1 and treat #2 as upside. That framing keeps the project healthy regardless of market outcome.

---

## 6. Revised technology stack

**Principle: minimise everything that is not research iteration speed.**

### 6.1 Recommended stack (Stage 1–5)

| Layer | Choice | Rationale |
|---|---|---|
| Language | **Python 3.12+**, single process | Research velocity dominates. Nothing at daily/hourly horizon needs more. |
| Data manipulation | **polars** (or pandas) | polars is faster and its lazy API discourages accidental look-ahead |
| Storage | **Parquet files + DuckDB** | 10 years of daily US equity data ≈ 1–2 GB. Fits in RAM. No server to run. |
| Numerics | numpy, scipy, statsmodels | statsmodels for proper hypothesis tests |
| Backtester | **Write your own, simple, event-loop** | The learning value is high and the code is ~500 lines. Evaluate `vectorbt` for fast parameter sweeps and `nautilus_trader` if you later want a Rust-core engine with a Python API. |
| Broker | **Alpaca** (paper + US equities) and/or **IBKR** via `ib_async` | Alpaca: fastest path to a first paper order, free paper environment, API-first. IBKR: far broader instrument and market coverage, the serious long-term choice for a UK resident. |
| Config | YAML + pydantic | Typed, validated config; every run reproducible from its config file |
| Experiment tracking | SQLite table, or MLflow if it earns its place | Start with SQLite. It is a table with 10 columns. |
| Scheduling | systemd timer or cron | Not Airflow |
| Monitoring | Structured JSON logs + a daily email/Telegram report | Grafana when you have something worth a dashboard |
| Secrets | Environment variables via `.env`, `.gitignore`d; consider `sops`/`age` for encrypted-at-rest | Never in code, never in logs, never in tracebacks |
| Testing | pytest, with property-based tests (`hypothesis`) on the risk engine | The risk engine is the one component where a bug is expensive |
| Version control | git, with the SHA embedded in every result artefact | Non-negotiable for reproducibility |

### 6.2 Deferred technologies and their entry conditions

| Technology | v1.0 role | Defer until |
|---|---|---|
| **Rust** | "Core infrastructure, execution, networking" | Profiling shows a Python hot path is the binding constraint on research throughput. Then rewrite *that function*, not the system. |
| **C++** | "Low-latency reference" | Never in this project |
| **ClickHouse** | "High-volume analytical workloads" | Dataset exceeds ~50 GB or DuckDB queries exceed ~30s |
| **Kafka/Redpanda** | "Event-streaming backbone" | Multiple independent processes genuinely need durable decoupled messaging. A single process does not. |
| **PostgreSQL** | "Transactional metadata" | You have live state that must survive a crash and SQLite's concurrency limits actually bite |
| **Prometheus/Grafana** | "Observability" | You have >1 service and a daily report is no longer sufficient |
| **PyTorch** | "Deep learning" | You have a validated linear/tree baseline *and* enough independent samples. sklearn + LightGBM covers the realistic 95%. |
| **Docker** | "Deployment foundation" | Useful early for reproducible environments — but as a dev convenience, not a deployment architecture |
| **FPGA** | "Hardware acceleration" | Never |

A note on the Rust question specifically: if your instincts are shaped by embedded and firmware work, Rust and C++ will feel like the natural home for "the serious part" of the system. In this domain that instinct is inverted. The serious part is the statistics, and the expensive resource is your research iteration time. Keep the system in Python until measurement says otherwise.

---

## 7. Cost, capital and tax — the missing chapter

### 7.1 The full cost stack

Every one of these must be in the backtest. Most retail backtests include only the first two.

| Cost | Typical magnitude | Notes |
|---|---|---|
| **Bid-ask spread** | 1–5 bps liquid large-cap; 20–100+ bps small-cap | You pay roughly half the spread each way if you cross |
| **Commission** | Per-share, per-order or per-value; often with a per-order minimum | The minimum is what destroys small accounts |
| **Slippage / market impact** | Grows with order size relative to volume | Roughly proportional to (order size / ADV)^0.5 in common models |
| **Stamp duty (SDRT)** | **0.5% on UK share purchases** | Buy side only. UK-specific and brutal for short holding periods. |
| **Financing / margin interest** | Broker rate, often base + a spread | On any leveraged or overnight-financed position |
| **Short borrow fee** | 0.3% to >20% annualised | Hard-to-borrow names can be uneconomic to short |
| **FX conversion** | 0.03%–0.5%+ depending on broker | Relevant for a GBP-based account trading USD assets |
| **Market data subscriptions** | £0 to hundreds per month | Real-time exchange data is not free |
| **Historical data** | £0 (biased) to £300–1,500/yr (point-in-time) | The survivorship-free option costs money |
| **Infrastructure** | £0–50/month | A small VPS |
| **Tax on gains** | See §7.4 | Frequently ignored entirely in backtests |

### 7.2 Minimum viable capital

The arithmetic that determines whether a strategy is even possible at your account size:

```
required_edge_per_trade  >  round_trip_cost_bps
annual_cost_drag         =  round_trip_cost_bps × round_trips_per_year
```

**Worked example A — UK share, small account.**
£500 position, £3 commission each way, 10 bps spread, 0.5% stamp duty on the buy.

```
Commission:   £6 / £500                    = 120 bps
Spread:       ~10 bps round trip           =  10 bps
Stamp duty:   0.5% on buy                  =  50 bps
                                          ---------
Round-trip cost                            = 180 bps  (1.8%)
```

At 50 round trips a year this is a **90% annual drag on traded notional**. No realistic edge survives. Conclusion: **UK shares in small size with frequent trading is structurally unviable.** This is arithmetic, not opinion — and v1.0's roadmap would have had you discover it in Phase 16.

**Worked example B — US ETF, commission-free.**
£5,000 position, zero commission, 2 bps spread, no stamp duty.

```
Spread:       ~2 bps round trip            =   2 bps
Slippage:     ~1 bp (small vs ADV)         =   1 bp
                                          ---------
Round-trip cost                            =   3 bps
```

At 50 round trips a year: **1.5% annual drag.** Viable — a strategy needs only to clear that plus your required return.

**Practical implications:**
- Prefer **larger position sizes and fewer trades** at small capital. Cost per trade is roughly fixed; cost as a *percentage* falls as position size rises.
- Prefer **commission-free or per-share pricing** over per-order minimums.
- Prefer **US instruments over UK shares** for anything with turnover, purely on stamp duty.
- Below roughly **£5,000–10,000** of trading capital, cost drag dominates almost any edge. Below that, treat the project as pure learning and stay in paper trading — the marginal knowledge from live trading £500 is small and the marginal cost is high.

### 7.3 The FCA regulatory environment (UK retail)

Relevant if you use leveraged products:

- Under FCA policy statement PS19/18, retail leverage on CFDs and CFD-like options is capped between 30:1 and 2:1 depending on the volatility of the underlying; firms must close out a retail client's position when funds fall to 50% of the margin required to maintain open positions; and firms must guarantee a client cannot lose more than the total funds in the trading account. Crypto CFDs are banned for UK retail clients and available only to elected professionals.
- Negative balance protection applies to **retail** clients of FCA-authorised firms only. Electing professional-client status forfeits FCA leverage protections, Financial Ombudsman Service access, and FSCS protection. Do not elect professional status simply to obtain more leverage.
- The 50% margin close-out rule matters for system design: your broker may liquidate you automatically. Your risk engine must keep you far from that boundary, not near it.

### 7.4 UK tax treatment — three different regimes

This materially changes which instrument you should trade, and v1.0 does not mention it at all. **Verify with an accountant; this is a summary, not advice.**

**Direct shares (owning the asset)**
- SDRT is charged at 0.5% of the purchase price when you buy UK shares electronically, collected automatically by the broker. No SDRT on sales. **US shares are not subject to it.**
- Two current exemptions worth knowing: AIM-listed shares are exempt from stamp duty and SDRT; and, from 27 November 2025, shares are exempt from the 0.5% SDRT charge for the first three years following a company's new listing on a UK regulated market (gov.uk, "Stamp Duty Reserve Tax — UK Listing Relief"). Note also that a single Securities Transfer Tax is proposed to replace stamp duty and SDRT from 2027 — worth tracking.
- Gains fall under Capital Gains Tax. For 2026/27: 18% within the basic-rate band, 24% above it, with a £3,000 annual exempt amount.
- **The share matching rules are the practical problem for an algorithmic trader.** Disposals are matched against acquisitions on the same day, then acquisitions in the following 30 days (the "bed and breakfast" rule), then the Section 104 pooled holding. A bot that repeatedly re-enters the same symbol generates a matching nightmare. Budget real engineering effort for tax lot tracking, or choose an instrument that avoids it.
- Reported via Self Assessment.

**CFDs**
- No stamp duty (you do not own the asset). Gains are subject to CGT at 18%/24% above the annual exempt amount — and, importantly, **CFD losses can be offset against other capital gains.**
- Leveraged, with overnight financing charges that accumulate — these must be modelled in your backtest, not ignored.

**Spread betting**
- HMRC classifies spread betting as gambling rather than investing (Business Income Manual BIM22015), so for most retail traders it is exempt — no CGT and no stamp duty.
- The trade-off: because spread betting sits outside the CGT regime, **losses cannot be offset against other capital gains.** Tax-free runs in both directions.
- Caveat worth taking seriously (HMRC BIM22020): if spread betting becomes your primary source of income and is conducted as a business or trade, the exempt status may be challenged and profits could become taxable as income. This affects only a small minority of very high-volume traders — but it is a real edge case.
- Costs are embedded in a wider spread rather than charged as commission, so the *pre-tax* cost is generally higher. The comparison is: wider spread vs (tighter spread + CGT + possibly SDRT).

**A note on ISAs.** Gains inside a stocks-and-shares ISA are CGT-free, and the annual allowance is £20,000. But ISA rules restrict eligible investments and most ISA providers do not offer API access. Worth checking whether your chosen broker offers an ISA wrapper with programmatic access before assuming you can use one.

**Practical guidance:** model your after-tax return in the backtest. A strategy with a 6% pre-tax return and 100% annual turnover looks materially different at 24% CGT than at 0%. And the instrument choice — shares vs CFD vs spread bet — can swing the net result more than a lot of strategy tuning will.

### 7.5 Record keeping from day one

Log for every fill: UTC timestamp, symbol, side, quantity, price, commission, taxes, FX rate applied, order ID, broker fill ID, and strategy ID. Reconstructing a year of trades retrospectively for a tax return is a genuinely miserable exercise, and broker statements are often insufficient on their own.

---

## 8. Risk and safety engineering (moved to Stage 1)

### 8.1 Hard limits — enforced in code, before every order

v1.0's §9 list is good. Make each one a hard exception, not a log line:

```python
class RiskLimits:
    max_position_notional: float      # per symbol
    max_gross_exposure: float         # sum of |positions|
    max_net_exposure: float           # sum of positions
    max_leverage: float
    max_order_notional: float         # single order
    max_orders_per_minute: int        # loop-bug protection
    max_daily_loss: float             # halt for the day
    max_drawdown_from_peak: float     # halt entirely
    max_open_positions: int
    max_position_pct_of_adv: float    # capacity / liquidity
    allowed_symbols: set[str]         # whitelist, not blacklist
    allowed_hours: TimeWindow         # no accidental after-hours orders
```

**`max_orders_per_minute` is the one that saves you.** The characteristic retail-algo disaster is not a bad prediction — it is a loop that resubmits because it did not see its own fill.

### 8.2 The three kill switches

1. **Internal.** A flag the strategy checks; halts new orders, optionally flattens.
2. **External file/API.** `touch KILL` in the working directory halts everything within one cycle, no code change and no redeploy.
3. **Dead-man's switch.** The bot writes a heartbeat every N seconds. An *independent* watchdog process (or hosted uptime monitor) alerts you — and ideally cancels working orders — if the heartbeat stops. **This is the one v1.0 omits, and it covers the worst state: your process is dead and your positions are not.**

Where the broker supports it, also set **server-side stop orders** as a backstop. A stop resting at the exchange survives your VPS dying.

### 8.3 Reconciliation

Daily, and on every restart:

```
broker_positions == internal_positions
broker_cash      == internal_cash      (within tolerance)
broker_orders    == internal_orders
```

Any mismatch: **halt trading, alert, do not auto-resolve.** A reconciliation break means your model of the world is wrong, and trading on a wrong model is how small bugs become large losses.

### 8.4 Restart semantics

Define explicitly, before you need them:
- On startup, fetch open orders and positions from the broker and reconcile against your last persisted intent. Do not assume a clean slate.
- Are working orders from the previous session cancelled or adopted?
- Use client-side order IDs so a retry cannot create a duplicate.
- Persist strategy state (indicators, warm-up buffers) or make it deterministically recomputable from data.
- Test by killing `-9` mid-session with an open position. Repeatedly.

---

## 9. Statistical validation with actual numbers

v1.0's §8 lists the right concepts. Here are the methods.

### 9.1 How much data do you need?

For approximately IID returns, the standard error of an estimated Sharpe ratio (Lo, 2002) is:

```
SE(SR) ≈ sqrt( (1 + SR² / 2) / N )
```

where `SR` and `N` are measured at the same frequency. Annualising gives the practical rule of thumb:

```
SE(annualised SR) ≈ 1 / sqrt(years of data)
```

| Observed annualised Sharpe | Years needed for ~95% confidence it exceeds 0 |
|---|---|
| 0.3 | ~44 years |
| 0.5 | ~16 years |
| 1.0 | ~4 years |
| 1.5 | ~1.8 years |
| 2.0 | ~1 year |

**Read this table before believing any backtest.** It explains why a strategy with three years of data and a Sharpe of 0.6 is essentially uninformative, and why claims of quickly validating a modest edge are not credible. It is also the strongest argument for strategies that generate many independent observations — cross-sectional strategies across hundreds of names produce far more information per calendar year than a single-instrument timing strategy.

Two caveats: financial returns are not IID (autocorrelation and fat tails inflate the true standard error), and overlapping positions reduce your effective sample below your nominal trade count.

### 9.2 Multiple testing

If you test 100 strategies against a 5% significance threshold, you expect ~5 false positives by construction. Your backtest count is a liability that must be tracked and paid for.

- **Log every backtest automatically** — the runner writes the row, you do not.
- Apply a correction: Bonferroni (conservative: α/n) or Benjamini–Hochberg (controls false discovery rate; usually the better choice).
- Recognise that *parameter tuning is also testing*. Trying 20 lookback windows is 20 tests, not one strategy.

### 9.3 Deflated Sharpe Ratio

Bailey & López de Prado's Deflated Sharpe Ratio adjusts an observed Sharpe for (a) the number of trials, (b) non-normality of returns (skew and kurtosis), and (c) sample length. It answers the actual question: *given that I tried N things, how likely is this result to be real?*

Implement it once, apply it to every promotion decision, and feed it your honest trial count. If your DSR is negative, you have found a fitting artefact regardless of how good the equity curve looks.

### 9.4 Walk-forward, properly

- Rolling or anchored windows; train on `[t-k, t)`, test on `[t, t+m)`, roll forward.
- **Purge and embargo.** If a feature uses a 20-day lookback, leave at least 20 days between train and test, or the boundary leaks.
- Report **only the concatenated out-of-sample results**. In-sample results are for debugging, never for decisions.
- Never re-tune parameters after seeing the test set. If you do, it is no longer a test set — it is a second training set, and you now need a fresh one.

### 9.5 Sanity tests to run against your own backtester

| Test | Expected result |
|---|---|
| Random-signal strategy | Net return ≈ −(cost per trade × trade count) |
| Strategy using tomorrow's close | Absurdly high Sharpe → confirms your leak detector is off, and validates it once you add one |
| Buy-and-hold benchmark | Matches published index returns for the period |
| Zero-cost mode vs realistic-cost mode | Difference exactly equals modelled costs |
| Shuffled returns | Edge disappears (if it does not, you have a bug) |
| Same config, twice | Byte-identical output |

---

## 10. Engineering failure modes checklist

Each becomes a test.

**Time**
- [ ] All internal timestamps UTC and timezone-aware
- [ ] Exchange calendar used, not weekday arithmetic
- [ ] Half-days and early closes handled
- [ ] DST transitions tested in both directions
- [ ] Bar timestamp convention documented (open vs close) and consistent
- [ ] Clock sync (NTP) on the trading host

**Data**
- [ ] Corporate actions applied; adjusted and raw both available
- [ ] Delisted symbols present in the historical universe
- [ ] Stale-feed detection (last update age vs threshold)
- [ ] Vendor revision detection via content hashing
- [ ] Data gaps fail loudly rather than forward-fill silently

**Orders**
- [ ] Client-side order IDs; retries are idempotent
- [ ] Partial fills handled and tested
- [ ] Rejects handled and tested
- [ ] Cancel/replace race conditions handled
- [ ] Rate limits respected with backoff
- [ ] No orders outside allowed hours

**State**
- [ ] Restart mid-session recovers correctly
- [ ] Positions reconciled on every startup
- [ ] Strategy warm-up state persisted or deterministically recomputable
- [ ] Crash during order submission leaves a recoverable state

**Ops**
- [ ] Secrets never in code, repo, logs or tracebacks
- [ ] Structured logs with run ID + git SHA + data hash
- [ ] Daily report delivered even when nothing traded (silence must not equal "fine")
- [ ] Alerting on: reconciliation break, risk-limit hit, heartbeat loss, feed staleness
- [ ] Backup and restore of the state database tested

**Statistics**
- [ ] Look-ahead detector implemented and validated on a deliberately broken strategy
- [ ] Every backtest logged with config, data hash, git SHA
- [ ] Costs required in config, no silent defaults
- [ ] Out-of-sample results reported separately, always

---

## Part II — Trading Fundamentals

*This is the minimum working knowledge needed to make sensible decisions in Part I. It is deliberately compressed. v1.0's Phase 1 was a reading list that blocks all progress; this is the subset you actually need before writing code, and the rest is best learned when a specific decision requires it.*

---

## 11. How markets actually work

### 11.1 The order book

An exchange maintains a **limit order book** per instrument: a sorted list of resting buy orders (**bids**) and sell orders (**asks/offers**).

```
        ASKS (people willing to sell)
  102.05  x  500
  102.03  x  200
  102.01  x  100     ← best ask
  ---------------    ← spread = 0.02
  101.99  x  300     ← best bid
  101.97  x  800
  101.95  x 1200
        BIDS (people willing to buy)
```

- **Best bid** — highest price a buyer will pay. **Best ask** — lowest price a seller will accept.
- **Spread** — the gap. It is a real cost: buy at the ask, sell at the bid, and you lose the spread instantly.
- **Mid price** — (bid + ask) / 2. A convenient fiction; you cannot generally trade there.
- **Depth** — quantity available at each level. Thin depth means your order moves the price.

**Key consequence.** Backtests that assume you trade at the closing price or the mid are systematically optimistic. Assume you cross the spread unless you have specifically modelled passive execution and the associated risk of not being filled at all.

### 11.2 Order types

| Type | Behaviour | Use |
|---|---|---|
| **Market** | Execute immediately at the best available price | Certain execution, uncertain price. Dangerous in thin markets. |
| **Limit** | Execute only at your price or better | Certain price, uncertain execution. May never fill. |
| **Stop (stop-loss)** | Becomes a market order when a trigger price is touched | Risk control. Note: no guaranteed price — a gap can fill you far below. |
| **Stop-limit** | Becomes a limit order at the trigger | Price protection, but may not fill at all — the worst outcome in a crash |
| **Market-on-close (MOC)** | Executes in the closing auction | Useful for daily-bar strategies; deep liquidity, deterministic timing |
| **IOC / FOK** | Immediate-or-cancel / fill-or-kill | Partial or all-or-nothing execution control |
| **GTC vs DAY** | Good-till-cancelled vs expires at session end | **GTC by accident is a classic bug** — a stale order fires days later |

### 11.3 Liquidity, impact and capacity

- **ADV** — average daily volume. Your practical capacity constraint.
- **Market impact** — your own buying pushes the price up. Commonly modelled as growing with the square root of (order size / ADV).
- **Rule of thumb.** Keep orders below ~1% of ADV and impact is usually negligible. Above ~5% you are the market.
- **Capacity** is why strategies decay: an edge that works on £10k may not exist at £10m, and edges published in papers are often already arbitraged away in liquid names.

### 11.4 Who is on the other side?

The most important question in trading, and the one v1.0 only gestures at.

Every trade has a counterparty. If you consistently make money, someone consistently loses it, or is paying you for a service. Legitimate sources of edge:

1. **Risk premia.** You are paid to hold something others find uncomfortable — equity risk, volatility risk, carry, illiquidity. Durable, but low Sharpe and correlated with everyone else's pain.
2. **Structural constraints.** Someone must trade regardless of price: index funds rebalancing on schedule, funds with mandate restrictions, forced liquidations, month-end flows. Durable while the constraint exists.
3. **Behavioural biases.** Overreaction, underreaction, disposition effect, attention effects. Real but crowded and decaying.
4. **Information or speed.** Requires resources you do not have. Not accessible.
5. **Providing liquidity.** Being paid the spread for immediacy. Requires infrastructure and inventory risk management.

Categories 1–3 are the realistic space for a retail systematic trader. If a strategy's thesis is "the backtest says so," it belongs to category 6: **noise**.

---

## 12. Returns, risk and the arithmetic that matters

### 12.1 Returns

```
simple return  r  = (P_t − P_{t−1}) / P_{t−1}
log return     ℓ  = ln(P_t / P_{t−1})
```

Log returns add across time, which makes them convenient for multi-period work. Simple returns add across a portfolio at a point in time. Use each where it is correct.

**Compounding is asymmetric and it is the reason drawdowns matter:**

| Loss | Gain required to recover |
|---|---|
| −10% | +11% |
| −20% | +25% |
| −33% | +50% |
| −50% | +100% |
| −80% | +400% |

This is why risk control beats return maximisation, and why v1.0's principle "risk management has priority over return maximisation" is correct.

### 12.2 Volatility and scaling

Volatility is the standard deviation of returns. It scales approximately with the square root of time:

```
σ_annual ≈ σ_daily × √252
```

(252 trading days per year.) A daily volatility of 1% is roughly 16% annualised. This square-root scaling underlies almost every risk calculation you will do — and it breaks down precisely when it matters most, because returns are not IID and volatility clusters (calm periods follow calm periods, crises follow crises).

### 12.3 Performance metrics

| Metric | Formula | Meaning | Watch out for |
|---|---|---|---|
| **Sharpe ratio** | (R − Rf) / σ | Excess return per unit of total volatility | Punishes upside volatility equally; assumes roughly normal returns; hugely noisy in small samples (§9.1) |
| **Sortino ratio** | (R − Rf) / σ_downside | Return per unit of *downside* volatility | Fewer observations in the denominator → even noisier |
| **Max drawdown** | max peak-to-trough decline | Worst historical loss | A single-observation statistic — expect worse in future |
| **Calmar ratio** | annual return / max DD | Return per unit of worst pain | Very sensitive to sample length |
| **Hit rate** | % of winning trades | How often you are right | Meaningless alone — 90% hit rate with a 10:1 loss ratio still loses money |
| **Payoff ratio** | avg win / avg loss | Size asymmetry | The necessary companion to hit rate |
| **Expectancy** | (hit × avg win) − ((1−hit) × avg loss) | Expected profit per trade | **Must exceed cost per trade.** This is the real test. |
| **Turnover** | traded notional / capital, annualised | How much you trade | Directly multiplies your cost drag |
| **Exposure** | % of time in the market | Capital efficiency | A strategy in the market 5% of the time has a different risk profile than the raw Sharpe suggests |

**Two metrics that matter more than Sharpe at small scale:** expectancy per trade net of costs, and turnover. A high Sharpe with high turnover and low per-trade expectancy is a strategy that works for someone with lower costs than you.

### 12.4 Position sizing

Sizing determines your outcome more than signal quality does. Three approaches, in order of increasing sophistication:

**1. Fixed fractional.** Risk a constant fraction of capital per trade:
```
position_size = (capital × risk_pct) / (entry_price − stop_price)
```
Typically `risk_pct` of 0.5%–2%. Simple, robust, hard to get catastrophically wrong.

**2. Volatility targeting.** Size inversely to recent volatility so each position contributes similar risk:
```
position_size = capital × (target_vol / realised_vol_of_asset)
```
This automatically shrinks in turbulent markets. Cap the leverage it can produce when realised volatility is very low — otherwise a quiet period generates an enormous position just before the quiet ends.

**3. Kelly criterion.** The growth-optimal fraction. For continuous returns:
```
f* = μ / σ²
```
For a discrete bet with win probability `p` and payoff ratio `b`:
```
f* = (p·b − (1−p)) / b
```
**Full Kelly is almost always wrong in practice** because you are using *estimated* μ and σ, and Kelly is extremely sensitive to overestimating edge. Half-Kelly gives roughly 75% of the growth rate at roughly half the volatility. Quarter-Kelly is a defensible default. If your edge estimate is wrong by 2×, full Kelly can be ruinous while quarter-Kelly is merely disappointing.

---

## 13. Strategy families

The realistic space for a first system. Each with its thesis and its known failure mode.

| Family | Thesis | Typical horizon | Fails when |
|---|---|---|---|
| **Time-series momentum / trend following** | Prices that have risen tend to keep rising over medium horizons; investors underreact to gradual information | Weeks–months | Choppy, mean-reverting markets. Long strings of small losses. |
| **Cross-sectional momentum** | Relative winners keep outperforming relative losers | 1–12 months | Sharp reversals ("momentum crashes") after market bottoms |
| **Mean reversion (short-horizon)** | Prices overshoot on liquidity demand and revert | Days | Trends and genuine regime change. Catches falling knives. |
| **Statistical arbitrage / pairs** | Related instruments' spread reverts to equilibrium | Days–weeks | The relationship structurally breaks; requires short borrow |
| **Carry** | Higher-yielding assets outperform, compensating for a risk | Months | The risk being compensated actually materialises. Slow gains, sudden losses. |
| **Volatility premium** | Implied volatility exceeds realised on average | Days–months | Volatility spikes. Sells insurance; occasionally pays a large claim. |
| **Event-driven** | Predictable price behaviour around earnings, index changes, corporate actions | Days | Requires clean event data; crowded in liquid names |
| **Seasonality / calendar** | Recurring flows produce recurring patterns | Varies | Usually data mining. Demand a mechanism, not a pattern. |

**Recommended starting point:** cross-sectional momentum on a liquid ETF or large-cap universe, or short-horizon mean reversion on liquid names. Both are extensively documented, giving you published results to sanity-check your implementation against — which is one of the few reliable ways to catch backtest bugs.

---

## 14. The ways backtests lie

Every one of these makes a bad strategy look good. Assume all of them are present until you have specifically tested otherwise.

| Bias | What happens | Defence |
|---|---|---|
| **Look-ahead** | Using data unavailable at decision time — today's close to decide today's trade, restated fundamentals, a moving average that includes the current bar | Strict signal-at-*t* → execute-at-*t+1* rule; automated leak detector |
| **Survivorship** | Universe contains only companies that still exist. Failed companies are silently excluded. | Point-in-time universe including delisted names |
| **Data snooping / overfitting** | Testing until something works. The strategy fits noise. | Pre-registration; hold-out sets; deflated Sharpe; count your trials |
| **Selection bias** | Choosing the asset or period where it worked | Test across assets and periods; report all results, not the best |
| **Cost underestimation** | Assuming mid-price fills, ignoring the per-order minimum, ignoring stamp duty | Sensitivity at 2× and 4× costs |
| **Ignoring capacity** | Backtest trades 20% of daily volume without impact | Cap position at a fraction of ADV; model impact |
| **Restatement / revision** | Fundamental data as-restated, not as-reported at the time | Point-in-time data only |
| **Time-zone and timestamp errors** | A bar labelled 16:00 that actually contains post-close data | Verify against a known event; test DST boundaries |
| **Ignoring shorting constraints** | Assuming any stock can be shorted freely and cheaply | Model borrow availability and cost; check hard-to-borrow lists |
| **Regime luck** | Ten years of testing spans one market regime | Test across 2008, 2020, 2022; accept that you cannot test regimes you have not seen |

**The single most useful defensive habit:** when a backtest looks excellent, your first hypothesis should be that there is a bug, not that you have found an edge. Investigate accordingly. Nearly every spectacular backtest a beginner produces is a look-ahead bug, and finding it is the actual skill being developed.

---

## 15. Instruments and leverage

| Instrument | Own the asset? | Leverage | UK tax | Notes |
|---|---|---|---|---|
| **Shares** | Yes | Margin only | CGT; 0.5% SDRT on UK buys | Simplest. Dividends, voting, no expiry. |
| **ETFs** | Yes (a fund) | Margin only | CGT; SDRT generally not applicable | Instant diversification. Best first instrument. |
| **Futures** | No (contract) | Built-in, high | CGT | Standardised, exchange-cleared, deep liquidity, but large contract sizes — often too big for small accounts |
| **Options** | No (right) | Built-in, non-linear | CGT | Powerful and easy to lose money on. Non-linear risk. Defer. |
| **CFDs** | No | Up to 30:1 retail | CGT; losses offsettable | OTC — your counterparty is the broker. Overnight financing. |
| **Spread bets** | No | Up to 30:1 retail | Exempt for most retail | UK-specific. Wider spreads. Losses not offsettable. |
| **FX spot** | Currency | High | Varies | 24/5, tight spreads, but a brutally competitive market |
| **Crypto** | Token | Varies (CFDs banned for UK retail) | CGT | 24/7, high volatility, uneven venue quality |

### 15.1 Leverage — the honest version

Leverage multiplies returns **and** losses, and it introduces a failure mode that unlevered positions do not have: **you can be forcibly closed at the worst possible moment.**

At 10:1 leverage a 10% adverse move wipes out your equity. But you will not survive to see it — you will be margin-called and liquidated well before, often at the point of maximum dislocation, and the position may then recover without you.

**Guidance for a first system: use no leverage.** If you later use it, treat the maximum leverage your broker permits as a boundary to stay far away from, not a target. The FCA's 50% margin close-out rule (§7.3) is the specific mechanism that will liquidate you; your risk limits must bind long before it does.

---

## 16. Glossary

**ADV** — average daily volume.
**Alpha** — return not explained by exposure to known risk factors.
**Basis point (bp)** — 0.01%. 100 bps = 1%.
**Beta** — sensitivity to a benchmark's returns.
**Cointegration** — two non-stationary series whose linear combination is stationary; the statistical basis for pairs trading.
**Drawdown** — decline from a running peak in equity.
**Fill** — an executed order (or part of one).
**Implementation shortfall** — difference between the price when you decided and the price you achieved, including unfilled portions.
**Liquidity** — the ability to trade size without moving price.
**Long / short** — positioned to profit from a rise / a fall.
**Notional** — total position value (price × quantity), as distinct from margin posted.
**OHLCV** — open, high, low, close, volume.
**Point-in-time (PIT) data** — data as it was known at the time, without later restatements.
**Sharpe ratio** — excess return per unit of volatility.
**Slippage** — difference between expected and actual execution price.
**Stationarity** — statistical properties constant over time; most price series are not stationary, most return series are closer to it.
**Tick** — minimum price increment, or an individual trade record.
**Turnover** — how much you trade relative to capital; the multiplier on your costs.
**VWAP / TWAP** — volume- / time-weighted average price; both a benchmark and an execution algorithm.
**Walk-forward** — repeatedly train on past data and test on the immediately following unseen period.

---

## 17. Reading list, ordered

Read in this order. Stop when you have what you need for the current stage — do not read all of it before writing code.

**Start here (Stage 0–1)**
1. Ernie Chan, *Quantitative Trading* — the most practical starting point for a technical reader; realistic about costs and pitfalls.
2. Robert Carver, *Systematic Trading* — outstanding on position sizing, diversification and the discipline of rule-following. Written by a former systematic fund manager for individuals, which is exactly your situation.

**Statistical discipline (Stage 2–3)**
3. Marcos López de Prado, *Advances in Financial Machine Learning* — chapters 1–8 especially. Dense and opinionated. The material on backtest overfitting, purging/embargoing and the deflated Sharpe ratio is the most valuable content in this list, and it directly implements §9.
4. Bailey & López de Prado, "The Deflated Sharpe Ratio" (paper) — read alongside the above.
5. Andrew Lo, "The Statistics of Sharpe Ratios" (2002) — the source of §9.1.

**Market structure (Stage 4–5)**
6. Larry Harris, *Trading and Exchanges* — the definitive reference on market mechanics. A reference book, not a cover-to-cover read.

**Depth (later, optional)**
7. Grinold & Kahn, *Active Portfolio Management* — the fundamental law of active management, information ratios, portfolio construction.
8. Carver, *Advanced Futures Trading Strategies* — if you go multi-instrument.

**Sceptical ballast (read early)**
9. Nassim Taleb, *Fooled by Randomness* — a useful corrective to the feeling that a good backtest means you have found something.

**Deliberately absent:** anything on chart patterns, indicator recipes, or "proven" systems for sale. If a source is selling a strategy, the strategy is not the product — you are.

---

## Appendix A — First 30 days, concrete

| Day | Task |
|---|---|
| 1–2 | Write `CHARTER.md`: market, horizon, capital, time budget, abandon criteria. Create the git repo. |
| 3–4 | Open an Alpaca paper account. Get API keys. Set up secrets handling with `.env` + `.gitignore`. |
| 5–7 | `RiskLimits` class + unit tests for every limit violation. **Before any order code.** |
| 8–9 | Kill switch (file-based) + heartbeat writer + external watchdog. Test by killing the process. |
| 10–14 | Data layer: pull 10 years of daily bars for one liquid ETF, write to Parquet, implement the 12 validation checks (§4.9). |
| 15–19 | Simple event-loop backtester. Explicit costs. Signal at *t*, execute at *t+1* open. |
| 20–21 | One strategy (SMA crossover). Run it. Expect it not to work net of costs. |
| 22–23 | Validation tests: random signal, tomorrow's-close strategy, buy-and-hold benchmark, determinism check. |
| 24–27 | Broker adapter: place a paper order. Handle reject, partial fill, disconnect. |
| 28–29 | Reconciliation job + structured logging with run ID, git SHA, data hash. |
| 30 | Kill the process mid-session holding a position. Restart. Confirm it reconciles correctly. **This is the Stage 1 gate.** |

At the end of 30 days you have a complete, working, safe, boring system — and you will know more about the real problems than v1.0's plan would have taught you in a year of specification writing.

---

## Appendix B — Summary of changes from v1.0

| # | Change | Rationale |
|---|---|---|
| 1 | Vertical slice in 6 weeks, replacing 16 phases of documents | Feedback loop is the whole value |
| 2 | Risk engine, kill switch and reconciliation moved to week 1 | They protect against the most likely failure — a bug, not a bad forecast |
| 3 | Added a dead-man's switch | v1.0's kill switch assumes the bot is alive |
| 4 | Every deliverable is now executable, not a specification | A design is a promise, not a deliverable |
| 5 | Added explicit abandon criteria | v1.0 could only ever conclude "continue" |
| 6 | Added statistical power analysis with required sample sizes | "Statistically defensible" needs a number |
| 7 | Added the full cost stack and minimum-viable-capital arithmetic | Determines whether the project is possible at all |
| 8 | Added UK tax and FCA regulatory treatment | Absent from v1.0; changes instrument choice |
| 9 | Deleted Phase 11 (low latency / FPGA / co-location) | Not economically accessible; unlimited time sink |
| 10 | Deleted Phase 13 (autonomous discovery) and Phase 14 (distributed infra) | Overfitting accelerator; unnecessary at n=1 |
| 11 | Stack simplified to Python + Parquet + DuckDB; Rust/Kafka/ClickHouse deferred behind explicit conditions | Research iteration speed is the binding constraint |
| 12 | Phase 1 learning distributed across stages rather than gating all work | A reading gate is where side projects die |
| 13 | Added the engineering failure-mode checklist (time, corporate actions, restart, idempotency) | These cause most real incidents and appear in no backtest |
| 14 | Added the 12 data validation checks | Data bugs are the most common cause of fake edges |
| 15 | Added realistic success definitions and base rates | Optimise for the achievable outcome |

---

*End of document.*
