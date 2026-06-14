# WrapperSurface Formal Source Surface

Request: `PMO-MWORKS-R1-MOSIMQUAD-WRAPPER-SURFACE-FORMAL-SOURCE-SURFACE-20260608-026`

Status: `passed_static`

## Source Surface

- Formal target: `MoSimQuadrotorModel.Dynamics.WrapperSurface`
- Formal source: `Models/MoSimQuadrotorModel/Dynamics/WrapperSurface.mo`
- Legacy alias preserved: `QuadrotorExperiments.DynamicsUpgrade.WrapperSurface`
- Legacy implementation preserved: `Models/QuadrotorExperiments/DynamicsUpgrade/Sunray150DynamicsWrapperSurface.mo`

The formal source is intentionally an extends-only project-owned surface. It does not duplicate wrapper equations, motor-command mapping, command-side thrust, yaw reaction, rotor-arm moment, or lagged total force/moment outputs.

## Static Anchors

- Wrapper command input: `dynamics.motor_command = motor_command`.
- Command-side thrust: `commanded_thrust[i] = dynamics.thrust_effectiveness[i] * dynamics.lift_coefficient * motor_command[i] * motor_command[i]`.
- Command-side yaw reaction: `commanded_yaw_reaction_moment[i] = dynamics.yaw_direction[i] * dynamics.reaction_moment_effectiveness[i] * dynamics.moment_constant * commanded_thrust[i]`.
- Effectiveness monitors: `minimum_thrust_effectiveness` and `minimum_reaction_moment_effectiveness` remain surfaced through the wrapper.
- Rotor-center r x F moment: command-side x/y/z terms remain in `Sunray150DynamicsWrapperSurface.mo`.
- Lagged outputs: `total_thrust`, `total_moment_body`, `hover_thrust_error`, and yaw gates remain in the legacy wrapper implementation.
- Rotor centers remain matched across wrapper, core implementation, and `MoSimQuadrotorModel.Parameters.Sunray150ParameterProvenance`.

## Claim Boundary

- Static source/package surface only.
- No live MWORKS load, `check_model`, `SimulateModel`, result variable, or graphical acceptance is claimed.
- No dynamics equation, numerical parameter, solver, controller, ROS2, UE, Sunray/PBR, Blender, References, official QuadrotorModel, or CoAgent runtime file was changed.
