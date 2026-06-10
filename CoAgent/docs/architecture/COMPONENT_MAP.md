# CoAgent Component Map

## Purpose

This file maps the CoAgent architecture to the files that currently implement
it in MoSim.

Use this before adding a new department, runtime, or workflow rule.

Current implementation gate:

- read `CoAgent/docs/decisions/coagent_design_discussion_packet.md` first,
- record approval or revision in
  `CoAgent/docs/decisions/coagent_design_decision_record.md`,
- use `CoAgent/docs/decisions/coagent_design_review_brief.md` for the short approval
  brief,
- use `CoAgent/docs/decisions/coagent_design_review_brief.zh.md` as the Chinese
  confirmation entry,
- use `CoAgent/docs/architecture/enterprise_to_agent_mapping.md` before mapping
  enterprise responsibilities into departments, conversations, subagents,
  skills, hooks, memory, or tools,
- use `CoAgent/docs/architecture/coagent_complexity_control.md` before adding durable
  conversations, nested workers, peer communication, transport expansion, or
  automation,
- use `CoAgent/docs/decisions/coagent_goal_readiness_audit.md` before claiming the
  current goal is complete,
- use `CoAgent/docs/decisions/coagent_post_approval_backlog.md` for the approved
  post-approval sequence,
- use `CoAgent/docs/research/THREE_ROUND_STUDY_AND_DISCUSSION.md` for supporting
  evidence,
- the discussion packet checklist is confirmed; `COAGENT-IMPL-01` through
  `COAGENT-IMPL-08` are complete, and the current approved implementation
  stream is `COAGENT-IMPL-LONGRUN-20260531` for project-local runtime,
  task/result, review, notification-packet, checkpoint, status, evidence, and
  recovery work.

## Current Mapping

