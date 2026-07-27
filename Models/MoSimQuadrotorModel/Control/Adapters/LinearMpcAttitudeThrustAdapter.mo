within MoSimQuadrotorModel.Control.Adapters;
model LinearMpcAttitudeThrustAdapter
  "Linear MPC C core adapted to the offline ATTITUDE_THRUST boundary"

  extends MoSimQuadrotorModel.Control.Interfaces.PartialAttitudeThrustController;

  parameter MoSimQuadrotorModel.Parameters.Sunray150VirtualPx4Classic profile;
  parameter Real sample_time_s = 0.01;
  parameter Real mass_kg = profile.takeoff_mass_kg;
  parameter Real gravity_mps2 = profile.gravity_mps2;
  parameter Real max_tilt_rad = 0.5235987755982989;
  parameter Real min_collective_thrust_n = 0;
  parameter Real max_collective_thrust_n = 2 * mass_kg * gravity_mps2;
  parameter Real hover_speed = profile.mworks_hover_visual_rotor_speed_rad_s;
  parameter Real lift_coefficient = profile.mworks_visual_thrust_coefficient;
  parameter Real hover_collective_thrust_n = 4 * lift_coefficient * hover_speed ^ 2;
  parameter Real collective_thrust_slope = 8 * lift_coefficient * hover_speed;
  parameter Real max_collective_thrust_delta_n = 30.0 * collective_thrust_slope;

  LinearMpcCFunction core;
  Real pitch_argument;
  Real desired_collective_thrust_n;
  Real solver_cost;
  Real solver_iterations;
  Real status_code;
  Real saturated;

equation
  core.controller_id_in = 1;
  core.dt_in = sample_time_s;
  core.position_x_in = position_mea[1];
  core.position_y_in = position_mea[2];
  core.position_z_in = position_mea[3];
  core.velocity_x_in = velocity_mea[1];
  core.velocity_y_in = velocity_mea[2];
  core.velocity_z_in = velocity_mea[3];
  core.reference_position_x_in = position_ref[1];
  core.reference_position_y_in = position_ref[2];
  core.reference_position_z_in = position_ref[3];
  core.reference_velocity_x_in = 0;
  core.reference_velocity_y_in = 0;
  core.reference_velocity_z_in = 0;
  core.reference_acceleration_x_in = 0;
  core.reference_acceleration_y_in = 0;
  core.reference_acceleration_z_in = 0;
  core.reference_yaw_in = 0;
  core.mass_kg_in = mass_kg;
  core.gravity_mps2_in = gravity_mps2;
  core.hover_percentage_in = profile.mworks_controller_hover_percentage;
  core.max_tilt_rad_in = max_tilt_rad;
  core.min_collective_thrust_n_in = min_collective_thrust_n;
  core.max_collective_thrust_n_in = max_collective_thrust_n;
  core.enable_in = 1;
  core.reset_in = if time < 1.5 * sample_time_s then 1 else 0;

  desired_collective_thrust_n = core.collective_thrust_n_out;
  solver_cost = core.solver_cost_out;
  solver_iterations = core.solver_iterations_out;
  saturated = core.saturated_out;
  status_code = core.status_code_out;
  attitude_ref[1] = atan2(2 * (core.desired_attitude_w_out * core.desired_attitude_x_out
    + core.desired_attitude_y_out * core.desired_attitude_z_out),
    1 - 2 * (core.desired_attitude_x_out ^ 2 + core.desired_attitude_y_out ^ 2));
  pitch_argument = 2 * (core.desired_attitude_w_out * core.desired_attitude_y_out
    - core.desired_attitude_z_out * core.desired_attitude_x_out);
  attitude_ref[2] = if pitch_argument >= 1 then Modelica.Constants.pi / 2
    else if pitch_argument <= -1 then -Modelica.Constants.pi / 2 else asin(pitch_argument);
  attitude_ref[3] = atan2(2 * (core.desired_attitude_w_out * core.desired_attitude_z_out
    + core.desired_attitude_x_out * core.desired_attitude_y_out),
    1 - 2 * (core.desired_attitude_y_out ^ 2 + core.desired_attitude_z_out ^ 2));
  collective_thrust_delta = min(max(desired_collective_thrust_n - hover_collective_thrust_n,
    -max_collective_thrust_delta_n), max_collective_thrust_delta_n);

  annotation(__MWORKS(version = "26.3.0"));
end LinearMpcAttitudeThrustAdapter;
