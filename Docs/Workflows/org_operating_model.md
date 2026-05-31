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
  -> DispatchCenter / CoordinationOffice
  -> TaskSecretary / DocumentationOffice
  -> ProjectDepartment / ProjectOwner
  -> TestDepartment / TestOwner
  -> SecurityDepartment / SecurityOfficer
  -> DevOpsDepartment / GitIntegrator
  -> ArchitectureCommittee / ArchitectureReviewer
  -> KnowledgeDepartment / KnowledgeManager
  -> IncidentReview / IncidentReviewOwner
```

This map lists operating functions, not the final execution topology. The
current CoAgent architecture has four persistent governance functions:

```text
Main / PMO
Dispatch Center
Knowledge Secretary
Release Integration
```

Verification, security, architecture review, incident review, and research are
mandatory gates or services when triggered. They become persistent
conversations only when recurring workload justifies the synchronization cost.

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

Important distinction: the departments below are MoSim operating roles, not
standing Codex subagents. A Codex subagent may temporarily perform one bounded
role slice, but persistent secretary, Git, test, security, review, and project
management behavior must be backed by MoSim-owned task state and event logs.

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
| Dispatch Center | `DispatchCenter` | MoSim task queue/status board plus current main session supervision | Task tickets, department status board, dependency routing, cadence checks, task packet generation, result-packet intake | Writing feature code, doing Git batches, silently changing technical scope |
| Documentation Secretary | `TaskSecretary` | Docs/intake records, docs review queue | User directives, decisions, work records, documentation patches, docs second review | Owning the whole task board, implementing features, or supervising all departments alone |
| Project Department | `ProjectOwner` | MoSim queue worker or explicit bounded subagent | One bounded implementation/research/migration stream with workers and evidence | Owning global priorities or cross-stream integration |
| Test Department | `TestOwner` | MoSim test queue and result logs | Independent verification across code, docs, Git, simulation, and reproducibility | Writing the feature being tested |
| Security Department | `SecurityOfficer` | MoSim preflight hooks and audit queue | Path boundary, secrets, destructive operations, large files, license/copyright, unsafe GUI/MCP actions | General code quality or product decisions |
| DevOps Department | `GitIntegrator` | MoSim Git queue with explicit locks/hooks | Branch hygiene, add/commit/push, large-file/LFS gates, release checkpoints | Feature implementation or architecture approval |
| Architecture Committee | `ArchitectureReviewer` | Durable review task plus optional Codex one-shot review | Module boundaries, MWORKS/UE5/Sysblock integration choices, long-term design risks | Day-to-day execution |
| Knowledge Department | `KnowledgeManager` | Recurring durable audit task | External Docs/skills/repo learning, source-to-doc coverage, rejected patterns | Importing full external runtimes without approval |
| Incident Review | `IncidentReviewOwner` | Durable postmortem task | Postmortems for Git failures, MCP crashes, lost agents, repeated mistakes | Blame assignment |

## 2.1 Codex App Operating Threads

Use this conversation structure as the current visible routing surface:

| Thread | Department | Includes |
|---|---|---|
| `MoSim｜主线总控` | General Management | User dialogue, current goal, final decisions, integrated progress report |
| `MoSim｜调度中台` | Dispatch Center | Task tickets, owner assignment, department status board, blocked-task checks, result-packet routing |
| `MoSim｜文档秘书部` | Documentation Secretary | Instruction records, decision logs, docs patches, docs consistency review |
| `MoSim｜研发工程部` | Project Department | UE/Fab scenes, MCP/skills implementation, MWORKS/Sysplorer work, controllers, planners, scene truth, parameter research implementation |
| `MoSim｜验证测试部` | Test Department | Unit/regression/simulation/UE/manual-review evidence gates |
| `MoSim｜安全合规部` | Security Department | Path boundary, secrets, large-file/license checks, destructive-operation review |
| `MoSim｜DevOps 发布部` | DevOps Department | Git hygiene, branches, commits, pushes, LFS/ignore strategy, release checkpoints |

As of 2026-05-26, these seven names are the approved visible operating-thread
set. They are not the architectural ceiling for CoAgent. Do not create
department or dedicated-task conversations by direct Codex App SQLite/JSONL
injection. Create them from the WSL/VSCode Codex side first; Codex App should
only display the synced conversations. Do not use the previous `总经办 PMO` or
`质量安全部` labels.

Current WSL-origin department threads visible in Codex App:

| Thread | ID |
|---|---|
| `MoSim｜调度中台` | `019e62b0-d755-7871-b061-0ea63fa12020` |
| `MoSim｜文档秘书部` | `019e62b1-3333-7870-8e1b-edd0e78f80eb` |
| `MoSim｜研发工程部` | `019e62b1-6806-7b52-88dd-070461772e79` |
| `MoSim｜验证测试部` | `019e62b1-a1d3-74c2-853c-85c510e41f59` |
| `MoSim｜安全合规部` | `019e62b1-d429-7311-8cbe-fbfcaae2f72e` |
| `MoSim｜DevOps 发布部` | `019e62b2-145f-7fc1-9ad1-914f7c1c6666` |

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
the Dispatch Center records it on the status board
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
  -> Dispatch Center ticket/status record
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

## 2.2 Task Ticket And Status Board Ownership

The task ticket mechanism and department status board belong to the Dispatch
Center, not to the Documentation Secretary.

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
  MainAgent defines scope -> DispatchCenter opens/updates ticket ->
  DevOpsDepartment executes batches -> Test/Security review gates -> MainAgent reports.

Documentation work:
  MainAgent or DispatchCenter marks a stable decision -> DocumentationSecretary
  patches docs -> DocsQualityTest reviews -> MainAgent reports.

Long technical research:
  MainAgent defines objective -> DispatchCenter creates task-team packet ->
  ProjectDepartment opens one or more scoped task conversations ->
  result packets and review notes return to MainAgent for integration.
```

