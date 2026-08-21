within MoSimQuadrotorModel.Guidance.Trajectories;
partial model PartialTrajectory
  "Common position, velocity, and acceleration reference interface"

  Modelica.Blocks.Interfaces.RealOutput position_command[3]
    "Reference position command [x, y, z] in m" 
    annotation(Placement(
      transformation(origin = {100, 60}, extent = {{-8, -8}, {8, 8}}),
      iconTransformation(origin = {100, 60}, extent = {{-8, -8}, {8, 8}})));
  Modelica.Blocks.Interfaces.RealOutput velocity_command[3]
    "Reference translational velocity [x, y, z] in m/s" 
    annotation(Placement(visible = false,
      transformation(origin = {100, 0}, extent = {{-8, -8}, {8, 8}}),
      iconTransformation(origin = {100, 0}, extent = {{-8, -8}, {8, 8}})));
  Modelica.Blocks.Interfaces.RealOutput acceleration_command[3]
    "Reference translational acceleration [x, y, z] in m/s2" 
    annotation(Placement(visible = false,
      transformation(origin = {100, -60}, extent = {{-8, -8}, {8, 8}}),
      iconTransformation(origin = {100, -60}, extent = {{-8, -8}, {8, 8}})));
  Modelica.Blocks.Interfaces.RealOutput direct_control_bus[6]
    "[velocity(1:3), acceleration(4:6)] for the top-level direct telemetry tap" 
    annotation(Placement(
      transformation(origin = {100, -75}, extent = {{-8, -8}, {8, 8}}),
      iconTransformation(origin = {100, -75}, extent = {{-8, -8}, {8, 8}})));
  Modelica.Blocks.Routing.Multiplex2 direct_control_multiplex(n1 = 3, n2 = 3) 
    annotation(Placement(
      transformation(origin = {25, -72}, extent = {{-12, -12}, {12, 12}})));

equation
  connect(velocity_command, direct_control_multiplex.u1) 
    annotation(Line(points = {{100, 0}, {65, 0}, {65, -65}, {39, -65}},
      color = {0, 0, 127}));
  connect(acceleration_command, direct_control_multiplex.u2) 
    annotation(Line(points = {{100, -60}, {65, -60}, {65, -79}, {39, -79}},
      color = {0, 0, 127}));
  connect(direct_control_multiplex.y, direct_control_bus) 
    annotation(Line(points = {{37, -72}, {100, -72}, {100, -75}},
      color = {0, 0, 127}));

  annotation(
    Icon(coordinateSystem(extent = {{-100, -100}, {100, 100}}), graphics = {
      Rectangle(extent = {{-100, 100}, {100, -100}}, lineColor = {0, 75, 135},
        fillColor = {240, 249, 255}, fillPattern = FillPattern.Solid),
      Text(origin = {0, 24}, extent = {{-82, 18}, {82, -18}},
        textString = "Trajectory", textColor = {0, 75, 135}),
      Text(origin = {0, -28}, extent = {{-82, 18}, {82, -18}},
        textString = "reference", textColor = {0, 75, 135})}),
    Diagram(coordinateSystem(extent = {{-120, -100}, {120, 100}}, grid = {2, 2})),
    __MWORKS(version = "26.3.0"));
end PartialTrajectory;