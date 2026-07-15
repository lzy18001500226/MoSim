# UE / Frontend Visualization Workflow

> Current short entry for UE-related MoSim work. The former long Unreal
> renderer workflow is archived at
> `Docs/Cache/legacy_workflows/unreal_renderer_full_20260624.md`.

Status: support-only workflow, 2026-07-01 CST.

## Current Scope

Use this file only when the task explicitly asks for:

```text
S11 display or frontend work
UE scene review
video/review material
source-static UE checks
explicitly authorized Unreal Editor work
Factory L2 static map import or UE Global Overview attitude trails
```

For UE bridge design or implementation, use
`Docs/Design/架构/04_展示与实验平台/UE渲染镜像桥接方案.md` first. The
current first implementation target is a one-way rendering mirror from
Gazebo/PX4/MAVROS/ROS1/Sunray evidence into UE display, not a UE-owned
simulation/control loop.

For the first official UE map, use
`Docs/Design/架构/04_展示与实验平台/Factory地图导入与全局态势视图.md`.
The current route is Factory L2 static import into Gazebo plus a UE Global
Overview view for live review. The authorized one-way live mirror consumes
ROS1 odometry and `/position_cmd` over UDP; UE remains display-only and does
not replace Gazebo/PX4/MAVROS/RViz evidence.

The Factory live-review default is a 100 Hz UDP state-mirror input. UE consumes
the newest frame at its own render rate; 100 Hz is not a 100 FPS claim. The
rate is intentionally bounded above the measured Factory world-truth source
rate while avoiding redundant 200 Hz JSON/UDP parsing. The default Factory
review hides both actual-flight and local-plan trails, applies each newest UAV
pose directly, and keeps the follow camera rigidly synchronized without a
second interpolation layer. This prevents display-only target chasing from
appearing as forward/backward airframe motion and does not alter Gazebo truth
or controller state. Rotor visuals
prefer measured relative angular velocity from `/gazebo/link_states`; when
that source is temporarily unavailable, MAVROS armed state may drive an
explicitly labeled visual-only spool fallback. Neither the 100 Hz mirror nor
rotor animation is actuator, controller, or flight-performance evidence.
For the repeatable UE-to-Gazebo static import procedure, use
`Docs/Workflows/ue_to_gazebo_static_scene_import.md` or the lightweight skill
entry `Docs/Skills/Unreal/ue-gazebo-static-scene-import/SKILL.md`.
After a static scene base is accepted, the first Sunray/Gazebo runtime gate is
`Docs/Workflows/factory_sunray_integration_gate.md`; do not jump directly to UE
Data Bridge before the bounded Factory/Sunray spawn and MID360 sensor gate.

UE is not the current plant, controller, localization, planner, or closed-loop
success authority. Current runtime evidence belongs to:

```text
Docs/Design/架构.md
Docs/Workflows/mainline_operations_board.md
Docs/Workflows/sunray_ros1_current_runtime_lane.md
Docs/Workflows/sunray_ros1_execution_checklist.md
```

If the task mentions current Sunray, ROS1, Gazebo Classic, PX4, MAVROS,
px4ctrl, RViz, MID360 point cloud, takeoff-hover-land, figure-8, or current
runtime review, stop reading this file and use the Sunray ROS1 lane instead.

## Work Split Gate

Before any UE work, classify the task into one or more lanes. Do not merge
these lanes into one vague "UE map" task:

| Lane | Typical Request | First Document | Minimum Output |
|---|---|---|---|
| Scene Base | Factory asset export, Gazebo static import, collision/semantic map, alignment | `Docs/Workflows/ue_to_gazebo_static_scene_import.md`; `Docs/Design/架构/04_展示与实验平台/Factory地图导入与全局态势视图.md` | source asset chain, Gazebo/RViz map artifacts, alignment report, review bundle |
| Data Bridge | UE should show real run state, per-UAV pose, trajectory trails, live/replay data | `Docs/Design/架构/04_展示与实验平台/UE渲染镜像桥接方案.md` | `ue_render_frame.jsonl` or live sidecar stream plus `mosim.ue_render_stream_manifest.v1` |
| Runtime Display | UE Global Overview, third-person views, attitude trails, camera/video display | `Docs/Design/架构/04_展示与实验平台/UE渲染镜像桥接方案.md` | display actor/component driven only by the Data Bridge stream |
| Evidence Export | screenshots, videos, manifests, review packets | this workflow plus the bridge/map design docs | evidence bundle tied back to ROS/Gazebo/PX4/RViz/log/metrics evidence |

