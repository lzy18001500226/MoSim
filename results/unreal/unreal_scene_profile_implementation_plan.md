# Unreal Scene Profile Implementation Plan

- Source profiles: `unreal/MworksUnrealRenderer/Content/MworksData/unreal_scene_profiles.json`
- RflySim registry: `unreal/MworksUnrealRenderer/Content/MworksData/rflysim_scene_registry.json`
- RflySim direct use supported: `False`
- RflySim direct editor open supported: `False`
- Profile count: `8`
- Next recommended task: Implement renderer_framework (S0) first, then competition_industrial_hybrid (S1). Later stages are planning contracts only until user review unlocks them.

## Active Execution Scope

- Allowed to implement now: `S0`, `S1`
- Requires review before implementation: `S2`, `S3`, `S4`, `S5`, `S6`, `S7`
- Rule: Define every stage now, but only implement S0/S1 until the first scene profile, blockout, and playback gates pass.

## Stage Roadmap

| Stage | Profile | Status | Objective | Manual Gate |
| --- | --- | --- | --- | --- |
| `S0` | `renderer_framework` | `active` | scene profile schema, object registry, collision proxy binding, MWORKS UDP/replay, UAV actor, camera, trail, radar/local-map display | profile and blockout review |
| `S1` | `competition_industrial_hybrid` | `active_after_S0_profile` | single-UAV local perception, unknown-map replanning, obstacle avoidance, trajectory tracking, and video-ready industrial visual context | blockout, perception overlay, and playback review |
| `S2` | `gate_ring_attitude` | `planned_only` | large-attitude tracking, smooth trajectory generation, controller performance display, gate/ring traversal | trajectory/control requirement review before implementation |
| `S3` | `park_city_patrol` | `planned_only` | patrol/logistics style mission, path planning, local avoidance, visual demonstration in a readable outdoor environment | asset/license/source review before implementation |
| `S4` | `open_grass_robustness` | `planned_only` | wind disturbance, mass/inertia perturbation, motor-efficiency degradation, sensor-noise and pulse-disturbance display | robustness scenario matrix review before implementation |
| `S5` | `maze_indoor_occlusion` | `planned_only` | wall occlusion, unknown-map memory, no-through-wall radar behavior, local replanning stress test | occlusion model and collision-proxy review before implementation |
| `S6` | `dense_forest_high_obstacle` | `planned_only` | dense local obstacle avoidance, local map stability, performance under many repeated obstacles | asset/performance strategy review before implementation |
| `S7` | `multi_uav_formation` | `planned_only` | leader-follower, line/triangle/diamond formation, inter-UAV distance constraints, formation obstacle avoidance | single-UAV scene and controller evidence must be stable first |

## Runtime Targets

- `state_stream_hz_min`: `20`
- `state_stream_hz_target`: `50`
- `render_fps_target`: `60`
- `sensor_map_hz_min`: `20`
- `planner_hz_range`: `[5, 20]`

## Profiles

