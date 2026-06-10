# Agentic Software Engineering Operating Research Plan

> Draft for user review. This is not yet a canonical workflow, checker, or
> entry policy. It records the current problem analysis, external research
> directions, and a proposed document/write mechanism for building large
> software projects with Codex-style agents.

Status: review draft, 2026-06-10 CST.

Scope:

- Host project: `C:\Users\HP\Desktop\MoSim`
- Write scope of this draft: `CoAgent/docs/research/`
- This draft does not change PMO authority, CoAgentOps authority, visible
  thread lifecycle, automation schedules, or MWORKS/ROS2/UE live state.

## 1. Core Thesis

Using Codex App for a large software project is not the same as using a raw
LLM API, and it is not the same as spawning many disposable subagents.

The useful primitive is:

```text
native tool surface + persistent visible conversation + durable project state
```

The project should treat Codex App as a native engineering workbench:

- native file editing, shell, local app/plugin/MCP/desktop tools;
- visible long-lived conversations with durable history and thread ids;
- cross-thread send/read/steer surfaces;
- app-level goals, settings, approvals, review surfaces, and automations;
- project hooks, skills, plugins, and workflow documents.

Raw API agents can reproduce some of this, but only after reimplementing
tool permissioning, desktop integration, file editing, thread state,
checkpointing, review surfaces, hooks, and project memory. The API route may
eventually be useful as a transport, but it is not a shortcut for the current
MoSim operating problem.

## 2. Terms We Must Keep Separate

| Term | Meaning | What It Is Not |
|---|---|---|
| Visible thread | A long-lived Codex App conversation with durable context, stable id, and dispatch/readback surface. | Not a disposable worker. |
| Disposable subagent | A bounded helper used for one task-local slice, usually context-isolated. | Not a durable department or authority holder. |
| Dispatch | PMO/CoAgentOps sends a scoped task to another visible thread with packet paths and SLO. | Not just chat. |
| Remote steer | A follow-up message sent to a running target thread that can alter or pause the current turn/goal. | Not guaranteed recovery; it requires readback validation. |
| Automation | A scheduled app-level wakeup or prompt. | Not a reliable interrupt when the target thread is busy or wedged. |
| Hook | Enforced lifecycle guard around tool or session events. | Not normal documentation guidance. |
| Workflow | A repeatable human/agent procedure. | Not an entry-file hotfix dump. |
| Skill/plugin | Discoverable capability package with instructions, scripts, tools, examples, or MCP. | Not guaranteed to be invoked unless routing/discovery is explicit. |
| Packet | Durable work/result/blocker/checkpoint communication. | Not a prose summary only. |
| Board | Current operating state for fast decisions. | Not historical ledger. |
| Ledger/archive | Trace-back and recovery history. | Not PMO's daily operating screen. |

## 3. External Research Signals

These are initial observations, not final adoption decisions.

### 3.1 OpenAI Codex / Agents

Observed useful ideas:

- Codex app-server exposes thread, turn, item, status, goal, fork, read, and
  resume primitives for rich interfaces.
- The app-server model supports thread status notifications and turn events,
  which is closer to our desired control plane than raw `codex resume`.
- OpenAI's agent guidance frames agents as model + tools + instructions, with
  guardrails, handoffs, and tool definitions as first-class design concerns.

Implication for MoSim:

- Stay inside Codex App for native tool leverage now.
- Treat app-server as a future transport adapter candidate, not as the
  architecture itself.
- Keep CoAgent protocol independent of the concrete transport:

```text
ThreadAdapter:
  list_threads
  read_thread
  send_message
  start_turn
  interrupt_turn
  read_status
```

### 3.2 Anthropic Claude Code

Observed useful ideas:

- `CLAUDE.md` is project memory/instruction context, not enforcement.
- Hooks are separate lifecycle commands/endpoints/prompts that can enforce or
  react to tool/session events.
- Subagents have explicit scope, model, tools, permissions, memory, hooks, and
  optional worktree isolation.
