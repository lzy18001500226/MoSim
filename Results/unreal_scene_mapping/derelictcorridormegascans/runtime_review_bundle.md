# Runtime Review Bundle: derelictcorridormegascans

- status: `blocked_runtime_dependencies`
- runtime_blockers: `missing_ros1_rviz_catkin_runtime`, `ros_env:missing_ros1_commands:roscore,roslaunch,rostopic,rosnode,rosparam,rviz`, `ros_env:missing_catkin_build_tool`, `ros_env:ros_environment_not_sourced`, `ros_env:fast_lio_package_not_visible:fast_lio`, `unreal_editor_listener_unavailable`, `blocked_missing_ros1_runtime`
- rendered_scene_window: `Unreal/MoSimSceneLibrary`
- mapping_window: `RViz/RViz2 or equivalent native robotics viewer`
- html_active_pointcloud_window: `false`
- global_truth_used_by_planner: `false`

Commands:
- `dry_run_ue_review`: `OPEN_UE=0 REVIEW_DRY_RUN=1 Scripts/UE5/review_scene_mapping_loop.sh derelictcorridormegascans`
- `unreal_editor_mcp_listener`: `Scripts/UE5/open_unreal_editor_mcp_listener.sh`
- `ue_rendered_scene_review`: `OPEN_UE=1 OPEN_RVIZ=0 STREAM_LOOP_COUNT=1 STREAM_FPS=12 WAIT_UDP_SECONDS=45 Scripts/UE5/review_scene_mapping_loop.sh derelictcorridormegascans`
- `fastlio_ros1_workspace_bootstrap`: `Scripts/UE5/bootstrap_fastlio_ros1_workspace.sh`
- `rviz_mapping_window`: `RVIZ_PROFILE=split Scripts/UE5/open_mapping_rviz_ros1.sh derelictcorridormegascans`
- `rviz_planning_grid_window`: `RVIZ_PROFILE=planning_grid Scripts/UE5/open_mapping_rviz_ros1.sh derelictcorridormegascans`
- `rviz_fastlio_pointcloud_window`: `RVIZ_PROFILE=fastlio_pointcloud Scripts/UE5/open_mapping_rviz_ros1.sh derelictcorridormegascans`
- `fastlio_rviz_runtime`: `Scripts/UE5/run_fastlio_rviz_replay_ros1.sh derelictcorridormegascans`
- `fastlio_topic_check`: `Scripts/UE5/check_fastlio_ros1_topics.sh`
- `fastlio_runtime_record`: `python3 Scripts/UE5/record_fastlio_ros1_runtime.py --scene-id derelictcorridormegascans --output-dir Results/unreal_scene_mapping/derelictcorridormegascans/fastlio_runtime --duration-seconds 20`
- `fastlio_runtime_evaluate`: `python3 Scripts/UE5/evaluate_fastlio_runtime.py --scene-id derelictcorridormegascans --truth-dataset Results/unreal_scene_mapping/derelictcorridormegascans/fastlio_replay_dataset.jsonl --odometry-jsonl Results/unreal_scene_mapping/derelictcorridormegascans/fastlio_runtime/fastlio_odometry.jsonl --output-json Results/unreal_scene_mapping/derelictcorridormegascans/fastlio_runtime/FASTLIO_RUNTIME_EVALUATION.json --output-md Results/unreal_scene_mapping/derelictcorridormegascans/fastlio_runtime/FASTLIO_RUNTIME_EVALUATION.md --fail-on-threshold`

Manual acceptance:
- UE window shows the accepted real rendered scene, not a blockout/STL/blank map.
- UAV body follows the replay inside valid scene bounds without wall penetration.
- RViz/RViz2 split windows show local occupancy/grid plus local plan, and point cloud plus FAST-LIO state.
- FAST-LIO outputs /cloud_registered and /Odometry during a live ROS runtime run.
- evaluate_fastlio_runtime.py passes against replay truth before any localization claim.
- Planner has no access to global truth; exported truth is used only for validation.

Claim boundary:
- This bundle is an execution contract and launch package, not proof that runtime already ran.
- HTML is not an accepted active point-cloud/map window.
- FAST-LIO localization remains unclaimed until ROS runtime topics are recorded and evaluated.
- MWORKS dynamics/control evidence remains separate from UE/RViz visual runtime evidence.
