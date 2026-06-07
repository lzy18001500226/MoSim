within QuadrotorExperiments.OfficialScenarios;
model Example3LinearMPCSysblockClosedLoop
  "Example3 plant with linear MPC-style outer-loop Sysblock controller"
  parameter Real legacy_hover_motor_speed_cmd = 13.985413115099604
    "Original MWORKS-equivalent hover command before Sunray150 SDF motorConstant calibration";
  parameter Real hover_motor_speed_cmd = 53.562090367172424
    "MWORKS visual rotor hover speed; physical Sunray150 motor speed is 10x by rotorVelocitySlowdownSim";
  parameter Real motor_command_scale = hover_motor_speed_cmd / legacy_hover_motor_speed_cmd
    "Scale legacy controller speed increments to the Sunray150 SDF motorConstant speed domain";
  QuadrotorModel.PathPlanning.EightPath climbePath;
  QuadrotorModel.Mechanics.QuadChassis quadChassisTest17_1;
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
  Modelica.Blocks.Sources.Constant z_ref_rate(k = 0);
  Modelica.Blocks.Sources.Constant yaw_ref(k = 0);

  AWFF_LinearMPCOuterLoopControllerEquation_Sysblock controller3_2(
    mpc_acc_limit_xy = 2.7,
    mpc_terminal_gain_xy = 0.12);

equation
  connect(actuator1_1.flange_a, quadChassisTest17_1.flange_a);
  connect(actuator1_2.flange_a, quadChassisTest17_1.flange_a1);
  connect(actuator1_3.flange_a, quadChassisTest17_1.flange_a2);
  connect(actuator1_4.flange_a, quadChassisTest17_1.flange_a3);
  connect(quadChassisTest17_1.frame_a, sensors1_1.frame_a);

  connect(climbePath.position_command[1], x_error.u1);
  connect(sensors1_1.PosMea[1], x_error.u2);
  connect(climbePath.position_command[2], y_error.u1);
  connect(sensors1_1.PosMea[2], y_error.u2);
  connect(climbePath.position_command[3], z_error.u1);
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

  annotation(experiment(Algorithm = Dassl, StartTime = 0, StopTime = 120, Tolerance = 0.0001, Interval = 0.01));
  annotation(__MWORKS(hide=true));
end Example3LinearMPCSysblockClosedLoop;
