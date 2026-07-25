within MoSimQuadrotorModel.ExperimentRunner.Adapters;
model OfflineBodyRateAllocator
  "MWORKS offline body-rate inner loop plus allocator; not PX4 evidence"

  parameter MoSimQuadrotorModel.Parameters.Sunray150VirtualPx4Classic profile;
  parameter Real hover_speed = profile.mworks_hover_visual_rotor_speed_rad_s;
  parameter Real command_scale = hover_speed / 13.985413115099604;
  parameter Real rate_gain = command_scale * 0.707 * 1.414;
  parameter Real max_rate_term = command_scale * 0.707 * 7;
  Modelica.Blocks.Interfaces.RealInput body_rate_ref[3];
  Modelica.Blocks.Interfaces.RealInput attitude_mea[3];
  Modelica.Blocks.Interfaces.RealInput collective_thrust_delta;
  Modelica.Blocks.Interfaces.RealOutput rotor_command[4];
  Modelica.Blocks.Continuous.Derivative body_rate_estimator[3](each k = 1, each T = 0.02);
protected
  Real roll_term;
  Real pitch_term;
  Real yaw_term;
  annotation(__MWORKS(version="26.3.0"));
equation
  connect(attitude_mea, body_rate_estimator.u);
  roll_term = min(max(rate_gain * (body_rate_estimator[1].y - body_rate_ref[1]), -max_rate_term), max_rate_term);
  pitch_term = min(max(rate_gain * (body_rate_ref[2] - body_rate_estimator[2].y), -max_rate_term), max_rate_term);
  yaw_term = min(max(rate_gain * (body_rate_ref[3] - body_rate_estimator[3].y), -max_rate_term), max_rate_term);
  rotor_command[1] = hover_speed + collective_thrust_delta - yaw_term - pitch_term + roll_term;
  rotor_command[2] = -hover_speed - collective_thrust_delta - yaw_term + pitch_term + roll_term;
  rotor_command[3] = hover_speed + collective_thrust_delta - yaw_term + pitch_term - roll_term;
  rotor_command[4] = -hover_speed - collective_thrust_delta - yaw_term - pitch_term - roll_term;
end OfflineBodyRateAllocator;
