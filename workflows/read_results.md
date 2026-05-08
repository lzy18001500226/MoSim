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
3. Match model-specific variable names to standard project names.
4. Read time series for required variables.
5. Save project-standard CSV under `results/raw/`.
6. Save variable mapping if non-obvious.

---

## 5. Variable Mapping

Create a mapping table if model variable names differ.

Example:

| Standard Name | Model Result Variable |
|---|---|
| `x` | `quadrotor.body.r_0[1]` |
| `y` | `quadrotor.body.r_0[2]` |
| `z` | `quadrotor.body.r_0[3]` |
| `roll` | `quadrotor.attitude.roll` |
| `u1` | `controller.motorCmd[1]` |

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
