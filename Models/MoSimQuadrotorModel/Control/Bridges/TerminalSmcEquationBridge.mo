within MoSimQuadrotorModel.Control.Bridges;
model TerminalSmcEquationBridge
  "Equation bridge for the graphical terminal sliding-mode outer-loop law"

  parameter Real position_power_exponent[3] = {0.72, 0.72, 0.78};
  parameter Real terminal_shape_gain[3] = {1.2, 1.2, 1.4};
  parameter Real velocity_reaching_gain[3] = {1.2, 1.2, 1.4};
  parameter Real surface_feedback_gain[3] = {0.8, 0.8, 1.0};
  parameter Real reaching_gain[3] = {2.2, 2.2, 2.8};
  parameter Real boundary_normalization[3] = {8.333333333333334, 8.333333333333334, 6.666666666666667};
  parameter Real gravity_mps2 = 9.80665;
  parameter Real roll_from_lateral_acceleration = -0.10197162129779283;
  parameter Real pitch_from_lateral_acceleration = 0.10197162129779283;
  parameter Real tilt_limit_rad = 0.5235987755982988;
  parameter Real normalized_thrust_scale = 0.03772949988018335;
  parameter Real collective_thrust_from_normalized = 17.745945945945948;

  input Real position_x;
  input Real position_y;
  input Real position_z;
  input Real velocity_x;
  input Real velocity_y;
  input Real velocity_z;
  input Real reference_position_x;
  input Real reference_position_y;
  input Real reference_position_z;
  input Real reference_velocity_x;
  input Real reference_velocity_y;
  input Real reference_velocity_z;
  input Real reference_acceleration_x;
  input Real reference_acceleration_y;
  input Real reference_acceleration_z;
  input Real dt "Retained for the graphical-core boundary";
  input Real enable;

  output Real desired_acceleration_x_out;
  output Real desired_acceleration_y_out;
  output Real desired_acceleration_z_out;
  output Real desired_roll_rad_out;
  output Real desired_pitch_rad_out;
  output Real normalized_thrust_out;
  output Real collective_thrust_n_out;

protected
  Real position_error[3];
  Real velocity_error[3];
  Real reference_acceleration[3];
  Real sliding_surface[3];
  Real desired_acceleration[3];
  Real desired_roll_rad;
  Real desired_pitch_rad;
  Real normalized_thrust;
  Real collective_thrust_n;
  Boolean enabled;

equation
  position_error = {reference_position_x - position_x, reference_position_y - position_y, reference_position_z - position_z};
  velocity_error = {reference_velocity_x - velocity_x, reference_velocity_y - velocity_y, reference_velocity_z - velocity_z};
  reference_acceleration = {reference_acceleration_x, reference_acceleration_y, reference_acceleration_z};
  for axis in 1:3 loop
    sliding_surface[axis] = velocity_error[axis] + terminal_shape_gain[axis] * sign(position_error[axis]) * abs(position_error[axis]) ^ position_power_exponent[axis];
    desired_acceleration[axis] = reference_acceleration[axis] + velocity_reaching_gain[axis] * velocity_error[axis] + surface_feedback_gain[axis] * sliding_surface[axis] + reaching_gain[axis] * min(max(boundary_normalization[axis] * sliding_surface[axis], -1.0), 1.0) + (if axis == 3 then gravity_mps2 else 0);
  end for;
  desired_roll_rad = min(max(roll_from_lateral_acceleration * desired_acceleration[2], -tilt_limit_rad), tilt_limit_rad);
  desired_pitch_rad = min(max(pitch_from_lateral_acceleration * desired_acceleration[1], -tilt_limit_rad), tilt_limit_rad);
  normalized_thrust = min(max(normalized_thrust_scale * desired_acceleration[3], 0.0), 1.0);
  collective_thrust_n = collective_thrust_from_normalized * normalized_thrust;
  enabled = enable >= 0.5;
  desired_acceleration_x_out = if enabled then desired_acceleration[1] else 0;
  desired_acceleration_y_out = if enabled then desired_acceleration[2] else 0;
  desired_acceleration_z_out = if enabled then desired_acceleration[3] else 0;
  desired_roll_rad_out = if enabled then desired_roll_rad else 0;
  desired_pitch_rad_out = if enabled then desired_pitch_rad else 0;
  normalized_thrust_out = if enabled then normalized_thrust else 0;
  collective_thrust_n_out = if enabled then collective_thrust_n else 0;

  annotation(__MWORKS(version = "26.3.0"));
end TerminalSmcEquationBridge;
