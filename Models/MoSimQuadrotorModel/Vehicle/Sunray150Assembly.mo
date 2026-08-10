within MoSimQuadrotorModel.Vehicle;
model Sunray150Assembly
  "Canonical Sunray150 physical assembly shared by every offline Runner"

  parameter MoSimQuadrotorModel.Parameters.Sunray150VirtualPx4Classic profile;
  parameter Real initial_position_m[3](each unit = "m") = {0, 0, 0}
    "World-frame body position at t = 0; defaults preserve every single-aircraft Runner";
  parameter Real initial_rotor_speed[4] = {
    profile.mworks_hover_visual_rotor_speed_rad_s,
    -profile.mworks_hover_visual_rotor_speed_rad_s,
    profile.mworks_hover_visual_rotor_speed_rad_s,
    -profile.mworks_hover_visual_rotor_speed_rad_s};
  parameter Real rotor_effectiveness[4] = {1, 1, 1, 1};
  parameter Real lift_coefficient(unit = "N.s2/rad2") =
    profile.mworks_visual_thrust_coefficient;
  parameter Real reaction_moment_ratio = profile.moment_constant_ratio_m;
  parameter Real yaw_reaction_direction[4] = -profile.mworks_yaw_direction
    "Aerodynamic reaction torque opposes the recorded rotor spin direction";
  parameter Real gust_force[3] = {0, 0, 0};
  parameter Real gust_start_s(unit = "s") = 0;
  parameter Real gust_duration_s(unit = "s") = 0;
  parameter Real mass_scale(min = 0.01) = 1
    "Plant-only body mass scale for parameter-mismatch experiments";
  parameter Real inertia_scale[3](each min = 0.01) = {1, 1, 1}
    "Plant-only diagonal inertia scale for parameter-mismatch experiments";
  parameter Real fault_start_s(unit = "s") = 1e9
    "Scheduled motor-fault start time; default is disabled over formal horizons";
  parameter Integer fault_rotor_index(min = 1, max = 4) = 1;
  parameter Real fault_rotor_effectiveness(min = 0, max = 1) = 1;

  Modelica.Blocks.Interfaces.RealInput rotor_command[4] 
    annotation(Placement(
      transformation(origin = {-220, 70}, extent = {{-10, -10}, {10, 10}}),
      iconTransformation(origin = {-100, 60}, extent = {{-5, -5}, {5, 5}})));
  Modelica.Blocks.Interfaces.RealOutput position[3] 
    annotation(Placement(
      transformation(origin = {220, 85}, extent = {{-10, -10}, {10, 10}}),
      iconTransformation(origin = {100, 80}, extent = {{-5, -5}, {5, 5}})));
  Modelica.Blocks.Interfaces.RealOutput attitude[3] 
    annotation(Placement(
      transformation(origin = {220, 35}, extent = {{-10, -10}, {10, 10}}),
      iconTransformation(origin = {100, 60}, extent = {{-5, -5}, {5, 5}})));
  Modelica.Blocks.Interfaces.RealOutput rotor_speed[4] 
    annotation(Placement(
      transformation(origin = {220, -30}, extent = {{-10, -10}, {10, 10}}),
      iconTransformation(origin = {100, 40}, extent = {{-5, -5}, {5, 5}})));
  Modelica.Blocks.Interfaces.RealOutput VelMea[3](each unit = "m/s") 
    annotation(Placement(
      transformation(origin = {220, -70}, extent = {{-10, -10}, {10, 10}}),
      iconTransformation(origin = {100, 20}, extent = {{-5, -5}, {5, 5}})));
  Modelica.Blocks.Interfaces.RealOutput BodyRateMea[3](each unit = "rad/s") 
    annotation(Placement(
      transformation(origin = {220, -105}, extent = {{-10, -10}, {10, 10}}),
      iconTransformation(origin = {100, 0}, extent = {{-5, -5}, {5, 5}})));
  Modelica.Blocks.Interfaces.RealOutput QuatMea[4] 
    annotation(Placement(
      transformation(origin = {220, -140}, extent = {{-10, -10}, {10, 10}}),
      iconTransformation(origin = {100, -20}, extent = {{-5, -5}, {5, 5}})));

  MoSimQuadrotorModel.Vehicle.Dynamics.PhysicalWrenchAdapter physical(
    profile = profile,
    initial_rotor_speed = initial_rotor_speed,
    lift_coefficient = lift_coefficient,
    reaction_moment_ratio = reaction_moment_ratio,
    yaw_reaction_direction = yaw_reaction_direction,
    thrust_effectiveness = rotor_effectiveness,
    reaction_moment_effectiveness = rotor_effectiveness,
    mass_scale = mass_scale,
    inertia_scale = inertia_scale,
    fault_start_s = fault_start_s,
    fault_rotor_index = fault_rotor_index,
    fault_rotor_effectiveness = fault_rotor_effectiveness,
    body(r_0(start = initial_position_m))) 
    annotation(Placement(transformation(origin = {-55, 10}, extent = {{-65, -65}, {65, 65}})));
  MoSimQuadrotorModel.Vehicle.Sensors.Sensors sensors 
    annotation(Placement(transformation(origin = {105, 55}, extent = {{-42, -30}, {42, 30}})));
  MoSimQuadrotorModel.Vehicle.Sunray150VisualShell visual_shell(profile = profile)
    "Massless body and propeller visuals for native formal-runner animation" 
    annotation(Placement(transformation(origin = {105, -45}, extent = {{-52, -32}, {52, 32}})));
  Modelica.Mechanics.MultiBody.Forces.WorldForce gust(
    resolveInFrame = Modelica.Mechanics.MultiBody.Types.ResolveInFrameB.world,
    animation = false) 
    annotation(Placement(transformation(origin = {-155, 100}, extent = {{-25, -18}, {25, 18}})));
  Modelica.Blocks.Interfaces.RealOutput rotor_thrust[4](each unit = "N") 
    annotation(Placement(
      transformation(origin = {220, 120}, extent = {{-10, -10}, {10, 10}}),
      iconTransformation(origin = {100, -40}, extent = {{-5, -5}, {5, 5}})));
  Modelica.Blocks.Interfaces.RealOutput rotor_yaw_reaction_moment[4](each unit = "N.m") 
    annotation(Placement(
      transformation(origin = {220, 60}, extent = {{-10, -10}, {10, 10}}),
      iconTransformation(origin = {100, -60}, extent = {{-5, -5}, {5, 5}})));
  Modelica.Blocks.Interfaces.RealOutput applied_reaction_yaw_moment(unit = "N.m") 
    annotation(Placement(
      transformation(origin = {220, 0}, extent = {{-10, -10}, {10, 10}}),
      iconTransformation(origin = {100, -80}, extent = {{-5, -5}, {5, 5}})));

