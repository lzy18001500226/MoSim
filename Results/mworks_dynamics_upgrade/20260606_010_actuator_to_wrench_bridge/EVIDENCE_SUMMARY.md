# RFLY-MOSIM-MWORKS-ACTUATOR-TO-WRENCH-BRIDGE-20260606-010

Date: 2026-06-06 CST

Status: blocked before actuator-to-wrench bridge implementation.

Source label: `source=MWORKS_MCP` for the minimal Sysplorer health/load/check
gate, plus `source=live_window_inventory` for GUI sentinels.

## Scope

Task 010 attempted to bridge the passing Iso27 actuator-input/preflight command
surface into the project-owned Sunray150 Rfly-style physical-wrench wrapper.

The bridge was not implemented because the current disk-reloaded
`Models/QuadrotorExperiments/package.mo` no longer contains the parent 006/007
wrapper/physical adapter classes listed in `package.order` and referenced by
prior evidence. After a forced load from disk, Sysplorer could still check the
005 rotor dynamics core but reported that
`QuadrotorExperiments.Sunray150PhysicalWrenchFrameAdapter` does not exist.

## Department-Local Goal

Recover the exact command-domain and connector boundary between Iso27 actuator
input aliases and the project-owned physical wrench wrapper, then either run
the smallest bridge smoke or stop at the first reproducibility/blocker gate.

## Critical Path Result

1. Read task packet, AGENTS/new context, task ledger, parameter workflow, and
   parent 005/006/007/008/021 return/evidence.
2. Inspected Iso27 actuator input aliases. Iso27 proves
   `actuator1_*.u == pre_actuator_command_*`, and sampled values use the
   project visual rotor speed command domain.
3. Inspected current model files. `FactoryTraceIso27ActuatorInputAliasSmoke.mo`
   exists as a separate project-owned model. `package.order` lists
   `Sunray150DynamicsWrapperSurface` and
   `Sunray150PhysicalWrenchFrameAdapter`, but current
   `Models/QuadrotorExperiments/package.mo` contains only the 005
   `Sunray150RflyStyleRotorDynamics` family at the tail and does not define
   the 006/007 wrapper/physical adapter classes.
4. Ran P0 GUI sentinel before MCP: clean.
5. Ran Sysplorer MCP `session_manager(action=health)`: pass on dedicated port
   49154.
6. Forced `model_manager(action=load_file)` from current disk package to avoid
   relying on stale in-memory classes.
7. Ran `check_model` for the 005 core and 007 physical adapter. The 005 core
   passed; the 007 adapter failed because the model does not exist after disk
   reload.
8. Ran P0 GUI sentinel after MCP: clean.

## MCP Gate

```text
session_manager(action=health): ok=true, driver_ready=true, api_ready=true,
dedicated_sysplorer_port=49154

model_manager(action=load_file,
  file_path=C:/Users/HP/Desktop/MoSim/Models/QuadrotorExperiments/package.mo,
  force_reload=true,
  auto_load_deps=false): ok=true

check_model QuadrotorExperiments.Sunray150RflyStyleRotorDynamics: ok=true
check_model QuadrotorExperiments.Sunray150PhysicalWrenchFrameAdapter: failed
  GetLastErrors: 模型“QuadrotorExperiments.Sunray150PhysicalWrenchFrameAdapter”不存在。
```

No simulation was run.

## Blocker

`model_definition_missing_after_disk_reload`: the required parent physical
wrench wrapper from 007 is not reproducible from current project-owned source.
Task 010 is not allowed to silently recreate/repair the parent 006/007 wrapper
and then bridge Iso27 in the same step, because that would exceed the bounded
single bridge objective and could mask source/evidence drift.

## Claim Boundary

Not claimed:

- actuator-to-wrench bridge implementation;
- check_model pass for a bridge model;
- smoke simulation;
- Factory trace consumption;
- controller performance;
- plant tracking;
- dynamic yaw transient acceptance;
- planner readiness;
- live runtime ack;
- closed loop;
- parameter identification.

## Next Safe PMO Action

Open a bounded recovery task to reconcile current
`Models/QuadrotorExperiments/package.mo` with the recorded 006/007 wrapper
evidence, restoring or intentionally superseding
`Sunray150DynamicsWrapperSurface` and
`Sunray150PhysicalWrenchFrameAdapter` under project-owned source. That recovery
task should run P0 sentinel before/after, force-load from disk, and check the
restored wrapper/adapter before re-dispatching the 010 actuator-to-wrench
bridge.
