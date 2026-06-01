# UE Scene Runtime Bundle Status

| Scene | Status | Frames | LiDAR Points | Runtime Blockers | Mapping Window |
|---|---|---:|---:|---|---|
| `factoryenvironmentcollect` | `blocked_runtime_dependencies` | 34 | 1934 | `missing_ros1_rviz_catkin_runtime`<br>`ros_env:missing_ros1_commands:roscore,roslaunch,rostopic,rosnode,rosparam,rviz`<br>`ros_env:missing_catkin_build_tool`<br>`ros_env:ros_environment_not_sourced`<br>`ros_env:fast_lio_package_not_visible:fast_lio`<br>`unreal_editor_listener_unavailable`<br>`blocked_missing_ros1_runtime` | `RViz/RViz2 or equivalent native robotics viewer` |
| `derelictcorridormegascans` | `blocked_runtime_dependencies` | 45 | 2068 | `missing_ros1_rviz_catkin_runtime`<br>`ros_env:missing_ros1_commands:roscore,roslaunch,rostopic,rosnode,rosparam,rviz`<br>`ros_env:missing_catkin_build_tool`<br>`ros_env:ros_environment_not_sourced`<br>`ros_env:fast_lio_package_not_visible:fast_lio`<br>`unreal_editor_listener_unavailable`<br>`blocked_missing_ros1_runtime` | `RViz/RViz2 or equivalent native robotics viewer` |

This status file is an execution contract summary, not runtime evidence.
Runtime evidence requires native UE/RViz windows plus FAST-LIO topic recording/evaluation.
