within MoSimQuadrotorModel.Control.Px4Ctrl;
model Px4CtrlRotorAllocator
  "Shared Sunray150 attitude-rate inner loop and signed four-rotor mapper"

  parameter MoSimQuadrotorModel.Parameters.Sunray150Parameters profile;
  parameter Real hover_speed = profile.mworks_hover_visual_rotor_speed_rad_s;
  parameter Real command_scale = hover_speed / 13.985413115099604;
  parameter Real kp_attitude = 14.142;
  parameter Real kd_attitude = 1.414;
  parameter Real kp_yaw = 5;
  parameter Real embedded_yaw_authority_reference_ratio = 0.016;
  parameter Real yaw_authority_scale =
    embedded_yaw_authority_reference_ratio / profile.moment_constant_ratio_m;
  parameter Real inner_limit = 7;
  parameter Real collective_thrust_slope =
    8 * profile.mworks_visual_thrust_coefficient * hover_speed;

  Modelica.Blocks.Interfaces.RealInput attitude_ref[3];
  Modelica.Blocks.Interfaces.RealInput attitude_mea[3];
  Modelica.Blocks.Interfaces.RealInput body_rate_mea[3];
  Modelica.Blocks.Interfaces.RealInput collective_thrust_delta(unit="N");
  Modelica.Blocks.Interfaces.RealOutput rotor_command[4](each unit="rad/s");

protected
  Real rotor_speed_delta;
  Real roll_term;
  Real pitch_term;
  Real yaw_term;

equation
  rotor_speed_delta = collective_thrust_delta / collective_thrust_slope;
  roll_term = command_scale * 0.707 * min(max(
    kp_attitude * (attitude_ref[1] + attitude_mea[1])
      + kd_attitude * body_rate_mea[1], -inner_limit), inner_limit);
  pitch_term = command_scale * 0.707 * min(max(
    kp_attitude * (attitude_ref[2] - attitude_mea[2])
      - kd_attitude * body_rate_mea[2], -inner_limit), inner_limit);
  yaw_term = command_scale * yaw_authority_scale * 0.707 * min(max(
    kp_yaw * (attitude_ref[3] - attitude_mea[3]), -inner_limit), inner_limit);
  rotor_command[1] = hover_speed + rotor_speed_delta - yaw_term - pitch_term + roll_term;
  rotor_command[2] = -hover_speed - rotor_speed_delta - yaw_term + pitch_term + roll_term;
  rotor_command[3] = hover_speed + rotor_speed_delta - yaw_term + pitch_term - roll_term;
  rotor_command[4] = -hover_speed - rotor_speed_delta - yaw_term - pitch_term - roll_term;

  annotation(
    Icon(coordinateSystem(extent={{-100,-100},{100,100}}), graphics={
      Rectangle(extent={{-100,100},{100,-100}}, lineColor={100,70,20},
        fillColor={255,250,240}, fillPattern=FillPattern.Solid),
      Text(origin={0,20}, extent={{-90,18},{90,-18}}, textString="ATTITUDE"),
      Text(origin={0,-20}, extent={{-90,18},{90,-18}}, textString="ALLOCATOR")}),
    __MWORKS(version="26.3.0"));
end Px4CtrlRotorAllocator;