# 用户手册

本文档说明如何检查项目结构、复现官方案例参考轨迹、处理 MWORKS/MCP 导出的仿真结果、生成指标和报告素材。

## 1. 环境要求

必需环境：

```text
Python 3.10+
MWORKS.Sysplorer 2026
MWORKS.Sysblock 2026
MWORKS.Syslab 2026
Codex MCP: syslab, sysplorer_mcp
```

可选环境：

```text
Julia / Syslab Julia runtime
Sysplorer plot_manager / Syslab plotting APIs
```

当前 WSL 自动化优先使用 Python 脚本；当 Syslab/Julia 不可用时，仍可完成 QA、参考轨迹、指标和 SVG 图表生成。

## 2. 快速检查

在项目根目录运行：

```bash
python3 scripts/qa_check.py
python3 scripts/check_reference_outputs.py
```

通过标准：

```text
Required project structure passed
MCP wrapper scripts found
official_example1/2/3 reference checks OK
```

## 3. 官方案例入口

官方模型包：

```text
QuadrotorModel/package.mo
```

官方场景配置：

```text
scenarios/official/example1_pid_baseline.yaml  阶梯爬升，50 s
scenarios/official/example2_pid_baseline.yaml  螺旋爬升，50 s
scenarios/official/example3_pid_baseline.yaml  8字形运动，120 s
```

对应模型：

```text
QuadrotorModel.Examples.Example1
QuadrotorModel.Examples.Example2
QuadrotorModel.Examples.Example3
```

## 4. 参考轨迹与回放

生成官方参考轨迹和回放 JSON：

```bash
python3 scripts/generate_reference.py --scene all
python3 scripts/check_reference_outputs.py
python3 scripts/generate_replay_html.py --all
```

输出：

```text
results/raw/reference_official_example1.csv
results/raw/reference_official_example2.csv
results/raw/reference_official_example3.csv
results/replay/reference_official_example1.json
results/replay/reference_official_example2.json
results/replay/reference_official_example3.json
results/replay_html/reference_official_example1.html
results/replay_html/reference_official_example2.html
results/replay_html/reference_official_example3.html
```

`results/replay_html/*.html` 为离线浏览器三维回放页面，可直接打开录屏，不依赖 CDN。

## 5. 官方仿真流程

使用 Sysplorer MCP 时按以下顺序执行：

```text
session_manager
→ model_manager load QuadrotorModel/package.mo
→ check_model
→ simulate_model
→ result_manager list/read variables
→ export raw CSV
→ calc metrics
→ generate figures/replay
```

变量映射见：

```text
docs/index/variable_mapping.md
```

完整官方 baseline 结果应写入：

```text
results/raw/official_example1_pid_baseline.csv
results/raw/official_example2_pid_baseline.csv
results/raw/official_example3_pid_baseline.csv
```

`qa_check.py` 会检查这些正式结果的时长，Example1/2 不得短于 50 s，Example3 不得短于 120 s。

## 6. Smoke 数据说明

当前仓库包含一个 0-1 s smoke 数据集：

```text
results/raw/smoke_official_example1_pid_baseline.csv
results/metrics/smoke_official_example1_pid_baseline.json
results/figures/smoke_official_example1_pid_baseline/
```

该数据只用于验证 MCP 结果读取、CSV 导出、指标计算和图表生成链路，不作为完整官方 baseline 性能结论。

## 7. 指标与图表

计算指标：

```bash
python3 scripts/calc_metrics.py \
  results/raw/smoke_official_example1_pid_baseline.csv \
  results/metrics/smoke_official_example1_pid_baseline.json \
  smoke_official_example1 \
  pid_baseline
```

指标输出包含：

```text
position_rmse_m
max_position_error_m
steady_state_error_m
settling_time_s
overshoot_x_pct / overshoot_y_pct / overshoot_z_pct / overshoot_max_pct
roll_rmse_rad / pitch_rmse_rad / yaw_rmse_rad / max_tilt_rad
minimum_altitude_m
constraint_violation_count
control_energy
control_smoothness
saturation_ratio
tracking_score / robustness_score / safety_score / energy_score / smoothness_score / fault_tolerance_score / total_health_score
```

生成 SVG 图表：

```bash
python3 scripts/plot_results.py \
  results/raw/smoke_official_example1_pid_baseline.csv \
  results/figures/smoke_official_example1_pid_baseline \
  --metrics results/metrics/smoke_official_example1_pid_baseline.json
```

图表输出：

```text
trajectory_xy.svg
altitude_tracking.svg
position_error.svg
metrics_summary.svg
figure_manifest.md
```

生成实验汇总：

```bash
python3 scripts/summarize_experiments.py --include-metrics-glob 'results/metrics/smoke_*.json'
```

输出：

```text
results/test_reports/experiment_summary.csv
results/test_reports/experiment_summary.md
```

说明：正式场景没有对应 metrics 文件时会标记为 `pending`，不会用 smoke 数据替代完整 baseline 结论。

## 8. 提交前检查

提交前运行：

```bash
python3 scripts/qa_check.py
python3 scripts/check_reference_outputs.py
python3 tests/test_metrics.py
python3 tests/test_summary.py
python3 -m py_compile scripts/*.py
git diff --check
```

若生成了新的二进制或官方资料文件，还需确认没有超过 GitHub 限制的大文件。
