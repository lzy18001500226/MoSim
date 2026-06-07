# QuadrotorExperiments Category Migration Table

Request: `RFLY-MOSIM-MWORKS-R2-QUADROTOR-EXPERIMENTS-ORGANIZATION-20260606-004`

This is a read-only static migration plan. No model/package files were edited, no GUI/MCP was used, and no graphical/check/simulation claim is made.

## Summary

- `package.order` entries: 115
- category package entries: 11
- flat legacy entries after categories: 104
- sibling `.mo` definitions: 94
- embedded `package.mo` definitions: 10
- category alias coverage: 100 / 104
- category alias gaps: FactoryTraceIso22SensorDisplayReconnectSmoke, FactoryTraceIso28ActuatorToWrenchBridgeSmoke, FactoryTraceIso29ExternalFrameWrenchBoundarySmoke, FactoryTraceIso30ExternalBodyStateBoundarySmoke
- `package.order` controls display order only; it is not a hiding, unload, deletion, or compatibility mechanism.

## Recommended Action Terms

- `keep_as_public_compatibility_must_not_delete`: old flat path is actively protected by evidence chains, support use, or system/runtime configs.
- `keep_as_public_compatibility_until_reference_migration`: keep flat path until all configs/scripts/docs/results move to category path and R1 verifies model checks.
- `deprecated_hide_candidate_after_full_reference_search`: possible future browser cleanup target only after full reference search and check-model gate; not deletion authority.
- `add_category_alias_later_then_keep_flat_path_compatibility`: later write task should add or finish category alias first, then keep old path as compatibility target.

## OfficialScenarios

| Flat entry | Definition | Existing alias | Recommendation | Canonical strategy | Reference risk |
|---|---|---|---|---|---|
| `Example1AWFFSysblockClosedLoop` | sibling_mo_file | QuadrotorExperiments.OfficialScenarios.Example1AWFF | `keep_as_public_compatibility_until_reference_migration` | `category_alias_exists_flat_path_remains_compatibility_target` | formal=11; tmp=2 |
| `Example1HelicalFigure8TrailSysblockClosedLoop` | sibling_mo_file | QuadrotorExperiments.OfficialScenarios.Example1HelicalFigure8Trail | `keep_as_public_compatibility_until_reference_migration` | `category_alias_exists_flat_path_remains_compatibility_target` | formal=7; tmp=0 |
| `Example1INDISysblockClosedLoop` | sibling_mo_file | QuadrotorExperiments.OfficialScenarios.Example1INDI | `keep_as_public_compatibility_until_reference_migration` | `category_alias_exists_flat_path_remains_compatibility_target` | formal=9; tmp=0 |
| `Example1L1SysblockClosedLoop` | sibling_mo_file | QuadrotorExperiments.OfficialScenarios.Example1L1 | `keep_as_public_compatibility_until_reference_migration` | `category_alias_exists_flat_path_remains_compatibility_target` | formal=9; tmp=0 |
| `Example1LinearMPCSysblockClosedLoop` | sibling_mo_file | QuadrotorExperiments.OfficialScenarios.Example1LinearMPC | `keep_as_public_compatibility_until_reference_migration` | `category_alias_exists_flat_path_remains_compatibility_target` | formal=13; tmp=69 |
| `Example1PlanarFigure8TrailSysblockClosedLoop` | sibling_mo_file | QuadrotorExperiments.OfficialScenarios.Example1PlanarFigure8Trail | `keep_as_public_compatibility_until_reference_migration` | `category_alias_exists_flat_path_remains_compatibility_target` | formal=8; tmp=0 |
| `Example2AWFFSysblockClosedLoop` | sibling_mo_file | QuadrotorExperiments.OfficialScenarios.Example2AWFF | `keep_as_public_compatibility_until_reference_migration` | `category_alias_exists_flat_path_remains_compatibility_target` | formal=10; tmp=0 |
| `Example2HelixTunedAWFFSysblockClosedLoop` | sibling_mo_file | QuadrotorExperiments.OfficialScenarios.Example2HelixTunedAWFF | `keep_as_public_compatibility_until_reference_migration` | `category_alias_exists_flat_path_remains_compatibility_target` | formal=9; tmp=0 |
| `Example2HelixTunedINDISysblockClosedLoop` | sibling_mo_file | QuadrotorExperiments.OfficialScenarios.Example2HelixTunedINDI | `keep_as_public_compatibility_until_reference_migration` | `category_alias_exists_flat_path_remains_compatibility_target` | formal=8; tmp=0 |
| `Example2INDISysblockClosedLoop` | sibling_mo_file | QuadrotorExperiments.OfficialScenarios.Example2INDI | `keep_as_public_compatibility_until_reference_migration` | `category_alias_exists_flat_path_remains_compatibility_target` | formal=6; tmp=0 |
| `Example2LinearMPCSysblockClosedLoop` | sibling_mo_file | QuadrotorExperiments.OfficialScenarios.Example2LinearMPC | `keep_as_public_compatibility_until_reference_migration` | `category_alias_exists_flat_path_remains_compatibility_target` | formal=8; tmp=0 |
| `Example3AWFFSysblockClosedLoop` | sibling_mo_file | QuadrotorExperiments.OfficialScenarios.Example3AWFF | `keep_as_public_compatibility_until_reference_migration` | `category_alias_exists_flat_path_remains_compatibility_target` | formal=10; tmp=0 |
| `Example3INDISysblockClosedLoop` | sibling_mo_file | QuadrotorExperiments.OfficialScenarios.Example3INDI | `keep_as_public_compatibility_until_reference_migration` | `category_alias_exists_flat_path_remains_compatibility_target` | formal=9; tmp=0 |
| `Example3L1SysblockClosedLoop` | sibling_mo_file | QuadrotorExperiments.OfficialScenarios.Example3L1 | `keep_as_public_compatibility_until_reference_migration` | `category_alias_exists_flat_path_remains_compatibility_target` | formal=9; tmp=0 |
| `Example3LinearMPCSysblockClosedLoop` | sibling_mo_file | QuadrotorExperiments.OfficialScenarios.Example3LinearMPC | `keep_as_public_compatibility_until_reference_migration` | `category_alias_exists_flat_path_remains_compatibility_target` | formal=8; tmp=0 |

