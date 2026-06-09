# Agent Organization Operating Model

> Use this file as the operational structure for multi-agent work. `AGENTS.md`
> stays policy-level; this file defines departments, responsibilities, records,
> and review gates.

Enterprise-management closure is recorded in
`CoAgent/docs/architecture/technical_enterprise_operating_system_closure.md`. This file
is the operational rulebook that applies that closed baseline.

## 1. Organization Map

```text
MainAgent / GeneralManager
  -> ProjectDepartment / ProjectOwner
  -> DevOpsDepartment / GitIntegrator
  -> ArchitectureCommittee / ArchitectureReviewer
  -> KnowledgeDepartment / KnowledgeManager
  -> CoAgentOps / MetaOps
  -> IncidentReview / IncidentReviewOwner
```

This map lists operating functions, not the final execution topology. The
current MoSim/Codex App execution topology keeps only a small number of visible
durable threads. PMO dispatches directly to them; CoAgentOps handles patrol,
recovery, bounded dispatch, and status reporting rather than acting as a
mandatory middle office.

```text
Main / PMO
CoAgent Ops / Meta-maintenance
Context Maintenance
Open-source Probe / Learning
Release Integration
```

Verification, security, architecture review, incident review, and research are
mandatory gates or services when triggered. They become persistent visible
conversations only when recurring workload justifies the synchronization and
runtime-resource cost.

Default rule: the main agent is the general manager. It owns the objective,
task graph, priority, integration, and final answer. It should not become the
hidden worker for large Git, research, audit, or simulation queues.

Codex App conversations should follow the same organization model. Do not
create one persistent conversation for every small specialty or temporary
task. Start with a small number of department-level conversations. For a long
task, do not assume one conversation is enough: build a scoped task team only
when the task needs sustained technical context, repeated human review, or
parallel substreams such as PX4-log-based parameter identification, UE scene
integration, simulator bring-up, or a broad Git migration.

Important distinction: the functions below are MoSim operating roles, not
standing Codex subagents and not always visible departments. A Codex subagent
may temporarily perform one bounded role slice, but persistent Git, runtime,
review, project management, context maintenance, and meta-ops behavior must be
backed by MoSim-owned task state and event logs.

The reusable project-owned description of that system now lives under
`CoAgent/`. This workflow file remains the operating rulebook; `CoAgent/`
stores the architecture, migration status, and external-reference index that
can later be transplanted into another project.

## 2. Department Responsibilities

The table below is an operating-function catalogue. It is not a mandate to
turn every function into an always-on department conversation.

| Department | Role | Durable Owner | Responsibility | Not Responsible For |
|---|---|---|---|---|
| General Management | `MainAgent` | Current Codex main session | Goal decomposition, priority, owner assignment, integration, user escalation, final decision | Grinding through every worker batch when durable workers can be used |
| CoAgent Ops | `MetaOps` | `MoSim｜CoAgent运维平台` plus patrol/recovery packets | 10-minute patrol, visible-thread recovery, bounded pre-authorized P0 dispatch, PMO state reporting, thread-registry hygiene, and MWORKS activation/window patrol | Replacing PMO for MoSim engineering decisions, defining PMO runtime rules, doing routine docs/skills rewrites, owning crawler/learning queues, or becoming a mandatory dispatch hop |
| Context Maintenance | `ContextMaintainer` | `MoSim｜Codex 上下文维护部` | New-conversation context, project memory index, compact recovery notes, scheduled context refreshes. Former title `MoSim｜文档秘书部` and R-suffixed context-maintenance titles are alias/history only. | Owning all documentation or executing business tasks |
| Project Department | `ProjectOwner` | MoSim queue worker or explicit bounded subagent | One bounded implementation/research/migration stream with workers and evidence | Owning global priorities or cross-stream integration |
| Test Gate | `TestOwner` | Task-local evidence bundle, isolated subagent, or explicitly scoped test thread | Independent verification across code, docs, Git, simulation, and reproducibility when a task reaches an acceptance gate | Acting as an always-on department that competes for ROS topics, ports, GUI/MCP sessions, or worktrees |
| Security Gate | `SecurityOfficer` | `AGENTS.md`, prompts, harnesses, preflight checks, and review gates | Path boundary, secrets, destructive operations, large files, license/copyright, unsafe GUI/MCP actions | General code quality, product decisions, or a separate standing department |
| DevOps Department | `GitIntegrator` | MoSim Git queue with explicit locks/hooks | Branch hygiene, add/commit/push, large-file/LFS gates, release checkpoints | Feature implementation or architecture approval |
| Architecture Committee | `ArchitectureReviewer` | Durable review task plus optional Codex one-shot review | Module boundaries, MWORKS/UE5/Sysblock integration choices, long-term design risks | Day-to-day execution |
| Knowledge Department | `KnowledgeManager` | Recurring durable audit task | External Docs/skills/repo learning, source-to-doc coverage, rejected patterns | Importing full external runtimes without approval |
| Incident Review | `IncidentReviewOwner` | Durable postmortem task | Postmortems for Git failures, MCP crashes, lost agents, repeated mistakes | Blame assignment |

