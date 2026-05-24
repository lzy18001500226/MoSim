within ;
model WaterTank
  Modelica.Blocks.Sources.Step step(height = 2, offset = 0)
    annotation (Placement(transformation(origin = {-133.99999999999997, 26.000000000000007}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  Modelica.Blocks.Math.Feedback feedback
    annotation (Placement(transformation(origin = {-96.0, 26.000000000000007}, 
      extent = {{-10.0, 10.0}, {10.0, -10.0}})));
  Modelica.Blocks.Math.Feedback feedback1
    annotation (Placement(transformation(origin = {18.00000000000003, 26.000000000000007}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  Modelica.Blocks.Math.Sqrt sqrt1
    annotation (Placement(transformation(origin = {70.0, -21.999999999999993}, 
      extent = {{10.0, 10.0}, {-10.0, -10.0}})));
  Modelica.Blocks.Math.Gain gain2(k = 0.25)
    annotation (Placement(transformation(origin = {-20.0, 26.000000000000007}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  Modelica.Blocks.Math.Gain gain3(k = 0.1)
    annotation (Placement(transformation(origin = {36.0, -21.999999999999993}, 
      extent = {{10.0, 10.0}, {-10.0, -10.0}})));
  Modelica.Blocks.Continuous.Integrator integrator(use_reset = false, initType = Modelica.Blocks.Types.Init.InitialState, y_start = 1)
    annotation (Placement(transformation(origin = {58.0, 26.000000000000014}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  Modelica.Blocks.Interfaces.RealOutput y
    annotation (Placement(transformation(origin = {118.0, 26.000000000000014}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  Modelica.Blocks.Continuous.PI PI1
    annotation (Placement(transformation(origin = {-58.00000000000001, 26.000000000000007}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
equation 
  connect(step.y, feedback.u1)
    annotation (Line(origin = {-113.0, 26.0}, 
      points = {{-10.0, 0.0}, {9.0, 0.0}}, 
      color = {0, 0, 127}));
  connect(feedback.y, PI1.u)
    annotation (Line(origin = {-78.0, 26.0}, 
      points = {{-9.0, 0.0}, {8.0, 0.0}}, 
      color = {0, 0, 127}));
  connect(PI1.y, gain2.u)
    annotation (Line(origin = {-39.0, 26.0}, 
      points = {{-8.0, 0.0}, {7.0, 0.0}}, 
      color = {0, 0, 127}));
  connect(gain2.y, feedback1.u1)
    annotation (Line(origin = {1.0, 26.0}, 
      points = {{-10.0, 0.0}, {9.0, 0.0}}, 
      color = {0, 0, 127}));
  connect(feedback1.y, integrator.u)
    annotation (Line(origin = {37.0, 26.0}, 
      points = {{-10.0, 0.0}, {9.0, 0.0}}, 
      color = {0, 0, 127}));
  connect(integrator.y, y)
    annotation (Line(origin = {94.0, 26.0}, 
      points = {{-25.0, 0.0}, {24.0, 0.0}}, 
      color = {0, 0, 127}));
  connect(sqrt1.u, y)
    annotation (Line(origin = {100.0, 2.0}, 
      points = {{-18.0, -24.0}, {-8.0, -24.0}, {-8.0, 24.0}, {18.0, 24.0}}, 
      color = {0, 0, 127}));
  connect(sqrt1.y, gain3.u)
    annotation (Line(origin = {54.0, -22.0}, 
      points = {{5.0, 0.0}, {-6.0, 0.0}}, 
      color = {0, 0, 127}));
  connect(gain3.y, feedback1.u2)
    annotation (Line(origin = {22.0, -2.0}, 
      points = {{3.0, -20.0}, {-4.0, -20.0}, {-4.0, 20.0}}, 
      color = {0, 0, 127}));
  connect(feedback.u2, y)
    annotation (Line(origin = {11.0, 24.0}, 
      points = {{-107.0, 10.0}, {-107.0, 30.0}, {81.0, 30.0}, {81.0, 2.0}, {107.0, 2.0}}, 
      color = {0, 0, 127}));
end WaterTank;