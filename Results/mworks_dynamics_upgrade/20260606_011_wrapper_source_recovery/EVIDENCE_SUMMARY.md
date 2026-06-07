# RFLY-MOSIM-MWORKS-WRAPPER-SOURCE-RECOVERY-20260606-011

Date: 2026-06-06 CST

Status: completed as a source-recovery and `check_model` reproducibility gate.

Source label: `source=PMO_MWORKS_MCP`.

## Scope

This task recovers the missing project-owned 006/007 wrapper definitions that
blocked `RFLY-MOSIM-MWORKS-ACTUATOR-TO-WRENCH-BRIDGE-20260606-010`.

Recovered in `Models/QuadrotorExperiments/package.mo`:

```text
QuadrotorExperiments.Sunray150DynamicsWrapperSurface
QuadrotorExperiments.Sunray150DynamicsWrapperHoverSmoke
QuadrotorExperiments.Sunray150DynamicsWrapperYawStepSmoke
QuadrotorExperiments.Sunray150PhysicalWrenchFrameAdapter
QuadrotorExperiments.Sunray150PhysicalWrenchHoverSmoke
QuadrotorExperiments.Sunray150PhysicalWrenchYawStepSmoke
```

`Models/QuadrotorExperiments/package.order` already listed these models and was
not changed in this task.

The official baseline `References/MWORKS/QuadrotorModel/package.mo` was not
edited.

## MCP Gate

Pre-sentinel:

```text
Results/mworks_dynamics_upgrade/20260606_011_wrapper_source_recovery/pre_sentinel.json
status=clean
```

Sysplorer MCP:

```text
session_manager(action=health): ok=true, driver_ready=true, api_ready=true, dedicated_sysplorer_port=49153
model_manager(load_file, force_reload=true): ok=true
```

`check_model` after force-loading current disk source:

```text
QuadrotorExperiments.Sunray150DynamicsWrapperSurface: ok=true
QuadrotorExperiments.Sunray150DynamicsWrapperHoverSmoke: ok=true
QuadrotorExperiments.Sunray150DynamicsWrapperYawStepSmoke: ok=true
QuadrotorExperiments.Sunray150PhysicalWrenchFrameAdapter: ok=true
QuadrotorExperiments.Sunray150PhysicalWrenchHoverSmoke: ok=true
QuadrotorExperiments.Sunray150PhysicalWrenchYawStepSmoke: ok=true
```

Post-sentinel:

```text
Results/mworks_dynamics_upgrade/20260606_011_wrapper_source_recovery/post_check_model_sentinel.json
status=clean
```

## Smart Layout Incident Avoided

An initial `check_model` attempt with `reload_mo_path` triggered a Sysplorer MCP
Smart Layout writeback that would have added broad annotation churn to existing
models. PMO reverted that worktree diff and reran validation with this safer
sequence:

```text
model_manager(load_file, force_reload=true)
check_model(model_names=[...], no reload_mo_path)
```

The retained source diff is limited to six recovered model definitions.

## Claim Boundary

Passed:

- current disk `package.mo` defines the 006/007 wrapper and physical adapter
  models again;
- all six recovered models pass `check_model`;
- official baseline remains unmodified;
- GUI sentinel was clean before and after the MCP gate.

Not claimed:

- actuator-to-wrench bridge implementation;
- Factory trace consumption;
- controller performance;
- dynamic yaw transient acceptance;
- parameter identification;
- allocation or fault-isolation readiness;
- live UE/ROS2 ack;
- planner readiness;
- closed loop.

## Next Gate

Dispatch a new bounded actuator-to-wrench bridge task that consumes the
recovered `Sunray150PhysicalWrenchFrameAdapter` source from disk and preserves
the 010 command-domain boundary: signed MWORKS visual rotor speed aliases, not
PX4 PWM, normalized actuator command, physical RPM, or identified Sunray150
truth.
