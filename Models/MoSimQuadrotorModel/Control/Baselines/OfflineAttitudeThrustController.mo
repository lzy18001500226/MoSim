within MoSimQuadrotorModel.Control.Baselines;
model OfflineAttitudeThrustController
  "Deterministic fixture for the offline ATTITUDE_THRUST boundary"

  extends MoSimQuadrotorModel.Control.Interfaces.PartialAttitudeThrustController;
  parameter Real kp_xy = 0.15;
  parameter Real kd_xy = 0.10;
  parameter Real max_tilt = 15 / 57.3;
  parameter Real kp_z = 30.63;
  parameter Real ki_z = 22.98;
  parameter Real kd_z = 15.32;
  parameter Real max_collective_delta = 45;
  parameter Real integral_limit = 2;
  Modelica.Blocks.Continuous.Derivative velocity_estimator[3](each k = 1, each T = 0.05);
  Real position_error[3];
  Real altitude_integral(start = 0, fixed = true);
  Real collective_unsaturated;
  annotation(__MWORKS(version="26.3.0"));
equation
  connect(position_mea, velocity_estimator.u);
  position_error = position_ref - position_mea;
  der(altitude_integral) = if (altitude_integral >= integral_limit and position_error[3] > 0)
    or (altitude_integral <= -integral_limit and position_error[3] < 0) then 0 else position_error[3];
  attitude_ref[1] = min(max(kp_xy * position_error[2] - kd_xy * velocity_estimator[2].y, -max_tilt), max_tilt);
  attitude_ref[2] = min(max(kp_xy * position_error[1] - kd_xy * velocity_estimator[1].y, -max_tilt), max_tilt);
  attitude_ref[3] = 0;
  collective_unsaturated = kp_z * position_error[3] + ki_z * altitude_integral
    - kd_z * velocity_estimator[3].y;
  collective_thrust_delta = min(max(collective_unsaturated, -max_collective_delta), max_collective_delta);
end OfflineAttitudeThrustController;