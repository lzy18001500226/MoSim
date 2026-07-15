# UE/ROS/MWORKS UAV Simulation Architecture Replan

Date: 2026-06-02

Status: draft v2 after rejecting the hand-rolled keyboard-grid / synthetic
point-cloud path and auditing Sunray / FAST-LIO / Gazebo-style UAV flows.

Current compact boundary and Gate matrix entry:
`Docs/Design/10_架构边界与当前状态ADR.md`.

## 0. Long-Run Task Scope, 2026-06-02 CST

The user rejected the current toy path for the right reason: a UAV simulator
cannot be built by moving a pose one grid cell at a time and drawing synthetic
point clouds. That path cannot support controller tuning, LiDAR-inertial
localization, or planner validation. It is now restricted to smoke testing
ROS/RViz wiring only.

Current long-run objective:

```text
Study and reuse real UAV simulation stacks first
  -> PX4/Gazebo/RFlySim/AirSim/Sunray/Mid360/FAST-LIO
  -> derive MoSim module boundaries and timing contracts
  -> keep MWORKS as solver/controller/truth authority
  -> keep UE as renderer and sensor/collision oracle
  -> keep ROS2/RViz2 as robotics middleware and native review surface
  -> only then resume implementation
```

Priority task list:

1. Record the hard stop on grid-cell movement, fake/static point cloud, and
   2D-only grid as product routes.
2. Study flight-control and companion-computer flow: PX4/Gazebo/ROS2
   Offboard-style streamed setpoints, failsafe, odometry validity, and command
   timeout behavior.
3. Study Mid360/FAST-LIO: Livox scan pattern, per-point time, CustomMsg,
   LiDAR/IMU extrinsics, timestamp policy, and throughput.
4. Read Sunray source for its actual architecture:
   `external_fusion`, `sunray_control_node`, Mid360/FAST-LIO launch path,
   EGO 3D local map, B-spline trajectory, and `positionCmd2sunray`.
5. Compare RFlySim/AirSim/Gazebo window and process split: simulator/rendering
   window separated from ROS/RViz point cloud, TF, odometry, map, and planner
   review.
6. Produce a MoSim minimum closed-loop design for the already accepted Factory
   and Derelict scenes.
7. Mark modules as reuse, adapt, replace, or abandon.
8. Send milestone/blocker notifications through WeChat when available; if the
   gateway fails, diagnose immediately through the documented cc-connect
   session/context recovery path and report in the main conversation if it
   cannot be restored quickly.

Current WeChat status: restored after the 2026-06-02 gateway diagnosis. The
adapter now resolves empty session, `s1`, project-name alias, session JSON path,
and platform key to the active `weixin:dm:...` session. WeChat remains a sparse
human-intervention/progress channel only; do not mirror high-volume Codex
transcripts or tool output through it.

## 0.0 Architecture Validation Gates, 2026-06-02 CST

The current task is architecture validation and design closure, not display
tuning. The architecture is considered validated only when the following gates
are either passed or explicitly rejected with a replacement design.

### Gate A: MWORKS Controller Codegen and SIL

Goal: prove that MWORKS/Sysblock-generated C/C++ controller code can be used as
the MoSim controller runtime.

Required evidence:

- MWORKS/Sysblock model generates project-local C/C++ controller code.
- Generated code compiles without polluting evidence folders with build
  residue.
- Generated runtime exposes a stable adapter shape such as `Init`, `Step`,
  input struct, output struct, and sample time.
- Nonzero input sequence is injected into both MWORKS/Sysblock and generated C
  runtime.
- Outputs match sample-by-sample within the configured tolerance.

Current status: runtime compile and C harness smoke passed; zero-input SIL
passed; nonzero constant-input SIL for the PID demo also passed with MWORKS MCP
reference `cmd_sum.y` and generated C runtime output-order comparison. Stronger
time-varying input SIL remains open for final controller-runtime authority.

### Gate B: UE Truth, ROS2, Mid360/FAST-LIO Localization

Goal: prove that UE-derived sensor/truth data plus ROS2 transport can produce a
credible FAST-LIO localization/map state before any RViz/UE manual review.

Required evidence:

- Accepted scene uses continuous MWORKS truth/state, not grid-cell movement.
- IMU is physically coherent and high-rate; target is 200Hz.
- Mid360/Livox-like LiDAR includes dense points, per-point timing, line/tag or
  equivalent fields, extrinsics, and monotonic timestamps.
- ROS2 TF and topic rates are measured.
- FAST-LIO publishes nonzero registered cloud, odometry, and path.
- FAST-LIO trajectory is compared against truth; nonzero topics alone are not
  acceptance evidence.
- 3D local map/planner state is available in a native RViz2 or equivalent
  robotics window.

Current status: Factory dense input and nonzero FAST-LIO topics exist, but the
formal truth-error gate is not yet passed. The 9-10m RMSE class failure was
traced to an invalid mixed-source/world-frame input route: LiDAR frames,
IMU/state, and evaluation truth were not generated from one MWORKS trajectory,
and world-frame points were published as `base/mid360_link` body-frame points.
The corrected same-source/body-frame smoke route now produces nonzero FAST-LIO
topics and an evaluation of RMSE `1.019363m`, max error `1.437659m`, but this is
still above the formal RMSE threshold and used only about 6.2k points/frame.
The next Gate B step is a formal same-source body-frame Factory dataset at
accepted Mid360 density and enough duration, followed by the same headless
truth gate before any UE/RViz2 manual review.

2026-06-02 formal update: Gate B passed headlessly for Factory with the formal
same-source body-frame dataset. Evidence directory:
`Results/unreal_scene_mapping/factoryenvironmentcollect/fastlio_runtime_factory_mworks_body_formal_20260602_122033`.
The input probe recorded Livox `9.887Hz`, IMU `198.857Hz`, monotonic stamps,
and `15607..16515` points/frame. FAST-LIO recorded `/Odometry=80`, `/path=8`,
and `/cloud_registered=80`. Truth evaluation passed with RMSE `0.39454m`, max
position error `0.611542m`, and yaw RMSE `0.017802rad`. The current gate status
is `ready_for_manual_rviz_ue_review`. This only opens the manual review stage;
it does not close final controller integration, planner performance, or visual
acceptance.

### Gate C: System Closed-Loop Contract

Goal: finalize the role split and data contract so implementation does not
collapse back into ad-hoc demos.

Required design outputs:

- MWORKS/Sysblock/Syslab authority: solver, plant/control model, generated
  controller code, truth, metrics, report evidence.
- UE authority: scene rendering, camera, collision, and sensor oracle. UE does
  not decide controller/planner success.
- ROS2/RViz2 authority: TF, LiDAR/IMU transport, FAST-LIO, local 3D map, planner
  review windows.
- V6X/PX4/companion-computer boundary: deployment adapter, offboard/control
  messaging semantics, failsafe assumptions, and hardware-facing C/C++ route.
- Frequency contract: controller/setpoint 20Hz baseline, IMU 200Hz, LiDAR 10Hz
  baseline with 20Hz only after throughput and localization gates pass.
- Coordinate/time contract: frame names, transforms, timestamp source, per-point
  LiDAR offset semantics, and truth-vs-estimate comparison convention.
- Reuse/adapt/replace matrix for RflySim, Sunray, PX4/Gazebo, AirSim,
  FAST-LIO/Livox, and local project code.
- Manual review points and WeChat notification policy.

Current status: role split and many contracts are drafted; final closure depends
on Gate A nonzero SIL and Gate B localization-quality diagnosis.

## 0.1 Ten-Hour Real UAV Stack Catch-Up Task, 2026-06-02 CST

This task is the current mainline. Do not continue the simplified mapping demo
until these work items are either completed or explicitly blocked.

### Task Checklist

1. Flight-control and companion-computer baseline:
   - read PX4 Offboard and ROS2/uXRCE-DDS docs;
   - extract the continuous streamed-control contract, failsafe behavior,
     required estimator validity, and ROS2 message/version constraints;
   - translate the contract into MoSim terms: MWORKS controller/setpoint output
     at 20Hz, IMU at 200Hz, LiDAR baseline at 10Hz, optional enhanced LiDAR at
     20Hz only after throughput and localization gates pass.
2. Sunray/YunZong source audit:
   - read `uav_control_mid360.sh`, `sunray_uav_ego_mid360.sh`, and
     `sunray_uav_ego_sim.sh`;
   - trace `external_fusion`, `sunray_control_node`, `msg_MID360`,
     `mapping_mid360`, `sunray_ego_single_mid360`, and `positionCmd2sunray`;
   - record which nodes can be reused directly, which must be ported from ROS1
     to ROS2, and which only provide architectural reference.
3. Mid360 and FAST-LIO runtime route:
   - use Livox `CustomMsg` semantics with per-point timestamp/offset fields as
     the target input, not a generic display-only `PointCloud2`;
   - compare patching local `spark-fast-lio` against importing a known
     ROS2/Mid360-capable FAST-LIO candidate;
   - run only headless gates until `/cloud_registered`, odometry, path, TF, and
     truth-error metrics are nonzero and coherent.
4. RflySim/AirSim/Gazebo reuse boundary:
   - treat RflySim as the role-boundary reference: CopterSim/PX4 handles motion
     and control, Unreal/RflySim3D handles rendering/sensor generation, ROS/RViz
     handles point cloud and algorithm review;
   - compare Gazebo `ros_gz_bridge` and AirSim ROS wrapper topic/window split;
   - avoid copying their full runtime when a narrow bridge or contract is
     enough.
5. Factory and Derelict minimum closed-loop gate:
   - MWORKS continuous state/truth output;
   - 200Hz physically coherent IMU;
   - 10Hz Mid360-like dense LiDAR with per-point timing and extrinsics;
   - ROS2 TF and topic rates measured;
   - FAST-LIO output topics present and evaluated against truth;
   - 3D local map/planner-state topic available in RViz2;
   - UE rendered scene opens only after the headless data gate passes.
6. Notification and audit:
   - progress, blockers, and manual review requests should be sent through
     WeChat by default;
   - if cc-connect returns `ret=-2` or no active session, record one bounded
     failure in `Results/coagent_gateway/` and continue with file-based
     progress records instead of retrying in a loop.

### Acceptance for the Next User Review

The next manual review should not ask the user to judge point size, grid color,
or RViz layout. It should ask the user to verify:

- UE window: Factory or Derelict rendered scene, UAV body, continuous movement.
- FAST-LIO RViz2 window: dense live LiDAR input plus registered cloud, odometry,
  TF, and path.
- 3D map RViz2 window: local 3D occupancy/voxel map and planner state that move
  with the UAV.
- Evidence bundle: source labels, topic rates, timestamp monotonicity, extrinsic
  contract, FAST-LIO truth error, and known blockers.

## 1. Decision

Do not continue the current route where one script moves a pose by grid cells
and fabricates LiDAR/occupancy output. It is not a credible UAV simulation
architecture:

- motion is discrete and not controller-compatible;
- point cloud and map update are not tied to a real vehicle dynamics loop;
- the "grid map" was mostly a 2D `OccupancyGrid`, while UAV planning needs a
  3D local map representation;
- generated point clouds do not behave like FAST-LIO/Mid360 runtime data;
- performance tuning the fake path would not solve the real integration
  problem.

The correct main line is a continuous multi-rate system:

```text
MWORKS dynamics / controller / faults / wind / motor efficiency
  -> vehicle state, IMU, command/state truth

UE / MoSimSceneLibrary
  -> rendered scene, UAV body, camera, collision/sensor oracle

ROS2 runtime
  -> LiDAR, IMU, odometry, TF, FAST-LIO, local 3D map, planner, RViz2

RViz2 native windows
  -> FAST-LIO point cloud / odometry / path
  -> 3D grid or voxel map / local planner state
```

MWORKS remains the solver/controller authority. UE is a scene rendering and
sensor/collision oracle. ROS2 is the robotics middleware for LiDAR/IMU,
localization, mapping, planning, and native visualization.

2026-06-02 code-generation update: MWORKS/Sysplorer/Sysblock controller code
generation is now verified through the official Python API
`GenerateModelCode(modelName)`, not only by `TranslateModel`. The minimal
Sysblock controller `AWFF_PID_Sysblock_Demo` generated C sources under
`Results/codegen_probe/AWFF_PID_Sysblock_Demo_api/` and the generated sources
compiled with `gcc -std=c99 -Wall -Wextra -pedantic -c`. This makes generated
C/C++ controller runtime a credible MoSim path, but it must pass SIL
equivalence against MWORKS/Sysblock before it can become runtime authority.

The corrected role split is:

```text
MWORKS/Sysblock
  -> controller design, plant solve, formal truth, metrics, code generation

Generated C/C++ ControllerRuntime
  -> deployable controller wrapper, SIL, ROS2/PX4/V6X adapter

UE / MoSimSceneLibrary
  -> rendering, camera, collision and sensor oracle

ROS2 / RViz2
  -> LiDAR/IMU/TF, FAST-LIO, local 3D map, planner review
```

