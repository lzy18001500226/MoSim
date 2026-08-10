within MoSimQuadrotorModel.Control.Bridges;
model LqrBaselineEquationBridge
  "Equation bridge for the selected readable graphical LQR outer-loop core"

  // These scalar laws and limits mirror
  // Controllers.GraphicalMIL.ClassicRobust.MoSim_G5_LQR_DIRECT_GRAPHICAL_MIL.
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
  input Real dt "Retained for full graphical-core boundary compatibility";
  input Real enable;

  output Real position_error_x_out;
  output Real position_error_y_out;
  output Real position_error_z_out;
  output Real velocity_error_x_out;
  output Real velocity_error_y_out;
  output Real velocity_error_z_out;
  output Real desired_acceleration_x_out;
  output Real desired_acceleration_y_out;
  output Real desired_acceleration_z_out;
  output Real desired_roll_rad_out;
  output Real desired_pitch_rad_out;
  output Real normalized_thrust_out;
  output Real collective_thrust_n_out;

protected
  Real position_error_x;
  Real position_error_y;
  Real position_error_z;
  Real velocity_error_x;
  Real velocity_error_y;
  Real velocity_error_z;
  Real desired_acceleration_x;
  Real desired_acceleration_y;
  Real desired_acceleration_z;
  Real desired_roll_rad;
  Real desired_pitch_rad;
  Real normalized_thrust;
  Real collective_thrust_n;
  Boolean enabled;

equation
  position_error_x = reference_position_x - position_x;
  position_error_y = reference_position_y - position_y;
  position_error_z = reference_position_z - position_z;
  velocity_error_x = reference_velocity_x - velocity_x;
  velocity_error_y = reference_velocity_y - velocity_y;
  velocity_error_z = reference_velocity_z - velocity_z;

  desired_acceleration_x = reference_acceleration_x
    + position_gain_x * position_error_x + velocity_gain_x * velocity_error_x;
  desired_acceleration_y = reference_acceleration_y
    + position_gain_y * position_error_y + velocity_gain_y * velocity_error_y;
  desired_acceleration_z = reference_acceleration_z + gravity_mps2
    + position_gain_z * position_error_z + velocity_gain_z * velocity_error_z;

  desired_roll_rad = min(max(
    roll_from_lateral_acceleration * desired_acceleration_y,
    -tilt_limit_rad), tilt_limit_rad);
  desired_pitch_rad = min(max(
    pitch_from_lateral_acceleration * desired_acceleration_x,
    -tilt_limit_rad), tilt_limit_rad);
  normalized_thrust = min(max(
    normalized_thrust_scale * desired_acceleration_z, 0.0), 1.0);
  collective_thrust_n = collective_thrust_from_normalized * normalized_thrust;

  enabled = enable >= 0.5;
  position_error_x_out = if enabled then position_error_x else 0;
  position_error_y_out = if enabled then position_error_y else 0;
  position_error_z_out = if enabled then position_error_z else 0;
  velocity_error_x_out = if enabled then velocity_error_x else 0;
  velocity_error_y_out = if enabled then velocity_error_y else 0;
  velocity_error_z_out = if enabled then velocity_error_z else 0;
  desired_acceleration_x_out = if enabled then desired_acceleration_x else 0;
  desired_acceleration_y_out = if enabled then desired_acceleration_y else 0;
  desired_acceleration_z_out = if enabled then desired_acceleration_z else 0;
  desired_roll_rad_out = if enabled then desired_roll_rad else 0;
  desired_pitch_rad_out = if enabled then desired_pitch_rad else 0;
  normalized_thrust_out = if enabled then normalized_thrust else 0;
  collective_thrust_n_out = if enabled then collective_thrust_n else 0;

  annotation(__MWORKS(version = "26.3.0"));
end LqrBaselineEquationBridge;