# Execution Standards

This file defines hard execution standards for TY hydraulic, thermal-hydraulic, and pneumatic Sysplorer tasks.

## Hard Gates

1. Source material must be readable before requirement understanding.
2. Requirement understanding must define task type, system type, objective, success criteria, and unresolved items before component mapping.
3. Component mapping must identify TY library family, medium, boundaries, main loop, control chain, and sensors before parameter completion.
4. Parameter completion must expose assumptions and units before model construction or repair.
5. Model construction or repair must produce a concrete model target before `check_model`.
6. `check_model` must pass before translation or simulation.
7. Translation failures must be repaired before simulation when translation is required by the workflow.
8. Simulation results must be verified against user objectives before delivery.
9. Actual model creation and diagram repair tasks must pass graphical review before being called complete.
10. Any failed gate must enter the repair loop and return to the failed gate after repair.

## Non-Negotiable Domain Rules

- Use built-in TY system libraries for system assembly unless the user asks for component-level design.
- Select `TYHydraulics`, `TYThermalHydraulics`, or `TYPneumatics` according to fluid domain before choosing component models.
- Select `TYOilMedia` for hydraulic and thermal-hydraulic media and `TYGasMedia` for pneumatic media unless the user provides a specific compatible medium.
- Do not silently assume 4/3 valve center type, single-acting actuator return mode, pump type when performance matters, thermal boundary conditions, or pneumatic exhaust boundary.
- Do not deliver an official example, wrapper, or `extends` chain as the user-owned model unless requested.
- State every equivalent component substitution with reason and risk.

## Graphical Completion Rules

- Key instances must be placed in the diagram with `annotation(Placement(...))`.
- Key instances must follow a zone-based layout with no overlaps, no crowding, and no out-of-bounds placements.
- For model-creation tasks, every planned visible `connect(...)` must include `annotation(Line(points=...))`.
- The model must include `Diagram(coordinateSystem(...))`.
- Diagram review must verify visible instance count, visible key connection count, symbol scaling, routing readability, and absence of major stretching or red dashed dangling wires.
- If the diagram does not display the created model normally, the model-creation task is incomplete even if the model tree, source text, check, or simulation succeeded.

## Reporting Rules

- Separate executed facts from assumptions.
- Report exact tool actions that succeeded in the current session.
- Report unresolved items as `to confirm` / `待确认`.
- Do not output intermediate iteration versions unless the user explicitly requests them.
- If a gate cannot be passed, state the blocker and the next executable action instead of claiming completion.
