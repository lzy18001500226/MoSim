# New Conversation Context

> Purpose: give a fresh Codex conversation enough current context to continue
> MoSim work without loading the old 2 GB chat transcript.

Status: current recovery entry, 2026-06-08 CST.

## 0. Startup Boundary Summary

This file is a compact recovery entry. Do not append every new incident rule to
this header. Detailed executable rules live in the linked workflow and packet
contracts:

- `Docs/Workflows/coagent_ops_patrol_workflow.md` for CoAgentOps patrol,
  bounded dispatch, dead-thread recovery, approval/review/provider surfaces,
  MWORKS window classification, email-before-restart, and semantic-boundary
  state classes.
- `CoAgent/dispatch/communication_contract.md` for cross-thread packets,
  `native_surface_gate`, `semantic_boundary`, return/blocker paths, department
  planning fields, and domain gates.
- `Docs/Workflows/org_operating_model.md` for current visible departments and
  owner boundaries.

Current short rules for fresh conversations:

1. Work only inside `C:\Users\HP\Desktop\MoSim` unless a named infrastructure
   exception is explicitly approved.
2. PMO owns priority, scope, acceptance, thread lifecycle decisions, and final
   integration. CoAgentOps owns patrol/recovery and bounded pre-authorized P0
   dispatch only within the workflow.
3. Dispatch only to current `status=active_visible` routes in
   `CoAgent/dispatch/department_threads.json`.
4. Cross-thread work needs `native_surface_gate`, `semantic_boundary`,
   `expected_return_path`, and `blocker_return_path`.
5. Treat approval/review/provider UI before dead-thread recovery. Native
   send/read success alone is not recovery evidence.
6. Sparse Chinese email is the default user notification route. Deleted WeChat
   gateway/message-path threads are historical only.
7. MWORKS routine activation/window patrol belongs to CoAgentOps; graphical,
   layout, wiring, Smart Layout, result-window, and animation review routes to
   MWORKS R2 when a real review artifact exists.
8. `MoSim｜文档秘书部` is the current documentation-secretary route. Old context
   maintenance or knowledge-secretary titles are alias/history only.
9. Read the active part of `Docs/Workflows/agent_task_ledger.md` and referenced
   packets; do not treat the full ledger as routine startup context.

## 1. Read Order For A Fresh Conversation

Start with this short chain:

```text
1. AGENTS.md
2. Docs/Workflows/new_conversation_context.md
3. Docs/Index/project_work_memory_index.md
4. PROGRESS.md only for the newest active entries, not as a full transcript
5. Docs/Workflows/agent_task_ledger.md only for active delegated tasks
6. Topic-specific workflow/design docs linked below
```

Do not read raw Codex session JSONL files or old chat dumps as the first
recovery route. The current long MoSim conversation file is too large and can
destabilize Codex App / VSCode plugin rendering.

## 1.1 Historical Context Coverage

The long MoSim conversation has been migrated into a cache-first recovery set
for the currently identified important topic set. A new conversation should be
able to recover project direction, accepted/rejected routes, current evidence
boundaries, and active workflow routing from:

```text
Docs/Cache/session_memory_migration/coverage_matrix_20260604.md
Docs/Cache/session_memory_migration/round3_promotion_rejection_map_20260604.md
Docs/Cache/session_memory_migration/completion_audit_20260604.md
Docs/Cache/session_memory_migration/round2_core_competition_report_docs_memory_20260604.md
```

This does not certify every line of an old Codex JSONL transcript. It means the
identified important topics have cache files, current-evidence review, and
round-3 promote/reject/cache-only dispositions. If a new conversation discovers
a useful historical claim that is not covered by the files above or by the
topic-specific docs, route it through `Docs/Workflows/session_memory_migration.md`
before treating it as project truth.

## 2. Current Product Direction

MoSim is being developed as an RflySim-like UAV simulation system with strict
authority boundaries:

| Layer | Authority | Current Rule |
|---|---|---|
| MWORKS/Sysplorer/Syslab | dynamics, controller, planner, truth, metrics, report evidence | This is the formal simulation source. |
| UE5 / MoSimSceneLibrary | high-quality scene rendering, UAV visual, camera, video, sensor/collision oracle | UE must not decide controller/planner success. |
| ROS2 / RViz2 / FAST-LIO | LiDAR/IMU transport, TF, localization/map/planner review windows | Use native robotics windows, not HTML/browser point-cloud demos. |
| CoAgent / WeChat | sparse progress and human-intervention channel | Useful but not the current MoSim technical mainline. |

Current agent/runtime entry point:

```text
primary Codex conversation/config/history: Windows-native VSCode/Codex under C:\Users\HP\.codex
project workspace: C:\Users\HP\Desktop\MoSim
WSL runtime lane: ROS2, RViz2, FAST-LIO-family, rosbridge, Linux-native robotics tools
```

Do not move ROS2/FAST-LIO execution into Windows-native PowerShell unless a
later workflow explicitly approves a Windows ROS route.

Codex native global hooks are configured for MoSim through:

```text
C:\Users\HP\.codex\hooks.json
CoAgent/hooks/codex_native_hook.py
CoAgent/hooks/preflight.py
```

The hook adapter acts only when the current `cwd` is inside this repository. It
can block hard tool-use risks and inject a concise startup reminder, but it does
not replace this file, `AGENTS.md`, task-specific workflows, result packets, or
manual review gates. If a new Codex surface asks to trust the hook, use `/hooks`
after verifying the paths above.

Primary architecture references:

```text
Docs/Design/10_架构边界与当前状态ADR.md
Docs/Design/12_MoSimQuadrotorModel模型归档与迁移计划.md
Docs/Index/project_work_memory_index.md
Docs/Design/00_系统总体设计.md
Docs/Design/09_UE_ROS_MWORKS无人机仿真架构重构.md
Docs/Workflows/unreal_renderer.md
Docs/Workflows/ros2_runtime_setup.md
Docs/Workflows/identify_quadrotor_parameters.md
```

## 3. Current Valid Sunray150 Geometry State

Current accepted geometry comes from the user-reviewed DAE/Blender assembly
manifest:

```text
Results/unreal_scene_mapping/sunray150_dae_assembly_parameters_20260604.json
```

Effective rotor centers now used by MWORKS/SDF geometry:

| Rotor | Role | Position in body frame, m |
|---|---|---|
| rotor_0 | front-right | `(0.053745, -0.05374, -0.014052)` |
| rotor_1 | back-left | `(-0.053761, 0.05376, -0.014052)` |
| rotor_2 | front-left | `(0.053746, 0.053759, -0.014052)` |
| rotor_3 | back-right | `(-0.053761, -0.053739, -0.014052)` |

Other current geometry candidates from the same manifest:

```text
front camera: (0, 0.1032, 0.0185, 0, 0, 0)
down camera:  (0, 0.0145, -0.0263, 0, 1.5707963, 3.14)
base collision box pose: (0, 0.001574, 0.044965, 0, 0, 0)
base collision box size: (0.211502, 0.214651, 0.16193)
```

Important limits:

- Geometry migration changed rotor/camera/collision geometry only.
- It did not change mass, inertia, motor constants, thrust constants,
  controller gains, timing, or identified-parameter status.
- Current values remain `source=SDF_migration` unless a later ULog/bench
  identification bundle proves otherwise.

## 4. Current MID-360 Boundary

Do not collapse these quantities into one number:

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

## 5. Current MWORKS Dynamics State

Formal package ownership:

```text
References/MWORKS/QuadrotorModel/package.mo
  -> official/upstream baseline and regression reference; do not destructively
     rewrite it for MoSim-specific plant experiments.

Models/MoSimQuadrotorModel/package.mo
  -> project-owned formal Sunray150/MoSim quadrotor package. New formal
     dynamics, mission, controller, planning, robustness, scene-trace, system,
     formation, and support entry points should move here.

Models/QuadrotorExperiments/package.mo
  -> legacy experiment pool and compatibility source. Keep old flat names as
     aliases during migration so existing scenario YAML, scripts, reports, and
     evidence bundles do not break in one step.
```