The main agent may perform small direct edits in the current turn when that is
the fastest safe path, but it must not become the default worker for long Git,
testing, research, or documentation queues.

## 3. Documentation Secretary Hard Rule

The documentation secretary must ensure user instructions and work records are
not chat-only state. It does not own the whole execution status board.

For every new user directive, correction, manual-review result, sub-agent
return, blocker, or work checkpoint, record at least one recoverable artifact:

```text
short-lived intake:
  Results/tmp/task_intake/<date>_*.md

long-running task state:
  Docs/Workflows/agent_task_ledger.md

current project status and repeated mistakes:
  PROGRESS.md

multi-turn or multi-agent event stream:
  Results/agent_runs/<run_id>/events.jsonl
```

Promotion rule:

```text
chat/user instruction
  -> TaskSecretary intake
  -> task ledger or PROGRESS when stable
  -> workflow/skill/doc update when it becomes a reusable rule
```

Do not rely on memory, active sub-agent nicknames, IDE tabs, or transient chat
history as the only record of work.

Documentation secretary checklist:

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

When several independent documentation reviews are needed, the secretary may
request parallel read-only reviewer tasks with disjoint review scopes. The
Dispatch Center records and routes those review tasks; the secretary merges the
results and records the final documentation decision.

Sub-agents are not peer-to-peer workers. They do not route instructions or
review findings directly to each other. They also should not be treated as
standing departments. The secretary role must be implemented as durable MoSim
state: queue rows, event logs, checkpoints, and human-readable recovery records.
The main agent or a future MoSim runtime dispatcher must distribute
instructions, reviewer findings, and next tasks.

## 4. Test Department Structure

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

## 5. Security Department Boundary

Security is a standing monitor, not just a test suite.

The security officer should stop or escalate when work may:

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
1. DispatchCenter creates or updates the task ticket and status-board record.
2. DocumentationSecretary records the directive/correction when it changes
   durable project knowledge.
3. MainAgent builds or confirms the task graph before executing.
4. MainAgent assigns ProjectOwner/TestOwner/SecurityOfficer/GitIntegrator as
   durable task roles, not as indefinite Codex subagents.
5. Project owners execute bounded work streams through MoSim queue items or
   one-shot subagent calls.
6. Test and security owners review evidence through durable records.
7. MainAgent routes review findings back to the responsible owner.
8. GitIntegrator commits and pushes safe changes.
9. DocumentationSecretary records completion, blockers, and next actions when
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

Use stable role names such as `TaskSecretary`, `GitIntegrator`,
`SecurityOfficer`, `TestOwner`, `ArchitectureReviewer`, and `KnowledgeManager`.
Avoid arbitrary nicknames that make active work hard to audit.

## 8. Completion Criteria

A task is complete only when:

```text
work product exists
required evidence exists
review gate passed or risk is explicitly accepted
Git state is known
TaskSecretary has recorded final state
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
