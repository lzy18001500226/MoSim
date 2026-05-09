model Electrical "电路部分"
  annotation(Diagram(coordinateSystem(extent={{-100,-100},{100,100}}, 
grid={2,2})),Icon(coordinateSystem(extent={{-100,-100},{100,100}}, 
grid={2,2}),graphics = {Rectangle(origin={0,0}, 
fillColor={255,255,255}, 
fillPattern=FillPattern.Solid, 
extent={{-100,100},{100,-100}}), Line(origin={0,-30}, 
points={{80,-70},{80,70},{-80,70},{-80,-70}}), Ellipse(origin={3.55271e-15,40}, 
fillColor={255,255,255}, 
fillPattern=FillPattern.Solid, 
extent={{-39.5,40},{39.5,-40}}), Text(origin={0,36}, 
lineColor={0,0,0}, 
extent={{-35,35},{35,-35}}, 
textString="V", 
textStyle={TextStyle.None}, 
textColor={0,0,0}, 
horizontalAlignment=LinePattern.None)}));
  Modelica.Electrical.Analog.Basic.Ground ground 
    annotation (Placement(transformation(origin={-132,-6}, 
  extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Interfaces.RealInput v "Voltage between pin p and n (= p.v - n.v) as input signal" 
    annotation (Placement(transformation(origin={-86,80}, 
  extent={{-20,-20},{20,20}}, 
  rotation=-90), 
  iconTransformation(origin={6.66134e-16,110}, 
  extent={{-10,-10},{10,10}}, 
  rotation=-90)));
  Modelica.Electrical.Analog.Interfaces.NegativePin n "Negative electrical pin" 
    annotation (Placement(transformation(origin={-54,4}, 
  extent={{-10,-10},{10,10}}), 
  iconTransformation(origin={80,-100}, 
  extent={{-10,-10},{10,10}})));
  Modelica.Electrical.Analog.Interfaces.Pin p 
    annotation (Placement(transformation(origin={-86,4}, 
  extent={{-10,-10},{10,10}}), 
  iconTransformation(origin={-80,-100}, 
  extent={{-10,-10},{10,10}})));
  Modelica.Electrical.Analog.Sources.SignalVoltage signalVoltage 
    annotation (Placement(transformation(origin={-86,37}, 
extent={{-10,10},{10,-10}}, 
rotation=-180)));
  Modelica.Electrical.Analog.Basic.Resistor resistor 
    annotation (Placement(transformation(origin={-46,37}, 
extent={{-10,-10},{10,10}})));
  Modelica.Electrical.Analog.Basic.Inductor inductor 
    annotation (Placement(transformation(origin={-18,37}, 
extent={{-10,-10},{10,10}})));
equation
  connect(inductor.p, resistor.n) 
  annotation(Line(origin={-146,13}, 
points={{118,24},{110,24}}, 
color={0,0,255}));
  connect(resistor.p, signalVoltage.p) 
  annotation(Line(origin={-91,57}, 
points={{35,-20},{15,-20}}, 
color={0,0,255}));
  connect(signalVoltage.n, ground.p) 
  annotation(Line(origin={-81.5,11}, 
points={{-14.5,26},{-50.5,26},{-50.5,-7}}, 
color={0,0,255}));
  connect(inductor.n, n) 
  annotation(Line(origin={-42.5,67}, 
points={{34.5,-30},{42.5,-30},{42.5,-63},{-11.5,-63}}, 
color={0,0,255}));
  connect(signalVoltage.v, v) 
  annotation(Line(origin={-86,70}, 
points={{0,-21},{0,10}}, 
color={0,0,127}));
  connect(ground.p, p) 
  annotation(Line(origin={-109,4}, 
  points={{-23,0},{23,0}}, 
  color={0,0,255}));

end Electrical;