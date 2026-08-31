# Testing and Quality Strategy

<details open>
<summary><b>Contents</b></summary>

- [Purpose](#purpose)
- [Quality Principles](#quality-principles)
- [Test Levels](#test-levels)
- [Test Environments](#test-environments)
- [Fixtures and Test Data](#fixtures-and-test-data)
- [Critical Behavior Matrix](#critical-behavior-matrix)
  - [Data and Time](#data-and-time)
  - [Backtest and Statistics](#backtest-and-statistics)
  - [Risk and Orders](#risk-and-orders)
  - [Recovery and Operations](#recovery-and-operations)
  - [Security](#security)
- [Property Based and Model Based Tests](#property-based-and-model-based-tests)
- [Determinism and Golden Tests](#determinism-and-golden-tests)
- [Broker Contract Testing](#broker-contract-testing)
- [Fault Injection](#fault-injection)
- [Continuous Integration Gates](#continuous-integration-gates)
- [Coverage and Mutation Policy](#coverage-and-mutation-policy)
- [Defect and Regression Policy](#defect-and-regression-policy)
- [Release Evidence](#release-evidence)
- [Open Decisions](#open-decisions)

</details>

---

**Version:** 1.0  
**Date:** 30 August 2026  
**Status:** Proposed baseline  
**Related:** [Requirements](01-requirements.md) | [Data Specification](04-data-specification.md) | [Execution Specification](06-execution-and-reconciliation.md) | [Operations Runbook](08-operations-and-observability.md)

## Purpose

This strategy defines the evidence required to trust the trading system at each stage. Tests focus on financial invariants, time, state transitions, failure recovery, and permission boundaries. Line coverage is diagnostic; it is not a substitute for proving named behaviors.

## Quality Principles

1. Test the dangerous path first: risk denial, duplicate prevention, ambiguous submit, restart, and reconciliation.
2. Use deterministic clocks, providers, brokers, and random seeds by default.
3. Make invalid and missing inputs explicit; do not build only happy-path fixtures.
4. Test contracts at module boundaries so adapters can be replaced without changing domain expectations.
5. Generate order and ledger sequences to find state combinations that examples miss.
6. Keep offline tests independent of network, wall clock, personal files, and broker credentials.
7. Treat every production or paper incident as a missing test until shown otherwise.
8. Preserve failed research runs, but quarantine invalid engine results.
9. Require executable evidence for gates; document review alone never proves runtime behavior.

## Test Levels

| Level | Scope | Typical dependencies | Required speed and use |
|---|---|---|---|
| Static validation | Types, lint, schemas, links, secret patterns, configuration | Source only | Every change |
| Unit | One rule, transition, calculation, parser, or formatter | In-memory values | Fast local and CI default |
| Property based | Invariants over generated values and event sequences | In-memory domain models | Every CI run for bounded examples; deeper scheduled run |
| Component | Data pipeline, backtester, risk engine, order manager, ledger, reconciler | Temporary files and deterministic fakes | Every CI run |
| Contract | One port implemented by fake and real adapter | Recorded sanitized cases; optional paper sandbox | Fake in CI, sandbox on controlled schedule |
| Integration | Multiple real local components and stores | Temporary Parquet and SQLite | Every CI run |
| System | Complete command path in `BACKTEST` or simulated `PAPER` | Local scheduler substitutes and fake broker | Release gate |
| Paper smoke | Small approved action against verified paper account | Network and paper credentials | Manual or protected release gate |
| Failure exercise | Process, network, data, and broker disruption | Paper or high-fidelity simulator | Before unattended paper and periodically |

No automated test may contact a broker unless it carries an explicit network marker and passes the paper environment guard.

## Test Environments

| Environment | Broker | Data | Secrets | Purpose |
|---|---|---|---|---|
| Local offline | Deterministic fake | Synthetic and pinned fixtures | None | Development and full safe test suite |
| CI offline | Deterministic fake | Synthetic and pinned fixtures | None | Required merge and release checks |
| Paper contract | Verified paper sandbox | Small approved current input | Paper secret provider | Adapter and environment smoke tests |
| Paper rehearsal | Verified paper account | Published data path | Paper secret provider | End-to-end and failure exercises |
| Future live | Real broker | Approved production data | Separate live provider | Prohibited until Stage 5 approval |

Environment identity is asserted inside tests. A network test aborts if account mode, endpoint, credential namespace, or order marker is not exactly approved.

## Fixtures and Test Data

- Synthetic fixtures are the default and are small enough to understand manually.
- Every fixture declares timezone, exchange calendar, session bounds, action policy, and information-availability timestamps.
- Include normal session, US holiday, half-day, leap day, and both US daylight-saving transition cases.
- Include split, cash dividend, symbol change, delisting, missing bar, duplicate bar, impossible OHLC, stale bar, extreme move, zero-volume run, and provider revision cases.
- Include accepted, rejected, partial, multi-fill, canceled, expired, unknown, duplicate-event, and cancel-fill-race orders.
- Include deposits, withdrawals, fees, FX conversion, realized and unrealized loss, new equity high, and drawdown.
- Captured broker payloads require provider-term review and irreversible sanitization. Synthetic equivalents are preferred.
- Fixture manifests and expected results are versioned and content-hashed.
- A test must not depend on the current date, local timezone, user directory, or unordered filesystem traversal.

## Critical Behavior Matrix

### Data and Time

| Behavior | Minimum cases |
|---|---|
| Twelve data validations | One passing dataset and one isolated failing fixture per `DV-*` rule |
| UTC normalization | Naive rejection, offset conversion, DST transitions, ambiguous local time |
| Exchange calendar | Holiday, half-day, unscheduled missing session, session boundary |
| Information availability | Before, exactly at, and after `available_at_utc` |
| Corporate actions | Split and dividend accounting, missing action, symbol continuity |
| Revision detection | Identical re-pull and one-cell, action, and calendar revisions |
| Snapshot integrity | Stable serialization, hash reload, corruption, wrong schema version |

### Backtest and Statistics

| Behavior | Minimum cases |
|---|---|
| Event order | Equal timestamps, next-session fill, no same-bar fill |
| Ledger | Buy, sell, partial, fees, actions, FX, external flow, flat close |
| Cost identity | Zero, baseline, doubled, quadrupled, minimum commission, spread direction |
| Determinism | Repeated run, stable sorting, recorded seed, different seed where expected |
| Walk forward | Fit only in training, purge, embargo, fold concatenation |
| Metrics | Empty, one observation, zero variance, known sequence, non-finite rejection |
| Sharpe uncertainty and DSR | Independently calculated golden cases and invalid sample cases |
| Promotion | Every criterion pass and each criterion failing alone |
| Negative controls | Random, shuffled, future-close, no-trade, benchmark |

### Risk and Orders

| Behavior | Minimum cases |
|---|---|
| Each hard limit | Below, exactly equal, above, missing input, stale input |
| Exposure projection | Positions plus pending buys, sells, partial fills, adverse price |
| Long-only control | Buy, valid sell, oversell, short intent, unknown position |
| Order rate | Rolling-window edge, simultaneous intents, restart persistence |
| Daily loss | Realized, unrealized, fees, external flow, session reset, sticky halt |
| Drawdown | Initial equity, new high, decline, capital reset, restart, owner reset |
| Idempotency | Repeated intent, submit retry, restart, provider conflict, hash collision path |
| Order states | Every allowed transition and every forbidden transition |
| Unknown outcome | Found by client ID, absence proven, conflicting matches, fill without local ack |

### Recovery and Operations

| Behavior | Minimum cases |
|---|---|
| Startup reconciliation | Clean state and isolated account, position, cash, order, and fill mismatch |
| Crash points | Before journal, after journal, during submit, after accept, partial fill, cancel, ledger update |
| Stream gap | Disconnect, overlap query, deduplication, missing page, reordered events |
| Kill controls | Present before start and activated before, during, and after submit |
| Watchdog | Healthy, stale, malformed, duplicate watchdog, broker unavailable, cancel race |
| Scheduler | Holiday, overlap, late start, missed run, no-trade report |
| Backup restore | Valid restore, corrupt backup, wrong key, missing linked artefact |
| Release rollback | Code rollback with current state replay and no broker fact loss |

### Security

| Behavior | Minimum cases |
|---|---|
| Environment denial | Live URL, redirect, wrong credential namespace, wrong account, unknown mode |
| Redaction | Canary in nested map, list, URL, header, exception, multiline text |
| Secret scanning | Representative key, token, private key, `.env`, false-positive allowlist review |
| Configuration integrity | Missing field, unknown key, changed hash, wrong approval, runtime mutation attempt |
| File access | Runtime paths restricted and failure to persist blocks submission |
| Network isolation | Offline suite fails on unexpected socket access |
| Dependency checks | Lock consistency, inventory, known-vulnerability policy |

## Property Based and Model Based Tests

Use Hypothesis or an equivalent established library for high-value invariants:

- Projected gross exposure is nonnegative and includes all pending worst-case fills.
- Accepted Stage 1 orders never create a negative position or leverage above one.
- Splits preserve economic position value at an unchanged theoretical market value.
- Deduplicating the same fill or broker event any number of times changes state once.
- Replaying a valid event journal produces the same ledger state as incremental processing.
- Cash plus marked positions minus liabilities equals equity within currency tolerance.
- A rejected risk decision never produces an adapter submission.
- Restart at any generated event boundary creates no additional logical order.
- State-machine generators produce only allowed transitions; invalid transitions fail visibly.
- Tightening a risk limit cannot cause an order previously rejected by that limit to become accepted.

Model-based tests compare the order manager and ledger with a simpler reference model across generated command and event sequences. Shrunk failing examples become named regression fixtures.

## Determinism and Golden Tests

- Freeze clock, calendar, locale, timezone, dependency lock, data hash, config hash, and random seed.
- Sort all unordered inputs and define event tie-break keys.
- Canonical result JSON excludes wall-clock duration and machine-specific paths or stores them outside the compared payload.
- Floating-point comparisons use domain-specific tolerances during calculation, but canonical serialization follows one stable policy.
- Golden files are reserved for reviewed schemas, statistical reference cases, broker mappings, and compact full-run outputs.
- Golden changes require a human-readable semantic diff and rationale; bulk acceptance is prohibited for financial outputs.
- Test the golden-test mechanism by corrupting a copy and proving detection.

Reproducibility means identical canonical evidence, not merely similar headline metrics.

## Broker Contract Testing

One reusable contract suite runs against:

1. An in-memory deterministic fake.
2. A transport-level stub that exercises serialization and error mapping.
3. The approved paper sandbox for a narrow protected smoke subset.

The suite covers environment verification, order mapping, client ID behavior, accepted and rejected submissions, ambiguous responses, partial fills, cancels, pagination, streaming gaps, deduplication, rate limits, and redaction.

Paper tests use distinctive low-risk test intent, verify current market/session constraints, and clean up known working orders. They never assume cleanup proves no fill; final broker facts and reconciliation decide the outcome.

## Fault Injection

Faults are injected at named boundaries, not by hoping an outage occurs:

- Clock unavailable or shifted.
- Disk full, database locked, commit failure, and corrupt checkpoint.
- Provider timeout, disconnect, malformed payload, stale response, and historical revision.
- Broker timeout before acceptance and after acceptance.
- Dropped, duplicated, reordered, and delayed broker events.
- Process termination at each journal and external side-effect boundary.
- Alert primary-channel failure.
- Watchdog duplicate execution and trading-process heartbeat loss.
- Scheduler overlap, late start, and missed session.

Every exercise records expected safe state, actual state, broker facts, alerts, recovery time, and unresolved differences. A fault test that leaves uncertain exposure is a failed test even if the process exits cleanly.

## Continuous Integration Gates

Recommended required sequence:

1. Validate Markdown navigation and relative links.
2. Scan for secrets and forbidden runtime or credential files.
3. Validate configuration and data schemas.
4. Run formatter and static analysis.
5. Run type checks for typed application boundaries.
6. Run unit and bounded property-based tests.
7. Run component and local integration tests with network denied.
8. Run deterministic backtest and golden sanity suite.
9. Run dependency inventory, lock consistency, license, and vulnerability checks.
10. Build the release manifest and verify all referenced hashes.

Paper sandbox tests run separately under explicit owner control or a protected scheduler. Their absence blocks a paper release but must not expose credentials to general CI.

## Coverage and Mutation Policy

- Trace every `DATA`, `BT`, `RES`, `RISK`, `EXEC`, `STATE`, `AUD`, and `NFR` requirement to at least one executable check or a clearly marked operational exercise.
- Require branch coverage of every named risk denial, order transition, reconciliation mismatch, mode guard, and restart decision.
- Use line and branch percentages to find untested code, not to waive missing behaviors.
- Run mutation testing on pure risk calculations, order-state transitions, cost accounting, and temporal guards. Surviving mutations are reviewed, not hidden by lowering a threshold.
- Exclude only generated code or proven unreachable defensive adapters with documented rationale.
- A high global percentage cannot compensate for an untested kill path or ambiguous-submit branch.

## Defect and Regression Policy

1. Record severity, affected mode, exposure, first bad release, and evidence identity.
2. Halt paper or future live operation for any defect that can add unauthorized exposure, duplicate an order, hide a reconciliation break, leak a secret, or invalidate evidence.
3. Preserve the minimal failing input and event sequence.
4. Add a failing regression test before or with the fix where reproducible.
5. Correct the smallest owning component and rerun its focused suite.
6. Rerun all affected invariants, system scenarios, and release gates.
7. Invalidate research or paper evidence produced by affected versions where conclusions may change.
8. Document root cause and control improvement for significant incidents.

Unrelated known failures are never silently ignored; they are either fixed, quarantined with owner-visible rationale, or block the applicable gate.

## Release Evidence

A paper release includes:

- Test summary by requirement and critical behavior.
- Exact source, environment lock, config, schema, and fixture hashes.
- Deterministic sanity-test results.
- Property-test settings and seeds for failures.
- Mutation-test result for critical pure modules.
- Secret, dependency, license, and vulnerability scan summaries.
- Fake and paper broker contract outcomes.
- Known limitations, quarantined failures, and evidence invalidation notes.
- Five induced-failure exercise reports before Stage 4 completion.
- Owner approval linked to the release manifest.

## Open Decisions

| Decision | Needed by | Blocking effect |
|---|---|---|
| Select formatter linter type checker and lock tool | Project scaffold | Blocks CI baseline |
| Select secret dependency and license scanners | Initial CI | Blocks security gate |
| Select mutation testing tool and bounded CI budget | Risk implementation | Blocks critical mutation policy |
| Define paper sandbox test order and safe scheduling policy | Adapter acceptance | Blocks network smoke tests |
| Define domain-specific decimal and float tolerances | Ledger and metrics implementation | Blocks golden results |
| Choose CI provider or local protected build workflow | First release | Blocks automated release evidence |