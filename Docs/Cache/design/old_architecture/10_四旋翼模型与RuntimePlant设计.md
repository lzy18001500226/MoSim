# 10 四旋翼模型与 Runtime Plant 设计

Status: source design, 2026-06-14.

This document is the compact source design for the MoSim quadrotor model and
CopterSim-like Runtime Plant. It absorbs the stable semantics from the previous
model migration, RflySim/CopterSim comparison, and long model-optimization
notes. The superseded long-form drafts remain under:

```text
Docs/Cache/design/historical_snapshots/absorbed_or_superseded_20260614/
```

## 1. Scope

MoSim uses RflySim/CopterSim as a structure reference, not as Sunray150
parameter truth.

For the current project, the Runtime Plant means:

```text
actuator command
  -> command bounds and mapping
  -> motor / propeller dynamics
  -> per-rotor force and moment
  -> 6DOF body dynamics
  -> truth state, sensor streams, events, and metrics
```

MWORKS currently hosts the formal plant implementation. Long term, the same
contract may be implemented by a separated runtime process, generated C/C++,
Simulink, PX4/HIL, or another backend. The public contract must not depend on
MWORKS internal variable names.

## 2. RflySim / CopterSim Capability Map

A mature RflySim-like plant is broader than a nominal rotor force equation.
The local RflySim/CopterSim references show these capability families:

| Capability | RflySim-like role | MoSim design target |
|---|---|---|
| Airframe profile | vehicle type, mass, inertia, initial state, GPS/map origin | `VehicleProfile` with provenance labels |
| Actuator and motor | PWM/throttle input, dead zone, motor count, time constant, motor speed | `ActuatorCommandMapper` + motor dynamics |
| Propeller / force moment | thrust coefficient, moment coefficient, arm geometry, drag/damping | `RotorActuatorCore` and force/moment surface |
| 6DOF body | multirotor state integration | MWORKS plant first, backend-replaceable later |
| Environment and ground | gravity, atmosphere, wind, terrain/contact | reserved Runtime Plant surfaces |
| Sensors | IMU/GPS/barometer/magnetometer/noise/HIL messages | `SensorObservationLayer` contracts in `04/05` |
| Faults | motor/propeller/payload/battery/wind faults and failure assessment | fault/event layer with metrics and command echo |
| HIL / MAVLink | PX4/QGC-compatible output bus | future adapter, not current plant truth |
| Parameter/fault API | initialization and runtime injection | `RunManager` config and command/echo adapters |

MoSim must copy this separation of concerns, not the sample numeric parameters.

## 3. Current MoSim Model Ownership

| Layer | Path | Role |
|---|---|---|
| Official baseline | `References/MWORKS/QuadrotorModel/package.mo` | Tongyuan/upstream reference and regression baseline. |
| Formal project model | `Models/MoSimQuadrotorModel/package.mo` | User-facing project-owned MoSim quadrotor package. |
| Legacy compatibility pool | `Models/QuadrotorExperiments/` | Historical experiments and implementation provenance. |

The formal entry for current model work is:

```text
MoSimQuadrotorModel.Dynamics
```

Legacy `QuadrotorExperiments` paths may appear in evidence as provenance, but
new accepted design claims should name the formal package surface.

## 4. Target Model Structure

```text
MoSimQuadrotorModel
  Dynamics
    ActuatorCommandMapper
    RotorActuatorCore
    WrapperSurface
    ActuatorMappedWrapperSurface
    OptionalDampingGyroLayer
    PhysicalWrenchAdapter
    HoverSmoke
    YawStepSmoke
    RotorEffectivenessSmoke
    PhysicalWrenchHoverSmoke
    PhysicalWrenchYawStepSmoke

  Parameters
    geometry provenance
    SDF/model seed provenance
    future identified-parameter records

  Controllers
    PID baseline
    improved PID / AWFF
    INDI / PID-INDI
    LinearMPC / NMPC
    L1 residual compensation
    safety filter
    fault allocation

  Runtime
    run identity
    clock/rate policy
    flight mode and stale-command behavior
    event log

  Interfaces
    MWORKS native setpoint adapter
    ROS2 bridge adapter
    UE command/echo adapter
    future PX4/QGC adapter

  Sensors
    IMU
    MID-360-like LiDAR
    camera/depth
    GPS/barometer/magnetometer where needed

  Experiments
    run manifest
    batch campaign
    scenario/controller/plant binding
```

Only implemented and checked package entries should be exposed as accepted
MWORKS model claims. Reserved branches are design targets until package files,
references, and model checks exist.

## 5. Current Implemented Concepts

Current source already contains these concepts in the project model or
implementation pool:

| Concept | Current status | Claim boundary |
|---|---|---|
| Rotor centers | DAE/Blender-derived Sunray150 positions are used in the dynamics surface. | Accepted as geometry only. |
| Command mapping | Normalized command to signed rotor-speed command with saturation residuals. | Not identified actuator truth. |
| Motor lag | First-order motor lag exists in the RflySim-style rotor dynamics source. | Time constants remain seed values. |
| Thrust | Per-rotor `k_f * omega^2` style surface exists. | Coefficient is seed/provenance-labelled. |
| Yaw reaction moment | Per-rotor yaw moment surface exists. | Sign/order must be validated by smoke. |
| Rotor-center moment | Body moment from rotor center and thrust exists in source. | Needs check/simulation evidence for behavior claims. |
| Optional drag/damping/gyro | Default-disabled optional layer exists. | Not identified or accepted until enabled evidence exists. |
| Physical wrench adapter | MultiBody force/torque adapter exists. | Needs live `check_model`/smoke per entry. |
| Rotor effectiveness fault | Per-rotor effectiveness line is preserved. | Needs live fault smoke before controller claims. |

