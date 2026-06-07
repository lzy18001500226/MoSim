# RFLY-MOSIM-MWORKS-PHYSICAL-WRENCH-WRAPPER-20260606-007

Date: 2026-06-06 CST

Status: completed as minimal project-owned physical wrench wrapper smoke.

Source label: `source=MWORKS_MCP`.

## Scope

This task continues the 006 wrapper surface and adds the smallest project-owned
physical body/frame binding surface under `Models/QuadrotorExperiments`.

Implemented models:

```text
QuadrotorExperiments.Sunray150PhysicalWrenchFrameAdapter
QuadrotorExperiments.Sunray150PhysicalWrenchHoverSmoke
QuadrotorExperiments.Sunray150PhysicalWrenchYawStepSmoke
```

The adapter consumes `Sunray150DynamicsWrapperSurface` motor commands and
applies the resulting dynamic wrapper wrench to a MultiBody `Frame_b` through
`Modelica.Mechanics.MultiBody.Forces.WorldForceAndTorque` with
`resolveInFrame=frame_b`.

This is not a controller retune, Factory trace consumer, ROS2/UE runtime
integration, parameter identification, controller performance claim, dynamic
yaw transient acceptance, planner readiness, live runtime ack, or closed loop.

## MCP Gate Results

Session:

```text
session_manager(action=health): ok=true, driver_ready=true, dedicated_sysplorer_port=49152
```

Project package load:

```text
model_manager(action=load_file, force_reload=true, auto_load_deps=false):
ok=true, OpenModelFile data=true
```

Model checks:

```text
check_model QuadrotorExperiments.Sunray150PhysicalWrenchFrameAdapter: ok=true
check_model QuadrotorExperiments.Sunray150PhysicalWrenchHoverSmoke: ok=true
check_model QuadrotorExperiments.Sunray150PhysicalWrenchYawStepSmoke: ok=true
```

No auth/license/login incident appeared during 007 MCP gates.

## Smoke Evidence

Hover smoke:

```text
simulate_model QuadrotorExperiments.Sunray150PhysicalWrenchHoverSmoke:
ok=true, data=true, force_application_error@end=0.0
```

End-time values:

| Variable | Value |
|---|---:|
| `applied_force_z_body` | `9.810000000000002 N` |
| `applied_yaw_torque_body` | `0.0 N.m` |
| `force_application_error` | `0.0 N` |
| `torque_application_error` | `0.0 N.m` |
| `hover_weight_balance_error` | `1.7763568394002505e-15 N` |
| `wrapper_total_thrust` | `9.810000000000002 N` |
| `wrapper_yaw_moment` | `0.0 N.m` |
| `motor_order_gate_error` | `0.0` |
| `yaw_direction_gate_error` | `0.0` |
| `body.frame_a.f[3]` | `9.810000000000002 N` |
| `body.frame_a.t[3]` | `0.0 N.m` |

Yaw smoke:

```text
simulate_model QuadrotorExperiments.Sunray150PhysicalWrenchYawStepSmoke:
ok=true, data=true, torque_application_error@end=0.0
```

End-time values:

| Variable | Value |
|---|---:|
| `yaw_step` | `300.0` |
| `applied_force_z_body` | `9.889798234010929 N` |
| `applied_yaw_torque_body` | `0.05418494199832341 N.m` |
| `wrapper_yaw_moment` | `0.05418494199832341 N.m` |
| `commanded_yaw_moment_gate` | `0.061549776 N.m` |
| `force_application_error` | `0.0 N` |
| `torque_application_error` | `0.0 N.m` |
| `motor_order_gate_error` | `0.0` |
| `yaw_direction_gate_error` | `0.0` |
| `body.frame_a.f[3]` | `9.889798234010929 N` |
| `body.frame_a.t[3]` | `0.05418494199832341 N.m` |

## Claim Boundary

Passed:

- project-owned physical wrench frame adapter exists;
- adapter applies wrapper force and torque to a MultiBody frame;
- `check_model` passed before simulation;
- shortest hover/yaw smoke simulations ran through Sysplorer MCP;
- explicit frame port values match applied wrapper force/torque values;
- official baseline remained unmodified.

Not claimed:

- identified Sunray150 parameters;
- controller performance;
- dynamic yaw transient acceptance;
- Factory trace consumption;
- ROS2/UE runtime data consumption;
- planner readiness;
- live runtime ack;
- closed loop.

## Result-Binding Note

For 007, `simulate_model` result probes through `GetResultVariableInfo` succeeded
for `force_application_error` and `torque_application_error`. Additional values
were read with `result_manager(action=get_vars_value_at)`.

## Follow-Up Gates

1. Validate yaw sign and motor order against PX4/Sunray allocation before any
   fault-isolation or allocation claim.
2. Resolve full official `QuadChassis` license limit before checking larger
   baseline chassis models in this education session.
3. Add rotor gyroscopic moment, body drag, and angular damping as separate
   source-labeled dynamics tasks.
4. Keep controller retuning and closed-loop validation as separate tasks with
   their own MWORKS/Sysplorer evidence gates.
