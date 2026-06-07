# RFLY-MOSIM-MWORKS-WRENCH-TO-EXTERNAL-FRAME-BOUNDARY-20260606-015

Date: 2026-06-06 CST

Status: completed as a minimal external MultiBody frame/test-body boundary smoke.

Source label: `source=MWORKS_MCP`.

## Scope

This task continues from 014 and adds only:

```text
QuadrotorExperiments.FactoryTraceIso29ExternalFrameWrenchBoundarySmoke
```

The model extends `FactoryTraceIso28ActuatorToWrenchBridgeSmoke`, then creates
one explicit external `Modelica.Mechanics.MultiBody.Parts.Body` and one
external `WorldForceAndTorque` component. It feeds the wrapper force/torque
from the 014 sidecar chain into this external test body and exposes read-only
boundary aliases.

No official baseline model was edited. No QuadChassis, Factory wrapper, actuator
flange, speedSensor, full plant, controller trace consumption, UE, ROS2, or
planner runtime was used.

## MCP Gate

P0 GUI sentinel:

```text
pre_sentinel.json: status=clean
post_sentinel.json: status=clean
```

Sysplorer MCP:

```text
session_manager(action=health): ok=true, driver_ready=true, api_ready=true, dedicated_sysplorer_port=49153
model_manager(load_file, force_reload=true):
  References/MWORKS/QuadrotorModel/package.mo: ok=true
  Models/QuadrotorControllerBlocks/AWFF_LinearMPCOuterLoopControllerEquation_Sysblock.mo: ok=true
  Models/QuadrotorExperiments/package.mo: ok=true
```

Check and smoke:

```text
check_model QuadrotorExperiments.FactoryTraceIso28ActuatorToWrenchBridgeSmoke: ok=true
check_model QuadrotorExperiments.FactoryTraceIso29ExternalFrameWrenchBoundarySmoke: ok=true
simulate 0.0..0.25 s: ok=true, data=true
GetVarTimes: count=251, first=0.0, last=0.25
external_boundary_gate_error@end = 0.0
```

## Result Samples

Compact sample table:

```text
Results/mworks_dynamics_upgrade/20260606_015_wrench_to_external_frame_boundary/external_frame_samples.csv
```

End sample:

```text
bridge_total_thrust = 12.771836020169136 N
bridge_yaw_moment = -0.06826526566283278 N.m
external_applied_force_z_body = 12.771836020169136 N
external_applied_yaw_torque_body = -0.06826526566283278 N.m
external_frame_force_z = 12.771836020169136 N
external_frame_yaw_torque = -0.06826526566283278 N.m
external_force_application_error = 0.0 N
external_torque_application_error = 0.0 N.m
external_force_matches_adapter_error = 0.0 N
external_torque_matches_adapter_error = 0.0 N.m
external_boundary_gate_error = 0.0
```

## Claim Boundary

Passed:

- the 014 wrapper force/torque can be applied to an explicit external
  MultiBody frame/test body in a minimal project-owned smoke;
- the external test body's frame force/torque aliases match the applied
  wrapper force/torque in sampled result reads;
- `check_model` passed before simulation and selected result aliases were
  readable after simulation.

Not claimed:

- Factory trace consumption;
- full Factory wrapper retry;
- QuadChassis, actuator flange, speedSensor, full plant, or full control path;
- controller performance;
- full plant tracking;
- dynamic yaw transient acceptance;
- parameter identification;
- allocation or fault-isolation readiness;
- planner readiness;
- live UE/ROS2 ack;
- mission success;
- closed_loop.