The current Sysplorer MCP `translate_model` wrapper still only calls
`TranslateModel(modelName)` and does not expose project-local C/C++ export.
The next MCP improvement is to wrap `GetModelCodeGenerationOptions`,
`SetModelCodeGenerationOptions`, and `GenerateModelCode`; details are recorded
in `Docs/Workflows/mworks_codegen_controller_runtime.md`.

2026-06-02 architecture source check: the MoSim plan should deliberately copy
the RflySim-style layering, not its solver implementation. RflySim separates
CopterSim motion/control, Unreal/RflySim3D scene simulation, QGroundControl
monitoring, MATLAB/Simulink automatic code generation, and Python/ROS
interfaces. MoSim maps those roles to MWORKS/Sysblock/Syslab for solver,
controller, truth, metrics, and generated C/C++ runtime; UE for rendering and
scene/sensor oracle; ROS2/RViz2 for middleware, FAST-LIO, 3D local mapping, and
planner review. AirSim and PX4/Gazebo remain bridge/contract references, not
the primary solver. The current MWORKS code-generation probe confirms this is
not only a conceptual split: a Sysblock controller can generate compilable C
sources, but every generated controller must pass SIL equivalence before it can
become MoSim runtime authority.

Hard design boundary:

```text
Grid resolution, keyboard step size, RViz marker size, or point-cloud display
parameters must never drive vehicle motion or controller tuning.
```

The vehicle moves only through continuous dynamics and controller state. A
manual keyboard command, if used for early review, must become a velocity,
position, acceleration, or yaw setpoint stream that the MWORKS/controller layer
consumes at the defined rate. It must not teleport the UAV pose.

The current reuse/adapt/replace matrix is:

```text
Results/unreal_scene_mapping/REAL_UAV_STACK_REUSE_MATRIX_20260602.md
```

Use that matrix to decide implementation order. In particular, do not spend
time polishing RViz point size, 2D grid displays, or keyboard-grid motion while
the FAST-LIO/Mid360 runtime and 200Hz IMU synchronization gates remain open.

## 2. Reference Architecture Findings

### 2026-06-02 Replan Findings

The earlier keyboard-step / 2D grid / static point-cloud prototype is now
classified as a smoke-only diagnostic. It must not be optimized into the
product path because it violates the basic UAV simulation contract: the vehicle
must move continuously under a controller and plant solver, while maps and
point clouds are sensor/planner state derived from that motion.

The credible architecture has to follow the same split used by PX4/Gazebo,
Sunray, AirSim, and RFlySim-style systems:

```text
high-fidelity renderer / scene oracle
  -> UE accepted scene, UAV mesh, camera, collision and raycast truth

flight dynamics and controller authority
  -> MWORKS model, controller, IMU/truth, wind/fault/motor-efficiency effects

robotics middleware and companion-computer stack
  -> ROS2 topics, TF, LiDAR/IMU sync, FAST-LIO, local 3D map, planner

native robotics review windows
  -> RViz2 point cloud / FAST-LIO / odometry / path
  -> RViz2 3D map / local planner state
```

This is not only a display choice. It defines the validation boundary:
rendered UE truth may be used as an oracle for collision and sensor generation,
but it must not be leaked into the planner as a known global map.

### PX4 / Flight Control

PX4's ROS2 integration uses uXRCE-DDS to bridge PX4 uORB topics into the ROS2
DDS graph. PX4 v1.14+ uses uXRCE-DDS, and PX4 recommends ROS2 Humble on Ubuntu
22.04 for current development.

Official PX4 ROS2 docs also show that offboard control is a streamed contract,
not a one-shot command. `OffboardControlMode` and `TrajectorySetpoint` are sent
periodically; PX4 exits offboard if the control-mode stream drops below about
2Hz. Our project should use 20Hz controller/setpoint output as the MoSim
contract, but it must still satisfy PX4-style continuous streaming semantics.

Important source:

- PX4 ROS 2 user guide:
  `https://docs.px4.io/main/en/ros2/user_guide.html`
- PX4 offboard mode / ROS2 examples:
  `https://docs.px4.io/main/en/flight_modes/offboard.html`

MoSim implication:

- even if PX4 is not in the first closed loop, the external-control interface
  must be a continuous streamed setpoint/control-mode contract;
- a 20Hz MoSim controller/setpoint stream is acceptable and comfortably above
  PX4's approximate 2Hz offboard-loss threshold, but missed timestamps and
  nonmonotonic clocks must be treated as control faults;
- if PX4 is introduced later, the ROS2 side must respect the matching
  `px4_msgs` / uXRCE-DDS message-definition contract.
- the architecture must include command timeout, localization validity,
  geofence/collision limits, and safe hover/land behavior as first-class
  controller-state-machine logic, not as RViz/manual-control conventions.

### Mid360 / LiDAR / IMU

Livox Mid-360 is not a generic spinning Velodyne. It has a non-repetitive
Livox scan pattern, typical point cloud frame rate of 10Hz, and about
200,000 points/s first return. The user target of 20Hz is acceptable as a
simulation/product target, but it should be documented as an enhanced simulated
sensor mode or split-scan mode, not as the default hardware spec.

Mid360 has built-in IMU support; user manuals report 200Hz IMU output. FAST-LIO
requires the point timestamps needed for motion undistortion, plus a coherent
LiDAR-to-IMU extrinsic and time offset policy.

Important source:

- Livox Mid-360 specs:
  `https://www.livoxtech.com/mid-360/specs`
- `https://www.manualslib.com/manual/2952267/Livox-Mid-360.html`
- `https://github.com/hku-mars/FAST_LIO`
- Local: `References/Lab/localization_slam/FAST_LIO/config/mid360.yaml`
- Local: `References/Sunray/simulation/sunray_simulator/launch_slam/mid360.yaml`

MoSim implication:

- the first hardware-faithful baseline should target 10Hz LiDAR frames and
  about 200k points/s overall, not a few hundred points/frame;
- the user-desired 20Hz LiDAR can be an enhanced simulation target, but then
  point density, time offsets, and FAST-LIO behavior must be measured rather
  than assumed;
- a useful Mid360 simulation must provide point coordinates plus per-point
  time offset, line, reflectivity/tag, LiDAR frame id, IMU frame id, and
  LiDAR-to-IMU extrinsics.
- the 20Hz enhanced-simulation mode should be documented as a MoSim product
  mode, not presented as the default hardware specification. It must pass a
  measured throughput gate and a localization-quality gate before it is used
  for controller/planner claims.

### FAST-LIO

FAST-LIO is not a visualization plugin; it is a LiDAR-inertial odometry runtime.
For Livox serial sensors it depends on Livox message data that carries
per-point timestamps. FAST-LIO's own README warns that Livox point timestamps
are important for motion undistortion and that software time sync should only
be enabled when external sync is unavailable.

Current local source status:

- `References/Lab/localization_slam/FAST_LIO` is ROS1/catkin.
- `References/Lab/localization_slam/FAST-LIVO2` is ROS1/catkin.
- `References/Lab/localization_slam/Point-LIO-point-lio-with-grid-map` is ROS1/catkin.
- Existing ROS2 candidate `spark-fast-lio` built under `Results/tmp`, but
  Factory runtime quality is currently degraded and cannot be claimed final.
- Existing Factory runtime recordings prove that the ROS2 FAST-LIO candidate
  does publish output topics, but quality fails: current Factory evaluations
  report RMSE around 9.8-10.2m and max error around 17.7-18.5m, with
  nonmonotonic odometry timestamp pairs in recorded runs.
- The later dense-Mid360 smoke exposed a stronger blocker: when configured as
  `lidar_type=1`, the current `spark-fast-lio` ROS2 candidate rejects the
  `PointCloud2` input path before producing any odometry/cloud output.

MoSim implication:

- Livox serial input should prefer Livox `CustomMsg` semantics, because
  FAST-LIO's upstream guidance depends on each point carrying a timestamp for
  motion undistortion;
- using ordinary `PointCloud2` without correct timestamp fields is acceptable
  for RViz display smoke, but not enough to claim FAST-LIO quality;
- a Livox-like `PointCloud2` field layout is still not enough if the selected
  FAST-LIO implementation does not actually parse Livox from `PointCloud2`;
- `time_sync_en` should stay false unless external synchronization is genuinely
  impossible, matching the local Mid360 configs;
- identity LiDAR/IMU extrinsics are allowed only for a controlled synthetic
  frame; final Sunray150 evidence needs measured or explicitly defined sensor
  mounting.

Evidence:

- `Results/unreal_scene_mapping/FASTLIO_FAMILY_COMPATIBILITY.md`
- `Results/unreal_scene_mapping/FASTLIO_RUNTIME_STATUS.md`
- `Results/unreal_scene_mapping/SPARK_FASTLIO_ROS2_CANDIDATE.md`
- `Results/unreal_scene_mapping/factoryenvironmentcollect/fastlio_runtime/FASTLIO_RUNTIME_EVALUATION.json`
- `Results/unreal_scene_mapping/factoryenvironmentcollect/fastlio_runtime_scan099/FASTLIO_RUNTIME_EVALUATION.json`
- `Results/unreal_scene_mapping/factoryenvironmentcollect/FASTLIO_MID360_RUNTIME_BLOCKER.md`

2026-06-02 09:05 CST executable update:

- imported/built a native ROS2 FAST-LIO candidate with `livox_ros_driver2`
  under `Results/tmp/fast_lio_ros2_import_ws`;
- added C++ ROS2 transport nodes under `Scripts/ros/mosim_dense_lidar_cpp`:
  `dense_lidar_replay_node`, `mworks_state_imu_replay_node`, and
  `livox_imu_probe_node`;
- replaced the Python double-subscriber input gate for dense Livox+IMU with
  the C++ `livox_imu_probe_node`, because Python deserialization of
  25k-point Livox frames distorted the observed 200Hz IMU rate;
- latest Factory headless run
  `Results/unreal_scene_mapping/factoryenvironmentcollect/fastlio_runtime_cpp_livox_headless_20260602_090500`
  passed the input gate:
  `/mosim/livox/lidar` about 18.68Hz, `/mosim/forward/imu` about 187.89Hz,
  24.5k-25.9k points/frame, Livox lines 0-3, per-point offset 0-49.998ms,
  and LiDAR/IMU latest stamp delta about -0.020s;
- FAST-LIO produced runtime output counts
  `/Odometry=172`, `/path=17`, `/cloud_registered=172`;
- truth evaluation still failed with position RMSE 9.576m and max error
  17.900m, so this is not acceptable localization evidence and must not
  trigger manual RViz/UE review.

This changes the active blocker from "FAST-LIO has no runtime output" to
"FAST-LIO output exists but is not truth-aligned enough for navigation or
controller claims". The next diagnostics must focus on LiDAR/IMU extrinsics,
coordinate frames, timestamp policy, scan-pattern replay, initialization
motion, and truth-alignment assumptions.

### Sunray / YunZong-like UAV Stack

Sunray already encodes a usable layering pattern. Relevant local scripts:

- `References/Sunray/scripts_sim/sunray_uav_ego_sim.sh`
- `References/Sunray/scripts_exp/sunray_uav_ego_mid360.sh`
- `References/Sunray/scripts_exp/uav_control_mid360.sh`

Observed stack:

```text
roscore
  -> simulator / PX4 / MAVROS
  -> external_fusion
  -> sunray_control_node
  -> terminal or waypoint control
  -> Mid360 message driver / FAST-LIO mapping
  -> EGO planner
  -> RViz
```

Important contracts extracted from Sunray:

- external localization is explicit (`external_fusion.launch`);
- control command topic is explicit (`/uav1/sunray/uav_control_cmd`);
- odometry timeout is a safety condition (`odom_valid_timeout=0.5`);
- EGO planner consumes odometry plus global-frame point cloud;
- EGO local grid is 3D and bounded by local update range, not a static 2D map;
- planning output is a B-spline converted into Sunray control commands.

This is the closest local reference for MoSim's architecture.

Local code-level details worth reusing:

- `References/Sunray/General_Module/sunray_uav_control/externalFusion/externalFusion.cpp`
  publishes PX4 state and odometry on a 0.01s timer and RViz path/mesh/TF on a
  0.1s timer. MoSim should mirror the separation between high-rate state and
  lower-rate visualization.
- `References/Sunray/General_Module/sunray_uav_control/uav_control/UAVControl.cpp`
  treats command timeout, geofence, odometry validity, control mode, takeoff,
  hover, landing, and command execution as controller-state-machine concerns.
  MoSim should not let a keyboard or planner node directly teleport the pose.
- `References/Sunray/General_Module/sunray_planner_utils/launch/sunray_ego_single_mid360.launch`
  configures a 3D local map with `grid_map/resolution=0.12`,
  local update ranges around 5.5m x 5.5m x 4.5m, and obstacle inflation. This
  is the right reference for the "3D grid map" review surface.
