# CoAgent Dynamic Task Team V2 Design

Date: 2026-05-29

Status: design draft for review. This document does not approve runtime
implementation, app-server transport, automatic conversation creation,
automatic worktree creation, unattended automation, plugin installation, hook
rewrites, email sending, or new permanent conversations.

## Purpose

This document turns the previous problem review into a concrete architecture
for dynamic task teams.

The design target is:

```text
stable governance organization
  -> one canonical user task
  -> one temporary task team
  -> multiple scoped Codex conversations when useful
  -> optional short-lived subagents inside each scoped conversation
  -> explicit context, mailbox, worktree, review, and closeout records
```

This is the missing layer between enterprise-style department management and
Codex App / CLI execution.

## Non-Goals

This design does not:

- increase the 11 permanent conversation baseline;
- create new Codex conversations automatically;
- choose app-server transport over CLI/file transport;
- create or merge Git worktrees;
- install plugins;
- rewrite hooks;
- send email or desktop notifications;
- authorize unattended scheduled execution.

Those are implementation decisions gated by later tasks.

## Architecture Principle

CoAgent must separate three things that are easy to confuse:

| Layer | Owns | Does not own |
|---|---|---|
| Department capability | stable responsibility and review boundary | every concrete task |
| Task team | one durable task outcome | permanent organization structure |
| Codex conversation / worktree | one execution slice and file surface | canonical task authority |

The permanent organization should stay stable. The task team should be dynamic.
The conversation and worktree surfaces should be disposable unless they contain
accepted project state.

## Core Objects

Dynamic Task Team V2 adds these first-class design objects.

| Object | Owner | Purpose |
|---|---|---|
| `task_team_charter` | Dispatch | creates a temporary team around one canonical task |
| `shared_task_board` | Dispatch | records team members, states, dependencies, critical path, blockers |
| `team_mailbox` | Dispatch + Knowledge Secretary | durable cross-conversation messages |
| `dynamic_team_policy` | Dispatch + Architecture | decides whether to spawn, reuse, merge, or close conversations |
| `conversation_fork_policy` | Runtime Platform | maps task slices to `thread/start`, `thread/fork`, or ephemeral fork |
| `context_shard_policy` | Context Memory | controls team context, slice context, refresh, compaction, stale context |
| `worktree_binding_policy` | DevOps + Runtime + Safety | binds Git worktree, Codex runtime roots, write scope, and merge owner |
| `integration_plan` | DevOps + task integration owner | defines merge order, conflict strategy, accepted artifacts, closeout |
| `team_trace_eval` | Verification + Flow Analytics | scores team process quality, not only final output |

## Task Intake Flow

When the user gives a task, PMO and Dispatch should process it in this order.

### 1. PMO Intake

PMO records:

```text
user_request
user_visible_goal
why_this_matters
acceptance_criteria
manual_review_points
non_goals
urgency
known constraints
```

PMO must not immediately decide conversation count.

### 2. Dispatch Task Charter

Dispatch turns PMO intake into:

```text
task_id
canonical_task_goal
definition_of_done
owner_department
integration_owner
review_owner
blocked_conditions
stop_conditions
task_topology
```

The canonical task goal is the only source of truth for what must be finished.

### 3. Topology Decision

Dispatch chooses one topology:

| Topology | Use when |
|---|---|
| single conversation | sequential, small, low conflict, enough context fits |
| single conversation + subagents | bounded parallel research/review inside one owner |
| task team, no worktrees | multiple knowledge slices, mostly read-only |
| task team with task worktrees | multiple implementation slices with separate files |
| task team with review worktree | independent verification or code review needed |
| arena comparison | competing approaches with same bounded objective and same eval rubric |
| human-interrupt task | manual login, license, GUI, account, or physical review is expected |

The default is the smallest topology that can finish safely.

### 4. Dynamic Team Creation

A task team is created only when all are true:

