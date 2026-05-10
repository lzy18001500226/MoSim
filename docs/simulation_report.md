# 仿真分析报告

> 当前 smoke 数据均只覆盖 0-1 s，用于验证 MCP 结果读取、CSV 导出和指标计算链路。完整性能结论只引用 `official_example*_*.csv` 对应的全时长真实 Sysplorer MCP 结果。

## 1. 报告范围

本报告记录当前工程已经可复现的仿真数据链路、官方参考轨迹、指标计算方法和图表生成方式。控制器性能对比只引用已保存 raw CSV、metrics JSON/CSV、MCP JSONL 日志和 SVG 图表的实验。

证据主线说明：赛题实现目标应以 **MWORKS.Sysblock 控制器仿真为主**。当前报告中的完整性能表包含真实 Sysplorer MCP / Modelica 派生模型闭环仿真，以及 `AWFF_FullControllerEquation_Sysblock` 接入官方 Example1/2/3 的全时长 Sysblock 控制器闭环证据。Sysblock 当前已完成 AWFF PID 高度环最小 demo、三段分层控制器、组合控制器 `AWFF_FullController_Sysblock` 的真实 MCP 验证，并完成 Example1 50 s、Example2 50 s、Example3 120 s 整机仿真；P1 创新控制器方向已完成 `AWFF_L1ResidualControllerEquation_Sysblock` 在 Example1 与横向阵风 Example1 中的首轮真实 MCP 消融。

当前已完成的可复现资产：

```text
官方 Example1/2/3 参考轨迹 CSV
官方 Example1/2/3 完整 PID baseline CSV、指标和图表
官方 Example1/2/3 MCP 参数搜索型 Improved PID CSV、指标和图表
官方 Example1 Enhanced PID 完整 CSV、指标、图表和 replay JSON
官方 Example1 AWFF 独立控制器完整 CSV、指标、图表和 replay JSON
Example1/2/3 AWFF Sysblock 整机完整 CSV、指标、图表和 replay JSON
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
| 螺旋爬升 AWFF Sysblock | `QuadrotorExperiments.Example2AWFFSysblockClosedLoop` | 50 s | 项目 Sysblock 控制器整机闭环已通过 Sysplorer MCP 仿真 |
| 8字形运动 | `QuadrotorModel.Examples.Example3` | 120 s | 完整 PID baseline 和 MCP 参数搜索型 Improved PID 已通过 Sysplorer MCP 仿真 |
| 8字形运动 AWFF Sysblock | `QuadrotorExperiments.Example3AWFFSysblockClosedLoop` | 120 s | 项目 Sysblock 控制器整机闭环已通过 Sysplorer MCP 仿真 |
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

## 7. Enhanced PID P1 初步结果

`QuadrotorExperiments.Example1EnhancedPID` 在 `Example1ImprovedPID` 的 MCP 参数搜索结果基础上，显式设置 PID 导数环节滤波时间常数，并收紧姿态参考限幅和姿态/yaw 控制限幅。该分支仍复用官方控制器结构，不修改官方模型本体，定位为 P1 控制器替换前的真实模型增强验证。

以下结果为 `source=MWORKS_MCP`、`evidence_level=real_sysplorer_mcp_full_enhanced_pid`：

| 场景 | controller | position_rmse_m | RMSE变化 | steady_state_error_m | max_tilt_rad | control_energy | control_smoothness | total_health_score |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| Example1 阶梯爬升 | baseline | 0.275253 | - | 0.111457 | 0.225729 | 39925.003500 | 111765.785252 | 52.464469 |
| Example1 阶梯爬升 | improved_pid | 0.269890 | +1.948% | 0.105559 | 0.273695 | 39926.972404 | 160907.671805 | 52.533227 |
| Example1 阶梯爬升 | enhanced_pid | 0.266250 | +3.270% | 0.103184 | 0.174432 | 39896.485617 | 13260.747831 | 55.422450 |

结论：Enhanced PID 在 Example1 完整 50 s 真实 Sysplorer MCP 仿真中，相比官方 PID 的 RMSE 降低 `3.270%`，稳态误差降低 `7.423%`，最大倾角降低 `22.733%`，控制平滑性指标明显改善；相比参数搜索型 Improved PID，RMSE 继续降低 `1.348%`，最大倾角降低 `36.268%`。该结果可以作为 P1 控制器增强的第一条真实证据。限制是：当前 Enhanced PID 仍通过参数化官方 PID 与限幅块实现，抗积分饱和和参考前馈尚未替换为独立控制器内部逻辑。

## 8. AWFF 独立控制器初步结果

`QuadrotorExperiments.Example1AntiWindupFeedforwardPID` 是项目自有控制器分支，不再只通过官方 `controller3_2` 的 PID 参数和 limiter modifier 实现增强。该模型在 `QuadrotorExperiments.Example1ProjectControllerBase` 中替换 `controller3_2` 的类型，但保持原官方接口兼容：输入仍为 `position_command[3]`、`position[3]`、`angle[3]`，输出仍为 `y`、`y1`、`y2`、`y3`，因此后续指标脚本和回放链路无需改变量映射。

控制器内部包含条件积分抗饱和、一阶滤波导数、竖直参考速度前馈、姿态参考限幅和电机命令绝对值限幅。以下结果为 `source=MWORKS_MCP`、`evidence_level=real_sysplorer_mcp_full_awff_pid`：

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
```

