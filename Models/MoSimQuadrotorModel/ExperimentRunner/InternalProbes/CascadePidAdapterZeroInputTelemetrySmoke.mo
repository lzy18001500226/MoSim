within MoSimQuadrotorModel.ExperimentRunner.InternalProbes;
model CascadePidAdapterZeroInputTelemetrySmoke
  "Zero-input telemetry probe for Cascade PID adapter conditioning"

  MoSimQuadrotorModel.ExperimentRunner.Adapters.CascadePidAttitudeThrustAdapter controller;
  Real velocity_estimate_x;
  Real velocity_estimate_y;
  Real velocity_estimate_z;
  Real angular_rate_estimate_x;
  Real angular_rate_estimate_y;
  Real angular_rate_estimate_z;
  Real core_position_x;
  Real core_position_y;
  Real core_position_z;
  Real core_velocity_x;
  Real core_velocity_y;
  Real core_velocity_z;
  Real core_attitude_w;
  Real core_attitude_x;
  Real core_attitude_y;
  Real core_attitude_z;
  Real core_angular_rate_x;
  Real core_angular_rate_y;
  Real core_angular_rate_z;
  Real core_reference_position_x;
  Real core_reference_position_y;
  Real core_reference_position_z;
  Real core_reset;
  Real core_desired_attitude_w;
  Real core_desired_attitude_x;
  Real core_desired_attitude_y;
  Real core_desired_attitude_z;
  Real core_desired_acceleration_x;
  Real core_desired_acceleration_y;
  Real core_desired_acceleration_z;
  Real core_collective_thrust_n;
  Real core_position_error_x;
  Real core_position_error_y;
  Real core_position_error_z;
  Real core_velocity_error_x;
  Real core_velocity_error_y;
  Real core_velocity_error_z;
  Real attitude_ref_x;
  Real attitude_ref_y;
  Real attitude_ref_z;
  Real collective_thrust_delta;
  Real status_code;

equation
  controller.position_ref = {0.0, 0.0, 0.0};
  controller.position_mea = {0.0, 0.0, 0.0};
  controller.attitude_mea = {0.0, 0.0, 0.0};

  velocity_estimate_x = controller.velocity_estimator[1].y;
  velocity_estimate_y = controller.velocity_estimator[2].y;
  velocity_estimate_z = controller.velocity_estimator[3].y;
  angular_rate_estimate_x = controller.angular_rate_estimator[1].y;
  angular_rate_estimate_y = controller.angular_rate_estimator[2].y;
  angular_rate_estimate_z = controller.angular_rate_estimator[3].y;
  core_position_x = controller.core.position_x_in;
  core_position_y = controller.core.position_y_in;
  core_position_z = controller.core.position_z_in;
  core_velocity_x = controller.core.velocity_x_in;
  core_velocity_y = controller.core.velocity_y_in;
  core_velocity_z = controller.core.velocity_z_in;
  core_attitude_w = controller.core.attitude_w_in;
  core_attitude_x = controller.core.attitude_x_in;
  core_attitude_y = controller.core.attitude_y_in;
  core_attitude_z = controller.core.attitude_z_in;
  core_angular_rate_x = controller.core.angular_velocity_x_in;
  core_angular_rate_y = controller.core.angular_velocity_y_in;
  core_angular_rate_z = controller.core.angular_velocity_z_in;
  core_reference_position_x = controller.core.reference_position_x_in;
  core_reference_position_y = controller.core.reference_position_y_in;
  core_reference_position_z = controller.core.reference_position_z_in;
  core_reset = controller.reset_source.y;
  core_desired_attitude_w = controller.core.desired_attitude_w_out;
  core_desired_attitude_x = controller.core.desired_attitude_x_out;
  core_desired_attitude_y = controller.core.desired_attitude_y_out;
  core_desired_attitude_z = controller.core.desired_attitude_z_out;
  core_desired_acceleration_x = controller.core.desired_acceleration_x_out;
  core_desired_acceleration_y = controller.core.desired_acceleration_y_out;
  core_desired_acceleration_z = controller.core.desired_acceleration_z_out;
  core_collective_thrust_n = controller.core.desired_collective_thrust_n_out;
  core_position_error_x = controller.core.position_error_x_out;
  core_position_error_y = controller.core.position_error_y_out;
  core_position_error_z = controller.core.position_error_z_out;
  core_velocity_error_x = controller.core.velocity_error_x_out;
  core_velocity_error_y = controller.core.velocity_error_y_out;
  core_velocity_error_z = controller.core.velocity_error_z_out;
  attitude_ref_x = controller.attitude_ref[1];
  attitude_ref_y = controller.attitude_ref[2];
  attitude_ref_z = controller.attitude_ref[3];
  collective_thrust_delta = controller.collective_thrust_delta;
  status_code = controller.status_code;

  annotation(
    experiment(Algorithm = Euler, StartTime = 0, StopTime = 0.2, Tolerance = 0.0001,
      Interval = 0.01, IntegratorStep = 0.01),
    __MWORKS(version = "26.3.0"));
end CascadePidAdapterZeroInputTelemetrySmoke;