## 2.1 Codex App Operating Threads

Use this conversation structure as the current visible routing surface for the
MoSim technical mainline. This is intentionally smaller than the older CoAgent
company model: PMO dispatches directly to the few durable specialty threads
that need long context, and treats the remaining functions as on-demand roles or
one-shot review packets.

| Thread | Department | Includes |
|---|---|---|
| `MoSim｜主线 PMO` | General Management / PMO | User dialogue, task intake, packet dispatch, result integration, final decisions |
| `MoSim｜UE实验控制台与场景交互部-R1` | UE Experiment Console And Scene Interaction | Primary UE route for RflySim-like UE operator console, scene/map switching, command/echo schema, render-review surfaces, build gates, and authorized runtime-review work |
| `MoSim｜UE实验控制台与场景交互部-R2` | UE Auxiliary Source/Static Backup | Auxiliary source/static review, implementation-surface backup, UI/command/echo contract review, source-only fixture/checker work, and bounded parallel support by explicit PMO/CoAgentOps packet |
| `MoSim｜Sunray150资产与PBR审核部` | Sunray150 Asset And PBR Review | DAE/Blender/UE visual asset, PBR materials, component close-up review, UE import readiness |
| `MoSim｜MWORKS动力学与控制验证部` | MWORKS Dynamics And Control Verification | Sysplorer/Sysblock/Syslab, dynamics/controller wrappers, trace consumption, formal simulation evidence |
| `MoSim｜ROS2感知定位与规划运行部` | ROS2 Perception, Localization, And Planning Runtime | ROS2/RViz2/FAST-LIO/local-map/planner runtime, topic/timing/truth-error gates, 20Hz setpoint adapter |
| `MoSim｜Git仓库代码管理部` | DevOps Department | Git hygiene, branches, commits, pushes, LFS/ignore strategy, release checkpoints |
| `MoSim｜微信网关运维部-R3-已删除` | Deleted historical gateway route | Archived by the user on 2026-06-07 after email-only notification switch, then deleted on 2026-06-08; no periodic self-check, no no-op/recovery, and no active dispatch unless explicitly restored with a new scoped route |

Optional/on-demand roles:

| Role | Use when |
|---|---|
| Validation / Evidence Review | A stage claims pass/completion and needs independent evidence review before PMO accepts it; default to bounded subagents or task-local isolated checks |
| Toolchain/MCP upkeep | MWORKS/UE/WindowsMCP/ROS2 MCP setup or health breaks; owned by the thread using the tool, or by `MoSim｜CoAgent运维平台` only when the issue is patrol/recovery infrastructure |
| Context Memory Update | A new long conversation needs a compact context pack or old-session recovery; route to `MoSim｜Codex 上下文维护部` |
| Security / Compliance Gate | External paths, secrets, destructive actions, licenses, or large-file release gates are involved; enforce through prompts, harnesses, preflight checks, and review records |
| External Intelligence | A concrete task needs fresh RflySim/Gazebo/PX4/model-vendor/open-source research |

