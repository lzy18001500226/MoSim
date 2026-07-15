# MoSim Agent Protocol

> Legacy/design reference after the 2026-06-24 single-thread reset. Do not use
> this directory as the active MoSim execution entry unless the user explicitly
> reopens durable agent-runtime or visible-thread protocol work.

## Purpose

This directory defines project-owned task coordination payloads and retained
agent-runtime design vocabulary.

In the current MoSim workflow, ordinary work starts from:

```text
AGENTS.md
Docs/Workflows/new_conversation_context.md
Docs/Workflows/mainline_operations_board.md
Docs/Workflows/single_thread_operating_model.md
task-specific Docs/Workflows or Docs/Skills entries
```

The protocol files below are reference material for future or explicitly
reopened durable-agent work. They are not a normal route for current
single-thread engineering execution.

Historically, these payloads bridged:

- the main conversation,
- visible department conversations,
- runtime queue state,
- future dispatch helpers,
- result ingestion and review.

## Retained Components

| File | Purpose |
|---|---|
| `conversation_protocol.md` | V1 conversation roles, creation criteria, lifecycle, and authority |
| `task_packet_schema.json` | normalized task packet shape |
| `result_packet_schema.json` | normalized result packet shape |
| `templates/task_charter.yaml` | design-time template for a durable task charter |
| `templates/context_pack.yaml` | design-time template for bounded scoped-conversation context |
| `templates/scoped_conversation_packet.yaml` | design-time template for creating or instructing a scoped task conversation |
| `templates/blocker_notification.yaml` | design-time template for human intervention or blocker escalation |
| `templates/review_packet.yaml` | design-time template for acceptance/rework/integration review |
| `templates/shared_task_board.yaml` | Dynamic Task Team V2 board template |
| `templates/team_mailbox.yaml` | Dynamic Task Team V2 cross-conversation mailbox template |
| `templates/dynamic_team_policy.yaml` | spawn/reuse/close policy template for dynamic task teams |
| `templates/conversation_fork_policy.yaml` | thread start/fork/rollback/compact edge record template |
| `templates/context_shard_policy.yaml` | project/task/slice/subagent context sharding policy template |
| `templates/worktree_binding.yaml` | worktree/runtime-root/write-scope binding template |
| `templates/integration_plan.yaml` | accepted slices, checks, merge order, rollback, and closeout template |
| `templates/team_trace_eval.yaml` | process-quality metrics template for task teams |

The template files are not current runtime schemas. They are a controlled
landing surface for the problem-to-solution design baseline in
`Docs/Cache/agent_legacy/coagent_deprecation_selection_review_20260624.md` and the Dynamic Task
Team V2 baseline in
`Docs/Cache/agent_legacy/coagent_deprecation_selection_review_20260624.md`.

## Canonical Vocabulary

`MOSIM-AGENT-IMPL-01` froze the V1 protocol vocabulary below. Runtime code may
keep backward-compatible aliases for historical artifacts, but new current
MoSim work should not create protocol packets unless the task explicitly
targets this legacy/design layer.

### Interaction Classes

| Class | Meaning | Durable state required |
|---|---|---|
| `simple_message` | A direct answer or clarification that does not create project state. | no |
| `durable_task` | Work that must be recoverable after chat/context loss. | yes |
| `long_running_task` | A durable task that needs multiple checkpoints, manual review, or a dedicated visible conversation. | yes |
| `checkpoint` | A recoverable progress/event update for an existing task. | yes |
| `result` | A task outcome packet returned for review/import. | yes |

### Task Intake Classes

| Class | Routing rule |
|---|---|
| `simple_message` | Reply in the current conversation; no task packet. |
| `clear_task` | Execute directly after a short plan if scope and acceptance are obvious. |
| `complicated_task` | Split into ordered steps with targeted checks. |
| `complex_task` | Start with discovery, assumptions, options, and user-facing decision points before implementation. |
| `chaotic_incident` | Stabilize first: capture symptoms, freeze risky writes, gather evidence, then decide recovery. |
| `disordered_task` | Normalize into a task packet before execution because ownership, scope, or acceptance is unclear. |
| `long_running_task` | Create a durable task packet with appetite, circuit breaker, checkpoints, escalation, context pack, and result packet. |

### Canonical Task States

| State | Meaning |
|---|---|
| `planned` | Captured but not ready to execute. |
| `ready` | Ready to claim once dependencies and approvals are satisfied. |
| `working` | Actively being handled by an owner. |
| `input_required` | Waiting for user/domain input that cannot be inferred safely. |
| `auth_required` | Waiting for login, token, license, GUI approval, or account action. |
| `review_required` | Work is produced but needs human or reviewer acceptance before closing. |
| `blocked` | Cannot progress without external state change or upstream fix. |
| `failed` | Attempt ended unsuccessfully with evidence. |
| `completed` | Accepted output meets the task acceptance gate. |
| `canceled` | Stopped intentionally before completion. |
| `rejected` | Returned result was not accepted. |
| `superseded` | Replaced by a newer task or decision. |

