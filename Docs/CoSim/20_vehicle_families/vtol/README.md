# VTOL Family

Status: discussion draft, 2026-06-14.

## 1. Scope

This family covers vertical-takeoff fixed-wing or quadplane-style vehicles:

- hover mode;
- transition mode;
- fixed-wing cruise mode;
- transition control and envelope protection;
- PX4 VTOL / ArduPilot QuadPlane / generated-controller routes;
- UE visualization across mode changes.

## 2. Default Route

The first practical route should be PX4 VTOL + Gazebo when engineering
autopilot behavior is the goal. JSBSim becomes important when fixed-wing aero
truth dominates the question.

| Surface | Candidate |
|---|---|
| Plant truth | Gazebo for PX4 engineering route; JSBSim/hybrid model for aero studies |
| Flight control | PX4 VTOL, ArduPilot QuadPlane, or generated controller |
| Algorithm bus | ROS2 |
| Frontend | UE |

## 3. Capability Tree

```text
vtol
  hover
    multirotor dynamics
    position hold
    takeoff/landing

  transition
    mode switch
    airspeed envelope
    actuator blending
    safety fallback

  cruise
    fixed-wing lift/drag
    route following
    energy management

  evidence
    mode-state log
    transition trajectory
    actuator allocation
    UE visual mode state
```

## 4. Key Architecture Decisions

1. VTOL must not be treated as "multirotor plus fixed-wing mesh."
2. Transition is its own authority surface and needs explicit mode-state
   evidence.
3. Gazebo and JSBSim must not both integrate the same vehicle truth unless a
   formal coupled model is designed.
4. The first version should probably use an existing PX4/ArduPilot VTOL route
   before custom aircraft dynamics.

## 5. First Architecture Gaps

- Choose first VTOL route: PX4 Gazebo target vs JSBSim aero prototype.
- Define transition-state contract.
- Define actuator-blending output and evidence.
- Define UE mode visualization.

