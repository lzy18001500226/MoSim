model Example1QPNMPCSafetyReturnLandSysblockClosedLoop
  "Example1 plant with QP/NMPC safety controller and return/landing mission reference"
  parameter Real return_trigger_time_s = 20.0;
  parameter Real land_trigger_time_s = 38.0;
  parameter Real return_altitude_m = 1.0;
  parameter Real landing_altitude_m = 0.15;
  parameter Real descent_rate_mps = 0.8;

  QuadrotorModel.PathPlanning.ClimbPath climbePath(gain(k = 1));
  QuadrotorModel.Mechanics.QuadChassis quadChassisTest17_1;
  QuadrotorModel.Electricals.Actuator actuator1_1;
  QuadrotorModel.Electricals.Actuator actuator1_2;
  QuadrotorModel.Electricals.Actuator actuator1_3;
  QuadrotorModel.Electricals.Actuator actuator1_4;
  QuadrotorModel.Sensors.Sensors sensors1_1;
  Modelica.Mechanics.Rotational.Sensors.SpeedSensor speedSensor[4];

  Modelica.Blocks.Sources.RealExpression mission_ref_x(y = if time >= return_trigger_time_s then 0 else climbePath.position_command[1]);
  Modelica.Blocks.Sources.RealExpression mission_ref_y(y = if time >= return_trigger_time_s then 0 else climbePath.position_command[2]);
  Modelica.Blocks.Sources.RealExpression mission_ref_z(y = if time >= land_trigger_time_s then max(landing_altitude_m, climbePath.position_command[3] - descent_rate_mps * (time - return_trigger_time_s)) else if time >= return_trigger_time_s then max(return_altitude_m, climbePath.position_command[3] - descent_rate_mps * (time - return_trigger_time_s)) else climbePath.position_command[3]);
  Modelica.Blocks.Sources.RealExpression mission_ref_z_rate(y = if time >= return_trigger_time_s and climbePath.position_command[3] - descent_rate_mps * (time - return_trigger_time_s) > landing_altitude_m then -descent_rate_mps else 0);
  Modelica.Blocks.Math.Feedback x_error;
  Modelica.Blocks.Math.Feedback y_error;
  Modelica.Blocks.Math.Feedback z_error;
  Modelica.Blocks.Sources.Constant yaw_ref(k = 0);

  AWFF_QPNMPCSafetyController_Sysblock controller3_2(
    return_trigger_time_s = return_trigger_time_s,
    land_trigger_time_s = land_trigger_time_s,
    landing_altitude_m = landing_altitude_m);

equation
  connect(actuator1_1.flange_a, quadChassisTest17_1.flange_a);
  connect(actuator1_2.flange_a, quadChassisTest17_1.flange_a1);
  connect(actuator1_3.flange_a, quadChassisTest17_1.flange_a2);
  connect(actuator1_4.flange_a, quadChassisTest17_1.flange_a3);
  connect(quadChassisTest17_1.frame_a, sensors1_1.frame_a);

  connect(mission_ref_x.y, x_error.u1);
  connect(sensors1_1.PosMea[1], x_error.u2);
  connect(mission_ref_y.y, y_error.u1);
  connect(sensors1_1.PosMea[2], y_error.u2);
  connect(mission_ref_z.y, z_error.u1);
  connect(sensors1_1.PosMea[3], z_error.u2);

  connect(x_error.y, controller3_2.x_error);
  connect(y_error.y, controller3_2.y_error);
  connect(z_error.y, controller3_2.z_error);
  connect(mission_ref_z_rate.y, controller3_2.z_ref_rate);
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
end Example1QPNMPCSafetyReturnLandSysblockClosedLoop;