说明：Sysblock 控制器文件不是单纯的截图支撑材料，而是后续控制器闭环仿真的主实现路线之一。结构截图应来自 MWORKS.Sysblock/Sysplorer 打开的实际控制器模型窗口，用于证明模块连接、端口和信号流；正式控制器仿真结论必须以 `load_file`、`check_model`、必要时 `simulate_model` 的真实 MWORKS 证据为准，不使用手绘示意图或离线脚本替代。

当前阶段结论：Sysblock 证据链已从最小 demo 推进到分层控制器模型检查通过，并完成 `AWFF_FullController_Sysblock` 组合控制器独立仿真。由于嵌套 Sysblock 在整机混合编译中暴露端口解析限制，当前整机主线使用扁平化 `AWFF_FullControllerEquation_Sysblock` 接入 `QuadrotorExperiments.Example1/2/3AWFFSysblockClosedLoop`。该主线已经完成 Example1 0-1 s、5 s、10 s、20 s 渐进验证，以及 Example1 50 s、Example2 50 s、Example3 120 s 全时长真实 Sysplorer MCP 仿真，可作为当前 Sysblock 控制器仿真的主证据。

当前验证状态：重新登录激活后，四个 Sysblock 控制器文件均已完成真实 Sysplorer MCP 复测：

```text
results/test_reports/sysplorer_sysblock_recheck_20260510.jsonl
results/test_reports/sysplorer_sysblock_recheck_20260510_summary.json
```

```text
AWFF_PID_Sysblock_Demo: load_file/check_model/simulate_model/result_manager 通过，0-1 s 输出 101 行
AWFF_PositionOuterLoop_Sysblock: load_file/check_model 通过
AWFF_AttitudeInnerLoop_Sysblock: load_file/check_model 通过
AWFF_MotorMixer_Sysblock: load_file/check_model 通过
```

组合控制器新增验证：

