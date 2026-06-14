# 13 RflySim四旋翼模型对标与MoSim优化路线

Status: active design note, 2026-06-11. User-reviewed decisions incorporated.

Purpose: clarify what an RflySim-like quadrotor model means, what the current
MoSim quadrotor model contains, and how MoSim should optimize the model before
claiming stronger controller or platform results.

This document is a design and audit source. It is not evidence that a model
change has passed `check_model`, `SimulateModel`, controller performance, or
final acceptance.

## 1. Scope Boundary

The current technical priority is:

```text
optimize the MWORKS quadrotor model
  -> run model-level smoke and scenario simulations
  -> validate controller and robustness results on a credible plant
  -> then extend UE / ROS2 / PX4 / QGC integration when needed
```

RflySim is used as a system-structure reference, not only as a rotor-dynamics
reference. The correct high-level decomposition is:

```text
Simulink
  -> controller design
  -> dynamics model design and verification
  -> MIL/SIL
  -> generated C/C++ controller code

PX4 / Pixhawk
  -> flight-control logic
  -> attitude/position control or generated-code integration
  -> actuator/motor command output

CopterSim
  -> real-time multirotor dynamics
  -> sensor simulation
  -> fault injection / HIL behavior
  -> flight-state stream to display/review surfaces

3DDisplay / RflySim3D / RflySimUE5
  -> real-time 3D animation
  -> scene display
  -> optional 3D engine and perception-data source
```

MoSim maps this as:

```text
MWORKS.Sysblock / Syslab / Modelica
  -> Modeling / MIL-SIL

MWORKS-native controller now, generated C/C++ or PX4/QGC later
  -> Flight Control

MWORKS-hosted plant now, future separated runtime plant/sensor/HIL layer later
  -> Runtime Plant / Sensors / HIL

UE5 / MoSimSceneLibrary / RViz2 / QGC review surfaces
  -> Display / Scene / Review
```

The current implementation may host several roles inside MWORKS. The long-term
architecture must still keep the roles separate.

RflySim is used as a detailed model-structure reference:

- how a mature UAV simulator separates airframe parameters, actuator dynamics,
  force/moment generation, external interfaces, faults, scene integration, and
  evidence;
- how a configurable multirotor model exposes initialization, command,
  parameter, and fault interfaces.

RflySim is not used as Sunray150 parameter truth. Do not copy RflySim example
mass, inertia, motor constants, drag, or damping values into the MoSim Sunray150
model unless a later task explicitly classifies them as reference-only seeds and
adds provenance labels.

Local RflySim evidence used for this comparison:

```text
References/RflySim/RflySimAdv3Full/4.HILApps/RflySimAPIs/RflySimAPIsPers.zip
  RflySimAPIs/4.RflySimModel/3.CustExps/e0_AdvApiExps/1.inCtrlExt/
    1.Matlab/MulticopterNoCtrl_init.m
    1.Matlab/MulticopterNoCtrl.slx
    1.Matlab/MulticopterModel.zip
    2.Python/inCtrl.py
```

The archive also contains parameter-injection and fault-injection examples
under `5.ParamAPI/`, which are useful for interface design but not for direct
Sunray150 parameter adoption.

Additional local CopterSim reference reviewed on 2026-06-11:

```text
References/RflySim/CopterSim/
  README.md
  Init.m
  MavLinkStruct.mat
  Multicopter_vPC.slx
  MathModelDocEn.pdf
  SupportedVehicleTypes.docx
  imgs/
```

This directory appears to be a complete standalone Simulink CopterSim model
example, not the complete RflySim platform source tree. It contains the main
multicopter Simulink model, initialization script, MAVLink/Simulink bus
objects, math/model documentation, supported vehicle-type documentation, and
README/tutorial assets. It does not by itself include the full platform runner,
PX4/ArduPilot projects, LabVIEW/HIL generated artifacts, RflySim3D/UE display
source, installer, or end-to-end build/release scripts.

Treat this directory as `reference_only` for architecture and model-structure
design. Do not import its parameters as Sunray150 truth.

## 2. What The RflySim-Like Model Looks Like

In this project, "RflySim-like quadrotor model" should mean a modular
multirotor plant with explicit interfaces, not just a visual UAV moving in a
scene.

In the broader project, "RflySim-like MoSim platform" means the four-layer
system above. In the narrower current task, "RflySim-like quadrotor model"
means the CopterSim-like Runtime Plant subset: actuator/motor dynamics,
force/moment generation, sensor/fault hooks, state output, and evidence labels.

### 2.1 Airframe And Initial State

