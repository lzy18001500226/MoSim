within MoSimQuadrotorModel.SceneTrace.Diagnostics;
model FactoryTraceIso29ExternalFrameWrenchBoundarySmoke
  "External-frame boundary smoke for the Iso28 wrapper wrench"
  extends FactoryTraceIso28ActuatorToWrenchBridgeSmoke;

  inner Modelica.Mechanics.MultiBody.World world(
    animateWorld = false,
    animateGravity = false,
    n = {0, 0, -1},
    gravityType = Modelica.Mechanics.MultiBody.Types.GravityTypes.UniformGravity,
    g = 9.81);
  Modelica.Mechanics.MultiBody.Parts.Body external_test_body(
    animation = false,
    r_CM = {0, 0, 0},
    m = physical_wrench_adapter.wrapper.dynamics.mass_kg,
    I_11 = 0.0085,
    I_22 = 0.0085,
    I_33 = 0.012,
    I_21 = 0,
    I_31 = 0,
    I_32 = 0,
    r_0(start = {0, 0, 0}, fixed = {true, true, true}),
    v_0(start = {0, 0, 0}, fixed = {true, true, true}),
    angles_fixed = true,
    angles_start = {0, 0, 0},
    w_0_fixed = true,
    w_0_start = {0, 0, 0},
    enforceStates = true);
  Modelica.Mechanics.MultiBody.Forces.WorldForceAndTorque external_force_and_torque(
    resolveInFrame = Modelica.Mechanics.MultiBody.Types.ResolveInFrameB.frame_b,
    animation = false);

  Real external_force_body[3](each unit = "N");
  Real external_torque_body[3](each unit = "N.m");
  Real external_applied_force_z_body(unit = "N");
  Real external_applied_yaw_torque_body(unit = "N.m");
  Real external_frame_force_z(unit = "N");
  Real external_frame_yaw_torque(unit = "N.m");
  Real external_force_application_error(unit = "N");
  Real external_torque_application_error(unit = "N.m");
  Real external_force_matches_adapter_error(unit = "N");
  Real external_torque_matches_adapter_error(unit = "N.m");
  Real external_boundary_gate_error;

equation
  external_force_body = {0, 0, physical_wrench_adapter.wrapper.total_thrust};
  external_torque_body = physical_wrench_adapter.wrapper.total_moment_body;
  external_force_and_torque.force = external_force_body;
  external_force_and_torque.torque = external_torque_body;
  connect(external_force_and_torque.frame_b, external_test_body.frame_a);

  external_applied_force_z_body = external_force_body[3];
  external_applied_yaw_torque_body = external_torque_body[3];
  external_frame_force_z = external_test_body.frame_a.f[3];
  external_frame_yaw_torque = external_test_body.frame_a.t[3];
  external_force_application_error = abs(external_frame_force_z - external_applied_force_z_body);
  external_torque_application_error = abs(external_frame_yaw_torque - external_applied_yaw_torque_body);
  external_force_matches_adapter_error = abs(external_applied_force_z_body - bridge_applied_force_z_body);
  external_torque_matches_adapter_error = abs(external_applied_yaw_torque_body - bridge_applied_yaw_torque_body);
  external_boundary_gate_error =
    external_force_application_error +
    external_torque_application_error +
    external_force_matches_adapter_error +
    external_torque_matches_adapter_error;

  annotation(experiment(Algorithm = Dassl, StartTime = 0, StopTime = 0.25, Tolerance = 0.0001, Interval = 0.001));
  annotation(__MWORKS(hide=true));
end FactoryTraceIso29ExternalFrameWrenchBoundarySmoke;
