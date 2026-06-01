# UE Scene Closed Loop Status

This aggregates the accepted scene truth, mapping, FAST-LIO handoff, MWORKS smoke, and UE-truth collision gates.
FAST-LIO replay handoff files are not localization results until a real FAST-LIO-family runtime produces output topics.

| Scene | Status | Path Cells | LiDAR Points | MWORKS Quality | Collision | FAST-LIO | Blockers |
|---|---|---:|---:|---|---|---|---|
| `factoryenvironmentcollect` | `ready_smoke_validated` | 34 | 1934 | `smoke_only` | `true` | `ready_for_ros2_replay` | `fastlio_ros1_compat_unavailable` |
| `derelictcorridormegascans` | `ready_smoke_validated` | 45 | 2068 | `smoke_only` | `true` | `ready_for_ros2_replay` | `fastlio_ros1_compat_unavailable` |

Acceptance boundary:
- `ready_smoke_validated` means the scene has file-level truth/mapping artifacts, controller-interface MWORKS smoke evidence, and post-simulation UE-truth collision validation.
- `smoke_only` is not a final controller-performance claim.
- `blocked_missing_ros2_runtime` means ROS2/RViz2 replay runtime must be installed or sourced before native map review can run.
- `fastlio_ros1_compat_unavailable` means the local ROS1/Catkin FAST_LIO package is not usable in this Ubuntu 22.04 session; it is a compatibility warning, not a blocker for ROS2 replay input review.
- FAST-LIO localization still requires a real ROS2 FAST-LIO-family package or approved ROS1 bridge publishing `/cloud_registered` and `/Odometry`.
- Global UE occupancy truth is used as a validation oracle only, not as planner input.
