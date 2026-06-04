# New Conversation Context

> Purpose: give a fresh Codex conversation enough current context to continue
> MoSim work without loading the old 2 GB chat transcript.

Status: current recovery entry, 2026-06-04 CST.

This file records only current effective decisions and known rejected routes.
It does not promote old chat history by itself. If a newly opened conversation
finds a historical claim that is not represented here or in the linked source
documents, route it through `Docs/Workflows/session_memory_migration.md` before
using it as project truth.

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

## 2. Current Product Direction

MoSim is being developed as an RflySim-like UAV simulation system with strict
authority boundaries:

| Layer | Authority | Current Rule |
|---|---|---|
| MWORKS/Sysplorer/Syslab | dynamics, controller, planner, truth, metrics, report evidence | This is the formal simulation source. |
| UE5 / MoSimSceneLibrary | high-quality scene rendering, UAV visual, camera, video, sensor/collision oracle | UE must not decide controller/planner success. |
| ROS2 / RViz2 / FAST-LIO | LiDAR/IMU transport, TF, localization/map/planner review windows | Use native robotics windows, not HTML/browser point-cloud demos. |
| CoAgent / WeChat | sparse progress and human-intervention channel | Useful but not the current MoSim technical mainline. |

Primary architecture references:

```text
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

Main file:

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

WeChat is the default sparse out-of-band progress/intervention channel when it
is working. It is not proof and must not mirror transcripts or logs.

Gateway route:

```text
CoAgent/gateway/cc_connect_weixin.py
```

If WeChat send fails, diagnose once according to `AGENTS.md` and record the
failure under `Results/coagent_gateway/`; do not retry in a tight loop.

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
