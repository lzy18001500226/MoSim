within MoSimQuadrotorModel.SceneTrace.Scenarios;
model Sunray150UEFactoryLinearMPCSysblockSmoke
  "Sunray150 UE accepted scene smoke reference for factoryenvironmentcollect; control interface only"
  parameter Real legacy_hover_motor_speed_cmd = 13.985413115099604
    "Original MWORKS-equivalent hover command before Sunray150 SDF motorConstant calibration";
  parameter Real hover_motor_speed_cmd = MoSimQuadrotorModel.Parameters.sunray150_virtual_px4_classic_hover_visual_rotor_speed_rad_s
    "MWORKS visual rotor hover speed; physical Sunray150 motor speed is 10x by rotorVelocitySlowdownSim";
  parameter Real motor_command_scale = hover_motor_speed_cmd / legacy_hover_motor_speed_cmd
    "Scale legacy controller speed increments to the Sunray150 SDF motorConstant speed domain";

  PlannedQuinticReference planningReference(
    n_segments = 33,
    p_x = {
      -55.58, -54.83, -54.83, -54.83, -54.08, -53.33,
      -52.58, -51.83, -51.08, -50.33, -49.58, -48.83,
      -48.08, -47.33, -46.58, -45.83, -45.08, -44.33,
      -43.58, -42.83, -42.08, -41.33, -40.58, -39.83,
      -39.08, -38.33, -37.58, -36.83, -36.08, -35.33,
      -34.58, -33.83, -33.08, -32.33, -32.33, -32.33,
      -32.33, -32.33, -32.33, -32.33, -32.33, -32.33,
      -32.33, -32.33, -32.33, -32.33, -32.33, -32.33,
      -32.33, -32.33, -32.33, -32.33, -32.33, -32.33,
      -32.33, -32.33, -32.33, -32.33, -32.33, -32.33,
      -32.33, -32.33, -32.33, -32.33, -32.33, -32.33,
      -32.33, -32.33, -32.33, -32.33, -32.33, -32.33,
      -32.33, -32.33, -32.33, -32.33, -32.33, -32.33,
      -32.33, -32.33, -32.33, -32.33, -32.33, -32.33,
      -32.33, -32.33, -32.33, -32.33, -32.33, -32.33,
      -32.33},
    p_y = {
      -24.48, -23.73, -22.98, -22.23, -22.23, -22.23,
      -22.23, -22.23, -22.23, -22.23, -22.23, -22.23,
      -22.23, -22.23, -22.23, -22.23, -22.23, -22.23,
      -22.23, -22.23, -22.23, -22.23, -22.23, -22.23,
      -22.23, -22.23, -22.23, -22.23, -22.23, -22.23,
      -22.23, -22.23, -22.23, -22.23, -22.23, -22.23,
      -22.23, -22.23, -22.23, -22.23, -22.23, -22.23,
      -22.23, -22.23, -22.23, -22.23, -22.23, -22.23,
      -22.23, -22.23, -22.23, -22.23, -22.23, -22.23,
      -22.23, -22.23, -22.23, -22.23, -22.23, -22.23,
      -22.23, -22.23, -22.23, -22.23, -22.23, -22.23,
      -22.23, -22.23, -22.23, -22.23, -22.23, -22.23,
      -22.23, -22.23, -22.23, -22.23, -22.23, -22.23,
      -22.23, -22.23, -22.23, -22.23, -22.23, -22.23,
      -22.23, -22.23, -22.23, -22.23, -22.23, -22.23,
      -22.23},
    p_z = {
      1.9, 1.9, 1.9, 1.9, 1.9, 1.9,
      1.9, 1.9, 1.9, 1.9, 1.9, 1.9,
      1.9, 1.9, 1.9, 1.9, 1.9, 1.9,
      1.9, 1.9, 1.9, 1.9, 1.9, 1.9,
      1.9, 1.9, 1.9, 1.9, 1.9, 1.9,
      1.9, 1.9, 1.9, 1.9, 1.9, 1.9,
      1.9, 1.9, 1.9, 1.9, 1.9, 1.9,
      1.9, 1.9, 1.9, 1.9, 1.9, 1.9,
      1.9, 1.9, 1.9, 1.9, 1.9, 1.9,
      1.9, 1.9, 1.9, 1.9, 1.9, 1.9,
      1.9, 1.9, 1.9, 1.9, 1.9, 1.9,
      1.9, 1.9, 1.9, 1.9, 1.9, 1.9,
      1.9, 1.9, 1.9, 1.9, 1.9, 1.9,
      1.9, 1.9, 1.9, 1.9, 1.9, 1.9,
      1.9, 1.9, 1.9, 1.9, 1.9, 1.9,
      1.9},
    segment_duration = {
      1.32582521472, 0.9375, 0.9375, 0.9375, 0.9375, 0.9375,
      0.9375, 0.9375, 0.9375, 0.9375, 0.9375, 0.9375,
      0.9375, 0.9375, 0.9375, 0.9375, 0.9375, 0.9375,
      0.9375, 0.9375, 0.9375, 0.9375, 0.9375, 0.9375,
      0.9375, 0.9375, 0.9375, 0.9375, 0.9375, 0.9375,
      0.9375, 0.9375, 0.9375, 1, 1, 1,
      1, 1, 1, 1, 1, 1,
      1, 1, 1, 1, 1, 1,
      1, 1, 1, 1, 1, 1,
      1, 1, 1, 1, 1, 1,
      1, 1, 1, 1, 1, 1,
      1, 1, 1, 1, 1, 1,
      1, 1, 1, 1, 1, 1,
      1, 1, 1, 1, 1, 1,
      1, 1, 1, 1, 1, 1});
  PlanningNavigationDisplay navigationDisplay(
    n_segments = 33,
    p_x = {
      -55.58, -54.83, -54.83, -54.83, -54.08, -53.33,
      -52.58, -51.83, -51.08, -50.33, -49.58, -48.83,
      -48.08, -47.33, -46.58, -45.83, -45.08, -44.33,
      -43.58, -42.83, -42.08, -41.33, -40.58, -39.83,
      -39.08, -38.33, -37.58, -36.83, -36.08, -35.33,
      -34.58, -33.83, -33.08, -32.33, -32.33, -32.33,
      -32.33, -32.33, -32.33, -32.33, -32.33, -32.33,
      -32.33, -32.33, -32.33, -32.33, -32.33, -32.33,
      -32.33, -32.33, -32.33, -32.33, -32.33, -32.33,
      -32.33, -32.33, -32.33, -32.33, -32.33, -32.33,
      -32.33, -32.33, -32.33, -32.33, -32.33, -32.33,
      -32.33, -32.33, -32.33, -32.33, -32.33, -32.33,
      -32.33, -32.33, -32.33, -32.33, -32.33, -32.33,
      -32.33, -32.33, -32.33, -32.33, -32.33, -32.33,
      -32.33, -32.33, -32.33, -32.33, -32.33, -32.33,
      -32.33},
    p_y = {
      -24.48, -23.73, -22.98, -22.23, -22.23, -22.23,
      -22.23, -22.23, -22.23, -22.23, -22.23, -22.23,
      -22.23, -22.23, -22.23, -22.23, -22.23, -22.23,
      -22.23, -22.23, -22.23, -22.23, -22.23, -22.23,
      -22.23, -22.23, -22.23, -22.23, -22.23, -22.23,
      -22.23, -22.23, -22.23, -22.23, -22.23, -22.23,
      -22.23, -22.23, -22.23, -22.23, -22.23, -22.23,
      -22.23, -22.23, -22.23, -22.23, -22.23, -22.23,
      -22.23, -22.23, -22.23, -22.23, -22.23, -22.23,
      -22.23, -22.23, -22.23, -22.23, -22.23, -22.23,
      -22.23, -22.23, -22.23, -22.23, -22.23, -22.23,
      -22.23, -22.23, -22.23, -22.23, -22.23, -22.23,
      -22.23, -22.23, -22.23, -22.23, -22.23, -22.23,
      -22.23, -22.23, -22.23, -22.23, -22.23, -22.23,
      -22.23, -22.23, -22.23, -22.23, -22.23, -22.23,
      -22.23},
    p_z = {
      1.9, 1.9, 1.9, 1.9, 1.9, 1.9,
      1.9, 1.9, 1.9, 1.9, 1.9, 1.9,
      1.9, 1.9, 1.9, 1.9, 1.9, 1.9,
      1.9, 1.9, 1.9, 1.9, 1.9, 1.9,
      1.9, 1.9, 1.9, 1.9, 1.9, 1.9,
      1.9, 1.9, 1.9, 1.9, 1.9, 1.9,
      1.9, 1.9, 1.9, 1.9, 1.9, 1.9,
      1.9, 1.9, 1.9, 1.9, 1.9, 1.9,
      1.9, 1.9, 1.9, 1.9, 1.9, 1.9,
      1.9, 1.9, 1.9, 1.9, 1.9, 1.9,
      1.9, 1.9, 1.9, 1.9, 1.9, 1.9,
      1.9, 1.9, 1.9, 1.9, 1.9, 1.9,
      1.9, 1.9, 1.9, 1.9, 1.9, 1.9,
      1.9, 1.9, 1.9, 1.9, 1.9, 1.9,
      1.9, 1.9, 1.9, 1.9, 1.9, 1.9,
      1.9},
    segment_duration = {
      1.32582521472, 0.9375, 0.9375, 0.9375, 0.9375, 0.9375,
      0.9375, 0.9375, 0.9375, 0.9375, 0.9375, 0.9375,
      0.9375, 0.9375, 0.9375, 0.9375, 0.9375, 0.9375,
      0.9375, 0.9375, 0.9375, 0.9375, 0.9375, 0.9375,
      0.9375, 0.9375, 0.9375, 0.9375, 0.9375, 0.9375,
      0.9375, 0.9375, 0.9375, 1, 1, 1,
      1, 1, 1, 1, 1, 1,
      1, 1, 1, 1, 1, 1,
      1, 1, 1, 1, 1, 1,
      1, 1, 1, 1, 1, 1,
      1, 1, 1, 1, 1, 1,
      1, 1, 1, 1, 1, 1,
      1, 1, 1, 1, 1, 1,
      1, 1, 1, 1, 1, 1,
      1, 1, 1, 1, 1, 1},
    x_min = -63.58,
    x_max = -24.33,
    y_min = -32.48,
    y_max = -14.23,
    boundary_line_diameter_m = 0.0,
    render_boundary_walls = false,
    boundary_wall_height_m = 0.0,
    boundary_wall_thickness_m = 0.0,
    highlight_local_costmap = true,
    local_costmap_radius_m = 6.0,
    local_costmap_fade_radius_m = 9.0,
    local_costmap_front_half_angle_rad = 3.141592653589793,
    local_costmap_update_period_s = 0.05,
    local_costmap_half_cells = 18,
    local_costmap_cell_size_m = 0.5,
    local_sensed_cell_size_m = 0.5,
    local_sensed_half_cells = 18,
    local_plan_horizon_s = 4.0,
    local_plan_point_count = 12,
    local_plan_max_length_m = 4.0,
    render_terrain_blocks = false,
    show_static_map_mesh = false,
    show_static_map_layers = false,
    show_continuous_ground = false,
    max_pillars = 1,
    pillar_count = 0,
    pillar_center = {{0.0, 0.0}},
    pillar_length = {0.16},
    pillar_width = {0.16},
    pillar_height = {1.0},
    pillar_z_min = {0.0},
    max_wall_groups = 1,
    wall_group_count = 0,
    wall_arm1_min = {{0.0, 0.0, 0.0}},
    wall_arm1_max = {{0.0, 0.0, 0.0}},
    wall_arm2_min = {{0.0, 0.0, 0.0}},
    wall_arm2_max = {{0.0, 0.0, 0.0}});
  MoSimQuadrotorModel.Plant.Mechanics.QuadChassis quadChassisTest17_1(
    body(color = {135, 206, 235}, r_0(start = {-55.58, -24.48, 1.9}, fixed = {true, true, true})));
  MoSimQuadrotorModel.Plant.Electricals.Actuator actuator1_1(dcpm(wMechanical(start = hover_motor_speed_cmd)));
  MoSimQuadrotorModel.Plant.Electricals.Actuator actuator1_2(dcpm(wMechanical(start = -hover_motor_speed_cmd)));
  MoSimQuadrotorModel.Plant.Electricals.Actuator actuator1_3(dcpm(wMechanical(start = hover_motor_speed_cmd)));
  MoSimQuadrotorModel.Plant.Electricals.Actuator actuator1_4(dcpm(wMechanical(start = -hover_motor_speed_cmd)));
  MoSimQuadrotorModel.Plant.Sensors.Sensors sensors1_1;
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

  annotation(experiment(Algorithm = Dassl, StartTime = 0, StopTime = 31.3258252147, Tolerance = 0.0001, Interval = 0.05));
  annotation(__MWORKS(hide=true,version="26.3.0"));
end Sunray150UEFactoryLinearMPCSysblockSmoke;