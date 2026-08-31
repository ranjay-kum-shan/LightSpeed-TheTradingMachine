# Trading Bot

<details open>
<summary><b>Contents</b></summary>

- [Overview](#overview)
- [Current Status](#current-status)
- [Parallel Collaboration](#parallel-collaboration)
- [Safety Boundary](#safety-boundary)
- [Decisions Needed From the Owner](#decisions-needed-from-the-owner)
- [Implementation Commands](#implementation-commands)
- [GitHub Upload](#github-upload)
  - [Include](#include)
  - [Do Not Upload](#do-not-upload)
  - [Publish With Git](#publish-with-git)
- [Documentation Set](#documentation-set)
  - [Foundation and Design](#foundation-and-design)
  - [Evidence and Operations](#evidence-and-operations)
  - [Templates](#templates)
- [Delivery Sequence](#delivery-sequence)
- [First Complete Outcome](#first-complete-outcome)
- [Documentation Rules](#documentation-rules)
- [Disclaimer](#disclaimer)

</details>

---

## Overview

This repository is the documentation-first baseline for a small, safety-first systematic trading bot. The design targets one liquid US-listed ETF, daily bars, a single-process Python runtime, deterministic net-of-cost backtesting, hard risk controls, and Alpaca paper trading as the proposed first broker path.

The source review is the [Trading System Plan Review v2](docs/reference/trading-system-plan-review-v2.md). The implementation contracts below preserve its risk-first vertical slice without returning to a long specification phase that delays executable feedback.

## Current Status

**Requirements status:** 59 SPECIFIED, 2 IMPLEMENTED, 0 VERIFIED  
**Current authorization:** PAPER_ONLY  
**Current gate:** Stage 0 not passed  
**Implementation status:** In progress - offline foundation and pre-trade controls

| Item | State |
| --- | --- |
| Documentation baseline | Complete draft |
| Requirements | 59 `SPECIFIED`; 2 `IMPLEMENTED`; 0 `VERIFIED` |
| Charter | Draft; Stage 0 not passed |
| External order authorization | `PAPER_ONLY` |
| Software implementation | Fail-closed config and CLI, canonical domain contracts, pure risk engine, operator kill assessment, and heartbeat health |
| Automated checks | Ruff and strict mypy clean; 79 tests passing |
| Reference ETF and data provider | Owner decision required |
| Paper broker | Alpaca proposed; owner eligibility and terms confirmation required |
| Real-money capability | Absent and unauthorized |

Documentation completion is not a stage pass. The next valid action is to resolve and sign the Stage 0 owner decisions in [CHARTER.md](CHARTER.md).

## Parallel Collaboration

All AI agents and developers start with [AGENTS.md](AGENTS.md). Task assignment,
dependencies, blockers, progress, and completed subtasks are indexed in the
[Master Task Tracker](MASTER-TASK-TRACKER.md). Claims, separate branches and
worktrees, task records, review handoffs, leases, and integration order follow
the [Parallel Work Protocol](docs/15-parallel-work-protocol.md).

The master tracker is coordinator-owned to avoid merge conflicts. Workers update
their own records under `coordination/` and may edit implementation files only
after an approved active claim. Parallel work remains blocked until the project
owner creates an approved baseline commit and appoints a coordinator.

## Safety Boundary

- Profitability is evidence-driven and never assumed.
- Strategy code cannot contact a broker or bypass risk checks.
- Hard risk limits, kill controls, durable intent, and reconciliation exist before the first paper submission.
- A daily-bar signal formed from session `t` cannot fill before the next eligible session.
- Missing, stale, ambiguous, unreconciled, or unauthorized state adds no new exposure.
- Broker timeout is an unknown outcome resolved by stable client order ID, never a blind retry.
- Restart begins in recovery and reconciles account, positions, cash, orders, and fills before strategy evaluation.
- No live capital or loss value is guessed from examples or broker defaults.
- Stage 5 remains separately gated and currently unauthorized.

## Decisions Needed From the Owner

| Priority | Decision | Current proposal | Effect if unresolved |
| --- | --- | --- | --- |
| 1 | Initial market and horizon | Liquid US-listed ETF, daily bars, 2 to 20 day holding | Stage 0 remains open |
| 2 | Weekly project capacity | 8 to 10 focused hours | Roadmap remains an assumption |
| 3 | Base reporting currency | GBP | Canonical PnL and FX policy remain open |
| 4 | Reference ETF | One broad liquid US-listed ETF | Data vertical cannot be finalized |
| 5 | Paper broker access | Alpaca paper | Adapter acceptance remains blocked |
| 6 | Historical and current data provider | To be qualified | Dataset publication remains blocked |
| 7 | Paper reference equity and limits | To be selected | Realistic paper risk profile remains blocked |
| 8 | Secret store alerts backup and runtime location | To be selected | Unattended paper operation remains blocked |

Future loss-tolerant capital, daily-loss, drawdown, tax, and account decisions are intentionally left `TBD`; they are required only for a separately approved Stage 5 review and currently deny that capability.

## Implementation Commands

Python 3.12 or newer is required. The current workspace is pinned to Python 3.14.3 and uses an isolated uv environment.

```powershell
uv sync --dev
uv run trading-bot config-check configs/backtest.yaml
uv run ruff check src tests
uv run mypy src tests
uv run pytest -q
$env:UV_LINK_MODE = "copy"
uv build
```

The current command surface validates configuration only. It has no broker adapter, credential input, network order path, or real-money capability. Invalid or explicit `LIVE` configuration reports `HALTED` with a stable reason code.

Copy mode avoids incompatible hardlinks when the workspace is stored in a
OneDrive-backed directory.

## GitHub Upload

### Include

The repository-ready source is everything Git shows through `git add --dry-run .`.
Important project content includes:

- `.github/`, `.vscode/`, `configs/`, `docs/`, `src/`, and `tests/`.
- `.editorconfig`, `.gitattributes`, `.gitignore`, and `.markdownlint.json`.
- `.python-version`, `CHARTER.md`, `README.md`, `pyproject.toml`, and `uv.lock`.

Keep `uv.lock` in Git. It is the reproducible dependency lock used by CI.

### Do Not Upload

Do not manually upload any of these local or generated items:

- `.venv/`, `__pycache__/`, `.pytest_cache/`, `.hypothesis/`, `.ruff_cache/`,
  or `.mypy_cache/`.
- `.env` or any `.env.*` file containing credentials.
- `data/`, `state/`, `logs/`, `reports/`, or `run/` runtime directories.
- SQLite or database files such as `*.sqlite`, `*.sqlite3`, or `*.db`.
- `build/`, `dist/`, coverage output, editor workspace files, or OS metadata.
- `.git/` when using GitHub's browser upload. It is local repository metadata and
  is never committed by Git.

The ignore rules already exclude these paths from normal Git commands. If you
copy the folder with Windows Explorer, hidden ignored folders may still be copied
locally; use the Git workflow below to ensure they are not published.

The superseded v1 DOCX is intentionally outside this public workspace because
its Office metadata contained local identity information. A verified private
copy is retained separately.

### Publish With Git

Review the dry run before the first commit:

```powershell
git add --dry-run .
git status --ignored --short
```

Then stage and publish only after reviewing the output:

```powershell
git add .
git commit -m "Initial safety-first trading bot foundation"
git push -u origin main
```

The local repository uses branch `main`, tracks the configured personal GitHub
repository, and uses a repository-scoped personal author identity. Before
pushing, authenticate GitHub CLI as the personal `ranjay-kum-shan` account and
verify that account has write permission. Do not push through a work or
organization account.

No open-source license has been selected. A public repository without a license
is visible but does not grant others permission to reuse, modify, or distribute
the code. Add a license only after choosing the terms you want.

## Documentation Set

### Foundation and Design

| Document | Purpose |
| --- | --- |
| [CHARTER.md](CHARTER.md) | Mission, scope, defaults, owner decisions, success and abandon criteria |
| [Requirements Specification](docs/01-requirements.md) | 61 functional and nonfunctional requirements with acceptance outcomes |
| [System Architecture](docs/02-architecture.md) | Boundaries, components, state ownership, flows, failure model, and topology |
| [Risk and Safety Specification](docs/03-risk-and-safety.md) | Hard limits, kill controls, loss semantics, restart, and risk verification |
| [Market Data Specification](docs/04-data-specification.md) | Schemas, time availability, immutable snapshots, and twelve validation rules |
| [Backtesting and Research Protocol](docs/05-backtesting-and-research.md) | Honest simulation, costs, preregistration, statistics, controls, and promotion |
| [Execution and Reconciliation Specification](docs/06-execution-and-reconciliation.md) | Broker boundary, idempotency, order states, unknown outcomes, and recovery |
| [Security and Secrets Specification](docs/07-security-and-secrets.md) | Threat model, endpoint separation, secret handling, supply chain, and incident response |

### Evidence and Operations

| Document | Purpose |
| --- | --- |
| [Operations and Observability Runbook](docs/08-operations-and-observability.md) | Events, metrics, alerts, watchdog, reports, runbooks, releases, and backups |
| [Testing and Quality Strategy](docs/09-testing-and-quality.md) | Test levels, critical matrix, property tests, fault injection, and CI gates |
| [Paper and Future Live Rollout Plan](docs/10-paper-and-live-rollout.md) | Promotion, demotion, tracking, stage clocks, and future activation controls |
| [Recordkeeping and Compliance Plan](docs/11-recordkeeping-and-compliance.md) | Fill, FX, broker, tax-support, licensing, retention, and personal-use records |
| [Delivery Roadmap](docs/12-delivery-roadmap.md) | Risk-first work packages, first 30 days, milestones, and definitions of done |
| [Project Decision Log](docs/13-decision-log.md) | Accepted constraints, proposed defaults, blocked decisions, and decision queue |
| [Requirements Traceability Matrix](docs/14-requirements-traceability.md) | Exact 61-requirement mapping to owner documents, planned evidence, and stages |
| [Parallel Work Protocol](docs/15-parallel-work-protocol.md) | Claims, leases, write scopes, branches, handoffs, review, and integration |

### Templates

| Template | Use |
| --- | --- |
| [Decision Record](docs/templates/decision-record-template.md) | Consequential technical, safety, provider, or scope decision |
| [Strategy Preregistration](docs/templates/strategy-preregistration-template.md) | Freeze thesis, data, timing, parameters, costs, and thresholds before a test |
| [Experiment Report](docs/templates/experiment-report-template.md) | Reproducible result, controls, uncertainty, and mechanical promotion decision |
| [Incident Report](docs/templates/incident-report-template.md) | Safe state, impact, timeline, root cause, reconciliation, and resume criteria |
| [Reconciliation Report](docs/templates/reconciliation-report-template.md) | Compare broker and internal account, position, cash, order, and fill facts |
| [Daily Paper Session Report](docs/templates/daily-paper-session-report-template.md) | Positive evidence for every expected session, including no-trade days |
| [Monthly Paper Report](docs/templates/monthly-paper-report-template.md) | Backtest-to-paper tracking and Stage 4 clock review |
| [Stage Gate Review](docs/templates/stage-gate-review-template.md) | Conjunctive promotion, remain, reset, demotion, invalidation, or abandon decision |
| [Data Source Qualification](docs/templates/data-source-qualification-template.md) | Terms, coverage, timestamps, actions, revisions, quality, cost, and approved use |
| [Task Claim](docs/templates/task-claim-template.md) | Proposed ownership, write scope, lease, overlap, and coordinator approval |
| [Task Record](docs/templates/task-record-template.md) | Scope, subtasks, progress, decisions, validation, review, and closure |
| [Task Handoff](docs/templates/task-handoff-template.md) | Reproducible worker-to-reviewer and reviewer-to-coordinator transfer |

## Delivery Sequence

1. Review and sign the owner-controlled Stage 0 rows in the charter.
2. Initialize the Python project and offline quality gates.
3. Implement risk limits, kill controls, heartbeat, and watchdog contracts.
4. Publish one validated immutable ETF dataset.
5. Build the deterministic event-loop backtester and machinery-only strategy.
6. Integrate the verified paper broker behind durable idempotent order handling.
7. Prove restart, reconciliation, alerts, reports, backup, and restore.
8. Pass the Stage 1 kill-and-recover exercise before deeper strategy research.

The detailed order and exit checks are in the [Delivery Roadmap](docs/12-delivery-roadmap.md).

## First Complete Outcome

Stage 1 is complete only when one command path can:

1. Resolve a published ten-year ETF dataset by content hash.
2. Run a deterministic net-of-cost backtest with next-session fills.
3. Produce a strategy intent that passes or fails hard risk checks.
4. Journal an accepted intent before sending exactly one paper order.
5. Consume reject, partial-fill, timeout, and disconnect outcomes safely.
6. Reconcile broker and internal state.
7. Survive process termination and restart without duplicate orders.
8. Emit redacted audit and daily evidence.

This proves the machinery, not a profitable edge.

## Documentation Rules

- The charter overrides conflicting lower-level documents.
- Requirement and decision IDs are stable and never silently repurposed.
- Every Markdown file contains synchronized section navigation.
- Behavior changes update the owning contract, traceability row, and executable test together.
- External terms, rates, and rules carry an as-of date and review trigger.
- Superseded evidence remains traceable; it is not edited into apparent compliance.
- Owner-dependent values remain blocked instead of receiving guessed defaults.

## Disclaimer

For informational and engineering-planning purposes only. This project and its
documentation do not constitute legal, regulatory, tax, accounting, financial,
or investment advice and do not predict profitability. Verify current broker,
market-data, HMRC, FCA, and other applicable requirements with primary sources
and qualified professionals before acting on them.
