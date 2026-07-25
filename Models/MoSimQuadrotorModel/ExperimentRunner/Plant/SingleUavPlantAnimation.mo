within MoSimQuadrotorModel.ExperimentRunner.Plant;
model SingleUavPlantAnimation
  "One shared Sunray150 plant used by every offline controller boundary"

  parameter MoSimQuadrotorModel.Parameters.Sunray150VirtualPx4Classic profile;
  parameter Real initial_rotor_speed[4] = {
    profile.mworks_hover_visual_rotor_speed_rad_s,
    -profile.mworks_hover_visual_rotor_speed_rad_s,
    profile.mworks_hover_visual_rotor_speed_rad_s,
    -profile.mworks_hover_visual_rotor_speed_rad_s};
  parameter Real rotor_effectiveness[4] = {1, 1, 1, 1};
  parameter Real lift_coefficient = profile.mworks_visual_thrust_coefficient;
  parameter Real gust_force[3] = {0, 0, 0};
  parameter Real gust_start_s = 15;
  parameter Real gust_duration_s = 4;

  Modelica.Blocks.Interfaces.RealInput rotor_command[4];
  Modelica.Blocks.Interfaces.RealOutput position[3];
  Modelica.Blocks.Interfaces.RealOutput attitude[3];
  Modelica.Blocks.Interfaces.RealOutput rotor_speed[4];

  Sunray150GazeboAlignedVisualChassis aircraft(
    profile = profile,
    gain2(k = lift_coefficient * rotor_effectiveness[1]),
    gain3(k = lift_coefficient * rotor_effectiveness[2]),
    gain4(k = lift_coefficient * rotor_effectiveness[3]),
    gain5(k = lift_coefficient * rotor_effectiveness[4]));
  MoSimQuadrotorModel.Plant.Electricals.Actuator actuator1(dcpm(wMechanical(start = initial_rotor_speed[1])));
  MoSimQuadrotorModel.Plant.Electricals.Actuator actuator2(dcpm(wMechanical(start = initial_rotor_speed[2])));
  MoSimQuadrotorModel.Plant.Electricals.Actuator actuator3(dcpm(wMechanical(start = initial_rotor_speed[3])));
  MoSimQuadrotorModel.Plant.Electricals.Actuator actuator4(dcpm(wMechanical(start = initial_rotor_speed[4])));
  MoSimQuadrotorModel.Plant.Sensors.Sensors sensors;
  Modelica.Mechanics.Rotational.Sensors.SpeedSensor speed_sensor[4];
  Modelica.Mechanics.MultiBody.Forces.WorldForce gust(
    resolveInFrame = Modelica.Mechanics.MultiBody.Types.ResolveInFrameB.world,
    animation = false);

equation
  gust.force[1] = if time >= gust_start_s and time <= gust_start_s + gust_duration_s then gust_force[1] else 0;
  gust.force[2] = if time >= gust_start_s and time <= gust_start_s + gust_duration_s then gust_force[2] else 0;
  gust.force[3] = if time >= gust_start_s and time <= gust_start_s + gust_duration_s then gust_force[3] else 0;

  connect(gust.frame_b, aircraft.body.frame_b);
  connect(actuator1.flange_a, aircraft.flange_a);
  connect(actuator2.flange_a, aircraft.flange_a1);
  connect(actuator3.flange_a, aircraft.flange_a2);
  connect(actuator4.flange_a, aircraft.flange_a3);
  connect(aircraft.frame_a, sensors.frame_a);
  connect(rotor_command[1], actuator1.u);
  connect(rotor_command[2], actuator2.u);
  connect(rotor_command[3], actuator3.u);
  connect(rotor_command[4], actuator4.u);
  connect(actuator1.flange_a, speed_sensor[1].flange);
  connect(actuator2.flange_a, speed_sensor[2].flange);
  connect(actuator3.flange_a, speed_sensor[3].flange);
  connect(actuator4.flange_a, speed_sensor[4].flange);

  position = sensors.PosMea;
  attitude = sensors.AngleMea;
  for i in 1:4 loop
    rotor_speed[i] = speed_sensor[i].w;
  end for;

  annotation(Icon(graphics = {Text(extent = {{-92, 20}, {92, -20}}, textString = "共享整机/动画")}),
    Diagram(coordinateSystem(extent = {{-200, -120}, {200, 120}})));
end SingleUavPlantAnimation;
