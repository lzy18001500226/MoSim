# Runtime Review Bundle: factoryenvironmentcollect

- status: `ready_for_manual_rviz_ue_review`
- runtime_blockers: `none_for_gate_b_manual_review`
- runtime_degraded: `unreal_editor_listener_unavailable_for_mcp_actor_ops_only`
- rendered_scene_window: `Unreal/MoSimSceneLibrary`
- mapping_window: `RViz/RViz2 or equivalent native robotics viewer`
- html_active_pointcloud_window: `false`
- global_truth_used_by_planner: `false`

Commands:
- `dry_run_ue_review`: `OPEN_UE=0 REVIEW_DRY_RUN=1 Scripts/UE5/review_scene_mapping_loop.sh factoryenvironmentcollect`
- `unreal_editor_mcp_listener`: `Scripts/UE5/open_unreal_editor_mcp_listener.sh`
- `ue_rendered_scene_review`: `OPEN_UE=1 OPEN_RVIZ=0 STREAM_LOOP_COUNT=1 STREAM_FPS=12 WAIT_UDP_SECONDS=45 Scripts/UE5/review_scene_mapping_loop.sh factoryenvironmentcollect`
- `fastlio_ros1_workspace_bootstrap`: `Scripts/UE5/bootstrap_fastlio_ros1_workspace.sh`
- `rviz_mapping_window`: `RVIZ_PROFILE=split Scripts/UE5/open_mapping_rviz_ros2.sh factoryenvironmentcollect`
- `rviz_planning_grid_window`: `RVIZ_PROFILE=planning_grid Scripts/UE5/open_mapping_rviz_ros2.sh factoryenvironmentcollect`
- `rviz_fastlio_pointcloud_window`: `RVIZ_PROFILE=fastlio_pointcloud Scripts/UE5/open_mapping_rviz_ros2.sh factoryenvironmentcollect`
- `fastlio_rviz_runtime`: `FASTLIO_ROS2_LAUNCH_CMD='set +u; source /opt/ros/humble/setup.bash; source Results/tmp/fast_lio_ros2_import_ws/install/fast_lio/share/fast_lio/local_setup.bash; ros2 launch fast_lio mapping.launch.py rviz:=false config_path:=/mnt/c/Users/HP/Desktop/MoSim/Config/ros2 config_file:=mosim_fast_lio_ros2_mid360.yaml' START_FASTLIO=1 START_RVIZ=1 RVIZ_PROFILE=split Scripts/UE5/run_fastlio_rviz_replay_ros2.sh factoryenvironmentcollect`
- `fastlio_topic_check`: `Scripts/UE5/check_fastlio_ros2_topics.sh`
- `fastlio_input_topic_check`: `REQUIRE_FASTLIO_OUTPUTS=0 Scripts/UE5/check_fastlio_ros2_topics.sh`
- `fastlio_runtime_record`: `python3 Scripts/UE5/record_fastlio_ros2_runtime.py --scene-id factoryenvironmentcollect --output-dir Results/unreal_scene_mapping/factoryenvironmentcollect/fastlio_runtime_manual_review --duration-seconds 20`
- `fastlio_runtime_evaluate`: `python3 Scripts/UE5/evaluate_fastlio_runtime.py --scene-id factoryenvironmentcollect --truth-dataset Results/unreal_scene_mapping/factoryenvironmentcollect/fastlio_mworks_truth_dataset.jsonl --odometry-jsonl Results/unreal_scene_mapping/factoryenvironmentcollect/fastlio_runtime_manual_review/fastlio_odometry.jsonl --output-json Results/unreal_scene_mapping/factoryenvironmentcollect/fastlio_runtime_manual_review/FASTLIO_RUNTIME_EVALUATION.json --output-md Results/unreal_scene_mapping/factoryenvironmentcollect/fastlio_runtime_manual_review/FASTLIO_RUNTIME_EVALUATION.md --fail-on-threshold`

Manual acceptance:
- UE window shows the accepted real rendered scene, not a blockout/STL/blank map.
- UAV body follows the replay inside valid scene bounds without wall penetration.
- RViz2 split windows show local occupancy/grid plus local plan, and point cloud plus FAST-LIO state.
- FAST-LIO outputs `/cloud_registered`, `/odometry`, and `/path` during the live ROS2 runtime review.
- Gate B formal evidence has already passed against `fastlio_mworks_truth_dataset.jsonl`; manual review now checks visual correctness of UE + RViz2 windows.
- Planner has no access to global truth; exported truth is used only for validation.

Claim boundary:
- This bundle is an execution contract and launch package, not proof that runtime already ran.
- HTML is not an accepted active point-cloud/map window.
- FAST-LIO Gate B headless localization evidence is claimable for Factory manual review only; final controller/planner integration remains unclaimed.
- MWORKS dynamics/control evidence remains separate from UE/RViz visual runtime evidence.