- Skills use progressive disclosure: the skill body loads when relevant, not
  as permanent global context.
- Skill visibility/triggering has budget and routing issues; descriptions can
  be truncated or too broad.

Implication for MoSim:

- `AGENTS.md` must stay compact because it is context, not a hard runtime
  enforcement layer.
- Enforceable rules belong in hooks/checkers/schema, not repeated prose.
- Subagent use must be explicitly planned, but long-lived work belongs to
  visible threads.
- Skills need a compact capability router, otherwise the model may not load
  the right skill/plugin even when the capability exists.

### 3.3 Google Gemini CLI

Observed useful ideas:

- `GEMINI.md` and `/memory` expose inspectable hierarchical context.
- Extensions package prompts, MCP servers, and commands together.
- Auto-memory experiments propose durable memory and skills from prior
  sessions, with review before activation.

Implication for MoSim:

- We need inspectable loaded-context snapshots by role/thread type.
- We should treat new memories/rules as candidates until reviewed.
- Plugin/skill bundles should not just exist; they need routing metadata and
  health checks.

### 3.4 Anthropic "Building Effective Agents"

Observed useful ideas:

- Start simple; add agentic complexity only when it improves outcomes.
- Distinguish fixed workflows from dynamic agents.
- Common patterns include routing, parallelization, orchestrator-workers, and
  evaluator-optimizer loops.
- Agents need environmental ground truth, checkpoints, stop conditions, and
  human feedback gates.
- Agent-computer interface design matters like human-computer interface design.

Implication for MoSim:

- More threads/subagents are not automatically better.
- The project needs routing, clear stop conditions, evidence gates, and
  checkpoint cadence before adding more automation.
- Tool interfaces and tool docs must be tested, not just written.

### 3.5 LangGraph / Durable Agent Runtimes

Observed useful ideas:

- Long-running agents need durable execution, persistence, state inspection,
  human-in-the-loop, and checkpoint history.
- A thread id plus checkpoints is the unit of recoverable execution state.
- Pending writes/checkpoints allow recovery without rerunning successful
  partial work.

Implication for MoSim:

- Our packet/checkpoint/lease files are the local equivalent of graph
  checkpoints.
- A visible thread that does not write a durable-start artifact cannot be
  distinguished reliably from a wedged turn.
- The thread transcript alone is not enough as recovery truth.

### 3.6 OpenHands / SWE-agent / Aider / Cline / Continue / Hermes / Dify

Observed useful ideas:

- OpenHands: complete agent development platform with CLI, local GUI, REST API,
  SDK, and cloud/enterprise lanes.
- SWE-agent: benchmark-oriented agent harness, config-driven issue fixing,
  trajectories, and evaluation.
- Aider/Cline/Continue: editor/terminal coding surfaces with focused repo
  context and tool use.
- Hermes: long-lived personal agent, gateway, cron, memory, self-improving
  skills, subagent delegation, and multiple backends.
- Dify/n8n/Flowise-style systems: workflow UI, queues, model/tool management,
  and observability.

Implication for MoSim:

- No single project directly replaces Codex App visible-thread orchestration.
- Useful patterns are: durable run state, queues, UI/review surfaces, tool
  routing, memory promotion, evaluation, and task trajectories.

## 4. Current MoSim Failure Modes

### 4.1 Documentation Patch Accretion

Problem:

- User corrections are often written directly into entry docs or workflows as
  hotfix prose.
- Similar constraints get repeated under different names.
- Agents spend time comparing overlapping boundaries instead of executing P0
  work.

Required shift:

```text
incident/correction
  -> candidate note / packet
  -> classification
  -> canonical workflow/schema/checker/skill update
  -> entry-file pointer only
  -> periodic dedup review
```

### 4.2 Context Pollution Across Main Threads

Problem:

- Some constraints are meant for PMO, others for CoAgentOps, others for a
  department, but they get written into a shared entry path.
