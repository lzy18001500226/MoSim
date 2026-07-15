# 05 场景传感器与 UE/ROS 链路

Status: source design, 2026-06-10.

## 1. Scene Role

UE5/MoSimSceneLibrary provides the visual and geometric world:

- Factory, Derelict, open field, gate, obstacle, or mission scenes;
- UAV visual mesh and component review;
- camera/depth/LiDAR raycast sources;
- collision and visibility queries;
- video and screenshot generation;
- operator-facing UE Experiment Console.

UE is a scene and sensor oracle. It is not plant truth and does not decide
controller or planner success.

## 2. Scene Truth Firewall

Allowed route:

```text
UE scene geometry
  -> camera/depth/LiDAR/collision observation
  -> SensorObservationLayer
  -> LocalizationAdapter / LocalMapAdapter
  -> PlannerAdapter
```

Rejected route:

```text
UE scene geometry
  -> hidden global map / obstacle truth
  -> PlannerAdapter
```

If a run intentionally uses global truth for debugging, it must label the
backend as `truth_debug` and cannot be final planning evidence.

## 3. Truth Map, Point Cloud, And Local Map Route

MoSim must treat three map-like products as different artifacts:

| Artifact | Source | Used for | May claim |
|---|---|---|---|
| UE truth occupancy map | UE scene geometry, collision proxies, or curated scene primitives | Abstract 3D world model, global planning sandbox, collision/clearance oracle, visual map review | scene-to-map extraction and truth-map planning only |
| Sensor point cloud | Gazebo LiDAR/depth by default for the exported-controller validation lane; UE raycast or replay only after explicit source selection | ROS2/RViz2 point-cloud display and localization/mapping input | raw sensor observation quality only |
| Local map / voxel map / ESDF | sensor point cloud plus localization/mapping backend such as FAST-LIO and LocalMapAdapter | local planning and replanning | downstream planner input only after ROS2/TF/extrinsic/rate/quality gates pass |

The intended implementation order is:

```text
M0: export UE truth occupancy map
  -> source-labelled scene/collision geometry
  -> voxel/occupancy map manifest
  -> coordinate, scale, and obstacle coverage check

M1: plan and display trajectory on the UE truth map
  -> path/trajectory from the abstract occupancy map
  -> 3D voxel map display
  -> collision and clearance check against the same truth geometry
  -> label as truth-map planning, not sensor-based autonomy

M2: publish ROS2 sensor observations
  -> Gazebo pose/IMU/LiDAR/depth raw point cloud by default
  -> or explicitly selected UE raycast/replay source
  -> TF/extrinsic
  -> RViz2 or equivalent native point-cloud review
  -> measured topic rates, PointCloud2 header frame, and frame consistency

M3: build local map from ROS2 observations
  -> OctoMap/voxel map first; FAST-LIO or ESDF backend when localization or
     planner handoff is claimed
  -> local occupancy/ESDF/obstacle-set output
  -> planner consumes local-map/localization products
  -> UE truth map used only as evaluation oracle

M4: execute planned trajectory through control stack
  -> FlightControlAdapter setpoints
  -> MWORKS RuntimePlant for MWORKS-hosted runs, or PX4+Gazebo for formal
     external SITL validation
  -> metrics, run manifest, screenshots/video, bags/logs, and blockers
```

This lets M0/M1 progress before the ROS2 live chain is fully accepted, while
M2/M3/M4 remain gated by ROS2/FAST-LIO evidence when they claim real-time
perception, local mapping, planner handoff, or closed-loop autonomy.

Current route correction:

- The main runtime validation world is Gazebo, not a UE occupancy-grid-to-box
  surrogate. Use the YunZong/Sunray Gazebo obstacle world where possible so
  obstacle geometry and collision semantics stay close to the open-source
  runtime assets.
- The visible vehicle in Gazebo must be the MoSim assembled Sunray150 visual
  mesh plus propeller visuals, not a simplified block aircraft. Simplified
  collision primitives may remain internal physics/collision approximations,
  but they must not replace the visible aircraft review surface.
