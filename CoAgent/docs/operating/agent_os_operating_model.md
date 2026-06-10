# CoAgent Agent OS Operating Model

> Canonical portable operating model for CoAgent. This document explains the
> small agent OS as a system. Detailed procedures remain in the linked
> operating docs and protocol files.

Status: canonical CoAgent operating entry, 2026-06-10 CST.

## 1. What The Agent OS Is

CoAgent is the reusable operations layer for running a project through multiple
Codex conversations, durable packets, visible department threads, bounded
sub-agents, review gates, and recovery records.

The core rule is:

```text
conversation = working surface
packet = durable communication
event/checkpoint = recovery truth
board = current state
ledger/archive = historical trace
```

CoAgent should be portable. Project-specific facts stay in the host project.
For MoSim, that means MWORKS/ROS2/UE engineering rules, competition priorities,
model evidence, PMO board state, and result artifacts remain in MoSim docs and
`Results/`. CoAgent carries only the reusable coordination machinery and
generic operating rules.

## 2. Core Roles

| Role | Portable Responsibility | Host-Project Responsibility |
|---|---|---|
| PMO / General Manager | Owns objective, priority, acceptance, integration, visible-thread lifecycle decisions, and final user-facing decisions. | Decides the project-specific roadmap and acceptance gates. |
| CoAgentOps / MetaOps | Patrols visible-thread health, dispatch SLOs, recovery, bounded low-risk dispatch, registry hygiene, and notification audits. | Uses host-specific board and packet paths. |
| Department Thread | Owns durable specialty context and executes packeted work inside declared scope. | Produces domain evidence required by the host project. |
| Context Maintenance | Keeps startup context, indexes, cache-first migration notes, and documentation consistency current. | Does not replace task owners or PMO decisions. |
| Review/Test/Security Gates | Verify evidence, safety, contracts, and acceptance risks when triggered. | Use host-specific checks and artifacts. |
| Disposable Sub-Agent | Performs a bounded task-local slice and returns evidence to its parent. | Never becomes hidden durable ownership. |

## 3. Task Lifecycle

```text
user objective or PMO queue
  -> task graph and local goal
  -> packet with read/write scope and native_surface_gate
  -> visible department or bounded sub-agent
  -> checkpoint/result/blocker packet
  -> review/import
  -> PMO accept/reject/integrate
  -> board/ledger/context update when needed
```

Non-trivial department work must include:

```text
department_local_goal
critical_path_steps
parallelizable_slices
subagent_plan
subagent_plan_reason
subagents_used
verification_gates
manual_review_or_blocker_triggers
```

`subagent_plan` is a planning decision, not a requirement to spawn a sub-agent.
Valid choices are `used`, `available_but_not_useful`, `unavailable`, and
`unsafe`.

## 4. Dispatch And SLO Model

PMO normally dispatches directly to visible departments. CoAgentOps may perform
bounded dispatch only when the target is active, routable, low-risk, already in
the current queue/evidence trail, and the packet is complete.

Every visible-thread dispatch needs a dispatch ticket and delivery SLO:

```text
send task
  -> target first writes a durable-start artifact unless this is a no-write probe
  -> immediate readback
  -> second readback if no visible turn
  -> 5-minute meaningful-progress surface check
  -> classify approval/provider/context/refresh before dead-thread recovery
```

Meaningful progress is one of:

```text
agent output
durable-start artifact
checkpoint packet
return packet
blocker packet
approval/provider surface
context-compression surface
explicit requested ACK
```

Native send success alone is not progress.
Routine patrol should not rely on clicking through every thread transcript.
Use native read/send state, expected packet paths, durable-start artifacts, and
main-shell observation for pending approval/review/provider indicators first.
Thread-row clicking is an incident-scoped exception, not the default heartbeat.

## 5. Failover Model

R2 is a safe failover lane when R1 is dead, stale, or blocked and a safe static
or diagnostic task exists. Default R2 classes:

```text
source_static
diagnostic_only
packet_contract_fix
rule_sync_only
checker/review
```

R2 default failover must not run live runtime work, GUI clicks, login or
authorization actions, save/restart actions, or project-specific actuator
commands.

