within MoSimQuadrotorModel.ExperimentRunner.Adapters;
model OfflineBodyRateThrustController
  "Deterministic fixture for the offline BODY_RATE_THRUST boundary"

  extends MoSimQuadrotorModel.ExperimentRunner.Interfaces.PartialBodyRateThrustController;
  parameter Real kp_xy = 0.15;
  parameter Real kd_xy = 0.10;
  parameter Real angle_to_rate_gain = 4;
  parameter Real max_tilt = 15 / 57.3;
  parameter Real max_body_rate = 1.5;
  parameter Real kp_z = 30.63;
  parameter Real ki_z = 22.98;
  parameter Real kd_z = 15.32;
  parameter Real max_collective_delta = 45;
  parameter Real integral_limit = 2;
  Modelica.Blocks.Continuous.Derivative velocity_estimator[3](each k = 1, each T = 0.05);
  Real position_error[3];
  Real desired_attitude[3];
  Real altitude_integral(start = 0, fixed = true);
  Real collective_unsaturated;
equation
  connect(position_mea, velocity_estimator.u);
  position_error = position_ref - position_mea;
  desired_attitude[1] = min(max(-kp_xy * position_error[2] + kd_xy * velocity_estimator[2].y, -max_tilt), max_tilt);
  desired_attitude[2] = min(max(kp_xy * position_error[1] - kd_xy * velocity_estimator[1].y, -max_tilt), max_tilt);
  desired_attitude[3] = 0;
  body_rate_ref[1] = min(max(angle_to_rate_gain * (desired_attitude[1] - attitude_mea[1]), -max_body_rate), max_body_rate);
  body_rate_ref[2] = min(max(angle_to_rate_gain * (desired_attitude[2] - attitude_mea[2]), -max_body_rate), max_body_rate);
  body_rate_ref[3] = min(max(-angle_to_rate_gain * attitude_mea[3], -max_body_rate), max_body_rate);
  der(altitude_integral) = if (altitude_integral >= integral_limit and position_error[3] > 0)
    or (altitude_integral <= -integral_limit and position_error[3] < 0) then 0 else position_error[3];
  collective_unsaturated = kp_z * position_error[3] + ki_z * altitude_integral
    - kd_z * velocity_estimator[3].y;
  collective_thrust_delta = min(max(collective_unsaturated, -max_collective_delta), max_collective_delta);
end OfflineBodyRateThrustController;
