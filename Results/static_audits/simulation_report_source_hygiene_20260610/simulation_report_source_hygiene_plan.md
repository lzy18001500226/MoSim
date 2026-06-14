# Simulation Report Source Hygiene Plan, 2026-06-10

Status: draft hygiene plan, not a report edit.

## Summary

- Findings: `6`
- Edits report source: `False`
- Deletes content: `False`
- Final acceptance: `False`

Severity counts:

- `high`: `2`
- `low`: `1`
- `medium`: `3`

## Claim Boundary

- This plan is a review aid only.
- It does not edit Docs/simulation_report.md.
- It does not delete report content.
- It does not change final PMO acceptance or live-runtime status.

## Findings

### old_airframe_snapshot_warnings

- Severity: `medium`
- Category: `old_stage_context`
- Risk: Old-airframe or old-controller notes are useful history, but they can distract from the final candidate evidence set.
- Recommendation: Move or condense old-stage context into a history/appendix block during the next report rewrite.
- Proposed action: `condense_keep_boundary`

Evidence:
- line 56: 迁移后，质量 +20% 场景的质量扰动改为 `1.0 kg -> 1.2 kg`；旋翼 85% 退化场景的升力增益改为 `0.000854858 -> 0.0007266293`。本报告后续历史表格是旧机体证据快照，不应继续作为新机体性能结论；正式控制器排名和视频素材需要基于 `sunray150_with_mid360` 重新运行 Sysplorer/MWORKS 仿真后刷新。
- line 384: 当前 `robust_mass20_example1` 场景用于真实模型鲁棒性验证：在 Example1 阶梯爬升任务中，将 `quadChassisTest17_1.body.m` 从当前 Sunray150 机体 `1.0 kg` 改为 `1.2 kg`，即中心机体质量 +20%。本节下方历史表格仍是旧轻量机架证据快照；新机体正式结论需要重跑后刷新。
- line 461: 当前 `robust_rotor1_loss15_example1` 场景用于执行器退化鲁棒性验证：在 Example1 阶梯爬升任务中，将 1 号旋翼对应升力增益 `quadChassisTest17_1.gain2.k` 从当前 Sunray150 nominal `0.000854858` 改为 `0.0007266293`，等效为单旋翼升力效率下降到 `85%`。本节下方历史表格仍是旧轻量机架证据快照；新机体正式结论需要重跑后刷新。
- line 725: 2026-05-14 收尾修正：Sunray150_with_mid360 迁移后，所有 `Models/QuadrotorExperiments/*SysblockClosedLoop.mo` 单机实验包装模型均补入悬停电机速度偏置 `53.5621 rad/s` 和控制增量缩放 `53.5621 / 13.9854`，避免旧控制器速度输出直接接入新机体电机输入域。修正后 Example1/2/3 LinearMPC 全时长真实 Sysplorer MCP 复测均为 `pass`，上表已更新为新机体指标。

### smoke_and_staged_prominence

- Severity: `medium`
- Category: `smoke_context`
- Risk: Smoke/staged rows are valid pipeline evidence but should not dominate the final performance narrative.
- Recommendation: Keep the smoke boundary, but move detailed smoke/staged tables out of the main final-results path.
- Proposed action: `move_to_appendix_or_summary`

Evidence:
- line 3: > 当前 smoke 数据均只覆盖 0-1 s，用于验证 MCP 结果读取、CSV 导出和指标计算链路。完整性能结论只引用 `official_example*_*.csv` 对应的全时长真实 Sysplorer MCP 结果。
- line 11: 质量判定规则：`check_model ok` 和 `simulate_model ok` 只说明模型可以执行；完整性能结论还必须通过 `Scripts/results/evaluate_result_quality.py` 写入的 `quality_status`。`pass` 可支撑报告结论，`smoke_only` 只证明链路可用，`needs_iteration` 必须继续调控制器或明确写为未完成限制。当前 Example2 已通过 `helix_tuned` Enhanced PID、AWFF PID 和 AWFF Sysblock 分支解决 RMSE 门禁问题；旋翼退化场景显示“仅靠外环鲁棒控制不足”，需要控制分配或故障补偿层。
- line 44: Example1/2/3 AWFF Sysblock 0-1 s 真实 Sysplorer MCP smoke 日志、CSV 和指标
- line 45: Example1 L1 residual Sysblock nominal/wind-gust 0-1 s smoke 与 50 s full CSV、指标、图表和 replay JSON
- line 82: | Example1 smoke | `QuadrotorModel.Examples.Example1` | 1 s | 已有 CSV、指标、图表 |
- line 83: | Example1 MWORKS MCP smoke | `QuadrotorModel.Examples.Example1` | 1 s | 已通过 Sysplorer MCP 真实加载、检查、仿真和读取变量 |
- line 96: `Scripts/quality/qa_check.py` 会阻止短时 smoke 数据误放入上述正式结果路径。
- line 107: → Scripts/mworks/run_sysplorer_mcp_smoke.py 导出标准 CSV
- ... 13 more matches