```text
results/test_reports/sysplorer_awff_full_sysblock_check_20260510.jsonl
results/test_reports/sysplorer_awff_full_sysblock_check_20260510_summary.json

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
results/test_reports/sysplorer_example1_awff_sysblock_smoke_20260510.jsonl
results/test_reports/sysplorer_example1_awff_sysblock_full_20260510.jsonl
results/test_reports/sysplorer_example2_awff_sysblock_smoke_20260510.jsonl
results/test_reports/sysplorer_example2_awff_sysblock_full_20260510.jsonl
results/test_reports/sysplorer_example3_awff_sysblock_smoke_20260510.jsonl
results/test_reports/sysplorer_example3_awff_sysblock_full_20260510.jsonl
results/raw/official_example1_awff_sysblock_smoke.csv
results/raw/official_example1_awff_sysblock.csv
results/raw/official_example2_awff_sysblock_smoke.csv
results/raw/official_example2_awff_sysblock.csv
results/raw/official_example3_awff_sysblock_smoke.csv
results/raw/official_example3_awff_sysblock.csv
results/metrics/official_example1_awff_sysblock_smoke.json
results/metrics/official_example1_awff_sysblock.json
results/metrics/official_example2_awff_sysblock_smoke.json
results/metrics/official_example2_awff_sysblock.json
results/metrics/official_example3_awff_sysblock_smoke.json
results/metrics/official_example3_awff_sysblock.json

QuadrotorExperiments.Example1AWFFSysblockClosedLoop: check_model/simulate_model/result_manager 通过，0-1 s 输出 101 行，50 s 输出 5001 行。
QuadrotorExperiments.Example2AWFFSysblockClosedLoop: check_model/simulate_model/result_manager 通过，0-1 s 输出 101 行，50 s 输出 5001 行。
QuadrotorExperiments.Example3AWFFSysblockClosedLoop: check_model/simulate_model/result_manager 通过，0-1 s 输出 101 行，120 s 输出 12001 行。
```

历史失败日志 `results/logs/sysplorer_layered_sysblock_check_failed_20260510_summary.json` 和 `results/logs/sysplorer_position_axis_check_failed_20260510_summary.json` 保留为授权/登录状态异常时的诊断记录，不再代表当前模型状态。

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
| Example2 螺旋爬升 | awff_sysblock | 0.487394 | -0.043% | 3.005597 | 0.190196 | 0.294113 | 37305.498694 | 30076.679195 | 47.793043 |
| Example3 8字形 | baseline | 0.172311 | - | 1.217033 | 0.068172 | 0.286482 | 95610.155697 | 73046.626000 | 60.505386 |
| Example3 8字形 | improved_pid | 0.167227 | +2.951% | 1.185933 | 0.061940 | 0.295880 | 95611.212646 | 79889.936000 | 60.546610 |
| Example3 8字形 | awff_sysblock | 0.166669 | +3.274% | 1.187258 | 0.061905 | 0.229426 | 95604.798934 | 27372.840134 | 60.281226 |

结论：AWFF PID 相比官方 PID 的 RMSE 降低 `5.573%`，最大位置误差降低 `9.350%`，稳态误差降低 `7.382%`，最大倾角降低 `22.699%`；相比 Enhanced PID，RMSE 继续降低 `2.380%`，最大位置误差降低 `4.315%`，稳态误差和最大倾角基本持平。该结果说明独立控制器本体替换已经跑通，并且比“参数化官方 PID”有进一步轨迹精度收益。

Sysblock 结论：`awff_sysblock` 在 Example1 50 s 全时长真实 Sysplorer MCP 仿真中达到与 `enhanced_pid` 基本一致的性能，并略高于其综合健康分。相比官方 PID，Sysblock 控制器 RMSE 降低 `3.283%`，稳态误差降低 `7.459%`，最大倾角降低 `22.723%`，控制平滑性降低 `88.137%`。在 Example2 螺旋爬升中，RMSE 与官方 PID 基本持平并略高 `0.043%`，但稳态误差降低 `9.495%`、最大倾角降低 `11.112%`、控制平滑性降低 `48.962%`。在 Example3 8字轨迹中，RMSE 降低 `3.274%`、稳态误差降低 `9.193%`、最大倾角降低 `19.916%`、控制平滑性降低 `62.527%`。该结果可以作为“MWORKS.Sysblock 控制器仿真为主”的完整官方场景证据；鲁棒场景结论见第 9 节。

