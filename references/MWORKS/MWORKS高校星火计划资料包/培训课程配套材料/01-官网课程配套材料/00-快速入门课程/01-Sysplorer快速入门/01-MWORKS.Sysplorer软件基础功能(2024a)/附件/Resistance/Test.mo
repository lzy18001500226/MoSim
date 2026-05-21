within Resistance;
model Test
  Resistance resistance
    annotation (Placement(transformation(origin = {0.0, 30.0}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  Modelica.Electrical.Analog.Basic.Ground ground
    annotation (Placement(transformation(origin = {34.0, -19.999999999999996}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  Modelica.Electrical.Analog.Sources.ConstantVoltage constantVoltage(V = 10)
    annotation (Placement(transformation(extent = {{-10.0, -10.0}, {10.0, 10.0}})));
equation 
  connect(constantVoltage.p, resistance.positivePin)
    annotation (Line(origin = {-24.0, 15.0}, 
      points = {{14.0, -15.0}, {-14.0, -15.0}, {-14.0, 15.0}, {14.0, 15.0}}, 
      color = {0, 0, 255}));
  connect(resistance.negativePin, constantVoltage.n)
    annotation (Line(origin = {22.0, 15.0}, 
      points = {{-12.0, 15.0}, {12.0, 15.0}, {12.0, -15.0}, {-12.0, -15.0}}, 
      color = {0, 0, 255}));
  connect(ground.p, constantVoltage.n)
    annotation (Line(origin = {22.0, -5.0}, 
      points = {{12.0, -5.0}, {12.0, 5.0}, {-12.0, 5.0}}, 
      color = {0, 0, 255}));
end Test;