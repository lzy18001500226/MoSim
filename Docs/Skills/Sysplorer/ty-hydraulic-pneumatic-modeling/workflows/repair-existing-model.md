# Repair Existing Model

## Scope

Use this workflow when the user provides or identifies an existing model and asks to repair connections, parameters, medium selection, check/translate/simulate failures, result behavior, diagram visibility, red dashed wires, dangling endpoints, chaotic routing, or stretched symbols.

## Required Inputs

- Model path, model name, or currently loaded model object.
- Current error, symptom, diagram export, result anomaly, or desired repair target.
- Whether preserving the current topology is required.
- Any known previous working version or benchmark result.

## Execution

1. Start from the parent seven gates and use the Gate 2 requirement additions in `SKILL.md` to normalize the repair target and success criteria.
2. Read `references/error-repair-playbook.md` first.
3. Read `references/common-errors.md` for hydraulic/pneumatic symptom shortcuts.
4. Read `references/validation-rules.md` when the symptom involves results, connections, or diagram quality.
5. Read `references/capacitor-resistive-check.md` when the model uses `TYHydraulics` / `TYHydraulicComponents`, or when symptoms point to fluid capacitance/resistance mismatch.
6. Use MCP/model inspection to identify the concrete model target.
7. Classify the fault: source/input, library/dependency, component mapping, medium, topology, capacitor/resistive topology, parameter, initialization, translation, simulation, result variable, or graphical annotation.
8. Isolate the shortest active failure chain.
9. Repair only what is needed for the failed gate to become meaningful again.
10. For diagram symptoms, check `Placement`, `Line`, `Diagram(coordinateSystem(...))`, connector anchors, and extents before assuming the physical topology is wrong.
11. After repair, rerun the failed gate: capacitor-resistive check, `check_model`, `translate_model`, `simulate_model`, result variable read, or diagram export/review.
12. Continue through the remaining Gate additions in `SKILL.md` until result and diagram acceptance are satisfied or a blocker is documented.

## Failure Handling

- Do not skip from failed `check` to `simulate`.
- Do not treat "model tree has components" as completion when the diagram is invisible.
- Do not perform broad unrelated cleanup before repairing the active failure chain.
- If a required model artifact is missing or inaccessible, stop and state the blocker.

## Delivery Focus

- Failed gate and symptom.
- Root-cause judgment and repair action.
- MCP actions rerun after repair and their results.
- Result variable verification when behavior was part of the request.
- Diagram review conclusion when graphical repair was part of the request.
- Remaining blockers and next executable action if not fully closed.
