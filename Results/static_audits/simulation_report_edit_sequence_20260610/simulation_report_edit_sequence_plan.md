# Simulation Report Edit Sequence Plan, 2026-06-10

Status: draft edit sequence, not a report edit.

## Summary

- Actions: `7`
- Candidate families: `3`
- Hygiene findings: `6`
- Edits report source: `False`
- Deletes content: `False`
- Final acceptance: `False`

## Claim Boundary

- This plan sequences report-source edits only.
- It does not edit Docs/simulation_report.md.
- It does not delete historical evidence.
- It does not generate PDFs/video or PMO final acceptance.

## Actions

### 1. preserve_final_acceptance_boundary

- Kind: `boundary_guard`
- Target section: 1. 报告范围
- Claim family: ``
- Source finding: `final_artifact_missing_boundary`
- Report line hint: `29`
- Rationale: Final PDF, demo video, and final PMO acceptance packet are still missing.
- Proposed change: Keep the current not-final paragraph near the front matter before any source rewrite.
- Safety boundary: Do not convert static candidate readiness into final acceptance.

### 2. rewrite_formation_next_stage_boundary

- Kind: `targeted_sentence_rewrite`
- Target section: 12. 扩展场景状态
- Claim family: `multi_uav_formation`
- Source finding: `formation_next_stage_statement_conflict`
- Report line hint: `594`
- Rationale: The current sentence says planning and formation are next-stage goals, but a formation candidate row now exists.
- Proposed change: Rewrite the sentence to separate static MWORKS/Sysplorer formation candidate evidence from unproven ROS2/PX4/QGC online formation claims.
- Safety boundary: Do not claim ROS2/PX4/QGC online formation or final formation acceptance.

### 3. insert_visual_trajectory_review_candidate_subsection

- Kind: `candidate_subsection_insert`
- Target section: 11. 当前图表
- Claim family: `visual_trajectory_review`
- Source finding: ``
- Report line hint: `None`
- Rationale: Candidate family `visual_trajectory_review` is not yet represented as a dedicated final-report subsection.
- Proposed change: 当前候选证据可用于报告草稿说明：平面 8 字和螺旋上升 8 字留痕审查模型已有 native GUI 候选行与图表路径。 候选实验包括 `official_example1_helical_figure8_trail_sysblock`、`official_example1_planar_figure8_trail_sysblock`，position_rmse_m 分别为 0.0188363、0.0188624。不支撑 UE build/runtime/editor 成功、最终演示视频完成或最终视觉验收声明。
- Safety boundary: 不支撑 UE build/runtime/editor 成功、最终演示视频完成或最终视觉验收声明。

### 4. insert_fault_tolerance_candidate_subsection

- Kind: `candidate_subsection_insert`
- Target section: 13. Linear MPC-style 外环闭环结果
- Claim family: `fault_tolerance`
- Source finding: ``
- Report line hint: `None`
- Rationale: Candidate family `fault_tolerance` is not yet represented as a dedicated final-report subsection.
- Proposed change: 当前候选证据可用于报告草稿说明：在 rotor1 85% 效率退化叠加横向阵风场景中，加入在线效率估计与控制分配的 LinearMPC Sysblock 候选行通过质量门。 候选实验 `robust_rotor1_loss15_wind_gust_example1_linear_mpc_online_fault_allocation_sysblock` 的 position_rmse_m=0.261434，total_health_score=51.3177，证据路径包括 metrics、raw CSV 和核心 SVG 图表。不支撑瞬态故障切换、多旋翼同时故障、真实飞控容错或最终 PMO 验收声明。
- Safety boundary: 不支撑瞬态故障切换、多旋翼同时故障、真实飞控容错或最终 PMO 验收声明。

### 5. insert_multi_uav_formation_candidate_subsection

- Kind: `candidate_subsection_insert`
- Target section: 13. Linear MPC-style 外环闭环结果
- Claim family: `multi_uav_formation`
- Source finding: ``
- Report line hint: `None`
- Rationale: Candidate family `multi_uav_formation` is not yet represented as a dedicated final-report subsection.
- Proposed change: 当前候选证据可用于报告草稿说明：triangle figure-8 编队场景已有一条 MWORKS/Sysplorer 候选行，记录了位置 RMSE、健康分和 formation_score。 候选实验 `formation_triangle_figure8_linear_mpc_sysblock` 的 position_rmse_m=0.0212508，formation_score=100，total_health_score=93.6862。不支撑 ROS2/PX4/QGC 在线编队、真实多机通信链路或最终编队验收声明。
- Safety boundary: 不支撑 ROS2/PX4/QGC 在线编队、真实多机通信链路或最终编队验收声明。

### 6. condense_smoke_and_legacy_sections

- Kind: `condense_without_delete`
- Target section: 5-9 legacy/smoke sections
- Claim family: ``
- Source finding: `smoke_and_staged_prominence;legacy_controller_comparison_sections`
- Report line hint: `3`
- Rationale: Smoke/staged and legacy comparison sections are useful provenance but should not dominate the final candidate narrative.
- Proposed change: Condense these sections into a short history/background block or appendix pointer after final table review.
- Safety boundary: Do not delete provenance or use smoke/staged rows as full performance conclusions.

### 7. renumber_l1_residual_subsection

- Kind: `structure_cleanup`
- Target section: 9.4 L1-inspired 残差补偿控制器首轮消融
- Claim family: ``
- Source finding: `heading_number_mismatch`
- Report line hint: `497`
- Rationale: The numbered subsection appears under a later report flow and can confuse navigation.
- Proposed change: Renumber or remove explicit subsection numbering after content placement is approved.
- Safety boundary: Structure cleanup only; do not change technical claims.

## Apply Prerequisites

- Human/PMO review approves which candidate families enter the report body.
- Historical evidence retention policy is confirmed before condensing legacy sections.
- Final acceptance boundary remains in the first report scope section.
