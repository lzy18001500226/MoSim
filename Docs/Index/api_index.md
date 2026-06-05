# API and Tool Index

> Quick lookup for MCP tools, project scripts, and common API-related questions.

---

## 1. Sysplorer MCP Tools

| Tool | Main Use | Use When |
|---|---|---|
| `session_manager` | Manage Sysplorer sessions | Start, connect, probe, reconnect, or close Sysplorer |
| `load_library` | Load model libraries | Before opening or simulating model library classes |
| `model_manager` | Manage and inspect models | Open, save, query components, query ports |
| `check_model` | Check model | Before simulation or after structural edits |
| `translate_model` | Translate model | Generate simulation code or intermediate build output |
| `simulate_model` | Run simulation | Execute automatic, independent, or real-time simulation |
| `smart_layout` | Auto layout | After model structure is stable |
| `call_code` | Run scripts | Sysblock automation or Sysplorer scripting |
| `resources_retrieval` | Search resources | Troubleshooting, examples, rules |
| `get_api_document` | Query API docs | Unknown Sysplorer Python API |
| `get_lib_model_document` | Query model docs | Unknown component, port, or parameter |
| `result_manager` | Read results | Open result files, list variables, read time series |
| `plot_manager` | Plot and animate | Visualize variables and animations |

---

## 2. Sysplorer Preferred Sequences

### Model check

```text
session_manager
  → load_library
  → model_manager
  → check_model
```

### Simulation

```text
session_manager
  → load_library
  → model_manager
  → check_model
  → simulate_model
  → result_manager
```

### Result plotting

```text
result_manager
  → plot_manager
```

### API lookup

```text
get_api_document
  → resources_retrieval if still unclear
```

### Sysblock graphical authoring

```text
session_manager
  → model_manager(load/open target)
  → get_api_document / get_lib_model_document when ports or APIs are unclear
  → call_code(mode="run_script") with ModelingPy
  → check_model
  → smart_layout only after structure is stable and when applicable
```

Preferred authoring calls:

```text
NewModel(..., "Sysblock")
OpenModel
AddComponent
ConnectPort
SetModelParamValue
```

Rules:

1. Use `ConnectPort` for Sysblock wiring.
2. Do not use `SetModelText`, Modelica `connect()` equations, or bulk `.mo` text patches as the primary Sysblock topology method.
3. Do not call `ClearAll`, `ChangeDirectory`, or broad workspace-reset APIs.
4. For hybrid models, build/check the Sysblock controller first, then instantiate/connect it from the Modelica physical wrapper.

---

## 3. Syslab MCP Tools

| Tool | Main Use | Use When |
|---|---|---|
| `detect_syslab_toolboxes` | Environment check | Verify Syslab and Julia setup |
| `evaluate_julia_code` | Run Julia snippet | Quick calculation or quick test |
| `run_julia_file` | Run Julia script | Metrics, plotting, batch experiments |
| `restart_julia` | Restart session | Julia state is broken or stale |
| `list_sessions` | List sessions | Debug session state |
| `search_syslab_docs` | Search docs | Unknown Syslab function |
| `read_syslab_doc` | Read doc body | Need full documentation page |
| `map_matlab_functions_to_julia` | MATLAB-to-Julia mapping | Porting MATLAB scripts |
| `read_syslab_skill` | Read Syslab skill docs | Need built-in skill guidance |

---

## 4. Syslab Preferred Sequences

### Environment check

```text
detect_syslab_toolboxes
```

### Quick calculation

```text
evaluate_julia_code
```

---

## 5. Unreal MCP Tools

Configured server names:

```text
mosim-unreal
mosim-epic
```

`mosim-unreal` is MoSim's live UE Editor automation boundary. It should point
to the project-specific MCP wrapper:

```text
Windows Codex App:
Docs/Skills/Unreal/mosim-unreal/wrappers/mosim-unreal.cmd
Docs/Skills/Unreal/mosim-epic/wrappers/mosim-epic.cmd

WSL-only Codex route:
Docs/Skills/Unreal/mosim-unreal/wrappers/mosim-unreal.sh
  -> Docs/Skills/Unreal/mosim-unreal/wrappers/wsl.sh
  -> Docs/Skills/Unreal/mosim-unreal/mcp/server.py
```

Windows Codex App config must not use `wsl.exe`, `\\wsl.localhost`, `/mnt/c`,
or `/home/linux` for MoSim MCP launchers. Current Windows-native project MCP
wrappers also include:

```text
Docs/Skills/Windows-MCP/wrappers/windows-mcp.cmd
Docs/Skills/ROS-MCP/wrappers/ros-mcp.cmd
Docs/Skills/Blender-MCP/wrappers/blender-mcp.cmd
```

`ros-mcp.cmd` starts the MCP process in Windows and connects to ROS through the
configured rosbridge address. The ROS runtime itself still needs to be running
and reachable.

