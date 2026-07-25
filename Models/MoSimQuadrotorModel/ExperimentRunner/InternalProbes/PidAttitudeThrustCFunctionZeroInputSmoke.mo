within MoSimQuadrotorModel.ExperimentRunner.InternalProbes;
model PidAttitudeThrustCFunctionZeroInputSmoke
  "Direct CFunction zero-input and hover-output isolation"

  MoSimQuadrotorModel.ExperimentRunner.Adapters.PidAttitudeThrustCFunction core;
  Real desired_attitude[4];
  Real desired_acceleration[3];
  Real desired_collective_thrust_n;
  Real status_code;
  Real algorithm_id;

equation
  core.algorithm_id_in = 1;
  core.dt_in = 0.01;
  core.position_x_in = 0;
  core.position_y_in = 0;
  core.position_z_in = 0;
  core.velocity_x_in = 0;
  core.velocity_y_in = 0;
  core.velocity_z_in = 0;
  core.attitude_w_in = 1;
  core.attitude_x_in = 0;
  core.attitude_y_in = 0;
  core.attitude_z_in = 0;
  core.angular_velocity_x_in = 0;
  core.angular_velocity_y_in = 0;
  core.angular_velocity_z_in = 0;
  core.reference_position_x_in = 0;
  core.reference_position_y_in = 0;
  core.reference_position_z_in = 0;
  core.reference_velocity_x_in = 0;
  core.reference_velocity_y_in = 0;
  core.reference_velocity_z_in = 0;
  core.reference_acceleration_x_in = 0;
  core.reference_acceleration_y_in = 0;
  core.reference_acceleration_z_in = 0;
  core.reference_yaw_in = 0;
  core.mass_kg_in = 1;
  core.gravity_mps2_in = 9.80665;
  core.max_tilt_rad_in = 0.5235987755982989;
  core.min_collective_thrust_n_in = 0;
  core.max_collective_thrust_n_in = 19.6133;
  core.schedule_x_in = 0;
  core.schedule_y_in = 0;
  core.schedule_z_in = 0;
  core.fuzzy_error_x_in = 0;
  core.fuzzy_error_y_in = 0;
  core.fuzzy_error_z_in = 0;
  core.neural_residual_x_in = 0;
  core.neural_residual_y_in = 0;
  core.neural_residual_z_in = 0;
  core.enable_in = 1;
  core.reset_in = 1;

  desired_attitude = {
    core.desired_attitude_w_out,
    core.desired_attitude_x_out,
    core.desired_attitude_y_out,
    core.desired_attitude_z_out};
  desired_acceleration = {
    core.desired_acceleration_x_out,
    core.desired_acceleration_y_out,
    core.desired_acceleration_z_out};
  desired_collective_thrust_n = core.desired_collective_thrust_n_out;
  status_code = core.status_code_out;
  algorithm_id = core.algorithm_id_out_out;

  annotation(
    experiment(Algorithm = Euler, StartTime = 0, StopTime = 0.03, Tolerance = 0.0001,
      Interval = 0.01, IntegratorStep = 0.01),
    __MWORKS(version = "26.3.0"));
end PidAttitudeThrustCFunctionZeroInputSmoke;
