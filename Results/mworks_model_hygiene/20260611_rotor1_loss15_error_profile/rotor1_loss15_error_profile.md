# Rotor1 Loss15 Error Profile

Status: `diagnostic_profile_ready`

Read-only diagnostic profile. It does not run MWORKS and does not modify controller/model files.

## Scenario Profiles

- `Config/scenarios/robustness/example1_rotor1_loss15_pid_baseline.yaml`: controller=`pid_baseline`, quality=`needs_iteration`, rmse=`0.392120`, health=`35.625782`, worst_phase=`startup`, dominant_axis=`y`
  - startup: rmse=`0.745190`, max_error=`1.401969` at `0.99s`, dominant_axis=`z`
  - pre_fault: rmse=`0.293615`, max_error=`0.397978` at `5.33s`, dominant_axis=`x`
  - fault_window: rmse=`0.279834`, max_error=`0.282842` at `16.56s`, dominant_axis=`x`
  - recovery: rmse=`0.394193`, max_error=`0.974188` at `31.02s`, dominant_axis=`x`
  - late_tracking: rmse=`0.288741`, max_error=`0.372628` at `43.84s`, dominant_axis=`y`
- `Config/scenarios/robustness/example1_rotor1_loss15_awff_sysblock.yaml`: controller=`awff_sysblock`, quality=`needs_iteration`, rmse=`0.369058`, health=`36.043895`, worst_phase=`startup`, dominant_axis=`z`
  - startup: rmse=`0.717817`, max_error=`1.329313` at `0.93s`, dominant_axis=`z`
  - pre_fault: rmse=`0.278319`, max_error=`0.422077` at `5.32s`, dominant_axis=`x`
  - fault_window: rmse=`0.255746`, max_error=`0.261832` at `16.30s`, dominant_axis=`x`
  - recovery: rmse=`0.364778`, max_error=`0.939098` at `30.95s`, dominant_axis=`x`
  - late_tracking: rmse=`0.267002`, max_error=`0.356744` at `40.96s`, dominant_axis=`y`

## AWFF vs PID

- RMSE improvement: `5.881%`
- Health score delta: `0.418113`
- startup: delta_rmse=`-0.027373`, improvement=`3.673%`
- pre_fault: delta_rmse=`-0.015295`, improvement=`5.209%`
- fault_window: delta_rmse=`-0.024088`, improvement=`8.608%`
- recovery: delta_rmse=`-0.029415`, improvement=`7.462%`
- late_tracking: delta_rmse=`-0.021739`, improvement=`7.529%`

## Next Engineering Focus

- Both current rotor1_loss15 artifacts remain quality_status=needs_iteration.
- The profile is read-only historical evidence; it does not prove a new live MWORKS run.
- Use the phase and dominant-axis profile to choose the smallest next controller/model change after a fresh rerun.
- Stop before multi-UAV formation work.
