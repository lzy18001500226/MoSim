model FormationTriangleFigure8LinearMPCSysblockClosedLoop
  "Three-UAV leader-follower triangle formation tracking a planar figure-8 with LinearMPC-style Sysblock controllers"
  parameter Real mission_altitude_m = 1.0;
  parameter Real x_scale_m = 2.5;
  parameter Real y_scale_m = 2.5;
  parameter Real omega_x = 0.02;
  parameter Real omega_y = 0.04;
  parameter Real x_phase_offset = 1 / 360;
  parameter Real follower1_offset_x = -1.0;
  parameter Real follower1_offset_y = -0.8;
  parameter Real follower2_offset_x = -1.0;
  parameter Real follower2_offset_y = 0.8;
  parameter Real legacy_hover_motor_speed_cmd = 13.985413115099604
    "Original MWORKS-equivalent hover command before Sunray150 SDF motorConstant calibration";
  parameter Real hover_motor_speed_cmd = 53.562090367172424
    "MWORKS visual rotor hover speed; physical Sunray150 motor speed is 10x by rotorVelocitySlowdownSim";
  parameter Real motor_command_scale = hover_motor_speed_cmd / legacy_hover_motor_speed_cmd
    "Scale legacy controller speed increments to the Sunray150 SDF motorConstant speed domain";

  Real leader_x_ref;
  Real leader_y_ref;
  Real leader_z_ref;
  Real follower1_x_ref;
  Real follower1_y_ref;
  Real follower1_z_ref;
  Real follower2_x_ref;
  Real follower2_y_ref;
  Real follower2_z_ref;
  Real follower1_x;
  Real follower1_y;
  Real follower1_z;
  Real follower2_x;
  Real follower2_y;
  Real follower2_z;
  Real follower1_formation_error_m;
  Real follower2_formation_error_m;
  Real formation_error_m;
  Real inter_uav_distance_01_m;
  Real inter_uav_distance_02_m;
  Real inter_uav_distance_12_m;
  Real min_inter_uav_distance_m;

  QuadrotorModel.Mechanics.QuadChassis quadChassisTest17_1(
    body(r_0(start = {x_scale_m * sin(x_phase_offset * Modelica.Constants.pi), 0, mission_altitude_m}, fixed = {true, true, true})));
  QuadrotorModel.Mechanics.QuadChassis quadChassisFollower1(
    body(r_0(start = {x_scale_m * sin(x_phase_offset * Modelica.Constants.pi) + follower1_offset_x, follower1_offset_y, mission_altitude_m}, fixed = {true, true, true})));
  QuadrotorModel.Mechanics.QuadChassis quadChassisFollower2(
    body(r_0(start = {x_scale_m * sin(x_phase_offset * Modelica.Constants.pi) + follower2_offset_x, follower2_offset_y, mission_altitude_m}, fixed = {true, true, true})));

  QuadrotorModel.Electricals.Actuator actuator1_1(dcpm(wMechanical(start = hover_motor_speed_cmd)));
  QuadrotorModel.Electricals.Actuator actuator1_2(dcpm(wMechanical(start = -hover_motor_speed_cmd)));
  QuadrotorModel.Electricals.Actuator actuator1_3(dcpm(wMechanical(start = hover_motor_speed_cmd)));
  QuadrotorModel.Electricals.Actuator actuator1_4(dcpm(wMechanical(start = -hover_motor_speed_cmd)));
  QuadrotorModel.Electricals.Actuator follower1Actuator1(dcpm(wMechanical(start = hover_motor_speed_cmd)));
  QuadrotorModel.Electricals.Actuator follower1Actuator2(dcpm(wMechanical(start = -hover_motor_speed_cmd)));
  QuadrotorModel.Electricals.Actuator follower1Actuator3(dcpm(wMechanical(start = hover_motor_speed_cmd)));
  QuadrotorModel.Electricals.Actuator follower1Actuator4(dcpm(wMechanical(start = -hover_motor_speed_cmd)));
  QuadrotorModel.Electricals.Actuator follower2Actuator1(dcpm(wMechanical(start = hover_motor_speed_cmd)));
  QuadrotorModel.Electricals.Actuator follower2Actuator2(dcpm(wMechanical(start = -hover_motor_speed_cmd)));
  QuadrotorModel.Electricals.Actuator follower2Actuator3(dcpm(wMechanical(start = hover_motor_speed_cmd)));
  QuadrotorModel.Electricals.Actuator follower2Actuator4(dcpm(wMechanical(start = -hover_motor_speed_cmd)));

  QuadrotorModel.Sensors.Sensors sensors1_1;
  QuadrotorModel.Sensors.Sensors follower1Sensors;
  QuadrotorModel.Sensors.Sensors follower2Sensors;

  Modelica.Blocks.Sources.RealExpression leader_x_ref_src(y = leader_x_ref);
  Modelica.Blocks.Sources.RealExpression leader_y_ref_src(y = leader_y_ref);
  Modelica.Blocks.Sources.RealExpression leader_z_ref_src(y = leader_z_ref);
  Modelica.Blocks.Sources.RealExpression follower1_x_ref_src(y = follower1_x_ref);
  Modelica.Blocks.Sources.RealExpression follower1_y_ref_src(y = follower1_y_ref);
  Modelica.Blocks.Sources.RealExpression follower1_z_ref_src(y = follower1_z_ref);
  Modelica.Blocks.Sources.RealExpression follower2_x_ref_src(y = follower2_x_ref);
  Modelica.Blocks.Sources.RealExpression follower2_y_ref_src(y = follower2_y_ref);
  Modelica.Blocks.Sources.RealExpression follower2_z_ref_src(y = follower2_z_ref);

  Modelica.Blocks.Sources.Constant z_ref_rate(k = 0);
  Modelica.Blocks.Sources.Constant yaw_ref(k = 0);
  Modelica.Blocks.Math.Feedback x_error;
  Modelica.Blocks.Math.Feedback y_error;
  Modelica.Blocks.Math.Feedback z_error;
  Modelica.Blocks.Math.Feedback follower1_x_error;
  Modelica.Blocks.Math.Feedback follower1_y_error;
  Modelica.Blocks.Math.Feedback follower1_z_error;
  Modelica.Blocks.Math.Feedback follower2_x_error;
  Modelica.Blocks.Math.Feedback follower2_y_error;
  Modelica.Blocks.Math.Feedback follower2_z_error;

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

  Modelica.Blocks.Math.Add follower1_motor1_hover_sum;
  Modelica.Blocks.Math.Add follower1_motor2_hover_sum;
  Modelica.Blocks.Math.Add follower1_motor3_hover_sum;
  Modelica.Blocks.Math.Add follower1_motor4_hover_sum;
  Modelica.Blocks.Math.Gain follower1_motor1_delta_scale(k = motor_command_scale);
  Modelica.Blocks.Math.Gain follower1_motor2_delta_scale(k = motor_command_scale);
  Modelica.Blocks.Math.Gain follower1_motor3_delta_scale(k = motor_command_scale);
  Modelica.Blocks.Math.Gain follower1_motor4_delta_scale(k = motor_command_scale);

  Modelica.Blocks.Math.Add follower2_motor1_hover_sum;
  Modelica.Blocks.Math.Add follower2_motor2_hover_sum;
  Modelica.Blocks.Math.Add follower2_motor3_hover_sum;
  Modelica.Blocks.Math.Add follower2_motor4_hover_sum;
  Modelica.Blocks.Math.Gain follower2_motor1_delta_scale(k = motor_command_scale);
  Modelica.Blocks.Math.Gain follower2_motor2_delta_scale(k = motor_command_scale);
  Modelica.Blocks.Math.Gain follower2_motor3_delta_scale(k = motor_command_scale);
  Modelica.Blocks.Math.Gain follower2_motor4_delta_scale(k = motor_command_scale);

  AWFF_LinearMPCOuterLoopControllerEquation_Sysblock controller3_2(
    mpc_acc_limit_xy = 2.7,
    mpc_terminal_gain_xy = 0.12);
  AWFF_LinearMPCOuterLoopControllerEquation_Sysblock follower1Controller(
    mpc_acc_limit_xy = 2.7,
    mpc_terminal_gain_xy = 0.12);
  AWFF_LinearMPCOuterLoopControllerEquation_Sysblock follower2Controller(
    mpc_acc_limit_xy = 2.7,
    mpc_terminal_gain_xy = 0.12);

