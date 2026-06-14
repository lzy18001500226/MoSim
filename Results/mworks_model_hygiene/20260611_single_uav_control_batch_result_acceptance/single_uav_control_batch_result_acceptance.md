# Single-UAV Control Batch Result Acceptance

Status: `needs_iteration`
Present results: `13` / `13`
Accepted results: `11`
Needs iteration: `2`

This checker is read-only. It does not run MWORKS, Sysplorer, MCP, `check_model`, `SimulateModel`, ROS2, UE, or GUI/window tools.

## Scenarios

- `Config/scenarios/official/example1_pid_baseline.yaml`: `accepted` / quality=`pass`
- `Config/scenarios/official/example1_awff_sysblock.yaml`: `accepted` / quality=`pass`
- `Config/scenarios/official/example2_pid_baseline.yaml`: `accepted` / quality=`pass`
- `Config/scenarios/official/example2_improved_pid.yaml`: `accepted` / quality=`pass`
- `Config/scenarios/official/example2_awff_sysblock_helix_tuned.yaml`: `accepted` / quality=`pass`
- `Config/scenarios/official/example3_pid_baseline.yaml`: `accepted` / quality=`pass`
- `Config/scenarios/official/example3_awff_sysblock.yaml`: `accepted` / quality=`pass`
- `Config/scenarios/official/example3_awff_indi_sysblock.yaml`: `accepted` / quality=`pass`
- `Config/scenarios/official/example3_linear_mpc_sysblock.yaml`: `accepted` / quality=`pass`
- `Config/scenarios/robustness/example1_rotor1_loss15_pid_baseline.yaml`: `needs_iteration` / quality=`needs_iteration`
- `Config/scenarios/robustness/example1_rotor1_loss15_awff_sysblock.yaml`: `needs_iteration` / quality=`needs_iteration`
- `Config/scenarios/robustness/example1_wind_gust_pid_baseline.yaml`: `accepted` / quality=`pass`
- `Config/scenarios/robustness/example1_wind_gust_awff_sysblock.yaml`: `accepted` / quality=`pass`

## Iteration Targets

- `Config/scenarios/robustness/example1_rotor1_loss15_pid_baseline.yaml`: quality=`needs_iteration`, rmse=`1.3752511875197824`, health=`18.80013043497445`
- `Config/scenarios/robustness/example1_rotor1_loss15_awff_sysblock.yaml`: quality=`needs_iteration`, rmse=`5229.534690333248`, health=`0.0`

## Claim Boundary

- Read-only acceptance of declared single-UAV raw/metrics/log artifacts.
- Existing artifacts may be historical evidence; this checker does not prove this turn ran live MWORKS.
- Status needs_iteration is preserved as engineering progress, not hidden as failure.
- This does not prove multi-UAV readiness and stops before formation work.

## Findings

- none
