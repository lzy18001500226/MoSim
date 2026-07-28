within MoSimQuadrotorModel.Guidance.Planning;
model Sunray150PlanningCorridorGateLinearMPCSysblockClosedLoop
  "Sunray150 single-UAV corridor-gate A* reference tracked by the LinearMPC-style Sysblock controller"
  parameter Real legacy_hover_motor_speed_cmd = 13.985413115099604
    "Original MWORKS-equivalent hover command before Sunray150 SDF motorConstant calibration";
  parameter Real hover_motor_speed_cmd = MoSimQuadrotorModel.Parameters.sunray150_virtual_px4_classic_hover_visual_rotor_speed_rad_s
    "MWORKS visual rotor hover speed; physical Sunray150 motor speed is 10x by rotorVelocitySlowdownSim";
  parameter Real motor_command_scale = hover_motor_speed_cmd / legacy_hover_motor_speed_cmd
    "Scale legacy controller speed increments to the Sunray150 SDF motorConstant speed domain";

  PlannedQuinticReference planningReference(
    n_segments = 5,
    p_x = cat(1, {-0.5, -0.5, 2.2, 4.2, 5.8, 6.6}, fill(6.6, 85)),
    p_y = cat(1, {-2.25, -2.25, -1.0, 0.15, 1.25, 2.1}, fill(2.1, 85)),
    p_z = cat(1, {0.5279007479379901, 1.0, 1.0, 1.0, 1.0, 1.0}, fill(1.0, 85)),
    segment_duration = cat(1, {3.0, 10.744961467121772, 2.197265625, 4.026470337517248, 2.197265625}, fill(1.0, 85)));
  PlanningNavigationDisplay navigationDisplay(
    n_segments = 5,
    p_x = cat(1, {-0.5, -0.5, 2.2, 4.2, 5.8, 6.6}, fill(6.6, 85)),
    p_y = cat(1, {-2.25, -2.25, -1.0, 0.15, 1.25, 2.1}, fill(2.1, 85)),
    p_z = cat(1, {0.5279007479379901, 1.0, 1.0, 1.0, 1.0, 1.0}, fill(1.0, 85)),
    segment_duration = cat(1, {3.0, 10.744961467121772, 2.197265625, 4.026470337517248, 2.197265625}, fill(1.0, 85)),
    x_min = -1.0,
    x_max = 8.0,
    y_min = -2.5,
    y_max = 2.5,
    local_costmap_radius_m = 100.0,
    max_pillars = 40,
    pillar_count = 34,
    pillar_center = {{1.05, -1.55}, {1.21, -1.55}, {1.13, -1.39},
      {1.55, 1.35}, {1.71, 1.35}, {1.55, 1.51}, {1.71, 1.51},
      {2.55, -1.95}, {2.71, -1.95}, {2.55, -1.79},
      {2.55, 1.05}, {2.71, 1.05}, {2.55, 1.21}, {2.71, 1.21},
      {3.35, -1.30}, {3.51, -1.30}, {3.43, -1.14},
      {4.35, 1.35}, {4.51, 1.35}, {4.35, 1.51}, {4.51, 1.51},
      {5.00, 0.35}, {5.16, 0.35}, {5.00, 0.51},
      {5.65, -1.35}, {5.81, -1.35}, {5.65, -1.19}, {5.81, -1.19},
      {6.20, 1.10}, {6.36, 1.10}, {6.28, 1.26},
      {6.75, -0.95}, {6.91, -0.95}, {6.83, -0.79},
      {0.0, 0.0}, {0.0, 0.0}, {0.0, 0.0}, {0.0, 0.0}, {0.0, 0.0}, {0.0, 0.0}},
    pillar_width = fill(0.16, 40),
    pillar_height = {2.2, 2.4, 2.1,
      2.0, 2.3, 2.2, 2.4,
      2.1, 2.3, 1.9,
      2.2, 2.4, 2.1, 2.3,
      1.9, 2.1, 2.3,
      2.0, 2.2, 2.4, 2.1,
      2.3, 2.0, 2.2,
      1.8, 2.0, 2.2, 1.9,
      2.2, 2.4, 2.1,
      1.9, 2.1, 2.3,
      1.0, 1.0, 1.0, 1.0, 1.0, 1.0});
  MoSimQuadrotorModel.Vehicle.Mechanics.QuadChassis quadChassisTest17_1(
    body(color = {135, 206, 235}, r_0(start = {-0.5, -2.25, 0.5279007479379901}, fixed = {true, true, true})));
  MoSimQuadrotorModel.Vehicle.Electricals.Actuator actuator1_1(dcpm(wMechanical(start = hover_motor_speed_cmd)));
  MoSimQuadrotorModel.Vehicle.Electricals.Actuator actuator1_2(dcpm(wMechanical(start = -hover_motor_speed_cmd)));
  MoSimQuadrotorModel.Vehicle.Electricals.Actuator actuator1_3(dcpm(wMechanical(start = hover_motor_speed_cmd)));
  MoSimQuadrotorModel.Vehicle.Electricals.Actuator actuator1_4(dcpm(wMechanical(start = -hover_motor_speed_cmd)));
  MoSimQuadrotorModel.Vehicle.Sensors.Sensors sensors1_1;
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
  MoSimQuadrotorModel.Control.Implementations.Sysblocks.AWFF_LinearMPCOuterLoopControllerEquation_Sysblock controller3_2;

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

  annotation(experiment(Algorithm = Dassl, StartTime = 0, StopTime = 23, Tolerance = 0.0001, Interval = 0.01));
  annotation(__MWORKS(hide=true,version="26.3.0"));
end Sunray150PlanningCorridorGateLinearMPCSysblockClosedLoop;
