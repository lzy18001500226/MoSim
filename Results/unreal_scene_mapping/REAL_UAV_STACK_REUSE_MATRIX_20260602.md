# Real UAV Stack Reuse Matrix, 2026-06-02

Status: active implementation guide for the UE/ROS2/MWORKS UAV line.

This matrix converts the current research into engineering decisions. The
goal is to reuse proven UAV-stack structure and code where practical, while
keeping MWORKS as the MoSim dynamics/controller/truth authority.

## Decision Summary

| Source | Reuse Level | What To Reuse | What Not To Reuse | MoSim Action |
|---|---|---|---|---|
| PX4 Offboard / ROS2 | architecture contract | continuous streamed control, keepalive/failsafe, estimator validity, frame discipline | direct PX4 dependency for the first MoSim minimum loop | Implement a PX4-style command/state machine around MWORKS setpoints: 20Hz setpoint/control, stale-command timeout, hover/land fallback, valid odometry requirement. |
| Sunray/YunZong control | adapt | `external_fusion`, `sunray_control_node` semantics, command timeout, geofence, takeoff/hover/land/kill states | ROS1/MAVROS runtime as the first production dependency | Port the semantics into MoSim MWORKS/controller adapter; use Sunray code as behavior reference. |
| Sunray Mid360 Gazebo plugin | adapt strongly | Livox `CustomMsg` schema, `CustomPoint` fields, `mid360-real-centr.csv` scan pattern, 200k points/s timing idea | Gazebo/ROS1 plugin binary as-is | Use this as the UE/ROS2 Mid360 bridge contract: `offset_time`, `x/y/z`, reflectivity/intensity, tag, line, coherent frame id, extrinsics. |
| Sunray EGO planner path | adapt later | 3D local map contract, B-spline trajectory, `PositionCommand` to control command at 20Hz | planner closure before FAST-LIO is valid | After FAST-LIO truth gate passes, map EGO-style output into MWORKS setpoints. |
| RflySim | architecture reference | process split: CopterSim/PX4 motion, Unreal/RflySim3D rendering/perception, ROS/RViz algorithm review | treating packaged RflySim scenes as editable MoSim maps or replacing MWORKS solver | Keep MoSim split: MWORKS=motion/control/truth, UE=sensor/render oracle, ROS2=algorithms/RViz review. |
| AirSim | architecture/API reference | ROS wrapper topics, LiDAR as `PointCloud2`, IMU/odom/tf separation, simulator window separate from RViz | AirSim runtime as core dependency | Reuse topic/window design, not runtime. |
| Gazebo / ros_gz | architecture/API reference | simulator-to-ROS bridge pattern for sensors and separate RViz review | switching main renderer from UE to Gazebo | Reuse bridge discipline and message contracts. |
| local `spark-fast-lio` | patch candidate | ROS2/ament build base and existing FAST-LIO2-family code | claiming Mid360 evidence through its current PointCloud2 path | Keep only if Livox CustomMsg support is patched and runtime output passes truth gates. |
| external `Ericsii/FAST_LIO_ROS2` branch `ros2` | preferred candidate to evaluate | visible ROS2 + `livox_ros_driver2` + Mid360 config/launch shape | claiming before local build/runtime proof | Import into ignored temp workspace, build with ROS2 Humble, run headless with MoSim Mid360 + IMU. |
| ROS1 `FAST_LIO`, `FAST-LIVO2`, `Point-LIO` | reference / fallback | Mid360 params, FAST-LIO topic expectations, registered cloud/odometry/path acceptance | native runtime on Ubuntu 22.04 without container/bridge | Use as semantic reference unless a ROS1 container/bridge is explicitly approved. |
| current keyboard/grid mapping loop | smoke only | RViz2 display plumbing check | controller, localization, mapping, or planning evidence | Do not improve as product route. |

## Required Runtime Contract

The first accepted Factory/Derelict loop must satisfy this data contract before
manual window review:

| Channel | Target | Notes |
|---|---:|---|
| MWORKS truth/state | continuous, at least 20Hz output | dynamics/controller/truth authority |
| Controller/setpoint stream | 20Hz | no pose overwrite; manual command becomes setpoint stream |
| IMU | 200Hz | coherent angular velocity and acceleration, one clock domain |
| Mid360 LiDAR baseline | 10Hz, about 200k points/s | enhanced 20Hz mode only after throughput/localization gates |
| LiDAR point fields | Livox-style per-point timing + line/tag/intensity | display-only `PointCloud2` is not enough for FAST-LIO claims |
| TF/extrinsics | monotonic and explicit | `map/odom/base_link/imu/lidar` relation must be documented |
| FAST-LIO outputs | registered cloud, odometry, path | nonzero topics plus truth-error evaluation |
| Local map | 3D voxel/SDF/point-cloud map | 2D `OccupancyGrid` is auxiliary only |

## Implementation Order

1. Keep UE/RViz GUI closed for this phase.
2. Finish the source audit into executable contracts:
   `FASTLIO_INPUT_CONTRACT`, `REALSTACK_MINILOOP_GATE`, and runtime candidate
   gate.
3. Import/build the preferred ROS2 Mid360 FAST-LIO candidate in
   `Results/tmp/fastlio_ros2_candidates/`.
4. Run a headless Factory proof:
   MWORKS state + 200Hz IMU + 10Hz Livox/Mid360 + TF + FAST-LIO runtime.
5. Evaluate FAST-LIO against MWORKS/UE truth.
6. Add the 3D local-map/planner-state topic.
7. Repeat for Derelict.
8. Only then open UE rendered scene plus separate RViz2 point-cloud and 3D map
   windows for user review.

## References Used

- PX4 Offboard Mode: `https://docs.px4.io/main/en/flight_modes/offboard.html`
- PX4 ROS2 Offboard Example: `References/PX4/docs/en/ros2/offboard_control.md`
- Livox Mid-360 specs/manual: `https://www.livoxtech.com/mobile/mid-360/specs`,
  `https://www.manualslib.com/manual/2952267/Livox-Mid-360.html`
- FAST-LIO Livox timestamp guidance: `https://github.com/hku-mars/FAST_LIO`
- RflySim3D/UE role split: `https://rflysim.com/doc/en/3/RflySim3DUE.html`
- RflySim Vision/RViz route: `https://rflysim.com/doc/en/RflySimAPIs/8.RflySimVision/PPT.pdf`
- AirSim ROS wrapper: `References/AirSim/AirSim/docs/airsim_ros_pkgs.md`
- AirSim LiDAR config: `References/AirSim/AirSim/docs/lidar.md`
- Sunray source: `References/Sunray/scripts_exp/`,
  `References/Sunray/General_Module/`, `References/Sunray/simulation/`
