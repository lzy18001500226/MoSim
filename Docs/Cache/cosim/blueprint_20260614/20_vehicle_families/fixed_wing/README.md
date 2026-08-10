# Fixed-Wing Family

Status: discussion draft, 2026-06-14.

## 1. Scope

This family covers benign fixed-wing model-aircraft simulation:

- six-degree-of-freedom aircraft dynamics;
- aerodynamic coefficient and propulsion modeling;
- control surfaces, servos, landing gear, and actuator limits;
- ArduPlane, generated controller, or custom controller routes;
- GPS/mission-oriented flight;
- UE aircraft visualization and replay;
- SIL/HIL/real-flight migration after separate safety review.

## 2. Default Route

| Surface | Default |
|---|---|
| Plant truth | JSBSim |
| Flight control | ArduPlane or generated controller |
| Algorithm bus | ROS2 optional; MAVLink/QGC/MAVSDK for autopilot ecosystem |
| Frontend | UE |
| Controller design | Simulink after competition; MWORKS only if explicitly scoped |

## 3. Capability Tree

```text
fixed_wing
  aircraft model
    geometry
    mass and inertia
    aero coefficient tables
    propulsion
    control surfaces and actuators
    landing gear / ground reaction

  control and mission
    manual/assisted modes
    ArduPlane SITL
    generated controller candidate
    route/mission planning
    GPS and navigation state

  evidence
    JSBSim batch logs
    ArduPlane SITL logs
    UE aircraft animation
    model-fidelity label
```

## 4. Key Architecture Decisions

1. Gazebo LiftDrag-style modeling is not the default for serious fixed-wing
   aero truth.
2. JSBSim is the default fixed-wing plant candidate.
3. ArduPlane is the default fixed-wing autopilot candidate.
4. Fixed-wing LiDAR/SLAM is not the main first route; GPS/mission and aero
   fidelity are more central.
5. Visual aircraft meshes do not prove aero fidelity.

## 5. First Architecture Gaps

- Fixed-wing model-fidelity levels.
- Initial benign open aircraft model selection.
- JSBSim/ArduPlane smoke path.
- Simulink-generated fixed-wing controller target decision.
- UE aircraft state/control-surface animation contract.

