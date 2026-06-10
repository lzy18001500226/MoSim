# Capability Index

> Host-local capability router for MoSim. This file tells Codex agents what
> native surface, plugin, MCP, skill, script, visible thread, or review route
> to consider for a task. It is an index, not a replacement for the owning
> workflow, skill, schema, checker, or human approval gate.

Status: initial PMO review draft, 2026-06-10 CST.

Use this after `AGENTS.md`, `Docs/Workflows/new_conversation_context.md`, and
the current PMO board when a task requires capability selection. Do not bulk
load every linked skill or workflow; load only the row that matches the task.

## 1. Operating Rule

Capabilities are shared across roles. PMO, CoAgentOps, R1/R2/R3 departments,
documentation maintenance, and disposable subagents may all need the same
tools, but they use them under different authority.

Use this routing model:

```text
shared core rule
  -> role view and authority
  -> task packet scope
  -> capability index row
  -> owning workflow/skill/checker
  -> evidence or blocker
```

Do not infer permission from capability existence. A capability row means
"consider this route"; the task packet and owning workflow decide whether this
turn may use it.

## 2. Capability Table

| Capability Family | Concrete Surface | Use When | Forbidden Or Stop Actions | Owner Doc / Skill | Health Or Checker |
|---|---|---|---|---|---|
| Codex visible thread dispatch | `codex_app.send_message_to_thread`, `read_thread`, thread registry | Durable department context, PMO dispatch, R1/R2/R3 work, remote pause/steer, no-op probes | Do not treat native send success as task success; do not use remote steer for new work while a critical task is running unless PMO/user authorizes | `CoAgent/dispatch/communication_contract.md`, `CoAgent/docs/operating/coagent_ops_patrol_workflow.md`, MoSim adapter `Docs/Workflows/mosim_visible_dispatch_adapter.md` | dispatch ticket under `Results/agent_packets/dispatch_tickets/`; `Scripts/quality/check_dispatch_ticket_slo.py` |
| Codex App thread lifecycle | `list_threads`, title/archive/fork/handoff tools when exposed | Route discovery, thread title repair, explicit lifecycle work | Do not create/fork/archive/rename visible threads without PMO/user approval | `AGENTS.md`, `CoAgent/docs/operating/agent_orchestration.md` | registry review in `CoAgent/dispatch/department_threads.json` |
| Disposable subagent | `multi_agent_v1.spawn_agent` | Bounded parallel research, read-only audits, disjoint implementation slices, focused verification | Do not use as durable department, PMO authority, live GUI owner, or hidden acceptance owner | `CoAgent/docs/operating/agent_orchestration.md` | parent review; result must be integrated by owning visible thread or PMO |
| Automation / recurring patrol | Codex App automation, CoAgentOps heartbeat | Idle/recovery patrol, reminder, post-restart sweep, scheduled status checks | Do not rely on target-thread automation to interrupt a busy/wedged target; do not make automation rewrite PMO policy silently | `CoAgent/docs/operating/coagent_ops_patrol_workflow.md` | patrol packet, board update, dispatch ticket SLO |
| Native hooks / preflight | `CoAgent/hooks/`, project hook, quality scripts | Hard path, secret, destructive command, broad Git, packet/schema, runtime gate enforcement | Do not move enforceable safety rules into prose only | `CoAgent/hooks/README.md`, `CoAgent/docs/operating/tooling_assets_governance.md` | hook tests and `Scripts/quality/*.py` |
| MWORKS / Sysplorer MCP | Sysplorer MCP tools, `Docs/Skills/Mworks/*` | Formal model operations, model check, simulation, Sysblock wiring, result evidence | Stop on login/license/authorization/GUI-error; do not use live MWORKS without task-local live gate | `Docs/Workflows/mosim_visible_dispatch_adapter.md`, `Docs/Skills/Mworks/mworks-mcp-operations/SKILL.md`, `Docs/Skills/Mworks/mworks-simulation-evidence/SKILL.md`, `Docs/Skills/Mworks/mworks-sysblock-graphical-modeling/SKILL.md` | MWORKS live gate, model check/simulation/result evidence, packet checker |
| MWORKS window review | Windows MCP / DPI-aware screenshot scripts / CoAgentOps window patrol | Window health, activation/login/license review, graphical layout/result-window review | Activation/login/license must use foreground or maximized target-main-window evidence; normal review may use background DPI-aware capture | `Docs/Workflows/mosim_visible_dispatch_adapter.md`, `CoAgent/docs/operating/coagent_ops_patrol_workflow.md`, MWORKS skills | screenshot evidence, MWORKS patrol packet |
| Syslab / Julia | Syslab MCP tools and built-in Syslab skills | Julia calculations, MATLAB/Syslab porting, plotting, installed package docs | Do not guess API details; detect environment before writing/running Julia | Syslab skill policy, `Docs/Skills/Mworks/mworks-syslab-porting/SKILL.md` | `detect_syslab_toolboxes`, docs search/read before unclear APIs |
| Unreal Editor MCP | `mosim-unreal` MCP, UE scripts | UE scene inspection, command/echo contract, reversible actor probe, source-static UE checks | Do not claim runtime ack/planner truth/final scene acceptance from screenshots or source-only evidence | `Docs/Workflows/mosim_visible_dispatch_adapter.md`, `Docs/Workflows/unreal_renderer.md`, `Docs/Skills/Unreal/mosim-unreal/SKILL.md` | capture bundle, validator, reversible probe evidence |
| Epic/Fab/library inventory | `mosim-epic` MCP, UE library scripts | Scene source discovery, asset inventory, manual import planning | Fab/library visibility is not automated import or planning truth | `Docs/Skills/Unreal/mosim-epic/SKILL.md`, `Docs/Workflows/unreal_renderer.md` | inventory/audit scripts, manual review evidence |
| ROS2 / RViz / FAST-LIO | WSL ROS2 runtime, ROS MCP, RViz, scripts | Native robotics transport/localization/map/planner review | No fake pointcloud/map/TF/odom, no keyboard pose, no setpoint publication without explicit live gate | `Docs/Workflows/mosim_visible_dispatch_adapter.md`, `Docs/Workflows/ros2_runtime_setup.md`, `Docs/Workflows/unreal_renderer.md` | ROS2 evidence bundle, TF/map/pointcloud checks, blocker packet |
| Git / DevOps | path-limited Git, GitHub plugin/CLI when available | Review, commit, push, issue/PR work, external reference drain | No broad staging, destructive history rewrite, destructive cleanup, or hidden ignore backlog without approval | `AGENTS.md`, `Docs/Workflows/agent_task_ledger.md`, DevOps packets | path-limited diff/status, diff whitespace check, packet evidence |
| GitHub issue / PR | GitHub plugin/skill, GitHub CLI when configured | Filing issues, reading PRs/issues, addressing comments | Do not publish external issue/PR without user approval when content is uncertain or private | GitHub skill, task-specific packet | source links, draft issue text, user confirmation |
| Browser / web research | `web` search, Browser plugin for local web UI | Current external facts, docs, official sources, local web app testing | Use primary sources for technical claims; do not rely on stale memory for unstable facts | task-specific workflow, relevant skill | source links in final/report |
| Documentation secretary | `Docs/Index/*`, `CoAgent/docs/research/*`, context-maintenance route | Context consistency, dedup, candidate promotion, file organization, index repair | Does not define PMO runtime authority, accept engineering results, or silently rewrite policy | `CoAgent/docs/operating/agent_os_operating_model.md`, session memory workflow | reviewable patch, not hidden policy change |
| Capability cards | `CoAgent/protocol/templates/capability_template.yaml`, future capability cards | Tool health, route ownership, fallback, claim ceiling | Do not infer health from past success; do not overclaim above health level | `CoAgent/docs/architecture/coagent_department_capability_model.md`, `CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/tool_capability_health_and_fallback_protocol.md` | future `check_capability_index.py` / capability-card checker |
| Review / evidence gate | result packets, review packages, screenshots, logs, metrics | Acceptance, blocker classification, claim boundary | Chat summary alone is not acceptance evidence | `CoAgent/dispatch/communication_contract.md`, domain workflows | `Scripts/quality/check_department_packet_contract.py`, evidence manifests |

## 3. Quick Selection Rules

- If a task needs durable specialty context, choose a visible department thread.
- If a task is bounded and independent, choose a disposable subagent.
- If a task is a hard safety boundary, choose a hook/checker.
- If a task needs live external app state, choose MCP/plugin/native desktop
  route and prove the route's current health first.
- If a task asks "what tool should I use", read this index before guessing.
- If a row points to a skill or workflow, load only that specific target.

## 4. Missing Work

This first index is intentionally lightweight. Follow-up work should add:

1. A machine-readable `CoAgent/capabilities/capability_index.json`.
2. Capability cards for MWORKS, UE, ROS2, Git, Codex transport, GitHub, and web
   research routes.
3. A quality checker to require owner docs, stop actions, evidence gates, and
   health checks for each row.
4. A task-packet field for selected/rejected capability surfaces.
