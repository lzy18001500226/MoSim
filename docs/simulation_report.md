# 仿真分析报告

> 当前 smoke 数据均只覆盖 0-1 s，用于验证 MCP 结果读取、CSV 导出和指标计算链路。完整性能结论只引用 `official_example*_*.csv` 对应的全时长真实 Sysplorer MCP 结果。

## 1. 报告范围

本报告记录当前工程已经可复现的仿真数据链路、官方参考轨迹、指标计算方法和图表生成方式。控制器性能对比只引用已保存 raw CSV、metrics JSON/CSV、MCP JSONL 日志和 SVG 图表的实验。

证据主线说明：赛题实现目标应以 **MWORKS.Sysblock 控制器仿真为主**。当前报告中的完整性能表包含真实 Sysplorer MCP / Modelica 派生模型闭环仿真，以及 `AWFF_FullControllerEquation_Sysblock` 接入官方 Example1/2/3 的全时长 Sysblock 控制器闭环证据。Sysblock 当前已完成 AWFF PID 高度环最小 demo、三段分层控制器、组合控制器 `AWFF_FullController_Sysblock` 的真实 MCP 验证，并完成 Example1 50 s、Example2 50 s、Example3 120 s 整机仿真；P1 创新控制器方向已完成 `AWFF_L1ResidualControllerEquation_Sysblock` 在 Example1 与横向阵风 Example1 中的首轮真实 MCP 消融。

质量判定规则：`check_model ok` 和 `simulate_model ok` 只说明模型可以执行；完整性能结论还必须通过 `scripts/evaluate_result_quality.py` 写入的 `quality_status`。`pass` 可支撑报告结论，`smoke_only` 只证明链路可用，`needs_iteration` 必须继续调控制器或明确写为未完成限制。当前 Example2 已通过 `helix_tuned` Enhanced PID、AWFF PID 和 AWFF Sysblock 分支解决 RMSE 门禁问题；旋翼退化场景健康分仍低于阈值，应作为后续控制分配/故障补偿迭代对象。

当前已完成的可复现资产：

```text
官方 Example1/2/3 参考轨迹 CSV
官方 Example1/2/3 完整 PID baseline CSV、指标和图表
官方 Example1/2/3 MCP 参数搜索型 Improved PID CSV、指标和图表
官方 Example1/2/3 Enhanced PID 完整 CSV、指标、图表和 replay JSON
官方 Example1/2/3 AWFF 独立控制器完整 CSV、指标、图表和 replay JSON
Example1/2/3 AWFF Sysblock 整机完整 CSV、指标、图表和 replay JSON
质量 +20%、横向阵风、1号旋翼效率85% 的 AWFF PID 鲁棒消融 CSV、指标、图表和 replay JSON
Example1/2/3 AWFF Sysblock 0-1 s 真实 Sysplorer MCP smoke 日志、CSV 和指标
Example1 L1 residual Sysblock nominal/wind-gust 0-1 s smoke 与 50 s full CSV、指标、图表和 replay JSON
```

## 2. 模型与场景

| 场景 | 官方模型 | 时长 | 当前状态 |
|---|---|---:|---|
| 阶梯爬升 | `QuadrotorModel.Examples.Example1` | 50 s | 完整 PID baseline 和 MCP 参数搜索型 Improved PID 已通过 Sysplorer MCP 仿真 |
| 阶梯爬升 Enhanced PID | `QuadrotorExperiments.Example1EnhancedPID` | 50 s | 导数滤波 + 保守限幅 Enhanced PID 已通过 Sysplorer MCP 仿真 |
| 阶梯爬升 AWFF PID | `QuadrotorExperiments.Example1AntiWindupFeedforwardPID` | 50 s | 项目自有抗饱和 + 竖直参考前馈控制器已通过 Sysplorer MCP 仿真 |
| 阶梯爬升 AWFF Sysblock | `QuadrotorExperiments.Example1AWFFSysblockClosedLoop` | 50 s | 项目 Sysblock 控制器整机闭环已通过 Sysplorer MCP 仿真 |
| 阶梯爬升 L1 residual Sysblock | `QuadrotorExperiments.Example1L1SysblockClosedLoop` | 50 s | AWFF + L1-inspired 残差补偿控制器已通过 Sysplorer MCP 仿真 |
| 横向阵风 L1 residual Sysblock | `QuadrotorExperiments.Example1WindGustL1SysblockClosedLoop` | 50 s | AWFF + L1-inspired 残差补偿风扰消融已通过 Sysplorer MCP 仿真 |
| 螺旋爬升 | `QuadrotorModel.Examples.Example2` | 50 s | 完整 PID baseline 和 MCP 参数搜索型 Improved PID 已通过 Sysplorer MCP 仿真 |
| 螺旋爬升 Enhanced PID | `QuadrotorExperiments.Example2EnhancedPID` | 50 s | 导数滤波 + 保守限幅 Enhanced PID 已通过 Sysplorer MCP 仿真，但质量门禁为 `needs_iteration` |
| 螺旋爬升 Helix-tuned Enhanced PID | `QuadrotorExperiments.Example2HelixTunedEnhancedPID` | 50 s | 15° 横向姿态权限 + 7.0 姿态控制限幅已通过 Sysplorer MCP 仿真，质量门禁为 `pass` |
| 螺旋爬升 AWFF PID | `QuadrotorExperiments.Example2AntiWindupFeedforwardPID` | 50 s | 项目自有抗饱和 + 竖直参考前馈控制器已通过 Sysplorer MCP 仿真，但质量门禁为 `needs_iteration` |
| 螺旋爬升 Helix-tuned AWFF PID | `QuadrotorExperiments.Example2HelixTunedAntiWindupFeedforwardPID` | 50 s | 15° 横向姿态权限 + 7.0 姿态控制限幅已通过 Sysplorer MCP 仿真，质量门禁为 `pass` |
| 螺旋爬升 AWFF Sysblock | `QuadrotorExperiments.Example2AWFFSysblockClosedLoop` | 50 s | inactive 历史诊断证据，正式矩阵使用 Helix-tuned AWFF Sysblock |
| 螺旋爬升 Helix-tuned AWFF Sysblock | `QuadrotorExperiments.Example2HelixTunedAWFFSysblockClosedLoop` | 50 s | Sysblock 控制器参数化调优已于 2026-05-11 复测通过，质量门禁为 `pass` |
| 8字形运动 | `QuadrotorModel.Examples.Example3` | 120 s | 完整 PID baseline 和 MCP 参数搜索型 Improved PID 已通过 Sysplorer MCP 仿真 |
| 8字形运动 Enhanced PID | `QuadrotorExperiments.Example3EnhancedPID` | 120 s | 导数滤波 + 保守限幅 Enhanced PID 已通过 Sysplorer MCP 仿真，质量门禁为 `pass` |
| 8字形运动 AWFF PID | `QuadrotorExperiments.Example3AntiWindupFeedforwardPID` | 120 s | 项目自有抗饱和 + 竖直参考前馈控制器已通过 Sysplorer MCP 仿真，质量门禁为 `pass` |
| 8字形运动 AWFF Sysblock | `QuadrotorExperiments.Example3AWFFSysblockClosedLoop` | 120 s | 项目 Sysblock 控制器整机闭环已通过 Sysplorer MCP 仿真 |
| Example1 smoke | `QuadrotorModel.Examples.Example1` | 1 s | 已有 CSV、指标、图表 |
| Example1 MWORKS MCP smoke | `QuadrotorModel.Examples.Example1` | 1 s | 已通过 Sysplorer MCP 真实加载、检查、仿真和读取变量 |

官方完整 baseline 结果文件预期路径：

```text
results/official/example1_step/official_example1_pid_baseline/raw/official_example1_pid_baseline.csv
results/official/example2_helix/official_example2_pid_baseline/raw/official_example2_pid_baseline.csv
results/official/example3_figure8/official_example3_pid_baseline/raw/official_example3_pid_baseline.csv
results/official/example1_step/official_example1_pid_baseline/metrics/official_example1_pid_baseline.json
results/official/example2_helix/official_example2_pid_baseline/metrics/official_example2_pid_baseline.json
results/official/example3_figure8/official_example3_pid_baseline/metrics/official_example3_pid_baseline.json
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
→ scripts/generate_replay_from_raw.py 生成 replay JSON
```

