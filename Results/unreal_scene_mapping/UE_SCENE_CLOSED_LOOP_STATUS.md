# UE Scene Closed Loop Status

This aggregates the accepted scene truth, mapping, FAST-LIO handoff, MWORKS smoke, and UE-truth collision gates.
FAST-LIO replay handoff files are not localization results until ROS1/FAST-LIO produces runtime output.

| Scene | Status | Path Cells | LiDAR Points | MWORKS Quality | Collision | FAST-LIO | Blockers |
|---|---|---:|---:|---|---|---|---|
| `factoryenvironmentcollect` | `ready_smoke_validated` | 34 | 1934 | `smoke_only` | `true` | `blocked_missing_ros1_runtime` | `fastlio_blocked_missing_ros1_runtime` |
| `derelictcorridormegascans` | `ready_smoke_validated` | 45 | 2068 | `smoke_only` | `true` | `blocked_missing_ros1_runtime` | `fastlio_blocked_missing_ros1_runtime` |

Acceptance boundary:
- `ready_smoke_validated` means the scene has file-level truth/mapping artifacts, controller-interface MWORKS smoke evidence, and post-simulation UE-truth collision validation.
- `smoke_only` is not a final controller-performance claim.
- `blocked_missing_ros1_runtime` means ROS1/Catkin/FAST-LIO runtime must be installed or sourced before localization can be claimed.
- Global UE occupancy truth is used as a validation oracle only, not as planner input.
