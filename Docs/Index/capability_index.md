# Capability Index

> Host-local capability router for MoSim. This file tells Codex agents what
> native surface, plugin, MCP, skill, script, legacy visible-thread route, or
> review route to consider for a task. It is an index, not a replacement for the owning
> workflow, skill, schema, checker, or human approval gate.

Status: current single-thread capability router with machine-readable
companion, 2026-07-01 CST.

Use this after `AGENTS.md`, `Docs/Workflows/new_conversation_context.md`, and
the current PMO board when a task requires capability selection. Do not bulk
load every linked skill or workflow; load only the row that matches the task.

## 1. Operating Rule

Capabilities are shared across task types. In current single-thread MoSim
work, choose local tools, skills, MCP surfaces, checkers, and evidence scripts
first. Former visible-thread dispatch, patrol automation, R1/R2/R3 routing,
and durable department surfaces are legacy/reference only unless the user asks
for explicit cleanup or historical packet audit.

Use this routing model:

```text
shared core rule
  -> role view and authority
  -> current user instruction and local goal scope
  -> capability index row
  -> owning workflow/skill/checker
  -> evidence or blocker
```

Do not infer permission from capability existence. A capability row means
"consider this route"; the current user instruction, local goal, and owning
workflow decide whether this turn may use it. Legacy task packets apply only
to explicit packet repair, historical audit, or an explicitly reopened
visible-thread route.

## 2. Current Capability Table