- A thread reads rules for work it should not perform and becomes over-cautious
  or misroutes tasks.
- Main thread A and main thread B can hold different mental models when one
  received a correction and the other did not.

Correction:

- The boundaries cannot be cleanly split. PMO, CoAgentOps, documentation
  maintenance, DevOps, and engineering departments share the same project and
  often need overlapping context.
- The goal is not "separate everything"; that would create stale local views
  and missed cross-role dependencies.
- The goal is a shared core plus role-specific views and explicit conflict
  arbitration.

Required shift:

```text
shared core context
  -> role view overlay
  -> task packet scope
  -> capability/tool selection
  -> conflict arbitration when role views disagree
```

The shared core contains only durable project facts, hard safety boundaries,
current source-of-truth pointers, and vocabulary. Role views are filters over
the shared core, not separate truth stores.

Every canonical workflow should carry:

```text
document_id
status
updated_at
revision
owner
scope
supersedes
applies_to_roles
shared_core_dependencies
role_view_dependencies
conflict_owner
```

- Task packets should record:

```text
context_revision_seen
workflow_revision_seen
source_of_authority
```

### 4.3 Tool/Skill/Plugin Non-Use

Problem:

- The project has many plugins, skills, MCP tools, and local helper scripts.
- The model often fails to discover or choose the right one unless prompted.
- Broad startup context cannot list every tool in detail without wasting tokens.

Required shift:

- Maintain a compact capability router:

```text
capability: MWORKS live screenshot
when_to_use: MWORKS GUI/window/layout/license review
preferred_surface: Windows MCP / MWORKS scripts / project skill
forbidden_surface: computer-use, ad hoc screenshot unless approved
health_check: script/tool probe
workflow_pointer: ...
```

- Add a planning gate:

```text
Before non-trivial task:
  identify required capability classes
  check capability router
  load only relevant skill/workflow
  record selected/rejected capabilities in task graph or packet
```

### 4.4 Dead Thread Ambiguity

Problem:

- A running visible turn can mean real work, provider wait, permission surface,
  context compression, UI refresh issue, or a wedged/dead thread.
- The PMO may not know the route is dead until a later send/read operation
  fails.
- Automations do not reliably interrupt a busy/wedged thread.
- Cross-thread `send_message_to_thread` can act as remote steer/pause, but
  that can also drift the target's current task if used casually.

Required shift:

- Do not define dead solely by elapsed time.
- Use layered liveness:

```text
L0: native transport/read/send status
L1: visible turn/readback state
L2: durable-start artifact exists
L3: checkpoint/packet/lease heartbeat updates
L4: approval/provider/context-compression/main-shell indicators
L5: remote pause/steer ACK when intervention is required
L6: failover or restart decision
```

- Treat remote steer as an incident-scoped control, not routine polling.

### 4.5 Scheduling Inefficiency

Problem:

- Threads stay idle while PMO is busy reading constraints or support tasks.
- CoAgentOps may report idle/blocked states but not create a PMO action.
- Metrics were added, but metrics alone did not change behavior.

Required shift:

- Board stays small, but each route must be classed as:

```text
busy_with_meaningful_progress
idle_with_ready_task
idle_blocked_by_dependency
waiting_user_or_review
dispatch_surface_failure_suspected
recovery_pending
no_ready_task
```

- Patrol must create either:

```text
dispatch action
PMO decision request
recovery action
explicit no-ready-task reason
```

No "quiet healthy closeout" when P0 lanes are idle and ready work exists.

## 5. Proposed Document Architecture For Large Agent Projects

This is a general model, not just MoSim's current folders.

### 5.1 Entry Layer

Purpose: minimal, stable, loaded often.

Files:

```text
AGENTS.md / CLAUDE.md / GEMINI.md adapter
new_conversation_context.md
workflow_index.md
```

Rules:

- Keep under a strict size target.
- Only hard boundaries, source-of-truth map, read order, and role pointers.
- Do not store every incident or procedure here.

