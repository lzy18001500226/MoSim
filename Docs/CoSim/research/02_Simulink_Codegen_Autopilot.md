# Simulink / Generated Code / Autopilot Deployment

Status: reviewed research decision draft, 2026-06-14.

Source raw notes:

- `research/raw/PX4-Autopilot.md`
- `research/raw/MAV层.md`
- `Docs/Design/README.md`
- `Docs/Design/架构/01_控制器平台/统一控制接口.md`

External sources:

- MathWorks UAV Toolbox Support Package for PX4 Autopilots: https://www.mathworks.com/help/uav/px4-spkg.html
- MathWorks Integration with General PX4 Architecture: https://www.mathworks.com/help/uav/px4/ug/px4-capabilities-integration.html
- MathWorks UAV Toolbox Support Package for ArduPilot Autopilots: https://www.mathworks.com/help/uav/ardupilot-spkg.html

## 1. Position

Simulink is the long-term controller design, model-based design, generated
code, SIL/PIL/HIL, and autopilot-integration route. It is not the default
world simulator or UE renderer.

In CoSim, Simulink/MWORKS-style model tools should connect through stable
controller and plant contracts:

```text
ControllerInput -> controller implementation -> ControllerOutput
```

The implementation behind that controller may be MWORKS Equation, Simulink
simulation, generated C/C++, a PX4 module, an ArduPilot module, or a ROS2
external controller.

## 2. Best-Fit Vehicle Families

| Vehicle family | Fit | Reason |
|---|---|---|
| Multirotor | default controller design route | Supports PX4 deployment and controller replacement patterns. |
| Fixed-wing | strong candidate | MathWorks ArduPilot support covers ArduPlane route; fixed-wing control design is Simulink-friendly. |
| VTOL | strong candidate | Simulink is useful for transition-control design, state machines, and HIL. |
| Ducted model-aircraft | optional | Useful for control-law prototyping and generated C/C++; plant fidelity depends on backend. |

## 3. Authority Classification

| Authority surface | Classification |
|---|---|
| Plant truth | Only owns plant truth when a Simulink plant is the declared physics backend for a run. |
| Flight-control authority | May own controller authority as generated code, PX4 module, ArduPilot module, or external node. |
| ROS2 / algorithm bus | Can interface through ROS Toolbox or generated nodes, but ROS2 bus authority remains separate. |
| UE / rendering frontend | No direct rendering authority. |
| Sensor generation | Can simulate sensor values in model/HITL contexts; must label source and fidelity. |
| RL / batch training | Useful for controller research but not the fastest large-scale RL backend. |
| SIL / HIL / deployment | Strong route through generated C/C++, PIL, HITL, PX4/ArduPilot support packages. |

## 4. Integration Pattern

Preferred controller abstraction:

```text
Scenario / VehicleProfile / SensorFrame
  -> ControllerInput
  -> Simulink model or generated controller
  -> ControllerOutput
  -> PX4 / ArduPilot / direct actuator / plant adapter
  -> logs and equivalence checks
```

Deployment modes:

| Mode | Meaning |
|---|---|
| MIL | Simulink/MWORKS model execution only. |
| SIL | Generated code runs on host and is compared with model behavior. |
| PIL | Generated code runs on target processor and is compared with model behavior. |
| HIL | Real flight controller participates with simulated plant/sensors. |
| Flight deployment | Generated or integrated code runs on real autopilot, after separate safety gates. |

## 5. Strengths

- Fits the user's plan to return to Simulink after the competition.
- Supports generated C/C++ and autopilot integration paths.
- Good for controller design, state machines, parameter tuning, and evidence
  reports.
- Creates a clean replacement path away from MWORKS without changing the public
  controller ABI.

## 6. Gaps And Risks

- Generated code is not automatically deployable just because a model runs.
- PX4 and ArduPilot integration are different products and must not be merged
  into one generic "autopilot codegen" claim.
- Simulink plant and Gazebo/JSBSim plant can create double truth if both
  integrate the same vehicle state.
- License/toolbox availability and supported firmware versions are moving
  dependencies that require live verification before implementation.

## 7. CoSim Adoption Decision

Decision: default future controller design and generated-code route.

It should be integrated through stable contracts first, then backend-specific
wrappers:

- PX4 module or uORB interface for PX4 vehicles;
- ArduPilot/ArduPlane integration for fixed-wing and ArduPilot vehicles;
- ROS2 external controller for research workflows;
- direct actuator adapter for RL/simplified plants.

## 8. Required Next Evidence

- Freeze `ControllerInput` and `ControllerOutput` fields across MWORKS,
  Simulink, generated C/C++, PX4, ArduPilot, and ROS2.
- Minimum generated-controller smoke: model run, code generation, host SIL,
  numerical equivalence, and logged controller outputs.
- Autopilot path decision per vehicle family: PX4 module, ArduPilot module,
  ROS2 external controller, or direct actuator.
- Version matrix for MATLAB/Simulink/UAV Toolbox/Embedded Coder/PX4/ArduPilot.
