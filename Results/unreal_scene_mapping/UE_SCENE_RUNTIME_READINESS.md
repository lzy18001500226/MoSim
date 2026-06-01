# UE Scene Runtime Readiness

This is a preflight report, not a new simulation result.
The primary point-cloud/map review route is a native ROS/RViz window, not browser HTML.
UE overlays and native file previews do not replace RViz/RViz2 evidence.
Global scene truth is a validation oracle only and is not a planner input.

- file_loop_ready: `true`
- runtime_ready: `false`
- runtime_blockers: `missing_ros1_rviz_catkin_runtime`, `ros_env:missing_ros1_commands:roscore,roslaunch,rostopic,rosnode,rosparam,rviz`, `ros_env:missing_catkin_build_tool`, `ros_env:ros_environment_not_sourced`, `ros_env:fast_lio_package_not_visible:fast_lio`, `unreal_editor_listener_unavailable`
- mapping_window: `RViz/RViz2 or equivalent native robotics viewer`
- html_active_pointcloud_window: `false`
- global_truth_used_by_planner: `false`

| Scene | File Loop | Path Cells | LiDAR Points | FAST-LIO | Frames | Issues |
|---|---|---:|---:|---|---:|---|
| `factoryenvironmentcollect` | `true` | 34 | 1934 | `blocked_missing_ros1_runtime` | 34 |  |
| `derelictcorridormegascans` | `true` | 45 | 2068 | `blocked_missing_ros1_runtime` | 45 |  |

Runtime commands:
- `roscore`: `None`
- `roslaunch`: `None`
- `rostopic`: `None`
- `rviz`: `None`
- `rviz2`: `None`
- `catkin_make`: `None`
- `colcon`: `None`

Next commands:
- `python3 Scripts/UE5/summarize_scene_closed_loop.py --fail-on-issue`
- `DRY_RUN=1 MAX_FRAMES=2 Scripts/UE5/open_mapping_rviz_ros1.sh factoryenvironmentcollect`
- `DRY_RUN=1 MAX_FRAMES=2 Scripts/UE5/open_mapping_rviz_ros1.sh derelictcorridormegascans`
- `DRY_RUN=1 MAX_FRAMES=2 RVIZ_PROFILE=split Scripts/UE5/open_mapping_rviz_ros1.sh factoryenvironmentcollect`
- `DRY_RUN=1 MAX_FRAMES=2 RVIZ_PROFILE=split Scripts/UE5/open_mapping_rviz_ros1.sh derelictcorridormegascans`
- `DRY_RUN=1 MAX_FRAMES=2 Scripts/UE5/run_fastlio_rviz_replay_ros1.sh factoryenvironmentcollect`
- `DRY_RUN=1 Scripts/UE5/check_fastlio_ros1_topics.sh`
- `DRY_RUN=1 Scripts/UE5/bootstrap_fastlio_ros1_workspace.sh`
- `DRY_RUN=1 Scripts/UE5/open_unreal_editor_mcp_listener.sh`
- `python3 Scripts/UE5/check_ros_mapping_runtime_env.py --write`
- `Scripts/UE5/bootstrap_fastlio_ros1_workspace.sh  # only after ROS1/Catkin is installed and sourced`
- `Scripts/UE5/open_unreal_editor_mcp_listener.sh  # opens UE Editor and waits up to 60s for UnrealMCP listener`
- `RVIZ_PROFILE=split Scripts/UE5/open_mapping_rviz_ros1.sh <scene>  # opens separate planning-grid and point-cloud RViz windows after ROS1/RViz is installed`
- `Scripts/UE5/run_fastlio_rviz_replay_ros1.sh <scene>  # only after ROS1/Catkin/FAST-LIO is installed and sourced`
- `Scripts/UE5/check_fastlio_ros1_topics.sh  # only during a live ROS1/FAST-LIO run`
