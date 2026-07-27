within MoSimQuadrotorModel.Control.Bridges;
model LqgEquationBridge
  "Equation bridge copied from the readable LQG observer/controller core"

  parameter Real sample_time_s = 0.01;
  parameter Real position_correction_xy = 0.65;
  parameter Real position_correction_z = 0.7;
  parameter Real velocity_correction_xy = 0.45;
  parameter Real velocity_correction_z = 0.5;
  parameter Real position_gain_x = 1.6;
  parameter Real position_gain_y = 1.6;
  parameter Real position_gain_z = 2.2;
  parameter Real velocity_gain_x = 1.8;
  parameter Real velocity_gain_y = 1.8;
  parameter Real velocity_gain_z = 2.0;
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
  output Real estimated_position_x_out;
  output Real estimated_position_y_out;
  output Real estimated_position_z_out;
  output Real estimated_velocity_x_out;
  output Real estimated_velocity_y_out;
  output Real estimated_velocity_z_out;
  output Real desired_roll_rad_out;
  output Real desired_pitch_rad_out;
  output Real normalized_thrust_out;

protected
  Modelica.Blocks.Discrete.UnitDelay estimated_position_x(
    samplePeriod = sample_time_s, y_start = 0);
  Modelica.Blocks.Discrete.UnitDelay estimated_position_y(
    samplePeriod = sample_time_s, y_start = 0);
  Modelica.Blocks.Discrete.UnitDelay estimated_position_z(
    samplePeriod = sample_time_s, y_start = 0);
  Modelica.Blocks.Discrete.UnitDelay estimated_velocity_x(
    samplePeriod = sample_time_s, y_start = 0);
  Modelica.Blocks.Discrete.UnitDelay estimated_velocity_y(
    samplePeriod = sample_time_s, y_start = 0);
  Modelica.Blocks.Discrete.UnitDelay estimated_velocity_z(
    samplePeriod = sample_time_s, y_start = 0);
  Real predicted_position_x;
  Real predicted_position_y;
  Real predicted_position_z;
  Real predicted_velocity_x;
  Real predicted_velocity_y;
  Real predicted_velocity_z;
  Real desired_acceleration_x;
  Real desired_acceleration_y;
  Real desired_acceleration_z;
  Boolean enabled;

equation
  predicted_position_x = estimated_position_x.y
    + sample_time_s * estimated_velocity_x.y;
  predicted_position_y = estimated_position_y.y
    + sample_time_s * estimated_velocity_y.y;
  predicted_position_z = estimated_position_z.y
    + sample_time_s * estimated_velocity_z.y;
  estimated_position_x.u = predicted_position_x
    + position_correction_xy * (position_x - predicted_position_x);
  estimated_position_y.u = predicted_position_y
    + position_correction_xy * (position_y - predicted_position_y);
  estimated_position_z.u = predicted_position_z
    + position_correction_z * (position_z - predicted_position_z);

  desired_acceleration_x = reference_acceleration_x
    + position_gain_x * (reference_position_x - estimated_position_x.y)
    + velocity_gain_x * (reference_velocity_x - estimated_velocity_x.y);
  desired_acceleration_y = reference_acceleration_y
    + position_gain_y * (reference_position_y - estimated_position_y.y)
    + velocity_gain_y * (reference_velocity_y - estimated_velocity_y.y);
  desired_acceleration_z = reference_acceleration_z + gravity_mps2
    + position_gain_z * (reference_position_z - estimated_position_z.y)
    + velocity_gain_z * (reference_velocity_z - estimated_velocity_z.y);

  predicted_velocity_x = estimated_velocity_x.y
    + sample_time_s * desired_acceleration_x;
  predicted_velocity_y = estimated_velocity_y.y
    + sample_time_s * desired_acceleration_y;
  predicted_velocity_z = estimated_velocity_z.y
    + sample_time_s * (desired_acceleration_z - gravity_mps2);
  estimated_velocity_x.u = predicted_velocity_x
    + velocity_correction_xy * (velocity_x - predicted_velocity_x);
  estimated_velocity_y.u = predicted_velocity_y
    + velocity_correction_xy * (velocity_y - predicted_velocity_y);
  estimated_velocity_z.u = predicted_velocity_z
    + velocity_correction_z * (velocity_z - predicted_velocity_z);

  enabled = enable >= 0.5;
  desired_acceleration_x_out = if enabled then desired_acceleration_x else 0;
  desired_acceleration_y_out = if enabled then desired_acceleration_y else 0;
  desired_acceleration_z_out = if enabled then desired_acceleration_z else 0;
  estimated_position_x_out = if enabled then estimated_position_x.y else 0;
  estimated_position_y_out = if enabled then estimated_position_y.y else 0;
  estimated_position_z_out = if enabled then estimated_position_z.y else 0;
  estimated_velocity_x_out = if enabled then estimated_velocity_x.y else 0;
  estimated_velocity_y_out = if enabled then estimated_velocity_y.y else 0;
  estimated_velocity_z_out = if enabled then estimated_velocity_z.y else 0;
  desired_roll_rad_out = if enabled then min(max(
    roll_from_lateral_acceleration * desired_acceleration_y,
    -tilt_limit_rad), tilt_limit_rad) else 0;
  desired_pitch_rad_out = if enabled then min(max(
    pitch_from_lateral_acceleration * desired_acceleration_x,
    -tilt_limit_rad), tilt_limit_rad) else 0;
  normalized_thrust_out = if enabled then min(max(
    normalized_thrust_scale * desired_acceleration_z, 0.0), 1.0) else 0;

  annotation(__MWORKS(version = "26.3.0"));
end LqgEquationBridge;