- UE truth occupancy fixtures are cache/debug/prototype evidence unless a task
  explicitly labels them as a truth-map planning sandbox. They must not be
  presented as the main Gazebo world, live point-cloud evidence, RViz evidence,
  or planner/local-map runtime proof.

## 4. Sensor Observation Profiles

Sensor profiles define what the simulated or replayed UAV can observe.

Minimum profile:

- truth state for visualization and sensor generation;
- IMU packet with timestamp, frame, bias/noise policy, and validity;
- LiDAR or depth observation with frame, extrinsic, point timing where
  applicable;
- optional camera frame for visual review;
- collision/visibility query output for safety and scene review.

MID-360-like profile:

- 10Hz baseline LiDAR unless an enhanced mode is explicitly measured;
- 200Hz IMU target;
- explicit LiDAR/IMU extrinsic;
- per-point timing or a declared approximation;
- frame and timestamp monotonicity checks;
- enough density/duration for localization and mapping gates.
- point-cloud scan envelope must be reviewed as data, not as RViz style:
  horizontal FOV, vertical FOV, minimum range, maximum range, frame rate, and
  points per frame must be recorded with each accepted sensor runtime.

Current Sunray ROS1 MID360 sensor status:

- The current executable lane is Sunray ROS1 / Gazebo Classic using the
  reviewed assembled `sunray150_with_mid360` model. The default sensor mode is
  `SUNRAY_MID360_SENSOR_MODE=nested`, which keeps the original Sunray nested
  `model://livox_mid360` Livox simulation plugin and fixes it to the reviewed
  Sunray150 assembly. `inline` mode is diagnostic-only because it can alter
  raw scan and FAST-LIO accumulated-map visual semantics.
- The current accepted raw topics are `/uav1/livox/lidar` and
  `/uav1/livox/imu`. The shell/visual mesh of the default Livox include must
  not be duplicated over the already assembled user-reviewed radar body.
  Mechanical mount pose, Gazebo ray sensor local pose, Livox point-cloud
  origin, built-in IMU pose, and FAST-LIO `extrinsic_T` are distinct
  quantities; do not copy one directly into another without an explicit
  transform audit.
- `/Laser_map` is the FAST-LIO accumulated ikd-tree map review output when
  FAST-LIO is running. `/cloud_registered` is the current registered scan, not
  proof of an accumulated map. Raw point-cloud presence, accumulated-map
  visibility, and localization quality are separate gates.
- The old Gazebo Fortress/ROS2 `gpu_lidar` profile (`500 x 40`, 10Hz,
  horizontal `360 deg`, vertical about `-7 deg` to `52 deg`, range `0.1 m` to
  `40 m`) is historical/future-reference only under the current Sunray ROS1
  lane. If that route is explicitly reopened, it must be labelled as a
  raster-like degraded MID360 approximation unless a Livox-compatible scan-mode
  source is implemented.
- RViz visual settings are part of the review surface, not the sensor model.
  LiDAR review should use native point display with small points and the
  human-review-only accumulated map-frame topic
  `/mosim/review/lidar_points_map_accumulated`. EGO occupancy review should
  use voxel/box display with `AxisColor` on the review-only above-floor topics
  `/mosim/review/occupancy_above_floor` and
  `/mosim/review/occupancy_inflate_above_floor`, not the raw
  `/grid_map/occupancy*` topics by default. Current EGO review paths may
  publish occupancy as XYZ-only voxel centers, so color is a review transform. A
  sparse-looking RViz cloud must be checked against runtime counts:
  `raw_point_count` proves frame shape, `finite_point_count` proves scene hit
  count, and `review_accumulated_cloud_map_frame.width` proves the visual
  multi-frame review density.