## RobustFaultScenarios

| Flat entry | Definition | Existing alias | Recommendation | Canonical strategy | Reference risk |
|---|---|---|---|---|---|
| `Example1Mass20AWFFSysblockClosedLoop` | sibling_mo_file | QuadrotorExperiments.RobustFaultScenarios.Mass20AWFF | `keep_as_public_compatibility_until_reference_migration` | `category_alias_exists_flat_path_remains_compatibility_target` | formal=7; tmp=0 |
| `Example1Mass20L1SysblockClosedLoop` | sibling_mo_file | QuadrotorExperiments.RobustFaultScenarios.Mass20L1 | `keep_as_public_compatibility_until_reference_migration` | `category_alias_exists_flat_path_remains_compatibility_target` | formal=9; tmp=0 |
| `Example1Mass20LinearMPCSysblockClosedLoop` | sibling_mo_file | QuadrotorExperiments.RobustFaultScenarios.Mass20LinearMPC | `keep_as_public_compatibility_until_reference_migration` | `category_alias_exists_flat_path_remains_compatibility_target` | formal=6; tmp=0 |
| `Example1QPNMPCSafetyReturnLandSysblockClosedLoop` | sibling_mo_file | QuadrotorExperiments.RobustFaultScenarios.SafetyReturnLand | `keep_as_public_compatibility_until_reference_migration` | `category_alias_exists_flat_path_remains_compatibility_target` | formal=9; tmp=0 |
| `Example1QPNMPCSafetySysblockClosedLoop` | sibling_mo_file | QuadrotorExperiments.RobustFaultScenarios.SafetyQPNMPC | `keep_as_public_compatibility_until_reference_migration` | `category_alias_exists_flat_path_remains_compatibility_target` | formal=10; tmp=0 |
| `Example1Rotor1Loss15AWFFSysblockClosedLoop` | sibling_mo_file | QuadrotorExperiments.RobustFaultScenarios.RotorLoss.Rotor1AWFF | `keep_as_public_compatibility_until_reference_migration` | `category_alias_exists_flat_path_remains_compatibility_target` | formal=8; tmp=0 |
| `Example1Rotor1Loss15L1FaultAllocationSysblockClosedLoop` | sibling_mo_file | QuadrotorExperiments.RobustFaultScenarios.RotorLoss.Rotor1L1FaultAllocation | `keep_as_public_compatibility_until_reference_migration` | `category_alias_exists_flat_path_remains_compatibility_target` | formal=9; tmp=0 |
| `Example1Rotor1Loss15L1MultiFaultIsolationSysblockClosedLoop` | sibling_mo_file | QuadrotorExperiments.RobustFaultScenarios.RotorLoss.Rotor1L1MultiFaultIsolation | `keep_as_public_compatibility_until_reference_migration` | `category_alias_exists_flat_path_remains_compatibility_target` | formal=6; tmp=0 |
| `Example1Rotor1Loss15L1OnlineFaultAllocationSysblockClosedLoop` | sibling_mo_file | QuadrotorExperiments.RobustFaultScenarios.RotorLoss.Rotor1L1OnlineFaultAllocation | `keep_as_public_compatibility_until_reference_migration` | `category_alias_exists_flat_path_remains_compatibility_target` | formal=10; tmp=0 |
| `Example1Rotor1Loss15L1SysblockClosedLoop` | sibling_mo_file | QuadrotorExperiments.RobustFaultScenarios.RotorLoss.Rotor1L1 | `keep_as_public_compatibility_until_reference_migration` | `category_alias_exists_flat_path_remains_compatibility_target` | formal=9; tmp=0 |
| `Example1Rotor1Loss15LinearMPCOnlineFaultAllocationSysblockClosedLoop` | sibling_mo_file | QuadrotorExperiments.RobustFaultScenarios.RotorLoss.Rotor1LinearMPCOnlineFaultAllocation | `keep_as_public_compatibility_until_reference_migration` | `category_alias_exists_flat_path_remains_compatibility_target` | formal=7; tmp=0 |
| `Example1Rotor1Loss15LinearMPCSysblockClosedLoop` | sibling_mo_file | QuadrotorExperiments.RobustFaultScenarios.RotorLoss.Rotor1LinearMPC | `keep_as_public_compatibility_until_reference_migration` | `category_alias_exists_flat_path_remains_compatibility_target` | formal=7; tmp=0 |
| `Example1Rotor1Loss15WindGustAWFFFaultCompensationSysblockClosedLoop` | sibling_mo_file | QuadrotorExperiments.RobustFaultScenarios.RotorLoss.Rotor1WindGustAWFFFaultCompensation | `keep_as_public_compatibility_until_reference_migration` | `category_alias_exists_flat_path_remains_compatibility_target` | formal=6; tmp=1 |
| `Example1Rotor1Loss15WindGustAWFFSysblockClosedLoop` | sibling_mo_file | QuadrotorExperiments.RobustFaultScenarios.RotorLoss.Rotor1WindGustAWFF | `keep_as_public_compatibility_until_reference_migration` | `category_alias_exists_flat_path_remains_compatibility_target` | formal=6; tmp=0 |
| `Example1Rotor1Loss15WindGustL1MultiFaultIsolationSysblockClosedLoop` | sibling_mo_file | QuadrotorExperiments.RobustFaultScenarios.RotorLoss.Rotor1WindGustL1MultiFaultIsolation | `keep_as_public_compatibility_until_reference_migration` | `category_alias_exists_flat_path_remains_compatibility_target` | formal=6; tmp=0 |
| `Example1Rotor1Loss15WindGustLinearMPCOnlineFaultAllocationSysblockClosedLoop` | sibling_mo_file | QuadrotorExperiments.RobustFaultScenarios.RotorLoss.Rotor1WindGustLinearMPCOnlineFaultAllocation | `keep_as_public_compatibility_until_reference_migration` | `category_alias_exists_flat_path_remains_compatibility_target` | formal=7; tmp=0 |
| `Example1Rotor2Loss15AWFFSysblockClosedLoop` | sibling_mo_file | QuadrotorExperiments.RobustFaultScenarios.RotorLoss.Rotor2AWFF | `keep_as_public_compatibility_until_reference_migration` | `category_alias_exists_flat_path_remains_compatibility_target` | formal=5; tmp=0 |
| `Example1Rotor2Loss15L1MultiFaultIsolationSysblockClosedLoop` | sibling_mo_file | QuadrotorExperiments.RobustFaultScenarios.RotorLoss.Rotor2L1MultiFaultIsolation | `keep_as_public_compatibility_until_reference_migration` | `category_alias_exists_flat_path_remains_compatibility_target` | formal=6; tmp=0 |
| `Example1Rotor2Loss15WindGustAWFFSysblockClosedLoop` | sibling_mo_file | QuadrotorExperiments.RobustFaultScenarios.RotorLoss.Rotor2WindGustAWFF | `keep_as_public_compatibility_until_reference_migration` | `category_alias_exists_flat_path_remains_compatibility_target` | formal=5; tmp=0 |
| `Example1Rotor2Loss15WindGustL1MultiFaultIsolationSysblockClosedLoop` | sibling_mo_file | QuadrotorExperiments.RobustFaultScenarios.RotorLoss.Rotor2WindGustL1MultiFaultIsolation | `keep_as_public_compatibility_until_reference_migration` | `category_alias_exists_flat_path_remains_compatibility_target` | formal=6; tmp=0 |
| `Example1Rotor2Loss15WindGustLinearMPCOnlineFaultAllocationSysblockClosedLoop` | sibling_mo_file | QuadrotorExperiments.RobustFaultScenarios.RotorLoss.Rotor2WindGustLinearMPCOnlineFaultAllocation | `keep_as_public_compatibility_until_reference_migration` | `category_alias_exists_flat_path_remains_compatibility_target` | formal=7; tmp=0 |
| `Example1Rotor3Loss15AWFFSysblockClosedLoop` | sibling_mo_file | QuadrotorExperiments.RobustFaultScenarios.RotorLoss.Rotor3AWFF | `keep_as_public_compatibility_until_reference_migration` | `category_alias_exists_flat_path_remains_compatibility_target` | formal=5; tmp=0 |
| `Example1Rotor3Loss15L1MultiFaultIsolationSysblockClosedLoop` | sibling_mo_file | QuadrotorExperiments.RobustFaultScenarios.RotorLoss.Rotor3L1MultiFaultIsolation | `keep_as_public_compatibility_until_reference_migration` | `category_alias_exists_flat_path_remains_compatibility_target` | formal=6; tmp=0 |
| `Example1Rotor3Loss15WindGustAWFFSysblockClosedLoop` | sibling_mo_file | QuadrotorExperiments.RobustFaultScenarios.RotorLoss.Rotor3WindGustAWFF | `keep_as_public_compatibility_until_reference_migration` | `category_alias_exists_flat_path_remains_compatibility_target` | formal=5; tmp=0 |
| `Example1Rotor3Loss15WindGustL1MultiFaultIsolationSysblockClosedLoop` | sibling_mo_file | QuadrotorExperiments.RobustFaultScenarios.RotorLoss.Rotor3WindGustL1MultiFaultIsolation | `keep_as_public_compatibility_until_reference_migration` | `category_alias_exists_flat_path_remains_compatibility_target` | formal=6; tmp=0 |
| `Example1Rotor3Loss15WindGustLinearMPCOnlineFaultAllocationSysblockClosedLoop` | sibling_mo_file | QuadrotorExperiments.RobustFaultScenarios.RotorLoss.Rotor3WindGustLinearMPCOnlineFaultAllocation | `keep_as_public_compatibility_until_reference_migration` | `category_alias_exists_flat_path_remains_compatibility_target` | formal=7; tmp=0 |
| `Example1Rotor4Loss15AWFFSysblockClosedLoop` | sibling_mo_file | QuadrotorExperiments.RobustFaultScenarios.RotorLoss.Rotor4AWFF | `keep_as_public_compatibility_until_reference_migration` | `category_alias_exists_flat_path_remains_compatibility_target` | formal=5; tmp=0 |
| `Example1Rotor4Loss15L1MultiFaultIsolationSysblockClosedLoop` | sibling_mo_file | QuadrotorExperiments.RobustFaultScenarios.RotorLoss.Rotor4L1MultiFaultIsolation | `keep_as_public_compatibility_until_reference_migration` | `category_alias_exists_flat_path_remains_compatibility_target` | formal=6; tmp=0 |
| `Example1Rotor4Loss15WindGustAWFFSysblockClosedLoop` | sibling_mo_file | QuadrotorExperiments.RobustFaultScenarios.RotorLoss.Rotor4WindGustAWFF | `keep_as_public_compatibility_until_reference_migration` | `category_alias_exists_flat_path_remains_compatibility_target` | formal=5; tmp=0 |
| `Example1Rotor4Loss15WindGustL1MultiFaultIsolationSysblockClosedLoop` | sibling_mo_file | QuadrotorExperiments.RobustFaultScenarios.RotorLoss.Rotor4WindGustL1MultiFaultIsolation | `keep_as_public_compatibility_until_reference_migration` | `category_alias_exists_flat_path_remains_compatibility_target` | formal=6; tmp=0 |
| `Example1Rotor4Loss15WindGustLinearMPCOnlineFaultAllocationSysblockClosedLoop` | sibling_mo_file | QuadrotorExperiments.RobustFaultScenarios.RotorLoss.Rotor4WindGustLinearMPCOnlineFaultAllocation | `keep_as_public_compatibility_until_reference_migration` | `category_alias_exists_flat_path_remains_compatibility_target` | formal=7; tmp=0 |
| `Example1WindGustAWFFSysblockClosedLoop` | sibling_mo_file | QuadrotorExperiments.RobustFaultScenarios.WindGustAWFF | `keep_as_public_compatibility_until_reference_migration` | `category_alias_exists_flat_path_remains_compatibility_target` | formal=8; tmp=0 |
| `Example1WindGustL1SysblockClosedLoop` | sibling_mo_file | QuadrotorExperiments.RobustFaultScenarios.WindGustL1 | `keep_as_public_compatibility_until_reference_migration` | `category_alias_exists_flat_path_remains_compatibility_target` | formal=9; tmp=0 |
| `Example1WindGustLinearMPCSysblockClosedLoop` | sibling_mo_file | QuadrotorExperiments.RobustFaultScenarios.WindGustLinearMPC | `keep_as_public_compatibility_until_reference_migration` | `category_alias_exists_flat_path_remains_compatibility_target` | formal=6; tmp=0 |

