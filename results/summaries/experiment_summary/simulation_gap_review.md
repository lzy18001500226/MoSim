# Simulation Gap Review

- source: `results/summaries/experiment_summary/experiment_summary.csv`
- evidence audit: `results/summaries/experiment_summary/evidence_audit.md`
- scenarios audited: `60`
- pass quality gate: `46`
- needs iteration: `14`
- blocking missing evidence: `0`

## Key Findings

1. All active scenario evidence bundles have raw CSV, metrics, replay/figure evidence, and MCP logs after path cleanup.
2. The remaining gaps are result-quality gaps, not missing-file gaps.
3. The weak cluster is rotor-loss robustness, especially fixed-gain/PID-derived controllers under single-rotor loss and rotor-loss plus wind-gust conditions.

## Needs Iteration

| Priority | Scenario | Controller | Health | RMSE | Improvement | Metrics |
|---|---|---|---:|---:|---:|---|
| P2 | `robust_rotor1_loss15_example1` | `awff_pid` | 36.185 | 0.364823 | 6.96118 | `results/robustness/rotor1_loss15_example1/robust_rotor1_loss15_example1_awff_pid/metrics/robust_rotor1_loss15_example1_awff_pid.json` |
| P2 | `robust_rotor1_loss15_example1` | `awff_sysblock` | 36.0439 | 0.369058 | 5.8814 | `results/robustness/rotor1_loss15_example1/robust_rotor1_loss15_example1_awff_sysblock/metrics/robust_rotor1_loss15_example1_awff_sysblock.json` |
| P2 | `robust_rotor1_loss15_example1` | `enhanced_pid` | 36.0506 | 0.368251 | 6.08711 | `results/robustness/rotor1_loss15_example1/robust_rotor1_loss15_example1_enhanced_pid/metrics/robust_rotor1_loss15_example1_enhanced_pid.json` |
| P2 | `robust_rotor1_loss15_example1` | `improved_pid` | 35.8849 | 0.371435 | 5.27511 | `results/robustness/rotor1_loss15_example1/robust_rotor1_loss15_example1_improved_pid/metrics/robust_rotor1_loss15_example1_improved_pid.json` |
| P2 | `robust_rotor1_loss15_example1` | `l1_residual_sysblock` | 36.8034 | 0.319854 | 13.3322 | `results/robustness/rotor1_loss15_example1/robust_rotor1_loss15_example1_l1_residual_sysblock/metrics/robust_rotor1_loss15_example1_l1_residual_sysblock.json` |
| P2 | `robust_rotor1_loss15_example1` | `linear_mpc_sysblock` | 36.8885 | 0.314041 | 1.81739 | `results/robustness/rotor1_loss15_example1/robust_rotor1_loss15_example1_linear_mpc_sysblock/metrics/robust_rotor1_loss15_example1_linear_mpc_sysblock.json` |
| P2 | `robust_rotor1_loss15_example1` | `pid_baseline` | 35.6258 | 0.39212 |  | `results/robustness/rotor1_loss15_example1/robust_rotor1_loss15_example1_pid_baseline/metrics/robust_rotor1_loss15_example1_pid_baseline.json` |
| P1 | `robust_rotor1_loss15_wind_gust_example1` | `awff_sysblock` | 35.5477 | 0.430261 | -35.207 | `results/robustness/rotor1_loss15_wind_gust_example1/robust_rotor1_loss15_wind_gust_example1_awff_sysblock/metrics/robust_rotor1_loss15_wind_gust_example1_awff_sysblock.json` |
| P2 | `robust_rotor2_loss15_example1` | `awff_sysblock` | 35.8532 | 0.369011 |  | `results/robustness/rotor2_loss15_example1/robust_rotor2_loss15_example1_awff_sysblock/metrics/robust_rotor2_loss15_example1_awff_sysblock.json` |
| P2 | `robust_rotor2_loss15_example1` | `pid_baseline` | 35.3967 | 0.391914 |  | `results/robustness/rotor2_loss15_example1/robust_rotor2_loss15_example1_pid_baseline/metrics/robust_rotor2_loss15_example1_pid_baseline.json` |
| P2 | `robust_rotor3_loss15_example1` | `awff_sysblock` | 35.8529 | 0.369087 |  | `results/robustness/rotor3_loss15_example1/robust_rotor3_loss15_example1_awff_sysblock/metrics/robust_rotor3_loss15_example1_awff_sysblock.json` |
| P2 | `robust_rotor3_loss15_example1` | `pid_baseline` | 35.3937 | 0.392261 |  | `results/robustness/rotor3_loss15_example1/robust_rotor3_loss15_example1_pid_baseline/metrics/robust_rotor3_loss15_example1_pid_baseline.json` |
| P2 | `robust_rotor4_loss15_example1` | `awff_sysblock` | 36.0443 | 0.369157 |  | `results/robustness/rotor4_loss15_example1/robust_rotor4_loss15_example1_awff_sysblock/metrics/robust_rotor4_loss15_example1_awff_sysblock.json` |
| P2 | `robust_rotor4_loss15_example1` | `pid_baseline` | 35.6262 | 0.391966 |  | `results/robustness/rotor4_loss15_example1/robust_rotor4_loss15_example1_pid_baseline/metrics/robust_rotor4_loss15_example1_pid_baseline.json` |

## Recommended Next Simulation Order

1. `scenarios/robustness/example1_rotor1_loss15_wind_gust_l1_multi_fault_isolation_sysblock.yaml`
2. `scenarios/robustness/example1_rotor1_loss15_wind_gust_linear_mpc_online_fault_allocation_sysblock.yaml`
3. `scenarios/robustness/example1_rotor1_loss15_l1_multi_fault_isolation_sysblock.yaml`
4. `scenarios/robustness/example1_rotor2_loss15_l1_multi_fault_isolation_sysblock.yaml`
5. `scenarios/robustness/example1_rotor3_loss15_l1_multi_fault_isolation_sysblock.yaml`
6. `scenarios/robustness/example1_rotor4_loss15_l1_multi_fault_isolation_sysblock.yaml`

## Do Not Claim As Completed

The `needs_iteration` rows are valid negative or boundary evidence, but they should not be presented as solved robustness results until a new controller/scenario run passes the quality gate.
