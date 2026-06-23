# Mainline Operations Board

> PMO-facing short board for current MoSim operations. Keep this file concise:
> it is not a history ledger, not a packet archive, and not a replacement for
> `CoAgent/docs/operating/coagent_ops_patrol_workflow.md`.

Status: temporary single-thread execution mode is active while the CoAgent
visible-thread architecture is being optimized. Do not dispatch to visible
department threads from this mode. Current 2026-06-20 evening override:
single-thread execution for Sunray takeoff-hover-land, 8字, Gazebo Classic
animation, RViz trajectory/path, and MID360 point-cloud review must use
`Docs/Workflows/sunray_ros1_current_runtime_lane.md`: Ubuntu-20.04 / ROS1
Noetic / `References/Sunray` / `References/Lab/FAST_LIO`. Do not use old
ROS2/PX4/x500, downloaded FAST-LIO replacements, empty point-cloud topics, or
equivalent-substitute runtimes as current review evidence. Historical ROS2/PX4
/Gazebo evidence below remains audit context only unless PMO/user explicitly
reopens that route.

Historical single-thread context is quarantined in Section 8. It is retained
for audit only and must not be read as the next-action queue during startup.
During normal startup, stop after the P0 partition board unless the current
task explicitly asks for historical ROS2/PX4 trace-back.
The old `Docs/Workflows/single_thread_longrun_execution_queue_20260610.md`
file is historical/context only; its former PX4/Gazebo/ROS2 queue must not
steer current execution.

## 1. PMO Startup Loop

Every PMO turn starts here after `AGENTS.md` and
`Docs/Workflows/new_conversation_context.md`:

1. Read this board first.
2. Check only the return/blocker packets named in this board.
3. If a state is unclear, trace back through
   `Docs/Workflows/agent_task_ledger.md` and the referenced packets.
4. Decide one next PMO action per P0 partition before support-lane work.
5. Update this board when a return/blocker changes PMO dispatch decisions.

Routine startup does not ingest the full ledger. The ledger is recovery and
audit context.

## 2. Ownership Boundaries

| Owner | Owns | Does Not Own |
|---|---|---|
| PMO | Mainline operating architecture, P0 priority, dispatch, acceptance, integration, thread lifecycle decisions, manual/GUI decisions, restart/recovery decisions | Long worker execution when a visible department owns the task |
| CoAgentOps | 10-minute patrol, recovery execution, bounded dispatch under `coagent_ops_patrol_workflow.md`, state reporting, thread-registry hygiene | Product priority, engineering acceptance, broad automation/thread lifecycle changes, final integration |
| 文档秘书部 | Context maintenance, documentation consistency review, cache-first migration, periodic cleanup, compact recovery notes | Defining PMO runtime rules, choosing P0 priority, accepting engineering results, recovering dead threads |
| Current single-thread executor | Temporary local-only PMO/docs/static/checker execution while visible dispatch is paused by user direction. It may complete explicitly authorized local simulation/UE evidence slices and must record goal/sub-agent planning locally. | Visible-thread dispatch, product acceptance, final integration claims, or durable role-policy changes |

`CoAgent/docs/operating/coagent_ops_patrol_workflow.md` is the primary
CoAgentOps patrol/recovery source. The MoSim compatibility adapter at
`Docs/Workflows/coagent_ops_patrol_workflow.md` remains valid for host-specific
board paths, thread ids, MWORKS/ROS2/UE details, and no-loss migration review.

## 3. State Enums

Use these board states only:

```text
running
waiting_return
dispatch_needed
blocked_open_dependency
manual_decision_needed
recovery_pending
ready_to_integrate
frozen_by_user
support_only
done_no_action
```

Do not write vague states such as `healthy`, `normal`, `looks fine`, or
`probably blocked`.

## 4. Dispatch SLO Watchlist

Active dispatch monitoring rows use exactly these columns. The detailed
dispatch ticket JSON stores target thread, task type, expected paths,
checkpoint due, observations, and validation evidence.

| sent_at | first_readback_due | expected_packet_due | last_observed_turn | breach_action | owner |
|---|---|---|---|---|---|
| 2026-06-09T21:38:17+08:00 | 2026-06-09T21:38:47+08:00 | 2026-06-09T22:38:17+08:00 | 019eac9a-f76d-7390-bb38-20b56bb723e1 status=inProgress agent_output_seen; no 032 return/blocker found in 2026-06-10 local sweep | breached_stale_no_terminal_packet | PMO / single-thread executor |

## 5. P0 Partition Board

