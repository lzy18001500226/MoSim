# Factory L2 Full System Validation Plan

> Execution plan for moving the accepted Factory L2 scene from static Gazebo
> import into the current ROS1/Sunray/Gazebo/PX4/MAVROS/px4ctrl system, then
> mirroring validated runtime evidence into UE display.

Status: active plan, 2026-07-01 CST.

## 1. Scope

Use this plan when the task is to validate existing MoSim work in the new
Factory environment.

Current historical scene base used by the first Factory F1-F8 runs:

```text
scene_profile: Config/gazebo/scene_profiles/factory_l2_static_sunray_scene.json
world: Results/unreal_scene_mapping/factory_l2_static_import/gazebo_review/worlds/factoryenvironmentcollect_l2_static_review.sdf
models: Results/unreal_scene_mapping/factory_l2_static_import/gazebo_review/models
static_review: Results/unreal_scene_mapping/factory_l2_static_import/gazebo_review/
```

Coordinate-clean candidate after the 2026-07-02 static-import cleanup:

```text
scene_profile: Config/gazebo/scene_profiles/factory_l2_static_sunray_scene_clean_candidate.json
world: Results/unreal_scene_mapping/factory_l2_static_import/gazebo_review_clean/worlds/factoryenvironmentcollect_l2_static_review_clean.sdf
models: Results/unreal_scene_mapping/factory_l2_static_import/gazebo_review_clean/models
coordinate_audit: Results/unreal_scene_mapping/factory_l2_coordinate_audit_20260702_104942/FACTORY_L2_COORDINATE_AUDIT.json
anchor_points: Results/unreal_scene_mapping/factory_l2_coordinate_audit_20260702_104942/factory_l2_anchor_points.csv
status: coordinate_audit_passed_visual_review_required
```

Current exploration envelope after source/static floor audit:

```text
envelope_profile: Config/gazebo/scene_profiles/factory_l2_exploration_envelope.json
audit_packet: Results/unreal_scene_mapping/factory_l2_flight_envelope_audit_20260703_014306/FACTORY_L2_FLIGHT_ENVELOPE_AUDIT.json
low_floor_candidates: 392
floor_components: 1
default_spawn_floor: SM_FactoryFloorLarge114
historical_full_low_floor_boundary:
  x: [-608.09999, 587.89997] m
  y: [-284.65, 246.35] m
  size: 1195.99996 m x 531.0 m
current_indoor_wall_fence_boundary:
  x: [-98.40496, 77.25491] m
  y: [-51.36291, 12.63665] m
  size: 175.65987 m x 63.99956 m
initial_z_policy:
  fixed_world_z: 1.2 m
  command_band: [0.9, 1.6] m
  pointcloud_review_band: [0.2, 4.0] m
status: current_runtime_scope_is_indoor_wall_fence_boundary
```

The historical full low-floor boundary is retained only as source-audit
context. The current runtime scope for Factory exploration is the indoor
wall/fence boundary stored in
`Config/gazebo/scene_profiles/factory_l2_exploration_envelope.json`. Do not
command FUEL, RACER, Diff-Planner, TARE, scripted coverage, or manual goals
outside this indoor boundary unless the user explicitly reopens exterior or
full low-floor exploration. The global mesh AABB is much larger and contains
high, far, and low assets; it is not a valid flight boundary by itself.

Primary calibration-rig review packet for joint human audit:

```text
packet: Results/unreal_scene_mapping/factory_l2_calibration_rig_review_20260702_192443/FACTORY_L2_CALIBRATION_FRAME_CONTRACT.json
segments_csv: Results/unreal_scene_mapping/factory_l2_calibration_rig_review_20260702_192443/factory_l2_calibration_segments.csv
calibration_markers_csv: Results/unreal_scene_mapping/factory_l2_calibration_rig_review_20260702_192443/factory_l2_calibration_markers.csv
gazebo_calibration_world: Results/unreal_scene_mapping/factory_l2_calibration_rig_review_20260702_192443/worlds/factoryenvironmentcollect_l2_static_calibration_review.sdf
rviz_config: Results/unreal_scene_mapping/factory_l2_calibration_rig_review_20260702_192443/rviz/factory_l2_calibration_frames.rviz
ue_placement_script: Results/unreal_scene_mapping/factory_l2_calibration_rig_review_20260702_192443/ue/place_factory_l2_calibration_frames.py
rviz_marker_publisher: Results/unreal_scene_mapping/factory_l2_calibration_rig_review_20260702_192443/ros/publish_factory_l2_calibration_frames.py
marker_topic: /mosim/factory_l2/calibration_frame_markers
origin_gazebo_m: [0.0, 120.0, 0.2]
origin_unreal_cm: [0.0, -12000.0, 20.0]
calibration_marker_count: 6
status: review_required
```

The 2026-07-02 F0.5 anchor is deliberately not the historical default
`[0.0, -1.0, 0.2]`. Collision-truth AABB review shows that old point overlaps
low-altitude Factory obstacle/proxy boxes and is invalid as a coordinate-review
origin. The current `[0.0, 120.0, 0.2]` origin and the derived uav2/uav3
relative spawn markers sit on `SM_FactoryFloorLarge114`; the nearest
low-altitude solid clearance observed from collision truth is greater than
100 m for all three spawn markers. Later runtime promotion must derive launch
spawn points from this clean scene profile, not from the historical pillar-map
defaults.

Auxiliary named-landmark review packet:

```text
packet: Results/unreal_scene_mapping/factory_l2_landmark_review_20260702_111256/FACTORY_L2_LANDMARK_REVIEW.json
anchor_csv: Results/unreal_scene_mapping/factory_l2_landmark_review_20260702_111256/factory_l2_landmark_anchors.csv
gazebo_landmark_world: Results/unreal_scene_mapping/factory_l2_landmark_review_20260702_111256/worlds/factoryenvironmentcollect_l2_static_landmark_review.sdf
rviz_config: Results/unreal_scene_mapping/factory_l2_landmark_review_20260702_111256/rviz/factory_l2_coordinate_landmarks.rviz
marker_topic: /mosim/factory_l2/anchor_markers
status: review_required
```

The clean candidate filters only `SkySphereMesh`, a nonphysical UE display
background object that polluted the old Gazebo mesh bounds to +/-16384 m. It
does not intentionally remove factory doors, walls, outdoor space, machines,
floors, or other physical map geometry.

2026-07-02 correction: `cmd/启动Diff工厂UE实时审核.cmd` previously opened the
Factory UE mirror while the underlying Diff/Sunray runner still inherited the
default pillar `planning_test.world`. That mixed two different scenes and is
not valid Factory coordinate evidence. F0.5 must not use flight/control proof.
Use `cmd/启动Factory坐标静态审核.cmd` for UE-only static calibration-rig review.
If a later scoped runtime display is required, the launcher must explicitly set
the clean Factory `WORLD_FILE` and Factory `GAZEBO_MODEL_PATH`; otherwise the
run is a non-Factory regression and cannot be cited for Factory alignment.

The old pillar-map results remain regression references, not the final scene.
Factory L2 is the new runtime validation scene after the gates below pass.
The first F1-F8 Factory pass remains historical evidence for the old static
base and local runtime route. It must not be used as proof that the cleaned
global coordinate contract has passed runtime regression.

## 2. Authority Boundary

Gazebo/PX4/MAVROS/RViz/logs/metrics are the runtime authority. UE is a display
and review layer until a one-way render stream has evidence.

Do not claim:

```text
closed-loop Factory success
UE-Gazebo runtime bridge success
SLAM/localization success
planner success
controller performance
```

from static scene export, Gazebo screenshot, UE screenshot, or source-only
checks.

## 3. Gate Order

Run gates in this order. Do not skip a blocked gate by substituting a different
runtime, fake point cloud, ROS2/x500 route, or UE-only proof.

| Gate | Purpose | Evidence | Next Gate |
|---|---|---|---|
| F0 plan/static boundary | Freeze this plan and confirm Factory static scene acceptance paths. | This document, scene profile, static import manifest. | F1 |
| F0.5 coordinate-clean scene gate | Prove the UE/Gazebo axis, unit, origin, bounds, spawn-anchor, and non-symmetric calibration-rig contract after static-map import changes. | coordinate audit JSON, anchor CSV, clean conversion manifest, SDF check, calibration-rig contract, UE placement script, backend Gazebo/RViz/log source checks, optional named UE landmark packet, UE-only user visual acceptance. | F1 rerun on promoted clean profile |
| F1 spawn/sensor repair | Make one `sunray150_with_mid360` spawn in Factory, MAVROS connect, and MID360 publish nonempty data. | `FACTORY_SUNRAY_SPAWN_GATE.json`, MAVROS sample, raw lidar sample, model states, launch log. | F2 |
| F2 single-UAV mission | Run bounded px4ctrl takeoff-hover-land in Factory. | px4ctrl mission manifest/metrics, trajectory/control diagnostics, MID360 sample. | F3 |
| F3 single-UAV planner | Run Diff single-UAV scripted/interactive equivalent in Factory. | planner metrics, trajectory, point-cloud/grid RViz evidence. | F4 |
| F4 three-UAV Diff | Run three-UAV scripted-target Diff baseline in Factory. | target errors, min inter-UAV distance, per-UAV logs, RViz evidence. | F5 |
| F5 exploration baselines | Re-run accepted FUEL/RACER evidence in Factory only after F1-F4 are stable. | exploration metrics, occupancy/frontier proxies, safety metrics. | F6 |
| F6 MWORKS/codegen regression | Re-inject accepted generated controller families into Factory runtime as needed. | MWORKS/codegen evidence plus Gazebo A/B runtime metrics. | F7 |
| F7 UE render mirror | Mirror validated Gazebo/PX4/MAVROS state into UE display. | replay/live stream manifest, UE screenshot/video tied to runtime run id. | F8 |
| F8 review packet | Package Factory full-system evidence and unresolved limits. | summary packet, commands, logs, metrics, screenshots, claim boundary. | UI work |

The UI/QGC/UE integrated interface starts only after F8, unless the user
explicitly opens a separate frontend-only prototype.

If the Factory static scene changes after F8, re-enter through F0.5. Do not
jump directly to UI/QGC/UE work until the clean scene is accepted and the
smallest runtime regression gates pass on the promoted clean profile.

F0.5 acceptance must be joint review, not a solo agent judgment:

```text
agent responsibility:
  - prove axis/unit conversion numerically;
  - prepare one source calibration-rig contract and derive UE/Gazebo/RViz
    review surfaces plus asymmetric calibration blocks from it;
  - verify Gazebo/RViz/log source data, frame ids, units, trajectory source,
    segment endpoints, and the documented Y sign flip without asking the user
    to compare these windows by eye;
  - record exact packet paths, commands, and claim boundaries.
user responsibility:
  - visually review UE only: the Factory scene, audit frame, expected
    trajectory, actual trajectory, UAV pose, multi-UAV relative layout, and
    the project-owned asymmetric calibration blocks;
  - reject the scene if the UAV starts outside the audit frame, moves in a
    mirrored/reversed direction, exceeds the task audit frame unexpectedly, or
    shows obvious position/scale/attitude drift.
  - optionally use named landmarks as extra context only after the calibration
    frame itself is visible and coherent.
```

Current F0.5 user-facing entry:

```text
cmd/启动Factory坐标静态审核.cmd
```

This entry opens UE Factory display with the source calibration-rig CSV drawn
as runtime debug lines. It does not start Gazebo, PX4, MAVROS, FAST-LIO,
planner, or controller nodes.

F0.6 exploration envelope acceptance is agent-side source/static evidence plus
runtime regression, not a visual-only decision:

```text
agent responsibility:
  - derive floor-supported XY envelope from UE collision truth or an equivalent
    source geometry contract;
  - prove all default spawn points are inside the selected floor component;
  - define the first Z policy before any full-map exploration run;
  - record the exact boundary and Z policy in a machine-readable profile;
  - prevent old pillar-map or local-window evidence from being reused as
    Factory full-map exploration proof.

current decision:
  - XY envelope for current runtime coverage uses the user-accepted indoor
    wall/fence boundary:
    x=[-98.40496, 77.25491], y=[-51.36291, 12.63665].
  - The larger low-floor component remains source-audit context only and must
    not be used for runtime exploration unless the user explicitly reopens the
    exterior/full-floor task.
  - First exploration uses fixed world-z band, target 1.2 m and command clamp
    [0.9, 1.6] m. Free-Z or terrain-aware exploration is not allowed until a
    specific height-variation gate proves it is needed and safe.
  - Review point-cloud filtering may keep [0.2, 4.0] m to preserve obstacle
    evidence, but controller/planner commands must stay in the command band.
```

The first Factory exploration mission after F0.6 must prove runtime behavior
inside this envelope. A 30 m x 30 m short FUEL run proves only local viability;
it is not full-map exploration.

2026-07-03 F5c operating decision:

```text
Factory L2 clean scene is now the runtime baseline for exploration and
fixed-goal regression. Old pillar-map results and old static-base Factory
results remain engineering references only.

Full-map exploration means boundary-limited exploration inside the accepted
indoor wall/fence envelope, not the global mesh AABB and not space outside the
floor/wall-supported envelope. The selected boundary is the current indoor
engineering boundary:
  x=[-98.40496, 77.25491] m
  y=[-51.36291, 12.63665] m

Do not start with one huge unbounded FUEL/RACER map. The current progression is:
  1. retain the passed fixed-64 FUEL acceptance and the full-Factory FUEL
     closeout evidence; do not reopen blind single-UAV parameter tuning;
  2. port the accepted MID360/frame/Hybrid-Z, unreachable-candidate recovery,
     freshness, emergency telemetry, and coverage packet contracts to RACER;
  3. run a three-UAV RACER static/smoke gate, then bounded 120 s and 300 s
     Factory gates before any longer run;
  4. if RACER repeats the disconnected free-space failure without measurable
     gain, stop and use explicitly classified known-map partitioned coverage;
  5. keep Diff single-/three-UAV fixed-goal Factory regressions as support
     baselines and open RViz/UE only for the requested visual audit.

The first Z strategy is fixed altitude, not free-Z exploration:
  target z=1.2 m
  command clamp [0.9, 1.6] m
  point-cloud review band [0.2, 4.0] m

If runtime evidence shows terrain/floor height variation inside the accepted
boundary invalidates this band, stop and create a source-geometry height audit.
 Do not silently widen Z, do not let the planner climb/descend freely to mask a
 map conversion problem, and do not treat a short takeoff/land or partial tile
 as global exploration success.
```

2026-07-03 F5c runtime evidence update:

```text
single_uav_fuel_center_80m_pass:
  Results/sunray_ros1/factory_l2_f5c_fuel_fixedz_center_80m_takeover90_pocc060_20260703/
  EGO_SINGLE_METRICS.json status=passed, blockers=[]
  bspline_count=2, planner_position_cmd=4688, raw_lidar=1701,
  world_cloud=1700, occupancy_max_points=289
  exploration Z truth range ~= [1.168, 1.229] m
  mission_exit_code=0

single_uav_fuel_tile_negx_negy_blocked:
  Results/sunray_ros1/factory_l2_f5c_fuel_fixedz_tile_negx_negy_80m_pocc060_20260703/
  blocker=ego_planner_trajectory_timeout
  bspline_count=0, planner_position_cmd=0

single_uav_fuel_tile_posx_posy_blocked:
  Results/sunray_ros1/factory_l2_f5c_fuel_fixedz_tile_posx_posy_80m_pocc060_20260703/
  blocker=occupancy_points_below_gate
  bspline_count=2, planner_position_cmd=5199, occupancy_max_points=0

summary_packet:
  Results/sunray_ros1/factory_l2_f5c_fuel_tile_summary_20260703/FACTORY_L2_FUEL_TILE_SUMMARY.json

suitability_decision_packet:
  Results/sunray_ros1/factory_l2_fuel_suitability_decision_20260703/FACTORY_L2_FUEL_SUITABILITY_DECISION.json
  status=not_suitable_as_factory_full_map_primary
  blockers=[
    representative_tile_pass_ratio_below_50_percent,
    fuel_kino_search_failed_in_representative_tile,
    fuel_occupancy_empty_or_zero_in_representative_tile,
    fuel_bspline_absent_in_representative_tile
  ]
```

Current interpretation:

```text
FUEL is accepted as a local single-UAV exploration baseline on the clean Factory
scene. It is not accepted as a one-shot full Factory coverage method. The center
window proves the PX4/MAVROS/px4ctrl/FUEL/Fast-LIO-like point-cloud route can
run at fixed z=1.2 m, but local windows alone cover only a small fraction of the
175.66 m x 64.00 m indoor envelope.

Do not keep spending runtime on a monolithic all-map FUEL run, and do not bypass
FUEL with direct constant-velocity forward commands. The reopened FUEL route is
now explicitly a coverage-strategy task:
  1. diagnose whether the latest FUEL run stopped because of planner failure,
     command-stream loss, or time-limited local-window execution;
  2. keep the fixed-z policy and clean-scene indoor envelope;
  3. use a boundary-aware rolling-window or tile supervisor to move the local
     FUEL window forward in small steps;
  4. judge progress by merged coverage packets, command stream continuity,
     trajectory span, z-band, and safety metrics;
  5. only promote to same-flight rolling supervision after the serial rolling
     probe proves that window selection and merged coverage improve.

Current reopened evidence and entry points:
  - stop/coverage diagnosis:
    Results/sunray_ros1/factory_l2_fuel_low_coverage_diagnosis_refresh_20260704/
  - rolling-window dry-run:
    Results/sunray_ros1/factory_l2_fuel_rolling_dryrun_20260704/
  - rolling-window entry:
    Scripts/sunray/start_factory_fuel_rolling_coverage_probe.ps1
  - single-window entry:
    Scripts/sunray/start_factory_fuel_single_exploration_review.ps1
  - merged coverage reducer:
    Scripts/sunray/build_factory_l2_indoor_coverage_packet.py

Claim boundary: the current rolling script reuses the existing single-run FUEL
launch per window, so it validates window selection and merged coverage, not
same-flight dynamic map-box migration. Same-flight migration requires a separate
runtime gate because FUEL's `sdf_map/box_min/max` are launch-time parameters.
```

2026-07-03 unified Factory validation口径:

```text
The clean Factory L2 world is the only current validation scene:
  Results/unreal_scene_mapping/factory_l2_static_import/gazebo_review_clean/worlds/factoryenvironmentcollect_l2_static_review_clean.sdf

The old pillar map, old Factory static base with SkySphereMesh pollution, and
UE-only display runs are reference material only. They cannot be used as proof
that Factory exploration, fixed-goal flight, or UE display alignment is ready.

"Full-map" means the accepted floor/wall-supported engineering boundary, not
the whole imported mesh AABB:
  x=[-608.09999, 587.89997] m
  y=[-284.65, 246.35] m

The area outside this floor-supported boundary is not part of the first
exploration target. If a later source audit proves extra floor support outside
the current boundary, the envelope profile must be updated before missions are
allowed to command that space.

The first runtime altitude policy is fixed world altitude:
  nominal z=1.2 m
  command/safety clamp [0.9, 1.6] m
  review point-cloud band [0.2, 4.0] m

Do not let FUEL, RACER, Diff-Planner, or a UI target click choose free-Z just
to cross a difficult map region. If a mission needs to leave the fixed band,
stop and run a source-geometry height audit. The likely failure is terrain or
map-conversion height policy, not a reason to silently widen controller limits.

Current task split:
  single-UAV autonomous exploration:
    FUEL is local/tiled evidence only. It can prove sensor/planner plumbing,
    but it is not accepted as full Factory coverage after the offset-tile
    blockers. FALCON fixed-z checks are also blocked for the current Factory
    route by roll/pitch and low coverage, so the next single-UAV route is
    `uav_frontier_exploration_3d` source-first integration.
  multi-UAV autonomous exploration:
    RACER is a runnable local three-UAV baseline, but the full-coverage route
    must reopen the `fast_multi_robot_exploration` FAME/RACER family at source
    level. It must run on the clean Factory world, stay inside the envelope,
    preserve inter-UAV separation, and keep Z inside the fixed band.
  single-UAV fixed-goal:
    Diff-Planner direct-goal regression on the clean Factory world. This proves
    controlled navigation to a known target, not autonomous exploration.
  multi-UAV fixed-goal:
    Diff-Planner three-UAV direct-goal regression on the clean Factory world.
    This proves scripted multi-UAV avoidance/reach/hover/land, not autonomous
    task allocation or coverage exploration.

Review order:
  1. backend metrics must pass and name the clean Factory world;
  2. RViz opens for point cloud, occupancy/grid, trajectory, axes, and status;
  3. UE opens only as one-way display/review, with the same source run id.

Do not ask the user to visually accept a run before the backend packet says it
is the clean Factory map and has no runtime blocker.
```

## 4. F1 Status

F1 was originally blocked by the evidence below:

```text
Results/sunray_ros1/factory_l2_sunray_fs1a_spawn_20260701_180358/
Results/sunray_ros1/factory_l2_sunray_spawn_only_20260701_180904/
Results/sunray_ros1/factory_gate_control_default_world_20260701_180700/
```

Observed chain:

```text
Gazebo starts.
spawn_model calls /gazebo/spawn_sdf_model.
uav1 can appear in /gazebo/model_states, but the spawn service does not return.
Gazebo reports sensor initialization through the factory mechanism failed or timed out.
PX4 waits for simulator TCP 4560.
MAVROS remains connected: False.
```

Therefore the root classification is:

```text
gazebo_model_spawn_sensor_init_blocker
```

`mavros_connection_blocker` is a downstream symptom for this incident.

Latest F1 repair evidence:

```text
control_world_pass: Results/sunray_ros1/factory_fs1a_control_sunray_world_aligned_20260701_235121/
factory_l2_pass: Results/sunray_ros1/factory_l2_sunray_fs1a_aligned_20260701_235306/
```

The accepted repair is to align the Factory FS1a wrapper with the proven
Goal5/Sunray Livox overlay and MID360 startup defaults before replacing the
world. F1 is passed.

Latest F2 diagnostic evidence:

```text
native_mission_blocked: Results/sunray_ros1/factory_l2_sunray_fs1b_takeoff_hover_land_20260701_235637/
px4ctrl_mission_passed: Results/sunray_ros1/factory_l2_px4ctrl_l1_awff_takeoff_hover_land_20260702_003341/
```

This native Sunray control run proved MAVROS, Gazebo truth/local pose, and
nonempty MID360 samples in Factory, but blocked on takeoff height convergence:
target `z=1.228 m`, observed `z` rose above the target and timed out while
descending. Treat this as a Sunray native mission diagnostic, not as the current
px4ctrl runtime authority gate. The F2 acceptance gate for this project is the
current px4ctrl route.

The accepted F2 px4ctrl evidence is
`Results/sunray_ros1/factory_l2_px4ctrl_l1_awff_takeoff_hover_land_20260702_003341/`.
It uses the Factory L2 launch route, `PX4CTRL_CORE_PROFILE=l1_awff`, and the
current Sunray/PX4/MAVROS/px4ctrl lane. `PX4CTRL_BASIC_MISSION_METRICS.json`
reports `status=passed`, `mission_exit_code=0`, landing/disarm success, and
`landing_disarm.final_z_rel_m=0.0009980636306080315`. A prior F2 attempt passed
hover metrics but failed final landing/disarm because the mission script checked
the force-disarm height only once while the vehicle was still descending; the
accepted fix is a bounded wait-until-low-enough disarm gate plus a 25 s default
landing wait for takeoff-hover-land.

Latest F3 diagnostic evidence:

```text
diff_single_passed: Results/sunray_ros1/factory_l2_diff_single_l1_awff_20260702_005615/
previous_landing_gate_false_block: Results/sunray_ros1/factory_l2_diff_single_l1_awff_20260702_004742/
```

The accepted F3 Diff single-UAV evidence is
`Results/sunray_ros1/factory_l2_diff_single_l1_awff_20260702_005615/`.
It uses the Factory L2 world and Factory Sunray launch route with
`PLANNER_VARIANT=diff_planner` and `PX4CTRL_CORE_PROFILE=l1_awff`.
`EGO_SINGLE_METRICS.json` reports `status=passed`, blockers `[]`,
`execute_target_error_m=0.05890040400644708`, and target hold success.
`DIFF_SINGLE_Z_AUDIT.json` and `DIFF_SINGLE_123_WAYPOINT_AUDIT.json` both
report `status=passed`.

The previous F3 attempt had already proven planner execution and target hold,
but blocked on `landed_by_truth_false` because the mission script used absolute
world `z < 0.18` for landed truth. Factory/Sunray landed body-center height is
about `0.235 m`, so the accepted fix is to check Gazebo truth height relative to
the recorded home height and to write `truth_home_z_m` / `truth_z_rel_m` into
the land evidence.

Latest F4 diagnostic evidence:

```text
diff_swarm_3uav_passed: Results/sunray_ros1/factory_l2_diff_swarm_3uav_l1_awff_20260702_025108/
```

The accepted F4 three-UAV Diff evidence is
`Results/sunray_ros1/factory_l2_diff_swarm_3uav_l1_awff_20260702_025108/`.
It uses the Factory L2 world, Factory Sunray launch route, `UAV_NUM=3`,
`PLANNER_VARIANT=diff_planner`, and `PX4CTRL_CORE_PROFILE=l1_awff`.
`EGO_SWARM_METRICS.json` reports `status=passed`, blockers `[]`, all three
UAVs observed `armed=True` and `offboard=True`, minimum inter-UAV distance
`0.9848678640870179 m`, and execute target errors:

```text
uav1: 0.023462082073575096 m
uav2: 0.031877418887012336 m
uav3: 0.08656129372835616 m
```

The F4 repair was gate-level startup hardening only: per-UAV MAVROS state
timeline, per-UAV takeoff status, staggered TAKEOFF command publishing, bounded
TAKEOFF retries, and precise takeoff blockers. It did not retune px4ctrl
controller gains, Diff planner parameters, or Factory geometry.

Latest F5a diagnostic evidence:

```text
fuel_single_passed: Results/sunray_ros1/factory_l2_fuel_single_l1_awff_20260702_032520/
previous_fuel_takeoff_blocked: Results/sunray_ros1/factory_l2_fuel_single_l1_awff_20260702_030446/
fuel_takeoff_retry_diagnostic: Results/sunray_ros1/factory_l2_fuel_single_l1_awff_20260702_031627/
```

The accepted F5a FUEL single-UAV evidence is
`Results/sunray_ros1/factory_l2_fuel_single_l1_awff_20260702_032520/`.
It uses the Factory L2 world, Factory Sunray launch route,
`PLANNER_VARIANT=fuel`, and `PX4CTRL_CORE_PROFILE=l1_awff`.
`EGO_SINGLE_METRICS.json` reports `status=passed`, blockers `[]`, FUEL
bspline output, bounded exploration-stream execution, and landed-by-truth
success. `fuel_bspline_bridge.json` reports input/output count `9/9`, and
`fuel_position_cmd_compat_bridge.json` reports `raw_count=1519`,
`forwarded_count=1319`, and `decode_error_count=0`.

The F5a repair was gate-level startup hardening only: px4ctrl now retries ARM
inside `AUTO_TAKEOFF` while OFFBOARD is active and PX4 has not armed yet. This
fix addresses the PX4 health/arming readiness race observed in the blocked
FUEL runs; it does not retune the control law, FUEL planner parameters, or
Factory geometry.

Latest F5b evidence:

```text
racer_swarm_factory_pairguard10_passed:
  Results/sunray_ros1/factory_l2_racer_swarm_l1_awff_pairguard10_20260702_044053/
racer_swarm_factory_pairguard_timeout:
  Results/sunray_ros1/factory_l2_racer_swarm_l1_awff_pairguard150_20260702_043123/
previous_pair_opt_unfixed_run:
  Results/sunray_ros1/factory_l2_racer_swarm_l1_awff_rcsfix_wait150_20260702_040412/
```

The accepted F5b pass is
`Results/sunray_ros1/factory_l2_racer_swarm_l1_awff_pairguard10_20260702_044053/`.
It uses the Factory L2 world and Factory model path,
`PLANNER_VARIANT=racer`, `UAV_NUM=3`, `PX4CTRL_CORE_PROFILE=l1_awff`,
`RACER_D3_DISABLE_PAIR_OPT=true`, and
`RACER_D3_EXPLORATION_DURATION_S=10`. `EGO_SWARM_METRICS.json` reports
`status=passed`, blockers `[]`, and minimum inter-UAV distance
`1.7804230644583365 m`. The runtime log audit reports `status=passed`,
`fatal_event_count=0`, and semantic blockers `[]`.

The earlier post-pairguard run reached RACER planner execution and produced
per-UAV command/map/trajectory evidence, but `TOTAL_TIMEOUT_S=150` interrupted
the landing phase with `land_interrupted_by_ros_shutdown` / `ros_shutdown`.
Keep that run as timing diagnosis only. Do not treat it as a crash, collision,
missing planner-output, or pair-opt regression without new evidence.

Accepted F5b operating note:

```text
entry:
  always use wsl -d Ubuntu-20.04, never bare/default wsl
Factory RACER guard:
  keep d3_disable_pair_opt=true unless the user explicitly reopens Factory
  pair optimization
bounded rerun:
  reduce RACER_D3_EXPLORATION_DURATION_S to 10-15 s first
  keep TOTAL_TIMEOUT_S within the normal live wait budget, max 300 s
accept/retry rule:
  if planner/map/command activity and safe separation pass but landing is
  still cut off by wall-time shutdown, classify it as a Factory slow-runtime
  timing blocker or shorten only the mission timing; do not retune the
  controller or switch scenes
```

Latest F6 evidence:

```text
factory_l2_f6_mworks_codegen_regression:
  Results/sunray_ros1/factory_l2_f6_mworks_codegen_regression_20260702_044942/
```

The accepted F6 packet reuses the frozen G10-B/D/E MWORKS/codegen
state-isolated evidence by id, then ties it to Factory Diff single-UAV and
three-UAV runtime reinjection with `PX4CTRL_CORE_PROFILE=l1_awff`.
`F6_MWORKS_CODEGEN_FACTORY_REGRESSION.json` reports `status=passed`.

Latest F7 evidence:

```text
factory_l2_ue_render_mirror:
  Results/unreal_scene_mapping/factory_l2_ue_render_mirror_20260702_045816/
```

The accepted F7 packet is
`Results/unreal_scene_mapping/factory_l2_ue_render_mirror_20260702_045816/F7_UE_RENDER_MIRROR.json`.
It reports `status=passed` for F7a replay contract, F7b one-way UDP sidecar,
and F7c UE visual review. The source runtime run id is
`factory_l2_racer_swarm_l1_awff_pairguard10_20260702_044053`; UE remains a
display/review mirror only.

Latest F8 evidence:

```text
factory_l2_full_system_review:
  Results/unreal_scene_mapping/factory_l2_full_system_review_20260702_0528/
```

The accepted F8 packet is
`Results/unreal_scene_mapping/factory_l2_full_system_review_20260702_0528/F8_FACTORY_FULL_SYSTEM_REVIEW.json`.
It reports `status=passed` and indexes F0-F7 evidence, metrics, screenshots,
accepted claims, non-claims, and remaining work.

Next mainline: user audit of F8, then UI/QGC/UE integrated operator interface
planning if accepted.

## 4.1 Current Factory Full-System Goal

The active Factory goal is to validate the existing MoSim work in the new
Factory environment, not to reopen the old pillar-map tuning loop.

Execution order:

```text
F5: re-run accepted exploration/planning baselines in Factory
  -> F6: re-run accepted MWORKS/codegen controller families through Factory runtime
  -> F7: mirror the validated Gazebo/PX4/MAVROS/RViz run into UE display
  -> F8: package one review packet with commands, metrics, screenshots/video,
         run ids, and explicit remaining limits
```

Factory Gazebo remains the control/runtime authority. UE rendering must consume
validated Gazebo/PX4/MAVROS state as a one-way display/review stream. It must
not feed truth, targets, control commands, estimator data, or planner state back
into the runtime loop.

## 4.2 Current Execution Packet After UE Export

The Factory UE map is treated as fully exported only after the accepted static
Gazebo scene paths in Section 1 are present and reviewable. From this point on,
new system validation must use Factory L2 as the primary environment:

```text
primary scene: Factory L2
old pillar scene: regression/reference only
runtime authority: Gazebo/PX4/MAVROS/RViz/logs/metrics
display authority: UE only after F7 one-way stream/replay evidence
controller baseline: accepted px4ctrl generated-family route, default profile
                    `PX4CTRL_CORE_PROFILE=l1_awff` unless the gate explicitly
                    tests another generated controller family
planner baselines: Diff-Planner, FUEL, RACER as already accepted in the old
                   environment, revalidated in Factory before UI work
```

Do not spend more time on static-map polishing unless it blocks the executable
runtime gates below. Static scene acceptance is necessary but not sufficient;
the project moves forward only when the same scene carries real Sunray/PX4,
planner, controller, MWORKS/codegen, and UE-display evidence.

## 4.3 Remaining Gate Acceptance Details

F5b RACER multi-UAV exploration in Factory:

```text
current result:
  passed at
  Results/sunray_ros1/factory_l2_racer_swarm_l1_awff_pairguard10_20260702_044053/
input:
  Factory L2 world and Factory Sunray launch route
  three Sunray150 + MID360 vehicles
  PX4/MAVROS/px4ctrl per vehicle
  RACER adapter/bridge from the accepted D3/D4 route
required evidence:
  MAVROS connected/OFFBOARD/armed per UAV
  nonempty MID360 or planner map topics per UAV
  RACER command/frontier/occupancy activity
  no crash, no collision, no fatal runtime event
  bounded mission metrics with min inter-UAV distance and per-UAV tracking
acceptance:
  status=passed, blockers=[]
  mission_exit_code=0 or an explicitly accepted landed/timeout-success code
  min inter-UAV distance stays above the current safety threshold
runtime constraints:
  use wsl -d Ubuntu-20.04
  keep Factory model path active
  keep RACER pair optimization disabled for Factory unless explicitly reopened
  keep live runtime bounded; prefer short exploration duration over long waits
```

F5c Factory full-envelope autonomous exploration:

