# 008 Yaw Sign And Motor Order Audit

Request: `RFLY-MOSIM-MWORKS-YAW-SIGN-MOTOR-ORDER-AUDIT-20260606-008`

Status: completed as a wrapper-level convention audit with explicit boundaries.

## Department-Local Plan

- `department_local_goal`: Validate the current `QuadrotorExperiments` yaw sign and motor order convention against local PX4 and Sunray source evidence, or precisely block it before any fault-isolation/allocation claim.
- `critical_path_steps`: read packet and parent evidence; audit local PX4/Sunray/YunZong source availability; build a source-to-wrapper convention matrix; run the smallest MWORKS check/smoke gate available; write evidence and return packet.
- `parallelizable_slices`: source convention audit; parent MWORKS evidence audit; MCP gate review. Completed locally without disposable sub-agents.
- `subagents_used`: none.
- `verification_gates`: local source matrix, MWORKS MCP health, `check_model` before smoke, official baseline untouched, claim-boundary denial.
- `manual_review_or_blocker_triggers`: require manual/PMO review before using this convention for fault isolation or allocation reconstruction; require a separate task if a PX4 actuator-control-to-MWORKS command bridge is implemented.

## Source Availability

Local PX4 source exists under `References/PX4/PX4`.

Local Sunray source exists under `References/Sunray`.

`References/YunZong` is absent in this checkout, so YunZong could not be used as a local source for this task.

RflySim was not used for acceptance. It remains only a structure reference and is not Sunray150 truth.

## Key Source Findings

Sunray150 SDF motor plugins define:

- `front_right_motor_model`: `rotor_0_joint`, `turningDirection=ccw`, `motorNumber=0`.
- `back_left_motor_model`: `rotor_1_joint`, `turningDirection=ccw`, `motorNumber=1`.
- `front_left_motor_model`: `rotor_2_joint`, `turningDirection=cw`, `motorNumber=2`.
- `back_right_motor_model`: `rotor_3_joint`, `turningDirection=cw`, `motorNumber=3`.

PX4 `4001_quad_x` defines Square quadrotor X numbering:

- rotor0: `PX=1`, `PY=1`, default positive `KM`.
- rotor1: `PX=-1`, `PY=-1`, default positive `KM`.
- rotor2: `PX=1`, `PY=-1`, `KM=-0.05`.
- rotor3: `PX=-1`, `PY=1`, `KM=-0.05`.

PX4 `module.yaml` labels `CA_ROTOR${i}_KM` as `Direction CCW` and displays it as true when positive. This aligns PX4 positive `KM` with CCW direction in the metadata.

## Wrapper Mapping

Current `QuadrotorExperiments.Sunray150RflyStyleRotorDynamics` uses MWORKS wrapper order:

1. front-right
2. front-left
3. back-left
4. back-right

This is a reorder of the PX4/Sunray motor-number order:

```text
PX4/Sunray 0 -> MWORKS 1
PX4/Sunray 2 -> MWORKS 2
PX4/Sunray 1 -> MWORKS 3
PX4/Sunray 3 -> MWORKS 4
```

Under that selected mapping:

```text
Sunray/PX4 direction order: ccw, cw, ccw, cw
MWORKS yaw_direction:       +1,  -1, +1,  -1
MWORKS spin_command_sign:   +1,  -1, +1,  -1
```

The current wrapper convention is therefore consistent with the selected reordered PX4/Sunray convention. It is not the raw PX4 motor index order.

## MWORKS MCP Gate

Source: `MWORKS_MCP`.

- `session_manager(action=health)`: passed, driver ready, dedicated Sysplorer port `49152`; no auth/license/demo/activation incident appeared.
- `model_manager(load_file)`: loaded `Models/QuadrotorExperiments/package.mo`.
- `check_model`: passed for `QuadrotorExperiments.Sunray150PhysicalWrenchYawStepSmoke` before simulation.
- `simulate_model`: returned `data=false` with no last-error log, but the tool's internal `verify_result_var=torque_application_error` probe confirmed a readable result and `torque_application_error@end = 0.0`.
- Follow-up `result_manager` reads could not recover explicit gate-variable values in this turn, so this task does not strengthen the parent 006/007 result-variable claims.

Parent 006/007 evidence remains the stronger archived MWORKS result evidence for current wrapper gates and physical wrench application. 008 adds the local source convention audit needed before a later allocation task.

## Acceptance And Boundaries

Accepted:

- Current MWORKS wrapper order and signs are acceptable as a documented wrapper-level convention when mapped from PX4/Sunray order `0,2,1,3`.
- `References/YunZong` is missing and not used.
- Official baseline `References/MWORKS/QuadrotorModel/package.mo` was not edited.

Not accepted or not claimed:

- parameter identification
- fault-isolation readiness
- allocation reconstruction readiness
- controller performance
- planner readiness
- live runtime ack
- Factory trace consumption
- closed loop

Next recommended gate: create a separate allocation-preflight task that uses this mapping explicitly and tests actuator-failure/mixer semantics without changing controller gains or consuming Factory traces.
