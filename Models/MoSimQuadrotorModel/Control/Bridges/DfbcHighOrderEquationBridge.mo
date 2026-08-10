within MoSimQuadrotorModel.Control.Bridges;
model DfbcHighOrderEquationBridge
  "Equation bridge for the selected graphical high-order DFBC attitude core"

  // These scalar laws, discrete surface memory, limits, and enable gates
  // mirror Controllers.GraphicalMIL.GeometricFlatness.
  // MoSim_G5_DFBC_HIGH_ORDER_ATTITUDE_DIRECT_GRAPHICAL_MIL.
  parameter Real sample_time_s = 0.01;
  parameter Real position_gain_x = 1.7;
  parameter Real position_gain_y = 1.7;
  parameter Real position_gain_z = 2.1;
  parameter Real velocity_gain_x = 1.2;
  parameter Real velocity_gain_y = 1.2;
  parameter Real velocity_gain_z = 1.55;
  parameter Real surface_rate_gain = 100.0;
  parameter Real high_order_rate_gain_x = 0.045;
  parameter Real high_order_rate_gain_y = 0.045;
  parameter Real high_order_rate_gain_z = 0.06;
  parameter Real acceleration_limit_xy = 4.0;
  parameter Real acceleration_limit_z = 3.0;
  parameter Real gravity_mps2 = 9.80665;
  parameter Real roll_from_lateral_acceleration = -0.10197162129779283;
  parameter Real pitch_from_lateral_acceleration = 0.10197162129779283;
  parameter Real tilt_limit_rad = 0.52;
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
  input Real body_rate_x "Retained for full graphical-core boundary compatibility";
  input Real body_rate_y "Retained for full graphical-core boundary compatibility";
  input Real body_rate_z "Retained for full graphical-core boundary compatibility";
  input Real dt "Retained for full graphical-core boundary compatibility";
  input Real enable;

  output Real position_error_x_out;
  output Real position_error_y_out;
  output Real position_error_z_out;
  output Real velocity_error_x_out;
  output Real velocity_error_y_out;
  output Real velocity_error_z_out;
  output Real sliding_surface_x_out;
  output Real sliding_surface_y_out;
  output Real sliding_surface_z_out;
  output Real surface_rate_x_out;
  output Real surface_rate_y_out;
  output Real surface_rate_z_out;
  output Real disturbance_estimate_x_out;
  output Real disturbance_estimate_y_out;
  output Real disturbance_estimate_z_out;
  output Real desired_acceleration_x_out;
  output Real desired_acceleration_y_out;
  output Real desired_acceleration_z_out;
  output Real desired_roll_rad_out;
  output Real desired_pitch_rad_out;
  output Real normalized_thrust_out;

protected
  Modelica.Blocks.Discrete.UnitDelay previous_surface_x(
    samplePeriod = sample_time_s,
    y_start = 0);
  Modelica.Blocks.Discrete.UnitDelay previous_surface_y(
    samplePeriod = sample_time_s,
    y_start = 0);
  Modelica.Blocks.Discrete.UnitDelay previous_surface_z(
    samplePeriod = sample_time_s,
    y_start = 0);
  Real position_error_x;
  Real position_error_y;
  Real position_error_z;
  Real velocity_error_x;
  Real velocity_error_y;
  Real velocity_error_z;
  Real sliding_surface_x;
  Real sliding_surface_y;
  Real sliding_surface_z;
  Real surface_rate_x;
  Real surface_rate_y;
  Real surface_rate_z;
  Real desired_acceleration_x;
  Real desired_acceleration_y;
  Real desired_acceleration_z;
  Real desired_roll_rad;
  Real desired_pitch_rad;
  Real normalized_thrust;
  Boolean enabled;

equation
  position_error_x = reference_position_x - position_x;
  position_error_y = reference_position_y - position_y;
  position_error_z = reference_position_z - position_z;
  velocity_error_x = reference_velocity_x - velocity_x;
  velocity_error_y = reference_velocity_y - velocity_y;
  velocity_error_z = reference_velocity_z - velocity_z;

  sliding_surface_x = position_gain_x * position_error_x
    + velocity_gain_x * velocity_error_x;
  sliding_surface_y = position_gain_y * position_error_y
    + velocity_gain_y * velocity_error_y;
  sliding_surface_z = position_gain_z * position_error_z
    + velocity_gain_z * velocity_error_z;
  previous_surface_x.u = sliding_surface_x;
  previous_surface_y.u = sliding_surface_y;
  previous_surface_z.u = sliding_surface_z;
  surface_rate_x = surface_rate_gain * (sliding_surface_x - previous_surface_x.y);
  surface_rate_y = surface_rate_gain * (sliding_surface_y - previous_surface_y.y);
  surface_rate_z = surface_rate_gain * (sliding_surface_z - previous_surface_z.y);

  desired_acceleration_x = min(max(
    reference_acceleration_x + sliding_surface_x + high_order_rate_gain_x * surface_rate_x,
    -acceleration_limit_xy), acceleration_limit_xy);
  desired_acceleration_y = min(max(
    reference_acceleration_y + sliding_surface_y + high_order_rate_gain_y * surface_rate_y,
    -acceleration_limit_xy), acceleration_limit_xy);
  desired_acceleration_z = min(max(
    reference_acceleration_z + sliding_surface_z + high_order_rate_gain_z * surface_rate_z,
    -acceleration_limit_z), acceleration_limit_z);

  desired_roll_rad = min(max(
    roll_from_lateral_acceleration * desired_acceleration_y,
    -tilt_limit_rad), tilt_limit_rad);
  desired_pitch_rad = min(max(
    pitch_from_lateral_acceleration * desired_acceleration_x,
    -tilt_limit_rad), tilt_limit_rad);
  normalized_thrust = min(max(
    normalized_thrust_scale * (desired_acceleration_z + gravity_mps2), 0.0), 1.0);

  enabled = enable >= 0.5;
  position_error_x_out = if enabled then position_error_x else 0;
  position_error_y_out = if enabled then position_error_y else 0;
  position_error_z_out = if enabled then position_error_z else 0;
  velocity_error_x_out = if enabled then velocity_error_x else 0;
  velocity_error_y_out = if enabled then velocity_error_y else 0;
  velocity_error_z_out = if enabled then velocity_error_z else 0;
  sliding_surface_x_out = if enabled then sliding_surface_x else 0;
  sliding_surface_y_out = if enabled then sliding_surface_y else 0;
  sliding_surface_z_out = if enabled then sliding_surface_z else 0;
  surface_rate_x_out = if enabled then surface_rate_x else 0;
  surface_rate_y_out = if enabled then surface_rate_y else 0;
  surface_rate_z_out = if enabled then surface_rate_z else 0;
  disturbance_estimate_x_out = 0;
  disturbance_estimate_y_out = 0;
  disturbance_estimate_z_out = 0;
  desired_acceleration_x_out = if enabled then desired_acceleration_x else 0;
  desired_acceleration_y_out = if enabled then desired_acceleration_y else 0;
  desired_acceleration_z_out = if enabled then desired_acceleration_z else 0;
  desired_roll_rad_out = if enabled then desired_roll_rad else 0;
  desired_pitch_rad_out = if enabled then desired_pitch_rad else 0;
  normalized_thrust_out = if enabled then normalized_thrust else 0;

  annotation(__MWORKS(version = "26.3.0"));
end DfbcHighOrderEquationBridge;