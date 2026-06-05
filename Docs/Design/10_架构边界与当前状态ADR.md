# 10 架构边界与当前状态 ADR

Status: active ADR, 2026-06-06 CST.

Purpose: give new MoSim conversations one compact source for the simulator
architecture boundary. This document does not replace detailed workflows. It
defines which layer owns which truth, how Gazebo/Sunray plugin semantics are
translated into MoSim, and which implementation streams may proceed.

## 1. Decision

MoSim is not a direct Gazebo clone and not a direct RflySim clone. The accepted
architecture is:

```text
MWORKS / Sysplorer / Sysblock / Syslab
  -> plant dynamics, controller, generated C/C++ controller runtime,
     truth state, events, metrics, report evidence

UE5 / MoSimSceneLibrary
  -> high-quality scene rendering, UAV visual, camera view,
     collision and sensor oracle

ROS2 / RViz2 / FAST-LIO-family
  -> LiDAR/IMU/TF transport, localization, local 3D map,
     planner state, native robotics review windows

CoAgent / WeChat
  -> sparse progress, task packets, human intervention, recovery signals
```

RflySim, Gazebo/PX4, AirSim, Sunray/YunZong, FAST-LIO, and EGO-Planner are
reference stacks. They provide structure, behavior contracts, message
semantics, and sanity checks. They do not become project truth until a local
MoSim workflow adopts them with build/runtime evidence.

## 2. Authority Boundary

| Layer | Owns | Must Not Own |
|---|---|---|
| MWORKS/Sysplorer/Sysblock/Syslab | continuous dynamics, controller, setpoint state machine, wind/fault/motor-efficiency experiments, generated controller code, truth, metrics | UE scene appearance, RViz display settings, direct adoption of Gazebo plugins |
| UE5/MoSimSceneLibrary | rendered Factory/Derelict scenes, accepted DAE-derived Sunray150 visual, camera, collision/sensor oracle, video review | controller success, planner truth, global map fed to planner, dynamics parameters |
| ROS2/RViz2/FAST-LIO | IMU/LiDAR/TF topics, FAST-LIO registered cloud/odometry/path, local 3D map, native robotics review | plant truth, fake odometry as FAST-LIO output, browser/HTML active point-cloud review |
| Sunray/Gazebo/PX4 references | plugin parameter seeds, streamed-control behavior, sensor/message contracts, failure modes | final Sunray150 identified truth, direct runtime dependency by implication |
| RflySim references | role split, process split, actuator/dynamics structure, parameter injection pattern | Sunray150 parameter truth, direct `.mo` translation of CopterSim, directly editable MoSim scene source |

UE may provide an RflySim-like experiment console, but its authority is
operator intent and review, not plant truth. The panel can request controller,
planner, fault, wind, sensor mode, scene, start/goal, and recording changes.
MWORKS/ROS2 adapters must accept, reject, timestamp, and echo those changes
before they affect the simulation. UE must not directly overwrite UAV pose,
inject hidden global map truth into a planner, or mark an experiment successful.

## 3. Gazebo/Sunray Plugin Translation

Sunray/YunZong uses Gazebo-style SDF and plugins. In MoSim, plugin tags are
not copied as runtime plugins. They are translated into explicit modules and
verified separately.