```text
purpose:
  Validate autonomous exploration against the clean Factory map and the
  accepted exploration envelope, not just the old pillar map or a 30 m local
  window.

source contract:
  Config/gazebo/scene_profiles/factory_l2_exploration_envelope.json

sub-gates:
  F5c-0 backend cleanup:
    no stale ROS/Gazebo/PX4/MAVROS/RViz/FUEL/RACER processes;
    clean Factory world and model path active;
    no old pillar planning_test.world in runtime logs.

  F5c-1 capacity smoke:
    run single-UAV Factory FUEL with bounded planner map but unlimited or high
    review accumulation for a short duration;
    prove accumulated point cloud and occupancy review topics grow without
    RViz/Gazebo/log failure;
    this does not prove full coverage.
    current blocker:
      Results/sunray_ros1/factory_l2_f5c1_fuel_capacity_smoke_20260703_0148/
      used the clean Factory world and kept z inside the first fixed-z band,
      but FUEL published only three short bsplines and `/sdf_map/occupancy_all`
      ended with zero occupied points. This is not accepted full-map
      exploration evidence.
    immediate repair hypothesis:
      FUEL's upstream demo ray/perception range was 4.5 m, while Factory
      MID360 returns often sit tens of meters away. Points beyond
      `sdf_map/max_ray_length` are treated as free ray endpoints rather than
      occupied hits, so Factory FUEL runs must record explicit ray/perception
      range parameters in `RUN_MANIFEST.json` before being accepted.
    2026-07-03 follow-up:
      `factory_l2_f5c1_fuel_window40_ray20_fix_20260703_0235` fixed the
      planner launch argument blocker but still produced no bspline because the
      40 m window clipped too much of the Factory MID360 cloud.
      `factory_l2_f5c1_fuel_window80_ray30_smoke_20260703_0310` and
      `factory_l2_f5c1_fuel_window80_ray30_frontier_relaxed_20260703_0325`
      used an 80 m local FUEL window and produced nonempty local cloud plus
      nonempty `/sdf_map/occupancy_all` (about 52 occupied points), but FUEL
      still reached `PLAN_TRAJ` with zero bspline output and
      `ego_planner_trajectory_timeout`. Relaxing `frontier/cluster_min`,
      `frontier/min_visib_num`, and `frontier/min_candidate_clearance` did not
      change the result.
      `factory_l2_f5c1_fuel_window80_ray80_frontier_relaxed_20260703_0345`
      increased occupied points to about 302 but still produced zero bspline
      and ended without a normal metrics packet, so ray-range increase alone is
      not an accepted repair.
      Additional diagnosis: the 80 m x 80 m x 5 m FUEL local map at the
      upstream 0.1 m SDF resolution implies roughly 32 million voxels for a
      frontier scan. The observed log stops after `Before remove/After remove`,
      before `new num/to visit/Frontier`, which makes local-map scan cost a
      primary blocker candidate. Do not increase Factory FUEL windows without
      recording `grid_resolution_m` and estimated voxel count in the run
      manifest.
      Current classification is `fuel_frontier_bspline_blocker`: Factory clean
      world, PX4/MAVROS, fixed-z hover, MID360 world cloud, local cloud bridge,
      and occupancy publication are working; FUEL's map/frontier/planning
      chain is not yet producing autonomous exploration trajectories in this
      Factory local window.
      2026-07-03 repair result:
      `factory_l2_f5c1_fuel_window60_res02_cluster100_ray30_smoke_20260703_0342`
      is the first accepted clean-Factory local FUEL smoke after exposing
      `grid_resolution_m`. It used a 60 m x 60 m x 5 m local map at 0.2 m
      resolution, `frontier_cluster_min=100`, ray/perception 30/30/12 m, and
      fixed target z=1.2 m. `EGO_SINGLE_METRICS.json` reports `status=passed`,
      blockers `[]`, bspline count `2`, planner position command count `2149`,
      nonempty MID360/world cloud and occupancy, safe fixed-z execution, and
      landed-by-truth success. This is accepted as a local autonomous
      exploration smoke only; it moved roughly 4 m and must not be cited as
      full Factory envelope coverage.
      `factory_l2_f5c1_fuel_tile_east230_res02_cluster100_20260703_0353`
      is the first accepted non-default tile smoke. It used `StartX=230`,
      `StartY=128`, the same 60 m / 0.2 m / cluster100 policy, and the clean
      Factory world. `EGO_SINGLE_METRICS.json` reports `status=passed`,
      blockers `[]`, bspline count `2`, planner position command count `3789`,
      occupancy last points `2982`, and landed-by-truth success. This proves
      that the parameterized FUEL local-frame bridge works outside the default
      origin tile; it still does not prove full Factory envelope coverage.
      2026-07-03 representative tile extension:
      `factory_l2_f5c1_fuel_tile_west250_res02_cluster100_20260703_0405`
      passed with bspline count `3`, planner position command count `2755`,
      raw/world cloud `1039/1038`, occupancy last points `6466`, and landed
      by truth. Truth Z during exploration was about `[1.075, 1.600]` m.
      `factory_l2_f5c1_fuel_tile_fareast470_res02_cluster100_20260703_0410`
      initially blocked with `ego_planner_trajectory_timeout` because the old
      point-cloud odom guard and review-only Z gate starved world-cloud output
      in the far-east Factory region. The repaired run
      `factory_l2_f5c1_fuel_tile_fareast470_res02_zsplit_20260703_0425`
      passed with bspline count `6`, planner position command count `4200`,
      raw/world cloud `1245/1243`, and landed by truth after separating
      planner-cloud and review-cloud Z filters. Truth Z during exploration was
      about `[0.866, 0.996]` m, so this run is accepted for exploration-chain
      viability but must remain flagged for height-margin review.
      `factory_l2_f5c1_fuel_tile_south010_y166_res02_zsplit_20260703_0429`
      passed with bspline count `7`, planner position command count `3518`,
      raw/world cloud `1116/1116`, and landed by truth. Truth Z during
      exploration was about `[0.885, 1.105]` m, again accepted as a runnable
      tile but flagged for height-margin review.
    next diagnostic order:
      1. Do not open RViz/UE review or proceed to multi-UAV exploration until
         FUEL produces nonzero frontier or bspline evidence in a backend run.
      2. First expose and record FUEL SDF resolution, local map size, and
         estimated voxel count. Then add or expose FUEL map/frontier diagnostics
         before more parameter sweeps: updated box, known-free seed count,
         frontier cluster count, dormant frontier count, viewpoint rejection
         counts, and bspline plan return code.
      3. Verify whether the clean Factory start window is too open/sparse for
         the upstream FUEL frontier assumptions by testing a bounded
         obstacle-near window inside the same accepted envelope.
      4. If local FUEL cannot produce frontiers from live MID360 clouds without
         source changes, switch F5c single-UAV exploration to a source-backed
         windowed/tiled or RACER-compatible route instead of declaring full-map
         FUEL coverage.

  F5c-2 single-UAV FUEL envelope exploration:
    use FUEL as the single-UAV autonomous exploration baseline;
    start with windowed/tiled exploration over the Factory envelope rather than
    one monolithic SDF map;
    accepted first local smoke is 60 m x 60 m x 5 m at 0.2 m SDF resolution
    with `frontier_cluster_min=100`; larger windows require explicit voxel-count
    and planner-time evidence before promotion;
    the reusable Windows entry `Scripts/sunray/start_factory_fuel_single_exploration_review.ps1`
    accepts `StartX`, `StartY`, and `StartYaw` so Factory tiles can be launched
    at different envelope positions without changing the clean world or the
    FUEL local-frame bridge logic;
    keep FUEL's internal SDF grid bounded, but keep review point cloud,
    trajectory, and coverage accounting global over the accepted boundary;
    expand only after metrics pass.
    "Full Factory exploration" means coverage over the accepted floor/wall
    envelope through a repeatable tile matrix, not one FUEL global grid. The
    first tile set should cover representative regions of the connected floor:
    center/default, east, west, far-east or far-west, and negative-y/south.
    A tile only counts when backend metrics pass with the clean Factory world,
    nonempty live sensor/map evidence, nonzero planner output, no fatal runtime
    logs, and Z inside the fixed policy. RViz/UE review is opened after those
    backend checks, not before.

    The first exploration altitude policy is deliberately conservative:
    command z target 1.2 m, command clamp [0.9, 1.6] m, review point-cloud band
    [0.2, 4.0] m. Large Factory height variation must not be handled by letting
    FUEL or Diff freely choose Z in this stage. If a tile needs terrain-aware
    height because floor support is not near world z=0, stop and create a
    source-geometry height audit instead of silently widening the Z band.

    Factory is larger than the old pillar world. Any odom sanity filters,
    point-cloud world conversion guards, click-goal bounds, planner box bounds,
    and RViz accumulation caps must be checked against the Factory envelope.
    For single-UAV FUEL, `start_factory_fuel_single_exploration_review.ps1`
    defaults `PointCloudMaxAbsOdomXYM=700.0` so far-east/far-west tiles are not
    rejected as absurd odom before world-cloud generation.

    Planner input cloud filtering and human review cloud filtering are separate
    concerns. In open Factory regions the MID360 may mainly see floor or
    near-ground returns; applying the review-only `min_world_z=0.2 m` gate
    before FUEL can delete every live return and starve frontier generation.
    The Factory FUEL wrapper therefore defaults the transform/planner cloud to
    `PointCloudTransformMinWorldZM=-0.2` while keeping accumulated RViz review
    at `PointCloudReviewMinWorldZM=0.2`. Do not collapse these two filters
    again without a run showing nonempty world cloud and clean review display.

  F5c-3 multi-UAV RACER envelope exploration:
    use RACER as the current multi-UAV autonomous exploration baseline;
    default to three UAVs and keep Factory pair optimization disabled unless
    explicitly reopened;
    prove frontier/map/command activity, inter-UAV distance, and z-band safety.
    Current clean-Factory RACER pass:
      Results/sunray_ros1/factory_l2_f5c3_racer_swarm_clean_staggered_range35_fix_20260703_0605/
      status=passed, blockers=[], mission_exit_code=0,
      clean Factory world active,
      RACER local-frame bridge offset=(0.0, 120.0, 0.0),
      min_inter_uav_distance_m=1.5189747530148507,
      runtime_log_audit.status=passed, fatal_event_count=0.
    This is accepted as the current backend multi-UAV autonomous exploration
    smoke on the new map. It is not yet a quantitative full-boundary coverage
    percentage claim.

    2026-07-03 indoor full-coverage check:
      the accepted indoor boundary is the wall/fence envelope in
      `Config/gazebo/scene_profiles/factory_l2_exploration_envelope.json`
      with x=[-98.40496,77.25491], y=[-51.36291,12.63665].
      Single-UAV RACER 120 s:
        `Results/sunray_ros1/factory_l2_indoor_racer_single_wallcenter_120s_20260703_131047/`
        has a follow-up coverage packet at
        `Results/sunray_ros1/factory_l2_indoor_coverage_single120_offline_20260703/`
        with sensor_footprint_coverage_ratio=0.0433.
      Three-UAV RACER 60 s:
        `Results/sunray_ros1/factory_l2_indoor_racer_swarm_coverage60_20260703_142323/`
        has a follow-up coverage packet at
        `Results/sunray_ros1/factory_l2_indoor_coverage_swarm60_offline_20260703/`
        with sensor_footprint_coverage_ratio=0.0327.
      These runs prove the Factory RACER runtime chain can execute, but they
      do not prove full indoor coverage. Do not continue by blindly increasing
      duration. First choose a source-backed full-coverage strategy.

  F5c-3b Factory indoor full-coverage mapping route:
    Current candidate audit:
      `Results/sunray_ros1/factory_l2_indoor_exploration_candidate_audit_20260703_234347/FACTORY_L2_INDOOR_EXPLORATION_CANDIDATE_AUDIT.json`.
    FALCON fixed-z runtime evidence is blocked and must not be blindly tuned:
      `Results/sunray_ros1/factory_l2_indoor_falcon_single_short_fixedz_gate30_20260703_233412/`
      reports roll/pitch safety blocking and poor coverage after low-Z
      viewpoint filtering was fixed.
    Single-UAV primary route:
      `uav_frontier_exploration_3d` source-first integration. This is preferred
      over TARE for the current UAV task because it is a 3D UAV frontier
      planner with point-cloud/odometry/frontier/planner interfaces closer to
      MoSim, while TARE is kept as reference/backup only if a source audit
      later proves the vehicle assumptions fit.
      1. UF-F0 source audit of README, package.xml, launch files, config files,
         frontier server, planner, trajectory execution, cloud/odom interfaces,
         and dependency assumptions.
      2. UF-F1 isolated ROS Noetic build or explicit dependency blocker.
      3. UF-F2 MoSim bridge dry-run:
         `/uav1/livox_world` or accepted accumulated/filtered world cloud ->
         planner cloud input, `/uav1/mavros/local_position/odom` -> odometry,
         Factory envelope -> boundary/coverage guard, planner goal/trajectory
         output -> existing px4ctrl/Diff/RACER-safe execution adapter.
      4. UF-F3 single-UAV clean-Factory bounded runtime with fixed-z policy,
         nonempty map/frontier/trajectory topics, z/attitude/boundary gates,
         and landing/disarm evidence.
      5. UF-F4 offline coverage packet over the accepted indoor boundary.
    Single-UAV backups:
      `3dmr/nbvplanner`, then `gbplanner2`, then `ExplorationRRT`, in that
      order, unless a source audit finds a lower-risk MoSim interface.
    Multi-UAV primary route:
      `fast_multi_robot_exploration` FAME/RACER family. Existing RACER runs are
      local-smoke evidence only; the next multi-UAV gate must inspect FAME vs
      RACER source-level coverage strategy before another long runtime.
    Multi-UAV backup:
      `3dmr` multiagent NBV, then graph-based backups if FAME/RACER cannot be
      adapted.
    Known-scene fallback:
      FC-Planner or scripted coverage mapping with the already validated
      Diff/RACER execution chain. It may satisfy the engineering goal of full
      indoor cumulative mapping, but must be labeled `scripted known-scene
      coverage mapping` rather than autonomous unknown-environment exploration.
      2026-07-06 same-flight Diff coverage route:
      `Results/sunray_ros1/factory_l2_diff_interactive_coverage_full_z4_nosoft_norejoin_20260706_082641/`
      is blocked at 91/895 by
      `goal_91/route_91:accepted_goal_stable_hold_not_reached`. The terminal
      state is safe and stable, about 2.37 m from the accepted goal, with z
      error about 0.04 m, speed about 0.02 m/s, and roll/pitch about 0.21 deg.
      Therefore the next active route is not another no-rejoin rerun. It is
      `factory_l2_diff_interactive_coverage_full_z4_continuous_rejoin_*`,
      using one UAV, fixed z=4.0 m, stable-arrival goal switching, no
      coverage-soft waypoint pass, `RuntimeSkipMaxXYErrorM=3.0`,
      `EnableRouteRejoin`, `AllowRouteRejoinOnStableFailure`, and
      `RouteRejoinLocalHorizonM=7.0`.
      The route contains 895 waypoints and has planned sensor footprint
      coverage proxy 0.8235 at 2.0 m coverage grid / 8.0 m sensor radius, so
      final acceptance still requires the runtime goal-chain report,
      `EGO_SINGLE_METRICS.json`, and
      `coverage_packet/FACTORY_L2_INDOOR_COVERAGE_PACKET.json`.
      Invalid local diagnostics must not be promoted: a corridor run that
      starts by respawning the UAV at route 83/84 is not valid if PX4 arming or
      pre-diff stability fails; a startup run with Gazebo/PX4 heartbeat loss is
      a runtime startup blocker, not a route-planning blocker.
      Latest invalid launch:
      `Results/sunray_ros1/factory_l2_diff_interactive_coverage_full_z4_continuous_rejoin_20260706_101908/`
      blocked at `goal_1/route_1:pre_goal_stability_timeout` while the UAV was
      still climbing near z=1.17 m and `interactive_goal_ready=false`. Do not
      use this run to reject continuous-rejoin; rerun from a clean launcher
      after ROS/Gazebo/PX4/MAVROS startup is stable.
      For Diff/EGO review, the accumulated occupancy evidence source is
      `/drone_0_ego_planner_node/grid_map/occupancy`; `/sdf_map/occupancy_all`
      is a FUEL-style topic and has no publisher in this Diff route.

  F5c-4 fixed-goal regression on the same clean Factory map:
    rerun single-UAV Diff fixed-target regression and three-UAV Diff fixed-
    target regression after exploration is stable, so old fixed-goal evidence
    is not silently reused.
    Factory fixed-goal runs must use either direct goal publication or a
    Factory-specific multipoint YAML. Do not reuse
    `Config/planners/diff_planner_goal4_points.yaml`, because that file is the
    old pillar-map Goal4 target set and can silently send `(2,0,1)` to Diff
    even when the Factory runner's `TARGET_X/Y/Z` is different.
    The Diff launch must pass the Factory map-size arguments into
    `grid_map/map_size_x`, `grid_map/map_size_y`, and `grid_map/map_size_z`;
    declaring shell arguments alone is not evidence that the planner saw the
    Factory window.
    For fixed-goal regression, final occupancy-frame nonemptiness is not the
    primary acceptance gate. It may be disabled explicitly with
    `EGO_ALLOW_EMPTY_FINAL_OCCUPANCY=true` when the run still proves nonempty
    raw MID360, nonempty world cloud, nonempty planner command evidence,
    target-hold success, safe Z/attitude, and landing/disarm success. Keep the
    stricter occupancy gate for FUEL/RACER exploration and map-quality review.
    Current single-UAV clean-Factory direct-goal regression:
      Results/sunray_ros1/factory_l2_clean_diff_single_directgoal_allowocc_/
      status=passed, blockers=[], target=(-4,118,1.0),
      direct goal publication enabled, `DIFF_USE_MULTIPOINT=false`,
      `EGO_ALLOW_EMPTY_FINAL_OCCUPANCY=true`,
      execute_target_error_m=0.02571499206213704.
    Current three-UAV clean-Factory fixed-goal regression:
      Results/sunray_ros1/factory_l2_clean_diff_swarm_3uav_direct_20260703_0707/
      status=passed, blockers=[], mission_exit_code=0,
      targets uav1=(-4,118,1.0), uav2=(-4,124,1.0),
      uav3=(-6,121,1.0), min_inter_uav_distance_m=1.645142134136173,
      runtime_log_audit.status=passed.

minimum evidence:
  - result directory under Results/sunray_ros1/ for each sub-gate;
  - RUN_MANIFEST or equivalent environment dump naming the clean Factory world;
  - MAVROS connected/OFFBOARD/armed per UAV where applicable;
  - nonempty MID360/planner cloud or map topics;
  - planner output evidence: frontier/bspline/position_cmd as applicable;
  - truth/odom path CSV and z-band audit;
  - boundary audit: all commanded and actual XY samples stay inside the
    envelope, with explicit tolerance;
  - accumulated point cloud and occupancy counts;
  - FUEL/RACER ray, perception, map-size, and boundary parameters recorded in
    the manifest;
  - runtime log audit with fatal_event_count=0 or classified blocker;
  - RViz/UE review opened only after backend metrics pass.

stop conditions:
  - the selected Factory world is not the clean Factory SDF;
  - FUEL/RACER requires prior static-world access instead of live sensor/map
    input;
  - monolithic full-map grid causes memory, latency, or planner instability;
  - Z cannot stay inside [0.9, 1.6] m without a terrain-aware design;
  - the next repair would change vehicle, sensor, controller authority, or
    runtime stack.
```

