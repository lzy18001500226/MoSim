# MWORKS UE Scene Truth Collision Status

This status validates MWORKS smoke trajectories against UE scene-truth occupancy after simulation.
The global occupancy truth is a validation oracle only; it is not planner input.

| Scene | Pass | Actual Occupied Samples | Reference Occupied Samples | Min Actual Clearance | Report |
|---|---:|---:|---:|---:|---|
| `factoryenvironmentcollect` | `true` | 0 | 0 | 0.9500 m | `Results/unreal_scene_mapping/factoryenvironmentcollect/mworks_smoke/collision/mworks_scene_truth_collision.json` |
| `derelictcorridormegascans` | `true` | 0 | 0 | 0.7909 m | `Results/unreal_scene_mapping/derelictcorridormegascans/mworks_smoke/collision/mworks_scene_truth_collision.json` |

Pass means the sampled MWORKS smoke trajectory and its reference stayed out of occupied validation cells.
Fail means the controller/planner coupling needs more clearance, slower references, or a safety filter before this can be promoted beyond smoke evidence.
