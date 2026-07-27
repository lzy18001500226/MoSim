within MoSimQuadrotorModel.Control.Adapters;
model LqrBaselineAttitudeThrustAdapter
  "Selected graphical LQR law through an equation bridge at ATTITUDE_THRUST"

  extends MoSimQuadrotorModel.Control.Interfaces.PartialAttitudeThrustController;

  parameter MoSimQuadrotorModel.Parameters.Sunray150VirtualPx4Classic profile;
  parameter Real sample_time_s = 0.01;
  parameter Real hover_speed = profile.mworks_hover_visual_rotor_speed_rad_s;
  parameter Real lift_coefficient = profile.mworks_visual_thrust_coefficient;
  parameter Real collective_thrust_slope = 8 * lift_coefficient * hover_speed;
  parameter Real max_collective_thrust_delta_n = 30.0 * collective_thrust_slope;

  LqrBaselineEquationBridge core;

  Real collective_thrust_delta_n
    "The graphical LQR Z channel is a thrust increment about hover";

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
  core.reference_velocity_x = 0;
  core.reference_velocity_y = 0;
  core.reference_velocity_z = 0;
  core.reference_acceleration_x = 0;
  core.reference_acceleration_y = 0;
  core.reference_acceleration_z = 0;
  core.dt = sample_time_s;
  core.enable = 1;

  attitude_ref[1] = core.desired_roll_rad_out;
  attitude_ref[2] = core.desired_pitch_rad_out;
  attitude_ref[3] = 0;
  collective_thrust_delta_n = core.collective_thrust_n_out;
  collective_thrust_delta = min(max(collective_thrust_delta_n,
    -max_collective_thrust_delta_n), max_collective_thrust_delta_n);

  annotation(__MWORKS(version = "26.3.0"));
end LqrBaselineAttitudeThrustAdapter;
