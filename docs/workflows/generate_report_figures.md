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

For generated figure/report batches, prefer a small structured spec over
ad-hoc command memory:

```text
experiment_id
source label
raw result path
metrics path
figure output directory
required figure list
manual review target
report section that will cite the outputs
```

The generation step passes only when expected outputs exist, have nonzero size,
and are listed in the figure manifest. A failed generation must expose the
original error and leave old report-selected figures untouched unless the new
bundle passes.

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
scripts/stream_unreal_udp.py
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

`scripts/stream_unreal_udp.py` streams a standard MWORKS raw CSV to an external
Unreal renderer over UDP. This is a video/display path only: it must not be used
as simulation evidence and must not feed back into controller, planner, or
metric calculations.

Before UE scene construction, export the render-only map truth:

```bash
python3 scripts/export_unreal_scene_map.py --terrain-cell-m 1.0
```

The output `unreal/MworksUnrealRenderer/Content/MworksData/map_open_blocks_render_map.json`
uses the same `map_open_blocks.yaml` wall/random-obstacle expansion as the
planner. Unreal may instantiate terrain, random columns, L/T wall boxes, radar
materials, and camera presets from this JSON, but the file remains a display
asset, not a planning input.

Example offline playback stream:

```bash
python3 scripts/stream_unreal_udp.py \
  results/planning/sunray150_planning_open_blocks_linear_mpc_sysblock/gui_review_route_filtered_obstacles_1p0_full_50hz_step2/raw/gui_review_route_filtered_obstacles_1p0_full_50hz_step2.csv \
  --host 127.0.0.1 \
  --port 5005 \
  --scene-id planning_open_blocks \
  --map-id map_open_blocks \
  --fps 20 \
  --near-radius-m 6 \
  --far-radius-m 9 \
  --fov-deg 120
```

Packet protocol:

```json
{
  "schema": "quadrotor.unreal_state.v1",
  "type": "frame",
  "scene_id": "planning_open_blocks",
  "seq": 0,
  "t": 0.0,
  "uav": {
    "id": "uav_1",
    "position_m": [-41.0, -26.0, 1.5],
    "rpy_rad": [0.0, 0.0, 0.0],
    "motor_command": [0.0, 0.0, 0.0, 0.0]
  },
  "reference": {"position_m": [-41.0, -26.0, 1.5]},
  "perception": {
    "radar_origin_m": [-41.0, -26.0, 1.5],
    "yaw_rad": 0.0,
    "near_radius_m": 6.0,
    "far_radius_m": 9.0,
    "fov_deg": 120.0
  }
}
```

Coordinate rule: packets keep MWORKS meters/radians. The Unreal receiver handles
centimeter conversion, material selection, camera follow, radar-sector display,
and any engine-specific axis conversion.

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
```

`results/official/example3_figure8/*/figures/` contains the current 8-shaped official
trajectory figure groups. Temporary process-check figures should not be used as
final report or demo-video material unless explicitly marked as diagnostic.

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
