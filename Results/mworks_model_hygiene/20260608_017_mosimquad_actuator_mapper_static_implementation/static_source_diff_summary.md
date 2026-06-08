# Static Source Diff Summary

Task: PMO-MWORKS-R1-MOSIMQUAD-ACTUATOR-MAPPER-STATIC-IMPLEMENTATION-20260608-017

Scope: static Modelica source implementation only. No MWORKS/Sysplorer/Syslab
window, MCP, check_model, SimulateModel, Smart Layout, screenshot, result
viewer, ClearAll, or ChangeDirectory action was performed.

## Changed Project-Owned Files

| File | Change |
|---|---|
| `Models/QuadrotorExperiments/DynamicsUpgrade/Sunray150ActuatorCommandMapper.mo` | Added a separate normalized actuator/throttle command to signed visual rotor speed mapper. |
| `Models/QuadrotorExperiments/DynamicsUpgrade/Sunray150ActuatorMappedWrapperSurface.mo` | Added a wrapper surface that feeds mapper output into the existing `Sunray150DynamicsWrapperSurface`. |
| `Models/QuadrotorExperiments/DynamicsUpgrade/package.mo` | Added compatibility alias entries `ActuatorCommandMapper` and `ActuatorMappedWrapperSurface`. |
| `Models/QuadrotorExperiments/DynamicsUpgrade/package.order` | Added package-order entries for the two new compatibility aliases. |
| `Models/MoSimQuadrotorModel/Dynamics/package.mo` | Added formal alias entries under `MoSimQuadrotorModel.Dynamics`. |
| `Models/MoSimQuadrotorModel/Dynamics/package.order` | Added formal package-order entries for the two new dynamics surfaces. |

## Boundary Added

The new mapper separates command domains:

```text
normalized_actuator_command[4]
  -> saturated_normalized_command[4]
  -> visual_rotor_speed_unsigned[4]
  -> signed_visual_rotor_speed_command[4]
  -> existing wrapper.motor_command
  -> existing Sunray150RflyStyleRotorDynamics chain
```

The existing chain was not edited:

```text
signed visual rotor speed command
  -> first-order lagged omega
  -> Ct * omega^2 thrust
  -> yaw reaction moment
  -> rotor-center r x F moment
```

## Source Labels

The normalized-command map bounds are source-labeled interface seeds. The
default hover command `0.5` and derived `max_visual_rotor_speed` are not
identified Sunray150 PWM, throttle, ESC RPM, or physical rotor-speed truth.

Mass, lift coefficient, motor lag, yaw moment ratio, rotor geometry, and spin
sign conventions remain the existing source-labeled seeds from the prior
dynamics upgrade. No RflySim numeric value was copied into Sunray150 truth.

## Out Of Scope

No rotor gyro, body drag, angular damping, contact, fault allocation, dynamic
parameter layer, controller runtime, ROS2, UE, FAST-LIO, planner, official
baseline, or live MWORKS evidence was added.
