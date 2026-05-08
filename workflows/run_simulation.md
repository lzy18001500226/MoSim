# Run Simulation Workflow

> Purpose: run one MWORKS quadrotor simulation through Sysplorer MCP, export results, and prepare data for metrics and figures.

---

## 1. Goal

Run a specified scene and controller, then save raw simulation results for analysis.

Example task:

```text
Run the figure8 scene with pid_baseline and save results to results/raw/figure8_pid_baseline.csv.
```

---

## 2. Inputs

Required inputs:

```text
scene_id
controller_id
model_path or model_name
simulation_start_time
simulation_stop_time
result_output_path
```

Optional inputs:

```text
disturbance_config
trajectory_file
controller_params_file
result_variables
```

Recommended config format:

```yaml
experiment_id: figure8_pid_baseline_001
scene_id: figure8
controller_id: pid_baseline
model_name: Quadrotor.Examples.Figure8_PID
start_time: 0
stop_time: 30
step_size: 0.01

result:
  raw_file: results/raw/figure8_pid_baseline.csv
  metrics_file: results/metrics/figure8_pid_baseline.json
  figure_dir: results/figures/figure8_pid_baseline/

variables:
  - time
  - x
  - y
  - z
  - vx
  - vy
  - vz
  - roll
  - pitch
  - yaw
  - u1
  - u2
  - u3
  - u4
  - x_ref
  - y_ref
  - z_ref
```

---

## 3. Required MCP Tools

Use Sysplorer MCP tools in this order:

```text
session_manager
  → load_library
  → model_manager
  → check_model
  → simulate_model
  → result_manager
```

Optional tools:

```text
plot_manager
get_api_document
get_lib_model_document
resources_retrieval
```

---

## 4. Procedure

### Step 1: Check MCP status

Run `/mcp` in Codex.

Success criteria:

```text
sysplorer_mcp Tools include:
session_manager
load_library
model_manager
check_model
simulate_model
result_manager
```

If tools are not listed, follow `workflows/debug_mcp.md`.

---

### Step 2: Connect to Sysplorer

Use `session_manager`.

Recommended action:

```text
Probe existing Sysplorer session.
If no session exists, start or connect to Sysplorer.
```

Expected output:

```text
session connected
platform label visible
Sysplorer version available
```

---

### Step 3: Load required libraries

Use `load_library`.

Load:

```text
Modelica Standard Library
MWORKS quadrotor model library
project custom controller library
```

If library loading fails:

1. Check model path.
2. Search `resources_retrieval`.
3. Query API with `get_api_document`.
4. Do not continue simulation before library loading succeeds.

---

### Step 4: Open target model

Use `model_manager`.

Tasks:

```text
open model
inspect model components
verify controller component exists
verify input/output ports exist
```

Required checks:

```text
quadrotor body component exists
controller component exists
motor/electric drive component exists
sensor component exists
trajectory/reference input exists
```

---

### Step 5: Check model

Use `check_model`.

Rules:

```text
Always run check_model before simulate_model.
Do not run simulation if check_model fails.
Save error messages into results/logs/ if possible.
```

Success criteria:

```text
model instantiation succeeds
no blocking compile errors
required variables can be generated
```

---

### Step 6: Run simulation

Use `simulate_model`.

Recommended simulation parameters:

```text
start_time = 0
stop_time = scenario-defined
step_size = scenario-defined
solver = default unless project specifies otherwise
```

Required outputs:

```text
result file path
simulation status
runtime logs
```

If simulation fails:

1. Save error message.
2. Check model again.
3. Reduce scenario complexity.
4. Run a short hover smoke test.
5. Do not fabricate results.

---

### Step 7: Read result variables

Use `result_manager`.

Required variables:

```text
time
x, y, z
x_ref, y_ref, z_ref
roll, pitch, yaw
u1, u2, u3, u4
```

Optional variables:

```text
vx, vy, vz
p, q, r
thrust
torque_x, torque_y, torque_z
disturbance_hat_x, disturbance_hat_y, disturbance_hat_z
motor_efficiency
formation_error
min_obstacle_distance
```

If a variable is missing:

1. Use `result_manager` to list available variables.
2. Map model variable names to standard result fields.
3. Update `docs/index/api_index.md` if a useful mapping is found.

---

### Step 8: Export raw results

Save to:

```text
results/raw/{scene_id}_{controller_id}.csv
```

CSV should include:

```csv
time,x,y,z,vx,vy,vz,roll,pitch,yaw,u1,u2,u3,u4,x_ref,y_ref,z_ref
```

If direct CSV export is unavailable, save the native result file and document the conversion method.

---

## 5. Output Requirements

For every successful simulation, create:

```text
results/raw/{scene_id}_{controller_id}.csv
results/logs/{scene_id}_{controller_id}.log
```

For every reported experiment, later create:

```text
results/metrics/{scene_id}_{controller_id}.json
results/figures/{scene_id}_{controller_id}_trajectory.png
results/figures/{scene_id}_{controller_id}_error.png
```

---

## 6. Smoke Test Variant

Use this for fast validation:

```yaml
experiment_id: hover_pid_smoke
scene_id: hover
controller_id: pid_baseline
stop_time: 3
step_size: 0.01
```

Pass conditions:

```text
simulation finishes
result file exists
time exists
x/y/z exist
no NaN values
z remains non-negative
motor commands are not all zero
```

---

## 7. Failure Handling

| Failure | Action |
|---|---|
| MCP tools missing | Follow `workflows/debug_mcp.md` |
| session_manager fails | Restart Sysplorer and retry |
| load_library fails | Check library path and model installation |
| check_model fails | Fix model before simulation |
| simulate_model fails | Run smoke test and inspect logs |
| result variable missing | Use result_manager to list variables |
| output file missing | Save native result and document path |

---

## 8. Report Notes

When using simulation results in the report, record:

```text
scene_id
controller_id
model version
simulation time
step size
disturbance parameters
controller parameters
result file path
metrics file path
figure path
```

Never make performance claims without metrics or figures.