### legacy_controller_comparison_sections

- Severity: `medium`
- Category: `legacy_comparison`
- Risk: Legacy Improved PID / Enhanced PID / AWFF sections are useful provenance but may compete with the current candidate LinearMPC report path.
- Recommendation: Compress these sections after the final candidate table is accepted; preserve evidence references until review completes.
- Proposed action: `compress_after_candidate_table_review`

Evidence:
- line 160: 7. 改进 PID 对比
- line 179: 8. Enhanced PID P1 初步结果
- line 202: 9. AWFF 独立控制器初步结果

### heading_number_mismatch

- Severity: `low`
- Category: `report_structure`
- Risk: A 9.4 subsection appears under the later report flow and can confuse navigation.
- Recommendation: Renumber or remove explicit subsection numbering during the final report rewrite.
- Proposed action: `renumber_in_report_rewrite`

Evidence:
- line 497: ### 9.4 L1-inspired 残差补偿控制器首轮消融

### formation_next_stage_statement_conflict

- Severity: `high`
- Category: `candidate_mismatch`
- Risk: The report says planning and formation remain next-stage goals, while the static candidate set now includes a multi-UAV formation candidate row.
- Recommendation: Rewrite this sentence to distinguish final acceptance from available candidate formation evidence.
- Proposed action: `rewrite_with_candidate_boundary`

Evidence:
- line 594: 质量 +20% 参数摄动、15-19 s 横向阵风扰动、1 号旋翼 85% 效率退化、Example1 AWFF 独立控制器替换、Example1/2/3 AWFF Sysblock 官方场景、L1 residual Sysblock 消融，以及已知效率退化控制分配补偿均已完成真实 MWORKS MCP 闭环。规划和编队仍保留在 `Docs/Design/` 中作为下一阶段实现目标，但必须完成以下闭环后才能进入本报告的性能结论：

### final_artifact_missing_boundary

- Severity: `high`
- Category: `final_acceptance_boundary`
- Risk: The report correctly states final packaging is not complete; any source rewrite must keep this boundary.
- Recommendation: Keep the not-final boundary until final PDFs, demo video, and PMO acceptance packet exist.
- Proposed action: `preserve_boundary`

Evidence:
- line 29: 它们只用于报告草稿选材、图表就绪度确认、表格起草、预提交准备度盘点和草稿改写规划，不是最终 PMO 验收。当前 13 条候选行的
- line 30: metrics/raw/figure/replay/log 路径均可解析，但最终 PDF、演示视频和最终验收 packet 仍未完成。静态清单也不证明
- line 683: 对应证据目录位于 `Results/robustness/rotor{1..4}_loss15_example1/robust_rotor{1..4}_loss15_example1_l1_multi_fault_isolation_sysblock/`，其中包含 `raw/`、`metrics/`、`figures/`、`replay/` 和 `logs/`。`figures/` 中除轨迹、误差和指标图外，还包含 `*_eta_hat_diagnostics.svg` 与 `*_fault_index_diagnostics.svg`，用于报告和演示视频中展示在线效率估计与故障编号锁存过程。该组结果可以支撑“四旋翼持续单故障隔离验证已完成”的表述；不支撑瞬态故障、复合多故障或故障切换声明。

## Recommended Order

1. Preserve current not-final and no-live-runtime boundaries.
2. Rewrite the formation/planning next-stage sentence with candidate-evidence boundaries.
3. Move smoke/staged details and legacy comparisons toward summary/appendix form.
4. Renumber report sections after content placement is approved.