| Gazebo/Sunray source | Local evidence | MoSim equivalent | Boundary |
|---|---|---|---|
| `libgazebo_motor_model.so` | `References/Sunray/simulation/sunray_simulator/models/drone_models/sunray150_with_mid360/sunray150_with_mid360.sdf` motor plugins | MWORKS actuator model: command mapping, speed limit, motor lag, `k_f omega^2`, yaw moment, drag/rolling moments where implemented | `motorConstant`, `momentConstant`, `timeConstant*`, drag coefficients are `source=SDF_migration` seeds until ULog/bench validation |
| `rotorVelocitySlowdownSim=10` | same SDF and `References/MWORKS/QuadrotorModel/package.mo` | documented conversion between Gazebo physical rotor speed and MWORKS visual/speed convention | Do not tune thrust because propeller visual speed looks wrong |
| `libgazebo_multirotor_base_plugin.so` | SDF base plugin | MWORKS truth/state output and bridge packet | Gazebo base plugin does not own MoSim truth |
| `libgazebo_mavlink_interface.so` | Sunray SDF plugin block | future PX4/V6X/companion adapter | Not required for first MWORKS-owned closed loop |
| `libgazebo_groundtruth_plugin.so`, `libgazebo_ros_p3d.so` | Sunray SDF plugin block | MWORKS/UE truth logs and ROS2 reference pose topics | Reference pose is not estimator output |
| `libgazebo_imu_plugin.so`, `libgazebo_ros_imu_sensor.so` | Sunray drone SDF and `livox_mid360.sdf` | 200Hz physically coherent IMU from MWORKS state/sensor model | MID-360 built-in IMU frame and flight-controller IMU frame must remain separate unless explicitly fused |
| `liblivox_laser_simulation.so` | `References/Sunray/.../sensor_models/livox_mid360/livox_mid360.sdf` | UE/sensor-oracle generated Livox-like LiDAR into ROS2, preferably Livox `CustomMsg` semantics | Ray plugin is not enough; FAST-LIO claims require timestamps, extrinsics, runtime output, and truth-error evaluation |
| Sunray camera/GPS/barometer/magnetometer includes | Sunray SDF includes/plugins | optional MoSim sensor adapters and health/status bus | Add only when a scenario or controller needs the sensor |

Current Sunray/SDF values remain a Gazebo/PX4-style simulation baseline:

```text
mass = 1.0 kg
inertia = Ixx/Iyy/Izz 0.0085 / 0.0085 / 0.012
motorConstant = 8.54858e-06
momentConstant = 0.06
timeConstantUp = 0.0125 s
timeConstantDown = 0.025 s
rotorVelocitySlowdownSim = 10
```

MWORKS currently carries `lift_cofficient=0.000854858`, which is the SDF
`motorConstant` scaled by `rotorVelocitySlowdownSim^2`. Treat this as
`source=SDF_migration`, not as Sunray150 identified truth.

Current timing policy:

- controller/setpoint contract is 20Hz streamed control, with stale-command and
  invalid-localization handling treated as controller-state-machine logic;
- IMU target is 200Hz in the same clock domain as LiDAR;
- Mid360 hardware-faithful baseline remains 10Hz, but the active MoSim product
  target may use 20Hz enhanced LiDAR only when measured throughput, monotonic
  timestamps, per-point offsets, explicit LiDAR/IMU extrinsics, FAST-LIO output,
  and truth-error gates all pass;
- a 20Hz LiDAR topic rate alone is not accepted localization, mapping,
  planning, or controller evidence.

## 4. RflySim Reference Boundary

RflySim confirms the split MoSim should keep:

```text
CopterSim / PX4 / generated plant
  -> motion, 6DOF dynamics, actuator/fault/dynamic parameters

RflySim3D / UE
  -> rendering, scene, perception API, camera/lidar-like data

ROS / RViz / upper-layer programs
  -> point cloud, odometry, map, planning and review
```

Reusable RflySim ideas:

- streamed state and command transport instead of teleporting UAV pose;
- actuator chain: normalized/PWM command, saturation, rotor speed target,
  first-order lag, thrust and moment;
- scenario parameter injection: initial parameters, fault parameters, dynamic
  modification parameters;
- multi-rate split: controller/state, IMU, LiDAR, rendering, and review at
  different rates;
- UE renderer drops/interpolates frames but does not write back plant truth.

Recommended UE console shape:

| Console group | User action | Owning runtime | Acceptance echo |
|---|---|---|---|
| Scenario | load Factory/Derelict, start pose, goal, reset, pause/resume, recording | MWORKS scenario runner + UE renderer | scenario id, run id, accepted start/goal, source labels |
| Controller | PID/AWFF/INDI/MPC/NMPC/L1/safety filter mode, parameter profile | MWORKS/Sysblock/generated controller runtime | active controller id, sample time, fallback state |
| Disturbance | wind gust profile, mass/payload profile, motor efficiency/fault injection | MWORKS plant/fault wrapper | active disturbance/fault id, start time, severity, source |
| Planner | planner selection, local map source, goal queue, replanning enable | ROS2 planner adapter + MWORKS setpoint interface | active planner id, 20Hz setpoint stream health |
| Perception | LiDAR 10Hz baseline vs 20Hz enhanced target, IMU status, FAST-LIO candidate | ROS2/FAST-LIO bridge | measured rates, timestamp gate, odometry quality |
| Evidence | mark review, export run packet, open RViz/UE review layout | Evidence scripts + RViz/UE | result paths, quality status, known blockers |

