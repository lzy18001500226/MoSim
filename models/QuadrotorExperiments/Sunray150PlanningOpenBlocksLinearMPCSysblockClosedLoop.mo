model Sunray150PlanningOpenBlocksLinearMPCSysblockClosedLoop
  "Sunray150 single-UAV A* obstacle-avoidance reference tracked by the LinearMPC-style Sysblock controller"
  parameter Real legacy_hover_motor_speed_cmd = 13.985413115099604
    "Original MWORKS-equivalent hover command before Sunray150 SDF motorConstant calibration";
  parameter Real hover_motor_speed_cmd = 53.562090367172424
    "MWORKS visual rotor hover speed; physical Sunray150 motor speed is 10x by rotorVelocitySlowdownSim";
  parameter Real motor_command_scale = hover_motor_speed_cmd / legacy_hover_motor_speed_cmd
    "Scale legacy controller speed increments to the Sunray150 SDF motorConstant speed domain";

  PlannedQuinticReference planningReference(
    n_segments = 5,
    p_x = {-0.5, -0.5, 1.0, 2.0, 4.5, 6.6},
    p_y = {-2.25, -2.25, -1.0, -1.0, 0.4, 2.1},
    p_z = {0.5279007479379901, 1.0, 1.0, 1.0, 1.0, 1.0},
    segment_duration = {3.0, 2.4407030237208294, 1.25, 3.5816371954736006, 3.377314021526574});
  PlanningNavigationDisplay navigationDisplay(
    n_segments = 5,
    p_x = {-0.5, -0.5, 1.0, 2.0, 4.5, 6.6},
    p_y = {-2.25, -2.25, -1.0, -1.0, 0.4, 2.1},
    p_z = {0.5279007479379901, 1.0, 1.0, 1.0, 1.0, 1.0},
    segment_duration = {3.0, 2.4407030237208294, 1.25, 3.5816371954736006, 3.377314021526574},
    x_min = -1.0,
    x_max = 7.0,
    y_min = -2.5,
    y_max = 2.5,
    highlight_local_costmap = true,
    local_costmap_radius_m = 1.25,
    local_costmap_front_half_angle_rad = 0.9599310885968813,
    local_costmap_update_period_s = 0.05,
    pillar_count = 34,
    pillar_center = {{0.82, -1.82}, {0.99, -1.76}, {0.90, -1.58},
      {1.28, 0.86}, {1.46, 0.93}, {1.33, 1.10}, {1.55, 1.13},
      {1.88, -0.62}, {2.05, -0.50}, {1.98, -0.32},
      {2.43, 1.64}, {2.60, 1.52}, {2.76, 1.66}, {2.58, 1.82},
      {3.05, -1.72}, {3.23, -1.58}, {3.00, -1.43},
      {3.68, 0.58}, {3.86, 0.47}, {3.79, 0.75}, {4.02, 0.66},
      {4.22, -1.05}, {4.42, -0.96}, {4.31, -0.76},
      {4.82, 1.42}, {5.01, 1.31}, {5.16, 1.50}, {4.96, 1.68},
      {5.54, -1.76}, {5.75, -1.66}, {5.62, -1.45},
      {6.18, 0.74}, {6.37, 0.90}, {6.10, 1.02},
      {0.0, 0.0}, {0.0, 0.0}, {0.0, 0.0}, {0.0, 0.0}, {0.0, 0.0}, {0.0, 0.0}},
    pillar_width = fill(0.16, 40),
    pillar_height = {1.8, 2.1, 1.9,
      1.7, 2.0, 2.2, 1.9,
      2.1, 1.8, 2.0,
      2.3, 2.0, 1.8, 2.1,
      2.2, 1.9, 2.0,
      1.9, 2.2, 1.8, 2.1,
      2.0, 2.3, 1.9,
      1.8, 2.1, 2.3, 2.0,
      2.2, 1.9, 2.1,
      1.9, 2.2, 2.0,
      1.0, 1.0, 1.0, 1.0, 1.0, 1.0});
  QuadrotorModel.Mechanics.QuadChassis quadChassisTest17_1(
    body(color = {135, 206, 235}, r_0(start = {-0.5, -2.25, 0.5279007479379901}, fixed = {true, true, true})));
  QuadrotorModel.Electricals.Actuator actuator1_1(dcpm(wMechanical(start = hover_motor_speed_cmd)));
  QuadrotorModel.Electricals.Actuator actuator1_2(dcpm(wMechanical(start = -hover_motor_speed_cmd)));
  QuadrotorModel.Electricals.Actuator actuator1_3(dcpm(wMechanical(start = hover_motor_speed_cmd)));
  QuadrotorModel.Electricals.Actuator actuator1_4(dcpm(wMechanical(start = -hover_motor_speed_cmd)));
  QuadrotorModel.Sensors.Sensors sensors1_1;
  Modelica.Mechanics.Rotational.Sensors.SpeedSensor speedSensor[4];
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

  Modelica.Blocks.Math.Feedback x_error;
  Modelica.Blocks.Math.Feedback y_error;
  Modelica.Blocks.Math.Feedback z_error;
  AWFF_LinearMPCOuterLoopControllerEquation_Sysblock controller3_2;

equation
  connect(actuator1_1.flange_a, quadChassisTest17_1.flange_a);
  connect(actuator1_2.flange_a, quadChassisTest17_1.flange_a1);
  connect(actuator1_3.flange_a, quadChassisTest17_1.flange_a2);
  connect(actuator1_4.flange_a, quadChassisTest17_1.flange_a3);
  connect(quadChassisTest17_1.frame_a, sensors1_1.frame_a);
  connect(sensors1_1.PosMea, navigationDisplay.actual_position);
  connect(planningReference.position_command, navigationDisplay.reference_position);

  connect(planningReference.position_command[1], x_error.u1);
  connect(sensors1_1.PosMea[1], x_error.u2);
  connect(planningReference.position_command[2], y_error.u1);
  connect(sensors1_1.PosMea[2], y_error.u2);
  connect(planningReference.position_command[3], z_error.u1);
  connect(sensors1_1.PosMea[3], z_error.u2);

  connect(x_error.y, controller3_2.x_error);
  connect(y_error.y, controller3_2.y_error);
  connect(z_error.y, controller3_2.z_error);
  connect(planningReference.z_ref_rate, controller3_2.z_ref_rate);
  connect(sensors1_1.AngleMea[1], controller3_2.roll_mea);
  connect(sensors1_1.AngleMea[2], controller3_2.pitch_mea);
  connect(sensors1_1.AngleMea[3], controller3_2.yaw_mea);
  connect(planningReference.yaw_ref, controller3_2.yaw_ref);

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

  annotation(experiment(Algorithm = Dassl, StartTime = 0, StopTime = 16, Tolerance = 0.0001, Interval = 0.01));
end Sunray150PlanningOpenBlocksLinearMPCSysblockClosedLoop;
