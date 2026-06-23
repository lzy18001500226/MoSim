# 07 验收 Gate 与交付物

Status: source design, 2026-06-10.

## 1. Gate Principle

Every acceptance claim needs evidence. A run is accepted only for the claim its
evidence can support.

Examples:

- nonzero FAST-LIO topics do not prove planner readiness;
- UE visual playback does not prove controller performance;
- MWORKS simulation results do not prove UE material acceptance;
- QGC status does not prove MWORKS metrics;
- truth-debug localization does not prove sensor-based localization.

## 2. Competition Control-Closure Gates

### Gate C0-A: MWORKS Plant And Control

Required evidence:

- model check or equivalent source/static gate;
- one short plant/controller run;
- controller input/output trace;
- plant truth state;
- actuator/motor model provenance labels;
- metrics for the claim being made.

### Gate C0-B: Official PID Baseline Coverage

Required evidence:

- Tongyuan-provided plant/controller case is labelled as the official baseline
  or the deviation from that case is documented;
- baseline controller id, parameter profile, and scenario config;
- hover or steady-hold trace;
- step-response trace for at least one controlled channel;
- spiral-climb trace;
- figure-8 trace;
- exported raw traces suitable for Syslab metric calculation;
- baseline limitation notes are tied to observed data, not visual impression.

This gate proves the reference point for later controller optimization. It does
not prove that any optimized controller is accepted.

### Gate C0-C: Syslab Metric Contract

Required metric capability:

- RMSE and maximum tracking error;
- steady-state error;
- overshoot and settling time for step-like commands;
- controller effort and saturation indicators;
- robustness comparison under at least one labelled perturbation, wind
  disturbance, or external disturbance scenario when robustness is claimed.

Required evidence:

- metric script or Syslab workflow reference;
- source trace labels and scenario id;
- controller id and parameter profile;
- metric output file with enough metadata to compare baseline and optimized
  runs.

This gate is about functional support for quantitative comparison. It is not a
requirement to write the final comparison report in this design document.

### Gate C0-D: Sensor Observation Boundary

Required evidence:

- sensor profile;
- timestamp and frame rules;
- extrinsic/source labels;
- proof that planner does not consume hidden global scene truth for final
  evidence;
- visual or file evidence for sensor generation route.

### Gate C0-E: Localization / Local Map / Planner Path

Required evidence depends on backend:

- UE truth-map sandbox: source-labelled geometry/collision export, voxel map
  manifest, coordinate/frame/scale check, trajectory trace, and collision/
  clearance validation against the same truth geometry;
- truth-debug backend: label as debug only;
- FAST-LIO/ROS2 backend: topic rates, TF/extrinsic, nonzero outputs, and
  truth-error or quality evaluation;
- native backend: equivalent odometry/local-map validity evidence.

For ROS2/FAST-LIO map/world grounding, source/static repair readiness is not
acceptance. The accepted live evidence must show the same-run raw TF/static-TF
chain from `camera_init` to `map`, `world`, or `ue_world`. If the latest live
evidence only shows `camera_init->body` and no grounding chain, planner or
controller handoff remains blocked.

Planner evidence:

- setpoint or trajectory trace;
- local-map/odometry source;
- stale/fallback status;
- no direct global-truth shortcut unless the run is explicitly labelled as the
  M0/M1 UE truth-map planning sandbox.

### Gate C0-F: FlightControlAdapter

Required evidence:

- selected active backend;
- 20Hz target or measured setpoint stream;
- stale-command timeout;
- accepted/rejected command echo where UI/automation requests are used;
- control status and failsafe status.
- when ROS2/planner handoff is claimed, the controller input must pass through
  the shared controller ABI rather than backend-specific MWORKS variable names.

For UE command/echo surfaces, source/static build-readiness means only that a
future build-only gate may be separately authorized. It is not build success,
live runtime ack, MWORKS downlink, ROS2 runtime echo, final UI acceptance,
planner readiness, controller performance, mission success, or closed-loop
evidence.

