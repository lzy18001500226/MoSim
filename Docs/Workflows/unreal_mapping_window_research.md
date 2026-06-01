# UE Mapping Window Research

> Last updated: 2026-06-01. Purpose: prevent the MoSim UE scene loop from
> confusing report previews with runtime mapping evidence.

## Conclusion

MoSim should use a two-window robotics simulation layout:

```text
UE / MoSimSceneLibrary
  -> rendered map, UAV body, camera, trajectory/local debug overlays

ROS RViz / RViz2 or equivalent native robotics viewer
  -> PointCloud2, OccupancyGrid or grid map, TF, odometry, path, FAST-LIO map
```

Browser HTML is not an accepted active point-cloud, occupancy-map, FAST-LIO, or
planner-state review surface. HTML can only be an explicitly requested offline
report preview.

## Why

The common UAV/robotics simulator pattern separates the high-fidelity simulator
window from the robotics-data visualization window:

| System | Observed Pattern | Source |
|---|---|---|
| RflySim | RflySim3D/Unreal provides the scene; LiDAR UDP/ROS workflows use RViz for point-cloud visualization. | `https://rflysim.com/doc/en/RflySimAPIs/8.RflySimVision/PPT.pdf`, `https://rflysim.com/doc/en/RflySimAPIs/8.RflySimVision/Index.pdf` |
| AirSim | AirSim runs separately; ROS wrapper starts `airsim_node.launch` and `rviz.launch`; LiDAR is published as `sensor_msgs::PointCloud2`. | `https://microsoft.github.io/AirSim/airsim_ros_pkgs/`, local `References/AirSim/AirSim/docs/airsim_ros_pkgs.md` |
| AirSim tutorials | Tutorial packages start RViz with TF, depth-derived point cloud, and LiDAR point cloud. | `https://microsoft.github.io/AirSim/airsim_tutorial_pkgs/`, local `References/AirSim/AirSim/docs/airsim_tutorial_pkgs.md` |
| PX4 + Gazebo | PX4 uses Gazebo as the SITL/rendered simulation environment and bridges state/data through ROS 2/uXRCE-DDS; PX4 docs explicitly mention RViz visualizers for vehicle state. | `https://docs.px4.io/main/en/sim_gazebo_gz/`, `https://docs.px4.io/main/en/ros2/user_guide` |
| Gazebo / Gazebo Sim | Gazebo remains the simulation window; ROS integration uses bridge packages, then RViz/RViz2 visualizes robot model, topics, maps, and point clouds. | `https://gazebosim.org/docs/garden/ros2_integration/`, `https://docs.ros.org/en/iron/p/ros_gz_sim_demos/` |
| ROS 2 + Gazebo lidar tutorial | Gazebo launches the simulation world, then ROS 2 configures and visualizes lidar data separately. | `https://docs.ros.org/en/iron/Tutorials/Advanced/Simulators/Gazebo/Gazebo.html` |
| ROS RViz | RViz is the native ROS 3D visualizer and has built-in displays for `Map` / `nav_msgs/msg/OccupancyGrid`, `Point Cloud(2)` / `sensor_msgs/msg/PointCloud2`, TF, odometry, and paths. | `https://docs.ros.org/en/rolling/Tutorials/Intermediate/RViz/RViz-User-Guide/RViz-User-Guide.html` |

Local project references match the same architecture:

| Local Source | Evidence |
|---|---|
| `References/Lab/FAST_LIO/launch/mapping_mid360.launch` and other FAST-LIO launch files | `rviz` is an optional launch arg and starts `rviz -d .../loam_livox.rviz`. |
| `References/Lab/FAST_LIO/rviz_cfg/loam_livox.rviz` | Displays `/cloud_registered`, `/Odometry`, `/path`, and PointCloud2 data. |
| `References/Lab/FAST-LIVO2/rviz_cfg/*.rviz` | Uses RViz configs for LiDAR-inertial-visual odometry review. |
| `References/AirSim/AirSim/ros/src/airsim_ros_pkgs/launch/rviz.launch` | Starts RViz from the AirSim ROS wrapper. |
| `References/AirSim/AirSim/ros/src/airsim_ros_pkgs/src/airsim_ros_wrapper.cpp` | Publishes LiDAR as `sensor_msgs::PointCloud2`. |
| `References/Sunray/.../*.rviz` and `References/Sunray/.../launch/*rviz*` | Planning, point clouds, robot state, trajectories, and maps are reviewed in RViz/RViz2-style windows. |

## MoSim Runtime Contract

Accepted runtime surfaces:

| Surface | Required Role |
|---|---|
| UE standalone/editor window | Visual map acceptance, UAV body/camera, wall/collision review, trajectory video, optional local debug overlays. |
| RViz/RViz2/native robotics viewer | Active point cloud, local occupancy/grid map, TF, odometry, FAST-LIO registered cloud, planner path. |
| QGroundControl or control UI, when used | Flight mode, mission command, arming and telemetry supervision. |

