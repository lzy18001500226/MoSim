within MoSimQuadrotorModel.Control.Adapters;
model CascadePidAttitudeThrustAdapter
  "Current-root cascade PID adapter at the offline ATTITUDE_THRUST boundary"

  extends MoSimQuadrotorModel.Control.Interfaces.PartialAttitudeThrustController;

  parameter MoSimQuadrotorModel.Parameters.Sunray150VirtualPx4Classic profile;
  parameter Real sample_time_s = 0.01;
  parameter Real mass_kg = profile.takeoff_mass_kg;
  parameter Real gravity_mps2 = profile.gravity_mps2;
  parameter Real max_tilt_rad = 0.5235987755982989;
  parameter Real min_collective_thrust_n = 0.0;
  parameter Real max_collective_thrust_n = 2 * mass_kg * gravity_mps2
    "Controller safety limit; below the virtual plant physical maximum thrust";
  parameter Real hover_speed = profile.mworks_hover_visual_rotor_speed_rad_s;
  parameter Real lift_coefficient = profile.mworks_visual_thrust_coefficient;
  parameter Real max_rotor_speed_delta = 30.0;
  parameter Real hover_collective_thrust_n = 4 * lift_coefficient * hover_speed ^ 2;
  parameter Real collective_thrust_slope = 8 * lift_coefficient * hover_speed;

  PidAttitudeThrustCFunction core
    annotation(Placement(transformation(origin = {0, 0}, extent = {{-32, -82}, {32, 82}})));
  Modelica.Blocks.Continuous.Derivative velocity_estimator[3](
    each k = 1,
    each T = 0.05,
    each initType = Modelica.Blocks.Types.Init.InitialOutput,
    each y_start = 0);
  Modelica.Blocks.Continuous.Derivative angular_rate_estimator[3](
    each k = 1,
    each T = 0.02,
    each initType = Modelica.Blocks.Types.Init.InitialOutput,
    each y_start = 0);
  Modelica.Blocks.Sources.Constant algorithm_id_source(k = 1) annotation(Placement(transformation(extent={{-15,-50},{15,-10}})));
  Modelica.Blocks.Sources.Constant dt_source(k = sample_time_s) annotation(Placement(transformation(extent={{-15,-50},{15,-10}})));
  Modelica.Blocks.Sources.Constant reference_velocity_source(k = 0) annotation(Placement(transformation(extent={{-15,-50},{15,-10}})));
  Modelica.Blocks.Sources.Constant reference_acceleration_source(k = 0) annotation(Placement(transformation(extent={{-15,-50},{15,-10}})));
  Modelica.Blocks.Sources.Constant reference_yaw_source(k = 0) annotation(Placement(transformation(extent={{-15,-50},{15,-10}})));
  Modelica.Blocks.Sources.Constant mass_source(k = mass_kg) annotation(Placement(transformation(extent={{-15,-50},{15,-10}})));
  Modelica.Blocks.Sources.Constant gravity_source(k = gravity_mps2) annotation(Placement(transformation(extent={{-15,-50},{15,-10}})));
  Modelica.Blocks.Sources.Constant max_tilt_source(k = max_tilt_rad) annotation(Placement(transformation(extent={{-15,-50},{15,-10}})));
  Modelica.Blocks.Sources.Constant min_thrust_source(k = min_collective_thrust_n) annotation(Placement(transformation(extent={{-15,-50},{15,-10}})));
  Modelica.Blocks.Sources.Constant max_thrust_source(k = max_collective_thrust_n) annotation(Placement(transformation(extent={{-15,-50},{15,-10}})));
  Modelica.Blocks.Sources.Constant auxiliary_zero_source(k = 0) annotation(Placement(transformation(extent={{-15,-50},{15,-10}})));
  Modelica.Blocks.Sources.Constant enable_source(k = 1) annotation(Placement(transformation(extent={{-15,-50},{15,-10}})));
  Modelica.Blocks.Sources.RealExpression reset_source(y = if time < 1.5 * sample_time_s then 1 else 0) annotation(Placement(transformation(extent={{-15,-50},{15,-10}})));

  Real roll_mea annotation(Placement(transformation(extent={{-15,-150},{15,-110}})));
  Real pitch_mea annotation(Placement(transformation(extent={{-15,162},{15,202}})));
  Real yaw_mea annotation(Placement(transformation(extent={{-15,-358},{15,-318}})));
  Real q_w annotation(Placement(transformation(extent={{-15,58},{15,98}})));
  Real q_x annotation(Placement(transformation(extent={{-15,6},{15,46}})));
  Real q_y annotation(Placement(transformation(extent={{-15,-46},{15,-6}})));
  Real q_z annotation(Placement(transformation(extent={{-15,-98},{15,-58}})));
  Real roll_ref annotation(Placement(transformation(extent={{-15,-202},{15,-162}})));
  Real pitch_ref annotation(Placement(transformation(extent={{-15,110},{15,150}})));
  Real yaw_ref annotation(Placement(transformation(extent={{-15,-410},{15,-370}})));
  Real pitch_argument annotation(Placement(transformation(extent={{-15,214},{15,254}})));
  Real desired_collective_thrust_n annotation(Placement(transformation(extent={{-15,318},{15,358}})));
  Real desired_rotor_speed_delta annotation(Placement(transformation(extent={{-15,266},{15,306}})));
  Real status_code annotation(Placement(transformation(extent={{-15,-306},{15,-266}})));
  Real saturated annotation(Placement(transformation(extent={{-15,-254},{15,-214}})));
  annotation(__MWORKS(version = "26.3.0"));