指标口径更新：当前 metrics JSON/CSV 已补充 `sample_rate_hz`、`control_energy_per_second`、`control_smoothness_per_second`、`constraint_violation_rate_hz`、`altitude_violation_rate_hz` 和 `tilt_violation_rate_hz`。当历史结果和新结果导出采样率不同，例如 `25001` 行与 `5001` 行并存时，报告优先比较 RMSE、稳态误差、最大倾角、恢复时间和每秒归一化指标；由采样点数量直接决定的原始 `constraint_violation_count` 只作为同采样率结果内的辅助信息。

## 9. P1 鲁棒场景与控制器消融

新增 `robust_mass20_example1` 场景用于真实模型鲁棒性验证：在 Example1 阶梯爬升任务中，将 `quadChassisTest17_1.body.m` 从官方 `0.159504 kg` 改为 `0.191405 kg`，即中心机体质量 +20%。该扰动模拟载荷变化或质量参数建模误差；路径、求解器、导出变量和仿真时长保持不变，因此可用于控制器消融对比。

模型替换位置：

```text
models/QuadrotorExperiments/package.mo
  QuadrotorExperiments.Example1Mass20PID
  QuadrotorExperiments.Example1Mass20ImprovedPID
  QuadrotorExperiments.Example1Mass20EnhancedPID
models/QuadrotorExperiments/Example1Mass20AWFFSysblockClosedLoop.mo
  QuadrotorExperiments.Example1Mass20AWFFSysblockClosedLoop
```

场景配置：

```text
scenarios/robustness/example1_mass20_pid_baseline.yaml
scenarios/robustness/example1_mass20_improved_pid.yaml
scenarios/robustness/example1_mass20_enhanced_pid.yaml
scenarios/robustness/example1_mass20_awff_sysblock.yaml
```

以下结果均为 `source=MWORKS_MCP`、`evidence_level=real_sysplorer_mcp_robust_mass20_ablation`，每条仿真均完成 `check_model ok`、`simulate_model ok`，导出 `5001` 行 50 s raw CSV：

| 场景 | controller | position_rmse_m | RMSE变化 | steady_state_error_m | 稳态误差变化 | max_tilt_rad | 最大倾角变化 | control_energy_per_second | control_smoothness_per_second | total_health_score |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| +20% 质量摄动 Example1 | baseline | 0.291441 | - | 0.111428 | - | 0.241303 | - | 953.889949 | 2367.712444 | 51.820711 |
| +20% 质量摄动 Example1 | improved_pid | 0.286484 | +1.701% | 0.105508 | +5.313% | 0.289414 | -19.938% | 953.929869 | 3618.603060 | 51.886273 |
| +20% 质量摄动 Example1 | enhanced_pid | 0.282610 | +3.030% | 0.103144 | +7.434% | 0.174124 | +27.840% | 953.305878 | 270.716005 | 52.444636 |
| +20% 质量摄动 Example1 | awff_sysblock | 0.282785 | +2.970% | 0.103112 | +7.463% | 0.174122 | +27.841% | 953.303498 | 266.591707 | 52.443573 |

消融结论：在同一 +20% 质量摄动下，Improved PID 主要改善轨迹 RMSE 和稳态误差，但最大倾角增加 `19.938%`，说明单纯增益搜索会引入姿态代价。Enhanced PID 与 AWFF Sysblock 在 RMSE、稳态误差、最大倾角、每秒控制能量和每秒控制平滑性上均优于同扰动 baseline。AWFF Sysblock 相比 baseline 的 RMSE 降低 `2.970%`，稳态误差降低 `7.463%`，最大倾角降低 `27.841%`，`control_smoothness_per_second` 降低 `88.741%`。该结果可作为 Sysblock 控制器质量参数鲁棒性的正式证据。



