# Static Source Diff Summary

Task: PMO-MWORKS-R1-MOSIMQUAD-OPTIONAL-DAMPING-GYRO-STATIC-LAYER-20260608-018

Scope: static Modelica source implementation only. No MWORKS/Sysplorer/Syslab
window, MCP, check_model, SimulateModel, Smart Layout, result viewer,
screenshot, solver work, Git stage, commit, or push was performed.

## Source Changes

Added:

- `Models/QuadrotorExperiments/DynamicsUpgrade/Sunray150OptionalDampingGyroLayer.mo`

Modified package surfaces:

- `Models/QuadrotorExperiments/DynamicsUpgrade/package.mo`
- `Models/QuadrotorExperiments/DynamicsUpgrade/package.order`
- `Models/MoSimQuadrotorModel/Dynamics/package.mo`
- `Models/MoSimQuadrotorModel/Dynamics/package.order`

The package files already contained the 017 actuator mapper entries in the
current worktree. Task 018 appended `OptionalDampingGyroLayer` after the mapper
surface and did not revert or rewrite the 017 mapper/core implementation.

## Boundary Implemented

The new model instantiates `Sunray150ActuatorMappedWrapperSurface`, preserving
the existing chain:

```text
normalized actuator command
  -> actuator command mapper
  -> signed visual rotor speed
  -> motor lag
  -> Ct * omega^2 thrust
  -> yaw reaction torque
  -> rotor-center r x F moment
```

It then exposes a separate optional force/moment layer:

```text
body_velocity_body, body_angular_velocity_body
  -> optional body drag force
  -> optional rotor gyroscopic moment
  -> optional angular damping moment
  -> total_force_body, total_moment_body
```

## Default Preservation

All optional effects are disabled by default:

- `enable_rotor_gyro=false`
- `enable_body_drag=false`
- `enable_angular_damping=false`

All new physical coefficients are zero/source-labeled seeds:

- `rotor_polar_inertia[4]={0,0,0,0}`
- `body_drag_coefficient[3]={0,0,0}`
- `angular_damping_coefficient[3]={0,0,0}`

With default settings, `optional_force_body` and `optional_moment_body` are
zero, so `total_force_body=base_force_body` and
`total_moment_body=base_moment_body` statically by construction.

## Not Changed

- `Sunray150RflyStyleRotorDynamics.mo` was not modified.
- `Sunray150DynamicsWrapperSurface.mo` was not modified.
- `Sunray150ActuatorCommandMapper.mo` was not modified by 018.
- `Sunray150ActuatorMappedWrapperSurface.mo` was not modified by 018.
- Official `References/MWORKS/QuadrotorModel` was not modified.
- No mass, inertia, Ct, Cm, lag, drag, damping, gyro, controller, ROS2, UE,
  FAST-LIO, planner, Sunray visual asset, or reference-truth value was promoted.

## Claim Boundary

018 is static source implementation only. It does not prove live MWORKS load,
check_model, SimulateModel, graphical layout, package-browser acceptance,
controller performance, planner_ready, runtime ack, mission success,
identified parameter truth, or closed_loop.