## PlanningScenarios

| Flat entry | Definition | Existing alias | Recommendation | Canonical strategy | Reference risk |
|---|---|---|---|---|---|
| `PlannedQuinticReference` | sibling_mo_file | QuadrotorExperiments.PlanningScenarios.QuinticReference | `keep_as_public_compatibility_must_not_delete` | `category_alias_exists_flat_path_remains_compatibility_target` | formal=44; tmp=1 |
| `PlanningNavigationDisplay` | sibling_mo_file | QuadrotorExperiments.PlanningScenarios.NavigationDisplay | `keep_as_public_compatibility_must_not_delete` | `category_alias_exists_flat_path_remains_compatibility_target` | formal=40; tmp=83 |
| `Sunray150PlanningCorridorGateAWFFSysblockClosedLoop` | sibling_mo_file | QuadrotorExperiments.PlanningScenarios.CorridorGateAWFF | `keep_as_public_compatibility_must_not_delete` | `category_alias_exists_flat_path_remains_compatibility_target` | formal=4; tmp=0 |
| `Sunray150PlanningCorridorGateLinearMPCSysblockClosedLoop` | sibling_mo_file | QuadrotorExperiments.PlanningScenarios.CorridorGateLinearMPC | `keep_as_public_compatibility_must_not_delete` | `category_alias_exists_flat_path_remains_compatibility_target` | formal=7; tmp=0 |
| `Sunray150PlanningOpenBlocksAWFFSysblockClosedLoop` | sibling_mo_file | QuadrotorExperiments.PlanningScenarios.OpenBlocksAWFF | `keep_as_public_compatibility_must_not_delete` | `category_alias_exists_flat_path_remains_compatibility_target` | formal=6; tmp=0 |
| `Sunray150PlanningOpenBlocksColorMapReview` | sibling_mo_file | QuadrotorExperiments.PlanningScenarios.OpenBlocksColorMapReview | `keep_as_public_compatibility_must_not_delete` | `category_alias_exists_flat_path_remains_compatibility_target` | formal=6; tmp=0 |
| `Sunray150PlanningOpenBlocksLinearMPCSysblockClosedLoop` | sibling_mo_file | QuadrotorExperiments.PlanningScenarios.OpenBlocksLinearMPC | `keep_as_public_compatibility_must_not_delete` | `category_alias_exists_flat_path_remains_compatibility_target` | formal=25; tmp=1 |

