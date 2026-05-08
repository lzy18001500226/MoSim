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

Use scripts:

```text
scripts/plot_results.jl
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

## 5. Figure Naming

Use:

```text
results/figures/{scene}_{controller}/trajectory_3d.png
results/figures/{scene}_{controller}/position_error.png
results/figures/{scene}_{controller}/attitude.png
results/figures/{scene}_{controller}/control_input.png
results/figures/{scene}_{controller}/metrics_bar.png
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
