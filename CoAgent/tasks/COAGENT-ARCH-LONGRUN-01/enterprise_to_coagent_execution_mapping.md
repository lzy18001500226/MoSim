# COAGENT-ARCH-LONGRUN-01 Enterprise To CoAgent Execution Mapping

Date: 2026-05-30
Status: design draft

## Purpose

This document closes a practical gap between the enterprise-management model
and the CoAgent execution model.

The enterprise layer says how a high-performing technical company should run:
task intake, ownership, shaped work, review gates, release control, incident
handling, and retrospective learning. CoAgent must not copy that model into a
static bureaucracy. It must convert those management ideas into durable runtime
objects that make one user task finish with evidence.

## Translation Rule

Use enterprise concepts only when they produce one of these CoAgent objects:

- task charter;
- dynamic task team;
- scoped conversation;
- context pack or context delta;
- mailbox message;
- result/review/blocker packet;
- worktree binding;
- artifact manifest;
- verification gate;
- Git integration packet;
- knowledge promotion record;
- retrospective action.

If a management concept does not create a decision, evidence, gate, or
recoverable state, it is process decoration and should not be added.

## Object Mapping

| Enterprise concept | CoAgent execution object | Required durable evidence | Failure if missing |
|---|---|---|---|
| Mission / strategy | project baseline and product appetite | design docs, task charter reference | task optimizes local activity instead of project value |
| User request | PMO intake record | task note or charter | chat fragments become competing goals |
| Shaped work | task charter | goal, DoD, appetite, non-goals, stop condition | workers start before scope is safe |
| DRI / owner | accountable owner field | task ledger, board owner | responsibility diffuses across conversations |
| Department | capability owner lane | department registry, owner in packet | fixed org chart drives task shape |
| Project team | dynamic task team | shared task board | many conversations exist without one team goal |
| Meeting | checkpoint/review packet | event log, result packet, review note | decisions remain trapped in chat |
| Status report | checkpoint packet | evidence path, blocker, next step | progress cannot be audited |
| Interface contract | context pack plus artifact contract | source paths, expected outputs | slices make incompatible assumptions |
| Release train | integration plan | worktree binding, merge order, checks | accepted work never reaches project state |
| QA gate | verification packet | tests, evidence, trace rubric | completion is claimed from execution only |
| Security/compliance gate | safety review or blocker packet | policy decision, stop/resume record | unsafe action depends on model judgment |
| Incident command | incident task team | blocker packet, last safe state, recovery plan | repeated failures burn time silently |
| Retrospective | knowledge promotion record | skill/hook/doc/test/backlog update | the same failure repeats in later tasks |

## Execution Chain

For any non-trivial user task, CoAgent should run this chain:

```text
PMO intake
  -> Dispatch task charter
  -> topology and task-team decision
  -> context pack construction
  -> scoped conversation or subagent dispatch
  -> checkpoint/result/blocker packet
  -> review packet
  -> integration packet
  -> knowledge promotion
  -> retrospective action if a repeated failure occurred
```

This is the practical translation of company operating rhythm into CoAgent.
The key point is that each arrow creates a recoverable artifact. A conversation
may discuss, but the artifact is what later agents can rely on.

## Task-Team Objects

### Task Charter

Enterprise role: shaped work, DRI assignment, scope control.

CoAgent fields:

```text
task_id
canonical_task_goal
definition_of_done
appetite
non_goals
owner_department
integration_owner
review_owner
stop_conditions
manual_review_points
first_checkpoint_due
```

Rule:

No scoped conversation starts until the charter exists.

### Shared Task Board

Enterprise role: project board and operating review.

CoAgent fields:

```text
team_id
task_id
canonical_task_goal
current_phase
critical_path_owner
wip_limit
members
open_blockers
integration_queue
review_gates
context_deltas_pending
```

Rule:

The board records state. It must not become a second transcript.

### Scoped Conversation

Enterprise role: temporary specialist on a project team.

CoAgent fields:

```text
conversation_id
slice_goal
parent_task_id
context_pack_path
read_scope
write_scope
worktree_binding
result_packet_path
review_owner
close_condition
```

Rule:

A scoped conversation owns a slice, not the task goal.

### Short-Lived Subagent

