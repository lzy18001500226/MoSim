# Candidate Submission Evidence Manifest, 2026-06-10

Status: review candidate, not final PMO acceptance.

- Source evidence map: `Results/static_audits/mworks_control_evidence_map_20260610/evidence_map.json`
- Candidate rows: `13`

## Boundaries

- Not final PMO acceptance.
- Does not claim native Syslab report completion.
- Does not claim live MWORKS no-start attach success.
- Does not claim ROS2 planner_ready, controller handoff, or closed_loop.
- Does not claim UE build/runtime/editor success or live command echo.
- Does not include metrics-only rows or needs_iteration rows as positive performance evidence.

## Candidate Rows

| Claim Slot | Experiment | Scene | Controller | Quality | RMSE | Health | Formation | Evidence Level |
|---|---|---|---|---|---:|---:|---:|---|
| C0-baseline-step-example1 | official_example1_pid_baseline | official_example1 | pid_baseline | pass | 0.276295 | 52.464 |  | real_sysplorer_mcp_full_baseline |
| C0-baseline-helix-example2 | official_example2_pid_baseline | official_example2 | pid_baseline | pass | 0.487183 | 47.8827 |  | real_sysplorer_mcp_full_baseline |
| C0-baseline-figure8-example3 | official_example3_pid_baseline | official_example3 | pid_baseline | pass | 0.172311 | 60.5054 |  | real_sysplorer_mcp_full_baseline |
| C1-optimized-step-example1 | official_example1_linear_mpc_sysblock | official_example1 | linear_mpc_sysblock | pass | 0.135014 | 65.6656 |  | real_sysplorer_mcp_sysblock_linear_mpc_full |
| C1-optimized-helix-example2 | official_example2_linear_mpc_sysblock | official_example2 | linear_mpc_sysblock | pass | 0.429079 | 62.0578 |  | real_sysplorer_mcp_sysblock_linear_mpc_helix_full |
| C1-optimized-figure8-example3 | official_example3_linear_mpc_sysblock | official_example3 | linear_mpc_sysblock | pass | 0.084584 | 68.3362 |  | real_sysplorer_mcp_sysblock_linear_mpc_figure8_full |
| C1-robustness-mass20 | robust_mass20_example1_linear_mpc_sysblock | robust_mass20_example1 | linear_mpc_sysblock | pass | 0.2588 | 55.3882 |  | real_sysplorer_mcp_sysblock_linear_mpc_mass20_ablation |
| C1-robustness-wind-gust | robust_wind_gust_example1_linear_mpc_sysblock | robust_wind_gust_example1 | linear_mpc_sysblock | pass | 0.2588 | 55.3882 |  | real_sysplorer_mcp_sysblock_linear_mpc_wind_ablation |
| C1-fault-tolerance-rotor1-loss-wind | robust_rotor1_loss15_wind_gust_example1_linear_mpc_online_fault_allocation_sysblock | robust_rotor1_loss15_wind_gust_example1 | linear_mpc_online_fault_allocation_sysblock | pass | 0.261434 | 51.3177 |  | real_sysplorer_mcp_sysblock_linear_mpc_online_fault_allocation_rotor_loss_wind_gust |
| C1-safety-filter-return-land | official_example1_qp_nmpc_safety_return_land_sysblock | official_example1 | nmpc_indi_l1 | pass | 0.208361 | 56.146 |  | real_sysplorer_mcp_sysblock_qp_nmpc_safety_return_land |
| C2-formation-triangle-figure8 | formation_triangle_figure8_linear_mpc_sysblock | formation_triangle_figure8 | linear_mpc_sysblock | pass | 0.0212508 | 93.6862 | 100 | real_sysplorer_mcp_sysblock_formation_triangle_figure8_linear_mpc |
| C1-visual-helical-figure8 | official_example1_helical_figure8_trail_sysblock | official_example1_helical_figure8 | linear_mpc_sysblock | pass | 0.0188363 | 93.3606 |  | real_sysplorer_mcp_native_gui_helical_figure8_trail |
| C1-visual-planar-figure8 | official_example1_planar_figure8_trail_sysblock | official_example1_planar_figure8 | linear_mpc_sysblock | pass | 0.0188624 | 93.3638 |  | real_sysplorer_mcp_native_gui_planar_figure8_trail |
