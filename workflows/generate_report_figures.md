# Generate Report Figures Workflow

> Purpose: generate report-ready figures from raw simulation results and metrics.

---

## 1. Goal

Generate figures that directly support the final report and demo video.

---

## 2. Inputs

```text
raw_result_file
metrics_file
scenario_config
figure_output_dir
```

---

## 3. Tools

Use Syslab MCP:

```text
run_julia_file
evaluate_julia_code
search_syslab_docs
read_syslab_doc
```

Available helper script:

```text
scripts/plot_results.py
scripts/plot_results.jl
scripts/generate_replay_html.py
```

`scripts/plot_results.py` generates dependency-free SVG figures from a standard
CSV and optional metrics JSON:

```bash
python3 scripts/plot_results.py \
  results/official/example1_step/official_example1_improved_pid/raw/official_example1_improved_pid.csv \
  results/official/example1_step/official_example1_improved_pid/figures \
  --metrics results/official/example1_step/official_example1_improved_pid/metrics/official_example1_improved_pid.json
```

Use `scripts/plot_results.jl`, Syslab MCP plotting APIs, or Sysplorer
`plot_manager` only when higher-fidelity native plots are required.

When the raw CSV contains `eta_hat1..4` and `fault_index`, the Python figure
generator also writes `*_eta_hat_diagnostics.svg` and
`*_fault_index_diagnostics.svg`. Use these figures for fault-isolation claims
instead of relying only on numeric metrics.

`scripts/generate_replay_html.py` creates self-contained offline browser replay
pages from `results/{group}/{scene}/{experiment}/replay/*.json`. The generated HTML has no CDN dependency
and can be used for browser recording and 3D demo video materials without
opening MWORKS:

```bash
python3 scripts/generate_replay_html.py --all
```

Output:

```text
results/{group}/{scene}/{experiment}/replay_html/{replay_name}.html
```

---

## 4. Required Figures

For core control comparison:

```text
3D trajectory comparison
position error vs time
axis errors vs time
attitude angles vs time
motor commands vs time
metrics bar chart
```

For robustness:

```text
wind disturbance error curve
mass change response
motor fault attitude response
recovery time comparison
```

For planning:

```text
obstacle map
planned path
smoothed trajectory
actual tracked trajectory
minimum obstacle distance curve
```

For formation:

```text
multi-UAV trajectory
formation error curve
minimum inter-UAV distance curve
formation switching process
```

---

## 5. Figure Directory Taxonomy

Put report figures under the owning experiment directory. The scenario groups should contain experiment directories, not shared asset directories:

```text
results/official/example1_step/official_example1_awff_sysblock/figures/
results/official/example2_helix/official_example2_awff_sysblock/figures/
results/official/example3_figure8/official_example3_awff_sysblock/figures/
results/robustness/mass20_example1/robust_mass20_example1_awff_sysblock/figures/
results/robustness/wind_gust_example1/robust_wind_gust_example1_awff_sysblock/figures/
results/robustness/rotor1_loss15_example1/robust_rotor1_loss15_example1_awff_sysblock/figures/
results/smoke/example1_mcp/{controller}_smoke/figures/
```

`results/official/example3_figure8/*/figures/` contains the current 8-shaped official
trajectory figure groups. `results/smoke/` figures are process evidence only and
should not be used as final report or demo-video material unless explicitly
marked as smoke.

Each generated directory should contain:

```text
trajectory_xy.svg
altitude_tracking.svg
position_error.svg
metrics_summary.svg
figure_manifest.md
```

After adding or regenerating figures, update:

```text
results/人工审核清单.csv
results/README.md
```

Copy report-selected figures to:

```text
docs/figures/
```

---

## 6. Figure Requirements

Each figure should have:

```text
clear title
axis labels
units
legend
scene name
controller name
```

Do not use figures without labels in the final report.

---

## 7. Report Linkage

For each figure used in the report, record:

```text
figure file path
source raw result
source metrics
generation script
caption draft
```

---

## 8. Validation

Pass if:

```text
figure file exists
figure is readable
figure has axis labels
figure corresponds to saved metrics
figure caption is prepared
```