### Gate C0-G: Evidence Bundle

Required evidence:

```text
RUN_MANIFEST
CONFIG_SNAPSHOT
model/source labels
sensor/log outputs
planner setpoint trace
controller/plant trace
metrics
screenshots/video where visual claims are made
acceptance or blocker note
```

## 3. Competition Optimized-Control Gates

Optimized-control acceptance requires repeatability and backend switching within
the competition scope:

- multiple controller configurations through the same interface;
- at least one Sysblock optimized controller can replace the official PID
  baseline in the MWORKS UAV model;
- optimized controller evidence includes controller input/output traces,
  plant truth traces, actuator/saturation state, and Syslab metrics;
- candidate algorithm labels match the implemented design route, such as
  improved PID, PID-INDI/INDI, MPC/NMPC, sliding-mode, fuzzy correction, neural
  compensation, or composite control;
- at least one credible local-map/planner path;
- scene/sensor profile switching without truth leakage;
- UE command/echo surface if a UI claim is made;
- automated metric generation;
- report asset export.

### Gate C1-A: Optimized Sysblock Controller

Required evidence:

- graphical Sysblock model or Sysblock-compatible module for the optimized
  controller when graphical controller structure is claimed;
- stable adapter to the baseline flight-control interface or a typed adapter
  documenting every changed signal;
- if full-system execution uses an Equation controller because graphical
  Sysblock embedding is blocked, the run bundle must declare the Equation
  backend and provide behavior-equivalence evidence or an explicit equivalence
  review target against the graphical controller;
- closed-loop MWORKS run on at least one baseline scene;
- comparative metrics against the official PID baseline;
- fallback or stop condition for unstable candidate behavior;
- codegen/SIL equivalence only when generated C/C++ runtime authority is
  claimed. Current MWORKS-native simulation does not require generated C/C++.

### Gate C1-B: Robustness Function

Required evidence when robustness is claimed:

- nominal baseline and optimized runs;
- at least one parameter perturbation, wind disturbance, or external
  disturbance run;
- metric output for performance retention, recovery time, steady-state error,
  RMSE, and saturation/effort;
- event labels showing when the disturbance or perturbation was active.

### Gate C1-C: Controller Deployment Progression

Controller deployment must progress through evidence gates in this order:

```text
1. MWORKS closed-loop controller run
2. Syslab metric comparison
3. graphical Sysblock vs executable Equation equivalence target
4. generated C/C++ compile/runtime smoke, only if generated runtime is claimed
5. SIL equivalence against a MWORKS reference, including nonzero inputs before
   any generated-runtime performance claim
6. ControllerInput / ControllerOutput ABI binding
7. ControllerOutput echo and stale-command guard
8. PX4+Gazebo plant-response or explicitly labelled fixture/pre-acceptance
9. planner/localization setpoint handoff through PX4-compatible surfaces
```

Required evidence by stage:

| Stage | Minimum evidence | Cannot claim |
|---|---|---|
| MWORKS closed-loop | model/source label, controller trace, plant truth, scenario config | generated runtime, ROS2 command authority |
| Syslab metrics | baseline/optimized trace ids and metric output | runtime deployment or HIL |
| Equation equivalence | graphical Sysblock review artifact plus declared executable Equation backend | that graphical artifact can be dropped |
| generated C/C++ smoke | generated source, compile result, runtime harness output | controller performance or SIL equivalence by itself |
| SIL equivalence | MWORKS reference, generated runtime output, tolerance, input sequence | nonzero behavior if only zero-input was tested |
| ABI binding | run manifest with `ControllerInput` / `ControllerOutput` mapping | backend-private signal names as public API |
| command echo | `ControllerOutput` sample, adapter report, ROS2/Gazebo actuator echo, stale rejection, or PX4 Offboard/uORB echo where scoped | hover, flight, planner readiness |
| plant-response pre-acceptance | same-run truth, actuator commands, response metric; PX4+Gazebo required for formal deployment claims | competition controller performance |
| planner handoff | fresh planner setpoint, controller input/output, safety/stale status | final autonomy unless full closed-loop metrics pass |