### 5.2 Shared Core And Role-View Layer

Purpose: make cross-role context usable without pretending the roles are
fully separable.

Files:

```text
shared_agent_context.md
role_views/pmo_view.md
role_views/coagentops_view.md
role_views/department_view.md
role_views/context_maintenance_view.md
context_conflict_resolution.md
```

Rules:

- The shared core is the common substrate; it should stay compact and factual.
- Role views are read filters and action filters, not independent policy
  universes.
- A role view states:

```text
what this role must see from shared core
what this role may ignore unless a packet/board says otherwise
what this role may do
what this role must escalate
which role wins if two documents disagree
```

- If PMO and CoAgentOps disagree, PMO owns product priority, dispatch
  acceptance, visible-thread lifecycle, and restart decision. CoAgentOps owns
  patrol evidence, recovery execution, and bounded dispatch evidence. The
  workflow must state the conflict owner instead of duplicating both policies.

### 5.3 Current State Layer

Purpose: fast operation, not history.

Files:

```text
mainline_operations_board.md
dispatch_slo_watchlist.md or board section
route_registry.json
```

Rules:

- Board shows current partition state, waiting items, blockers, next action.
- Details go into dispatch tickets and packets.

### 5.4 Protocol Layer

Purpose: durable communication contract.

Files:

```text
communication_contract.md
task_packet_schema.json
result_packet_schema.json
dispatch_ticket_schema.json
templates/*.json
```

Rules:

- Every non-trivial dispatch records read/write scope, native surface,
  semantic boundary, expected return/blocker, durable-start requirement, and
  stop triggers.
- Ambiguous prose is replaced with enum fields where possible.

### 5.5 Workflow Layer

Purpose: repeatable procedures.

Files:

```text
workflows/dispatch.md
workflows/dead_thread_recovery.md
workflows/document_promotion.md
workflows/tool_skill_routing.md
workflows/domain_specific/*.md
```

Rules:

- Workflows are executable steps, not postmortem essays.
- If a workflow grows incident patches, create a dedup task.

### 5.6 Skill/Tool Layer

Purpose: progressive disclosure of domain/tool procedures.

Files:

```text
skills/<skill>/SKILL.md
capability_router.json
tool_health_checks/*.py
```

Rules:

- Skill descriptions must be precise enough for model routing.
- Capability router maps user intent to skill/tool/plugin/workflow.
- Health checks keep stale tools from being selected silently.

### 5.7 Enforcement Layer

Purpose: hard checks.

Files:

```text
hooks/
quality/check_*.py
schemas/
```

Rules:

- Anything that can be checked should become a checker or schema rule.
- Hooks block dangerous actions; docs guide behavior.

### 5.8 Research And Candidate Memory Layer

Purpose: prevent unreviewed chat facts from becoming project truth.

Files:

```text
research/*.md
memory_candidates/*.md
incident_notes/*.md
```

Rules:

- New ideas land here first.
- Promotion requires review and explicit target document.

### 5.9 Evidence Layer

Purpose: acceptance and recovery truth.

Files:

```text
Results/agent_packets/
Results/agent_packets/dispatch_tickets/
Results/runtime_leases/
Results/review_assets/
Results/logs/
```

Rules:

- Claims need evidence.
- Thread transcript is not enough for acceptance.

## 6. Proposed Documentation Write Mechanism

### 6.1 Four-Stage Promotion

```text
Stage 0: Chat correction or observation
  - Not durable.
  - May guide current turn only.

Stage 1: Candidate note or packet
  - Records exact fact, evidence, affected workflows, and uncertainty.
  - Does not change default behavior yet unless user explicitly says so.

Stage 2: Review patch
  - Moves candidate into one of: entry pointer, workflow, protocol, schema,
    checker, skill, board, or archive.
  - Removes duplicates and superseded wording.

Stage 3: Canonicalization
  - Updates target doc/checker/template.
  - Adds revision metadata.
  - Updates index or router.
  - Adds regression test/checker when possible.
```