## SceneTraceScenarios

| Flat entry | Definition | Existing alias | Recommendation | Canonical strategy | Reference risk |
|---|---|---|---|---|---|
| `Sunray150UEFactoryLinearMPCSysblockSmoke` | sibling_mo_file | QuadrotorExperiments.SceneTraceScenarios.UEFactoryLinearMPC | `keep_as_public_compatibility_must_not_delete` | `category_alias_exists_flat_path_remains_compatibility_target` | formal=11; tmp=0 |
| `Sunray150UEFactoryTraceTableLinearMPCSysblockSmoke` | sibling_mo_file | QuadrotorExperiments.SceneTraceScenarios.UEFactoryTraceTable | `keep_as_public_compatibility_must_not_delete` | `category_alias_exists_flat_path_remains_compatibility_target` | formal=20; tmp=82 |
| `Sunray150UEDerelictLinearMPCSysblockSmoke` | sibling_mo_file | QuadrotorExperiments.SceneTraceScenarios.UEDerelictLinearMPC | `keep_as_public_compatibility_must_not_delete` | `category_alias_exists_flat_path_remains_compatibility_target` | formal=9; tmp=0 |

## TraceIsolation

| Flat entry | Definition | Existing alias | Recommendation | Canonical strategy | Reference risk |
|---|---|---|---|---|---|
| `FactoryLiteTraceSmoke` | sibling_mo_file | QuadrotorExperiments.TraceIsolation.FactoryLite | `keep_as_public_compatibility_must_not_delete` | `category_alias_exists_flat_path_remains_compatibility_target` | formal=19; tmp=79 |
| `FactoryTraceIso01FullDisplaySmoke` | sibling_mo_file | QuadrotorExperiments.TraceIsolation.Iso01FullDisplay | `keep_as_public_compatibility_must_not_delete` | `category_alias_exists_flat_path_remains_compatibility_target` | formal=24; tmp=73 |
| `FactoryTraceIso02ControllerOnlySmoke` | sibling_mo_file | QuadrotorExperiments.TraceIsolation.Iso02ControllerOnly | `keep_as_public_compatibility_must_not_delete` | `category_alias_exists_flat_path_remains_compatibility_target` | formal=6; tmp=73 |
| `FactoryTraceIso03PlantHoverStackSmoke` | sibling_mo_file | QuadrotorExperiments.TraceIsolation.Iso03PlantHoverStack | `keep_as_public_compatibility_must_not_delete` | `category_alias_exists_flat_path_remains_compatibility_target` | formal=8; tmp=73 |
| `FactoryTraceIso04ControllerPlantWiringSmoke` | sibling_mo_file | QuadrotorExperiments.TraceIsolation.Iso04ControllerPlantWiring | `keep_as_public_compatibility_must_not_delete` | `category_alias_exists_flat_path_remains_compatibility_target` | formal=7; tmp=73 |
| `FactoryTraceIso05CleanHoverSumSmoke` | sibling_mo_file | QuadrotorExperiments.TraceIsolation.Iso05CleanHoverSum | `keep_as_public_compatibility_must_not_delete` | `category_alias_exists_flat_path_remains_compatibility_target` | formal=6; tmp=69 |
| `FactoryTraceIso06CleanControllerPlantWiringSmoke` | sibling_mo_file | QuadrotorExperiments.TraceIsolation.Iso06CleanControllerPlantWiring | `keep_as_public_compatibility_must_not_delete` | `category_alias_exists_flat_path_remains_compatibility_target` | formal=8; tmp=69 |
| `FactoryTraceIso07CleanControllerOpenFeedbackSmoke` | sibling_mo_file | QuadrotorExperiments.TraceIsolation.Iso07ControllerOpenFeedback | `keep_as_public_compatibility_must_not_delete` | `category_alias_exists_flat_path_remains_compatibility_target` | formal=8; tmp=69 |
| `FactoryTraceIso08PositionFeedbackSmoke` | sibling_mo_file | QuadrotorExperiments.TraceIsolation.Iso08PositionFeedback | `keep_as_public_compatibility_must_not_delete` | `category_alias_exists_flat_path_remains_compatibility_target` | formal=10; tmp=66 |
| `FactoryTraceIso09PositionAttitudeFeedbackSmoke` | sibling_mo_file | QuadrotorExperiments.TraceIsolation.Iso09PositionAttitudeFeedback | `keep_as_public_compatibility_must_not_delete` | `category_alias_exists_flat_path_remains_compatibility_target` | formal=8; tmp=66 |
| `FactoryTraceIso10RollFeedbackSmoke` | sibling_mo_file | QuadrotorExperiments.TraceIsolation.Iso10RollFeedback | `keep_as_public_compatibility_must_not_delete` | `category_alias_exists_flat_path_remains_compatibility_target` | formal=9; tmp=63 |
| `FactoryTraceIso11PitchFeedbackSmoke` | sibling_mo_file | QuadrotorExperiments.TraceIsolation.Iso11PitchFeedback | `keep_as_public_compatibility_must_not_delete` | `category_alias_exists_flat_path_remains_compatibility_target` | formal=7; tmp=63 |
| `FactoryTraceIso12RollFeedbackNegatedSmoke` | sibling_mo_file | QuadrotorExperiments.TraceIsolation.Iso12RollFeedbackNegated | `keep_as_public_compatibility_must_not_delete` | `category_alias_exists_flat_path_remains_compatibility_target` | formal=7; tmp=63 |
| `FactoryTraceIso13PitchFeedbackNegatedSmoke` | sibling_mo_file | QuadrotorExperiments.TraceIsolation.Iso13PitchFeedbackNegated | `keep_as_public_compatibility_must_not_delete` | `category_alias_exists_flat_path_remains_compatibility_target` | formal=7; tmp=63 |
| `FactoryTraceIso14ConstantAttitudeInputSmoke` | sibling_mo_file | QuadrotorExperiments.TraceIsolation.Iso14ConstantAttitudeInput | `keep_as_public_compatibility_must_not_delete` | `category_alias_exists_flat_path_remains_compatibility_target` | formal=8; tmp=55 |
| `FactoryTraceIso15TableAttitudeInputSmoke` | sibling_mo_file | QuadrotorExperiments.TraceIsolation.Iso15TableAttitudeInput | `keep_as_public_compatibility_must_not_delete` | `category_alias_exists_flat_path_remains_compatibility_target` | formal=8; tmp=55 |
| `FactoryTraceIso16RealExpressionAngleSmoke` | sibling_mo_file | QuadrotorExperiments.TraceIsolation.Iso16RealExpressionAngle | `keep_as_public_compatibility_must_not_delete` | `category_alias_exists_flat_path_remains_compatibility_target` | formal=8; tmp=55 |
| `FactoryTraceIso17SampleHoldAngleSmoke` | sibling_mo_file | QuadrotorExperiments.TraceIsolation.Iso17SampleHoldAngle | `keep_as_public_compatibility_must_not_delete` | `category_alias_exists_flat_path_remains_compatibility_target` | formal=7; tmp=43 |
| `FactoryTraceIso18ProjectAttitudeEstimatorSmoke` | sibling_mo_file | QuadrotorExperiments.TraceIsolation.Iso18ProjectAttitudeEstimator | `keep_as_public_compatibility_must_not_delete` | `category_alias_exists_flat_path_remains_compatibility_target` | formal=7; tmp=43 |
| `FactoryTraceIso19RollPitchEstimatorSmoke` | sibling_mo_file | QuadrotorExperiments.TraceIsolation.Iso19RollPitchEstimator | `keep_as_public_compatibility_must_not_delete` | `category_alias_exists_flat_path_remains_compatibility_target` | formal=9; tmp=44 |
| `FactoryTraceIso20RollPitchYawEstimatorSmoke` | sibling_mo_file | QuadrotorExperiments.TraceIsolation.Iso20RollPitchYawEstimator | `keep_as_public_compatibility_must_not_delete` | `category_alias_exists_flat_path_remains_compatibility_target` | formal=13; tmp=37 |
| `FactoryTraceIso21ControllerRateAliasSmoke` | sibling_mo_file | QuadrotorExperiments.TraceIsolation.Iso21RateAlias | `keep_as_public_compatibility_must_not_delete` | `category_alias_exists_flat_path_remains_compatibility_target` | formal=16; tmp=30 |
| `FactoryTraceIso22SensorDisplayReconnectSmoke` | sibling_mo_file | missing | `keep_as_public_compatibility_must_not_delete` | `add_missing_category_alias_later_then_keep_flat_path_compatibility` | formal=12; tmp=19 |
| `FactoryTraceIso23PositionSampleHoldBridgeSmoke` | sibling_mo_file | QuadrotorExperiments.TraceIsolation.Iso23PositionSampleHold | `keep_as_public_compatibility_must_not_delete` | `category_alias_exists_flat_path_remains_compatibility_target` | formal=22; tmp=17 |
| `FactoryTraceIso24DirectAttitudeFeedbackSmoke` | sibling_mo_file | QuadrotorExperiments.TraceIsolation.Iso24DirectAttitudeFeedback | `keep_as_public_compatibility_must_not_delete` | `category_alias_exists_flat_path_remains_compatibility_target` | formal=14; tmp=8 |
| `FactoryTraceIso25SampleHoldAttitudeFeedbackSmoke` | sibling_mo_file | QuadrotorExperiments.TraceIsolation.Iso25AttitudeSampleHold | `keep_as_public_compatibility_must_not_delete` | `category_alias_exists_flat_path_remains_compatibility_target` | formal=16; tmp=6 |
| `FactoryTraceIso26ControllerOutputAliasSmoke` | sibling_mo_file | QuadrotorExperiments.TraceIsolation.Iso26ControllerOutput | `keep_as_public_compatibility_must_not_delete` | `category_alias_exists_flat_path_remains_compatibility_target` | formal=14; tmp=0 |
| `FactoryTraceIso27ActuatorInputAliasSmoke` | sibling_mo_file | QuadrotorExperiments.TraceIsolation.Iso27ActuatorInput | `keep_as_public_compatibility_must_not_delete` | `category_alias_exists_flat_path_remains_compatibility_target` | formal=18; tmp=0 |
| `FactoryTraceIso28ActuatorToWrenchBridgeSmoke` | sibling_mo_file | missing | `keep_as_public_compatibility_must_not_delete` | `add_missing_category_alias_later_then_keep_flat_path_compatibility` | formal=19; tmp=1 |
| `FactoryTraceIso29ExternalFrameWrenchBoundarySmoke` | sibling_mo_file | missing | `keep_as_public_compatibility_must_not_delete` | `add_missing_category_alias_later_then_keep_flat_path_compatibility` | formal=18; tmp=1 |
| `FactoryTraceIso30ExternalBodyStateBoundarySmoke` | embedded_in_package_mo | missing | `keep_as_public_compatibility_must_not_delete` | `add_missing_category_alias_later_then_keep_flat_path_compatibility` | formal=18; tmp=0 |