Because the current accepted indoor envelope is about 175.7 m x 64.0 m, do
not equate "full indoor exploration" with a single huge FUEL local grid or a
short local RACER smoke. The project should first prove that the selected
strategy actually expands coverage over the accepted indoor boundary, then
validate it with the offline coverage packet. If a later source-backed test
proves one monolithic map is stable, the profile may be promoted, but that is
not the default assumption.

2026-07-04 FUEL local-first coverage-design correction:

```text
latest bounded duration check:
  Results/sunray_ros1/factory_l2_fuel_5min_coverage_probe_20260704/
  status=passed, blockers=[]
  exploration_duration=300 s
  bspline=43, position_cmd=9451
  truth span ~= 10.13 m x 9.01 m
  coverage_packet:
    Results/sunray_ros1/factory_l2_fuel_5min_coverage_probe_20260704/coverage_packet/FACTORY_L2_INDOOR_COVERAGE_PACKET.json
  sensor_footprint_coverage_ratio=0.0444

interpretation:
  FUEL is not stuck and not unusable. It can repeatedly produce local
  command-stream/frontier evidence, and a longer 5 min local run improves over
  the short smoke. The blocker is still expansion strategy: a single local
  center window does not scale to the full indoor envelope.

correct next action:
  Do not keep increasing duration as the primary experiment. Reopen FUEL only
  as a rolling-window/tile coverage strategy task:
    1. run small representative tile sets first;
    2. count only backend-passed tiles toward merged coverage;
    3. combine coverage by union over all accepted tile trajectories;
    4. use blocked tiles as diagnostics for seed placement, visibility,
       planner window, and map-input failures;
    5. promote tile count only when merged coverage grows and safety/log gates
       remain clean.

reusable entries:
  single local FUEL tile:
    Scripts/sunray/start_factory_fuel_single_exploration_review.ps1
  serial tile probe and merged coverage packet:
    Scripts/sunray/start_factory_fuel_tile_coverage_probe.ps1
  offline merged coverage reducer:
    Scripts/sunray/build_factory_l2_indoor_coverage_packet.py

coverage reducer rule:
  Multi-run coverage acceptance must use
  acceptance.merged_sensor_footprint_coverage_ratio. The
  best_single_run_* fields are diagnostics only and must not be used as
  full-envelope acceptance.
```

2026-07-04 FUEL rolling-window review:

```text
review_packet:
  Results/sunray_ros1/factory_l2_fuel_rolling_coverage_review_20260704/

runtime hygiene result:
  The first 2-window rolling attempt exposed serial runtime contamination.
  The wrapper now performs per-tile cleanup, waits for runtime quiescence,
  stops on tile failure by default, and forwards TakeoffTimeoutS=50.

accepted evidence:
  one-window clean smoke:
    Results/sunray_ros1/factory_l2_fuel_rolling_1win_takeoff50_20260704/
    merged_sensor_footprint_coverage_ratio=0.0234375
  two-window rolling probe:
    Results/sunray_ros1/factory_l2_fuel_rolling_2win_takeoff50_20260704/
    eligible_run_count=2
    merged_sensor_footprint_coverage_ratio=0.04296875
  32 m local-window check:
    Results/sunray_ros1/factory_l2_fuel_rolling_1win_win32_20260704/
    merged_sensor_footprint_coverage_ratio=0.024502840909090908
  1.2 m/s speed check:
    Results/sunray_ros1/factory_l2_fuel_rolling_1win_vel12_20260704/
    merged_sensor_footprint_coverage_ratio=0.024857954545454544

decision:
  FUEL basic chain is usable as a local baseline. FUEL single-window
  full-indoor coverage remains blocked. Blind parameter tuning is exhausted as
  the primary route because larger window and higher speed only give marginal
  coverage gain. The reopened FUEL route is now an explicit coverage-supervisor
  experiment, not a claim that upstream FUEL will naturally explore the whole
  Factory indoor boundary from one start.

next promotion gate:
  Generate a bounded strip/lawnmower tile list over the indoor boundary and run
  a small 4-8 window batch first. Promote only if
  acceptance.merged_sensor_footprint_coverage_ratio grows roughly with each
  eligible window and safety/log gates stay clean. If 4-8 windows do not show
  clean merged-coverage growth, stop and classify FUEL as local-only for this
  Factory full-coverage task unless a stronger same-flight supervisor is
  explicitly designed.

script mode:
  Scripts/sunray/start_factory_fuel_rolling_coverage_probe.ps1 now exposes
  CoveragePattern=forward_strip|lawnmower. Use forward_strip to validate the
  user's "keep moving forward" hypothesis from the current center line. Use
  lawnmower only when the task is explicitly boundary coverage mapping.

dry-run plans:
  forward_strip:
    Results/sunray_ros1/factory_l2_fuel_rolling_8win_dryrun_forward_20260704/
  lawnmower:
    Results/sunray_ros1/factory_l2_fuel_rolling_8win_dryrun_lawnmower_20260704/

follow-up blocker:
  The first live extension past the accepted two-window run blocked at win03:
    Results/sunray_ros1/factory_l2_fuel_rolling_forward_win03_20260704_win03/
    blocker=pre_diff_hover_not_stable
    planner outputs: bspline=0, position_cmd=0
  Source-truth start-clearance audit:
    Results/sunray_ros1/factory_l2_fuel_rolling_coverage_review_20260704/START_CLEARANCE_AUDIT.md
  Interpretation: the naive +X center-line forward strip intersects cluttered
  low-altitude Factory AABBs after the first two windows. Do not continue
  launching raw forward-strip centers. The next coverage-supervisor gate must
  filter candidate start/window centers by floor support and obstacle clearance
  before runtime.
```

2026-07-04 clearance-filtered FUEL supervisor result:

```text
tile generator:
  Scripts/sunray/build_factory_l2_clearance_filtered_fuel_tiles.py
  purpose:
    Generate FUEL rolling-window start centers from Factory collision truth,
    not by eye. Candidate centers must be inside the accepted indoor boundary,
    supported by stable low floor, clear of flight-height obstacles, and clear
    of spawn-footprint blockers before runtime launch.

accepted candidate list:
  Results/sunray_ros1/factory_l2_fuel_clearance_filtered_tiles_lawnmower5_margin08_window16_spawnpoint_yaw0_20260704/clearance_filtered_fuel_tiles.csv
  generation policy:
    pattern=lawnmower
    step_x=5 m
    step_y=5 m
    fuel_window_xy=16 m
    flight_clearance_margin=0.8 m
    spawn_clearance_margin=0 m
    tile_yaw=0 rad

bounded runtime batch:
  Results/sunray_ros1/factory_l2_fuel_spawnfiltered_yaw0_4win_20260704/
  max_windows=4
  exploration_execute_s=45
  all 4 windows passed backend metrics
  excluded_run_count=0
  outside_boundary_rows=0 for every eligible run
  flight_safety_violation=null for every eligible run

coverage packet:
  Results/sunray_ros1/factory_l2_fuel_spawnfiltered_yaw0_4win_20260704/coverage_packet/FACTORY_L2_INDOOR_COVERAGE_PACKET.json
  status=blocked
  eligible_run_count=4
  merged_sensor_footprint_coverage_ratio=0.10475852272727272
  merged_path_coverage_ratio=0.005681818181818182
  min_required=0.80
  blocker=indoor_sensor_footprint_coverage_below_threshold

interpretation:
  Clearance-filtered tile selection fixed the unsafe win03 spawn/takeoff
  failure. FUEL can be made into a stable local-window coverage probe under
  the Factory indoor boundary, but 4 clean windows only cover about 10.5% by
  the accepted sensor-footprint metric. This is not full indoor autonomous
  exploration.

promotion boundary:
  Do not promote reset-and-respawn multi-window FUEL tiling as the final
  unknown-environment autonomy result. It is useful as map-building support or
  coverage evidence infrastructure. A true FUEL-based autonomous route now
  requires a same-flight global/frontier supervisor that keeps one vehicle
  moving, issues bounded subgoals inside the accepted envelope, and proves
  continuous merged coverage growth without reinitializing the vehicle for
  every window.

next decision:
  Either design the same-flight supervisor as a new runtime gate, or stop FUEL
  full-coverage work and pivot to another source-backed exploration strategy.
  Blind duration increases, raw forward strips, and more reset windows are not
  valid primary optimization by themselves.
```

2026-07-05 same-flight Diff clearance-route support result:

```text
scripts:
  Scripts/sunray/generate_factory_l2_lawnmower_waypoints.py
  Scripts/sunray/generate_factory_l2_clearance_route_waypoints.py
  Scripts/sunray/start_factory_diff_lawnmower_coverage_probe.ps1
  Scripts/sunray/run_px4ctrl_ego_single_gate.sh
  cmd/启动Factory单机同飞行覆盖建图.cmd

route policy:
  planner=Diff-Planner multipoint
  mission_mode=exploration_stream
  waypoint_yaml_section=test1
  fixed_z=1.2 m
  current_route_mode=clearance_route
  current_route_policy=nearest_neighbor
  no_center_start=true
  min_start_target_distance=4 m
  accepted_indoor_boundary=Config/gazebo/scene_profiles/factory_l2_exploration_envelope.json

fixes made:
  - multipoint only reads fixed YAML keys test1/test2/test3/test4/test_back;
    the first generated Factory lawnmower YAML used factory_l2_lawnmower and
    produced No pyt loaded after trigger.
  - Goal4 fixed_goal semantics landed after the first target; coverage probing
    must run exploration_stream so the same aircraft keeps executing planner
    commands for a bounded duration.
  - direct center-to-row endpoints created about 80 m target jumps and caused
    Diff-Planner Local target in collision / EMERGENCY_STOP; lawnmower waypoints
    are now densified into bounded segments before runtime.
  - land timeout is exposed as GOAL4_LAND_TIMEOUT_S so short smoke probes can
    write metrics instead of being killed before packet generation.
  - the straight full lawnmower route later still placed goals through Factory
    obstacle space and stalled at WAIT_TARGET. It must not be rerun as the
    active full-coverage route.
  - clearance-route generation now filters targets against UE collision-truth
    floor support and low-altitude obstacle AABBs, then orders safe targets
    with nearest-neighbor. This is scripted known-scene map-building support,
    not autonomous unknown-environment exploration.
  - exploration_stream mission evidence now uses wall-clock bounded execution
    during exploration/landing so timeout kills do not erase metrics packets.

accepted bounded smokes:
  Results/sunray_ros1/factory_l2_diff_lawnmower_12wp_stream_probe_20260705/
    EGO_SINGLE_METRICS.json status=passed, blockers=[]
    mission_mode=exploration_stream
    planner_position_cmd=1509
    position_cmd=856
    raw_lidar/world_cloud=554/554
    occupancy_inflate=222
    landed_by_truth=true
    coverage_packet.status=blocked
    merged_sensor_footprint_coverage_ratio=0.026278409090909092

  Results/sunray_ros1/factory_l2_diff_clearance_route_10target_smoke4_20260705_current/
    route_mode=clearance_route
    waypoint_count=10
    EGO_SINGLE_METRICS.json status=passed, blockers=[]
    planner_position_cmd=780
    position_cmd=619
    raw_lidar/world_cloud=520/519
    occupancy_inflate=208
    landed_by_truth=true
    position_cmd_motion.x_range_m=3.802
    coverage_packet.status=blocked
    merged_sensor_footprint_coverage_ratio=0.0241

  Results/sunray_ros1/factory_l2_diff_clearance_route_g3c06_30target_probe_20260705_current/
    route_mode=clearance_route
    waypoint_count=30
    EGO_SINGLE_METRICS.json status=passed, blockers=[]
    planner_position_cmd=3431
    position_cmd=2635
    raw_lidar/world_cloud=921/921
    occupancy_inflate=368
    landed_by_truth=true
    position_cmd_motion.x_range_m=7.871
    position_cmd_motion.y_range_m=3.093
    coverage_packet.status=blocked
    merged_sensor_footprint_coverage_ratio=0.0334

current full-route dry-runs:
  Results/sunray_ros1/factory_l2_diff_clearance_route_g3c06_nn_full_dryrun_20260705_current/
    grid_step=3.0 m
    clearance_margin=0.6 m
    route_policy=nearest_neighbor
    waypoint_count=282
    estimated_path_length_m=1338.2
    estimated_time_at_0.8mps=27.9 min
    planned_sensor_footprint_coverage_ratio=0.8008

  Results/sunray_ros1/factory_l2_diff_clearance_route_nn_full_nocenter_dryrun_20260705_current/
    grid_step=2.5 m
    clearance_margin=0.6 m
    route_policy=nearest_neighbor
    waypoint_count=432
    estimated_path_length_m=1617.4
    estimated_time_at_0.8mps=33.7 min
    planned_sensor_footprint_coverage_ratio=0.8132

interpretation:
  The same-flight continuous-command route is no longer blocked at spawn,
  MAVROS, YAML loading, first-target auto-land, or metrics packet loss. The
  clearance-route smokes prove that one aircraft can start moving and collecting
  cloud/occupancy evidence in the clean Factory runtime. They do not prove full
  indoor coverage because they intentionally run only 10-30 targets.

next required action:
  Run a long same-flight clearance-route pass, starting with the 3.0 m / 0.6 m
  route because it is shorter while still barely meeting the planned 0.80
  coverage proxy. If runtime coverage falls below 0.80, rerun with the denser
  2.5 m / 0.6 m route. Do not claim full coverage unless both
  EGO_SINGLE_METRICS.json passes and FACTORY_L2_INDOOR_COVERAGE_PACKET.json
  reports merged_sensor_footprint_coverage_ratio >= 0.80.

long_run_policy:
  Full-route execution is expected to take more than the ordinary 5-minute
  interactive wait budget. It should be treated as an explicitly accepted
  long/background gate and judged by metrics/coverage packets, not by partial
  screenshots.
```

Historical same-flight Diff lawnmower checks:

```text
4wp_smoke:
  Results/sunray_ros1/factory_l2_diff_lawnmower_4wp_stream_smoke_20260705_009/
  backend_exit_code=14
  EGO_SINGLE_METRICS.json exists
  mission_mode=exploration_stream
  planner_position_cmd_raw samples=758
  position_cmd samples=344
  planner command moved about 4.87 m in x
  executed position_cmd moved about 1.78 m in x
  coverage packet status=blocked
  best_single_run_sensor_footprint_coverage_ratio=0.02130681818181818
  blocker=landed_by_truth_false plus expected low coverage for short smoke

dry_run_12wp:
  Results/sunray_ros1/factory_l2_diff_lawnmower_12wp_dryrun_20260705/
  waypoint_count=12
  planned_sensor_footprint_coverage_ratio=0.09588068181818182

runtime_12wp_30s:
  Results/sunray_ros1/factory_l2_diff_lawnmower_12wp_stream_probe_20260705/
  EGO_SINGLE_METRICS.json status=passed, blockers=[]
  mission_mode=exploration_stream
  planner_position_cmd=1509
  position_cmd=856
  raw_lidar/world_cloud=554/554
  occupancy_inflate=222
  landed_by_truth=true
  forwarded_goal_count=3
  position_cmd_motion.x_range_m=5.573
  planner_position_cmd_motion.x_range_m=9.977
  coverage_packet.status=blocked
  merged_sensor_footprint_coverage_ratio=0.026278409090909092
  blocker=indoor_sensor_footprint_coverage_below_threshold
  interpretation:
    Flight, command continuity, lidar/world-cloud, occupancy, and landing are
    good for the bounded 30 s scale check. The remaining blocker is simply
    coverage extent; the aircraft has not flown enough of the route.

full_route_dry_run:
  Results/sunray_ros1/factory_l2_diff_lawnmower_fullroute_dryrun_20260705/
  waypoint_count=203
  estimated_path_length_m=998.1
  estimated_time_at_0.8mps=20.8 min
  planned_sensor_footprint_coverage_ratio=0.9950284090909091

user_entry:
  cmd/启动Factory单机同飞行覆盖建图.cmd

long_run_policy:
  superseded by clearance-route full coverage because the straight full route
  can place targets in obstacle space.
```

2026-07-06 same-flight coverage execution contract:

```text
decision:
  FUEL/RACER/FALCON remain local exploration baselines for Factory L2. The
  current full-indoor map-building route is scripted known-scene support, not
  an unknown-environment autonomous exploration claim.

active_backend:
  Diff-Planner supervised interactive goal-chain
  Scripts/sunray/start_factory_diff_interactive_coverage_probe.ps1
  route generator: Scripts/sunray/generate_factory_l2_clearance_route_waypoints.py
  user entry: cmd/启动Factory单机同飞行覆盖建图.cmd

why_not_z3:
  Source-truth connectivity checks showed that the z=3 flight band cannot be
  promoted as the final full-indoor route: Factory internal obstacles split the
  reachable component enough that the start-connected route cannot cleanly
  satisfy the 0.80 merged sensor-footprint threshold. z=3 remains diagnostic
  evidence only.

promoted_route:
  target_z: 4.0 m
  flight_obstacle_band: [3.5, 4.5] m
  command_clamp_z: [3.60, 4.40] m
  planner_z_band: [3.50, 4.50] m
  virtual_ceiling: 4.50 m
  clearance_grid_step: 6.0 m
  transit_grid_step: 1.5 m
  max_segment: 3.0 m
  coverage_target_min_new_cells: 1
  coverage_target_stop_ratio: 0.90

static_dry_run:
  Results/sunray_ros1/factory_l2_diff_interactive_coverage_segmentclear_z4_g6_t15_seg3_min1_dryrun/
  waypoint_count: 895
  planned_sensor_footprint_coverage_ratio: 0.8235
  segment_clearance_audit.blocked_segment_count: 0

runtime_small_gates:
  Results/sunray_ros1/factory_l2_diff_interactive_coverage_z4_seg3_min1_20goal_probe_20260706_0135/
    DIFF_INTERACTIVE_COVERAGE_GOAL_CHAIN_PROBE.json status=passed
    EGO_SINGLE_METRICS.json status=passed
    completed_goal_count=20
    merged_sensor_footprint_coverage_ratio=0.0678
  Results/sunray_ros1/factory_l2_diff_interactive_coverage_z4_seg3_min1_60goal_probe_20260706_0153/
    DIFF_INTERACTIVE_COVERAGE_GOAL_CHAIN_PROBE.json status=passed
    EGO_SINGLE_METRICS.json status=passed
    completed_goal_count=60
    merged_sensor_footprint_coverage_ratio=0.1701

first_full_run:
  Results/sunray_ros1/factory_l2_diff_interactive_coverage_full_z4_seg3_min1_20260706_022858/
  status: blocked
  DIFF_INTERACTIVE_COVERAGE_GOAL_CHAIN_PROBE.json:
    status: blocked
    completed_goal_count: 447 / 895
    blocker: goal_447/route_672:accepted_goal_stable_hold_not_reached
  EGO_SINGLE_METRICS.json: missing because the backend did not reach a passed
    terminal state
  coverage_packet/FACTORY_L2_INDOOR_COVERAGE_PACKET.json:
    status: blocked
    reason: no_backend_passed_runs_for_merged_coverage
  terminal_diagnosis:
    target: (32.59504, -32.86291, 4.0)
    terminal_truth_position: approximately (35.24230, -31.24170, 4.05547)
    terminal_xy_error: approximately 3.10 m
    terminal_truth_speed: approximately 0.00025 m/s
    terminal_roll_pitch: approximately 29.5 deg
  interpretation:
    Command and raw-command surfaces reached the target region, but truth/odom
    did not. The terminal state is therefore not a simple soft-radius miss. It
    is a route/local-map/controller-saturation boundary problem near
    route_670-672.
  next_action_before_rerun:
    Do not repeat the exact same full configuration as-is. First diagnose
    source-truth clearance, Diff local-map/virtual-wall reachability, and add a
    high-roll/pitch stuck gate or safe route-pruning/rejoin policy for the
    route_670-672 corridor.

full_run_acceptance:
  DIFF_INTERACTIVE_COVERAGE_GOAL_CHAIN_PROBE.json status=passed
  EGO_SINGLE_METRICS.json status=passed
  coverage_packet/FACTORY_L2_INDOOR_COVERAGE_PACKET.json status=passed
  coverage_packet.acceptance.merged_sensor_footprint_coverage_ratio >= 0.80
  no boundary, Z-band, roll/pitch, landed_by_truth, or planner-emergency
  blocker

long_run_policy:
  Run as a background/long job with short polling. Do not use a 5 min
  foreground window as proof of failure because Factory startup consumes a
  large part of that window. Poll partial goal-chain evidence and report
  completed_goal_count, blockers, stability, and coverage trend rather than
  waiting silently.
```

2026-07-06 FUEL same-flight continuous supervisor reopening:

```text
decision:
  The active exploration objective is reopened as FUEL same-flight continuous
  coverage, not Diff known-scene coverage. Diff interactive coverage remains a
  support/fallback map-building route only if FUEL is proven blocked with
  same-flight evidence.

active_backend:
  FUEL exploration_node + MoSim same-flight coverage supervisor
  Scripts/sunray/start_factory_fuel_same_flight_coverage_probe.ps1
  underlying launcher: Scripts/sunray/start_factory_fuel_single_exploration_review.ps1
  supervisor: Scripts/sunray/factory_l2_same_flight_coverage_supervisor.py
  user entry: cmd/启动Factory单机同飞行覆盖建图.cmd

source_truth:
  FUEL's /waypoint_generator/waypoints topic is a trigger for the exploration
  FSM, not a direct waypoint follower. The supervisor must not fake coverage by
  publishing position_cmd or bypassing FUEL. It may only start/retrigger FUEL,
  monitor odometry, command stream, bspline/frontier evidence, and classify
  coverage stalls.

acceptance:
  One PX4/MAVROS/px4ctrl/FUEL runtime, one UAV, no reset-and-respawn tiling.
  The aircraft remains airborne and keeps moving while coverage grows.
  FACTORY_L2_FUEL_SAME_FLIGHT_COVERAGE_PROBE.json is present.
  factory_l2_same_flight_coverage_supervisor.json is present and shows trigger
    events, odometry, bspline, position_cmd, and coverage progression.
  EGO_SINGLE_METRICS.json passes with no safety, Z, boundary, landed_by_truth,
    planner emergency, or command-stream blockers.
  coverage_packet/FACTORY_L2_INDOOR_COVERAGE_PACKET.json passes with
    acceptance.merged_sensor_footprint_coverage_ratio >= 0.80.

execution_policy:
  First run a short bounded gate that proves same-flight movement and coverage
  growth over multiple supervisor trigger cycles. Only after that passes, run
  the long full-boundary gate. Use short polling and partial JSON inspection;
  do not wait silently for more than the bounded policy permits.

blocker_policy:
  If FUEL emits bspline/position_cmd but coverage stalls, classify it as a FUEL
  frontier/map-expansion blocker, not a startup failure. If startup topics,
  MAVROS, PX4 heartbeat, MID360, /clock, or odometry are absent, classify it as
  runtime startup blocker before changing planner parameters.

short_gate_evidence:
  First conservative same-flight short gate:
    Results/sunray_ros1/factory_l2_fuel_same_flight_shortgate_v035_20260706_104809/
  status:
    backend metrics passed; coverage packet blocked only because 240 s short
    gate did not reach the 0.80 full-boundary threshold.
  key metrics:
    EGO_SINGLE_METRICS.json status=passed, blockers=[]
    bspline=82
    position_cmd=7160
    world_cloud=1815
    occupancy_inflate=439
    flight_safety_violation=null
    position_cmd_motion.start_to_end_xyz_m=29.0095
    supervisor_trigger_events=6
    supervisor_sensor_footprint_coverage_ratio=0.0533
    coverage_packet.merged_sensor_footprint_coverage_ratio=0.0600
  interpretation:
    FUEL same-flight continuous movement is now proven for the short gate. The
    previous 0.8 m/s attempt failed by roll/pitch safety, so the promoted
    long-run parameters are conservative: planner max vel/acc 0.35, command
    smoothing max speed 0.35, smoothing max step 0.02 m. The remaining question
    is whether coverage keeps expanding to the accepted indoor boundary before
    the runtime budget or no-growth stall gate.

long_gate_diagnostic:
  Run:
    Results/sunray_ros1/factory_l2_fuel_same_flight_full_v035_takeoff120_20260706_110303/
  Summary:
    Results/sunray_ros1/factory_l2_fuel_same_flight_full_v035_takeoff120_20260706_110303/SUMMARY.md
  status:
    manually_stopped_as_inefficient_coverage_expansion
  key supervisor metrics before stop:
    wall_elapsed_s=1420.3
    bspline=140
    position_cmd=13909
    trigger_events=35
    supervisor_sensor_footprint_coverage_ratio=0.0803
    outside_boundary_rows=0
  interpretation:
    This is valid same-flight diagnostic evidence but not an accepted coverage
    run. FUEL was alive and commanding the aircraft, but the retrigger-only
    supervisor expanded too slowly for Factory full-indoor coverage. Do not
    spend more runtime on this same FUEL retrigger-only strategy. The next
    gate must either implement a true same-flight coverage target-chain
    supervisor and classify it as map-building support, or switch to another
    source-backed exploration planner with a real goal/output contract.

target_chain_entry:
  user entry:
    cmd/启动Factory单机同飞行覆盖建图.cmd
  implementation:
    Scripts/sunray/start_factory_diff_interactive_coverage_probe.ps1
  classification:
    same-flight known-scene map-building support route, not pure FUEL
    autonomous exploration.
  correction:
    The wrapper now separates initial takeoff/pre-goal stability height from
    coverage target height. This prevents the high-clearance z=4 route from
    failing before the first target is published merely because the aircraft
    is still at the low takeoff/ready height.
  dry_run:
    Results/sunray_ros1/factory_l2_same_flight_target_chain_dryrun_g55_20260706_114552/
  dry_run_result:
    waypoint_count=596
    planned_sensor_footprint_coverage_ratio=0.8146
    clearance_grid_step_m=5.5
  acceptance:
    Full coverage still requires the goal-chain probe, backend metrics, and
    indoor coverage packet to pass. The route is not accepted merely because
    the target-chain entry starts or because RViz opens.
```

2026-07-08 HighStar/FUEL source review:

```text
review_packet:
  Results/sunray_ros1/factory_l2_unknown_exploration_highstar_fuel_review_20260708/SUMMARY.md

FUEL status:
  The latest FUEL work exposed perception/frontier parameters through the
  MoSim wrappers and confirmed that FUEL is not a startup failure. Low-altitude
  local exploration still publishes commands, while high-altitude or aggressive
  FOV/frontier parameter sets either finish early with "No coverable frontier"
  or create unstable degenerate planning. Further FUEL work must be source-level
  frontier/FOV/FINISH behavior or an explicit coverage strategy, not another
  blind long parameter run.

HighStar status:
  HighStar is now stored at
  References/Lab/exploration_coverage/HighStar.
  Its minimal ROS1 Noetic core build passed in
  Results/build/highstar_overlay_ws_20260708_try1, producing murder_node and
  traj_exc_node. The build used local shim packages for gflags_catkin and
  glog_catkin to avoid the legacy ExternalProject GitHub download path.

claim boundary:
  HighStar is a source-backed UAV exploration fallback, not a direct runtime
  replacement for FUEL. Its default contract is depth image + camera info +
  odometry and modified RotorS. MoSim's current contract is MID360 point cloud,
  FAST-LIO-like localization, Gazebo/PX4/MAVROS/px4ctrl, and px4ctrl-safe
  command output.

next_adapter_spike:
  1. Use Scripts/sunray/run_highstar_mosim_dry_run_probe.sh against an
     already-running bounded Factory runtime.
  2. It starts Scripts/sunray/highstar_pointcloud_depth_adapter.py and
     Scripts/sunray/highstar_mosim_dry_run.launch.
  3. Require nonempty HighStar SwarmTraj before any px4ctrl bridge.
  4. Bridge SwarmTraj only into the existing px4ctrl/Diff-safe command path,
     never directly to MAVROS as the accepted control authority.
```

2026-07-08 HighStar Factory control-authority update:

```text
latest review:
  Results/sunray_ros1/factory_l2_unknown_exploration_highstar_fuel_review_20260708/SUMMARY.md

local source/root-cause:
  HighStar clean-workspace Factory smoke originally blocked at InitGainRays0
  because runtime viewpoint_z_gate=[0.8,1.8] was applied during offline
  gain-ray dictionary initialization around f_center=(0,0,0). Disable the
  init-time HighStar viewpoint Z gate in the MoSim wrapper; enforce flight Z
  through px4ctrl-safe command fixed_z/clamp/smoothing instead.

evidence progression:
  highstar_zgate_off_smoke_20260708_203021:
    HighStar publishes commands, but raw Z/segment aggressiveness trips
    roll/pitch safety.
  highstar_fixedz_conservative_smoke_20260708_203918:
    fixed z and smoothing avoid attitude violation, but motion is very local
    and stalls.
  highstar_livox_pointcloud_smoke_20260708_204758:
    native pointcloud+Livox produces more commands than pseudo-depth, but
    segment jumps still trip roll/pitch safety.
  highstar_livox_fixedzyaw_ultrasafe_20260708_205448:
    native pointcloud+Livox, fixed z=1.2m, fixed yaw, odom seed, and
    ultra-conservative smoothing produce sustained px4ctrl-safe command
    output with no exploration roll/pitch blocker. It remains blocked by
    generic occupancy topic accounting and short landing timeout, not by
    HighStar startup or direct control-authority absence.

current decision:
  HighStar is promoted from planner dry-run fallback to bounded Factory
  closed-loop spike candidate. It is not accepted as full Factory unknown
  coverage. The next gate must add HighStar-specific map/trajectory metrics
  for /block_map/cloud, /Frontier/grid, and /highstar/position_cmd_preview
  before running a longer 2-5 minute Livox fixed-z/yaw coverage probe.
```

F6 MWORKS/codegen Factory regression:

```text
current result:
  passed at
  Results/sunray_ros1/factory_l2_f6_mworks_codegen_regression_20260702_044942/
input:
  accepted generated controller families from G9/G10
  Factory F2/F3/F4/F5 evidence as runtime baselines
required evidence:
  generated-code/model checks or existing generated-code freeze reused by id
  at least one Factory Diff single-UAV runtime reinjection
  at least one Factory Diff three-UAV runtime reinjection when startup permits
  A/B metrics against the current Factory px4ctrl baseline
acceptance:
  codegen/static checks pass
  Gazebo runtime gate passes with no new controller/planner safety blocker
  failures are classified by controller family, not hidden by switching scenes
```

F7 UE render mirror:

```text
input:
  one or more passed Factory runtime run ids from F2-F6
  UE Factory scene already exported
required evidence:
  replay or live one-way stream manifest tied to those run ids
  UE screenshot/video showing Factory scene, UAV pose, attitude/trail state
  no UE-to-Gazebo/PX4/planner feedback path enabled
acceptance:
  UE display is synchronized enough for review at the declared rate
  the render evidence names the exact Gazebo/PX4/MAVROS source run id
```

F7 is split into bounded sub-gates so the project does not confuse a replay
contract with live UE rendering:

```text
F7a replay contract:
  convert a passed Factory runtime run directory into
  ue_render_frame.jsonl and UE_RENDER_STREAM_MANIFEST.json
  schema must be mosim.ue_render_frame.v1 and
  mosim.ue_render_stream_manifest.v1
  output rate defaults to 10 Hz
  source may be Gazebo truth CSV or MAVROS odom CSV, but the manifest must
  name which source was used
  status can pass without opening UE

F7b live/UDP sidecar:
  only after F7a passes
  publish the same contract at 10 Hz as a one-way display stream
  UE/network delay may drop old frames, but must not back-pressure ROS,
  Gazebo, PX4, MAVROS, FAST-LIO, planners, or px4ctrl

F7c UE visual review:
  capture UE screenshot or video of the Factory scene with UAV pose,
  attitude axes or heading marker, and trajectory trails
  evidence must reference the same F7a/F7b manifest and source run id
```

