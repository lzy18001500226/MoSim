# MWORKS R2 Static GUI Review Prep Checklist

Request: `RFLY-MOSIM-MWORKS-R2-STATIC-GUI-REVIEW-PREP-20260606-003`

Selected P0 family: `FactoryTrace Iso chain`

This checklist is static preparation for a later GUI/manual review. It is not a GUI/MCP pass, Smart Layout output, `check_model` evidence, simulation evidence, Factory trace consumption evidence, controller performance evidence, planner readiness, live runtime acknowledgement, plant tracking, or closed-loop evidence.

## Window Policy

- Use `mworks_window_policy=reuse_existing_do_not_close`.
- R2 static tasks must not open, close, restart, or otherwise touch MWORKS/Sysplorer/Syslab windows.
- A later approved GUI review should reuse the existing user-opened, logged-in, activated MWORKS/Sysplorer session when possible.
- Close/restart/new-window actions require explicit PMO/user approval or documented evidence of freeze, login/license blocker, crash dialog, duplicate-window runaway, or failed MCP recovery.
- If a GUI crash, error-report, login, or license popup appears in a future GUI task, capture evidence and return a blocker. Do not click close, restart, send report, or continue solver/model trial-and-error.

## Review Boundary

- Review exactly this family: FactoryTrace Iso chain.
- Do not broaden to `FormationTriangleFigure8LinearMPCSysblockClosedLoop` or the full `Sunray150UEFactoryTraceTableLinearMPCSysblockSmoke` wrapper in the same GUI review.
- Use FactoryLite only as context for inherited trace/display wiring.
- Treat Iso24 as a known failed direct-attitude-feedback boundary context, not as a passing model.
- Treat Iso30 as an embedded class in `Models/QuadrotorExperiments/package.mo`; lack of a sibling `.mo` file is not a missing-model defect by itself.

## Suggested Open Order For Later Approved GUI Review

1. `QuadrotorExperiments.FactoryLiteTraceSmoke` - context only.
2. `QuadrotorExperiments.FactoryTraceIso23PositionSampleHoldBridgeSmoke`.
3. `QuadrotorExperiments.FactoryTraceIso24DirectAttitudeFeedbackSmoke` - known direct-feedback boundary context.
4. `QuadrotorExperiments.FactoryTraceIso25SampleHoldAttitudeFeedbackSmoke`.
5. `QuadrotorExperiments.FactoryTraceIso26ControllerOutputAliasSmoke`.
6. `QuadrotorExperiments.FactoryTraceIso27ActuatorInputAliasSmoke`.
7. `QuadrotorExperiments.FactoryTraceIso28ActuatorToWrenchBridgeSmoke`.
8. `QuadrotorExperiments.FactoryTraceIso29ExternalFrameWrenchBoundarySmoke`.
9. `QuadrotorExperiments.FactoryTraceIso30ExternalBodyStateBoundarySmoke` embedded in `Models/QuadrotorExperiments/package.mo`.

## Per-Model Checklist

### FactoryLiteTraceSmoke

- Confirm `TraceInlineReference` and `PlanningNavigationDisplay` are visually distinguishable.
- Confirm reference position and actual position/display paths are not hidden behind ambiguous inherited text.
- Confirm trace/reference aliases are label-readable enough for manual screenshots.
- Escalate to R1 for any trace consumption, `check_model`, simulation, or variable-read claim.

### FactoryTraceIso23PositionSampleHoldBridgeSmoke

- Confirm the sampled/held display-position bridge is visually separable from direct `sensors1_1.PosMea` wiring.
- Confirm `navigationDisplay.actual_position` bridge intent is visible, not just implied by equations.
- Check for wire crossing, overlong routing, unlabeled hold/sampler blocks, or hidden inherited feedback loops.
- Confirm no diagram impression suggests full Factory wrapper or closed loop.

### FactoryTraceIso24DirectAttitudeFeedbackSmoke

