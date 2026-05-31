# CoAgent Task Team Architecture V1

Date: 2026-05-28

Status: design baseline. This does not approve runtime, transport,
automatic conversation creation, automatic worktree creation, or unattended
multi-agent execution.

Task id: `COAGENT-DESIGN-10`

## Purpose

This document corrects the previous over-simplified model where a long task
was treated as one specialist conversation or one fixed department lane.

CoAgent's target model is:

```text
one durable task
  -> one task team
  -> multiple scoped task conversations when needed
  -> optional short-lived subagents inside each conversation
  -> optional worktrees for file isolation
  -> packet/state/review records as the source of truth
```

The goal is not to create many permanent departments. The goal is to make one
long task executable by a visible, recoverable, context-managed agent team.

## Architecture Layers

CoAgent V1 separates four layers.

### 1. Governance Core

The governance core is persistent and small. It defines authority, routing,
knowledge, and integration.

| Governance function | Purpose |
|---|---|
| Main / PMO | User dialogue, project direction, final decision, integrated report |
| Dispatch Center | Canonical task goal, task state, owner assignment, routing, packet intake |
| Knowledge Secretary | Shared context, decision memory, learning records, reusable workflow updates |
| Release Integration | Git disposition, merge planning, branch/worktree closeout |

Verification, security, architecture review, incident review, and research are
mandatory functions when triggered. They do not have to be modeled as always-on
departments unless the project has enough recurring load to justify persistent
threads.

### 2. Task Team

A task team is the durable execution container for one long task.

It is created when one task:

- spans many turns or manual reviews,
- contains multiple technical slices,
- needs separate conversations to prevent context mixing,
- needs shared context across those conversations,
- needs isolated file surfaces or review surfaces,
- has one canonical task goal and one integration owner.

A task team is not a department. It is a temporary organization around one
objective.

### 3. Scoped Task Conversations

A scoped task conversation is one visible, durable working conversation inside
a task team.

It owns one slice, for example:

```text
Sunray150 parameter identification
  -> log audit conversation
  -> estimator implementation conversation
  -> MWORKS parameter mapping conversation
  -> verification conversation
```

Each scoped conversation receives a compact slice context and returns
checkpoint/result packets. It does not own the canonical task goal.

### 4. Subagents

Subagents are consumed and released inside one scoped conversation.

They are appropriate for:

- reading a bounded source slice,
- reviewing a limited diff,
- testing one local behavior,
- summarizing one paper or project module,
- generating one candidate implementation patch.

They are not appropriate for durable Git ownership, long review queues,
cross-conversation communication, or task-goal authority.

## Worktree Model

Worktrees are first-class execution-isolation surfaces.

Default rule:

```text
task team may have one integration worktree
each scoped task conversation may have one task worktree
each subagent may use an ephemeral worktree only when the parent conversation
explicitly owns review and cleanup
```

Worktree identity must not become agent identity. A worktree is a file/Git
surface, not the source of task authority.

Required binding:

```text
task_id:
team_id:
conversation_id:
worktree_kind: none | task | review | integration | ephemeral
worktree_path:
write_scope:
review_owner:
merge_owner:
close_owner:
close_condition:
```

### Conversation Worktree

Use for a scoped conversation when:

- it will edit multiple files,
- its diff must be reviewed independently,
- it may run longer than one main-thread turn,
- it may conflict with other task slices,
- DevOps needs a clean merge/discard decision.

### Subagent Ephemeral Worktree

Use only when:

- the subagent performs an experimental patch or isolated repro,
- the parent conversation can summarize and discard or import the result,
- the subagent worktree has a strict lifetime and close condition.

The parent conversation must own cleanup. Ephemeral subagent worktrees must not
become durable backlog items.

### Integration Worktree

Use when DevOps or release integration needs to combine accepted slices from
multiple scoped conversations.

The integration worktree is not a place for new feature work. It is for merge,
conflict resolution, final checks, and release packaging.

## Shared Context Model

Long-task quality depends on controlling context, not copying everything.