说明：`replay JSON/HTML` 只用于导出展示素材，不参与控制闭环，也不作为在线仿真证据。当前控制器仿真的正式证据为 MWORKS/Sysplorer 模型检查、仿真日志、raw CSV、metrics JSON/CSV 和报告图表。

标准 CSV 核心字段：

```text
time,x,y,z,x_ref,y_ref,z_ref,roll,pitch,yaw,u1,u2,u3,u4
```

官方变量映射见 `docs/index/variable_mapping.md`。

## 4. 当前 Smoke 指标

数据文件：

```text
results/smoke/example1_mcp/pid_baseline_smoke/logs/sysplorer_example1_pid_mcp_smoke_20260509.jsonl
results/smoke/example1_mcp/pid_baseline_smoke/raw/mworks_mcp_example1_pid_smoke.csv
results/smoke/example1_mcp/pid_baseline_smoke/metrics/mworks_mcp_example1_pid_smoke.json
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

当前 `QuadrotorExperiments.Example1ImprovedPID`、`QuadrotorExperiments.Example2ImprovedPID` 和 `QuadrotorExperiments.Example3ImprovedPID` 采用 MCP 参数搜索选出的统一 PID 参数集 `pos_kp_165_att_170`：将水平位置环 `PID3/PID4.KP` 从 `1.5` 提高到 `1.65`，将姿态内环 `PID5/PID6.KD` 从 `1.414` 提高到 `1.70`，其余高度环与 yaw 环参数保持官方基线不变。搜索脚本为 `scripts/tune_improved_pid_mcp.py`，搜索摘要见 `results/tuning/pid_search/summary/pid_tuning_summary.md`。

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

## 7. Enhanced PID P1 初步结果

`QuadrotorExperiments.Example1/2/3EnhancedPID` 在 `Example*_ImprovedPID` 的 MCP 参数搜索结果基础上，显式设置 PID 导数环节滤波时间常数，并收紧姿态参考限幅和姿态/yaw 控制限幅。该分支仍复用官方控制器结构，不修改官方模型本体，定位为 P1 控制器替换前的真实模型增强验证。

以下结果为 `source=MWORKS_MCP`、`evidence_level=real_sysplorer_mcp_full_enhanced_pid`：

| 场景 | controller | position_rmse_m | RMSE变化 | steady_state_error_m | max_tilt_rad | control_energy | control_smoothness | total_health_score |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| Example1 阶梯爬升 | baseline | 0.275253 | - | 0.111457 | 0.225729 | 39925.003500 | 111765.785252 | 52.464469 |
| Example1 阶梯爬升 | improved_pid | 0.269890 | +1.948% | 0.105559 | 0.273695 | 39926.972404 | 160907.671805 | 52.533227 |
| Example1 阶梯爬升 | enhanced_pid | 0.266250 | +3.270% | 0.103184 | 0.174432 | 39896.485617 | 13260.747831 | 55.422450 |
| Example2 螺旋爬升 | baseline | 0.487183 | - | 0.210149 | 0.330881 | 37306.013865 | 58929.532569 | 47.882655 |
| Example2 螺旋爬升 | improved_pid | 0.479834 | +1.508% | 0.190661 | 0.358260 | 37312.619310 | 86192.163000 | 48.025785 |
| Example2 螺旋爬升 | enhanced_pid | 0.487385 | -0.041% | 0.190195 | 0.294113 | 37305.466126 | 30076.777420 | 47.793116 |
| Example2 螺旋爬升 | helix_tuned_enhanced_pid | 0.475477 | +2.403% | 0.190195 | 0.353326 | 37311.173150 | 36103.346725 | 47.887799 |
| Example2 螺旋爬升 | helix_tuned_awff_pid | 0.474799 | +2.542% | 0.190196 | 0.353611 | 37324.236832 | 77900.174207 | 47.943117 |
| Example2 螺旋爬升 | helix_tuned_awff_sysblock | 0.474850 | +2.531% | 0.190196 | 0.353611 | 37310.845815 | 77894.127608 | 47.908065 |
| Example3 8字形 | baseline | 0.172311 | - | 0.068172 | 0.286482 | 95610.155697 | 73046.625676 | 60.505386 |
| Example3 8字形 | improved_pid | 0.167227 | +2.951% | 0.061940 | 0.295880 | 95611.212646 | 79889.936000 | 60.546610 |
| Example3 8字形 | enhanced_pid | 0.166670 | +3.274% | 0.061916 | 0.229426 | 95604.823917 | 27373.214928 | 60.281192 |

结论：Enhanced PID 在 Example1 和 Example3 上可以作为有效增强证据：Example1 RMSE 降低 `3.270%`，Example3 RMSE 降低 `3.274%`，同时最大倾角和控制平滑性明显改善。Example2 的问题已定位为螺旋轨迹 `t≈10 s` 横向圆轨迹启动时参考突变导致的姿态权限不足：原 Enhanced PID 将最大倾角压低到 `0.294113 rad`，但 RMSE 变差；`helix_tuned_enhanced_pid` 恢复 15° 横向姿态权限和 7.0 姿态控制限幅后，RMSE 降到 `0.475477 m`，相比 baseline 降低 `2.403%`，相比原 Improved PID 继续降低 `0.908%`，质量门禁为 `pass`。同一调优迁移到 AWFF PID 和 AWFF Sysblock 后，RMSE 分别为 `0.474799 m` 与 `0.474850 m`，均通过质量门禁。代价是最大倾角回升到约 `0.3536 rad`，但仍低于门禁 `0.45 rad`。

## 8. AWFF 独立控制器初步结果

`QuadrotorExperiments.Example1/2/3AntiWindupFeedforwardPID` 是项目自有控制器分支，不再只通过官方 `controller3_2` 的 PID 参数和 limiter modifier 实现增强。该模型在 `QuadrotorExperiments.Example*ProjectControllerBase` 中替换 `controller3_2` 的类型，但保持原官方接口兼容：输入仍为 `position_command[3]`、`position[3]`、`angle[3]`，输出仍为 `y`、`y1`、`y2`、`y3`，因此后续指标脚本和回放链路无需改变量映射。

控制器内部包含条件积分抗饱和、一阶滤波导数、竖直参考速度前馈、姿态参考限幅和电机命令绝对值限幅。以下结果为 `source=MWORKS_MCP`、`evidence_level=real_sysplorer_mcp_full_awff_pid`：

| 场景 | controller | position_rmse_m | RMSE变化 | max_position_error_m | steady_state_error_m | max_tilt_rad | control_energy | control_smoothness | total_health_score | quality_status |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| Example1 阶梯爬升 | awff_pid | 0.259914 | +5.573% | 1.241362 | 0.103229 | 0.174490 | 39906.269209 | 14346.392213 | 52.334668 | - |
| Example2 螺旋爬升 | awff_pid | 0.486621 | +0.115% | 3.005621 | 0.190196 | 0.294114 | 37318.468375 | 64715.876271 | 47.849265 | needs_iteration |
| Example3 8字形 | awff_pid | 0.164733 | +4.398% | 1.164021 | 0.061888 | 0.229670 | 95624.607100 | 62864.460905 | 60.418339 | pass |

AWFF PID 结论：Example1 和 Example3 均有明确 RMSE 收益，其中 Example3 8 字轨迹 RMSE 降低 `4.398%`，比 Enhanced PID 继续降低 `1.162%`。Example2 虽然 RMSE 相比 baseline 仅改善 `0.115%`，并且相对 Enhanced PID 只改善 `0.157%`，低于质量门禁 `0.500%`，因此仍标记为 `needs_iteration`。这说明当前 AWFF 结构的竖直前馈对阶梯/8字轨迹有效，但对螺旋轨迹的横向相位误差处理不足。

Sysblock 控制器仿真路线：

```text
已验证的高度环最小模型：
models/QuadrotorControllerBlocks/AWFF_PID_Sysblock_Demo.mo
AWFF_PID_Sysblock_Demo

