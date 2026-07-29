within MoSimQuadrotorModel.Control.Allocation;
model OfflineWrenchAllocator
  "MWORKS offline wrench-to-rotor allocator"

  parameter MoSimQuadrotorModel.Parameters.Sunray150VirtualPx4Classic profile;
  parameter Real hover_speed = profile.mworks_hover_visual_rotor_speed_rad_s;
  parameter Real maximum_speed = profile.mworks_max_visual_rotor_speed_rad_s;
  parameter Real lift_coefficient = profile.mworks_visual_thrust_coefficient;
  parameter Real moment_ratio_m = profile.moment_constant_ratio_m;
  parameter Real arm_x_m = abs(profile.mworks_rotor_center_m[1, 1]);
  parameter Real arm_y_m = abs(profile.mworks_rotor_center_m[1, 2]);
  parameter Real thrust_per_rotor_speed_delta = 2 * lift_coefficient * hover_speed;
  parameter Real hover_collective_thrust_n = 4 * lift_coefficient * hover_speed ^ 2;
  parameter Real collective_thrust_slope = 4 * thrust_per_rotor_speed_delta;
  parameter Real roll_torque_slope = -4 * thrust_per_rotor_speed_delta * arm_y_m;
  parameter Real pitch_torque_slope = 4 * thrust_per_rotor_speed_delta * arm_x_m;
  parameter Real yaw_torque_slope = -4 * thrust_per_rotor_speed_delta * moment_ratio_m;
  Modelica.Blocks.Interfaces.RealInput body_force[3];
  Modelica.Blocks.Interfaces.RealInput body_torque[3];
  Modelica.Blocks.Interfaces.RealOutput rotor_command[4];
protected
  Real roll_term;
  Real pitch_term;
  Real yaw_term;
  Real collective_speed_delta;
  Real raw_rotor_command[4];
  annotation(__MWORKS(version="26.3.0"));
equation
  // The WRENCH contract is physical force/torque. Linearize the physical
  // rotor map about hover before applying the established signed X mixer.
  collective_speed_delta = (body_force[3] - hover_collective_thrust_n)
    / collective_thrust_slope;
  roll_term = body_torque[1] / roll_torque_slope;
  pitch_term = body_torque[2] / pitch_torque_slope;
  yaw_term = body_torque[3] / yaw_torque_slope;
  raw_rotor_command[1] = hover_speed + collective_speed_delta
    - yaw_term - pitch_term + roll_term;
  raw_rotor_command[2] = -hover_speed - collective_speed_delta
    - yaw_term + pitch_term + roll_term;
  raw_rotor_command[3] = hover_speed + collective_speed_delta
    - yaw_term + pitch_term - roll_term;
  raw_rotor_command[4] = -hover_speed - collective_speed_delta
    - yaw_term - pitch_term - roll_term;
  rotor_command[1] = min(max(raw_rotor_command[1], 0), maximum_speed);
  rotor_command[2] = min(max(raw_rotor_command[2], -maximum_speed), 0);
  rotor_command[3] = min(max(raw_rotor_command[3], 0), maximum_speed);
  rotor_command[4] = min(max(raw_rotor_command[4], -maximum_speed), 0);
end OfflineWrenchAllocator;
