within Resistance;
model Resistance "电阻"
  parameter Modelica.SIunits.Resistance R = 10;
  Modelica.SIunits.Voltage v;
  Modelica.SIunits.Current i;
  PositivePin positivePin
    annotation (Placement(transformation(origin = {-100.0, 0.0}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  NegativePin negativePin
    annotation (Placement(transformation(origin = {100.0, 0.0}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  annotation (Icon(coordinateSystem(extent = {{-100.0, -100.0}, {100.0, 100.0}}, 
    grid = {2.0, 2.0}), graphics = {Rectangle(origin = {0.0, 0.0}, 
    lineColor = {0, 0, 255}, 
    fillColor = {0, 0, 255}, 
    fillPattern = FillPattern.Solid, 
    extent = {{-60.0, 20.0}, {60.0, -20.0}}), Line(origin = {-76.0, 0.0}, 
    points = {{16.0, 0.0}, {-16.0, 0.0}, {-14.0, 0.0}}, 
    color = {0, 0, 255}), Line(origin = {73.99999999999997, 0.0}, 
    points = {{16.0, 0.0}, {-16.0, 0.0}, {-14.0, 0.0}}, 
    color = {0, 0, 255})}));
equation 
  v = R * i;
  i = positivePin.i;
  positivePin.i + negativePin.i = 0;
  v = positivePin.v - negativePin.v;
end Resistance;