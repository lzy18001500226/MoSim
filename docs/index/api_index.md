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
| `scripts/qa_check.py` | Project quality check | project root | pass/fail report |
| `scripts/scan_mworks_docs.py` | Scan local MWORKS resource package with PDF preview review | `references/MWORKS高校星火计划资料包` | `docs/mworks/scan/` indexes |
| `scripts/convert_mworks_pdfs.py` | Convert selected PDFs via MinerU or PyMuPDF fallback | selected local PDFs | `docs/mworks/converted/` Markdown and `_images/` directories |
| `scripts/calc_metrics.jl` | Compute standard tracking/control metrics | `results/raw/*.csv` | `results/metrics/*.json` and `.csv` |
| `scripts/plot_results.jl` | Write figure manifest for report assets | raw CSV and figure dir | `figure_manifest.md` |

## 6. MinerU Precise Parsing API

| Item | Value |
|---|---|
| Reference | `docs/mworks/mcp/mineru_precise_api.md` |
| Token variable | `MINERU_API_TOKEN` |
| Single URL task | `POST https://mineru.net/api/v4/extract/task` |
| Single result query | `GET https://mineru.net/api/v4/extract/task/{task_id}` |
| Local batch upload URLs | `POST https://mineru.net/api/v4/file-urls/batch` |
| URL batch task | `POST https://mineru.net/api/v4/extract/task/batch` |
| Batch result query | `GET https://mineru.net/api/v4/extract-results/batch/{batch_id}` |
| Models | `pipeline`, `vlm`, `MinerU-HTML` |

Rules:

1. Never write the real Token into tracked files.
2. Use `MINERU_API_TOKEN` from the environment.
3. Use `vlm` for high-fidelity PDF/PPT/DOC parsing.
4. Use `MinerU-HTML` only for HTML input.
5. Store converted outputs under `docs/mworks/converted/` and update `docs/mworks/converted/转换索引.md`.

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
Syslab run_julia_file scripts/plot_results.jl
```

Prefer Syslab script plots for report figures when a result CSV is available.

---

### How to compute RMSE?

Use:

```text
Syslab run_julia_file scripts/calc_metrics.jl
```

`scripts/calc_metrics.jl` is implemented. Use `--help` to inspect the accepted CSV schema and `--self-test` for a quick local verification.

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

## 7. API Usage Rules

1. Do not guess API names.
2. Use `get_api_document` for Sysplorer API.
3. Use `search_syslab_docs` for Syslab functions.
4. Save useful mappings in this file.
5. If a tool call works, document the exact successful pattern in `workflows/`.
6. If a tool call fails repeatedly, save the error and fallback method.