新增 `robust_wind_gust_example1` 场景用于外部扰动鲁棒性验证：在 Example1 阶梯爬升任务中，将一个世界坐标系横向阵风力接入 `quadChassisTest17_1.body.frame_b`。阵风在 `15-19 s` 生效，基准力为 `Fx=0.22 N, Fy=-0.10 N`，并叠加 `1.2 Hz` 的小幅正弦脉动。该场景不改官方旋翼升力方程，扰动通过项目派生模型额外接入机体。

模型替换位置：

```text
models/QuadrotorExperiments/package.mo
  QuadrotorExperiments.Example1WindGustBase
  QuadrotorExperiments.Example1WindGustPID
  QuadrotorExperiments.Example1WindGustImprovedPID
  QuadrotorExperiments.Example1WindGustEnhancedPID
models/QuadrotorExperiments/Example1WindGustAWFFSysblockClosedLoop.mo
  QuadrotorExperiments.Example1WindGustAWFFSysblockClosedLoop
```

场景配置：

```text
scenarios/robustness/example1_wind_gust_pid_baseline.yaml
scenarios/robustness/example1_wind_gust_improved_pid.yaml
scenarios/robustness/example1_wind_gust_enhanced_pid.yaml
scenarios/robustness/example1_wind_gust_awff_sysblock.yaml
```

以下结果均为 `source=MWORKS_MCP`、`evidence_level=real_sysplorer_mcp_robust_wind_gust_ablation`，每条仿真均完成 `check_model ok`、`simulate_model ok`，导出 `25001` 行 50 s raw CSV：

| 场景 | controller | position_rmse_m | RMSE变化 | disturbance_peak_error_m | 峰值误差变化 | disturbance_recovery_time_s | max_tilt_rad | 最大倾角变化 | control_smoothness_per_second | total_health_score |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 15-19s 横向阵风 Example1 | baseline | 0.334706 | - | 0.753994 | - | 3.460 | 0.228849 | - | 2757.199851 | 51.989919 |
| 15-19s 横向阵风 Example1 | improved_pid | 0.322116 | +3.762% | 0.699255 | +7.260% | 3.296 | 0.278640 | -21.757% | 3987.595477 | 52.117069 |
| 15-19s 横向阵风 Example1 | enhanced_pid | 0.318260 | +4.914% | 0.696234 | +7.661% | 3.242 | 0.196606 | +14.089% | 276.951339 | 55.004469 |
| 15-19s 横向阵风 Example1 | awff_sysblock | 0.318224 | +4.924% | 0.696309 | +7.652% | 3.250 | 0.196645 | +14.072% | 269.391389 | 55.001701 |

消融结论：在同一横向阵风扰动下，Improved PID 可降低 RMSE 和扰动窗口峰值误差，但最大倾角增加 `21.757%`，说明仅靠增益搜索仍会提高姿态代价。AWFF Sysblock 相比 baseline 的 RMSE 降低 `4.924%`，扰动窗口峰值误差降低 `7.652%`，恢复时间从 `3.460 s` 缩短到 `3.250 s`，最大倾角降低 `14.072%`，`control_smoothness_per_second` 降低 `90.230%`。因此风扰场景可以作为 Sysblock 控制器外部扰动鲁棒性的正式证据。注意：该组 baseline/enhanced 历史结果导出为 `25001` 行，AWFF Sysblock 导出为 `5001` 行；报告已使用每秒归一化指标避免 sample-count 直接影响。



新增 `robust_rotor1_loss15_example1` 场景用于执行器退化鲁棒性验证：在 Example1 阶梯爬升任务中，将 1 号旋翼对应升力增益 `quadChassisTest17_1.gain2.k` 从官方 `0.002` 改为 `0.0017`，等效为单旋翼升力效率下降到 `85%`。该场景不修改控制器接口，扰动直接作用在官方机体升力链路上。

模型替换位置：

