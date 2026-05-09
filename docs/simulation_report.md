# 仿真分析报告

> 当前 smoke 数据均只覆盖 0-1 s，用于验证 MCP 结果读取、CSV 导出和指标计算链路。完整性能结论只引用 `official_example*_*.csv` 对应的全时长真实 Sysplorer MCP 结果。

## 1. 报告范围

本报告记录当前工程已经可复现的仿真数据链路、官方参考轨迹、指标计算方法和图表生成方式。控制器性能对比只引用已保存 raw CSV、metrics JSON/CSV、MCP JSONL 日志和 SVG 图表的实验。

当前已完成的可复现资产：

```text
官方 Example1/2/3 参考轨迹 CSV
官方 Example1/2/3 完整 PID baseline CSV、指标和图表
官方 Example1/3 保守阻尼增强 PID CSV、指标和图表
官方 Example1/2/3 离线浏览器回放 HTML
Example1 0-1 s smoke 结果 CSV
Example1 0-1 s smoke 指标 JSON/CSV
Example1 0-1 s smoke SVG 图表
Example1 0-1 s 真实 Sysplorer MCP smoke 日志、CSV 和指标
```

## 2. 模型与场景

| 场景 | 官方模型 | 时长 | 当前状态 |
|---|---|---:|---|
| 阶梯爬升 | `QuadrotorModel.Examples.Example1` | 50 s | 完整 PID baseline 和保守阻尼增强 PID 已通过 Sysplorer MCP 仿真 |
| 螺旋爬升 | `QuadrotorModel.Examples.Example2` | 50 s | 完整 PID baseline 已通过 Sysplorer MCP 仿真 |
| 8字形运动 | `QuadrotorModel.Examples.Example3` | 120 s | 完整 PID baseline 和保守阻尼增强 PID 已通过 Sysplorer MCP 仿真 |
| Example1 smoke | `QuadrotorModel.Examples.Example1` | 1 s | 已有 CSV、指标、图表 |
| Example1 MWORKS MCP smoke | `QuadrotorModel.Examples.Example1` | 1 s | 已通过 Sysplorer MCP 真实加载、检查、仿真和读取变量 |

官方完整 baseline 结果文件预期路径：

```text
results/raw/official_example1_pid_baseline.csv
results/raw/official_example2_pid_baseline.csv
results/raw/official_example3_pid_baseline.csv
results/metrics/official_example1_pid_baseline.json
results/metrics/official_example2_pid_baseline.json
results/metrics/official_example3_pid_baseline.json
```

`scripts/qa_check.py` 会阻止短时 smoke 数据误放入上述正式结果路径。

## 3. 数据链路

当前数据处理闭环：

```text
QuadrotorModel/package.mo
→ scenarios/official/*.yaml
→ Sysplorer MCP check_model/simulate_model
→ result_manager 读取变量
→ scripts/run_sysplorer_mcp_smoke.py 导出标准 CSV
→ scripts/calc_metrics.py 计算指标
→ scripts/plot_results.py 生成 SVG 图表
→ scripts/generate_replay_html.py 生成离线三维回放
```

标准 CSV 核心字段：

```text
time,x,y,z,x_ref,y_ref,z_ref,roll,pitch,yaw,u1,u2,u3,u4
```

官方变量映射见 `docs/index/variable_mapping.md`。

## 4. 当前 Smoke 指标

数据文件：

```text
results/raw/smoke_official_example1_pid_baseline.csv
results/metrics/smoke_official_example1_pid_baseline.json
results/test_reports/sysplorer_example1_pid_mcp_smoke_20260509.jsonl
results/raw/mworks_mcp_example1_pid_smoke.csv
results/metrics/mworks_mcp_example1_pid_smoke.json
```

当前 smoke 指标用于验证计算链路：

| 指标 | 数值 |
|---|---:|
| row_count | 101 |
| duration_s | 1.0 |
| position_rmse_m | 0.977959 |
| max_position_error_m | 1.369402 |
| steady_state_error_m | 0.873718 |
| nan_count | 0 |

其中 `mworks_mcp_example1_pid_smoke` 是 `source=MWORKS_MCP` 的真实 Sysplorer MCP smoke：脚本通过 `model_manager load_file` 加载 `QuadrotorModel/package.mo`，`check_model` 检查 `QuadrotorModel.Examples.Example1`，`simulate_model` 运行 0-1 s，并通过 `result_manager get_vars_values` 导出 `time,x,y,z,x_ref,y_ref,z_ref,roll,pitch,yaw,u1,u2,u3,u4`。

