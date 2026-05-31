# CoAgent Review And Merge Protocol V1

Date: 2026-05-28

Status: design baseline for the final closure of `COAGENT-DESIGN-09`.

## Purpose

This document freezes the last missing rule inside the task surface model:

```text
who reviews
who merges
who closes the worktree
who decides the task is accepted
```

Without this layer, CoAgent still has one dangerous ambiguity:

- a task may complete technically but nobody owns acceptance,
- DevOps may merge work that verification or security has not accepted,
- a reviewer may reject work but the worktree still looks "active",
- a result packet may exist without a merge/discard decision.

## Four Distinct Roles

CoAgent V1 distinguishes four roles:

| Role | Responsibility | May be the same lane as another role? |
|---|---|---|
| `accountable_owner` | delivers the task outcome and returns the result packet | yes, but should not self-certify high-risk review |
| `review_owner` | decides accept / reject / changes requested | yes for low-risk work |
| `merge_owner` | decides merge / stage / discard for Git state | often DevOps or approved Git owner |
| `close_owner` | closes task surface and worktree after state is recorded | may equal merge owner or DispatchCenter |

These roles must not collapse into one vague "owner".

## Acceptance Chain

V1 acceptance is sequential:

```text
task execution complete
  -> result packet returned
  -> review owner decides acceptance_state and review_status
  -> merge owner decides Git disposition if file surface is mutable
  -> close owner records closeout state
  -> DispatchCenter / PMO marks durable task terminal
```

Review acceptance and Git merge are related but not identical.

## Review Outcome States

The review owner must emit one of:

| review_status | Meaning |
|---|---|
| `accepted` | evidence and output are sufficient for this review gate |
| `needs_review` | more review or additional evidence is required |
| `rejected` | the result is not acceptable in current form |
| `pending` | review has not run yet |
| `not_required` | explicit bypass for low-risk work only |

The paired `acceptance_state` should be:

| acceptance_state | Meaning |
|---|---|
| `met` | acceptance criteria satisfied |
| `partially_met` | some criteria met, more work needed |
| `not_met` | criteria not satisfied |
| `unknown` | not yet determined |

## Merge Outcome States

If a mutable file surface or worktree exists, merge owner must emit one of:

| git_disposition | Meaning |
|---|---|
| `merge_ready` | accepted and ready for merge/stage |
| `staged_for_integration` | accepted but waiting for batch integration |
| `hold` | technically accepted but intentionally not merged yet |
| `discard` | worktree/output should not be integrated |
| `superseded` | replaced by newer work |
| `not_applicable` | no mutable Git surface exists |

This decision belongs in task metadata, result review notes, or closeout notes.

## Default Role Mapping

### Low-risk main-thread task

```text
accountable_owner = MainAgent
review_owner = PMO/main
merge_owner = PMO/main or Git owner
close_owner = DispatchCenter or MainAgent
```

### Department execution task

```text
accountable_owner = department owner
review_owner = PMO or verification/docs/security lane as needed
merge_owner = DevOps or approved Git owner
close_owner = DispatchCenter
```

### Dedicated long task with worktree

```text
accountable_owner = task team integration owner
review_owner = explicit reviewer lane
merge_owner = DevOps / GitIntegrator
close_owner = DispatchCenter after review + Git disposition are recorded
```

### Task team with multiple worktrees

```text
accountable_owner = task team integration owner
slice_owner = scoped conversation owner
review_owner = explicit reviewer for each slice plus team-level reviewer
merge_owner = DevOps / GitIntegrator or approved release integrator
close_owner = DispatchCenter after slice closeout and team closeout are recorded
```

Each scoped conversation may have a task worktree. Verification may have a
review worktree. DevOps may have an integration worktree. A subagent may use an
ephemeral worktree only if its parent scoped conversation owns cleanup and
imports or discards the result.

## Mandatory Review/Merge Metadata

Any durable task with mutable output should be able to answer:

```text
review_owner:
review_gate:
review_status:
acceptance_state:
merge_owner:
git_disposition:
close_owner:
close_condition:
```

If these fields are not known yet, the task is not ready for final closeout.

## Worktree Closeout Contract

A worktree may be closed only when all are true:

- result packet exists,
- review owner has recorded outcome,
- merge owner has recorded Git disposition,
- remaining Git state is summarized,
- unresolved generated/untracked artifacts are explained,
- next task is recorded if work continues elsewhere.

Allowed worktree closeout endings:

```text
accepted_and_merged
accepted_staged_pending_integration
accepted_hold
rejected_discarded
superseded_closed
```

## Separation Rules

1. Review owner can reject without merge owner ever merging.
2. Merge owner cannot silently convert `needs_review` into merged work.
3. Accountable owner cannot claim `completed` if review is still materially pending.
4. Close owner cannot close the worktree only because the conversation went quiet.
5. DispatchCenter cannot mark the task fully done if Git disposition is still unknown for mutable work.

## Anti-Patterns

Do not allow:

- "review later" with no review owner,
- "merge later" with no merge owner,
- merged work from a task whose result packet still says `needs_review`,
- discarded worktree with no recorded reason,
- a reviewer modifying the same write surface as the accountable owner and then self-accepting the task without separation,
- closing the conversation edge before result/review/Git disposition are all recoverable.

## Integration With Current V1 Model

This document does not change the previously frozen protocol.

It specializes `COAGENT-DESIGN-09` by making the following explicit:

- task surface decides where execution happens,
- file surface decides where edits live,
- review surface decides acceptance,
- merge owner decides Git integration,
- close owner decides worktree/task-surface closure after durable state is updated.

## Next Gate

After this closure, the next safe step is no longer broad design discussion.
It should be one bounded implementation item, such as:

1. worktree registry / closeout metadata support, or
2. review/merge-owner fields added to runtime closeout helpers, or
3. transport/session-state repair for visible thread lifecycle reliability.