## DynamicsUpgrade

| Flat entry | Definition | Existing alias | Recommendation | Canonical strategy | Reference risk |
|---|---|---|---|---|---|
| `Sunray150RflyStyleRotorDynamics` | embedded_in_package_mo | QuadrotorExperiments.DynamicsUpgrade.RotorDynamicsCore | `keep_as_public_compatibility_must_not_delete` | `category_alias_exists_flat_path_remains_compatibility_target` | formal=20; tmp=0 |
| `Sunray150DynamicsUpgradeHoverSmoke` | embedded_in_package_mo | QuadrotorExperiments.DynamicsUpgrade.RotorHoverSmoke | `keep_as_public_compatibility_must_not_delete` | `category_alias_exists_flat_path_remains_compatibility_target` | formal=13; tmp=0 |
| `Sunray150DynamicsUpgradeYawStepSmoke` | embedded_in_package_mo | QuadrotorExperiments.DynamicsUpgrade.RotorYawStepSmoke | `keep_as_public_compatibility_must_not_delete` | `category_alias_exists_flat_path_remains_compatibility_target` | formal=14; tmp=0 |
| `Sunray150DynamicsWrapperSurface` | embedded_in_package_mo | QuadrotorExperiments.DynamicsUpgrade.WrapperSurface | `keep_as_public_compatibility_must_not_delete` | `category_alias_exists_flat_path_remains_compatibility_target` | formal=19; tmp=0 |
| `Sunray150DynamicsWrapperHoverSmoke` | embedded_in_package_mo | QuadrotorExperiments.DynamicsUpgrade.WrapperHoverSmoke | `keep_as_public_compatibility_must_not_delete` | `category_alias_exists_flat_path_remains_compatibility_target` | formal=11; tmp=0 |
| `Sunray150DynamicsWrapperYawStepSmoke` | embedded_in_package_mo | QuadrotorExperiments.DynamicsUpgrade.WrapperYawStepSmoke | `keep_as_public_compatibility_must_not_delete` | `category_alias_exists_flat_path_remains_compatibility_target` | formal=14; tmp=0 |
| `Sunray150PhysicalWrenchFrameAdapter` | embedded_in_package_mo | QuadrotorExperiments.DynamicsUpgrade.PhysicalWrenchAdapter | `keep_as_public_compatibility_must_not_delete` | `category_alias_exists_flat_path_remains_compatibility_target` | formal=20; tmp=0 |
| `Sunray150PhysicalWrenchHoverSmoke` | embedded_in_package_mo | QuadrotorExperiments.DynamicsUpgrade.PhysicalWrenchHoverSmoke | `keep_as_public_compatibility_must_not_delete` | `category_alias_exists_flat_path_remains_compatibility_target` | formal=16; tmp=0 |
| `Sunray150PhysicalWrenchYawStepSmoke` | embedded_in_package_mo | QuadrotorExperiments.DynamicsUpgrade.PhysicalWrenchYawStepSmoke | `keep_as_public_compatibility_must_not_delete` | `category_alias_exists_flat_path_remains_compatibility_target` | formal=18; tmp=0 |