The first `MoSimQuadrotorModel` package skeleton is intentionally an
`extends`/alias layer. It classifies existing experiments under stable
project-owned categories before destructive file moves or class renames. Each
later migration batch must update references, keep source/provenance labels,
and pass targeted `check_model` evidence before the old alias can be retired.

Main baseline file:

```text
References/MWORKS/QuadrotorModel/package.mo
```

Current `QuadrotorModel.Mechanics.QuadChassis` is still a simplified plant:

| Item | Current State |
|---|---|
| mass/inertia | `m=1.0`, `Ixx=0.0085`, `Iyy=0.0085`, `Izz=0.012` |
| rotor inertias | `m=0.005`, `Ixx=9.75e-7`, `Iyy=0.000173104`, `Izz=0.000174004` |
| thrust | per-rotor `WorldForce`, `lift_cofficient=0.000854858` |
| coefficient provenance | Sunray `motorConstant=8.54858e-06` scaled by `rotorVelocitySlowdownSim^2=100` |
| missing/weak | motor lag, command-to-speed mapping, yaw reaction torque, rotor gyroscopic moment, body drag, angular damping, contact/fault parameter layers |

RflySim is local and should be used as structure reference:

```text
References/RflySim/RflySimAdv3Full/4.HILApps/RflySimAPIs/RflySimAPIsPers.zip
  RflySimAPIs/4.RflySimModel/3.CustExps/e0_AdvApiExps/1.inCtrlExt/1.Matlab/
    MulticopterNoCtrl.slx
    MulticopterNoCtrl_init.m
    MulticopterModel.zip
```

Do not replace Sunray150 parameters with RflySim sample parameters. Use RflySim
to migrate model structure into a new wrapper or experimental chassis first,
then validate hover/yaw/step response before replacing the baseline.

Current MWORKS GUI/activation operating boundary:

```text
CoAgentOps 10-minute automation
  -> owns routine MWORKS/Sysplorer/Syslab activation and window-health patrol
MWORKS R1/R2 engineering departments
  -> reference the latest patrol and focus on model/check/sim/layout evidence
PMO or CoAgentOps
  -> may bring the existing MWORKS window foreground/maximized for full
     screenshot review or official login/license recovery when needed
```

MWORKS graphical simulation, wiring/layout, Smart Layout, result viewer, and
animation review should be routed to MWORKS R2. For ordinary review, use the
current DPI-aware background full-window screenshot route plus written
observations. For activation/login/license/authorization acceptance, use a
foreground or maximized target main-window screenshot, then minimize/restore
after checking.

Do not make every MWORKS engineering dispatch spend its turn repeatedly proving
activation. A `[教育版]` title is not activation proof, but it is also not a
standalone blocker. Departments stop only when the current task or patrol shows
demo/login/authorization/error evidence, or when no recent patrol exists and a
live MCP/GUI operation cannot be safely checked. Login/license patrols need
maximized-window evidence when a hidden login pane is possible; minimized
background captures are not enough for that case. Use the existing maximized
foreground window first. If official login does not return or cannot complete
on the existing window, PMO/CoAgentOps may reopen MWORKS and log in through the
official UI as a bounded recovery.

## 6. Current UE Vehicle Visual State

Accepted:

- DAE-derived geometry/assembly is the source route.
- Three-blade `sunray_cw.stl` visual propeller route is the current accepted
  visual propeller basis.
- Primitive UAV, giant cylinder, cube/cylinder fallback, MWORKS STL runtime
  animation, and procedural runtime vehicle mesh are not accepted vehicle
  review evidence.

Pending:

- Material/texture realism is not final. Previous broad PBR/simple-color
  attempts were rejected or remain audit candidates.
- Before UE export/import is called final, component-specific material closeups
  must be reviewed: MID-360, carbon frame, screws/standoffs, cameras,
  electronics/connectors/cables, motors/propellers, battery/payload, landing
  gear/guards.

Authoritative workflow:

```text
Docs/Workflows/unreal_renderer.md
Docs/Skills/Unreal/sunray-pbr-material-workflow/SKILL.md
```

## 7. Current UE/ROS2/FAST-LIO State