- Mark this as known boundary context: direct `sensors1_1.AngleMea[1..3]` attitude feedback produced empty result context in prior evidence.
- Confirm any later GUI review labels it as rejected/direct boundary context, not a passing bridge.
- Check whether direct attitude-feedback source/modification text is visually obvious enough to explain the boundary.
- Escalate any proposed fix to a separate R1/R2 scoped task; do not repair in the GUI review.

### FactoryTraceIso25SampleHoldAttitudeFeedbackSmoke

- Confirm sampled/held attitude-feedback bridge is visually separated from direct `AngleMea` wiring.
- Confirm roll, pitch, and yaw measurement paths are labeled clearly.
- Check for sign/coordinate ambiguity in labels; do not infer correctness from static layout.
- Confirm Iso23 display bridge remains readable in the same diagram context.

### FactoryTraceIso26ControllerOutputAliasSmoke

- Confirm controller output aliases are visually or textually grouped as read-only probes.
- Confirm `controller3_2` outputs and pre-actuator command aliases are not presented as actuator/flange closure.
- Check whether alias labels distinguish controller output, delta scale, and hover sum stages.
- Escalate any controller performance or behavior-equivalence question to R1.

### FactoryTraceIso27ActuatorInputAliasSmoke

- Confirm actuator input aliases are shown as probe/consistency surfaces only.
- Confirm alias route does not visually imply actuator flange, speedSensor, chassis, or full plant closure.
- Check if per-motor labels `actuator1_1.u` through `actuator1_4.u` are readable in screenshots.
- Escalate any actuator dynamics claim to a separately scoped R1 evidence task.

### FactoryTraceIso28ActuatorToWrenchBridgeSmoke

- Confirm the sidecar actuator-input to physical-wrench adapter command surface is visually separated from full plant/QuadChassis paths.
- Confirm any `Sunray150PhysicalWrenchFrameAdapter` or equivalent adapter block is readable as project-owned bridge evidence.
- Check force/torque command labels and adapter gate/error aliases for screenshot clarity.
- Do not accept layout that visually hides the adapter behind inherited or collapsed topology.

### FactoryTraceIso29ExternalFrameWrenchBoundarySmoke

- Confirm the external MultiBody frame/test-body boundary is visible as the single next boundary.
- Confirm force/torque entry into the explicit external test body is visually distinguishable.
- Check for missing-class/red-block indicators, broken connectors, unreadable frame connector placement, or line crossings around the external frame.
- Escalate any physical body response or yaw transient claim to R1.

### FactoryTraceIso30ExternalBodyStateBoundarySmoke

- Confirm the class opens from the package surface even though there is no sibling `.mo` file.
- Confirm external body state and motion response aliases are visible and grouped as read-only boundary probes.
- Confirm embedded-package location does not make the diagram hard to find or review manually.
- Escalate any request to split the embedded class into its own `.mo` file as a separate package-organization write task.

## Screenshot Expectations For Later GUI Task

- Capture one overview screenshot per selected model opened in the approved GUI task.
- Capture close-up screenshots for trace/display bridge, attitude bridge, controller output aliases, actuator input aliases, wrench adapter, and external frame/body boundary.
- Each screenshot set should include a short manual note: red/missing components, unreadable ports, crossing/overlong lines, ambiguous inherited modifications, and whether screenshot evidence is sufficient for a later cleanup task.

## Static Cleanup Candidates, Not For This Task

- Add or repair graphical annotations only under a separately approved write-scope task.
- Consider documenting the embedded-class convention for `QuadrotorExperiments/package.mo` before treating package-order entries as missing files.
- Consider a separate `QuadrotorControllerBlocks` package-organization design task; do not mix it with FactoryTrace Iso GUI review.

## Non-Claims

- No MWORKS/Sysplorer/Syslab GUI was opened by this task.
- No MCP call was made by this task.
- No Smart Layout was run.
- No `.mo`, `package.order`, script, Reference, or CoAgent runtime file was modified.
- No graphical pass, `check_model`, simulation success, Factory trace consumption, controller performance, planner readiness, live runtime acknowledgement, plant tracking, parameter identification, mission success, or closed-loop claim is made.
