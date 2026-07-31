within MoSimQuadrotorModel.Control.Bridges;
model NmpcOuterEquationBridge
  "Equation bridge anchored to the externally-driven graphical NMPC outer probe"

  parameter Real position_prediction_gain = 0.25
    "Matches position_prediction in the graphical probe";
  parameter Real velocity_prediction_gain = 0.25
    "Matches velocity_prediction in the graphical probe";
  parameter Real quadratic_optimizer_gain = 3.2
    "Matches quadratic_optimizer in the graphical probe";
  parameter Real increment_low_limit = -1.2
    "Matches increment_limit.lowLimit in the graphical probe";
  parameter Real increment_high_limit = 1.2
    "Matches increment_limit.upLimit in the graphical probe";
  parameter Real acceleration_limit = 4.0
    "Matches acceleration_limit magnitude in the graphical probe";
  parameter Real sample_time_s = 0.01
    "Matches the graphical probe sample interval";
  parameter Real roll_from_lateral_acceleration = -0.10197162129779283;
  parameter Real pitch_from_lateral_acceleration = 0.10197162129779283;
  parameter Real tilt_limit_rad = 0.5235987755982988;

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
  input Real enable;

  output Real desired_acceleration_x_out;
  output Real desired_acceleration_y_out;
  output Real desired_acceleration_z_out;
  output Real desired_roll_rad_out;
  output Real desired_pitch_rad_out;
  output Real horizon_state_x_out;
  output Real horizon_state_y_out;
  output Real horizon_state_z_out;

protected
  Modelica.Blocks.Discrete.UnitDelay previous_command_x(
    samplePeriod = sample_time_s,
    y_start = 0);
  Modelica.Blocks.Discrete.UnitDelay previous_command_y(
    samplePeriod = sample_time_s,
    y_start = 0);
  Modelica.Blocks.Discrete.UnitDelay previous_command_z(
    samplePeriod = sample_time_s,
    y_start = 0);
  Real position_error_x;
  Real position_error_y;
  Real position_error_z;
  Real velocity_error_x;
  Real velocity_error_y;
  Real velocity_error_z;
  Real horizon_state_x;
  Real horizon_state_y;
  Real horizon_state_z;
  Real raw_command_x;
  Real raw_command_y;
  Real raw_command_z;
  Real limited_increment_x;
  Real limited_increment_y;
  Real limited_increment_z;
  Real desired_roll_rad;
  Real desired_pitch_rad;
  Boolean enabled;

equation
  position_error_x = reference_position_x - position_x;
  position_error_y = reference_position_y - position_y;
  position_error_z = reference_position_z - position_z;
  velocity_error_x = reference_velocity_x - velocity_x;
  velocity_error_y = reference_velocity_y - velocity_y;
  velocity_error_z = reference_velocity_z - velocity_z;
  horizon_state_x = position_prediction_gain * position_error_x + velocity_prediction_gain * velocity_error_x;
  horizon_state_y = position_prediction_gain * position_error_y + velocity_prediction_gain * velocity_error_y;
  horizon_state_z = position_prediction_gain * position_error_z + velocity_prediction_gain * velocity_error_z;
  raw_command_x = quadratic_optimizer_gain * horizon_state_x;
  raw_command_y = quadratic_optimizer_gain * horizon_state_y;
  raw_command_z = quadratic_optimizer_gain * horizon_state_z;
  limited_increment_x = min(max(raw_command_x - previous_command_x.y, increment_low_limit), increment_high_limit);
  limited_increment_y = min(max(raw_command_y - previous_command_y.y, increment_low_limit), increment_high_limit);
  limited_increment_z = min(max(raw_command_z - previous_command_z.y, increment_low_limit), increment_high_limit);
  previous_command_x.u = limited_increment_x;
  previous_command_y.u = limited_increment_y;
  previous_command_z.u = limited_increment_z;
  desired_roll_rad = min(max(roll_from_lateral_acceleration * min(max(limited_increment_y, -acceleration_limit), acceleration_limit), -tilt_limit_rad), tilt_limit_rad);
  desired_pitch_rad = min(max(pitch_from_lateral_acceleration * min(max(limited_increment_x, -acceleration_limit), acceleration_limit), -tilt_limit_rad), tilt_limit_rad);
  enabled = enable >= 0.5;

  desired_acceleration_x_out = if enabled then min(max(limited_increment_x, -acceleration_limit), acceleration_limit) else 0;
  desired_acceleration_y_out = if enabled then min(max(limited_increment_y, -acceleration_limit), acceleration_limit) else 0;
  desired_acceleration_z_out = if enabled then min(max(limited_increment_z, -acceleration_limit), acceleration_limit) else 0;
  desired_roll_rad_out = if enabled then desired_roll_rad else 0;
  desired_pitch_rad_out = if enabled then desired_pitch_rad else 0;
  horizon_state_x_out = if enabled then horizon_state_x else 0;
  horizon_state_y_out = if enabled then horizon_state_y else 0;
  horizon_state_z_out = if enabled then horizon_state_z else 0;

  annotation(__MWORKS(version = "26.3.0"));
end NmpcOuterEquationBridge;