正在推进的分层控制器模型：
models/QuadrotorControllerBlocks/AWFF_PositionOuterLoop_Sysblock.mo
AWFF_PositionOuterLoop_Sysblock
models/QuadrotorControllerBlocks/AWFF_AttitudeInnerLoop_Sysblock.mo
AWFF_AttitudeInnerLoop_Sysblock
models/QuadrotorControllerBlocks/AWFF_MotorMixer_Sysblock.mo
AWFF_MotorMixer_Sysblock

已完成独立组合仿真的控制器模型：
models/QuadrotorControllerBlocks/AWFF_FullController_Sysblock.mo
AWFF_FullController_Sysblock

models/QuadrotorControllerBlocks/AWFF_FullControllerFlatGraphical_Sysblock.mo
AWFF_FullControllerFlatGraphical_Sysblock

models/QuadrotorControllerBlocks/AWFF_FullControllerEquation_Sysblock.mo
AWFF_FullControllerEquation_Sysblock
```

说明：Sysblock 控制器文件不是单纯的截图支撑材料，而是控制器设计和审核的主实现路线之一。结构截图应来自 MWORKS.Sysblock/Sysplorer 打开的实际控制器模型窗口，用于证明模块连接、端口和信号流；正式控制器仿真结论必须以 `load_file`、`check_model`、必要时 `simulate_model` 的真实 MWORKS 证据为准，不使用手绘示意图或离线脚本替代。

可视化状态：`AWFF_PositionOuterLoop_Sysblock`、`AWFF_AttitudeInnerLoop_Sysblock`、`AWFF_MotorMixer_Sysblock` 和 `AWFF_FullController_Sysblock` 已补齐 `connect(...)` 对应的 `annotation(Line(...))` 图形连线注释。这样模型既保留原有逻辑连接，又能在 Sysblock/Sysplorer 画布中显示连接线，避免人工连线时出现“连接已存在但画布无可见线段”的审核问题。复测日志见 `results/model_checks/awff_sysblock/logs/sysplorer_sysblock_line_annotation_check_20260511.jsonl` 与 `results/model_checks/awff_sysblock/logs/sysplorer_sysblock_line_annotation_check_20260511_summary.json`。

当前阶段结论：Sysblock 证据链已从最小 demo 推进到分层控制器模型检查通过，并完成 `AWFF_FullController_Sysblock` 组合控制器独立仿真。2026-05-11 新增 `AWFF_FullControllerFlatGraphical_Sysblock` 单层扁平图形化控制器，静态契约检查显示其具备 8 个输入端口、4 个输出端口、46 个图形元素放置、60 条连接线且全部具备 `annotation(Line(...))` 可视化连线。`scripts/check_graphical_sysblock_mcp.py` 已对位置环、姿态环、电机分配、三层组合控制器和单层扁平图形化控制器共 5 个图形化 Sysblock 文件完成真实 MCP `load_file/check_model/simulate_model` 验收，日志见：

```text
results/model_checks/awff_sysblock/logs/sysplorer_graphical_sysblock_controller_check_20260511.jsonl
results/model_checks/awff_sysblock/logs/sysplorer_graphical_sysblock_controller_check_20260511_summary.json
results/model_checks/awff_sysblock/graphical_contract/graphical_awff_sysblock_contract_20260511.json
```

整机接入限制：三层组合图形化控制器和单层扁平图形化控制器作为 `controller3_2` 嵌入 `QuadrotorExperiments.Example1GraphicalAWFFSysblockClosedLoop` 时，当前 Sysplorer 编译器均在 `Sum.u1/u2/...` 等 Sysblock 内部多输入端口处报 `组件引用 ... 查找不到`。失败诊断日志保留为：

```text
results/model_checks/awff_sysblock/logs/sysplorer_graphical_sysblock_closed_loop_failed_hierarchical_20260511.jsonl
results/model_checks/awff_sysblock/logs/sysplorer_graphical_sysblock_closed_loop_failed_flat_20260511.jsonl
```

因此当前整机闭环主线继续使用等价扁平方程实现 `AWFF_FullControllerEquation_Sysblock` 接入 `QuadrotorExperiments.Example1/2/3AWFFSysblockClosedLoop`。该主线已经完成 Example1 0-1 s、5 s、10 s、20 s 渐进验证，以及 active official 场景中的 Example1 50 s、Example2 helix-tuned 50 s、Example3 120 s 全时长真实 Sysplorer MCP 闭环复测，均通过质量门禁，可作为当前 Sysblock 控制器整机仿真的主证据。图形化 Sysblock 文件用于控制器结构审核、截图和独立模型验证；Equation 版用于整机闭环性能结论，两者保持相同 `controller3_2` 外部端口语义。

2026-05-11 official Sysblock 闭环复测使用 `scripts/run_mworks_batch.py --reuse-mcp-process` 在同一个 Sysplorer MCP wrapper 进程中连续执行三条 active official Sysblock 场景，避免反复打开新窗口。共享初始化日志为：

```text
results/official/sysblock_closed_loop/logs/mcp_reuse_batch_official_sysblock_20260511.jsonl
```

单场景证据日志、raw CSV、metrics JSON/CSV、SVG 图表和 replay JSON 位于：

```text
results/official/example1_step/official_example1_awff_sysblock/
results/official/example2_helix/official_example2_awff_sysblock_helix_tuned/
results/official/example3_figure8/official_example3_awff_sysblock/
```

当前验证状态：重新登录激活后，四个 Sysblock 控制器文件均已完成真实 Sysplorer MCP 复测：

```text
results/model_checks/awff_sysblock/logs/sysplorer_sysblock_recheck_20260510.jsonl
results/model_checks/awff_sysblock/logs/sysplorer_sysblock_recheck_20260510_summary.json
```

```text
AWFF_PID_Sysblock_Demo: load_file/check_model/simulate_model/result_manager 通过，0-1 s 输出 101 行
AWFF_PositionOuterLoop_Sysblock: load_file/check_model 通过
AWFF_AttitudeInnerLoop_Sysblock: load_file/check_model 通过
AWFF_MotorMixer_Sysblock: load_file/check_model 通过
```

组合控制器新增验证：

```text
results/model_checks/awff_sysblock/logs/sysplorer_awff_full_sysblock_check_20260510.jsonl
results/model_checks/awff_sysblock/logs/sysplorer_awff_full_sysblock_check_20260510_summary.json

