within MoSimQuadrotorModel.Control.Bridges;
model DfbcBasicEquationBridge
  "Vectorized equation bridge for the approved readable DFBC graphical core"

  // MoSim_G9_DFBC_GRAPHICAL_OVERVIEW adds a delayed 0.02 auxiliary path,
  // scaled by -0.4, to the same 1.5/1.5 nominal force path before the
  // +/-4 acceleration limit. This preserves that graph's causal structure.
  parameter Real sample_time_s = 0.01;
  parameter Real position_gain = 1.5;
  parameter Real velocity_gain = 1.5;
  parameter Real auxiliary_source = 0.02;
  parameter Real disturbance_compensation_gain = -0.4;
  parameter Real acceleration_limit = 4.0;
  parameter Real gravity_mps2 = 9.80665;
  parameter Real roll_from_lateral_acceleration = -0.10197162129779283;
  parameter Real pitch_from_lateral_acceleration = 0.10197162129779283;
  parameter Real tilt_limit_rad = 0.5235987755982988;
  parameter Real normalized_thrust_scale = 0.03772949988018335;

  input Real position[3];
  input Real velocity[3];
  input Real reference_position[3];
  input Real reference_velocity[3];
  input Real reference_acceleration[3];
  input Real enable;

  output Real position_error_out[3];
  output Real velocity_error_out[3];
  output Real disturbance_compensation_out;
  output Real desired_acceleration_out[3];
  output Real desired_roll_rad_out;
  output Real desired_pitch_rad_out;
  output Real normalized_thrust_out;

protected
  Modelica.Blocks.Discrete.UnitDelay disturbance_state(
    samplePeriod = sample_time_s,
    y_start = 0);
  Real position_error[3];
  Real velocity_error[3];
  Real disturbance_compensation;
  Real desired_acceleration[3];
  Real desired_roll_rad;
  Real desired_pitch_rad;
  Real normalized_thrust;
  Boolean enabled;

equation
  position_error = reference_position - position;
  velocity_error = reference_velocity - velocity;
  disturbance_state.u = auxiliary_source;
  disturbance_compensation = disturbance_compensation_gain * disturbance_state.y;
  for axis in 1:3 loop
    desired_acceleration[axis] = min(max(reference_acceleration[axis]
      + position_gain * position_error[axis] + velocity_gain * velocity_error[axis]
      + disturbance_compensation, -acceleration_limit), acceleration_limit);
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
    desired_acceleration_out[axis] = if enabled then desired_acceleration[axis] else 0;
  end for;
  disturbance_compensation_out = if enabled then disturbance_compensation else 0;
  desired_roll_rad_out = if enabled then desired_roll_rad else 0;
  desired_pitch_rad_out = if enabled then desired_pitch_rad else 0;
  normalized_thrust_out = if enabled then normalized_thrust else 0;

  annotation(__MWORKS(version = "26.3.0"));
end DfbcBasicEquationBridge;