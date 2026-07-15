# FUEL

Status: FUEL-D4 REVIEW READY / single-UAV autonomous exploration baseline.

Source: `References/Lab/exploration_coverage/FUEL`.

Upstream role: fast single-UAV unknown-environment exploration using an
incremental frontier information structure, hierarchical frontier/viewpoint
planning, and minimum-time B-spline trajectory generation.

## Upstream Interface

Observed local source entry:

```text
References/Lab/exploration_coverage/FUEL/README.md
References/Lab/exploration_coverage/FUEL/fuel_planner/exploration_manager/launch/exploration.launch
References/Lab/exploration_coverage/FUEL/fuel_planner/exploration_manager/launch/algorithm.xml
References/Lab/exploration_coverage/FUEL/fuel_planner/plan_manage/launch/kino_replan.launch
```

Default upstream inputs:

```text
odometry_topic: /state_ukf/odom
sensor_pose_topic: /pcl_render_node/sensor_pose
depth_topic: /pcl_render_node/depth
cloud_topic: /pcl_render_node/cloud
manual start: /move_base_simple/goal through RViz 2D Nav Goal
environment source in demo: map_generator .pcd resource for the simulator
```

Default upstream outputs:

```text
planning/pos_cmd
/planning/bspline or planner internal trajectory messages
frontier, viewpoint, trajectory and occupancy visualization topics
```

Key parameters seen in upstream launch:

```text
sdf_map/resolution: 0.1
sdf_map/obstacles_inflation: 0.199
sdf_map/local_map_margin: 50
sdf_map/max_ray_length: 4.5
fsm/replan_time: 0.200
manager/max_vel: launch arg, default 2.0 m/s in exploration.launch
manager/max_acc: launch arg, default 2.0 m/s in exploration.launch
manager/max_jerk: 4
```

Dependencies noted by upstream docs:

```text
ROS Melodic/Noetic
NLopt 2.7.1
libarmadillo-dev
LKH for TSP
```

## Current Local Build Evidence

FUEL-D1 planner-only build is passed for the current ROS1/Noetic lane.

```text
preflight:
  NLOPT_ROOT=/mnt/c/Users/HP/Desktop/MoSim/Results/sunray_ros1/workspaces/fuel_deps/install/nlopt-v2.7.1
  bash Scripts/sunray/check_fuel_ros1_preflight.sh --strict-build
  result: FUEL_ROS1_PREFLIGHT=PASS

local NLopt:
  Results/sunray_ros1/workspaces/fuel_deps/install/nlopt-v2.7.1

build workspace:
  /opt/mosim_work/sunray_ws/fuel_ws_planner_only_debug_20260701_003

build command:
  FUEL_BUILD_SCOPE=planner_only
  FUEL_BUILD_TYPE=Debug
  FUEL_BUILD_JOBS=2
  FUEL_BUILD_TEST_TOOLS=OFF
  bash Scripts/sunray/build_fuel_ros1_upstream_smoke.sh

build log:
  Results/sunray_ros1/workspaces/fuel_ws_planner_only_native_20260701_003/build_fuel_planner_only_native_final2.log

result:
  FUEL_UPSTREAM_BUILD=PASS
  rospack find exploration_manager/lkh_tsp_solver/bspline_opt/plan_manage passed
  devel/lib/exploration_manager/exploration_node executable exists
  devel/lib/plan_manage/traj_server executable exists
```

Scope boundary: this is not a MoSim autonomous-exploration runtime pass. It
proves that the upstream FUEL exploration node and trajectory server can be
built in the current ROS1/Noetic environment with local NLopt. The upstream
`local_sensing_node`, `.pcd` simulator, and full demo launch are optional
diagnostics for source understanding; they are not required before the MoSim
FUEL-D2 adapter dry-run, and they must not become hidden map/sensor authority
for a Gazebo/Sunray/PX4 success claim.

FUEL-D2 adapter dry-run is now passed for the current ROS1/Noetic lane.

```text
runner:
  NLOPT_ROOT=Results/sunray_ros1/workspaces/fuel_deps/install/nlopt-v2.7.1
  bash Scripts/sunray/run_fuel_d2_adapter_dry_run.sh

launch:
  Scripts/sunray/fuel_d2_adapter_dry_run.launch

stimulus/recorder:
  Scripts/sunray/fuel_d2_synthetic_stimulus.py

evidence:
  Results/sunray_ros1/fuel_d2_adapter_dry_run_20260701_053851/
  RUN_MANIFEST.json status=passed
  fuel_d2_stimulus_summary.json status=passed

observed interface:
  input odom:        /mosim/fuel_d2/odom
  input sensor pose: /mosim/fuel_d2/sensor_pose
  input cloud:       /mosim/fuel_d2/cloud
  trigger path:      /waypoint_generator/waypoints
  output bspline:    /planning/bspline, count=1
  observed command:  /mosim/fuel_d2/position_cmd_observed,
                     count_after_bspline=8
  occupancy topics:  /sdf_map/occupancy_local count=13,
                     /sdf_map/occupancy_all count=10
  forbidden topics:  no /mavros, /uav*/mavros, /fmu, setpoint, or actuator
                     command topics in the isolated ROS master

notes:
  The synthetic cloud is a world-frame interface stimulus matching FUEL
  map_ros cloud semantics. It is not Gazebo, MID360, FAST-LIO, or autonomous
  exploration evidence. The FUEL log prints its internal "Total time too long"
  warning during planning, but still publishes the B-spline and observed
  PositionCommand stream.
```

