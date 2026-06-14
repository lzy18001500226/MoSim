# Rotor1 Loss15 Candidate Matrix

Status: `ready_with_accepted_candidates`
Accepted candidates: `1`
Needs iteration or unverified: `10`

Read-only historical matrix. It does not run MWORKS.

## Rows

| Controller | Quality | Health | RMSE | Known fault | State |
|---|---:|---:|---:|---|---|
| pid_baseline | needs_iteration | 18.800130 | 1.375251 | None | needs_iteration_or_unverified |
| awff_pid | needs_iteration | 36.184951 | 0.364823 | None | needs_iteration_or_unverified |
| improved_pid | needs_iteration | 35.884927 | 0.371435 | None | needs_iteration_or_unverified |
| enhanced_pid | needs_iteration | 36.050556 | 0.368251 | None | needs_iteration_or_unverified |
| awff_sysblock | needs_iteration | 0.000000 | 5229.534690 | None | needs_iteration_or_unverified |
| l1_residual_sysblock | needs_iteration | 36.803366 | 0.319854 | None | needs_iteration_or_unverified |
| l1_fault_allocation_sysblock | needs_iteration | 0.000000 | 5232.532064 | True | needs_iteration_or_unverified |
| l1_online_fault_allocation_sysblock | needs_iteration | 0.000000 | 5099.066579 | False | needs_iteration_or_unverified |
| l1_multi_fault_isolation_sysblock | needs_iteration | 9.277930 | 19.599125 | False | needs_iteration_or_unverified |
| linear_mpc_sysblock | needs_iteration | 36.888509 | 0.314041 | False | needs_iteration_or_unverified |
| linear_mpc_online_fault_allocation_sysblock | pass | 62.536015 | 0.167569 | False | accepted_candidate |

## Best RMSE Candidate

- `linear_mpc_online_fault_allocation_sysblock` via `Config/scenarios/robustness/example1_rotor1_loss15_linear_mpc_online_fault_allocation_sysblock.yaml`: rmse=`0.167569`, health=`62.536015`

## Recommended Next Steps

- Use accepted rotor1_loss15 allocation/isolation candidates as the single-UAV robustness direction before multi-UAV.
- Do not promote the plain PID/AWFF rotor1_loss15 rows as passing evidence.
- After MWORKS clean preflight, rerun the minimal two-scenario PID/AWFF gate if the report needs refreshed baseline comparison.
- If selecting a final rotor-loss controller, rerun the chosen accepted candidate under current MWORKS before final report wording.

## Claim Boundary

- This matrix reads historical metrics only; it does not prove this turn ran live MWORKS.
- It does not enter multi-UAV formation work.
- It does not prove final controller acceptance without PMO/report review and any required fresh rerun.
