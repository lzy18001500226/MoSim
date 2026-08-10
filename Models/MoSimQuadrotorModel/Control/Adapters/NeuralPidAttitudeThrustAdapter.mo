within MoSimQuadrotorModel.Control.Adapters;
model NeuralPidAttitudeThrustAdapter
  "Bounded neural-residual PID core adapted to the shared ATTITUDE_THRUST boundary"

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

  MoSimQuadrotorModel.Control.Bridges.NeuralPidEquationBridge core;
  Modelica.Blocks.Continuous.Derivative angular_rate_estimator[3](
    each k = 1,
    each T = 0.02,
    each initType = Modelica.Blocks.Types.Init.InitialOutput,
    each y_start = 0);

  Real roll_mea;
  Real pitch_mea;
  Real yaw_mea;
  Real q_w;
  Real q_x;
  Real q_y;
  Real q_z;
  Real roll_ref;
  Real pitch_argument;
  Real desired_collective_thrust_n;

equation
  connect(attitude_mea, angular_rate_estimator.u);

  // The shared MWORKS plant reports roll opposite to the ENU/FLU PID core.
  roll_mea = -attitude_mea[1];
  pitch_mea = attitude_mea[2];
  yaw_mea = attitude_mea[3];
  q_w = cos(roll_mea / 2) * cos(pitch_mea / 2) * cos(yaw_mea / 2)
    + sin(roll_mea / 2) * sin(pitch_mea / 2) * sin(yaw_mea / 2);
  q_x = sin(roll_mea / 2) * cos(pitch_mea / 2) * cos(yaw_mea / 2)
    - cos(roll_mea / 2) * sin(pitch_mea / 2) * sin(yaw_mea / 2);
  q_y = cos(roll_mea / 2) * sin(pitch_mea / 2) * cos(yaw_mea / 2)
    + sin(roll_mea / 2) * cos(pitch_mea / 2) * sin(yaw_mea / 2);
  q_z = cos(roll_mea / 2) * cos(pitch_mea / 2) * sin(yaw_mea / 2)
    - sin(roll_mea / 2) * sin(pitch_mea / 2) * cos(yaw_mea / 2);

  core.dt_in = sample_time_s;
  core.position_x_in = position_mea[1];
  core.position_y_in = position_mea[2];
  core.position_z_in = position_mea[3];
  core.velocity_x_in = velocity_mea[1];
  core.velocity_y_in = velocity_mea[2];
  core.velocity_z_in = velocity_mea[3];
  core.attitude_w_in = q_w;
  core.attitude_x_in = q_x;
  core.attitude_y_in = q_y;
  core.attitude_z_in = q_z;
  core.angular_velocity_x_in = -angular_rate_estimator[1].y;
  core.angular_velocity_y_in = angular_rate_estimator[2].y;
  core.angular_velocity_z_in = angular_rate_estimator[3].y;
  core.reference_position_x_in = position_ref[1];
  core.reference_position_y_in = position_ref[2];
  core.reference_position_z_in = position_ref[3];
  core.reference_velocity_x_in = velocity_ref[1];
  core.reference_velocity_y_in = velocity_ref[2];
  core.reference_velocity_z_in = velocity_ref[3];
  core.reference_acceleration_x_in = acceleration_ref[1];
  core.reference_acceleration_y_in = acceleration_ref[2];
  core.reference_acceleration_z_in = acceleration_ref[3];
  core.reference_yaw_in = 0;
  core.mass_kg_in = mass_kg;
  core.gravity_mps2_in = gravity_mps2;
  core.max_tilt_rad_in = max_tilt_rad;
  core.min_collective_thrust_n_in = min_collective_thrust_n;
  core.max_collective_thrust_n_in = max_collective_thrust_n;
  core.schedule_x_in = 0;
  core.schedule_y_in = 0;
  core.schedule_z_in = 0;
  core.fuzzy_error_x_in = 0;
  core.fuzzy_error_y_in = 0;
  core.fuzzy_error_z_in = 0;
  // The declared Neural PID profile is a bounded zero-untrained residual route.
  core.neural_residual_x_in = 0;
  core.neural_residual_y_in = 0;
  core.neural_residual_z_in = 0;
  core.enable_in = 1;
  core.reset_in = if time < 1.5 * sample_time_s then 1 else 0;

  desired_collective_thrust_n = core.desired_collective_thrust_n_out;
  roll_ref = atan2(2 * (core.desired_attitude_w_out * core.desired_attitude_x_out
    + core.desired_attitude_y_out * core.desired_attitude_z_out),
    1 - 2 * (core.desired_attitude_x_out ^ 2 + core.desired_attitude_y_out ^ 2));
  pitch_argument = 2 * (core.desired_attitude_w_out * core.desired_attitude_y_out
    - core.desired_attitude_z_out * core.desired_attitude_x_out);
  attitude_ref[1] = -roll_ref;
  attitude_ref[2] = if pitch_argument >= 1 then Modelica.Constants.pi / 2 
    else if pitch_argument <= -1 then -Modelica.Constants.pi / 2 else asin(pitch_argument);
  attitude_ref[3] = atan2(2 * (core.desired_attitude_w_out * core.desired_attitude_z_out
    + core.desired_attitude_x_out * core.desired_attitude_y_out),
    1 - 2 * (core.desired_attitude_y_out ^ 2 + core.desired_attitude_z_out ^ 2));
  collective_thrust_delta = min(max(desired_collective_thrust_n - hover_collective_thrust_n,
    -max_collective_thrust_delta_n), max_collective_thrust_delta_n);

  annotation(__MWORKS(version = "26.3.0"));
end NeuralPidAttitudeThrustAdapter;