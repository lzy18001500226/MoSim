# Candidate Report Table Scaffold, 2026-06-10

Status: draft table scaffold, not final report acceptance.

- Source manifest: `Results/static_audits/submission_evidence_manifest_20260610/candidate_submission_evidence_manifest.json`
- Source figure inventory: `Results/static_audits/candidate_figure_readiness_20260610/candidate_figure_readiness_inventory.json`
- Rows: `13`
- Figure-ready rows: `13`
- Missing figure slots: `0`
- Non-pass quality slots: `0`

## Claim Boundary

- This scaffold is for report table drafting only.
- It is not final PMO acceptance and does not select final wording.
- Rows must keep candidate_report_evidence_only_not_final_pmo_acceptance until PMO/report review accepts final claims.

## Candidate Claim Families

| Claim Family | Rows |
|---|---:|
| fault_tolerance | 1 |
| multi_uav_formation | 1 |
| official_baseline | 3 |
| optimized_controller | 3 |
| robustness | 2 |
| safety_filter | 1 |
| visual_trajectory_review | 2 |

## Draft Table Rows

| Claim Slot | Family | Scene | Controller | RMSE m | Health | Formation | Figure Ready |
|---|---|---|---|---:|---:|---:|---|
| C0-baseline-step-example1 | official_baseline | official_example1 | pid_baseline | 0.276295 | 52.464 |  | True |
| C0-baseline-helix-example2 | official_baseline | official_example2 | pid_baseline | 0.487183 | 47.8827 |  | True |
| C0-baseline-figure8-example3 | official_baseline | official_example3 | pid_baseline | 0.172311 | 60.5054 |  | True |
| C1-optimized-step-example1 | optimized_controller | official_example1 | linear_mpc_sysblock | 0.135014 | 65.6656 |  | True |
| C1-optimized-helix-example2 | optimized_controller | official_example2 | linear_mpc_sysblock | 0.429079 | 62.0578 |  | True |
| C1-optimized-figure8-example3 | optimized_controller | official_example3 | linear_mpc_sysblock | 0.084584 | 68.3362 |  | True |
| C1-robustness-mass20 | robustness | robust_mass20_example1 | linear_mpc_sysblock | 0.2588 | 55.3882 |  | True |
| C1-robustness-wind-gust | robustness | robust_wind_gust_example1 | linear_mpc_sysblock | 0.2588 | 55.3882 |  | True |
| C1-fault-tolerance-rotor1-loss-wind | fault_tolerance | robust_rotor1_loss15_wind_gust_example1 | linear_mpc_online_fault_allocation_sysblock | 0.261434 | 51.3177 |  | True |
| C1-safety-filter-return-land | safety_filter | official_example1 | nmpc_indi_l1 | 0.208361 | 56.146 |  | True |
| C2-formation-triangle-figure8 | multi_uav_formation | formation_triangle_figure8 | linear_mpc_sysblock | 0.0212508 | 93.6862 | 100 | True |
| C1-visual-helical-figure8 | visual_trajectory_review | official_example1_helical_figure8 | linear_mpc_sysblock | 0.0188363 | 93.3606 |  | True |
| C1-visual-planar-figure8 | visual_trajectory_review | official_example1_planar_figure8 | linear_mpc_sysblock | 0.0188624 | 93.3638 |  | True |

## Figure Pointers

