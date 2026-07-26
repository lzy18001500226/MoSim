within MoSimQuadrotorModel.Visualization.Diagnostics;
model FactoryTraceIso30ExternalBodyStateBoundarySmoke
  "External-body state response boundary smoke after Iso29"
  extends FactoryTraceIso29ExternalFrameWrenchBoundarySmoke;

  parameter Real external_body_initial_z(unit = "m") = 0;
  parameter Real external_body_initial_vz(unit = "m/s") = 0;
  parameter Real external_body_initial_yaw_rate(unit = "rad/s") = 0;
  Real external_body_z(unit = "m");
  Real external_body_vz(unit = "m/s");
  Real external_body_yaw_rate(unit = "rad/s");
  Real external_body_z_delta(unit = "m");
  Real external_body_vz_delta(unit = "m/s");
  Real external_body_yaw_rate_delta(unit = "rad/s");
  Real external_body_vertical_response_gate;
  Real external_body_yaw_response_gate;
  Real external_body_state_boundary_gate_error;

equation
  external_body_z = external_test_body.r_0[3];
  external_body_vz = der(external_test_body.r_0[3]);
  external_body_yaw_rate = external_test_body.w_a[3];
  external_body_z_delta = external_body_z - external_body_initial_z;
  external_body_vz_delta = external_body_vz - external_body_initial_vz;
  external_body_yaw_rate_delta = external_body_yaw_rate - external_body_initial_yaw_rate;
  external_body_vertical_response_gate =
    if time >= 0.2 then abs(external_body_z_delta) + abs(external_body_vz_delta) else 0;
  external_body_yaw_response_gate =
    if time >= 0.2 then abs(external_body_yaw_rate_delta) else 0;
  external_body_state_boundary_gate_error =
    external_boundary_gate_error +
    (if time >= 0.2 and external_body_vertical_response_gate <= 1e-9 then 1 else 0);

  annotation(experiment(Algorithm = Dassl, StartTime = 0, StopTime = 0.25, Tolerance = 0.0001, Interval = 0.001));
  annotation(__MWORKS(hide=true,version="26.3.0"));
end FactoryTraceIso30ExternalBodyStateBoundarySmoke;