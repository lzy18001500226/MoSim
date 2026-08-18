within MoSimQuadrotorModel.Guidance.Trajectories;
model ClimbPath "阶梯爬升模型"
  extends PartialTrajectory;
  Modelica.Blocks.Sources.Ramp ramp(startTime = 10, duration = 3,
    height = 5)
    annotation (Placement(transformation(origin = {-52.0, -28.0},
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  Modelica.Blocks.Sources.Ramp ramp1(offset = 0, startTime = 0, height = 10, duration = 5)
    annotation (Placement(transformation(origin = {-52.0, -72.0},
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));



  Modelica.Blocks.Math.Add add
    annotation (Placement(transformation(origin = {6.0, -50.0},
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  Modelica.Blocks.Math.Gain gain(k = 1)
    annotation (Placement(transformation(origin = {46.0, -50.0},
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  annotation (experiment(Algorithm = Dassl, Interval = 0.001, StartTime = 0, StopTime = 20, Tolerance = 0.0001),
    Icon(coordinateSystem(extent = {{-100.0, -100.0}, {100.0, 100.0}},
      grid = {2.0, 2.0}), graphics = {Rectangle(origin = {0.11311672683513052, 0.808664259927788},
      lineColor = {200, 200, 200},
      fillColor = {248, 248, 248},
      fillPattern = FillPattern.HorizontalCylinder,
      extent = {{-100.0, -100.0}, {100.0, 100.0}},
      radius = 25.0), Line(origin = {3.0, -3.0},
      points = {{-83.0, -37.0}, {-5.0, -37.0}, {15.0, 37.0}, {83.0, 37.0}},
      color = {136, 136, 136},
      thickness = 0.5,
      arrow = {Arrow.None, Arrow.Filled}), Line(origin = {-63.0, -26.0},
      points = {{-17.0, 0.0}, {17.0, 0.0}},
      color = {134, 134, 134},
      pattern = LinePattern.Dash,
      arrow = {Arrow.None, Arrow.Filled},
      arrowSize = 4.0,
      __MWorks_Manhattanize = true)}));
  Modelica.Blocks.Sources.Ramp ramp3(startTime = 30, duration = 10,
    height = 10)
    annotation (Placement(transformation(origin = {6.0, 0.0},
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  Modelica.Blocks.Sources.Ramp ramp5(startTime = 20, duration = 10,
    height = 10)
    annotation (Placement(transformation(origin = {6.0, 44.0},
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
equation
  connect(ramp.y, add.u1)
    annotation (Line(origin = {-21.999999999999996, -35.0},
      points = {{-19.0, 7.0}, {4.0, 7.0}, {4.0, -9.0}, {16.0, -9.0}},
      color = {0, 0, 127}));
  connect(ramp1.y, add.u2)
    annotation (Line(origin = {-21.999999999999996, -63.0},
      points = {{-19.0, -9.0}, {4.0, -9.0}, {4.0, 7.0}, {16.0, 7.0}},
      color = {0, 0, 127}));
  connect(add.y, gain.u)
    annotation (Line(origin = {13.0, -50.0},
      points = {{4.0, 0.0}, {21.0, 0.0}},
      color = {0, 0, 127}));
  connect(gain.y, position_command[3])
    annotation (Line(origin = {84.0, -25.0},
      points = {{-27.0, -25.0}, {-22.0, -25.0}, {-22.0, 25.0}, {26.0, 25.0}},
      color = {0, 0, 127}));
  connect(ramp3.y, position_command[2])
    annotation (Line(origin = {64.0, 0.0},
      points = {{-47.0, 0.0}, {46.0, 0.0}},
      color = {0, 0, 127}));
  connect(ramp5.y, position_command[1])
    annotation (Line(origin = {64.0, 22.0},
      points = {{-47.0, 22.0}, {-2.0, 22.0}, {-2.0, -22.0}, {46.0, -22.0}},
      color = {0, 0, 127}));
  velocity_command[1] = if time >= 20 and time < 30 then 1 else 0;
  velocity_command[2] = if time >= 30 and time < 40 then 1 else 0;
  velocity_command[3] = (if time >= 0 and time < 5 then 2 else 0)
    + (if time >= 10 and time < 13 then 5 / 3 else 0);
  acceleration_command = {0, 0, 0};
end ClimbPath;
