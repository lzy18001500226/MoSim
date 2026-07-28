within MoSimQuadrotorModel.Control.Adapters;
model DfbcSmoothRobustBodyRateAdapter
  "Smooth-robust DFBC graphical core adapted to BODY_RATE_THRUST"

  extends MoSimQuadrotorModel.Control.Interfaces.PartialBodyRateThrustController;

  parameter MoSimQuadrotorModel.Parameters.Sunray150VirtualPx4Classic profile;
  parameter Real sample_time_s = 0.01;
  parameter Real hover_speed = profile.mworks_hover_visual_rotor_speed_rad_s;
  parameter Real lift_coefficient = profile.mworks_visual_thrust_coefficient;
  parameter Real normalized_thrust_scale = 0.03772949988018335;
  parameter Real collective_thrust_slope = 8 * lift_coefficient * hover_speed;
  parameter Real max_collective_thrust_delta_n = 30 * collective_thrust_slope;

  MoSimQuadrotorModel.Control.Bridges.DfbcSmoothRobustBodyRateEquationBridge core(
    sample_time_s = sample_time_s);
  Real desired_collective_thrust_n;

equation
  core.position = position_mea;
  core.velocity = velocity_mea;
  core.reference_position = position_ref;
  core.reference_velocity = velocity_ref;
  core.reference_acceleration = acceleration_ref;
  core.enable = 1;
  // The direct graphical body-rate output is passed without an adapter-side
  // sign change; any convention defect is a G2/G3 route-level observation.
  body_rate_ref = core.desired_body_rate_out;
  desired_collective_thrust_n = core.normalized_thrust_out
    / normalized_thrust_scale;
  collective_thrust_delta = min(max(desired_collective_thrust_n
    - 4 * lift_coefficient * hover_speed ^ 2,
    -max_collective_thrust_delta_n), max_collective_thrust_delta_n);

  annotation(__MWORKS(version = "26.3.0"));
end DfbcSmoothRobustBodyRateAdapter;