- `References/Sunray/simulation/gazebo_plugin/livox_laser_simulation/src/livox_points_plugin.cpp`
  already implements a Livox scan-pattern replay from `mid360-real-centr.csv`,
  and can publish either `PointCloud2` with Livox-like fields or Livox
  `CustomMsg` with `offset_time`.

Additional implementation lessons from the current source pass:

- `externalFusion.cpp` publishes PX4-like composite state and odometry on a
  0.01s timer, while RViz trajectory/mesh/TF display runs on a 0.1s timer.
  MoSim should copy this separation: high-rate state for control and
  localization, lower-rate display for operator review.
- `UAVControl.cpp` treats command timeout, geofence, localization validity,
  takeoff, hover, landing, mode switching, and setpoint output as controller
  responsibilities. MoSim should not let a mapping or keyboard node own these
  safety semantics.
- `sunray_ego_single_mid360.launch` uses a 3D local map with resolution around
  0.12m, local update ranges around 5.5m x 5.5m x 4.5m, obstacle inflation, and
  B-spline trajectory output. This is the right category for our 3D grid-map
  review, not `nav_msgs/OccupancyGrid` alone.
- Sunray's Mid360 path converts Livox data into world-frame point cloud for
  EGO planner. MoSim must maintain a clear distinction between sensor-frame
  raw LiDAR, FAST-LIO registered cloud/odometry, and planner-consumed
  world-frame local map.

This last point is now critical. MoSim should not infer that any Livox-shaped
`PointCloud2` is accepted by FAST-LIO. The implementation-specific subscriber
surface must be checked first: CustomMsg-capable FAST-LIO, ROS2 Livox driver
messages, or a proven Livox `PointCloud2` parser.

### RFlySim / AirSim / Gazebo Architecture

The common pattern is process and responsibility separation, not one
monolithic viewer:

```text
flight dynamics / controller / PX4 or simulator core
  -> state, actuator, sensor timing, fault/safety semantics

3D engine / simulator window
  -> rendered world, camera view, visual UAV motion, scene sensor oracle

ROS / RViz
  -> LiDAR, IMU, TF, odometry, point clouds, local map, planner state
```

For MoSim, this means:

- UE/MoSimSceneLibrary is the high-fidelity rendering window and sensor oracle.
  It can generate raycast/collision truth, but it is not the controller or
  physics authority.
- RViz2 remains the native review surface for point cloud, FAST-LIO, TF,
  odometry, path, and 3D local map.
- MWORKS remains the dynamics/controller/truth solver. If PX4/Sunray code is
  reused, it should be treated as interface and architecture reference first,
  not as a replacement for the MWORKS solver.
- Gazebo/Sunray code is most useful for the Mid360 plugin semantics, launch
  topology, odometry-valid safety logic, and EGO local-map/planner chain.

## 3. MoSim Timing And Topic Contract

Minimum frequency contract:

| Signal | Baseline | Enhanced target | Owner | Notes |
|---|---:|---:|---|---|
| MWORKS plant/controller step exposed to ROS | 20Hz | 20Hz+ internal solver substeps allowed | MWORKS | Continuous state and setpoint stream; no pose teleport. |
| IMU | 200Hz | 200Hz+ | MWORKS/ROS2 bridge | Must be timestamped in the same clock domain as LiDAR. |
| Mid360 LiDAR frame | 10Hz | 20Hz MoSim enhanced mode | UE sensor oracle / ROS2 bridge | Hardware-faithful baseline about 200k pts/s; 20Hz must pass throughput and FAST-LIO quality gates. |
| FAST-LIO odometry | LiDAR-driven | LiDAR-driven | ROS2 FAST-LIO | Must be compared against MWORKS truth before being trusted. |
| RViz display | 10-20Hz where useful | bounded by UI performance | ROS2/RViz2 | Display rate is evidence/review only, not controller truth. |
| Planner setpoint output | 20Hz or trajectory sampled to 20Hz | 20Hz | ROS2 planner adapter / MWORKS interface | Uses local sensed map only; UE global truth is validation oracle. |

Current synchronization contract for the user-requested 20Hz loop:

- controller and planner-to-controller setpoints run as a 20Hz streamed
  contract, never as direct pose overwrite;
- enhanced LiDAR may run at 20Hz, but every scan must keep valid per-point
  offsets inside the scan period and must share one clock domain with 200Hz IMU;
- FAST-LIO odometry is accepted only when the recorded run proves topic rates,
  monotonic timestamps, explicit LiDAR/IMU extrinsics, registered cloud,
  odometry/path outputs, and truth-vs-estimate error against MWORKS truth;
- `/mosim/truth/odometry` can synchronize and evaluate the stack, but cannot be
  substituted for FAST-LIO odometry in planner/localization claims.

Minimum topic families:

```text
/mosim/truth/odometry         MWORKS truth odometry for validation and UE playback
/mosim/forward/imu            high-rate IMU for FAST-LIO
/mosim/livox/lidar            Livox CustomMsg input for FAST-LIO when using Mid360
/mosim/lidar_points           PointCloud2 display/debug mirror, not the primary Mid360 claim
/cloud_registered             FAST-LIO registered cloud
/odometry or /mosim/lio/odom  FAST-LIO odometry
/path                         FAST-LIO path
/mosim/local_map/*            3D local map / voxel / ESDF-style planner state
/mosim/planner/setpoint       continuous position/velocity/acceleration/yaw setpoints
```

Clock policy:

- all sensor and state messages in one run must use one clock domain;
- per-point LiDAR offsets must fit the scan duration;
- nonmonotonic timestamps are a failed runtime gate;
- LiDAR-to-IMU extrinsic must be explicit even when initially identity;
- truth odometry may be used for evaluation and display alignment, but not as
  a replacement for FAST-LIO estimate when claiming localization.

## 4. Reuse / Adapt / Replace Decisions

| Module | Decision | Reason |
|---|---|---|
| MWORKS quadrotor dynamics/controller | Reuse/extend | Project solver authority and competition evidence source. |
| UE Factory/Derelict accepted maps | Reuse | Already visually reviewed; enough for first closed loop. |
| Keyboard grid-cell mapping publisher | Abandon as product route | Discrete motion and fake perception break controller/planner validity. |
| Existing sparse/static point-cloud demos | Smoke-only | Useful for RViz/topic checks only. |
| Sunray `external_fusion` and `sunray_control_node` design | Adapt | Strong reference for state fusion, command timeout, geofence, control state machine. |
| Sunray Livox Gazebo plugin | Adapt concept/code | Provides Mid360 scan pattern and CustomMsg/offset_time semantics. |
| Sunray/EGO planner chain | Adapt after localization gate | Good 3D local map and B-spline setpoint model, but must be bridged to ROS2/MWORKS. |
| ROS2 `spark-fast-lio` candidate | Patch or replace | Built locally, but Mid360 CustomMsg path had blockers; build success alone is not localization evidence. |
| ROS1 FAST_LIO | Reference/possible bridge | Semantically correct Mid360 reference, not direct ROS2 runtime evidence without bridge/container decision. |
| RViz2 split windows | Reuse | Native point-cloud/local-map review surface. |

## 5. Minimum Closed Loop To Build Next

The next accepted minimum closed loop is not free-flight autonomy. It is a
measurable continuous replay/control loop:

```text
Factory scene first
  1. MWORKS produces continuous UAV truth state and IMU at agreed rates.
  2. UE scene oracle produces Mid360-shaped LiDAR frames from the UAV pose.
  3. ROS2 publishes synchronized Livox CustomMsg + IMU + TF.
  4. FAST-LIO publishes nonzero registered cloud, odometry, and path.
  5. A recorder computes topic rates, monotonic timestamps, point counts, and
     truth-vs-estimate error.
  6. RViz2 opens only after headless runtime gates pass.
  7. A Sunray/EGO-style 3D local map consumes the estimated odometry/cloud.
  8. Planner setpoints are sampled into a 20Hz MWORKS controller interface.
```

Acceptance before user visual review:

- `/mosim/livox/lidar` publishes nonzero Livox CustomMsg frames with correct
  point count and offset range;
- `/mosim/forward/imu` publishes about 200Hz and leads/overlaps LiDAR scans;
- FAST-LIO publishes nonzero registered cloud, odometry, and path;
- timestamps are monotonic;
- truth error is reported and not hidden;
- local map is 3D, not only a 2D OccupancyGrid;
- UE global truth is not fed to planner as a pre-known global map.

Manual review points:

1. UE window: accepted scene, UAV body, smooth continuous motion, no wall
   penetration.
2. RViz2 FAST-LIO window: raw Livox/debug cloud, registered cloud, odometry,
   path, TF.
3. RViz2 local-map window: 3D local map/voxels/ESDF-style state and local
   planner output.
4. Evidence report: topic rates, frame counts, truth error, known limitations.

## 5.1 Requirement Traceability And Current Gaps

This table is the control surface for the next implementation work. A row is
not complete until the evidence column exists and passes the stated gate.

| Requirement | Current Evidence | Gap | Next Gate |
|---|---|---|---|
| Stop grid-cell / fake point-cloud product route | This document, `Docs/Workflows/unreal_renderer.md`, and `PROGRESS.md` mark it smoke-only. | Existing scripts still exist for smoke and could be misused by later agents. | Smoke scripts must print/record `quality_status=smoke_only` and must not be accepted by FAST-LIO/planner evidence checks. |
| Continuous UAV motion | MWORKS replay CSV bridge exists and publishes odometry/IMU topics in prior tests. | Current path is replay/export, not live closed-loop MWORKS solver driving UE/ROS2. | A run report must show continuous pose, bounded velocity/acceleration jumps, monotonic timestamps, and no direct pose overwrite. |
| MWORKS as solver/controller/truth authority | Design boundary is explicit. Existing MWORKS smoke CSV is used as truth replay. | Live high-rate MWORKS export/co-simulation is not proven. | MWORKS bridge must label source as `MWORKS_MCP`, `MWORKS_GUI`, or `offline/replay`; final claims require MWORKS-produced state and metrics. |
| IMU 200Hz | `publish_mworks_uav_state_ros2.py` can publish 200Hz resampled IMU. | Resampled IMU from 20Hz rows is not hardware-faithful. | Report must distinguish `resampled` vs `native/high-rate`; FAST-LIO quality claims require synchronized high-rate or physically consistent simulated IMU. |
| Mid360 LiDAR baseline | Dense Factory/Derelict Livox-like replay exists, about 20k-24k points/frame. | Runtime is replay, not live UE raycast; 20Hz enhanced mode is not proven. | Baseline: 10Hz, about 200k pts/s, correct per-point offsets. Enhanced: 20Hz only after measured throughput and FAST-LIO quality pass. |
| Livox/FAST-LIO message compatibility | `spark-fast-lio` patch-readiness gate exists and currently reports required Livox CustomMsg fixes. | Current ROS2 candidate was not natively Mid360-ready through PointCloud2. | Headless FAST-LIO smoke must prove nonzero `/cloud_registered`, odometry, and path from `/mosim/livox/lidar` + `/mosim/forward/imu`. |
| Time synchronization | Current docs identify nonmonotonic timestamps as hard failure. | Prior Factory evaluations had nonmonotonic odometry timestamps and mixed timing symptoms. | Recorder must verify one clock domain, monotonic message stamps, LiDAR offset range within scan duration, and IMU coverage before/inside each scan. |
| Extrinsics | Local Mid360 configs provide reference extrinsic fields; identity is allowed only for synthetic-aligned tests. | Sunray150 physical LiDAR/IMU mounting is not measured in MoSim yet. | Every run must write `extrinsic_T`, `extrinsic_R`, source (`measured`, `CAD`, `synthetic_identity`), and whether online extrinsic estimation is enabled. |
| 3D local map | Sunray/EGO launch provides 3D local grid pattern and parameters. | Current MoSim visible map work still has smoke-only or display-only components. | RViz2 planner window must show 3D local voxel/SDF/ESDF-like state tied to odometry/cloud, not only `nav_msgs/OccupancyGrid`. |
| Planner does not know global truth | Design says UE global truth is validation-only. | Need enforcement in data flow. | Planner input audit must show it consumes local sensed map/estimated odometry only; UE collision/global map may be used only by validator/sensor oracle. |
| Planner-to-controller interface | Sunray `PositionCommand` / `UAVControlCMD` and `positionCmd2sunray` define position/velocity/acceleration/yaw/yaw-rate contract. | MoSim ROS2-to-MWORKS setpoint adapter is not yet finalized. | Adapter must stream 20Hz setpoints into MWORKS and record command timeout/failsafe behavior. |
| Native review windows | UE/RViz2 split is documented. | No new manual review should happen until headless runtime gates pass. | Open UE + RViz2 only after headless topics/rates/error reports are generated; user reviews visual correctness, not hidden data validity. |
| WeChat progress/manual intervention | cc-connect adapter exists and the 2026-06-02 gateway repair verified live sends through `MoSim｜微信通知网关`. | available-with-recovery-rule | Send sparse milestone/blocker/manual-review packets by default. If send fails, diagnose immediately: resolve active session for `no active session found`; for `ret=-2`, ask the user to send one normal WeChat message, retry once, then redo QR setup if still blocked. |

