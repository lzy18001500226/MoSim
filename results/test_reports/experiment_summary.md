# Experiment Summary

- CSV: `results/test_reports/experiment_summary.csv`
- Total scenarios: `23`
- Done: `20`
- Pending: `3`
- Invalid: `0`

## Available Results

| Experiment | Scene | Controller | RMSE | Health | Status |
|---|---|---|---:|---:|---|
| official_example3_improved_pid | official_example3 | improved_pid | 0.167227 | 60.5466 | done |
| official_example3_pid_baseline | official_example3 | pid_baseline | 0.172311 | 60.5054 | done |
| official_example1_enhanced_pid | official_example1 | enhanced_pid | 0.26625 | 55.4225 | done |
| robust_wind_gust_example1_enhanced_pid | robust_wind_gust_example1 | enhanced_pid | 0.31826 | 55.0045 | done |
| official_example1_improved_pid | official_example1 | improved_pid | 0.26989 | 52.5332 | done |
| official_example1_pid_baseline | official_example1 | pid_baseline | 0.275253 | 52.4645 | done |
| robust_mass20_example1_enhanced_pid | robust_mass20_example1 | enhanced_pid | 0.28261 | 52.4446 | done |
| official_example1_awff_pid | official_example1 | awff_pid | 0.259914 | 52.3347 | done |
| robust_wind_gust_example1_improved_pid | robust_wind_gust_example1 | improved_pid | 0.322116 | 52.1171 | done |
| robust_wind_gust_example1_pid_baseline | robust_wind_gust_example1 | pid_baseline | 0.334706 | 51.9899 | done |
| robust_mass20_example1_improved_pid | robust_mass20_example1 | improved_pid | 0.286484 | 51.8863 | done |
| robust_mass20_example1_pid_baseline | robust_mass20_example1 | pid_baseline | 0.291441 | 51.8207 | done |
| official_example2_improved_pid | official_example2 | improved_pid | 0.479834 | 48.0258 | done |
| official_example2_pid_baseline | official_example2 | pid_baseline | 0.487183 | 47.8827 | done |
| robust_rotor1_loss15_example1_enhanced_pid | robust_rotor1_loss15_example1 | enhanced_pid | 0.368251 | 36.0506 | done |
| robust_rotor1_loss15_example1_improved_pid | robust_rotor1_loss15_example1 | improved_pid | 0.371435 | 35.8849 | done |
| robust_rotor1_loss15_example1_pid_baseline | robust_rotor1_loss15_example1 | pid_baseline | 0.39212 | 35.6258 | done |
| mworks_mcp_example1_awff_pid_smoke | mworks_mcp_example1 | awff_pid | 0.926241 | 29.2493 | done |
| mworks_mcp_example1_enhanced_pid_smoke | mworks_mcp_example1 | enhanced_pid | 0.953097 | 28.8416 | done |
| mworks_mcp_example1_pid_smoke | mworks_mcp_example1 | pid_baseline | 0.977959 | 28.4231 | done |

## Evidence Levels

| Experiment | Source | Evidence Level | Raw File |
|---|---|---|---|
| official_example1_awff_pid | MWORKS_MCP | real_sysplorer_mcp_full_awff_pid | `results/raw/official_example1_awff_pid.csv` |
| official_example1_pid_baseline | MWORKS_MCP | real_sysplorer_mcp_full_baseline | `results/raw/official_example1_pid_baseline.csv` |
| official_example2_pid_baseline | MWORKS_MCP | real_sysplorer_mcp_full_baseline | `results/raw/official_example2_pid_baseline.csv` |
| official_example3_pid_baseline | MWORKS_MCP | real_sysplorer_mcp_full_baseline | `results/raw/official_example3_pid_baseline.csv` |
| official_example1_enhanced_pid | MWORKS_MCP | real_sysplorer_mcp_full_enhanced_pid | `results/raw/official_example1_enhanced_pid.csv` |
| official_example1_improved_pid | MWORKS_MCP | real_sysplorer_mcp_full_improved_pid | `results/raw/official_example1_improved_pid.csv` |
| official_example2_improved_pid | MWORKS_MCP | real_sysplorer_mcp_full_improved_pid | `results/raw/official_example2_improved_pid.csv` |
| official_example3_improved_pid | MWORKS_MCP | real_sysplorer_mcp_full_improved_pid | `results/raw/official_example3_improved_pid.csv` |
| robust_mass20_example1_enhanced_pid | MWORKS_MCP | real_sysplorer_mcp_robust_mass20_ablation | `results/raw/robust_mass20_example1_enhanced_pid.csv` |
| robust_mass20_example1_improved_pid | MWORKS_MCP | real_sysplorer_mcp_robust_mass20_ablation | `results/raw/robust_mass20_example1_improved_pid.csv` |
| robust_mass20_example1_pid_baseline | MWORKS_MCP | real_sysplorer_mcp_robust_mass20_ablation | `results/raw/robust_mass20_example1_pid_baseline.csv` |
| robust_rotor1_loss15_example1_enhanced_pid | MWORKS_MCP | real_sysplorer_mcp_robust_rotor_loss_ablation | `results/raw/robust_rotor1_loss15_example1_enhanced_pid.csv` |
| robust_rotor1_loss15_example1_improved_pid | MWORKS_MCP | real_sysplorer_mcp_robust_rotor_loss_ablation | `results/raw/robust_rotor1_loss15_example1_improved_pid.csv` |
| robust_rotor1_loss15_example1_pid_baseline | MWORKS_MCP | real_sysplorer_mcp_robust_rotor_loss_ablation | `results/raw/robust_rotor1_loss15_example1_pid_baseline.csv` |
| robust_wind_gust_example1_enhanced_pid | MWORKS_MCP | real_sysplorer_mcp_robust_wind_gust_ablation | `results/raw/robust_wind_gust_example1_enhanced_pid.csv` |
| robust_wind_gust_example1_improved_pid | MWORKS_MCP | real_sysplorer_mcp_robust_wind_gust_ablation | `results/raw/robust_wind_gust_example1_improved_pid.csv` |
| robust_wind_gust_example1_pid_baseline | MWORKS_MCP | real_sysplorer_mcp_robust_wind_gust_ablation | `results/raw/robust_wind_gust_example1_pid_baseline.csv` |
| mworks_mcp_example1_awff_pid_smoke | MWORKS_MCP | real_sysplorer_mcp_smoke | `results/raw/mworks_mcp_example1_awff_pid_smoke.csv` |
| mworks_mcp_example1_enhanced_pid_smoke | MWORKS_MCP | real_sysplorer_mcp_smoke | `results/raw/mworks_mcp_example1_enhanced_pid_smoke.csv` |
| mworks_mcp_example1_pid_smoke | MWORKS_MCP | real_sysplorer_mcp_smoke | `results/raw/mworks_mcp_example1_pid_smoke.csv` |

## Pending Results

| Experiment | Scene | Controller | Metrics File | Notes |
|---|---|---|---|---|
| robust_mass20_example1_awff_pid | robust_mass20_example1 | awff_pid | `results/metrics/robust_mass20_example1_awff_pid.json` | metrics missing |
| robust_rotor1_loss15_example1_awff_pid | robust_rotor1_loss15_example1 | awff_pid | `results/metrics/robust_rotor1_loss15_example1_awff_pid.json` | metrics missing |
| robust_wind_gust_example1_awff_pid | robust_wind_gust_example1 | awff_pid | `results/metrics/robust_wind_gust_example1_awff_pid.json` | metrics missing |
