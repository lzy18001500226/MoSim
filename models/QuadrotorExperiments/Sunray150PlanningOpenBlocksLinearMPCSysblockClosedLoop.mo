model Sunray150PlanningOpenBlocksLinearMPCSysblockClosedLoop
  "Sunray150 single-UAV A* obstacle-avoidance reference tracked by the LinearMPC-style Sysblock controller"
  parameter Real legacy_hover_motor_speed_cmd = 13.985413115099604
    "Original MWORKS-equivalent hover command before Sunray150 SDF motorConstant calibration";
  parameter Real hover_motor_speed_cmd = 53.562090367172424
    "MWORKS visual rotor hover speed; physical Sunray150 motor speed is 10x by rotorVelocitySlowdownSim";
  parameter Real motor_command_scale = hover_motor_speed_cmd / legacy_hover_motor_speed_cmd
    "Scale legacy controller speed increments to the Sunray150 SDF motorConstant speed domain";

  PlannedQuinticReference planningReference(
    n_segments = 12,
    p_x = {-7.5, -7.5, -4.5, -1.8, -0.9, 0.9, 0.9, 1.5, 4.2, 5.1, 8.7, 10.5, 13.8, 13.8, 13.8, 13.8, 13.8},
    p_y = {-6.75, -6.75, -4.2, -2.4, 0, 3.3, 4.2, 4.8, 4.8, 5.1, 5.1, 4.8, 6.3, 6.3, 6.3, 6.3, 6.3},
    p_z = {0.527900747938, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1},
    segment_duration = {3, 9.61260113409, 7.92235387675, 6.25781524315, 9.17721978965, 2.197265625, 2.07160189801, 6.591796875, 2.31612133313, 8.7890625, 4.45514833762, 8.84988718769, 1, 1, 1, 1});
  PlanningNavigationDisplay navigationDisplay(
    n_segments = 12,
    p_x = {-7.5, -7.5, -4.5, -1.8, -0.9, 0.9, 0.9, 1.5, 4.2, 5.1, 8.7, 10.5, 13.8, 13.8, 13.8, 13.8, 13.8},
    p_y = {-6.75, -6.75, -4.2, -2.4, 0, 3.3, 4.2, 4.8, 4.8, 5.1, 5.1, 4.8, 6.3, 6.3, 6.3, 6.3, 6.3},
    p_z = {0.527900747938, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1},
    segment_duration = {3, 9.61260113409, 7.92235387675, 6.25781524315, 9.17721978965, 2.197265625, 2.07160189801, 6.591796875, 2.31612133313, 8.7890625, 4.45514833762, 8.84988718769, 1, 1, 1, 1},
    x_min = -9.0,
    x_max = 15.0,
    y_min = -7.5,
    y_max = 7.5,
    boundary_line_diameter_m = 0.0,
    boundary_wall_height_m = 0.0,
    boundary_wall_thickness_m = 0.0,
    highlight_local_costmap = true,
    local_costmap_radius_m = 1.25,
    local_costmap_front_half_angle_rad = 0.9599310885968813,
    local_costmap_update_period_s = 0.05,
    local_costmap_half_cells = 15,
    local_costmap_cell_size_m = 0.16,
    local_plan_horizon_s = 4.0,
    local_plan_point_count = 6,
    local_plan_max_length_m = 3.5,
    terrain_cell_size_m = 1.0,
    terrain_fill_scale = 0.92,
    max_pillars = 144,
    pillar_count = 108,
    pillar_center = {
      {1.707, -4.376}, {2.055, -4.376}, {1.881, -4.226},
      {1.653, 3.678}, {2.115, 3.678}, {1.884, 3.877},
      {10.685, 3.883}, {11.119, 3.883}, {10.902, 4.070},
      {1.536, 0.148}, {1.868, 0.148}, {1.702, 0.291},
      {-1.815, 2.814}, {-1.335, 2.814}, {-1.575, 3.021},
      {5.333, -2.088}, {5.655, -2.088}, {5.494, -1.949},
      {-0.178, -0.335}, {0.150, -0.335}, {-0.014, -0.194},
      {9.777, 5.890}, {10.247, 5.890}, {10.012, 6.092},
      {4.009, 0.910}, {4.451, 0.910}, {4.230, 1.100},
      {2.229, -1.173}, {2.673, -1.173}, {2.451, -0.982},
      {11.193, 0.084}, {11.535, 0.084}, {11.364, 0.231},
      {8.947, -6.594}, {9.391, -6.594}, {9.169, -6.403},
      {-7.582, 3.471}, {-7.208, 3.471}, {-7.395, 3.633},
      {0.726, -5.920}, {1.110, -5.920}, {0.918, -5.754},
      {7.149, -1.415}, {7.615, -1.415}, {7.382, -1.215},
      {11.607, -1.273}, {11.929, -1.273}, {11.768, -1.134},
      {-6.754, -1.828}, {-6.308, -1.828}, {-6.531, -1.636},
      {5.633, 6.488}, {6.091, 6.488}, {5.862, 6.686},
      {-6.160, -3.695}, {-5.714, -3.695}, {-5.937, -3.503},
      {4.975, 4.036}, {5.445, 4.036}, {5.210, 4.238},
      {2.274, 1.751}, {2.740, 1.751}, {2.507, 1.951},
      {13.244, -4.303}, {13.588, -4.303}, {13.416, -4.154},
      {8.076, -4.297}, {8.402, -4.297}, {8.239, -4.156},
      {3.286, -6.275}, {3.734, -6.275}, {3.510, -6.082},
      {9.375, -1.347}, {9.751, -1.347}, {9.563, -1.185},
      {-2.852, -4.564}, {-2.388, -4.564}, {-2.620, -4.364},
      {2.259, -2.768}, {2.683, -2.768}, {2.471, -2.586},
      {-6.016, 2.681}, {-5.620, 2.681}, {-5.818, 2.852},
      {5.184, 2.486}, {5.530, 2.486}, {5.357, 2.635},
      {3.906, 5.824}, {4.294, 5.824}, {4.100, 5.991},
      {10.743, -4.697}, {11.229, -4.697}, {10.986, -4.488},
      {6.915, -6.714}, {7.383, -6.714}, {7.149, -6.513},
      {-3.123, 5.929}, {-2.711, 5.929}, {-2.917, 6.107},
      {13.114, 1.016}, {13.466, 1.016}, {13.290, 1.168},
      {13.567, 2.485}, {13.983, 2.485}, {13.775, 2.664},
      {13.036, -2.086}, {13.352, -2.086}, {13.194, -1.950},
      {0.000, 0.000}, {0.000, 0.000}, {0.000, 0.000},
      {0.000, 0.000}, {0.000, 0.000}, {0.000, 0.000},
      {0.000, 0.000}, {0.000, 0.000}, {0.000, 0.000},
      {0.000, 0.000}, {0.000, 0.000}, {0.000, 0.000},
      {0.000, 0.000}, {0.000, 0.000}, {0.000, 0.000},
      {0.000, 0.000}, {0.000, 0.000}, {0.000, 0.000},
      {0.000, 0.000}, {0.000, 0.000}, {0.000, 0.000},
      {0.000, 0.000}, {0.000, 0.000}, {0.000, 0.000},
      {0.000, 0.000}, {0.000, 0.000}, {0.000, 0.000},
      {0.000, 0.000}, {0.000, 0.000}, {0.000, 0.000},
      {0.000, 0.000}, {0.000, 0.000}, {0.000, 0.000},
      {0.000, 0.000}, {0.000, 0.000}, {0.000, 0.000}},
    pillar_width = {
      0.299, 0.299, 0.299, 0.398, 0.398, 0.398, 0.374, 0.374,
      0.374, 0.287, 0.287, 0.287, 0.413, 0.413, 0.413, 0.277,
      0.277, 0.277, 0.282, 0.282, 0.282, 0.405, 0.405, 0.405,
      0.381, 0.381, 0.381, 0.382, 0.382, 0.382, 0.294, 0.294,
      0.294, 0.382, 0.382, 0.382, 0.323, 0.323, 0.323, 0.332,
      0.332, 0.332, 0.401, 0.401, 0.401, 0.277, 0.277, 0.277,
      0.385, 0.385, 0.385, 0.395, 0.395, 0.395, 0.385, 0.385,
      0.385, 0.405, 0.405, 0.405, 0.401, 0.401, 0.401, 0.297,
      0.297, 0.297, 0.281, 0.281, 0.281, 0.387, 0.387, 0.387,
      0.324, 0.324, 0.324, 0.400, 0.400, 0.400, 0.365, 0.365,
      0.365, 0.341, 0.341, 0.341, 0.298, 0.298, 0.298, 0.334,
      0.334, 0.334, 0.419, 0.419, 0.419, 0.403, 0.403, 0.403,
      0.355, 0.355, 0.355, 0.304, 0.304, 0.304, 0.358, 0.358,
      0.358, 0.272, 0.272, 0.272, 0.000, 0.000, 0.000, 0.000,
      0.000, 0.000, 0.000, 0.000, 0.000, 0.000, 0.000, 0.000,
      0.000, 0.000, 0.000, 0.000, 0.000, 0.000, 0.000, 0.000,
      0.000, 0.000, 0.000, 0.000, 0.000, 0.000, 0.000, 0.000,
      0.000, 0.000, 0.000, 0.000, 0.000, 0.000, 0.000, 0.000},
    pillar_height = {
      1.816, 1.816, 1.816, 2.334, 2.334, 2.334, 2.126, 2.126,
      2.126, 1.530, 1.530, 1.530, 1.983, 1.983, 1.983, 1.911,
      1.911, 1.911, 2.384, 2.384, 2.384, 1.657, 1.657, 1.657,
      2.210, 2.210, 2.210, 1.712, 1.712, 1.712, 1.713, 1.713,
      1.713, 2.347, 2.347, 2.347, 2.007, 2.007, 2.007, 1.894,
      1.894, 1.894, 2.353, 2.353, 2.353, 2.284, 2.284, 2.284,
      1.525, 1.525, 1.525, 1.993, 1.993, 1.993, 1.992, 1.992,
      1.992, 1.819, 1.819, 1.819, 1.774, 1.774, 1.774, 2.203,
      2.203, 2.203, 1.693, 1.693, 1.693, 1.637, 1.637, 1.637,
      1.724, 1.724, 1.724, 1.986, 1.986, 1.986, 1.865, 1.865,
      1.865, 1.855, 1.855, 1.855, 2.324, 2.324, 2.324, 2.187,
      2.187, 2.187, 1.814, 1.814, 1.814, 1.983, 1.983, 1.983,
      1.550, 1.550, 1.550, 2.064, 2.064, 2.064, 1.924, 1.924,
      1.924, 1.747, 1.747, 1.747, 1.000, 1.000, 1.000, 1.000,
      1.000, 1.000, 1.000, 1.000, 1.000, 1.000, 1.000, 1.000,
      1.000, 1.000, 1.000, 1.000, 1.000, 1.000, 1.000, 1.000,
      1.000, 1.000, 1.000, 1.000, 1.000, 1.000, 1.000, 1.000,
      1.000, 1.000, 1.000, 1.000, 1.000, 1.000, 1.000, 1.000},
    pillar_z_min = {
      0.000, 0.000, 0.000, 0.000, 0.000, 0.000, 0.000, 0.000,
      0.000, 0.000, 0.000, 0.000, 0.000, 0.000, 0.000, 0.000,
      0.000, 0.000, 0.000, 0.000, 0.000, 0.000, 0.000, 0.000,
      0.000, 0.000, 0.000, 0.000, 0.000, 0.000, 0.000, 0.000,
      0.000, 0.000, 0.000, 0.000, 0.000, 0.000, 0.000, 0.000,
      0.000, 0.000, 0.000, 0.000, 0.000, 0.000, 0.000, 0.000,
      0.000, 0.000, 0.000, 0.000, 0.000, 0.000, 0.000, 0.000,
      0.000, 0.000, 0.000, 0.000, 0.000, 0.000, 0.000, 0.000,
      0.000, 0.000, 0.000, 0.000, 0.000, 0.000, 0.000, 0.000,
      0.000, 0.000, 0.000, 0.000, 0.000, 0.000, 0.000, 0.000,
      0.000, 0.000, 0.000, 0.000, 0.000, 0.000, 0.000, 0.000,
      0.000, 0.000, 0.000, 0.000, 0.000, 0.000, 0.000, 0.000,
      0.000, 0.000, 0.000, 0.000, 0.000, 0.000, 0.000, 0.000,
      0.000, 0.000, 0.000, 0.000, 0.000, 0.000, 0.000, 0.000,
      0.000, 0.000, 0.000, 0.000, 0.000, 0.000, 0.000, 0.000,
      0.000, 0.000, 0.000, 0.000, 0.000, 0.000, 0.000, 0.000,
      0.000, 0.000, 0.000, 0.000, 0.000, 0.000, 0.000, 0.000,
      0.000, 0.000, 0.000, 0.000, 0.000, 0.000, 0.000, 0.000});
  QuadrotorModel.Mechanics.QuadChassis quadChassisTest17_1(
    body(color = {135, 206, 235}, r_0(start = {-7.5, -6.75, 0.5279007479379901}, fixed = {true, true, true})));
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
