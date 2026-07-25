within MoSimQuadrotorModel.ExperimentRunner.Adapters;
model OfflineAttitudeRateAllocator
  "MWORKS offline attitude/rate inner loop plus allocator; not PX4 evidence"

  parameter MoSimQuadrotorModel.Parameters.Sunray150VirtualPx4Classic profile;
  parameter Real hover_speed = profile.mworks_hover_visual_rotor_speed_rad_s;
  parameter Real command_scale = hover_speed / 13.985413115099604;
  parameter Real kp_attitude = 14.142;
  parameter Real kd_attitude = 1.414;
  parameter Real kp_yaw = 5;
  parameter Real inner_limit = 7;
  parameter Real body_rate_filter_time_constant_s = 0.01
    "Derivative filter time constant; the official PID default is 0.01 s";
  Modelica.Blocks.Interfaces.RealInput attitude_ref[3];
  Modelica.Blocks.Interfaces.RealInput attitude_mea[3];
  Modelica.Blocks.Interfaces.RealInput collective_thrust_delta;
  Modelica.Blocks.Interfaces.RealOutput rotor_command[4];
  Modelica.Blocks.Continuous.Derivative body_rate_estimator[3](
    each k = 1,
    each T = body_rate_filter_time_constant_s,
    each initType = Modelica.Blocks.Types.Init.InitialOutput,
    each y_start = 0);
protected
  Real roll_term;
  Real pitch_term;
  Real yaw_term;
  annotation(__MWORKS(version="26.3.0"));
equation
  connect(attitude_mea, body_rate_estimator.u);
  roll_term = command_scale * 0.707 * min(max(kp_attitude * (attitude_ref[1] + attitude_mea[1])
    + kd_attitude * body_rate_estimator[1].y, -inner_limit), inner_limit);
  pitch_term = command_scale * 0.707 * min(max(kp_attitude * (attitude_ref[2] - attitude_mea[2])
    - kd_attitude * body_rate_estimator[2].y, -inner_limit), inner_limit);
  yaw_term = command_scale * 0.707 * min(max(kp_yaw * (attitude_ref[3] - attitude_mea[3]), -inner_limit), inner_limit);
  rotor_command[1] = hover_speed + collective_thrust_delta - yaw_term - pitch_term + roll_term;
  rotor_command[2] = -hover_speed - collective_thrust_delta - yaw_term + pitch_term + roll_term;
  rotor_command[3] = hover_speed + collective_thrust_delta - yaw_term + pitch_term - roll_term;
  rotor_command[4] = -hover_speed - collective_thrust_delta - yaw_term - pitch_term - roll_term;
end OfflineAttitudeRateAllocator;