equation
  gust.force[1] = if time >= gust_start_s and time <= gust_start_s + gust_duration_s then gust_force[1] else 0;
  gust.force[2] = if time >= gust_start_s and time <= gust_start_s + gust_duration_s then gust_force[2] else 0;
  gust.force[3] = if time >= gust_start_s and time <= gust_start_s + gust_duration_s then gust_force[3] else 0;

  connect(gust.frame_b, physical.body.frame_a) 
    annotation(Line(points = {{-130, 100}, {-100, 100}, {-100, 10}}, color = {95, 95, 95}, thickness = 0.5));
  connect(physical.body.frame_a, sensors.frame_a) 
    annotation(Line(points = {{10, 10}, {60, 10}, {60, 55}}, color = {95, 95, 95}, thickness = 0.5));
  connect(physical.body.frame_a, visual_shell.frame_a) 
    annotation(Line(points = {{10, 10}, {55, 10}, {55, -45}}, color = {95, 95, 95}, thickness = 0.5));
  connect(rotor_speed, visual_shell.rotor_speed) 
    annotation(Line(points = {{220, -30}, {170, -30}, {170, -65}, {157, -65}}, color = {0, 0, 127}));

  for i in 1:4 loop
    physical.wrapper.motor_command[i] = rotor_command[i];
    rotor_speed[i] = physical.wrapper.dynamics.omega[i];
    rotor_thrust[i] = physical.wrapper.dynamics.thrust[i];
    rotor_yaw_reaction_moment[i] = physical.wrapper.dynamics.yaw_reaction_moment[i];
  end for;
  applied_reaction_yaw_moment = physical.applied_yaw_torque_body;

  position = sensors.PosMea;
  attitude = sensors.AngleMea;
  VelMea = sensors.VelMea;
  BodyRateMea = sensors.BodyRateMea;
  QuatMea = sensors.QuatMea;

  annotation(
    Icon(coordinateSystem(extent = {{-100, -100}, {100, 100}}), graphics = {
      Rectangle(extent = {{-100, 100}, {100, -100}}, lineColor = {160, 80, 0},
        fillColor = {255, 250, 240}, fillPattern = FillPattern.Solid),
      Bitmap(origin = {0, 18}, extent = {{-75, -61.6}, {75, 61.6}},
        fileName = "modelica://MoSimQuadrotorModel/Vehicle/Resources/Images/Sunray150-Side.png"),
      Text(origin = {0, -76}, extent = {{-92, 14}, {92, -14}},
        textString = "Sunray150", textColor = {160, 80, 0})}),
    Diagram(coordinateSystem(extent = {{-240, -150}, {240, 145}}, grid = {2, 2})),
    __MWORKS(version="26.3.0"));
end Sunray150Assembly;