# Agent Organization Operating Model

> Use this file as the operational structure for multi-agent work. `AGENTS.md`
> stays policy-level; this file defines departments, responsibilities, records,
> and review gates.

## 1. Organization Map

```text
MainAgent / GeneralManager
  -> TaskSecretary / PMO
  -> ProjectDepartment / ProjectOwner
  -> TestDepartment / TestOwner
  -> SecurityDepartment / SecurityOfficer
  -> DevOpsDepartment / GitIntegrator
  -> ArchitectureCommittee / ArchitectureReviewer
  -> KnowledgeDepartment / KnowledgeManager
  -> IncidentReview / IncidentReviewOwner
```

Default rule: the main agent is the general manager. It owns the objective,
task graph, priority, integration, and final answer. It should not become the
hidden worker for large Git, research, audit, or simulation queues.

## 2. Department Responsibilities

| Department | Role | Responsibility | Not Responsible For |
|---|---|---|---|
| General Management | `MainAgent` | Goal decomposition, priority, owner assignment, integration, user escalation, final decision | Grinding through every worker batch when the task can be delegated |
| Secretary / PMO | `TaskSecretary` | Instruction intake, task ledger, work record, status supervision, docs second review | Implementing features or silently changing scope |
| Project Department | `ProjectOwner` | One bounded implementation/research/migration stream with workers and evidence | Owning global priorities or cross-stream integration |
| Test Department | `TestOwner` | Independent verification across code, docs, Git, simulation, and reproducibility | Writing the feature being tested |
| Security Department | `SecurityOfficer` | Path boundary, secrets, destructive operations, large files, license/copyright, unsafe GUI/MCP actions | General code quality or product decisions |
| DevOps Department | `GitIntegrator` | Branch hygiene, add/commit/push, large-file/LFS gates, release checkpoints | Feature implementation or architecture approval |
| Architecture Committee | `ArchitectureReviewer` | Module boundaries, MWORKS/UE5/Sysblock integration choices, long-term design risks | Day-to-day execution |
| Knowledge Department | `KnowledgeManager` | External docs/skills/repo learning, source-to-doc coverage, rejected patterns | Importing full external runtimes without approval |
| Incident Review | `IncidentReviewOwner` | Postmortems for Git failures, MCP crashes, lost agents, repeated mistakes | Blame assignment |

## 3. Secretary / PMO Hard Rule

The secretary department must ensure user instructions and work records are not
chat-only state.

For every new user directive, correction, manual-review result, sub-agent
return, blocker, or work checkpoint, record at least one recoverable artifact:

```text
short-lived intake:
  results/tmp/task_intake/<date>_*.md

long-running task state:
  workflows/agent_task_ledger.md

current project status and repeated mistakes:
  PROGRESS.md

multi-turn or multi-agent event stream:
  results/agent_runs/<run_id>/events.jsonl
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

Secretary checklist:

```text
[ ] New user directive captured.
[ ] Owner, scope, stop condition, and next action recorded.
[ ] Active sub-agents and waiting agents listed.
[ ] Sub-agent returns consumed or queued.
[ ] Manual-review decisions recorded.
[ ] Blockers and required user actions recorded.
[ ] Stable rules promoted to docs/workflows.
[ ] Docs update received a second review when important.
```

When several independent reviews are needed, the secretary may spawn parallel
read-only reviewer agents with disjoint review scopes. The parent secretary
must merge the results and record the final decision.

Sub-agents are not peer-to-peer workers. They do not route instructions or
review findings directly to each other. The secretary must record dependencies,
and the main agent or an explicitly assigned parent owner must distribute
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
leave C:\Users\HP\Desktop\Quadrotor without explicit approval
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
1. TaskSecretary records the instruction and recovery state.
2. MainAgent builds the task graph.
3. MainAgent assigns ProjectOwner/TestOwner/SecurityOfficer/GitIntegrator.
4. Project owners execute bounded work streams.
5. Test and security owners review evidence.
6. MainAgent routes review findings back to the responsible owner.
7. GitIntegrator commits and pushes safe changes.
8. TaskSecretary records completion, blockers, and next actions.
9. MainAgent reports the integrated result.
```

If the conversation ends, context compacts, or a sub-agent disappears, resume
from `workflows/agent_task_ledger.md`, `PROGRESS.md`, and any
`results/agent_runs/*/events.jsonl` records.

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