equation
  leader_x_ref = x_scale_m * sin((omega_x * time + x_phase_offset) * Modelica.Constants.pi);
  leader_y_ref = y_scale_m * sin(omega_y * time * Modelica.Constants.pi);
  leader_z_ref = mission_altitude_m;
  follower1_x_ref = leader_x_ref + follower1_offset_x;
  follower1_y_ref = leader_y_ref + follower1_offset_y;
  follower1_z_ref = leader_z_ref;
  follower2_x_ref = leader_x_ref + follower2_offset_x;
  follower2_y_ref = leader_y_ref + follower2_offset_y;
  follower2_z_ref = leader_z_ref;
  follower1_x = follower1Sensors.PosMea[1];
  follower1_y = follower1Sensors.PosMea[2];
  follower1_z = follower1Sensors.PosMea[3];
  follower2_x = follower2Sensors.PosMea[1];
  follower2_y = follower2Sensors.PosMea[2];
  follower2_z = follower2Sensors.PosMea[3];

  follower1_formation_error_m = sqrt((follower1_x - sensors1_1.PosMea[1] - follower1_offset_x) ^ 2 + (follower1_y - sensors1_1.PosMea[2] - follower1_offset_y) ^ 2 + (follower1_z - sensors1_1.PosMea[3]) ^ 2);
  follower2_formation_error_m = sqrt((follower2_x - sensors1_1.PosMea[1] - follower2_offset_x) ^ 2 + (follower2_y - sensors1_1.PosMea[2] - follower2_offset_y) ^ 2 + (follower2_z - sensors1_1.PosMea[3]) ^ 2);
  formation_error_m = 0.5 * (follower1_formation_error_m + follower2_formation_error_m);
  inter_uav_distance_01_m = sqrt((follower1_x - sensors1_1.PosMea[1]) ^ 2 + (follower1_y - sensors1_1.PosMea[2]) ^ 2 + (follower1_z - sensors1_1.PosMea[3]) ^ 2);
  inter_uav_distance_02_m = sqrt((follower2_x - sensors1_1.PosMea[1]) ^ 2 + (follower2_y - sensors1_1.PosMea[2]) ^ 2 + (follower2_z - sensors1_1.PosMea[3]) ^ 2);
  inter_uav_distance_12_m = sqrt((follower2_x - follower1_x) ^ 2 + (follower2_y - follower1_y) ^ 2 + (follower2_z - follower1_z) ^ 2);
  min_inter_uav_distance_m = min(inter_uav_distance_01_m, min(inter_uav_distance_02_m, inter_uav_distance_12_m));

  connect(actuator1_1.flange_a, quadChassisTest17_1.flange_a);
  connect(actuator1_2.flange_a, quadChassisTest17_1.flange_a1);
  connect(actuator1_3.flange_a, quadChassisTest17_1.flange_a2);
  connect(actuator1_4.flange_a, quadChassisTest17_1.flange_a3);
  connect(quadChassisTest17_1.frame_a, sensors1_1.frame_a);
  connect(follower1Actuator1.flange_a, quadChassisFollower1.flange_a);
  connect(follower1Actuator2.flange_a, quadChassisFollower1.flange_a1);
  connect(follower1Actuator3.flange_a, quadChassisFollower1.flange_a2);
  connect(follower1Actuator4.flange_a, quadChassisFollower1.flange_a3);
  connect(quadChassisFollower1.frame_a, follower1Sensors.frame_a);
  connect(follower2Actuator1.flange_a, quadChassisFollower2.flange_a);
  connect(follower2Actuator2.flange_a, quadChassisFollower2.flange_a1);
  connect(follower2Actuator3.flange_a, quadChassisFollower2.flange_a2);
  connect(follower2Actuator4.flange_a, quadChassisFollower2.flange_a3);
  connect(quadChassisFollower2.frame_a, follower2Sensors.frame_a);

  connect(leader_x_ref_src.y, x_error.u1);
  connect(sensors1_1.PosMea[1], x_error.u2);
  connect(leader_y_ref_src.y, y_error.u1);
  connect(sensors1_1.PosMea[2], y_error.u2);
  connect(leader_z_ref_src.y, z_error.u1);
  connect(sensors1_1.PosMea[3], z_error.u2);
  connect(x_error.y, controller3_2.x_error);
  connect(y_error.y, controller3_2.y_error);
  connect(z_error.y, controller3_2.z_error);
  connect(z_ref_rate.y, controller3_2.z_ref_rate);
  connect(sensors1_1.AngleMea[1], controller3_2.roll_mea);
  connect(sensors1_1.AngleMea[2], controller3_2.pitch_mea);
  connect(sensors1_1.AngleMea[3], controller3_2.yaw_mea);
  connect(yaw_ref.y, controller3_2.yaw_ref);

  connect(follower1_x_ref_src.y, follower1_x_error.u1);
  connect(follower1Sensors.PosMea[1], follower1_x_error.u2);
  connect(follower1_y_ref_src.y, follower1_y_error.u1);
  connect(follower1Sensors.PosMea[2], follower1_y_error.u2);
  connect(follower1_z_ref_src.y, follower1_z_error.u1);
  connect(follower1Sensors.PosMea[3], follower1_z_error.u2);
  connect(follower1_x_error.y, follower1Controller.x_error);
  connect(follower1_y_error.y, follower1Controller.y_error);
  connect(follower1_z_error.y, follower1Controller.z_error);
  connect(z_ref_rate.y, follower1Controller.z_ref_rate);
  connect(follower1Sensors.AngleMea[1], follower1Controller.roll_mea);
  connect(follower1Sensors.AngleMea[2], follower1Controller.pitch_mea);
  connect(follower1Sensors.AngleMea[3], follower1Controller.yaw_mea);
  connect(yaw_ref.y, follower1Controller.yaw_ref);

  connect(follower2_x_ref_src.y, follower2_x_error.u1);
  connect(follower2Sensors.PosMea[1], follower2_x_error.u2);
  connect(follower2_y_ref_src.y, follower2_y_error.u1);
  connect(follower2Sensors.PosMea[2], follower2_y_error.u2);
  connect(follower2_z_ref_src.y, follower2_z_error.u1);
  connect(follower2Sensors.PosMea[3], follower2_z_error.u2);
  connect(follower2_x_error.y, follower2Controller.x_error);
  connect(follower2_y_error.y, follower2Controller.y_error);
  connect(follower2_z_error.y, follower2Controller.z_error);
  connect(z_ref_rate.y, follower2Controller.z_ref_rate);
  connect(follower2Sensors.AngleMea[1], follower2Controller.roll_mea);
  connect(follower2Sensors.AngleMea[2], follower2Controller.pitch_mea);
  connect(follower2Sensors.AngleMea[3], follower2Controller.yaw_mea);
  connect(yaw_ref.y, follower2Controller.yaw_ref);

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

  connect(follower1Controller.y, follower1_motor1_delta_scale.u);
  connect(follower1_motor1_delta_scale.y, follower1_motor1_hover_sum.u1);
  connect(hover_u1.y, follower1_motor1_hover_sum.u2);
  connect(follower1_motor1_hover_sum.y, follower1Actuator1.u);
  connect(follower1Controller.y1, follower1_motor2_delta_scale.u);
  connect(follower1_motor2_delta_scale.y, follower1_motor2_hover_sum.u1);
  connect(hover_u2.y, follower1_motor2_hover_sum.u2);
  connect(follower1_motor2_hover_sum.y, follower1Actuator2.u);
  connect(follower1Controller.y2, follower1_motor3_delta_scale.u);
  connect(follower1_motor3_delta_scale.y, follower1_motor3_hover_sum.u1);
  connect(hover_u3.y, follower1_motor3_hover_sum.u2);
  connect(follower1_motor3_hover_sum.y, follower1Actuator3.u);
  connect(follower1Controller.y3, follower1_motor4_delta_scale.u);
  connect(follower1_motor4_delta_scale.y, follower1_motor4_hover_sum.u1);
  connect(hover_u4.y, follower1_motor4_hover_sum.u2);
  connect(follower1_motor4_hover_sum.y, follower1Actuator4.u);

  connect(follower2Controller.y, follower2_motor1_delta_scale.u);
  connect(follower2_motor1_delta_scale.y, follower2_motor1_hover_sum.u1);
  connect(hover_u1.y, follower2_motor1_hover_sum.u2);
  connect(follower2_motor1_hover_sum.y, follower2Actuator1.u);
  connect(follower2Controller.y1, follower2_motor2_delta_scale.u);
  connect(follower2_motor2_delta_scale.y, follower2_motor2_hover_sum.u1);
  connect(hover_u2.y, follower2_motor2_hover_sum.u2);
  connect(follower2_motor2_hover_sum.y, follower2Actuator2.u);
  connect(follower2Controller.y2, follower2_motor3_delta_scale.u);
  connect(follower2_motor3_delta_scale.y, follower2_motor3_hover_sum.u1);
  connect(hover_u3.y, follower2_motor3_hover_sum.u2);
  connect(follower2_motor3_hover_sum.y, follower2Actuator3.u);
  connect(follower2Controller.y3, follower2_motor4_delta_scale.u);
  connect(follower2_motor4_delta_scale.y, follower2_motor4_hover_sum.u1);
  connect(hover_u4.y, follower2_motor4_hover_sum.u2);
  connect(follower2_motor4_hover_sum.y, follower2Actuator4.u);

  annotation(experiment(Algorithm = Dassl, StartTime = 0, StopTime = 80, Tolerance = 0.0001, Interval = 0.02));
end FormationTriangleFigure8LinearMPCSysblockClosedLoop;
