# New Conversation Context

> Compact recovery context for a fresh Codex conversation in
> `C:\Users\HP\Desktop\MoSim`. This file stays short. Load detailed workflows
> only when the current task needs them.

Status: coordinating-thread operating entry, 2026-07-01 CST.

## 0. Startup Chain

Start every ordinary MoSim turn with:

```text
1. AGENTS.md
2. Docs/Workflows/new_conversation_context.md
3. Docs/Workflows/mainline_operations_board.md
4. Topic-specific workflow / skill / design docs only as needed
```

Do not load raw Codex session JSONL files, old chat dumps, retired agent-OS
internal docs, retired dispatch internals, or
`Docs/Workflows/agent_task_ledger.md` during normal startup. Use them only for
explicit legacy cleanup, packet audit, or historical trace-back.

## 1. Current Operating Mode

MoSim currently uses one active coordinating Codex thread for project work. It
can use official temporary subagents for independent bounded slices when
parallelism materially helps, while the coordinating thread retains scope,
integration, and final-claim ownership. Do not use the former multi-thread /
visible-department model as active workflow:

- no R1/R2/R3 route selection;
- no visible-thread dispatch queue;
- no patrol-owner bounded dispatch;
- no dispatch ticket SLO as a live PMO control loop;
- no routine thread patrol or dead-thread recovery policy inside project docs.

The current coordinating-thread rules are in:

```text
Docs/Workflows/single_thread_operating_model.md
```

Legacy multi-thread cleanup notes are review/cache material at
`Docs/Cache/agent_legacy/legacy_coagent_cleanup_plan_20260624.md`, not routine startup
workflow.

## 2. Current Product Direction

MoSim is an RflySim-like UAV simulation project. The main line is still robust
quadrotor modeling, control, simulation evidence, visualization, and report
output.

Current four-layer architecture:

| Layer | Current Role |
|---|---|
| Modeling / MIL-SIL | MWORKS/Sysplorer/Sysblock/Syslab model and controller design, model checks, simulations, generated artifacts, and metrics. |
| Flight Control | Exactly one active controller backend per run. Current P0 uses Sunray px4ctrl through PX4/MAVROS; MWORKS-generated C/C++ and PX4-native modules are later gated routes. |
| Runtime Plant / Sensors / HIL | CopterSim-like plant role: actuator/motor dynamics, truth state, sensors, faults, disturbances, and events. |
| Display / Scene / Review | UE, Gazebo/RViz, QGC/operator review, screenshots, videos, and visualization evidence. |

Claims must name the layer being validated. Do not convert a source/static
check, diagnostic smoke, screenshot, or headless output into final closed-loop
success.

## 3. Current Runtime Lane

The current active P0 review target is:

```text
ROS1 Noetic / Sunray / Gazebo Classic / PX4 / MAVROS / px4ctrl
Sunray150 + MID360 model and sensor chain
RViz point-cloud, trajectory, map, and frame review with nonempty evidence
board: Docs/Workflows/mainline_operations_board.md
architecture: Docs/Design/架构.md
runtime lane: Docs/Workflows/sunray_ros1_current_runtime_lane.md
execution checklist: Docs/Workflows/sunray_ros1_execution_checklist.md
```

Use Ubuntu-20.04 / ROS1 Noetic / YunZong Sunray Gazebo Classic / PX4 / MAVROS /
RViz as the current executable route. UE/frontend work belongs to S11 display,
experiment-platform, and video/review enhancement; it is not the current
control-loop authority. Do not use the old Ubuntu-22.04 / ROS2 Humble / PX4
x500 route, downloaded replacement FAST-LIO source, fake point clouds, or
equivalent-substitute runtimes as current evidence unless the user explicitly
reopens that architecture.

For Sunray ROS1 live runtime from Windows, do not use bare/default `wsl`.
Enter through `wsl -d Ubuntu-20.04` and run
`Scripts/sunray/check_sunray_ros1_runtime_preflight.sh` before launching Gazebo,
PX4, MAVROS, RViz, FAST-LIO, EGO, Diff-Planner, or swarm review. A wrong
Ubuntu/ROS/Gazebo runtime is an entry blocker, not a controller/planner/plugin
parameter issue.

## 4. How To Work

For each non-trivial task:

1. State the local goal.
2. Read only the smallest relevant docs/source/evidence.
3. Add logs/prints/checkpoints when debugging runtime behavior.
4. Use local docs/source first; if API/tool behavior is unclear, check official
   docs or targeted web/community sources.
5. Stop and ask the user before changing architecture, substituting a runtime,
   deleting large structures, or performing disruptive GUI/runtime actions.
6. Keep live/runtime waits bounded. Use the current runtime workflow or
   `Docs/Workflows/sunray_ros1_execution_checklist.md` for the active wait
   budget. Split longer work into small cases or background execution with
   short polling and partial evidence.
7. Save durable evidence in normal project paths under `Results/`, `Docs/`,
   `Scripts/`, or `Models/` as appropriate.

## 5. Current High-Value Documents

| Need | Source |
|---|---|
| Current PMO board | `Docs/Workflows/mainline_operations_board.md` |
| Coordinating-thread operating rule | `Docs/Workflows/single_thread_operating_model.md` |
| Document placement and archive rule | `Docs/Workflows/documentation_governance.md` |
| Legacy multi-thread cleanup review | `Docs/Cache/agent_legacy/legacy_coagent_cleanup_plan_20260624.md` |
| Agent execution/tool/guard/evidence layers | `Docs/Workflows/agent_project_operating_layers.md` |
| Current ROS1 Sunray/Gazebo/PX4/MAVROS/px4ctrl target | `Docs/Design/架构.md`, `Docs/Workflows/mainline_operations_board.md`, `Docs/Workflows/sunray_ros1_current_runtime_lane.md`, `Docs/Workflows/sunray_ros1_execution_checklist.md` |
| RViz point-cloud/trajectory/map review | `Docs/Workflows/sunray_ros1_current_runtime_lane.md`, `Docs/Workflows/sunray_ros1_execution_checklist.md` |
| UE/frontend display enhancement | `Docs/Workflows/unreal_renderer.md` |
| Sunray source/runtime index | `Docs/Index/sunray_migration_index.md` |
| Workflow index | `Docs/Index/workflow_index.md` |
| API/MCP/tool index | `Docs/Index/api_index.md` |
| Historical/recovery project memory index | `Docs/Index/project_work_memory_index.md` |
| MWORKS skills | `Docs/Skills/Mworks/` |
| UE workflow | `Docs/Workflows/unreal_renderer.md` |
| Pre-submit check | `Docs/Workflows/pre_submit_check.md` |

## 6. Legacy Multi-Thread Boundary

Visible-thread packet workflows, department routes, patrol/recovery docs, and
dispatch-ticket SLO material are legacy reference after 2026-06-24. Keep them
out of ordinary startup unless the user asks to audit, archive, or delete
them.

Executable paths such as hooks, checkers, protocol templates, skills, and
quality scripts must not be deleted until a separate dependency audit proves
they are unused or updates every reference.
