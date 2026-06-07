within QuadrotorExperiments.SupportModels;
model TraceLookupStandaloneSmoke
  "Standalone diagnostic model for B0 ROS2 adapter trace lookup result binding"
  TraceInlineReference traceReference;

  Real x_ref;
  Real y_ref;
  Real z_ref;
  Real yaw_ref;
  Real z_ref_rate;
  Real probe_state(start = 0, fixed = true);

equation
  x_ref = traceReference.position_command[1];
  y_ref = traceReference.position_command[2];
  z_ref = traceReference.position_command[3];
  yaw_ref = traceReference.yaw_ref;
  z_ref_rate = traceReference.z_ref_rate;
  der(probe_state) = x_ref;

  annotation(experiment(Algorithm = Dassl, StartTime = 0, StopTime = 2.0, Tolerance = 0.0001, Interval = 0.05));
  annotation(__MWORKS(hide=true));
end TraceLookupStandaloneSmoke;