| Claim Slot | Trajectory | Error | Metrics | Altitude |
|---|---|---|---|---|
| C0-baseline-step-example1 | `Results/official/example1_step/official_example1_pid_baseline/figures/official_example1_pid_baseline_trajectory_xy.svg` | `Results/official/example1_step/official_example1_pid_baseline/figures/official_example1_pid_baseline_position_error.svg` | `Results/official/example1_step/official_example1_pid_baseline/figures/metrics_summary.svg` | `Results/official/example1_step/official_example1_pid_baseline/figures/altitude_tracking.svg` |
| C0-baseline-helix-example2 | `Results/official/example2_helix/official_example2_pid_baseline/figures/trajectory_xy.svg` | `Results/official/example2_helix/official_example2_pid_baseline/figures/position_error.svg` | `Results/official/example2_helix/official_example2_pid_baseline/figures/metrics_summary.svg` | `Results/official/example2_helix/official_example2_pid_baseline/figures/altitude_tracking.svg` |
| C0-baseline-figure8-example3 | `Results/official/example3_figure8/official_example3_pid_baseline/figures/trajectory_xy.svg` | `Results/official/example3_figure8/official_example3_pid_baseline/figures/position_error.svg` | `Results/official/example3_figure8/official_example3_pid_baseline/figures/metrics_summary.svg` | `Results/official/example3_figure8/official_example3_pid_baseline/figures/altitude_tracking.svg` |
| C1-optimized-step-example1 | `Results/official/example1_step/official_example1_linear_mpc_sysblock/figures/official_example1_linear_mpc_sysblock_trajectory_xy.svg` | `Results/official/example1_step/official_example1_linear_mpc_sysblock/figures/official_example1_linear_mpc_sysblock_position_error.svg` | `Results/official/example1_step/official_example1_linear_mpc_sysblock/figures/official_example1_linear_mpc_sysblock_metrics_summary.svg` | `Results/official/example1_step/official_example1_linear_mpc_sysblock/figures/official_example1_linear_mpc_sysblock_altitude_tracking.svg` |
| C1-optimized-helix-example2 | `Results/official/example2_helix/official_example2_linear_mpc_sysblock/figures/official_example2_linear_mpc_sysblock_trajectory_xy.svg` | `Results/official/example2_helix/official_example2_linear_mpc_sysblock/figures/official_example2_linear_mpc_sysblock_position_error.svg` | `Results/official/example2_helix/official_example2_linear_mpc_sysblock/figures/official_example2_linear_mpc_sysblock_metrics_summary.svg` | `Results/official/example2_helix/official_example2_linear_mpc_sysblock/figures/official_example2_linear_mpc_sysblock_altitude_tracking.svg` |
| C1-optimized-figure8-example3 | `Results/official/example3_figure8/official_example3_linear_mpc_sysblock/figures/official_example3_linear_mpc_sysblock_trajectory_xy.svg` | `Results/official/example3_figure8/official_example3_linear_mpc_sysblock/figures/official_example3_linear_mpc_sysblock_position_error.svg` | `Results/official/example3_figure8/official_example3_linear_mpc_sysblock/figures/official_example3_linear_mpc_sysblock_metrics_summary.svg` | `Results/official/example3_figure8/official_example3_linear_mpc_sysblock/figures/official_example3_linear_mpc_sysblock_altitude_tracking.svg` |
| C1-robustness-mass20 | `Results/robustness/mass20_example1/robust_mass20_example1_linear_mpc_sysblock/figures/robust_mass20_example1_linear_mpc_sysblock_trajectory_xy.svg` | `Results/robustness/mass20_example1/robust_mass20_example1_linear_mpc_sysblock/figures/robust_mass20_example1_linear_mpc_sysblock_position_error.svg` | `Results/robustness/mass20_example1/robust_mass20_example1_linear_mpc_sysblock/figures/robust_mass20_example1_linear_mpc_sysblock_metrics_summary.svg` | `Results/robustness/mass20_example1/robust_mass20_example1_linear_mpc_sysblock/figures/robust_mass20_example1_linear_mpc_sysblock_altitude_tracking.svg` |
| C1-robustness-wind-gust | `Results/robustness/wind_gust_example1/robust_wind_gust_example1_linear_mpc_sysblock/figures/robust_wind_gust_example1_linear_mpc_sysblock_trajectory_xy.svg` | `Results/robustness/wind_gust_example1/robust_wind_gust_example1_linear_mpc_sysblock/figures/robust_wind_gust_example1_linear_mpc_sysblock_position_error.svg` | `Results/robustness/wind_gust_example1/robust_wind_gust_example1_linear_mpc_sysblock/figures/robust_wind_gust_example1_linear_mpc_sysblock_metrics_summary.svg` | `Results/robustness/wind_gust_example1/robust_wind_gust_example1_linear_mpc_sysblock/figures/robust_wind_gust_example1_linear_mpc_sysblock_altitude_tracking.svg` |
| C1-fault-tolerance-rotor1-loss-wind | `Results/robustness/rotor1_loss15_wind_gust_example1/robust_rotor1_loss15_wind_gust_example1_linear_mpc_online_fault_allocation_sysblock/figures/robust_rotor1_loss15_wind_gust_example1_linear_mpc_online_fault_allocation_sysblock_trajectory_xy.svg` | `Results/robustness/rotor1_loss15_wind_gust_example1/robust_rotor1_loss15_wind_gust_example1_linear_mpc_online_fault_allocation_sysblock/figures/robust_rotor1_loss15_wind_gust_example1_linear_mpc_online_fault_allocation_sysblock_position_error.svg` | `Results/robustness/rotor1_loss15_wind_gust_example1/robust_rotor1_loss15_wind_gust_example1_linear_mpc_online_fault_allocation_sysblock/figures/robust_rotor1_loss15_wind_gust_example1_linear_mpc_online_fault_allocation_sysblock_metrics_summary.svg` | `Results/robustness/rotor1_loss15_wind_gust_example1/robust_rotor1_loss15_wind_gust_example1_linear_mpc_online_fault_allocation_sysblock/figures/robust_rotor1_loss15_wind_gust_example1_linear_mpc_online_fault_allocation_sysblock_altitude_tracking.svg` |
| C1-safety-filter-return-land | `Results/official/example1_step/official_example1_qp_nmpc_safety_return_land_sysblock/figures/official_example1_qp_nmpc_safety_return_land_sysblock_trajectory_xy.svg` | `Results/official/example1_step/official_example1_qp_nmpc_safety_return_land_sysblock/figures/official_example1_qp_nmpc_safety_return_land_sysblock_position_error.svg` | `Results/official/example1_step/official_example1_qp_nmpc_safety_return_land_sysblock/figures/official_example1_qp_nmpc_safety_return_land_sysblock_metrics_summary.svg` | `Results/official/example1_step/official_example1_qp_nmpc_safety_return_land_sysblock/figures/official_example1_qp_nmpc_safety_return_land_sysblock_altitude_tracking.svg` |
| C2-formation-triangle-figure8 | `Results/formation/triangle_figure8/formation_triangle_figure8_linear_mpc_sysblock/figures/formation_triangle_figure8_linear_mpc_sysblock_trajectory_xy.svg` | `Results/formation/triangle_figure8/formation_triangle_figure8_linear_mpc_sysblock/figures/formation_triangle_figure8_linear_mpc_sysblock_position_error.svg` | `Results/formation/triangle_figure8/formation_triangle_figure8_linear_mpc_sysblock/figures/formation_triangle_figure8_linear_mpc_sysblock_metrics_summary.svg` | `Results/formation/triangle_figure8/formation_triangle_figure8_linear_mpc_sysblock/figures/formation_triangle_figure8_linear_mpc_sysblock_altitude_tracking.svg` |
| C1-visual-helical-figure8 | `Results/official/example1_helical_figure8/official_example1_helical_figure8_trail_sysblock/figures/official_example1_helical_figure8_trail_sysblock_trajectory_xy.svg` | `Results/official/example1_helical_figure8/official_example1_helical_figure8_trail_sysblock/figures/official_example1_helical_figure8_trail_sysblock_position_error.svg` | `Results/official/example1_helical_figure8/official_example1_helical_figure8_trail_sysblock/figures/official_example1_helical_figure8_trail_sysblock_metrics_summary.svg` | `Results/official/example1_helical_figure8/official_example1_helical_figure8_trail_sysblock/figures/official_example1_helical_figure8_trail_sysblock_altitude_tracking.svg` |
| C1-visual-planar-figure8 | `Results/official/example1_planar_figure8/official_example1_planar_figure8_trail_sysblock/figures/official_example1_planar_figure8_trail_sysblock_trajectory_xy.svg` | `Results/official/example1_planar_figure8/official_example1_planar_figure8_trail_sysblock/figures/official_example1_planar_figure8_trail_sysblock_position_error.svg` | `Results/official/example1_planar_figure8/official_example1_planar_figure8_trail_sysblock/figures/official_example1_planar_figure8_trail_sysblock_metrics_summary.svg` | `Results/official/example1_planar_figure8/official_example1_planar_figure8_trail_sysblock/figures/official_example1_planar_figure8_trail_sysblock_altitude_tracking.svg` |
