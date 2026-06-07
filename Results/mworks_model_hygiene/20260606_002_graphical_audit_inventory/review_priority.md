# MWORKS R2 Graphical Model Audit Inventory

Request: `RFLY-MOSIM-MWORKS-R2-GRAPHICAL-MODEL-AUDIT-INVENTORY-20260606-002`

This is a read-only static inventory and prioritization pass. It is not a GUI/MCP review, not Smart Layout output, not model-check evidence, and not simulation evidence.

## Scope Read

- `Models/QuadrotorExperiments/`
- `Models/QuadrotorControllerBlocks/`
- `References/MWORKS/QuadrotorModel/package.mo` as read-only baseline reference
- task 013 classification return packet
- MWORKS model-context and Sysblock graphical-modeling skills
- current agent task ledger and department registry

## Static Findings

- `Models/QuadrotorExperiments/` has 95 `.mo` files and 115 `package.order` entries.
- 21 `package.order` entries do not have sibling `.mo` files, but this is not automatically a defect:
  - 11 are categorized compatibility package aliases from task 013.
  - Sunray150 dynamics/wrench classes and `FactoryTraceIso30ExternalBodyStateBoundarySmoke` are embedded in `Models/QuadrotorExperiments/package.mo`.
- 80 experiment files contain `connect(...)`; 79 have no `Line(...)` annotations and 79 have no `Placement(...)` annotations in the static text scan.
- Only a small support subset has visible annotation density: `PlannedQuinticReference`, `TraceTableReference`, `TraceInlineReference`, `PlanningNavigationDisplay`, and the top-level `package.mo` embedded classes.
- `Models/QuadrotorControllerBlocks/` has 19 `.mo` files, several backup directories, and no `package.mo`/`package.order` discovered by this static pass.
- Controller files with mature graphical density exist and should be treated as reference patterns: `AWFF_InnovationGraphicalControllers.mo`, `AWFF_FullController_Sysblock.mo`, and `AWFF_FullControllerFlatGraphical_Sysblock.mo`.

## Priority Queue

### P0: First GUI/MCP Graphical Review Candidates

1. `FormationTriangleFigure8LinearMPCSysblockClosedLoop`
   - Reason: largest standalone wiring surface found, with 105 `connect(...)` equations and no static `Placement`, `Line`, `Diagram`, or `Icon` annotations.
   - Next gate: Sysplorer graphical open plus manual screenshot/layout review under a separate PMO-approved GUI/MCP task.

2. `Sunray150UEFactoryTraceTableLinearMPCSysblockSmoke`
   - Reason: historically important Factory trace wrapper; prior trace consumption was blocked around this family. Static text has 41 connects and no visible diagram annotations.
   - Next gate: GUI/layout inspection only after PMO scopes it; R1 owns any check/sim/trace-consumption evidence.

3. `FactoryTraceIso23` through current Iso chain including embedded `FactoryTraceIso30ExternalBodyStateBoundarySmoke`
   - Reason: current evidence-chain baselines are operationally important and mostly lack standalone readable diagram annotation surfaces.
   - Next gate: inventory-preserving GUI review of the current passing/boundary chain, separate from simulation evidence.

### P1: Secondary Review Candidates

4. `Sunray150PlanningOpenBlocksLinearMPCSysblockClosedLoop`, `Sunray150PlanningCorridorGateLinearMPCSysblockClosedLoop`, and related planning wrappers
   - Reason: planning/navigation/control interfaces have about 41 connects each and no static diagram annotations.
   - Next gate: GUI/manual review focused on navigation display, reference, and actual-position wiring.

5. `AWFF_QPNMPCSafetyController_Sysblock`, `AWFF_LinearMPCMultiFaultAllocationController_Sysblock`, `AWFF_LinearMPCOnlineFaultAllocationController_Sysblock`
   - Reason: Sysblock files expose ports and some connect surfaces but no `Line(...)` annotations in the static scan.
   - Next gate: Sysblock graphical open/check and line-layout review; behavior equivalence remains separate R1/controller work.

6. `Models/QuadrotorControllerBlocks/` organization surface
   - Reason: no package file/order file discovered, and backup directories remain next to active `.mo` files.
   - Next gate: static package organization design task before any file edits.

### P2: Preserve/Reference

- `PlannedQuinticReference`, `TraceTableReference`, `TraceInlineReference`, `PlanningNavigationDisplay`: lower-risk support blocks with smaller annotation surfaces.
- `AWFF_InnovationGraphicalControllers`, `AWFF_FullController_Sysblock`, `AWFF_FullControllerFlatGraphical_Sysblock`: use as graphical layout/reference patterns before touching weaker diagrams.

## Next-Step Separation

- Static cleanup only: document package-order embedded-class conventions and design `QuadrotorControllerBlocks` package organization.
- GUI/MCP graphical review: P0/P1 candidates above, with explicit PMO task boundaries.
- Manual screenshot review: only after a Sysplorer GUI/MCP task opens the models.
- R1 simulation evidence: any `check_model`, `simulate_model`, controller performance, Factory trace consumption, or closed-loop claim.

## Non-Claims

This pass does not prove graphical acceptance, line correctness, Sysplorer rendering quality, model check health, simulation success, controller performance, planner readiness, Factory trace consumption, live runtime acknowledgement, or closed loop.
