# Ducted Model-Aircraft Family

Status: discussion draft, 2026-06-14.

## 1. Scope

This family covers benign ducted model-aircraft and test-body simulation. It is
for hobby/model-aircraft, propulsion/control research, and non-destructive
simulation.

Out of scope:

- weaponization;
- targeting;
- destructive payloads;
- terminal guidance for harm;
- deployment guidance for destructive systems.

## 2. Default Route

| Surface | Candidate |
|---|---|
| Plant truth | JSBSim or custom six-DOF backend |
| Flight control | custom controller, ArduPilot route if applicable, or generated controller |
| Algorithm bus | optional ROS2 |
| Frontend | UE |
| Controller design | Simulink generated C/C++ candidate |

## 3. Capability Tree

```text
ducted_model_aircraft
  model-fidelity levels
    visual animation
    control-law research
    flight-envelope research
    identified model

  dynamics
    mass and inertia
    thrust curve
    aerodynamic force/moment approximation
    actuator delay and saturation
    wind/disturbance profile

  control
    attitude stabilization
    speed/altitude guidance for benign test paths
    RC/autopilot/generated-controller adapters

  evidence
    open-loop trajectory smoke
    closed-loop stabilization smoke
    UE replay
    parameter provenance
```

## 4. Key Architecture Decisions

1. Start with fidelity levels, not a claim of exact real-world model.
2. JSBSim is a strong candidate if the body behaves like an aircraft and
   aerodynamic coefficients can be represented.
3. A custom six-DOF backend may be better for very short-duration special
   model-aircraft tests.
4. UE remains display/review, not physics truth.

## 5. First Architecture Gaps

- Define first benign scenario.
- Define allowed controller tasks and safety boundaries.
- Choose JSBSim vs custom six-DOF first prototype.
- Identify what physical parameters can be measured or estimated.

