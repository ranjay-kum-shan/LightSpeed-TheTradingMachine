# Project Agent Instructions

<details open>
<summary><b>Contents</b></summary>

- [Start Here](#start-here)
- [Mandatory Claim Workflow](#mandatory-claim-workflow)
- [Source of Truth](#source-of-truth)
- [Safety Boundary](#safety-boundary)
- [Editing Boundaries](#editing-boundaries)
- [Validation and Evidence](#validation-and-evidence)
- [Handoff and Completion](#handoff-and-completion)
- [Build and Test](#build-and-test)
- [Documentation](#documentation)

</details>

---

## Start Here

Before changing any file:

1. Read [MASTER-TASK-TRACKER.md](MASTER-TASK-TRACKER.md).
2. Read the [Parallel Work Protocol](docs/15-parallel-work-protocol.md).
3. Read the task's linked requirements, decisions, and owning specification.
4. Confirm the task is `READY`, unblocked, and has no overlapping active claim.
5. Obtain an `ACTIVE` claim before editing implementation files.

An approved `ACTIVE` claim is required before any implementation edit.

If there is no active coordinator, do not self-approve a claim. Ask the project
owner to appoint one or work sequentially without claiming parallel safety.

## Mandatory Claim Workflow

- Create `coordination/claims/TB-NNNN.md` from the claim template.
- Use branch `task/TB-NNNN-short-name` and a separate worktree.
- Record the exact base commit, write scope, lease expiry, and planned checks.
- After approval, create `coordination/tasks/TB-NNNN.md` from the task template.
- Update the task record and claim heartbeat as work progresses.
- Submit `coordination/handoffs/TB-NNNN.md` for review.
- Never mark the master task `DONE`; only the coordinator closes it.

## Source of Truth

Apply this priority order when records conflict:

1. [CHARTER.md](CHARTER.md).
2. Accepted [project decisions](docs/13-decision-log.md).
3. Requirements and owning specifications.
4. [Requirements traceability](docs/14-requirements-traceability.md).
5. [Master task tracker](MASTER-TASK-TRACKER.md).
6. Individual task, claim, and handoff records.

Stop and escalate conflicts; do not choose the more convenient interpretation.

## Safety Boundary

- Current authorization is `PAPER_ONLY`; Stage 0 is not passed.
- Never add or enable live trading, leverage, shorting, or real credentials.
- Never invent owner capital, loss limits, broker eligibility, tax treatment, or
  data rights.
- Strategy code cannot bypass risk or call a concrete broker adapter.
- Ambiguous, stale, missing, conflicting, or unreconciled state adds no new risk.
- Do not weaken safety gates because current code or results fail them.

## Editing Boundaries

- Edit only the active claim's declared write scope.
- Never share one worktree between workers.
- Do not perform unrelated refactors, repo-wide formatting, or generated-file
  changes inside a feature task.
- Protected shared files require explicit coordinator permission; see the
  protocol for the list.
- Work with existing user changes and never discard another worker's branch or
  uncommitted work.
- Do not add `.venv`, caches, `.env`, data, state, logs, reports, databases, or
  package build output.

## Validation and Evidence

- State a falsifiable local hypothesis and the cheapest check before the first
  edit.
- Run that focused check immediately after the first substantive edit.
- Record exact commands, exit codes, test counts, failures, and artefact IDs in
  the task record.
- Run affected broader checks before handoff.
- Never report a requirement as `VERIFIED` unless its release and gate evidence
  standard is met.
- Preserve failed approaches in the progress log so another worker does not
  repeat them.

## Handoff and Completion

A worker finishes by creating a self-contained handoff with changed files,
contracts, validation, residual risk, migration notes, and rollback guidance.
The worker sets the task record to `IN_REVIEW`, not `DONE`. A reviewer reproduces
the evidence, and the coordinator integrates and closes the task.

## Build and Test

```powershell
uv sync --locked --dev
uv run ruff check src tests
uv run mypy src tests
uv run pytest -q
$env:UV_LINK_MODE = "copy"
uv build
```

Use narrower tests first. Run the complete sequence for shared contracts, risk,
state, execution, packaging, or release changes.

## Documentation

- Every created Markdown file must have a linked contents block immediately
  after its H1, including all H2 headings and nested H3 headings.
- Keep links, task IDs, status counts, and evidence references synchronized.
- Behavioral changes update the owning specification, tests, and traceability in
  the same reviewed work item.
- Do not put secrets, personal records, full account identifiers, or raw private
  logs in coordination documents.
