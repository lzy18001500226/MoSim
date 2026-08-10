within MoSimQuadrotorModel.Control.Adapters;
model LqrBaselineAttitudeThrustAdapter
  "Selected graphical LQR law through an equation bridge at ATTITUDE_THRUST"

  extends MoSimQuadrotorModel.Control.Interfaces.PartialAttitudeThrustController;

  parameter MoSimQuadrotorModel.Parameters.Sunray150VirtualPx4Classic profile;
  parameter Real sample_time_s = 0.01;
  parameter Real mass_kg = profile.takeoff_mass_kg;
  parameter Real gravity_mps2 = profile.gravity_mps2;
  parameter Real hover_speed = profile.mworks_hover_visual_rotor_speed_rad_s;
  parameter Real lift_coefficient = profile.mworks_visual_thrust_coefficient;
  parameter Real collective_thrust_slope = 8 * lift_coefficient * hover_speed;
  parameter Real hover_normalized_command = profile.mworks_controller_hover_percentage;
  parameter Real normalized_to_physical_collective_thrust_n =
    mass_kg * gravity_mps2 / hover_normalized_command;
  parameter Real max_collective_thrust_delta_n = 30.0 * collective_thrust_slope;

  MoSimQuadrotorModel.Control.Bridges.LqrBaselineEquationBridge core;

  Real collective_thrust_delta_n
    "Physical collective-thrust increment about the shared plant hover point";

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
  core.dt = sample_time_s;
  core.enable = 1;

  // The LQR bridge emits ENU/FLU roll while the shared MWORKS plant uses the
  // reciprocal physical roll sign at the allocator boundary.
  attitude_ref[1] = -core.desired_roll_rad_out;
  attitude_ref[2] = core.desired_pitch_rad_out;
  attitude_ref[3] = 0;
  // The readable graphical core is calibrated around a 0.37 normalized hover
  // command. Convert that signal to physical total thrust before the shared
  // allocator receives its required increment about hover.
  collective_thrust_delta_n = normalized_to_physical_collective_thrust_n
    * core.normalized_thrust_out - mass_kg * gravity_mps2;
  collective_thrust_delta = min(max(collective_thrust_delta_n,
    -max_collective_thrust_delta_n), max_collective_thrust_delta_n);

  annotation(__MWORKS(version = "26.3.0"));
end LqrBaselineAttitudeThrustAdapter;