This gate prevents a common failure mode: using Gazebo actuator echo or RViz
activity as proof that the optimized controller has been deployed. Echo proves
the transport path only. Controller deployment is accepted only for the latest
stage whose evidence exists.

## 4. Competition Formation Gates

Formation acceptance is part of competition closure after the single-UAV
control line is stable:

- multi-UAV scenario identity is defined;
- each UAV has separated truth, controller, and evidence traces;
- formation route and safety constraints are declared.

### Gate C2-A: Formation Control

Required evidence:

- multi-UAV scenario id and per-UAV run identity;
- `swarm_id`, `formation_id`, `uav_count`, and `uav_id` in the run manifest;
- formation route, with leader-follower as the minimum accepted route;
- target formation geometry and per-UAV reference traces;
- per-UAV controller traces and plant truth traces;
- formation error metric;
- minimum inter-UAV distance;
- collision/safety status;
- communication delay/dropout labels if they are part of the scenario.
- result layout that keeps each UAV's raw trace, controller trace, plant truth,
  and metrics inspectable by `uav_id`.

Formation acceptance proves only the specific formation route and scenario that
the evidence covers. It does not prove general swarm autonomy or final
multi-UAV product readiness.

Formation acceptance must not be based on animation alone, copied single-UAV
metrics, merged traces without `uav_id`, ROS2 topic presence without same-run
namespace/frame evidence, or database rows without raw trace and manifest
references.

## 5. Post-Competition Extension Gates

Post-competition acceptance requires migration-ready external stack integration:

- PX4 Offboard/SITL/HIL backend defined and tested for the stated scope;
- QGC monitoring only for PX4/QGC claims;
- MAVLink/DDS/ROS2 route evidence where used;
- hardware or real-sensor replay evidence where claimed;
- safety/failsafe behavior under latency, dropout, invalid estimator, or
  geofence/collision conditions.

### Gate P1-A: Controller Backend Migration

Required evidence when MWORKS Equation, graphical Sysblock, generated C/C++,
future Simulink codegen, or PX4-compatible controllers are compared or swapped:

- one shared controller ABI recorded in the run manifest;
- backend adapter mapping from backend-private signals to `ControllerInput` and
  `ControllerOutput`;
- equivalence test or explicit non-equivalence label between graphical
  Sysblock review model and executable backend;
- generated code compile/runtime smoke only when generated-runtime authority
  is claimed;
- SIL/HIL or PX4/QGC evidence only when that backend is in the claim scope;
- no public ROS2/PX4/runtime contract that depends on MWORKS-internal variable
  names.

### Gate P1-B: ROS / FAST-LIO / Planner Handoff

Required evidence when the run claims real-time point cloud, 3D local map,
FAST-LIO localization, RViz/RViz2 review, or planner handoff:

- plant/sensor source label: `gazebo`, `ue_raycast`, `bag_replay`, or another
  declared backend;
- actual topic names, namespaces, frame ids, and measured rates;
- same-run raw `/tf` and `/tf_static`;
- LiDAR/IMU extrinsic source and transform chain;
- FAST-LIO odometry/cloud/path outputs with quality or truth-error evaluation;
- local-map representation and update rate;
- planner input proof showing it consumes localization/local-map products, not
  UE global truth or hidden plant truth;
- blocker if any item is source-static only, fake, stale, or debug-labelled.

For the preferred formal exported-controller PX4+Gazebo validation lane, add:

- Gazebo world/model/sensor configuration snapshot;
- PX4 SITL version/config, vehicle model, mode/arming/failsafe state, and ULog
  or topic evidence where available;
- controller backend label: generated C/C++ through L1 PX4 Offboard adapter or
  L2 PX4 module/uORB adapter;
