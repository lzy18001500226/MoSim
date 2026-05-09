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
python3 scripts/summarize_experiments.py \
  --include-metrics-glob 'results/metrics/smoke_*.json' \
  --include-metrics-glob 'results/metrics/trackability_*.json' \
  --include-metrics-glob 'results/metrics/formation_*.json' \
  --include-metrics-glob 'results/metrics/fault_*.json'
```

输出：

```text
results/test_reports/experiment_summary.csv
results/test_reports/experiment_summary.md
```

说明：正式场景没有对应 metrics 文件时会标记为 `pending`，不会用 smoke 数据替代完整 baseline 结论。

## 8. 扰动补偿与模式切换

生成风扰残差估计、L1-inspired 低通补偿和模式切换演示数据：

```bash
python3 scripts/generate_disturbance_mode_demo.py
python3 scripts/generate_replay_html.py \
  results/replay/wind_nmpc_indi_l1.json \
  results/replay_html/wind_nmpc_indi_l1.html
```

输出：

```text
results/raw/wind_nmpc_indi_l1.csv
results/metrics/wind_nmpc_indi_l1.json
results/logs/wind_nmpc_indi_l1_events.jsonl
results/replay/wind_nmpc_indi_l1.json
results/replay_html/wind_nmpc_indi_l1.html
```

指标包含 `raw_residual_rmse_m_s2`、`compensated_residual_rmse_m_s2`、`residual_reduction_pct`、`controller_mode_switch_count`、`wind_rejection_entered` 和 `total_health_score`。事件日志应包含 `NORMAL → WIND_REJECTION → NORMAL`，用于证明 P1-A 的扰动识别和控制模式切换链路。

生成投递后质量变化自适应演示数据：

```bash
python3 scripts/generate_mass_adaptation_demo.py
python3 scripts/generate_replay_html.py \
  results/replay/delivery_mass_change.json \
  results/replay_html/delivery_mass_change.html
```

输出：

```text
results/raw/reference_delivery_mass_change.csv
results/raw/delivery_mass_change.csv
results/metrics/delivery_mass_change.json
results/logs/delivery_mass_change_events.jsonl
results/replay/delivery_mass_change.json
results/replay_html/delivery_mass_change.html
```

指标包含 `raw_vertical_residual_rmse_m_s2`、`compensated_vertical_residual_rmse_m_s2`、`vertical_residual_reduction_pct`、`mass_adaptation_entered`、`return_position_error_m` 和 `degraded_task_completion`。事件日志应包含 `delivery` 和 `MASS_ADAPTATION`，用于证明投递任务中的质量变化识别与 z 向补偿链路。

## 9. 规划参考轨迹

生成可跟踪航点规划参考：

```bash
python3 scripts/generate_planning_reference.py
python3 scripts/generate_replay_html.py \
  results/replay/planning_trackable_waypoint.json \
  results/replay_html/planning_trackable_waypoint.html
```

输出：

```text
results/raw/reference_planning_trackable_waypoint.csv
results/metrics/trackability_planning_trackable_waypoint.json
results/replay/planning_trackable_waypoint.json
results/replay_html/planning_trackable_waypoint.html
```

`trackability` 报告包含速度、加速度、jerk、倾角、预测饱和比例和 `final_trackability_score`。脚本会在动态约束超限时自动放大分段时间，直到满足阈值或达到最大迭代次数。

生成带障碍物的 3D A* 规划参考：

```bash
python3 scripts/generate_obstacle_planning_reference.py
python3 scripts/generate_replay_html.py \
  results/replay/planning_obstacle_corridor.json \
  results/replay_html/planning_obstacle_corridor.html
```

输出：

```text
results/raw/path_planning_obstacle_corridor.csv
results/raw/reference_planning_obstacle_corridor.csv
results/metrics/planning_obstacle_corridor.json
results/replay/planning_obstacle_corridor.json
results/replay_html/planning_obstacle_corridor.html
```

障碍规划指标包含 `minimum_obstacle_distance_m`、`safety_margin_m`、`obstacle_violation_count`、`obstacle_avoidance_score`、`final_trackability_score` 和 `total_health_score`。该场景用于证明规划器不是简单手工航点，而是能在 3D 地图中绕开膨胀障碍并输出可跟踪轨迹。

## 10. 编队参考轨迹

生成三机 Leader-Follower 编队参考：

```bash
python3 scripts/generate_formation_reference.py
python3 scripts/generate_replay_html.py \
  results/replay/formation_triangle_switch.json \
  results/replay_html/formation_triangle_switch.html
