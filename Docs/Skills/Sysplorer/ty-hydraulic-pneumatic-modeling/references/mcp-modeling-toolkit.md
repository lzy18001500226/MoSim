# MCP Modeling Toolkit

Use MCP / Sysplorer official capabilities for platform actions. Use this skill for domain decisions.

| Stage | Preferred MCP Tool | Notes |
|---|---|---|
| Session and version | `session_manager` | Use `action="ensure"` before real model work. Use health/version information in delivery when available. |
| Library loading | `load_library` | Load only required TY libraries and required dependencies. Built-in Modelica version follows Sysplorer defaults. |
| Model lifecycle | `model_manager` | Create, load, save, open, inspect text, inspect components, query ports, and export diagrams. |
| API help | `get_api_document`, `get_lib_model_document` | Use for Sysplorer API or class details when local references are insufficient. |
| Scripted modeling | `call_code(mode="run_script")` | Use only with explicit imports such as `import mworks.sysplorer as ModelingPy`. Do not call `ClearAll` or `ChangeDirectory`. |
| Smart layout / writeback | `smart_layout` | Use when automatic placement or line annotations need to be computed or patched into `.mo`. |
| Diagram layout preflight | `scripts/check_modelica_diagram_layout.ps1` | Run on the saved `.mo` before `check_model`; failure means Step 5 layout is not complete. |
| Line annotation preflight | `scripts/check_modelica_line_annotations.ps1` | Run on the saved `.mo` before `check_model`; failure means Step 5 is not complete. |
| Model check | `check_model` | Must pass before translate/simulate. Use reload options when checking a modified `.mo`. |
| Translation | `translate_model` | Use when the workflow or runtime path needs generated simulation code before simulation. |
| Simulation | `simulate_model` | Use after check and required translation. Verify at least one target variable when possible. |
| Results | `result_manager` | Use targeted variable queries before broad result listing. Read variable info and values before judging behavior. |
| Plotting / animation | `plot_manager` | Use for curves or animation when the user requests visual result artifacts. |
| Local reference search | `resources_retrieval` | Use for indexed reference corpora when available; otherwise use file reads or `scripts/search_manual_text.ps1`. |

## Safety Rules

- Do not use Sysplorer `ClearAll` or `ChangeDirectory`.
- Do not claim downstream stages after MCP session failure.
- Do not infer success from source text alone; use the relevant MCP result.
- When a generated model is written to disk, reload or check the exact file/model that will be delivered.

## Stage-to-Tool Pattern

1. `session_manager(action="ensure")`
2. `load_library` for `TYHydraulics` / `TYThermalHydraulics` / `TYPneumatics` and medium libraries as needed
3. `model_manager(action="new" | "load_file")`
4. `call_code(mode="run_script")` or modeling APIs for components, connections, parameters, and annotations
5. Ensure zone-based `Placement` follows `references/diagram-layout-rules.md`
6. Ensure every planned visible `connect(...)` has `annotation(Line(points=...))`; use `references/diagram-line-annotation-rules.md` as the pattern
7. Run `scripts/check_modelica_diagram_layout.ps1 <model.mo> -Json`
8. Run `scripts/check_modelica_line_annotations.ps1 <model.mo> -Json`
9. `smart_layout` if diagram annotations need repair or writeback
10. Re-run both preflight scripts after writeback
11. `check_model`
12. `translate_model` when required
13. `simulate_model`
14. `result_manager` for target variables
15. `model_manager(action="export_model_diagram")` for diagram review when required
