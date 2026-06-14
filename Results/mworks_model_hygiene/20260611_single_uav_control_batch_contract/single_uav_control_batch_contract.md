# Single-UAV Control Batch Contract

Status: `passed`
Scenario count: `13`

Static/read-only contract. It does not call MWORKS, Sysplorer, MCP, `check_model`, `SimulateModel`, ROS2, UE, or GUI/window tools.

## Coverage

- `official_step`: `True`
- `official_helix`: `True`
- `official_figure8`: `True`
- `pid_baseline`: `True`
- `awff_sysblock`: `True`
- `linear_mpc_sysblock`: `True`
- `single_rotor_efficiency_degradation`: `True`
- `wind_gust`: `True`
- `formation_excluded`: `True`

## Scenarios

- `Config/scenarios/official/example1_pid_baseline.yaml` -> `QuadrotorModel.Examples.Example1` / `pid_baseline`
- `Config/scenarios/official/example1_awff_sysblock.yaml` -> `QuadrotorExperiments.Example1AWFFSysblockClosedLoop` / `awff_sysblock`
- `Config/scenarios/official/example2_pid_baseline.yaml` -> `QuadrotorModel.Examples.Example2` / `pid_baseline`
- `Config/scenarios/official/example2_improved_pid.yaml` -> `QuadrotorExperiments.Example2ImprovedPID` / `improved_pid`
- `Config/scenarios/official/example2_awff_sysblock_helix_tuned.yaml` -> `QuadrotorExperiments.Example2HelixTunedAWFFSysblockClosedLoop` / `awff_sysblock`
- `Config/scenarios/official/example3_pid_baseline.yaml` -> `QuadrotorModel.Examples.Example3` / `pid_baseline`
- `Config/scenarios/official/example3_awff_sysblock.yaml` -> `QuadrotorExperiments.Example3AWFFSysblockClosedLoop` / `awff_sysblock`
- `Config/scenarios/official/example3_awff_indi_sysblock.yaml` -> `QuadrotorExperiments.Example3INDISysblockClosedLoop` / `awff_indi_sysblock`
- `Config/scenarios/official/example3_linear_mpc_sysblock.yaml` -> `QuadrotorExperiments.Example3LinearMPCSysblockClosedLoop` / `linear_mpc_sysblock`
- `Config/scenarios/robustness/example1_rotor1_loss15_pid_baseline.yaml` -> `QuadrotorExperiments.Example1Rotor1Loss15PID` / `pid_baseline`
- `Config/scenarios/robustness/example1_rotor1_loss15_awff_sysblock.yaml` -> `QuadrotorExperiments.Example1Rotor1Loss15AWFFSysblockClosedLoop` / `awff_sysblock`
- `Config/scenarios/robustness/example1_wind_gust_pid_baseline.yaml` -> `QuadrotorExperiments.Example1WindGustPID` / `pid_baseline`
- `Config/scenarios/robustness/example1_wind_gust_awff_sysblock.yaml` -> `QuadrotorExperiments.Example1WindGustAWFFSysblockClosedLoop` / `awff_sysblock`

## Future Live Command

```powershell
D:\Dev\Anaconda3\python.exe Scripts/mworks/run_mworks_batch.py --no-gui-result-viewer --no-gui-open --continue-on-failure Config/scenarios/official/example1_pid_baseline.yaml Config/scenarios/official/example1_awff_sysblock.yaml Config/scenarios/official/example2_pid_baseline.yaml Config/scenarios/official/example2_improved_pid.yaml Config/scenarios/official/example2_awff_sysblock_helix_tuned.yaml Config/scenarios/official/example3_pid_baseline.yaml Config/scenarios/official/example3_awff_sysblock.yaml Config/scenarios/official/example3_awff_indi_sysblock.yaml Config/scenarios/official/example3_linear_mpc_sysblock.yaml Config/scenarios/robustness/example1_rotor1_loss15_pid_baseline.yaml Config/scenarios/robustness/example1_rotor1_loss15_awff_sysblock.yaml Config/scenarios/robustness/example1_wind_gust_pid_baseline.yaml Config/scenarios/robustness/example1_wind_gust_awff_sysblock.yaml
```

## Preconditions

- current MWORKS/Sysplorer/Syslab preflight is clean and not blocked by upgrade, login, license, authorization, crash, save, restart, or unknown windows
- formal Dynamics smoke blocker is either cleared or explicitly declared unrelated to this single-UAV control batch by PMO/user
- live run uses no automatic GUI result viewer and no GUI-open side paths
- after each live result, evaluate_result_quality.py must pass or preserve the failed result as iteration evidence

## Claim Boundary

- This contract prepares a single-UAV control batch only.
- It does not run MWORKS, check_model, SimulateModel, or GUI actions.
- It does not prove controller performance, mission success, closed_loop, or multi-UAV readiness.
- Formation scenarios are explicitly out of scope for this goal stage.

## Findings

- none
