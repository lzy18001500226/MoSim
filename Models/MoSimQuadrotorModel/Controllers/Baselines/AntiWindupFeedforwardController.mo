within MoSimQuadrotorModel.Controllers.Baselines;
model AntiWindupFeedforwardController
  "Project-owned PID controller with conditional integration and reference feedforward"
  parameter Real kp_x = 1.65;
  parameter Real ki_x = 0.0;
  parameter Real kd_x = 1.0;
  parameter Real kp_y = 1.65;
  parameter Real ki_y = 0.0;
  parameter Real kd_y = 1.0;
  parameter Real kp_z = 8.0;
  parameter Real ki_z = 6.0;
  parameter Real kd_z = 4.0;
  parameter Real kp_roll = 14.142;
  parameter Real kd_roll = 1.70;
  parameter Real kp_pitch = 14.142;
  parameter Real kd_pitch = 1.70;
  parameter Real kp_yaw = 5.0;
  parameter Real roll_pitch_cmd_limit = 12 / 57.3;
  parameter Real attitude_cmd_limit = 6.5;
  parameter Real yaw_cmd_limit = 6.5;
  parameter Real output_limit = 20.0;
  parameter Real reference_feedforward_z = 0.35;
  parameter Real reference_filter_T = 0.20;
  parameter Real position_derivative_filter_T = 0.05;
  parameter Real altitude_derivative_filter_T = 0.08;
  parameter Real attitude_derivative_filter_T = 0.03;

  Modelica.Blocks.Interfaces.RealInput position_command[3];
  Modelica.Blocks.Interfaces.RealInput position[3];
  Modelica.Blocks.Interfaces.RealInput angle[3];
  Modelica.Blocks.Interfaces.RealOutput y;
  Modelica.Blocks.Interfaces.RealOutput y1;
  Modelica.Blocks.Interfaces.RealOutput y2;
  Modelica.Blocks.Interfaces.RealOutput y3;

  Real ex;
  Real ey;
  Real ez;
  Real e_roll;
  Real e_pitch;
  Real e_yaw;
  Real ex_filter(start = 0, fixed = true);
  Real ey_filter(start = 0, fixed = true);
  Real ez_filter(start = 0, fixed = true);
  Real e_roll_filter(start = 0, fixed = true);
  Real e_pitch_filter(start = 0, fixed = true);
  Real dex;
  Real dey;
  Real dez;
  Real d_roll;
  Real d_pitch;
  Real ix(start = 0, fixed = true);
  Real iy(start = 0, fixed = true);
  Real iz(start = 0, fixed = true);
  Real x_cmd_raw;
  Real y_cmd_raw;
  Real z_cmd_raw;
  Real x_cmd;
  Real y_cmd;
  Real z_cmd;
  Real roll_cmd_raw;
  Real pitch_cmd_raw;
  Real yaw_cmd_raw;
  Real roll_cmd;
  Real pitch_cmd;
  Real yaw_cmd;
  Real z_ref_filter(start = 0, fixed = true);
  Real z_ref_rate;
  Real common;
  Real yaw_mix;
  Real pitch_mix;
  Real roll_mix;
  Real u1_raw;
  Real u2_raw;
  Real u3_raw;
  Real u4_raw;

equation
  ex = position_command[1] - position[1];
  ey = position_command[2] - position[2];
  ez = position_command[3] - position[3];

  der(z_ref_filter) = (position_command[3] - z_ref_filter) / reference_filter_T;
  z_ref_rate = (position_command[3] - z_ref_filter) / reference_filter_T;

  der(ex_filter) = (ex - ex_filter) / position_derivative_filter_T;
  der(ey_filter) = (ey - ey_filter) / position_derivative_filter_T;
  der(ez_filter) = (ez - ez_filter) / altitude_derivative_filter_T;
  dex = (ex - ex_filter) / position_derivative_filter_T;
  dey = (ey - ey_filter) / position_derivative_filter_T;
  dez = (ez - ez_filter) / altitude_derivative_filter_T;

  x_cmd_raw = kp_x * ex + ki_x * ix + kd_x * dex;
  y_cmd_raw = kp_y * ey + ki_y * iy + kd_y * dey;
  z_cmd_raw = kp_z * ez + ki_z * iz + kd_z * dez + reference_feedforward_z * z_ref_rate;
  x_cmd = saturate(0.1 * x_cmd_raw, roll_pitch_cmd_limit);
  y_cmd = saturate(0.1 * y_cmd_raw, roll_pitch_cmd_limit);
  z_cmd = z_cmd_raw;

  der(ix) = if abs(0.1 * x_cmd_raw) < roll_pitch_cmd_limit or ex * x_cmd_raw < 0 then ex else 0;
  der(iy) = if abs(0.1 * y_cmd_raw) < roll_pitch_cmd_limit or ey * y_cmd_raw < 0 then ey else 0;
  der(iz) = if abs(z_cmd_raw) < output_limit or ez * z_cmd_raw < 0 then ez else 0;

  e_pitch = x_cmd - angle[2];
  e_roll = y_cmd + angle[1];
  e_yaw = -angle[3];

  der(e_pitch_filter) = (e_pitch - e_pitch_filter) / attitude_derivative_filter_T;
  der(e_roll_filter) = (e_roll - e_roll_filter) / attitude_derivative_filter_T;
  d_pitch = (e_pitch - e_pitch_filter) / attitude_derivative_filter_T;
  d_roll = (e_roll - e_roll_filter) / attitude_derivative_filter_T;

  pitch_cmd_raw = kp_pitch * e_pitch + kd_pitch * d_pitch;
  roll_cmd_raw = kp_roll * e_roll + kd_roll * d_roll;
  yaw_cmd_raw = kp_yaw * e_yaw;
  pitch_cmd = saturate(pitch_cmd_raw, attitude_cmd_limit);
  roll_cmd = saturate(roll_cmd_raw, attitude_cmd_limit);
  yaw_cmd = saturate(yaw_cmd_raw, yaw_cmd_limit);

  common = z_cmd;
  yaw_mix = 0.707 * yaw_cmd;
  pitch_mix = 0.707 * pitch_cmd;
  roll_mix = 0.707 * roll_cmd;

  u1_raw = common + (-yaw_mix - pitch_mix + roll_mix);
  u2_raw = -(common + (yaw_mix - pitch_mix - roll_mix));
  u3_raw = common + (-yaw_mix + pitch_mix - roll_mix);
  u4_raw = -(common + (yaw_mix + pitch_mix + roll_mix));

  y = saturate(u1_raw, output_limit);
  y1 = saturate(u2_raw, output_limit);
  y2 = saturate(u3_raw, output_limit);
  y3 = saturate(u4_raw, output_limit);
  annotation(__MWORKS(hide=true));
end AntiWindupFeedforwardController;