R3 is reserve capacity. PMO proposes or approves it only after R2 failover
still leaves a P0 partition idle or blocked long enough that another safe
static/diagnostic/checker/review lane is useful.

## 6. Patrol And Incident Model

Patrol work should prioritize:

```text
1. abnormal or recovery-pending visible threads
2. idle routable P0 engineering capacity with ready gates
3. open PMO/user dependencies
4. review/audit work
5. support-lane probe, learning, and meta checks
```

Classify UI/provider/review surfaces before dead-thread recovery. Slow or blank
thread views are refresh evidence first, not dead-thread proof. A dead-thread
claim requires native/read/send checks, packet checks, durable-start checks, and
approval/provider/context inspection to fail to find output, ACK, checkpoint,
expected packet, blocker, durable artifact, or a known UI blocker.

## 7. Documentation And Memory Model

Stable rules must be written through to the right durable document. Chat
context is not enough.

Use this promotion path:

```text
chat/user correction
  -> task intake or packet
  -> board if it affects current operations
  -> ledger/archive if historical
  -> workflow/protocol/skill/checker if reusable
```

Historical conversation claims must pass the cache-first migration workflow
before becoming project truth.

## 8. Shared Core, Role Views, And Capabilities

Agent OS boundaries cannot be fully separated by role. PMO, CoAgentOps,
department threads, context maintenance, DevOps, and disposable sub-agents
often share the same facts and tools. The scalable model is:

```text
shared core context
  -> role view and authority
  -> task packet scope
  -> capability/tool selection
  -> evidence or blocker
```

The shared core carries durable vocabulary, packet protocol, evidence rules,
and source-of-truth pointers. Role views are filters over that shared core:
they decide what a role must act on, what it may ignore for the current task,
and who arbitrates conflicts. They are not separate truth stores.

Conflicts are resolved by owner, not by hiding facts:

```text
priority/scope/acceptance conflict -> PMO
dispatch/recovery/SLO conflict -> PMO or CoAgentOps within bounded authority
domain-evidence conflict -> accountable department plus review gate
documentation/index conflict -> context maintenance proposes reviewable patch
tool/safety/path conflict -> hook/checker/schema or safety owner
```

Host projects should maintain a capability index that maps task intent to
native Codex surfaces, visible threads, sub-agents, MCP/tools, skills,
plugins, scripts, hooks, and checkers. For MoSim, the host-local capability
index is `Docs/Index/capability_index.md`.

The capability index is a router, not an authority grant. It answers which
surface should be considered and points to owner docs, health checks, stop
actions, and evidence gates. Permission still comes from the task packet,
workflow, schema/checker, hook, PMO/user approval, or accountable owner.

Use this enforcement split:

| Rule Type | Preferred Landing |
|---|---|
| hard path, secret, destructive, schema, SLO, packet-field, or safety gate | hook, checker, JSON schema, protocol template |
| task procedure, recovery ladder, role view, evidence interpretation | operating workflow or skill |
| host domain evidence and current route names | host adapter, board, domain workflow, skill |
| tool discovery and route selection | capability index and capability cards |
| current task authority | task packet scope, semantic boundary, PMO/user decision |

## 9. Source Map

| Need | Canonical Source |
|---|---|
| Portable operating overview | `CoAgent/docs/operating/agent_os_operating_model.md` |
| Organization and owner boundaries | `CoAgent/docs/operating/org_operating_model.md` |
| Visible-thread packet contract and SLO | `CoAgent/dispatch/communication_contract.md` |
| Patrol/recovery/failover procedure | `CoAgent/docs/operating/coagent_ops_patrol_workflow.md` |
| Full task graph and long-task rules | `CoAgent/docs/operating/agent_orchestration.md` |
| Tooling/native surface governance | `CoAgent/docs/operating/tooling_assets_governance.md` |
| Session-memory anti-pollution | `CoAgent/docs/operating/session_memory_migration.md` |
| Capability routing model | portable capability template `CoAgent/protocol/templates/capability_template.yaml`; host index such as `Docs/Index/capability_index.md` |
| CoAgent implementation status | `CoAgent/STATUS.md` |

Host projects may keep local adapter documents that point here and add
project-specific paths, boards, evidence gates, and domain rules.