The local RflySim `MulticopterNoCtrl_init.m` exposes the model as a configurable
airframe:

- 3D display type and UAV type are separate parameters;
- initial position and Euler attitude are explicit external inputs;
- GPS latitude/longitude and environment altitude define map origin behavior;
- mass and inertia matrix are explicit plant parameters;
- initial body velocity and angular rate are explicit initial conditions.

MoSim equivalent:

```text
VehicleProfile
  -> geometry
  -> mass / inertia
  -> rotor centers
  -> sensor mounts
  -> parameter provenance
  -> initial state
```

For Sunray150, DAE/Blender geometry can support rotor and sensor positions, but
it does not prove mass, inertia, motor constants, controller gains, drag, or
disturbance parameters.

### 2.2 Actuator And Motor Layer

The local RflySim sample separates motor and rotor parameters from the 6DOF
body:

- motor count;
- minimum thrust / command floor;
- motor static and dynamic coefficients;
- motor time constant;
- motor inertia;
- rotor thrust coefficient;
- rotor moment coefficient;
- initial motor speed;
- input vector.

MoSim equivalent:

```text
normalized actuator command
  -> command saturation
  -> command-to-speed or command-to-thrust mapping
  -> motor speed lag
  -> rotor thrust
  -> yaw reaction moment
  -> actuator saturation / health / effectiveness state
```

The key design point is not the exact RflySim variable names. The key point is
that the motor/rotor layer is an explicit physical and interface layer, not a
hidden constant inside a controller.

### 2.3 Force And Moment Layer

The local RflySim sample exposes force/moment model parameters such as rotor
arm radius, aerodynamic drag coefficient, moment/drag coefficients, and rotor
disk/aero distance. A mature RflySim-like plant therefore contains:

- total thrust from individual rotors;
- body moments from rotor-arm geometry;
- yaw reaction torque;
- aerodynamic drag and angular damping;
- optional rotor gyroscopic effects;
- fault and disturbance injection points.

MoSim equivalent:

```text
per-rotor force and moment
  -> body-frame total force
  -> body-frame total moment
  -> MultiBody force/torque application
  -> truth state and plant events
```

This is why model optimization must start at the plant/actuator layer before
we over-interpret controller improvements.

### 2.4 External Interfaces

RflySim examples show external command, DLL, parameter API, and fault API
patterns:

- `inCtrlExt`-style external command path;
- `InitInParams` for initialization or parameter injection;
- `FaultInParams` for fault injection;
- SITL/HITL/QGC-style scripts and scene interaction examples.

MoSim equivalent:

```text
RunManager config
  -> command packet / setpoint stream
  -> actuator and fault command validation
  -> accepted/rejected echo
  -> MWORKS truth result and event log
  -> UE/ROS2 displays echoed state only
```

UE, ROS2, PX4, and QGC are adapter surfaces. They must not bypass the MWORKS
plant when the claim is about dynamics, controller performance, or metrics.

### 2.5 CopterSim Runtime-Plant Structure

The local `References/RflySim/CopterSim/Multicopter_vPC.slx` model confirms
that a mature CopterSim-like plant is broader than the nominal rotor/6DOF
chain. Its visible Simulink structure includes:

- top-level inputs `inPWMs` and `Terrain`;
- top-level outputs `MavHILSensor`, `MavHILGPS`, and
  `MavVehileStateInfo`;
- `Actuator Model: Motor_ESC`;
- `Propeller Model`;
- `Force and Moment Model`;
- `6DOF`;
- `Environment Model`;
- `Ground Model`;
- `Battery Model`;
- `Fail Model`, `Model Failure`, and `Model Fail Assessment`;
- `HILSensorMavModel`, `HILGPSModel`, and `HILStateMavModel`;
- sensor/noise blocks for accelerometer, gyro, magnetometer, GPS, barometer,
  wind, atmospheric model, world magnetic model, gravity model, and turbulence.

`Init.m` exposes these design classes:

- initial state: position, body velocity, Euler angle, body rate, motor RPM;
- vehicle and actuator parameters: mass, inertia, vehicle type, motor count,
  arm radius, throttle-speed curve, motor time constant, rotor inertia, thrust
  coefficient, moment coefficient, throttle dead zone;
- aerodynamics: drag, damping moment vector, aero-center offset;
- environment: latitude, longitude, altitude, sample rates, gravity/air
  density placeholders;
- sensor and noise parameters for accelerometer, gyro, magnetometer, GPS,
  barometer, wind, and IMU;
