within MoSimQuadrotorModel.Control.Bridges;
model LqiEquationBridge
  "Equation bridge copied from the readable LQI graphical outer-loop core"

  parameter Real sample_time_s = 0.01;
  parameter Real position_gain_x = 1.6;
  parameter Real position_gain_y = 1.6;
  parameter Real position_gain_z = 2.2;
  parameter Real velocity_gain_x = 1.8;
  parameter Real velocity_gain_y = 1.8;
  parameter Real velocity_gain_z = 2.0;
  parameter Real integral_gain_x = 0.2;
  parameter Real integral_gain_y = 0.2;
  parameter Real integral_gain_z = 0.3;
  parameter Real integral_limit_xy = 0.5;
  parameter Real integral_limit_z = 0.35;
  parameter Real gravity_mps2 = 9.80665;
  parameter Real roll_from_lateral_acceleration = -0.10197162129779283;
  parameter Real pitch_from_lateral_acceleration = 0.10197162129779283;
  parameter Real tilt_limit_rad = 0.5235987755982988;
  parameter Real normalized_thrust_scale = 0.03772949988018335;

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
  input Real enable;

  output Real desired_acceleration_x_out;
  output Real desired_acceleration_y_out;
  output Real desired_acceleration_z_out;
  output Real integral_position_error_x_out;
  output Real integral_position_error_y_out;
  output Real integral_position_error_z_out;
  output Real desired_roll_rad_out;
  output Real desired_pitch_rad_out;
  output Real normalized_thrust_out;

protected
  Modelica.Blocks.Discrete.UnitDelay integral_state_x(
    samplePeriod = sample_time_s,
    y_start = 0);
  Modelica.Blocks.Discrete.UnitDelay integral_state_y(
    samplePeriod = sample_time_s,
    y_start = 0);
  Modelica.Blocks.Discrete.UnitDelay integral_state_z(
    samplePeriod = sample_time_s,
    y_start = 0);
  Real position_error_x;
  Real position_error_y;
  Real position_error_z;
  Real velocity_error_x;
  Real velocity_error_y;
  Real velocity_error_z;
  Real integral_position_error_x;
  Real integral_position_error_y;
  Real integral_position_error_z;
  Real desired_acceleration_x;
  Real desired_acceleration_y;
  Real desired_acceleration_z;
  Boolean enabled;

equation
  position_error_x = reference_position_x - position_x;
  position_error_y = reference_position_y - position_y;
  position_error_z = reference_position_z - position_z;
  velocity_error_x = reference_velocity_x - velocity_x;
  velocity_error_y = reference_velocity_y - velocity_y;
  velocity_error_z = reference_velocity_z - velocity_z;

  integral_position_error_x = min(max(integral_state_x.y
    + sample_time_s * position_error_x, -integral_limit_xy), integral_limit_xy);
  integral_position_error_y = min(max(integral_state_y.y
    + sample_time_s * position_error_y, -integral_limit_xy), integral_limit_xy);
  integral_position_error_z = min(max(integral_state_z.y
    + sample_time_s * position_error_z, -integral_limit_z), integral_limit_z);
  integral_state_x.u = integral_position_error_x;
  integral_state_y.u = integral_position_error_y;
  integral_state_z.u = integral_position_error_z;

  desired_acceleration_x = reference_acceleration_x
    + position_gain_x * position_error_x + velocity_gain_x * velocity_error_x
    + integral_gain_x * integral_position_error_x;
  desired_acceleration_y = reference_acceleration_y
    + position_gain_y * position_error_y + velocity_gain_y * velocity_error_y
    + integral_gain_y * integral_position_error_y;
  desired_acceleration_z = reference_acceleration_z + gravity_mps2
    + position_gain_z * position_error_z + velocity_gain_z * velocity_error_z
    + integral_gain_z * integral_position_error_z;

  enabled = enable >= 0.5;
  desired_acceleration_x_out = if enabled then desired_acceleration_x else 0;
  desired_acceleration_y_out = if enabled then desired_acceleration_y else 0;
  desired_acceleration_z_out = if enabled then desired_acceleration_z else 0;
  integral_position_error_x_out = if enabled then integral_position_error_x else 0;
  integral_position_error_y_out = if enabled then integral_position_error_y else 0;
  integral_position_error_z_out = if enabled then integral_position_error_z else 0;
  desired_roll_rad_out = if enabled then min(max(
    roll_from_lateral_acceleration * desired_acceleration_y,
    -tilt_limit_rad), tilt_limit_rad) else 0;
  desired_pitch_rad_out = if enabled then min(max(
    pitch_from_lateral_acceleration * desired_acceleration_x,
    -tilt_limit_rad), tilt_limit_rad) else 0;
  normalized_thrust_out = if enabled then min(max(
    normalized_thrust_scale * desired_acceleration_z, 0.0), 1.0) else 0;

  annotation(__MWORKS(version = "26.3.0"));
end LqiEquationBridge;
