# ActuatorCommandMapper Formal Source Surface

Request: `PMO-MWORKS-R1-MOSIMQUAD-ACTUATOR-COMMAND-MAPPER-FORMAL-SOURCE-SURFACE-20260608-027`

Status: `passed_static`

## Source Surface

- Formal target: `MoSimQuadrotorModel.Dynamics.ActuatorCommandMapper`
- Formal source: `Models/MoSimQuadrotorModel/Dynamics/ActuatorCommandMapper.mo`
- Legacy alias preserved: `QuadrotorExperiments.DynamicsUpgrade.ActuatorCommandMapper`
- Legacy implementation preserved: `Models/QuadrotorExperiments/DynamicsUpgrade/Sunray150ActuatorCommandMapper.mo`

The formal source is intentionally an extends-only project-owned surface. It does not duplicate normalized command bounds, saturation, hover placeholder, visual-speed scaling, spin sign, or signed visual rotor speed equations.

## Static Anchors

- Normalized command bounds: `normalized_command_min = 0.0` and `normalized_command_max = 1.0`.
- Hover placeholder: `hover_normalized_command = 0.5`, source-labeled as an interface seed.
- Visual speed mapping: `hover_visual_rotor_speed`, `max_visual_rotor_speed`, and `visual_rotor_speed_unsigned` remain in the legacy implementation.
- Spin sign: `spin_command_sign[4] = {1, -1, 1, -1}` remains source-labeled as an existing MWORKS visual convention, not PX4 allocation proof.
- Saturation observability: `saturated_normalized_command` and `actuator_saturation_error` remain exposed.
- Wrapper feed output: `signed_visual_rotor_speed_command` remains the output for `Sunray150RflyStyleRotorDynamics.motor_command` consumers.

## Claim Boundary

- Static source/package surface only.
- No live MWORKS load, `check_model`, `SimulateModel`, result variable, or graphical acceptance is claimed.
- No command mapping equation, numerical parameter, spin sign, solver, controller, ROS2, UE, Sunray/PBR, Blender, References, official QuadrotorModel, or CoAgent runtime file was changed.
