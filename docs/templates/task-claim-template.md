# Task Claim Template

<details open>
<summary><b>Contents</b></summary>

- [Claim Identity](#claim-identity)
- [Preconditions](#preconditions)
- [Write Scope](#write-scope)
- [Shared Files and Overlap](#shared-files-and-overlap)
- [Planned Validation](#planned-validation)
- [Lease Heartbeat](#lease-heartbeat)
- [Coordinator Approval](#coordinator-approval)
- [Release or Expiration](#release-or-expiration)

</details>

---

**Task ID:** `TB-NNNN`  
**Claim status:** `PROPOSED`  
**Claimant:** `TBD`  
**Base commit:** `TBD`  
**Branch:** `task/TB-NNNN-short-name`  
**Worktree:** `TBD`  
**Claimed at UTC:** `TBD`  
**Lease expires at UTC:** `TBD`  
**Last heartbeat UTC:** `TBD`

## Claim Identity

| Field | Value |
| --- | --- |
| Task record | `coordination/tasks/TB-NNNN.md` |
| Master task status | Must be `READY` before approval |
| Work package | `TBD` |
| Requirements | `TBD` |
| Coordinator | `TBD` |

## Preconditions

- [ ] Task is `READY` in the master tracker.
- [ ] Internal dependencies are `DONE`.
- [ ] External blockers are closed or not applicable.
- [ ] Source contracts and acceptance checks are understood.
- [ ] Base commit exists and is shared with all workers.
- [ ] No active claim overlaps the proposed write scope.
- [ ] Current focused baseline checks pass.

Unmet precondition: `TBD`.

## Write Scope

**May edit:**

- `TBD`

**Must not edit:**

- `TBD`
- Protected shared files unless listed in Coordinator Approval.

**Expected new files:** `TBD`

## Shared Files and Overlap

| File or boundary | Other task or owner | Integration order | Coordinator decision |
| --- | --- | --- | --- |
| None identified | - | - | `TBD` |

If overlap is discovered after approval, stop both writes and ask the coordinator
to revise the claims.

## Planned Validation

| Check | Command or method | Expected discriminator |
| --- | --- | --- |
| Focused first check | `TBD` | `TBD` |
| Affected component tests | `TBD` | `TBD` |
| Broader quality gate | `TBD` | `TBD` |

## Lease Heartbeat

Append heartbeat rows; never rewrite prior rows.

| UTC time | Progress since prior heartbeat | Current blocker | Files touched | New expiry |
| --- | --- | --- | --- | --- |
| `TBD` | Claim proposed | None | None | `TBD` |

## Coordinator Approval

| Decision | Value |
| --- | --- |
| Claim decision | `APPROVE`, `REJECT`, or `REVISE` |
| Approved write scope | `TBD` |
| Protected shared files granted | None unless named |
| Integration owner and order | `TBD` |
| Approved lease expiry | `TBD` |
| Coordinator and UTC time | `TBD` |

**Claim becomes active only when:** `Claim decision = APPROVE` and the master task
is `CLAIMED`.

## Release or Expiration

| Field | Value |
| --- | --- |
| Final claim state | `RELEASED`, `EXPIRED`, `SUPERSEDED`, or `CANCELLED` |
| Released by | `TBD` |
| Released at UTC | `TBD` |
| Branch or handoff preserving work | `TBD` |
| Reason | `TBD` |
