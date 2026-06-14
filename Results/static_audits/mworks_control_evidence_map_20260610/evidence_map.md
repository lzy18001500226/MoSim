# MWORKS Control Evidence Map, 2026-06-10

Status: static audit only. No live MWORKS/Sysplorer/Syslab GUI, MCP, check_model, or SimulateModel action was executed for this map.

## Inputs

- CSV summary: `Results/static_audits/mworks_control_evidence_map_20260610/experiment_summary.csv`
- Markdown summary: `Results/static_audits/mworks_control_evidence_map_20260610/experiment_summary.md`

## Counts

| Metric | Count |
|---|---:|
| total_rows | 176 |
| metrics_only_rows_priority_empty | 95 |
| formal_rows_priority_nonempty | 81 |
| formal_pass_rows | 64 |
| formal_needs_iteration_rows | 17 |
| formal_visual_review_rows | 2 |

Priority distribution, formal rows only:

| Priority | Count |
|---|---:|
| P0 | 6 |
| P1 | 46 |
| P1-B | 12 |
| P1-C | 12 |
| P1-D | 2 |
| P2 | 1 |
| visual-review | 2 |

Quality distribution, formal rows only:

| Quality | Count |
|---|---:|
| needs_iteration | 17 |
| pass | 64 |

## Claim Boundary

Supported by this static map:

- A formal MWORKS/Sysplorer metric-result matrix exists for 81 priority-tagged rows.
- 64 priority-tagged rows have quality_status=pass and may be considered candidate report evidence after PMO/report selection.
- The formal matrix includes official baseline, optimized-controller, robustness/fault-tolerance, safety-filter, visual-review, and one multi-UAV formation evidence family.

Not supported by this static map:

- Do not treat the 95 priority-empty metrics-only rows as formal acceptance rows.
- Do not claim all robustness or fault cases pass; 17 formal rows are needs_iteration.
- Do not claim native Syslab report completion from these rows alone.
- Do not claim live MWORKS no-start attach success, ROS2 planner readiness, UE build/runtime success, or final closed-loop product acceptance from this static audit.

## Representative Candidate Evidence

| Priority | Family | Experiment | Scene | Controller | RMSE | Health | Formation | Evidence Level |
|---|---|---|---|---|---:|---:|---:|---|
| P0 | official_baseline | official_example1_pid_baseline | official_example1 | pid_baseline | 0.276295 | 52.464 |  | real_sysplorer_mcp_full_baseline |
| P0 | optimized_controller | official_example1_improved_pid | official_example1 | improved_pid | 0.26989 | 52.5332 |  | real_sysplorer_mcp_full_improved_pid |
| P1 | optimized_controller | official_example1_awff_indi_sysblock | official_example1 | awff_indi_sysblock | 0.243827 | 55.8166 |  | real_sysplorer_mcp_sysblock_l1_indi_full |
| P1 | robustness | robust_mass20_example1_awff_pid | robust_mass20_example1 | awff_pid | 0.276253 | 51.8138 |  | real_sysplorer_mcp_robust_mass20_awff |
| P1-B | fault_tolerance | robust_rotor1_loss15_example1_l1_fault_allocation_sysblock | robust_rotor1_loss15_example1 | l1_fault_allocation_sysblock | 0.24434 | 55.8166 |  | real_sysplorer_mcp_sysblock_l1_fault_allocation_rotor_loss_ablation |
| P1-B | optimized_controller | sunray150_complete_system_battery_low_sysblock | system_battery_low | awff_complete_system | 1.46884 | 9.92465 |  | real_sysplorer_mcp_complete_system_battery_low |
| P1-C | fault_tolerance | robust_rotor1_loss15_wind_gust_example1_l1_multi_fault_isolation_sysblock | robust_rotor1_loss15_wind_gust_example1 | l1_multi_fault_isolation_sysblock | 0.272091 | 50.9942 |  | real_sysplorer_mcp_sysblock_l1_multi_fault_isolation_rotor_loss_wind_gust |
| P1-D | safety_filter | official_example1_qp_nmpc_safety_return_land_sysblock | official_example1 | nmpc_indi_l1 | 0.208361 | 56.146 |  | real_sysplorer_mcp_sysblock_qp_nmpc_safety_return_land |
| P2 | multi_uav_formation | formation_triangle_figure8_linear_mpc_sysblock | formation_triangle_figure8 | linear_mpc_sysblock | 0.0212508 | 93.6862 | 100 | real_sysplorer_mcp_sysblock_formation_triangle_figure8_linear_mpc |
| visual-review | visual_trajectory_review | official_example1_helical_figure8_trail_sysblock | official_example1_helical_figure8 | linear_mpc_sysblock | 0.0188363 | 93.3606 |  | real_sysplorer_mcp_native_gui_helical_figure8_trail |

