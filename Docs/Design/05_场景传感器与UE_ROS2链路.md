# 05 场景传感器与 UE/ROS2 链路

Status: source design, 2026-06-10.

## 1. Scene Role

UE5/MoSimSceneLibrary provides the visual and geometric world:

- Factory, Derelict, open field, gate, obstacle, or mission scenes;
- UAV visual mesh and component review;
- camera/depth/LiDAR raycast sources;
- collision and visibility queries;
- video and screenshot generation;
- operator-facing UE Experiment Console.

UE is a scene and sensor oracle. It is not plant truth and does not decide
controller or planner success.

## 2. Scene Truth Firewall

Allowed route:

```text
UE scene geometry
  -> camera/depth/LiDAR/collision observation
  -> SensorObservationLayer
  -> LocalizationAdapter / LocalMapAdapter
  -> PlannerAdapter
```

Rejected route:

```text
UE scene geometry
  -> hidden global map / obstacle truth
  -> PlannerAdapter
```

If a run intentionally uses global truth for debugging, it must label the
backend as `truth_debug` and cannot be final planning evidence.

## 3. Sensor Observation Profiles

Sensor profiles define what the simulated or replayed UAV can observe.

Minimum profile:

- truth state for visualization and sensor generation;
- IMU packet with timestamp, frame, bias/noise policy, and validity;
- LiDAR or depth observation with frame, extrinsic, point timing where
  applicable;
- optional camera frame for visual review;
- collision/visibility query output for safety and scene review.

MID-360-like profile:

- 10Hz baseline LiDAR unless an enhanced mode is explicitly measured;
- 200Hz IMU target;
- explicit LiDAR/IMU extrinsic;
- per-point timing or a declared approximation;
- frame and timestamp monotonicity checks;
- enough density/duration for localization and mapping gates.

## 4. ROS2 Integration Boundary

ROS2 is the formal robotics integration backend for the complete system route.
It should be used when MoSim claims credible access to established robotics
surfaces:

- TF;
- IMU and LiDAR topics;
- bags and topic-rate summaries;
- RViz2 native review;
- FAST-LIO-family localization;
- planner packages and local-map tooling.

ROS2 does not own plant truth. It transports and processes observations and
estimates.

Competition closure can still run MWORKS-first when the active claim is only
model/control evidence. If the active claim includes real-time point cloud,
3D voxel/local map, FAST-LIO, planner handoff, or RViz2 robotics review, ROS2
becomes part of the required evidence path. The system should still keep a
native internal API path possible so the core model/control interfaces are not
hard-coded to ROS2-specific variable names.

The full ROS2 integration and controller-backend migration route is defined in:

```text
Docs/Design/14_ROS2正式接入与控制器后端迁移设计.md
```

## 5. FAST-LIO Path

FAST-LIO does not require PX4. It requires coherent sensor and transform data:

```text
IMU + LiDAR + TF/extrinsic + timestamps + motion
  -> FAST-LIO
  -> odometry / path / cloud_registered
  -> truth-error or consistency evaluation
  -> local map / planner input
```

Acceptance cannot be based only on nonzero topics. It requires rate, timestamp,
frame, extrinsic, output, and error/quality evidence.

Current grounding boundary:

- source/static launch files and checkers can prepare the next evidence route,
  but they do not prove current localization or map/world grounding;
- `camera_init` to `map`, `world`, or `ue_world` grounding requires same-run
  raw `/tf` and `/tf_static` evidence that derives a non-fake transform chain;
- a run that only observes `camera_init->body` and no static edges remains
  blocked for planner/controller handoff, even if source files contain a future
  `map_frame` binding;
- future grounding evidence must reject arbitrary static transforms, header
  renames, fake odometry/maps/clouds/TF, keyboard pose, UE truth shortcuts, GUI
  display state, and alias-only `world` claims.

## 6. Local Map Path

The local map is a planner input derived from observations or estimates:

```text
SensorObservationLayer
  -> LocalizationAdapter
  -> registered cloud / occupancy / ESDF / obstacle set
  -> LocalMapAdapter
  -> PlannerAdapter
```

The local map must declare:

- representation;
- frame;
- update rate;
- source;
- validity;
- whether it is estimator-derived or truth-debug.

## 7. Planner Observation Boundary

PlannerAdapter may consume:

- localization estimate;
- local map;
- mission constraints;
- dynamic limits;
- safety constraints;
- optional debug truth only under a debug label.

PlannerAdapter may not consume:

- raw UE global scene geometry as final evidence;
- MWORKS plant truth as final localization evidence;
- hand-edited obstacle shortcuts that are not in the run config or evidence
  bundle.

## 8. UE Experiment Console

The UE console is a frontend. It can request:

- scene switch;
- controller switch;
- planner switch;
- wind/fault/sensor-profile changes;
- start/goal changes;
- recording or review actions.

All requests must go through:

```text
CommandPacket -> authority adapter validation -> RuntimeEcho -> UI display
```

The console must not:

- directly teleport the UAV as control output;
- write hidden global map truth into planner;
- label a run pass/fail without evidence;
- change plant/controller state without accepted echo.

## 9. Visual Review

Visual review proves visual/scene/sensor presentation quality. It does not by
itself prove:

- controller performance;
- planner correctness;
- localization accuracy;
- final closed-loop acceptance.

Visual review evidence should be linked into the run bundle with explicit
claim boundaries.
