# Parallel Agent and Developer Work Protocol

<details open>
<summary><b>Contents</b></summary>

- [Purpose](#purpose)
- [Source of Truth Hierarchy](#source-of-truth-hierarchy)
- [Roles](#roles)
- [Coordination Records](#coordination-records)
- [Task Lifecycle](#task-lifecycle)
  - [Refine](#refine)
  - [Claim](#claim)
  - [Implement](#implement)
  - [Handoff](#handoff)
  - [Review](#review)
  - [Integrate](#integrate)
- [Claim Leases](#claim-leases)
- [Write Scope and Conflict Prevention](#write-scope-and-conflict-prevention)
- [Git Branch and Worktree Rules](#git-branch-and-worktree-rules)
- [Task Record Rules](#task-record-rules)
- [Evidence and Validation](#evidence-and-validation)
- [Status and Completion Rules](#status-and-completion-rules)
- [Blockers Decisions and Incidents](#blockers-decisions-and-incidents)
- [Protected Shared Files](#protected-shared-files)
- [Coordinator Reconciliation Cycle](#coordinator-reconciliation-cycle)
- [Worker Startup Checklist](#worker-startup-checklist)
- [Worker Shutdown Checklist](#worker-shutdown-checklist)
- [Stale Claim and Failure Recovery](#stale-claim-and-failure-recovery)
- [GitHub Mirroring](#github-mirroring)
- [Safety Constraints](#safety-constraints)

</details>

---

**Version:** 1.0  
**Date:** 31 August 2026  
**Status:** Active coordination baseline  
**Master tracker:** [MASTER-TASK-TRACKER.md](../MASTER-TASK-TRACKER.md)  
**Authority:** [CHARTER.md](../CHARTER.md)

## Purpose

This protocol lets multiple AI agents and developers work concurrently without
duplicating tasks, editing the same files unknowingly, losing decisions, or
claiming completion without reproducible evidence.

The central design is deliberate:

- The master tracker is a read-mostly coordinator-owned index.
- Each worker owns a separate claim, task record, branch, and handoff.
- Requirement and safety status remain in their existing authoritative files.
- Integration occurs through one ordered queue after independent review.

Only the coordinator may edit master tracker status, counts, claims, integration
queue, completed work, or change log.

## Source of Truth Hierarchy

When records conflict, stop work and apply this priority order:

1. [Project Charter](../CHARTER.md) for scope, authorization, loss boundaries,
   and stage gates.
2. Accepted entries in the [Decision Log](13-decision-log.md).
3. Requirements and owning specifications in `docs/01` through `docs/11`.
4. The [Requirements Traceability Matrix](14-requirements-traceability.md) for
   requirement implementation and verification status.
5. [MASTER-TASK-TRACKER.md](../MASTER-TASK-TRACKER.md) for task status,
   dependencies, claims, integration order, and aggregate progress.
6. The individual task record for scope, subtasks, progress, and evidence.
7. Claim and handoff records for temporary ownership and transfer details.

A lower-priority record never overrides a higher-priority safety or behavioral
contract. The coordinator resolves inconsistencies before work resumes.

## Roles

| Role | Responsibilities | Prohibited actions |
| --- | --- | --- |
| Project owner | Approves charter, external providers, capital, stage gates, and consequential decisions | Delegating personal loss decisions to an agent |
| Coordinator | Owns master status, approves claims, resolves overlap, orders integration, and closes tasks | Marking requirements verified without their required evidence |
| Implementer | Works one approved task inside its write scope and records evidence | Editing the master tracker or another active task scope |
| Reviewer | Reproduces acceptance evidence and checks contracts, regressions, and scope | Approving from summaries without running available checks |
| Release integrator | Integrates reviewed branches in queue order and runs combined gates | Dropping conflicting changes silently |

One person or agent may hold several roles at different times, but a
safety-critical implementation should receive independent review whenever a
second qualified reviewer is available.

## Coordination Records

| Record | Path | Owner | Mutation policy |
| --- | --- | --- | --- |
| Master tracker | `MASTER-TASK-TRACKER.md` | Coordinator | Coordinator edits only |
| Claim | `coordination/claims/TB-NNNN.md` | Worker, then coordinator | Lease fields only after approval |
| Task record | `coordination/tasks/TB-NNNN.md` | Assigned worker | Append progress; preserve prior evidence |
| Handoff | `coordination/handoffs/TB-NNNN.md` | Worker and reviewer | Worker submits; reviewer appends decision |
| Decision | Existing decision-record process | Project owner or coordinator | Supersede; never rewrite accepted history |
| Incident | Existing incident-report process | Incident owner | Append and close through review |

Create records from the templates in `docs/templates/`. Coordination records are
committed with the code they describe and may not contain credentials, personal
tax data, full broker account identifiers, or raw private logs.

## Task Lifecycle

### Refine

The coordinator may change a `BACKLOG` item to `READY` only when:

- The task has one stable ID and one owning work package.
- Dependencies are `DONE` or explicitly unnecessary.
- External blockers are absent.
- Acceptance checks are executable or a deterministic fake is defined.
- The primary write scope and protected shared-file needs are named.
- Relevant requirements, decisions, safety effects, and documentation are linked.
- The task is small enough for one reviewable branch.

Split a task before claiming it when workers would need unrelated write scopes or
when one part can be independently accepted.

### Claim

1. Read the master tracker, source-of-truth documents, current claims, and
   integration queue.
2. Select a `READY` task only.
3. Create `coordination/claims/TB-NNNN.md` from the claim template with status
   `PROPOSED`.
4. Record claimant, base commit, branch, worktree, exact write scope, expected
   shared files, start time, lease expiry, and planned checks.
5. Ask the coordinator to detect overlap and approve the claim.
6. Do not edit implementation files until the claim is `ACTIVE` and the master
   task is `CLAIMED`.

The first locally created claim does not win. The first coordinator-approved and
shared claim wins.

### Implement

1. Create a dedicated branch and worktree from the claim's exact base commit.
2. Change the task record to `IN_PROGRESS` and renew the claim heartbeat.
3. Gather the smallest local evidence, state a falsifiable hypothesis, make a
   narrow edit, and immediately run the focused check.
4. Stay inside the approved write scope. Request scope expansion before editing
   an undeclared file.
5. Update the task progress log after meaningful checkpoints, failed hypotheses,
   new blockers, contract changes, or evidence invalidation.
6. Rebase or merge the coordinator-approved baseline only at a deliberate sync
   point, then rerun affected checks.
7. Never add credentials, runtime data, broker account details, or generated
   environments to the branch.

### Handoff

The worker creates `coordination/handoffs/TB-NNNN.md` when:

- Every agreed subtask is complete or explicitly deferred with approval.
- Focused tests and required broader checks pass.
- Changed files, migrations, public contracts, and documentation are listed.
- Exact commands, exit codes, test counts, and known residual risk are recorded.
- The branch contains no unrelated changes or generated artefacts.
- The task record status is `IN_REVIEW`, not `DONE`.

The handoff must be understandable without private chat history.

### Review

The reviewer:

1. Confirms the branch and base commit match the active claim.
2. Compares implementation with the task, requirements, architecture, and safety
   contracts.
3. Runs the focused acceptance checks and affected quality gates.
4. Checks missing, stale, invalid, retry, restart, and failure behavior where
   applicable.
5. Reviews security, data, migration, evidence, and documentation impact.
6. Records `APPROVE`, `CHANGES_REQUESTED`, or `BLOCKED` in the handoff.

A reviewer does not change the master status directly.

### Integrate

1. The coordinator places an approved task into the Integration Queue.
2. The release integrator applies tasks in dependency and shared-file order.
3. Conflicts are resolved against the source-of-truth hierarchy with both task
   records visible. No side is silently discarded.
4. Combined lint, type, test, documentation, and package checks run after each
   risky or cross-cutting integration.
5. The coordinator updates exports and shared metadata when workers were told not
   to touch those files.
6. Only after integration evidence passes does the coordinator mark the task
   `DONE`, release its claim, update counts, and assess requirement status.

## Claim Leases

Claims are leases, not permanent ownership.

| Field | Default rule |
| --- | --- |
| Lease duration | 24 hours unless the coordinator records another duration |
| Heartbeat | At least every 4 hours of active work and before any pause |
| Renewal | Update progress, changed-file scope, and new expiry before expiration |
| Expiration | Coordinator verifies inactivity before marking `EXPIRED` |
| Release | Required after integration, cancellation, handoff withdrawal, or reassignment |

An expired claim is not automatically safe to overwrite. The coordinator first
checks its branch, task record, unpushed work, and file overlap, then preserves or
hands off useful changes.

## Write Scope and Conflict Prevention

- Every claim lists exact files or glob-like directory boundaries it may edit.
- Two `ACTIVE` claims may not overlap a write scope unless the coordinator names
  an integration owner and merge order in both claims.
- Read access is unrestricted; write ownership is not.
- Workers avoid shared `__init__.py`, `pyproject.toml`, `uv.lock`, CI, and master
  documents unless their claim explicitly grants those files.
- When a new dependency is needed, the worker records it in the task and asks the
  coordinator to make or assign the shared metadata change.
- Generated files, format-only repo-wide rewrites, and broad renames require a
  dedicated task because they create conflicts across lanes.
- A worker who discovers an out-of-scope root cause pauses, records evidence, and
  requests a task or scope change instead of repairing it opportunistically.

## Git Branch and Worktree Rules

- Establish one approved baseline commit before parallel work begins.
- Use branch `task/TB-NNNN-short-name` and one separate worktree per active task.
- Record the full base commit SHA in the claim and task record.
- Never let two agents write in the same worktree.
- Do not commit directly to `main` and do not force-push a shared branch.
- Keep commits task-scoped and explain behavioral intent.
- Pull, merge, or rebase only after preserving current work and checking claim
  overlap.
- Before handoff, compare the branch with its base and remove unrelated files.
- The coordinator records the integrated commit in the task and master change
  log.

If a remote is unavailable, the same branch and worktree rules apply locally,
but the coordinator must ensure all workers can access the current claim records
and branches before authorizing concurrency.

## Task Record Rules

Each task record contains:

- ID, parent work package, status, priority, worker, reviewer, branch, base commit,
  claim, lease, and last update.
- Linked requirements, decisions, dependencies, blockers, and source contracts.
- In-scope and out-of-scope behavior plus exact write scope.
- Ordered subtasks with checkboxes and acceptance evidence for each.
- A progress log that appends date, actor, action, result, and next step.
- Decisions and assumptions discovered during implementation.
- Validation commands, exit codes, test counts, artefacts, and failures.
- Changed files and any migration, compatibility, or evidence impact.
- Review decision, integration commit, closure rationale, and follow-up tasks.

Never delete a failed experiment or failed validation entry. Correct it with a
later record so another worker does not repeat the same path.

## Evidence and Validation

Evidence quality follows the [Testing and Quality Strategy](09-testing-and-quality.md).

- Run the cheapest behavior-scoped check immediately after the first edit.
- Record exact commands and outcomes, not merely "tests passed".
- Run Ruff, strict mypy, and the affected pytest suite for Python behavior.
- Run complete tests for shared contracts, risk, state, execution, or release
  changes.
- Validate Markdown navigation and relative links for documentation changes.
- Build and smoke-test packaging when package metadata or public commands change.
- Never expose secrets or full private logs in evidence records.
- A task can be `DONE` while linked requirements remain `SPECIFIED` or
  `IMPLEMENTED`; requirement `VERIFIED` has its own release and gate standard.

## Status and Completion Rules

- Workers may propose status in their task record but cannot mark master tasks
  `DONE`.
- Code existence is not completion; acceptance evidence and review are required.
- A passing unit suite does not satisfy a paper, duration, recovery, or stage gate.
- Partial work remains `IN_PROGRESS` or `BLOCKED`; it is not rounded up.
- Deferred subtasks become new linked task IDs before the parent closes.
- Regressions reopen the owning task or create a defect task and identify invalid
  evidence.
- Summary counts and task rows change together in one coordinator commit.

## Blockers Decisions and Incidents

- Use `BLOCKED` only for an external dependency, unresolved decision, credential,
  provider, incident, or unavailable evidence. Unfinished internal dependencies
  remain `BACKLOG`.
- Record the blocker ID, owner, date, impact, evidence needed, and next review.
- Do not guess owner capital, broker eligibility, tax treatment, data rights, or
  provider behavior to unblock work.
- Consequential choices use the existing decision-record template and decision
  log.
- Safety, credential, state, order, data-integrity, or evidence failures use the
  incident template and may halt related lanes.
- A blocker resolution updates the decision or incident first, then the task and
  master tracker.

## Protected Shared Files

The following require explicit coordinator write permission in a claim:

- `CHARTER.md` and `MASTER-TASK-TRACKER.md`.
- `AGENTS.md` and this protocol.
- `docs/01-requirements.md`, `docs/02-architecture.md`, and owning specifications
  when behavior changes.
- `docs/13-decision-log.md` and `docs/14-requirements-traceability.md`.
- `pyproject.toml`, `uv.lock`, `.github/workflows/**`, and repository-wide config.
- Shared package exports such as `src/trading_bot/**/__init__.py`.

Workers may propose exact patches to protected files in their handoff. The
coordinator applies them during integration unless the claim grants direct
ownership.

## Coordinator Reconciliation Cycle

At the start and end of each coordination cycle:

1. Pull or identify the agreed baseline and check the working tree.
2. Reconcile claim files with Active Claims and expire stale leases deliberately.
3. Check write-scope overlap and integration-order changes.
4. Reconcile task records with master statuses and summary counts.
5. Process blockers, decisions, incidents, and evidence invalidation.
6. Review handoffs and place approved items in the Integration Queue.
7. Integrate in dependency order and run combined checks.
8. Update requirement traceability only where its standard is met.
9. Publish the new baseline commit and notify workers to sync deliberately.

## Worker Startup Checklist

- [ ] Read `AGENTS.md`, the master tracker, this protocol, and the task's owning
      specifications.
- [ ] Confirm the task is `READY` and has no open blocker.
- [ ] Confirm no active claim or write scope overlaps the intended work.
- [ ] Record the exact base commit, branch, worktree, and lease.
- [ ] Obtain coordinator approval before editing.
- [ ] Run the current focused baseline checks.
- [ ] State the local hypothesis and first discriminating validation in the task
      record.

## Worker Shutdown Checklist

- [ ] Update the task progress log and claim heartbeat or release the claim.
- [ ] Record changed files, exact validation outcomes, failures, and residual risk.
- [ ] Remove generated artefacts and verify no secret or runtime data is included.
- [ ] Commit or otherwise preserve work on the task branch.
- [ ] Create or update the handoff when work is ready for review.
- [ ] Do not edit the master tracker to self-close the task.

## Stale Claim and Failure Recovery

When a worker disappears, a branch breaks, or two agents collide:

1. Stop affected writes.
2. Preserve each branch, worktree state, claim, and task log.
3. Identify the latest valid common base and overlapping files.
4. Let the coordinator select one owner and integration order.
5. Convert useful unintegrated work into a handoff; do not copy changes without
   attribution and validation.
6. Reassign with a new lease and record the superseded claim.
7. Run focused checks after conflict resolution, then the affected combined suite.

No worker resolves a semantic conflict by choosing whichever version merges
cleanly.

## GitHub Mirroring

GitHub Issues, assignees, labels, milestones, pull requests, and Projects may
mirror repository coordination records after a remote exists.

Recommended labels are `status:ready`, `status:claimed`, `status:blocked`,
`status:review`, `workstream:data`, `workstream:risk`, `workstream:execution`, and
`safety-critical`.

Until an accepted decision changes the policy, repository records remain the
portable source of truth. A GitHub issue that conflicts with the committed master
tracker or an active claim must be reconciled by the coordinator before work.

## Safety Constraints

- Current authorization remains `PAPER_ONLY` and Stage 0 is not passed.
- No task, claim, issue, branch, reviewer, or coordinator may authorize live
  trading or invent owner-dependent values.
- Broker order code waits for risk, durable intent, account guards, restart, and
  reconciliation contracts.
- Secrets never enter coordination records, commits, logs, screenshots, or chat
  summaries.
- Ambiguous state, stale data, conflicting records, or unknown order outcomes add
  no new exposure.
- Safety limits may be tightened through review; relaxing them requires the
  existing approval process and new evidence.
