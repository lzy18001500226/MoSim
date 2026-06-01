# UE Scene Runtime Readiness

This is a preflight report, not a new simulation result.
The primary point-cloud/map review route is a native ROS/RViz window, not browser HTML.
UE overlays and native file previews do not replace RViz/RViz2 evidence.
Global scene truth is a validation oracle only and is not a planner input.

- file_loop_ready: `true`
- runtime_ready: `false`
- runtime_blockers: `unreal_editor_listener_unavailable`
- runtime_degraded: `missing_ros1_commands:roscore,roslaunch,rostopic,rosnode,rosparam,rviz`, `missing_catkin_build_tool`, `fast_lio_ros1_package_not_visible:fast_lio`, `missing_ros1_rviz_catkin_runtime`
- mapping_window: `RViz/RViz2 or equivalent native robotics viewer`
- html_active_pointcloud_window: `false`
- global_truth_used_by_planner: `false`

| Scene | File Loop | Path Cells | LiDAR Points | FAST-LIO | Frames | Issues |
|---|---|---:|---:|---|---:|---|
| `factoryenvironmentcollect` | `true` | 34 | 1934 | `ready_for_ros2_replay` | 34 |  |
| `derelictcorridormegascans` | `true` | 45 | 2068 | `ready_for_ros2_replay` | 45 |  |

Runtime commands:
- `ros2`: `/opt/ros/humble/bin/ros2`
- `roscore`: `None`
- `roslaunch`: `None`
- `rostopic`: `None`
- `rviz`: `None`
- `rviz2`: `/opt/ros/humble/bin/rviz2`
- `catkin_make`: `None`
- `colcon`: `/usr/bin/colcon`

Next commands:
- `python3 Scripts/UE5/summarize_scene_closed_loop.py --fail-on-issue`
- `DRY_RUN=1 MAX_FRAMES=2 Scripts/UE5/open_mapping_rviz_ros2.sh factoryenvironmentcollect`
- `DRY_RUN=1 MAX_FRAMES=2 Scripts/UE5/open_mapping_rviz_ros2.sh derelictcorridormegascans`
- `DRY_RUN=1 MAX_FRAMES=2 RVIZ_PROFILE=split Scripts/UE5/open_mapping_rviz_ros2.sh factoryenvironmentcollect`
- `DRY_RUN=1 MAX_FRAMES=2 RVIZ_PROFILE=split Scripts/UE5/open_mapping_rviz_ros2.sh derelictcorridormegascans`
- `DRY_RUN=1 MAX_FRAMES=2 Scripts/UE5/run_fastlio_rviz_replay_ros2.sh factoryenvironmentcollect`
- `DRY_RUN=1 Scripts/UE5/check_fastlio_ros2_topics.sh`
- `DRY_RUN=1 Scripts/UE5/bootstrap_fastlio_ros1_workspace.sh`
- `DRY_RUN=1 Scripts/UE5/open_unreal_editor_mcp_listener.sh`
- `python3 Scripts/UE5/check_ros_mapping_runtime_env.py --write`
- `source /opt/ros/humble/setup.bash`
- `Scripts/UE5/open_unreal_editor_mcp_listener.sh  # opens UE Editor and waits up to 60s for UnrealMCP listener`
- `RVIZ_PROFILE=split Scripts/UE5/open_mapping_rviz_ros2.sh <scene>  # opens separate planning-grid and point-cloud RViz2 windows`
- `Scripts/UE5/run_fastlio_rviz_replay_ros2.sh <scene>  # publishes ROS2 replay inputs; START_FASTLIO=0 until a ROS2 FAST-LIO launch is configured`
- `Scripts/UE5/check_fastlio_ros2_topics.sh  # during a live ROS2 replay; REQUIRE_FASTLIO_OUTPUTS=0 checks replay inputs only`