## Needs-Iteration Exclusions

These rows are formal evidence rows but should not be used as positive submission claims without retuning, replacement, or explicit negative/boundary discussion.

| Priority | Family | Experiment | Scene | Controller | RMSE | Health | Reason |
|---|---|---|---|---|---:|---:|---|
| P1 | fault_tolerance | robust_rotor1_loss15_example1_awff_pid | robust_rotor1_loss15_example1 | awff_pid | 0.364823 | 36.185 | quality_status=needs_iteration |
| P1 | fault_tolerance | robust_rotor1_loss15_example1_awff_sysblock | robust_rotor1_loss15_example1 | awff_sysblock | 0.369058 | 36.0439 | quality_status=needs_iteration |
| P1 | fault_tolerance | robust_rotor1_loss15_example1_enhanced_pid | robust_rotor1_loss15_example1 | enhanced_pid | 0.368251 | 36.0506 | quality_status=needs_iteration |
| P1 | fault_tolerance | robust_rotor1_loss15_example1_improved_pid | robust_rotor1_loss15_example1 | improved_pid | 0.371435 | 35.8849 | quality_status=needs_iteration |
| P1 | fault_tolerance | robust_rotor1_loss15_example1_l1_residual_sysblock | robust_rotor1_loss15_example1 | l1_residual_sysblock | 0.319854 | 36.8034 | quality_status=needs_iteration |
| P1 | fault_tolerance | robust_rotor1_loss15_example1_linear_mpc_sysblock | robust_rotor1_loss15_example1 | linear_mpc_sysblock | 0.314041 | 36.8885 | quality_status=needs_iteration |
| P1 | fault_tolerance | robust_rotor1_loss15_example1_pid_baseline | robust_rotor1_loss15_example1 | pid_baseline | 0.39212 | 35.6258 | quality_status=needs_iteration |
| P1 | fault_tolerance | robust_rotor2_loss15_example1_awff_sysblock | robust_rotor2_loss15_example1 | awff_sysblock | 0.369011 | 35.8532 | quality_status=needs_iteration |
| P1 | fault_tolerance | robust_rotor2_loss15_example1_pid_baseline | robust_rotor2_loss15_example1 | pid_baseline | 0.391914 | 35.3967 | quality_status=needs_iteration |
| P1 | fault_tolerance | robust_rotor3_loss15_example1_awff_sysblock | robust_rotor3_loss15_example1 | awff_sysblock | 0.369087 | 35.8529 | quality_status=needs_iteration |
| P1 | fault_tolerance | robust_rotor3_loss15_example1_pid_baseline | robust_rotor3_loss15_example1 | pid_baseline | 0.392261 | 35.3937 | quality_status=needs_iteration |
| P1 | fault_tolerance | robust_rotor4_loss15_example1_awff_sysblock | robust_rotor4_loss15_example1 | awff_sysblock | 0.369157 | 36.0443 | quality_status=needs_iteration |
| P1 | fault_tolerance | robust_rotor4_loss15_example1_pid_baseline | robust_rotor4_loss15_example1 | pid_baseline | 0.391966 | 35.6262 | quality_status=needs_iteration |
| P1-C | fault_tolerance | robust_rotor1_loss15_wind_gust_example1_awff_sysblock | robust_rotor1_loss15_wind_gust_example1 | awff_sysblock | 0.379238 | 35.9674 | quality_status=needs_iteration |
| P1-C | fault_tolerance | robust_rotor2_loss15_wind_gust_example1_awff_sysblock | robust_rotor2_loss15_wind_gust_example1 | awff_sysblock | 0.374681 | 35.8117 | quality_status=needs_iteration |
| P1-C | fault_tolerance | robust_rotor3_loss15_wind_gust_example1_awff_sysblock | robust_rotor3_loss15_wind_gust_example1 | awff_sysblock | 0.364125 | 35.8996 | quality_status=needs_iteration |
| P1-C | fault_tolerance | robust_rotor4_loss15_wind_gust_example1_awff_sysblock | robust_rotor4_loss15_wind_gust_example1 | awff_sysblock | 0.368973 | 36.0511 | quality_status=needs_iteration |

## Next Use

- Use `candidate_submission_evidence_rows` in `evidence_map.json` as the candidate pool for report selection.
- Keep `needs_iteration_exclusions` out of positive performance claims unless the report explicitly discusses them as failed or boundary cases.
- Select final report rows by claim, not by directory presence: baseline, optimized controller, robustness, safety/fault tolerance, visual trajectory review, and formation each need a named row and metric file.
