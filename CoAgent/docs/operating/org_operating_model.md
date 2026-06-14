# Agent Organization Operating Model

Status: portable core, split-audited 2026-06-10 CST.

This file defines reusable organization and role mechanics for a CoAgent-style
agent OS. Host-project visible thread names, concrete thread IDs, product
domains, current boards, and local path rules live in host adapters and the
route registry.

MoSim host adapters:

```text
Docs/Workflows/org_operating_model.md
Docs/Workflows/mosim_visible_dispatch_adapter.md
CoAgent/dispatch/department_threads.json
Docs/Workflows/mainline_operations_board.md
```

The no-loss split is recorded in:

```text
CoAgent/docs/operating/audits/no_loss_split_audit_20260610.md
CoAgent/docs/operating/MIGRATION_MAP.md
```

## 1. Core Model

The organization model is:

```text
Shared Core Context
  -> Role View And Authority
  -> Task Packet Scope
  -> Capability/Tool Selection
  -> Evidence, Review, Or Blocker
```

The model is not hard isolation. Large projects have naturally overlapping
roles. The correct split is:

```text
shared core: objective, current board, constraints, packet protocol, evidence
role view: what this actor is allowed and expected to decide
conflict owner: who resolves priority, acceptance, or authority conflicts
task packet scope: concrete read/write/action boundary for this turn
capability router: which native surface, skill, MCP, script, checker, thread,
  or disposable subagent should be considered
```

Persistent departments are for durable context and repeated ownership.
Disposable subagents are bounded workers or reviewers. A subagent is not a
standing department unless the host creates a durable route and records it in
the registry.

## 2. Reusable Roles

The table below is an operating-function catalogue. It is not a mandate to
create a persistent conversation for every function.

| Role | Durable Owner Pattern | Responsibility | Not Responsible For |
|---|---|---|---|
| `MainAgent` / PMO | Current user-facing main session or host PMO route | Objective, task graph, priority, owner assignment, integration, user escalation, final decision | Grinding through every long worker queue when bounded workers can safely execute |
| `MetaOps` / CoAgentOps | Patrol/recovery route plus packets | Patrol, dispatch-surface recovery, bounded pre-authorized dispatch, registry hygiene, SLO audit, status reporting | Product acceptance, final integration, routine docs rewrite ownership, arbitrary live GUI actions |
| `ContextMaintainer` | Documentation/context-maintenance route or bounded task | New-conversation context, memory/index drift, compact recovery notes, cache-first migration drafts | Owning all documentation, changing product rules, executing business tasks |
| `ProjectOwner` | Department route, task team, or bounded worker | One bounded implementation/research/migration stream with evidence | Global priority or cross-stream integration |
| `TestOwner` | Task-local evidence bundle, isolated review, or explicit test route | Independent verification when an acceptance gate is reached | Competing for scarce runtime resources as an always-on department |
| `SecurityGate` | Entry rules, prompts, hooks, preflight checks, review records | Secrets, path boundaries, destructive operations, unsafe GUI/MCP actions, license/large-file risk | Product priority or general code quality |
| `GitIntegrator` | Host Git queue or explicit lock/task | Branch hygiene, add/commit/push, LFS/ignore gates, release checkpoints | Feature implementation or architecture approval |
| `ArchitectureReviewer` | Durable review task or bounded reviewer | Module boundaries, integration choices, long-term design risks | Day-to-day execution |
| `KnowledgeManager` | Recurring audit or bounded research task | External-source learning, capability/source coverage, rejected-pattern records | Importing external runtimes without approval |
| `IncidentReviewOwner` | Postmortem task and recovery packet | Postmortems for lost work, tool failures, repeated mistakes | Blame assignment |

## 3. Visible Route Registry

The host project owns the visible-route registry. Each dispatchable route must
declare at least:

```text
thread_id or native route id
thread_name
status
department / role key
mission
routing_role
allowed task classes
forbidden actions
paired primary/auxiliary/reserve routes when relevant
history/supersession notes when needed
default model/thinking settings when supported by the native tool
```

Dispatch uses an allowlist-only rule: only routes currently marked
dispatchable by the registry are valid targets. Deleted, archived, historical,
or superseded routes are evidence sources only and must not be no-oped,
patrolled, recovered, or used for dispatch unless the host explicitly restores
a scoped route.

Thread replacement is not complete merely because a new route exists. Reusable
decisions and workflows from the old route must be landed into canonical
documents, packets, or indexes that future routes actually read.

## 4. Department Topology

Start with a small number of durable department-level routes. Do not create
one persistent route for every narrow skill or temporary task. Use persistent
routes only when durable context, repeated human review, scarce native
surface ownership, or long-running coordination justifies the synchronization
cost.

Default topology:

```text
Main / PMO
CoAgentOps / MetaOps
Context Maintenance
Domain Department R1 primary lanes
Domain Department R2 auxiliary/failover lanes when useful
R3 reserve lanes only when approved by the host
Release/Git integration when needed
On-demand review, security, test, architecture, and research roles
```

Dedicated long-running task teams are allowed when:

```text
the task spans many turns or manual reviews
the task needs stable technical context not suitable for one-shot subagents
the task has a parent department and task id
the task has a stop condition and packet contract
PMO or CoAgentOps records it in a recoverable ledger/status packet
```

Split rule:

```text
primary conversation
  -> board/ledger/status packet when durable state is needed
  -> department route for normal durable work
  -> task team only for high-context long-running work
    -> scoped task conversations as needed
  -> disposable subagent only for bounded research/review/execution slices
```

## 5. Task Ticket And Status Ownership

PMO/direct owner dispatch is the default. A separate dispatch-center route is
not required unless the host explicitly creates one for durable queue state,
packet generation, visibility diagnosis, result import, or evidence
validation.