| Layer | Current implementation | Notes |
|---|---|---|
| Policy | `AGENTS.md` | highest-priority project rules |
| Agent OS operating model | `CoAgent/docs/operating/agent_os_operating_model.md` | portable CoAgent operating overview and source map |
| Organization model | `CoAgent/docs/operating/org_operating_model.md` | department responsibilities and thread model |
| Orchestration workflow | `CoAgent/docs/operating/agent_orchestration.md` | task graph, queue, visible thread routing, runtime contracts |
| Progress memory | `PROGRESS.md` | short current-state recovery file |
| Durable task ledger | `Docs/Workflows/agent_task_ledger.md` | long-running tasks and ownership |
| External learning routing | `Docs/Index/external_learning_index.md` | recurring audit trigger and patch rules |
| CoAgent learning strategy | `CoAgent/docs/research/LEARNING_STRATEGY.md` | audit taxonomy for external projects, official articles, SDK resources, and agent skills |
| Current discussion packet | `CoAgent/docs/decisions/coagent_design_discussion_packet.md` | implementation freeze checklist and design questions for user confirmation |
| Current decision record | `CoAgent/docs/decisions/coagent_design_decision_record.md` | durable pending/approved/revision-required state for the current CoAgent design gate |
| Current review brief | `CoAgent/docs/decisions/coagent_design_review_brief.md` | short approval surface for department boundaries, communication defaults, and first implementation order |
| Current Chinese review brief | `CoAgent/docs/decisions/coagent_design_review_brief.zh.md` | Chinese confirmation surface for the same department and communication decisions |
| Enterprise-to-agent mapping | `CoAgent/docs/architecture/enterprise_to_agent_mapping.md` | maps enterprise concepts to CoAgent goals, departments, conversations, subagents, hooks, skills, memory, and MCP tools |
| Complexity control | `CoAgent/docs/architecture/coagent_complexity_control.md` | version boundaries, goal ownership, nesting limits, context budget, communication control, and expansion rules |
| Agent design protocol | `CoAgent/docs/architecture/coagent_agent_design_protocol.md` | current goal/context/conversation/packet protocol baseline |
| Task surface model | `CoAgent/docs/architecture/coagent_task_surface_model.md` | task surface, worktree, review surface, and closeout design baseline |
| Task team architecture | `CoAgent/docs/architecture/coagent_task_team_architecture.md` | multi-conversation task team, shared context, scoped conversation, and worktree architecture |
| Vendor/framework pattern mapping | `CoAgent/docs/architecture/coagent_vendor_pattern_mapping.md` | maps existing model-vendor and framework multi-agent audits into CoAgent architecture objects and gaps |
| Review / merge protocol | `CoAgent/docs/architecture/coagent_review_merge_protocol.md` | separates review owner, merge owner, close owner, and Git disposition |
| Current readiness audit | `CoAgent/docs/decisions/coagent_goal_readiness_audit.md` | requirement-by-requirement completion audit for the active CoAgent goal |
| Post-approval backlog | `CoAgent/docs/decisions/coagent_post_approval_backlog.md` | frozen first implementation tasks, acceptance gates, and stop conditions after approval |
| Three-round synthesis | `CoAgent/docs/research/THREE_ROUND_STUDY_AND_DISCUSSION.md` | expanded study notes behind the current packet |
| External project master index | `CoAgent/docs/research/REFERENCE_PROJECT_INDEX.md` | stable entry to `References/` |
| Runtime seed | `CoAgent/runtime/mosim_agent_runtime.py` | SQLite task queue, JSONL event stream, conversation edge graph, and event audit |
| Runtime data | `Results/agent_runtime/` | local queue DB and event log |
| Compatibility launcher | `Scripts/agent/mosim_agent_runtime.py` | thin wrapper kept for old workflows |
| Protocol schemas | `CoAgent/protocol/` | task packet and result packet definitions |
| Task bootstrap | `CoAgent/bootstrap/` | creates reusable context, dispatch, handoff, transport-plan, runtime edge, recovery, knowledge-upsert artifacts, and read-only recovery status for long-running task conversations |
| Dispatch helpers | `CoAgent/dispatch/` | department registry, dispatch envelope/text builder, review brief, result packet import |
| Transport adapters | `CoAgent/transport/` | visible conversation delivery interface and `codex_exec_resume` adapter |
| Result router | `CoAgent/result_router/` | validates, review-gates, imports, archives, and summarizes result packets from visible conversations |
| Context packs | `CoAgent/context/` | compact startup packets and measurable quality/budget metrics for dedicated long-running task conversations |
| Memory context | `CoAgent/memory/` | fenced and sanitised project-memory recall with source weights and character budgets, injected only as background evidence |
| Status export | `CoAgent/status_export/` | compact task, active-board, review-queue, doctor, and context-quality bundles for human review |
| Task health | `CoAgent/task_health/` | read-only task health snapshots that combine runtime state, review queue, event audit, and preflight findings into intervention hints |
| Blocker packet | `CoAgent/blocker_packet/` | `blocker_notification` packet generator from task-health continuation decisions; read-only by default, with explicit claim-token metadata recording |
| Evidence manifest | `CoAgent/evidence/` | read-only index of task evidence paths from runtime metadata and known review/status/check artifact folders; separates current recovery staleness from archival/supporting staleness and owns the shared standard refresh-command plan |
| Review package | `CoAgent/review_package/` | read-only human-review package that summarizes task checkpoint, review queue, closeout verification, runtime audit, generated artifacts, and advisory evidence-refresh state |
| Lifecycle proof | `CoAgent/tests/test_lifecycle_smoke.py` | executable proof that task, context pack, dispatch text, conversation edge, result router, summary, and knowledge recovery form one closed loop |
| Hooks / preflight | `CoAgent/hooks/` | CoAgent-owned guardrails and local preflight checks |
| Automation | `CoAgent/automation/` | recurring automation definitions, runtime enqueue helper, execution guardrails, worker lock TTL, and concurrency policy |
| DevOps helpers | `CoAgent/devops/` | read-only Git integration planning, batch splitting, handoff packets, and release hygiene helpers |
| Knowledge | `CoAgent/knowledge/` | project-owned source list, index build, and local search |
| Learning records | `CoAgent/learning/` | bounded architecture audits, source-to-architecture indexer, and adopt/adapt/portable/reject decisions |
| Doctor / health report | `CoAgent/doctor/` | structured CoAgent recoverability report inspired by Codex doctor and Hermes runtime guardrails |
| MWORKS skill layer | `Docs/Skills/Mworks/` | project-local MWORKS skills |
| Unreal skill layer | `Docs/Skills/Unreal/mosim-epic`, `Docs/Skills/Unreal/mosim-unreal` | project-local Unreal/Epic skills and MCP wrappers |
| External agent references | `References/Agent/` | Hermes, Codex, OpenHands, MetaGPT, etc. |
| External agent reference corpus | `References/Agent/`, routed through `Docs/Index/agent_project_classification.md` | runtimes, orchestration, durable workflow, skill/operator systems, safety/eval, context-engineering references |
| Anthropic SDK beta resources | `References/Agent/anthropic-sdk-python/src/anthropic/resources/beta` | agents, sessions, threads, memory stores, skills, environments, vaults, webhooks |
| External simulator references | `References/AirSim/`, `References/RflySim/`, `References/UnrealScenes/` | simulator and scene references |
| Codex user-visible frontends | WSL-backed VSCode Codex, Codex App | VSCode side is primary execution surface; App is visible review surface |

