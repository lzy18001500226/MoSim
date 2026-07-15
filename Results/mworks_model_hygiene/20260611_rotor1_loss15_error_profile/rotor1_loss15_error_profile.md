# Rotor1 Loss15 Error Profile

Status: `diagnostic_profile_ready`

Read-only diagnostic profile. It does not run MWORKS and does not modify controller/model files.

## Scenario Profiles

- `Config/scenarios/robustness/example1_rotor1_loss15_pid_baseline.yaml`: controller=`pid_baseline`, quality=`needs_iteration`, rmse=`1.375251`, health=`18.800130`, worst_phase=`startup`, dominant_axis=`z`
  - startup: rmse=`2.691993`, max_error=`4.375561` at `2.41s`, dominant_axis=`z`
  - pre_fault: rmse=`1.282728`, max_error=`1.739763` at `5.22s`, dominant_axis=`y`
  - fault_window: rmse=`1.170712`, max_error=`1.320081` at `15.50s`, dominant_axis=`y`
  - recovery: rmse=`1.121064`, max_error=`1.807838` at `30.82s`, dominant_axis=`y`
  - late_tracking: rmse=`1.042064`, max_error=`1.137097` at `43.94s`, dominant_axis=`x`
- `Config/scenarios/robustness/example1_rotor1_loss15_awff_sysblock.yaml`: controller=`awff_sysblock`, quality=`needs_iteration`, rmse=`5229.534690`, health=`0.000000`, worst_phase=`late_tracking`, dominant_axis=`y`
  - startup: rmse=`55.564140`, max_error=`126.458079` at `5.00s`, dominant_axis=`y`
  - pre_fault: rmse=`639.156427`, max_error=`1167.126091` at `15.00s`, dominant_axis=`y`
  - fault_window: rmse=`1512.019074`, max_error=`1854.494088` at `19.00s`, dominant_axis=`y`
  - recovery: rmse=`3897.935996`, max_error=`5902.452622` at `35.00s`, dominant_axis=`y`
  - late_tracking: rmse=`8605.640699`, max_error=`11238.400863` at `50.00s`, dominant_axis=`y`

## AWFF vs PID

- RMSE improvement: `-380160.329%`
- Health score delta: `-18.800130`
- startup: delta_rmse=`52.872147`, improvement=`-1964.053%`
- pre_fault: delta_rmse=`637.873699`, improvement=`-49727.899%`
- fault_window: delta_rmse=`1510.848362`, improvement=`-129053.802%`
- recovery: delta_rmse=`3896.814932`, improvement=`-347599.682%`
- late_tracking: delta_rmse=`8604.598635`, improvement=`-825726.533%`

## Next Engineering Focus

- Both current rotor1_loss15 artifacts remain quality_status=needs_iteration.
- The profile is read-only historical evidence; it does not prove a new live MWORKS run.
- Use the phase and dominant-axis profile to choose the smallest next controller/model change after a fresh rerun.
- Stop before multi-UAV formation work.
