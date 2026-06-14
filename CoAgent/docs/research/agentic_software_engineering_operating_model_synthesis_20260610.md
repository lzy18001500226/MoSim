# Agentic Software Engineering Operating Model Synthesis

> Consolidated research result for MoSim/CoAgent. This is a research report,
> not an execution workflow, dispatch authority, or runtime approval.

Status: research synthesis, 2026-06-10 CST.

Scope:

- Host project: `C:\Users\HP\Desktop\MoSim`
- Current execution substrate: Codex App visible threads, native tools,
  skills, plugins, MCP servers, hooks, packets, and project files.
- Write target: `CoAgent/docs/research/`
- No MWORKS, ROS2, UE, Git, visible-thread lifecycle, or automation action is
  authorized by this file.

## 1. Executive Conclusion

The practical unit of this project is not a department chart. It is an
evidence-producing control loop over a native agent execution surface:

```text
objective
  -> context and authority resolution
  -> capability resolution
  -> scoped dispatch
  -> durable start proof
  -> checkpoint / return / blocker
  -> checker-backed integration
  -> document promotion only when reusable
```

Roles such as PMO, CoAgentOps, R1/R2/R3 departments, documentation secretary,
and disposable subagents are role views over the same loop. They cannot be
fully isolated, because real tasks cross boundaries: a dead-thread incident can
affect dispatch, documentation, PMO scheduling, capability routing, and user
notification at the same time.

The design target should therefore be:

```text
shared core context
  + role views
  + task packet scope
  + capability routing
  + durable evidence
  + checker/schema/hook enforcement
  + small current-state board
  + reviewed document promotion
```

The immediate improvement path is not to import a new runtime or create more
departments. It is to make the current Codex App visible-thread operating loop
less ambiguous and more machine-checkable.

## 2. Reuse Audit

This report reuses existing local work instead of restarting the survey.

| Existing file | Current value | Gap this synthesis closes |
|---|---|---|
| `CoAgent/docs/research/agentic_software_engineering_operating_research_plan_20260610.md` | Broad problem analysis, terms, dead-thread stack, document architecture, and research tasks. | Converts the plan into an implementable priority order. |
| `CoAgent/docs/research/context_documentation_governance_research_20260610.md` | Authority ladder and document responsibility split. | Connects context governance to capability resolution and task-control artifacts. |
| `CoAgent/docs/research/REFERENCE_PROJECT_INDEX.md` | Local reference inventory and first-read priorities. | Selects representative projects by operating layer. |
| `Docs/Cache/design_intake/inbox/20260610_agent_project_operating_layers_and_research_plan.md` | Six-layer operating model draft. | Promotes the useful model as research synthesis, not authority. |
| `Docs/Cache/design_intake/inbox/20260610_capability_resolution_context_gap.md` | Concrete failure case: existing window skills were missed. | Turns the failure into a capability-resolution implementation plan. |
| `Docs/Index/capability_index.md` | Human-readable capability router with stable IDs. | Needs machine-readable manifest and checker. |
| `CoAgent/dispatch/communication_contract.md` | Dispatch ticket, SLO, semantic boundary, native surface gate, capability-resolution scaffold. | Needs checker coverage for capability-resolution and evidence reports. |

Do not create another broad survey unless it answers a missing question not
covered above.

## 3. Six-Layer Operating Model

### Layer 1: Execution Surface

What actually executes work:

```text
Codex App visible threads
PowerShell / WSL / shell
MCP tools
plugins and skills
desktop window surfaces
MWORKS / Sysplorer / Syslab
ROS2 / RViz / FAST-LIO
UE editor/runtime
Git and filesystem
```

Primary risk:

```text
the user and PMO think a worker is working, but the execution surface has not
started, is wedged, is waiting for approval, or is using the wrong capability
```

Needed local object:

```text
HostSurfaceSnapshot
```

It should record what the current host can actually observe: visible turn,
readback status, approval/provider/context surface, durable-start file, packet,
and any safe native status indicator.

### Layer 2: Task Control Loop

The task-control loop is the core of the operating system.

Required artifacts:

```text
dispatch ticket
task packet
runtime lease
readback observation
checkpoint
return packet
blocker packet
checker result
PMO board row
```

