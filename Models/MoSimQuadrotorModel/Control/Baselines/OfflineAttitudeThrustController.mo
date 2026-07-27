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
  parameter MoSimQuadrotorModel.Parameters.Sunray150VirtualPx4Classic profile;
  parameter Real hover_speed = profile.mworks_hover_visual_rotor_speed_rad_s;
  parameter Real lift_coefficient = profile.mworks_visual_thrust_coefficient;
  parameter Real collective_thrust_slope = 8 * lift_coefficient * hover_speed;
  parameter Real max_collective_rotor_speed_delta = 45;
  parameter Real integral_limit = 2;
  Real position_error[3];
  Real altitude_integral(start = 0, fixed = true);
  Real collective_unsaturated;
  annotation(__MWORKS(version="26.3.0"));
equation
  position_error = position_ref - position_mea;
  der(altitude_integral) = if (altitude_integral >= integral_limit and position_error[3] > 0)
    or (altitude_integral <= -integral_limit and position_error[3] < 0) then 0 else position_error[3];
  attitude_ref[1] = min(max(kp_xy * position_error[2] - kd_xy * velocity_mea[2], -max_tilt), max_tilt);
  attitude_ref[2] = min(max(kp_xy * position_error[1] - kd_xy * velocity_mea[1], -max_tilt), max_tilt);
  attitude_ref[3] = 0;
  collective_unsaturated = kp_z * position_error[3] + ki_z * altitude_integral
    - kd_z * velocity_mea[3];
  collective_thrust_delta = collective_thrust_slope * min(max(collective_unsaturated,
    -max_collective_rotor_speed_delta), max_collective_rotor_speed_delta);
end OfflineAttitudeThrustController;