FUEL-D3 single-UAV Gazebo proof is now passed for the current
ROS1/Sunray/PX4/MAVROS/px4ctrl lane.

```text
runner:
  wsl -d Ubuntu-20.04 --exec bash -lc 'cd /mnt/c/Users/HP/Desktop/MoSim && \
    bash Scripts/sunray/check_sunray_ros1_runtime_preflight.sh && \
    NLOPT_ROOT=Results/sunray_ros1/workspaces/fuel_deps/install/nlopt-v2.7.1 \
    PLANNER_VARIANT=fuel TOTAL_TIMEOUT_S=180 FUEL_EXPLORATION_EXECUTE_S=20 \
    FUEL_ALIGN_TRAJ_START_TO_RECEIVE=true \
    FUEL_CMD_SMOOTH_ENABLE=true FUEL_CMD_SMOOTH_MAX_SPEED_MPS=0.6 \
    FUEL_CMD_SMOOTH_MAX_STEP_M=0.02 \
    bash Scripts/sunray/run_px4ctrl_ego_single_gate.sh'

evidence:
  Results/sunray_ros1/sunray_ros1_goal4_ego_single_20260701_072618/
  EGO_SINGLE_METRICS.json status=passed, blockers=[]
  RUN_MANIFEST.json records planner_variant=fuel and mission_mode=exploration_stream

observed runtime:
  bspline count: 5
  raw FUEL planner PositionCommand count: 2320
  px4ctrl-facing /position_cmd count: 1527
  raw LiDAR/world cloud/occupancy counts: 788 / 787 / 22
  last point counts raw/world/occupancy: 9171 / 4150 / 1882
  bounded exploration execution: 20.00 s, then landed_by_truth=true

interface fix retained:
  FUEL traj_server may publish B-splines whose msg->start_time lags receipt
  time. The local FUEL traj_server keeps upstream behavior by default, but
  the MoSim D3 runner enables traj_server/align_start_time_to_receive=true.

  The planner odometry contract is separate from px4ctrl's controller
  contract: `/uav1/mavros/local_position/odom` has `child_frame_id=base_link`,
  so its twist is body-frame under the ROS `nav_msgs/Odometry` convention.
  px4ctrl rotates that twist into world-frame before control. FUEL must receive
  the same world-frame velocity for its P/V/A replan boundary; a position-only
  offset bridge is not sufficient. The FUEL launch therefore enables
  `ros1_coordinate_offset_bridge.py`'s
  `rotate_odom_twist_body_to_world=true` and publishes `child_frame_id=world`.
  This is a frame-contract correction, not a controller gain or trajectory
  smoothing change.

  The recorder stores both callback time and `PositionCommand.header.stamp`.
  Command derivatives must be evaluated on the header timestamp; Python
  callback time can be delayed or sampled twice in one callback under a slow
  Gazebo real-time factor and is diagnostic-only.
  The FUEL command adapter also keeps /fuel/position_cmd_raw observable while
  publishing a smoothed px4ctrl-facing /position_cmd. Current D3 smoothing:
  max speed 0.6 m/s, max step 0.02 m, zero dynamic terms during limiting.

command-continuity evidence:
  raw FUEL command max jump: 0.3085 m, diagnostic gate disabled for raw topic
  px4ctrl-facing command max jump: 0.0530 m
  px4ctrl-facing command max jump speed: 2.4106 m/s
  adapter max published step: 0.0200 m
  adapter max published step speed: 0.6000 m/s

claim boundary:
  D3 proves that live Sunray/Gazebo/PX4/MAVROS/px4ctrl can execute a bounded
  FUEL exploration command stream from online world cloud input and land
  without the prior roll/pitch divergence. D3 alone does not prove coverage
  quality; the current D4 evaluation package below adds coverage/path/safety
  proxies over this same run. Neither D3 nor D4 proves full-map exploration
  completion, RACER multi-UAV exploration, Swarm-Formation, UE map import, or
  QGC UI work.
```

FUEL-D4 evaluation package is now review-ready for the current D3 run.

