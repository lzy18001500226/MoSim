# Real UAV Stack Source Audit, 2026-06-02

Status: active design checkpoint. This file records why the current
keyboard-grid/static-cloud route is stopped and what to reuse next.

## User Correction

The visible mapping prototype is not acceptable as a product path:

- UAV motion must not step by occupancy-grid cell size.
- Keyboard/manual control must become a continuous velocity/position/
  acceleration/yaw setpoint stream, not a direct pose overwrite.
- Point cloud and local map must update with UAV state, LiDAR, IMU, TF, and
  estimator output.
- A 2D `OccupancyGrid` is not the accepted UAV map surface. It can be a
  reference layer only; active review needs a 3D local map/voxel/SDF-style
  state.
- RViz point size or point-density reductions must not be used to mask missing
  FAST-LIO or synchronization semantics.

## Upstream Contracts

| Source | Finding | MoSim Contract |
|---|---|---|
| PX4 Offboard | External control requires continuous proof-of-life/setpoint streaming and exits/failsafes if the stream drops below about 2Hz. | MoSim command path uses a 20Hz streamed setpoint/control contract with stale-command timeout. |
| PX4 ROS2/uXRCE-DDS | PX4 ROS2 integration depends on uXRCE-DDS and matching message definitions. | Future PX4 route must be message-version-aware; do not hard-code an arbitrary `px4_msgs` version. |
| Livox Mid360 | Hardware baseline is 10Hz typical frame rate, about 200k points/s, built-in IMU, and explicit PTP/GPS sync options. | Baseline simulation is 10Hz LiDAR plus 200Hz IMU; 20Hz LiDAR is an enhanced mode requiring throughput and localization gates. |
| FAST-LIO | Livox route needs LiDAR/IMU synchronization, per-point timing, extrinsics, and runtime odometry/cloud/path outputs. | A visible `PointCloud2` is display evidence only unless the chosen FAST-LIO runtime actually parses it for Livox. |
| RflySim | CopterSim/PX4 owns motion/control; RflySim3D/UE renders and generates perception data; ROS/external programs consume sensor data. | MWORKS owns dynamics/control/truth, UE owns rendering/sensor oracle, ROS2 owns algorithms and RViz2 review. |

Reference URLs:

- `https://docs.px4.io/main/en/flight_modes/offboard.html`
- `https://docs.px4.io/main/en/ros2/user_guide.html`
- `https://www.livoxtech.com/mobile/mid-360/specs`
- `https://github.com/hku-mars/FAST_LIO`
- `https://rflysim.com/doc/en/3/RflySim3DUE.html`

## Local Source Audit

### Sunray Control And Fusion

Relevant files:

- `References/Sunray/scripts_exp/uav_control_mid360.sh`
- `References/Sunray/scripts_exp/sunray_uav_ego_mid360.sh`
- `References/Sunray/scripts_sim/sunray_uav_ego_sim.sh`
- `References/Sunray/General_Module/sunray_uav_control/externalFusion/externalFusion.cpp`
- `References/Sunray/General_Module/sunray_uav_control/uav_control/UAVControl.cpp`

Reusable architecture:

```text
simulator/PX4/MAVROS
  -> external_fusion
  -> sunray_control_node
  -> Mid360 driver / FAST-LIO
  -> EGO planner 3D local map
  -> traj_server
  -> positionCmd2sunray
  -> control command
```

Specific lessons:

- `externalFusion.cpp` publishes high-rate fused state and odometry on a
  0.01s timer, while RViz trajectory/mesh/TF display is only 0.1s. MoSim should
  keep control/localization rates separate from display rates.
- `UAVControl.cpp` owns control mode, command timeout, odometry validity,
  geofence, takeoff, hover, landing, emergency kill, and setpoint publication.
  MoSim should put these semantics in the MWORKS/controller state machine or a
  dedicated command adapter, not in RViz/manual scripts.
- `handle_rc_control()` integrates joystick velocity over real elapsed time,
  proving that even manual control should be continuous. It is not grid-cell
  motion.
