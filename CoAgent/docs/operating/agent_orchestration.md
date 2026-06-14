# Agent Orchestration Workflow

> Portable CoAgent workflow for planning, dispatching, checkpointing,
> reviewing, and resuming non-trivial agent work.

Status: split-audited portable core, 2026-06-10 CST.

Host-specific product priorities, visible-thread names, route ids, domain
evidence gates, restart tools, notification channels, and long Git/import
examples belong in host adapters. For MoSim, use
`Docs/Workflows/agent_orchestration.md`,
`Docs/Workflows/mosim_visible_dispatch_adapter.md`,
`Docs/Workflows/coagent_ops_patrol_workflow.md`, and
`CoAgent/dispatch/department_threads.json`.

## 0. Canonical Protocol

Use the vocabulary in `CoAgent/protocol/README.md` unless a task packet
explicitly documents a temporary runtime alias.

Canonical interaction classes:

```text
simple_message
durable_task
long_running_task
checkpoint
result
```

Canonical task-intake classes:

```text
simple_message
clear_task
complicated_task
complex_task
chaotic_incident
disordered_task
long_running_task
```

Canonical states:

```text
planned
ready
working
input_required
auth_required
review_required
blocked
failed
completed
canceled
rejected
superseded
```

Goal hierarchy:

```text
Project Goal -> Canonical Task Goal -> Conversation Objective -> Subagent Objective
```

Task/worktree/review surface selection is defined in
`CoAgent/docs/architecture/coagent_task_surface_model.md`. Review acceptance,
merge ownership, and worktree closeout are defined in
`CoAgent/docs/architecture/coagent_review_merge_protocol.md`.

## 1. Native Surface Gate

Choose the smallest sufficient surface before adding CoAgent runtime machinery:

| Need | Preferred Surface |
|---|---|
| mechanical guardrail | hook plus checker/preflight |
| durable project rule | entry document |
| task procedure | workflow or skill |
| live external tool or GUI operation | MCP/app/plugin or host desktop surface |
| durable specialty context | visible thread |
| bounded parallel research/review/execution | short-lived sub-agent |
| independent write stream | visible thread or task conversation with isolated worktree when practical |
| code-review gate | native review or scoped review sub-agent |
| clear background one-shot | non-interactive exec surface |
| recurring check/reminder | verified automation or wakeup |
| project-specific return/evidence glue | CoAgent packet, ledger, result import, or doctor helper |

For every non-trivial dispatch, record the selected surface, rejected
alternatives when relevant, worktree decision, and expected return/blocker path
before dispatch.

CoAgent runtime, transport, automation, queue, schema, permanent department, or
broad hook changes require the relevant status/decision gate. Do not infer
implementation approval from this orchestration workflow.

## 2. Task Graph First

Planning is mandatory before execution for any non-trivial task. Do not spawn
agents, copy large trees, run simulations, start long commands, or begin Git
batches before the plan exists in chat, a task packet, a ledger, or an event
record.

Minimum planning gate:

```text
objective:
current repo / tool state:
native surfaces to use:
critical path:
parallelizable side work:
owners and write scopes:
worktree / thread / sub-agent / exec / review selection:
verification gates:
Git or integration strategy:
stop / ask conditions:
```

For a learn-and-update audit, also declare:

```text
round 1 source slice:
round 1 doc patch target:
round 2 source slice:
round 2 doc patch target:
round 3 source slice:
round 3 doc patch target:
do-not-adopt guardrails:
```

Keep the main agent on the critical path. Delegated work should be
independent, material, and narrower than the main task.

## 3. Task Queue

For long tasks, convert the graph into a queue. Chat history is not the work
source.

A ready task must have:

```text
task_id:
task_class:
project_goal:
canonical_task_goal:
conversation_objective:
objective:
read_scope:
write_set:
owner_role:
accountable_owner:
dependencies:
acceptance_check:
definition_of_done:
non_goals:
required_evidence:
reviewer_role:
appetite:
circuit_breaker:
checkpoint_plan:
escalation_conditions:
next_task_on_success:
next_task_on_blocker:
```

An owner may continue taking the next ready task in its assigned queue without
waiting for a new user message only when the next task is inside the same
approved write set and does not require new approval.

Stop when the next task:

- changes write ownership;
- touches external or private paths;
- requires GUI/login/license/manual-review action;
- requires destructive Git/history operations;
- lacks required evidence or return paths.

## 4. Durable Start And Dispatch SLO

Every non-trivial visible-thread or long-running dispatch must declare a first
durable-start artifact unless it is an exact no-write probe.

The first durable-start artifact should usually be one of:

```text
checkpoint packet
event log line
claimed task ticket
created output skeleton
initial audit file
status packet
```

If no meaningful progress appears inside the host's dispatch SLO window, classify
the surface before recovery:

```text
approval/review/provider pending
context-compression or view-refresh surface
dispatch surface / agent-loop failure
unknown blocked
```