Execution order:

```text
If the task is UE runtime display:
  1. prove T0 replay first from an existing run bundle;
  2. then use the existing T1 live sidecar at the declared review rate when
     explicitly needed;
  3. bind the stream to Factory or another Scene Base only after manifest fields are known.

If the task is Factory map import:
  1. use UE source assets and mature/export tools;
  2. produce L2 static import review evidence;
  3. do not claim UE runtime display until Data Bridge evidence exists.
```

Scene Base and Data Bridge may proceed in parallel. If they conflict, prefer
the Data Bridge contract for runtime display, because a near-lossless Factory
map without real state input is only an empty display stage.

Stop and return a blocker instead of improvising when:

```text
UE source assets cannot be exported by an official or mature tool;
no existing run bundle or authorized live topic source is available for Data Bridge;
no stream manifest can be produced;
the requested action would make UE publish control, planner, PX4 mode, or truth feedback.
```

## Allowed Work

Allowed when explicitly scoped:

```text
inspect UE source/static assets
inspect UE workflow or build scripts
implement the one-way UE rendering mirror after the bridge design contract is satisfied
prepare Factory L2 static import review assets and alignment reports
implement UE Global Overview attitude trails with configurable trail sampling
prepare scene review or video-review material
run bounded Unreal MCP probes after live/editor scope is authorized
record UE/frontend blocker with exact missing precondition
```

## Forbidden Claims

Do not claim any of the following from UE screenshots, source-only checks,
command echo, or scene review alone:

```text
controller success
PX4/MAVROS/px4ctrl success
localization success
planner readiness
FAST-LIO acceptance
closed-loop success
competition runtime acceptance
```

## Evidence Rules

For source/static UE work, save the changed files, validator output, and exact
claim boundary.

For live UE/editor work, first prove the task explicitly authorizes live/editor
scope, then capture the command, window/editor evidence, output bundle, and
post-action readback. A nonblank screenshot is only visual evidence; it is not
runtime authority.

## Native Mapping Window Policy

MoSim uses separate native review surfaces:

| Surface | Role |
|---|---|
| Unreal / `MoSimSceneLibrary` | rendered scene, vehicle visual, camera/sensor oracle, review media |
| RViz / RViz2 or equivalent native robotics viewer | active point-cloud, TF, map, odometry, trajectory, and FAST-LIO-style review |
| HTML report preview | offline report artifact only; never the active point-cloud/map review surface |

The operator-facing default is split RViz windows:

```text
RViz planning/grid window
RViz point-cloud/FAST-LIO window
RVIZ_PROFILE=split
```

Hard implementation constraints:

- Global scene truth stays hidden from the planner; it is a validation oracle,
  not runtime planner input.
- Browser or HTML point-cloud previews may be generated only as offline report
  artifacts or dry-run fallbacks, not active runtime evidence.
- UE screenshots can support display review, but they cannot replace RViz,
  topic/log, map, TF, or metric evidence for current Sunray ROS1 runtime work.
- Gazebo GUI is a diagnostic/manual-review window only; it is not the persistent
  foreground display for current Factory/RViz/UE review.
- `References/Lab/visualization/visualize_uav_trajectory` is a post-processing/demo
  material reference for time-lapse trajectory visuals, not a runtime pose
  source or trajectory-accuracy evidence source.

## Historical Notes

The archived workflow contains old ROS2, Factory, FAST-LIO, command-echo, and
UE sensor-bridge design history. Treat it as historical/reference material.
Do not import its route into current work unless the user explicitly reopens
that architecture and the current board/architecture docs are updated first.
