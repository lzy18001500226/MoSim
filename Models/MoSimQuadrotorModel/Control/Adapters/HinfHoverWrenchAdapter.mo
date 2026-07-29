within MoSimQuadrotorModel.Control.Adapters;
model HinfHoverWrenchAdapter
  "H-infinity hover-wrench CFunction law adapted to the WRENCH boundary"

  extends MoSimQuadrotorModel.Control.Interfaces.PartialWrenchController;

  parameter MoSimQuadrotorModel.Parameters.Sunray150VirtualPx4Classic profile;
  parameter Real sample_time_s = 0.01;
  MoSimQuadrotorModel.Control.Bridges.HinfHoverWrenchEquationBridge core(
    profile = profile);
  Modelica.Blocks.Continuous.Derivative angular_rate_estimator[3](
    each k = 1,
    each T = 0.02,
    each initType = Modelica.Blocks.Types.Init.InitialOutput,
    each y_start = 0);

equation
  connect(attitude_mea, angular_rate_estimator.u);

  // The H-infinity C core is ENU/FLU; its roll measurement and p rate use the
  // reciprocal sign of the shared MWORKS plant boundary.
  core.state_roll = -attitude_mea[1];
  core.state_pitch = attitude_mea[2];
  core.state_yaw = attitude_mea[3];
  core.state_p = -angular_rate_estimator[1].y;
  core.state_q = angular_rate_estimator[2].y;
  core.state_r = angular_rate_estimator[3].y;
  core.state_u = velocity_mea[1];
  core.state_v = velocity_mea[2];
  core.state_w = velocity_mea[3];
  core.state_x = position_mea[1];
  core.state_y = position_mea[2];
  core.state_z = position_mea[3];
  core.reference_roll = 0;
  core.reference_pitch = 0;
  core.reference_yaw = 0;
  core.reference_p = 0;
  core.reference_q = 0;
  core.reference_r = 0;
  core.reference_u = velocity_ref[1];
  core.reference_v = velocity_ref[2];
  core.reference_w = velocity_ref[3];
  core.reference_x = position_ref[1];
  core.reference_y = position_ref[2];
  core.reference_z = position_ref[3];
  core.enable = 1;
  core.reset = if time < 1.5 * sample_time_s then 1 else 0;

  // Preserve the CFunction's physical wrench. The shared allocator owns the
  // force/torque-to-rotor-speed conversion at this boundary.
  body_force = {0, 0, core.wrench_force_n_out};
  body_torque = {core.wrench_tau_x_nm_out, core.wrench_tau_y_nm_out,
    core.wrench_tau_z_nm_out};

  annotation(__MWORKS(version = "26.3.0"));
end HinfHoverWrenchAdapter;