AWFF_FullController_Sysblock: load_file/check_model/simulate_model/result_manager 通过，0-1 s 输出 101 行
```

Sysblock 整机 smoke 新增验证：

```text
models/QuadrotorControllerBlocks/AWFF_FullControllerEquation_Sysblock.mo
models/QuadrotorExperiments/Example1AWFFSysblockClosedLoop.mo
models/QuadrotorExperiments/Example2AWFFSysblockClosedLoop.mo
models/QuadrotorExperiments/Example3AWFFSysblockClosedLoop.mo
scenarios/smoke/example1_awff_sysblock_mcp_smoke.yaml
scenarios/smoke/example2_awff_sysblock_mcp_smoke.yaml
scenarios/smoke/example3_awff_sysblock_mcp_smoke.yaml
scenarios/smoke/example1_awff_sysblock_mcp_5s.yaml
scenarios/smoke/example1_awff_sysblock_mcp_10s.yaml
scenarios/smoke/example1_awff_sysblock_mcp_20s.yaml
scenarios/official/example1_awff_sysblock.yaml
scenarios/official/example2_awff_sysblock.yaml
scenarios/official/example3_awff_sysblock.yaml
results/smoke/example1_step/awff_sysblock_smoke/logs/sysplorer_example1_awff_sysblock_smoke_20260510.jsonl
results/official/example1_step/official_example1_awff_sysblock/logs/sysplorer_example1_awff_sysblock_full_20260510.jsonl
results/smoke/example2_helix/awff_sysblock_smoke/logs/sysplorer_example2_awff_sysblock_smoke_20260510.jsonl
results/official/example2_helix/official_example2_awff_sysblock/logs/sysplorer_example2_awff_sysblock_full_20260510.jsonl
results/smoke/example3_figure8/awff_sysblock_smoke/logs/sysplorer_example3_awff_sysblock_smoke_20260510.jsonl
results/official/example3_figure8/official_example3_awff_sysblock/logs/sysplorer_example3_awff_sysblock_full_20260510.jsonl
results/smoke/example1_step/awff_sysblock_smoke/raw/official_example1_awff_sysblock_smoke.csv
results/official/example1_step/official_example1_awff_sysblock/raw/official_example1_awff_sysblock.csv
results/smoke/example2_helix/awff_sysblock_smoke/raw/official_example2_awff_sysblock_smoke.csv
results/official/example2_helix/official_example2_awff_sysblock/raw/official_example2_awff_sysblock.csv
results/smoke/example3_figure8/awff_sysblock_smoke/raw/official_example3_awff_sysblock_smoke.csv
results/official/example3_figure8/official_example3_awff_sysblock/raw/official_example3_awff_sysblock.csv
results/smoke/example1_step/awff_sysblock_smoke/metrics/official_example1_awff_sysblock_smoke.json
results/official/example1_step/official_example1_awff_sysblock/metrics/official_example1_awff_sysblock.json
results/smoke/example2_helix/awff_sysblock_smoke/metrics/official_example2_awff_sysblock_smoke.json
results/official/example2_helix/official_example2_awff_sysblock/metrics/official_example2_awff_sysblock.json
results/smoke/example3_figure8/awff_sysblock_smoke/metrics/official_example3_awff_sysblock_smoke.json
results/official/example3_figure8/official_example3_awff_sysblock/metrics/official_example3_awff_sysblock.json

QuadrotorExperiments.Example1AWFFSysblockClosedLoop: check_model/simulate_model/result_manager 通过，0-1 s 输出 101 行，50 s 输出 5001 行。
QuadrotorExperiments.Example2AWFFSysblockClosedLoop: check_model/simulate_model/result_manager 通过，0-1 s 输出 101 行，50 s 输出 5001 行。
QuadrotorExperiments.Example3AWFFSysblockClosedLoop: check_model/simulate_model/result_manager 通过，0-1 s 输出 101 行，120 s 输出 12001 行。
```

历史失败日志 `results/model_checks/awff_sysblock/logs/sysplorer_layered_sysblock_check_failed_20260510_summary.json` 和 `results/model_checks/awff_sysblock/logs/sysplorer_position_axis_check_failed_20260510_summary.json` 保留为授权/登录状态异常时的诊断记录，不再代表当前模型状态。

Sysblock 渐进验证指标如下，均为 `source=MWORKS_MCP`：

| 场景 | 时长/s | row_count | position_rmse_m | steady_state_error_m | max_tilt_rad | total_health_score |
|---|---:|---:|---:|---:|---:|---:|
| Sysblock smoke | 1.0 | 101 | 0.952870 | 0.855110 | 0.000000 | 28.844595 |
| Sysblock staged | 5.0 | 501 | 0.659238 | 0.474227 | 0.000000 | 32.857746 |
| Sysblock staged | 10.0 | 1001 | 0.473190 | 0.073953 | 0.000000 | 53.758541 |
| Sysblock staged | 20.0 | 2001 | 0.339268 | 0.015494 | 0.000000 | 54.844389 |
| Sysblock full Example1 | 50.0 | 5001 | 0.266217 | 0.103144 | 0.174437 | 55.423227 |
| Sysblock full Example2 | 50.0 | 5001 | 0.487394 | 0.190196 | 0.294113 | 47.793043 |
| Sysblock full Example3 | 120.0 | 12001 | 0.166669 | 0.061905 | 0.229426 | 60.281226 |

全时长对比结果：


| 场景 | controller | position_rmse_m | RMSE变化 | max_position_error_m | steady_state_error_m | max_tilt_rad | control_energy | control_smoothness | total_health_score |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Example1 阶梯爬升 | baseline | 0.275253 | - | 1.369402 | 0.111457 | 0.225729 | 39925.003500 | 111765.785252 | 52.464469 |
| Example1 阶梯爬升 | enhanced_pid | 0.266250 | +3.270% | 1.297338 | 0.103184 | 0.174432 | 39896.485617 | 13260.747831 | 55.422450 |
| Example1 阶梯爬升 | awff_pid | 0.259914 | +5.573% | 1.241362 | 0.103229 | 0.174490 | 39906.269209 | 14346.392213 | 52.334668 |
| Example1 阶梯爬升 | awff_sysblock | 0.266217 | +3.283% | 1.297165 | 0.103144 | 0.174437 | 39896.207840 | 13258.808831 | 55.423227 |
| Example2 螺旋爬升 | baseline | 0.487183 | - | 3.005422 | 0.210149 | 0.330881 | 37306.013865 | 58929.533000 | 47.882655 |
| Example2 螺旋爬升 | improved_pid | 0.479834 | +1.508% | 3.005563 | 0.190661 | 0.358260 | 37312.619310 | 86192.163000 | 48.025785 |
| Example2 螺旋爬升 | enhanced_pid | 0.487385 | -0.041% | 3.005600 | 0.190195 | 0.294113 | 37305.466126 | 30076.777420 | 47.793116 |
| Example2 螺旋爬升 | helix_tuned_enhanced_pid | 0.475477 | +2.403% | 3.006573 | 0.190195 | 0.353326 | 37311.173150 | 36103.346725 | 47.887799 |
| Example2 螺旋爬升 | awff_pid | 0.486621 | +0.115% | 3.005621 | 0.190196 | 0.294114 | 37318.468375 | 64715.876271 | 47.849265 |
| Example2 螺旋爬升 | helix_tuned_awff_pid | 0.474799 | +2.542% | 3.006664 | 0.190196 | 0.353611 | 37324.236832 | 77900.174207 | 47.943117 |
| Example2 螺旋爬升 | awff_sysblock | 0.487394 | -0.043% | 3.005597 | 0.190196 | 0.294113 | 37305.498694 | 30076.679195 | 47.793043 |
| Example2 螺旋爬升 | helix_tuned_awff_sysblock | 0.474850 | +2.531% | 3.006676 | 0.190196 | 0.353611 | 37310.845815 | 77894.127608 | 47.908065 |
| Example3 8字形 | baseline | 0.172311 | - | 1.217033 | 0.068172 | 0.286482 | 95610.155697 | 73046.626000 | 60.505386 |
| Example3 8字形 | improved_pid | 0.167227 | +2.951% | 1.185933 | 0.061940 | 0.295880 | 95611.212646 | 79889.936000 | 60.546610 |
| Example3 8字形 | enhanced_pid | 0.166670 | +3.274% | 1.187273 | 0.061916 | 0.229426 | 95604.823917 | 27373.214928 | 60.281192 |
| Example3 8字形 | awff_pid | 0.164733 | +4.398% | 1.164021 | 0.061888 | 0.229670 | 95624.607100 | 62864.460905 | 60.418339 |
| Example3 8字形 | awff_sysblock | 0.166669 | +3.274% | 1.187258 | 0.061905 | 0.229426 | 95604.798934 | 27372.840134 | 60.281226 |

结论：AWFF PID 在 Example1 相比官方 PID 的 RMSE 降低 `5.573%`，最大位置误差降低 `9.350%`，稳态误差降低 `7.382%`，最大倾角降低 `22.699%`；相比 Enhanced PID，RMSE 继续降低 `2.380%`。Example3 中 AWFF PID 是当前 PID 系列最优结果，RMSE 降低 `4.398%`。Example2 当前最优是 `helix_tuned_awff_pid`，RMSE `0.474799 m`，相比 baseline 降低 `2.542%`，相比原 Improved PID 继续降低 `1.049%`，质量门禁为 `pass`。

Sysblock 结论：`awff_sysblock` 在 Example1 50 s 全时长真实 Sysplorer MCP 仿真中达到与 `enhanced_pid` 基本一致的性能，并略高于其综合健康分。2026-05-11 复测结果显示，相比官方 PID，Sysblock 控制器 RMSE 降低 `3.283%`，稳态误差降低 `7.459%`，最大倾角降低 `22.723%`，控制平滑性降低 `88.137%`。在 Example3 8字轨迹中，RMSE 降低 `3.274%`、稳态误差降低 `9.193%`、最大倾角降低 `19.916%`、控制平滑性降低 `62.527%`，并通过 8 字形状检查。Example2 螺旋爬升中，active official 主线使用 `helix_tuned_awff_sysblock`，复测 RMSE `0.474850 m`，相比 baseline 降低 `2.531%`，相比原 Improved PID 继续降低 `1.039%`，质量门禁为 `pass`。这说明 Example2 的 Sysblock 主线已完成参数迁移，后续应把同样的场景化参数写入用户手册和演示脚本。鲁棒场景结论见第 9 节。

指标口径更新：当前 metrics JSON/CSV 已补充 `sample_rate_hz`、`control_energy_per_second`、`control_smoothness_per_second`、`constraint_violation_rate_hz`、`altitude_violation_rate_hz` 和 `tilt_violation_rate_hz`。当历史结果和新结果导出采样率不同，例如 `25001` 行与 `5001` 行并存时，报告优先比较 RMSE、稳态误差、最大倾角、恢复时间和每秒归一化指标；由采样点数量直接决定的原始 `constraint_violation_count` 只作为同采样率结果内的辅助信息。

## 9. P1 鲁棒场景与控制器消融

新增 `robust_mass20_example1` 场景用于真实模型鲁棒性验证：在 Example1 阶梯爬升任务中，将 `quadChassisTest17_1.body.m` 从官方 `0.159504 kg` 改为 `0.191405 kg`，即中心机体质量 +20%。该扰动模拟载荷变化或质量参数建模误差；路径、求解器、导出变量和仿真时长保持不变，因此可用于控制器消融对比。

模型替换位置：

```text
models/QuadrotorExperiments/package.mo
  QuadrotorExperiments.Example1Mass20PID
  QuadrotorExperiments.Example1Mass20ImprovedPID
  QuadrotorExperiments.Example1Mass20EnhancedPID
  QuadrotorExperiments.Example1Mass20AntiWindupFeedforwardPID
