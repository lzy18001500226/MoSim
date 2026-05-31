# FAST-LIO Replay Adapter Status

This file records the current bridge between UE scene-truth mapping outputs and FAST-LIO.
It is not a FAST-LIO localization result.

| Scene | Status | Dataset | ROS1 Ready |
|---|---|---|---:|
| `factoryenvironmentcollect` | `blocked_missing_ros1_runtime` | `Results/unreal_scene_mapping/factoryenvironmentcollect/fastlio_replay_dataset.jsonl` | False |
| `derelictcorridormegascans` | `blocked_missing_ros1_runtime` | `Results/unreal_scene_mapping/derelictcorridormegascans/fastlio_replay_dataset.jsonl` | False |

Current blocker if status is `blocked_missing_ros1_runtime`: install/source a ROS1 Catkin environment with FAST-LIO dependencies before running the publisher.
Do not feed the planner global occupancy truth; FAST-LIO replay inputs come from per-frame LiDAR observations and synthetic IMU derived from the replay trajectory.
