# UE Scene Mapping Pipeline Run

This run consumes exported Unreal collision truth and produces file-level mapping/planning artifacts.

| Scene | Grid | Path Cells | Replans | Known Occupied / Truth | Lidar Points | Viewer |
|---|---:|---:|---:|---:|---:|---|
| `factoryenvironmentcollect` | 188x188 | 34 | 11 | 1452/16968 | 1934 | `Results/unreal_scene_mapping/factoryenvironmentcollect/pointcloud_viewer.html` |
| `derelictcorridormegascans` | 182x104 | 45 | 11 | 1673/8206 | 2068 | `Results/unreal_scene_mapping/derelictcorridormegascans/pointcloud_viewer.html` |

Policy:
- Planner uses a local discovered map and does not receive the full global occupancy grid.
- Collision validation is still checked against exported UE truth.
- FAST-LIO artifacts are input handoff files, not a completed FAST-LIO localization result.