models/QuadrotorExperiments/Example1Mass20AWFFSysblockClosedLoop.mo
  QuadrotorExperiments.Example1Mass20AWFFSysblockClosedLoop
```

场景配置：

```text
scenarios/robustness/example1_mass20_pid_baseline.yaml
scenarios/robustness/example1_mass20_improved_pid.yaml
scenarios/robustness/example1_mass20_enhanced_pid.yaml
scenarios/robustness/example1_mass20_awff_pid.yaml
scenarios/robustness/example1_mass20_awff_sysblock.yaml
```

以下结果均为 `source=MWORKS_MCP`、`evidence_level=real_sysplorer_mcp_robust_mass20_ablation`，每条仿真均完成 `check_model ok`、`simulate_model ok`，导出 `5001` 行 50 s raw CSV：

| 场景 | controller | position_rmse_m | RMSE变化 | steady_state_error_m | 稳态误差变化 | max_tilt_rad | 最大倾角变化 | control_energy_per_second | control_smoothness_per_second | total_health_score |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| +20% 质量摄动 Example1 | baseline | 0.291441 | - | 0.111428 | - | 0.241303 | - | 953.889949 | 2367.712444 | 51.820711 |
| +20% 质量摄动 Example1 | improved_pid | 0.286484 | +1.701% | 0.105508 | +5.313% | 0.289414 | -19.938% | 953.929869 | 3618.603060 | 51.886273 |
| +20% 质量摄动 Example1 | enhanced_pid | 0.282610 | +3.030% | 0.103144 | +7.434% | 0.174124 | +27.840% | 953.305878 | 270.716005 | 52.444636 |
| +20% 质量摄动 Example1 | awff_pid | 0.276253 | +5.211% | 0.103142 | +7.435% | 0.174106 | +27.847% | 953.596290 | 279.280619 | 51.813783 |
| +20% 质量摄动 Example1 | awff_sysblock | 0.282785 | +2.970% | 0.103112 | +7.463% | 0.174122 | +27.841% | 953.303498 | 266.591707 | 52.443573 |

消融结论：在同一 +20% 质量摄动下，Improved PID 主要改善轨迹 RMSE 和稳态误差，但最大倾角增加 `19.938%`，说明单纯增益搜索会引入姿态代价。AWFF PID 的 RMSE 改善最大，达到 `5.211%`，质量门禁为 `pass`；Enhanced PID 与 AWFF Sysblock 在稳态误差、最大倾角、每秒控制能量和每秒控制平滑性上更稳。AWFF Sysblock 相比 baseline 的 RMSE 降低 `2.970%`，稳态误差降低 `7.463%`，最大倾角降低 `27.841%`，`control_smoothness_per_second` 降低 `88.741%`。该结果可作为 Sysblock 控制器质量参数鲁棒性的正式证据。



新增 `robust_wind_gust_example1` 场景用于外部扰动鲁棒性验证：在 Example1 阶梯爬升任务中，将一个世界坐标系横向阵风力接入 `quadChassisTest17_1.body.frame_b`。阵风在 `15-19 s` 生效，基准力为 `Fx=0.22 N, Fy=-0.10 N`，并叠加 `1.2 Hz` 的小幅正弦脉动。该场景不改官方旋翼升力方程，扰动通过项目派生模型额外接入机体。

模型替换位置：

```text
models/QuadrotorExperiments/package.mo
  QuadrotorExperiments.Example1WindGustBase
  QuadrotorExperiments.Example1WindGustPID
  QuadrotorExperiments.Example1WindGustImprovedPID
  QuadrotorExperiments.Example1WindGustEnhancedPID
  QuadrotorExperiments.Example1WindGustAntiWindupFeedforwardPID
models/QuadrotorExperiments/Example1WindGustAWFFSysblockClosedLoop.mo
  QuadrotorExperiments.Example1WindGustAWFFSysblockClosedLoop
