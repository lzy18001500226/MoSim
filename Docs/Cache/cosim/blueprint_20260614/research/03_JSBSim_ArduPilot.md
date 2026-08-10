# JSBSim / ArduPilot

Status: reviewed research decision draft, 2026-06-14.

Source raw notes:

- `research/raw/JSBSim.md`
- `research/raw/固定翼仿真.md`

External sources:

- JSBSim project page: https://jsbsim-team.github.io/jsbsim/
- JSBSim overview manual: https://jsbsim-team.github.io/jsbsim-reference-manual/user/overview/
- ArduPilot SITL with JSBSim: https://ardupilot.org/dev/docs/sitl-with-jsbsim.html

## 1. Position

JSBSim is the default fixed-wing and aircraft flight-dynamics-model candidate.
It is a data-driven six-degree-of-freedom aerospace dynamics library, not a
high-fidelity map, ROS2 system bus, or UE renderer.

ArduPilot/ArduPlane is the natural fixed-wing autopilot route. Together they
give CoSim a fixed-wing line that is not forced through multirotor Gazebo
semantics.

## 2. Best-Fit Vehicle Families

| Vehicle family | Fit | Reason |
|---|---|---|
| Fixed-wing | default | JSBSim models aero, propulsion, mass, ground reactions, FCS, and logs through XML/property-tree concepts. |
| VTOL | strong candidate | Useful for aircraft-like cruise/transition modeling, but VTOL integration must avoid double truth with Gazebo. |
| Ducted model-aircraft | candidate | Suitable for benign test-body / model-aircraft dynamics when aero and propulsion dominate. |
| Multirotor | reference only | Possible in theory, but Gazebo/PX4 is a better engineering default for multirotor robotics. |

## 3. Authority Classification

| Authority surface | Classification |
|---|---|
| Plant truth | JSBSim may own fixed-wing/aircraft plant truth. |
| Flight-control authority | ArduPlane, internal JSBSim FCS, Simulink-generated controller, or external controller may own control authority depending on run mode. |
| ROS2 / algorithm bus | Optional bridge for mission, telemetry, logging, and algorithm integration. |
| UE / rendering frontend | UE consumes JSBSim state and animates aircraft/scene; it does not own aircraft dynamics. |
| Sensor generation | JSBSim can output aircraft state and some sensor-like data; detailed LiDAR/vision remains external. |
| RL / batch training | JSBSim batch mode is useful for aero/control sweeps; not a generic GPU RL engine. |
| SIL / HIL / deployment | Strong path through ArduPilot SITL/HIL and Simulink/ArduPilot support where applicable. |

## 4. Integration Pattern

```text
AircraftProfile XML / aero database / mass / propulsion
  -> JSBSim FDM step
  -> ArduPlane or controller adapter
  -> telemetry / state / command logs
  -> ROS2 mission and evidence bus
  -> UE renderer consumes aircraft state and control-surface events
```

For VTOL, the architecture must declare whether the whole vehicle truth is
JSBSim, Gazebo, or a coordinated hybrid model. Do not let Gazebo and JSBSim
integrate the same vehicle state at the same time.

## 5. Strengths

- Designed for aerospace dynamics rather than generic robotics.
- XML/data-driven aircraft model representation.
- Property tree and configurable output make integration and logging tractable.
- ArduPilot has a documented SITL-with-JSBSim path.
- Better fixed-wing starting point than Gazebo LiftDrag-only modeling for
  serious aerodynamic behavior.

## 6. Gaps And Risks

- High-fidelity aircraft models require aerodynamic coefficient data; visual
  meshes are not enough.
- Fixed-wing claims need envelope and model-fidelity labels.
- UE animation of control surfaces is visual only unless backed by JSBSim
  state/control outputs.
- Benign model-aircraft simulation must stay separated from weaponization,
  targeting, destructive payload, and deployment guidance.

## 7. CoSim Adoption Decision

Decision: default backend route for fixed-wing and candidate route for VTOL
cruise/transition and ducted model-aircraft research.

## 8. Required Next Evidence

- Fixed-wing vehicle-profile template: mass, inertia, aero coefficients,
  propulsion, control surfaces, actuator limits, and source provenance.
- JSBSim batch smoke for one open model with logged state/control outputs.
- ArduPlane SITL smoke for a benign model-aircraft route.
- UE state mirror for aircraft pose and control-surface animation.
- Clear model-fidelity levels: animation, control-law research, flight-envelope
  research, and identified digital twin.