Rejected product routes:

- keyboard/grid-cell pose movement;
- fake/static point clouds;
- 2D-only grid map as UAV local map;
- browser/HTML point-cloud review as active evidence;
- hand-polishing RViz display parameters while the UAV/sensor stack is wrong.

Current accepted direction:

```text
MWORKS continuous truth/state
  -> UE scene/sensor oracle
  -> ROS2 LiDAR/IMU/TF
  -> native FAST-LIO / RViz2 windows
  -> truth-error and topic-rate evidence
```

Factory Gate B has passed a headless same-source/body-frame FAST-LIO gate and
opens manual UE/RViz review only. It does not prove final controller
integration, planner performance, scene acceptance, or product completion.

Before making a FAST-LIO/current-runtime claim, read:

```text
Docs/Workflows/ros2_runtime_setup.md
Docs/Design/09_UE_ROS_MWORKS无人机仿真架构重构.md
Results/unreal_scene_mapping/factoryenvironmentcollect/
```

## 8. Current CoAgent And WeChat Boundary

CoAgent is not the immediate MoSim technical mainline. Existing CoAgent docs
are useful for task orchestration, but new runtime/transport/schema/department
expansion remains gated.

Current multi-conversation operation is PMO-authorized direct dispatch with
bounded CoAgentOps dispatch. PMO owns product authority, priority changes, user
questions, thread lifecycle, acceptance, and final integration. CoAgentOps may
send pre-authorized low-risk P0 packets to existing active visible departments
when the bounded-dispatch gate above is satisfied. Treat visible threads as
reusable department surfaces, not disposable subagents. CoAgent
dispatch/runtime tools are supporting infrastructure for packet formatting,
registry/visibility checks, result import, recovery, evidence validation, and
bounded P0 queue dispatch; they are not an independent dispatch-center
authority for ordinary MoSim work.

Every cross-thread task packet must include at least:

```text
request_id
origin_thread and origin_thread_id
target_thread and target_thread_id when known
expected_return_path
blocker_return_path
read/write scope
forbidden actions
definition_of_done
```

The return surface is the project file packet under
`Results/agent_packets/returns/` or `Results/agent_packets/blockers/`. Chat
replies and email/WeChat messages are useful notifications, but they are not the
durable return channel.

Notifications are sparse Chinese human-facing email summaries. WeChat is no
longer a routine project notification channel because outbound context can
expire after several hours; keep it for explicit gateway diagnosis,
user-requested retry, or gateway validation tasks only. Notification delivery is
not proof, and email must not mirror transcripts or logs.

Thread route distinction:

```text
019e8358-86b4-7070-8fd6-a2b4f4d2af97 = MoSim｜WechatCodex
  Deleted by user decision on 2026-06-08. Historical WeChat-side message path
  only. Not visible, not dispatchable, not a no-op target, and not an inbound
  refresh route under the current email-only notification policy.

019e9c7d-a8bd-7dd1-ad94-6feef5a07e9c = MoSim｜微信网关运维部
  Archived by user decision on 2026-06-07 after MoSim notifications moved to
  email-only, then deleted by user decision on 2026-06-08. Do not dispatch,
  patrol, no-op, recover, or treat absence of this thread as an outage unless
  the user explicitly reopens WeChat gateway diagnosis with a new scoped route.
```

Gateway route:

```text
CoAgent/gateway/cc_connect_weixin.py
```

If WeChat send fails during an explicit gateway-diagnosis task, diagnose once
according to `AGENTS.md` and record the failure under
`Results/coagent_gateway/`; do not retry in a tight loop or block ordinary
notifications on WeChat recovery.

## 9. Historical Routes Not To Resume

Do not continue these unless the user explicitly asks for an audit of the old
route:

