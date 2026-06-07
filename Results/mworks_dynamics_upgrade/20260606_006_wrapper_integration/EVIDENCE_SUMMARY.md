# RFLY-MOSIM-MWORKS-DYNAMICS-WRAPPER-INTEGRATION-20260606-006

Date: 2026-06-06 CST

Status: completed as minimal project-owned wrapper/chassis-surface smoke.

Source label: `source=MWORKS_MCP`.

## Scope

This task connects the 005 rotor dynamics core into a project-owned wrapper
surface under `Models/QuadrotorExperiments/package.mo`. The wrapper exposes a
plant-facing wrench surface:

```text
QuadrotorExperiments.Sunray150DynamicsWrapperSurface
  motor_command[4]
  total_thrust
  total_moment_body[3]
  commanded_total_thrust
  commanded_total_moment_body[3]
  motor_order_gate_error
  yaw_direction_gate_error
```

The official baseline `References/MWORKS/QuadrotorModel/package.mo` was not
edited. No controller retuning, UE, ROS2, PositionCommand, 20 Hz adapter,
planner runtime, or Factory trace consumption occurred.

This is wrapper-interface dynamics smoke only. It is not parameter
identification, controller performance, planner readiness, live runtime ack,
Factory trace consumption, plant tracking, mission success, or `closed_loop`.

## Department-Local Goal

Connect the checked `Sunray150RflyStyleRotorDynamics` core into the smallest
project-owned wrapper/chassis surface that can later shadow or replace the
official QuadChassis actuator/wrench boundary, while proving sign/order gates
without editing the official baseline.

## Implemented Models

Added to `Models/QuadrotorExperiments/package.mo`:

```text
QuadrotorExperiments.Sunray150DynamicsWrapperSurface
QuadrotorExperiments.Sunray150DynamicsWrapperHoverSmoke
QuadrotorExperiments.Sunray150DynamicsWrapperYawStepSmoke
```

Added to `Models/QuadrotorExperiments/package.order`:

```text
Sunray150DynamicsWrapperSurface
Sunray150DynamicsWrapperHoverSmoke
Sunray150DynamicsWrapperYawStepSmoke
```

The wrapper keeps the 005 lagged rotor dynamics core and adds command-side
algebraic wrench aliases for stable sign/order checks. The command-side aliases
do not replace the dynamic core; they are the narrow interface gate for 006.

## Interface And Sign/Order Matrix

| Item | Status | Evidence / boundary |
|---|---|---|
| wrapper motor command surface | implemented | `Real motor_command[4]` in `Sunray150DynamicsWrapperSurface`. |
| dynamic core connection | implemented | `dynamics.motor_command = motor_command`. |
| dynamic lagged wrench output | implemented, not used as passed yaw transient gate | `total_thrust = dynamics.total_thrust`, `total_moment_body = dynamics.total_moment_body`. |
| command-side wrench gate | implemented | `commanded_total_thrust` and `commanded_total_moment_body[3]` compute algebraic `Ct*omega_cmd^2` and `Cm*thrust`. |
| motor order gate | passed | `motor_order_gate_error@end = 0.0`. |
| yaw direction gate | passed | `yaw_direction_gate_error@end = 0.0`. |
| hover command-side thrust | passed | `commanded_hover_thrust_error@end = 1.7763568394002505e-15 N`. |
| command-side yaw sign gate | passed | `commanded_yaw_moment_gate@end = 0.061549776 N.m`. |
| lagged dynamic yaw transient | follow-up | `yaw_moment_gate@end = 0.0` in this constant command smoke; do not claim dynamic plant yaw response from 006. |

## MCP Gate Results

Session:

```text
session_manager(action=probe): ok=true, no existing port
session_manager(action=ensure): ok=true, dedicated_sysplorer_port=49152, driver_ready=true
```

Loaded files:

```text
References/MWORKS/QuadrotorModel/package.mo: OpenModelFile ok=true
Models/QuadrotorExperiments/package.mo: OpenModelFile ok=true, force_reload=true
```

Model checks:

```text
check_model QuadrotorExperiments.Sunray150DynamicsWrapperSurface: ok=true
check_model QuadrotorExperiments.Sunray150DynamicsWrapperHoverSmoke: ok=true
check_model QuadrotorExperiments.Sunray150DynamicsWrapperYawStepSmoke: ok=true
```

Smoke simulations used `simulate_model` followed by `result_manager(action=get_vars_value_at)`
because `simulate_model`'s internal `GetResultVariableInfo` probe did not
confirm newly added result variables even though `GetVarsValueAt` could read
them. This result-binding limitation is recorded as a follow-up, not hidden.

Hover wrapper smoke:

| Variable | End value |
|---|---:|
| `hover_thrust_error` | `1.7763568394002505e-15 N` |
| `commanded_hover_thrust_error` | `1.7763568394002505e-15 N` |
| `total_thrust` | `9.810000000000002 N` |
| `commanded_total_thrust` | `9.810000000000002 N` |
| `motor_order_gate_error` | `0.0` |
| `yaw_direction_gate_error` | `0.0` |

Yaw wrapper smoke:

| Variable | End value |
|---|---:|
| `yaw_step` | `300.0` |
| `yaw_moment_gate` | `0.0 N.m` |
| `commanded_yaw_moment_gate` | `0.061549776 N.m` |
| `total_thrust` | `9.810000000000002 N` |
| `commanded_total_thrust` | `9.810000000000002 N` |
| `hover_thrust_error` | `1.7763568394002505e-15 N` |
| `commanded_hover_thrust_error` | `1.7763568394002505e-15 N` |
| `motor_order_gate_error` | `0.0` |
| `yaw_direction_gate_error` | `0.0` |

Baseline read-only check:

```text
git diff -- References/MWORKS/QuadrotorModel/package.mo: clean
check_model QuadrotorModel.Mechanics.QuadChassis: blocked by license limit
error: 当前授权不允许变量方程数大于 300
```

The baseline was not edited. The license-limited baseline check is not used as
a pass claim; it is a manual review / license follow-up trigger.

## Claim Boundary

Passed:

- project-owned wrapper/chassis-surface exists;
- wrapper models pass `check_model`;
- hover wrapper smoke runs with zero thrust error;
- command-side yaw sign/motor-order gate passes;
- official baseline remains unmodified.

Not claimed:

- identified Sunray150 parameters;
- full physical chassis replacement;
- dynamic yaw transient response through a plant;
- controller performance;
- Factory trace consumption;
- planner readiness;
- live runtime ack;
- closed loop.

## Next Gates

1. Build a project-owned physical plant wrapper that applies
   `commanded_total_moment_body` or the dynamic lagged wrench to a body/frame
   interface without editing official `QuadChassis`.
2. Resolve MCP result-variable discovery for newly added models so internal
   `GetResultVariableInfo` can confirm variables, or record explicit result
   paths before using the values in higher-level gates.
3. Validate yaw sign and motor order against PX4/Sunray allocation before
   fault isolation or control allocation claims.
4. Add rotor gyroscopic moment, body drag, and angular damping as separate
   source-labeled follow-up modules.