```

场景配置：

```text
scenarios/robustness/example1_wind_gust_pid_baseline.yaml
scenarios/robustness/example1_wind_gust_improved_pid.yaml
scenarios/robustness/example1_wind_gust_enhanced_pid.yaml
scenarios/robustness/example1_wind_gust_awff_pid.yaml
scenarios/robustness/example1_wind_gust_awff_sysblock.yaml
```

以下结果均为 `source=MWORKS_MCP`、`evidence_level=real_sysplorer_mcp_robust_wind_gust_ablation`，每条仿真均完成 `check_model ok`、`simulate_model ok`，导出 `25001` 行 50 s raw CSV：

| 场景 | controller | position_rmse_m | RMSE变化 | disturbance_peak_error_m | 峰值误差变化 | disturbance_recovery_time_s | max_tilt_rad | 最大倾角变化 | control_smoothness_per_second | total_health_score |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 15-19s 横向阵风 Example1 | baseline | 0.334706 | - | 0.753994 | - | 3.460 | 0.228849 | - | 2757.199851 | 51.989919 |
| 15-19s 横向阵风 Example1 | improved_pid | 0.322116 | +3.762% | 0.699255 | +7.260% | 3.296 | 0.278640 | -21.757% | 3987.595477 | 52.117069 |
| 15-19s 横向阵风 Example1 | enhanced_pid | 0.318260 | +4.914% | 0.696234 | +7.661% | 3.242 | 0.196606 | +14.089% | 276.951339 | 55.004469 |
| 15-19s 横向阵风 Example1 | awff_pid | 0.313084 | +6.460% | 0.697626 | +7.477% | 3.242 | 0.196916 | +13.953% | 291.266878 | 51.903696 |
| 15-19s 横向阵风 Example1 | awff_sysblock | 0.318224 | +4.924% | 0.696309 | +7.652% | 3.250 | 0.196645 | +14.072% | 269.391389 | 55.001701 |

消融结论：在同一横向阵风扰动下，Improved PID 可降低 RMSE 和扰动窗口峰值误差，但最大倾角增加 `21.757%`，说明仅靠增益搜索仍会提高姿态代价。AWFF PID 的 RMSE 改善最大，达到 `6.460%`，质量门禁为 `pass`；AWFF Sysblock 相比 baseline 的 RMSE 降低 `4.924%`，扰动窗口峰值误差降低 `7.652%`，恢复时间从 `3.460 s` 缩短到 `3.250 s`，最大倾角降低 `14.072%`，`control_smoothness_per_second` 降低 `90.230%`。因此风扰场景可以作为 Sysblock 控制器外部扰动鲁棒性的正式证据。注意：该组历史结果存在 `25001` 行与 `5001` 行并存；报告已使用每秒归一化指标避免 sample-count 直接影响。



新增 `robust_rotor1_loss15_example1` 场景用于执行器退化鲁棒性验证：在 Example1 阶梯爬升任务中，将 1 号旋翼对应升力增益 `quadChassisTest17_1.gain2.k` 从官方 `0.002` 改为 `0.0017`，等效为单旋翼升力效率下降到 `85%`。该场景不修改控制器接口，扰动直接作用在官方机体升力链路上。

模型替换位置：

```text
models/QuadrotorExperiments/package.mo
  QuadrotorExperiments.Example1Rotor1Loss15PID
  QuadrotorExperiments.Example1Rotor1Loss15ImprovedPID
  QuadrotorExperiments.Example1Rotor1Loss15EnhancedPID
  QuadrotorExperiments.Example1Rotor1Loss15AntiWindupFeedforwardPID
models/QuadrotorExperiments/Example1Rotor1Loss15AWFFSysblockClosedLoop.mo
  QuadrotorExperiments.Example1Rotor1Loss15AWFFSysblockClosedLoop