```

输出：

```text
results/raw/reference_formation_triangle_switch.csv
results/metrics/formation_triangle_switch.json
results/replay/formation_triangle_switch.json
results/replay_html/formation_triangle_switch.html
```

编队指标包含 `formation_error_rmse`、`formation_error_max`、`minimum_inter_uav_distance`、`formation_mode_switch_count`、`switching_time_s` 和 `formation_score`。当前脚本生成三角形到一字形再恢复三角形的三机参考轨迹，用于后续多机仿真或视频回放。

## 11. 安全故障与安全过滤

生成单电机效率下降与降级返航参考：

```bash
python3 scripts/generate_fault_scenario.py
python3 scripts/generate_replay_html.py \
  results/replay/fault_motor_return.json \
  results/replay_html/fault_motor_return.html
```

输出：

```text
results/raw/fault_motor_return_reference.csv
results/metrics/fault_motor_return.json
results/logs/fault_motor_return_events.jsonl
results/replay/fault_motor_return.json
results/replay_html/fault_motor_return.html
```

故障指标包含 `eta_min`、`controller_mode_switch_count`、`fault_tolerance_score`、`degraded_task_completion`、`minimum_altitude_m` 和 `altitude_violation_count`。事件日志记录 `motor_fault`、`mode_switch`、`degraded_return_start`、`fault_clear`，用于报告、视频字幕和后续容错控制器接入。

生成电机故障下有/无控制分配重构对比：

```bash
python3 scripts/generate_fault_reallocation_demo.py
python3 scripts/generate_replay_html.py \
  results/replay/fault_reallocation_compare.json \
  results/replay_html/fault_reallocation_compare.html
```

输出：

```text
results/raw/reference_fault_reallocation_compare.csv
results/raw/fault_reallocation_compare.csv
results/metrics/fault_reallocation_compare.json
results/logs/fault_reallocation_compare_events.jsonl
results/replay/fault_reallocation_compare.json
results/replay_html/fault_reallocation_compare.html
```

重构指标包含 `no_realloc_wrench_rmse`、`realloc_wrench_rmse`、`wrench_error_reduction_pct`、`no_realloc_saturation_ratio`、`realloc_saturation_ratio` 和 `fault_tolerance_score`。该场景用于证明 `eta=0.7` 时按故障效率矩阵重构控制分配可以显著降低期望力/力矩误差。

生成安全过滤器约束保护演示数据：

```bash
python3 scripts/generate_safety_filter_demo.py
python3 scripts/generate_replay_html.py \
  results/replay/safety_filter_guard.json \
  results/replay_html/safety_filter_guard.html
```

输出：

```text
results/raw/reference_safety_filter_guard.csv
results/raw/safety_filter_guard.csv
results/metrics/safety_filter_guard.json
results/logs/safety_filter_guard_events.jsonl
results/replay/safety_filter_guard.json
results/replay_html/safety_filter_guard.html
```

安全过滤指标包含 `raw_constraint_violation_count`、`safe_constraint_violation_count`、`constraint_violation_reduction_pct`、`safe_minimum_altitude_m`、`safe_minimum_obstacle_distance_m` 和 `safety_filter_activation_count`。该场景用于对比同一条不安全参考轨迹在过滤前后的高度、速度、加速度和障碍距离违规数量。

## 12. 提交前检查

提交前运行：

```bash
python3 scripts/qa_check.py
python3 scripts/check_reference_outputs.py
python3 tests/test_metrics.py
python3 tests/test_summary.py
python3 tests/test_planning_reference.py
python3 tests/test_obstacle_planning.py
python3 tests/test_formation_reference.py
python3 tests/test_fault_scenario.py
python3 tests/test_disturbance_mode_demo.py
python3 tests/test_mass_adaptation_demo.py
python3 tests/test_safety_filter_demo.py
python3 tests/test_fault_reallocation_demo.py
python3 -m py_compile scripts/*.py tests/*.py
git diff --check
```

若生成了新的二进制或官方资料文件，还需确认没有超过 GitHub 限制的大文件。
