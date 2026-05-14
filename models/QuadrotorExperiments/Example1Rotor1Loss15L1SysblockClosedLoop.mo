model Example1Rotor1Loss15L1SysblockClosedLoop
  "Example1 rotor 1 lift efficiency 85% with AWFF L1-inspired residual compensation Sysblock controller"
  QuadrotorModel.PathPlanning.ClimbPath climbePath(gain(k = 1));
  QuadrotorModel.Mechanics.QuadChassis quadChassisTest17_1(gain2(k = 0.0007266293));
  QuadrotorModel.Electricals.Actuator actuator1_1;
  QuadrotorModel.Electricals.Actuator actuator1_2;
  QuadrotorModel.Electricals.Actuator actuator1_3;
  QuadrotorModel.Electricals.Actuator actuator1_4;
  QuadrotorModel.Sensors.Sensors sensors1_1;
  Modelica.Mechanics.Rotational.Sensors.SpeedSensor speedSensor[4];

  Modelica.Blocks.Math.Feedback x_error;
  Modelica.Blocks.Math.Feedback y_error;
  Modelica.Blocks.Math.Feedback z_error;
  Modelica.Blocks.Sources.Constant z_ref_rate(k = 0);
  Modelica.Blocks.Sources.Constant yaw_ref(k = 0);

  AWFF_L1ResidualControllerEquation_Sysblock controller3_2;

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

  connect(actuator1_1.u, controller3_2.y);
  connect(actuator1_2.u, controller3_2.y1);
  connect(actuator1_3.u, controller3_2.y2);
  connect(actuator1_4.u, controller3_2.y3);

  connect(actuator1_1.flange_a, speedSensor[1].flange);
  connect(actuator1_2.flange_a, speedSensor[2].flange);
  connect(actuator1_3.flange_a, speedSensor[3].flange);
  connect(actuator1_4.flange_a, speedSensor[4].flange);

  annotation(experiment(Algorithm = Dassl, StartTime = 0, StopTime = 50, Tolerance = 0.0001, Interval = 0.01));
end Example1Rotor1Loss15L1SysblockClosedLoop;