- Raw LiDAR review and EGO local-map review are separate acceptance surfaces.
  The raw Gazebo LiDAR, review-cloud, and FAST-LIO compatibility topics must
  remain unfiltered so point density, intensity/color proxy, scan envelope, and
  rate can be reviewed directly. The planner-cloud path may apply local-map
  preprocessing before EGO consumes it. Current preprocessing blanks map-frame
  points below the configured ground threshold and points inside the UAV
  self-filter cylinder by writing NaN into `/uav1/global_points` and
  `/mosim/planner/global_points`. This prevents a flat floor or self/body hits
  from being inflated into local obstacle voxels while preserving the raw
  LiDAR evidence. Because EGO consumes finite XYZ points as obstacles, a
  visible under-UAV obstacle blob in `/grid_map/occupancy_inflate` is a
  planner-input filtering issue first, not a map-color or RViz-style issue.
  A low layer in the filtered review output with minimum z around `1.04 m` is
  usually obstacle inflation around valid obstacle points, not direct floor
  leakage. Changing EGO resolution, obstacle inflation, or z-inflation changes
  planner behavior and is not a review-style fix.

Historical Gazebo/ROS2 single-UAV figure-8 baseline:

- The old light-world figure-8/static-obstacle Gazebo gate used
  `Scripts/gazebo/run_sunray150_figure8_obstacle_gate.sh` and
  `Config/scenarios/system/sunray150_single_uav_competition_light.yaml`.
  The reference trajectory is synchronized to Gazebo truth time, not wall
  time. This is required because WSL/Gazebo may run slower than real time; a
  wall-clock reference can otherwise advance into the figure-8 or landing
  phase while the vehicle is still taking off.
- Historical accepted baseline:
  `Results/gazebo_ros2/single_uav_figure8_truthsynced_config_gate_20260619_015624/RUNTIME_STATUS.json`.
  It passes the stricter figure-8 shape gate, static-obstacle clearance,
  takeoff/landing phases, raw Gazebo LiDAR review, local voxel review, and
  local occupancy-grid review. This is Gazebo truth-feedback pre-acceptance,
  not current Sunray ROS1 evidence, final MWORKS controller-performance proof,
  FAST-LIO localization acceptance, EGO planner acceptance, or multi-UAV
  readiness.
- The next sensor-fidelity upgrade is not another RViz style change. In the
  current Sunray ROS1 lane, keep the Sunray Livox plugin source stable and
  validate frames, timestamps, extrinsics, and FAST-LIO output quality first.
  If a future Gazebo-Fortress/ROS2 lane is reopened, it must implement an
  equivalent Livox scan-mode source before claiming physical MID360 realism.
- Reference spec for the current approximation: Livox MID-360 official specs
  list detection range `40 m @ 10% reflectivity` and `70 m @ 80%
  reflectivity`, close-proximity blind zone `0.1 m`, FOV `horizontal 360 deg,
  vertical -7 deg to 52 deg`, point rate `200,000 points/s`, and typical frame
  rate `10 Hz`: `https://www.livoxtech.com/mid-360/specs`.
- The current Sunray ROS1 lane has passed px4ctrl Goal2/G7 baseline evidence
  and Goal4 EGO single-UAV engineering evidence, but FAST-LIO is still not
  accepted as a control state source. FAST-LIO promotion must follow
  `Docs/Design/架构/MoSim_FASTLIO定位闭环与规划复现基础方案.md`.

## 5. ROS Integration Boundary

The current executable robotics integration backend is Sunray ROS1. ROS2 is a
future or explicitly reopened complete-system route. Use the current Sunray
ROS1 lane when MoSim claims current Gazebo/RViz/MID360/FAST-LIO/EGO execution;
use ROS2 only after PMO/user reopens that route.

ROS should be used when MoSim claims credible access to established robotics
surfaces:

- TF;
- IMU and LiDAR topics;
- bags and topic-rate summaries;
- RViz or RViz2 native review, depending on lane;
- FAST-LIO-family localization;
- planner packages and local-map tooling.

ROS does not own plant truth. It transports and processes observations and
estimates.

Competition closure can still run MWORKS-first when the active claim is only
model/control evidence. If the active claim includes real-time point cloud,
3D voxel/local map, FAST-LIO, planner handoff, or RViz robotics review, the
active ROS lane becomes part of the required evidence path.