Documentation ownership rule: `MoSim｜Codex 上下文维护部` is the current
documentation-secretary/context-maintenance route for scheduled context,
memory/index drift, and consistency tasks. Former `MoSim｜文档秘书部`,
R-suffixed context-maintenance titles, and `MoSim｜知识秘书` wording are history
only. Each responsible thread must still update the relevant project docs,
indexes, workflow notes, or result packets before claiming completion.
PMO may request an extra docs-quality review for high-impact rule changes, but
that review is a task, not a standing owner of all documentation.
MCP/skills/workflow ownership follows the same rule: the task thread that
discovers a reusable command, failure mode, recovery path, or operating
constraint must update the relevant workflow/skill doc immediately. For
documentation consistency or context cleanup, route the support task to
`MoSim｜Codex 上下文维护部`; route to `MoSim｜CoAgent运维平台` only for patrol/recovery
infrastructure, thread-registry hygiene, or bounded ops workflow issues.

CoAgent/meta-task routing:

| Thread | ID | Responsibility |
|---|---|---|
| `MoSim｜Codex 环境迁移部-旧` | `019e8181-6653-73b3-9685-f5bc9a24b947` | Historical Windows-native Codex environment migration, WSL bridge-residue audits, Codex config/MCP launcher cleanup, and related one-time environment repair history; not dispatchable unless the user explicitly restores it. |
| `MoSim｜Codex 上下文维护部` | `019eab73-c5bc-7740-a6d1-5e0541bdb0c5` | Receives scheduled tasks to update `Docs/Workflows/new_conversation_context.md`, `Docs/Index/project_work_memory_index.md`, memory/index docs, compact recovery notes, documentation consistency checks, and cache-first migration drafts. Legacy internal key: `CodexContextMaintenanceAgent`; former titles include `MoSim｜文档秘书部` and R-suffixed context-maintenance titles. |
| `MoSim｜CoAgent运维平台` | `019e9bc1-ea9f-7102-b41a-4ef9b2308992` | Codex App native coordinator for 10-minute patrol, visible-thread recovery, MWORKS activation/window patrol, bounded pre-authorized P0 dispatch, PMO state reporting, thread-registry hygiene, and ops recovery checklists. It does not replace `MoSim｜主线 PMO` for MoSim engineering work and does not own routine context/docs/skills/crawler-learning queues. |
| `MoSim｜开源项目探针` | `019e9be3-94de-7dc3-b067-92a78b678287` | Periodically checks local reference-project inventory, upstream freshness, metadata completeness, and update candidates. It should return manifests and candidate learning queues, not adoption decisions; broad new crawling belongs to scoped sub-agents or explicit task packets. |
| `MoSim｜开源项目学习部` | `019e9be4-56d0-7981-b71c-a5ded1c7ec76` | Learns crawled projects/vendor articles, compares them with current MoSim/CoAgent needs, and returns adopt/reject proposals with evidence. |

Tooling-asset governance route: plugins, MCP servers, wrappers, project-local
skills, workflow docs, and crawled reference projects are maintained through
`Docs/Workflows/tooling_assets_governance.md`. The task thread owns immediate
updates discovered during its work. `MoSim｜CoAgent运维平台` owns patrol/recovery
infrastructure and thread-registry hygiene, `MoSim｜开源项目探针` owns local reference
inventory and freshness checks, scoped sub-agents own one-shot crawl/fetch
tasks, and `MoSim｜开源项目学习部` owns adopt/reject/reference-only proposals.

Recurring-task rule: if Codex App automation tools are available, schedule the
recurring task against the appropriate visible thread. If automation tools are
not exposed in the current context, `MoSim｜CoAgent运维平台` or PMO must maintain
a recoverable manual schedule/checklist and dispatch task packets when resumed.
Do not claim a timed automation exists until a real automation tool or external
scheduler has been configured and verified.

Thread replacement rule: when a department thread is replaced because an older
conversation lacks reliable Codex App native thread or automation tools, the
replacement is not complete merely because a new thread exists. The old
conversation's reusable decisions and workflows must be landed into the
canonical project documents that future departments actually read. Use a
result packet to list the landing document for each important topic, then mark
the old thread as superseded for user deletion. Backups or chat history are
only evidence sources, not the long-term operating surface.

