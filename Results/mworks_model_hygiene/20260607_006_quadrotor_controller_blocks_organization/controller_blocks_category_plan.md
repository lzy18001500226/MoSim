# QuadrotorControllerBlocks Category Plan

This is a read-only planning artifact for `Models/QuadrotorControllerBlocks`. It does not create `package.mo` or `package.order` and does not change any model file.

## Proposed Package Shell

Future package name: `QuadrotorControllerBlocks`.

Recommended top-level category entries:

1. `AWFFPidBlocks`
2. `InnovationControllers`
3. `FaultAllocationControllers`
4. `LinearMPCControllers`
5. `SafetyControllers`
6. `DemosAndSIL`
7. `CompatibilityAndLegacy`

The first write gate should create only a package shell and category aliases. Existing flat class names must remain available until every scenario config, experiment model, and report reference has been migrated and checked.

## Category Membership

### AWFFPidBlocks

- `AWFF_PositionOuterLoop_Sysblock`
- `AWFF_AttitudeInnerLoop_Sysblock`
- `AWFF_MotorMixer_Sysblock`
- `AWFF_FullController_Sysblock`
- `AWFF_FullControllerEquation_Sysblock`
- `AWFF_FullControllerFlatGraphical_Sysblock`

Rationale: baseline AWFF PID decomposition, mixer, combined graphical controller, and equation bridge used by current scenario integration.

### InnovationControllers

- `AWFF_INDIControllerEquation_Sysblock`
- `AWFF_L1ResidualControllerEquation_Sysblock`
- `AWFF_InnovationGraphicalControllers`

Rationale: INDI-like, L1-inspired residual, and graphical innovation overview/entry surface.

### FaultAllocationControllers

- `AWFF_FaultCompensationControllerEquation_Sysblock`
- `AWFF_L1FaultAllocationControllerEquation_Sysblock`
- `AWFF_L1OnlineFaultAllocationControllerEquation_Sysblock`
- `AWFF_L1MultiFaultIsolationControllerEquation_Sysblock`
- `AWFF_LinearMPCOnlineFaultAllocationController_Sysblock`
- `AWFF_LinearMPCMultiFaultAllocationController_Sysblock`

Rationale: known-fault compensation, online efficiency estimation, multi-fault isolation, and LinearMPC plus allocation variants.

### LinearMPCControllers

- `AWFF_LinearMPCOuterLoopControllerEquation_Sysblock`

Rationale: current finite-horizon LinearMPC-style outer-loop equation bridge; this category is intentionally narrow so LinearMPC nominal control remains distinct from fault-allocation wrappers.

### SafetyControllers

- `AWFF_QPNMPCSafetyController_Sysblock`

Rationale: QP/NMPC-style safety wrapper around nominal LinearMPC control and return/landing signals.

### DemosAndSIL

- `AWFF_PID_Sysblock_Demo`
- `AWFF_PID_Sysblock_Demo_SIL_Constant`

Rationale: code generation/SIL/demo models should remain discoverable, but separate from reusable controller library blocks.

### CompatibilityAndLegacy

No main active `.mo` file should be moved here in the first write gate. Use this category only for explicit alias entries that preserve old names or for future deprecated wrappers after PMO approval.

## Boundary With QuadrotorExperiments.SystemModules

`QuadrotorExperiments.SystemModules.AWFFController` is a system-architecture interface module inside a full Sunray150 system diagram. It should not own the controller library taxonomy. `QuadrotorControllerBlocks` should own reusable controller block definitions and category aliases; `QuadrotorExperiments.SystemModules` should only expose system-level architecture modules that may instantiate or reference those controllers.

## Compatibility Strategy

- Keep all current flat class load paths for the first write slice.
- Add category aliases only after a separate write task approves package files.
- Do not rewrite scenario YAML, experiment models, or docs in the package-shell write gate.
- After MCP/static validation, a later reference-migration task can decide whether to promote category paths as canonical names.
