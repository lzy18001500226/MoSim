# Manual Review Packet: derelictcorridormegascans

Review target:
- Scene source: `local_derelictcorridormegascans`
- UE map: `/Game/DerelictCorridor/Maps/DerelictCorridor`
- UAV replay CSV: `/mnt/c/Users/HP/Desktop/MoSim/Results/unreal_scene_mapping/derelictcorridormegascans/render_replay.csv`
- Point-cloud viewer: `/mnt/c/Users/HP/Desktop/MoSim/Results/unreal_scene_mapping/derelictcorridormegascans/pointcloud_viewer.html`
- FAST-LIO handoff: `/mnt/c/Users/HP/Desktop/MoSim/Results/unreal_scene_mapping/derelictcorridormegascans/fastlio_handoff.json`
- Local-known-map replay: `/mnt/c/Users/HP/Desktop/MoSim/Results/unreal_scene_mapping/derelictcorridormegascans/local_known_map_frames.jsonl`
- UE LiDAR point replay: `/mnt/c/Users/HP/Desktop/MoSim/Results/unreal_scene_mapping/derelictcorridormegascans/lidar_point_frames.jsonl`

Expected evidence:
- The UE window shows the accepted real rendered scene, not the old STL/blockout preview.
- A blue UAV body moves inside the map, with propellers, trajectory trail, radar sector, reference marker, local-plan spline, local-known-map cells, and in-scene LiDAR point cloud.
- The second browser window still shows the offline LiDAR-derived point cloud and planned path.
- The planner did not receive the global truth map as a prior.
- Collision validation against exported UE truth is true.

Planner summary:
- policy: `unknown_global_map_receding_astar_known_obstacles_only`
- path_cells: `43`
- replans: `11`
- lidar_points: `2072`
- global_truth_available_to_planner: `False`
- collision_free_against_truth: `True`

FAST-LIO status:
- `offline_simulated_sensor_handoff_ready`
- This is still an input handoff, not a completed FAST-LIO localization result.

Reject if:
- The scene is black/white/blank, loaded outside the accepted map, or clearly shows the old generated preview map.
- The UAV path starts outside the usable map, visibly clips through walls, or the overlay is absent.
- The UE in-scene point cloud or the browser point-cloud window has zero/obviously wrong points.