- battery model parameters;
- fault toggles for battery, propeller effectiveness, payload/drop/shift/leak,
  and wind disturbance.

MoSim does not need all of these layers before the next model smoke. However,
they should define the long-term Runtime Plant/Sensors/HIL backlog:

```text
Runtime Plant nominal core
  -> actuator / propeller / force-moment / 6DOF
  -> environment and ground contact
  -> sensor/noise/delay outputs
  -> battery / ESC / thrust-margin behavior
  -> fault injection and failure assessment
  -> MAVLink/PX4-compatible HIL output bus
```

For the current MoSim slice, the immediate adoption is architectural:
`Battery`, `Ground`, `Environment`, `SensorNoise`, `MavlinkHilOutput`, and
`FailureAssessment` should become reserved design surfaces, not accepted
Sunray150 model claims.

## 3. What The Current MoSim Model Looks Like

Current formal ownership:

| Layer | Path | Role |
|---|---|---|
| Official baseline | `References/MWORKS/QuadrotorModel/package.mo` | Tongyuan/upstream baseline and regression reference. Do not destructively rewrite. |
| Formal MoSim package | `Models/MoSimQuadrotorModel/package.mo` | Project-owned formal package surface. New accepted Sunray150 work should land here after checks. |
| Legacy implementation pool | `Models/QuadrotorExperiments/DynamicsUpgrade/` | Current dynamics implementation source and compatibility pool. |

The present model is not just the old `QuadChassis` seed anymore. The source
surface now contains a project-owned Sunray150 dynamics chain, but its
acceptance level is mixed.

### 3.1 Current Dynamics Source Chain

Implementation pool:

```text
Models/QuadrotorExperiments/DynamicsUpgrade/
  Sunray150ActuatorCommandMapper.mo
  Sunray150ActuatorMappedWrapperSurface.mo
  Sunray150RflyStyleRotorDynamics.mo
  Sunray150DynamicsWrapperSurface.mo
  Sunray150OptionalDampingGyroLayer.mo
  Sunray150PhysicalWrenchFrameAdapter.mo
  Sunray150RotorEffectivenessSmoke.mo
```

Formal package surface:

```text
Models/MoSimQuadrotorModel/Dynamics/
  ActuatorCommandMapper.mo
  ActuatorMappedWrapperSurface.mo
  RotorActuatorCore.mo
  WrapperSurface.mo
  OptionalDampingGyroLayer.mo
  PhysicalWrenchAdapter.mo
  *Smoke.mo aliases
```

The formal package currently acts mainly as an `extends`/alias surface over the
legacy implementation pool. That is acceptable for migration, but not enough
for final model acceptance.

### 3.2 Current Implemented Concepts

Current source already contains these concepts:

| Concept | Current state | Acceptance boundary |
|---|---|---|
| Rotor centers | DAE/Blender-derived Sunray150 positions are embedded in the dynamics core. | Geometry is accepted as geometry only; not mass/inertia/motor truth. |
| Command-to-speed mapping | `Sunray150ActuatorCommandMapper` maps normalized command to signed visual rotor speed and saturation residuals. | Mapping uses interface seeds such as hover command; not identified actuator truth. |
| Motor lag | `Sunray150RflyStyleRotorDynamics` has first-order motor lag with up/down time constants. | Values are SDF-migration seeds until identified or fitted. |
| Thrust | Per-rotor thrust uses `thrust_effectiveness * lift_coefficient * omega^2`; default effectiveness is 1. | Coefficient is a scaled SDF seed, not physical truth. |
| Yaw reaction moment | Per-rotor yaw reaction moment uses `reaction_moment_effectiveness * moment_constant * thrust`; default effectiveness is 1. | Sign/order and moment coefficient still need validation. |
| Rotor-center moment | Body moment uses rotor center cross thrust plus yaw moment. | Requires MWORKS check and scenario smoke evidence before behavior claims. |
| Optional drag/damping/gyro | `Sunray150OptionalDampingGyroLayer` has default-disabled drag, angular damping, and rotor gyro terms. | Default-off behavior is a design safeguard; enabled behavior needs parameter evidence. |
| Physical wrench adapter | `Sunray150PhysicalWrenchFrameAdapter` applies force/torque to a MultiBody body. | Needs live `check_model` and simulation evidence for canonical entry points. |
| Rotor effectiveness/fault | Source now contains per-rotor effectiveness, wrapper-level monitors, actuator-mapped monitor pass-through, and a single-rotor smoke model. | Static source validation passes; live MWORKS `check_model`/`SimulateModel` evidence is still required before behavior claims. |