| Capability Family | Concrete Surface | Use When | Forbidden Or Stop Actions | Owner Doc / Skill | Health Or Checker |
|---|---|---|---|---|---|
| Native hooks / preflight | `Scripts/hooks/`, project hook, quality scripts | Hard path, secret, destructive command, broad Git, packet/schema, runtime gate enforcement | Do not move enforceable safety rules into prose only | `Scripts/hooks/README.md`, `Docs/Workflows/tooling_assets_governance.md` | hook tests and `Scripts/quality/*.py` |
| MWORKS / Sysplorer MCP | Sysplorer MCP tools, `Docs/Skills/Mworks/*` | Formal model operations, model check, simulation, Sysblock wiring, result evidence | Stop on login/license/authorization/GUI-error; do not use live MWORKS without current live gate | `Docs/Skills/Mworks/mworks-mcp-operations/SKILL.md`, `Docs/Skills/Mworks/mworks-simulation-evidence/SKILL.md`, `Docs/Skills/Mworks/mworks-sysblock-graphical-modeling/SKILL.md` | MWORKS live gate, model check/simulation/result evidence |
| MWORKS window review and screenshot evidence | Windows MCP / DPI-aware screenshot scripts / desktop skills | Activation/login/license evidence, graphical layout/result-window review, or ordinary background screenshot evidence | Screenshot ability does not authorize clicks/login; maximize only for activation/login/license/authorization evidence; stop on ambiguous windows | `Docs/Skills/Desktop/window-capture-evidence/SKILL.md`, `Docs/Skills/Desktop/window-ui-action-control/SKILL.md`, `Docs/Skills/Mworks/mworks-mcp-operations/SKILL.md` | screenshot path, window metadata, MWORKS live-gate checker |
| Syslab / Julia | Syslab MCP tools and built-in Syslab skills | Julia calculations, MATLAB/Syslab porting, plotting, installed package docs | Do not guess API details; detect environment before writing/running Julia | Syslab skill policy, `Docs/Skills/Mworks/mworks-syslab-porting/SKILL.md` | `detect_syslab_toolboxes`, docs search/read before unclear APIs |
| Unreal Editor MCP | `mosim-unreal` MCP, UE scripts | Explicit S11 UE/frontend display work, scene inspection, command/echo contract, reversible actor probe, or source-static UE checks | Do not claim current ROS1/Gazebo/PX4 control-loop success, localization success, planner truth, runtime ack, or final scene acceptance from screenshots or source-only evidence | `Docs/Workflows/unreal_renderer.md`, `Docs/Skills/Unreal/mosim-unreal/SKILL.md` | capture bundle, validator, reversible probe evidence |
| Epic/Fab/library inventory | `mosim-epic` MCP, UE library scripts | Scene source discovery, asset inventory, manual import planning | Fab/library visibility is not automated import or planning truth | `Docs/Skills/Unreal/mosim-epic/SKILL.md`, `Docs/Workflows/unreal_renderer.md` | inventory/audit scripts, manual review evidence |
| Current Sunray ROS1 / Gazebo / PX4 / MAVROS / RViz / MID360 | WSL Ubuntu-20.04 ROS1 Noetic, References/Sunray, Gazebo Classic, PX4, MAVROS, px4ctrl, RViz, `Scripts/sunray/` | Current P0 minimum big system: Sunray150 takeoff/hover/land, trajectory gates, PX4/MAVROS/px4ctrl control, and real MID360/RViz point-cloud, trajectory, map, and frame review | No x500/PX4/ROS2 substitution, no downloaded FAST-LIO replacement while local `References/Lab/localization_slam/FAST_LIO` exists, no fake or empty point cloud, no headless pass as GUI acceptance, no UE screenshot as control-loop proof | `Docs/Design/架构.md`, `Docs/Workflows/sunray_ros1_current_runtime_lane.md`, `Docs/Workflows/sunray_ros1_execution_checklist.md`, `Docs/Index/sunray_migration_index.md` | Sunray ROS1 result dir, nonempty PointCloud2 sample, PX4/MAVROS/px4ctrl logs or metrics, Gazebo/RViz review manifest or blocker |
| Historical/future ROS2 / RViz2 / FAST-LIO | WSL ROS2 runtime, ROS MCP, RViz2, scripts | Future/reference native robotics transport/localization/map/planner review after explicit route reopening | No fake pointcloud/map/TF/odom, no keyboard pose, no setpoint publication without explicit live gate; not current Sunray ROS1 lane | `Docs/Workflows/ros2_runtime_setup.md` | ROS2 evidence bundle, TF/map/pointcloud checks, blocker packet |
| Git / DevOps | path-limited Git, GitHub plugin/CLI when available | Review, commit, push, issue/PR work, external reference drain | No broad staging, destructive history rewrite, destructive cleanup, or hidden ignore backlog without approval | `AGENTS.md`, `Docs/Workflows/documentation_governance.md` | path-limited diff/status, diff whitespace check, explicit staged-file review |
| GitHub issue / PR | GitHub plugin/skill, GitHub CLI when configured | Filing issues, reading PRs/issues, addressing comments | Do not publish external issue/PR without user approval when content is uncertain or private | GitHub skill, task-specific user scope | source links, draft issue text, user confirmation |
| Browser / web research | `web` search, Browser plugin for local web UI | Current external facts, docs, official sources, local web app testing | Use primary sources for technical claims; do not rely on stale memory for unstable facts | task-specific workflow, relevant skill | source links in final/report |
| Desktop window screenshot evidence | Win32 `PrintWindow`, screenshot scripts, Windows MCP/UIA read-only inspection | Background screenshot evidence for visible-but-covered windows, foreground/maximized review evidence, minimized-window restore/maximize/capture/minimize exception, blank capture triage | Observation only; screenshot permission does not authorize clicks, login, save, restart, send, approve, close, archive, or lifecycle actions; minimized windows are state evidence until restore is authorized | `Docs/Skills/Desktop/window-capture-evidence/SKILL.md`; MoSim script examples in `Docs/Index/api_index.md#12-desktop-window-screenshot-and-action-helpers` | screenshot path or skipped-minimized manifest, window metadata, blank/ambiguous retry note |
| Desktop window UI action control | Application API/MCP/CLI, UI Automation, Win32 handle/control messages, foreground or coordinate fallback | Explicitly authorized background click/control invocation, foreground click then minimize, safe low-risk UI operation, dry-run action planning | Do not infer permission from capability; high-risk controls need explicit task authority; stop on ambiguous target, blank/loading UI, or project workflow ban | `Docs/Skills/Desktop/window-ui-action-control/SKILL.md`; MoSim script examples in `Docs/Index/api_index.md#12-desktop-window-screenshot-and-action-helpers` | pre-action target proof, post-action readback, action evidence/blocker |
| Documentation secretary | `Docs/Index/*`, `Docs/Cache/*`, current documentation governance | Context consistency, dedup, candidate promotion, file organization, index repair | Does not define PMO runtime authority, accept engineering results, or silently rewrite policy | `Docs/Workflows/documentation_governance.md`, session memory workflow | reviewable patch, not hidden policy change |
| Capability cards and resolution | `Config/capabilities/capability_index.json`, `Config/protocol/templates/capability_template.yaml`, `Config/protocol/templates/capability_resolution.json` | Tool health, route ownership, fallback, claim ceiling, and duplicate-asset prevention before creating skills/workflows/scripts/checkers/MCP adapters | Do not infer health from past success; do not overclaim above health level; do not treat capability resolution as permission | `Docs/Workflows/tooling_assets_governance.md`; legacy protocol templates remain design/audit material only | `Scripts/quality/check_capability_resolution.py`; `Scripts/quality/check_capability_index.py`; legacy packet strict checks only when packet work is explicitly reopened |
| Review / evidence gate | `Results/runs/<run_id>`, result packets, review packages, screenshots, logs, metrics | Acceptance, blocker classification, claim boundary | Chat summary alone is not acceptance evidence | `Docs/Workflows/agent_project_operating_layers.md`, `Config/profiles/README.md`, domain workflows | `Scripts/quality/check_run_evidence.py`, evidence manifests, legacy packet checker only for packet audit |

