within MoSimQuadrotorModel.Control.Adapters;
model NmpcOuterAttitudeThrustAdapter
  "External-input graphical NMPC outer law adapted to ATTITUDE_THRUST"

  extends MoSimQuadrotorModel.Control.Interfaces.PartialAttitudeThrustController;

  parameter MoSimQuadrotorModel.Parameters.Sunray150VirtualPx4Classic profile;
  parameter Real sample_time_s = 0.01;
  parameter Real collective_thrust_slope =
    8 * profile.mworks_visual_thrust_coefficient * profile.mworks_hover_visual_rotor_speed_rad_s;
  parameter Real max_collective_thrust_delta_n = 30.0 * collective_thrust_slope;

  MoSimQuadrotorModel.Control.Bridges.NmpcOuterEquationBridge core(
    sample_time_s = sample_time_s);
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
  core.enable = 1;

  // The bridge is ENU/FLU; the shared allocator receives its roll command with this established sign conversion.
  attitude_ref[1] = -core.desired_roll_rad_out;
  attitude_ref[2] = core.desired_pitch_rad_out;
  attitude_ref[3] = 0;
  // The shared allocator owns hover thrust, so this remains a gravity-excluded delta.
  collective_thrust_delta = min(max(profile.takeoff_mass_kg * core.desired_acceleration_z_out,
    -max_collective_thrust_delta_n), max_collective_thrust_delta_n);

  annotation(__MWORKS(version = "26.3.0"));
end NmpcOuterAttitudeThrustAdapter;
