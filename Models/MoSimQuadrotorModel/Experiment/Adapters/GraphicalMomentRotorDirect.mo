within MoSimQuadrotorModel.Experiment.Adapters;
model GraphicalMomentRotorDirect
  "Direct moment-to-rotor adapter for INDI/AWFF controllers"

  parameter Real hover_thrust = 0.37 "Nominal hover thrust per rotor";

  Modelica.Blocks.Interfaces.RealInput moment_command[4] 
    annotation(Placement(transformation(origin = {-260, 0}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Interfaces.RealOutput rotor_command[4] 
    annotation(Placement(transformation(origin = {260, 0}, extent = {{-10, -10}, {10, 10}})));

  Modelica.Blocks.Sources.Constant hover_bias[4](each k = hover_thrust) 
    annotation(Placement(transformation(origin = {-100, -60}, extent = {{-20, -20}, {20, 20}})));
  Modelica.Blocks.Math.Add rotor_sum[4](each k1 = 1, each k2 = 1) 
    annotation(Placement(transformation(origin = {80, 0}, extent = {{-40, -40}, {40, 40}})));

equation
  connect(moment_command[1], rotor_sum[1].u1) 
    annotation(Line(points = {{-260, 0}, {-100, 0}, {-100, 20}, {40, 20}}, color = {0, 0, 127}));
  connect(moment_command[2], rotor_sum[2].u1) 
    annotation(Line(points = {{-260, 0}, {-110, 0}, {-110, 20}, {40, 20}}, color = {0, 0, 127}));
  connect(moment_command[3], rotor_sum[3].u1) 
    annotation(Line(points = {{-260, 0}, {-120, 0}, {-120, 20}, {40, 20}}, color = {0, 0, 127}));
  connect(moment_command[4], rotor_sum[4].u1) 
    annotation(Line(points = {{-260, 0}, {-130, 0}, {-130, 20}, {40, 20}}, color = {0, 0, 127}));
  connect(hover_bias[1].y, rotor_sum[1].u2) 
    annotation(Line(points = {{-78, -60}, {-20, -60}, {-20, -20}, {40, -20}}, color = {0, 0, 127}));
  connect(hover_bias[2].y, rotor_sum[2].u2) 
    annotation(Line(points = {{-78, -60}, {-10, -60}, {-10, -20}, {40, -20}}, color = {0, 0, 127}));
  connect(hover_bias[3].y, rotor_sum[3].u2) 
    annotation(Line(points = {{-78, -60}, {0, -60}, {0, -20}, {40, -20}}, color = {0, 0, 127}));
  connect(hover_bias[4].y, rotor_sum[4].u2) 
    annotation(Line(points = {{-78, -60}, {10, -60}, {10, -20}, {40, -20}}, color = {0, 0, 127}));
  connect(rotor_sum[1].y, rotor_command[1]) 
    annotation(Line(points = {{120, 20}, {200, 20}, {200, 0}, {260, 0}}, color = {0, 0, 127}));
  connect(rotor_sum[2].y, rotor_command[2]) 
    annotation(Line(points = {{120, 7}, {210, 7}, {210, 0}, {260, 0}}, color = {0, 0, 127}));
  connect(rotor_sum[3].y, rotor_command[3]) 
    annotation(Line(points = {{120, -7}, {220, -7}, {220, 0}, {260, 0}}, color = {0, 0, 127}));
  connect(rotor_sum[4].y, rotor_command[4]) 
    annotation(Line(points = {{120, -20}, {230, -20}, {230, 0}, {260, 0}}, color = {0, 0, 127}));

  annotation(
    Diagram(coordinateSystem(extent = {{-280, -100}, {280, 100}}, grid = {2, 2})),
    Icon(coordinateSystem(extent = {{-100, -100}, {100, 100}}), graphics = {
      Rectangle(extent = {{-100, 100}, {100, -100}}, lineColor = {80, 80, 120},
        fillColor = {245, 240, 255}, fillPattern = FillPattern.Solid),
      Text(origin = {0, 20}, extent = {{-90, 18}, {90, -18}}, textString = "MOMENT"),
      Text(origin = {0, -20}, extent = {{-90, 18}, {90, -18}}, textString = "ROTOR DIRECT")}),
    __MWORKS(version = "26.3.0"));
end GraphicalMomentRotorDirect;