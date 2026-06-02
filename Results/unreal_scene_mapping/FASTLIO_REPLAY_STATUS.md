# FAST-LIO Replay Adapter Status

This file records the current bridge between UE scene-truth mapping outputs and FAST-LIO.
It is not by itself a FAST-LIO localization result.

| Scene | Status | Dataset | ROS2 Replay Ready | ROS1 Compat Ready |
|---|---|---|---:|
| `factoryenvironmentcollect` | `ready_for_ros2_replay` | `Results/unreal_scene_mapping/factoryenvironmentcollect/fastlio_replay_dataset.jsonl` | True | False |
| `derelictcorridormegascans` | `ready_for_ros2_replay` | `Results/unreal_scene_mapping/derelictcorridormegascans/fastlio_replay_dataset.jsonl` | True | False |

Current primary runtime blocker if status is `blocked_missing_ros2_runtime`: source/install ROS2 Humble with RViz2 and colcon before running the publisher.
Current host status: native ROS2 Humble/RViz2/colcon works, the ROS apt key/source issue is resolved, and the `spark-fast-lio` ROS2 candidate has produced real `/cloud_registered`, `/odometry`, and `/path` runtime outputs.
The local `References/Lab/FAST_LIO` package is ROS1/Catkin-oriented. Treat ROS1 blockers as compatibility blockers unless an approved ROS1 bridge route is being used.
Current localization status is still failed/degraded, not accepted: Factory RMSE is about 10.203 m with max error 17.709 m; Derelict RMSE is about 0.761 m with max error 3.945 m against the current 3.0 m max-error threshold.
Do not feed the planner global occupancy truth; FAST-LIO replay inputs come from per-frame LiDAR observations and synthetic IMU derived from the replay trajectory.
Do not use browser HTML as the active point-cloud/map window; use RViz/RViz2 or an equivalent native robotics viewer.