| Route | Status |
|---|---|
| Reading the old 2 GB chat transcript as context | forbidden as routine recovery |
| Promoting old chat numeric parameters | forbidden without current file/result recheck |
| Manual propeller/radar tuning by eye as final assembly | superseded by DAE/source/manifest route |
| MWORKS STL / MWORKS animation as UE runtime UAV visual | rejected |
| Primitive cube/cylinder UAV fallback | rejected |
| Simple whole-aircraft coloring as "texture" | rejected |
| Opening `.blend` through Windows file association / Ansys / Visual Studio Blend routes | forbidden after wrong app dialogs |
| Directly treating RflySim parameters as Sunray150 truth | rejected |
| Directly treating DAE MID-360 mount pose as FAST-LIO extrinsic | rejected |
| HTML/browser point cloud as active mapping review surface | rejected |
| Fake point cloud / toy 2D grid / grid-cell movement | rejected except smoke/debug |
| Broad Git add over huge external trees | forbidden; use path-limited split batches |

## 10. Current Best Next Engineering Moves

Recommended next work after opening a new conversation:

```text
1. Do not resume from old chat memory.
2. Pick one active topic and read its workflow/design doc.
3. If working on dynamics:
   - create a new RflySim-style MWORKS wrapper/chassis first;
   - add motor lag and yaw torque before drag/gyro/contact;
   - validate hover, yaw, step, and short trajectory.
4. If working on UE vehicle:
   - use DAE-derived StaticMesh/FBX/GLB route;
   - keep geometry locked;
   - handle materials component by component.
5. If working on FAST-LIO:
   - start from latest same-source/body-frame Gate B evidence;
   - keep native RViz2 windows and truth-error gate.
6. If a historical claim appears useful:
   - add it to session-memory cache;
   - verify current files;
   - promote narrowly or mark rejected/superseded.
```

New conversations should treat this file as the short context pack and the
linked documents as the source of truth.

## 11. Codex Native Feature Use

Prefer Codex-native surfaces before expanding CoAgent:

| Need | Preferred Surface |
|---|---|
| Hard command/file guardrail | Native hook plus `CoAgent/hooks/preflight.py` |
| Durable project rule | `AGENTS.md` |
| Task-specific procedure | One workflow or skill loaded on demand |
| Live GUI/web/private-tool operation | Native plugin/app/MCP/Browser/Windows MCP |
| Recurring health check or reminder | Codex App automation or verified external scheduler |
| Durable specialty context | Visible Codex thread with result/blocker packet |
| Bounded parallel research/review | Sub-agent with explicit scope and stop condition |

Dead-thread recovery, heartbeat fail-close behavior, email-before-restart
order, CoAgentOps-self-dead PMO takeover, and replacement policy are executable
workflow rules in `Docs/Workflows/coagent_ops_patrol_workflow.md`. New
conversations should not copy or reinterpret that ladder here. The short
startup rule is: classify approval/review/provider surfaces first; native
send/read success alone is not recovery; email is audit/notification rather
than a recovery endpoint; CoAgentOps handles routine patrol and PMO handles
CoAgentOps-self-dead recovery only from a healthy interactive/user-triggered
turn. Detached cron and Windows watchdog routes remain removed unless the user
explicitly approves an incident-scoped exception.

Foreground desktop caution: Windows MCP `Snapshot` / `Screenshot` are not
background capture. They observe the user's active desktop and can catch
whatever the user is typing or viewing. For Codex++ restart and ordinary GUI
maintenance, use UI Automation/PowerShell/app APIs first; use visible desktop
screenshots only after warning the user or when explicitly authorized.
MoSim desktop GUI caution: Computer Use is deprecated for MoSim desktop GUI
monitoring, screenshots, recovery, and click workflows. Use Windows MCP,
Win32/UI Automation, and project-local PowerShell/Python scripts instead;
Browser remains the route for browser/local web targets.

Email notification format: keep the subject and body as short Chinese status
text. Do not copy concrete English file names, long paths, JSON/log names, or
raw evidence lists into user-facing notifications; those stay in
result/blocker packets and project evidence. Routine completion can use
`【MoSim 进度】`; manual intervention, incident, auth/license, GUI crash, or
dead-thread messages should use a clearly different header such as
`!!! MoSim 需要人工介入 !!!`.

Do not create CoAgent runtime machinery when a native Codex surface already
covers the need. CoAgent remains project glue for packets, evidence manifests,
gateway wrappers, recovery checks, and MoSim-specific orchestration conventions.