Current MoSim already has most of this. The gap is consistency and enforcement,
not concept invention.

### Layer 3: Capability Discovery And Routing

The project already has many assets: skills, plugins, MCP servers, scripts,
workflows, reference projects, and checkers. A thread can still propose
creating something that already exists because it did not resolve the current
capability index first.

Required artifacts:

```text
Docs/Index/capability_index.md             # human router, already exists
CoAgent/capabilities/capability_index.json # future machine manifest
CoAgent/protocol/templates/capability_resolution.json
Scripts/quality/check_capability_resolution.py
```

The capability index is not authorization. It answers "what should this task
consider first?" Authority still comes from user/PMO scope, task packet,
workflow, hook, checker, schema, and domain gate.

### Layer 4: Context Governance

Multiple visible threads can hold different recent context. The project cannot
rely on thread memory or compressed chat as truth.

Needed rule:

```text
chat correction
  -> design intake or packet
  -> review and dedup
  -> workflow/schema/checker/skill/index update
  -> entry-file pointer only when fresh startup needs it
```

Important distinction:

```text
memory can help find files
memory does not prove current facts
research notes can propose rules
research notes do not grant authority
```

### Layer 5: Project Domain Layer

This is the actual MoSim product:

```text
MWORKS formal simulation
UE scene / sensor / visual surface
ROS2 / RViz / FAST-LIO transport and review
controllers / planners / metrics / reports
```

CoAgent only supports this. It must not become a substitute for domain
evidence.

### Layer 6: Human Governance

The human is part of the runtime, not an afterthought.

Human-owned decisions:

```text
objective and priority
accept/reject final evidence
manual GUI/review decisions
high-risk live/runtime authorization
restart and visible-thread lifecycle approval when required
```

The system should reduce manual scheduling, but it should not hide authority
changes behind automation.

## 4. External Calibration Matrix

### Official And Vendor Sources

| Source | Relevant mechanism | MoSim implication |
|---|---|---|
| OpenAI Agents SDK | Agents, tools, handoffs, guardrails, sessions, human-in-loop, tracing, sandbox agents. | If MoSim owns orchestration inside Codex App, it still needs explicit state, guardrails, and traces. Raw model calls are not enough. |
| OpenAI Agents SDK tracing | Traces/spans and long-running worker export concepts. | MoSim packets and leases are local trace substitutes; a future evidence report should aggregate them. |
| Anthropic Claude Code hooks | Lifecycle hooks can block or enrich tool/session events; hooks can return additional context and decisions. | Hard safety belongs in hook/checker/schema, not repeated prose in `AGENTS.md`. |
| Anthropic Claude Code skills | Skills turn repeated procedures into loadable `SKILL.md` files; troubleshooting includes over/under-triggering. | MoSim should route skills through capability IDs and avoid bloating startup context. |
| Anthropic Claude Code subagents | Subagents are scoped definitions with tools, model, permissions, hooks, memory, and isolation. | Disposable subagents are not the same as durable visible departments. |
| Gemini CLI configuration | Project settings, context filename, tool/MCP include/exclude, sandbox, checkpointing, telemetry. | Project-local config and explicit tool allowlists are a real pattern; simple string excludes are not sufficient hard security. |
| LangGraph persistence | Checkpointers use `thread_id` to save and resume state, with state history and pending writes. | MoSim runtime leases and dispatch tickets are a lightweight local checkpoint layer. |
| LangGraph interrupts | Interrupts pause execution, save state, and resume with external input. | MoSim needs explicit approval/review/provider/context-surface vocabulary rather than treating all pauses as dead threads. |

### Local Reference Projects

