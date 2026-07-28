within MoSimQuadrotorModel.Control.Adapters;
model IlqrAttitudeThrustAdapter
  "Five-iteration iLQR graphical core adapted to ATTITUDE_THRUST"

  extends MoSimQuadrotorModel.Control.Interfaces.PartialAttitudeThrustController;

  parameter MoSimQuadrotorModel.Parameters.Sunray150VirtualPx4Classic profile;
  parameter Real sample_time_s = 0.01;
  parameter Real hover_speed = profile.mworks_hover_visual_rotor_speed_rad_s;
  parameter Real lift_coefficient = profile.mworks_visual_thrust_coefficient;
  parameter Real normalized_thrust_scale = 0.03772949988018335;
  parameter Real collective_thrust_slope = 8 * lift_coefficient * hover_speed;
  parameter Real max_collective_thrust_delta_n = 30 * collective_thrust_slope;

  MoSimQuadrotorModel.Control.Bridges.IlqrEquationBridge core(
    sample_time_s = sample_time_s);
  Real desired_collective_thrust_n;

equation
  core.position = position_mea;
  core.velocity = velocity_mea;
  core.reference_position = position_ref;
  core.reference_velocity = velocity_ref;
  core.reference_acceleration = acceleration_ref;
  core.enable = 1;
  attitude_ref[1] = -core.desired_roll_rad_out;
  attitude_ref[2] = core.desired_pitch_rad_out;
  attitude_ref[3] = 0;
  desired_collective_thrust_n = core.normalized_thrust_out
    / normalized_thrust_scale;
  collective_thrust_delta = min(max(desired_collective_thrust_n
    - 4 * lift_coefficient * hover_speed ^ 2,
    -max_collective_thrust_delta_n), max_collective_thrust_delta_n);

  annotation(__MWORKS(version = "26.3.0"));
end IlqrAttitudeThrustAdapter;
