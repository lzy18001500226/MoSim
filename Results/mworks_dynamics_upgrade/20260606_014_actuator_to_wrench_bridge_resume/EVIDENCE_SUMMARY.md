# RFLY-MOSIM-MWORKS-ACTUATOR-TO-WRENCH-BRIDGE-RESUME-20260606-014

Date: 2026-06-06 CST

Status: completed as a minimal actuator-input alias to physical-wrench wrapper smoke.

Source label: `source=MWORKS_MCP`.

## Scope

This task resumed the actuator-to-wrench bridge after package cleanup task 013
lifted the `Models/QuadrotorExperiments` write lock. It adds only:

```text
QuadrotorExperiments.FactoryTraceIso28ActuatorToWrenchBridgeSmoke
```

The model extends the passing Iso27 actuator-input alias surface and instantiates
one independent `Sunray150PhysicalWrenchFrameAdapter`. It assigns
`actuator_input_1..4` to the adapter's signed visual rotor-speed command
surface and exposes read-only bridge/wrench consistency aliases.

No official baseline model was edited.

## MCP Gate

P0 GUI sentinel:

```text
pre_sentinel.json: status=clean
pre_bridge_check_sentinel.json: status=clean
post_sentinel.json: status=clean
```

Sysplorer MCP:

```text
session_manager(action=health): ok=true, driver_ready=true, api_ready=true, dedicated_sysplorer_port=49154
model_manager(load_file, force_reload=true):
  References/MWORKS/QuadrotorModel/package.mo: ok=true
  Models/QuadrotorControllerBlocks/AWFF_LinearMPCOuterLoopControllerEquation_Sysblock.mo: ok=true
  Models/QuadrotorExperiments/package.mo: ok=true
```

Parent checks before the bridge smoke:

```text
QuadrotorExperiments.FactoryTraceIso27ActuatorInputAliasSmoke: ok=true
QuadrotorExperiments.Sunray150PhysicalWrenchFrameAdapter: ok=true
QuadrotorExperiments.Sunray150PhysicalWrenchHoverSmoke: ok=true
QuadrotorExperiments.Sunray150DynamicsWrapperSurface: ok=true
```

Bridge check and smoke:

```text
check_model QuadrotorExperiments.FactoryTraceIso28ActuatorToWrenchBridgeSmoke: ok=true
simulate 0.0..0.25 s: ok=true, data=true
GetVarTimes: count=251, first=0.0, last=0.25
bridge_command_error_abs_sum@end = 0.0
```

## Result Samples

The full compact sample table is:

```text
Results/mworks_dynamics_upgrade/20260606_014_actuator_to_wrench_bridge_resume/bridge_samples.csv
```

End sample:

```text
actuator_input = [42.59016682167076, -111.19256307819137, 42.59016682167076, -40.792186841443275]
bridge_command = [42.59016682167076, -111.19256307819137, 42.59016682167076, -40.792186841443275]
bridge_command_error_abs_sum = 0.0
bridge_total_thrust = 12.770141435152444 N
bridge_yaw_moment = -0.0707076455900288 N.m
bridge_applied_force_z_body = 12.770141435152444 N
bridge_applied_yaw_torque_body = -0.0707076455900288 N.m
bridge_force_application_error = 0.0 N
bridge_torque_application_error = 0.0 N.m
bridge_motor_order_gate_error = 0.0
bridge_yaw_direction_gate_error = 0.0
```

## Claim Boundary

Passed:

- Iso27 actuator-input aliases can drive the project-owned physical-wrench
  adapter command surface in a minimal bridge smoke.
- The bridge preserves exact command equality into the wrapper.
- The adapter exposes matching wrapper thrust/yaw moment and applied
  force/torque aliases with zero application error in the sampled smoke.
- The parent physical adapter and new bridge both pass `check_model` before
  simulation.

Not claimed:

- Factory trace consumption;
- full Factory wrapper retry;
- actuator flange, chassis, speedSensor, full plant, or full control path;
- controller performance;
- plant tracking;
- dynamic yaw transient acceptance;
- parameter identification;
- allocation or fault-isolation readiness;
- planner readiness;
- live UE/ROS2 ack;
- closed_loop.
