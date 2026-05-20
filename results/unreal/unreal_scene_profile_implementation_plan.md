# Unreal Scene Profile Implementation Plan

- Source profiles: `unreal/MworksUnrealRenderer/Content/MworksData/unreal_scene_profiles.json`
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

- visible trunks/rocks have collision_proxy_id equivalents
- radar sector shows only currently sensed region
- local plan is not a fixed straight line through obstacles

### `gate_ring_indoor`

- reference path passes through gate center with visible attitude change
- actual UAV body does not clip frame proxies
- attitude and position errors are exported from MWORKS evidence

### `maze_building`

- radar does not reveal geometry behind walls
- trajectory keeps minimum obstacle distance
- planner can recover from blocked local plan without yaw spinning

### `old_factory`

- industrial visual objects are not only decorative when they affect flight
- collision proxies are reviewed before video claim
- MWORKS event_log records replanning or safety-filter interventions

### `open_grass_wind`

- wind and motor-efficiency parameters are displayed and logged
- trajectory comparison shows tracking degradation/recovery
- rendered video maps to MWORKS raw/native result timestamps