Other frontends must stay role-specific:

| Frontend | Role | Data it may command | Data it must display from echo |
|---|---|---|---|
| MoSim Studio | experiment manager and report/evidence browser | scenario/config/run requests | metrics, quality status, result paths, event logs |
| UE Experiment Console | RflySim-like in-scene operator panel | scene, goal, controller/planner/fault/wind/sensor-mode requests | accepted runtime state, render status, evidence level |
| QGC/GCS-style window | future PX4/V6X/offboard supervision | arm/mode/mission/offboard requests only when adapter is active | heartbeat, mode, failsafe, odometry-valid state |
| RViz2 | native robotics review | view/display config only, plus limited goal tools through ROS2 adapter when enabled | TF, LiDAR, FAST-LIO odometry/path, 3D local map, planner state |
| Sysplorer/Syslab GUI | model and result authority review | MWORKS model/simulation operations | native result curves, animation, variables, model checks |

Initial implementation should use a narrow command channel:

```text
UE console command packet
  -> MWORKS/ROS2 command adapter
  -> authoritative runtime applies or rejects
  -> MWORKS/ROS2 state frame echoes active mode/status
  -> UE displays confirmed state only
```

Do not wire UI buttons directly to actor transforms, motor visuals, planner map
truth, or result pass/fail labels.

Scene and map switching rule:

```text
select scene_source_id / map_id
  -> validate registry and active scene links
  -> bind scenario scene_id/map_id/run_id
  -> load or activate UE map for rendering
  -> bind MWORKS scenario and ROS2 topic contract
  -> run required headless gates
  -> only then open UE/RViz review windows
```

The current project already has `scene_id`, `map_id`,
`active_scene_links.json`, `scene_source_registry.json`,
`unreal_scene_profiles.json`, and `AQuadrotorMworksMapActor` map resolution
hooks. The missing product layer is a unified scene-switch UI and command
adapter that keeps those identities synchronized across UE, MWORKS, ROS2, and
Results. Do not treat a visible UE map switch as a complete scenario switch
until the MWORKS/ROS2/evidence echoes match.

Rejected RflySim uses:

- copying RflySim sample mass/inertia/`Ct/Cm` into Sunray150;
- translating CopterSim wholesale into one `.mo`;
- treating packaged RflySim scenes as accepted editable UE5 scene assets;
- leaking full scene truth into the planner as a known global map.

## 5. Current Gate Matrix

| Gate | Purpose | Current Status | Claim Allowed | Claim Not Allowed |
|---|---|---|---|---|
| Gate A: MWORKS controller codegen/SIL | prove generated controller C/C++ can be a runtime candidate | PID demo compile/runtime/nonzero constant-input SIL passed | codegen path is credible for checked controllers | all controllers are deployable; `TranslateModel` proves codegen |
| Gate B: UE truth + ROS2 + Mid360/FAST-LIO | prove sensor/robotics stack is coherent before GUI review | Factory headless gate reached manual-review readiness in current docs; final product acceptance still open | open UE/RViz review only for the passed evidence bundle | final localization, navigation, planner, or controller performance |
| Gate C: system closed-loop contract | freeze MWORKS/UE/ROS2 responsibility split and timing | this ADR closes the current design boundary; implementation still must verify modules | downstream conversations can use this as architecture contract | implementation is complete |
| Parameter identification | upgrade SDF seeds to Sunray150 evidence | no ULog/bench identification bundle found | use SDF values as baseline seeds with source label | call values identified truth |
| UE vehicle visual | use accepted DAE-derived runtime visual | accepted source route exists; material realism remains separate review | DAE-derived FBX/GLB is the runtime visual route | MWORKS STL, cube/cylinder, primitive vehicle, MWORKS animation |

If current status conflicts with older files, prefer:

```text
1. current project files and latest *_CURRENT result gate
2. this ADR and current workflow docs
3. evidence bundles under Results/
4. cache migration audits
5. PROGRESS.md historical entries
6. old chat memory
```

## 6. Parameter And Geometry Rules

The accepted DAE/Blender assembly may update:

- rotor center geometry;
- camera candidate geometry;
- conservative collision envelope;
- UE visual mesh and material source.

It must not update without separate evidence:

- mass;
- inertia;
- thrust/motor constants;
- yaw moment coefficient;
- motor time constants;
- drag and damping;
- controller gains;
- FAST-LIO LiDAR/IMU extrinsics.

Keep MID-360 quantities separate:

```text
mechanical mount pose
point-cloud coordinate origin
built-in IMU position
FAST-LIO extrinsic_T
Gazebo/Sunray ray-sensor pose
```

## 7. Implementation Streams

Use these streams for manual multi-dialog work. Each stream must write result
or blocker packets when assigned cross-thread work.

| Stream | Scope | First Output |
|---|---|---|
| ArchitectureIntegrator | ADR, Gate matrix, cross-doc consistency | updated ADR / status matrix |
| MWORKS-Control | plant/controller model, Sysblock, MCP simulation | checked model and scenario evidence |
| Codegen-SIL | `GenerateModelCode`, C/C++ wrapper, per-controller equivalence | compile/SIL report |
| Dynamics-Parameter | SDF seed audit, ULog/bench route, YAML mapping | parameter status bundle |
| UE-Renderer | accepted scenes, DAE/FBX/GLB visual, camera/video | manual visual review packet |
| ROS2-FASTLIO | ROS2 Humble, IMU/LiDAR/TF, FAST-LIO, RViz2 | headless truth-error gate |
| Evidence-Report | metrics, figures, report-ready evidence, quality status | evidence audit summary |
| Git-Quality | path-limited staging/commit/push | split commit result packet |
| UE-ExperimentConsole | RflySim-like operator panel, command packet schema, accepted-state display | UI design spec and command-adapter smoke |

Latest architecture-thread return:

```text
request_id = UAV-ARCH-SYNC-20260606-001
origin_thread_id = 019e9868-83ea-70f0-92c5-a3a408bd78c6
target_thread_id = 019e0198-a041-77f1-84d0-c5524bfd4b81
return = Results/agent_packets/returns/UAV-ARCH-SYNC-20260606-001.json
status = completed, needs_user_action = false
```

Open blockers from that return remain active until closed by evidence:

- exact local PX4 Iris model source was not located; Sunray SDF proves active
  Gazebo plugin semantics, but direct Iris numeric comparison needs a later
  parameter-audit pass;
- no PX4 ULog or bench identification bundle is present, so mass, inertia,
  motor constants, yaw moment ratio, motor lag, drag, and damping remain
  baseline seeds or open modeling work;
- FAST-LIO current evidence opens review gates only where the latest
  `*_CURRENT` result says so; it does not close final production localization,
  planner performance, or controller integration.

## 8. Anti-Regression Checklist

Do not restart or optimize these routes:

- keyboard/grid-cell movement as UAV control;
- direct pose overwrite as manual control;
- fake/static point cloud as mapping or localization evidence;
- 2D-only occupancy grid as UAV local 3D map;
- browser/HTML point cloud as active runtime review;
- UE debug overlay as replacement for RViz/FAST-LIO;
- `/mosim/replay_odometry` as FAST-LIO odometry;
- nonzero FAST-LIO topics without truth-error evaluation;
- RflySim/Gazebo/AirSim sample parameters as Sunray150 truth;
- DAE mechanical mount center as FAST-LIO extrinsic;
- MWORKS STL/runtime animation or primitive UAV as UE vehicle evidence;
- full UE collision/occupancy truth as planner input;
- `TranslateModel` as C/C++ controller codegen proof;
- PID demo SIL as all-controller deployment proof.

## 9. Next Architecture-Driven Tasks

1. MWORKS plant delta design: add or wrap yaw reaction torque, motor lag,
   rotor drag/rolling moment, and optional body drag as explicit modules.
2. Run minimal hover, yaw, and step-response checks before touching complex
   scenes.
3. Keep Sunray SDF parameters as baseline seeds, but label all values with
   `source=SDF_migration` until PX4 ULog/bench identification exists.
4. Keep UE and RViz windows closed until headless gates pass for the target
   implementation slice.
5. Use WeChat only for sparse milestone/blocker/manual-review notifications.
6. Design the UE experiment console together with the command/status schema
   before implementing fault, wind, controller, or planner switches in the UI.