### 6.2 Where The Current Remote-Steer Correction Belongs

Observation:

```text
send_message_to_thread can reach a busy visible thread and act like remote
steer/pause when the target execution surface is responsive.
```

Do not put this in `AGENTS.md` as a long rule.

Candidate placement after review:

| Target | Content |
|---|---|
| `CoAgent/dispatch/communication_contract.md` | Dispatch is not only idle-turn delivery; it can also be remote steer. Require readback and classify as transport/steer evidence only. |
| `CoAgent/docs/operating/coagent_ops_patrol_workflow.md` | For risky long-running tasks, try one scoped remote pause/steer before restart when safe, then validate by readback/ACK/durable artifact. |
| `CoAgent/docs/operating/agent_orchestration.md` | Conceptual distinction between visible thread dispatch, remote steer, automation, and disposable subagents. |
| Checker/template | Optional field `intervention_mode: normal_dispatch | remote_steer | pause_request | no_op_probe`. |

### 6.3 Periodic Documentation Cleanup

This is similar to Hermes-style memory/skill evolution, but should be stricter:

```text
incident packets + candidate notes + repeated user corrections
  -> documentation secretary review
  -> deduplicate
  -> propose patch
  -> PMO/user review
  -> canonical update
  -> checker/schema if enforceable
```

The documentation secretary should not invent PMO policy. It should propose
patches, mark duplicates, and identify stale rules. If automation is used, it
should produce reviewable patches rather than silently rewriting entry docs.

## 7. Dead Thread And Liveness Design Options

### 7.1 Current Weakness

The current system can miss a wedged target because:

- "in progress" does not prove work;
- elapsed time does not prove death;
- target-thread automation may not run while the target is busy;
- PMO may be occupied and not retry/readback;
- native send/read failure may only appear when another message is sent.

### 7.2 Recommended Liveness Stack

Every non-trivial dispatch should include:

```json
{
  "request_id": "...",
  "nonce": "...",
  "durable_start_requirement": {
    "path": "Results/runtime_leases/<thread_id>/<request_id>.json",
    "due_at": "...",
    "minimum_fields": [
      "request_id",
      "thread_id",
      "nonce",
      "started_at",
      "last_checkpoint_at",
      "current_phase",
      "next_checkpoint_due_at"
    ]
  }
}
```

The target thread's first action is to create or update the lease/checkpoint.
This does not prove completion. It proves the target started and can write
recoverable state.

### 7.3 Lease State Classes

```text
no_visible_turn
visible_turn_no_durable_start
started_no_checkpoint
checkpoint_fresh
checkpoint_stale
expected_packet_seen
blocker_seen
approval_or_provider_surface
context_compression_surface
remote_pause_ack_seen
dispatch_surface_failure_suspected
```

### 7.4 Watcher Design

No single watcher can be sufficient because it can itself die. Use layered
watching:

| Watcher | What It Can Detect | What It Cannot Detect |
|---|---|---|
| Dispatcher PMO | immediate readback, ticket state, target packet | PMO itself being wedged |
| CoAgentOps patrol | stale tickets, missing leases, idle routes | CoAgentOps itself being wedged |
| Target thread lease | self-progress checkpoints | target death after last checkpoint |
| App/server thread status if available | loaded/active/idle/systemError | business progress |
| User/manual audit | global app confusion | timely detection without alert |

### 7.5 Recovery Ladder

```text
1. Check expected packet/blocker/lease.
2. Check native read/status.
3. Check approval/provider/context-compression surface.
4. If safe, send one remote pause/steer or no-op probe with exact expected ACK.
5. If no ACK/lease/packet after the surface window, classify suspected failure.
6. Fail over to R2/R3 for safe static/diagnostic work.
7. Restart only when all useful failover lanes are exhausted or PMO/user
   approves because app-level state is corrupted.
```

