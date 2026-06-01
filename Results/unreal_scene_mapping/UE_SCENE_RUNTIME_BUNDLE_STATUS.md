# UE Scene Runtime Bundle Status

| Scene | Status | Frames | LiDAR Points | Runtime Blockers | Runtime Degraded | Mapping Window |
|---|---|---:|---:|---|---|---|
| `factoryenvironmentcollect` | `blocked_runtime_dependencies` | 34 | 1934 | `unreal_editor_listener_unavailable` | `missing_ros1_commands:roscore,roslaunch,rostopic,rosnode,rosparam,rviz`<br>`missing_catkin_build_tool`<br>`fast_lio_ros1_package_not_visible:fast_lio`<br>`missing_ros1_rviz_catkin_runtime`<br>`ros1_fastlio_compat_runtime_unavailable` | `RViz/RViz2 or equivalent native robotics viewer` |
| `derelictcorridormegascans` | `blocked_runtime_dependencies` | 45 | 2068 | `unreal_editor_listener_unavailable` | `missing_ros1_commands:roscore,roslaunch,rostopic,rosnode,rosparam,rviz`<br>`missing_catkin_build_tool`<br>`fast_lio_ros1_package_not_visible:fast_lio`<br>`missing_ros1_rviz_catkin_runtime`<br>`ros1_fastlio_compat_runtime_unavailable` | `RViz/RViz2 or equivalent native robotics viewer` |

This status file is an execution contract summary, not runtime evidence.
Runtime evidence requires native UE/RViz2 windows plus FAST-LIO topic recording/evaluation.