User decision on 2026-06-11: keep the single-rotor effectiveness degradation
line and include it in the next model-simulation slice. As of the 2026-06-11
static checker alignment, the source/validator surface is consistent; it
remains behavior-unaccepted until the formal entry points pass live checks and
smoke simulations.

### 3.3 Current Parameter Truth Level

Use these labels until stronger evidence exists:

| Parameter group | Current source | Truth level |
|---|---|---|
| Rotor centers | DAE/Blender geometry audit | accepted geometry seed |
| Camera/collision geometry | DAE/scene mapping | geometry seed, not control truth |
| Mass/inertia | SDF/model seed and current wrapper constants | simulation seed, not identified truth |
| Thrust coefficient | Sunray SDF motor constant scaled by visual-speed convention | simulation seed, not identified truth |
| Yaw moment coefficient | SDF/reference seed | simulation seed, not identified truth |
| Motor time constants | SDF motor plugin seed | simulation seed, not identified truth |
| Drag/angular damping | zero or optional placeholder | not identified |
| Rotor inertia/gyro | zero or optional placeholder | not identified |
| Battery/ESC/thrust margin | not modeled as a formal layer | missing |
| Sensor noise/delay/bias | not a plant-core accepted layer | missing or adapter-level only |

The project may use seeds for model development, but reports must not call them
identified Sunray150 physical parameters.

## 4. Main Gaps Against An RflySim-Like Model

| Gap | Why it matters | Current MoSim state | Required next evidence |
|---|---|---|---|
| Formal model acceptance | A user-facing model must be loadable, checkable, and reproducible. | Formal `MoSimQuadrotorModel.Dynamics` is mostly an alias surface. | `check_model` for each canonical entry and smoke model. |
| Motor order and sign convention | Wrong order/sign can make yaw/fault/controller claims meaningless. | Source labels admit convention risk. | Hover, yaw-step, and one asymmetric-thrust smoke with expected signs. |
| Actuator mapping realism | Controller output must correspond to physically bounded motors. | Normalized mapping exists but uses placeholder hover command and max speed. | Identify or justify command units; add saturation metrics and actuator trace. |
| Force/moment application | Rotor dynamics must actually move the MultiBody plant correctly. | Physical wrench adapter exists. | `check_model` and short simulation with force/torque variables exported. |
| Parameter identification | Strong controller claims need credible plant parameters. | Most values are SDF seeds. | Follow `Docs/Workflows/identify_quadrotor_parameters.md` or simulation-fit evidence. |
| Drag/damping/gyro | Needed for higher-fidelity attitude/trajectory and robustness claims. | Optional layer exists, default disabled. | Default-off preservation proof, then enabled parameter-fit scenario. |
| Fault/disturbance | Required for robustness and fault-aware allocation studies. | Rotor effectiveness source and static validators are aligned; wind/fault scenarios exist elsewhere. | Live fault smoke simulation, fault command schema, event log, and controller response metrics. |
| Battery/ESC/thrust margin | Needed for saturation, payload, and voltage-sag realism. | Missing as formal plant layer. | Add optional bounded layer after nominal motor/force checks pass. |
| Sensor/noise/delay | Needed for estimator/planner realism. | Not a plant-core accepted layer. | Add after plant/controller loop is stable; keep source labels. |
| Environment/ground model | Needed for terrain, landing/contact, altitude, and HIL realism. | Terrain and contact are not formal accepted plant surfaces. | Reserve environment/ground contracts; implement only after core flight smoke passes. |
| HIL/MAVLink output bus | Needed for PX4/ArduPilot/QGC-compatible expansion. | Future interface contract only. | Define bus schema and source labels before any PX4/QGC runtime claim. |
| Failure assessment | Needed to separate injected fault, observed failure, and accepted/rejected scenario outcome. | Not formalized in MoSim model evidence. | Add event/failure-assessment labels before robustness acceptance. |

## 5. Optimization Roadmap

The model should be optimized in a staged way. Do not jump from source edits to
controller-performance claims.

### M0: Freeze Model Taxonomy And Evidence Rules

Goal: make the model structure understandable before more implementation.

Deliverables:

- this document as the active model-design source;
- README/index entry for the model-comparison document;
- list of current canonical and legacy dynamics entry points;
- decision recorded: keep the interrupted rotor-effectiveness source line, but
  validate it before making behavior claims.

Exit gate:

```text
No behavior claim. Only design and source inventory are accepted.
```

### M1: Nominal Rotor/Actuator Core

Goal: establish a credible RflySim-like nominal motor/rotor chain.

