# Task Handoff Template

<details open>
<summary><b>Contents</b></summary>

- [Handoff Identity](#handoff-identity)
- [Completion Summary](#completion-summary)
- [Scope Delivered](#scope-delivered)
- [Changed Files](#changed-files)
- [Contracts and Requirements](#contracts-and-requirements)
- [Validation](#validation)
- [Safety and Security](#safety-and-security)
- [Known Issues and Follow Ups](#known-issues-and-follow-ups)
- [Integration Instructions](#integration-instructions)
- [Reviewer Decision](#reviewer-decision)
- [Coordinator Closure](#coordinator-closure)

</details>

---

**Task ID:** `TB-NNNN`  
**Handoff status:** `DRAFT`  
**From:** `TBD`  
**To reviewer:** `TBD`  
**Branch:** `task/TB-NNNN-short-name`  
**Base commit:** `TBD`  
**Head commit:** `TBD`  
**Submitted at UTC:** `TBD`

## Handoff Identity

| Field | Value |
| --- | --- |
| Task record | `coordination/tasks/TB-NNNN.md` |
| Claim record | `coordination/claims/TB-NNNN.md` |
| Work package | `TBD` |
| Requirement IDs | `TBD` |
| Requested review decision | `APPROVE` or `TBD` |

## Completion Summary

State what now works, what evidence supports it, and what is deliberately not
included: `TBD`.

## Scope Delivered

- [ ] Every approved subtask is complete.
- [ ] Any deferred item has a new linked task ID.
- [ ] Work stayed inside the approved write scope.
- [ ] Owning tests and documentation were updated.
- [ ] No unrelated change or generated artefact is included.

Deviation from approved scope: `None` or `TBD`.

## Changed Files

| Path | Behavioral or documentation change | Review focus |
| --- | --- | --- |
| `TBD` | `TBD` | `TBD` |

Shared or protected file changes approved by: `None` or `TBD`.

## Contracts and Requirements

| Requirement or invariant | Implementation evidence | Proposed status effect |
| --- | --- | --- |
| `TBD` | `TBD` | No status change unless coordinator approves |

Decision, migration, schema, or compatibility impact: `TBD`.

## Validation

| Check | Exact command | Exit code | Result and count | Artefact or log reference |
| --- | --- | --- | --- | --- |
| Focused acceptance | `TBD` | `TBD` | `TBD` | `TBD` |
| Affected suite | `TBD` | `TBD` | `TBD` | `TBD` |
| Ruff | `TBD` | `TBD` | `TBD` | `TBD` |
| Strict mypy | `TBD` | `TBD` | `TBD` | `TBD` |
| Full pytest when required | `TBD` | `TBD` | `TBD` | `TBD` |
| Documentation or package checks | `TBD` | `TBD` | `TBD` | `TBD` |

Failures encountered and regression proof: `TBD`.

## Safety and Security

- [ ] Current authorization remains `PAPER_ONLY`.
- [ ] No real credential, account identifier, private path, or runtime data exists
      in the branch or evidence.
- [ ] Missing, stale, ambiguous, retry, restart, and failure behavior was reviewed
      where applicable.
- [ ] Risk and reconciliation boundaries were not bypassed or weakened.
- [ ] Secret and generated-file checks pass.

Residual safety or security risk: `TBD`.

## Known Issues and Follow Ups

| Item | Severity | Blocking | Owner | Follow-up task |
| --- | --- | --- | --- | --- |
| `TBD` | `TBD` | `YES` or `NO` | `TBD` | `TBD` |

Open assumptions or questions: `TBD`.

## Integration Instructions

| Field | Value |
| --- | --- |
| Required integration order | `TBD` |
| Expected conflict files | `TBD` |
| Dependency or lockfile action | `TBD` |
| Migration or data action | `TBD` |
| Post-integration commands | `TBD` |
| Rollback method | `TBD` |

## Reviewer Decision

Reviewer appends the decision; do not rewrite worker evidence.

| Field | Value |
| --- | --- |
| Decision | `APPROVE`, `CHANGES_REQUESTED`, or `BLOCKED` |
| Reviewer | `TBD` |
| Review UTC time | `TBD` |
| Reproduced evidence | `TBD` |
| Findings | `TBD` |
| Required changes | `None` or `TBD` |

## Coordinator Closure

| Field | Value |
| --- | --- |
| Integration decision | `QUEUED`, `INTEGRATED`, `REJECTED`, or `TBD` |
| Integration commit | `TBD` |
| Combined gates | `TBD` |
| Master task status | Not `DONE` until integration evidence passes |
| Requirement status decision | `TBD` |
| Claim release | `TBD` |
| Coordinator and UTC time | `TBD` |