## What CoAgent Does Not Own Yet

These are still missing or partial:

| Capability | Current status |
|---|---|
| durable visible-thread dispatcher | partial; bootstrap now creates durable handoff artifacts and dry-run transport plans; transport still owns live delivery |
| durable task-to-conversation graph | present, first version |
| department-owned long-running worker loop | missing |
| project-owned result packet router | present, first version with conservative review gate |
| project-owned context-pack generator | present, first version |
| richer transport adapter abstraction | present, first version |
| project-owned Codex App conversation bootstrap helper | partial; project-local handoff/transport planning exists, but App thread creation remains manual or transport-driven |
| project-owned automation scheduler | partial; guardrails and worker lock policy now exist before unattended starts |
| searchable CoAgent knowledge cache | partial; memory recall now has a policy/budget layer and generated evidence can be upserted without a full rescan |
| integrated review/test/security queue runtime | missing |
| source-to-architecture audit database | partial, generated from `CoAgent/learning/audits/*.md` |
| project-local doctor report | present, first version |
| compact human-review status export | present, first version |
| task-health/intervention snapshot | present, read-only first version |
| blocker notification packet generator | present, first version with explicit claim-token metadata recording |
| task evidence manifest | present, read-only first version |
| task human-review package | present, includes closeout verification so manual decisions can be checked before resuming |

## Planned Runtime Ownership

Runtime code that belongs to CoAgent should gradually live here, not in generic
script buckets:

| Target area | Intended home |
|---|---|
| queue and task state | `CoAgent/runtime/` |
| task/result packet helpers | `CoAgent/protocol/` |
| task conversation bootstrap | `CoAgent/bootstrap/` |
| dispatch helpers | `CoAgent/dispatch/` |
| transport adapters | `CoAgent/transport/` |
| result packet router | `CoAgent/result_router/` |
| safety hooks | `CoAgent/hooks/` |
| recurring automation | `CoAgent/automation/` |
| Git integration helpers | `CoAgent/devops/` |
| knowledge and indexing utilities | `CoAgent/knowledge/` |
| context-pack generation | `CoAgent/context/` |
| fenced memory/context recall | `CoAgent/memory/` |
| compact status/review export | `CoAgent/status_export/` |
| task-health snapshots | `CoAgent/task_health/` |
| blocker notification packets | `CoAgent/blocker_packet/` |
| evidence manifests | `CoAgent/evidence/` |
| human-review packages | `CoAgent/review_package/` |
| review closeout verification | `CoAgent/review_queue/` |
| architecture-learning audit records | `CoAgent/learning/` |
| doctor and recovery checks | `CoAgent/doctor/` |

`Scripts/` should keep:

- domain scripts,
- checks,
- exporters,
- simulators,
- compatibility launchers,
- repository utility scripts that are not CoAgent-internal runtime logic.

## Immediate Build Order

1. Keep `CoAgent/docs/research/REFERENCE_PROJECT_INDEX.md` complete and validated.
2. Keep `CoAgent/runtime/mosim_agent_runtime.py` as the durable state seed.
3. Add project-owned task-packet / result-packet helpers.
4. Add visible-thread dispatch helpers only after the contract is stable.
5. Add automation and worker loops only after the dispatch path is reliable.
