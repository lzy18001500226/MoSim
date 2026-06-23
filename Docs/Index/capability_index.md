# Capability Index

> Host-local capability router for MoSim. This file tells Codex agents what
> native surface, plugin, MCP, skill, script, visible thread, or review route
> to consider for a task. It is an index, not a replacement for the owning
> workflow, skill, schema, checker, or human approval gate.

Status: initial PMO review draft with machine-readable companion,
2026-06-10 CST.

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
| Current Sunray ROS1 / Gazebo / RViz / MID360 | WSL Ubuntu-20.04 ROS1 Noetic, References/Sunray, Gazebo Classic, RViz, `Scripts/sunray/` | Current single-thread Sunray150 takeoff/hover/land, figure-8, trajectory/path, and real MID360 PointCloud2 review | No x500/PX4/ROS2 substitution, no downloaded FAST-LIO replacement while local `References/Lab/FAST_LIO` exists, no fake or empty point cloud, no headless pass as GUI acceptance | `Docs/Workflows/sunray_ros1_current_runtime_lane.md`, `Docs/Index/sunray_migration_index.md` | Sunray ROS1 result dir, nonempty PointCloud2 sample, Gazebo/RViz review manifest or blocker |
| Historical/future ROS2 / RViz2 / FAST-LIO | WSL ROS2 runtime, ROS MCP, RViz2, scripts | Future/reference native robotics transport/localization/map/planner review after explicit route reopening | No fake pointcloud/map/TF/odom, no keyboard pose, no setpoint publication without explicit live gate; not current Sunray review lane | `Docs/Workflows/ros2_runtime_setup.md`, `Docs/Workflows/mosim_visible_dispatch_adapter.md`, `Docs/Workflows/unreal_renderer.md` | ROS2 evidence bundle, TF/map/pointcloud checks, blocker packet |
| Git / DevOps | path-limited Git, GitHub plugin/CLI when available | Review, commit, push, issue/PR work, external reference drain | No broad staging, destructive history rewrite, destructive cleanup, or hidden ignore backlog without approval | `AGENTS.md`, `Docs/Workflows/agent_task_ledger.md`, DevOps packets | path-limited diff/status, diff whitespace check, packet evidence |
| GitHub issue / PR | GitHub plugin/skill, GitHub CLI when configured | Filing issues, reading PRs/issues, addressing comments | Do not publish external issue/PR without user approval when content is uncertain or private | GitHub skill, task-specific packet | source links, draft issue text, user confirmation |
| Browser / web research | `web` search, Browser plugin for local web UI | Current external facts, docs, official sources, local web app testing | Use primary sources for technical claims; do not rely on stale memory for unstable facts | task-specific workflow, relevant skill | source links in final/report |
| Desktop window screenshot evidence | Win32 `PrintWindow`, screenshot scripts, Windows MCP/UIA read-only inspection | Background screenshot evidence for visible-but-covered windows, foreground/maximized review evidence, minimized-window restore/maximize/capture/minimize exception, blank capture triage | Observation only; screenshot permission does not authorize clicks, login, save, restart, send, approve, close, archive, or lifecycle actions; minimized windows are state evidence until restore is authorized | `CoAgent/skills/window-capture-evidence/SKILL.md`; MoSim script examples in `Docs/Index/api_index.md#12-desktop-window-screenshot-and-action-helpers` | screenshot path or skipped-minimized manifest, window metadata, blank/ambiguous retry note |
| Desktop window UI action control | Application API/MCP/CLI, UI Automation, Win32 handle/control messages, foreground or coordinate fallback | Explicitly authorized background click/control invocation, foreground click then minimize, safe low-risk UI operation, dry-run action planning | Do not infer permission from capability; high-risk controls need explicit task authority; stop on ambiguous target, blank/loading UI, or project workflow ban | `CoAgent/skills/window-ui-action-control/SKILL.md`; MoSim script examples in `Docs/Index/api_index.md#12-desktop-window-screenshot-and-action-helpers` | pre-action target proof, post-action readback, action evidence/blocker |
| Documentation secretary | `Docs/Index/*`, `CoAgent/docs/research/*`, context-maintenance route | Context consistency, dedup, candidate promotion, file organization, index repair | Does not define PMO runtime authority, accept engineering results, or silently rewrite policy | `CoAgent/docs/operating/agent_os_operating_model.md`, session memory workflow | reviewable patch, not hidden policy change |
| Capability cards and resolution | `CoAgent/protocol/templates/capability_template.yaml`, `CoAgent/protocol/templates/capability_resolution.json`, `CoAgent/capabilities/capability_index.json` | Tool health, route ownership, fallback, claim ceiling, and duplicate-asset prevention before creating skills/workflows/scripts/checkers/MCP adapters | Do not infer health from past success; do not overclaim above health level; do not treat capability resolution as permission | `CoAgent/docs/architecture/coagent_department_capability_model.md`, `CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/tool_capability_health_and_fallback_protocol.md`, `CoAgent/dispatch/communication_contract.md#capability-resolution` | `Scripts/quality/check_capability_resolution.py`; `Scripts/quality/check_capability_index.py`; `Scripts/quality/check_agent_task_native_surface_gate.py --strict` invokes capability-resolution validation for new strict visible-thread packets |
| Review / evidence gate | result packets, review packages, screenshots, logs, metrics | Acceptance, blocker classification, claim boundary | Chat summary alone is not acceptance evidence | `CoAgent/dispatch/communication_contract.md`, domain workflows | `Scripts/quality/check_department_packet_contract.py`, evidence manifests |

