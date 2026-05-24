# Build from Scenario

## Scope

Use this workflow when the user asks to build a hydraulic, thermal-hydraulic, pneumatic, or closely related control-system model from natural language, a component list, a table, CSV, or a scenario template.

## Required Inputs

- System type: hydraulic, thermal-hydraulic, pneumatic, or mixed.
- Main components and quantity.
- Medium, source, return/exhaust boundary, actuator/load, control method, and target variables.
- Whether the user requires a real Sysplorer model, a topology/parameter plan only, or a structured report.
- Allowed defaults and values that must remain `to confirm`.

## Execution

1. Follow the parent seven gates, then apply the Gate 2 through Gate 11 additions in `SKILL.md` in order.
2. Read `references/requirement-map.md` to classify task type and system scope.
3. Read `references/component-map.md` before selecting libraries or blocks.
4. Read `references/parameter-rules.md` before setting first-round parameters.
5. Read `references/mcp-modeling-toolkit.md` before real Sysplorer actions.
6. Read `references/diagram-layout-rules.md` and `references/diagram-line-annotation-rules.md` before generating model text or graphical connections.
7. Build the smallest viable source-to-actuator or source-to-load loop first.
8. Write the topology connection table before writing `connect(...)`.
9. Write a zone-based layout table and line-route table before emitting placements or visible connections.
10. Create a user-owned model from scratch unless the user explicitly requests an example-based modification.
11. Place key instances in the diagram as they are created; do not postpone graphical instantiation to an unspecified future cleanup.
12. Ensure key `Placement`, every planned visible `Line(points=...)`, and `Diagram(coordinateSystem(...))` annotations exist.
13. Run `scripts/check_modelica_diagram_layout.ps1 <model.mo> -Json` on the saved model file; if it fails, return to step 9 or 12.
14. Run `scripts/check_modelica_line_annotations.ps1 <model.mo> -Json` on the saved model file; if it fails, return to step 9 or 12.
15. Run `check_model` before translation or simulation.
16. For `TYHydraulics` / `TYHydraulicComponents` models, run or manually apply `references/capacitor-resistive-check.md`; if it changes topology or volume switches, return to the affected parent gate and rerun `check_model`.
17. Run `translate_model` when the active runtime path requires it.
18. Run `simulate_model`, then read target variables with `result_manager`.
19. Verify results with `references/validation-rules.md`.
20. Export or directly review the diagram for actual model-creation tasks.
21. Package delivery with `references/acceptance-checklist.md` and `references/output-contract.md`.

## Failure Handling

- If any gate fails, enter `references/error-repair-playbook.md`.
- Repair the smallest active blocker and return to the failed gate.
- Do not present the model as complete if the graphical layer is not visible/readable.
- Do not output intermediate iteration versions unless the user explicitly asks.

## Delivery Focus

- Final model name/path and actual Sysplorer version.
- Actual TY libraries and medium libraries used.
- Component mapping table and substitution notes.
- Topology connection table.
- Parameter table, assumptions, and `to confirm` items.
- Successful MCP actions: create/load/save/check/translate/simulate/result-read/diagram-export.
- Key result variables and pass/fail/no-reference judgments.
- Diagram review status: visible instances, visible key wires, symbol scaling, routing readability, and annotation checks.