The short-term preferred source for real-time raw point cloud and downstream
3D occupancy map work is Gazebo+Sunray ROS1. For formal external runtime
validation, that Gazebo world is controlled through PX4/MAVROS/px4ctrl today,
and later through generated MWORKS C/C++ integrated by a declared PX4 Offboard
or PX4 module/uORB adapter. Gazebo provides the validation plant/world/sensors;
PX4 owns flight-control semantics; ROS transports TF, IMU, raw LiDAR point
cloud, local-map outputs, planner products, and optional Offboard messages; UE
renders the resulting state for high-quality presentation. This route does not
replace MWORKS competition simulation or Syslab metric evidence.

This route is not a real-time MWORKS-Gazebo co-simulation route by default.
Sysplorer/Syslab do not need to run synchronously with Gazebo physics ticks for
the first point-cloud/map validation slice. MWORKS supplies the accepted
controller/model evidence and parameter provenance; Gazebo/ROS owns live
plant, sensor, transport, map, and planner evidence. A true synchronous
MWORKS-Gazebo route is a later HIL-like backend and must satisfy the gate in
`02_总体架构与权威边界.md`.

The same lane must also carry controller output through the public ABI before
it reaches any runtime backend. For PX4-native deployment, the ABI maps into
Offboard setpoints or declared uORB surfaces. The current scaffold that maps
`/mosim/sunray150/controller_output` to
`/sunray150/gazebo/command/motor_speed` through Gazebo
`Actuators.velocity[]` is retained only as a direct-actuator fixture for
message, stale-command, plant, and visual-review debugging. It must not be
reported as generated-controller deployment or final closed-loop evidence.

UE raycast remains a possible sensor source, but it is no longer the default
first implementation for point-cloud/map work because it requires us to own
LiDAR scan timing, TF, extrinsics, collision-query semantics, and ROS
publication quality ourselves.

The active ROS integration and controller-backend route is split across:

```text
Docs/Design/02_总体架构与权威边界.md
Docs/Design/04_接口数据契约与时钟频率.md
Docs/Design/07_验收Gate与交付物.md
```

The old long-form note is retained only as cached trace-back:
`Docs/Cache/design/historical_snapshots/absorbed_or_superseded_20260614/14_ROS2正式接入与控制器后端迁移设计.md`.

## 6. FAST-LIO Path

FAST-LIO does not require PX4. It requires coherent sensor and transform data:

```text
IMU + LiDAR + TF/extrinsic + timestamps + motion
  -> FAST-LIO
  -> odometry / path / cloud_registered
  -> truth-error or consistency evaluation
  -> local map / planner input
```

Acceptance cannot be based only on nonzero topics. It requires rate, timestamp,
frame, extrinsic, output, and error/quality evidence.

FAST-LIO also does not require Gazebo in principle. However, when MoSim needs a
credible short-term source for live point cloud, IMU, TF, and map evidence,
Gazebo is the preferred source because those sensor and ROS2 integration paths
are standard. A pure ROS2-only path must name its sensor generator, frame
source, time base, and map source explicitly.

Current grounding boundary:

- source/static launch files and checkers can prepare the next evidence route,
  but they do not prove current localization or map/world grounding;
- `camera_init` to `map`, `world`, or `ue_world` grounding requires same-run
  raw `/tf` and `/tf_static` evidence that derives a non-fake transform chain;
- a run that only observes `camera_init->body` and no static edges remains
  blocked for planner/controller handoff, even if source files contain a future
  `map_frame` binding;
- future grounding evidence must reject arbitrary static transforms, header
  renames, fake odometry/maps/clouds/TF, keyboard pose, UE truth shortcuts, GUI
  display state, and alias-only `world` claims.

Minimum live FAST-LIO evidence for planner handoff:

| Evidence | Required content |
|---|---|
| Source window | exact launch/config/bridge files and sensor profile used by the run |
| Topic/rate capture | IMU, LiDAR, TF, FAST-LIO odometry/cloud/path, and local-map topics with measured rates |
| Frame capture | raw `/tf` and `/tf_static` for the same run, including LiDAR/IMU/body/map relationships |
| Extrinsic evidence | source of LiDAR-IMU transform and whether it is measured, geometry-derived, or seed value |
| Output quality | nonzero localization output plus truth-error, consistency, or stated debug-only quality label |
| Handoff record | which LocalMapAdapter and PlannerAdapter consumed the output, or why handoff stayed blocked |

## 7. Local Map Path

The local map is a planner input derived from observations or estimates:

```text
SensorObservationLayer
  -> LocalizationAdapter
  -> registered cloud / occupancy / ESDF / obstacle set
  -> LocalMapAdapter
  -> PlannerAdapter
```

The local map must declare:

- representation;
- frame;
- update rate;
- source;
- validity;
- whether it is estimator-derived or truth-debug.

For the first validation lane, OctoMap or an equivalent simple voxel occupancy
map is the preferred first target. It is enough to demonstrate 3D occupied,
free, and unknown space from the live point-cloud stream. ESDF/Nvblox/Voxblox
are later targets for higher-performance planning, not prerequisites for the
first credible point-cloud/map demo.

The active Gazebo+ROS2 voxel adapter must transform the input point cloud into
the declared local-map frame with same-run TF evidence. For the current
assembled Sunray150 lane, the input `PointCloud2.header.frame_id` is expected
to be derived from the scenario `vehicle_id`, currently
`sunray150_assembled/base_link/mid360_lidar`. The adapter publishes `map`
frame voxel/grid outputs only after a same-run transform from that input frame
to `map` is available. The no-TF adapter may only be used when the input cloud
already matches the declared local-map frame in the same run. It must not
relabel sensor/body-frame points as `map` by changing headers alone.

## 8. Planner Observation Boundary

PlannerAdapter may consume:

- localization estimate;
- local map;
- mission constraints;
- dynamic limits;
- safety constraints;
- optional debug truth only under a debug label.

PlannerAdapter may not consume:

- raw UE global scene geometry as autonomous sensor-based final evidence;
- MWORKS plant truth as final localization evidence;
- hand-edited obstacle shortcuts that are not in the run config or evidence
  bundle.

PlannerAdapter may consume a source-labelled UE truth occupancy map only in the
M0/M1 truth-map planning sandbox. The run manifest must label that route
explicitly and must not present it as ROS2/FAST-LIO/local-map autonomy.

## 9. UE Experiment Console

The UE console is a frontend. The broader MoSim Operator Console may be a
separate desktop/web frontend, while UE may host a smaller in-scene version for
demonstration. Both use the same command/echo idea. They can request:

- scene switch;
- controller switch;
- planner switch;
- wind/fault/sensor-profile changes;
- start/goal changes;
- recording or review actions.

All requests must go through:

```text
CommandPacket -> authority adapter validation -> RuntimeEcho -> UI display
```

The console must not:

- directly teleport the UAV as control output;
- write hidden global map truth into planner;
- label a run pass/fail without evidence;
- change plant/controller state without accepted echo.

Recommended implementation order:

1. Keep scenario YAML and launch scripts as the authoritative run entrypoint.
2. Stabilize Gazebo/ROS2 command topics, echo, and evidence output.
3. Add a lightweight external Operator Console for scenario/controller/fault/
   wind selection and accepted-state display.
4. Add a UE in-scene panel only for polished demonstration after the underlying
   command/echo path already works.

MWORKS GUI remains the evidence surface for model/controller review and Syslab
metric plots. It should not be stretched into the unified runtime console for
Gazebo, ROS2, RViz, UE, screenshots, and recording.

## 10. Visual Review

Visual review proves visual/scene/sensor presentation quality. It does not by
itself prove:

- controller performance;
- planner correctness;
- localization accuracy;
- final closed-loop acceptance.

Visual review evidence should be linked into the run bundle with explicit
claim boundaries.
