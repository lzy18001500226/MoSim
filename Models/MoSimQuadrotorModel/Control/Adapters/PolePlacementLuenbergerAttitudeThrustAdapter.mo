within MoSimQuadrotorModel.Control.Adapters;
model PolePlacementLuenbergerAttitudeThrustAdapter
  "Pole-placement/Luenberger CFunction law adapted to ATTITUDE_THRUST"

  extends MoSimQuadrotorModel.Control.Interfaces.PartialAttitudeThrustController;

  parameter MoSimQuadrotorModel.Parameters.Sunray150VirtualPx4Classic profile;
  parameter Real sample_time_s = 0.01;
  parameter Real hover_speed = profile.mworks_hover_visual_rotor_speed_rad_s;
  parameter Real lift_coefficient = profile.mworks_visual_thrust_coefficient;
  parameter Real hover_collective_thrust_n = 4 * lift_coefficient * hover_speed ^ 2;
  parameter Real collective_thrust_slope = 8 * lift_coefficient * hover_speed;
  parameter Real max_collective_thrust_delta_n = 30.0 * collective_thrust_slope;

  MoSimQuadrotorModel.Control.Bridges.PolePlacementLuenbergerEquationBridge core;

  Real roll_ref;
  Real pitch_argument;
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
  core.reference_yaw = 0;
  core.enable = 1;
  core.reset = if time < 1.5 * sample_time_s then 1 else 0;

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
  collective_thrust_delta = min(max(
    core.collective_thrust_n_out - hover_collective_thrust_n,
    -max_collective_thrust_delta_n), max_collective_thrust_delta_n);

  annotation(__MWORKS(version = "26.3.0"));
end PolePlacementLuenbergerAttitudeThrustAdapter;