The old open-source Flopperam wrapper is retained only for rollback:

```text
Docs/Skills/Unreal/mosim-unreal/wrappers/legacy_flopperam_wsl.sh
```

Current MoSim-native `mosim-unreal` tools:

| Tool Group | Examples | Use |
|---|---|---|
| Health/context | `ue_health`, `project_context` | Check project files, installed engines, enabled plugins, and listener reachability |
| Listener | `editor_listener_health` | Check WSL reachability of the UE Editor-side listener |
| Local Content | `asset_search`, `list_maps` | Search project-local `.uasset` / `.umap` files without requiring a live editor |
| Live read-only scene | `current_level_summary`, `find_level_actors` | Inspect current level and actors through the editor listener without modifying the map |
| Controlled edit probe | `reversible_actor_probe` | Plan by default, or explicitly execute a temporary spawn/move/delete actor round trip without saving |
| Diagnostics | `editor_log_summary` | Return a bounded, redacted tail of the latest UE project log |
| Scene truth planning | `scene_source_status`, `scene_truth_export_plan` | Audit local scene sources with compact default output and produce truth-export command plans |
| Boundary | `tool_boundary` | Explain the split between UE automation and Epic/Fab inventory |

Current MoSim-native `mosim-epic` tools:

| Tool Group | Examples | Use |
|---|---|---|
| Library inventory | `epic_library_inventory`, `epic_scene_library_view` | Read sanitized Epic/Fab/Launcher scene inventory |
| Scene source | `scene_source_registry`, `scene_truth_export_plan` | Read scene-source contract and plan collision/planning-truth export |
| Acceptance gates | `scene_source_acceptance` | Distinguish inventory visibility from scene import/truth readiness |
| Boundary | `tool_boundary` | Explain the split between UE automation and Epic/Fab inventory |

Important boundary:

```text
mosim-unreal owns live UE project/editor/listener operations.
mosim-epic owns sanitized Epic/Fab/Launcher inventory and scene-source gates.
Neither MCP logs in to Epic, clicks Launcher buttons, downloads Fab assets, or
claims an account-owned asset is editable before it is imported/linked locally.
```

Command-line checks:

```bash
Scripts/UE5/build_unreal_renderer.sh
Scripts/UE5/open_unreal_renderer.sh editor
python3 Docs/Skills/Unreal/mosim-unreal/mcp/server.py dump-tools
python3 Docs/Skills/Unreal/mosim-unreal/mcp/server.py dump-context
python3 Docs/Skills/Unreal/mosim-unreal/mcp/server.py dump-assets --limit 5
python3 Docs/Skills/Unreal/mosim-unreal/mcp/server.py dump-maps --limit 5
python3 Docs/Skills/Unreal/mosim-unreal/mcp/server.py dump-level --timeout 0.5 --limit 5
python3 Docs/Skills/Unreal/mosim-unreal/mcp/server.py dump-reversible-probe
python3 Docs/Skills/Unreal/mosim-unreal/mcp/server.py dump-scene-sources --limit 1 --map-limit 2
python3 Docs/Skills/Unreal/mosim-unreal/mcp/server.py dump-log --lines 20
python3 Docs/Skills/Unreal/mosim-unreal/mcp/server.py dump-boundary
python3 Docs/Skills/Unreal/mosim-epic/mcp/server.py dump-tools
python3 Docs/Skills/Unreal/mosim-epic/mcp/server.py dump-boundary
python3 Scripts/UE5/check_epic_library_inventory.py --json
```

Current renderer engine association is UE `5.5`. UE 4.27 local scene projects
use `UE4Editor.exe` / `UE4Editor-Cmd.exe`, not the UE5 executable names.

Before write operations, prove an editor-side listener and map source first.
Avoid switching back to broad generic scene-generation tools to bypass
import/editability/truth acceptance gates.

### Script execution

```text
detect_syslab_toolboxes
  → run_julia_file
```

### Documentation lookup

```text
search_syslab_docs
  → read_syslab_doc
```

### MATLAB code migration

```text
map_matlab_functions_to_julia
  → search_syslab_docs
  → read_syslab_doc
```

---

## 5. Project Scripts