```text
models/QuadrotorExperiments/package.mo
  QuadrotorExperiments.Example1Rotor1Loss15PID
  QuadrotorExperiments.Example1Rotor1Loss15ImprovedPID
  QuadrotorExperiments.Example1Rotor1Loss15EnhancedPID
models/QuadrotorExperiments/Example1Rotor1Loss15AWFFSysblockClosedLoop.mo
  QuadrotorExperiments.Example1Rotor1Loss15AWFFSysblockClosedLoop
```

场景配置：

```text
scenarios/robustness/example1_rotor1_loss15_pid_baseline.yaml
scenarios/robustness/example1_rotor1_loss15_improved_pid.yaml
scenarios/robustness/example1_rotor1_loss15_enhanced_pid.yaml
scenarios/robustness/example1_rotor1_loss15_awff_sysblock.yaml
```

以下结果均为 `source=MWORKS_MCP`、`evidence_level=real_sysplorer_mcp_robust_rotor_loss_ablation`，每条仿真均完成 `check_model ok`、`simulate_model ok`，导出 `5001` 行 50 s raw CSV：

| 场景 | controller | position_rmse_m | RMSE变化 | steady_state_error_m | max_tilt_rad | 最大倾角变化 | constraint_violation_rate_hz | control_smoothness_per_second | total_health_score |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 1号旋翼效率85% Example1 | baseline | 0.392120 | - | 0.286884 | 0.211287 | - | 1.340 | 2167.565293 | 35.625782 |
| 1号旋翼效率85% Example1 | improved_pid | 0.371435 | +5.275% | 0.265699 | 0.254032 | -20.231% | 1.340 | 3128.825699 | 35.884927 |
| 1号旋翼效率85% Example1 | enhanced_pid | 0.368251 | +6.087% | 0.265416 | 0.174661 | +17.335% | 1.300 | 265.211626 | 36.050556 |
| 1号旋翼效率85% Example1 | awff_sysblock | 0.369058 | +5.881% | 0.265419 | 0.174661 | +17.335% | 1.300 | 264.978146 | 36.043895 |

消融结论：单旋翼效率退化场景明显比质量摄动和横向阵风更困难，baseline 的 RMSE 增至 `0.392120 m`，健康分降至 `35.625782`。Improved PID 可降低 RMSE，但最大倾角增加 `20.231%`；AWFF Sysblock 相比 baseline 的 RMSE 降低 `5.881%`，稳态误差降低 `7.482%`，最大倾角降低 `17.335%`，约束违规率从 `1.340 Hz` 降到 `1.300 Hz`，`control_smoothness_per_second` 降低 `87.775%`。该场景可作为 Sysblock 控制器执行器退化鲁棒性证据，但报告中应明确：当前控制器没有故障检测与控制分配重构逻辑，仍属于固定控制器在退化工况下的抗扰表现验证。

### 9.4 L1-inspired 残差补偿控制器首轮消融

`l1_residual_sysblock` 在 `AWFF_FullControllerEquation_Sysblock` 基础上加入低通残差估计和有界补偿，不改变 `controller3_2` 的输入输出接口。当前实现文件和场景为：

```text
models/QuadrotorControllerBlocks/AWFF_L1ResidualControllerEquation_Sysblock.mo
models/QuadrotorExperiments/Example1L1SysblockClosedLoop.mo
models/QuadrotorExperiments/Example1WindGustL1SysblockClosedLoop.mo
controllers/l1_residual_sysblock/default.yaml
scenarios/official/example1_l1_residual_sysblock.yaml
scenarios/robustness/example1_wind_gust_l1_residual_sysblock.yaml
```

以下结果均为 `source=MWORKS_MCP`。两条 full 场景均先完成 0-1 s smoke，再完成 50 s `check_model/simulate_model/result_manager`，导出 `5001` 行 raw CSV。

