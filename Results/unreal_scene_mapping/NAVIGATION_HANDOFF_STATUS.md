# Navigation Control Handoff Status

| Scene | Status | Waypoints | Planner Truth | Control Buffer | FAST-LIO Adapter |
|---|---|---:|---|---:|---|
| `factoryenvironmentcollect` | `ready_for_mworks_controller_interface_smoke` | 34 | `global_truth_available_to_planner=false`, `collision_free_against_truth=true`, `buffered_collision_free_against_truth=true` | 1 | `blocked_missing_ros1_runtime` |
| `derelictcorridormegascans` | `ready_for_mworks_controller_interface_smoke` | 45 | `global_truth_available_to_planner=false`, `collision_free_against_truth=true`, `buffered_collision_free_against_truth=true` | 2 | `blocked_missing_ros1_runtime` |

These files prepare controller-interface smoke work only. They are not MWORKS dynamics simulation evidence.
Each scene directory also contains an inactive scenario draft plus PlannedQuinticReference parameters for later Sysplorer model integration.