## 5.2 Authoritative Source Traceability

Use these sources as the current reference set. Do not substitute random
examples or display demos for them.

| Topic | Authoritative Source | MoSim Rule Derived |
|---|---|---|
| PX4 ROS2 integration | `https://docs.px4.io/main/en/ros2/user_guide.html` | PX4/ROS2 uses uXRCE-DDS and matching `px4_msgs`; keep future PX4 route message-version-aware. |
| PX4 Offboard setpoint semantics | `https://docs.px4.io/main/en/flight_modes/offboard.html` | External control must be a continuous heartbeat/setpoint stream; 20Hz MoSim setpoints satisfy the concept, but missed/stale messages are faults. |
| Livox Mid360 hardware profile | `https://www.livoxtech.com/mid-360/specs`, Livox Mid360 user manual PDFs | Use 10Hz and about 200k pts/s as hardware-faithful baseline; 200Hz IMU and explicit time sync are required. |
| FAST-LIO semantics | `https://github.com/hku-mars/FAST_LIO`, local `References/Lab/localization_slam/FAST_LIO/config/mid360.yaml` | Livox path needs per-point timing and LiDAR/IMU synchronization; display-only point clouds are not localization evidence. |
| Sunray control stack | `References/Sunray/scripts_*`, `externalFusion.cpp`, `UAVControl.cpp` | Reuse state-fusion/control-state-machine concepts: odom validity, command timeout, geofence, takeoff/hover/land, and separate high-rate state vs lower-rate display. |
| Sunray Mid360/EGO stack | `sunray_ego_single_mid360.launch`, Sunray Livox Gazebo plugin, `livox2Point.cpp` | Reuse 3D local map parameters, Livox scan pattern, CustomMsg/offset_time, and B-spline-to-control-command structure. |
| RFlySim architecture | `https://rflysim.com/doc/en/3/RflySim3DUE.html`, `https://rflysim.com/doc/en/1/Intro.html` | Treat UE/RflySim3D as 3D engine and perception-data source, while CopterSim/PX4 or MWORKS owns motion/control. |
| AirSim / Gazebo pattern | Local `References/AirSim/*`, `References/PX4/docs/en/sim_*` | Keep simulator/rendering separate from ROS/RViz tooling; bridge sensor and state topics rather than merging all behavior into one viewer. |

## 5.3 Implementation Gates, In Order

The next implementation should advance only through these gates. If a gate
fails, do not compensate by changing visualization parameters.

1. **Source contract gate**:
   confirm Factory scene, MWORKS truth source, LiDAR frame file/live source,
   IMU source, clock policy, and extrinsics are declared in a manifest.
2. **Headless sensor gate**:
   record `/mosim/livox/lidar`, `/mosim/forward/imu`, `/tf`, and
   `/mosim/truth/odometry`; verify rates, nonzero data, point counts,
   timestamp monotonicity, and scan offset range.
3. **FAST-LIO subscriber gate**:
   run the selected FAST-LIO route with Livox CustomMsg or proven supported
   PointCloud2; require nonzero registered cloud, odometry, and path.
4. **Truth-error gate**:
   compare FAST-LIO odometry/path against MWORKS/UE truth; report RMSE, max
   error, timestamp anomalies, and initialization failures.
5. **3D map gate**:
   feed estimator output and cloud into a 3D local map; verify the review
   surface is rotatable 3D occupancy/voxel/SDF-style state.
6. **Planner-command gate**:
   connect local-map planner output to a 20Hz position/velocity/acceleration
   and yaw setpoint stream; no direct pose jumps.
7. **MWORKS closed-loop gate**:
   MWORKS consumes planner/controller setpoints, runs the plant/controller,
   emits truth and metrics, and UE follows truth pose.
8. **Manual visual audit gate**:
   open UE and RViz2 split windows for user audit only after the headless
   evidence above exists.

2026-06-02 executable gate update: `Scripts/UE5/check_realstack_miniloop_gate.py`
now blocks RViz2/UE manual review until the headless real-stack evidence is
credible. It requires both nonzero FAST-LIO runtime topics and a passing
truth-evaluation file. Current Factory result is
`Results/unreal_scene_mapping/factoryenvironmentcollect/REALSTACK_MINILOOP_GATE.md`:
MWORKS state and dense Livox/IMU input are now live enough for FAST-LIO to
publish `/Odometry`, `/path`, and `/cloud_registered`, but manual review is
still blocked because truth evaluation fails (`RMSE=9.576m`,
`max_error=17.900m`). The next engineering step is localization-quality
diagnosis, not RViz point size tuning, 2D grid work, or more keyboard/manual
mapping.

### Additional RFlySim / AirSim / Gazebo Notes

The common architecture is not one all-in-one window:

```text
simulator/rendering window
  -> UE/AirSim/RFlySim3D/Gazebo world

robotics visualization window
  -> RViz/RViz2 point clouds, TF, odometry, grid/voxel map, planner path

control/mission interface
  -> QGC or custom command UI when needed
```

MoSim should copy this separation. UE should not replace RViz2 for active
FAST-LIO/grid-map review.

Local reference documents:

- `Docs/Workflows/unreal_mapping_window_research.md`
- `Docs/Workflows/unreal_renderer.md`
- `Results/rflysim/*_migration_plan.md`
- `References/AirSim/AirSim/docs/px4_sitl.md`
- `References/AirSim/AirSim/docs/px4_lockstep.md`
- `References/AirSim/AirSim/docs/airsim_ros_pkgs.md`
- `References/AirSim/AirSim/docs/gazebo_drone.md`
- `References/AirSim/AirSim/docs/lidar.md`

MoSim implication:

- AirSim's architecture supports using one component as the flight-dynamic
  model and another as the high-fidelity environment/sensor generator. That is
  the same split MoSim needs: MWORKS for dynamics/control and UE for scene
  rendering/sensors.
- AirSim ROS wrapper exposes vehicle state, IMU, LiDAR `PointCloud2`, TF, and
  camera topics through ROS. MoSim should expose comparable topics, but keep
  MWORKS as the solver authority instead of adopting AirSim's simple_flight or
  PX4 as the first controller.

## 6. Detailed Runtime Evidence And Contracts

Earlier implementation work produced useful runtime evidence. Keep it as
evidence and diagnostics, but treat Sections 0-5 above as the current design
front door. Initial contract for the minimum credible loop:

| Signal | Topic / Interface | Target Rate | Owner |
|---|---:|---:|---|
| MWORKS solver step | internal / bridge | >=100Hz preferred, 20Hz minimum review mode | MWORKS |
| controller setpoint | ROS2/PX4-style setpoint or MoSim command | 20Hz | MWORKS/controller |
| UAV pose / odometry truth | `/mosim/truth/odometry` | 20-100Hz | MWORKS bridge |
| IMU | `/mosim/imu` or `/uav1/livox/imu` | 200Hz | MWORKS sensor bridge |
| LiDAR scan | `/mosim/lidar_points` or `/uav1/livox/lidar` | 10Hz hardware-faithful, 20Hz enhanced sim target | UE/sensor bridge |
| TF | `map/world -> base_link -> lidar/imu` | >=20Hz | ROS2 bridge |
| FAST-LIO registered cloud | `/cloud_registered` | LiDAR-rate dependent | FAST-LIO runtime |
| FAST-LIO odometry | `/odometry` or `/Odometry` | LiDAR-rate dependent | FAST-LIO runtime |
| local 3D map | planner's native map/marker topics | 5-20Hz | EGO/grid map |
| planner command | B-spline / position cmd / MoSim setpoint | 10-20Hz | planner adapter |
| UE render | UDP/shared bridge from MWORKS truth | visual frame rate | UE renderer |

Do not couple controller motion to occupancy-grid cell size. The UAV must move
continuously according to dynamics and control. Grid/voxel maps are sensor and
planner state, not the motion primitive.

## 6.1 Current Minimum Bridge Evidence

2026-06-02 verification added a narrow MWORKS-to-ROS2 replay bridge:

```bash
python3 Scripts/ros/publish_mworks_uav_state_ros2.py \
  --mworks-raw-csv Results/unreal_scene_mapping/factoryenvironmentcollect/mworks_smoke/raw/sunray150_ue_factoryenvironmentcollect_linear_mpc_smoke.csv \
  --lidar-point-frames-jsonl Results/unreal_scene_mapping/factoryenvironmentcollect/lidar_point_frames.jsonl \
  --dry-run --max-frames 20
```

The bridge publishes the following runtime topics when ROS2 Humble is sourced:

```text
/mosim/truth/odometry  nav_msgs/Odometry     measured about 20.0 Hz
/mosim/imu             sensor_msgs/Imu       measured about 200.0 Hz
/mosim/lidar_points    sensor_msgs/PointCloud2 measured about 10.0 Hz
/tf                    TF world/body link
```

Important boundary: the 200Hz IMU stream is currently resampled from the 20Hz
MWORKS state CSV. It is useful for ROS2 scheduling and topic-contract tests,
but it is not final high-rate PX4/IMU sensor truth. Final evidence must come
from either a higher-rate MWORKS solver/export or a live co-simulation bridge.

The current Factory `lidar_point_frames.jsonl` is not acceptable FAST-LIO input.
The first 20 frames contain only about 156-176 points per frame. A Mid360-class
sensor is closer to 200,000 points/s and 10Hz typical frame output, so a
hardware-faithful simulation should be on the order of tens of thousands of
points per scan or use a Livox CustomMsg-compatible scan pattern with per-point
timestamps. Low-density replay may remain a smoke input only.

2026-06-02 dense replay probe:

- `Scripts/UE5/generate_livox_like_lidar_replay.py` now reuses Sunray's
  `mid360-real-centr.csv` scan-mode file plus UE collision truth to generate
  `mosim.livox_like_lidar_frame.v1`.
- Factory 5-frame probe with 30k rays/frame produced about 24,536-25,862
  points/frame, averaging about 25,262 points/frame.
- The generated frames include point attributes for `offset_time_ns`, `line`,
  `reflectivity`, and `tag`, matching the data needed to move toward a Livox
  CustomMsg-compatible path.
- Publishing 25k-point frames through the current Python/rclpy bridge is not
  viable as a real-time mainline. The point data appears on
  `/mosim/lidar_points`, but `ros2 topic hz` measured only about 0.3-0.5Hz on
  this WSL/ROS2 path.

Therefore, the next implementation must not optimize the Python publisher as
the dense real-time transport. Use it for smoke/replay only. Dense LiDAR should
move to one of these routes:

1. C++ ROS2 publisher node that reads MWORKS/UE replay or live shared-memory
   packets and publishes `PointCloud2` / Livox-like fields efficiently.
2. UE C++ sensor plugin that performs scene raycasts and emits LiDAR frames to
   ROS2/UDP/shared memory, using the Sunray Mid360 scan CSV as the pattern.
3. Gazebo/Sunray Livox plugin as a reference implementation for scan pattern,
   `CustomMsg`, `offset_time`, and `line` semantics.

2026-06-02 C++ transport probe:

- Added `Scripts/ros/mosim_dense_lidar_cpp` as a minimal `ament_cmake` ROS2
  package.
- Initial C++ publisher that rebuilt `PointCloud2` every timer tick was still
  too slow, around 0.5-0.8Hz for 25k-point frames.
- After prepacking `PointCloud2` frame payloads and updating only headers in
  the timer callback, the same 25k-point replay measured about 7-8Hz on this
  WSL/ROS2 path.
- Added publisher-side statistics because `ros2 topic hz` can become the
  bottleneck for large `PointCloud2` messages. With prepacked frames and about
  21k points/frame, the C++ publisher's own timer reported about 9.73Hz and
  mean publish call time around 100-130 microseconds.
- Added `dense_lidar_subscriber_probe_node` to measure subscriber-side
  contract and throughput before involving FAST-LIO. A short 2026-06-02 probe
  on Factory Livox-like replay received 8 frames at about 9.69Hz, with about
  19.9k-21.0k points/frame, `point_step=22`, Livox fields present, and
  monotonic stamps.
- This validates C++ replay transport as a credible next step, but it is not
  yet final FAST-LIO input. Next work must evaluate the actual FAST-LIO
  subscriber path, timestamp policy, extrinsics, QoS/DDS/WSL bottlenecks, and a
  realistic point-density/rate tradeoff before making localization claims.

Target next gate before FAST-LIO claims:

```text
MWORKS-derived continuous trajectory
  -> dense LiDAR frame or Livox-like CustomMsg with per-point offset_time/tag/line
  -> synchronized IMU/LiDAR timestamps and extrinsics
  -> FAST-LIO runtime publishes /cloud_registered, odometry, and path
  -> RViz2 shows small rendered points, not large sphere markers
```

## 6.2 Source-Code Contracts To Reuse

The local Sunray source gives the best concrete template for MoSim. It should
be treated as a contract reference rather than copied blindly.