- evidence that the runtime controller interface maps through the shared
  `ControllerInput` / `ControllerOutput` ABI before entering PX4 setpoint or
  uORB surfaces;
- PX4 setpoint/uORB/control-allocation/actuator evidence appropriate to the
  selected level;
- direct `ControllerOutput -> Actuators -> Gazebo` bridge evidence only when
  the run is explicitly labelled `fixture`, `scaffold`, or `pre_acceptance`;
- if MWORKS signed visual rotor speeds are used as a source, proof that the
  sign convention is checked before converting to Gazebo nonnegative motor
  speed magnitudes;
- PointCloud2 or Livox-like point-cloud capture with frame and timestamp
  checks;
- for the active TF voxel smoke adapter, same-run proof that the input
  `PointCloud2.header.frame_id` matches the declared sensor/body frame and
  that a TF chain to the declared local-map frame exists; if no-TF mode is used,
  same-run proof that the input already equals the local-map frame is required;
  either way, the adapter must block instead of relabelling sensor/body-frame
  points as `map`;
- OctoMap/voxel-map output or equivalent 3D occupancy artifact;
- UE render/replay evidence only as visual presentation, not as plant truth.

Current Sunray ROS1 lane note:

The active runtime lane is Sunray ROS1 / Gazebo Classic / PX4 / MAVROS /
px4ctrl. For current Sunray review, use
`Docs/Workflows/sunray_ros1_current_runtime_lane.md` and
`Docs/Design/架构/MoSim_FASTLIO定位闭环与规划复现基础方案.md`.
The table below is retained as historical Gazebo/ROS2 assembled-lane gate
context and must not steer current Sunray ROS1 execution unless PMO/user
explicitly reopens that route.

Historical Gazebo/ROS2 assembled lane acceptance split:

| Gate | Current evidence can claim | Current evidence must not claim |
|---|---|---|
| `sensor_local_map` | Gazebo world/model launched, ROS2 bridge publishes IMU and `PointCloud2`, same-run TF exists, local voxel/grid smoke output exists | correct MID360 scan pattern, FAST-LIO localization, planner readiness, controller performance |
| `controller_output_node_handoff` | `ControllerOutput` can be converted to `actuator_msgs/Actuators` and bridged to `gz.msgs.Actuators` as a fixture | hover, flight, mode/arming behavior, PX4 deployment, stale-command policy, final command acknowledgement |
| `fastlio_planner_input` | Gazebo LiDAR/IMU can be republished to MoSim/Sunray-compatible input topics with frames and rates | physical MID360 realism while source remains `gpu_lidar`; FAST-LIO success; planner readiness |
| `spark_fastlio_localization` | real FAST-LIO-family output topics exist when the Spark node is launched and recorded | localization quality unless truth-error gate is present; planner or closed-loop success |
| `hover_hold_closed_loop_pre_acceptance` | blocked until current assembled world produces same-run Gazebo truth-pose samples for `sunray150_assembled` | old Factory hover results, competition controller performance, trajectory tracking, final closed-loop acceptance |

Historical 2026-06-16 evidence paths:

```text
sensor_local_map: Results/gazebo_ros2/sunray150_gazebo_ros2_smoke/RUNTIME_STATUS.json
controller_output_node_handoff: Results/gazebo_ros2/yunzong_planning_test_sunray150_assembled_controller_output_node_handoff_verify_20260616_151729/RUNTIME_STATUS.json
fastlio_planner_input: Results/gazebo_ros2/yunzong_planning_test_sunray150_assembled_fastlio_planner_input_verify_20260616_151804/RUNTIME_STATUS.json
hover_hold_closed_loop_pre_acceptance blocker: Results/gazebo_ros2/yunzong_planning_test_sunray150_assembled_hover_hold_closed_loop_verify_20260616_152301/BLOCKER.json
hover truth recording: Results/gazebo_ros2/yunzong_planning_test_sunray150_assembled_hover_hold_closed_loop_verify_20260616_152301/GAZEBO_TRUTH_POSE_RECORDING.json
```

