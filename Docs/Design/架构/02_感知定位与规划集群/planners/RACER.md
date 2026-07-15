# RACER

Status: RACER-D4 REVIEW READY / primary multi-UAV autonomous exploration
baseline.

Source: `References/Lab/exploration_coverage/RACER`.

Related local fork/reference: `References/Lab/exploration_coverage/fast_multi_robot_exploration`
extends the RACER-style stack for decentralized forest exploration and adds
planner selection, logging and scripted experiment support.

Upstream role: decentralized collaborative exploration by multiple UAVs with
asynchronous/limited communication, workload allocation, shared map chunks and
swarm-aware B-spline optimization.

## Upstream Interface

Observed local source entry:

```text
References/Lab/exploration_coverage/RACER/README.md
References/Lab/exploration_coverage/RACER/swarm_exploration/exploration_manager/launch/swarm_exploration.launch
References/Lab/exploration_coverage/RACER/swarm_exploration/exploration_manager/launch/single_drone_exploration.xml
References/Lab/exploration_coverage/RACER/swarm_exploration/exploration_manager/launch/single_drone_planner.xml
References/Lab/exploration_coverage/fast_multi_robot_exploration/swarm_exploration/exploration_manager/launch/swarm_exploration.launch
```

Default upstream inputs:

```text
odom_prefix: /state_ukf/odom in RACER demo
per-drone odom: $(odom_prefix)_$(drone_id) in single_drone_exploration.xml
sensor_pose_topic: /pcl_render_node/sensor_pose_$(drone_id)
depth_topic: /pcl_render_node/depth_$(drone_id)
cloud_topic: /pcl_render_node/cloud_$(drone_id)
manual start: RViz 2D Nav Goal in upstream demo
environment source in demo: map_generator .pcd resource for the simulator
```

Important upstream shared topics:

```text
/swarm_expl/drone_state
/swarm_expl/pair_opt
/swarm_expl/pair_opt_res
/swarm_expl/grid_tour
/swarm_expl/hgrid
/multi_map_manager/chunk_stamps
/multi_map_manager/chunk_data
/planning/swarm_traj
```

Default upstream outputs:

```text
/planning/bspline_$(drone_id)
planning/pos_cmd_$(drone_id)
planning/position_cmd_vis_$(drone_id)
planning/travel_traj_$(drone_id)
/sdf_map/occupancy_all_$(drone_id)
/sdf_map/occupancy_local_$(drone_id)
/planning_vis/frontier_$(drone_id)
/planning_vis/trajectory_$(drone_id)
```

Key parameters seen in upstream launch:

```text
sdf_map/resolution: 0.1
sdf_map/obstacles_inflation: 0.199
sdf_map/box_min_z: 0.0
sdf_map/box_max_z: 1.7 in RACER single_drone_planner.xml
fsm/replan_time: 0.200
fsm/sync_interval: 0.200
exploration/drone_num and exploration/drone_id
optimization/ld_swarm: 5.0
optimization/swarm_safe_dist: 1.0
manager/max_vel: 1.5 m/s
manager/max_acc: 1.0 m/s
```

Dependencies noted by upstream docs:

```text
ROS Melodic/Noetic
NLopt 2.7.1
libarmadillo-dev
LKH-3
```

Current D0 evidence:

```text
Results/sunray_ros1/racer_d0_source_audit_20260701_075800/
  RACER_D0_SOURCE_AUDIT.json
  SUMMARY.md
status: review_ready
scope: source/interface/dependency audit only
inventory: 69 launch/xml files, 39 msg files, 2 srv files, 26 package.xml files
claim boundary: no ROS/Gazebo/PX4/MAVROS/RViz runtime started; no build,
  smoke, adapter dry-run or multi-UAV exploration success claimed.
```

Current D1 evidence:

```text
Results/sunray_ros1/racer_d1_build_optimized_20260701_084307/
  RACER_D1_BUILD_AUDIT.json
  SUMMARY.md
status: review_ready
workspace:
  Results/sunray_ros1/workspaces/racer_ws_d1_optimized_20260701_084307/
scope: isolated ROS1/Noetic planner-side build and launch-parse only
key executables:
  exploration_manager/exploration_node
  exploration_manager/ground_node
  plan_manage/traj_server
  lkh_tsp_solver/tsp_node
  lkh_mtsp_solver/mtsp_node
  map_generator/map_pub
launch parse:
  single_drone_exploration.xml -> exploration/tsp/acvrp/traj/map_pub nodes
  swarm_exploration_2.launch -> two-UAV exploration/tsp/acvrp/traj nodes
claim boundary: no upstream runtime smoke, no Gazebo/PX4/MAVROS/RViz, no
  three-UAV MoSim exploration success.
warning: /usr/local/bin/LKH is missing; runtime TSP/MTSP service gates must
  install or configure LKH before acceptance.
```

Current D2 evidence:

```text
primary:
  Results/sunray_ros1/racer_d2_adapter_dry_run_repeat_20260701_103254/
    RUN_MANIFEST.json
    racer_d2_stimulus_summary.json
    SUMMARY.md
  status: review_ready
  scope: MoSim namespace adapter dry-run only
  claim boundary: no Gazebo/PX4/MAVROS/RViz and no exploration-success claim

stability support:
  Results/sunray_ros1/racer_d2_adapter_dry_run_20260701_103220/
    RUN_MANIFEST.json
    racer_d2_stimulus_summary.json
    SUMMARY.md

repeat-pass checks:
  input_ok.uav1/uav2/uav3=true
  per_uav_outputs_ok.uav1/uav2/uav3=true
  forbidden_topics=[]
  shared_core_ok=true
  per-UAV B-spline count=1/1/1
  per-UAV pos_cmd count=10/10/10
  shared topics include /swarm_expl/drone_state, /planning/swarm_traj,
    /multi_map_manager/chunk_stamps and /multi_map_manager/chunk_data
```

D2 used two default-off switches only for the adapter proof:

```text
partitioning/mosim_d2_round_robin_init=true
fsm/mosim_d2_disable_pair_opt=true
```

Rationale: upstream RACER initially gives relevant level-1 grids only to
`drone_id == 1`; on the compact synthetic D2 map, pair optimization/ACVRP was
nondeterministic and could leave other UAVs with empty dominance. D2 enables a
deterministic initial grid split and disables pair optimization only to prove
namespace, mapping input and planner-output contracts before Gazebo.

Current D3 evidence:

```text
primary:
  Results/sunray_ros1/racer_d3_pair_opt_enabled_30s_cutofffix_20260701_161557/
    RUN_MANIFEST.json
    EGO_SWARM_METRICS.json
    planner_runtime_log_audit.json
    STARTUP_ATTEMPT_SUMMARY.json
    SUMMARY.md
  status: passed
  scope: three-UAV Gazebo/Sunray/PX4/MAVROS runtime, log and metrics proof
  mission_completion_mode: exploration
  mission_exit_code: 0
  min_inter_uav_distance_m: 1.2665096729442211
  safe-distance gate: 1.2 m
  claim boundary: not full-map completion and not RViz manual visual acceptance

runtime/log checks:
  uav1/uav2/uav3 MAVROS state, odom and raw lidar all received
  Gazebo Livox marker count=3
  runtime audit status=passed
  fatal_event_count=0
  semantic blockers=[]
```

D3 kept `round_robin_init=true`, enabled pair optimization
(`disable_pair_opt=false`), and delayed pair optimization until after planner
trigger (`pair_opt_after_trigger_only=true`). RACER pair-optimization candidate
rejections are retained as diagnostics. ACVRP failures remain hard blockers
during the active mission window; after mission done/shutdown they are retained
as diagnostics only.

Current D4 evidence:

```text
primary:
  Results/sunray_ros1/racer_d4_evaluation_20260701_163532/
    RACER_D4_EVALUATION.json
    SUMMARY.md
    figures/racer_d4_xy_paths.png
    figures/racer_d4_altitude.png
    figures/racer_d4_inter_uav_separation.png
    figures/racer_d4_workload_proxy.png
  status: review_ready
  source_result_dir:
    Results/sunray_ros1/racer_d3_pair_opt_enabled_30s_cutofffix_20260701_161557/
  min_inter_uav_distance_m: 1.2665096729442211
  occupancy_last_points_sum: 11663
  frontier_topic_count_sum: 6498
  world_cloud_message_count_sum: 2326
  trajectory_xy_area_proxy_m2: 79.401889148319
  execute_path_length_cv: 0.08093620147050037
  frontier_count_cv: 0.04832158056458077
```

D4 is an offline evaluation package for one completed D3 run. Coverage is a
proxy from recorded occupancy/frontier/world-cloud counts and flight envelope;
revisit/overlap is a planner-log proxy from rediscovered grids and
cluster-covered replans. It is not a full-map completion proof.

Current clean-Factory single-UAV smoke evidence:

```text
primary:
  Results/sunray_ros1/factory_l2_racer_single_rawdiag_smoke_20260703_120555/
    EGO_SINGLE_METRICS.json
    RUN_MANIFEST.json
    ego_single_px4ctrl_goal4.log
    pointcloud_to_world_stats.json
    racer_local_cloud_bridge.json
    racer_position_cmd_compat_bridge.json
  status: passed
  mission_mode: exploration_stream
  blockers: []
  raw_lidar: 617
  world_cloud: 582
  frontier: 883
  trajectory_vis: 46
  bspline: 23
  planner_position_cmd: 1891
  position_cmd: 920
  landed_by_truth: true
  flight_safety_violation: null
```

This smoke proves the single-UAV RACER path on the clean Factory L2 scene:
online MID360-derived cloud enters the world-cloud bridge, RACER receives the
local-frame cloud/odom bridge, frontier and trajectory visualization markers
are observed, B-splines and planner position commands stream, `/position_cmd`
is forwarded through the MoSim safety adapter to px4ctrl, and the vehicle
takes off, explores for a bounded 15 s window, and lands. It is not a full-map
coverage proof and does not use fixed-goal target error as the acceptance
metric. Raw planner command continuity remains a diagnostic stream; the hard
control-input continuity gate is `/position_cmd` after the safety adapter.

