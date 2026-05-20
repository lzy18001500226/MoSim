# Unreal Scene Profile Implementation Plan

- Source profiles: `unreal/MworksUnrealRenderer/Content/MworksData/unreal_scene_profiles.json`
- RflySim registry: `unreal/MworksUnrealRenderer/Content/MworksData/rflysim_scene_registry.json`
- RflySim direct use supported: `False`
- RflySim direct editor open supported: `False`
- Profile count: `5`
- Next recommended task: Implement gate_ring_indoor first if the goal is attitude-control video; implement maze_building first if the goal is local perception and replanning.

## Runtime Targets

- `state_stream_hz_min`: `20`
- `state_stream_hz_target`: `50`
- `render_fps_target`: `60`
- `sensor_map_hz_min`: `20`
- `planner_hz_range`: `[5, 20]`

## Profiles

| Order | Profile | Priority | Planner visibility | Visual classes | Proxy classes |
| ---: | --- | --- | --- | --- | --- |
| 1 | `dense_forest` | P0 | `local_sensor_only` | `terrain`, `tree_trunks`, `canopy`, `rocks`, `waypoint_markers`, `radar_sector`, `local_plan`, `trajectory_trail` | `tree_trunk_capsule_or_box`, `rock_box`, `terrain_heightfield` |
| 2 | `gate_ring_indoor` | P0 | `known_task_geometry_plus_local_sensor` | `tilted_gate`, `ring`, `indoor_floor`, `axis_marker`, `smooth_reference`, `actual_trail` | `gate_frame_boxes`, `ring_proxy`, `safe_corridor` |
| 3 | `maze_building` | P0 | `raycast_occluded_local_sensor` | `walls`, `doors_or_passages`, `floor`, `occlusion_shading`, `radar_sector`, `local_known_map` | `wall_box`, `passage_box`, `floor_plane` |
| 4 | `old_factory` | P0 | `local_sensor_only` | `buildings`, `pipes`, `columns`, `machines`, `inspection_targets`, `local_plan`, `trail` | `building_box`, `pipe_capsule`, `column_box`, `target_marker` |
| 5 | `open_grass_wind` | P0 | `mostly_open_known_task_area` | `grass_field`, `wind_vector_overlay`, `gust_zone`, `UAV`, `trail`, `metric_overlay` | `terrain_plane`, `optional_boundary` |

## Acceptance Gates

### `dense_forest`

RflySim runtime references:

- `rflysim_neighborhood_park` -> `ModularNeighborhood/Maps/NeighborhoodPark.umap` (direct_use=False, editor_open=False)
- `rflysim_mountain_terrain` -> `MountainTerrain/Maps/MountainTerrain.umap` (direct_use=False, editor_open=False)

Reconstruction units:

| Visual class | Proxy class | Source | Action |
| --- | --- | --- | --- |
| `terrain` | `terrain_heightfield` | `project_owned_geometry` | create visible asset and bind to matching collision/world_geometry proxy |
| `tree_trunks` | `tree_trunk_capsule_or_box` | `project_owned_geometry` | create visible asset and bind to matching collision/world_geometry proxy |
| `canopy` | `` | `project_owned_visual_only` | create visual asset; mark render_only unless later linked to a proxy |
| `rocks` | `rock_box` | `project_owned_geometry` | create visible asset and bind to matching collision/world_geometry proxy |
| `waypoint_markers` | `` | `bridge_runtime_visual` | render from MWORKS UDP/replay packet; not a static scene asset |
| `radar_sector` | `` | `bridge_runtime_visual` | render from MWORKS UDP/replay packet; not a static scene asset |
| `local_plan` | `` | `bridge_runtime_visual` | render from MWORKS UDP/replay packet; not a static scene asset |
| `trajectory_trail` | `` | `bridge_runtime_visual` | render from MWORKS UDP/replay packet; not a static scene asset |

Acceptance:

- visible trunks/rocks have collision_proxy_id equivalents
- radar sector shows only currently sensed region
- local plan is not a fixed straight line through obstacles

### `gate_ring_indoor`

RflySim runtime references:

- `rflysim_vision_ring` -> `Vision/Maps/VisionRing.umap` (direct_use=False, editor_open=False)
- `rflysim_vision_ring_blank` -> `Vision/Maps/VisionRingBlank.umap` (direct_use=False, editor_open=False)

Reconstruction units:

| Visual class | Proxy class | Source | Action |
| --- | --- | --- | --- |
| `tilted_gate` | `gate_frame_boxes` | `project_owned_geometry` | create visible asset and bind to matching collision/world_geometry proxy |
| `ring` | `ring_proxy` | `project_owned_geometry` | create visible asset and bind to matching collision/world_geometry proxy |
| `indoor_floor` | `safe_corridor` | `project_owned_geometry` | create visible asset and bind to matching collision/world_geometry proxy |
| `axis_marker` | `` | `project_owned_visual_only` | create visual asset; mark render_only unless later linked to a proxy |
| `smooth_reference` | `` | `bridge_runtime_visual` | render from MWORKS UDP/replay packet; not a static scene asset |
| `actual_trail` | `` | `bridge_runtime_visual` | render from MWORKS UDP/replay packet; not a static scene asset |

Acceptance:

- reference path passes through gate center with visible attitude change
- actual UAV body does not clip frame proxies
- attitude and position errors are exported from MWORKS evidence

### `maze_building`

RflySim runtime references:

- `rflysim_challenge_map` -> `RobotMissionChallenge/Map/ChallengeMap.umap` (direct_use=False, editor_open=False)
- `rflysim_old_factory` -> `OldFactory/Maps/OldFactory.umap` (direct_use=False, editor_open=False)

Reconstruction units:

| Visual class | Proxy class | Source | Action |
| --- | --- | --- | --- |
| `walls` | `wall_box` | `project_owned_geometry` | create visible asset and bind to matching collision/world_geometry proxy |
| `doors_or_passages` | `passage_box` | `project_owned_geometry` | create visible asset and bind to matching collision/world_geometry proxy |
| `floor` | `floor_plane` | `project_owned_geometry` | create visible asset and bind to matching collision/world_geometry proxy |
| `occlusion_shading` | `` | `project_owned_visual_only` | create visual asset; mark render_only unless later linked to a proxy |
| `radar_sector` | `` | `bridge_runtime_visual` | render from MWORKS UDP/replay packet; not a static scene asset |
| `local_known_map` | `` | `bridge_runtime_visual` | render from MWORKS UDP/replay packet; not a static scene asset |

Acceptance:

- radar does not reveal geometry behind walls
- trajectory keeps minimum obstacle distance
- planner can recover from blocked local plan without yaw spinning

### `old_factory`

RflySim runtime references:

- `rflysim_old_factory` -> `OldFactory/Maps/OldFactory.umap` (direct_use=False, editor_open=False)

Reconstruction units:

| Visual class | Proxy class | Source | Action |
| --- | --- | --- | --- |
| `buildings` | `building_box` | `project_owned_geometry` | create visible asset and bind to matching collision/world_geometry proxy |
| `pipes` | `pipe_capsule` | `project_owned_geometry` | create visible asset and bind to matching collision/world_geometry proxy |
| `columns` | `column_box` | `project_owned_geometry` | create visible asset and bind to matching collision/world_geometry proxy |
| `machines` | `` | `project_owned_visual_only` | create visual asset; mark render_only unless later linked to a proxy |
| `inspection_targets` | `target_marker` | `project_owned_geometry` | create visible asset and bind to matching collision/world_geometry proxy |
| `local_plan` | `` | `bridge_runtime_visual` | render from MWORKS UDP/replay packet; not a static scene asset |
| `trail` | `` | `bridge_runtime_visual` | render from MWORKS UDP/replay packet; not a static scene asset |

Acceptance:

- industrial visual objects are not only decorative when they affect flight
- collision proxies are reviewed before video claim
- MWORKS event_log records replanning or safety-filter interventions

### `open_grass_wind`

RflySim runtime references:

- `rflysim_grasslands_3d_display` -> `Grasslands/Maps/Grasslands/3DDisplay.umap` (direct_use=False, editor_open=False)
- `rflysim_grasslands` -> `Grasslands/Maps/Grasslands/Grasslands.umap` (direct_use=False, editor_open=False)

Reconstruction units:

| Visual class | Proxy class | Source | Action |
| --- | --- | --- | --- |
| `grass_field` | `terrain_plane` | `project_owned_geometry` | create visible asset and bind to matching collision/world_geometry proxy |
| `wind_vector_overlay` | `` | `bridge_runtime_visual` | render from MWORKS UDP/replay packet; not a static scene asset |
| `gust_zone` | `optional_boundary` | `project_owned_geometry` | create visible asset and bind to matching collision/world_geometry proxy |
| `UAV` | `` | `bridge_runtime_visual` | render from MWORKS UDP/replay packet; not a static scene asset |
| `trail` | `` | `bridge_runtime_visual` | render from MWORKS UDP/replay packet; not a static scene asset |
| `metric_overlay` | `` | `bridge_runtime_visual` | render from MWORKS UDP/replay packet; not a static scene asset |

Acceptance:

- wind and motor-efficiency parameters are displayed and logged
- trajectory comparison shows tracking degradation/recovery
- rendered video maps to MWORKS raw/native result timestamps
