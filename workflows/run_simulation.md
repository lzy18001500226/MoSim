# Run Simulation Workflow

> Purpose: run one MWORKS quadrotor simulation through Sysplorer MCP, export results, and prepare data for metrics and figures.

---

## 1. Goal

Run a specified scene and controller, then save raw simulation results for analysis.

Example task:

```text
Run the figure8 scene with pid_baseline and save results to results/official/example3_figure8/official_example3_pid_baseline/raw/official_example3_pid_baseline.csv.
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
experiment_id: official_example3_pid_baseline
scene_id: official_example3
controller_id: pid_baseline
model_name: QuadrotorModel.Examples.Example3
start_time: 0
stop_time: 30
step_size: 0.01

result:
  raw_file: results/official/example3_figure8/official_example3_pid_baseline/raw/official_example3_pid_baseline.csv
  metrics_file: results/official/example3_figure8/official_example3_pid_baseline/metrics/official_example3_pid_baseline.json
  figure_dir: results/official/example3_figure8/official_example3_pid_baseline/figures

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

### Step 0: Confirm the MCP wrapper

Before running a real MWORKS simulation, verify that the wrapper can start the
Sysplorer MCP server from the current shell. The runner auto-detects these
locations:

```text
/home/linux/mcp-wrappers/sysplorer_mcp.sh
~/mcp-wrappers/sysplorer_mcp.sh
~/mcp-wrappers/sysplorer_mcp.bat
~/mcp-wrappers/sysplorer_mcp.cmd
~/mcp-wrappers/sysplorer_mcp.ps1
```

For a non-standard location, use either:

```powershell
$env:SYSPLORER_MCP_WRAPPER="C:\path\to\sysplorer_mcp.cmd"
python scripts\run_mworks_scenario.py scenarios\official\example1_pid_baseline.yaml
```

or pass it per run:

```powershell
python scripts\run_mworks_scenario.py scenarios\official\example1_pid_baseline.yaml --wrapper "C:\path\to\sysplorer_mcp.cmd"
```

If the wrapper directly `exec`s a Windows `python.exe` from WSL and WSL reports
`cannot execute binary file: Exec format error`, the simulation cannot be
launched from the current shell. In that case:

```text
1. Do not label the attempted run as MWORKS evidence.
2. Remove any partial raw/metrics/log directories created by the failed attempt.
3. Keep the scenario inactive with inactive_reason describing the wrapper block.
4. Re-run from a Windows-capable shell or repair the wrapper so WSL can launch it.
```

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
Save error messages into results/{group}/{scene}/{experiment}/logs/ if possible.
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
results/{group}/{scene}/{experiment}/raw/{scene_id}_{controller_id}.csv
```

CSV should include:

```csv
time,x,y,z,vx,vy,vz,roll,pitch,yaw,u1,u2,u3,u4,x_ref,y_ref,z_ref
```

If direct CSV export is unavailable, save the native result file and document the conversion method.

---

### Step 9: Evaluate result quality

Run the quality gate after metrics are available:

```bash
python3 scripts/evaluate_result_quality.py scenarios/official/example3_awff_sysblock.yaml --write-metrics
```

The scenario runner does this automatically unless `--no-quality-gate` is set:

```bash
python3 scripts/run_mworks_scenario.py scenarios/official/example3_awff_sysblock.yaml
```

Interpretation:

```text
quality_status=pass             result can support the stated performance claim
quality_status=smoke_only       chain check only; do not use for full performance
quality_status=needs_iteration  preserve evidence, revise controller/scenario, rerun
```

Execution success is not enough. A result with worse RMSE than its baseline,
failed 8 字形 shape check, excessive error, low health score, or missing duration
must be treated as unfinished even when MWORKS reports no runtime error.

---

### Step 8.1: Reference/Replay Fallback

If MWORKS or Sysplorer MCP is unavailable, do not fabricate simulated states.
Instead, generate only the official reference trajectory and replay scaffold:

```bash
python3 scripts/generate_reference.py --scene all
```

Outputs:

```text
results/official/example1_step/reference_official_example1/raw/reference_official_example1.csv
results/official/example2_helix/reference_official_example2/raw/reference_official_example2.csv
results/official/example3_figure8/reference_official_example3/raw/reference_official_example3.csv
results/official/example1_step/reference_official_example1/replay/reference_official_example1.json
results/official/example2_helix/reference_official_example2/replay/reference_official_example2.json
results/official/example3_figure8/reference_official_example3/replay/reference_official_example3.json
```

These files are valid for P0 trajectory inspection and video/replay pipeline
development. They are not a substitute for controller simulation metrics; once
Sysplorer simulation results are available, export measured `x,y,z` and compute
metrics against the reference columns.

Official scenario configs:

```text
scenarios/official/example1_pid_baseline.yaml  -> QuadrotorModel.Examples.Example1
scenarios/official/example2_pid_baseline.yaml  -> QuadrotorModel.Examples.Example2
scenarios/official/example3_pid_baseline.yaml  -> QuadrotorModel.Examples.Example3
```

Smoke logs may cover only a short interval such as 0-1 s. Full official
baseline metrics require the scenario stop times in `scenarios/official/*.yaml`.

---

## 5. Output Requirements

For every successful simulation, create:

```text
results/{group}/{scene}/{experiment}/raw/{scene_id}_{controller_id}.csv
results/{group}/{scene}/{experiment}/logs/{scene_id}_{controller_id}.log
```

For every reported experiment, later create:

```text
results/{group}/{scene}/{experiment}/metrics/{scene_id}_{controller_id}.json
results/{group}/{scene_id}/figures/{controller_id}/trajectory.png
results/{group}/{scene_id}/figures/{controller_id}/error.png
```

---

## 6. Smoke Test Variant

Use this for fast validation:

```yaml
experiment_id: official_example1_mcp_smoke
scene_id: official_example1
controller_id: pid_baseline
model_name: QuadrotorModel.Examples.Example1
stop_time: 1
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