Scope:

- normalized command saturation;
- command-to-speed mapping;
- motor first-order lag;
- thrust = `k_f * omega^2`;
- yaw moment;
- rotor-center moment;
- wrapper total force/moment outputs.

Evidence:

```text
check_model:
  MoSimQuadrotorModel.Dynamics.RotorActuatorCore
  MoSimQuadrotorModel.Dynamics.WrapperSurface
  MoSimQuadrotorModel.Dynamics.ActuatorMappedWrapperSurface

simulate:
  hover smoke
  yaw-step smoke

export:
  motor command
  omega
  thrust
  total thrust
  body moment
  hover thrust error
  yaw moment gate
  saturation residual
```

Allowed claim after passing:

```text
The nominal source model has a checked motor/rotor force-moment surface.
```

Forbidden claim:

```text
Identified Sunray150 truth, controller improvement, closed-loop success.
```

### M2: Physical Wrench Integration

Goal: prove the rotor force/moment surface is applied to the MWORKS MultiBody
plant rather than remaining a disconnected calculator.

Scope:

- physical force/torque adapter;
- MultiBody body parameters with provenance labels;
- force/torque application variables;
- hover and yaw-step physical smoke.

Evidence:

```text
check_model:
  MoSimQuadrotorModel.Dynamics.PhysicalWrenchAdapter

simulate:
  PhysicalWrenchHoverSmoke
  PhysicalWrenchYawStepSmoke
```

Allowed claim after passing:

```text
The project-owned Sunray150 force/moment adapter can be checked and smoked in
MWORKS.
```

### M3: Optional Drag, Damping, And Rotor Gyro

Goal: add higher-fidelity terms without silently changing nominal behavior.

Scope:

- default-disabled rotor gyroscopic moment;
- default-disabled body drag;
- default-disabled angular damping;
- explicit parameter provenance;
- enabled-case smoke after parameters are selected.

Evidence:

```text
default_off_check:
  optional force delta == 0
  optional moment delta == 0

enabled_smoke:
  nonzero drag/damping/gyro terms produce expected sign and bounded magnitude
```

Allowed claim:

```text
Optional fidelity terms are available and default-safe.
```

Forbidden claim:

```text
Aerodynamic model has been identified or validated, unless parameter evidence
exists.
```

### M4: Fault And Disturbance Layer

Goal: make robustness experiments part of the plant contract, not scattered
scenario hacks.

Scope:

- per-rotor thrust effectiveness;
- per-rotor reaction moment effectiveness;
- wind/disturbance force or acceleration input;
- mass/inertia perturbation profile;
- event log and accepted/rejected command echo.

Immediate decision:

```text
The currently edited per-rotor effectiveness source should be either:
  A. kept and validated with live check_model + RotorEffectivenessSmoke
     simulation; or
  B. reshaped before making behavior or controller-response claims.

Static source status:

```text
2026-06-11:
  wrapper and actuator-mapped validators are aligned with per-rotor
  thrust/reaction-moment effectiveness.
  This is source validation only, not MWORKS runtime acceptance.
```
```

Evidence:

```text
check_model:
  MoSimQuadrotorModel.Dynamics.RotorEffectivenessSmoke

simulate:
  one nominal run
  one single-rotor effectiveness-loss run

metrics:
  total thrust loss
  roll/pitch/yaw imbalance
  event labels
```

Allowed claim:

```text
The plant has a checked rotor-effectiveness fault surface.
```

Forbidden claim:

```text
Fault-tolerant controller performance, until the controller scenario is run.
```

### M5: Parameter Identification Or Fit

Goal: move selected parameters from seed to evidence-backed values.

Primary route:

```text
PX4 ULog / bench / simulation-fit data
  -> identification output YAML
  -> MWORKS parameter mapping
  -> hover / yaw / trajectory validation
```

Follow:

```text
Docs/Workflows/identify_quadrotor_parameters.md
```

Target parameters:

- mass and inertia;
- motor command units and bounds;
- thrust coefficient;
- yaw moment coefficient;
- motor time constants;
- drag/damping coefficients;
- rotor inertia if rotor-gyro claims are needed.

Allowed claim:

```text
Parameter group X has source label Y and validation result Z.
```

### M6: Controller And Scenario Re-Validation

Goal: rerun selected control/scenario evidence on the improved plant.

Scope:

- official PID baseline re-run only where the plant changed enough to require
  comparison;
- selected optimized controller re-run;
- robustness/fault cases;
- selected formation case after single-UAV plant is stable.

Evidence:

```text
scenario config
  -> MWORKS check_model
  -> SimulateModel
  -> raw result
  -> metrics
  -> figure/replay
  -> report note
```

Allowed claim:

```text
Controller/scenario result under improved plant, with exact run_id.
```

## 6. Immediate Engineering Slice After This Document

Do not start by changing controller gains. Start by closing the smallest model
slice that increases plant credibility.

Recommended first executable task:

```text
M1/M4 decision slice:
  1. keep current rotor-effectiveness source line and validate it;
  2. run static source checks for package/order and alias consistency;
  3. run MWORKS check_model for the relevant Dynamics aliases;
  4. simulate hover/yaw/effectiveness smoke only if check_model passes;
  5. save evidence under:
     Results/mworks_model_optimization/20260611_rotor_actuator_core/
```

Expected evidence files:

```text
Results/mworks_model_optimization/20260611_rotor_actuator_core/
  check_model/
  simulations/
  metrics/
  source_inventory.json
  model_optimization_note.md
```

If live MWORKS is blocked by activation, license, GUI error, or unknown window
state, stop and return a blocker. Do not keep tuning `.mo` files without a
model check path.

## 7. User-Confirmed Decisions

The following decisions were confirmed by the user on 2026-06-11 and should be
treated as the current model-optimization baseline until superseded:

1. Keep the single-rotor effectiveness degradation line.
2. Include the single-rotor effectiveness smoke in the next simulation slice
   together with nominal hover/yaw checks.
3. Use `MoSimQuadrotorModel.Dynamics` as the formal user-facing model entry
   surface. Keep legacy `QuadrotorExperiments.DynamicsUpgrade` names visible in
   evidence notes only as implementation provenance and compatibility paths
   until all aliases are checked.
4. Use current parameters for the next phase: accepted DAE assembly geometry
   plus existing model/SDF-migration parameter seeds. Do not wait for PX4 or
   bench identification before the next model-simulation slice. Keep provenance
   labels clear; these parameters are still not `ulog_identified` truth.

## 8. Model Structure Tree

Target formal entry tree:

```text
MoSimQuadrotorModel
  Baseline
    official upstream examples and chassis reference

  Dynamics
    ActuatorCommandMapper
      normalized actuator command
      command saturation
      signed visual rotor-speed command

    RotorActuatorCore
      rotor centers from DAE assembly geometry
      motor first-order lag
      thrust = thrust_effectiveness * lift_coefficient * omega^2
      yaw reaction moment = reaction_moment_effectiveness * moment_constant * thrust
      rotor-center moment
      per-rotor thrust effectiveness
      per-rotor reaction-moment effectiveness

    WrapperSurface
      motor command input surface
      total thrust output
      body moment output
      hover thrust error
      yaw moment gate
      minimum thrust/reaction-moment effectiveness monitors
      motor-order and yaw-direction gates

    ActuatorMappedWrapperSurface
      normalized actuator command input
      command mapper
      wrapper force/moment surface
      saturation residuals
      wrapper effectiveness monitor pass-through

    OptionalDampingGyroLayer
      default-disabled rotor gyro
      default-disabled body drag
      default-disabled angular damping
      default-off preservation variables

    PhysicalWrenchAdapter
      MultiBody body
      WorldForceAndTorque application
      applied force and torque checks

    HoverSmoke
      nominal rotor hover check

    YawStepSmoke
      nominal yaw-moment/sign check

    RotorEffectivenessSmoke
      single-rotor effectiveness degradation smoke

    WrapperHoverSmoke
      wrapper-level hover check

    WrapperYawStepSmoke
      wrapper-level yaw-step check

    PhysicalWrenchHoverSmoke
      physical force application hover check

    PhysicalWrenchYawStepSmoke
      physical force/moment application yaw-step check

  Parameters
    Sunray150ParameterProvenance
      DAE assembly geometry provenance
      existing model / SDF_migration seed provenance
      future identified-parameter records

  Sensors
    ImuModel
      rate, bias, noise, delay, frame

    LidarModel
      MID360-like scan profile, extrinsic, timestamp, validity

    CameraModel
      front/down camera extrinsic, frame, timestamp, image source

    GpsBarometerMagnetometerModels
      optional navigation sensors for PX4/QGC/post-competition use

    SensorFaultAndDegradation
      dropout, delay, bias, noise, invalid-state echo

  Controllers
    PIDBaseline
    ImprovedPID / AWFFPID
    INDI / PID-INDI
    LinearMPC
    NMPC
    L1ResidualCompensation
    SafetyFilter
    FaultAllocation

  Runtime
    RunState
      run_id, scenario_id, vehicle_id, controller_id

    ClockAndRate
      solver time, sample time, setpoint rate, sensor rate

    FlightModeAndFailsafe
      mode, arming/enable state, stale-command timeout, estimator validity

    EventLog
      command accepted/rejected, fault active, safety/failsafe reason

  Interfaces
    MworksNativeSetpointAdapter
      PlannerSetpoint / MissionSetpoint to MWORKS controller input

    UECommandEchoAdapter
      UE request packet, accepted/rejected echo, display-only state

    ROS2BridgeAdapter
      topic/rate/frame boundary for IMU/LiDAR/odometry/planner traces

    PX4QgcAdapter
      post-competition Offboard/SITL/HIL/QGC-compatible semantics

  Missions
    official examples
    step / hover / yaw
    helix / spiral climb
    figure-8
    obstacle / corridor / waypoint

  Experiments
    ExperimentProfile
      scenario + vehicle + controller + plant + disturbance + sensor profile

    BatchCampaign
      repeatable comparison campaign and selected report runs

    RunManifest
      raw result, metrics, figures, screenshots, logs, evidence labels

  Robustness
    mass perturbation
    wind gust
    external disturbance
    rotor loss / effectiveness loss
    safety return / land

  Planning
    QuinticReference
    waypoint / polynomial trajectory
    local planner and smoothing
    planner display/review helpers

  Formation
    leader-follower
    virtual structure
    formation metrics
    inter-UAV collision constraints

  SceneTrace
    accepted UE scenes
    trace isolation diagnostics
    visual/review surfaces

  System
    architecture diagrams
    subsystem wiring/layout reviews
    hardware abstraction

  Support
    trace tables
    MCP/tool helper models
    echo/state helper surfaces

  LegacyCompatibility
    legacy QuadrotorExperiments aliases
```

