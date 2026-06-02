# UE/ROS/MWORKS UAV Simulation Architecture Replan

Date: 2026-06-02

Status: draft v2 after rejecting the hand-rolled keyboard-grid / synthetic
point-cloud path and auditing Sunray / FAST-LIO / Gazebo-style UAV flows.

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

## 2. Reference Architecture Findings

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

- `https://docs.px4.io/main/en/ros2/user_guide`
- `https://docs.px4.io/main/en/ros2/offboard_control`

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

- `https://www.livoxtech.com/cn/mid-360/specs`
- `https://github.com/hku-mars/FAST_LIO`
- Local: `References/Lab/FAST_LIO/config/mid360.yaml`
- Local: `References/Sunray/simulation/sunray_simulator/launch_slam/mid360.yaml`

### FAST-LIO

FAST-LIO is not a visualization plugin; it is a LiDAR-inertial odometry runtime.
For Livox serial sensors it depends on Livox message data that carries
per-point timestamps. FAST-LIO's own README warns that Livox point timestamps
are important for motion undistortion and that software time sync should only
be enabled when external sync is unavailable.

Current local source status:

- `References/Lab/FAST_LIO` is ROS1/catkin.
- `References/Lab/FAST-LIVO2` is ROS1/catkin.
- `References/Lab/Point-LIO-point-lio-with-grid-map` is ROS1/catkin.
- Existing ROS2 candidate `spark-fast-lio` built under `Results/tmp`, but
  Factory runtime quality is currently degraded and cannot be claimed final.

Evidence:

- `Results/unreal_scene_mapping/FASTLIO_FAMILY_COMPATIBILITY.md`
- `Results/unreal_scene_mapping/FASTLIO_RUNTIME_STATUS.md`
- `Results/unreal_scene_mapping/SPARK_FASTLIO_ROS2_CANDIDATE.md`

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

### RFlySim / AirSim / Gazebo Pattern

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

## 3. Target Multi-Rate Contract

Initial contract for the minimum credible loop:

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

## 3.1 Current Minimum Bridge Evidence

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
- This validates C++ as the correct direction, but it is not yet a final
  FAST-LIO input. Next work should evaluate the actual FAST-LIO subscriber path
  or a dedicated C++ subscriber, then investigate QoS, DDS/WSL bottlenecks,
  loaned messages or shared-memory transport, and a realistic point-density/rate
  tradeoff before making localization claims.

Target next gate before FAST-LIO claims:

```text
MWORKS-derived continuous trajectory
  -> dense LiDAR frame or Livox-like CustomMsg with per-point time/ring
  -> synchronized IMU/LiDAR timestamps and extrinsics
  -> FAST-LIO runtime publishes /cloud_registered, odometry, and path
  -> RViz2 shows small rendered points, not large sphere markers
```

## 3.2 Source-Code Contracts To Reuse

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

### Mid360 / FAST-LIO contract

Observed in:

- `References/Sunray/simulation/sunray_simulator/launch_slam/mid360.yaml`
- `References/Lab/FAST_LIO/config/mid360.yaml`
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

## 4. Proposed MoSim Minimum Loop

### Phase A: Architecture Alignment

1. Finish source audit of:
   - Sunray `sunray_uav_control`, `external_fusion`, EGO planner launch,
     Mid360/FAST-LIO launch, RViz configs;
   - RFlySim docs and scene bridge ideas;
   - AirSim/PX4 lockstep and ROS wrapper patterns;
   - existing MoSim MWORKS/UE bridge scripts.
2. Produce topic table and timing contract.
3. Decide whether the first credible runtime uses:
   - ROS2 native `spark-fast-lio`; or
   - ROS1 FAST-LIO in a container/bridge; or
   - Sunray ROS1 stack isolated as a reference-only route.

Decision for the next implementation slice:

```text
MWORKS-first continuous dynamics bridge + ROS2-native runtime first.
Sunray/ROS1 remains the reference contract and fallback, not the first runtime.
```

Reason:

- the host is Ubuntu 22.04 with ROS2 Humble already working;
- local Sunray/FAST_LIO sources are mostly ROS1/catkin and are valuable as
  architecture references but add bridge/container work before we can test the
  MoSim controller loop;
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

## 5. Reuse-First Choices

Prefer reuse:

- Sunray launch architecture and topic contracts.
- EGO planner local 3D map and B-spline pipeline, if buildable.
- FAST-LIO-family runtime, but only when real topics are recorded.
- RViz/RViz2 configs from Sunray/FAST-LIO as templates.
- RFlySim's separation of UE rendering from ROS point-cloud visualization.
- AirSim/PX4 lockstep principle when simulator timing is expensive.

Avoid or defer:

- hand-coded fake point clouds as final evidence;
- moving the UAV by occupancy cells;
- browser/HTML runtime visualization;
- claiming FAST-LIO from replay truth or reference odometry;
- feeding UE global truth directly to planner.

## 6. Immediate Open Questions

1. Can UE LiDAR generation run fast enough at 10-20Hz while preserving per-point
   timestamps, or should we first use a validated ROS/Gazebo-style sensor plugin?
2. What exact Sunray150 physical parameters should be treated as source of truth
   for mass, inertia, motor, propeller, battery, and sensor extrinsics?
3. Should PX4 be included in the first MoSim loop, or should MWORKS controller
   replace PX4 initially and only maintain PX4-compatible topics?
4. Factory FAST-LIO runtime is currently degraded. The next audit must isolate
   whether the main causes are timestamp policy, extrinsic mismatch, scan
   pattern, initial motion excitation, or map/sensor sparsity.

## 7. Next Work

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