```

场景配置：

```text
scenarios/robustness/example1_rotor1_loss15_pid_baseline.yaml
scenarios/robustness/example1_rotor1_loss15_improved_pid.yaml
scenarios/robustness/example1_rotor1_loss15_enhanced_pid.yaml
scenarios/robustness/example1_rotor1_loss15_awff_pid.yaml
scenarios/robustness/example1_rotor1_loss15_awff_sysblock.yaml
```

以下结果均为 `source=MWORKS_MCP`、`evidence_level=real_sysplorer_mcp_robust_rotor_loss_ablation`，每条仿真均完成 `check_model ok`、`simulate_model ok`，导出 `5001` 行 50 s raw CSV：

| 场景 | controller | position_rmse_m | RMSE变化 | steady_state_error_m | max_tilt_rad | 最大倾角变化 | constraint_violation_rate_hz | control_smoothness_per_second | total_health_score |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 1号旋翼效率85% Example1 | baseline | 0.392120 | - | 0.286884 | 0.211287 | - | 1.340 | 2167.565293 | 35.625782 |
| 1号旋翼效率85% Example1 | improved_pid | 0.371435 | +5.275% | 0.265699 | 0.254032 | -20.231% | 1.340 | 3128.825699 | 35.884927 |
| 1号旋翼效率85% Example1 | enhanced_pid | 0.368251 | +6.087% | 0.265416 | 0.174661 | +17.335% | 1.300 | 265.211626 | 36.050556 |
| 1号旋翼效率85% Example1 | awff_pid | 0.364823 | +6.961% | 0.265442 | 0.174642 | +17.344% | 1.240 | 278.351622 | 36.184951 |
| 1号旋翼效率85% Example1 | awff_sysblock | 0.369058 | +5.881% | 0.265419 | 0.174661 | +17.335% | 1.300 | 264.978146 | 36.043895 |

消融结论：单旋翼效率退化场景明显比质量摄动和横向阵风更困难，baseline 的 RMSE 增至 `0.392120 m`，健康分降至 `35.625782`。Improved PID 可降低 RMSE，但最大倾角增加 `20.231%`；AWFF PID 相比 baseline 的 RMSE 降低 `6.961%`，约束违规率降到 `1.240 Hz`，但健康分仍只有 `36.184951`，质量门禁为 `needs_iteration`。AWFF Sysblock 相比 baseline 的 RMSE 降低 `5.881%`，稳态误差降低 `7.482%`，最大倾角降低 `17.335%`，`control_smoothness_per_second` 降低 `87.775%`。该场景可作为“已执行真实退化工况消融”的证据，但不能包装成已解决执行器故障；后续应优先补旋翼效率估计、控制分配重构或故障容错限幅，再重新复测。

### 9.4 L1-inspired 残差补偿控制器首轮消融

`l1_residual_sysblock` 在 `AWFF_FullControllerEquation_Sysblock` 基础上加入低通残差估计和有界补偿，不改变 `controller3_2` 的输入输出接口。当前实现文件和场景为：

```text
models/QuadrotorControllerBlocks/AWFF_L1ResidualControllerEquation_Sysblock.mo
models/QuadrotorExperiments/Example1L1SysblockClosedLoop.mo
models/QuadrotorExperiments/Example3L1SysblockClosedLoop.mo
models/QuadrotorExperiments/Example1Mass20L1SysblockClosedLoop.mo
models/QuadrotorExperiments/Example1WindGustL1SysblockClosedLoop.mo
models/QuadrotorExperiments/Example1Rotor1Loss15L1SysblockClosedLoop.mo
controllers/l1_residual_sysblock/default.yaml
scenarios/official/example1_l1_residual_sysblock.yaml
scenarios/official/example3_l1_residual_sysblock.yaml
scenarios/robustness/example1_mass20_l1_residual_sysblock.yaml
scenarios/robustness/example1_wind_gust_l1_residual_sysblock.yaml
scenarios/robustness/example1_rotor1_loss15_l1_residual_sysblock.yaml
```

以下结果均为 `source=MWORKS_MCP`，每条正式场景均完成 `check_model/simulate_model/result_manager` 并导出 raw CSV。Example3 为 `12001` 行 120 s 8 字形数据，其余 Example1 派生场景为 `5001` 行 50 s 数据。

| 场景 | controller | status | position_rmse_m | RMSE变化 | disturbance_peak_error_m | 峰值误差变化 | disturbance_recovery_time_s | steady_state_error_m | max_tilt_rad | control_smoothness_per_second | total_health_score |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Example1 阶梯爬升 | awff_sysblock | pass | 0.266217 | - | 0.075009 | - | 3.030 | 0.103144 | 0.174437 | 265.176177 | 55.423227 |
| Example1 阶梯爬升 | l1_residual_sysblock | pass | 0.243837 | +8.406% | 0.066028 | +11.974% | 2.700 | 0.074804 | 0.205017 | 275.737107 | 55.816606 |
| Example3 8字形 | awff_sysblock | pass | 0.166669 | - | 0.098743 | - | 0.000 | 0.061905 | 0.229426 | 228.107001 | 60.281226 |
| Example3 8字形 | l1_residual_sysblock | pass | 0.152236 | +8.660% | 0.070219 | +28.887% | 0.000 | 0.049720 | 0.241367 | 227.238718 | 60.201910 |
| 质量+20% Example1 | awff_sysblock | pass | 0.282785 | - | 0.083369 | - | 3.030 | 0.103112 | 0.174122 | 266.591707 | 52.443573 |
| 质量+20% Example1 | l1_residual_sysblock | pass | 0.260769 | +7.785% | 0.072645 | +12.864% | 2.700 | 0.074850 | 0.204374 | 276.357145 | 55.360839 |
| 15-19s 横向阵风 Example1 | awff_sysblock | pass | 0.318224 | - | 0.696413 | - | 3.250 | 0.103106 | 0.196645 | 269.391389 | 55.001701 |
| 15-19s 横向阵风 Example1 | l1_residual_sysblock | pass | 0.278231 | +12.568% | 0.541739 | +22.210% | 2.850 | 0.074807 | 0.204982 | 279.930682 | 55.537737 |
| 1号旋翼效率85% Example1 | awff_sysblock | needs_iteration | 0.369058 | - | 0.261832 | - | 13.760 | 0.265419 | 0.174661 | 264.978146 | 36.043895 |
| 1号旋翼效率85% Example1 | l1_residual_sysblock | needs_iteration | 0.319854 | +13.332% | 0.213491 | +18.463% | 13.330 | 0.214432 | 0.205298 | 275.174488 | 36.803366 |
| 1号旋翼效率85% Example1 | l1_fault_allocation_sysblock | pass | 0.244340 | +33.793% | 0.067839 | +74.091% | 2.730 | 0.082946 | 0.205545 | 292.033122 | 55.816623 |
| 1号旋翼效率85% Example1 | l1_online_fault_allocation_sysblock | pass | 0.260671 | +29.363% | 0.110916 | +57.638% | 2.560 | 0.117032 | 0.205199 | 283.382251 | 51.143948 |
| 1号旋翼效率85% Example1 | l1_multi_fault_isolation_sysblock | pass | 0.267917 | +27.405% | 0.110916 | +57.637% | 4.910 | 0.140601 | 0.204720 | 284.641308 | 50.984182 |

消融结论：L1-inspired 残差补偿在 Example1、Example3 8 字形、质量 +20% 和横向阵风四类正式场景中均通过质量门，并稳定降低 RMSE、稳态误差和扰动窗口峰值误差。横向阵风中 `position_rmse_m` 降低 `12.568%`、峰值误差降低 `22.210%`；8 字形中 RMSE 降低 `8.660%`。代价是 Example1 派生场景最大倾角约增加到 `0.205 rad`，控制平滑性约增加 `3.9%`。旋翼退化场景中，单独 L1 仍为 `needs_iteration`；加入已知效率 `eta=0.85` 的混合控制分配补偿后，`l1_fault_allocation_sysblock` 通过质量门，RMSE 相比 AWFF Sysblock 降低 `33.793%`，稳态误差降低 `68.749%`，扰动窗口峰值误差降低 `74.091%`，恢复时间从 `13.760 s` 缩短到 `2.730 s`。进一步加入残差驱动在线效率估计后，`l1_online_fault_allocation_sysblock` 在不直接读取真实 `eta=0.85` 的条件下通过质量门，导出 `eta_hat` 诊断列，末值约 `0.904`，RMSE 相比 AWFF Sysblock 降低 `29.363%`。多旋翼隔离雏形 `l1_multi_fault_isolation_sysblock` 输出 `eta_hat1..4` 与 `fault_index`，在 rotor1 退化场景中 `5-50 s` 的 `fault_index=1` 正确率为 `100%`，并保持质量门 `pass`。该结果可作为“多旋翼故障隔离结构已接入并在 rotor1 场景验证”的证据；完整四旋翼故障隔离仍需补 rotor2/3/4 退化场景后才能声明。

## 10. 当前图表

已生成图表：

```text
results/official/example1_step/*/figures
results/official/example2_helix/*/figures
results/official/example3_figure8/*/figures
results/robustness/mass20_example1/*/figures
results/robustness/wind_gust_example1/*/figures
results/robustness/rotor1_loss15_example1/*/figures
```

已生成 replay JSON：

```text
results/official/example1_step/official_example1_pid_baseline/replay/official_example1_pid_baseline.json
results/official/example1_step/official_example1_improved_pid/replay/official_example1_improved_pid.json
results/official/example1_step/official_example1_enhanced_pid/replay/official_example1_enhanced_pid.json
results/official/example1_step/official_example1_awff_pid/replay/official_example1_awff_pid.json
results/official/example2_helix/official_example2_pid_baseline/replay/official_example2_pid_baseline.json
results/official/example2_helix/official_example2_improved_pid/replay/official_example2_improved_pid.json
results/official/example3_figure8/official_example3_pid_baseline/replay/official_example3_pid_baseline.json
results/official/example3_figure8/official_example3_improved_pid/replay/official_example3_improved_pid.json
results/official/example1_step/official_example1_awff_sysblock/replay/official_example1_awff_sysblock.json
results/official/example2_helix/official_example2_awff_sysblock/replay/official_example2_awff_sysblock.json
results/official/example3_figure8/official_example3_awff_sysblock/replay/official_example3_awff_sysblock.json
results/robustness/mass20_example1/robust_mass20_example1_pid_baseline/replay/robust_mass20_example1_pid_baseline.json
results/robustness/mass20_example1/robust_mass20_example1_improved_pid/replay/robust_mass20_example1_improved_pid.json
results/robustness/mass20_example1/robust_mass20_example1_enhanced_pid/replay/robust_mass20_example1_enhanced_pid.json
results/robustness/mass20_example1/robust_mass20_example1_awff_sysblock/replay/robust_mass20_example1_awff_sysblock.json
results/robustness/wind_gust_example1/robust_wind_gust_example1_pid_baseline/replay/robust_wind_gust_example1_pid_baseline.json
results/robustness/wind_gust_example1/robust_wind_gust_example1_improved_pid/replay/robust_wind_gust_example1_improved_pid.json
results/robustness/wind_gust_example1/robust_wind_gust_example1_enhanced_pid/replay/robust_wind_gust_example1_enhanced_pid.json
results/robustness/wind_gust_example1/robust_wind_gust_example1_awff_sysblock/replay/robust_wind_gust_example1_awff_sysblock.json
results/robustness/rotor1_loss15_example1/robust_rotor1_loss15_example1_pid_baseline/replay/robust_rotor1_loss15_example1_pid_baseline.json
results/robustness/rotor1_loss15_example1/robust_rotor1_loss15_example1_improved_pid/replay/robust_rotor1_loss15_example1_improved_pid.json
results/robustness/rotor1_loss15_example1/robust_rotor1_loss15_example1_enhanced_pid/replay/robust_rotor1_loss15_example1_enhanced_pid.json
results/robustness/rotor1_loss15_example1/robust_rotor1_loss15_example1_awff_sysblock/replay/robust_rotor1_loss15_example1_awff_sysblock.json
results/robustness/rotor1_loss15_example1/robust_rotor1_loss15_example1_l1_fault_allocation_sysblock/replay/robust_rotor1_loss15_example1_l1_fault_allocation_sysblock.json
results/robustness/rotor1_loss15_example1/robust_rotor1_loss15_example1_l1_online_fault_allocation_sysblock/replay/robust_rotor1_loss15_example1_l1_online_fault_allocation_sysblock.json
results/official/example1_step/official_example1_l1_residual_sysblock/replay/official_example1_l1_residual_sysblock.json
results/robustness/wind_gust_example1/robust_wind_gust_example1_l1_residual_sysblock/replay/robust_wind_gust_example1_l1_residual_sysblock.json
results/official/example1_step/reference_official_example1/replay/reference_official_example1.json
results/official/example2_helix/reference_official_example2/replay/reference_official_example2.json
results/official/example3_figure8/reference_official_example3/replay/reference_official_example3.json
```

其中 `results/{group}/{scene}/{experiment}/replay/*.json` 来自真实 Sysplorer MCP raw CSV 或官方参考轨迹 CSV，可作为后续 Gazebo/视频展示输入；它不是在线仿真结果。

## 11. 扩展场景状态

此前用于横向展示的 Python/Julia 离线仿真结果已清理。当前报告结论只引用真实 Sysplorer/MWORKS MCP 证据。

质量 +20% 参数摄动、15-19 s 横向阵风扰动、1 号旋翼 85% 效率退化、Example1 AWFF 独立控制器替换、Example1/2/3 AWFF Sysblock 官方场景、L1 residual Sysblock 消融，以及已知效率退化控制分配补偿均已完成真实 MWORKS MCP 闭环。规划和编队仍保留在 `Design/` 中作为下一阶段实现目标，但必须完成以下闭环后才能进入本报告的性能结论：

```text
MWORKS/Sysplorer 模型或派生模型
→ check_model 成功
→ simulate_model 完整运行
→ result_manager 导出 raw CSV
→ metrics/figures/replay 可复现
→ source=MWORKS_MCP 或 source=MWORKS_GUI
```

下一阶段优先任务：

1. 将 Example2 helix tuned AWFF PID / AWFF Sysblock 写入用户手册运行流程和演示素材清单；
2. 为旋翼退化场景补 `eta` 在线估计或故障检测模块，形成从检测到控制分配重构的完整闭环；
3. INDI 或线性 MPC 外环的最小可运行模型；
4. 对已通过的 L1 residual / fault allocation 场景继续降低高频控制动作和最大倾角。

更新状态：已补充 AWFF PID 与 AWFF Sysblock 的质量 +20%、横向阵风和 1 号旋翼 85% 效率退化派生模型及场景配置：

```text
QuadrotorExperiments.Example1Mass20AntiWindupFeedforwardPID
QuadrotorExperiments.Example1WindGustAntiWindupFeedforwardPID
QuadrotorExperiments.Example1Rotor1Loss15AntiWindupFeedforwardPID
QuadrotorExperiments.Example1Mass20AWFFSysblockClosedLoop
QuadrotorExperiments.Example1WindGustAWFFSysblockClosedLoop
QuadrotorExperiments.Example1Rotor1Loss15AWFFSysblockClosedLoop

scenarios/robustness/example1_mass20_awff_pid.yaml
scenarios/robustness/example1_wind_gust_awff_pid.yaml
scenarios/robustness/example1_rotor1_loss15_awff_pid.yaml
scenarios/robustness/example1_mass20_awff_sysblock.yaml
scenarios/robustness/example1_wind_gust_awff_sysblock.yaml
scenarios/robustness/example1_rotor1_loss15_awff_sysblock.yaml
```

授权恢复后，三条 AWFF PID 与三条 AWFF Sysblock 鲁棒场景均已完成 `check_model/simulate_model/result_manager`，导出 `5001` 行 50 s raw CSV，并进入本报告性能结论。其中质量摄动 AWFF PID、横向阵风 AWFF PID 质量门禁为 `pass`，旋翼退化 AWFF PID 为 `needs_iteration`。早期授权失效导致的失败日志只保留为诊断记录，不再代表当前模型状态。

L1 residual Sysblock 已完成以下真实 MCP 证据：

```text
QuadrotorExperiments.Example1L1SysblockClosedLoop
QuadrotorExperiments.Example3L1SysblockClosedLoop
QuadrotorExperiments.Example1Mass20L1SysblockClosedLoop
QuadrotorExperiments.Example1WindGustL1SysblockClosedLoop
QuadrotorExperiments.Example1Rotor1Loss15L1SysblockClosedLoop

scenarios/smoke/example1_l1_residual_sysblock_mcp_smoke.yaml
scenarios/smoke/example1_wind_gust_l1_residual_sysblock_mcp_smoke.yaml
scenarios/official/example1_l1_residual_sysblock.yaml
scenarios/official/example3_l1_residual_sysblock.yaml
scenarios/robustness/example1_mass20_l1_residual_sysblock.yaml
scenarios/robustness/example1_wind_gust_l1_residual_sysblock.yaml
scenarios/robustness/example1_rotor1_loss15_l1_residual_sysblock.yaml

results/smoke/example1_step/l1_residual_sysblock_smoke/logs/sysplorer_example1_l1_residual_sysblock_smoke_20260510.jsonl
results/smoke/robustness/wind_gust_example1_l1_residual_sysblock_smoke/logs/sysplorer_robust_wind_gust_example1_l1_residual_sysblock_smoke_20260510.jsonl
results/official/example1_step/official_example1_l1_residual_sysblock/logs/sysplorer_example1_l1_residual_sysblock_full_20260510.jsonl
results/official/example3_figure8/official_example3_l1_residual_sysblock/logs/sysplorer_example3_l1_residual_sysblock_full_20260511.jsonl
results/robustness/mass20_example1/robust_mass20_example1_l1_residual_sysblock/logs/sysplorer_robust_mass20_example1_l1_residual_sysblock_20260511.jsonl
results/robustness/wind_gust_example1/robust_wind_gust_example1_l1_residual_sysblock/logs/sysplorer_robust_wind_gust_example1_l1_residual_sysblock_20260510.jsonl
results/robustness/rotor1_loss15_example1/robust_rotor1_loss15_example1_l1_residual_sysblock/logs/sysplorer_robust_rotor1_loss15_example1_l1_residual_sysblock_20260511.jsonl
```

已知效率退化控制分配补偿已完成以下真实 MCP 证据：

```text
QuadrotorExperiments.Example1Rotor1Loss15L1FaultAllocationSysblockClosedLoop

scenarios/robustness/example1_rotor1_loss15_l1_fault_allocation_sysblock.yaml

results/robustness/rotor1_loss15_example1/robust_rotor1_loss15_example1_l1_fault_allocation_sysblock/logs/sysplorer_robust_rotor1_loss15_example1_l1_fault_allocation_sysblock_20260511.jsonl
```

在线效率估计控制分配补偿已完成以下真实 MCP 证据：

```text
QuadrotorExperiments.Example1Rotor1Loss15L1OnlineFaultAllocationSysblockClosedLoop

scenarios/robustness/example1_rotor1_loss15_l1_online_fault_allocation_sysblock.yaml

results/robustness/rotor1_loss15_example1/robust_rotor1_loss15_example1_l1_online_fault_allocation_sysblock/logs/sysplorer_robust_rotor1_loss15_example1_l1_online_fault_allocation_sysblock_20260511.jsonl
```

多旋翼故障隔离与控制分配补偿已完成 rotor1-4 四个方向的真实 MCP 证据，全部为 50 s Sysplorer 闭环仿真：

| 退化旋翼 | 场景文件 | RMSE (m) | 稳态误差 (m) | 恢复时间 (s) | `fault_index` 正确率 |
|---|---|---:|---:|---:|---:|
| rotor1 | `scenarios/robustness/example1_rotor1_loss15_l1_multi_fault_isolation_sysblock.yaml` | 0.2679 | 0.1406 | 4.91 | 100% |
| rotor2 | `scenarios/robustness/example1_rotor2_loss15_l1_multi_fault_isolation_sysblock.yaml` | 0.2689 | 0.1471 | 4.91 | 100% |
| rotor3 | `scenarios/robustness/example1_rotor3_loss15_l1_multi_fault_isolation_sysblock.yaml` | 0.2684 | 0.1449 | 4.56 | 100% |
| rotor4 | `scenarios/robustness/example1_rotor4_loss15_l1_multi_fault_isolation_sysblock.yaml` | 0.2695 | 0.1423 | 4.56 | 100% |

对应证据目录位于 `results/robustness/rotor{1..4}_loss15_example1/robust_rotor{1..4}_loss15_example1_l1_multi_fault_isolation_sysblock/`，其中包含 `raw/`、`metrics/`、`figures/`、`replay/` 和 `logs/`。`figures/` 中除轨迹、误差和指标图外，还包含 `*_eta_hat_diagnostics.svg` 与 `*_fault_index_diagnostics.svg`，用于报告和演示视频中展示在线效率估计与故障编号锁存过程。该组结果可以支撑“四旋翼持续单故障隔离验证已完成”的表述；不支撑瞬态故障、复合多故障或故障切换声明。

## 12. 结论约束

1. 不使用 smoke 数据做完整控制性能结论。
2. 不使用离线脚本结果作为 MWORKS 控制性能结论。
3. 报告中的每张图必须能追溯到 `results/{group}/{scene}/{experiment}/raw/` 和生成脚本。
4. 完整 baseline 与优化控制器必须使用同一场景、同一时长和同一指标脚本。