Implementation provenance tree:

```text
MoSimQuadrotorModel.Dynamics.* formal aliases
  -> QuadrotorExperiments.DynamicsUpgrade short package entries
    -> Sunray150ActuatorCommandMapper.mo
    -> Sunray150RflyStyleRotorDynamics.mo
    -> Sunray150DynamicsWrapperSurface.mo
    -> Sunray150ActuatorMappedWrapperSurface.mo
    -> Sunray150OptionalDampingGyroLayer.mo
    -> Sunray150PhysicalWrenchFrameAdapter.mo
    -> Sunray150RotorEffectivenessSmoke.mo
```

Target package staging:

```text
current checked/migration focus:
  Baseline
  Dynamics
  Parameters
  Missions
  Controllers
  Robustness
  Planning
  SceneTrace
  System
  Formation
  Support
  LegacyCompatibility

design-only reserved branches before implementation:
  Sensors
  Runtime
  Interfaces
  Experiments
```

Do not create or advertise the reserved branches as accepted package-browser
entries until a separate package migration batch adds package files,
`package.order` entries, reference updates, and MWORKS checks.

## 9. Long-Term Architecture Contract

The full target structure is designed now so later UE, ROS2, PX4/QGC, sensors,
formation, and report automation do not force another plant-package rewrite.
This section is an architecture contract, not an implementation claim.

### 9.1 Stable Core

The stable core is the minimum model surface that every later stage must
respect:

```text
Dynamics
  -> Parameters
  -> Controllers
  -> Runtime
  -> Interfaces
  -> Experiments
```

Rules:

1. `Dynamics` is the model-package source for physical forces, moments, states,
   faults, and plant events. At system level, this evidence is reported through
   the Runtime Plant role rather than as a generic MWORKS success claim.
2. `Parameters` owns provenance and truth labels. Controllers, planners, and
   reports consume parameters through labels, not through hidden constants.
3. `Controllers` consume state/setpoint/fault surfaces and output bounded
   actuator or thrust/moment commands. They do not own plant truth.
4. `Runtime` owns run identity, time/rate semantics, stale-command handling,
   mode/failsafe state, and event logging.
5. `Interfaces` adapt external surfaces such as UE, ROS2, PX4/QGC, and native
   setpoint paths. Adapters must echo accepted/rejected commands and must not
   bypass the MWORKS plant for dynamics claims.
6. `Experiments` binds scenario, vehicle, controller, parameter profile,
   disturbance/fault profile, sensor profile, and evidence output into a
   reproducible run manifest.

If a later feature cannot fit into this core without changing the meaning of
`Dynamics`, `Parameters`, `Runtime`, or `Experiments`, treat it as an
architecture review item before changing `.mo` packages.

