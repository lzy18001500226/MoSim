model Example1HelicalFigure8TrailSysblockClosedLoop
  "Official EightPath-style helical figure-8 with LinearMPC controller and native GUI review trail"
  parameter Real takeoff_duration_s = 10.0;
  parameter Real mission_figure8_duration_s = 110.0;
  parameter Real mission_figure8_x_scale_m = 2.5;
  parameter Real mission_figure8_y_scale_m = 2.5;
  parameter Real mission_altitude_m = 1.0;
  parameter Real mission_altitude_gain_m = 2.0;
  parameter Real legacy_hover_motor_speed_cmd = 13.985413115099604
    "Original MWORKS-equivalent hover command before Sunray150 SDF motorConstant calibration";
  parameter Real hover_motor_speed_cmd = 53.562090367172424
    "MWORKS visual rotor hover speed; physical Sunray150 motor speed is 10x by rotorVelocitySlowdownSim";
  parameter Real motor_command_scale = hover_motor_speed_cmd / legacy_hover_motor_speed_cmd
    "Scale legacy controller speed increments to the Sunray150 SDF motorConstant speed domain";
  parameter Real official_x_omega = 0.02;
  parameter Real official_y_omega = 0.04;
  parameter Real official_x_phase_offset = 1 / 360;
  parameter Boolean show_online_reference_trail = true
    "Enable planned trajectory line in the native 3D animation";
  parameter Integer online_trail_points = 601
    "5 Hz reference trajectory samples over 120 s for responsive native 3D animation";
  parameter Real online_trail_sample_period_s = 0.2;
  parameter Real online_trail_line_diameter_m = 0.006;
  parameter Real current_position_marker_diameter_m = 0.04;
  parameter Real current_reference_marker_diameter_m = 0.03;
  parameter Real body_axis_marker_length_m = 0.28
    "Native GUI attitude audit body-axis marker length";
  parameter Real body_axis_marker_diameter_m = 0.012
    "Native GUI attitude audit body-axis marker diameter";
  parameter Real reference_trail_time[online_trail_points] = {(i - 1) * online_trail_sample_period_s for i in 1:online_trail_points};
  parameter Real reference_trail_path_time[online_trail_points] = {max(0, reference_trail_time[i] - takeoff_duration_s) for i in 1:online_trail_points};
  parameter Real reference_trail_point[online_trail_points, 3] = {{
      if reference_trail_time[i] <= takeoff_duration_s then 0 else mission_figure8_x_scale_m * sin((official_x_omega * reference_trail_path_time[i] + official_x_phase_offset) * Modelica.Constants.pi),
      if reference_trail_time[i] <= takeoff_duration_s then 0 else mission_figure8_y_scale_m * sin(official_y_omega * reference_trail_path_time[i] * Modelica.Constants.pi),
      if reference_trail_time[i] <= takeoff_duration_s then mission_altitude_m else if reference_trail_time[i] <= takeoff_duration_s + mission_figure8_duration_s then mission_altitude_m + mission_altitude_gain_m * reference_trail_path_time[i] / mission_figure8_duration_s else mission_altitude_m + mission_altitude_gain_m
    } for i in 1:online_trail_points};
  parameter Real reference_trail_segment_vector[online_trail_points - 1, 3] = {{
      reference_trail_point[i + 1, 1] - reference_trail_point[i, 1],
      reference_trail_point[i + 1, 2] - reference_trail_point[i, 2],
      reference_trail_point[i + 1, 3] - reference_trail_point[i, 3]
    } for i in 1:online_trail_points - 1};
  parameter Real reference_trail_segment_length[online_trail_points - 1] = {
    sqrt(reference_trail_segment_vector[i, 1] ^ 2 + reference_trail_segment_vector[i, 2] ^ 2 + reference_trail_segment_vector[i, 3] ^ 2) for i in 1:online_trail_points - 1};
  parameter Real reference_trail_segment_direction[online_trail_points - 1, 3] = {{
      if reference_trail_segment_length[i] > 1e-6 then reference_trail_segment_vector[i, 1] else 1.0,
      if reference_trail_segment_length[i] > 1e-6 then reference_trail_segment_vector[i, 2] else 0.0,
      if reference_trail_segment_length[i] > 1e-6 then reference_trail_segment_vector[i, 3] else 0.0
    } for i in 1:online_trail_points - 1};

  QuadrotorModel.Mechanics.QuadChassis quadChassisTest17_1(
    body(r_0(start = {0, 0, mission_altitude_m}, fixed = {true, true, true})));
  QuadrotorModel.PathPlanning.EightPath climbePath(
    XAMP = mission_figure8_x_scale_m,
    YAMP = mission_figure8_y_scale_m);
  QuadrotorModel.Electricals.Actuator actuator1_1(dcpm(wMechanical(start = hover_motor_speed_cmd)));
  QuadrotorModel.Electricals.Actuator actuator1_2(dcpm(wMechanical(start = -hover_motor_speed_cmd)));
  QuadrotorModel.Electricals.Actuator actuator1_3(dcpm(wMechanical(start = hover_motor_speed_cmd)));
  QuadrotorModel.Electricals.Actuator actuator1_4(dcpm(wMechanical(start = -hover_motor_speed_cmd)));
  QuadrotorModel.Sensors.Sensors sensors1_1;
  Modelica.Mechanics.Rotational.Sensors.SpeedSensor speedSensor[4];
  Real figure8_phase_time;
  Real figure8_vx_ref;
  Real figure8_vy_ref;

  Modelica.Blocks.Math.Feedback x_error;
  Modelica.Blocks.Math.Feedback y_error;
  Modelica.Blocks.Math.Feedback z_error;
  Modelica.Blocks.Sources.Constant hover_u1(k = hover_motor_speed_cmd);
  Modelica.Blocks.Sources.Constant hover_u2(k = -hover_motor_speed_cmd);
  Modelica.Blocks.Sources.Constant hover_u3(k = hover_motor_speed_cmd);
  Modelica.Blocks.Sources.Constant hover_u4(k = -hover_motor_speed_cmd);
  Modelica.Blocks.Math.Add motor1_hover_sum;
  Modelica.Blocks.Math.Add motor2_hover_sum;
  Modelica.Blocks.Math.Add motor3_hover_sum;
  Modelica.Blocks.Math.Add motor4_hover_sum;
  Modelica.Blocks.Math.Gain motor1_delta_scale(k = motor_command_scale);
  Modelica.Blocks.Math.Gain motor2_delta_scale(k = motor_command_scale);
  Modelica.Blocks.Math.Gain motor3_delta_scale(k = motor_command_scale);
  Modelica.Blocks.Math.Gain motor4_delta_scale(k = motor_command_scale);
  Modelica.Blocks.Sources.RealExpression z_ref(y = if time <= takeoff_duration_s then mission_altitude_m else if time <= takeoff_duration_s + mission_figure8_duration_s then mission_altitude_m + mission_altitude_gain_m * figure8_phase_time / mission_figure8_duration_s else mission_altitude_m + mission_altitude_gain_m);
  Modelica.Blocks.Sources.RealExpression z_ref_rate(y = if time <= takeoff_duration_s then 0 else if time <= takeoff_duration_s + mission_figure8_duration_s then mission_altitude_gain_m / mission_figure8_duration_s else 0);
  Modelica.Blocks.Sources.Constant yaw_ref(k = 0);
  Modelica.Mechanics.MultiBody.Visualizers.Advanced.Shape actual_position_marker(
    shapeType = "sphere",
    R = Modelica.Mechanics.MultiBody.Frames.nullRotation(),
    r = {sensors1_1.PosMea[1], sensors1_1.PosMea[2], sensors1_1.PosMea[3]},
    r_shape = {0, 0, 0},
    lengthDirection = {1, 0, 0},
    widthDirection = {0, 1, 0},
    length = current_position_marker_diameter_m,
    width = current_position_marker_diameter_m,
    height = current_position_marker_diameter_m,
    color = {0, 210, 90},
    specularCoefficient = 0.4);
  Modelica.Mechanics.MultiBody.Visualizers.Advanced.Shape current_reference_marker(
    shapeType = "sphere",
    R = Modelica.Mechanics.MultiBody.Frames.nullRotation(),
    r = {climbePath.position_command[1], climbePath.position_command[2], z_ref.y},
    r_shape = {0, 0, 0},
    lengthDirection = {1, 0, 0},
    widthDirection = {0, 1, 0},
    length = current_reference_marker_diameter_m,
    width = current_reference_marker_diameter_m,
    height = current_reference_marker_diameter_m,
    color = {255, 220, 0},
    specularCoefficient = 0.4);
  Modelica.Mechanics.MultiBody.Visualizers.FixedShape body_x_axis_marker(
    shapeType = "cylinder",
    r_shape = {0, 0, 0.09},
    lengthDirection = {1, 0, 0},
    widthDirection = {0, 1, 0},
    length = body_axis_marker_length_m,
    width = body_axis_marker_diameter_m,
    height = body_axis_marker_diameter_m,
    color = {255, 40, 40},
    animation = true)
    "Red body-frame x axis marker for native GUI attitude audit";
  Modelica.Mechanics.MultiBody.Visualizers.FixedShape body_y_axis_marker(
    shapeType = "cylinder",
    r_shape = {0, 0, 0.10},
    lengthDirection = {0, 1, 0},
    widthDirection = {1, 0, 0},
    length = body_axis_marker_length_m,
    width = body_axis_marker_diameter_m,
    height = body_axis_marker_diameter_m,
    color = {40, 220, 80},
    animation = true)
    "Green body-frame y axis marker for native GUI attitude audit";
  Modelica.Mechanics.MultiBody.Visualizers.FixedShape body_z_axis_marker(
    shapeType = "cylinder",
    r_shape = {0, 0, 0.11},
    lengthDirection = {0, 0, 1},
    widthDirection = {1, 0, 0},
    length = body_axis_marker_length_m,
    width = body_axis_marker_diameter_m,
    height = body_axis_marker_diameter_m,
    color = {40, 120, 255},
    animation = true)
    "Blue body-frame z axis marker for native GUI attitude audit";
  Modelica.Mechanics.MultiBody.Visualizers.Advanced.Shape reference_trajectory_trail_line[online_trail_points - 1](
    each shapeType = "cylinder",
    each R = Modelica.Mechanics.MultiBody.Frames.nullRotation(),
    r = {reference_trail_point[i, :] for i in 1:online_trail_points - 1},
    each r_shape = {0, 0, 0},
    lengthDirection = reference_trail_segment_direction,
    each widthDirection = {0, 0, 1},
    length = {if show_online_reference_trail then reference_trail_segment_length[i] else 0.0 for i in 1:online_trail_points - 1},
    each width = online_trail_line_diameter_m,
    each height = online_trail_line_diameter_m,
    color = {{255 * (i - 1) / (online_trail_points - 2), 80 + 120 * (i - 1) / (online_trail_points - 2), 255 - 230 * (i - 1) / (online_trail_points - 2)} for i in 1:online_trail_points - 1},
    each specularCoefficient = 0.4);

  AWFF_LinearMPCOuterLoopControllerEquation_Sysblock controller3_2(
    mpc_acc_limit_xy = 2.7,
    mpc_terminal_gain_xy = 0.12);