| Order | Profile | Priority | Planner visibility | Visual classes | Proxy classes |
| ---: | --- | --- | --- | --- | --- |
| 1 | `renderer_framework` | P0 | `framework_only_no_planner_truth_leakage` | `UAV`, `propellers`, `body_axes`, `overview_camera`, `follow_camera`, `radar_sector`, `local_plan`, `trajectory_trail`, `metric_overlay`, `scene_status_overlay`, `scene_bounds_box`, `optional_ground_plane`, `debug_collision_proxy` | `scene_bounds_box`, `optional_ground_plane`, `debug_collision_proxy` |
| 2 | `competition_industrial_hybrid` | P0 | `raycast_occluded_local_sensor_with_map_memory` | `terrain_or_floor`, `takeoff_pad`, `landing_pad`, `pillars`, `boxes`, `short_walls`, `gate_or_frame`, `industrial_props`, `inspection_targets`, `radar_sector`, `local_known_map`, `local_plan`, `trajectory_trail` | `terrain_heightfield_or_plane`, `takeoff_pad_box`, `landing_pad_box`, `pillar_box_or_cylinder`, `box_obstacle`, `wall_box`, `gate_frame_boxes`, `inspection_target_box` |
| 3 | `gate_ring_attitude` | P1 | `known_task_geometry_plus_local_sensor` | `tilted_gate`, `ring`, `indoor_floor`, `axis_marker`, `smooth_reference`, `actual_trail` | `gate_frame_boxes`, `ring_proxy`, `safe_corridor` |
| 4 | `park_city_patrol` | P1 | `local_sensor_only_with_mission_waypoints` | `terrain`, `roads`, `buildings`, `trees`, `park_props`, `inspection_waypoints`, `radar_sector`, `local_plan`, `trajectory_trail` | `building_box`, `tree_trunk_capsule_or_box`, `road_plane`, `waypoint_marker_box` |
| 5 | `open_grass_robustness` | P1 | `mostly_open_known_task_area` | `grass_field`, `wind_vector_overlay`, `gust_zone`, `UAV`, `trail`, `metric_overlay`, `fault_efficiency_overlay` | `terrain_plane`, `optional_boundary`, `gust_zone_box` |
| 6 | `maze_indoor_occlusion` | P2 | `raycast_occluded_local_sensor` | `walls`, `doors_or_passages`, `floor`, `occlusion_shading`, `radar_sector`, `local_known_map` | `wall_box`, `passage_box`, `floor_plane` |
| 7 | `dense_forest_high_obstacle` | P2 | `local_sensor_only` | `terrain`, `tree_trunks`, `canopy`, `rocks`, `waypoint_markers`, `radar_sector`, `local_plan`, `trajectory_trail` | `tree_trunk_capsule_or_box`, `rock_box`, `terrain_heightfield` |
| 8 | `multi_uav_formation` | P3 | `per_vehicle_local_sensor_plus_shared_formation_state` | `multiple_UAVs`, `formation_links`, `role_labels`, `inter_uav_distance_overlay`, `shared_obstacles`, `leader_trail`, `follower_trails` | `formation_safety_radius`, `shared_obstacle_proxy`, `mission_bounds_box` |

## Acceptance Gates

### `renderer_framework`

- Map IDs: `renderer_framework`, `ue5_framework_smoke`

Reconstruction units:

| Visual class | Proxy class | Source | Action |
| --- | --- | --- | --- |
| `UAV` | `` | `bridge_runtime_visual` | render from MWORKS UDP/replay packet; not a static scene asset |
| `propellers` | `` | `bridge_runtime_visual` | render from MWORKS UDP/replay packet; not a static scene asset |
| `body_axes` | `` | `bridge_runtime_visual` | render from MWORKS UDP/replay packet; not a static scene asset |
| `overview_camera` | `` | `bridge_runtime_visual` | render from MWORKS UDP/replay packet; not a static scene asset |
| `follow_camera` | `` | `bridge_runtime_visual` | render from MWORKS UDP/replay packet; not a static scene asset |
| `radar_sector` | `` | `bridge_runtime_visual` | render from MWORKS UDP/replay packet; not a static scene asset |
| `local_plan` | `` | `bridge_runtime_visual` | render from MWORKS UDP/replay packet; not a static scene asset |
| `trajectory_trail` | `` | `bridge_runtime_visual` | render from MWORKS UDP/replay packet; not a static scene asset |
| `metric_overlay` | `` | `bridge_runtime_visual` | render from MWORKS UDP/replay packet; not a static scene asset |
| `scene_status_overlay` | `` | `bridge_runtime_visual` | render from MWORKS UDP/replay packet; not a static scene asset |
| `scene_bounds_box` | `scene_bounds_box` | `project_owned_geometry` | create visible asset and bind to matching collision/world_geometry proxy |
| `optional_ground_plane` | `optional_ground_plane` | `project_owned_geometry` | create visible asset and bind to matching collision/world_geometry proxy |
| `debug_collision_proxy` | `debug_collision_proxy` | `project_owned_geometry` | create visible asset and bind to matching collision/world_geometry proxy |

Acceptance:

- UAV pose, attitude and propeller visuals are driven by MWORKS/replay state
- scene profile and object registry can be loaded without hard-coded map assumptions
- camera presets, radar sector, local plan and trajectory trail are visible and reviewable

### `competition_industrial_hybrid`

- Map IDs: `competition_industrial_hybrid`, `match_industrial_challenge`

RflySim runtime references:

- `rflysim_old_factory` -> `OldFactory/Maps/OldFactory.umap` (direct_use=False, editor_open=False)
- `rflysim_challenge_map` -> `RobotMissionChallenge/Map/ChallengeMap.umap` (direct_use=False, editor_open=False)

Reconstruction units:

| Visual class | Proxy class | Source | Action |
| --- | --- | --- | --- |
| `terrain_or_floor` | `terrain_heightfield_or_plane` | `project_owned_geometry` | create visible asset and bind to matching collision/world_geometry proxy |
| `takeoff_pad` | `takeoff_pad_box` | `project_owned_geometry` | create visible asset and bind to matching collision/world_geometry proxy |
| `landing_pad` | `landing_pad_box` | `project_owned_geometry` | create visible asset and bind to matching collision/world_geometry proxy |
| `pillars` | `pillar_box_or_cylinder` | `project_owned_geometry` | create visible asset and bind to matching collision/world_geometry proxy |
| `boxes` | `box_obstacle` | `project_owned_geometry` | create visible asset and bind to matching collision/world_geometry proxy |
| `short_walls` | `wall_box` | `project_owned_geometry` | create visible asset and bind to matching collision/world_geometry proxy |
| `gate_or_frame` | `gate_frame_boxes` | `project_owned_geometry` | create visible asset and bind to matching collision/world_geometry proxy |
| `industrial_props` | `` | `project_owned_visual_only` | create visual asset; mark render_only unless later linked to a proxy |
| `inspection_targets` | `inspection_target_box` | `project_owned_geometry` | create visible asset and bind to matching collision/world_geometry proxy |
| `radar_sector` | `` | `bridge_runtime_visual` | render from MWORKS UDP/replay packet; not a static scene asset |
| `local_known_map` | `` | `bridge_runtime_visual` | render from MWORKS UDP/replay packet; not a static scene asset |
| `local_plan` | `` | `bridge_runtime_visual` | render from MWORKS UDP/replay packet; not a static scene asset |
| `trajectory_trail` | `` | `bridge_runtime_visual` | render from MWORKS UDP/replay packet; not a static scene asset |

Acceptance:

- start and goal are explicit and coordinate-frame reviewed
- every planning-relevant visible object has a collision_proxy_id equivalent
- radar/local map does not reveal occluded or unknown global geometry
- local plan begins at the UAV center and avoids proxies rather than drawing a fixed straight line
- MWORKS playback shows actual trail, reference/local plan, UAV attitude, and scene overlays

### `gate_ring_attitude`

- Map IDs: `map_corridor_gate`, `gate_ring_indoor`, `gate_ring_attitude`
- Render map JSON: `MworksData/map_corridor_gate_render_map.json`

RflySim runtime references:

- `rflysim_vision_ring` -> `Vision/Maps/VisionRing.umap` (direct_use=False, editor_open=False)
- `rflysim_vision_ring_blank` -> `Vision/Maps/VisionRingBlank.umap` (direct_use=False, editor_open=False)

Reconstruction units:

| Visual class | Proxy class | Source | Action |
| --- | --- | --- | --- |
| `tilted_gate` | `gate_frame_boxes` | `project_owned_geometry` | create visible asset and bind to matching collision/world_geometry proxy |
| `ring` | `ring_proxy` | `project_owned_geometry` | create visible asset and bind to matching collision/world_geometry proxy |
| `indoor_floor` | `safe_corridor` | `project_owned_geometry` | create visible asset and bind to matching collision/world_geometry proxy |
| `axis_marker` | `` | `bridge_runtime_visual` | render from MWORKS UDP/replay packet; not a static scene asset |
| `smooth_reference` | `` | `bridge_runtime_visual` | render from MWORKS UDP/replay packet; not a static scene asset |
| `actual_trail` | `` | `bridge_runtime_visual` | render from MWORKS UDP/replay packet; not a static scene asset |

Acceptance:

- reference path passes through gate center with visible attitude change
- actual UAV body does not clip frame proxies
- attitude and position errors are exported from MWORKS evidence

### `park_city_patrol`

- Map IDs: `park_city_patrol`, `neighborhood_park`, `modern_city_patrol`

RflySim runtime references:

- `rflysim_neighborhood_park` -> `ModularNeighborhood/Maps/NeighborhoodPark.umap` (direct_use=False, editor_open=False)

Reconstruction units:

| Visual class | Proxy class | Source | Action |
| --- | --- | --- | --- |
| `terrain` | `terrain_heightfield_or_plane` | `project_owned_geometry` | create visible asset and bind to matching collision/world_geometry proxy |
| `roads` | `road_plane` | `project_owned_geometry` | create visible asset and bind to matching collision/world_geometry proxy |
| `buildings` | `building_box` | `project_owned_geometry` | create visible asset and bind to matching collision/world_geometry proxy |
| `trees` | `tree_trunk_capsule_or_box` | `project_owned_geometry` | create visible asset and bind to matching collision/world_geometry proxy |
| `park_props` | `` | `project_owned_visual_only` | create visual asset; mark render_only unless later linked to a proxy |
| `inspection_waypoints` | `waypoint_marker_box` | `project_owned_geometry` | create visible asset and bind to matching collision/world_geometry proxy |
| `radar_sector` | `` | `bridge_runtime_visual` | render from MWORKS UDP/replay packet; not a static scene asset |
| `local_plan` | `` | `bridge_runtime_visual` | render from MWORKS UDP/replay packet; not a static scene asset |
| `trajectory_trail` | `` | `bridge_runtime_visual` | render from MWORKS UDP/replay packet; not a static scene asset |

Acceptance:

- waypoint mission is visible and not confused with global planner truth
- buildings and tree trunks have proxies when flight-relevant
- local avoidance remains readable in outdoor view

### `open_grass_robustness`

- Map IDs: `open_grass_wind`, `open_grass_robustness`

RflySim runtime references:

- `rflysim_grasslands_3d_display` -> `Grasslands/Maps/Grasslands/3DDisplay.umap` (direct_use=False, editor_open=False)
- `rflysim_grasslands` -> `Grasslands/Maps/Grasslands/Grasslands.umap` (direct_use=False, editor_open=False)

Reconstruction units:

| Visual class | Proxy class | Source | Action |
| --- | --- | --- | --- |
| `grass_field` | `terrain_plane` | `project_owned_geometry` | create visible asset and bind to matching collision/world_geometry proxy |
| `wind_vector_overlay` | `` | `bridge_runtime_visual` | render from MWORKS UDP/replay packet; not a static scene asset |
| `gust_zone` | `gust_zone_box` | `project_owned_geometry` | create visible asset and bind to matching collision/world_geometry proxy |
| `UAV` | `` | `bridge_runtime_visual` | render from MWORKS UDP/replay packet; not a static scene asset |
| `trail` | `` | `bridge_runtime_visual` | render from MWORKS UDP/replay packet; not a static scene asset |
| `metric_overlay` | `` | `bridge_runtime_visual` | render from MWORKS UDP/replay packet; not a static scene asset |
| `fault_efficiency_overlay` | `` | `bridge_runtime_visual` | render from MWORKS UDP/replay packet; not a static scene asset |

Acceptance:

- wind and motor-efficiency parameters are displayed and logged
- trajectory comparison shows tracking degradation/recovery
- rendered video maps to MWORKS raw/native result timestamps

### `maze_indoor_occlusion`

- Map IDs: `map_maze_building`, `maze_building`, `maze_indoor_occlusion`
- Render map JSON: `MworksData/map_maze_building_render_map.json`

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

### `dense_forest_high_obstacle`

- Map IDs: `dense_forest`, `dense_forest_high_obstacle`

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

### `multi_uav_formation`

- Map IDs: `multi_uav_formation`, `formation_line_triangle_diamond`

Reconstruction units:

| Visual class | Proxy class | Source | Action |
| --- | --- | --- | --- |
| `multiple_UAVs` | `` | `bridge_runtime_visual` | render from MWORKS UDP/replay packet; not a static scene asset |
| `formation_links` | `` | `bridge_runtime_visual` | render from MWORKS UDP/replay packet; not a static scene asset |
| `role_labels` | `` | `bridge_runtime_visual` | render from MWORKS UDP/replay packet; not a static scene asset |
| `inter_uav_distance_overlay` | `` | `bridge_runtime_visual` | render from MWORKS UDP/replay packet; not a static scene asset |
| `shared_obstacles` | `shared_obstacle_proxy` | `project_owned_geometry` | create visible asset and bind to matching collision/world_geometry proxy |
| `leader_trail` | `` | `bridge_runtime_visual` | render from MWORKS UDP/replay packet; not a static scene asset |
| `follower_trails` | `` | `project_owned_visual_only` | create visual asset; mark render_only unless later linked to a proxy |

Acceptance:

- formation role and target offsets are visible
- minimum inter-UAV distance is displayed and logged
- scene can reuse a validated single-UAV profile without changing controller truth
