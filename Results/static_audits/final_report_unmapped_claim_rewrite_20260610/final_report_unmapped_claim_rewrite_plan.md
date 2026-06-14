# Final Report Unmapped Claim Rewrite Plan, 2026-06-10

Status: draft rewrite plan, not final report acceptance.

## Summary

- Families: `3`
- Candidate rows: `4`
- Missing family rows: `0`
- Edits report source: `False`
- Final acceptance: `False`

## Claim Boundary

- This plan provides patch-ready wording only.
- It does not edit Docs/simulation_report.md.
- It does not generate final PDFs/video or PMO final acceptance.
- All wording keeps candidate_report_evidence_only_not_final_pmo_acceptance boundaries.

## 执行器退化与复合扰动容错候选证据

- Claim family: `fault_tolerance`
- Insert after: `13. Linear MPC-style 外环闭环结果`
- Candidate rows: `1`

Suggested paragraph:

当前候选证据可用于报告草稿说明：在 rotor1 85% 效率退化叠加横向阵风场景中，加入在线效率估计与控制分配的 LinearMPC Sysblock 候选行通过质量门。 候选实验 `robust_rotor1_loss15_wind_gust_example1_linear_mpc_online_fault_allocation_sysblock` 的 position_rmse_m=0.261434，total_health_score=51.3177，证据路径包括 metrics、raw CSV 和核心 SVG 图表。不支撑瞬态故障切换、多旋翼同时故障、真实飞控容错或最终 PMO 验收声明。

Suggested table:

| Claim Slot | Scene | Controller | RMSE m | Health | Formation | Metrics | Main Figure |
|---|---|---|---:|---:|---:|---|---|
| C1-fault-tolerance-rotor1-loss-wind | robust_rotor1_loss15_wind_gust_example1 | linear_mpc_online_fault_allocation_sysblock | 0.261434 | 51.3177 |  | `Results/robustness/rotor1_loss15_wind_gust_example1/robust_rotor1_loss15_wind_gust_example1_linear_mpc_online_fault_allocation_sysblock/metrics/robust_rotor1_loss15_wind_gust_example1_linear_mpc_online_fault_allocation_sysblock.json` | `Results/robustness/rotor1_loss15_wind_gust_example1/robust_rotor1_loss15_wind_gust_example1_linear_mpc_online_fault_allocation_sysblock/figures/robust_rotor1_loss15_wind_gust_example1_linear_mpc_online_fault_allocation_sysblock_trajectory_xy.svg` |

## 多无人机编队控制候选证据

- Claim family: `multi_uav_formation`
- Insert after: `13. Linear MPC-style 外环闭环结果`
- Candidate rows: `1`

Suggested paragraph:

当前候选证据可用于报告草稿说明：triangle figure-8 编队场景已有一条 MWORKS/Sysplorer 候选行，记录了位置 RMSE、健康分和 formation_score。 候选实验 `formation_triangle_figure8_linear_mpc_sysblock` 的 position_rmse_m=0.0212508，formation_score=100，total_health_score=93.6862。不支撑 ROS2/PX4/QGC 在线编队、真实多机通信链路或最终编队验收声明。

Suggested table:

| Claim Slot | Scene | Controller | RMSE m | Health | Formation | Metrics | Main Figure |
|---|---|---|---:|---:|---:|---|---|
| C2-formation-triangle-figure8 | formation_triangle_figure8 | linear_mpc_sysblock | 0.0212508 | 93.6862 | 100 | `Results/formation/triangle_figure8/formation_triangle_figure8_linear_mpc_sysblock/metrics/formation_triangle_figure8_linear_mpc_sysblock.json` | `Results/formation/triangle_figure8/formation_triangle_figure8_linear_mpc_sysblock/figures/formation_triangle_figure8_linear_mpc_sysblock_trajectory_xy.svg` |

## 原生轨迹留痕与视觉审查候选证据

- Claim family: `visual_trajectory_review`
- Insert after: `11. 当前图表`
- Candidate rows: `2`

Suggested paragraph:

当前候选证据可用于报告草稿说明：平面 8 字和螺旋上升 8 字留痕审查模型已有 native GUI 候选行与图表路径。 候选实验包括 `official_example1_helical_figure8_trail_sysblock`、`official_example1_planar_figure8_trail_sysblock`，position_rmse_m 分别为 0.0188363、0.0188624。不支撑 UE build/runtime/editor 成功、最终演示视频完成或最终视觉验收声明。

Suggested table:

| Claim Slot | Scene | Controller | RMSE m | Health | Formation | Metrics | Main Figure |
|---|---|---|---:|---:|---:|---|---|
| C1-visual-helical-figure8 | official_example1_helical_figure8 | linear_mpc_sysblock | 0.0188363 | 93.3606 |  | `Results/official/example1_helical_figure8/official_example1_helical_figure8_trail_sysblock/metrics/official_example1_helical_figure8_trail_sysblock.json` | `Results/official/example1_helical_figure8/official_example1_helical_figure8_trail_sysblock/figures/official_example1_helical_figure8_trail_sysblock_trajectory_xy.svg` |
| C1-visual-planar-figure8 | official_example1_planar_figure8 | linear_mpc_sysblock | 0.0188624 | 93.3638 |  | `Results/official/example1_planar_figure8/official_example1_planar_figure8_trail_sysblock/metrics/official_example1_planar_figure8_trail_sysblock.json` | `Results/official/example1_planar_figure8/official_example1_planar_figure8_trail_sysblock/figures/official_example1_planar_figure8_trail_sysblock_trajectory_xy.svg` |
