within MoSimQuadrotorModel.Control.Bridges;
model DfbcSmoothRobustAttitudeEquationBridge
  "Equation bridge copied from the direct graphical smooth-robust DFBC core"

  // This mirrors MoSim_G5_DFBC_SMOOTH_ROBUST_ATTITUDE_DIRECT_GRAPHICAL_MIL:
  // a P/D sliding surface, tanh boundary layer, delayed disturbance observer,
  // acceleration saturation, and acceleration-to-attitude/thrust projection.
  parameter Real sample_time_s = 0.01;
  parameter Real position_gain[3] = {1.7, 1.7, 2.1};
  parameter Real velocity_gain[3] = {1.2, 1.2, 1.55};
  parameter Real surface_rate_gain = 100.0;
  parameter Real smooth_boundary_normalization[3] = {
    2.2222222222222223, 2.2222222222222223, 2.857142857142857};
  parameter Real smooth_robust_gain[3] = {-0.75, -0.75, -0.95};
  parameter Real disturbance_observer_gain[3] = {0.18, 0.18, 0.14};
  parameter Real disturbance_compensation_limit[3] = {1.0, 1.0, 0.8};
  parameter Real acceleration_limit[3] = {4.0, 4.0, 3.0};
  parameter Real gravity_mps2 = 9.80665;
  parameter Real roll_from_lateral_acceleration = -0.10197162129779283;
  parameter Real pitch_from_lateral_acceleration = 0.10197162129779283;
  parameter Real tilt_limit_rad = 0.52;
  parameter Real normalized_thrust_scale = 0.03772949988018335;

  input Real position[3];
  input Real velocity[3];
  input Real reference_position[3];
  input Real reference_velocity[3];
  input Real reference_acceleration[3];
  input Real enable;

  output Real position_error_out[3];
  output Real velocity_error_out[3];
  output Real sliding_surface_out[3];
  output Real surface_rate_out[3];
  output Real disturbance_estimate_out[3];
  output Real desired_acceleration_out[3];
  output Real desired_roll_rad_out;
  output Real desired_pitch_rad_out;
  output Real normalized_thrust_out;

protected
  Modelica.Blocks.Discrete.UnitDelay previous_surface[3](
    each samplePeriod = sample_time_s,
    each y_start = 0);
  Modelica.Blocks.Discrete.UnitDelay disturbance_state[3](
    each samplePeriod = sample_time_s,
    each y_start = 0);
  Real position_error[3];
  Real velocity_error[3];
  Real sliding_surface[3];
  Real surface_rate[3];
  Real smooth_feedback[3];
  Real disturbance_innovation[3];
  Real disturbance_next[3];
  Real desired_acceleration[3];
  Real desired_roll_rad;
  Real desired_pitch_rad;
  Real normalized_thrust;
  Boolean enabled;

equation
  position_error = reference_position - position;
  velocity_error = reference_velocity - velocity;
  for axis in 1:3 loop
    sliding_surface[axis] = position_gain[axis] * position_error[axis]
      + velocity_gain[axis] * velocity_error[axis];
    previous_surface[axis].u = sliding_surface[axis];
    surface_rate[axis] = surface_rate_gain * (sliding_surface[axis]
      - previous_surface[axis].y);
    smooth_feedback[axis] = smooth_robust_gain[axis] * Modelica.Math.tanh(
      smooth_boundary_normalization[axis] * sliding_surface[axis]);
    disturbance_innovation[axis] = sliding_surface[axis]
      - disturbance_state[axis].y;
    disturbance_next[axis] = min(max(disturbance_state[axis].y
      + disturbance_observer_gain[axis] * disturbance_innovation[axis],
      -disturbance_compensation_limit[axis]),
      disturbance_compensation_limit[axis]);
    disturbance_state[axis].u = disturbance_next[axis];
    desired_acceleration[axis] = min(max(reference_acceleration[axis]
      + sliding_surface[axis] + smooth_feedback[axis]
      - disturbance_state[axis].y, -acceleration_limit[axis]),
      acceleration_limit[axis]);
  end for;

  desired_roll_rad = min(max(roll_from_lateral_acceleration
    * desired_acceleration[2], -tilt_limit_rad), tilt_limit_rad);
  desired_pitch_rad = min(max(pitch_from_lateral_acceleration
    * desired_acceleration[1], -tilt_limit_rad), tilt_limit_rad);
  normalized_thrust = min(max(normalized_thrust_scale
    * (desired_acceleration[3] + gravity_mps2), 0), 1);

  enabled = enable >= 0.5;
  for axis in 1:3 loop
    position_error_out[axis] = if enabled then position_error[axis] else 0;
    velocity_error_out[axis] = if enabled then velocity_error[axis] else 0;
    sliding_surface_out[axis] = if enabled then sliding_surface[axis] else 0;
    surface_rate_out[axis] = if enabled then surface_rate[axis] else 0;
    disturbance_estimate_out[axis] = if enabled then disturbance_state[axis].y else 0;
    desired_acceleration_out[axis] = if enabled then desired_acceleration[axis] else 0;
  end for;
  desired_roll_rad_out = if enabled then desired_roll_rad else 0;
  desired_pitch_rad_out = if enabled then desired_pitch_rad else 0;
  normalized_thrust_out = if enabled then normalized_thrust else 0;

  annotation(__MWORKS(version = "26.3.0"));
end DfbcSmoothRobustAttitudeEquationBridge;