If F7a passes but F7b/F7c cannot be run because UE editor, receiver, project
state, or window capture is unavailable, record a partial F7 evidence packet:

```text
status: replay_contract_passed_ue_runtime_pending
claim_boundary:
  Data Bridge replay contract is valid for the named Factory run.
  UE runtime display is not yet accepted.
next_required_action:
  open/repair the UE receiver/display endpoint and rerun F7b/F7c.
```

F8 review packet:

```text
input:
  F1-F7 evidence directories
required evidence:
  one summary packet with gate table, run ids, metrics, screenshots/videos,
  command entrypoints, changed files, and remaining limitations
acceptance:
  the user can audit the Factory full-system loop without reading chat history
```

## 5. F1 Repair Strategy

Do not debug Factory L2 first. First make the Factory FS1a wrapper match the
proven Sunray/Goal5 environment, then replace only the world.

Minimum repair sequence:

1. Run Sunray ROS1 preflight through `wsl -d Ubuntu-20.04`.
2. Align `Scripts/sunray/run_factory_l2_sunray_spawn_gate.sh` with the proven
   Goal5 startup environment:
   - source the project-local Livox plugin overlay when present;
   - prepend the Livox plugin overlay to `GAZEBO_PLUGIN_PATH` and
     `LD_LIBRARY_PATH`;
   - strip PX4 Gazebo model path unless a scoped diagnostic proves it is needed;
   - use the Goal5 MID360 startup load-reduction defaults:
     `SUNRAY_MID360_PLUGIN_DOWNSAMPLE=4` and `SUNRAY_MID360_GOAL5_CSV_STRIDE=4`;
   - preserve Factory model path only as scene geometry input.
3. Prove original Sunray world + same wrapper can spawn one
   `sunray150_with_mid360`.
4. Replace only `WORLD_FILE`/Factory model path and rerun FS1a.
5. If factory insertion still fails, test a bounded Gazebo factory plugin load
   timeout increase in the Factory world, because Gazebo explicitly recommends
   `<ignition:model_plugin_loading_timeout/>` when sensor initialization exceeds
   the default.

Every attempt must write a result directory under `Results/sunray_ros1/`.

## 6. Factory Runtime Defaults

Unless a gate proves these are wrong, use the current accepted runtime defaults:

```text
runtime: Ubuntu-20.04 / ROS1 Noetic / Gazebo Classic / PX4 / MAVROS / px4ctrl
entry: wsl -d Ubuntu-20.04
preflight: Scripts/sunray/check_sunray_ros1_runtime_preflight.sh
MAVROS stream target: 100 Hz where supported
MID360 lidar: 20 Hz
MID360 IMU: 200 Hz
PX4 flight-controller IMU simulation target: 400 Hz
point-cloud review size: follow Docs/Workflows/sunray_ros1_execution_checklist.md
```

Do not retune px4ctrl or planner parameters while repairing Factory spawn or
sensor readiness.

## 7. UE Render Mirror Route

After F1-F6 pass, UE work is allowed only as a rendering mirror:

```text
T0 replay: consume an existing Factory run bundle and render pose/trajectory trails in UE.
T1 live sidecar: publish a 10 Hz one-way state stream from ROS/Gazebo to UE.
T2 evidence: record UE screenshot/video plus stream manifest tied to the same run id.
```

UE must not publish control commands, planner targets, estimator feedback, or
truth state into PX4/MAVROS/planners in this route.

Default F7 source selection:

```text
first replay source:
  Results/sunray_ros1/factory_l2_racer_swarm_l1_awff_pairguard10_20260702_044053/
  state_source: uav*_truth.csv
reason:
  this is the latest accepted Factory F5b three-UAV RACER run and contains
  per-UAV position, velocity, roll, pitch, and yaw for display-only replay
optional comparison:
  rerun the same generator with state_source=uav*_odom.csv when reviewing
  MAVROS/local-estimator display alignment
```

The bridge adapter owns display-coordinate conversion. The source CSV remains
in ROS/Gazebo meters, radians, z-up, and original timestamps. The manifest must
record that UE uses centimeters and UE scene binding, while the JSONL frame
keeps ROS/Gazebo meter values for auditability.

## 8. Stop Conditions

Stop and report a blocker when:

```text
Sunray ROS1 preflight fails
Factory FS1a cannot produce nonempty MID360 after the spawn repair sequence
the fix would require changing vehicle model, controller authority, sensor source, or runtime stack
MWORKS login/license/activation blocks codegen or simulation work
UE export/rendering requires replacing the accepted Factory geometry with hand-built proxy geometry
```

When a gate completes or blocks, send one sparse Chinese email through
`Scripts/agent/send_gateway_email_alert.py`.

## 9. FUEL MID360 Frontend And Stability Repair (2026-07-12)

The Factory FUEL lane must not reuse the upstream depth-camera contract
unchanged. The accepted MID360 frontend is:

```text
/cloud_registered + /Odometry
  -> shared camera_init frame and measurement timestamps
  -> FUEL cloud/pose inputs

PX4 EKF / MAVROS local odom
  -> px4ctrl state input
```

Do not feed FAST-LIO odometry directly to px4ctrl. Runtime evidence at
`Results/sunray_ros1/factory_l2_fuel_fastlio_frontend_e3_20260712/` proved a
1.0 synchronized callback ratio and initially zero cloud/pose stamp delta.

The later FUEL stop included a source defect, not a remaining absence of lidar
messages. ASan found an Eigen expression lifetime error in
`FrontierFinder::splitHorizontally`: `auto` retained lazy views of temporary
`real()` results. The repair stores owned fixed-size Eigen values, uses
`SelfAdjointEigenSolver` for the symmetric covariance matrix, rejects
non-finite/degenerate clusters, and requires every recursive split to produce
two nonempty, strictly smaller children. Keep the upstream PCL `VoxelGrid`;
the earlier PCL destructor failure was secondary heap damage, while a
project-owned `std::map` voxel replacement caused unacceptable 97% CPU stalls.

Release regression
`Results/sunray_ros1/factory_l2_fuel_fastlio_release_pcl_e10_20260712/`
passed 80 s of Gazebo exploration with 9 B-splines, 8041 planner commands,
about 7.86 m displacement, and no `double free`, process death, or blocker.
Its coverage packet remains blocked at sensor-footprint coverage `0.037642`
and path coverage `0.004261` against the full-indoor `0.80` threshold. This
proves the synchronized MID360 message path and local FUEL runtime are
executable; it does not prove that the whole perception model is lidar-native.
The accepted E10 launch still used `perception_omni_horizontal=false`, so
frontier visibility was filtered by the upstream depth-camera left/right FOV.
It also configured a fixed `16 m x 16 m x 3 m` SDF map, while upstream FUEL
examples use a fixed global map such as `40 m x 20 m x 5 m`. Therefore the next
diagnostic is not a project-owned rolling-window implementation. Run bounded
`40 m` then `80 m` fixed-map A/B regressions with MID360 horizontal omnidirectional
visibility, an origin/bounds audit, and otherwise unchanged E10 parameters.
Only if coverage growth remains blocked after that test may global map/window
migration be considered.

The first 40 m A/B is recorded at
`Results/sunray_ros1/factory_l2_fuel_mid360_fixed40_ab_20260712/`. With
`0.1 m` resolution and `omni_horizontal=true`, the synchronized lidar path
remained healthy and FUEL produced one B-spline, but `exploration_node` reached
about 95% CPU and a planning cycle took 2.597 s. The bounded run was stopped at
the five-minute wall-time limit; its partial 8 m sensor-footprint proxy was
`0.024858`. Do not run 80 m at 0.1 m. The next A/B is 40 m at 0.2 m resolution.

The follow-up A/B changed the diagnosis materially. At `0.2 m` resolution,
publishing the complete occupancy cloud at 1 Hz instead of the previous 10 Hz
removed the map-display/planning contention without reducing map integration or
planning update rates. The 80 m gate at
`Results/sunray_ros1/factory_l2_fuel_mid360_fixed80_res02_map1hz_v05_20260712/`
passed with 54 B-splines and no safety blocker. Its mean planning time was about
0.024 s and `exploration_node` CPU dropped from about 95% to roughly 10-14%.

Do not interpret `new_frontiers=0` messages after the execute window as FUEL
termination. In the 80 m evidence, the configured 30 s execute interval ended
at simulation time 64.298 s; FUEL still retained 28 visitable frontiers and
continued publishing B-splines during the scripted landing/cleanup interval.
The stop was imposed by the runtime gate, not by `FINISH` or loss of MID360
input.

The complete accepted Factory indoor envelope is now executable as one fixed
FUEL map. The safe short baseline is:

```text
map size                 175.65987 x 63.99956 x 3 m
resolution               0.2 m
horizontal perception    omnidirectional
all-map review publish   1 Hz
planner max velocity     0.3 m/s
planner max acceleration 0.2 m/s^2
```

Evidence is
`Results/sunray_ros1/factory_l2_fuel_mid360_full176x64_res02_map1hz_v03_a02_30s_20260712/`.
It passed the Gazebo/PX4/MAVROS/px4ctrl safety gate, ran the full 30.002 s
execute window, generated 56 B-splines and 3777 planner commands, and had no
flight-safety violation. Planning mean/max were about 0.030/0.081 s. The
full-indoor sensor-footprint proxy reached 0.0355 in this short run; this proves
continued expansion, not the required 0.80 full-coverage acceptance.

`start_factory_fuel_single_exploration_review.ps1` therefore defaults to the
envelope dimensions above. The original 0.3/0.2 motion limits were the first
safe diagnostic baseline; the later frame-corrected speed A/B below supersedes
them for normal Factory FUEL runs. A caller may
still request a smaller diagnostic window explicitly. The next runtime task is
a bounded long-duration growth run using this baseline. Do not reintroduce the
16 m default, depth-camera horizontal FOV, 0.1 m full map, or 10 Hz complete-map
publication.

Long runs must distinguish ROS simulation time from wall time. The first 120 s
growth attempt was externally terminated with exit code 124 at simulation time
about 97.5 s while FUEL still retained 12 frontiers and continued publishing
trajectories. The old wrapper computed wall timeout as `execute_s + 180`, which
assumed real-time factor 1.0. The complete Factory map currently runs near a
0.2-0.3 real-time factor, so this was a harness timeout, not planner FINISH.
The wrapper now computes its default wall timeout as
`execute_s / minimum_expected_real_time_factor + 180`, with the conservative
Factory default `minimum_expected_real_time_factor=0.20`. Explicit
`MissionTotalTimeoutS` still overrides this calculation.

The timeout-corrected 120 s retry exposed a separate control-interface safety
defect before full duration: the adapted reference advanced more than 3 m ahead
of the aircraft while velocity and acceleration feed-forward terms were zeroed.
The vehicle accelerated to about 0.83 m/s and truth roll exceeded 45 degrees,
although the configured planner/reference speed was 0.3 m/s. This is not a
MID360 or frontier failure. The existing `goal4_position_cmd_safety_adapter`
already supports an odometry-relative target guard, so the Factory FUEL wrapper
now enables it and projects the px4ctrl-facing XY reference to at most 0.6 m
from current MAVROS odometry. Raw FUEL commands remain unchanged and recorded;
the guard is an execution safety boundary, not a replacement planner.

Spatial alignment and command-dynamics follow-up changed the diagnosis. Raw
FAST-LIO `camera_init` odometry and cloud were not in Factory/MAVROS local.
One initialized rigid transform now aligns both inputs before FUEL. After that,
retaining raw B-spline velocity/acceleration while limiting position to
`0.3 m/s` produced a truth attitude peak near 68.96 deg. The adapter now derives
velocity from final published position and zeros acceleration/jerk.

The bounded runtime regression at
`Results/sunray_ros1/factory_l2_fuel_mid360_spatial_dynamics_v2_retry_30s_20260712/`
passed, landed by truth, published 1048/1048 aligned clouds, bounded final
command speed to 0.300000 m/s, and reduced exploration truth roll/pitch peak to
20.35 deg. Coverage remains blocked at 0.01953125 because the executed path
covered only about 0.64 x 1.12 m while FUEL continued emitting B-splines and
retaining frontiers. The next gate is long-duration progression with
raw/aligned/executed trajectory comparison, not another lidar message, FOV,
timestamp, or frame experiment.

The progression run found a fixed frontend frame-contract error that static
initialization could not expose. The FUEL-specific FAST-LIO adapter used
`input_pose_frame=base`, bypassing the MID360 mount yaw of `4.712389 rad`.
During motion, MAVROS moved about 4.65 m along local `-Y` while the aligned
FAST-LIO output moved about 4.71 m along `+X`. The adapter now uses
`input_pose_frame=livox` with the configured MID360 mount xyz/rpy. The
PointCloud2-to-Livox bridge uses `instantaneous` point time because the Gazebo
PointCloud2 frame does not contain per-point acquisition timestamps.

Corrected 60 s evidence is:

```text
0.3 m/s baseline:
  Results/sunray_ros1/factory_l2_fuel_fastlio_framefix_60s_20260712/
  backend passed; coverage 0.040838; truth span about 15.19 x 2.67 m

1.0 m/s, 0.8 m/s^2:
  Results/sunray_ros1/factory_l2_fuel_fastlio_framefix_v10_retry_60s_20260712/
  backend passed; coverage 0.089134; truth span about 19.77 x 20.84 m
```

Disabling FUEL local refinement did not improve coverage (`0.038707`), so it
is not the current primary blocker. The speed A/B more than doubled 60 s
coverage without a flight-safety violation. Timestamp-matched FAST-LIO versus
MAVROS diagnostics at 1.0 m/s report mean/P95/max XY residuals of approximately
0.052/0.096/0.127 m; larger values from the old online diagnostic were caused
by comparing messages up to 0.27 s apart. The diagnostic now keeps a bounded
MAVROS history and selects the nearest timestamp.

The 1.0 m/s short run is not the frozen default. Its 120 s continuation reached
about 51 x 12 m of motion but was stopped near simulation time 116 s when
actual speed rose to about 2.01 m/s and MAVROS roll/pitch exceeded 45 degrees.
The long-safe motion baseline is instead `0.6 m/s` maximum velocity,
`0.5 m/s^2` maximum acceleration, and `0.6 m/s` command smoothing. Evidence at
`Results/sunray_ros1/factory_l2_fuel_fastlio_framefix_v06_120s_20260712/`
passed the complete 120.017 s execute window with 123 B-splines, no safety
violation, 0.064986 sensor-footprint coverage, and timestamp-matched FAST-LIO
XY residual of about 0.047 m mean / 0.082 m max. The Factory FUEL wrapper now
defaults to this long-safe configuration.

This is an executable lidar-native exploration repair, not full-indoor
acceptance: `0.064986 < 0.80`. It proves that the corrected FUEL lane continues
moving and expanding for two simulation minutes; a full-map completion claim
still requires a substantially longer accepted run and the same coverage
packet. Do not promote the unsafe 1.0 m/s short result or infer full coverage
from a short speed A/B.

### 9.1 Fixed 64 m long-duration diagnosis

The article-scale follow-up uses
`Config/gazebo/scene_profiles/factory_l2_fuel_fixed64_diagnostic_envelope.json`
and a centered `64 m x 64 m x 3 m` fixed FUEL map. It keeps the corrected
MID360/FAST-LIO frontend and evaluates coverage against the same 64 m boundary,
not the complete `175.66 m x 64 m` Factory denominator.

The `0.6 m/s` attempt at
`Results/sunray_ros1/factory_l2_fuel_mid360_fixed64_long300_cleanfg_20260712/`
did not reach 300 s. FUEL remained active with 103 B-splines and healthy
cloud/pose synchronization, but the flight reached about `2.04 m/s` and
`67.7 deg` roll/pitch after about 74 s of exploration. The position-command
adapter had bounded the published reference to `0.6 m/s`; therefore this is a
trajectory-to-controller dynamics limit, not a MID360 disconnect or FUEL
`FINISH`. An `original` px4ctrl comparison failed even earlier, so changing
controller profile alone does not remove the interface excitation.

The safe long run is
`Results/sunray_ros1/factory_l2_fuel_mid360_fixed64_l1_v03_long300_20260712/`:

```text
execute duration                    300.006 s simulation time
backend status                      passed
FUEL B-splines                      428
64 m sensor-footprint coverage      0.2373046875
FAST-LIO aligned clouds             6501 received / 6501 published / 0 dropped
FAST-LIO versus MAVROS XY residual  0.0147 m mean / 0.0384 m max
truth peak speed                    0.924 m/s
truth peak roll/pitch               28.70 deg
```

The 30 s coverage progression is stored in `coverage_progression_30s.json`.
Coverage grew from about `0.074` at 30 s to `0.129` at 120 s, `0.194` at
210 s, and `0.237` at 300 s. The final 30 s added only two 2 m footprint cells,
while FUEL still retained about 39 visitable frontiers. This is not a frontend
failure and not natural completion. It is a global-tour/coverage-efficiency
and runtime-cost problem after the safe motion limit is reduced to `0.3 m/s`.