## SupportModels

| Flat entry | Definition | Existing alias | Recommendation | Canonical strategy | Reference risk |
|---|---|---|---|---|---|
| `EchoMcpStateSmoke` | sibling_mo_file | QuadrotorExperiments.SupportModels.EchoMcpState | `keep_as_public_compatibility_must_not_delete` | `category_alias_exists_flat_path_remains_compatibility_target` | formal=14; tmp=0 |
| `TraceInlineReference` | sibling_mo_file | QuadrotorExperiments.SupportModels.TraceInline | `keep_as_public_compatibility_must_not_delete` | `category_alias_exists_flat_path_remains_compatibility_target` | formal=25; tmp=82 |
| `TraceLookupStandaloneSmoke` | sibling_mo_file | QuadrotorExperiments.SupportModels.TraceLookupStandalone | `keep_as_public_compatibility_must_not_delete` | `category_alias_exists_flat_path_remains_compatibility_target` | formal=11; tmp=84 |
| `TraceTableReference` | sibling_mo_file | QuadrotorExperiments.SupportModels.TraceTable | `keep_as_public_compatibility_must_not_delete` | `category_alias_exists_flat_path_remains_compatibility_target` | formal=8; tmp=0 |

## FormationScenarios

| Flat entry | Definition | Existing alias | Recommendation | Canonical strategy | Reference risk |
|---|---|---|---|---|---|
| `FormationTriangleFigure8LinearMPCSysblockClosedLoop` | sibling_mo_file | QuadrotorExperiments.FormationScenarios.TriangleFigure8LinearMPC | `keep_as_public_compatibility_must_not_delete` | `category_alias_exists_flat_path_remains_compatibility_target` | formal=13; tmp=0 |