### Sunray process graph

Observed in:

- `References/Sunray/scripts_sim/sunray_uav_ego_sim.sh`
- `References/Sunray/scripts_exp/sunray_uav_ego_mid360.sh`
- `References/Sunray/scripts_exp/uav_control_mid360.sh`

The flow is:

```text
simulator/PX4/MAVROS
  -> external_fusion
  -> sunray_control_node
  -> terminal / waypoint / planner command source
  -> Mid360 message conversion
  -> FAST-LIO
  -> EGO planner
  -> trajectory server
  -> positionCmd2sunray
  -> /uav1/sunray/uav_control_cmd
```

Important implications for MoSim:

- localization is a first-class external-fusion input, not a display artifact;
- odometry validity has timeout semantics (`odom_valid_timeout=0.5`);
- commands are streamed into a control node, not applied as direct pose jumps;
- planner output is a trajectory command surface, not a grid-cell movement;
- RViz is part of runtime evidence, not a report-only preview.

### Sunray planner/map contract

Observed in:

- `References/Sunray/General_Module/sunray_planner_utils/launch/sunray_ego_single_mid360.launch`
- `References/Sunray/External_Module/ego-planner-swarm/src/planner/plan_env/*`

EGO planner consumes:

```text
odom:  /sunray/odometry
cloud: /sunray/pointCloud     # world/global-frame point cloud
goal:  /goal or preset target
```

It publishes:

```text
/drone_0_planning/bspline
/uav1/pos_cmd
/uav1/sunray/uav_control_cmd
```

The local map is 3D and local:

```text
grid_map/resolution           0.12 m in the UAV Mid360 launch
grid_map/local_update_range_x 5.5 m
grid_map/local_update_range_y 5.5 m
grid_map/local_update_range_z 4.5 m
grid_map/obstacles_inflation  0.25 m
grid_map/max_ray_length       4.5 m
```

MoSim must preserve this architecture: 2D `nav_msgs/OccupancyGrid` may be kept
as an auxiliary operator view, but the planner map should be a 3D local
voxel/SDF/grid-map equivalent.

### Sunray command contract

Observed in:

- `References/Sunray/General_Module/sunray_planner_utils/src/positionCmd2sunray.cpp`
- `References/Sunray/General_Module/sunray_common/sunray_msgs/msg/UAVControlCMD.msg`
- `References/Sunray/General_Module/sunray_common/sunray_msgs/msg/PositionCommand.msg`

`PositionCommand` contains position, velocity, acceleration, yaw, yaw rate, and
trajectory status. `positionCmd2sunray` runs at 20Hz and converts it to
`UAVControlCMD`, typically `XyzPosVelYaw` or `CTRL_Traj`.

MoSim's controller interface should therefore expose a trajectory/setpoint
surface compatible with:

```text
position[m], velocity[m/s], acceleration[m/s^2], yaw[rad], yaw_rate[rad/s]
```

and should not accept a cell index or a discrete keyboard step as a control
input for formal evidence.

Code-level source:

- `References/Sunray/General_Module/sunray_common/sunray_msgs/msg/PositionCommand.msg`
  defines position, velocity, acceleration, yaw, yaw rate, gains, trajectory id,
  and trajectory status.
- `References/Sunray/General_Module/sunray_common/sunray_msgs/msg/UAVControlCMD.msg`
  defines position/velocity/acceleration/yaw/yaw-rate command modes, takeoff,
  land, hover, return, and trajectory commands.
- `References/Sunray/General_Module/sunray_planner_utils/src/positionCmd2sunray.cpp`
  loops at 20Hz.
- `References/Sunray/General_Module/sunray_uav_control/uav_control/uav_control_node.cpp`
  loops at 200Hz.
- `References/Sunray/General_Module/sunray_uav_control/externalFusion/external_fusion_node.cpp`
  loops at 200Hz.

These rates reinforce the MoSim split: high-rate state/control health is not
the same as 20Hz planner command streaming, and neither should be tied to map
cell size.

### Mid360 / FAST-LIO contract

Observed in:

- `References/Sunray/simulation/sunray_simulator/launch_slam/mid360.yaml`
- `References/Lab/localization_slam/FAST_LIO/config/mid360.yaml`
- `References/Sunray/General_Module/sunray_planner_utils/launch_driver/mapping_mid360.launch`

Required shape:

```text
lid_topic:  /uav1/livox/lidar or remapped MoSim equivalent
imu_topic:  /uav1/livox/imu or remapped MoSim equivalent
lidar_type: 1  # Livox serials
scan_line:  4
blind:      0.5
time_sync_en: false unless external sync is impossible
extrinsic_T/R: calibrated or explicitly identity only for a controlled sim frame
```

FAST-LIO acceptance requires runtime topics and evaluation against truth. A
dense static cloud, replay truth odometry, or RViz display alone is not
FAST-LIO evidence.

Sunray's local Livox simulation package provides the most concrete message
shape for MoSim's next sensor bridge:

```text
References/Sunray/simulation/gazebo_plugin/livox_laser_simulation/msg/CustomMsg.msg
References/Sunray/simulation/gazebo_plugin/livox_laser_simulation/msg/CustomPoint.msg
```

`CustomPoint` contains `offset_time`, `x`, `y`, `z`, `reflectivity`, `tag`, and
`line`. `livox_points_plugin.cpp` can publish a Livox `CustomMsg` route and
uses `offset_time = 1e9 / 200000 * i` for a 200k points/s scan model. This is
the correct source to port or mirror before trying another FAST-LIO run.

## 7. Proposed MoSim Minimum Loop

### Phase A: Architecture Alignment

1. Finish source audit of:
   - Sunray `sunray_uav_control`, `external_fusion`, EGO planner launch,
     Mid360/FAST-LIO launch, RViz configs;
   - RFlySim docs and scene bridge ideas;
   - AirSim/PX4 lockstep and ROS wrapper patterns;
   - existing MoSim MWORKS/UE bridge scripts.
2. Produce topic table and timing contract.
3. Decide whether the first credible runtime uses:
   - ROS2 native `spark-fast-lio` only after adding/proving Livox CustomMsg
     support;
   - another ROS2 FAST-LIO/FAST-LIO2 fork with documented Mid360/Livox support;
   - ROS1 FAST-LIO in a container/bridge; or
   - Sunray ROS1 stack isolated as a reference-only route.

Decision for the next implementation slice:

```text
MWORKS-first continuous dynamics bridge remains first. The previous
`spark-fast-lio + Mid360 PointCloud2` runtime is no longer accepted as the
default ROS2-native localization route until its Livox subscriber path is fixed
or replaced. Sunray/ROS1 remains the reference contract and fallback, but a
temporary ROS1 bridge may be justified if it is the shortest route to a real
FAST-LIO/Mid360 proof.
```

Reason:

- the host is Ubuntu 22.04 with ROS2 Humble already working, but ROS2 alone is
  not sufficient if the selected FAST-LIO build cannot parse Mid360 input;
- local Sunray/FAST_LIO sources are mostly ROS1/catkin and are valuable as
  architecture references; they also provide the strongest known Livox/FAST-LIO
  route if the ROS2 candidate remains blocked;
- MWORKS must remain the solver/controller authority, so the first credible
  slice is state/IMU/setpoint timing correctness, then LiDAR/FAST-LIO quality.

### Phase B: Minimal Continuous Runtime

1. MWORKS publishes continuous vehicle state and IMU at fixed rates.
2. UE publishes or assists LiDAR ray generation from the accepted Factory map.
3. ROS2 publishes `PointCloud2` and IMU with coherent timestamps.
4. FAST-LIO consumes those streams and outputs odometry/cloud.
5. RViz2 has two native windows:
   - point cloud/FAST-LIO window;
   - 3D grid/planner window.
6. UE renders the same UAV pose from MWORKS truth, not from a grid-step loop.

Concrete first runtime target:

```text
Factory scene only
  -> MWORKS continuous Sunray150 state / IMU source
  -> ROS2 bridge publishes /mosim/truth/odometry and /mosim/imu
  -> UE receives the same truth pose for rendering
  -> sensor bridge publishes Mid360-shaped PointCloud2 at 10Hz first, then 20Hz
  -> RViz2 point-cloud window shows raw LiDAR as points, not spheres
  -> RViz2 map/planner window shows 3D local voxel/known map, not only 2D grid
```

The first implementation must measure topic rates and timestamp monotonicity
before visual quality tuning:

```text
/mosim/imu                  200Hz target
/mosim/truth/odometry       20-100Hz target
/mosim/lidar_points         10Hz hardware-faithful baseline, 20Hz enhanced target
/tf                         >=20Hz
controller/setpoint stream  20Hz target
```

### Phase C: Planner and Control Closure

1. Reuse EGO-style local mapping/planning where practical.
2. Convert planner B-spline/position command into MoSim controller setpoints.
3. Keep MWORKS as the controller and plant solver.
4. Validate with truth:
   - no global map leakage into planner;
   - collision clearance from UE truth;
   - FAST-LIO odometry error against truth;
   - controller tracking and safety metrics from MWORKS.

## 8. Reuse-First Choices

Prefer reuse:

- Sunray launch architecture and topic contracts:
  `external_fusion` -> `sunray_control_node` -> mission/planner command ->
  Mid360/FAST-LIO -> EGO -> `positionCmd2sunray`.
- Sunray message surfaces as interface templates:
  `PX4State`, `UAVState`, `UAVControlCMD`, and `PositionCommand`. The first
  MoSim-native version may be ROS2 standard messages plus a compact custom
  message package, but the fields must preserve position, velocity,
  acceleration, yaw, yaw-rate, mode, odometry-valid, command timeout, and
  geofence semantics.
- Sunray Mid360 Gazebo plugin semantics:
  `mid360-real-centr.csv`, Livox non-repetitive scan indexing, `CustomMsg`,
  `CustomPoint`, `offset_time`, `line`, `tag`, and reflectivity.
- Sunray `livox2Point.cpp` conversion logic as the exact `PointCloud2` field
  layout reference for RViz display:
  `offset_time:uint32`, `x/y/z:float32`, `intensity:float32`, `tag:uint8`,
  `line:uint8`.
- EGO planner local 3D map and B-spline pipeline, if buildable or portable to
  ROS2. Its local map should be treated as the main planner-state target.
- FAST-LIO-family runtime, but only when real topics are recorded.
- RViz/RViz2 configs from Sunray/FAST-LIO as templates, with point rendering
  configured as small points rather than large markers/spheres.
- RFlySim's separation of UE rendering from ROS point-cloud visualization.
- AirSim/PX4 lockstep principle when simulator timing is expensive.

Avoid or defer:

- hand-coded fake point clouds as final evidence;
- moving the UAV by occupancy cells;
- browser/HTML runtime visualization;
- claiming FAST-LIO from replay truth or reference odometry;
- feeding UE global truth directly to planner.

## 8.1 Reuse / Adapt / Reject Matrix

| Source | Component | Use In MoSim | Reason |
|---|---|---|---|
| Sunray | `external_fusion` state aggregation | adapt | Matches the needed separation of external localization, PX4/state aggregation, RViz state, and TF. Reimplement as ROS2/MWORKS bridge rather than copying ROS1/MAVROS code directly. |
| Sunray | `sunray_control_node` state machine | adapt | Provides takeoff/hover/land/geofence/timeout/control-mode structure. MWORKS should own the numerical controller, but the state-machine concepts should remain. |
| Sunray | `UAVControlCMD` / `PositionCommand` | reuse as contract | The field shape matches planner-to-controller needs: position, velocity, acceleration, yaw, yaw-rate, trajectory status. |
| Sunray | `positionCmd2sunray` | adapt | Confirms the 20Hz trajectory-command adapter surface. MoSim should build a ROS2 `PositionCommand -> MWORKS setpoint` adapter instead of direct pose motion. |
| Sunray | Mid360 Gazebo plugin | reuse semantics, maybe port | Strongest available local reference for Livox scan pattern, per-point time, line, tag, and reflectivity. Porting to UE C++ raycasts or ROS2 C++ publisher is more credible than Python point-cloud fabrication. |
| Sunray | `livox2Point.cpp` | reuse field layout | Gives exact Livox-to-PointCloud2 field mapping for RViz display while preserving per-point offset fields. |
| Sunray/EGO | local 3D grid map and B-spline planner | adapt/port | Correct planning architecture: unknown global map, local 3D sensor map, replanning, B-spline output. First port can be interface-level if full ROS2 build is expensive. |
| FAST-LIO / spark-fast-lio | LIO runtime | use only with evidence | Runtime acceptance requires `/cloud_registered`, odometry/path, rate/timestamp checks, and truth comparison. |
| Current `spark-fast-lio` Mid360 `PointCloud2` route | FAST-LIO runtime | blocked | Source inspection shows `PointCloud2` accepts Ouster/Kimera/Velodyne cases only; `lidar_type=1` requires guarded Livox CustomMsg support. |
| AirSim | flight-dynamics/sensor/rendering split | reuse design | Supports using one solver/FDM and one UE sensor/render component, aligning with MWORKS+UE split. |
| PX4 | uXRCE-DDS/offboard stream contract | reuse design | Even if PX4 is deferred, control setpoints must be continuous streamed commands with loss detection. |
| Current keyboard grid scripts | manual movement demo | reject for product, keep smoke-only | Cell-step motion is incompatible with controller optimization and realistic odometry/IMU/LiDAR synchronization. |
| Current low-density point frames | quick ROS/RViz smoke | reject for FAST-LIO evidence | Hundreds of points/frame is far below Mid360-class input and cannot support credible FAST-LIO/map claims. |

