# Read Results Workflow

> Purpose: read simulation results from Sysplorer output files and convert them into project-standard raw CSV files.

---

## 1. Goal

Use Sysplorer MCP `result_manager` to inspect and read simulation result variables.

---

## 2. Inputs

```text
result_file
required_variables
output_csv
```

Required project variables:

```text
time
x, y, z
x_ref, y_ref, z_ref
roll, pitch, yaw
u1, u2, u3, u4
```

Official model candidate names are maintained in:

```text
docs/index/variable_mapping.md
```

---

## 3. MCP Tools

Use:

```text
result_manager
plot_manager
```

Optional:

```text
get_api_document
resources_retrieval
```

---

## 4. Procedure

1. Open the result file with `result_manager`.
2. List available variables.
3. Query `docs/index/variable_mapping.md` candidate names first.
4. Match model-specific variable names to standard project names.
5. If a candidate is missing, list available variables and update the mapping.
6. Read time series for required variables.
7. Save project-standard CSV under `results/raw/`.
8. Save variable mapping if non-obvious.

---

## 5. Variable Mapping

Create a mapping table if model variable names differ.

Example:

| Standard Name | Model Result Variable |
|---|---|
| `x` | `sensors1_1.PosMea[1]` |
| `y` | `sensors1_1.PosMea[2]` |
| `z` | `sensors1_1.PosMea[3]` |
| `roll` | `sensors1_1.AngleMea[1]` |
| `u1` | `controller3_2.y` |

Save mappings to:

```text
docs/index/api_index.md
```

or:

```text
results/logs/variable_mapping_{experiment_id}.md
```

---

## 6. Output CSV Format

```csv
time,x,y,z,vx,vy,vz,roll,pitch,yaw,u1,u2,u3,u4,x_ref,y_ref,z_ref
```

---

## 7. Validation

Pass if:

```text
output CSV exists
time column exists
position columns exist
reference columns exist
no NaN in core fields
row count > 10
```

---

## 8. Failure Handling

| Failure | Action |
|---|---|
| Result file missing | Re-run simulation |
| Variable missing | List all variables and map names |
| Data unreadable | Export native result and document |
| Time axis missing | Check simulation output settings |
| NaN values | Mark experiment invalid |

---

## 9. Next Step

After raw CSV is generated, run:

```text
workflows/calc_metrics.md
```
