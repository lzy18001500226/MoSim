# 012 MoSimQuadrotorModel Graphical Audit Queue Refinement

This is a static-only queue refinement. No MWORKS/Sysplorer/Syslab GUI, MCP, screenshots, check_model, simulation, Smart Layout, or model edits were used.

## Inputs
- 011 static source inventory: 126 candidates, 109 ready_for_live_audit, 17 low_priority, 0 missing-source blockers.
- 006/CoAgentOps live context: live MWORKS route remains blocked by reusable-session/session_manager startup behavior.

## First Batch
- Selected candidates: 20 / 20 maximum.
- controller_category_package_browser_and_topology_screen: 5
- factory_trace_wiring_isolation_screen: 3
- package_browser_visibility: 8
- package_browser_visibility_and_r1_serialized_check_model: 1
- planning_display_or_map_visual_screen: 2
- system_level_sysblock_layout_screen: 1

| Seq | Candidate | Bucket | Source |
|---:|---|---|---|
| 1 | `MoSimQuadrotorModel.Controllers` | package_browser_visibility | `MoSimQuadrotorModel.Controllers` |
| 2 | `MoSimQuadrotorModel.Dynamics` | package_browser_visibility_and_r1_serialized_check_model | `MoSimQuadrotorModel.Dynamics` |
| 3 | `MoSimQuadrotorModel.Missions` | package_browser_visibility | `MoSimQuadrotorModel.Missions` |
| 4 | `MoSimQuadrotorModel.Robustness` | package_browser_visibility | `MoSimQuadrotorModel.Robustness` |
| 5 | `MoSimQuadrotorModel.Planning` | package_browser_visibility | `MoSimQuadrotorModel.Planning` |
| 6 | `MoSimQuadrotorModel.SceneTrace` | package_browser_visibility | `MoSimQuadrotorModel.SceneTrace` |
| 7 | `MoSimQuadrotorModel.System` | package_browser_visibility | `MoSimQuadrotorModel.System` |
| 8 | `MoSimQuadrotorModel.Formation` | package_browser_visibility | `MoSimQuadrotorModel.Formation` |
| 9 | `MoSimQuadrotorModel.Support` | package_browser_visibility | `MoSimQuadrotorModel.Support` |
| 10 | `MoSimQuadrotorModel.Controllers.AWFFPidBlocks` | controller_category_package_browser_and_topology_screen | `QuadrotorControllerBlocks.AWFFPidBlocks` |
| 11 | `MoSimQuadrotorModel.Controllers.InnovationControllers` | controller_category_package_browser_and_topology_screen | `QuadrotorControllerBlocks.InnovationControllers` |
| 12 | `MoSimQuadrotorModel.Controllers.FaultAllocationControllers` | controller_category_package_browser_and_topology_screen | `QuadrotorControllerBlocks.FaultAllocationControllers` |
| 13 | `MoSimQuadrotorModel.Controllers.LinearMPCControllers` | controller_category_package_browser_and_topology_screen | `QuadrotorControllerBlocks.LinearMPCControllers` |
| 14 | `MoSimQuadrotorModel.Controllers.SafetyControllers` | controller_category_package_browser_and_topology_screen | `QuadrotorControllerBlocks.SafetyControllers` |
| 15 | `MoSimQuadrotorModel.Planning.PlanningNavigationDisplay` | planning_display_or_map_visual_screen | `QuadrotorExperiments.PlanningScenarios.PlanningNavigationDisplay` |
| 16 | `MoSimQuadrotorModel.Planning.Sunray150PlanningOpenBlocksColorMapReview` | planning_display_or_map_visual_screen | `QuadrotorExperiments.PlanningScenarios.Sunray150PlanningOpenBlocksColorMapReview` |
| 17 | `MoSimQuadrotorModel.System.Architecture.Sunray150CompleteSystemGraphical_Sysblock` | system_level_sysblock_layout_screen | `QuadrotorExperiments.SystemArchitecture.Sunray150CompleteSystemGraphical_Sysblock` |
| 18 | `MoSimQuadrotorModel.SceneTrace.Isolation.FactoryTraceIso04ControllerPlantWiringSmoke` | factory_trace_wiring_isolation_screen | `QuadrotorExperiments.TraceIsolation.FactoryTraceIso04ControllerPlantWiringSmoke` |
| 19 | `MoSimQuadrotorModel.SceneTrace.Isolation.FactoryTraceIso22SensorDisplayReconnectSmoke` | factory_trace_wiring_isolation_screen | `QuadrotorExperiments.TraceIsolation.FactoryTraceIso22SensorDisplayReconnectSmoke` |
| 20 | `MoSimQuadrotorModel.SceneTrace.Isolation.FactoryTraceIso28ActuatorToWrenchBridgeSmoke` | factory_trace_wiring_isolation_screen | `QuadrotorExperiments.TraceIsolation.FactoryTraceIso28ActuatorToWrenchBridgeSmoke` |

## Live Prerequisites
- Resolve the CoAgentOps reusable-session blocker before any live audit.
- Serialize with R1; do not run R2 package/browser/diagram work while R1 owns the MWORKS resource.
- Future live audit may collect package-browser and diagram screenshots, but must not claim check_model, simulation, graphical acceptance, controller performance, planner_ready, mission success, or closed_loop unless a later task explicitly proves those gates.

## Evidence Files
- `first_batch_live_audit_queue.json`
- `first_batch_candidate_matrix.json`
- `r1_r2_resource_serialization_plan.json`
- `queue_refinement_blockers.json`
