# Swarm-Formation

Status: IMPLEMENTATION CANDIDATE / later formation and cluster-planning route,
not autonomous exploration.

Source: `References/Lab/swarm_coordination/Swarm-Formation`.

Upstream role: distributed swarm trajectory optimization for formation flight
in dense environments. It optimizes formation similarity, obstacle avoidance
and dynamic feasibility. It is related to EGO-Swarm and GCOPTER/MINCO-style
trajectory optimization.

## Upstream Interface

Observed local source entry:

```text
References/Lab/swarm_coordination/Swarm-Formation/README.md
References/Lab/swarm_coordination/Swarm-Formation/src/planner/plan_manage/launch/normal_hexagon.launch
References/Lab/swarm_coordination/Swarm-Formation/src/planner/plan_manage/launch/run_in_sim.launch
References/Lab/swarm_coordination/Swarm-Formation/src/planner/plan_manage/config/normal_hexagon.yaml
References/Lab/swarm_coordination/Swarm-Formation/src/planner/swarm_bridge/launch/bridge.launch
```

Default upstream inputs:

```text
odom_topic: visual_slam/odom in normal_hexagon.launch
map: random_forest / mockamap generated map
goal input: flight_type 2 global waypoints or flight_type 3 RViz 2D Nav Goal
formation_type: launch/profile parameter
swarm bridge: broadcast_ip based bridge.launch
```

Default upstream outputs:

```text
drone_$(drone_id)_planning/pos_cmd
drone_$(drone_id)_planning/trajectory
drone_$(drone_id)_planning/start
drone_$(drone_id)_planning/finish
traj_utils/PolyTraj and related visualization / assignment messages
```

Key upstream constraints:

```text
the quick-start demo uses seven drones in a normal hexagon-like setup
the run_in_sim.launch trajectory server publishes per-drone pos_cmd
the upstream simulator is not MoSim's PX4/MAVROS/Sunray runtime
```

## MoSim Integration Boundary

Swarm-Formation should be opened after the project already has:

```text
Diff-Planner three-UAV known-goal baseline
FUEL single-UAV exploration or an equivalent map/exploration proof
RACER three-UAV exploration or an equivalent multi-UAV coordination proof
```

It belongs to the formation/cluster-planning layer, not the exploration layer:

```text
formation or cluster task profile
  -> Swarm-Formation trajectory optimization
  -> per-UAV Planner Adapter
  -> per-UAV Trajectory Server
  -> per-UAV controller / MAVROS / PX4 / Gazebo
```

The formation layer may set target shape, relative geometry, formation
similarity cost, obstacle clearance and inter-UAV clearance. It must not replace
per-UAV state estimation, controller ownership, MAVROS/PX4 control authority or
Gazebo/Sunray plant evidence.

## Suggested Gate Sequence

```text
SF-D0 source audit:
  read normal_hexagon launch, config, swarm_bridge, topic and message contracts
  current status: review_ready
  evidence: Results/sunray_ros1/swarm_formation_d0_source_audit_20260701_164457/

SF-D1 isolated upstream smoke:
  run upstream normal_hexagon demo and record expected formation metrics and
  topic graph
  current status: review_ready
  evidence: Results/sunray_ros1/swarm_formation_d1_upstream_smoke_20260701_175452/

SF-D2 MoSim adapter dry-run:
  remap three MoSim UAV states and produce per-UAV trajectory references
  without sending MAVROS commands
  current status: review_ready
  evidence: Results/sunray_ros1/swarm_formation_d2_adapter_dry_run_20260701_183500/

SF-D3 three-UAV Gazebo proof:
  run a small known-goal formation transition in Sunray/PX4/MAVROS with
  per-UAV trajectory servers and current controller baseline
  current status: blocked
  latest evidence:
    Results/sunray_ros1/factory_l2_swarm_formation_obstacle_runtime_r10_20260716/
  current interpretation:
    Swarm-Formation is not accepted as a Gazebo/PX4/MAVROS formation-flight
    baseline. In r10 all three planners produced commands, minimum inter-UAV
    distance was 1.3227 m, and no emergency hold fired. The mission still failed:
    formation RMSE was 3.7901 m and peak error was 8.7465 m because UAV3 did not
    follow UAV1/UAV2 through the obstacle corridor.
  latest source fix:
    The one-segment MinJerk initialization boundary in
    `poly_traj_optimizer.cpp` now inserts the midpoint into `simple_path`
    before setting `piece_num=2` and clamps segment durations to at least
    0.10 s. This prevents the previous simple_path[2]/Eigen assertion crash,
    but does not by itself prove SF-D3 success. The Factory pass also adds the
    three-UAV triangle definition, peer-readiness gating, near-body occupancy
    filtering, and member-corridor scenario audit. r10 exposed a separate source
    defect: collision recovery called `planFromLocalTraj(true, false)` and
    disabled formation optimization after the first trajectory. It now calls
    `planFromLocalTraj(true, true)`; the optimizer retains its peer-readiness
    fallback. The corrected source builds and targeted tests pass. A five-minute
    r11 smoke was stopped before trajectory execution, so runtime acceptance is
    still pending and must not be inferred from the source/build result.

SF-D4 expanded formation proof:
  current status: blocked/frozen for this pass
  evidence:
    Results/sunray_ros1/swarm_formation_d4_blocker_20260701_2310/
  reopen only after repeatable three-UAV MID360 startup and safe SF-D3
  target-hold execution are proven.
```

