within MoSimQuadrotorModel.Control.Bridges;
model SmcBoundaryLayerEquationBridge
  "Equation bridge anchored to the externally-driven graphical SMC boundary-layer probe"

  parameter Real position_surface_gain = 2.0
    "Matches lambda_position in the graphical probe";
  parameter Real boundary_low_limit = -0.4
    "Matches boundary_layer.lowLimit in the graphical probe";
  parameter Real boundary_high_limit = 0.4
    "Matches boundary_layer.upLimit in the graphical probe";
  parameter Real switching_gain = 0.1
    "Matches switching_gain in the graphical probe";
  parameter Real acceleration_limit = 4.0
    "Matches acceleration_limit magnitude in the graphical probe";
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
  input Real reference_acceleration_x
    "External auxiliary input for the graphical probe";
  input Real reference_acceleration_y
    "External auxiliary input for the graphical probe";
  input Real reference_acceleration_z
    "External auxiliary input for the graphical probe";
  input Real enable;

  output Real desired_acceleration_x_out;
  output Real desired_acceleration_y_out;
  output Real desired_acceleration_z_out;
  output Real desired_roll_rad_out;
  output Real desired_pitch_rad_out;
  output Real sliding_surface_x_out;
  output Real sliding_surface_y_out;
  output Real sliding_surface_z_out;

protected
  Real position_error_x;
  Real position_error_y;
  Real position_error_z;
  Real velocity_error_x;
  Real velocity_error_y;
  Real velocity_error_z;
  Real sliding_surface_x;
  Real sliding_surface_y;
  Real sliding_surface_z;
  Real boundary_output_x;
  Real boundary_output_y;
  Real boundary_output_z;
  Real desired_acceleration_x;
  Real desired_acceleration_y;
  Real desired_acceleration_z;
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

  // This is the scalar graphical topology applied independently to x, y, and z.
  sliding_surface_x = position_surface_gain * position_error_x + velocity_error_x;
  sliding_surface_y = position_surface_gain * position_error_y + velocity_error_y;
  sliding_surface_z = position_surface_gain * position_error_z + velocity_error_z;
  boundary_output_x = min(max(sliding_surface_x, boundary_low_limit), boundary_high_limit);
  boundary_output_y = min(max(sliding_surface_y, boundary_low_limit), boundary_high_limit);
  boundary_output_z = min(max(sliding_surface_z, boundary_low_limit), boundary_high_limit);
  desired_acceleration_x = min(max(switching_gain * boundary_output_x + reference_acceleration_x, -acceleration_limit), acceleration_limit);
  desired_acceleration_y = min(max(switching_gain * boundary_output_y + reference_acceleration_y, -acceleration_limit), acceleration_limit);
  desired_acceleration_z = min(max(switching_gain * boundary_output_z + reference_acceleration_z, -acceleration_limit), acceleration_limit);
  desired_roll_rad = min(max(roll_from_lateral_acceleration * desired_acceleration_y, -tilt_limit_rad), tilt_limit_rad);
  desired_pitch_rad = min(max(pitch_from_lateral_acceleration * desired_acceleration_x, -tilt_limit_rad), tilt_limit_rad);
  enabled = enable >= 0.5;

  desired_acceleration_x_out = if enabled then desired_acceleration_x else 0;
  desired_acceleration_y_out = if enabled then desired_acceleration_y else 0;
  desired_acceleration_z_out = if enabled then desired_acceleration_z else 0;
  desired_roll_rad_out = if enabled then desired_roll_rad else 0;
  desired_pitch_rad_out = if enabled then desired_pitch_rad else 0;
  sliding_surface_x_out = if enabled then sliding_surface_x else 0;
  sliding_surface_y_out = if enabled then sliding_surface_y else 0;
  sliding_surface_z_out = if enabled then sliding_surface_z else 0;

  annotation(__MWORKS(version = "26.3.0"));
end SmcBoundaryLayerEquationBridge;