Remote steer is useful, but it must be scoped:

- "pause current goal" is allowed as an emergency brake;
- "continue but also do X" can drift the target task and should be avoided
  during critical execution;
- every remote steer needs readback or durable ACK evidence.

## 8. Scheduling Efficiency Design

### 8.1 What Metrics Alone Miss

Metrics do not dispatch tasks. They only expose failure after the fact.
Scheduling efficiency requires a control loop:

```text
observe state
classify route
choose next action
dispatch or request decision
verify start
watch for progress
integrate or recover
```

### 8.2 PMO Minimal Board

Keep the board small:

```text
partition
state
waiting_return
blocker
human_decision
integrable_result
next_action
forbidden_action
```

Dispatch ticket holds:

```text
target_thread_id
task_type
sent_at
first_readback_due
durable_start_due
checkpoint_due
expected_packet_due
last_observed_turn
lease_path
breach_action
owner
terminal_state
```

### 8.3 Utilization Rule

An active P0 department is unhealthy if:

```text
state = idle_with_ready_task
and PMO/CoAgentOps has no dispatch, decision request, or explicit blocker
```

This should be tracked as `idle_dispatch_debt`, not `healthy`.

### 8.4 R1/R2/R3 Rule

R2/R3 are not replicas of R1. They are failover lanes with default safe task
classes:

```text
source_static
diagnostic_only
checker/review
packet_contract_fix
rule_sync_only
```

R2/R3 become useful when R1's live lane is wedged. They should not wait for
R1 if a safe parallel task exists.

## 9. Tool/Skill/Plugin Awareness Plan

Problem:

```text
Capabilities exist but the model does not call them reliably.
```

Proposed components:

### 9.1 Capability Router

```json
{
  "capability_id": "mworks_window_screenshot",
  "trigger_phrases": ["MWORKS screenshot", "window audit", "activation check"],
  "preferred_surfaces": ["windows-mcp", "project script", "Mworks skill"],
  "forbidden_surfaces": ["computer-use"],
  "skill_paths": ["Docs/Skills/Mworks/mworks-mcp-operations/SKILL.md"],
  "health_checks": ["Scripts/..."],
  "requires_user_or_pmo_approval": false,
  "notes": "activation/login needs maximized/front evidence; normal review can use DPI-aware background capture"
}
```

This should not be a second system separate from current CoAgent capability
cards. It should extend the existing capability-card model:

```text
CoAgent/docs/architecture/coagent_department_capability_model.md
CoAgent/protocol/templates/capability_template.yaml
CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/tool_capability_health_and_fallback_protocol.md
```

Proposed minimum index files:

```text
CoAgent/capabilities/capability_index.json
CoAgent/capabilities/capability_cards/*.yaml
CoAgent/capabilities/tool_health_checks.md
```

The index answers "what exists and when to use it"; capability cards answer
"what this route can safely do right now"; health checks answer "is it still
valid".

### 9.2 Planning Gate

For non-trivial tasks:

```text
1. Identify capability classes.
2. Query capability router/tool search.
3. Load only relevant skills/workflows.
4. Record selected and rejected surfaces.
5. If no capability is available, return blocker instead of ad hoc guessing.
```

### 9.3 Skill Hygiene

Every skill should answer:

```text
when to use
when not to use
required tools
required evidence
first safe check
stop triggers
known failure modes
```

## 10. Human-Agent Interaction Model

The human should not be a manual scheduler for every small step. The human
owns:

- objective and priority;
- acceptance/rejection;
- product direction;
- high-risk GUI/live/runtime authorization;
- ambiguous visual/manual review;
- restart and visible-thread lifecycle decisions when policy requires.

The agent system owns:

- task decomposition;
- capability selection;
- safe dispatch;
- evidence collection;
- checkpointing;
- recovery classification;
- documentation candidate generation;
- low-risk dedup and checker proposals.

The interaction should look like:

```text
human sets objective and constraints
PMO turns objective into queue and packets
departments execute and checkpoint
CoAgentOps watches delivery/recovery
reviewers/checkers validate
PMO integrates or asks for human decision
documentation secretary promotes reusable lessons after review
```

## 11. Proposed Research Tasks For Review

The user approved parallel research for this design pass. Initial read-only
subagent research has covered vendor mechanisms, open-source systems, and the
local CoAgent/MoSim landing surface. These tasks remain useful as durable work
items if PMO later wants deeper packets, source tables, or checker designs.

| ID | Task | Scope | Output |
|---|---|---|---|
| AGENTOS-RESEARCH-01 | Vendor instruction/memory systems | Codex AGENTS/app-server, Claude CLAUDE/hooks/skills/subagents, Gemini GEMINI/extensions/auto-memory | Comparison table: context load, enforcement, skill routing, memory promotion |
| AGENTOS-RESEARCH-02 | Open-source coding-agent platforms | OpenHands, SWE-agent, Aider, Cline, Continue, OpenInterpreter, Hermes | Adopt/adapt/reject map for MoSim visible-thread operating model |
| AGENTOS-RESEARCH-03 | Durable execution and liveness | LangGraph, Temporal, workflow engines, app-server status events | Proposed lease/checkpoint schema and failure classifications |
| AGENTOS-RESEARCH-04 | Tool/skill/plugin routing | Claude skills, Gemini extensions, MCP registries, local Codex skills/plugins | Capability router schema and skill-health checker proposal |
| AGENTOS-RESEARCH-05 | Documentation promotion and dedup | Claude memory guidance, Gemini auto-memory, Hermes memory/skills, current MoSim docs | Document write lifecycle and periodic cleanup workflow |
| AGENTOS-RESEARCH-06 | Dispatch and scheduling control loop | Current board/tickets plus external queue/workflow systems | PMO dispatch algorithm and idle-dispatch-debt metric |
| AGENTOS-RESEARCH-07 | Human review and approval surfaces | Claude hooks/permissions, Codex approvals, current app behavior | Manual-review taxonomy and safe remote-steer policy |

Each task should return:

```text
sources read
findings
adopt/adapt/reject
MoSim impact
candidate doc target
checker/schema opportunity
risks
```

## 12. Initial Parallel Research Synthesis

### 12.1 Vendor Mechanisms

Adopt:

- Codex/Claude/Gemini all treat project instruction files as context, not as
  the only enforcement layer. MoSim should keep `AGENTS.md` compact.
- Hooks and guardrails are the right place for hard safety and packet/schema
  gates.
- Skills use progressive disclosure. A capability index should route to the
  relevant skill instead of loading all skills at startup.
- Subagents are isolated, disposable helpers. Persistent responsibility belongs
  to visible threads or durable task conversations.
- Agent teams/handoffs validate the PMO + department model, but typed handoff
  fields and shared task state are essential.

Adapt:

- OpenAI app-server thread/turn/status primitives are useful as a future
  transport adapter, not as the CoAgent architecture itself.
- Agent SDK sessions and Gemini/Claude auto-memory are useful for context
  recovery, but MoSim should keep cache-first review before promotion to
  project truth.

Reject:

- Do not bind the architecture to one vendor's product-specific feature.
- Do not let auto-memory or self-generated skills silently become canonical
  project facts.

### 12.2 Open-Source System Patterns

Adopt or adapt:

- OpenHands: event stream, workspace isolation, action/observation trace.
- SWE-agent / mini-SWE-agent: trajectory files and task evidence as first-class
  output.
- Cline: Plan/Act and checkpoint rollback as user-reviewable execution units.
- LangGraph: thread, checkpoint, interrupt, durable state, and
  human-in-the-loop vocabulary.
- Temporal: task queue, worker, lease, durable execution, and replay semantics
  as a future runtime analogy.
- Aider: repo map and small Git-backed edit cycles.
- MetaGPT/CrewAI: role/task/SOP templates only when hard evidence packets
  prevent role-play from replacing real engineering output.