Enterprise role: bounded expert consultation or delegated analysis.

CoAgent fields:

```text
objective
read_scope
forbidden_actions
expected_output
stop_condition
parent_result_path
```

Rule:

Subagents are consumed by their parent conversation. They do not own Git,
review queues, safety gates, or cross-conversation communication.

## Communication Objects

### Mailbox Message

Enterprise role: formal cross-team request.

Allowed message classes:

- `context_refresh`;
- `dependency_ready`;
- `blocker`;
- `review_request`;
- `integration_request`;
- `human_action_request`;
- `decision_required`.

Rule:

Peer-to-peer communication is allowed only if it is represented in the
mailbox. Hidden peer chat is not accepted authority.

### Result Packet

Enterprise role: deliverable handoff.

Minimum content:

```text
status
canonical_goal_restatement
completed_scope
evidence
unknowns
risks
context_delta_proposal
next_action
review_owner
```

Rule:

Conditional success uses `review_status=needs_review` and
`acceptance_state=partially_met`. It must not invent custom completion states
that the router cannot validate.

### Blocker Packet

Enterprise role: escalation with one accountable owner.

Minimum content:

```text
blocker_class
last_safe_state
human_action_required
resume_packet_path
dedupe_key
verification_after_resume
```

Rule:

Blockers stop blind retry. They do not automatically expand authority or
change the task goal.

## Worktree And Release Objects

### Worktree Binding

Enterprise role: branch ownership and change isolation.

CoAgent fields:

```text
binding_id
task_id
conversation_id
worktree_kind
read_scope
write_scope
merge_owner
review_owner
close_owner
conflict_policy
```

Rule:

Worktree identity is not agent identity. A worktree is a file surface, not
authority.

### Integration Packet

Enterprise role: release train and final merge review.

CoAgent fields:

```text
accepted_slices
rejected_slices
merge_order
checks_required
artifact_manifest
rollback_plan
final_review_owner
```

Rule:

DevOps integrates accepted evidence. It does not reinterpret the task goal or
silently accept unreviewed worker output.

## Review And Learning Objects

### Verification Gate

Enterprise role: QA and independent acceptance.

CoAgent dimensions:

- product correctness;
- process correctness;
- evidence completeness;
- context freshness;
- safety compliance;
- integration readiness.

Rule:

Execution success is not acceptance. A command that ran is evidence only after
the gate confirms it covers the claim.

### Knowledge Promotion Record

Enterprise role: standard work update.

Possible destinations:

- architecture decision;
- workflow doc;
- skill;
- hook or preflight;
- doctor check;
- backlog item;
- rejected-idea archive.

Rule:

Promote only behavior-changing knowledge. Do not promote raw chat or broad
research summaries.

### Retrospective Action

Enterprise role: continuous improvement.

Trigger:

- same blocker repeats;
- same packet format fails;
- a review catches a preventable issue;
- a task runs beyond appetite without checkpoint;
- context drift causes rework.

Rule:

Retrospective output must be an explicit system change or a tracked rejected
change. A discussion alone does not close the loop.

## Authority Boundaries

| Action | May approve |
|---|---|
| Change canonical task goal | PMO plus Dispatch record |
| Add a scoped conversation | Dispatch after context/result/close contract exists |
| Add a permanent department | user or approved architecture decision |
| Resume after stale context | Context Memory plus required acknowledgement |
| Continue after auth/license/manual review blocker | PMO or Operator Experience after user action |
| Merge file changes | DevOps after review gate |
| Promote policy into hook/preflight | Safety plus Architecture/Dispatch |

## Anti-Patterns

- More departments are treated as more progress.
- A scoped conversation starts without a context pack.
- A worker changes the canonical goal because it found a better local route.
- A subagent becomes an untracked durable department.
- A worktree becomes the only place where task truth exists.
- Research output is promoted without a problem-to-decision mapping.
- Human intervention is spread across many agents instead of one PMO ask.

## Design Consequence

CoAgent should be designed as an execution operating system:

```text
enterprise management principle
  -> durable CoAgent object
  -> packet/state transition
  -> evidence/review gate
  -> integration or knowledge promotion
```

This keeps the architecture task-first while still using enterprise management
ideas where they add control, quality, and recoverability.