Do not run another blind full-Factory duration extension. The next source-level
gate must explain why retained far frontiers produce little new 64 m coverage,
and must compare selected global-tour targets, executed target progress, and
new coverage cells before changing frontier weights or adding a supervisor.

### 9.2 Dynamic-interface follow-up result

The command-side dynamic limiter follow-up did not make the `0.6 m/s` planner
configuration safe for a full fixed-64 run. The best short candidate used a
`0.5 m/s` final command speed, `0.7 m/s2` acceleration limits, a `0.5 m` odom
lookahead, and stable takeover at absolute `z=1.2 m`. Its 30 s gate passed at
`0.724 m/s` truth peak and `14.9 deg` peak roll/pitch.

The directly comparable long run is:

`Results/sunray_ros1/factory_l2_fuel_true_fixed64_dyn_cmd05_long300_20260712/`

It explicitly used the same centered `64 m x 64 m` envelope as the `23.73%`
baseline. It stopped after about `189.5 s` of exploration when truth
roll/pitch crossed the `45 deg` safety gate. Recorded peaks were `2.16 m/s`
truth speed and `52.32 deg` truth roll/pitch. FUEL produced `275` B-splines;
FAST-LIO received and published `4237/4237` aligned clouds with zero drops.
This is a trajectory-to-controller tracking blocker, not FUEL completion or a
MID360 disconnect.

An earlier run named `factory_l2_fuel_fixed64_dyn_cmd05_long300_20260712` used
the full `175.66 m` Factory X extent because the wrapper default had changed;
its fixed-64 coverage packet is not a valid baseline comparison. Future
fixed-64 runs must pass both `FuelWindowXYM=64` and `FuelWindowYM=64`
explicitly and verify the generated startup manifest before takeoff.

Do not continue blind scalar speed/acceleration tuning. The next admissible
change must be controller-aware: either time-scale the trajectory using
measured tracking error and curvature, or change the handoff contract so the
controller receives a dynamically feasible trajectory with an explicit
tracking-error safety state. Re-run the short gate first, then the same 300 s
fixed-64 gate. Until that passes, `23.73%` at the safe `0.3 m/s` configuration
remains the accepted coverage baseline.
## FUEL 2 m/s 门禁（2026-07-13）

Factory L2 的单机 FUEL 速度验证必须按以下顺序执行：

1. 固定 `EGO_MAX_VEL=2.0 m/s`、`EGO_MAX_ACC=1.5 m/s^2`，保留原生 FUEL B-spline，不启用桥接平滑、位置限幅或单步截断。
2. 当前长测基线使用 `EKF2_EV_CTRL=7`（水平/垂直位置 + 水平速度），但 FAST-LIO pose、velocity 和 covariance 必须通过同一个 `/uav1/mavros/odometry/out` 消息进入 MAVROS `odom` 插件，再由 MAVLink `ODOMETRY` 送入 PX4。FAST-LIO 门禁中禁止继续并行使用 Sunray `external_fusion` 和 MAVROS `vision_speed` 分流。
3. 每轮必须同时保存 `/uav1/mavros/estimator_status`、MAVROS odom 插件订阅与频率证据、统一 odometry 适配器诊断、PX4 ULog、外部定位一致性、真实姿态/速度和 FUEL B-spline 重规划日志。
4. 45 秒门禁通过条件：真实峰值速度进入 `1.8-2.2 m/s`、最大滚转/俯仰低于 `45 deg`、轨迹发布间隔不超过 `10 s`、无连续重规划失败、外部定位一致性比例不低于 `0.80`。
5. 只有 45 秒通过后才允许运行 120 秒，再通过后才允许运行 300 秒；任何门禁失败都不得把后续时长当作有效证据。

当前诊断证据：

每次 live gate 必须将 `ROS_LOG_DIR` 指向本次 `Results` 目录下的独立子目录，不能继续复用共享 `~/.ros/log`。共享日志目录曾累积到 21GB，并与 Gazebo/PX4 spawn/transport 崩溃同时出现；日志隔离是运行前置条件，但不能单独作为 spawn 根因修复的证明。

- `r30` (`Kp/Kv=4/4`) 已达到约 `1.93 m/s`，但探索阶段最大倾角约 `51.5 deg`，不接受为控制证据。
- `r31`（官方 `Kp/Kv=1.5/1.5`）峰值速度约 `2.01 m/s`、最大倾角约 `24.76 deg`，PX4 `estimator_status` 状态有效；但约仿真 `t=63.3 s` 起 FUEL 连续 8 次动态可行性重规划失败，最后一次轨迹发布到结束间隔约 `25.1 s`，因此门禁为 `blocked`。
- 下一步只调查 FUEL 动态可行性失败的原因（边界保持、重规划起点速度/加速度、时间下界与地图候选点），不得先调高控制器增益或把失败轨迹替换成平滑/限幅轨迹。

### 9.3 上游对照与当前修复边界

已对照上游 `HKUST-Aerial-Robotics/FUEL` 的 README 和
`plan_manage/src/planner_manager.cpp`。上游 `planExploreTraj` 的流程是：
以当前速度/加速度构造多项式初轨迹，参数化为 B-spline，执行优化后直接发布；
上游没有当前补丁中的“向量范数采样门禁 + 失败即拒绝 + 重规划内二次时间修复”组合。

当前 r31 日志表明，问题不是单纯的速度上限：在同一失败候选中，初始
`sample_peak_acc=1.886`，局部 `reallocateTime()` 后反而出现
`2.602~3.171 m/s^2`，继续重分配仍未收敛。源码中该函数按导数控制点局部修改
knot，而当前补丁随后又以统一 knot 重建并重写前三个控制点；两套时间参数化叠加，
会破坏内部曲率，不能作为已验证的恢复策略。

因此下一轮只允许以下实验：

1. 从 r31 失败窗口固定起始 P/V/A、控制点、knot 和约束，离线复现
   `checkRatio()`、`checkFeasibility()` 与 `reallocateTime()` 的变化；
2. 禁止在同一候选上混用局部 `reallocateTime()` 与统一 knot 重建，比较“重新生成
   更长初始时间的候选”是否保持 P/V/A 连续并收敛；
3. 只有离线候选满足位置连续、起始速度/加速度连续、速度/加速度上限和有限轨迹年龄，
   才进入 45 秒 Gazebo 门禁；
4. 若 120 秒仍失败，形成源码调用链、失败候选数据和对照运行包，停止盲目调参。

本节采用的公开上游来源：
`https://github.com/HKUST-Aerial-Robotics/FUEL`、
`https://arxiv.org/abs/2010.11561`。上游资料只用于实现对照，不能替代本项目的
ROS1/Gazebo/PX4/MAVROS 实时证据。
## Current FUEL 2 m/s diagnostic gate (2026-07-13)

The r31/r32/r33 comparison found that planner-declared speed stayed near
1.98 m/s, while r33 truth reached 3.55 m/s after odometry and command tracking
diverged. The first source-level defect identified is the FUEL planner odom
frame: MAVROS odometry twist is body-frame, but the position-only local-frame
bridge passed it to FUEL as world-frame. The minimal correction rotates the
linear and angular twist with the odometry orientation and labels the output
child frame as `world`.

Acceptance order after this correction:

1. static compile, quaternion/frame contract test, and recorder header-time audit;
2. 45 s Gazebo gate at approximately 2 m/s;
3. compare planner/raw command, px4ctrl-facing command, odom, and truth using
   message header time, not callback arrival time;
4. only if command/odom error stays bounded and no truth safety gate trips,
   proceed to 120 s, then 300 s.

Do not compensate this defect with smoothing, position clamping, gain inflation,
or a substitute planner. A 45 s failure must be classified by frame,
trajectory handoff, estimator, or controller tracking evidence before another
runtime change.
### FUEL 2 m/s long-run gate: height-contract invariant

The FUEL planner box and the px4ctrl-facing position-command adapter must use
the same effective **world-frame** Z interval. The Factory launcher derives
`DIFF_CMD_MIN_Z` and `DIFF_CMD_MAX_Z` from `FUEL_BOX_MIN_Z` and
`FUEL_BOX_MAX_Z` unless explicit command bounds are supplied. A disjoint
interval is rejected before Gazebo/PX4 startup. `FUEL_CMD_FIXED_Z` is empty by
default so native FUEL Z is preserved; a fixed Z is permitted only when it is
inside the command interval. This prevents a local-height/world-height
contract error from silently clamping every FUEL command and invalidating a
controller result.

For the 2 m/s gate, keep smoothing, position-based velocity recomputation, and
extra target projection disabled. Verify
`position_cmd_safety_adapter.json` has `fixed_z=null`, zero high/low clamp
counts, and raw/published Z ranges inside the same interval before accepting
the run. The required runtime sequence remains 45 s, 120 s, then 300 s; the
45 s result is only a short-gate pass and does not establish long-run
stability.

2026-07-13 bounded results:

- `factory_l2_fuel_odom_worldframe_fix45_r40_20260713`: passed, 45.018 s,
  zero Z clamps.
- `factory_l2_fuel_odom_worldframe_fix120_r41_20260713`: passed, 120.015 s,
  117 B-splines, zero Z clamps.
- `factory_l2_fuel_odom_worldframe_fix300_r42_20260713`: blocked only by
  `planner_trajectory_stale`. The exploration node remained alive and the
  aircraft settled safely, but the final planning callback entered at
  simulation time 264.956 s and produced no later B-spline. The last trajectory
  publish was 264.448 s and terminal staleness was 86.884 s. Earlier
  `open set empty` and NLopt failures recovered; this terminal event did not.
  Treat this as a FUEL planner callback/hang investigation, not a px4ctrl or
  command-height failure.

### 9.4 r48/r52 fusion and regenerated-feasibility closeout

The r48 fusion diagnosis at
`Results/sunray_ros1/factory_l2_fuel_fusiondiag_gate45_r48_20260713_133549/`
showed that the estimator diverged before the controller became unsafe:

```text
FAST-LIO aligned velocity divergence  65.656 s
PX4 local XY divergence               65.855 s
PX4 local Z divergence                79.255 s
```

Position-only external vision is therefore not an accepted 2 m/s long-run
configuration. r52 then added a timestamp-checked MAVROS `vision_speed` stream
and used `EKF2_EV_CTRL=7`; that short run is retained as historical evidence,
but it no longer establishes that PX4 fused external velocity.

The previous dynamic-feasibility repair was also rejected because repeated
knot modification could stretch an approximately 1.5 s local trajectory past
20 s and starve FUEL replanning. The replacement regenerates every candidate
from the original path points and requested start P/V/A, uses a vector-norm
tolerance of `0.01`, limits total time growth to `2.0x`, and rejects a candidate
that cannot satisfy the bound. It does not smooth, clamp, project, or replace
the native planner command at the controller boundary.

The first accepted short gate is:

`Results/sunray_ros1/factory_l2_fuel_evvel_dynregen_gate45_r52_20260713/`

```text
gate duration                         45.001 s simulation time
backend metrics                       passed
FUEL B-splines                        44
planner commands                      5260
truth peak speed                      1.9307 m/s
truth peak roll/pitch                 24.34 deg
minimum exploration height           1.139 m
maximum B-spline interval             2.029 s
terminal trajectory age               0.803 s
vision-speed publishes                1501 / 1501, zero drops
vision-speed mean / P95 / max age     51.3 / 108 / 209 ms
fusion divergence classification      no sustained position divergence
safety violations                     none
```

The subsequent r54 120 s run invalidated the split-interface assumption. At
approximately `123.16 s`, PX4 local Z jumped from about `1.21 m` to `2.83 m`
while Gazebo truth and aligned FAST-LIO vision Z stayed near `1.15 m`. The run
is classified as `px4_estimator_divergence_after_consistent_mavros_input`:

`Results/sunray_ros1/factory_l2_fuel_evvel_dynregen_gate120_r54_20260713_163140/`

The runtime is MAVROS `1.20.1` with PX4 `1.14.0`. PX4 v1.14 handles
`VISION_POSITION_ESTIMATE` and `ODOMETRY` in `mavlink_receiver.cpp`, but has no
receiver branch for `VISION_SPEED_ESTIMATE`. Therefore the r52/r54 chain sent
pose to PX4 through Sunray `external_fusion`, while the velocity message emitted
by MAVROS was not consumed by PX4. Sunray `ExternalPosition.h` also rewrites the
pose stamp to `ros::Time::now()`, whereas the velocity adapter preserved the
measurement stamp. The split path cannot guarantee one pose/velocity sample or
one time base.

### 9.5 Unified MAVLink ODOMETRY correction

The accepted correction is one synchronized interface:

```text
/mosim/fastlio/odom_aligned
  -> fastlio_odom_to_mavros_odometry.py
  -> /uav1/mavros/odometry/out
  -> MAVROS odom plugin
  -> MAVLink ODOMETRY
  -> PX4 EKF2
```

The ROS message uses `header.frame_id=odom` and
`child_frame_id=base_link`. Pose remains in local ENU. The aligned FAST-LIO
linear velocity is world-frame, so the adapter rotates it by the inverse body
attitude into body FLU before publication, as required by ROS REP-147 and the
MAVROS 1.20.1 odom plugin. Pose, velocity, covariance and header stamp are
emitted from one original measurement. Nonfinite, zero-stamp, stale, future,
duplicate and out-of-order samples are rejected and counted in JSON evidence.

This interface change reopens the sequence at 45 s. Only after the new 45 s
gate proves a loaded MAVROS odom plugin, nonempty synchronized odometry, PX4 EV
position/velocity fusion without local-Z reset, `1.8-2.2 m/s` peak speed,
roll/pitch below `45 deg`, and continuing FUEL replans may the 120 s gate run.
The 300 s gate remains inadmissible until 120 s passes. No gain change,
smoothing, position projection, or substitute planner is part of this repair.

The first unified-interface run is retained at:

`Results/sunray_ros1/factory_l2_fuel_mavlink_odom_gate45_r55_20260713/`

Its flight metrics passed the 45 s mission gate and the adapter published
`1474/1478` samples at `19.41 Hz` measurement time with zero nonfinite, future,
duplicate, out-of-order, or frame-mismatch drops. Four samples (`0.27%`) were
older than the explicit `250 ms` acceptance window and were correctly rejected.
The odometry gate therefore permits at most `max(5, ceil(received * 1%))` stale
drops; it still requires every structural/error drop count to remain zero.

The captured PX4 ULog must also pass
`Scripts/sunray/analyze_px4_ev_fusion_ulog.py`. For r55, EV position, velocity,
and height became active together at `18.63 s` and did not drop afterward.
Fusion fractions were `99.86%`, `99.66%`, and `99.86%`; no vision-data timeout
or post-fusion reset occurred. Three isolated EV velocity innovation rejections
were below the `1%` rejection limit. This ULog result confirms that PX4 consumed
the MAVLink `ODOMETRY` velocity; topic publication alone is not sufficient
evidence.

The first repeated 120 s gate after r56 was:

`Results/sunray_ros1/factory_l2_fuel_mavlink_odom_gate120_r57_20260713/`

It stopped near simulation time `129.38 s`. FAST-LIO odometry dropped
`56/2118` samples as older than `250 ms`; PX4 reported four
`vision_data_stopped` events, repeatedly disabled EV position/velocity/height,
and reset the local estimate. MAVROS local Z fell to `-0.027 m` while Gazebo
truth remained at `1.221 m`. This is an estimator-input continuity blocker, not
a controller gain or FUEL trajectory blocker.

The same run emitted `2250` PCL VoxelGrid overflow warnings. The active FAST-LIO
localization leaf sizes were `0.02 m`, while the local MID360 reference launch
uses `0.5 m`. For a 360-degree scan with a `40 m` detection range, `0.02 m`
can overflow PCL's integer voxel-grid index product and defeat downsampling.
The first bounded correction used `0.05 m` for FAST-LIO internal surf/map
voxels while keeping RViz accumulated-cloud display density at `0.08 m`.
The 45 s r58 gate passed with zero VoxelGrid overflow warnings, `1507/1507`
odometry samples published, no stale drops, and EV position/velocity/height
fusion each at `99.87%`. The repeated 120 s r59 gate still blocked at
simulation time `76.10 s`, but with a different failure: FAST-LIO continued
publishing at 20 Hz with zero stale drops while its timestamp-matched motion
temporarily fell to roughly one quarter of PX4 local motion. PX4-to-FAST-LIO
XY residual rose from about `0.03 m` to `0.80 m`; EV position and velocity
innovations were rejected, estimator resets followed, and truth roll/pitch
crossed `45 deg`. Thus `0.05 m` fixes processing continuity but is not an
accepted MID360 registration baseline.

The next one-variable A/B uses the upstream MID360 internal leaf sizes of
`0.5 m` for both surf and map. FUEL, px4ctrl, message rates, trajectory handoff,
and the `0.08 m` RViz review voxel remain unchanged. Acceptance still requires
zero VoxelGrid overflow warnings, bounded stale bursts, no registration stall
large enough to break EV fusion, and the unchanged
`45 s -> 120 s -> 300 s` gate order.

