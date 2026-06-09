# New Conversation Context

> Compact recovery context for a fresh Codex conversation in
> `C:\Users\HP\Desktop\MoSim`. This file should stay short; load detailed
> workflows only when the current task needs them.

Status: current recovery entry, 2026-06-09 CST.

## 0. Startup Boundary Summary

Executable details live in:

- `Docs/Workflows/coagent_ops_patrol_workflow.md` for CoAgentOps patrol,
  bounded dispatch, visible-thread refresh, dead-thread recovery,
  approval/review/provider surfaces, MWORKS window classification,
  email-before-restart, R2/R3 failover, and semantic-boundary state classes.
- `CoAgent/dispatch/communication_contract.md` for cross-thread packets,
  dispatch ticket SLOs, `native_surface_gate`, `semantic_boundary`,
  return/blocker paths, department-local planning fields, and domain gates.
- `Docs/Workflows/mainline_operations_board.md` for the current PMO operating
  board, P0 partition state, dispatch SLO watchlist, ops/recovery state, and
  support-lane state.
- `CoAgent/dispatch/department_threads.json` for current visible routes,
  refresh-only watchlist, default model/thinking settings, and R2/R3 routing
  constraints.

Current short rules:

1. Work only inside `C:\Users\HP\Desktop\MoSim` unless the user explicitly
   approves a named infrastructure exception.
2. PMO owns priority, scope, acceptance/rejection, final integration,
   visible-thread lifecycle decisions, manual/GUI decisions, and restart
   decisions.
3. CoAgentOps owns patrol/recovery and bounded pre-authorized P0 dispatch only
   within the workflow. It may update only fixed board areas: P0 partition
   state, Dispatch SLO watchlist, Ops/recovery state, and Support lane state.
4. Dispatch only to current `status=active_visible` routes in
   `CoAgent/dispatch/department_threads.json`.
5. Cross-thread work needs `native_surface_gate`, `semantic_boundary`,
   `expected_return_path`, and `blocker_return_path`; non-trivial work also
   needs department-local goal and `subagent_plan` fields.
6. Treat approval/review/provider UI and `view_refresh_required` before
   dead-thread recovery. Native send/read success alone is not recovery
   evidence.
7. Sparse Chinese email is the default user-notification route. Deleted WeChat
   gateway/message-path threads are historical only.
8. MWORKS routine activation/window patrol belongs to CoAgentOps. Graphical,
   layout, wiring, Smart Layout, result-window, and animation review routes to
   MWORKS R2 when a real review artifact exists.
9. `MoSim｜Codex 上下文维护部`
   (`019eab73-c5bc-7740-a6d1-5e0541bdb0c5`) is the current
   documentation-secretary/context-maintenance route. `MoSim｜文档秘书部`,
   R-suffixed context-maintenance titles, and knowledge-secretary titles are
   alias/history only.
10. `019de24d-e993-72c0-a0b2-caf2ac8ac85e` is a refresh-only non-MoSim watch
    target after Codex App/PC restart. It is not a MoSim dispatchable route.

## 1. Read Order For A Fresh Conversation

Start with this short chain:

```text
1. AGENTS.md
2. Docs/Workflows/new_conversation_context.md
3. Docs/Workflows/mainline_operations_board.md
4. CoAgent/dispatch/department_threads.json
5. Docs/Index/project_work_memory_index.md when work-history context is needed
6. PROGRESS.md only for newest active entries, not as a full transcript
7. Docs/Workflows/agent_task_ledger.md only when the board or packet requires trace-back
8. Topic-specific workflow/design/skill docs
```

Do not read raw Codex session JSONL files or old chat dumps as the first
recovery route. Historical claims not already represented in current source
documents must go through `Docs/Workflows/session_memory_migration.md` before
they become project truth.

The long-session migration is cache-first and three-round-gated. When a task
needs old conversation coverage, start from these indexes instead of raw JSONL:

```text
Docs/Cache/session_memory_migration/00_index/coverage_matrix_20260604.md
Docs/Cache/session_memory_migration/03_round3_disposition/round3_promotion_rejection_map_20260604.md
Docs/Cache/session_memory_migration/00_index/completion_audit_20260604.md
Docs/Cache/session_memory_migration/02_round2_review/
```

These files do not certify every old chat line. They record current-evidence
review and promote/reject/cache-only disposition for identified important
topics.

## 2. Current Product Direction

MoSim is being developed as an RflySim-like UAV simulation system with strict
authority boundaries:

| Layer | Authority | Current Rule |
|---|---|---|
| MWORKS/Sysplorer/Syslab | Dynamics, controller, planner, truth, metrics, report evidence | Formal simulation source. |
| UE5 / MoSimSceneLibrary | High-quality scene rendering, UAV visual, camera, video, sensor/collision oracle | UE must not decide controller/planner success. |
| ROS2 / RViz2 / FAST-LIO | LiDAR/IMU transport, TF, localization/map/planner review windows | Use native robotics windows, not HTML/browser point-cloud demos. |
| CoAgent / notification glue | Sparse progress, recovery packets, user-intervention channel | Support infrastructure, not the technical mainline. |