- Hermes: memory/skill evolution and scheduled cleanup as inspiration for
  documentation secretary, but only through reviewable promotion.

Reference only or reject as primary base:

- Dify/Flowise/n8n are useful for workflow UI and variables, but not as the
  code-engineering PMO substrate.
- Continue and AutoGen are useful references, but current maintenance posture
  and target use do not make them primary runtime choices.

### 12.3 Local Landing Surface

Local structure already supports the corrected design direction:

- `CoAgent/docs/operating/agent_os_operating_model.md` is the portable shared
  core entry.
- `CoAgent/dispatch/communication_contract.md` is the durable packet and SLO
  contract.
- `CoAgent/docs/architecture/coagent_department_capability_model.md` and
  `CoAgent/protocol/templates/capability_template.yaml` already define
  capability concepts.
- `Docs/Index/api_index.md` should stay a concrete API/tool lookup.
- `Docs/Index/workflow_index.md` should stay a workflow route table.
- `Docs/Index/capability_index.md` should be the host-local capability router.

Corrected design principle:

```text
Do not hard-split roles into isolated documents.
Use shared core + role views + conflict owner + task packet scope.
```

## 13. Proposed Implementation Phases After Review

### Phase A: Document Candidate Only

- Keep this draft in `CoAgent/docs/research/`.
- Add user-reviewed corrections.
- Do not update canonical workflows yet.

### Phase B: Minimal Canonical Patch

After approval, patch:

- `CoAgent/dispatch/communication_contract.md` for remote steer vs dispatch.
- `CoAgent/docs/operating/coagent_ops_patrol_workflow.md` for remote pause
  and liveness ladder.
- `CoAgent/docs/operating/agent_orchestration.md` for terms and surface
  selection.

Do not expand `AGENTS.md`; add only a pointer if needed.

### Phase C: Schema/Checker

Add or update:

- dispatch ticket lease fields;
- `intervention_mode`;
- context revision fields;
- stale lease checker;
- duplicate/hotfix wording detector for entry docs.

### Phase D: Capability Router

Add:

- `CoAgent/capabilities/capability_router.json`;
- health checks for critical tool groups;
- PMO planning gate requiring selected/rejected capability surfaces.

### Phase E: Periodic Documentation Secretary Workflow

Add a periodic cleanup workflow that:

- scans candidate notes, packets, and repeated user corrections;
- groups duplicate rules;
- proposes a patch;
- does not silently change PMO policy;
- reports unresolved conflicts for human review.

## 14. Open Questions For User

1. Should remote pause/steer be allowed automatically by PMO and CoAgentOps for
   any active visible department, or only when the user/PMO explicitly asks for
   an emergency pause?
2. Should every non-trivial visible-thread task be required to write a lease
   file first, even for very small static tasks, or should this apply only to
   tasks expected to run longer than a few minutes?
3. Should the documentation secretary be allowed to apply low-risk dedup
   patches automatically, or should it only produce reviewable patches until
   you explicitly approve each cleanup?
4. Should PMO and CoAgentOps use shared-core plus role-view startup files so
   they retain necessary overlap without loading every operational detail into
   every task?
5. Should the capability router be enforced by a checker in task packets, or
   initially kept as a planning recommendation?

## 15. Current Recommendation

The immediate next step is not to add more constraints. It is to approve a
small research-and-design pass:

```text
1. Keep this draft as the candidate artifact.
2. Review and answer the open questions.
3. Dispatch AGENTOS-RESEARCH-01..07 in parallel where safe.
4. Convert accepted findings into a minimal canonical patch.
5. Add checkers for fields that should not depend on agent memory.
```

The target architecture is not "more agents". It is:

```text
shared core context + role views
  + native Codex surfaces
  + durable packets/checkpoints/leases
  + explicit capability routing
  + small current board
  + periodic doc dedup
  + checker-backed guardrails
```
