# CoAgent Communication Contract V1

Date: 2026-05-28

Status: design baseline for `COAGENT-DESIGN-08`.

## Purpose

This contract defines how work moves between CoAgent conversations and workers.

The rule is:

```text
conversation is UI and working surface
packet is durable communication
event log is recovery truth
```

## Durable Communication Units

| Unit | Created By | Consumed By | Purpose |
|---|---|---|---|
| task packet | DispatchCenter | owner conversation | start or update durable work |
| context pack | DispatchCenter / runtime | dedicated task conversation | compact startup state |
| checkpoint packet | owner conversation | DispatchCenter / PMO | recoverable progress, risk, blocker |
| result packet | owner conversation | result router / reviewer | terminal or reviewable output |
| review note | Verification/Security/Docs/DevOps/PMO | DispatchCenter / owner | accept, reject, or request changes |
| event log entry | runtime/dispatcher | all recovery flows | state transition evidence |

Plain chat may explain work, but it is not sufficient for handoff or
acceptance.

## Standard Task Dispatch

```text
PMO/main:
  frames user objective

DispatchCenter:
  creates task_id
  records canonical_task_goal
  assigns accountable_owner
  records worktree binding when file isolation is required
  writes task packet

Owner conversation:
  receives task packet
  works within read/write scope
  emits checkpoint or result packet

Result router/reviewer:
  imports packet
  marks review metadata

PMO/main:
  reports accepted result or escalation
```

## Worktree-Aware Dispatch

When a task uses a separate Codex App worktree or Git worktree, the dispatch
packet must carry:

```yaml
worktree_path:
branch_or_base:
write_scope:
merge_owner:
review_gate:
close_condition:
```

Worktree state is part of execution context, not acceptance. A result is still
accepted only through result packet evidence and review metadata.

Worktree closeout requires:

- result packet imported,
- review state known,
- Git state summarized,
- merge or discard decision recorded,
- no untracked broad artifacts left unexplained.

## Checkpoint Contract

Checkpoint content:

```yaml
task_id:
canonical_task_goal:
conversation_objective:
owner:
current_state:
evidence_found:
files_changed:
commands_run:
blockers:
risks:
decision_needed:
next_step:
continue_or_stop:
```

Checkpoint required when:

- a long task reaches its checkpoint interval,
- appetite or circuit breaker may be exceeded,
- evidence contradicts the plan,
- the worker needs user input,
- the worker wants to change owner, scope, or goal,
- an irreversible step is near.

## Result Packet Contract

A result packet must include:

- task id,
- task class,
- canonical status,
- summary,
- owner/role,
- files changed,
- commands run,
- evidence,
- acceptance state,
- review status,
- known exclusions,
- residual risks,
- next recommended action.

Terminal result without evidence should be imported as `needs_review` or
`rejected`, not accepted.

## Support Work

Supporting departments do not change the canonical task goal.

Support flow:

```text
accountable owner requests support
DispatchCenter records child/support task or review request
support owner returns result packet or review note
accountable owner integrates
PMO/DispatchCenter accepts or escalates
```

## Owner Change

Owner change requires:

- current owner checkpoint,
- reason for handoff,
- new accountable owner,
- updated task packet or context pack,
- event log entry,
- unresolved risks.

No worker may silently hand work to another durable conversation.

## Goal Change

Goal change requires:

- evidence that current goal is wrong or incomplete,
- proposed replacement canonical task goal,
- affected scope and acceptance changes,
- PMO/user or DispatchCenter decision record,
- event log entry.

Until accepted, the task remains under the old canonical task goal and should
usually be `review_required` or `blocked`.

## Communication Failure

Treat communication as failed when:

- the target conversation is not visible or recoverable,
- no task packet was delivered,
- the packet was delivered only through a shadow/local Codex home while the
  user expected a front-end-visible department message,
- no result packet can be found,
- the worker result exists only in chat,
- the task id or canonical goal does not match,
- packet evidence paths are missing,
- review metadata is absent for high-risk work.

Recovery action:

```text
stop dispatch
record blocker
repair registry or context pack
retry only with a fresh packet or explicit recovery note
```

If the accountable owner falls back to local execution after department
transport fails, the fallback must be reported as a coordination failure, not
as successful department execution. A visible department status message should
be sent and synced before claiming that the department conversation has been
updated.

## V1 Constraint

V1 communication is hub-and-spoke through DispatchCenter. Peer-to-peer
department communication may happen as human-readable discussion, but it is not
durable authority unless DispatchCenter records the packet/event.
