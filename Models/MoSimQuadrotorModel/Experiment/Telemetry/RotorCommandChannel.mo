within MoSimQuadrotorModel.Experiment.Telemetry;
block RotorCommandChannel
  "One physical rotor command/speed telemetry channel without duplicate dynamics"

  parameter Integer channel_index(min = 1, max = 4) = 1;
  Modelica.Blocks.Interfaces.RealInput command(unit = "rad/s")
    "Command after the ESC nominal path" 
    annotation(Placement(
      transformation(origin = {-110, 35}, extent = {{-8, -8}, {8, 8}}),
      iconTransformation(origin = {-100, 35}, extent = {{-8, -8}, {8, 8}})));
  Modelica.Blocks.Interfaces.RealInput speed(unit = "rad/s")
    "Measured signed rotor speed from Sunray150Assembly" 
    annotation(Placement(
      transformation(origin = {-110, -35}, extent = {{-8, -8}, {8, 8}}),
      iconTransformation(origin = {-100, -35}, extent = {{-8, -8}, {8, 8}})));
  Modelica.Blocks.Interfaces.RealOutput command_to_plant(unit = "rad/s")
    "Command forwarded to the shared physical plant" 
    annotation(Placement(
      transformation(origin = {110, 35}, extent = {{-8, -8}, {8, 8}}),
      iconTransformation(origin = {100, 35}, extent = {{-8, -8}, {8, 8}})));
  Modelica.Blocks.Interfaces.RealOutput speed_telemetry(unit = "rad/s")
    "Speed telemetry forwarded for result inspection" 
    annotation(Placement(
      transformation(origin = {110, -35}, extent = {{-8, -8}, {8, 8}}),
      iconTransformation(origin = {100, -35}, extent = {{-8, -8}, {8, 8}})));
  Modelica.Blocks.Math.Gain command_pass_through(k = 1) 
    annotation(Placement(transformation(origin = {0, 35}, extent = {{-18, -12}, {18, 12}})));
  Modelica.Blocks.Math.Gain speed_pass_through(k = 1) 
    annotation(Placement(transformation(origin = {0, -35}, extent = {{-18, -12}, {18, 12}})));

equation
  connect(command, command_pass_through.u) 
    annotation(Line(points = {{-110, 35}, {-18, 35}}, color = {0, 0, 127}));
  connect(command_pass_through.y, command_to_plant) 
    annotation(Line(points = {{18, 35}, {110, 35}}, color = {0, 0, 127}));
  connect(speed, speed_pass_through.u) 
    annotation(Line(points = {{-110, -35}, {-18, -35}}, color = {0, 0, 127}));
  connect(speed_pass_through.y, speed_telemetry) 
    annotation(Line(points = {{18, -35}, {110, -35}}, color = {0, 0, 127}));
  annotation(
    Icon(coordinateSystem(extent = {{-100, -100}, {100, 100}}), graphics = {
      Rectangle(extent = {{-100, 100}, {100, -100}}, lineColor = {130, 0, 130},
        fillColor = {252, 244, 255}, fillPattern = FillPattern.Solid),
      Bitmap(origin = {0, 10}, extent = {{-78, -44.265}, {78, 44.265}},
        fileName = "modelica://MoSimQuadrotorModel/Vehicle/Resources/Images/motor.png"),
      Text(origin = {0, -78}, extent = {{-90, 14}, {90, -14}},
        textString = "Rotor %channel_index", textColor = {130, 0, 130})}),
    Diagram(coordinateSystem(extent = {{-130, -80}, {130, 80}}, grid = {2, 2})),
    __MWORKS(version = "26.3.0"));
end RotorCommandChannel;