| Script | Purpose | Expected Input | Expected Output |
|---|---|---|---|
| `Scripts/quality/qa_check.py` | Project quality check | project root | pass/fail report |
| `Scripts/docs/scan_mworks_docs.py` | Scan a local MWORKS resource package with PDF preview review | optional `--source` directory | `Docs/MworksDocs/scan/` indexes |
| `Scripts/docs/convert_mworks_pdfs.py` | Convert selected PDFs via MinerU or PyMuPDF fallback | selected local PDFs | `Docs/MworksDocs/converted/` Markdown and `_images/` directories |
| `Scripts/results/calc_metrics.jl` | Compute standard tracking/control metrics | `Results/{group}/{scene}/{experiment}/raw/*.csv` | `Results/{group}/{scene}/{experiment}/metrics/*.json` and `.csv` |
| `Scripts/results/evaluate_result_quality.py` | Decide whether a completed scenario passes, is smoke-only, or needs iteration | scenario YAML and existing metrics/raw files | `quality_status` fields written into metrics JSON |
| `Scripts/results/plot_results.jl` | Write figure manifest for report assets | raw CSV and figure dir | `figure_manifest.md` |

## 6. MinerU Precise Parsing API

| Item | Value |
|---|---|
| Reference | `Docs/MinerU/mineru_precise_api.md` |
| Token variable | `MINERU_API_TOKEN` |
| Single URL task | `POST https://mineru.net/api/v4/extract/task` |
| Single result query | `GET https://mineru.net/api/v4/extract/task/{task_id}` |
| Local batch upload URLs | `POST https://mineru.net/api/v4/file-urls/batch` |
| URL batch task | `POST https://mineru.net/api/v4/extract/task/batch` |
| Batch result query | `GET https://mineru.net/api/v4/extract-Results/batch/{batch_id}` |
| Models | `pipeline`, `vlm`, `MinerU-HTML` |

Rules:

1. Never write the real Token into tracked files.
2. Use `MINERU_API_TOKEN` from the environment.
3. Use `vlm` for high-fidelity PDF/PPT/DOC parsing.
4. Use `MinerU-HTML` only for HTML input.
5. Store converted outputs under `Docs/MworksDocs/converted/` and update `Docs/MworksDocs/converted/转换索引.md`.

---

## 7. Common API Questions

### How to check a model?

Use:

```text
check_model
```

Before that, ensure:

```text
session_manager
load_library
model_manager
```

have already been used.

---

### How to run a simulation?

Use:

```text
simulate_model
```

Required before simulation:

```text
check_model succeeds
model is open
libraries are loaded
scenario parameters are set
```

---

### How to read result variables?

Use:

```text
result_manager
```

Required variables for this project:

```text
time
x, y, z
x_ref, y_ref, z_ref
roll, pitch, yaw
u1, u2, u3, u4
```

---

### How to plot results?

Use either:

```text
plot_manager
```

or future local scripts:

```text
Syslab run_julia_file Scripts/results/plot_results.jl
```

Prefer Syslab script plots for report figures when a result CSV is available.

---

### How to compute RMSE?

Use:

```text
Syslab run_julia_file Scripts/results/calc_metrics.jl
```

`Scripts/results/calc_metrics.jl` is implemented. Use `--help` to inspect the accepted CSV schema and `--self-test` for a quick local verification.

Formula:

```text
RMSE_p = sqrt(mean(||p - p_ref||^2))
```

---

### How to debug missing variables?

Use:

```text
result_manager list variables
```

Then create a mapping from model-specific variable names to standard project names.

---

### How to create or extend a Sysblock controller?

Known API evidence:

```text
OpenModelFile
CheckModel
TranslateModel
SimulateModel
GetComponents
SetParamValue
SetModelText
ExportDiagram
```

Current project rule:

1. Prefer official MWORKS.Sysblock GUI/API generated models for new block diagrams.
2. Use `call_code(mode="run_script")` / ModelingPy with `NewModel(..., "Sysblock")`, `AddComponent`, `ConnectPort`, and `SetModelParamValue` for scripted topology.
3. Treat hand-written Sysblock `.mo` only as a diagnostic sketch or metadata/display repair input. It is not accepted as graphical Sysblock evidence until Sysplorer opens it with visible blocks/wires and `check_model` passes.
4. Store successful check/simulation evidence under `Results/{group}/{scene}/{experiment}/logs/`.
5. Store failed check diagnostics under `Results/{group}/{scene}/{experiment}/logs/` or a preserved MCP log.

---

## 8. API Usage Rules

1. Do not guess API names.
2. Use `get_api_document` for Sysplorer API.
3. Use `search_syslab_docs` for Syslab functions.
4. Save useful mappings in this file.
5. If a tool call works, document the exact successful pattern in `Docs/Workflows/`.
6. If a tool call fails repeatedly, save the error and fallback method.

---

## 9. Blender MCP

Local MCP source:

```text
Docs/Skills/Blender-MCP
```

Wrapper:

```bash
Docs/Skills/Blender-MCP/wrappers/blender-mcp.sh
```

Codex server name:

```text
blender
```

Primary use:

```text
Blender asset inspection, material assignment, DAE/FBX/glTF conversion, and
Sunray150 visual asset preparation before UE import.
```

Details and repair steps live in:

```text
Docs/Workflows/debug_mcp.md#11-blender-mcp
```
