within QuadrotorExperiments.SystemArchitecture;
model Sunray150CompleteSystemBatteryLowSysblock
  "Complete Sunray150 system smoke case with battery low triggering return mode"
  extends Sunray150CompleteSystemGraphical_Sysblock(
    system_battery_voltage_drop_per_second = 8.0);
  annotation(experiment(Algorithm = Dassl, StartTime = 0, StopTime = 1, Tolerance = 0.0001, Interval = 0.01));
  annotation(__MWORKS(hide=true));
end Sunray150CompleteSystemBatteryLowSysblock;
