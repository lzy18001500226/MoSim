# Experiment Summary

- CSV: `results/test_reports/experiment_summary.csv`
- Total scenarios: `19`
- Done: `13`
- Pending: `6`
- Invalid: `0`

## Available Results

| Experiment | Scene | Controller | RMSE | Health | Status |
|---|---|---|---:|---:|---|
| planning_trackable_waypoint | planning_trackable_waypoint |  |  | 100 | done |
| planning_obstacle_corridor | obstacle_corridor | improved_pid |  | 100 | done |
| formation_triangle_switch | formation_triangle_switch | improved_pid |  | 100 | done |
| fault_reallocation_compare | motor_fault_reallocation_compare | nmpc_indi_l1 |  | 100 | done |
| safety_filter_guard | safety_filter_guard | nmpc_indi_l1 |  | 98.3483 | done |
| wind_nmpc_indi_l1_001 | wind_corridor | nmpc_indi_l1 |  | 93.5086 | done |
| delivery_mass_change | delivery_mass_change | nmpc_indi_l1 |  | 92.9197 | done |
| fault_motor_return | motor_fault_return | nmpc_indi_l1 |  | 82 | done |
| official_example3_pid_baseline | official_example3 | pid_baseline | 0.172311 | 50.0054 | done |
| official_example1_pid_baseline | official_example1 | pid_baseline | 0.275253 | 41.9645 | done |
| official_example2_pid_baseline | official_example2 | pid_baseline | 0.487183 | 37.3827 | done |
| mworks_mcp_example1_pid_smoke | mworks_mcp_example1 | pid_baseline | 0.977959 | 17.9231 | done |
| smoke_official_example1_pid_baseline | official_example1 | pid_baseline | 0.977959 | 17.9231 | done |

## Pending Results

| Experiment | Scene | Controller | Metrics File | Notes |
|---|---|---|---|---|
| figure8_improved_pid_001 | figure8 | improved_pid | `results/metrics/figure8_improved_pid.json` | metrics missing |
| hover_pid_baseline_001 | hover | pid_baseline | `results/metrics/hover_pid_baseline.json` | metrics missing |
| official_example1_improved_pid | official_example1 | improved_pid | `results/metrics/official_example1_improved_pid.json` | metrics missing |
| official_example3_improved_pid | official_example3 | improved_pid | `results/metrics/official_example3_improved_pid.json` | metrics missing |
| wind_improved_pid_001 | wind_figure8 | improved_pid | `results/metrics/wind_improved_pid.json` | metrics missing |
| planning_trackable_waypoint | planning_trackable_waypoint | improved_pid | `results/metrics/planning_trackable_waypoint_tracking.json` | metrics missing |