## 8.2 Next Minimal Closed Loop

The next credible implementation should be narrow and continuous:

```text
Factory scene only
  -> MWORKS or MWORKS-exported continuous Sunray150 trajectory and IMU
  -> ROS2 state bridge publishes truth odometry, IMU, TF, and command/status
  -> UE renderer follows MWORKS truth pose
  -> UE/C++ or ROS2/C++ LiDAR adapter emits Livox-shaped scan frames
  -> FAST-LIO consumes LiDAR + IMU and publishes registered cloud/odometry/path
  -> local 3D map/planner consumes LIO/world cloud + odometry
  -> planner command adapter streams 20Hz setpoints back to MWORKS
```

Minimum acceptance for this loop:

- no cell-sized pose jumps; all vehicle motion comes from MWORKS state or
  MWORKS-tracked setpoints;
- `/mosim/imu` has monotonic stamps and measured 200Hz publish cadence from
  real/high-rate source or explicitly marked resampling;
- LiDAR has Livox-style per-point timing and at least a 10Hz hardware-faithful
  baseline before attempting 20Hz enhanced mode;
- selected FAST-LIO implementation demonstrably accepts the exact MoSim LiDAR
  message type (`CustomMsg` or supported `PointCloud2`) before any RViz/window
  review is treated as localization evidence;
- RViz2 point window shows raw/registered point clouds as small points and
  FAST-LIO odometry/path;
- RViz2 planner window shows a 3D local occupancy/SDF/voxel surface, not only
  a 2D `OccupancyGrid`;
- FAST-LIO error is evaluated against MWORKS/UE truth before any localization
  claim;
- global UE truth remains validation-only and is not provided to the planner.

Open implementation decision before coding:

```text
LiDAR generation path:
  A. UE C++ raycast sensor bridge using Sunray Mid360 scan CSV.
  B. ROS2 C++ replay/live adapter using UE exported collision truth.
  C. ROS1 Sunray/Gazebo plugin reference route with bridge/container.
```

Current recommendation: start with B for repeatable rate/timestamp validation,
then move to A for real UE live scenes. C remains the reference and fallback
because the host mainline is ROS2 Humble.

## 8.3 Current MoSim Gap Analysis

Existing MoSim files are useful but not yet product-correct:

| File / Module | Current Status | Required Correction |
|---|---|---|
| `Scripts/ros/publish_mworks_uav_state_ros2.py` | Useful replay bridge for truth odometry, IMU, TF, and LiDAR smoke. IMU may be resampled from lower-rate MWORKS rows. | Keep as replay/smoke unless a live or high-rate MWORKS export is connected. Add explicit high-rate source validation before calling IMU 200Hz final evidence. |
| `Scripts/UE5/generate_livox_like_lidar_replay.py` | Good direction: reuses Sunray `mid360-real-centr.csv` and UE collision truth to create dense frames with attributes. | Treat as repeatable sensor-oracle replay, not live UE LiDAR. Add manifest checks for point density, scan duration, per-point time monotonicity, frame id, and scan pattern slice. |
| `Scripts/ros/mosim_dense_lidar_cpp` | Correct direction for transport performance. The ROS2 mainline now uses Livox-compatible `PointCloud2` fields: `offset_time`, `x`, `y`, `z`, `intensity`, `tag`, `line`. | Still only a replay/transport probe until actual FAST-LIO subscriber throughput, timestamp policy, extrinsics, and truth-error evaluation pass. Use Sunray `livox2Point.cpp` as the compatibility reference. |
| `Scripts/ros/mosim_scene_replay/launch/spark_fast_lio_mosim.launch.py` | Useful ROS2 FAST-LIO candidate launcher with MoSim frame names. | FAST-LIO acceptance still requires actual subscriber-side throughput, stable timestamps, extrinsic review, and truth-error evaluation. |
| `Config/rviz2/mosim_uav_fastlio_pointcloud*.rviz` | Correct native review surface. | Ensure point display uses small point rendering, not large spheres/markers. |
| `Config/rviz2/mosim_uav_planning_grid*.rviz` | Correct window split direction. | Replace or augment 2D-only grid with 3D local occupancy/SDF/voxel PointCloud2 or MarkerArray view. |
| keyboard/manual mapping scripts | Useful only for operator smoke tests. | Mark as non-product route. Formal controller/planner work must not depend on cell-step motion. |

## 8.4 Rate And Synchronization Contract

All future implementation slices must write an evidence summary with the
following checks:

```text
state/truth:
  /mosim/truth/odometry        20-100Hz, monotonic stamps, continuous pose
  /tf                          >=20Hz, world/map -> base -> imu/lidar

IMU:
  /mosim/imu or /uav1/livox/imu
  200Hz target
  source is either high-rate MWORKS/sensor output or explicitly resampled

LiDAR:
  /mosim/livox/lidar or /uav1/livox/lidar
  10Hz hardware-faithful baseline, 20Hz enhanced-sim target
  per-point offset_time required
  line/tag/reflectivity required for Livox-compatible path

controller/planner:
  planner PositionCommand / B-spline output
  adapter streams 20Hz setpoints to MWORKS
  no direct pose jumps

FAST-LIO:
  consumes synchronized LiDAR + IMU
  publishes registered cloud, odometry, and path
  output compared against MWORKS/UE truth
```

Hard failure conditions:

- nonmonotonic timestamps;
- LiDAR frame rate below the declared mode without a documented performance
  reason;
- missing per-point time for any FAST-LIO claim;
- planner using global UE occupancy truth as input;
- UAV motion controlled by grid-cell increments;
- RViz map review limited to a 2D `OccupancyGrid` when claiming 3D planning.

## 9. Immediate Open Questions

1. Can UE LiDAR generation run fast enough at 10-20Hz while preserving per-point
   timestamps, or should we first use a validated ROS/Gazebo-style sensor plugin?
2. What exact Sunray150 physical parameters should be treated as source of truth
   for mass, inertia, motor, propeller, battery, and sensor extrinsics?
3. Should PX4 be included in the first MoSim loop, or should MWORKS controller
   replace PX4 initially and only maintain PX4-compatible topics?
4. Factory FAST-LIO runtime is currently degraded. The next audit must isolate
   whether the main causes are timestamp policy, extrinsic mismatch, scan
   pattern, initial motion excitation, or map/sensor sparsity.

## 10. Next Work

Continue with a small credible runtime instead of polishing the rejected
manual/keyboard path:

1. mark keyboard/manual mapping scripts as smoke-only/deprecated for mainline
   evidence;
2. implement or identify the MWORKS-to-ROS2 continuous state/IMU publisher;
3. publish a Mid360-shaped LiDAR topic with coherent stamps and measured rate;
4. run RViz2 split windows with point size matching FAST-LIO practice;
5. run `spark-fast-lio` on Factory and record why it fails or passes;
6. only then add planner closure from local 3D map to MWORKS controller
   setpoints.

## 11. Implementation Plan After This Design Gate

Priority order:

1. **Clean evidence boundary.**
   Mark existing keyboard/grid movement outputs as `smoke_only` in the relevant
   workflow/docs and prevent them from being cited as controller or FAST-LIO
   evidence.
2. **State/IMU bridge correction.**
   Upgrade the MWORKS-to-ROS2 bridge so every run reports source rate,
   resampling status, timestamp monotonicity, odometry continuity, TF tree, and
   controller/setpoint contract status.
   2026-06-02 update: `publish_mworks_uav_state_ros2.py --dry-run` now emits
   machine-readable `source_rate`, `resampling`, `timestamp_policy`,
   `odometry_continuity`, `lidar_input`, and `tf_contract` fields. Current IMU
   remains explicitly marked `resampled_from_mworks_state` when the source CSV
   is only 20Hz.
3. **Livox-compatible dense publisher.**
   Change the dense C++ publisher/replay path from generic Velodyne-style fields
   to Livox-compatible fields or custom message semantics:
   `offset_time`, `x`, `y`, `z`, `intensity`, `tag`, `line`. Use Sunray
   `livox2Point.cpp` as the compatibility reference.
   2026-06-02 update: the ROS2 Python bridge, ROS2 FAST-LIO replay publisher,
   and C++ dense replay publisher now advertise the Livox-compatible
   `PointCloud2` field names. This is a data-contract correction only; it does
   not by itself prove FAST-LIO quality.
4. **3D map review surface.**
   The planning RViz2 configs keep 2D `OccupancyGrid` disabled as a reference
   layer and make `/mosim/local_occupancy_voxels` the active map evidence
   surface. The default view is now 3D Orbit rather than top-down orthographic
   so vertical occupancy can be manually inspected.
5. **FAST-LIO subscriber-side acceptance.**
   Measure the real FAST-LIO subscriber path instead of only publisher-side
   speed. Required outputs: registered cloud, odometry/path, topic rates,
   timestamp diagnostics, and truth-error summary.
6. **Planner adapter.**
   Reuse/adapt the Sunray/EGO contract: local 3D map + odometry -> B-spline or
   position command -> 20Hz MWORKS setpoint stream. Keep the planner global-map
   blind except for local sensor-derived data.
7. **UE live LiDAR bridge.**
   After replay timing is credible, port the scan generation into the UE side
   using the same Mid360 CSV pattern and scene raycasts, so the rendered map
   and sensor oracle are live.

Human review points:

- first RViz2 point-cloud window with corrected point size and dense
  Livox-shaped frames;
- first RViz2 3D local map window, specifically verifying that it can rotate in
  3D and is not a 2D-only grid;
- first UE + RViz2 + MWORKS synchronized run in Factory;
- first FAST-LIO truth-error report before accepting localization;
- first planner-to-MWORKS setpoint loop before accepting autonomous movement.

Blockers that should trigger WeChat/manual intervention:

- UE Editor or MCP listener cannot be controlled when live raycasts are needed;
- MWORKS activation/login or solver export fails;
- ROS2/FAST-LIO build/runtime cannot publish required output topics;
- cc-connect/WeChat notification state fails repeatedly after one recorded
  retry boundary;
- any implementation requires deleting or moving user scene assets.

## 12. Goal Coverage Audit

| Requirement | Current Evidence | Status | Missing Evidence |
|---|---|---|---|
| Stop the rejected keyboard/grid-cell route | Keyboard/manual loop is documented and marked `quality_status=smoke_only`; product claims are blocked in dry-run output. | partially done | Keep future workflow/tests from depending on this route for controller or FAST-LIO claims. |
| Understand and reuse UAV/Gazebo/Sunray/RFlySim-style architecture | Source audit captured PX4-style streaming setpoints, Sunray `external_fusion`/control/planner/Mid360 contracts, FAST-LIO boundaries, and UE/RViz window split. | design gate done | Deeper Sunray150 physical parameter/extrinsics audit still required. |
| MWORKS remains solver/controller authority | Design and bridge contract state MWORKS owns truth, IMU source, controller/setpoint interface. | design done | Live/high-rate MWORKS export or co-simulation bridge is still missing. |
| IMU 200Hz, controller 20Hz, LiDAR 10Hz baseline/20Hz target | Bridge dry-run now reports target rates, source rate, resampling, timestamp policy, and odometry continuity. | partial | Current IMU is resampled from 20Hz CSV; final 200Hz sensor evidence is not available. |
| Mid360/FAST-LIO-compatible LiDAR data | ROS2 Python bridge, ROS2 replay publisher, and C++ dense publisher now use Livox-compatible `PointCloud2` fields. | partial | Need real subscriber-side throughput, CustomMsg route decision, extrinsics, and FAST-LIO output quality. |
| 3D map and point-cloud native windows | RViz2 point cloud uses `Points` with 1 px size; planning window uses 3D voxel cloud and default 3D Orbit view; 2D grid disabled as reference. | partial | Need runtime screenshot/manual audit and real local mapping/planner output, not smoke oracle only. |
| FAST-LIO runtime claim | Factory has recorded `/odometry`, `/path`, and `/cloud_registered`, but evaluations fail with RMSE about 9.8-10.2m and max error about 17.7-18.5m. Dense LiDAR transport subscriber gate now passes around 9.69Hz, so the next issue is FAST-LIO quality, not only raw transport. | not done | Diagnose Factory failure causes: timestamp policy, scan pattern, extrinsics, motion excitation, initialization, and map/scene geometry. |
| WeChat milestone/blocker reports | WeChat send failed twice with `ret=-2`; recorded in `PROGRESS.md`. | blocked | Gateway repair or re-login needed before relying on WeChat again. |

