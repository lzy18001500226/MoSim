# Actuator Mapper Boundary

Task: PMO-MWORKS-R1-MOSIMQUAD-ACTUATOR-MAPPER-STATIC-IMPLEMENTATION-20260608-017

## Purpose

016 classified the next smallest RflySim-like dynamics gap as the missing
command-domain boundary before the existing rotor dynamics core. 017 implements
that boundary as project-owned static Modelica source without live MWORKS
validation.

## New Static Interfaces

### `Sunray150ActuatorCommandMapper`

Location:
`Models/QuadrotorExperiments/DynamicsUpgrade/Sunray150ActuatorCommandMapper.mo`

Inputs and outputs:

| Surface | Meaning |
|---|---|
| `normalized_command[4]` | External normalized actuator/throttle command surface, expected in `[0, 1]`. |
| `saturated_normalized_command[4]` | Bounded command after min/max gate. |
| `actuator_saturation_error[4]` | Difference between raw and saturated command. |
| `visual_rotor_speed_unsigned[4]` | Unsigned MWORKS visual rotor speed target. |
| `signed_visual_rotor_speed_command[4]` | Signed visual rotor speed command for the existing rotor core. |
| `hover_command_error[4]` | Command-side hover reference diagnostic. |

### `Sunray150ActuatorMappedWrapperSurface`

Location:
`Models/QuadrotorExperiments/DynamicsUpgrade/Sunray150ActuatorMappedWrapperSurface.mo`

This wrapper feeds:

```text
actuator_mapper.signed_visual_rotor_speed_command
  -> wrapper.motor_command
```

and re-exposes the existing wrapper observations:

```text
total_thrust
total_moment_body
commanded_total_thrust
commanded_total_moment_body
hover_thrust_error
commanded_hover_thrust_error
yaw_moment_gate
commanded_yaw_moment_gate
motor_order_gate_error
yaw_direction_gate_error
```

## Formal Package Exposure

Compatibility aliases:

```text
QuadrotorExperiments.DynamicsUpgrade.ActuatorCommandMapper
QuadrotorExperiments.DynamicsUpgrade.ActuatorMappedWrapperSurface
```

Formal aliases:

```text
MoSimQuadrotorModel.Dynamics.ActuatorCommandMapper
MoSimQuadrotorModel.Dynamics.ActuatorMappedWrapperSurface
```

## Claim Boundary

This boundary is a static source implementation only. It does not prove
`check_model`, simulation, graphical layout, controller performance, actuator
trace consumption, plant tracking, parameter identification, planner readiness,
runtime acknowledgement, mission success, or closed loop.