The hover-hold blocker is specifically a current assembled-lane truth-pose
blocker: world unpause succeeded, but
`/world/yunzong_planning_test_sunray150_assembled/dynamic_pose/info` produced
zero samples for `sunray150_assembled`, so the truth-feedback controller had no
input and no adapter/controller command samples were produced. Do not replace
this blocker with the older Factory hover-hold pass unless the world/model
identity is intentionally rolled back and labelled as historical evidence.

Historical execution entry while the assembled large world and motor-plugin
issue was being repaired:

```text
Config/gazebo/worlds/sunray150_single_uav_competition_light.sdf
Config/gazebo/models/sunray150_assembled/model.sdf
```

This light competition world kept the user-approved assembled Sunray150 visual
and sensor lane, adds a small static-obstacle field, and is the preferred
single-UAV Figure-8/avoidance development entry until the large YunZong map is
stable enough for the same gate. The four `MulticopterMotorModel` plugin blocks
in `sunray150_assembled/model.sdf` are currently retained but disabled because
the current Fortress configuration can stall or crash the server loop. Any run
with disabled motor plugins, truth-feedback-only control, kinematic pose
injection, or no actuator-response samples must be labelled as scaffold,
pre-acceptance, or planner/sensor validation only. It must not be called final
Gazebo plant closed-loop, controller deployment, trajectory tracking, or
competition controller-performance evidence.

If `PointCloud2.width=360` and `PointCloud2.height=32` are observed from the
historical assembled Gazebo/ROS2 model, the run must be labelled as regular
`gpu_lidar`/degraded MID360 smoke. It is invalid to accept MID360 realism by
changing RViz point size, colors, decay, or by row-bucketing the cloud into a
Livox-like `CustomMsg`.

This gate can support raw point-cloud transport, downstream voxel-map,
planner-handoff, and system-validation claims. It cannot replace
MWORKS/Syslab evidence for the competition controller-performance claim.

Current source-static scaffold for the exported-controller lane:

```text
Scripts/ros/mosim_msgs/msg/ControllerOutput.msg
Scripts/ros/controller_output_to_gazebo_actuators.py
Config/gazebo/models/sunray150/model.sdf
Config/scenarios/system/sunray150_gazebo_ros2_smoke.yaml
```

Passing these source/static checks means the command path is structurally
declared. It does not prove Gazebo physics quality, controller performance,
planner readiness, or closed-loop behavior until a live run records measured
topics, motor command bridge status, TF, point cloud, local-map output, and
runtime status.

### Gate P1-C: Platform Comparison / RflySim-Like Claim

Required evidence when MoSim claims RflySim-like or better platform behavior:

- role split between Modeling, Flight Control, Runtime Plant/Sensors, and
  Display/Review is visible in the run bundle;
- active control backend and active plant backend are named;
- sensor/scene/display evidence is separated from controller/plant/metric
  evidence;
- parameter labels distinguish accepted target-vehicle truth from reference
  examples;
- command/echo shows frontend intent was accepted or rejected by the authority
  adapter;
- unsupported RflySim parity areas are listed as gaps rather than hidden in a
  generic success statement.

### Gate P1-D: UE Truth Map To ROS2 Perception Migration

Required evidence for the staged map/perception route:

| Stage | Acceptance evidence | Must not claim |
|---|---|---|
| M0 UE truth-map extraction | source-labelled scene/collision geometry, voxel/occupancy map manifest, coordinate/scale check, visual alignment screenshot | sensor-based perception, localization, planner readiness |
| M1 truth-map planning sandbox | trajectory/path output, collision/clearance check against the same truth map, planner config, visual path overlay | autonomous local mapping, FAST-LIO success, closed-loop control |
| M2 ROS2 observation pipeline | UAV pose, IMU, LiDAR/depth point-cloud topics, TF/extrinsic, measured rates, RViz2/native visualization | localization success or planner handoff without mapping output quality |
| M3 local map / FAST-LIO handoff | localization/local-map output, quality/truth-error or debug label, planner input proof | final controller performance or mission success |
| M4 closed-loop execution | FlightControlAdapter setpoints, MWORKS/RuntimePlant tracking, metrics, run bundle | broader platform acceptance beyond the scenario evidence |