Minimum status-board fields:

```text
task_id
parent_goal
department
owner_route
task_route
state: planned | ready | running | waiting_user | blocked | review | done | superseded
read_scope
write_scope
dependencies
next_action
human_needed
last_checkpoint
evidence
review_status
git_status
```

Durable task records may live in result packets, blockers, recovery packets,
event logs, board rows, or host ledgers. The main agent may perform small
direct edits when that is the safest path, but it must not become the default
hidden worker for long Git, runtime bring-up, research, or documentation
queues.

## 6. Documentation Ownership

Documentation is owned by the responsible work thread first. Context
maintenance is a support function, not a substitute for immediate doc/packet
updates by the actor that discovered a durable rule or result.

Promotion rule:

```text
chat/user instruction
  -> responsible-thread intake or packet
  -> current board when it affects dispatch
  -> ledger/progress/packet when stable or historical
  -> workflow/skill/doc update when reusable
  -> index update when discovery/routing changes
```

Context/documentation-maintenance routes may propose reviewable patches,
deduplicate entries, update indexes, and prepare cache-first migration drafts.
They must not silently change product priority, acceptance decisions, PMO
runtime rules, or engineering facts without the owning role's review.

For high-impact rule changes, request an independent docs-quality review with
a narrow read scope and explicit pass/fail criteria.

## 7. Non-Trivial Task Flow

The task graph is mandatory for non-trivial work. It must name:

```text
objective
current state
critical path
parallelizable side work
owners
read scope
write scope
verification gates
Git strategy when relevant
stop conditions
subagent_plan decision
first durable-start artifact unless exact no-write probe
```

Required flow:

1. PMO/current owner creates or updates recoverable task state when needed.
2. The responsible thread records any directive or correction that changes
   durable project knowledge.
3. MainAgent builds or confirms the task graph.
4. MainAgent assigns durable owners or bounded roles with explicit scopes.
5. Project owners execute bounded work through department routes, task teams,
   or disposable subagents.
6. Test/security/review gates inspect evidence when triggered.
7. Review findings route back to the responsible owner.
8. Git/release integration happens only after evidence and scope are clear.
9. The responsible thread records completion, blockers, and next action when
   they affect project memory.
10. MainAgent reports the integrated result.

If work resumes after context compaction or a missing subagent, recover from
durable board, ledger, packet, and event-log records instead of acting from
memory alone.

## 8. Delegation Contract

Every delegated task should include:

```text
role
objective
read scope
write set
forbidden actions
acceptance criteria
evidence required
checkpoint cadence
stop condition
handoff format
```

Use stable role names such as `ContextMaintainer`, `MetaOps`,
`GitIntegrator`, `SecurityGate`, `TestOwner`, `ArchitectureReviewer`, and
`KnowledgeManager`. Avoid arbitrary nicknames in durable records.

Subagents do not route instructions or review findings directly to each other.
The main owner or durable dispatcher integrates subagent findings and records
final decisions.

## 9. Review And Test Gates

Do not keep always-on test/review departments by default. Testing and review
are usually bounded gates owned by the task that needs acceptance.

Use separate test lanes when risk is non-trivial:

| Test Lane | Checks |
|---|---|
| `SecurityTest` | Secrets, path boundary, unsafe files, external-path access, license risk |
| `CodeQualityTest` | Style, maintainability, narrow diffs, local patterns |
| `BugRegressionTest` | Reproduction, regression checks, expected behavior |
| `RaceConcurrencyTest` | Parallel agent/Git/process collisions, locks, stale sessions |
| `FlakinessTest` | Repeated or timing-sensitive failures, GUI instability, MCP instability |
| `MaintainabilityTest` | Folder structure, docs consistency, ownership boundaries |
| `SimulationValidationTest` | Model check, simulation/runtime evidence, result variables, manual review |
| `ArtifactGitTest` | Large files, generated artifacts, gitlinks, LFS pointers, ignored outputs |
| `DocsQualityTest` | Source-to-doc coverage, stale claims, overlong policy files |
| `PerformanceTest` | Runtime bottlenecks and practical throughput |

Execution topology for tests:

| Test Scope | Default Executor | Resource Rule |
|---|---|---|
| Small script/doc/Git checks | Current task thread | Run locally after implementation and record command/evidence |
| Independent read-only review | Disposable subagent or bounded reviewer | No runtime mutation; return findings/evidence only |
| Runtime or GUI checks | Single owning task thread | Claim the runtime resource first; no parallel durable test thread on the same resource |
| High-impact acceptance | Host-created scoped visible test route if needed | Explicit read/write scope, resource lock, stop condition, result packet |

Testing has veto power when required evidence is missing.

## 10. Security Gate

Security is enforced by written boundaries, prompts, hooks, preflight checks,
and review gates. Escalate before acting when work may:

```text
leave the approved workspace
touch secrets, tokens, SSH keys, OAuth files, or browser profiles
force-push or rewrite history
commit oversized or unmanaged binary bulk
copy unclear third-party assets without license/source notes
open disruptive GUI/MCP sessions without need
delete, reset, clean, or move broad paths
perform live runtime/manual actions outside the packet
```

Security findings should be short, factual, and action-oriented.

## 11. Completion Criteria

A task is complete only when:

```text
work product exists
required evidence exists
review gate passed or residual risk is explicitly accepted
Git state is known when relevant
responsible owner recorded final state when durable memory is affected
next action is clear or unnecessary
```

For documentation and workflow changes, completion also requires:

```text
source reason recorded
entry point or index updated when needed
compact entry files kept policy-level
host progress files updated only for active status or repeated mistakes
diff/format checks passed for changed docs
no-loss migration rows recorded before slimming
```