The interrupted-finalization r60 45 s run contains complete Gazebo metrics and
ULog evidence even though the outer shell stopped before writing every final
manifest. It passed flight safety at `1.889 m/s` truth peak with `33.58 deg`
peak roll/pitch, published `1417/1417` FAST-LIO odometry samples with zero stale
drops, and emitted zero VoxelGrid overflow warnings. EV position and height
fusion each reached `99.86%` with no rejection, control-flag drop, timeout, or
post-fusion reset. EV velocity alone reached `98.87%`: a `0.648 s` rejection
burst occurred during the most dynamic segment. Synchronized diagnostics show
FAST-LIO velocity error near `0.128 m/s` at the 95th percentile with rare peaks
near `0.50 m/s`, so the previous declared velocity standard deviation of
`0.20 m/s` was overconfident. The next one-variable correction declares
`0.35 m/s` velocity standard deviation; it does not smooth or alter the
measurement, planner trajectory, controller command, or controller gains.

### 9.6 Obstacle-clearance root cause and long-run acceptance

The next 300 s attempt, `r63`, showed that the remaining failure was not an
unbounded native FUEL trajectory or an initial FAST-LIO registration failure.
Synchronized truth, command, attitude, and estimator evidence showed this
sequence:

1. the vehicle's truth displacement nearly stopped beside an obstacle while
   FUEL and px4ctrl continued commanding motion and increasing pitch;
2. the physical contact/stuck condition preceded the large FAST-LIO/PX4
   disagreement;
3. EV innovation rejection, local-estimator resets, and the final attitude
   safety violation occurred after the contact condition.

The active Factory wrapper had inherited
`sdf_map/obstacles_inflation=0.099 m`. At the current `0.2 m` FUEL grid
resolution this protects only one occupied voxel and does not provide a
reliable clearance margin for the physical Sunray150 envelope. The existing
Sunray FUEL simulation launch uses `0.35 m`; at the same grid resolution it
protects two voxels. The Factory speed-gate wrapper now defaults
`FUEL_OBSTACLES_INFLATION` to `0.35`, while still allowing an explicit test
override. This is a planner-map/vehicle-clearance correction, not controller
gain tuning or command smoothing.

The required sequence then passed without another runtime change:

| Gate | Evidence | Truth peak speed | Peak roll/pitch | Truth Z range | B-splines | FAST-LIO odometry | EV fusion result |
|---|---|---:|---:|---:|---:|---:|---|
| 45 s | `Results/sunray_ros1/factory_l2_fuel_mavlink_odom_gate45_r64_20260713/` | 1.9720 m/s | 22.77 deg | 1.182-1.376 m | 50 | 1571/1571 at 19.998 Hz | passed; no rejection or reset |
| 120 s | `Results/sunray_ros1/factory_l2_fuel_mavlink_odom_gate120_r65_20260713/` | 1.8687 m/s | 20.57 deg | 1.184-1.336 m | 118 | 3039/3039 at 19.993 Hz | passed; no reset |
| 300 s | `Results/sunray_ros1/factory_l2_fuel_mavlink_odom_gate300_r66_20260713/` | 1.9652 m/s | 21.77 deg | 1.101-1.429 m | 281 | 6689/6689 at 19.972 Hz | passed; one isolated velocity rejection, no reset |

All three runs emitted zero FAST-LIO adapter drops and zero PCL VoxelGrid
overflow warnings. In `r66`, EV position, velocity, and height fused for
`99.9701%`, `99.9552%`, and `99.9701%` of samples; the maximum fused-sample
gap was `0.104 s`, no EV control flag dropped after activation, and no
post-fusion estimator reset occurred. The native FUEL stream remained fresh
through the 300 s exploration interval.

Acceptance boundary: this closes the approximately-2-m/s long-duration
tracking and estimator-continuity gate for the current
FUEL + px4ctrl `l1_awff` + FAST-LIO/MAVLink ODOMETRY route. It does not prove
80% Factory indoor coverage, full-map completion, multi-UAV exploration, or UE
display acceptance. Coverage remains a separate mission-level gate.

### 2026-07-14 Native FUEL 600 s fixed-64 coverage gate

The unmodified native-FUEL coverage route was extended to 600 s without
enabling the project coverage-expansion selector or same-flight coverage
supervisor:

`Results/sunray_ros1/factory_l2_fuel_mavlink_odom_gate600_r67_20260713/`

The backend remained valid for the full run: `EGO_SINGLE_METRICS.json`,
`FASTLIO_MAVROS_ODOMETRY_GATE.json`, and `PX4_EV_FUSION_GATE.json` all report
`status=passed`. The run completed 600.006 s of exploration, reached
1.954 m/s truth peak speed and 22.99 deg peak roll/pitch, produced 665
B-splines, and had no flight-safety violation. FAST-LIO published
12681/12681 accepted odometry messages at 19.982 Hz with zero adapter drops.
EV position, velocity, and height fused for 99.984%, 99.976%, and 99.984% of
samples; one isolated velocity innovation rejection occurred, with no
post-fusion estimator reset or EV control-flag drop.

The fixed `64 x 64 m` mission coverage packet is:

`Results/sunray_ros1/factory_l2_fuel_mavlink_odom_gate600_r67_20260713/coverage_packet_fixed64/FACTORY_L2_INDOOR_COVERAGE_PACKET.json`

It reports 655/1024 sensor-footprint cells (`63.9648%`) and 141/1024 path
cells (`13.7695%`) against the `80%` threshold. The 30 s progression is in
`coverage_progression_30s.json`. Coverage reached `45.3125%` at 150 s, stayed
unchanged through 420 s while native FUEL repeatedly selected a near residual
frontier, then resumed and reached `63.9648%` at 600 s. The last 150 s added
15.2343 percentage points, so the planner was not permanently deadlocked, but
the long near-frontier loop made native coverage too inefficient to pass the
gate. The 600 s result is only 1.1718 percentage points above the accepted
300 s result (`62.7930%`).

Decision: native FUEL remains a valid approximately-2-m/s closed-loop local
exploration baseline, but it does not pass fixed-64 coverage and must not be
reported as full-map autonomous exploration. The next coverage experiment may
enable the already source-backed coverage-expansion/global-selector mechanism
under a separate A/B gate. Do not change controller gains, FAST-LIO timing, or
the accepted obstacle-clearance baseline to hide this mission-level ranking
problem.

### 2026-07-14 Fixed-64 acceptance and complete-map result

The coverage-expansion/global-selector A/B is complete. The fixed `64 x 64 m`
run at
`Results/sunray_ros1/factory_l2_fuel_frame_unified_selector_r83_300s_20260714_060951/`
passed the declared `80%` gate with `82.32%` sensor-footprint coverage and
`16.89%` path coverage. Its backend metrics also passed. This supersedes the
earlier `r67` and `r72` fixed-64 coverage blockers; retain those runs only as
root-cause and regression evidence.

The complete Factory envelope is `175.65987 x 63.99956 m`. On this larger map,
the accepted `0.5 s` fixed-64 trajectory handoff horizon was shorter than some
full-map planning cycles. Valid trajectories were discarded after the
predicted start time, producing a `31.505 s` maximum trajectory gap in `r90`.
`Scripts/sunray/run_factory_l2_fuel_full_map_gate.sh` now defaults only the
complete-map route to `FUEL_REPLAN_TIME_S=3.0`; fixed-64 behavior remains
unchanged. This parameter predicts a future PVA-continuous handoff and does not
relax the `10 s` freshness gate or any collision, controller, localization, or
flight-safety threshold.

The same complete-map configuration passed the bounded progression:

| Gate | Evidence | Sensor coverage | Max trajectory gap | Peak speed | Peak roll/pitch | Result |
|---|---|---:|---:|---:|---:|---|
| 120 s | `Results/sunray_ros1/factory_l2_fuel_full176x64_replan3_r91_120s_20260714/` | 16.90% | 3.861 s | 1.740 m/s | 22.44 deg | backend passed |
| 300 s | `Results/sunray_ros1/factory_l2_fuel_full176x64_replan3_r92_300s_20260714/` | 41.34% | 5.351 s | 2.008 m/s | 30.23 deg | backend passed |
| 600 s | `Results/sunray_ros1/factory_l2_fuel_full176x64_replan3_r93_600s_20260714/` | 65.59% | 6.618 s | 1.939 m/s | 29.06 deg | backend passed |

The 600 s run published 165 trajectories, stayed within `1.148-1.329 m` truth
Z, and had no flight-safety violation. PX4 EV position, velocity, and height
fusion remained active for `99.984%`, `99.953%`, and `99.984%` of samples,
with no vision-data stop or post-fusion estimator reset. Full evidence and the
claim boundary are in the run's `SUMMARY.md` and `coverage_packet_full/`.

Acceptance boundary: fixed-64 autonomous coverage is passed. Complete-map
runtime, safety, localization fusion, and continued coverage growth are also
proved. The complete-map `65.59%` result is not an `80%` full-map coverage
claim; reaching that separate threshold would require a new explicitly opened
longer-duration or coverage-completion goal.

### 2026-07-14 Complete-map 900 s follow-up

The explicitly opened 900 s follow-up is at
`Results/sunray_ros1/factory_l2_fuel_full176x64_replan3_r94_900s_20260714/`.
Its diagnostic sensor-footprint coverage reached `81.29%` and path coverage
reached `16.80%`, but the backend did not pass. The run is excluded from merged
coverage acceptance because it reports `position_cmd_discontinuous` and
`planner_trajectory_stale`; the terminal trajectory stale interval is
`31.579 s` against the `10 s` gate.

The terminal log retains 28 frontiers but repeatedly reports
`No path to next viewpoint` for the selected candidate while restoring expired
trajectory id `238`. A separate command transition around simulation time
`846.33 s` moved the published command by `0.765 m` in `0.020 s`. Therefore the
next task is not a longer blind run: add bounded unreachable-frontier
fallback/re-ranking and repair recovery-path PVA continuity, then require a
short reproducer, 300 s regression, and a new 900 s gate.

### 2026-07-15 Unreachable-recovery closeout

The recovery implementation and bounded regressions are complete. The 300 s
run `factory_l2_fuel_unreachable_recovery_r96_300s_20260714` passed with
`42.01%` diagnostic sensor coverage, `4.671 s` maximum trajectory gap, and no
backend blocker. The 900 s acceptance attempt is
`Results/sunray_ros1/factory_l2_fuel_unreachable_recovery_r100_900s_20260715/`.

The new logic was exercised in airborne exploration: three planning cycles
successfully skipped an unavailable/cooling first candidate and selected a
later ranked candidate. This proves the recovery primitive and makes it a
valid RACER porting candidate. It does not solve a disconnected current
free-space component. The run eventually retained 31 frontiers but published
no trajectory after `831.465 s`; maximum/terminal stale time was `115.043 s`.

The backend remained blocked by `planner_trajectory_stale` and
`position_cmd_discontinuous`. The latter was an explicit emergency odometry
hold after collision distance fell below braking distance; command-to-odom
separation was `0.589 m`. Diagnostic sensor coverage was `77.77%`, below 80%,
and the blocked run is excluded from merged acceptance.

Auto-2D coverage scoring (`axis=-1`) was also bounded and rejected: one 120 s
run stalled with a `32.265 s` trajectory gap; a 2.0 s replan variant passed but
improved coverage by only `0.14` percentage points over the axis-1 repeat,
within run-to-run path variation. Do not spend more time on this parameter
lane.

Decision: stop FUEL full-map tuning. Preserve fixed-64 acceptance, the passed
600 s full-dimension runtime packet, and the candidate-recovery patch. Move to
a bounded RACER multi-UAV gate with the MID360/frame/Hybrid-Z chain, recovery,
freshness, emergency telemetry, and coverage evidence ported explicitly. If
RACER repeats the disconnected-map failure, open the documented known-map
partitioned coverage fallback rather than claiming autonomous coverage.

### 2026-07-16 RACER MID360 input and long-run PVA gate

The three-UAV RACER sensor migration is accepted through the independent live
chains:

```text
MID360 -> FAST-LIO -> /uavN/mosim/racer/local_cloud -> RACER /map_ros/cloud
```

The synchronized cloud and pose samples are non-empty in `world`, measured
timestamp delta is zero, Hybrid-Z uses truth height, and the default depth
camera topics are intentionally unused. The current input gate is:

`Results/sunray_ros1/factory_l2_racer_fastlio_grid8_spacing3_infl035_nativeff_slew2_odom060_gate120_r55_20260715/RACER_FASTLIO_INPUT_GATE.json`

The accepted 30 s and 120 s runtime baselines are r54 and r55. r55 completed
120.019 s with 2.268 m minimum inter-UAV distance, 41.94/34.42/42.83 deg truth
attitude peaks, fresh trajectories, and 19.4247% diagnostic full-indoor sensor
coverage.

The 300 s r56 run at
`Results/sunray_ros1/factory_l2_racer_fastlio_grid8_spacing3_infl035_nativeff_slew2_odom060_gate300_r56_20260716/`
is blocked. It completed 300.02 s, retained fresh trajectories and 2.724 m
minimum inter-UAV distance, and reached 31.0724% diagnostic coverage, but UAV3
reached 59.58 deg and 3.75 m/s. Near simulation time 102.378 s, a reverse
replan generated px4ctrl desired acceleration of 17.38 m/s^2 in X and
6.59 m/s^2 in Y. The static 0.60 m XY odometry-window guard bounds position
separation but does not guarantee velocity/acceleration continuity.

The next bounded A/B regenerates command dynamics from the guarded position
stream with 2.0 m/s velocity, 1.2 m/s^2 acceleration and lateral acceleration,
and 6.0 m/s^3 jerk limits. It must pass 30 s, then 120 s, before a new 300 s
run. r60-r63 are not algorithm results: Gazebo did not finish loading the
0.735 GB clean Factory STL set while an unrelated host scan saturated CPU, so
PX4 never connected to simulator TCP 4560 and RACER never started. Do not use
those attempts to assess coverage or PVA behavior.

Before the next live run, the limiter was replayed against all recorded r56
adapted-command position samples. The first hard-velocity implementation was
rejected because terminal speed clipping caused 38.9-42.7 m/s^3 jerk. The
accepted implementation reserves a jerk-aware braking margin before the speed
boundary and does not apply a discontinuous terminal velocity clip. Evidence:

`Results/sunray_ros1/factory_l2_racer_fastlio_grid8_spacing3_infl035_nativeff_slew2_odom060_gate300_r56_20260716/RACER_COMMAND_DYNAMICS_REPLAY_PVA_A12_J6.json`

The replay covers 11277/11280/11304 `ego_execute` rows for UAV1/UAV2/UAV3.
Maximum replayed speed is 1.88/1.90/1.89 m/s, maximum acceleration is
1.20 m/s^2, and maximum jerk is 6.00 m/s^3. In the UAV3 100-105 s reverse-replan
window, maxima are 1.69 m/s, 1.20 m/s^2, and 6.00 m/s^3. This is an offline
command-dynamics preflight only. It does not prove px4ctrl tracking, attitude,
collision avoidance, freshness, or coverage; those claims still require the
30 s, 120 s, and 300 s Gazebo gates.

#### Live PVA and inter-UAV safety closeout

r65-r67 were bounded wrapper diagnostics rather than planner results. They
identified an outer timeout that incorrectly consumed startup time, a redundant
ROS-master `/run_id` probe, and a mission process that could survive cleanup.
The wrapper now records independent startup, mission, and wall budgets in
`WRAPPER_TIMEOUT_BUDGET.json`, latches ROS-master readiness once, and terminates
the actual `px4ctrl_ego_swarm_mission_node.py` process during cleanup.

r68 completed the 30 s live PVA gate but is rejected as unsafe. RACER's raw
commands retained `3.162 m` separation, independently regenerated commands
reduced it to `0.929 m`, and Gazebo truth reached `0.466 m`. The independent
time reshaping therefore broke RACER's coordinated temporal separation even
though the backend still used the legacy generic `0.45 m` pass threshold.

The replacement safety chain uses MAVROS/FAST-LIO odometry, relative closing
speed, braking distance, and a configured margin. A predicted violation
disables all PVA adapters, commands current-position team hover, lands, records
`inter_uav_emergency_hold`, and blocks the run. Gazebo truth is retained only
for evaluation. RACER planning clearance is `2.5 m`, initial vehicle spacing is
`3.0 m`, and physical acceptance remains `1.5 m`; these values are distinct and
must not be collapsed into one threshold.

The resulting r69 smoke is accepted at:

`Results/sunray_ros1/factory_l2_racer_fastlio_infl035_pvaregen_v3_a12_j6_spacing3_safedist25_pairhold_smoke30_r69_20260716/`

It completed `30.01 s` of fresh exploration with `2.993 m` minimum separation,
zero emergency holds, truth attitude peaks `39.00/42.92/44.87 deg`, live PVA
limits of `1.20 m/s^2` acceleration and `6.00 m/s^3` jerk, and passed the
MID360/FAST-LIO input and runtime-log gates. Diagnostic sensor-footprint and
path coverage were `6.108%` and `0.781%`; the smoke intentionally used a zero
coverage threshold because it is a safety promotion gate, not full-map
acceptance. Promote exactly this parameter set to 120 s, report actual
coverage, and open 300 s only after 120 s passes without emergency hold,
sub-1.5 m separation, attitude above 45 deg, stale trajectories, input-gate
failure, or incomplete landing.