- the task is high-context or long-running;
- there is a canonical task goal;
- a context pack can be built;
- slices can be named with clear read/write boundaries;
- there is an integration owner;
- there is a review gate;
- close conditions are known.

If these cannot be stated, creating more conversations is prohibited.

## Dynamic Team Policy

### Spawn Criteria

Create a scoped conversation when one of these is true:

1. The slice requires a distinct context shard.
2. The slice may edit files independently.
3. The slice needs a separate worktree.
4. The slice needs independent review or competing hypothesis testing.
5. The slice may block on a different human/tool/license dependency.
6. The main conversation would exceed the context budget if it kept the slice.

### Do Not Spawn When

Do not create a scoped conversation when:

- ownership is unclear;
- two slices will edit the same files without a merge plan;
- the task is mostly sequential;
- the only reason is to make progress appear parallel;
- no context pack exists;
- no result-packet contract exists;
- nobody owns integration.

### Team Size Rule

Start with the smallest useful team:

```text
1 PMO owner
1 Dispatch owner
1 integration owner
1-3 scoped execution conversations
1 independent review lane if risk requires it
```

Promote beyond that only when the critical path is genuinely parallel.

### Decommission Criteria

A scoped conversation closes when:

- result packet is imported;
- review packet is accepted or waiver is recorded;
- context delta is promoted or explicitly rejected;
- worktree is merged, discarded, or archived;
- no mailbox item requires response;
- final state is recorded on the shared task board.

## Shared Task Board

The task board is the team state source of truth.

Minimum schema:

```yaml
board_id:
team_id:
task_id:
canonical_task_goal:
current_phase:
critical_path_owner:
team_wip_limit:
members:
  - conversation_id:
    owner:
    slice_goal:
    state:
    context_pack_path:
    worktree_binding:
    dependencies:
    next_checkpoint_due:
    close_condition:
open_blockers:
review_gates:
integration_queue:
accepted_artifacts:
context_deltas_pending:
last_dispatch_decision:
```

Rules:

1. A conversation is not part of the team until it appears on the board.
2. A blocked conversation must update `open_blockers`.
3. A finished conversation must move its result into `integration_queue`.
4. The board records state, not long reasoning.
5. Dispatch owns board mutation.

## Team Mailbox

The mailbox is the durable communication channel between scoped conversations.

Minimum schema:

```yaml
mailbox_id:
team_id:
messages:
  - message_id:
    from_owner:
    to_owner:
    message_type:
    task_id:
    related_slice:
    requires_response:
    dedupe_key:
    payload_path:
    created_at:
    expires_at_or_close_condition:
    state:
```

Allowed message types:

```text
context_refresh
interface_change
dependency_ready
blocker
review_request
integration_request
human_action_request
decision_required
```

Forbidden message types:

```text
raw_chat_forward
unscoped_instruction
silent_goal_change
unreviewed_merge_request
```

## Context Model

Dynamic teams require context sharding instead of transcript copying.

### Context Layers

| Layer | Scope | Owner |
|---|---|---|
| project baseline | stable project rules, active architecture, current phase | Knowledge Secretary |
| task shared context | task goal, definitions, accepted facts, non-goals, shared constraints | Context Memory |
| slice context | local objective, read/write scope, dependencies, local evidence | scoped conversation owner |
| subagent context | one bounded source/review/test slice | parent conversation |

### Context Refresh Flow

```text
result packet
  -> Dispatch imports result
  -> Context Memory writes context_delta
  -> affected slices receive context_refresh mailbox item
  -> conversations update local context only after acknowledging refresh
```

### Context Budget Policy

Each new scoped conversation gets:

- one compact project baseline pointer;
- one task shared context pack;
- one slice context;
- links to source files and evidence;
- no raw full transcript unless explicitly approved for an incident review.

If a slice needs more history, Context Memory should build a targeted digest
instead of copying chat logs.

## Conversation Fork Policy

Codex conversation operations map to task-team intent.