| 场景 | controller | position_rmse_m | RMSE变化 | disturbance_peak_error_m | 峰值误差变化 | disturbance_recovery_time_s | steady_state_error_m | max_tilt_rad | control_smoothness_per_second | total_health_score |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Example1 阶梯爬升 | awff_sysblock | 0.266217 | - | 0.075009 | - | 3.030 | 0.103144 | 0.174437 | 265.176177 | 55.423227 |
| Example1 阶梯爬升 | l1_residual_sysblock | 0.248070 | +6.816% | 0.066026 | +11.976% | 2.790 | 0.082080 | 0.195313 | 275.683925 | 55.782282 |
| 15-19s 横向阵风 Example1 | awff_sysblock | 0.318224 | - | 0.696413 | - | 3.250 | 0.103106 | 0.196645 | 269.391389 | 55.001701 |
| 15-19s 横向阵风 Example1 | l1_residual_sysblock | 0.287024 | +9.804% | 0.583631 | +16.195% | 2.960 | 0.082172 | 0.195237 | 279.885642 | 55.466442 |

消融结论：L1-inspired 残差补偿在 nominal Example1 中降低 `position_rmse_m 6.816%`、稳态误差 `20.422%`、扰动窗口峰值误差 `11.976%`；在横向阵风场景中降低 `position_rmse_m 9.804%`、扰动窗口峰值误差 `16.195%`，恢复时间从 `3.250 s` 缩短到 `2.960 s`。代价是控制平滑性变差：nominal `control_smoothness_per_second` 增加 `3.963%`，风扰场景增加 `3.896%`。因此当前 L1 residual 可以作为 P1 创新控制器的首轮正式证据，但后续仍需在质量摄动和旋翼退化场景中复测，并调参降低高频控制动作。

## 10. 当前图表

已生成图表：

```text
results/figures/official_example1_pid_baseline/
results/figures/official_example1_improved_pid/
results/figures/official_example1_enhanced_pid/
results/figures/official_example1_awff_pid/
results/figures/official_example2_pid_baseline/
results/figures/official_example2_improved_pid/
results/figures/official_example3_pid_baseline/
results/figures/official_example3_improved_pid/
results/figures/official_example1_awff_sysblock/
results/figures/official_example2_awff_sysblock/
results/figures/official_example3_awff_sysblock/
results/figures/robust_mass20_example1_pid_baseline/
results/figures/robust_mass20_example1_improved_pid/
results/figures/robust_mass20_example1_enhanced_pid/
results/figures/robust_mass20_example1_awff_sysblock/
results/figures/robust_wind_gust_example1_pid_baseline/
results/figures/robust_wind_gust_example1_improved_pid/
results/figures/robust_wind_gust_example1_enhanced_pid/
results/figures/robust_wind_gust_example1_awff_sysblock/
results/figures/robust_rotor1_loss15_example1_pid_baseline/
results/figures/robust_rotor1_loss15_example1_improved_pid/
results/figures/robust_rotor1_loss15_example1_enhanced_pid/
results/figures/robust_rotor1_loss15_example1_awff_sysblock/
results/figures/official_example1_l1_residual_sysblock/
results/figures/robust_wind_gust_example1_l1_residual_sysblock/
```

已生成 replay JSON：

```text
results/replay/official_example1_pid_baseline.json
results/replay/official_example1_improved_pid.json
results/replay/official_example1_enhanced_pid.json
results/replay/official_example1_awff_pid.json
results/replay/official_example2_pid_baseline.json
results/replay/official_example2_improved_pid.json
results/replay/official_example3_pid_baseline.json
results/replay/official_example3_improved_pid.json
results/replay/official_example1_awff_sysblock.json
results/replay/official_example2_awff_sysblock.json
results/replay/official_example3_awff_sysblock.json
results/replay/robust_mass20_example1_pid_baseline.json
results/replay/robust_mass20_example1_improved_pid.json
results/replay/robust_mass20_example1_enhanced_pid.json
results/replay/robust_mass20_example1_awff_sysblock.json
results/replay/robust_wind_gust_example1_pid_baseline.json
results/replay/robust_wind_gust_example1_improved_pid.json
results/replay/robust_wind_gust_example1_enhanced_pid.json
results/replay/robust_wind_gust_example1_awff_sysblock.json
results/replay/robust_rotor1_loss15_example1_pid_baseline.json
results/replay/robust_rotor1_loss15_example1_improved_pid.json
results/replay/robust_rotor1_loss15_example1_enhanced_pid.json
results/replay/robust_rotor1_loss15_example1_awff_sysblock.json
results/replay/official_example1_l1_residual_sysblock.json
results/replay/robust_wind_gust_example1_l1_residual_sysblock.json
results/replay/reference_official_example1.json
results/replay/reference_official_example2.json
results/replay/reference_official_example3.json
```