Current runtime aliases remain accepted during migration:

| Runtime alias | Canonical meaning |
|---|---|
| `queued` | `ready` |
| `claimed`, `running` | `working` |
| `done` | `completed` |
| `done_with_concerns` | `review_required` until accepted |
| `cancelled` | `canceled` |

### Event Vocabulary

Canonical lifecycle events:

| Event | State effect |
|---|---|
| `task_created` | creates `planned` or `ready` task |
| `task_ready` | moves to `ready` |
| `task_claimed` | moves to `working` |
| `heartbeat` | records owner liveness without changing state |
| `checkpoint` | records recoverable progress without closing work |
| `input_requested` | moves to `input_required` |
| `auth_requested` | moves to `auth_required` |
| `review_requested` | moves to `review_required` |
| `task_blocked` | moves to `blocked` |
| `task_failed` | moves to `failed` |
| `task_completed` | moves to `completed` |
| `task_canceled` | moves to `canceled` |
| `task_rejected` | moves to `rejected` |
| `task_superseded` | moves to `superseded` |
| `result_received` | records result packet receipt before acceptance |
| `result_accepted` | accepts imported evidence and closes or advances review |
| `conversation_linked` | links a visible conversation to a task/department |
| `conversation_closed` | closes a task-conversation edge |

Runtime alias `task_cancelled` remains accepted and maps to canonical
`task_canceled`.

### Cancellation Boundary

Agent cancellation is a runtime lifecycle transition, not a Codex UI goal
operation. Use the runtime `cancel` command or a validated result packet with
canonical status `canceled` to stop an internal task intentionally. Keep the
event history and artifacts as a tombstone for audit and recovery.

Do not physically delete task records by default. Physical deletion is allowed
only for test fixtures, duplicate bootstrap artifacts, or explicit
user-approved cleanup. Deleting a Codex thread goal, clearing a visible
conversation goal, or deleting a Codex UI conversation does not cancel a
agent task unless the runtime also records the corresponding terminal event.

Current limitation: automatic Codex goal clearing is not a proven MoSim Agent Protocol
capability. Until a tested command/API path exists, stale Codex thread goals
require manual UI recovery or must be treated as non-authoritative display
state.

### Goal Hierarchy

| Level | Owner | Purpose |
|---|---|---|
| Project Goal | PMO/main conversation | The broad product or project outcome. |
| Canonical Task Goal | DispatchCenter | The stable objective for one durable task, independent of which conversation executes it. |
| Conversation Objective | Department or dedicated task conversation | The scoped objective visible in that conversation. |
| Subagent Objective | Parent owner | A bounded one-shot objective that must return evidence to its parent. |

Rule: workers may narrow execution details, but they must not silently rewrite a
canonical task goal. If the objective is wrong or drifting, return
`review_required` or `blocked` with evidence.

### V1 Complexity Boundary

Maximum durable nesting in V1:

```text
PMO/main -> DispatchCenter -> department or dedicated task conversation -> short-lived subagent
```

Out of scope for V1:

- department-internal durable agent swarms,
- peer-to-peer worker communication as source of truth,
- app-server transport,
- unattended write automation,
- new permanent departments without a repeated queue-pressure record.

## Usage Boundary

Historical runtime tooling supported exporting:

- a task packet from a queued task,
- a human-readable text task packet,
- a result packet from a task plus its latest events,
- a human-readable text result packet,
- a status board snapshot for all tasks.

The old runtime was intentionally local-file based. It is not the current
single-thread operating surface.

Conversation creation and lifecycle rules are defined in
`Config/protocol/conversation_protocol.md`.

Result packets should include `evidence` and `next_recommended_action` for
terminal states. The result router can still import incomplete packets, but it
will mark them `needs_review` or `rejected` so the main conversation does not
treat weak department output as accepted work.

## Required Long-Task Fields

A `long_running_task` packet must carry, directly or through `metadata`:

- `task_class`,
- `project_goal`,
- `canonical_task_goal`,
- `conversation_objective`,
- `accountable_owner`,
- `definition_of_done`,
- `non_goals`,
- `appetite`,
- `circuit_breaker`,
- `checkpoint_plan`,
- `escalation_conditions`,
- `acceptance`,
- `required_evidence`,
- `result_file`.

If any of these are unknown, the task starts as `disordered_task` or
`complex_task`; it should not be assigned as a long-running execution task.