equation
  connect(position_mea, velocity_estimator.u);
  connect(attitude_mea, angular_rate_estimator.u);

  roll_mea = attitude_mea[1];
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

  connect(algorithm_id_source.y, core.algorithm_id_in);
  connect(dt_source.y, core.dt_in);
  connect(position_mea[1], core.position_x_in);
  connect(position_mea[2], core.position_y_in);
  connect(position_mea[3], core.position_z_in);
  connect(velocity_estimator[1].y, core.velocity_x_in);
  connect(velocity_estimator[2].y, core.velocity_y_in);
  connect(velocity_estimator[3].y, core.velocity_z_in);
  core.attitude_w_in = q_w;
  core.attitude_x_in = q_x;
  core.attitude_y_in = q_y;
  core.attitude_z_in = q_z;
  connect(angular_rate_estimator[1].y, core.angular_velocity_x_in);
  connect(angular_rate_estimator[2].y, core.angular_velocity_y_in);
  connect(angular_rate_estimator[3].y, core.angular_velocity_z_in);
  connect(position_ref[1], core.reference_position_x_in);
  connect(position_ref[2], core.reference_position_y_in);
  connect(position_ref[3], core.reference_position_z_in);
  connect(reference_velocity_source.y, core.reference_velocity_x_in);
  connect(reference_velocity_source.y, core.reference_velocity_y_in);
  connect(reference_velocity_source.y, core.reference_velocity_z_in);
  connect(reference_acceleration_source.y, core.reference_acceleration_x_in);
  connect(reference_acceleration_source.y, core.reference_acceleration_y_in);
  connect(reference_acceleration_source.y, core.reference_acceleration_z_in);
  connect(reference_yaw_source.y, core.reference_yaw_in);
  connect(mass_source.y, core.mass_kg_in);
  connect(gravity_source.y, core.gravity_mps2_in);
  connect(max_tilt_source.y, core.max_tilt_rad_in);
  connect(min_thrust_source.y, core.min_collective_thrust_n_in);
  connect(max_thrust_source.y, core.max_collective_thrust_n_in);
  connect(auxiliary_zero_source.y, core.schedule_x_in);
  connect(auxiliary_zero_source.y, core.schedule_y_in);
  connect(auxiliary_zero_source.y, core.schedule_z_in);
  connect(auxiliary_zero_source.y, core.fuzzy_error_x_in);
  connect(auxiliary_zero_source.y, core.fuzzy_error_y_in);
  connect(auxiliary_zero_source.y, core.fuzzy_error_z_in);
  connect(auxiliary_zero_source.y, core.neural_residual_x_in);
  connect(auxiliary_zero_source.y, core.neural_residual_y_in);
  connect(auxiliary_zero_source.y, core.neural_residual_z_in);
  connect(enable_source.y, core.enable_in);
  connect(reset_source.y, core.reset_in);

  desired_collective_thrust_n = core.desired_collective_thrust_n_out;
  saturated = core.saturated_out;
  status_code = core.status_code_out;
  roll_ref = atan2(2 * (core.desired_attitude_w_out * core.desired_attitude_x_out
    + core.desired_attitude_y_out * core.desired_attitude_z_out),
    1 - 2 * (core.desired_attitude_x_out ^ 2 + core.desired_attitude_y_out ^ 2));
  pitch_argument = 2 * (core.desired_attitude_w_out * core.desired_attitude_y_out
    - core.desired_attitude_z_out * core.desired_attitude_x_out);
  pitch_ref = if pitch_argument >= 1 then Modelica.Constants.pi / 2
    else if pitch_argument <= -1 then -Modelica.Constants.pi / 2 else asin(pitch_argument);
  yaw_ref = atan2(2 * (core.desired_attitude_w_out * core.desired_attitude_z_out
    + core.desired_attitude_x_out * core.desired_attitude_y_out),
    1 - 2 * (core.desired_attitude_y_out ^ 2 + core.desired_attitude_z_out ^ 2));
  desired_rotor_speed_delta = min(max(
    (desired_collective_thrust_n - hover_collective_thrust_n) / collective_thrust_slope,
    -max_rotor_speed_delta), max_rotor_speed_delta);
  attitude_ref[1] = roll_ref;
  attitude_ref[2] = pitch_ref;
  attitude_ref[3] = yaw_ref;
  collective_thrust_delta = desired_rotor_speed_delta;
end CascadePidAttitudeThrustAdapter;
