# 仿真分析报告

> 当前 smoke 数据均只覆盖 0-1 s，用于验证 MCP 结果读取、CSV 导出和指标计算链路。完整性能结论只引用 `official_example*_*.csv` 对应的全时长真实 Sysplorer MCP 结果。

## 1. 报告范围

本报告记录当前工程已经可复现的仿真数据链路、官方参考轨迹、指标计算方法和图表生成方式。控制器性能对比只引用已保存 raw CSV、metrics JSON/CSV、MCP JSONL 日志和 SVG 图表的实验。

当前已完成的可复现资产：

```text
官方 Example1/2/3 参考轨迹 CSV
官方 Example1/2/3 完整 PID baseline CSV、指标和图表
官方 Example1/2/3 MCP 参数搜索型 Improved PID CSV、指标和图表
官方 Example1/2/3 浏览器三维回放 HTML
Example1 0-1 s 真实 Sysplorer MCP smoke 日志、CSV 和指标
```

## 2. 模型与场景

| 场景 | 官方模型 | 时长 | 当前状态 |
|---|---|---:|---|
| 阶梯爬升 | `QuadrotorModel.Examples.Example1` | 50 s | 完整 PID baseline 和 MCP 参数搜索型 Improved PID 已通过 Sysplorer MCP 仿真 |
| 螺旋爬升 | `QuadrotorModel.Examples.Example2` | 50 s | 完整 PID baseline 和 MCP 参数搜索型 Improved PID 已通过 Sysplorer MCP 仿真 |
| 8字形运动 | `QuadrotorModel.Examples.Example3` | 120 s | 完整 PID baseline 和 MCP 参数搜索型 Improved PID 已通过 Sysplorer MCP 仿真 |
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
→ scripts/generate_replay_from_raw.py 生成真实轨迹回放 JSON
→ scripts/generate_replay_html.py 生成离线三维回放 HTML
```

标准 CSV 核心字段：

```text
time,x,y,z,x_ref,y_ref,z_ref,roll,pitch,yaw,u1,u2,u3,u4
```

官方变量映射见 `docs/index/variable_mapping.md`。

## 4. 当前 Smoke 指标

数据文件：

```text
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

当前 `QuadrotorExperiments.Example1ImprovedPID`、`QuadrotorExperiments.Example2ImprovedPID` 和 `QuadrotorExperiments.Example3ImprovedPID` 采用 MCP 参数搜索选出的统一 PID 参数集 `pos_kp_165_att_170`：将水平位置环 `PID3/PID4.KP` 从 `1.5` 提高到 `1.65`，将姿态内环 `PID5/PID6.KD` 从 `1.414` 提高到 `1.70`，其余高度环与 yaw 环参数保持官方基线不变。搜索脚本为 `scripts/tune_improved_pid_mcp.py`，搜索摘要见 `results/test_reports/pid_tuning_summary.md`。

候选选择原则：不用单场景最优作为正式参数，而选取在 Example1 阶梯爬升和 Example3 8 字轨迹上均能降低 RMSE 的统一参数集。`pos_kd_115_att_170` 在 Example1 上 RMSE 更低，但最大倾角达到 `0.345064 rad`，且 Example3 不如 `pos_kp_165_att_170`；因此正式模型选择后者。

以下结果均为 `source=MWORKS_MCP`、`evidence_level=real_sysplorer_mcp_full_improved_pid`：

| 场景 | controller | position_rmse_m | RMSE变化 | steady_state_error_m | max_tilt_rad | control_energy | total_health_score |
|---|---|---:|---:|---:|---:|---:|---:|
| Example1 阶梯爬升 | baseline | 0.275253 | - | 0.111457 | 0.225729 | 39925.003500 | 52.464469 |
| Example1 阶梯爬升 | improved_pid | 0.269890 | +1.948% | 0.105559 | 0.273695 | 39926.972404 | 52.533227 |
| Example2 螺旋爬升 | baseline | 0.487183 | - | 0.210149 | 0.330881 | 37306.013865 | 47.882655 |
| Example2 螺旋爬升 | improved_pid | 0.479834 | +1.508% | 0.190661 | 0.358260 | 37312.619310 | 48.025785 |
| Example3 8字形 | baseline | 0.172311 | - | 0.068172 | 0.286482 | 95610.155697 | 60.505386 |
| Example3 8字形 | improved_pid | 0.167227 | +2.951% | 0.061940 | 0.295880 | 95611.212646 | 60.546610 |

结论：参数搜索型 Improved PID 相比官方 PID 在 Example1/2/3 上分别降低 RMSE `1.948%`、`1.508%` 和 `2.951%`，稳态误差分别降低 `5.291%`、`9.273%` 和 `9.141%`。代价是最大倾角和控制能量略有增加，因此该结果适合作为 P0 可复现优化基线，不应包装成最终控制创新；后续仍应推进带抗饱和、参考前馈或 NMPC/INDI 的真实模型集成。

## 7. 当前图表

已生成图表：

```text
results/figures/official_example1_pid_baseline/
results/figures/official_example1_improved_pid/
results/figures/official_example2_pid_baseline/
results/figures/official_example2_improved_pid/
results/figures/official_example3_pid_baseline/
results/figures/official_example3_improved_pid/
```

已生成回放：

```text
results/replay_html/official_example1_pid_baseline.html
results/replay_html/official_example1_improved_pid.html
results/replay_html/official_example2_pid_baseline.html
results/replay_html/official_example2_improved_pid.html
results/replay_html/official_example3_pid_baseline.html
results/replay_html/official_example3_improved_pid.html
results/replay_html/reference_official_example1.html
results/replay_html/reference_official_example2.html
results/replay_html/reference_official_example3.html
```

其中 `official_example*_*.html` 来自真实 Sysplorer MCP raw CSV，包含实际飞行轨迹和参考轨迹；`reference_official_example*.html` 仅为官方参考路径展示。

## 8. 扩展场景状态

此前用于横向展示的 Python/Julia 离线仿真结果已清理。当前报告结论只引用真实 Sysplorer/MWORKS MCP 证据。

风扰、质量变化、故障、规划和编队仍保留在 `Design/` 中作为下一阶段实现目标，但必须完成以下闭环后才能进入本报告的性能结论：

```text
MWORKS/Sysplorer 模型或派生模型
→ check_model 成功
→ simulate_model 完整运行
→ result_manager 导出 raw CSV
→ metrics/figures/replay 可复现
→ source=MWORKS_MCP 或 source=MWORKS_GUI
```

下一阶段优先把一个高展示度场景升级为真实证据：

1. 风扰/质量变化下的鲁棒控制对比；
2. 改进 PID 的抗积分饱和、导数滤波和参考前馈真实模型实现；
3. INDI 或线性 MPC 外环的最小可运行模型。

## 9. 结论约束

1. 不使用 smoke 数据做完整控制性能结论。
2. 不使用离线脚本结果作为 MWORKS 控制性能结论。
3. 报告中的每张图必须能追溯到 `results/raw/` 和生成脚本。
4. 完整 baseline 与优化控制器必须使用同一场景、同一时长和同一指标脚本。