| Intent | Codex operation | Requirements |
|---|---|---|
| new independent slice | `thread/start` | task charter, context pack, slice goal |
| context-seeded slice | `thread/fork` | source thread id, filtered context, fork edge record |
| temporary experiment | `thread/fork` with `ephemeral: true` | parent owns cleanup, no durable state claim |
| independent review | detached review thread or scoped review conversation | review request, target diff/artifacts |
| drift recovery | `thread/rollback` or new clean thread | accepted state recorded first |
| context overload | `thread/compact/start` | Context Memory approval and post-compact check |

Edge record:

```yaml
edge_id:
task_id:
team_id:
source_conversation_id:
target_conversation_id:
operation: start | fork | ephemeral_fork | detached_review | rollback | compact
reason:
input_context_pack:
slice_goal:
authority_boundary:
close_condition:
```

## Goal Ownership

Dynamic Task Team V2 uses three goal layers.

| Goal | Owner | Can change by |
|---|---|---|
| canonical task goal | Dispatch, accepted by PMO/user | PMO decision or Dispatch revision record |
| team goal | task-team charter | Dispatch update to team charter |
| thread goal | scoped conversation | local slice update, cannot change canonical goal |

No scoped conversation may reinterpret the canonical task goal. If it detects
goal ambiguity, it must send `decision_required` to Dispatch.

## Worktree And File Surface Policy

Worktree identity is not agent identity.

Minimum worktree binding:

```yaml
binding_id:
task_id:
team_id:
conversation_id:
git_worktree_path:
runtime_workspace_roots:
write_scope:
read_scope:
merge_owner:
review_owner:
close_owner:
conflict_policy:
close_condition:
```

Rules:

1. Read-only research defaults to no worktree.
2. Implementation slices get one task worktree only when write scope is clear.
3. Review lanes use read-only view or review worktree.
4. Integration worktree is for merge and checks only, not new feature work.
5. Subagent worktrees are ephemeral and parent-owned.
6. No worktree merge without result packet and review disposition.

## Review And Integration Flow

Dynamic teams close through review and integration, not by chat completion.

```text
scoped conversation result packet
  -> Dispatch imports
  -> Verification reviews if required
  -> Safety reviews if risk class requires it
  -> DevOps integrates accepted file changes
  -> Knowledge Secretary promotes durable lessons
  -> PMO reports outcome to user
```

Integration plan fields:

```yaml
task_id:
team_id:
accepted_slices:
rejected_slices:
merge_order:
conflict_policy:
checks_required:
artifact_manifest:
rollback_plan:
final_review_owner:
```

## Human Intervention Flow

Manual intervention is a first-class workflow state, not a failure.

Common classes:

```text
auth_required
license_required
gui_required
manual_review_required
data_unavailable
external_service_unavailable
unsafe_action_approval_required
```

Blocker notification must include:

```yaml
task_id:
team_id:
blocked_conversation_id:
blocker_class:
human_action_required:
last_safe_state:
resume_packet_path:
verification_after_resume:
dedupe_key:
notification_policy:
```

Only Operator Experience or PMO should turn this into user-facing text. Many
agents must not independently ask the user for the same manual action.

## Metrics And Drift Control

Dynamic task teams need process metrics, not only final tests.

Minimum metrics:

| Metric | Detects |
|---|---|
| critical_path_time | slowest required path |
| blocked_time | tool/user/license/Git waiting |
| fake_parallelism_count | unnecessary splits |
| serial_collapse_count | all work silently assigned to one lane |
| handoff_failure_count | unclear packet or owner |
| context_pack_size | context bloat |
| context_refresh_latency | stale context |
| rework_count | drift or bad assumptions |
| review_escape_count | issues found after acceptance |
| closeout_latency | finished work not integrated |

If a task team cannot produce these metrics after a proof run, promote or
activate `Flow Analytics / Operating Metrics`.

