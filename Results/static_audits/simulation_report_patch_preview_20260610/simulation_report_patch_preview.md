# Simulation Report Patch Preview, 2026-06-10

Status: draft patch preview, not a report edit.

## Summary

- Previews: `7`
- Candidate insert previews: `3`
- Replacement previews: `1`
- Edits report source: `False`
- Deletes content: `False`
- Final acceptance: `False`

## Claim Boundary

- This artifact previews possible report-source edits only.
- It does not edit Docs/simulation_report.md.
- It does not delete historical evidence.
- It does not generate a patch to apply automatically.
- It does not change final PMO acceptance.

## Preview Items

### preserve_final_acceptance_boundary_preview

- Operation: `verify_keep_existing_text`
- Source action: `preserve_final_acceptance_boundary`
- Target: 1. 报告范围
- Line hint: `37`
- Applies patch now: `False`
- Safety boundary: Do not convert static candidate readiness into final acceptance.

Original:

```text
它们只用于报告草稿选材、图表就绪度确认、表格起草、预提交准备度盘点、草稿改写规划、旧阶段/冲突内容审查、报告源编辑排序、人工审查前的片段预览和正文编辑准入判断，不是最终 PMO 验收。当前 13 条候选行的
```

Preview:

```text
Keep this boundary near the front matter before any report-source rewrite.
```

### rewrite_formation_next_stage_boundary_preview

- Operation: `replace_single_sentence_after_review`
- Source action: `rewrite_formation_next_stage_boundary`
- Target: 12. 扩展场景状态
- Line hint: `602`
- Applies patch now: `False`
- Safety boundary: Do not claim ROS2/PX4/QGC online formation or final formation acceptance.

Original:

```text
质量 +20% 参数摄动、15-19 s 横向阵风扰动、1 号旋翼 85% 效率退化、Example1 AWFF 独立控制器替换、Example1/2/3 AWFF Sysblock 官方场景、L1 residual Sysblock 消融，以及已知效率退化控制分配补偿均已完成真实 MWORKS MCP 闭环。规划和编队仍保留在 `Docs/Design/` 中作为下一阶段实现目标，但必须完成以下闭环后才能进入本报告的性能结论：
```

Preview:

```text
质量 +20% 参数摄动、15-19 s 横向阵风扰动、1 号旋翼 85% 效率退化、Example1 AWFF 独立控制器替换、Example1/2/3 AWFF Sysblock 官方场景、L1 residual Sysblock 消融、已知效率退化控制分配补偿，以及 triangle figure-8 编队候选行均已有静态候选证据或真实 MWORKS/Sysplorer 证据；其中编队候选证据只支撑报告草稿中的 MWORKS/Sysplorer 编队验证描述，不支撑 ROS2/PX4/QGC 在线编队、真实多机通信链路或最终编队验收声明。
```

### insert_visual_trajectory_review_candidate_subsection_preview

- Operation: `insert_candidate_subsection_after_review`
- Source action: `insert_visual_trajectory_review_candidate_subsection`
- Target: 11. 当前图表
- Line hint: `None`
- Applies patch now: `False`
- Safety boundary: 不支撑 UE build/runtime/editor 成功、最终演示视频完成或最终视觉验收声明。

Original:

```text

```

Preview:

```text
### 原生轨迹留痕与视觉审查候选证据

当前候选证据可用于报告草稿说明：平面 8 字和螺旋上升 8 字留痕审查模型已有 native GUI 候选行与图表路径。 候选实验包括 `official_example1_helical_figure8_trail_sysblock`、`official_example1_planar_figure8_trail_sysblock`，position_rmse_m 分别为 0.0188363、0.0188624。不支撑 UE build/runtime/editor 成功、最终演示视频完成或最终视觉验收声明。

| claim_slot | scene_id | controller_id | position_rmse_m | total_health_score | figure |
|---|---|---|---:|---:|---|
| C1-visual-helical-figure8 | official_example1_helical_figure8 | linear_mpc_sysblock | 0.0188363 | 93.3606 | Results/official/example1_helical_figure8/official_example1_helical_figure8_trail_sysblock/figures/official_example1_helical_figure8_trail_sysblock_trajectory_xy.svg |
| C1-visual-planar-figure8 | official_example1_planar_figure8 | linear_mpc_sysblock | 0.0188624 | 93.3638 | Results/official/example1_planar_figure8/official_example1_planar_figure8_trail_sysblock/figures/official_example1_planar_figure8_trail_sysblock_trajectory_xy.svg |
```