## 13. Factory FAST-LIO Failure Diagnosis

2026-06-02 update: the Factory FAST-LIO issue is now diagnosed as a quality and
input-contract failure, not a missing-topic failure. The reusable diagnostic is:

```bash
python3 Scripts/UE5/diagnose_fastlio_factory_failure.py
```

It writes:

```text
Results/unreal_scene_mapping/factoryenvironmentcollect/fastlio_failure_diagnosis.json
Results/unreal_scene_mapping/factoryenvironmentcollect/FASTLIO_FACTORY_FAILURE_DIAGNOSIS.md
```

Current diagnosis:

- both Factory runtime recordings publish odometry/path/registered-cloud
  outputs, but both fail quality gates;
- `fastlio_runtime` RMSE is about `10.20m`, max error about `17.71m`, with 2
  nonmonotonic odometry timestamp pairs;
- `fastlio_runtime_scan099` RMSE is about `9.76m`, max error about `18.55m`,
  with 59 nonmonotonic odometry timestamp pairs;
- the evaluated FAST-LIO replay dataset averages only about `509` points per
  frame, while the dense Livox-like replay manifest averages about `20.5k`
  points per frame;
- the evaluated replay uses synthetic finite-difference IMU for all frames,
  fixed yaw, and no per-point attribute array in the sampled
  `fastlio_replay_dataset.jsonl` frames;
- current ROS2 FAST-LIO config is still Velodyne-like:
  `lidar_type=2`, `scan_line=16`, `scan_rate=10`, while the target Sunray /
  Mid360 contract is Livox-like, typically `lidar_type=1`, `scan_line=4`, with
  per-point timing and a defined LiDAR/IMU extrinsic.

Required order before another Factory FAST-LIO claim:

1. Move Factory runtime input from the low-density legacy replay to the dense
   Livox/Mid360-shaped path with per-point timing fields.
2. Create and test a Mid360/Livox FAST-LIO config route for the chosen ROS2
   FAST-LIO implementation.
3. Replace synthetic finite-difference IMU with high-rate MWORKS IMU or a
   physically consistent simulated IMU synchronized to LiDAR.
4. Fix nonmonotonic runtime timestamps and rerun runtime evaluation.
5. Only after Factory localization passes should local 3D map and planner
   closure be reconnected.

2026-06-02 follow-up: the Mid360 config route and input contract checker now
exist. `Config/ros2/mosim_spark_fast_lio_mid360.yaml` uses Livox semantics
(`lidar_type=1`, `scan_line=4`, `scan_rate=10`, `blind=0.5`) with fixed
identity extrinsics for the current synthetic-aligned MoSim replay. ROS2 launch
defaults were moved from the legacy `/velodyne_points` and `/imu/data` route to
`/mosim/lidar_points` and `/mosim/forward/imu`. The contract report for Factory
is `dense_lidar_ready_but_fastlio_input_blocked`: the dense Mid360 replay
sample is ready, but the old FAST-LIO dataset and synthetic IMU remain blocked
for any localization claim.

Current gate command:

```bash
python3 Scripts/UE5/check_fastlio_input_contract.py \
  --scene-dir Results/unreal_scene_mapping/factoryenvironmentcollect \
  --config Config/ros2/mosim_spark_fast_lio_mid360.yaml
```

Factory FAST-LIO input replay now prefers the MWORKS-state plus dense Mid360
bridge instead of the old 512-point adapter:

```text
Scripts/ros/publish_mworks_uav_state_ros2.py
  --mworks-raw-csv .../mworks_smoke/raw/sunray150_ue_factoryenvironmentcollect_linear_mpc_smoke.csv
  --lidar-point-frames-jsonl .../livox_like_lidar_frames.jsonl
  --imu-rate-hz 200
  --lidar-rate-hz 10
```

This is still replay/co-simulation plumbing, not final localization evidence.
It becomes a claim only after real FAST-LIO runtime produces registered cloud,
odometry/path, monotonic timestamps, and acceptable truth-error metrics.

ROS2 topic separation is now explicit:

```text
/mosim/lidar_points                dense Mid360/FAST-LIO input
/mosim/forward/imu                 IMU input for FAST-LIO
/mosim/mapping_smoke/lidar_points  sparse visualization-only mapping smoke
```

Derelict was brought to the same dense Mid360 input gate on 2026-06-02. Its
Livox-like replay averages about 24.3k points/frame and passes the dense input
portion of the contract. Both accepted scenes are therefore ready for the next
FAST-LIO runtime integration step, but neither scene has accepted localization
metrics yet.

2026-06-02 runtime blocker: the current ROS2 `spark-fast-lio` candidate is not
a valid Mid360/Livox `PointCloud2` runtime for this config. Its
`Preprocess::process(sensor_msgs::msg::PointCloud2)` path accepts only
`OUST64`, `KMOUST64`, and `VELO16`; `lidar_type=1` reaches `Error LiDAR Type`.
The Livox handler is behind `LIVOX_ROS_DRIVER_FOUND` and expects
`livox_ros_driver::CustomMsg`. The dense Factory smoke run therefore generated
zero odometry/path/registered-cloud output. Evidence:

```text
Results/unreal_scene_mapping/factoryenvironmentcollect/FASTLIO_MID360_RUNTIME_BLOCKER.md
```

This changes the next implementation decision. Do not continue by changing
RViz point size, grid-cell step, or visualization-only publishers. The next
accepted route must either provide Livox `CustomMsg` support for the FAST-LIO
runtime, switch to a Mid360/Livox-capable FAST-LIO implementation, or mark a
Velodyne-compatible run as degraded smoke only. Timestamp policy also remains
open because the failed run emitted `TF_OLD_DATA`, indicating mixed replay-time
and wall-time stamps.

2026-06-02 follow-up: the runtime route choice is now executable through:

```bash
python3 Scripts/UE5/check_fastlio_runtime_candidates.py --write
```

The report is:

```text
Results/unreal_scene_mapping/FASTLIO_RUNTIME_CANDIDATES.md
Results/unreal_scene_mapping/FASTLIO_RUNTIME_CANDIDATES.json
```

Current decision: `patch_ros2_livox_custommsg_candidate_first`.
`spark-fast-lio` is the only local native ROS2 FAST-LIO-family candidate, but
it must be patched before it can be used for Mid360. The candidate scan reports
four hard blockers in the current source: Livox/Mid360 `lidar_type=1` is not
accepted through `PointCloud2`; the Livox CustomMsg path is guarded; ROS1
`livox_ros_driver` and ROS2 `livox_ros_driver2` naming is mixed; and one Livox
callback macro is inconsistent. Local ROS1 `FAST_LIO` plus Sunray Livox Gazebo
plugin remain the strongest semantic references for `CustomMsg`, per-point
time, line id, and Mid360 scan pattern, but they are not native ROS2 evidence
unless an explicit bridge/container route is selected.

2026-06-02 patch-readiness gate:

```bash
python3 Scripts/UE5/check_spark_fastlio_livox_patch_readiness.py --write
```

Report:

```text
Results/unreal_scene_mapping/SPARK_FASTLIO_LIVOX_PATCH_READINESS.md
Results/unreal_scene_mapping/SPARK_FASTLIO_LIVOX_PATCH_READINESS.json
```

Current result: `ready=false`,
`decision=patch_required_before_mid360_runtime_claim`. The stricter static gate
finds the exact source-level blockers that must be fixed before opening more
RViz/FAST-LIO review windows:

- CMake/package logic still looks for ROS1 `livox_ros_driver` instead of
  consistently using ROS2 `livox_ros_driver2`;
- `preprocess.h` still includes ROS1 `livox_ros_driver/CustomMsg.h`;
- `Preprocess::process()` / `avia_handler()` signatures do not consistently
  accept `livox_ros_driver2::msg::CustomMsg`;
- the Livox macro path contains `LIVOXROS_DRIVER_FOUND` vs
  `LIVOX_ROS_DRIVER_FOUND`;
- the subscriber binding uses `livoxLidarCallback` while the declared function
  is `livoxLiDARCallback`;
- the Livox callback contains `imu_buffer` vs `imu_buffer_` and
  `nanseconds()` vs `nanoseconds()` typos;
- the standard `PointCloud2` path still cannot be treated as a Mid360 runtime
  claim because it is Ouster/Kimera/Velodyne-oriented.

This gate is intentionally static. Passing it later will only mean "the
candidate is coherent enough to build and run a Livox CustomMsg runtime test".
Localization evidence still requires nonzero `/cloud_registered`, odometry,
path, coherent LiDAR/IMU/TF timestamps, and truth-error metrics.

## 14. Correct Execution Order After User Review

The user explicitly rejected optimizing the current grid-step and toy-display
route. The next work must follow this order:

1. Reuse real UAV stack patterns first: MWORKS solver/controller, UE
   scene/sensor oracle, ROS2 LiDAR/IMU/TF, FAST-LIO, 3D local map, planner,
   RViz2 native review windows.
2. Patch or replace the FAST-LIO runtime so it accepts the actual MoSim
   Mid360/Livox message surface.
3. Prove a headless runtime contract before any GUI review: dense LiDAR input,
   200Hz IMU, unified timestamps, fixed extrinsic, nonzero registered cloud,
   odometry, and path.
4. Only then open RViz2 split windows for user review. Point cloud and 3D map
   should be live outputs tied to UAV motion, not static data or hand-tuned
   marker sizes.
5. After localization is credible, reconnect a Sunray/EGO-style local 3D map
   and planner. The planner may use local sensed map state only; UE global
   truth remains a validation oracle.
6. After planner commands are credible, convert position/velocity/acceleration
   and yaw setpoints to the 20Hz MWORKS controller interface. Do not let map
   cell size or keyboard step size drive vehicle motion.

## 15. 2026-06-02 Real UAV Stack Correction

The latest review exposed a deeper issue than RViz display tuning: the current
prototype still treats mapping as a visual script rather than as a UAV
perception-control stack. The next implementation must not optimize the wrong
abstraction.

Rejected product behaviors:

- moving the UAV by one map cell or any other display-grid step;
- using a 2D `OccupancyGrid` as the accepted UAV map review surface;
- treating static or synthetic point clouds as FAST-LIO evidence;
- reducing point density merely to make a fake display reach frame rate;
- directly overwriting pose from keyboard/manual input;
- opening RViz/UE for acceptance before headless sensor, timing, FAST-LIO, and
  truth-error gates pass.

Correct stack boundary:

```text
MWORKS
  -> continuous dynamics, controller, truth, motor/wind/fault effects,
     200Hz IMU source, 20Hz setpoint/control interface

UE / MoSimSceneLibrary
  -> accepted Factory/Derelict rendered scene, UAV body, camera,
     collision and LiDAR raycast oracle

ROS2 Humble
  -> /mosim/forward/imu, /mosim/livox/lidar or /mosim/lidar_points,
     /tf, odometry, FAST-LIO, local 3D map, planner, command adapter

RViz2
  -> live FAST-LIO point cloud/registered cloud/odometry/path window
  -> live 3D local map/planner-state window
```

Authoritative patterns rechecked:

- PX4 Offboard: external control is a continuous streamed contract. PX4
  requires a continuous proof-of-life stream above 2Hz before and during
  offboard operation; MoSim's command interface should use 20Hz setpoint/control
  streaming and explicit timeout/failsafe handling.
- PX4 ROS2: PX4/ROS2 integration depends on matched message definitions and
  uXRCE-DDS bridge semantics; future PX4 integration must be version-aware.
- Livox Mid360: hardware-faithful baseline is 10Hz point-cloud frames at about
  200k points/s, built-in IMU at 200Hz, and explicit time synchronization
  options. A 20Hz LiDAR mode is allowed only as an enhanced simulated sensor
  after baseline throughput and localization quality gates pass.
- FAST-LIO: localization evidence requires synchronized LiDAR/IMU, per-point
  timing for motion compensation, known extrinsics/time offset, and runtime
  outputs. A visible cloud alone is not evidence.
- Sunray source: reuse the architecture shape, not only individual scripts:
  `external_fusion`, `sunray_control_node`, Mid360/FAST-LIO launch,
  EGO-planner 3D local map, `traj_server`, `positionCmd2sunray`, and command
  timeout/odom-valid/geofence style checks.
- RflySim: RflySim3D/UE is a 3D rendering and perception-data engine, while
  CopterSim/PX4 owns motion/control. Sensor data is exported to algorithms by
  ROS, UDP, or shared memory; this validates MoSim's UE/ROS2/RViz split.

Minimum credible loop, in order:

1. **State source gate**: MWORKS state is continuous; velocity/acceleration
   jumps are bounded; no direct pose overwrite exists in the product path.
2. **Sensor timing gate**: IMU is published at 200Hz, LiDAR at 10Hz baseline,
   controller/setpoints at 20Hz; all message stamps are monotonic in one clock
   domain.