The UE truth map may be used as an evaluation oracle for M2/M3/M4, but it must
not be silently fed to the planner when the run claims autonomous perception or
local-map planning.

### Gate P1-E: Exported-Controller PX4+Gazebo/ROS2/UE System Validation

Required evidence when a MWORKS-designed controller is validated in
PX4+Gazebo, routed through ROS2 where needed, and rendered in UE:

- MWORKS source controller/model evidence remains available for the competition
  claim;
- exported generated C/C++ controller artifact is named, compiled, and passed
  through its SIL gate;
- selected PX4 integration level is named: L1 Offboard setpoint adapter or L2
  PX4 module/uORB adapter;
- ABI wrapper maps state/reference/fault/safety inputs and command outputs
  into PX4-compatible setpoint or uORB surfaces;
- PX4 owns mode, arming, failsafe, estimator/control-allocation semantics, and
  the actuator pipeline for the run;
- Gazebo owns validation plant truth and sensor observations for that run;
- ROS2 owns TF, sensor topics, raw point cloud, downstream voxel/local map,
  planner state, optional Offboard messages, and bags/topic summaries;
- UE receives state/map/replay data for visual rendering only;
- run manifest separates `competition_metric` from `system_validation` claim
  scope;
- no claim that Gazebo validation alone satisfies Syslab quantitative
  comparison requirements.

Behavior-equivalent ROS2/C++ or Python controller nodes and direct Gazebo
actuator bridges may be attached to this gate only as fixture/pre-acceptance
evidence. They cannot satisfy this gate's formal deployment requirement.

### Gate P1-F: Single-UAV Figure-8 With Obstacle Avoidance

This is the current non-UE single-UAV system-validation target before
multi-UAV implementation. The task is not "track a fixed figure-8 at all
costs". The task is to complete a figure-8 mission while avoiding obstacles
with the live local-map/planner stack.

Mission chain:

```text
figure-8 mission target / waypoint sequence
  -> global reference or mission manager
  -> Gazebo MID360-like raw point cloud + downstream local 3D occupancy / EGO map
  -> local planner replanning around static obstacles
  -> PlannerSetpoint / trajectory output
  -> ControllerInput / ControllerOutput ABI
  -> Gazebo actuator bridge
  -> Gazebo truth trajectory and collision/clearance evaluation
```

Minimum acceptance evidence:

- scenario config snapshot with figure-8 height, scale, speed, obstacle
  geometry, safety bounds, and active controller/backend labels;
- same-run Gazebo world/model/sensor snapshot for the assembled Sunray150 lane;
- motor plugin / plant authority state: enabled `MulticopterMotorModel` plus
  actuator-response samples for final plant closed-loop claims, or an explicit
  scaffold label when the run is truth-feedback, pose-driven, or motor-disabled;
- measured LiDAR, TF, odometry/localization, local-map, planner-output,
  controller-output, actuator-echo, and truth-state topics;
- planner output is produced from localization/local-map inputs, not from a
  hidden global truth shortcut;
- guarded setpoint publication with timeout, stale-command rejection, NaN/Inf
  rejection, altitude/position/velocity/tilt bounds, actuator command bounds,
  and cleanup evidence;
- truth trajectory shows figure-8 mission progress, obstacle avoidance,
  return-to-route behavior after detour, and no collision;
- every Gazebo GUI animation review must enable camera follow and a live
  history trajectory overlay by default. The trajectory overlay must keep a
  continuous actual-flight trail, switch from green to blue after the second
  center revisit band, and record marker evidence in
  `gazebo_truth_trail_marker.json`. If the overlay is disabled, missing, not
  published, or has fewer than two points, the GUI review is blocked even when
  numeric metrics pass;