## Stress Test A: PX4 Log To Simulation Parameters

Recommended team:

```text
PMO: confirm user goal and acceptance
Dispatch: own task charter and board
Context Memory: build log/algorithm/MWORKS context packs
Applied Research slice: papers and open-source parameter-identification methods
Log Audit slice: usable fields, time windows, units, sensor health
Estimator slice: identification code and uncertainty
MWORKS Mapping slice: parameter mapping and constraints
Verification: reproduce estimates and simulation evidence
DevOps: merge accepted code/docs/results
Knowledge Secretary: promote reusable workflow
```

Key design point:

The task is not complete when parameters are estimated. It is complete only
when parameter confidence, non-identifiable parameters, simulation mapping,
verification evidence, residual tuning requirements, and reportable artifacts
are recorded.

## Stress Test B: UE Scene Truth And RflySim-Like Product Line

Recommended team:

```text
PMO: confirm product-facing scenario goal
Dispatch: split scene-truth, MCP/tooling, algorithm integration, UI, verification
Toolchain MCP: UE/Fab/MWORKS/MCP capability cards and blockers
UE Scene Truth slice: occupancy/collision/navigation truth export
Algorithm slice: FastLIO/planning/navigation integration plan
Simulation Platform slice: experiment control, degradation, wind disturbance
Product Strategy: RflySim-like UI scope and non-goals
Verification: path-planning truth and simulation acceptance evidence
Safety: Fab/license/path/large-asset/Git boundaries
DevOps: large asset strategy, worktree, LFS/ignore, merge
```

Key design point:

Rendering is not the acceptance target. Acceptance depends on map truth,
collision/planning validity, reproducible scenario configuration, algorithm
integration, and reviewable evidence.

## Failure Mode Matrix

| Failure | Preventive design |
|---|---|
| task drifts from user intent | canonical goal + PMO acceptance + Dispatch charter |
| conversations cannot see each other | shared task board + mailbox + registry |
| context too long | context shards + compact packs + context delta |
| context too thin | slice context requirements + targeted digest |
| fake parallelism | spawn criteria + team-size cap + metrics |
| serial collapse | critical path owner + board state |
| Git explosion | worktree binding + DevOps integration plan |
| same-file conflicts | write scope + conflict policy before spawn |
| login/license blocks | blocker notification + resume packet |
| unsafe command/tool use | Safety gate + hooks as hard policy |
| review after wrong direction | early review gates + checkpoint cadence |
| accepted work not integrated | integration queue + closeout latency metric |

## Design Extension Backlog

Before runtime implementation, create templates for:

1. `shared_task_board.yaml`
2. `team_mailbox.yaml`
3. `dynamic_team_policy.yaml`
4. `conversation_fork_policy.yaml`
5. `context_shard_policy.yaml`
6. `worktree_binding.yaml`
7. `integration_plan.yaml`
8. `team_trace_eval.yaml`

After templates, run a paper proof against:

1. PX4 log parameter identification;
2. UE scene truth / planning truth export;
3. one Git-heavy rename/import scenario;
4. one manual login/license interruption scenario.

## Acceptance Criteria For This Design

This design is acceptable when:

- it keeps permanent organization stable while allowing dynamic task teams;
- every scoped conversation has owner, context, goal, work surface, and close
  condition;
- cross-conversation communication is mailbox/packet-based, not raw chat;
- context refresh is delta-based;
- worktrees are file isolation surfaces, not authority;
- human interruption has a resume path;
- review and integration are required before closeout;
- metrics can detect fake parallelism, drift, blocked work, and integration
  lag.

## Final Position

CoAgent should evolve as:

```text
small permanent governance core
  + dynamic task teams
  + context-sharded scoped conversations
  + bounded disposable subagents
  + explicit worktree/file-surface isolation
  + mailbox/packet communication
  + measurable review and integration gates
```

This design is the bridge from "large-company operating system" to a practical
Codex-based multi-agent implementation.
