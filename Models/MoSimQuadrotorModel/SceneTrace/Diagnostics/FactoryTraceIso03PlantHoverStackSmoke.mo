within MoSimQuadrotorModel.SceneTrace.Diagnostics;
model FactoryTraceIso03PlantHoverStackSmoke
  "Incremental trace isolation 03: Iso01 plus open-loop hover plant, actuators, sensors, and speed sensors"
  extends FactoryTraceIso01FullDisplaySmoke;

  parameter Real hover_motor_speed_cmd = MoSimQuadrotorModel.Parameters.sunray150_virtual_px4_classic_hover_visual_rotor_speed_rad_s
    "MWORKS visual rotor hover speed; copied from project-owned Factory smoke wrapper without changing parameters";

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

equation
  connect(actuator1_1.flange_a, quadChassisTest17_1.flange_a);
  connect(actuator1_2.flange_a, quadChassisTest17_1.flange_a1);
  connect(actuator1_3.flange_a, quadChassisTest17_1.flange_a2);
  connect(actuator1_4.flange_a, quadChassisTest17_1.flange_a3);
  connect(quadChassisTest17_1.frame_a, sensors1_1.frame_a);

  connect(hover_u1.y, actuator1_1.u);
  connect(hover_u2.y, actuator1_2.u);
  connect(hover_u3.y, actuator1_3.u);
  connect(hover_u4.y, actuator1_4.u);

  connect(actuator1_1.flange_a, speedSensor[1].flange);
  connect(actuator1_2.flange_a, speedSensor[2].flange);
  connect(actuator1_3.flange_a, speedSensor[3].flange);
  connect(actuator1_4.flange_a, speedSensor[4].flange);
  annotation(__MWORKS(hide=true,version="26.3.0"));
end FactoryTraceIso03PlantHoverStackSmoke;