Elapsed time alone is not proof of failure. Evidence may include agent output,
tool activity, file changes, a checkpoint, an expected packet, or a documented
pending UI/provider state.

## 5. Cross-Thread Packet Contract

Visible-thread work must carry enough scope for the receiver to act without
guessing.

Minimum fields:

```text
read_scope:
write_scope:
native_surface_gate:
semantic_boundary:
expected_return_path:
blocker_return_path:
evidence_minimum:
allowed_actions:
forbidden_actions:
stop_triggers:
expected_engineering_outputs:
next_owner:
```

Non-trivial task packets must also include:

```text
local_goal:
critical_path:
parallelizable_slices:
verification_gates:
subagent_plan:
durable_start_requirement:
```

`subagent_plan` is a planning decision, not a requirement to spawn an agent.
Allowed values:

```text
used
available_but_not_useful
unavailable
unsafe
```

The return channel is a durable packet or declared artifact path. The thread
transcript is useful evidence, but it is not the only return channel.

## 6. Delegation Rules

Use visible threads for durable role context and recurring follow-up. Use
short-lived sub-agents for bounded, independent slices.

Before delegating, define:

```text
why this is not local critical-path work:
read scope:
write scope:
non-goals:
expected output:
blocker condition:
merge/review owner:
```

Do not use sub-agents as a hidden persistent queue. Do not use visible threads
for disposable work that can be completed by a scoped sub-agent. Do not create
peer-to-peer worker state outside packets, ledgers, or task queues.

Maximum durable nesting:

```text
PMO/main -> visible department or task team -> scoped task conversation -> short-lived subagent
```

## 7. Checkpoints And Resume

Checkpoint cadence is required for long-running work. A checkpoint should state:

```text
task_id:
state:
completed_since_last_checkpoint:
evidence_paths:
open_risks:
next_step:
blockers:
owner:
timestamp:
```

On resume:

1. Re-read the task queue, latest checkpoint, and expected return/blocker path.
2. Confirm the write scope is still valid.
3. Check whether another owner already completed or superseded the task.
4. Continue only from the next ready task.
5. If evidence is missing or stale, return a blocker instead of overclaiming.

## 8. Review And Completion

A task is complete only when its definition of done and evidence minimum are
met. Metadata-only packets cannot complete engineering or runtime work unless
the task itself is metadata-only.

Host projects may require an out-of-band completion notification when a local
visible conversation finishes a delegated task, returns a blocker, or reaches a
review-required terminal state. For MoSim, the default notification channel is
a sparse Chinese email through `Scripts/agent/send_gateway_email_alert.py`.
The email is a user attention signal only: keep it short, do not paste long
paths or raw logs, and keep durable evidence in packets, tickets, leases,
reports, or review artifacts. Do not send email for every ordinary chat reply
or intermediate observation unless the task packet or host workflow requires
it.

Completion packet should include:

```text
task_id:
status:
summary:
artifacts:
evidence:
tests_or_checks:
known_limits:
next_owner:
```

Blocker packet should include:

```text
task_id:
status: blocked
blocking_dependency:
missing_gate:
evidence_seen:
attempted_actions:
safe_next_step:
next_owner:
```

For review, findings lead. Cite files, lines, packets, or artifacts. Summaries
are secondary.

## 9. Evidence Format

Evidence entries should be structured:

```json
{"path":"Results/.../artifact.json","source":"tool_or_workflow","sha256":"","bytes":0,"role":"metrics"}
```

Use host-specific source labels only when the host workflow defines their claim
ceiling. Distinguish offline helpers, live runtime evidence, GUI observation,
manual review, and packet-only evidence.

## 10. Git And Release Ownership

Git or release integration requires an explicit owner. For large imports,
multi-batch changes, or unrelated dirty worktrees:

- inspect relevant diffs before editing;
- keep path-limited adds;
- avoid broad reset/clean/force operations unless explicitly approved;
- split large work into reviewable batches;
- record ignore/LFS/large-file decisions;
- keep generated or external source provenance visible.

Host projects may keep detailed long-Git examples in host workflows or ledgers.

## 11. Prompt And Packet Sanity Gate

Before dispatching a prompt or task packet, verify:

- the task has a real objective and definition of done;
- authority and owner boundaries are explicit;
- read/write scopes are narrow;
- allowed and forbidden actions are not contradictory;
- live/manual/destructive actions have approval or stop triggers;
- expected evidence matches the claim;
- result and blocker paths are durable;
- the next owner is clear.

If the packet cannot meet this gate, return a blocker or request for PMO/user
decision instead of sending ambiguous work.

## 12. Documentation Update Rule

When a task changes reusable operating behavior, update the owning workflow,
schema, checker, skill, or index before reporting completion. If the change is
host-specific, patch the host adapter, not the portable CoAgent core.

Do not add repeated dated incident prose to multiple documents. Record the
incident once, then promote only the reusable rule.
