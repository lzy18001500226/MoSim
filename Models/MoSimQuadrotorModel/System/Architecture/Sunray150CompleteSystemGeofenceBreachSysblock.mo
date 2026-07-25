within MoSimQuadrotorModel.System.Architecture;
model Sunray150CompleteSystemGeofenceBreachSysblock
  "Complete Sunray150 system smoke case with geofence breach triggering return mode"
  extends Sunray150CompleteSystemGraphical_Sysblock(
    system_geofence_breach_start_s = 0.35,
    system_geofence_breach_end_s = 0.85);
  annotation(experiment(Algorithm = Dassl, StartTime = 0, StopTime = 1, Tolerance = 0.0001, Interval = 0.01));
  annotation(__MWORKS(hide=true,version="26.3.0"));
end Sunray150CompleteSystemGeofenceBreachSysblock;