### 9.2 Why The Reserved Branches Exist Now

`Sensors`, `Runtime`, `Interfaces`, and `Experiments` are reserved before they
are implemented because they prevent four common design traps:

| Reserved branch | Trap avoided | Required future role |
|---|---|---|
| `Sensors` | Treating UE/ROS visual or LiDAR output as plant truth. | IMU/LiDAR/camera/GPS/barometer/magnetometer noise, delay, frame, timestamp, and degradation contracts. |
| `Runtime` | Mixing solver time, controller sample time, sensor time, and external command freshness in scenario code. | Run identity, clocks, rates, flight mode, failsafe, stale-command timeout, and event log. |
| `Interfaces` | Letting PX4/QGC/ROS2/UE semantics leak into the plant or controller internals. | Bounded adapters with command echo, frame/rate contracts, and display-vs-authority separation. |
| `Experiments` | Scattering repeatable runs across ad hoc YAML/scripts/results names. | Run manifests, batch campaigns, evidence labels, metric/figure/replay output routing. |

These branches should be introduced into the real package tree only when their
first class has a concrete interface, package entry, reference update, and
MWORKS check path.

### 9.3 Stage-To-Branch Activation Plan

The project can design the final system now while activating branches in a
safe order:

```text
Stage A: Plant credibility
  Active:
    Dynamics
    Parameters
  Evidence:
    check_model
    hover/yaw/effectiveness smoke
    force/moment/result variables

Stage B: Controller comparison on improved plant
  Active:
    Controllers
    Missions
    Robustness
    Experiments (first manifest-level surface)
  Evidence:
    scenario config
    SimulateModel
    metrics
    figures
    report notes

Stage C: Runtime discipline
  Active:
    Runtime
    Interfaces.MworksNativeSetpointAdapter
  Evidence:
    run_id
    command accepted/rejected echo
    stale-command and failsafe events
    rate/sample-time trace

Stage D: Sensor and planning realism
  Active:
    Sensors
    Planning
    Interfaces.ROS2BridgeAdapter
  Evidence:
    frame/timestamp/rate contracts
    estimator/planner trace
    no claim of closed-loop autonomy unless acceptance gates pass

Stage E: Multi-UAV and visualization platform
  Active:
    Formation
    SceneTrace
    Interfaces.UECommandEchoAdapter
  Evidence:
    formation metrics
    inter-UAV separation checks
    UE display echo and review artifacts

Stage F: PX4/QGC-compatible expansion
  Active:
    Interfaces.PX4QgcAdapter
    optional navigation sensors
  Evidence:
    Offboard/SITL/HIL/QGC command semantics
    estimator validity
    command echo and failsafe behavior
```

Stage order is not a claim that all later stages must wait for perfect earlier
stages. It is a rule for authority: later adapters and displays cannot
invalidate or replace the MWORKS plant evidence.

### 9.4 Current Model Sufficiency Judgment

The current model structure is sufficient to support the next executable
simulation slice, but not sufficient to support final RflySim-like platform
claims.

Sufficient now:

- a formal `MoSimQuadrotorModel.Dynamics` entry surface exists;
- actuator mapping, rotor dynamics, yaw moment, force/moment aggregation,
  optional damping/gyro layer, physical wrench adapter, and rotor-effectiveness
  source surfaces exist;
- current parameter seeds are enough for smoke and model-credibility work when
  labelled as seeds.

Not sufficient yet:

- current dynamics aliases still need live `check_model` and smoke evidence;
- mass, inertia, thrust, moment, drag, damping, motor lag, and rotor inertia
  are not identified Sunray150 truth;
- sensor noise/delay/bias and estimator contracts are not formal accepted
  package surfaces;
- runtime semantics such as command freshness, event logging, and failsafe are
  design-only until implemented;
- PX4/QGC compatibility is a future interface contract, not a current control
  dependency;
- controller performance, closed-loop autonomy, planner readiness, and final
  platform acceptance remain forbidden claims until their evidence gates pass.

Therefore the correct next engineering move is still model-level validation:
check and smoke the current `Dynamics` entry surface, including the single
rotor-effectiveness slice, before expanding into controller tuning or external
runtime integration.

Parameter provenance for the next executable slice:

```text
rotor/camera/body geometry:
  source = DAE_geometry / assembly audit

mass / inertia / lift coefficient / moment coefficient / motor time constants:
  source = existing model or SDF_migration seed

single-rotor effectiveness degradation:
  source = simulation fault seed

identified physical parameters:
  source = none yet
```