CoAgent separates:

### Team-Level Shared Context

This is common to every scoped conversation in the task team.

It includes:

- canonical task goal,
- task charter,
- definitions and terminology,
- confirmed facts,
- non-goals,
- common constraints,
- shared evidence index,
- accepted interface contracts,
- current global decisions,
- open integration risks,
- stop conditions.

### Conversation-Level Slice Context

This is specific to one scoped conversation.

It includes:

- local objective,
- local read scope,
- local write scope,
- local worktree binding,
- local dependencies,
- expected outputs,
- result packet contract,
- escalation rules,
- local stop condition.

### Context Refresh

When one conversation produces a result that affects other slices, it should
not paste the full transcript into every other thread. Instead:

```text
result packet
  -> Dispatch Center imports state
  -> Knowledge Secretary updates shared context delta
  -> affected conversations receive compact context refresh packet
```

## Task Team Charter

A task team must start with a charter:

```text
team_id:
task_id:
canonical_task_goal:
parent_department_or_governance_owner:
integration_owner:
review_owner:
merge_owner:
team_shared_context_path:
member_conversations:
worktree_strategy:
accepted_interfaces:
non_goals:
definition_of_done:
stop_conditions:
human_review_points:
```

No task team is valid without a charter.

## Scoped Conversation Contract

Each scoped conversation must have:

```text
conversation_id:
team_id:
task_id:
slice_name:
slice_objective:
read_scope:
write_scope:
context_pack_path:
worktree_binding:
dependencies:
checkpoint_cadence:
result_packet_path:
review_gate:
local_stop_condition:
forbidden_actions:
```

## Communication Rules

Task-team conversations do not coordinate by unstructured peer chat.

Allowed durable communication units:

- team charter,
- shared context pack,
- slice task packet,
- context refresh packet,
- checkpoint packet,
- result packet,
- review note,
- integration result,
- event log entry.

Forbidden V1 patterns:

- a scoped conversation silently changing the canonical task goal,
- a subagent sending instructions directly to another scoped conversation,
- peer conversations treating chat text as accepted state,
- worktree merge without result/review/Git disposition records,
- context refresh by raw full transcript copy,
- creating more conversations to compensate for unclear ownership.

## Example: Sunray150 Parameter Identification

One task team:

```text
team_id: team-sunray150-param-id
canonical_task_goal: identify and validate simulator parameters from logs and
MWORKS mapping constraints
integration_owner: PMO / Dispatch Center
review_owner: Verification
merge_owner: DevOps
```

Possible scoped conversations:

| Slice | Purpose | Worktree |
|---|---|---|
| Log Audit | Validate usable log windows, sensor fields, timestamps, units | none or read-only review worktree |
| Estimator Implementation | Implement/repair identification code and metrics | task worktree |
| MWORKS Mapping | Map estimated values to model parameters and constraints | task worktree |
| Verification | Reproduce estimates, compare against MWORKS evidence, approve/reject | review worktree |
| Integration | Merge accepted code/docs/results into main project state | integration worktree |

Subagents may be used inside each slice for bounded reviews, but they do not
own the durable task.

## Relationship To Current Department Threads

The current visible Codex App department threads are operational channels.
They are not the final architecture boundary.

They exist because V1 needs stable places to route work, but the main execution
unit for a large objective is the task team. A department can sponsor a task
team; it should not force the whole task into one department conversation.

## Design Decision

CoAgent should be described as:

```text
small governance core
  + elastic task teams
  + scoped task conversations
  + optional short-lived subagents
  + explicit worktree isolation
  + packet/state/review source of truth
```

Not as:

```text
seven permanent departments doing all work
```

The seven current threads are a transport/UI convenience and an operational
starting point. They are not the architectural ceiling.

## Next Design Gate

Before implementation, freeze:

1. the task-team charter schema,
2. the shared-context delta format,
3. conversation/worktree registry fields,
4. review/merge rules for multi-worktree teams,
5. closeout rules for ephemeral subagent worktrees.