equation
  figure8_phase_time = if time <= takeoff_duration_s then 0 else time - takeoff_duration_s;
  figure8_vx_ref = mission_figure8_x_scale_m * official_x_omega * Modelica.Constants.pi * cos((official_x_omega * figure8_phase_time + official_x_phase_offset) * Modelica.Constants.pi);
  figure8_vy_ref = mission_figure8_y_scale_m * official_y_omega * Modelica.Constants.pi * cos(official_y_omega * figure8_phase_time * Modelica.Constants.pi);

  connect(actuator1_1.flange_a, quadChassisTest17_1.flange_a);
  connect(actuator1_2.flange_a, quadChassisTest17_1.flange_a1);
  connect(actuator1_3.flange_a, quadChassisTest17_1.flange_a2);
  connect(actuator1_4.flange_a, quadChassisTest17_1.flange_a3);
  connect(quadChassisTest17_1.frame_a, sensors1_1.frame_a);
  connect(quadChassisTest17_1.frame_a, body_x_axis_marker.frame_a);
  connect(quadChassisTest17_1.frame_a, body_y_axis_marker.frame_a);
  connect(quadChassisTest17_1.frame_a, body_z_axis_marker.frame_a);

  connect(climbePath.position_command[1], x_error.u1);
  connect(sensors1_1.PosMea[1], x_error.u2);
  connect(climbePath.position_command[2], y_error.u1);
  connect(sensors1_1.PosMea[2], y_error.u2);
  connect(z_ref.y, z_error.u1);
  connect(sensors1_1.PosMea[3], z_error.u2);

  connect(x_error.y, controller3_2.x_error);
  connect(y_error.y, controller3_2.y_error);
  connect(z_error.y, controller3_2.z_error);
  connect(z_ref_rate.y, controller3_2.z_ref_rate);
  connect(sensors1_1.AngleMea[1], controller3_2.roll_mea);
  connect(sensors1_1.AngleMea[2], controller3_2.pitch_mea);
  connect(sensors1_1.AngleMea[3], controller3_2.yaw_mea);
  connect(yaw_ref.y, controller3_2.yaw_ref);

  connect(controller3_2.y, motor1_delta_scale.u);
  connect(motor1_delta_scale.y, motor1_hover_sum.u1);
  connect(hover_u1.y, motor1_hover_sum.u2);
  connect(motor1_hover_sum.y, actuator1_1.u);
  connect(controller3_2.y1, motor2_delta_scale.u);
  connect(motor2_delta_scale.y, motor2_hover_sum.u1);
  connect(hover_u2.y, motor2_hover_sum.u2);
  connect(motor2_hover_sum.y, actuator1_2.u);
  connect(controller3_2.y2, motor3_delta_scale.u);
  connect(motor3_delta_scale.y, motor3_hover_sum.u1);
  connect(hover_u3.y, motor3_hover_sum.u2);
  connect(motor3_hover_sum.y, actuator1_3.u);
  connect(controller3_2.y3, motor4_delta_scale.u);
  connect(motor4_delta_scale.y, motor4_hover_sum.u1);
  connect(hover_u4.y, motor4_hover_sum.u2);
  connect(motor4_hover_sum.y, actuator1_4.u);

  connect(actuator1_1.flange_a, speedSensor[1].flange);
  connect(actuator1_2.flange_a, speedSensor[2].flange);
  connect(actuator1_3.flange_a, speedSensor[3].flange);
  connect(actuator1_4.flange_a, speedSensor[4].flange);

  annotation(experiment(Algorithm = Dassl, StartTime = 0, StopTime = 120, Tolerance = 0.0001, Interval = 0.05));
end Example1HelicalFigure8TrailSysblockClosedLoop;