## 3. Legacy / Explicit-Reopen Only Capabilities

These rows stay indexed so historical packets and old docs remain readable, but
they are not current execution routes.

| Capability Family | Concrete Surface | Use When | Forbidden Or Stop Actions | Owner Doc / Skill | Health Or Checker |
|---|---|---|---|---|---|
| Legacy Codex visible thread dispatch | `codex_app.send_message_to_thread`, `read_thread`, thread registry | Explicit legacy cleanup, historical packet review, or user-approved thread lifecycle audit only | Do not use for current single-thread engineering work; do not treat native send success as task success | `Config/protocol/communication_contract.md`, `Docs/Workflows/coagent_ops_patrol_workflow.md`, MoSim adapter `Docs/Workflows/mosim_visible_dispatch_adapter.md` | dispatch ticket under `Results/agent_packets/dispatch_tickets/`; `Scripts/quality/check_dispatch_ticket_slo.py` |
| Legacy Codex App thread lifecycle | `list_threads`, title/archive/fork/handoff tools when exposed | Route discovery, title repair, archive/fork work only when explicitly approved | Do not create/fork/archive/rename visible threads without PMO/user approval; do not use as normal task execution | `AGENTS.md`, archived notes via `Docs/Workflows/agent_orchestration.md` redirect only | registry review in `Config/legacy/department_threads.json` |
| Disposable subagent | `multi_agent_v1.spawn_agent` | Bounded parallel research, read-only audits, disjoint implementation slices, focused verification only if explicitly requested | Do not use as durable department, PMO authority, live GUI owner, hidden acceptance owner, or current default workflow | archived notes via `Docs/Workflows/agent_orchestration.md` redirect only | parent review; result must be integrated by the current owning thread before any claim |
| Legacy automation / recurring patrol | Codex App automation, patrol heartbeat | Explicitly configured reminder, post-restart sweep, or legacy audit only | Do not use as the normal single-thread control loop; do not make automation rewrite PMO policy silently | `Docs/Workflows/coagent_ops_patrol_workflow.md` | patrol packet, board update, dispatch ticket SLO |

## 4. Stable Capability IDs

Use stable ids in local goals, capability notes, task packets, and
`capability_resolution` blocks when a machine-readable route decision is
needed. Human-readable capability names may change; stable ids should remain
compatible unless the capability is explicitly superseded.