| Local reference | Useful pattern | Adopt / adapt / reject |
|---|---|---|
| `References/Agent/Workflow/okwinds/capability-runtime` | `Protocol -> Runtime -> Report`; `AgentSpec`, `WorkflowSpec`, `Runtime`, `NodeReport`, host snapshots, approvals, resume intents. | Adapt as object-model inspiration. Do not import as dependency now. |
| `References/Agent/Platforms/OpenHands` | SDK/CLI/GUI/cloud lanes, agent platform, sandbox, REST API, scalable execution. | Reference for platform shape and execution surface separation. |
| `References/Agent/Platforms/open-swe` | AGENTS context, curated tools, sandbox per task, middleware, deterministic thread IDs, mid-run follow-up injection. | Adapt dispatch/readback/middleware lessons; do not replace Codex App. |
| `References/Agent/Workflow/langgraph` | Durable execution, checkpoint, memory, interrupts, observability. | Adapt vocabulary and checkpoint concepts. |
| `References/Agent/Workflow/temporal` | Durable workflow, queues, retries, replay. | Reference only for future runtime thinking; too heavy for current step. |
| `References/Agent/Workflow/agentops` | Observability, replay, cost, framework integrations. | Adapt evidence aggregation idea. |
| `References/Agent/Platforms/hermes-agent` | Long-lived agent, gateway, cron, memory, skill creation, subagents, terminal backends. | Adapt memory/skill cleanup loop carefully; do not allow silent policy mutation. |
| `References/Agent/Platforms/codex` | Codex CLI/App/IDE surfaces and current native workbench model. | Current primary surface remains Codex App. |
| `References/Agent/Platforms/gemini-cli` | Project config, MCP, checkpointing, memory/context files. | Adapt configuration and context-scope ideas. |
| `References/Agent/Platforms/cline` | Plan/Act mode, checkpoints, Kanban/multi-agent board, worktrees. | Adapt user-reviewable phases and rollback/checkpoint thinking. |
| `References/Agent/Platforms/SWE-agent` | Config-driven issue-solving, trajectories, agent-computer interface. | Adapt trajectory/evaluation pattern for task evidence. |

## 5. Current MoSim/CoAgent Gaps

### Gap A: Capability Index Is Human-Readable Only

Current:

```text
Docs/Index/capability_index.md
```

Problem:

```text
Agents can read it, but checkers cannot reliably validate route selection,
duplicate capability creation, health state, or evidence coverage.
```

Needed:

```text
CoAgent/capabilities/capability_index.json
CoAgent/capabilities/capability_coverage_map.json
Scripts/quality/check_capability_resolution.py
```

### Gap B: Capability Resolution Has A Template But No Enforcement

Current:

```text
CoAgent/protocol/templates/capability_resolution.json
```

Problem:

```text
A packet can omit capability resolution and still propose duplicate assets.
```

Needed:

```text
check_capability_resolution.py
test_capability_resolution.py
```

Minimum fail cases:

```text
create_new_assets non-empty but searched_existing_assets empty
create_new_assets conflicts with do_not_recreate
matched reusable capability exists but insufficiency reason is blank
```

### Gap C: Evidence Is Split Across Many Files

Current evidence can be spread across:

```text
task packet
dispatch ticket
runtime lease
return packet
blocker packet
checker output
screenshot manifest
PMO board
raw result files
```

This is acceptable, but PMO needs a compact report object that points to those
files.

Needed:

```text
EvidenceReport / NodeReport-like JSON
```

It should not replace underlying evidence. It should aggregate:

```text
request_id
task_type
target_thread_id
capability_resolution
dispatch_ticket
runtime_lease
terminal_packet
checker_results
domain_artifacts
claim_ceiling
next_owner
```

### Gap D: Host Wait/Resume/Approval States Are Not Unified

Current words are scattered:

```text
approval/review/provider surface
context compression surface
view refresh required
remote pause/steer
restart validation
dead-thread suspected
```

Needed:

```text
HostSurfaceSnapshot state enum
```

Recommended initial values:

```text
no_visible_turn
visible_turn_no_durable_start
durable_start_seen
checkpoint_fresh
checkpoint_stale
expected_packet_seen
blocker_packet_seen
approval_pending
provider_pending
review_pending
context_compression_surface
view_refresh_required
remote_pause_ack_seen
dispatch_surface_failure_suspected
global_app_or_network_surface
```

### Gap E: Documentation Intake Exists But Promotion Is Manual And Ad Hoc

Current:

```text
Docs/Cache/design_intake/
CoAgent/docs/research/
session-memory migration docs
```

Problem:

```text
Good design notes can remain unpromoted; bad notes can be copied into entry
docs as patches.
```

Needed:

```text
Docs/Workflows/design_intake_promotion_workflow.md
Scripts/quality/check_entry_doc_size_and_duplicates.py
```

