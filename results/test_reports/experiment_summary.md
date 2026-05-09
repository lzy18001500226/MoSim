# Experiment Summary

- CSV: `results/test_reports/experiment_summary.csv`
- Total scenarios: `20`
- Done: `20`
- Pending: `0`
- Invalid: `0`

## Available Results

| Experiment | Scene | Controller | RMSE | Health | Status |
|---|---|---|---:|---:|---|
| trackability_planning_trackable_waypoint | planning_trackable_waypoint |  |  | 100 | done |
| planning_obstacle_corridor | obstacle_corridor | improved_pid |  | 100 | done |
| formation_triangle_switch | formation_triangle_switch | improved_pid |  | 100 | done |
| fault_reallocation_compare | motor_fault_reallocation_compare | nmpc_indi_l1 |  | 100 | done |
| planning_trackable_waypoint | planning_trackable_waypoint | improved_pid | 0.0799408 | 99.722 | done |
| safety_filter_guard | safety_filter_guard | nmpc_indi_l1 |  | 98.3483 | done |
| wind_nmpc_indi_l1_001 | wind_corridor | nmpc_indi_l1 |  | 93.5086 | done |
| delivery_mass_change | delivery_mass_change | nmpc_indi_l1 |  | 92.9197 | done |
| fault_motor_return | motor_fault_return | nmpc_indi_l1 |  | 82 | done |
| wind_improved_pid_001 | wind_figure8 | improved_pid | 0.227463 | 74.7497 | done |
| hover_pid_baseline_001 | hover | pid_baseline | 0.500789 | 74.4184 | done |
| official_example3_improved_pid | official_example3 | improved_pid | 0.167227 | 60.5466 | done |
| official_example3_pid_baseline | official_example3 | pid_baseline | 0.172311 | 60.5054 | done |
| figure8_improved_pid_001 | figure8 | improved_pid | 0.282178 | 53.1636 | done |
| official_example1_improved_pid | official_example1 | improved_pid | 0.26989 | 52.5332 | done |
| official_example1_pid_baseline | official_example1 | pid_baseline | 0.275253 | 52.4645 | done |
| official_example2_improved_pid | official_example2 | improved_pid | 0.479834 | 48.0258 | done |
| official_example2_pid_baseline | official_example2 | pid_baseline | 0.487183 | 47.8827 | done |
| mworks_mcp_example1_pid_smoke | mworks_mcp_example1 | pid_baseline | 0.977959 | 17.9231 | done |
| smoke_official_example1_pid_baseline | official_example1 | pid_baseline | 0.977959 | 17.9231 | done |

## Evidence Levels

| Experiment | Source | Evidence Level | Raw File |
|---|---|---|---|
| official_example1_pid_baseline | MWORKS_MCP | real_sysplorer_mcp_full_baseline | `results/raw/official_example1_pid_baseline.csv` |
| official_example2_pid_baseline | MWORKS_MCP | real_sysplorer_mcp_full_baseline | `results/raw/official_example2_pid_baseline.csv` |
| official_example3_pid_baseline | MWORKS_MCP | real_sysplorer_mcp_full_baseline | `results/raw/official_example3_pid_baseline.csv` |
| official_example1_improved_pid | MWORKS_MCP | real_sysplorer_mcp_full_improved_pid | `results/raw/official_example1_improved_pid.csv` |
| official_example2_improved_pid | MWORKS_MCP | real_sysplorer_mcp_full_improved_pid | `results/raw/official_example2_improved_pid.csv` |
| official_example3_improved_pid | MWORKS_MCP | real_sysplorer_mcp_full_improved_pid | `results/raw/official_example3_improved_pid.csv` |
| mworks_mcp_example1_pid_smoke | glob:results/metrics/mworks_mcp_*.json | real_sysplorer_mcp_smoke | `results/raw/mworks_mcp_example1_pid_smoke.csv` |
| smoke_official_example1_pid_baseline | glob:results/metrics/smoke_*.json | offline_smoke_demo | `results/raw/smoke_official_example1_pid_baseline.csv` |
| trackability_planning_trackable_waypoint | glob:results/metrics/trackability_*.json | offline_reference_trackability | `` |
| figure8_improved_pid_001 | offline_script | offline_tracking_demo | `results/raw/figure8_improved_pid.csv` |
| hover_pid_baseline_001 | offline_script | offline_tracking_demo | `results/raw/hover_pid_baseline.csv` |
| planning_trackable_waypoint | offline_script | offline_tracking_demo | `results/raw/planning_trackable_waypoint_tracking.csv` |
| wind_improved_pid_001 | offline_script | offline_tracking_demo | `results/raw/wind_improved_pid.csv` |
| fault_motor_return | scenarios/fault/motor_fault_return.yaml | offline_scenario_demo | `results/raw/fault_motor_return_reference.csv` |
| fault_reallocation_compare | scenarios/fault/reallocation_compare.yaml | offline_scenario_demo | `results/raw/fault_reallocation_compare.csv` |
| formation_triangle_switch | scenarios/formation/triangle_switch.yaml | offline_reference_generation | `results/raw/reference_formation_triangle_switch.csv` |
| delivery_mass_change | scenarios/mass/delivery_mass_change.yaml | offline_scenario_demo | `results/raw/delivery_mass_change.csv` |
| planning_obstacle_corridor | scenarios/planning/obstacle_corridor.yaml | offline_reference_generation | `results/raw/reference_planning_obstacle_corridor.csv` |
| safety_filter_guard | scenarios/safety/filter_guard.yaml | offline_scenario_demo | `results/raw/safety_filter_guard.csv` |
| wind_nmpc_indi_l1_001 | scenarios/wind/nmpc_indi_l1.yaml | offline_scenario_demo | `results/raw/wind_nmpc_indi_l1.csv` |

## Pending Results

| Experiment | Scene | Controller | Metrics File | Notes |
|---|---|---|---|---|