- metrics for mission completion, waypoint/loop completion, tracking RMSE to
  the planned feasible trajectory, maximum error, minimum obstacle distance,
  max tilt, max velocity, actuator saturation, guard triggers, and runtime
  duration;
- separate review artifacts for raw/review LiDAR point cloud and local 3D
  occupancy / EGO grid-map surfaces when visual quality is claimed.

Allowed deviation:

- local planner detours around obstacles may deviate from the nominal
  figure-8 reference;
- the run is accepted only if the vehicle returns to the mission route and
  completes the declared figure-8 coverage or waypoint sequence.

Must not claim:

- final competition controller-performance from Gazebo alone;
- final Gazebo plant closed-loop while `MulticopterMotorModel` is disabled,
  stalled, crashing, or replaced by truth/pose feedback scaffolding;
- final `closed_loop` acceptance if only transport, hover, or no-actuation
  planner-output evidence exists;
- Gazebo GUI animation acceptance from static plots, headless metrics, or a
  GUI run where the live trajectory overlay was not visible;
- MID360 physical realism while the source remains a regular `gpu_lidar`;
- multi-UAV readiness;
- UE visual acceptance.

Recommended incremental proof order:

```text
1. obstacle-free figure-8 trajectory tracking in Gazebo;
2. static-obstacle figure-8 with live local-map/planner detour;
3. metrics and review screenshots for LiDAR and local-map outputs;
4. report-ready evidence bundle that preserves the MWORKS competition metric
   boundary and labels Gazebo as system validation.
```

## 6. Deliverables

Design deliverables:

- system design source documents;
- interface/schema definitions;
- ADRs for accepted/rejected architecture routes;
- scenario and backend capability maps.

Runtime deliverables:

- run manifest;
- config snapshot;
- official PID baseline run bundle;
- Sysblock optimized-controller model evidence where controller optimization
  is claimed;
- Equation controller run evidence where it is the declared current executable
  backend;
- generated C/C++ artifacts only where generated-runtime, SIL/HIL, PX4, or
  external deployment claims are made;
- behavior-equivalent ROS2/C++ or Python controller node evidence only where a
  fixture/pre-acceptance Gazebo lane is used before formal generated C/C++ and
  PX4 integration;
- controller ABI wrapper evidence where ROS2/PX4/generated-runtime/Simulink
  replacement claims are made;
- Gazebo world/model/sensor config, ROS2 topic summary, point-cloud capture,
  and OctoMap/voxel-map output where Gazebo+ROS2 system validation is claimed;
- MWORKS result files;
- ROS2 bag or topic summary where ROS2 is used;
- UE truth-map manifest and voxel/occupancy preview where truth-map planning is
  used;
- FAST-LIO/localization outputs where localization is claimed;
- planner traces;
- Syslab or equivalent labelled metrics;
- formation traces and metrics where formation is claimed;
- figures;
- screenshots and videos;
- blocker or acceptance record.

Report deliverables:

- method description;
- architecture diagram;
- controller/planner/sensor evidence;
- metrics tables and plots;
- scenario videos;
- competition limitations and post-competition extension notes.

## 7. Failure And Blocker Rules

Return a blocker instead of stretching evidence when:

- a backend is missing;
- frames or timestamps are inconsistent;
- localization is truth-debug but final localization evidence is requested;
- planner consumed global truth unexpectedly;
- MWORKS model or plant evidence is unavailable;
- UE/ROS2/PX4/QGC surface proves only UI status, not the requested technical
  claim;
- a claim requires manual visual review and no reviewed artifact exists.

## 8. Minimum Useful Run Bundle

A minimum useful bundle should answer:

```text
What ran?
Which backend owned control?
Which backend generated observations?
Which backend localized and built local map?
Which planner generated setpoints?
Which parameters and sources were used?
What metrics and logs were produced?
What claim does this evidence support?
What claim remains blocked or unproven?
```
