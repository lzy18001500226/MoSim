# RotorActuatorCore Formal Source Surface

Request: `PMO-MWORKS-R1-MOSIMQUAD-ROTOR-ACTUATOR-CORE-FORMAL-SOURCE-SURFACE-20260608-025`

Status: `passed_static`

## Source Surface

- Formal target: `MoSimQuadrotorModel.Dynamics.RotorActuatorCore`
- Formal source: `Models/MoSimQuadrotorModel/Dynamics/RotorActuatorCore.mo`
- Legacy alias preserved: `QuadrotorExperiments.DynamicsUpgrade.RotorDynamicsCore`
- Legacy implementation preserved: `Models/QuadrotorExperiments/DynamicsUpgrade/Sunray150RflyStyleRotorDynamics.mo`

The formal source is intentionally an extends-only project-owned surface. It does not duplicate motor lag, thrust, yaw reaction, rotor-arm moment, or hover-error equations.

## Static Anchors

- Motor lag: `der(omega[i]) = (motor_command[i] - omega[i]) / motor_tau[i]`
- Thrust: `thrust[i] = lift_coefficient * omega[i] * omega[i]`
- Yaw reaction torque: `yaw_reaction_moment[i] = yaw_direction[i] * moment_constant * thrust[i]`
- Rotor-center r x F moment: x/y terms remain in `Sunray150RflyStyleRotorDynamics.mo`.
- Rotor centers remain matched with `MoSimQuadrotorModel.Parameters.Sunray150ParameterProvenance`.

## Claim Boundary

- Static source/package surface only.
- No live MWORKS load, `check_model`, `SimulateModel`, result variable, or graphical acceptance is claimed.
- No dynamics equation, numerical parameter, solver, controller, ROS2, UE, Sunray/PBR, Blender, References, official QuadrotorModel, or CoAgent runtime file was changed.
