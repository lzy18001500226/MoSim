# Rotor1 Loss15 Iteration Plan

Status: `blocked_by_mworks_gui`
Live gate: `blocked_by_current_sentinel`

Read-only plan. It does not run MWORKS or modify controller/model files.

## Current Targets

- `Config/scenarios/robustness/example1_rotor1_loss15_pid_baseline.yaml`: quality=`needs_iteration`, rmse=`0.3921196664904746`, health=`35.6257817116079`
- `Config/scenarios/robustness/example1_rotor1_loss15_awff_sysblock.yaml`: quality=`needs_iteration`, rmse=`0.36905752375323286`, health=`36.043895052437605`

## Future Live Rerun Command

```powershell
D:\Dev\Anaconda3\python.exe Scripts/mworks/run_mworks_batch.py --no-gui-result-viewer --no-gui-open --continue-on-failure --allow-needs-iteration Config/scenarios/robustness/example1_rotor1_loss15_pid_baseline.yaml Config/scenarios/robustness/example1_rotor1_loss15_awff_sysblock.yaml
```

## Iteration Strategy

- First rerun only the two rotor1_loss15 scenarios after fresh clean MWORKS preflight.
- Do not tune controller parameters until the two-scenario rerun refreshes raw/metrics evidence.
- If both remain needs_iteration, inspect AWFF fault-allocation/control-allocation parameters against the rotor-1 0.85 effectiveness case.
- Keep PID baseline as comparative failure/robustness evidence; do not require PID baseline to pass before optimizing AWFF.

## Forbidden Actions

- do not run live MWORKS while the upgrade-model GUI blocker is present
- do not click upgrade/login/license/save/restart/close controls from this engineering task
- do not enter multi-UAV formation work from this plan
- do not claim controller improvement until fresh rerun metrics pass the declared quality gate