| Partition | Current State | Waiting Returns | Blockers | Human Decisions | Integrable Results | Next PMO Action | Forbidden Actions |
|---|---|---|---|---|---|---|---|
| MWORKS | ready_to_integrate | none for current single-thread MWORKS smoke/closeout slice | 032 remains historical visible-thread terminal-packet debt, but it no longer blocks the current UE source-static/loopback path | User/PMO still decides any new live MWORKS GUI/layout/result-window review or report-final wording | 7/7 formal Dynamics smoke scenarios accepted as `dynamics_smoke_only`; single-UAV gate is `single_uav_gate_ready_for_ue_prep`; LinearMPC online fault-allocation rotor1-loss candidate remains the accepted current MWORKS_MCP run; its raw/metrics/replay artifacts now feed a passed UE replay input bundle and local UDP loopback smoke | Treat current MWORKS slice as closed for UE prep; do not start formation yet | No duplicate 031/032, no login click, no activation/license overclaim, no controller-performance claim from diagnostics smoke, no final report acceptance by implication |
| Sunray ROS1 | running | none yet for the current Sunray ROS1 review lane; latest timing proof is `Results/sunray_ros1/sunray_ros1_topic_probe_longwait_20260620_181942/` | Current blockers must stay in this lane. If takeoff-hover-land, 8字, Gazebo animation, RViz trajectory/path, or MID360 PointCloud2 fails, return a Sunray ROS1 blocker instead of switching to ROS2/PX4/x500 or downloaded FAST-LIO. | PMO/user decides any architecture change away from ROS1/Sunray or any acceptance of headless output as visual review evidence. | Long-wait probe observed `/uav1/livox/lidar` as nonempty `PointCloud2` and `/uav1/livox/imu`; this is timing/source proof only, not mission completion. | Start from `Docs/Workflows/sunray_ros1_current_runtime_lane.md`; next actions are source/runtime preflight, takeoff-hover-land, MID360 nonempty proof, 8字 mission, and Gazebo/RViz review package under `Results/sunray_ros1/`. | No ROS2/PX4/x500 substitution, no `Results/external_downloads/fast_lio_main.zip` as first source while `References/Lab/FAST_LIO` exists, no fake/static/empty point cloud, no headless pass as GUI/RViz acceptance, no planner_ready/final_closed_loop/controller-performance claim. |
| UE | running | none for current UE replay and command-echo hardening slices | 034 remains latest historical live preflight; no live seven-artifact command-echo capture bundle exists yet; current opened review screenshots do not show Sunray150 clearly by eye; UE/RViz runtime readiness still reports `unreal_editor_listener_unavailable` | PMO/user product acceptance is still needed for final/manual visual acceptance and material acceptance, but opening existing review materials no longer waits for separate authorization | 037 classifies the 036 runtime-echo implementation surface as `build_only_gate_ready`; accepted MWORKS run has `ue_replay_input_bundle.json` plus passed local `ue_state_stream_loopback.json`; build-only gate passed at `Results/ue_build/20260612_102452_mosim_scene_library_editor_build/build_manifest.json`; bounded runtime replay ingest probe passed at `Results/ue_replay_input/20260612_rotor1_loss15_linear_mpc_online_fault_allocation/ue_runtime_probe_20260612_1105/ue_runtime_replay_probe_summary.json`; current UE truth/replay aggregate contract passed at `Results/unreal_scene_mapping/UE_TRUTH_REPLAY_CONTRACT_CHECK.json` for Factory and Derelict scenes; current command-echo hardening evidence is under `Results/unreal_experiment_console/command_echo_evidence_hardening_20260612_001/`; current visual-review planning packet is `Results/ue_replay_input/20260612_rotor1_loss15_linear_mpc_online_fault_allocation/ue_review_path_20260612_001/current_review_packet.json` | Treat UE truth/replay file contract as ready for downstream prep; continue with the next executable UE path: either produce close/zoomed after-stream Sunray150 visual-review evidence, or run one bounded command-echo live probe that produces the seven required artifacts and then validate it | No duplicate 036/037, no authoritative UE command echo ack from static/checker/build/sender/UDP/state-frame evidence, no final/manual visual acceptance from far scene screenshots, no MWORKS downlink, ROS2 runtime echo, Gazebo runtime success, PointCloud2 runtime evidence, planner_ready, controller-performance-from-UE, material acceptance, multi-UAV readiness, or closed_loop claim |
| Git | running | DevOps closeout remains active by ledger | Large-tree ignore/drain queue still active; broad Git porcelain can be slow/noisy | PMO decides specific next path-limited batch when Git work becomes priority | Prior pushed slices are historical evidence; current staged runtime outputs are not this board's completion evidence | Keep Git work path-limited and do not let support work mask P0 engineering blockers | No `git add -A`, no force push/reset/clean, no broad cleanup, no hidden `.gitignore` backlog |
| Ops | recovery_pending | Post-PC-restart sweep blocker is available at `PMO-POST-PC-RESTART-P0-DISPATCH-SURFACE-SWEEP-20260609-001`; CoAgentOps is currently ACK-capable | MWORKS R1, ROS2 R1, and UE failed current post-PC-restart send attempts; 文档秘书部 also remains support-lane recovery debt | No restart now. User-facing notice was sent by sparse email at 2026-06-09T15:17:03+08:00 | CoAgentOps and MWORKS R2 returned exact post-PC-restart ACKs; CoAgentOps 029/079/036 blocker is validated; R2 030 delivery completed and return passed validation | Keep recovery evidence current; use R2 only for bounded static MWORKS work until primary P0 threads are superseded restored | No WeChat health checks, no archived gateway no-op, no replacement thread without explicit approval, no Codex restart from this sweep, no treating probe ACK as business/runtime success |

## 8. Historical Quarantine: ROS2/PX4/Gazebo Audit Context

Do not read this section during normal startup. It exists only for trace-back
after the current Sunray ROS1 lane workflow or a packet explicitly asks for old
ROS2/PX4/Gazebo evidence.

2026-06-18 historical single-thread Gazebo/ROS2 increment retained for audit
only. It must not steer current Sunray ROS1 review work unless PMO/user
explicitly reopens the ROS2/PX4 route:

```text
latest plant parameter audit: Results/gazebo_ros2/sunray150_assembled_parameter_audit_20260618/GAZEBO_PARAMETER_CONSISTENCY_AUDIT.md. The audit has 13 rows, adopts 6 reviewed assembly geometry rows, keeps MID360 pose as held_for_review, keeps mass/inertia/motor plugin constants under separate-source/runtime validation, and records no reviewed-geometry mismatches. Current SDF total link mass is 0.69kg and the theoretical normalized hover command is 0.0556055205.
current accepted Gazebo plant parameter correction: Config/gazebo/models/sunray150_assembled/model.sdf now uses the reviewed assembly rotor centers and the reviewed body collision envelope pose [0, 0.001574, 0.044965, 0, 0, 0] with size [0.211502, 0.214651, 0.16193]. Do not replace dynamics constants from the assembly JSON.
latest takeoff-hover-land plant sanity pass: Results/gazebo_ros2/sunray150_takeoff_hover_land_plant_sanity_20260618_004/RUNTIME_STATUS.json passed. It uses a simple truth-feedback staged controller against Config/gazebo/worlds/sunray150_takeoff_hover_land_plant_sanity.sdf and proves only that the accepted Gazebo plant can take off, hover near 0.6m, and land under a bounded simple controller. Metrics: duration 13.032s, max z 0.836887m, final z 0.048684m, hover mean abs z error 0.140992m, hover max abs z error 0.234829m, max XY 0.165252m, max tilt 0.004286rad.
plant sanity claim boundary: this does not prove MWORKS controller deployment, competition controller performance, planner_ready, final closed_loop acceptance, UE acceptance, or multi-UAV readiness.
scope: non-UE, non-multi-UAV competition closure
truth source status: accepted for light-world same-run comparison
vehicle: model://sunray150_assembled
truth topic: /world/sunray150_single_uav_competition_light/state
truth entity: selected assembled UAV body entity id 24 near initial pose (0,0,1.2)
truth evidence: Results/gazebo_ros2/sunray150_single_uav_competition_light_truth_state_probe_20260617_002/GAZEBO_TRUTH_POSE_RECORDING.json
current sensor/local-map/truth aggregation: Results/gazebo_ros2/sunray150_single_uav_competition_light_sensor_local_map_truth_20260618_header_rate_001/RUNTIME_STATUS.json passed. It records raw MID360-like LiDAR PointCloud2 at 20000 points/frame, frame sunray150_assembled/base_link/mid360_lidar, LiDAR header-stamp rate about 10Hz, local voxels 432 points in map, local grid 120x120 in map, and TF map -> sunray150_assembled/base_link/mid360_lidar. Warning retained: topic_list_snapshot_empty_but_samples_or_rates_recorded, because the ros2 topic-list snapshot was empty while samples/rates were recorded.
default competition development gate: the light-world 48s figure-8/static-obstacle default now matches the stable validated configuration instead of the earlier 24s/1.2m aggressive preset. The current default scenario is the 48s, 1.0m reference-altitude, 0.6m amplitude, y_offset 0.8m single-UAV development gate; it passed again without `TRACKER_KI_Z_OVERRIDE` and remains pre-acceptance only.
latest same-run default gate with map review: Results/gazebo_ros2/default_48s_same_run_current_recheck_20260618_072626/RUNTIME_STATUS.json passed. It records the same stable 48s default gate and a same-run map review with raw LiDAR PointCloud2 at 20000 points/frame in frame sunray150_assembled/base_link/mid360_lidar, 6637 finite lidar points in the reviewed sample, 1181 local occupancy voxels in map, and a 120x120 local occupancy grid with 1049 occupied cells. Tracking metrics: truth_samples=239, tracker_samples=834, adapter_published=874, rmse_xy_m=0.860137, max_xy_error_m=1.200738, max_z_error_m=0.585952, truth_min_clearance_m=0.367781. This is the current best same-run review baseline for the default single-UAV development gate.
latest continuation regression: Results/gazebo_ros2/single_uav_goal_continue_same_run_20260618_075113/RUNTIME_STATUS.json passed. It records the stable default 48s single-UAV figure-8/static-obstacle gate plus same-run raw LiDAR and downstream local-map review. Tracking metrics: truth_samples=239, tracker_samples=834, adapter_published=874, rmse_xy_m=0.863938, max_xy_error_m=1.203297, max_z_error_m=0.591766, truth_min_clearance_m=0.366812. Map review passed with raw LiDAR PointCloud2 at 20000 points/frame in frame sunray150_assembled/base_link/mid360_lidar, 2569 finite lidar points in the reviewed sample, 356 local occupancy voxels in map, and a 120x120 local occupancy grid with 131 occupied cells. Use this as the freshest same-run regression evidence for the current single-UAV goal; the preferred visual-density baseline remains default_48s_same_run_current_recheck_20260618_072626.
latest default hover entry repair and pass: Scripts/gazebo/run_sunray150_hover_hold_closed_loop.sh now defaults to Config/scenarios/system/sunray150_single_uav_competition_light.yaml instead of the older smoke scenario. Verification: Results/gazebo_ros2/hover_hold_default_entry_after_fix_20260618_080459/RUN_MANIFEST.json passed with scene_id sunray150_single_uav_competition_light and vehicle_id sunray150_assembled. Hover metrics: controller_samples=218, adapter_published=258, truth_samples=82 after controller-window crop, final_z_m=1.163734, final_abs_z_error_m=0.036266, max_abs_z_error_m=0.530641, max_xy_distance_m=0.076043, max_tilt_rad=0.001183. This is bounded hover pre-acceptance only.
latest pre-multi-UAV same-run review: Results/gazebo_ros2/single_uav_prenulti_same_run_review_20260618_081009/RUNTIME_STATUS.json passed. It combines the current 48s single-UAV figure-8/static-obstacle gate with same-run raw LiDAR and downstream local-map review. Flight metrics: truth_samples=239, tracker_samples=834, adapter_published=874, rmse_xy_m=0.856613, max_xy_error_m=1.200777, max_z_error_m=0.582842, truth_min_clearance_m=0.376729. Raw LiDAR is /mosim/gazebo/lidar_points/points in frame sunray150_assembled/base_link/mid360_lidar with 20000 points/frame and 7631 finite points in the reviewed sample. Downstream local occupancy voxels are 643 finite points in map, and the 120x120 local occupancy grid has 574 occupied cells. Review figures are under Results/gazebo_ros2/single_uav_prenulti_same_run_review_20260618_081009/map_review/figures/.
latest FAST-LIO/planner input surface recheck: Results/gazebo_ros2/fastlio_planner_input_competition_light_recheck_20260618_081645 now has a sparse-graph 补判定 pass at RUNTIME_STATUS_REBUILT_AFTER_SPARSE_GRAPH_FIX.json. The original ROS graph snapshot/echo samples were sparse, but adapter report evidence, TF, source LiDAR sample, and IMU passthrough evidence prove the bounded input surface. fastlio_planner_input_adapter.json records lidar_received=1323, fastlio_lidar_published=1323, spark_livox_custom_published=1323, planner_global_points_published=1323, mosim_planner_global_points_published=1323, planner_odom_published=1908, mosim_planner_odom_published=1908, tf_lookup_failures=0, frame_mismatch_count=0, and review_accumulated_last_point_count=57180. fastlio_imu_passthrough.json records imu_received=255685, fastlio_imu_published=255685, sunray_imu_published=255685, frame_mismatch_count=0, observed_input_average_hz=748.105. This remains FAST-LIO/planner input-surface evidence only: no FAST-LIO localization success, planner_ready, setpoint, command authority, actuator command, final closed_loop, or multi-UAV readiness.
latest hover regression pass: Results/gazebo_ros2/hover_hold_current_recheck_/GAZEBO_HOVER_HOLD_CLOSED_LOOP_EVAL.json. This current hover recheck passed with final z 0.968090m, final abs z error 0.231910m, max XY distance 0.079899m, max tilt 0.001038rad, controller samples=218, adapter publishes=258, and truth samples=76. It proves only bounded hover pre-acceptance, not trajectory completion or final closed-loop acceptance.
previous 30s hover regression pass: Results/gazebo_ros2/hover_hold_split_axis_30s_20260618_015039/GAZEBO_HOVER_HOLD_CLOSED_LOOP_EVAL.json. This 30s hover gate passed with final z 0.963296m, final abs z error 0.236704m, max XY distance 0.082392m, and max tilt 0.003862rad.
previous short hover confirmation: Results/gazebo_ros2/hover_hold_split_axis_12s_20260618_014824/GAZEBO_HOVER_HOLD_CLOSED_LOOP_EVAL.json. This 12s hover gate passed with final z 0.968339m, final abs z error 0.231661m, max XY distance 0.080526m, and max tilt 0.001128rad.
previous hover regression pass: Results/gazebo_ros2/sunray150_single_uav_hover_regression_after_figure8_20260617_001/GAZEBO_HOVER_HOLD_CLOSED_LOOP_EVAL.json
latest full-window figure-8/static-obstacle pre-acceptance pass: Results/gazebo_ros2/figure8_full_window_headless_safe_20260618_2150/FIGURE8_STATIC_OBSTACLE_GATE.json
full-window figure-8 notes: 48s real Gazebo/ROS2 headless run, period 40s, x_amp=0.6m, y_amp=0.6m, y_offset=0.8m, altitude=1.0m, obstacle radius=0.35m, split-axis horizontal control signs roll=-1 and pitch=+1. Gate passed with independent Gazebo truth samples=239 after tracker/reference-window cropping, tracker samples=834, adapter publishes=874, XY RMSE=0.858035m, max XY error=1.200852m, max Z error=0.60843m, max reference time delta=0.045899s, reference clearance=0.37267m, and truth obstacle clearance=0.37024m. This is complete-window pre-acceptance and review evidence, not final controller-performance proof.
latest full-window review artifact: `Results/gazebo_ros2/figure8_full_window_headless_safe_20260618_2150/review/FIGURE8_REVIEW_MANIFEST.json` plus `figure8_truth_reference_topdown.png` and `figure8_altitude_time.png`.
previous figure-8/static-obstacle pre-acceptance pass: Results/gazebo_ros2/figure8_headless_after_gui_blocker_20260618_053129/FIGURE8_STATIC_OBSTACLE_GATE.json
figure-8 gate notes: current safe 24s headless real Gazebo/ROS2 run, period 40s, x_amp=0.6m, y_amp=0.6m, y_offset=0.8m, altitude=1.0m, obstacle radius=0.35m, split-axis horizontal control signs roll=-1 and pitch=+1, PositionCommand -> PlannerSetpoint -> ControllerOutput -> Gazebo actuator plant. Gate passed with independent Gazebo truth samples=119, tracker samples=401, adapter publishes=441, XY RMSE=0.701829m, max XY error=0.926982m, max Z error=0.608634m, reference clearance=0.372671m, and truth obstacle clearance=0.620884m.
previous safe figure-8/static-obstacle pass: Results/gazebo_ros2/figure8_current_recheck_safe_20260618_052106/FIGURE8_STATIC_OBSTACLE_GATE.json. It passed with XY RMSE=0.698173m, max XY error=0.927457m, max Z error=0.608395m, reference clearance=0.372671m, and truth obstacle clearance=0.619878m.
latest GUI review blocker: Results/gazebo_ros2/figure8_gui_review_safe_20260618_052911/BLOCKER.json. The same safe parameter set failed when run with Gazebo GUI review: max Z error 0.983114m exceeded 0.85m, truth clearance -0.049548m was below 0m, and Gazebo GUI stderr contains an OGRE render shutdown segmentation fault. Treat this as a visual-review/runtime-performance blocker, not as superseding the passing headless control-chain evidence.
latest figure-8 blocker: Results/gazebo_ros2/figure8_current_recheck_20260618_051818/BLOCKER.json failed because the reference trajectory clearance was below the declared minimum (0.309794<0.350000), not because the current safe trajectory failed.
previous figure-8/static-obstacle pass: Results/gazebo_ros2/sunray150_single_uav_figure8_split_axis_sign_60s_gate_20260617_001/FIGURE8_STATIC_OBSTACLE_GATE.json. This 60s long-window run used 0.18m x/y amplitude and passed with XY RMSE=0.224955m, max XY error=0.414160m, max Z error=0.533687m, and truth obstacle clearance=0.398927m.
historical long-window figure-8 blocker: Results/gazebo_ros2/sunray150_single_uav_figure8_long_window_probe_20260617_001/BLOCKER.json
historical blocker notes: earlier 60s Gazebo/ROS2 run failed because the truth-feedback position controller used one global XY sign, stayed mostly in takeoff_altitude_hold, ended near z=0.106m, and failed xy RMSE, max XY, max Z, and obstacle-clearance thresholds. Current split-axis 60s gate supersedes it for the active pre-acceptance lane.
late visual recheck blocker: user-observed Gazebo animation showed falling-leaf/self-rotation style behavior, so all previous "full simulation OK" wording is invalid until revalidated from real Gazebo animation.
latest plant-stability regression pass: Results/gazebo_ros2/hover_hold_12s_plant_recheck_after_sdf_fix_1781710139/GAZEBO_HOVER_HOLD_CLOSED_LOOP_EVAL.json. This 12s hover gate passed with max tilt 0.003094rad and max XY 0.381683m; it proves only bounded hover pre-acceptance, not trajectory completion.
latest root-cause correction: pitch horizontal control sign was wrong for the accepted `model://sunray150_assembled` Gazebo plant. A 12s override test with `pitch_control_sign=+1` passed at Results/gazebo_ros2/figure8_12s_hover0558_pitchpos_recheck_1781710894/FIGURE8_STATIC_OBSTACLE_GATE.json.
latest default short-gate pass after YAML/runner update: Results/gazebo_ros2/figure8_12s_yaml_defaults_recheck_1781711062/FIGURE8_STATIC_OBSTACLE_GATE.json. It passed with XY RMSE=0.258130m, max XY error=0.392050m, max Z error=0.613725m, and truth obstacle clearance=0.517515m. The tracker used roll_control_sign=-1 and pitch_control_sign=+1. This is a short 12s, small-amplitude pre-acceptance regression only.
latest same-run figure-8 + raw LiDAR/local-map evidence: Results/gazebo_ros2/figure8_full_window_same_run_map_review_20260618_001/RUNTIME_STATUS.json passed. It records a 47.968s figure-8/static-obstacle pre-acceptance run and a same-run map review at Results/gazebo_ros2/figure8_full_window_same_run_map_review_20260618_001/map_review/GAZEBO_ROS2_MAP_REVIEW.json. Raw LiDAR PointCloud2 is 20000 points/frame in frame sunray150_assembled/base_link/mid360_lidar; local occupancy voxels are 130 points in map; local occupancy grid is 120x120 in map. Tracking metrics: truth_samples=237, tracker_samples=801, adapter_published=841, xy_rmse_m=0.851403, max_xy_error_m=1.20125, max_z_error_m=0.589446, truth_min_clearance_m=0.37766.
latest control-tuned same-run figure-8 + raw LiDAR/local-map candidate: Results/gazebo_ros2/single_uav_48s_alt10_ki00035_same_run_map_20260618_064629/RUNTIME_STATUS.json passed. It uses `TRACKER_KI_Z_OVERRIDE=0.00035`, keeps hover command at the baseline value, and records a 48.004s figure-8/static-obstacle pre-acceptance run at 1.0m reference altitude. The altitude steady-state error improved materially: final tracker z error is about 0.036655m, while XY/clearance still pass. Tracking metrics: truth_samples=235, tracker_samples=834, adapter_published=874, rmse_xy_m=0.854535, max_xy_error_m=1.200862, max_z_error_m=0.580719, truth_min_clearance_m=0.378079. Same-run map review passed with raw LiDAR PointCloud2 at 20000 points/frame in frame sunray150_assembled/base_link/mid360_lidar, 2477 finite points in the reviewed sample, 91 finite local occupancy voxels in map, and a 120x120 local occupancy grid with 91 occupied cells. Because this map review captured a near-field slice, keep the wider-view map figures from the previous 48s baseline as better human map-review illustrations.
latest wider-view same-run figure-8 + raw LiDAR/local-map review baseline: Results/gazebo_ros2/single_uav_48s_alt10_same_run_map_20260618_063729/RUNTIME_STATUS.json passed. It records a 47.944s figure-8/static-obstacle pre-acceptance run at 1.0m reference altitude and a same-run map review at Results/gazebo_ros2/single_uav_48s_alt10_same_run_map_20260618_063729/map_review/GAZEBO_ROS2_MAP_REVIEW.json. Raw LiDAR PointCloud2 is 20000 points/frame in frame sunray150_assembled/base_link/mid360_lidar with 5850 finite points in the reviewed sample; local occupancy voxels are 518 finite points in map; local occupancy grid is 120x120 in map with 448 occupied cells. Tracking metrics: truth_samples=239, tracker_samples=834, adapter_published=874, rmse_xy_m=0.857047, max_xy_error_m=1.200668, max_z_error_m=0.600444, truth_min_clearance_m=0.374302. Review figures are under Results/gazebo_ros2/single_uav_48s_alt10_same_run_map_20260618_063729/review/ and Results/gazebo_ros2/single_uav_48s_alt10_same_run_map_20260618_063729/map_review/figures/.
previous long-goal same-run figure-8 + raw LiDAR/local-map evidence: Results/gazebo_ros2/single_uav_long_goal_same_run_20260618_062314/RUNTIME_STATUS.json passed. It records a 59.216s figure-8/static-obstacle pre-acceptance run and a same-run map review at Results/gazebo_ros2/single_uav_long_goal_same_run_20260618_062314/map_review/GAZEBO_ROS2_MAP_REVIEW.json. Raw LiDAR PointCloud2 is 20000 points/frame in frame sunray150_assembled/base_link/mid360_lidar; local occupancy voxels are 110 points in map; local occupancy grid is 120x120 in map. Tracking metrics: truth_samples=295, tracker_samples=1001, adapter_published=1041, rmse_xy_m=1.965496, max_xy_error_m=3.96896, max_z_error_m=0.683334, truth_min_clearance_m=0.26493. This run remains useful as a longer-window pass, but the 48s 1.0m same-run baseline above is the current cleaner review baseline.
failed altitude-hover tuning note: Results/gazebo_ros2/single_uav_alt_tune_hover05545_20260618_063149/BLOCKER.json failed after increasing hover command to 0.05545. Failure was dominated by XY divergence (rmse_xy_m=12.674327, max_xy_error_m=22.996596) and obstacle clearance breach, so simple hover-command uplift is not the next tuning route.
failed old-default gate note: Results/gazebo_ros2/sunray150_single_uav_figure8_static_obstacle_pre_acceptance/BLOCKER.json is retained as the historical blocker for the old aggressive default preset. It failed with `xy_rmse_m=19.539031`, `max_xy_error_m=26.862408`, and `max_z_error_m=1.182180` before the scenario default was rebased to the current stable development gate.
current review gate: do not package current evidence as full competition completion or final controller-performance proof. The active review requirement remains complete Gazebo simulation animation using the accepted `model://sunray150_assembled`, light competition world, visible rotating propellers, stable attitude, and figure-8/static-obstacle control chain. The figure-8 evaluator now includes hard shape checks for XY span, path-length ratio, lobe coverage, and center crossings, because the previous numeric-only gate could pass a visually invalid small/partial loop.
headless review artifact: `Results/gazebo_ros2/figure8_headless_after_gui_blocker_20260618_053129/review/FIGURE8_REVIEW_MANIFEST.json` plus `figure8_truth_reference_topdown.png` and `figure8_altitude_time.png`. These are review aids built from the passing 24s headless run only; they do not replace GUI animation acceptance.
claim boundary: LiDAR point cloud is raw radar/sensor output for localization/mapping input; local occupancy voxels/grid are downstream map products derived from point cloud plus pose/TF/local-map processing. Current Gazebo LiDAR remains a gpu_lidar approximation of MID360-like output, not a full Livox scan-mode plugin. Truth-feedback position controller evidence remains pre-acceptance; do not claim planner_ready, final closed_loop, competition controller performance, UE acceptance, or multi-UAV readiness.
latest single-UAV review package: Results/gazebo_ros2/single_uav_goal_review_20260618_153349/SINGLE_UAV_REVIEW_INDEX.md. The old `single_uav_goal_figure8_same_run_20260618_153005` completion claim remains withdrawn because shape re-evaluation fails (`truth_path_length_ratio=0.596884<0.8`, `center_crossings_x=1<2`). The corrected default Gazebo/ROS2 run is Results/gazebo_ros2/single_uav_final_shape_default_map_review_20260618_163650/RUNTIME_STATUS.json: it passes the stricter shape gate and same-run map review with duration 124.96s, XY RMSE 0.719315m, max XY error 1.089462m, max Z error 0.573923m, truth clearance 0.507697m, span x 1.200476m, span y 1.309029m, path-length ratio 1.20432, and center crossings x 2. Current status is `review_required_after_shape_fix`: do not claim final Gazebo GUI animation acceptance until the corrected run is visually reviewed in Gazebo.
current truth-synced single-UAV Gazebo baseline: Results/gazebo_ros2/single_uav_figure8_truthsynced_config_gate_20260619_015624/RUNTIME_STATUS.json passed. The runner now advances the figure-8 reference from Gazebo truth time instead of wall time, preventing WSL/Gazebo slowdowns from feeding late-mission setpoints to a newly taking-off vehicle. The active scenario default is 60s total, 20Hz reference, 24s figure-8 period, 0.6m x/y amplitude, y_offset=1.0m, altitude=1.0m, takeoff/hold/figure8/post-hold/land/final-hold phases, and same-run raw LiDAR/local voxel/local grid review. Metrics: XY RMSE 0.041045m, max XY error 0.218811m, figure-8 phase max XY error 0.224344m, max Z error 0.447848m, truth clearance 0.502827m, truth span x 1.22932m, truth span y 0.65144m, path-length ratio 1.078463, center crossings x 3, final z 0.035999m, landing-window XY displacement 0.000138m. Same-run map review passed with raw LiDAR 20000 points/frame, 5157 finite points in the reviewed sample, local occupancy voxels 486 finite points in map, and 120x120 local occupancy grid with 361 occupied cells. This supersedes the older wall-clock reference attempts for current single-UAV Gazebo figure-8 evidence, but it remains truth-feedback pre-acceptance rather than final MWORKS controller-performance proof, planner_ready, final closed_loop acceptance, UE acceptance, FAST-LIO localization acceptance, or multi-UAV readiness.
latest pre-multi-UAV Gazebo/ROS2 runtime closeout, 2026-06-19: single-UAV runtime evidence has advanced from scaffolding to real Gazebo/ROS2 gates. FAST-LIO source-runtime localization passed at `Results/gazebo_ros2/single_uav_spark_fastlio_localization_gate_20260619_024023/RUNTIME_STATUS.json`: Gazebo raw LiDAR is 20000 PointCloud2 points/frame, Spark Livox input records `point_num=5376`, `/cloud_registered` is frame `map` with 33 recorded frames, `/odometry` has 1911 records, `/path` has 3 records, and truth-error evaluation at `FASTLIO_TRUTH_ERROR_EVAL.json` passes with origin-aligned RMSE `0.007244m`; direct RMSE `1.035199m` is retained as map-origin offset diagnosis. Plant sanity passed at `Results/gazebo_ros2/single_uav_takeoff_hover_land_gate_20260619_024335/GAZEBO_TAKEOFF_HOVER_LAND_EVAL.json`: max z `0.845334m`, final z `0.106126m`, hover max abs z error `0.261879m`, max XY `0.207448m`, and max tilt `0.003432rad`. The freshest full 8字/static-obstacle gate passed at `Results/gazebo_ros2/single_uav_figure8_obstacle_gate_20260619_025019/FIGURE8_STATIC_OBSTACLE_GATE.json`: duration `59.94s`, XY RMSE `0.034684m`, figure-8 phase XY RMSE `0.051321m`, truth clearance `0.501935m`, path-length ratio `1.077358`, center crossings `3`, final z `0.035999m`, and landing-window XY displacement `0.000036m`; same-run map review used raw LiDAR 20000 points/frame, 5158 finite points, 501 local occupancy voxels, and 120x120 local grid with 363 occupied cells. Real EGO bspline/local-map gate passed at `Results/gazebo_ros2/single_uav_real_ego_bspline_gate_20260619_025648/REAL_EGO_BSPLINE_GATE.json`: planner cloud recorder finite points `4187`, `/grid_map/occupancy_inflate` width `8280`, occupancy inflate recorder finite points `8237`, `/planning/bspline` sampled, `final_plan_success_true=true`, raw Gazebo LiDAR rate about `9.95Hz`, planner cloud rate about `3.38Hz`, and EGO occupancy/inflate rate about `9.94Hz`. Remaining blockers are bounded and explicit: `single_uav_hover_hold_gate_20260619_024608` failed only by a narrow evaluation-window edge (`1.053042>1.050000`, `0.146958<0.150000`); `single_uav_mworks_replay_gate_20260619_024817` proves ControllerOutput replay transport but the selected old MWORKS CSV does not produce useful Gazebo z response (`0.004302<0.020000`). Current status is `review_required`: tomorrow's audit should open Gazebo animation plus two RViz review surfaces for FAST-LIO/trajectory and EGO occupancy/bspline. Do not claim final MWORKS-controller deployment, final competition controller performance, final closed_loop, UE acceptance, or multi-UAV readiness from these gates.
latest formal MWORKS/AWFF-to-PX4/Gazebo deployment correction, 2026-06-20: the active priority is no longer point-cloud/EGO exploration, Python behavior-equivalent runtime work, or ROS2-direct-to-Gazebo motor control. The formal target follows the normal PX4/Gazebo/Simulink-style flow: `MWORKS Sysblock -> GenerateModelCode -> generated C/C++ -> SIL -> PX4 Offboard adapter or PX4 module/uORB adapter -> PX4 SITL -> Gazebo plant/sensors`. The previous route `Gazebo truth pose -> AWFF_FullControllerEquation behavior-equivalent Python wrapper -> gazebo_ref_adapter -> mosim_msgs/ControllerOutput -> controller_output_to_gazebo_actuators_node.py -> Gazebo sunray150_assembled motor plugins` remains useful only as temporary bridge/reference evidence. A fresh 13s rerun passed at `Results/gazebo_ros2/mworks_awff_formal_deploy_gate_rerun_20260619_001/GAZEBO_TAKEOFF_HOVER_LAND_EVAL.json` with max z `0.656293m`, final z `0.032899m`, settled hover max z error `0.164013m`, max XY `0.328021m`, and max airborne tilt `0.068927rad`. The AWFF GUI long-hover review run passed at `Results/gazebo_ros2/mworks_awff_takeoff_hover_land_animation_review_long_hover_20260619_live_001/GAZEBO_TAKEOFF_HOVER_LAND_EVAL.json` with duration `69.02s`, max XY `0.201183m`, max airborne tilt `0.02211rad`, final z `0.035997m`, adapter publishes `1144`, and camera-follow request `published` at `gazebo_camera_follow_request.json`. Gazebo still reports an OGRE shutdown segmentation fault on teardown; record that as GUI teardown/rendering risk, not as a control failure. This Python bridge is not generated C/C++ deployment, not PX4 integration, not full SIL equivalence, and not final competition controller performance. Formal codegen target correction: `AWFF_FullControllerEquation_Sysblock` is blocked for Sysblock code generation because `CheckModel` reports unsupported `der()` use; the active generated-code target is `QuadrotorControllerBlocks.AWFF_FullController_Sysblock`. Gates A/B/C and the first Gate D SIL slice now have evidence under `Results/generated_mworks/AWFF_FullController_Sysblock_20260620_032747/`: generated code, WSL gcc C99 compile, 8-input/4-output `runtime_schema.json`, runtime schema smoke, real MWORKS nonzero constant-input reference, and `sil_constant_input_check.json` with max_abs_error about `1.23e-8` under tolerance `1e-5`. Fresh PX4-native continuation evidence is now the stable single-UAV baseline: `Results/px4_gazebo/night_continuation_takeoff_hover_land_20260620_090113/PX4_OFFBOARD_TAKEOFF_HOVER_LAND.json` passed with hover z RMSE `0.063863m`, hover XY max `0.028142m`, hover vxy max `0.023381m/s`, post-land XY span `0.028004m`, and no failsafe; `Results/px4_gazebo/night_continuation_figure8_gate_20260620_090302/PX4_OFFBOARD_FIGURE8_GATE.json` passed with figure-8 XY RMSE `0.215951m`, max XY error `0.515443m`, z RMSE `0.008580m`, actual span `5.243365m x 2.959799m`, center crossings `3`, post-land XY span `0.060074m`, and no failsafe. The matching generated AWFF C shadow gate at `Results/px4_gazebo/night_continuation_figure8_gate_20260620_090302/mworks_awff_codegen_shadow/MWORKS_AWFF_CODEGEN_SHADOW_GATE.json` passed as `passed_position_loop_shadow`, with `928` matched shadow inputs and `position_loop_pitch_roll_thrust` marked candidate-ready; root outputs `y/y1/y2/y3` remain not L1 setpoint-ready. The next work is `targeted checks -> formal L1 TrajectorySetpoint or L2 PX4 module/uORB adapter design/implementation -> real Gazebo LiDAR/FAST-LIO/local-map EGO-to-PX4 upgrade -> full obstacle-map EGO validation -> UE truth-map export later`; do not revert to old MWORKS CSV replay, truth-feedback-only claims, EGO/FAST-LIO-only demos, ROS2-direct actuator control, rejected PX4 attitude shortcut tuning, or static visual evidence as the main proof route.
```

Historical override note, 2026-06-20 evening: after the old ROS2/PX4/x500 route was
incorrectly used as an equivalent substitute, the current executable review
lane is narrowed to `Docs/Workflows/sunray_ros1_current_runtime_lane.md`.
Single-thread execution for Sunray takeoff-hover-land, 8字, Gazebo Classic
animation, RViz trajectory/path, and MID360 point-cloud review must use
Ubuntu-20.04 / ROS1 Noetic / `References/Sunray` / `References/Lab/FAST_LIO`
as documented there. Historical ROS2/PX4/Gazebo evidence in this board remains
audit context only unless PMO/user explicitly reopens that route.

Historical authorization note, 2026-06-17: this applied to the then-active
Gazebo/ROS2 single-thread goal. It is not permission to leave the current
Sunray ROS1 lane.

2026-06-15 historical single-thread Gazebo/ROS2 increment:

```text
gate: bounded_ego_style_planner_output_without_actuation
status: passed
runtime evidence: Results/gazebo_ros2/sunray150_gazebo_ros2_ego_style_planner_output_without_actuation_20260615_005/RUNTIME_STATUS.json
planner gate evidence: Results/gazebo_ros2/sunray150_gazebo_ros2_ego_style_planner_output_without_actuation_20260615_005/EGO_STYLE_PLANNER_OUTPUT_GATE.json
same-run inputs: /mosim/planner/odom, /mosim/planner/global_points
published outputs: /position_cmd, /mosim/planner/position_cmd, /mosim/planner/setpoint, /mosim/planner/setpoint_adapter_status
counts: odom=2128, global_points=1713, position_cmd=900, mosim_position_cmd=900
measured command rate: about 4.999Hz
cloud frame: map
cloud shape: width=360, height=32
cloud finite bounds: x=[-8.132, 8.016], y=[-9.013, 8.083], z=[0.948, 2.905]
forbidden controller/actuator topics: absent
```

This gate proved only a same-run planner output and setpoint-surface
publication path in the old route. It did not prove `planner_ready`,
trajectory tracking, controller output, actuator command, final closed-loop
acceptance, competition controller performance, or multi-UAV readiness. Do not
continue from this historical "next slice" while the current board selects
Sunray ROS1.

### Paused UE Execution Pointer

This pointer is not the current Sunray ROS1 execution lane. Use it only if the
PMO/user explicitly reopens UE visual-review or command-echo work.

Current UE next-slice plan:

```text
Results/ue_replay_input/20260612_rotor1_loss15_linear_mpc_online_fault_allocation/ue_review_path_20260612_001/next_execution_plan.json
```

The preferred next executable slice is UE visual-review hardening with the
Factory follow-camera route, because the existing screenshot proves a nonblank
Factory scene but not a human-visible Sunray150 body. Command-echo live probe
remains the second slice unless PMO/user explicitly prioritizes it first; it
must produce the seven required artifacts and pass the existing validator.

## 6. Support Lanes

| Lane | State | Rule |
|---|---|---|
| Sunray/PBR | frozen_by_user | Do not dispatch material/PBR/DAE visual changes unless the user explicitly reopens the lane. |
| Open-source probe/learning | support_only | Use only for a concrete source-first question; it cannot substitute for idle P0 engineering dispatch. |
| 文档秘书部 | support_only | Use for consistency review, context maintenance, and cleanup; it does not define PMO runtime rules. |
| DH TDMS goal thread | support_only | Refresh-only watch target `019de24d-e993-72c0-a0b2-caf2ac8ac85e` after Codex App/PC restart so its active goal can resume; not a MoSim dispatchable department. |

## 7. Current Board Maintenance Rules

- PMO updates this board when accepting a return, recording a blocker, changing
  the next dispatch, or after a CoAgentOps patrol changes a P0 state.
- CoAgentOps must directly dispatch routable idle P0 work when every
  bounded-dispatch gate in `coagent_ops_patrol_workflow.md` is satisfied. If
  any gate is missing, it reports `dispatch_needed` with the missing
  precondition. PMO decides acceptance, priority changes, narrowing,
  supersede, and any dispatch that needs product/user judgment.
- CoAgentOps may update only the fixed operating areas needed for patrol:
  P0 partition state, Dispatch SLO watchlist, Ops/recovery state, and Support
  lane state. It must not change product priority, accept/reject conclusions,
  or final integration judgments.
- Historical detail belongs in `Docs/Workflows/agent_task_ledger.md` and
  `Results/agent_packets/`, not in this board.
- Packet paths remain the durable evidence; this board is the short operating
  index that points to them.
- Dispatch SLO details belong in
  `Results/agent_packets/dispatch_tickets/<request_id>.json`. This board only
  displays `sent_at`, `first_readback_due`, `expected_packet_due`,
  `last_observed_turn`, `breach_action`, and `owner` for active dispatch
  monitoring.
- The dispatcher that sends a visible-thread task owns the dispatch ticket
  until terminal closure. A row with a visible turn stuck in progress/thinking
  but no agent output, checkpoint, final response, expected packet, blocker,
  approval/provider surface, or context-compression surface is not healthy
  progress and must breach through the ticket workflow.
- This board and the return packet
  `Results/agent_packets/returns/PMO-MAINLINE-OPERATIONS-BOARD-ARCHITECTURE-20260608-001.json`
  are the durable evidence for the PMO operating-architecture update.
- Current Git lock or staged `References/` warnings are unrelated Git/reference
  intake blockers. They do not block this control-plane board/packet delivery
  unless the exact board or packet paths are locked, staged-conflicted, or fail
  their targeted checks.