其中 `results/replay/*.json` 来自真实 Sysplorer MCP raw CSV 或官方参考轨迹 CSV，可作为后续 Gazebo/视频展示输入；它不是在线仿真结果。

## 11. 扩展场景状态

此前用于横向展示的 Python/Julia 离线仿真结果已清理。当前报告结论只引用真实 Sysplorer/MWORKS MCP 证据。

质量 +20% 参数摄动、15-19 s 横向阵风扰动、1 号旋翼 85% 效率退化、Example1 AWFF 独立控制器替换、Example1/2/3 AWFF Sysblock 官方场景，以及 Example1 L1 residual Sysblock nominal/wind-gust 消融均已完成真实 MWORKS MCP 闭环。规划和编队仍保留在 `Design/` 中作为下一阶段实现目标，但必须完成以下闭环后才能进入本报告的性能结论：

```text
MWORKS/Sysplorer 模型或派生模型
→ check_model 成功
→ simulate_model 完整运行
→ result_manager 导出 raw CSV
→ metrics/figures/replay 可复现
→ source=MWORKS_MCP 或 source=MWORKS_GUI
```

下一阶段优先任务：

1. 将 L1 residual Sysblock 补偿扩展到质量摄动和旋翼退化场景，并降低高频控制动作；
2. 在旋翼退化场景中加入故障检测、控制分配重构或安全降级逻辑，区别于固定控制器抗扰；
3. INDI 或线性 MPC 外环的最小可运行模型。

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

授权恢复后，三条 AWFF Sysblock 鲁棒场景均已完成 `check_model/simulate_model/result_manager`，导出 `5001` 行 50 s raw CSV，并进入本报告性能结论。早期授权失效导致的失败日志只保留为诊断记录，不再代表当前模型状态。

L1 residual Sysblock 已完成以下真实 MCP 证据：

```text
QuadrotorExperiments.Example1L1SysblockClosedLoop
QuadrotorExperiments.Example1WindGustL1SysblockClosedLoop

scenarios/smoke/example1_l1_residual_sysblock_mcp_smoke.yaml
scenarios/smoke/example1_wind_gust_l1_residual_sysblock_mcp_smoke.yaml
scenarios/official/example1_l1_residual_sysblock.yaml
scenarios/robustness/example1_wind_gust_l1_residual_sysblock.yaml

results/test_reports/sysplorer_example1_l1_residual_sysblock_smoke_20260510.jsonl
results/test_reports/sysplorer_robust_wind_gust_example1_l1_residual_sysblock_smoke_20260510.jsonl
results/test_reports/sysplorer_example1_l1_residual_sysblock_full_20260510.jsonl
results/test_reports/sysplorer_robust_wind_gust_example1_l1_residual_sysblock_20260510.jsonl
```

## 12. 结论约束

1. 不使用 smoke 数据做完整控制性能结论。
2. 不使用离线脚本结果作为 MWORKS 控制性能结论。
3. 报告中的每张图必须能追溯到 `results/raw/` 和生成脚本。
4. 完整 baseline 与优化控制器必须使用同一场景、同一时长和同一指标脚本。