## 3. Stable Capability IDs

Use stable ids in task packets and `capability_resolution` blocks. Human-readable
capability names may change; stable ids should remain compatible unless the
capability is explicitly superseded.

| Stable ID | Capability Row | Primary Existing Assets |
|---|---|---|
| `codex.visible_thread.dispatch` | Codex visible thread dispatch | `CoAgent/dispatch/communication_contract.md`; `CoAgent/protocol/templates/visible_thread_dispatch_packet.json`; `CoAgent/protocol/templates/visible_thread_dispatch_ticket.json` |
| `codex.thread_lifecycle` | Codex App thread lifecycle | `AGENTS.md`; `CoAgent/dispatch/department_threads.json`; `CoAgent/docs/operating/agent_orchestration.md` |
| `automation.recurring_patrol` | Automation / recurring patrol | `CoAgent/docs/operating/coagent_ops_patrol_workflow.md`; Codex App `.codex/automations` user-profile storage |
| `hooks.preflight` | Native hooks / preflight | `CoAgent/hooks/README.md`; `CoAgent/hooks/preflight.py`; `CoAgent/hooks/codex_native_hook.py` |
| `mworks.sysplorer_mcp` | MWORKS / Sysplorer MCP | `Docs/Skills/Mworks/mworks-mcp-operations/SKILL.md`; `Docs/Workflows/mosim_visible_dispatch_adapter.md` |
| `mworks.window_review` | MWORKS window review | `Docs/Workflows/mosim_visible_dispatch_adapter.md`; `CoAgent/docs/operating/coagent_ops_patrol_workflow.md` |
| `desktop.window.capture_evidence` | Desktop window screenshot evidence | `CoAgent/skills/window-capture-evidence/SKILL.md`; `Docs/Index/api_index.md#12-desktop-window-screenshot-and-action-helpers` |
| `desktop.window.ui_action_control` | Desktop window UI action control | `CoAgent/skills/window-ui-action-control/SKILL.md`; `Docs/Index/api_index.md#12-desktop-window-screenshot-and-action-helpers` |
| `ue.runtime_or_source` | Unreal Editor MCP | `Docs/Workflows/unreal_renderer.md`; `Docs/Skills/Unreal/mosim-unreal/SKILL.md` |
| `sunray.ros1_runtime_review` | Current Sunray ROS1 / Gazebo / RViz / MID360 | `Docs/Workflows/sunray_ros1_current_runtime_lane.md`; `Docs/Index/sunray_migration_index.md` |
| `ros2.runtime_review` | Historical/future ROS2 / RViz2 / FAST-LIO | `Docs/Workflows/ros2_runtime_setup.md`; `Docs/Workflows/mosim_visible_dispatch_adapter.md` |
| `git.devops` | Git / DevOps | `AGENTS.md`; DevOps packets; path-limited Git workflow |
| `github.issue_pr` | GitHub issue / PR | GitHub skill or CLI when configured; task-specific user approval |
| `browser.web_research` | Browser / web research | `web` search; Browser plugin for local UI; task-specific workflow |
| `docs.secretary` | Documentation secretary | `CoAgent/docs/operating/context_documentation_governance.md`; `Docs/Cache/design_intake/index.md` |
| `capability.cards` | Capability cards and resolution | `CoAgent/protocol/templates/capability_template.yaml`; `CoAgent/protocol/templates/capability_resolution.json`; `CoAgent/capabilities/capability_index.json`; `Scripts/quality/check_capability_resolution.py`; `Scripts/quality/check_capability_index.py` |
| `review.evidence_gate` | Review / evidence gate | `CoAgent/dispatch/communication_contract.md`; `Scripts/quality/check_department_packet_contract.py` |

## 4. Quick Selection Rules

- If a task needs durable specialty context, choose a visible department thread.
- If a task is bounded and independent, choose a disposable subagent.
- If a task is a hard safety boundary, choose a hook/checker.
- If a task needs live external app state, choose MCP/plugin/native desktop
  route and prove the route's current health first.
- If a task asks "what tool should I use", read this index before guessing.
- If a row points to a skill or workflow, load only that specific target.
- If a task would create a new skill, workflow, script, checker, or MCP
  adapter, first add a `capability_resolution` block naming the existing
  assets checked and why they are insufficient.

## 5. Missing Work

This first index is intentionally lightweight. Current machine-readable support:

- `CoAgent/capabilities/capability_index.json` mirrors the stable capability
  ids, owner docs, stop actions, evidence gates, existing assets, and checker
  routes.
- `Scripts/quality/check_capability_index.py` validates the JSON index, checks
  Markdown/JSON stable-id alignment, and rejects capability entries that imply
  authorization.
- `Scripts/quality/check_capability_resolution.py` validates per-task
  `capability_resolution` blocks.

Follow-up work should add:

1. Capability cards for MWORKS, UE, ROS2, Git, Codex transport, GitHub, and web
   research routes.
2. Optional integration from `check_capability_resolution.py` into more packet
   checkers after older packets and fixtures are migrated. New strict
   visible-thread preflight already invokes it through
   `Scripts/quality/check_agent_task_native_surface_gate.py --strict`.
