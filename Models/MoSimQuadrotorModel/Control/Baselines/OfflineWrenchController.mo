within MoSimQuadrotorModel.Control.Baselines;
model OfflineWrenchController
  "Deterministic fixture for the offline WRENCH boundary"

  extends MoSimQuadrotorModel.Control.Interfaces.PartialWrenchController;
  parameter Real kp_xy = 0.15;
  parameter Real kd_xy = 0.10;
  parameter Real angle_to_rate_gain = 4;
  parameter Real rate_gain = 1.414;
  parameter Real max_tilt = 15 / 57.3;
  parameter Real max_body_torque = 7;
  parameter Real kp_z = 30.63;
  parameter Real ki_z = 22.98;
  parameter Real kd_z = 15.32;
  parameter Real max_collective_force = 45;
  parameter Real integral_limit = 2;
  Modelica.Blocks.Continuous.Derivative body_rate_estimator[3](each k = 1, each T = 0.02);
  Real position_error[3];
  Real desired_attitude[3];
  Real desired_body_rate[3];
  Real altitude_integral(start = 0, fixed = true);
  Real collective_unsaturated;
  annotation(__MWORKS(version="26.3.0"));
equation
  connect(attitude_mea, body_rate_estimator.u);
  position_error = position_ref - position_mea;
  desired_attitude[1] = min(max(-kp_xy * position_error[2] + kd_xy * velocity_mea[2], -max_tilt), max_tilt);
  desired_attitude[2] = min(max(kp_xy * position_error[1] - kd_xy * velocity_mea[1], -max_tilt), max_tilt);
  desired_attitude[3] = 0;
  desired_body_rate[1] = angle_to_rate_gain * (desired_attitude[1] - attitude_mea[1]);
  desired_body_rate[2] = angle_to_rate_gain * (desired_attitude[2] - attitude_mea[2]);
  desired_body_rate[3] = -angle_to_rate_gain * attitude_mea[3];
  der(altitude_integral) = if (altitude_integral >= integral_limit and position_error[3] > 0)
    or (altitude_integral <= -integral_limit and position_error[3] < 0) then 0 else position_error[3];
  collective_unsaturated = kp_z * position_error[3] + ki_z * altitude_integral
    - kd_z * velocity_mea[3];
  body_force[1] = 0;
  body_force[2] = 0;
  body_force[3] = min(max(collective_unsaturated, -max_collective_force), max_collective_force);
  body_torque[1] = min(max(rate_gain * (body_rate_estimator[1].y - desired_body_rate[1]), -max_body_torque), max_body_torque);
  body_torque[2] = min(max(rate_gain * (desired_body_rate[2] - body_rate_estimator[2].y), -max_body_torque), max_body_torque);
  body_torque[3] = min(max(rate_gain * (desired_body_rate[3] - body_rate_estimator[3].y), -max_body_torque), max_body_torque);
end OfflineWrenchController;
