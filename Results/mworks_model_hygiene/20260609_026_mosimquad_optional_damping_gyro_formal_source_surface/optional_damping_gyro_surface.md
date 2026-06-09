# OptionalDampingGyroLayer Formal Source Surface

Request: `PMO-MWORKS-R2-MOSIMQUAD-OPTIONAL-DAMPING-GYRO-FORMAL-SOURCE-SURFACE-20260609-026`

Status: `passed_static`

## Source Surface

- Formal target: `MoSimQuadrotorModel.Dynamics.OptionalDampingGyroLayer`
- Formal source: `Models/MoSimQuadrotorModel/Dynamics/OptionalDampingGyroLayer.mo`
- Legacy alias preserved: `QuadrotorExperiments.DynamicsUpgrade.OptionalDampingGyroLayer`
- Legacy implementation preserved: `Models/QuadrotorExperiments/DynamicsUpgrade/Sunray150OptionalDampingGyroLayer.mo`

The formal source is intentionally an extends-only project-owned surface. It does not duplicate optional rotor gyro, body drag, angular damping, force/moment delta, or mapper-wrapper equations.

## Static Anchors

- Default flags remain false: `enable_rotor_gyro`, `enable_body_drag`, and `enable_angular_damping`.
- Zero seeds remain for `rotor_polar_inertia`, `body_drag_coefficient`, and `angular_damping_coefficient`.
- Gyro sign anchors remain `gyro_axis_sign` and `gyro_convention_sign` in the legacy implementation.
- Observability anchors remain `optional_force_norm`, `optional_moment_norm`, `default_disabled_force_delta`, `default_disabled_moment_delta`, `motor_order_gate_error`, and `yaw_direction_gate_error`.

## Claim Boundary

- Static source/package surface only.
- No live MWORKS load, `check_model`, `SimulateModel`, result variable, or graphical acceptance is claimed.
- No optional gyro/drag/damping equation, numerical parameter, enable flag, sign convention, command mapping, solver, controller, ROS2, UE, Sunray/PBR, Blender, References, official QuadrotorModel, or CoAgent runtime file was changed.
