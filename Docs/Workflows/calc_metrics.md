# Calculate Metrics Workflow

> Purpose: compute quantitative metrics from simulation results using Syslab MCP or local scripts.

---

## 1. Goal

Given a raw simulation result file, compute tracking, robustness, safety, planning, and formation metrics.

Example task:

```text
Compute RMSE, max error, settling time, control energy, and saturation ratio for Results/official/example3_figure8/official_example3_pid_baseline/raw/official_example3_pid_baseline.csv.
```

---

## 2. Inputs

Required:

```text
raw_result_file
scene_id
controller_id
metrics_output_file
```

Optional:

```text
reference_trajectory_file
scenario_config_file
obstacle_config_file
formation_config_file
baseline_metrics_file
```

Recommended input format:

```yaml
metrics_job:
  raw_file: Results/official/example3_figure8/official_example3_nmpc_indi_l1/raw/official_example3_nmpc_indi_l1.csv
  scene_id: official_example3
  controller_id: nmpc_indi_l1
  output_file: Results/official/example3_figure8/official_example3_nmpc_indi_l1/metrics/official_example3_nmpc_indi_l1.json
  figure_dir: Results/official/example3_figure8/official_example3_nmpc_indi_l1/figures
```

---

## 3. Required Tools

Use Syslab MCP:

```text
detect_syslab_toolboxes
evaluate_julia_code
run_julia_file
search_syslab_docs
read_syslab_doc
```

Use local scripts:

```text
Scripts/results/calc_metrics.jl
Scripts/results/calc_metrics.py
Scripts/results/plot_results.jl
```

Prefer `Scripts/results/calc_metrics.jl` when Syslab/Julia is available. If local WSL
does not provide `julia`, use `Scripts/results/calc_metrics.py` as the fallback so the
automation can still produce `Results/{group}/{scene}/{experiment}/metrics/*.json` and `*.csv`.

---

## 4. Seven-Scenario Contract

For the controlled seven-scenario A/B matrix, use the frozen configuration at
`Config/control_platform/seven_scenario_injection_contract.json` and its
versioned profiles. The implementation is in `Scripts/results/calc_metrics.jl`,
`Scripts/results/calc_metrics.py`, and
`Scripts/syslab/compare_controllers.jl`. Self-checks are:

`julia Scripts/results/calc_metrics.jl --self-test`

`julia Scripts/syslab/compare_controllers.jl --self-test`

The step response uses signed X/Y overshoot, a persistent plus-or-minus 5
percent settling band after 15 s, and 40-45 s steady-state position error.
The wind case uses a 0.25 N world-frame lateral force. The plant mismatch is
plus 20 percent mass and diagonal inertia while controller parameters remain
nominal. Rotor 1 changes to 50 percent thrust and reaction-moment
effectiveness at 15 s.

The scripts and their deterministic fixtures are ready, but no seven-scenario
MWORKS result CSV exists yet. Do not present the self-tests as controller
performance evidence.

---

## 5. Standard Metrics

### 5.1 Tracking Metrics

Position error:

```text
e_p(t) = ||p(t) - p_ref(t)||
```

Position RMSE:

```text
RMSE_p = sqrt(mean(e_p(t)^2))
```

Axis RMSE:

```text
RMSE_x = sqrt(mean((x - x_ref)^2))
RMSE_y = sqrt(mean((y - y_ref)^2))
RMSE_z = sqrt(mean((z - z_ref)^2))
```

Maximum error:

```text
E_max = max(e_p(t))
```

Steady-state error:

```text
E_ss = mean(e_p(t) over final time window)
```

---

### 5.2 Step Response Metrics

Overshoot:

```text
Overshoot = (max(response) - target) / abs(target - initial) * 100%
```

Settling time:

```text
First time after which error remains within tolerance band.
```

Default tolerance:

```text
5% of step amplitude
```

---

### 5.3 Attitude Metrics

```text
roll_rmse
pitch_rmse
yaw_rmse
max_tilt_angle
max_angular_rate
```

Tilt angle:

```text
tilt = sqrt(roll^2 + pitch^2)
```

---

### 5.4 Robustness Metrics

Disturbance recovery time:

```text
time after disturbance until position error returns below threshold
```

Performance degradation:

```text
degradation = RMSE_disturbed / RMSE_nominal
```

Improvement over baseline:

```text
improvement = (metric_baseline - metric_proposed) / metric_baseline
```

---

### 5.5 Control Effort Metrics

Control energy:

```text
E_u = integral(||u(t)||^2 dt)
```

Control smoothness:

```text
E_du = integral(||du/dt||^2 dt)
```

Motor saturation ratio:

```text
saturation_ratio = saturated_samples / total_samples
```

---

### 5.6 Safety Metrics

```text
constraint_violation_count
max_constraint_violation
minimum_altitude
minimum_obstacle_distance
minimum_inter_uav_distance
collision_count
```

---

### 5.7 Planning Metrics

```text
planning_success
planning_time
path_length
trajectory_length
minimum_obstacle_distance
jerk_integral
dynamic_violation_count
```

---

### 5.8 Formation Metrics

Formation error:

```text
e_form_i = ||(p_i - p_leader) - offset_i||
```

Metrics:

```text
formation_error_rmse
formation_error_max
minimum_inter_uav_distance
formation_keeping_rate
formation_recovery_time
```

---

## 6. Procedure

### Step 1: Check Syslab MCP

Use `detect_syslab_toolboxes`.

Success criteria:

```text
Syslab environment is detected
Julia session is available
required packages can be listed
```

---

### Step 2: Load raw result file

Use either:

```text
evaluate_julia_code
```

or, after the script is implemented:

```text
run_julia_file Scripts/results/calc_metrics.jl
```

Required fields:

```text
time
x
y
z
x_ref
y_ref
z_ref
```

If required fields are missing:

1. Inspect available columns.
2. Map model variable names to standard field names.
3. Update the raw export workflow.

---

### Step 3: Compute metrics

Current status:

```text
Scripts/results/calc_metrics.jl has a minimal implemented version.
```

Run:

```text
Scripts/results/calc_metrics.jl
```

Recommended command via Syslab MCP:

```text
run_julia_file with script_path = absolute path to Scripts/results/calc_metrics.jl
```

Script should save:

```text
Results/{group}/{scene}/{experiment}/metrics/{scene_id}_{controller_id}.json
Results/{group}/{scene}/{experiment}/metrics/{scene_id}_{controller_id}.csv
```

---

### Step 4: Generate figures

Current status:

```text
Scripts/results/plot_results.jl has a minimal manifest-writing version.
```

For publication-quality images, generate figures with Syslab plotting APIs or `plot_manager`; use the script to keep a stable output contract and figure manifest. Run:

```text
Scripts/results/plot_results.jl
```

Save figures to:

```text
Results/{group}/{scene_id}/figures/{controller_id}/
Docs/figures/
```

Recommended figures:

```text
3D trajectory
position error vs time
axis error vs time
attitude error vs time
control input vs time
metrics bar chart
```

---

### Step 5: Compare with baseline

If baseline exists:

```text
Results/{group}/{scene}/{experiment}/metrics/{scene_id}_pid_baseline.json
```

Compute:

```text
RMSE improvement
max error improvement
control energy change
recovery time improvement
```

Do not claim improvement without baseline data.

---

## 7. Output Schema

Recommended JSON:

```json
{
  "experiment_id": "figure8_nmpc_indi_l1_001",
  "scene_id": "figure8",
  "controller_id": "nmpc_indi_l1",
  "tracking": {
    "position_rmse": 0.0,
    "rmse_x": 0.0,
    "rmse_y": 0.0,
    "rmse_z": 0.0,
    "max_position_error": 0.0,
    "steady_state_error": 0.0
  },
  "attitude": {
    "roll_rmse": 0.0,
    "pitch_rmse": 0.0,
    "yaw_rmse": 0.0,
    "max_tilt_angle": 0.0
  },
  "control": {
    "control_energy": 0.0,
    "control_smoothness": 0.0,
    "saturation_ratio": 0.0
  },
  "safety": {
    "constraint_violation_count": 0,
    "minimum_altitude": 0.0,
    "minimum_obstacle_distance": null,
    "minimum_inter_uav_distance": null
  }
}
```

---

## 8. Pass / Fail Criteria

Default pass criteria for a valid experiment:

```text
raw result file exists
time column exists
position columns exist
reference position columns exist
metrics file generated
no NaN in core variables
position_rmse is finite
figures generated
```

Regression criteria:

```text
RMSE must not worsen by more than 20% compared with previous valid result unless documented.
Simulation must not fail.
Constraint violation count must not increase unexpectedly.
```

---

## 9. Report Usage

Metrics used in the report must match saved files.

For each table in the report, record:

```text
source raw file
source metrics file
script version
generated timestamp
```

Report claims must be phrased conservatively if data is incomplete.