The older `MoSim｜调度中台` thread is deprecated for ordinary MoSim work. Do not
insert it as a mandatory hop between PMO and departments. CoAgent queue/runtime
tools may still be used as support infrastructure when a task specifically
needs durable queue state, packet generation, visibility diagnosis, result
import, or evidence validation.

Current project-registered visible department thread IDs live in
`CoAgent/dispatch/department_threads.json` and
`Docs/Index/codex_app_session_research.md#department-thread-layout`. Dispatch
uses an allowlist-only rule: only IDs registered as `active_visible` in the
current registry are valid targets. If an old thread ID is absent from the
current visible scan, treat it as gone and remove it from dispatchable registry
instead of maintaining a separate blacklist. Future context-memory and
documentation-secretary work routes to `MoSim｜Codex 上下文维护部`
(`019eab73-c5bc-7740-a6d1-5e0541bdb0c5`).

Dead-thread rule: `Docs/Workflows/coagent_ops_patrol_workflow.md` is the only
execution source for visible-thread recovery. If a visible department can be
read but cannot reliably receive work, expose native tools, run automations, or
keep a healthy agent loop, stop business dispatch and follow that workflow's
bounded diagnosis/restart-recovery sequence. Do not create/select a replacement
thread merely because the first start-turn failed. Replacement requires
explicit PMO/user approval, repeated failed restart recovery, or a critical
path that cannot wait. Reusable historical content must still be landed into
canonical project documents or the session-memory migration flow before any
old thread is marked superseded for user deletion.

Do not create separate long-lived App conversations for every narrow role such
as `McpSkillsMaintainer`, `UEScenePipeline`, or `ParameterEstimator` by default.
Those are roles or tasks inside a department.

Dedicated long-running task teams are the preferred execution topology for
large objectives. They are allowed when all conditions hold:

```text
the task will span many turns or manual reviews
the task needs stable technical context not suitable for one-shot subagents
the task has a parent department and task_id
the conversation has a stop condition and result-packet contract
PMO or CoAgent ops records it in a recoverable ledger/status packet
```

Examples:

| Task Team | Parent Department | Use Case |
|---|---|---|
| `MoSim｜专项｜Sunray150 参数识别` | Project Department | Can contain separate conversations for log audit, estimator implementation, MWORKS parameter mapping, and verification |
| `MoSim｜专项｜UE Fab 场景导入` | Project Department | Can contain separate conversations for source acceptance, truth export, scene integration, and verification |
| `MoSim｜专项｜AirSim 批量迁移 Git` | DevOps Department | Can contain separate conversations for path-group batches, Git review, and integration |

Split rule:

```text
primary conversation
  -> PMO/CoAgent ops ledger or status packet when durable state is needed
  -> department conversation for normal work
  -> task team only for long-running high-context work
    -> one or more scoped task conversations
  -> one-shot subagent only for bounded research/review/execution slices
```

When a new department thread is created, record its name, role, scope, and stop
condition in this file or `PROGRESS.md`. When a task team is created, record
the parent governance owner or sponsor, canonical task id, member
conversations, shared context path, worktree bindings, write scopes,
acceptance gates, and expected result packets.

## 2.2 Task Ticket And Status Ownership

The current default is PMO direct dispatch. There is no required dispatch-center
conversation between PMO and durable departments. PMO's current operating
surface is `Docs/Workflows/mainline_operations_board.md`. Durable historical
task records remain in result/blocker packets, recovery packets, event logs,
and `Docs/Workflows/agent_task_ledger.md`. CoAgent ops may own recurring
meta-task schedules, patrol/recovery state, bounded dispatch, and
thread-registry maintenance, but PMO owns product priority, dispatch,
acceptance, integration, and recovery decisions.

Required status-board fields:

```text
task_id:
parent_goal:
department:
owner_conversation:
task_conversation:
state: planned | ready | running | waiting_user | blocked | review | done | superseded
read_scope:
write_scope:
dependencies:
next_action:
human_needed:
last_checkpoint:
evidence:
review_status:
git_status:
```

Routing rules:

```text
Git work:
  MainAgent defines scope -> DevOpsDepartment executes batches ->
  task-local test/security gates run as needed -> MainAgent reports.

Documentation work:
  Responsible thread records the stable decision -> patches docs immediately ->
  optional bounded DocsQualityTest reviews high-impact changes -> MainAgent reports.

Long technical research:
  MainAgent defines objective -> PMO creates task-team packet if needed ->
  ProjectDepartment or durable specialty thread opens scoped conversations ->
  result packets and review notes return to MainAgent for integration.
```

The main agent may perform small direct edits in the current turn when that is
the fastest safe path, but it must not become the default worker for long Git,
runtime bring-up, research, or documentation queues.

## 3. Documentation Ownership Rule

`MoSim｜Codex 上下文维护部` is the current documentation-secretary/context-maintenance
route. It owns context maintenance, documentation consistency review,
cache-first migration drafts, and periodic cleanup. It does not define PMO
runtime rules, product priority, dispatch order, engineering acceptance, or
thread recovery decisions. Those remain PMO responsibilities, with
CoAgentOps owning patrol/recovery execution only within
`Docs/Workflows/coagent_ops_patrol_workflow.md`.

The thread doing the work must still ensure user instructions and work records
are not chat-only state. Documentation secretary review is a support lane, not
a substitute for the responsible thread's immediate doc/packet updates.

For every new user directive, correction, manual-review result, sub-agent
return, blocker, or work checkpoint, record at least one recoverable artifact:

```text
short-lived intake:
  Results/tmp/task_intake/<date>_*.md

current PMO operating board:
  Docs/Workflows/mainline_operations_board.md

historical/recovery task state:
  Docs/Workflows/agent_task_ledger.md

current project status and repeated mistakes:
  PROGRESS.md

multi-turn or multi-agent event stream:
  Results/agent_runs/<run_id>/events.jsonl
```

Promotion rule:

```text
chat/user instruction
  -> responsible-thread intake
  -> PMO board for current operations when it affects dispatch
  -> task ledger / PROGRESS / packets when stable or historical
  -> workflow/skill/doc update when it becomes a reusable rule
```

Do not rely on memory, active sub-agent nicknames, IDE tabs, or transient chat
history as the only record of work.

Documentation ownership checklist:

```text
[ ] New user directive captured.
[ ] Stable decision or correction promoted to the right doc.
[ ] Owner, scope, stop condition, and next action mirrored from the Dispatch Center when needed.
[ ] Sub-agent returns consumed or queued.
[ ] Manual-review decisions recorded.
[ ] Blockers and required user actions recorded.
[ ] Stable rules promoted to Docs/workflows.
[ ] Docs update received a second review when important.
```

When several independent documentation reviews are needed, PMO or the
responsible thread may request parallel read-only reviewer tasks with disjoint
review scopes. PMO or CoAgent ops records and routes those review tasks; the
responsible owner merges the results and records the final documentation
decision.

Sub-agents are not peer-to-peer workers. They do not route instructions or
review findings directly to each other. They also should not be treated as
standing departments. Documentation ownership must be implemented as durable
MoSim state: queue rows, event logs, checkpoints, and human-readable recovery
records. The main agent, responsible durable thread, or future MoSim runtime
dispatcher must distribute instructions, reviewer findings, and next tasks.

## 4. Test Gate Structure

Do not keep an always-on test department by default. Testing is usually a
bounded verification gate owned by the task that needs acceptance. This avoids
multiple durable conversations competing for ROS topics, simulator processes,
ports, GUI/MCP sessions, worktrees, or result directories.

Use separate test lanes when risk is non-trivial:

| Test Lane | Checks |
|---|---|
| `SecurityTest` | Secrets, path boundary, unsafe files, external-path access, license risk |
| `CodeQualityTest` | Style, maintainability, narrow diffs, local patterns |
| `BugRegressionTest` | Reproduction, regression checks, expected behavior |
| `RaceConcurrencyTest` | Parallel agent/Git/process collisions, locks, stale sessions |
| `FlakinessTest` | Repeated or timing-sensitive failures, GUI instability, MCP instability |
| `MaintainabilityTest` | Folder structure, docs consistency, ownership boundaries |
| `SimulationValidationTest` | Model check, simulation evidence, result variables, manual GUI review |
| `ArtifactGitTest` | >100 MB files, generated artifacts, gitlinks, LFS pointers, ignored outputs |
| `DocsQualityTest` | Source-to-doc coverage, stale claims, overlong policy files |
| `PerformanceTest` | Solver/runtime/rendering bottlenecks and practical frame rates |