## 6. Parameter Truth Policy

Use provenance labels instead of generic "true parameter" wording.

| Parameter group | Current source | Truth level |
|---|---|---|
| Rotor/camera/collision geometry | DAE/Blender audit | accepted geometry seed |
| Mass and inertia | existing model / SDF migration | simulation seed |
| Thrust coefficient | scaled SDF/model seed | simulation seed |
| Yaw moment coefficient | SDF/reference seed | simulation seed |
| Motor time constants | model/plugin seed | simulation seed |
| Drag and angular damping | optional/default-off placeholders | not identified |
| Rotor inertia/gyro | optional/default-off placeholders | not identified |
| Battery/ESC/thrust margin | not formalized yet | missing |
| Sensor noise/delay/bias | adapter/design surface only | missing or unaccepted |

Strong physical claims require PX4 ULog, bench, or simulation-fit evidence as
defined by `Docs/Workflows/identify_quadrotor_parameters.md`.

## 7. Main Gaps Against RflySim-Like Runtime Plant

These are design and evidence gaps, not only implementation backlog:

| Gap | Required design/evidence |
|---|---|
| Formal model acceptance | Canonical entry points, `package.order`, `check_model`, smoke evidence. |
| Motor order and sign convention | Hover, yaw-step, asymmetric-thrust/fault smoke with expected signs. |
| Actuator realism | Command units, bounds, hover command, saturation metrics, actuator trace. |
| Force/moment application | Exported force/torque variables and physical adapter smoke. |
| Parameter identification | Provenance-labelled identified values or explicit seed status. |
| Drag/damping/gyro | Default-off preservation, then enabled bounded-sign smoke. |
| Fault/disturbance layer | Fault command schema, event log, plant response metrics. |
| Battery/ESC/thrust margin | Optional bounded layer after nominal plant passes. |
| Sensor/noise/delay | Sensor contract and validation before estimator/planner claims. |
| Environment/ground/contact | Reserved design surface until landing/contact is in scope. |
| HIL/MAVLink output bus | Future adapter schema and PX4/QGC evidence gate. |
| Failure assessment | Separate injected fault, observed failure, and scenario outcome. |

## 8. Optimization Roadmap

### M1: Nominal Rotor / Actuator Core

Scope:

- command saturation;
- command-to-speed or command-to-thrust mapping;
- motor first-order lag;
- thrust and yaw reaction moment;
- rotor-center body moment;
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
```

### M2: Physical Wrench Integration

Scope:

- force/torque adapter;
- MultiBody body parameters with provenance;
- physical hover/yaw smoke.

Evidence:

```text
check_model:
  MoSimQuadrotorModel.Dynamics.PhysicalWrenchAdapter

simulate:
  PhysicalWrenchHoverSmoke
  PhysicalWrenchYawStepSmoke
```

### M3: Optional Drag, Damping, And Rotor Gyro

Scope:

- default-disabled rotor gyro;
- default-disabled body drag;
- default-disabled angular damping;
- enabled-case evidence only after parameter choice.

Default-off behavior must be preserved unless the active task explicitly opens
parameter identification or fitted-model validation.

### M4: Fault And Disturbance Layer

Scope:

- per-rotor thrust effectiveness;
- per-rotor reaction-moment effectiveness;
- wind/disturbance input;
- mass/inertia perturbation profile;
- event log and accepted/rejected command echo.

Immediate decision: keep the single-rotor effectiveness degradation line and
include it in the next model-simulation slice.

### M5: Parameter Identification Or Fit

Primary route:

```text
PX4 ULog / bench / simulation-fit data
  -> identification output YAML
  -> MWORKS parameter mapping
  -> hover / yaw / trajectory validation
```

### M6: Controller And Scenario Re-Validation

After plant changes, rerun only the scenarios needed for the claim:

- official PID baseline where required;
- selected optimized controller;
- robustness/fault slice;
- formation slice only after single-UAV evidence is stable.

## 9. Runtime Plant Acceptance Boundary

Allowed claim after model-level smoke:

```text
The nominal source model has a checked motor/rotor force-moment surface.
```

Forbidden without additional evidence:

```text
identified Sunray150 truth
controller performance improvement
closed-loop autonomy
PX4/HIL compatibility
FAST-LIO/planner readiness
final platform acceptance
```

## 10. Relationship To Other Design Files

| Topic | Source |
|---|---|
| System scope and phases | `01_系统目标与需求边界.md` |
| Four-layer architecture and RflySim/MoSim authority split | `02_总体架构与权威边界.md` |
| Module map and adapters | `03_核心模块设计.md` |
| Controller ABI, topics, frames, rates | `04_接口数据契约与时钟频率.md` |
| UE/ROS2/FAST-LIO sensor and local-map path | `05_场景传感器与UE_ROS2链路.md` |
| Control, planning, safety, model credibility, metrics | `06_控制规划安全与评估目标.md` |
| Evidence and acceptance gates | `07_验收Gate与交付物.md` |
| Current status matrix | `08_赛题闭环实现证据矩阵.md` |
| Multi-UAV formation model/data design | `09_多机编队架构与数据设计.md` |
