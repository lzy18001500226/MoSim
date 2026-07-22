within MoSimQuadrotorModel.System.Architecture;
model Sunray150CompleteSystemGPSDropoutSysblock
  "Complete Sunray150 system smoke case with GPS dropout triggering degraded navigation mode"
  extends Sunray150CompleteSystemGraphical_Sysblock(
    system_degraded_nav_start_s = 0.35,
    system_degraded_nav_end_s = 0.85,
    perception(gps_dropout_start_s = 0.35, gps_dropout_end_s = 0.85),
    mission_computer(estimator_degraded_threshold = 0.6, degraded_nav_start_s = 0.35, degraded_nav_end_s = 0.85));
  annotation(experiment(Algorithm = Dassl, StartTime = 0, StopTime = 1, Tolerance = 0.0001, Interval = 0.01));
  annotation(__MWORKS(hide=true));
end Sunray150CompleteSystemGPSDropoutSysblock;