### insert_fault_tolerance_candidate_subsection_preview

- Operation: `insert_candidate_subsection_after_review`
- Source action: `insert_fault_tolerance_candidate_subsection`
- Target: 13. Linear MPC-style 外环闭环结果
- Line hint: `None`
- Applies patch now: `False`
- Safety boundary: 不支撑瞬态故障切换、多旋翼同时故障、真实飞控容错或最终 PMO 验收声明。

Original:

```text

```

Preview:

```text
### 执行器退化与复合扰动容错候选证据

当前候选证据可用于报告草稿说明：在 rotor1 85% 效率退化叠加横向阵风场景中，加入在线效率估计与控制分配的 LinearMPC Sysblock 候选行通过质量门。 候选实验 `robust_rotor1_loss15_wind_gust_example1_linear_mpc_online_fault_allocation_sysblock` 的 position_rmse_m=0.261434，total_health_score=51.3177，证据路径包括 metrics、raw CSV 和核心 SVG 图表。不支撑瞬态故障切换、多旋翼同时故障、真实飞控容错或最终 PMO 验收声明。

| claim_slot | scene_id | controller_id | position_rmse_m | total_health_score | figure |
|---|---|---|---:|---:|---|
| C1-fault-tolerance-rotor1-loss-wind | robust_rotor1_loss15_wind_gust_example1 | linear_mpc_online_fault_allocation_sysblock | 0.261434 | 51.3177 | Results/robustness/rotor1_loss15_wind_gust_example1/robust_rotor1_loss15_wind_gust_example1_linear_mpc_online_fault_allocation_sysblock/figures/robust_rotor1_loss15_wind_gust_example1_linear_mpc_online_fault_allocation_sysblock_trajectory_xy.svg |
```

### insert_multi_uav_formation_candidate_subsection_preview

- Operation: `insert_candidate_subsection_after_review`
- Source action: `insert_multi_uav_formation_candidate_subsection`
- Target: 13. Linear MPC-style 外环闭环结果
- Line hint: `None`
- Applies patch now: `False`
- Safety boundary: 不支撑 ROS2/PX4/QGC 在线编队、真实多机通信链路或最终编队验收声明。

Original:

```text

```

Preview:

```text
### 多无人机编队控制候选证据

当前候选证据可用于报告草稿说明：triangle figure-8 编队场景已有一条 MWORKS/Sysplorer 候选行，记录了位置 RMSE、健康分和 formation_score。 候选实验 `formation_triangle_figure8_linear_mpc_sysblock` 的 position_rmse_m=0.0212508，formation_score=100，total_health_score=93.6862。不支撑 ROS2/PX4/QGC 在线编队、真实多机通信链路或最终编队验收声明。

| claim_slot | scene_id | controller_id | position_rmse_m | total_health_score | figure |
|---|---|---|---:|---:|---|
| C2-formation-triangle-figure8 | formation_triangle_figure8 | linear_mpc_sysblock | 0.0212508 | 93.6862 | Results/formation/triangle_figure8/formation_triangle_figure8_linear_mpc_sysblock/figures/formation_triangle_figure8_linear_mpc_sysblock_trajectory_xy.svg |
```

### condense_smoke_and_legacy_sections_preview

- Operation: `manual_condense_no_delete`
- Source action: `condense_smoke_and_legacy_sections`
- Target: 5-9 legacy/smoke sections
- Line hint: `3`
- Applies patch now: `False`
- Safety boundary: Do not delete provenance or use smoke/staged rows as full performance conclusions.

Original:

```text
smoke/staged and legacy comparison sections remain in source until reviewer approves condensation
```

Preview:

```text
Move detailed smoke/staged and legacy-comparison tables toward a history or appendix summary only after the final candidate table is reviewed.
```

### renumber_l1_residual_subsection_preview

- Operation: `rename_heading_after_review`
- Source action: `renumber_l1_residual_subsection`
- Target: 9.4 L1-inspired 残差补偿控制器首轮消融
- Line hint: `505`
- Applies patch now: `False`
- Safety boundary: Structure cleanup only; do not change technical claims.

Original:

```text
### 9.4 L1-inspired 残差补偿控制器首轮消融
```

Preview:

```text
### L1-inspired 残差补偿控制器首轮消融
```