The documentation secretary should propose patches, not silently define PMO
policy.

### Gap F: Dispatch SLO Is Stronger Than Before But Still Needs Reporting

Current:

```text
dispatch_ticket v2
dispatch_nonce
runtime lease
5-minute surface-health window
```

Problem:

```text
The mechanism detects missing start proof only if every dispatcher actually
creates and updates the ticket.
```

Needed:

```text
one low-risk closed-loop drill per new mechanism
board row that points to ticket, not long prose
checker output recorded in packet/report
```

## 6. Recommended Implementation Slices

The next work should be small, checkable, and reversible.

### Slice 1: Capability Resolution Checker

Files:

```text
Scripts/quality/check_capability_resolution.py
Scripts/tests/test_capability_resolution.py
CoAgent/protocol/templates/capability_resolution.json
CoAgent/dispatch/communication_contract.md
```

Acceptance:

```text
checker passes a valid resolution block
checker fails duplicate/new asset creation without searched assets
checker fails do_not_recreate conflict
checker is referenced from communication_contract
```

Why first:

```text
This directly prevents the current failure where an existing screenshot skill
was treated as a missing asset.
```

### Slice 2: Machine-Readable Capability Manifest

Files:

```text
CoAgent/capabilities/capability_index.json
CoAgent/capabilities/README.md
Docs/Index/capability_index.md
```

Minimum fields:

```json
{
  "stable_id": "",
  "human_name": "",
  "owner_doc": "",
  "primary_skill_or_workflow": "",
  "scripts": [],
  "mcp_or_plugin_surfaces": [],
  "checker_or_test_anchor": "",
  "evidence_contract": "",
  "authority_ceiling": "",
  "stop_actions": [],
  "known_failure_modes": []
}
```

Acceptance:

```text
manifest covers existing stable IDs from Docs/Index/capability_index.md
human index and JSON manifest agree on IDs
no capability row grants permission by itself
```

### Slice 3: Capability Coverage Map

Files:

```text
CoAgent/capabilities/capability_coverage_map.json
Scripts/quality/check_capability_coverage.py
```

Purpose:

```text
capability id
  -> human doc
  -> skill/workflow
  -> script/MCP/plugin
  -> checker/test
  -> evidence path/class
```

Acceptance:

```text
top P0 capabilities have at least owner_doc and evidence_contract
missing checker/test is explicit, not hidden
```

### Slice 4: EvidenceReport Aggregator

Files:

```text
CoAgent/protocol/templates/evidence_report.json
Scripts/agent/build_evidence_report.py
Scripts/tests/test_build_evidence_report.py
```

Purpose:

```text
produce a compact NodeReport-like summary without moving existing evidence
```

Acceptance:

```text
given request_id, report links ticket, lease, return/blocker, checker output
report has claim_ceiling and next_owner
missing artifacts are reported as missing, not guessed
```

### Slice 5: Host Surface Snapshot Vocabulary

Files:

```text
CoAgent/protocol/templates/host_surface_snapshot.json
CoAgent/docs/operating/agent_orchestration.md
CoAgent/docs/operating/coagent_ops_patrol_workflow.md
```

Purpose:

```text
separate dead thread, provider wait, approval wait, context compression, stale
lease, and global app/network surface
```

Acceptance:

```text
state enum exists
dispatch ticket references the snapshot path optionally
CoAgentOps can classify without clicking through every thread
```

### Slice 6: Design Intake Promotion Workflow

Files:

```text
Docs/Workflows/design_intake_promotion_workflow.md
Docs/Cache/design_intake/index.md
CoAgent/docs/operating/context_documentation_governance.md
```

Purpose:

```text
keep discussions and architecture ideas landing somewhere without polluting
AGENTS.md or startup context
```

Acceptance:

```text
candidate note statuses are defined
promotion targets are defined
documentation secretary can propose patch but not own PMO authority
```

## 7. What Not To Do Now

Do not:

1. Import `capability-runtime` as a dependency before the local control loop
   is proven.
2. Replace Codex App visible threads with a generic agent framework.
3. Add more prose constraints to `AGENTS.md` or
   `Docs/Workflows/new_conversation_context.md` for problems that belong in
   schema/checker/template/workflow/skill/index.
