# QuadrotorExperiments Classification Cleanup Evidence

Date: 2026-06-06 CST

Owner: MoSim PMO (`019e9868-83ea-70f0-92c5-a3a408bd78c6`)

## Scope

Cleaned the project-owned `Models/QuadrotorExperiments` package organization after the user reported that the package tree was too chaotic.

This pass is a compatibility classification pass only. It keeps historical flat model names available and adds categorized package entries with Chinese descriptions. It does not migrate every model into physical subdirectories and does not change controller, dynamics, planner, or parameter semantics.

## File Changes

- Updated `Models/QuadrotorExperiments/package.mo`.
- Updated `Models/QuadrotorExperiments/package.order`.
- Deleted `Models/QuadrotorExperiments/Sunray150DynamicsUpgradeSmoke.mo`.

## Categories Added

- `OfficialScenarios` - official task and Sysblock closed-loop scenario aliases.
- `ControllerBaselines` - AWFF/PID comparison baseline aliases.
- `RobustFaultScenarios` - mass perturbation, wind, safety, rotor-loss and fault-allocation aliases.
- `PlanningScenarios` - trajectory planning and obstacle scenario aliases.
- `SceneTraceScenarios` - UE scene and trace-table smoke aliases.
- `TraceIsolation` - Factory trace isolation smoke aliases.
- `DynamicsUpgrade` - Sunray150 RflySim-like dynamics and physical-wrench aliases.
- `SystemArchitecture` - complete-system graphical and failure-mode aliases.
- `SystemModules` - complete-system nested module aliases.
- `SupportModels` - trace table/reference and MWORKS echo-state support aliases.
- `FormationScenarios` - multi-UAV formation alias.

## Deletion Basis

`Sunray150DynamicsUpgradeSmoke.mo` was deleted because its three classes were byte-equivalent after newline normalization to the definitions already embedded in `Models/QuadrotorExperiments/package.mo`:

- `Sunray150RflyStyleRotorDynamics`
- `Sunray150DynamicsUpgradeHoverSmoke`
- `Sunray150DynamicsUpgradeYawStepSmoke`

The file was not listed in `package.order` and had a filename that did not match any single contained class. Keeping it created a duplicate source path for the same dynamics smoke classes.

`FormationTriangleFigure8LinearMPCSysblockClosedLoop.mo` was not deleted. It is a real model referenced by `Docs/Index/project_work_memory_index.md`, `Docs/Design/06_多机编队控制.md`, and historical formation results. It was registered in `package.order` and exposed through `FormationScenarios.TriangleFigure8LinearMPC`.

## Static Checks

Passed:

- All `extends QuadrotorExperiments.*` terminal targets found in local package/files.
- No `.mo` files missing from `package.order`.
- No `package.order` entries without a same-name file or embedded package/class definition.
- No duplicate `package.order` entries.
- `git diff --check` clean for the touched files.

Remaining intentional multi-class files:

- `PlannedQuinticReference.mo` includes helper functions.
- `PlanningNavigationDisplay.mo` includes helper functions.
- `TraceInlineReference.mo` includes `traceLookup`.

## Sysplorer MCP Checks

Session:

- `session_manager(action=health)` passed.
- Dedicated Sysplorer port: `49153`.
- `model_manager(load_file, force_reload=true)` succeeded for `Models/QuadrotorExperiments/package.mo`.
- `model_manager(load_file, force_reload=true)` succeeded for `References/MWORKS/QuadrotorModel/package.mo`.
- `model_manager(load_file, force_reload=true)` succeeded for:
  - `Models/QuadrotorControllerBlocks/AWFF_LinearMPCOuterLoopControllerEquation_Sysblock.mo`
  - `Models/QuadrotorControllerBlocks/AWFF_FullControllerEquation_Sysblock.mo`

Representative `check_model` passes:

- `QuadrotorExperiments.DynamicsUpgrade.RotorDynamicsCore`
- `QuadrotorExperiments.DynamicsUpgrade.PhysicalWrenchAdapter`
- `QuadrotorExperiments.TraceIsolation.Iso27ActuatorInput`
- `QuadrotorExperiments.SupportModels.EchoMcpState`
- `QuadrotorExperiments.FormationScenarios.TriangleFigure8LinearMPC`
- `QuadrotorExperiments.ControllerBaselines.AntiWindupFeedforwardCore`
- `QuadrotorExperiments.SystemModules.PerceptionInterface`
- `QuadrotorExperiments.SystemArchitecture.CompleteSystemGraphical`

Dependency note:

- `TraceIsolation.Iso27ActuatorInput` required the independent controller file `AWFF_LinearMPCOuterLoopControllerEquation_Sysblock.mo` to be loaded.
- `SystemModules.PerceptionInterface` required `AWFF_FullControllerEquation_Sysblock.mo` for complete-system nested module resolution.

## GUI Sentinel Boundary

Windows MCP visible-desktop screenshots were taken before and after the Sysplorer MCP checks. No visible MWORKS/Sysplorer error-report dialog was observed on the active desktop. This is a visible-desktop sentinel only; it does not prove an occluded Sysplorer window had no hidden dialog.

## Non-Claims

This pass does not claim:

- final package migration into physical subdirectories,
- controller or plant behavior improvement,
- dynamics parameter identification,
- Factory trace consumption,
- live UE/ROS2 runtime ack,
- planner readiness,
- closed-loop mission success.
