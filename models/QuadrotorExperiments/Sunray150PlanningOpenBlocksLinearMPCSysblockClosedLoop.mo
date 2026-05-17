model Sunray150PlanningOpenBlocksLinearMPCSysblockClosedLoop
  "Sunray150 single-UAV A* obstacle-avoidance reference tracked by the LinearMPC-style Sysblock controller"
  parameter Real legacy_hover_motor_speed_cmd = 13.985413115099604
    "Original MWORKS-equivalent hover command before Sunray150 SDF motorConstant calibration";
  parameter Real hover_motor_speed_cmd = 53.562090367172424
    "MWORKS visual rotor hover speed; physical Sunray150 motor speed is 10x by rotorVelocitySlowdownSim";
  parameter Real motor_command_scale = hover_motor_speed_cmd / legacy_hover_motor_speed_cmd
    "Scale legacy controller speed increments to the Sunray150 SDF motorConstant speed domain";

  PlannedQuinticReference planningReference(
    n_segments = 53,
    p_x = {
      -41, -41, -39, -36.6, -35, -33.4,
      -31, -28.6, -26.2, -25.4, -23.4, -21,
      -18.6, -16.2, -14.2, -12.2, -10.6, -9,
      -7.8, -6.2, -4.6, -3, -1.4, 0.2,
      1.8, 3.4, 5.4, 7.4, 9, 11,
      13.4, 15.8, 17, 17, 16.2, 15.8,
      15.8, 17.4, 19, 21, 22.6, 24.6,
      25.8, 28.2, 30.6, 32.2, 34.2, 35,
      36.2, 36.2, 36.6, 38.6, 41, 41,
      41, 41, 41, 41, 41, 41,
      41, 41, 41, 41, 41, 41,
      41, 41, 41, 41, 41, 41,
      41, 41, 41, 41, 41, 41,
      41, 41, 41, 41, 41, 41,
      41, 41, 41, 41, 41, 41,
      41},
    p_y = {
      -26, -26, -24.8, -24.4, -22.8, -21.2,
      -20.4, -19.6, -19.6, -19.2, -17.6, -17.6,
      -16.8, -16, -15.2, -14.8, -13.2, -11.6,
      -10.8, -9.2, -7.6, -6, -4.4, -2.8,
      -1.2, 0.4, 1.6, 1.6, 3.2, 4,
      4.4, 4.8, 6.8, 8, 10.4, 11.2,
      11.6, 13.2, 14.8, 16, 16.8, 18.4,
      19.2, 19.6, 19.6, 19.6, 20.8, 21.2,
      23.2, 23.6, 24, 25.2, 26, 26,
      26, 26, 26, 26, 26, 26,
      26, 26, 26, 26, 26, 26,
      26, 26, 26, 26, 26, 26,
      26, 26, 26, 26, 26, 26,
      26, 26, 26, 26, 26, 26,
      26, 26, 26, 26, 26, 26,
      26},
    p_z = {
      1.5, 2.28, 1.9, 1.89, 1.39, 1.46,
      1.7, 2.05, 1.63, 1.38, 1.22, 1.64,
      1.97, 2.02, 1.98, 1.78, 1.94, 2.19,
      2.26, 2.41, 2.47, 2.23, 2.34, 2.21,
      2.47, 2.44, 2.44, 2.26, 1.99, 2.2,
      2.36, 2.26, 2.19, 2.06, 2.15, 2.13,
      2.21, 2.1, 2.02, 2.27, 2.21, 2.1,
      1.6, 1.58, 1.89, 1.99, 2.2, 2.12,
      2, 1.91, 2.09, 1.47, 1.46, 0.68,
      0.68, 0.68, 0.68, 0.68, 0.68, 0.68,
      0.68, 0.68, 0.68, 0.68, 0.68, 0.68,
      0.68, 0.68, 0.68, 0.68, 0.68, 0.68,
      0.68, 0.68, 0.68, 0.68, 0.68, 0.68,
      0.68, 0.68, 0.68, 0.68, 0.68, 0.68,
      0.68, 0.68, 0.68, 0.68, 0.68, 0.68,
      0.68},
    segment_duration = {
      3, 1.53849838082, 1.58406612103, 1.50867581071, 1.47384387899, 1.65441460149,
      1.66270739442, 1.58624535189, 1.171875, 1.67073072212, 1.58624535189, 1.66097304253,
      1.64734126678, 1.40262843849, 1.33423838098, 1.4768173832, 1.48210318201, 1.171875,
      1.47637245709, 1.47365693694, 1.48140235972, 1.47487882127, 1.47556837952, 1.48283225751,
      1.4732685969, 1.51847705595, 1.30734613515, 1.48358954456, 1.40903526736, 1.58747402647,
      1.58539006014, 1.51916077496, 1.171875, 1.6480615397, 1.171875, 1.171875,
      1.47487882127, 1.47405955188, 1.52717501377, 1.171875, 1.66901740552, 1.171875,
      1.58410625666, 1.57548047899, 1.171875, 1.52461948894, 1.171875, 1.52048547677,
      1.171875, 1.171875, 1.57121052956, 1.64703248196, 3, 1,
      1, 1, 1, 1, 1, 1,
      1, 1, 1, 1, 1, 1,
      1, 1, 1, 1, 1, 1,
      1, 1, 1, 1, 1, 1,
      1, 1, 1, 1, 1, 1,
      1, 1, 1, 1, 1, 1});
  PlanningNavigationDisplay navigationDisplay(
    n_segments = 53,
    p_x = {
      -41, -41, -39, -36.6, -35, -33.4,
      -31, -28.6, -26.2, -25.4, -23.4, -21,
      -18.6, -16.2, -14.2, -12.2, -10.6, -9,
      -7.8, -6.2, -4.6, -3, -1.4, 0.2,
      1.8, 3.4, 5.4, 7.4, 9, 11,
      13.4, 15.8, 17, 17, 16.2, 15.8,
      15.8, 17.4, 19, 21, 22.6, 24.6,
      25.8, 28.2, 30.6, 32.2, 34.2, 35,
      36.2, 36.2, 36.6, 38.6, 41, 41,
      41, 41, 41, 41, 41, 41,
      41, 41, 41, 41, 41, 41,
      41, 41, 41, 41, 41, 41,
      41, 41, 41, 41, 41, 41,
      41, 41, 41, 41, 41, 41,
      41, 41, 41, 41, 41, 41,
      41},
    p_y = {
      -26, -26, -24.8, -24.4, -22.8, -21.2,
      -20.4, -19.6, -19.6, -19.2, -17.6, -17.6,
      -16.8, -16, -15.2, -14.8, -13.2, -11.6,
      -10.8, -9.2, -7.6, -6, -4.4, -2.8,
      -1.2, 0.4, 1.6, 1.6, 3.2, 4,
      4.4, 4.8, 6.8, 8, 10.4, 11.2,
      11.6, 13.2, 14.8, 16, 16.8, 18.4,
      19.2, 19.6, 19.6, 19.6, 20.8, 21.2,
      23.2, 23.6, 24, 25.2, 26, 26,
      26, 26, 26, 26, 26, 26,
      26, 26, 26, 26, 26, 26,
      26, 26, 26, 26, 26, 26,
      26, 26, 26, 26, 26, 26,
      26, 26, 26, 26, 26, 26,
      26, 26, 26, 26, 26, 26,
      26},
    p_z = {
      1.5, 2.28, 1.9, 1.89, 1.39, 1.46,
      1.7, 2.05, 1.63, 1.38, 1.22, 1.64,
      1.97, 2.02, 1.98, 1.78, 1.94, 2.19,
      2.26, 2.41, 2.47, 2.23, 2.34, 2.21,
      2.47, 2.44, 2.44, 2.26, 1.99, 2.2,
      2.36, 2.26, 2.19, 2.06, 2.15, 2.13,
      2.21, 2.1, 2.02, 2.27, 2.21, 2.1,
      1.6, 1.58, 1.89, 1.99, 2.2, 2.12,
      2, 1.91, 2.09, 1.47, 1.46, 0.68,
      0.68, 0.68, 0.68, 0.68, 0.68, 0.68,
      0.68, 0.68, 0.68, 0.68, 0.68, 0.68,
      0.68, 0.68, 0.68, 0.68, 0.68, 0.68,
      0.68, 0.68, 0.68, 0.68, 0.68, 0.68,
      0.68, 0.68, 0.68, 0.68, 0.68, 0.68,
      0.68, 0.68, 0.68, 0.68, 0.68, 0.68,
      0.68},
    segment_duration = {
      3, 1.53849838082, 1.58406612103, 1.50867581071, 1.47384387899, 1.65441460149,
      1.66270739442, 1.58624535189, 1.171875, 1.67073072212, 1.58624535189, 1.66097304253,
      1.64734126678, 1.40262843849, 1.33423838098, 1.4768173832, 1.48210318201, 1.171875,
      1.47637245709, 1.47365693694, 1.48140235972, 1.47487882127, 1.47556837952, 1.48283225751,
      1.4732685969, 1.51847705595, 1.30734613515, 1.48358954456, 1.40903526736, 1.58747402647,
      1.58539006014, 1.51916077496, 1.171875, 1.6480615397, 1.171875, 1.171875,
      1.47487882127, 1.47405955188, 1.52717501377, 1.171875, 1.66901740552, 1.171875,
      1.58410625666, 1.57548047899, 1.171875, 1.52461948894, 1.171875, 1.52048547677,
      1.171875, 1.171875, 1.57121052956, 1.64703248196, 3, 1,
      1, 1, 1, 1, 1, 1,
      1, 1, 1, 1, 1, 1,
      1, 1, 1, 1, 1, 1,
      1, 1, 1, 1, 1, 1,
      1, 1, 1, 1, 1, 1,
      1, 1, 1, 1, 1, 1},
    x_min = -45,
    x_max = 45,
    y_min = -30,
    y_max = 30,
    boundary_line_diameter_m = 0.0,
    render_boundary_walls = false,
    boundary_wall_height_m = 0.0,
    boundary_wall_thickness_m = 0.0,
    highlight_local_costmap = true,
    local_costmap_radius_m = 6,
    local_costmap_fade_radius_m = 9,
    local_costmap_front_half_angle_rad = 3.141592653589793,
    local_costmap_update_period_s = 0.05,
    local_costmap_half_cells = 23,
    local_costmap_cell_size_m = 0.4,
    local_sensed_cell_size_m = 0.4,
    local_sensed_half_cells = 23,
    local_plan_horizon_s = 4.0,
    local_plan_point_count = 12,
    local_plan_max_length_m = 3.5,
    terrain_cell_size_m = 3.0,
    terrain_fill_scale = 1.02,
    render_terrain_blocks = false,
    show_static_map_mesh = false,
    terrain_x_offset_m = 0.0,
    terrain_y_offset_m = 0.0,
    terrain_render_stride = 2,
    local_terrain_half_cells = 6,
    show_continuous_ground = false,
    show_static_map_layers = false,
    max_pillars = 1,
    pillar_count = 0,
    pillar_center = {
      {0, 0}},
    pillar_length = {0.16},
    pillar_width = {0.16},
    pillar_height = {3},
    pillar_z_min = {0},
    max_wall_groups = 8,
    wall_group_count = 8,
    wall_arm1_min = {
      {-10.46, -2.61, 0}, {6.53, 9.83, 0}, {-7.99, -21.2, 0},
      {-35.17, -12.99, 0}, {17.57, 8.88, 0}, {31.68, -24.84, 0},
      {-42.84, 17, 0}, {14.16, 20, 0}},
    wall_arm1_max = {
      {-10.14, 15.07, 3.5}, {6.85, 27.51, 3.5}, {9.69, -20.88, 3.5},
      {-17.49, -12.67, 3.5}, {35.25, 9.2, 3.5}, {32, -7.16, 3.5},
      {-25.16, 17.32, 3.5}, {31.84, 20.32, 3.5}},
    wall_arm2_min = {
      {-16.14, -2.77, 0}, {3.53, 9.67, 0}, {-8.15, -26.88, 0},
      {-17.65, -15.99, 0}, {17.41, 3.2, 0}, {28.68, -7.32, 0},
      {-25.32, 17.16, 0}, {14, 17, 0}},
    wall_arm2_max = {
      {-10.3, -2.45, 3.5}, {9.85, 9.99, 3.5}, {-7.83, -21.04, 3.5},
      {-17.33, -9.67, 3.5}, {17.73, 9.04, 3.5}, {35, -7, 3.5},
      {-25, 23, 3.5}, {14.32, 23.32, 3.5}});
  QuadrotorModel.Mechanics.QuadChassis quadChassisTest17_1(
    body(color = {135, 206, 235}, r_0(start = {-41, -26, 1.5}, fixed = {true, true, true})));
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

  annotation(experiment(Algorithm = Dassl, StartTime = 0, StopTime = 80.1247340259, Tolerance = 0.0001, Interval = 0.05));
end Sunray150PlanningOpenBlocksLinearMPCSysblockClosedLoop;