4. Treat R1/R2/R3 as a clean company org chart. They are execution surfaces
   with role views and authority ceilings.
5. Let documentation secretary define product priority or accept engineering
   evidence.
6. Use metrics as a substitute for dispatch. An idle P0 lane needs a dispatch,
   recovery action, decision request, or explicit no-ready-task reason.
7. Treat thread transcript, chat reply, or memory recall as final evidence
   without packet/checker/domain artifacts.

## 8. Recommended Directory Shape

This is a target shape for future migration, not a required immediate move.

```text
CoAgent/
  capabilities/
    README.md
    capability_index.json
    capability_coverage_map.json
    cards/
  dispatch/
    communication_contract.md
    department_threads.json
  docs/
    operating/
    research/
  hooks/
  protocol/
    schemas/
    templates/
  skills/
  runtime/
    README.md                  # future only

Docs/
  Workflows/
    mainline_operations_board.md
    mosim_visible_dispatch_adapter.md
    design_intake_promotion_workflow.md
  Index/
    capability_index.md
    workflow_index.md
    api_index.md
  Cache/
    design_intake/

Scripts/
  quality/
    check_capability_resolution.py
    check_capability_coverage.py
    check_dispatch_ticket_slo.py
  agent/
    build_evidence_report.py

Results/
  agent_packets/
    dispatch_tickets/
    returns/
    blockers/
  runtime_leases/
  evidence_reports/
```

MoSim-specific MWORKS/ROS2/UE facts stay in host docs, host workflows,
domain skills, `Models/`, `Scripts/`, and `Results/`. Portable CoAgent should
carry the reusable operating pattern, not the project-specific truth.

## 9. Future Crawl List

Local references are enough for the next implementation slices. Ask the user
for crawling only if a future task specifically needs missing source detail.

Potential future targets:

```text
specific blog posts by the capability-runtime author
Codex App issue/discussion links about visible-thread state and automations
private examples of internal coding-agent operating systems
current official docs for any newly exposed Codex App thread/server API
```

Do not crawl more projects just to expand the bibliography.

## 10. Practical Next Step

Start with Slice 1:

```text
implement capability-resolution checker
add tests
run it against a small valid fixture and duplicate-asset failure fixture
then require it for dispatch packets that create or modify reusable assets
```

This is the highest leverage step because it closes a real observed failure:
an already-existing window screenshot skill was missed by the responding
thread, causing duplicate planning and context drift.

After Slice 1, implement Slice 2 and Slice 3 so capability discovery stops
being only a human-readable markdown convention.

## 11. Source Notes

Local sources:

- `CoAgent/docs/research/agentic_software_engineering_operating_research_plan_20260610.md`
- `CoAgent/docs/research/context_documentation_governance_research_20260610.md`
- `CoAgent/docs/research/REFERENCE_PROJECT_INDEX.md`
- `Docs/Cache/design_intake/inbox/20260610_agent_project_operating_layers_and_research_plan.md`
- `Docs/Cache/design_intake/inbox/20260610_capability_resolution_context_gap.md`
- `References/Agent/Workflow/okwinds/capability-runtime/README.md`
- `References/Agent/Platforms/OpenHands/README.md`
- `References/Agent/Platforms/open-swe/README.md`
- `References/Agent/Workflow/langgraph/README.md`
- `References/Agent/Platforms/hermes-agent/README.md`
- `References/Agent/Platforms/codex/README.md`

Official/current web sources used for calibration:

- OpenAI Agents SDK: <https://openai.github.io/openai-agents-python/>
- OpenAI Agents SDK tracing: <https://openai.github.io/openai-agents-python/tracing/>
- Claude Code hooks: <https://code.claude.com/docs/en/hooks>
- Claude Code skills: <https://code.claude.com/docs/en/skills>
- Claude Code subagents: <https://code.claude.com/docs/en/sub-agents>
- Gemini CLI configuration: <https://github.com/google-gemini/gemini-cli/blob/main/docs/cli/configuration.md>
- LangGraph persistence: <https://docs.langchain.com/oss/python/langgraph/persistence>
- LangGraph interrupts: <https://docs.langchain.com/oss/python/langgraph/interrupts>