## Current Evidence

```text
SF-D0:
  Results/sunray_ros1/swarm_formation_d0_source_audit_20260701_164457/
  status=review_ready.
  This proves source/launch/topic/message/config audit only.

SF-D1:
  Results/sunray_ros1/swarm_formation_d1_upstream_smoke_20260701_175452/
  status=review_ready.
  Required ROS1 packages and executables are present in the isolated workspace.
  normal_hexagon.launch resolves 37 nodes.
  run_in_sim.launch resolves 5 nodes.
  This is build/launch-parse evidence only; it is not Gazebo/PX4/MAVROS proof.

SF-D2:
  Results/sunray_ros1/swarm_formation_d2_adapter_dry_run_20260701_183500/
  status=review_ready.
  The dry-run starts only /drone_0..2 ego_planner_node and traj_server nodes.
  It maps MoSim user-facing uav1/uav2/uav3 to upstream drone_0/drone_1/drone_2,
  publishes MoSim-like odom/cloud inputs, sends one central formation goal, and
  verifies per-drone trajectory or pos_cmd outputs without publishing any
  MAVROS/PX4 command topics. Summary evidence: input_ok=true for all three
  drones, per_drone_outputs_ok=true for all three drones, broadcast_ok=true,
  forbidden_topics=[], and per-UAV outputs drone_0 trajectory=1 pos_cmd=65,
  drone_1 trajectory=1 pos_cmd=39, drone_2 trajectory=1 pos_cmd=8.
  This is adapter dry-run evidence only; it is not Gazebo/PX4/MAVROS/RViz
  formation-flight proof.

SF-D3:
  Results/sunray_ros1/factory_l2_swarm_formation_obstacle_runtime_r10_20260716/
  status=blocked.
  Historical July 1 evidence remains below. The current Factory mission-level
  run is r10: backend status=blocked, minimum inter-UAV distance=1.3227 m,
  emergency holds=0, formation RMSE=3.7901 m, and formation peak error=8.7465 m.
  The current source fix is build/test evidence only. The earlier strongest run was
  Results/sunray_ros1/sunray_ros1_goal5_swarm_formation_3uav_20260701_codex_sf_d3_scale100/:
  planner_runtime_log_audit.status=passed, fatal_event_count=0,
  planner_broadcast_traj_relay.per_drone={0:2,1:4,2:4}, but
  mission_exit_code=13, min_inter_uav_distance_m=0.2460, uav2 does not reach
  target hold, and uav2 violates execute Z/roll-pitch gates. The latest
  sequential-spawn shifted-geometry run is
  Results/sunray_ros1/sunray_ros1_goal5_swarm_formation_3uav_20260701_codex_sf_d3_seq_centery_m2_scale100/:
  both startup attempts exit 7 because uav2 /livox/lidar does not publish a
  first frame; no EGO_SWARM_METRICS.json or RUN_MANIFEST.json is produced.
```

## Required Metrics

```text
per-UAV tracking error
formation-shape error
minimum inter-UAV distance
minimum obstacle clearance
goal/formation completion
replan count and failed optimization count
runtime CPU/load if team size grows
RViz trajectory, body-axis and map evidence
```

## Forbidden Claims

```text
Swarm-Formation is not autonomous exploration.
Swarm-Formation upstream simulator success is not MoSim Gazebo/PX4 proof.
Diff-Planner swarm success is not Swarm-Formation success.
Swarm-Formation must not directly publish final MAVROS/PX4 control commands.
```
