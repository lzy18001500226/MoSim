# FAST-LIO Runtime Candidate Decision

- decision: `evaluate_external_ros2_mid360_fastlio_candidate_first`
- next_action: import the best external ROS2 Mid360 FAST-LIO candidate into ignored temp workspace, build it with ROS2 Humble and local livox_ros_driver2, then run headless truth evaluation
- candidate_count: `7`
- preferred_ros2_mid360_count: `0`
- patchable_ros2_livox_count: `1`
- strong_ros1_mid360_reference_count: `1`
- external_candidate_count: `1`

## Ranked Candidates

| Score | Path | Generation | Role | Blockers | Recommendation |
|---:|---|---|---|---|---|
| 75 | `Results/tmp/fastlio_ros2_candidates/spark-fast-lio/spark_fast_lio` | `ros2_ament` | `ros2_candidate_needs_patch` | `pointcloud2_path_rejects_livox_lidar_type` | patch Livox CustomMsg build/subscriber path before any Mid360 runtime claim |
| 70 | `References/Lab/FAST_LIO` | `ros1_catkin` | `strong_ros1_mid360_reference` | `requires_ros1_or_bridge_on_ubuntu_22_04`, `pointcloud2_path_rejects_livox_lidar_type` | reuse config/message semantics; runtime requires ROS1 container/bridge or ROS2 port |
| 65 | `References/Sunray/simulation/gazebo_plugin/livox_laser_simulation` | `ros1_catkin` | `sensor_semantics_reference` | `requires_ros1_or_bridge_on_ubuntu_22_04` | reuse scan pattern and CustomMsg schema when implementing MoSim UE/ROS2 sensor bridge |
| 60 | `References/Lab/FAST-LIVO2` | `ros1_catkin` | `pointcloud2_conversion_reference` | `requires_ros1_or_bridge_on_ubuntu_22_04`, `pointcloud2_path_rejects_livox_lidar_type` | reuse conversion fields for planner/RViz path; verify target FAST-LIO accepts this PointCloud2 layout |
| 60 | `References/Lab/Point-LIO-point-lio-with-grid-map` | `ros1_catkin` | `pointcloud2_conversion_reference` | `requires_ros1_or_bridge_on_ubuntu_22_04`, `pointcloud2_path_rejects_livox_lidar_type` | reuse conversion fields for planner/RViz path; verify target FAST-LIO accepts this PointCloud2 layout |
| 60 | `References/Sunray/General_Module/sunray_planner_utils` | `ros1_catkin` | `pointcloud2_conversion_reference` | `requires_ros1_or_bridge_on_ubuntu_22_04` | reuse conversion fields for planner/RViz path; verify target FAST-LIO accepts this PointCloud2 layout |
| 55 | `Scripts/ros/mosim_dense_lidar_cpp` | `ros2_ament` | `mosim_transport_probe` | none | keep as ROS2 PointCloud2 transport/performance probe; not FAST-LIO evidence by itself |

## External Candidates To Import First

| Score | Candidate | Branch | Status | Blockers | Recommendation |
|---:|---|---|---|---|---|
| 90 | `Ericsii/FAST_LIO_ROS2` | `ros2` | `not_imported_or_built_locally` | `network_import_timeout_in_current_probe`, `not_yet_built_in_mosim_workspace`, `not_yet_runtime_verified_with_mosim_livox_custommsg` | import into ignored temp workspace first, build on ROS2 Humble with local livox_ros_driver2, then run headless Mid360 truth evaluation |

## Claim Boundary

- A candidate is not localization evidence until it publishes FAST-LIO odometry/path/registered cloud at runtime.
- Velodyne/Ouster PointCloud2 smoke does not satisfy the MoSim Mid360/Livox evidence contract.
- MoSim Mid360 evidence requires coherent LiDAR, IMU, TF timestamps, per-point timing, and truth-error evaluation.

## Critical Finding

The current `spark-fast-lio` source is a useful ROS2 FAST-LIO2-family base,
but it is not ready for Mid360 evidence. Its standard `PointCloud2` path
handles Ouster/Kimera/Velodyne-style cases, while the Livox path is guarded
behind CustomMsg support and currently shows driver-name and macro-name
mismatches that must be patched before a Mid360 run can be claimed.

The next attempt should evaluate the external `Ericsii/FAST_LIO_ROS2`
`ros2` branch before spending more engineering time patching `spark-fast-lio`,
because its visible ROS2 branch already declares `ament_cmake`,
`livox_ros_driver2`, and a Mid360 launch/config path. It is still not
local evidence until it builds and publishes runtime FAST-LIO outputs.
