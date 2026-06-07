within QuadrotorExperiments.SystemArchitecture;
model Sunray150CompleteSystemOffboardLossSysblock
  "Complete Sunray150 system smoke case with offboard heartbeat loss triggering return mode"
  extends Sunray150CompleteSystemGraphical_Sysblock(
    system_offboard_loss_start_s = 0.35,
    system_offboard_loss_end_s = 0.85);
  annotation(experiment(Algorithm = Dassl, StartTime = 0, StopTime = 1, Tolerance = 0.0001, Interval = 0.01));
  annotation(__MWORKS(hide=true));
end Sunray150CompleteSystemOffboardLossSysblock;
