# 仿真分析报告

> 当前 `results/raw/smoke_official_example1_pid_baseline.csv` 仅为 0-1 s smoke 数据，用于验证 MCP 结果读取、CSV 导出和指标计算链路。完整官方 baseline 必须重新运行 `scenarios/official/*.yaml` 中的完整仿真时长后再写入性能结论。

## 1. 报告范围

本报告记录当前工程已经可复现的仿真数据链路、官方参考轨迹、指标计算方法和图表生成方式。控制器性能对比结论必须等完整官方 baseline 和优化控制器仿真结果生成后再填写。

当前已完成的可复现资产：

```text
官方 Example1/2/3 参考轨迹 CSV
官方 Example1/2/3 离线浏览器回放 HTML
Example1 0-1 s smoke 结果 CSV
Example1 0-1 s smoke 指标 JSON/CSV
Example1 0-1 s smoke SVG 图表
```

## 2. 模型与场景

| 场景 | 官方模型 | 时长 | 当前状态 |
|---|---|---:|---|
| 阶梯爬升 | `QuadrotorModel.Examples.Example1` | 50 s | 参考轨迹已生成；完整 baseline 待 MCP 仿真 |
| 螺旋爬升 | `QuadrotorModel.Examples.Example2` | 50 s | 参考轨迹已生成；完整 baseline 待 MCP 仿真 |
| 8字形运动 | `QuadrotorModel.Examples.Example3` | 120 s | 参考轨迹已生成；完整 baseline 待 MCP 仿真 |
| Example1 smoke | `QuadrotorModel.Examples.Example1` | 1 s | 已有 CSV、指标、图表 |

官方完整 baseline 结果文件预期路径：

```text
results/raw/official_example1_pid_baseline.csv
results/raw/official_example2_pid_baseline.csv
results/raw/official_example3_pid_baseline.csv
```

`scripts/qa_check.py` 会阻止短时 smoke 数据误放入上述正式结果路径。

## 3. 数据链路

当前数据处理闭环：

```text
QuadrotorModel/package.mo
→ scenarios/official/*.yaml
→ Sysplorer MCP check_model/simulate_model
→ result_manager 读取变量
→ scripts/extract_mcp_timeseries.py 导出标准 CSV
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

说明：该结果只覆盖起飞初始 1 s，不能用于评价完整阶梯爬升控制性能。

## 5. 当前图表

已生成图表：

```text
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

## 6. 待补全实验

| 优先级 | 实验 | 输出 |
|---|---|---|
| P0 | 完整官方 PID baseline：Example1/2/3 | raw CSV、metrics、figures、replay |
| P0 | 改进 PID 对比：Example1/3 | RMSE、稳态误差、控制能量对比 |
| P1 | 风扰/质量变化鲁棒性 | recovery_time、degradation |
| P1 | 电机效率下降/故障重分配 | saturation_ratio、max_error |
| P2 | 规划与编队展示场景 | replay、健康度评分、最小距离 |

## 7. 结论约束

1. 不使用 smoke 数据做完整控制性能结论。
2. 不引用未保存 raw CSV 和 metrics 的实验结果。
3. 报告中的每张图必须能追溯到 `results/raw/` 和生成脚本。
4. 完整 baseline 与优化控制器必须使用同一场景、同一时长和同一指标脚本。