3. **Mid360 message gate**: Livox/Mid360 data includes per-point offset,
   line/ring identity, intensity/reflectivity, frame id, extrinsic, and scan
   duration. `PointCloud2` may be used only if the selected FAST-LIO runtime
   actually supports that contract; otherwise use Livox `CustomMsg`.
4. **FAST-LIO runtime gate**: require nonzero registered cloud, odometry, and
   path; record topic rates, frame counts, timestamp diagnostics, and
   truth-error metrics.
5. **3D local map gate**: local map must be rotatable 3D voxel/SDF/ESDF-style
   state derived from live sensor/odometry data. A 2D grid is a reference layer
   only.
6. **Planner gate**: planner consumes local sensed map and estimated odometry
   only. UE global truth is a validation oracle and must not become the known
   global map.
7. **Controller gate**: planner output is converted to position, velocity,
   acceleration, yaw/yaw-rate setpoints streamed to MWORKS at 20Hz with timeout
   handling.

Current implementation implication:

- Continue treating `spark-fast-lio` as a patch/replace target, not accepted
  evidence. The latest static gate still shows the decisive blocker: its
  standard `PointCloud2` preprocessing path rejects Livox `lidar_type=1`, so a
  visible PointCloud2 cloud is not enough for Mid360 FAST-LIO evidence.
- Before spending more time on that patch, evaluate a native Mid360 ROS2
  candidate first. The current preferred external candidate is
  `Ericsii/FAST_LIO_ROS2` branch `ros2`: visible source metadata shows
  `ament_cmake`, `livox_ros_driver2`, `mapping.launch.py`, default
  `mid360.yaml`, `/livox/lidar`, `/livox/imu`, `lidar_type=1`,
  `scan_line=4`, and `scan_rate=10`. Current local import by `git clone`,
  `git ls-remote`, and branch zip download timed out within the 60s operation
  gate, so this is a candidate-selection decision only, not runtime evidence.
  The next implementation should import it into an ignored temp workspace,
  build it with ROS2 Humble plus local `livox_ros_driver2`, then run the same
  headless truth gates.
- Do not open manual UE/RViz review windows again until the headless gates
  above pass for Factory.
- WeChat notification for this checkpoint was attempted once through the
  project adapter with `MoSim｜微信通知网关` and the project-local session key.
  It failed with `weixin: sendMessage: ret=-2 errcode=0`; do not retry in a
  loop until cc-connect runtime/session state is refreshed.

Reference URLs used for this checkpoint:

- `https://docs.px4.io/main/en/flight_modes/offboard.html`
- `https://docs.px4.io/main/en/ros2/user_guide.html`
- `https://www.livoxtech.com/mid-360/specs`
- `https://livox-wiki-en.readthedocs.io/en/latest/tutorials/new_product/mid360/mid360.html`
- `https://github.com/hku-mars/FAST_LIO`
- `https://rflysim.com/doc/en/3/RflySim3DUE.html`

## 16. 2026-06-02 Headless Runtime Handoff

Current status after the handoff check:

- ROS MCP currently sees only rosbridge and static TF nodes. There is no active
  FAST-LIO, MoSim sensor publisher, odometry, registered-cloud, or planner
  runtime in the ROS graph.
- Factory dense input is not the blocker anymore. The input contract is
  `claimable_input_ready`: MWORKS replay can provide continuous truth/control
  timing, 200Hz IMU, and dense 10Hz Livox-like frames with four lines and
  per-point timing fields.
- The blocker is now the selected FAST-LIO runtime. The patched
  `spark-fast-lio` route reaches the Livox `CustomMsg` callback, logs
  `point_num=21002`, enters `Livox avia_handler`, then crashes with exit code
  `-11` before publishing `/odometry`, `/path`, or `/cloud_registered`.
- Because the runtime output count is still zero, opening UE/RViz2 windows
  would only review display plumbing. It is not accepted evidence for
  localization, 3D mapping, or controller integration.
- The temporary `spark-fast-lio` candidate source had repeated startup-log and
  filter-check blocks in `spark_fast_lio.cpp`; those were removed so future
  diagnostics are readable. Python gates now pass, but the C++ component build
  on the Windows-mounted `/mnt/c` workspace still exceeds the 60 second
  command rule and reports clock-skew warnings. Treat the current build as
  incomplete until a dedicated WSL-local or longer approved build finishes.
- A fresh import attempt for `Ericsii/FAST_LIO_ROS2` timed out at the 60 second
  network gate and the partial clone was removed. It remains a preferred
  candidate by interface shape, but it is not yet local evidence.

Immediate implementation order:

1. Keep the Factory headless gate as the first acceptance gate:
   `FASTLIO_INPUT_CONTRACT.md` must remain `claimable_input_ready`, and
   `REALSTACK_MINILOOP_GATE.md` must become nonzero for odometry, path, and
   registered cloud.
2. Decide the FAST-LIO route by evidence, not by code ownership:
   - finish a bounded `spark-fast-lio` Livox preprocess/runtime patch only if
     it can publish stable output after rebuild;
   - otherwise switch to a ROS2 Mid360 implementation that natively declares
     `livox_ros_driver2`, `/livox/lidar`, `/livox/imu`, `lidar_type=1`,
     `scan_line=4`, and `scan_rate=10`;
   - keep ROS1 `FAST_LIO` and Sunray as semantic references unless a ROS1/ROS2
     bridge is explicitly chosen.
3. Use Sunray as the local architecture reference:
   - `external_fusion_node` loops at 200Hz;
   - Mid360 mapping uses `/livox/lidar` and `/livox/imu`;
   - EGO planner consumes odometry plus world-frame/local point cloud and owns
     a 3D local map;
   - `traj_server` and `positionCmd2sunray` convert planner output into UAV
     control commands.
4. After FAST-LIO is nonzero, add the 3D local map gate. A 2D occupancy grid is
   allowed only as an auxiliary projection, not the accepted UAV map surface.
5. Only after Factory passes the headless gates should manual review open the
   three native windows: UE render, RViz2 FAST-LIO point cloud, and RViz2 3D
   local map/planner state.

Reusable commands:

```bash
python3 Scripts/UE5/check_fastlio_input_contract.py \
  --output-json Results/unreal_scene_mapping/factoryenvironmentcollect/fastlio_input_contract.json \
  --output-md Results/unreal_scene_mapping/factoryenvironmentcollect/FASTLIO_INPUT_CONTRACT.md

python3 Scripts/UE5/check_realstack_miniloop_gate.py \
  --output-json Results/unreal_scene_mapping/factoryenvironmentcollect/realstack_miniloop_gate.json \
  --output-md Results/unreal_scene_mapping/factoryenvironmentcollect/REALSTACK_MINILOOP_GATE.md
```

## 17. 2026-06-02 Architecture Validation Closure

This checkpoint closes the current design question and defines the next
implementation gate. The result is not "ready to fly"; it is "the architecture
boundary is now clear enough to implement without returning to toy mapping".

### Gate A Result: MWORKS Generated Controller Runtime

Status: `passed_for_pid_demo_runtime_path`.

Evidence:

- `Models/QuadrotorControllerBlocks/AWFF_PID_Sysblock_Demo_SIL_Constant.mo`
- `Results/codegen_probe/AWFF_PID_Sysblock_Demo_api/mworks_constant_0p1_reference.json`
- `Results/codegen_probe/AWFF_PID_Sysblock_Demo_api/runtime_constant_0p1_check.json`
- `Results/codegen_probe/AWFF_PID_Sysblock_Demo_api/sil_constant_0p1_check.json`
- tests:
  - `python3 Scripts/tests/test_mworks_codegen_runtime.py`
  - `python3 Scripts/tests/test_mworks_codegen_sil_equivalence.py`

Engineering conclusion:

- MWORKS/Sysblock can generate a C runtime with a stable `Init`/`Step`
  interface, input/output globals, and 0.01s sample time.
- The PID demo nonzero constant-input SIL check passed: generated C output
  matches MWORKS reference output order with max absolute error below `1e-5`.
- This validates the generated-controller-runtime direction for MoSim.
- It does not prove all future controllers are accepted. Each generated
  controller still needs its own SIL gate, especially time-varying inputs,
  saturation, delay, mode switches, and safety/fault logic.

### Gate B Result: UE Truth + ROS2 + Mid360/FAST-LIO

Status: `blocked_before_manual_review`.

Evidence:

- `Results/unreal_scene_mapping/factoryenvironmentcollect/REALSTACK_MINILOOP_GATE.md`
- `Results/unreal_scene_mapping/factoryenvironmentcollect/FASTLIO_FACTORY_FAILURE_DIAGNOSIS.md`
- `Results/unreal_scene_mapping/factoryenvironmentcollect/fastlio_failure_diagnosis.json`
- `Results/unreal_scene_mapping/factoryenvironmentcollect/fastlio_runtime_cpp_livox_headless_20260602_090500/FASTLIO_RUNTIME_EVALUATION.json`

Engineering conclusion:

- Dense Mid360-shaped input and nonzero FAST-LIO output are no longer the only
  blockers. The current evidence shows three relevant stages:
  - older selected runs could record zero FAST-LIO odometry/path/cloud samples;
  - earlier nonzero-output runs failed with about 9-10m RMSE and about 18m max
    position error because the replay route mixed LiDAR, IMU/state, and truth
    sources and published world-frame points as body-frame LiDAR points;
  - the corrected same-source body-frame smoke run produced `/Odometry=41`,
    `/path=4`, `/cloud_registered=40`, RMSE `1.019363m`, and max error
    `1.437659m`, which is close but still above the formal RMSE threshold and
    not dense/long enough for final evidence.
- Therefore RViz/UE review windows must stay closed as acceptance evidence.
  Visual point-cloud tuning cannot fix the missing runtime and localization
  quality gates.
- The next valid implementation is a formal same-source body-frame Factory
  headless gate. If that route remains above threshold, diagnose evaluation
  alignment, initialization transient, extrinsics, gravity/IMU convention, and
  scan timing before changing the product architecture.
- The first accepted Factory result must show nonzero `/cloud_registered`,
  odometry, and path, monotonic timestamps, explicit extrinsics, and a passing
  truth-error evaluation before user window review.

2026-06-02 formal result: the accepted headless Factory result is
`fastlio_runtime_factory_mworks_body_formal_20260602_122033`; it satisfies the
nonzero runtime-topic, monotonic timestamp, and truth-error requirements for
opening manual UE/RViz2 review.

### Gate C Result: Closed-Loop Contract

Status: `design_closed_for_next_implementation`.

Accepted role split:

```text
MWORKS/Sysblock/Syslab
  -> plant solve, controller design, generated controller runtime, formal
     truth, IMU source, metrics, report evidence

UE / MoSimSceneLibrary
  -> accepted Factory/Derelict rendering, UAV visual body, camera, collision
     and LiDAR/sensor oracle

ROS2 / RViz2
  -> LiDAR/IMU/TF transport, FAST-LIO, registered cloud, odometry, path,
     3D local map, planner state, native robotics review windows

V6X/PX4/companion-computer adapter
  -> deployment boundary, streamed setpoint/control semantics, failsafe,
     timeout handling, hardware-facing C/C++ route
```

Minimum accepted data contract:

| Channel | Baseline | Owner | Acceptance |
|---|---:|---|---|
| controller/setpoint | 20Hz | MWORKS/controller runtime | continuous stream; no pose overwrite |
| MWORKS truth/state | at least 20Hz | MWORKS | monotonic, bounded velocity/acceleration jumps |
| IMU | 200Hz | MWORKS/sensor bridge | one clock domain, coherent acceleration/angular velocity |
| Mid360 LiDAR | 10Hz, about 200k points/s | UE sensor oracle / ROS2 bridge | per-point timing, line/tag/intensity, explicit frame id |
| FAST-LIO | LiDAR driven | ROS2 runtime | nonzero registered cloud, odometry, path, truth RMSE/max-error gate |
| 3D local map | runtime local map | ROS2 planner stack | rotatable 3D map; 2D grid is auxiliary only |
| planner output | 20Hz setpoint-compatible | ROS2 planner / adapter | local sensed map only; no UE global truth leakage |

Manual review policy:

- WeChat is the default progress, blocker, and manual-review channel for this
  work. Use sparse packets only.
- If WeChat sending fails, diagnose before assuming the user was notified:
  `no active session found` means resolve the cc-connect active session;
  `ret=-2` means refresh the Weixin/iLink send context by asking the user to
  send one normal message, then retry once.
- If the gateway cannot be restored quickly, report the exact failure in the
  main conversation and continue with file-based progress records unless the
  task requires approval.

Next implementation gate:

```text
Factory headless FAST-LIO acceptance
  -> selected Mid360/Livox FAST-LIO runtime builds and runs
  -> MWORKS state/IMU + dense LiDAR + TF are published in one clock domain
  -> /cloud_registered, odometry, and path are nonzero
  -> odometry is compared against MWORKS/UE truth and passes thresholds
  -> only then open UE + RViz2 FAST-LIO + RViz2 3D local-map windows
```
