within MoSimQuadrotorModel.Control.Adapters;
model DfbcHighOrderBodyRateAdapter
  "High-order DFBC graphical core adapted to BODY_RATE_THRUST"

  extends MoSimQuadrotorModel.Control.Interfaces.PartialBodyRateThrustController;

  parameter MoSimQuadrotorModel.Parameters.Sunray150VirtualPx4Classic profile;
  parameter Real sample_time_s = 0.01;
  parameter Real hover_speed = profile.mworks_hover_visual_rotor_speed_rad_s;
  parameter Real lift_coefficient = profile.mworks_visual_thrust_coefficient;
  parameter Real normalized_thrust_scale = 0.03772949988018335;
  parameter Real collective_thrust_slope = 8 * lift_coefficient * hover_speed;
  parameter Real max_collective_thrust_delta_n = 30 * collective_thrust_slope;
  parameter Real attitude_to_rate_gain = 4
    "Shared BODY_RATE_THRUST attitude-error-to-rate projection";
  parameter Real max_body_rate_rad_s = 1.5
    "Shared BODY_RATE_THRUST rate limit";

  MoSimQuadrotorModel.Control.Bridges.DfbcHighOrderBodyRateEquationBridge core(
    sample_time_s = sample_time_s);
  Real desired_collective_thrust_n;

equation
  core.position_x = position_mea[1];
  core.position_y = position_mea[2];
  core.position_z = position_mea[3];
  core.velocity_x = velocity_mea[1];
  core.velocity_y = velocity_mea[2];
  core.velocity_z = velocity_mea[3];
  core.reference_position_x = position_ref[1];
  core.reference_position_y = position_ref[2];
  core.reference_position_z = position_ref[3];
  core.reference_velocity_x = velocity_ref[1];
  core.reference_velocity_y = velocity_ref[2];
  core.reference_velocity_z = velocity_ref[3];
  core.reference_acceleration_x = acceleration_ref[1];
  core.reference_acceleration_y = acceleration_ref[2];
  core.reference_acceleration_z = acceleration_ref[3];
  // The selected high-order graphical body-rate core declares body-rate ports
  // but does not consume them in its equations. Bind them deterministically
  // instead of adding a second adapter-owned derivative estimator.
  core.body_rate_x = 0;
  core.body_rate_y = 0;
  core.body_rate_z = 0;
  core.dt = sample_time_s;
  core.enable = 1;
  // The graphical body's direct acceleration-to-rate outputs have no attitude
  // feedback. Convert its checked acceleration-to-attitude result through the
  // shared BODY_RATE_THRUST boundary so a persistent position error commands
  // a bounded target attitude rather than an unbounded rotation.
  body_rate_ref[1] = min(max(attitude_to_rate_gain * (
    core.desired_roll_rad_out - attitude_mea[1]),
    -max_body_rate_rad_s), max_body_rate_rad_s);
  body_rate_ref[2] = min(max(attitude_to_rate_gain * (
    core.desired_pitch_rad_out - attitude_mea[2]),
    -max_body_rate_rad_s), max_body_rate_rad_s);
  body_rate_ref[3] = min(max(-attitude_to_rate_gain * attitude_mea[3],
    -max_body_rate_rad_s), max_body_rate_rad_s);
  desired_collective_thrust_n = core.normalized_thrust_out
    / normalized_thrust_scale;
  collective_thrust_delta = min(max(desired_collective_thrust_n
    - 4 * lift_coefficient * hover_speed ^ 2,
    -max_collective_thrust_delta_n), max_collective_thrust_delta_n);

  annotation(__MWORKS(version = "26.3.0"));
end DfbcHighOrderBodyRateAdapter;