```text
builder:
  python Scripts/sunray/build_fuel_d4_evaluation_package.py \
    --source Results/sunray_ros1/sunray_ros1_goal4_ego_single_20260701_072618 \
    --output-dir Results/sunray_ros1/fuel_d4_evaluation_20260701_073800

evidence:
  Results/sunray_ros1/fuel_d4_evaluation_20260701_073800/
  FUEL_D4_EVALUATION.json status=review_ready
  SUMMARY.md
  figures/fuel_d4_xy_path.png
  figures/fuel_d4_altitude.png
  figures/fuel_d4_command_tracking_error.png
  figures/fuel_d4_world_cloud_points.png

mission timing:
  configured_execute_duration_s: 20
  measured_execute_wall_duration_s: 20.0022
  truth_exploration_phase_sim_duration_s: 13.5840
  truth_exploration_path_length_m: 4.2924

command and map evidence:
  bspline_count: 5
  raw_fuel_position_cmd_count: 2320
  px4ctrl_facing_position_cmd_count: 1527
  accumulated_review_cloud_voxels: 10777
  accumulated_review_cloud_voxel_volume_proxy_m3: 5.5178
  occupancy_last_points: 1882
  occupancy_voxel_volume_proxy_m3: 3.2521
  world_cloud_envelope_volume_proxy_m3: 303.7683

safety/tracking evidence:
  source_run_status: passed
  source_blockers: []
  landed_by_truth: true
  min_truth_z_explore_m: 1.0267
  max_truth_roll_pitch_explore_deg: 29.7946
  flight_safety_violation: null
  command_to_odom_rmse_xyz_m: 0.1929
  command_to_odom_max_xyz_m: 0.4683

claim boundary:
  D4 is an offline evaluation package over the completed D3 run. Coverage is
  reported as accumulated-cloud voxel, local occupancy, and world-cloud
  envelope proxies, not a formal full-map completion percentage. No Gazebo
  contact-sensor stream is parsed in this package, so absence of crash is
  inferred from mission metrics, safety gates, and successful landing rather
  than direct contact-state evidence. D4 does not prove RACER multi-UAV
  exploration, Swarm-Formation, UE map import, QGC UI, or final competition
  performance.
```

## MoSim Integration Boundary

FUEL can become the first single-UAV autonomous exploration baseline only
through MoSim adapters:

```text
MoSim state source
  -> remap to FUEL odometry_topic
MoSim MID360 / local point cloud / depth-equivalent source
  -> remap to FUEL cloud_topic or depth_topic
FUEL B-spline / pos_cmd
  -> Planner Adapter
  -> MoSim Trajectory Server
  -> px4ctrl / generated controller
  -> MAVROS / PX4 / Gazebo
```

FUEL must not publish final MAVROS control commands. It may publish an
exploration trajectory, B-spline, waypoint, viewpoint, or position-command
reference for the MoSim trajectory layer.

The upstream `.pcd` map generator is acceptable for an isolated upstream smoke
test and for creating repeatable sensor-renderer environments. It is not
acceptable as a hidden global-map input for a MoSim autonomous-exploration
success claim. The MoSim proof run must declare whether a point cloud comes
from live Gazebo/Sunray sensors, a sensor renderer, or an oracle/debug PCD.

FAST-LIO dependency: profile-dependent. If the run uses FAST-LIO state or map
input, it must declare the `state_source_profile`, `sensor_profile`, timestamp
policy, and frame transform. Gazebo truth can only be used for metrics unless a
separate debug/oracle profile says otherwise.

## Suggested Gate Sequence

```text
FUEL-D0 source audit:
  read README, launch, topic remaps, message types and dependency list

FUEL-D1 isolated build/smoke:
  build the local planner-only FUEL workspace and prove exploration_node plus
  traj_server are available without MoSim controller claims. The upstream
  CPU/PCD demo is optional diagnostic evidence, not a required MoSim adapter
  precondition.

FUEL-D2 adapter dry-run:
  remap odom/cloud and record that FUEL produces trajectory or B-spline output
  from MoSim-like topics without sending MAVROS commands. Current D2 evidence
  is passed at
  Results/sunray_ros1/fuel_d2_adapter_dry_run_20260701_053851/.

FUEL-D3 single-UAV Gazebo proof:
  one Sunray UAV, FAST-LIO/current state source, online point cloud, FUEL
  exploration output through Planner Adapter and Trajectory Server. Current D3
  evidence is passed at
  Results/sunray_ros1/sunray_ros1_goal4_ego_single_20260701_072618/.

FUEL-D4 evaluation:
  coverage/explored-volume, mission time, path length, no collision, no
  persistent offboard loss, tracking metrics, RViz map/trajectory/frontier
  screenshots or replay. Current D4 package is review-ready at
  Results/sunray_ros1/fuel_d4_evaluation_20260701_073800/.
```

## Forbidden Claims

```text
FUEL source review is not autonomous exploration success.
The upstream PCD demo is not MoSim Gazebo/PX4/Sunray proof.
FUEL must not bypass Planner Adapter, Trajectory Server, px4ctrl, MAVROS or PX4.
FUEL single-UAV success is not multi-UAV exploration, task allocation, or
formation control.
```