Current agent/runtime entry point:

```text
primary Codex conversation/config/history: Windows-native Codex under C:\Users\HP\.codex
project workspace: C:\Users\HP\Desktop\MoSim
WSL runtime lane: ROS2, RViz2, FAST-LIO-family, rosbridge, Linux-native robotics tools
```

Do not move ROS2/FAST-LIO execution into Windows-native PowerShell unless a
later workflow explicitly approves a Windows ROS route.

## 3. Current Route And Dispatch State

Use the board, registry, and packets as current truth:

```text
Docs/Workflows/mainline_operations_board.md
CoAgent/dispatch/department_threads.json
Results/agent_packets/
```

Current routing highlights:

- MWORKS, ROS2, and UE now have R1/R2/R3 route sets in the registry.
- R2 is the first safe failover lane when R1 is stale/dead/blocked and a safe
  static or diagnostic task exists.
- R2 default task classes are `source_static`, `diagnostic_only`,
  `packet_contract_fix`, `rule_sync_only`, and `checker/review`.
- R2 must not perform live MWORKS, live ROS2/RViz/FAST-LIO, UE runtime/build/
  editor, GUI clicks, login/authorization/save/restart, or setpoint
  publication under the default failover rule.
- R3 is reserve capacity only. PMO proposes or approves R3 after R2 failover
  still leaves a P0 partition idle/blocked long enough that reserve static,
  diagnostic, checker, or review capacity is useful.

## 4. Current Geometry And Dynamics Pointers

Accepted Sunray150 geometry comes from:

```text
Results/unreal_scene_mapping/sunray150_dae_assembly_parameters_20260604.json
```

Effective rotor centers used by MWORKS/SDF geometry:

| Rotor | Role | Position in body frame, m |
|---|---|---|
| rotor_0 | front-right | `(0.053745, -0.05374, -0.014052)` |
| rotor_1 | back-left | `(-0.053761, 0.05376, -0.014052)` |
| rotor_2 | front-left | `(0.053746, 0.053759, -0.014052)` |
| rotor_3 | back-right | `(-0.053761, -0.053739, -0.014052)` |

Other current geometry candidates:

```text
front camera: (0, 0.1032, 0.0185, 0, 0, 0)
down camera:  (0, 0.0145, -0.0263, 0, 1.5707963, 3.14)
base collision box pose: (0, 0.001574, 0.044965, 0, 0, 0)
base collision box size: (0.211502, 0.214651, 0.16193)
```

These values changed geometry only. They did not change mass, inertia, motor
constants, thrust constants, controller gains, timing, or identified-parameter
status.

Formal package ownership:

```text
References/MWORKS/QuadrotorModel/package.mo
  -> official/upstream baseline and regression reference.

Models/MoSimQuadrotorModel/package.mo
  -> project-owned formal Sunray150/MoSim quadrotor package.

Models/QuadrotorExperiments/package.mo
  -> legacy experiment pool and compatibility source.
```

Current dynamics boundary:

- `QuadrotorModel.Mechanics.QuadChassis` is still a simplified plant seed.
- Current nominal body parameters include `m=1.0`, `Ixx=0.0085`,
  `Iyy=0.0085`, `Izz=0.012`; rotor inertias and current thrust seed are
  documented in `Docs/Workflows/identify_quadrotor_parameters.md`.
- `lift_cofficient=0.000854858` comes from Sunray
  `motorConstant=8.54858e-06` scaled by `rotorVelocitySlowdownSim^2=100`.
- Missing or weak dynamics include explicit command-to-speed mapping, motor
  lag, yaw reaction torque, rotor gyroscopic moment, body drag, angular
  damping, and contact/fault parameter layers until model text and simulation
  evidence prove otherwise.
- RflySim is local structure reference only:
  `References/RflySim/RflySimAdv3Full/4.HILApps/RflySimAPIs/RflySimAPIsPers.zip`.
  Use it to design wrappers or experimental chassis structure; do not copy
  RflySim sample parameters into Sunray150 truth.

## 5. Current MID-360 Boundary

Do not collapse these into one number:

```text
mechanical mount pose
point-cloud coordinate origin
built-in IMU position
FAST-LIO extrinsic_T
Gazebo/Sunray ray-sensor pose
```

Current confirmed Livox manual fact:

```text
MID-360 built-in IMU position in point-cloud frame:
(11.0, 23.29, -44.12) mm

FAST-LIO LiDAR pose in IMU body frame if axes are aligned:
[-0.011, -0.02329, 0.04412] m
```

Do not write a DAE mechanical mount center directly into FAST-LIO extrinsics.
Any MID-360 extrinsic change requires a separate coordinate-frame review.

## 6. Current MWORKS Boundary

Current MWORKS GUI/activation operating split:

```text
CoAgentOps 10-minute automation
  -> routine MWORKS/Sysplorer/Syslab activation and window-health patrol
MWORKS R1/R2 engineering departments
  -> model/check/simulation/layout evidence, referencing the latest patrol
PMO or CoAgentOps
  -> foreground/maximized review or official login/license recovery when needed
```

Rules:

- A visible `[教育版]` title is not activation proof, but it is not a standalone
  blocker.
- Background screenshots are useful for ordinary layout/result review; hidden
  login/license panes require foreground or maximized target-main-window
  evidence.
- If CoAgentOps audit finds no reusable MWORKS/Sysplorer/Syslab main window,
  it should open MWORKS directly and recheck instead of only reporting a
  missing-window blocker.
- Live MWORKS work still needs task-local engineering evidence such as `.mo`,
  `check_model`, `SimulateModel`, native result/`.msr`, metrics, screenshots,
  or wiring observations as applicable.

## 7. Current UE / ROS2 / FAST-LIO Boundary

Rejected product routes:

- keyboard/grid-cell pose movement;
- fake/static point clouds;
- toy 2D grid maps as UAV local maps;
- browser/HTML point-cloud review as active evidence;
- hand-polishing RViz display parameters while the UAV/sensor stack is wrong.
- primitive UAV, giant cylinder, cube/cylinder fallback, MWORKS STL runtime
  animation, procedural runtime vehicle mesh, and simple whole-aircraft color
  passes as final Sunray150 vehicle review evidence.
- opening `.blend` through Windows file association, Ansys, or Visual Studio
  Blend routes after wrong-app dialogs.

Current accepted direction:

```text
MWORKS continuous truth/state
  -> UE scene/sensor oracle
  -> ROS2 LiDAR/IMU/TF
  -> native FAST-LIO / RViz2 windows
  -> truth-error and topic-rate evidence
```

UE vehicle visual state:

- DAE-derived geometry/assembly is the source route.
- The current accepted visual propeller basis is the three-blade
  `sunray_cw.stl` source under the Sunray150-with-MID360 local assets.
- Material/texture realism is not final until component close-ups are reviewed:
  MID-360, carbon frame, screws/standoffs, cameras, electronics/connectors/
  cables, motors/propellers, battery/payload, and landing gear/guards.

Factory Gate B / FAST-LIO state:

- Current Factory Gate B evidence opens manual UE/RViz review only.
- It does not prove final controller integration, planner performance, scene
  acceptance, product completion, or closed-loop runtime success.

Before making UE/ROS2/FAST-LIO runtime claims, read only the relevant workflow:

```text
Docs/Workflows/unreal_renderer.md
Docs/Workflows/ros2_runtime_setup.md
Docs/Design/09_UE_ROS_MWORKS无人机仿真架构重构.md
```

Do not declare `planner_ready`, `closed_loop`, runtime success, controller
performance, or final material/scene acceptance without the declared evidence
gate.

## 8. Current CoAgent Boundary

CoAgent is MoSim-specific support glue for packet formatting, registry checks,
result import, evidence validation, sparse notifications, bounded P0 queue
dispatch, and recovery audit. It is not an independent product-management
authority.

Visible threads are durable department surfaces, not disposable sub-agents.
Disposable sub-agents may be used only for bounded task-local research, review,
or independent checks when the packet records objective, scope, stop condition,
and returned evidence.

Deleted WeChat routes:

```text
019e8358-86b4-7070-8fd6-a2b4f4d2af97 = MoSim｜WechatCodex
019e9c7d-a8bd-7dd1-ad94-6feef5a07e9c = MoSim｜微信网关运维部
```

Both are historical only under the current email-only notification policy.

## 9. Current Best Next Engineering Moves

Recommended next work in a fresh conversation:

1. Start from the board, not from old chat memory.
2. Pick one active P0 partition and read its workflow/design doc.
3. If working on MWORKS dynamics, create or validate a RflySim-style wrapper or
   chassis evidence gate before replacing the baseline.
4. If working on UE vehicle visuals, keep geometry locked and review materials
   component by component.
5. If working on FAST-LIO, start from latest same-source/body-frame evidence
   and keep native RViz2/truth-error gates.
6. If a historical claim appears useful, route it through session-memory
   migration and current-file verification before promotion.

## 10. Codex Native Feature Use

Prefer Codex-native surfaces before expanding CoAgent:

| Need | Preferred Surface |
|---|---|
| Hard command/file guardrail | Native hook plus `CoAgent/hooks/preflight.py` |
| Durable project rule | `AGENTS.md` |
| Task-specific procedure | One workflow or skill loaded on demand |
| Live GUI/web/private-tool operation | Native plugin/app/MCP/Browser/Windows MCP |
| Recurring health check | Codex App automation or verified scheduler |
| Durable specialty context | Visible Codex thread with result/blocker packet |
| Bounded parallel research/review | Disposable sub-agent with explicit scope |

Foreground desktop caution: Windows MCP screenshot/snapshot observes the
active desktop. Use UI Automation, PowerShell, app APIs, or project-local
evidence scripts first; use visible desktop screenshots only when explicitly
authorized or when the workflow requires them.

Email notification format: short Chinese status only. Keep file paths, JSON
names, logs, and raw evidence details in packets and project files. Routine
completion can use `【MoSim 进度】`; manual intervention, incident, auth/license,
GUI crash, or dead-thread messages should use
`!!! MoSim 需要人工介入 !!!`.
