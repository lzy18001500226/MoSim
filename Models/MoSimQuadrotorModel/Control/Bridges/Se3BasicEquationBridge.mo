within MoSimQuadrotorModel.Control.Bridges;
model Se3BasicEquationBridge
  "Vectorized equation bridge for the approved readable SE(3) graphical core"

  // MoSim_G9_SE3_GRAPHICAL_OVERVIEW contains the scalar path
  // 1.5 * position_error + 1.5 * velocity_error, followed by a 30 deg
  // tilt bound and a normalized-thrust bound. The bridge applies that same
  // scalar path independently on x/y/z so the fixed-input overview can use
  // the shared typed whole-aircraft boundary without modifying the diagram.
  parameter Real position_gain = 1.5;
  parameter Real velocity_gain = 1.5;
  parameter Real gravity_mps2 = 9.80665;
  parameter Real roll_from_lateral_acceleration = -0.10197162129779283;
  parameter Real pitch_from_lateral_acceleration = 0.10197162129779283;
  parameter Real tilt_limit_rad = 0.5236;
  parameter Real normalized_thrust_scale = 0.03772949988018335;

  input Real position[3];
  input Real velocity[3];
  input Real reference_position[3];
  input Real reference_velocity[3];
  input Real reference_acceleration[3];
  input Real enable;

  output Real position_error_out[3];
  output Real velocity_error_out[3];
  output Real desired_acceleration_out[3];
  output Real desired_roll_rad_out;
  output Real desired_pitch_rad_out;
  output Real normalized_thrust_out;

protected
  Real position_error[3];
  Real velocity_error[3];
  Real desired_acceleration[3];
  Real desired_roll_rad;
  Real desired_pitch_rad;
  Real normalized_thrust;
  Boolean enabled;

equation
  position_error = reference_position - position;
  velocity_error = reference_velocity - velocity;
  for axis in 1:3 loop
    desired_acceleration[axis] = reference_acceleration[axis]
      + position_gain * position_error[axis]
      + velocity_gain * velocity_error[axis];
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
  desired_roll_rad_out = if enabled then desired_roll_rad else 0;
  desired_pitch_rad_out = if enabled then desired_pitch_rad else 0;
  normalized_thrust_out = if enabled then normalized_thrust else 0;

  annotation(__MWORKS(version = "26.3.0"));
end Se3BasicEquationBridge;