- `handle_cmd_control()` streams setpoints and checks command timeout when
  enabled. MoSim should use this pattern for planner-to-controller safety.

### Sunray Mid360 And FAST-LIO

Relevant files:

- `References/Sunray/General_Module/sunray_planner_utils/launch_driver/msg_MID360.launch`
- `References/Sunray/General_Module/sunray_planner_utils/launch_driver/mapping_mid360.launch`
- `References/Sunray/simulation/gazebo_plugin/livox_laser_simulation/src/livox_points_plugin.cpp`
- `References/Sunray/simulation/gazebo_plugin/livox_laser_simulation/msg/CustomMsg.msg`
- `References/Sunray/simulation/gazebo_plugin/livox_laser_simulation/msg/CustomPoint.msg`

Reusable details:

- Sunray launches `livox_ros_driver2` for MID360 and FAST-LIO mapping with
  `mid360.yaml`.
- The Gazebo Livox plugin replays `mid360-real-centr.csv`, assigns four lines,
  and can publish Livox-style `CustomMsg`.
- `CustomPoint` contains `offset_time`, `x/y/z`, `reflectivity`, `tag`, and
  `line`. MoSim must preserve these fields or prove the selected runtime
  supports an equivalent layout.
- Current plugin code uses `offset_time = 1e9 / 200000 * i`, matching the
  200k points/s baseline concept. MoSim must keep offsets within scan duration
  and in one clock domain.

### Sunray EGO Planner And 3D Map

Relevant files:

- `References/Sunray/General_Module/sunray_planner_utils/launch/sunray_ego_single_mid360.launch`
- `References/Sunray/General_Module/sunray_planner_utils/src/positionCmd2sunray.cpp`

Reusable details:

- EGO planner consumes odometry and global-frame point cloud.
- Its local grid-map settings are 3D: `resolution=0.12`,
  `local_update_range_x=5.5`, `local_update_range_y=5.5`,
  `local_update_range_z=4.5`, and obstacle inflation.
- `traj_server` converts B-spline trajectory to `PositionCommand`.
- `positionCmd2sunray` runs at 20Hz and maps position, velocity,
  acceleration, and yaw to a UAV control command.

MoSim implication: the accepted local-map/planner loop must be 3D and should
reuse the B-spline/setpoint contract before inventing a new planner interface.

## FAST-LIO Candidate Decision

Current local result:

- `spark-fast-lio` is ROS2/ament and patchable.
- It is not accepted for Mid360 because its standard `PointCloud2` path rejects
  Livox `lidar_type=1`.
- ROS1 `FAST_LIO` and Sunray Livox plugin are semantic references, not native
  ROS2 Humble runtime evidence.

Updated next route:

- Evaluate external `Ericsii/FAST_LIO_ROS2` branch `ros2` first.
- Visible metadata shows `ament_cmake`, `livox_ros_driver2`,
  `mapping.launch.py`, default `mid360.yaml`, `/livox/lidar`, `/livox/imu`,
  `lidar_type=1`, `scan_line=4`, and `scan_rate=10`.
- Current local import attempts timed out under the 60s command gate, so this
  is not yet local evidence.

Do not claim FAST-LIO until a runtime publishes nonzero registered cloud,
odometry, and path, with monotonic timestamps and truth-error evaluation.

## Next Gates

1. Import/build the preferred ROS2 Mid360 FAST-LIO candidate in ignored temp
   workspace when network allows.
2. Publish MWORKS truth/IMU and UE/Sunray-shaped Mid360 LiDAR with one clock
   domain.
3. Require headless topic evidence before GUI review:
   `/mosim/forward/imu`, `/mosim/livox/lidar` or equivalent,
   `/tf`, FAST-LIO odometry/path/registered cloud.
4. Compare FAST-LIO odometry to MWORKS/UE truth and record RMSE/max error.
5. Only after that open separate windows: UE rendered scene, RViz2 FAST-LIO
   point cloud, and RViz2 3D local map/planner state.