The default operator-facing route should be split when screen space allows:

```text
RViz planning/grid window
  -> /mosim/local_occupancy_grid, /mosim/local_known_map_cloud,
     /mosim/local_plan, /mosim/uav_path, TF

RViz point-cloud/FAST-LIO window
  -> /velodyne_points, /cloud_registered, /Odometry, /path, TF
```

A single overview RViz window with all displays is acceptable for smoke tests
or constrained displays. Browser HTML is never an active runtime map window.

Accepted ROS topic contract for the current Ubuntu 22.04 ROS2/RViz2 path:

```text
/velodyne_points             # simulated LiDAR input, sensor_msgs/PointCloud2
/imu/data                    # IMU input
/mosim/local_occupancy_grid  # planner-known local map, nav_msgs/OccupancyGrid
/mosim/local_plan            # local planner path
/mosim/replay_odometry       # replay reference pose, nav_msgs/Odometry
/mosim/uav_path              # replay/path visualization
/cloud_registered            # FAST-LIO registered cloud output
/Odometry                    # FAST-LIO odometry output
/path                        # FAST-LIO or planner path output, when available
TF: ue_world/map -> base_link -> lidar
```

## Evidence Boundary

Do not claim runtime mapping, localization, or planning completion from:

- HTML files;
- static `.ply`, `.pcd`, CSV, or JSONL files;
- UE debug meshes or overlays;
- WPF/native file-preview helpers;
- offline scene-truth simulation outputs alone.

Those artifacts are useful handoff or report assets. They become runtime
evidence only after a native robotics viewer consumes live/replayed ROS topics
and FAST-LIO/planner outputs are recorded and evaluated.

FAST-LIO acceptance requires all of the following:

```text
ROS runtime publishes /velodyne_points and /imu/data
FAST-LIO publishes /cloud_registered and /Odometry
RViz/RViz2 shows the input and output topics in a native window
record/evaluate tooling records the runtime output
evaluate_fastlio_runtime.py compares output against replay truth
```

`/mosim/replay_odometry` is allowed in mapping/planning RViz2 windows as a
reference trajectory marker. It does not satisfy the FAST-LIO `/Odometry`
requirement.

## Current MoSim Assets

Current project implementation should continue from these native-window assets:

```text
Config/rviz2/mosim_uav_mapping.rviz
Config/rviz2/mosim_uav_planning_grid.rviz
Config/rviz2/mosim_uav_fastlio_pointcloud.rviz
Scripts/ros/publish_mosim_mapping_replay_ros2.py
Scripts/UE5/check_ros_mapping_runtime_env.py
Scripts/UE5/open_mapping_rviz_ros2.sh
Scripts/UE5/run_fastlio_rviz_replay_ros2.sh
Scripts/UE5/check_fastlio_ros2_topics.sh
Scripts/UE5/record_fastlio_ros1_runtime.py
Scripts/UE5/evaluate_fastlio_runtime.py
```

Dry-run contracts, valid even without ROS installed:

```bash
DRY_RUN=1 MAX_FRAMES=2 Scripts/UE5/open_mapping_rviz_ros2.sh factoryenvironmentcollect
DRY_RUN=1 MAX_FRAMES=2 Scripts/UE5/open_mapping_rviz_ros2.sh derelictcorridormegascans
DRY_RUN=1 MAX_FRAMES=2 RVIZ_PROFILE=split Scripts/UE5/open_mapping_rviz_ros2.sh factoryenvironmentcollect
DRY_RUN=1 MAX_FRAMES=2 Scripts/UE5/run_fastlio_rviz_replay_ros2.sh factoryenvironmentcollect
DRY_RUN=1 Scripts/UE5/check_fastlio_ros2_topics.sh
```

Real runtime commands after ROS2 Humble is installed and sourced:

```bash
RVIZ_PROFILE=split Scripts/UE5/open_mapping_rviz_ros2.sh factoryenvironmentcollect
Scripts/UE5/run_fastlio_rviz_replay_ros2.sh factoryenvironmentcollect
REQUIRE_FASTLIO_OUTPUTS=0 Scripts/UE5/check_fastlio_ros2_topics.sh
```

`RVIZ_PROFILE=overview` opens the combined smoke-test view,
`RVIZ_PROFILE=planning_grid` opens only the 2D grid/local-plan view,
`RVIZ_PROFILE=fastlio_pointcloud` opens only the 3D point-cloud/FAST-LIO view,
and `RVIZ_PROFILE=split` opens the two specialized RViz windows together.

The current WSL session has ROS2/RViz2 replay readiness. The local
`References/Lab/FAST_LIO` package is still ROS1/Catkin-oriented, so completed
FAST-LIO localization remains unclaimed until a ROS2 FAST-LIO-family package or
approved ROS1 bridge publishes output topics.