| Stable ID | Capability Row | Primary Existing Assets |
|---|---|---|
| `codex.visible_thread.dispatch` | Legacy Codex visible thread dispatch | Legacy/reference only: `Config/protocol/communication_contract.md`; `Config/protocol/templates/visible_thread_dispatch_packet.json`; `Config/protocol/templates/visible_thread_dispatch_ticket.json` |
| `codex.thread_lifecycle` | Legacy Codex App thread lifecycle | `AGENTS.md`; `Config/legacy/department_threads.json`; archived notes via `Docs/Workflows/agent_orchestration.md` redirect only |
| `automation.recurring_patrol` | Legacy automation / recurring patrol | `Docs/Workflows/coagent_ops_patrol_workflow.md`; Codex App `.codex/automations` user-profile storage |
| `hooks.preflight` | Native hooks / preflight | `Scripts/hooks/README.md`; `Scripts/hooks/preflight.py`; `Scripts/hooks/codex_native_hook.py` |
| `mworks.sysplorer_mcp` | MWORKS / Sysplorer MCP | `Docs/Skills/Mworks/mworks-mcp-operations/SKILL.md`; `Docs/Skills/Mworks/mworks-simulation-evidence/SKILL.md` |
| `mworks.window_review` | MWORKS window review and screenshot evidence | `Docs/Skills/Desktop/window-capture-evidence/SKILL.md`; `Docs/Skills/Desktop/window-ui-action-control/SKILL.md`; `Docs/Skills/Mworks/mworks-mcp-operations/SKILL.md` |
| `desktop.window.capture_evidence` | Desktop window screenshot evidence | `Docs/Skills/Desktop/window-capture-evidence/SKILL.md`; `Docs/Index/api_index.md#12-desktop-window-screenshot-and-action-helpers` |
| `desktop.window.ui_action_control` | Desktop window UI action control | `Docs/Skills/Desktop/window-ui-action-control/SKILL.md`; `Docs/Index/api_index.md#12-desktop-window-screenshot-and-action-helpers` |
| `ue.runtime_or_source` | Unreal Editor MCP | `Docs/Workflows/unreal_renderer.md`; `Docs/Skills/Unreal/mosim-unreal/SKILL.md`; S11 display/frontend enhancement only unless explicitly scoped otherwise |
| `sunray.ros1_runtime_review` | Current Sunray ROS1 / Gazebo / PX4 / MAVROS / RViz / MID360 | `Docs/Design/架构.md`; `Docs/Workflows/sunray_ros1_current_runtime_lane.md`; `Docs/Workflows/sunray_ros1_execution_checklist.md`; `Docs/Index/sunray_migration_index.md` |
| `ros2.runtime_review` | Historical/future ROS2 / RViz2 / FAST-LIO | `Docs/Workflows/ros2_runtime_setup.md`; explicit route reopening required |
| `git.devops` | Git / DevOps | `AGENTS.md`; `Docs/Workflows/documentation_governance.md`; path-limited Git workflow |
| `github.issue_pr` | GitHub issue / PR | GitHub skill or CLI when configured; task-specific user approval |
| `browser.web_research` | Browser / web research | `web` search; Browser plugin for local UI; task-specific workflow |
| `docs.secretary` | Documentation secretary | `Docs/Workflows/documentation_governance.md`; `Docs/Cache/design_intake/index.md` |
| `capability.cards` | Capability cards and resolution | `Config/capabilities/capability_index.json`; `Docs/Workflows/tooling_assets_governance.md`; `Config/protocol/templates/capability_template.yaml`; `Config/protocol/templates/capability_resolution.json`; `Scripts/quality/check_capability_resolution.py`; `Scripts/quality/check_capability_index.py` |
| `review.evidence_gate` | Review / evidence gate | `Config/profiles/README.md`; `Scripts/quality/check_run_evidence.py`; legacy packet checker only for packet audit |

## 5. Quick Selection Rules

- For ordinary MoSim work, choose the relevant workflow/skill/script/checker,
  not a legacy visible-thread route.
- If a task is a hard safety boundary, choose a hook/checker.
- If a task needs live external app state, choose MCP/plugin/native desktop
  route and prove the route's current health first.
- If a task asks "what tool should I use", read this index before guessing.
- If a row points to a skill or workflow, load only that specific target.
- If a task would create a new skill, workflow, script, checker, or MCP
  adapter, first add a `capability_resolution` block naming the existing
  assets checked and why they are insufficient.

## 6. Missing Work

This index is intentionally lightweight. Current machine-readable support:

- `Config/capabilities/capability_index.json` mirrors the stable capability
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
  legacy visible-thread preflight already invokes it through
  `Scripts/quality/check_agent_task_native_surface_gate.py` with `--strict`.