## MoSim Integration Boundary

RACER is the preferred first multi-UAV autonomous exploration route after
FUEL-D3/D4 succeeds. It must be connected through per-UAV MoSim adapters:

```text
uav1/uav2/uav3 state source
  -> RACER odom_1/odom_2/odom_3 equivalent remaps
uav1/uav2/uav3 point cloud or depth-equivalent source
  -> RACER cloud_1/cloud_2/cloud_3 or depth_1/depth_2/depth_3
RACER B-spline / pos_cmd_i
  -> per-UAV Planner Adapter
  -> per-UAV Trajectory Server
  -> per-UAV px4ctrl / generated controller
  -> per-UAV MAVROS / PX4 / Gazebo
```

RACER may own exploration target assignment, map sharing and candidate
trajectory generation. It must not own final control publication. Multi-UAV
state, map, trajectory and log topics must stay namespace-isolated enough to
prove which UAV produced each result.

D0 confirmed the following adapter requirements:

```text
1. Use uav1/uav2/uav3 only for the first MoSim gate, overriding upstream
   swarm_exploration.launch default drone_num=5.
2. Feed RACER odometry with per-UAV MoSim state topics equivalent to
   odom_1/odom_2/odom_3.
3. Feed RACER mapping with sensor pose plus either cloud or depth. Cloud alone
   is insufficient because MapROS synchronizes /map_ros/cloud with
   /map_ros/pose.
4. Keep /swarm_expl/* and /multi_map_manager/* as shared RACER communication
   channels, but verify self-message filtering and per-UAV output isolation in
   D2.
5. Treat RACER /planning/bspline_i and planning/pos_cmd_i as planner outputs.
   Any bridge to px4ctrl/MAVROS must remain MoSim-owned, reversible and logged.
```

The `fast_multi_robot_exploration` reference is useful when the task is
forest exploration, larger team sizes, automatic run/evaluation scripts, or a
comparison between `fame` and `racer` style planners. It should not replace the
RACER source review unless its topic and map contracts are explicitly adopted.

## Suggested Gate Sequence

```text
RACER-D0 source audit:
  read README, swarm_exploration launch, shared communication topics,
  per-drone namespace rules and map/log outputs
  status: complete/review_ready at
  Results/sunray_ros1/racer_d0_source_audit_20260701_075800/

RACER-D1 isolated upstream build / launch parse:
  status: complete/review_ready at
  Results/sunray_ros1/racer_d1_build_optimized_20260701_084307/
  This gate copied selected RACER packages into an isolated workspace, patched
  the local NLopt path, enabled tsp_node, created TSP/MTSP resource dirs, built
  key libraries/executables, and proved selected launch files parse. It remains
  source/build/launch-parse proof only. No runtime smoke was accepted because
  /usr/local/bin/LKH is missing and D1 does not start services.

RACER-D2 MoSim namespace adapter:
  status: complete/review_ready at
  Results/sunray_ros1/racer_d2_adapter_dry_run_repeat_20260701_103254/
  This gate maps uav1/uav2/uav3 state, sensor pose and cloud topics into RACER
  without direct MAVROS output; it verifies per-UAV B-spline and pos_cmd
  topics, shared swarm/map topic health, and no publication to forbidden final
  control channels. It remains dry-run proof only.

RACER-D3 three-UAV Gazebo proof:
  status: complete/passed at
  Results/sunray_ros1/racer_d3_pair_opt_enabled_30s_cutofffix_20260701_161557/
  This gate proves uav1/uav2/uav3 simultaneous bounded exploration command
  streaming in Gazebo/Sunray/PX4/MAVROS, online sensor input, per-UAV Planner
  Adapter and Trajectory Server, landing, and min inter-UAV distance safety
  for the recorded run. It does not prove full-map completion or RViz visual
  acceptance.

RACER-D4 evaluation:
  status: complete/review_ready at
  Results/sunray_ros1/racer_d4_evaluation_20260701_163532/
  This gate reports coverage/map proxies, revisit/overlap proxy, workload
  balance, min inter-UAV distance, per-UAV tracking metrics, topic evidence and
  review figures. Optional RViz screenshots are still separate visual-review
  evidence if requested.

RACER-F5c single-UAV clean-Factory smoke:
  status: complete/passed at
  Results/sunray_ros1/factory_l2_racer_single_rawdiag_smoke_20260703_120555/
  This gate proves one UAV can run RACER autonomous exploration on the clean
  Factory L2 Gazebo scene through Sunray/PX4/MAVROS/px4ctrl with online sensor
  input, MoSim frame bridges, planner visualization evidence, command-stream
  evidence and landing. It is a bounded smoke, not a full Factory coverage
  claim.
```

## Forbidden Claims

```text
RACER source review or upstream demo is not MoSim multi-UAV Gazebo proof.
RACER success is not fixed-formation control or Swarm-Formation success.
RACER must not use Gazebo truth, UE truth or a full static map as planner input
unless the run is explicitly marked oracle/debug-only.
The Diff-Planner scripted-goal swarm baseline is not autonomous exploration;
RACER evidence must use exploration/coverage metrics, not only target error.
```