说明：这些结果只覆盖起飞初始 1 s，不能用于评价完整阶梯爬升控制性能。

## 5. 官方 PID Baseline 指标

以下结果均为 `source=MWORKS_MCP`、`evidence_level=real_sysplorer_mcp_full_baseline`：

| 场景 | 时长/s | position_rmse_m | max_position_error_m | steady_state_error_m | max_tilt_rad | control_energy | total_health_score |
|---|---:|---:|---:|---:|---:|---:|---:|
| Example1 阶梯爬升 | 50.0 | 0.275253 | 1.369402 | 0.111457 | 0.225729 | 39925.003500 | 52.464469 |
| Example2 螺旋爬升 | 50.0 | 0.487183 | 3.005422 | 0.210149 | 0.330881 | 37306.013865 | 47.882655 |
| Example3 8字形 | 120.0 | 0.172311 | 1.217033 | 0.068172 | 0.286482 | 95610.155697 | 60.505386 |

说明：`u1-u4` 当前取自 `controller3_2.y*` 原始控制命令，数值范围不是 0-1 归一化电机占空比，因此 `saturation_ratio` 不用于本批结果的饱和结论；相关 JSON 中记录 `control_command_min/max` 和 `control_command_normalized=false`。

## 6. 改进 PID 对比

当前 `QuadrotorExperiments.Example1ImprovedPID` 和 `QuadrotorExperiments.Example3ImprovedPID` 采用保守阻尼增强参数：保持位置环比例/微分参数与官方基线一致，仅将姿态内环 `PID5/PID6.KD` 从 `1.414` 提高到 `1.65`。该方案的目标是先建立不破坏官方模型的参数替换与对比链路，而不是宣称最终最优控制器。

以下结果均为 `source=MWORKS_MCP`、`evidence_level=real_sysplorer_mcp_full_improved_pid`：

| 场景 | controller | position_rmse_m | RMSE变化 | steady_state_error_m | max_tilt_rad | control_energy | total_health_score |
|---|---|---:|---:|---:|---:|---:|---:|
| Example1 阶梯爬升 | baseline | 0.275253 | - | 0.111457 | 0.225729 | 39925.003500 | 52.464469 |
| Example1 阶梯爬升 | improved_pid | 0.274717 | +0.195% | 0.111766 | 0.262259 | 39925.741869 | 52.467486 |
| Example3 8字形 | baseline | 0.172311 | - | 0.068172 | 0.286482 | 95610.155697 | 60.505386 |
| Example3 8字形 | improved_pid | 0.171874 | +0.254% | 0.068177 | 0.293644 | 95610.320496 | 60.508930 |

结论：该参数集能在 Example1/3 上带来很小的 RMSE 改善，但稳态误差基本持平或略差，不能作为最终创新算法的主要得分点。后续应继续推进带抗饱和、参考前馈或 NMPC/INDI 的真实模型集成。

## 7. 当前图表

已生成图表：

```text
results/figures/official_example1_pid_baseline/
results/figures/official_example1_improved_pid/
results/figures/official_example2_pid_baseline/
results/figures/official_example3_pid_baseline/
results/figures/official_example3_improved_pid/
results/figures/smoke_official_example1_pid_baseline/trajectory_xy.svg
results/figures/smoke_official_example1_pid_baseline/altitude_tracking.svg
results/figures/smoke_official_example1_pid_baseline/position_error.svg
results/figures/smoke_official_example1_pid_baseline/metrics_summary.svg
```

已生成回放：

```text
results/replay_html/reference_official_example1.html
results/replay_html/reference_official_example2.html
results/replay_html/reference_official_example3.html
```

## 8. 待补全实验

| 优先级 | 实验 | 输出 |
|---|---|---|
| P0 | 改进 PID 深化：抗饱和/前馈参数集 | RMSE、稳态误差、控制能量对比 |
| P1 | 风扰/质量变化鲁棒性 | recovery_time、degradation |
| P1 | 电机效率下降/故障重分配 | saturation_ratio、max_error |
| P2 | 规划与编队展示场景 | replay、健康度评分、最小距离 |

## 9. 结论约束

1. 不使用 smoke 数据做完整控制性能结论。
2. 不引用未保存 raw CSV 和 metrics 的实验结果。
3. 报告中的每张图必须能追溯到 `results/raw/` 和生成脚本。
4. 完整 baseline 与优化控制器必须使用同一场景、同一时长和同一指标脚本。