Testing has veto power over integration when required evidence is missing.

Execution topology for tests:

| Test Scope | Default Executor | Resource Rule |
|---|---|---|
| Small script/doc/git checks | Current task thread | Run locally after implementation and record command/evidence |
| Independent read-only review | One-shot subagent or bounded reviewer | No runtime mutation; return findings/evidence only |
| ROS2/UE/MWORKS runtime checks | Single owning task thread | Claim the runtime resource first; no parallel durable test thread on the same topics/ports/session |
| High-impact acceptance | PMO-created scoped visible test conversation if needed | Explicit read/write scope, resource lock, stop condition, and result packet |

Test dispatch contract:

```text
objective:
evidence needed:
allowed commands:
forbidden mutations:
resource lock:
timeout:
result path:
pass/fail/blocker criteria:
```

## 5. Security Gate Boundary

Security is not a standing visible department in the current operating model.
Security is enforced by written boundaries, prompts, harnesses, preflight
checks, and review gates. When a task may cross a boundary, the task owner must
stop or escalate before acting.

Stop or escalate when work may:

```text
leave C:\Users\HP\Desktop\MoSim without explicit approval
touch secrets, tokens, SSH keys, OAuth files, or browser profiles
force push or rewrite history without explicit approval
commit files above GitHub limits or unmanaged binary bulk
copy unclear third-party assets without license/source notes
open disruptive GUI/MCP sessions without need
delete, reset, or clean broad paths
```

Security findings should be short, factual, and action-oriented.

## 6. Required Flow For Non-Trivial Tasks

```text
1. PMO or CoAgent ops creates or updates a recoverable task record when needed.
2. The responsible thread records the directive/correction when it changes
   durable project knowledge.
3. MainAgent builds or confirms the task graph before executing.
4. MainAgent assigns ProjectOwner/GitIntegrator or bounded TestOwner/Security
   gate roles with explicit scopes, not as indefinite Codex subagents.
5. Project owners execute bounded work streams through MoSim queue items or
   one-shot subagent calls.
6. Test and security gates review evidence through durable records when
   triggered.
7. MainAgent routes review findings back to the responsible owner.
8. GitIntegrator commits and pushes safe changes.
9. The responsible thread records completion, blockers, and next actions when
   they affect project memory.
10. MainAgent reports the integrated result.
```

The task graph is not optional. It must name the objective, current state,
critical path, side work, owners, write scopes, verification gates, Git
strategy, and stop conditions. If the task is resumed from a previous session,
the first step is recovering that graph from durable records, not acting from
memory.

If the conversation ends, context compacts, or a sub-agent disappears, resume
from `Docs/Workflows/agent_task_ledger.md`, `PROGRESS.md`, and any
`Results/agent_runs/*/events.jsonl` records.

## 7. Role Prompt Contract

Every delegated task should include:

```text
role:
objective:
read scope:
write set:
forbidden actions:
acceptance criteria:
evidence required:
checkpoint cadence:
stop condition:
handoff format:
```

Use stable role names such as `ContextMaintainer`, `MetaOps`, `GitIntegrator`,
`SecurityGate`, `TestOwner`, `ArchitectureReviewer`, and `KnowledgeManager`.
Avoid arbitrary nicknames that make active work hard to audit.

## 8. Completion Criteria

A task is complete only when:

```text
work product exists
required evidence exists
review gate passed or risk is explicitly accepted
Git state is known
the responsible thread has recorded final state
next action is clear or unnecessary
```

For documentation and workflow changes, completion also requires:

```text
source reason recorded
entry point/index updated when needed
AGENTS.md kept policy-level
PROGRESS.md updated only with active status or repeated mistakes
git diff --check passed for changed docs
```
