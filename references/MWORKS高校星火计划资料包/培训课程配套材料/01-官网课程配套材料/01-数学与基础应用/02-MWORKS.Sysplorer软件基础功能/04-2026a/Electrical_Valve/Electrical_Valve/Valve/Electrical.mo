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
  Modelica.Electrical.Analog.Sources.SignalVoltage signalVoltage 
    annotation (Placement(transformation(origin={-86,30},
extent={{-10,10},{10,-10}},
rotation=-180)));
  Modelica.Blocks.Interfaces.RealInput v "Voltage between pin p and n (= p.v - n.v) as input signal" 
    annotation (Placement(transformation(origin={-86,64},
extent={{-12,-12},{12,12}},
rotation=-90),
iconTransformation(origin={6.66134e-16,110},
extent={{-10,-10},{10,10}},
rotation=-90)));
  Modelica.Electrical.Analog.Basic.Resistor resistor 
    annotation (Placement(transformation(origin={-46,30},
extent={{-10,-10},{10,10}})));
  Modelica.Electrical.Analog.Basic.Inductor inductor 
    annotation (Placement(transformation(origin={-20,30},
extent={{-10,-10},{10,10}})));
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
  equation
  connect(inductor.p, resistor.n) 
  annotation(Line(origin={-146,6},
points={{116,24},{110,24}},
color={0,0,255}));
  connect(resistor.p, signalVoltage.p) 
  annotation(Line(origin={-91,50},
points={{35,-20},{15,-20}},
color={0,0,255}));
  connect(signalVoltage.n, ground.p) 
  annotation(Line(origin={-51,-7},
points={{-45,37},{-81,37},{-81,11}},
color={0,0,255}));
  connect(signalVoltage.v, v) 
  annotation(Line(origin={-109,30},
points={{23,12},{23,34}},
color={0,0,127}));
  connect(inductor.n, n) 
  annotation(Line(origin={-12,49},
points={{2,-19},{5,-19},{5,-45},{-42,-45}},
color={0,0,255}));
  connect(ground.p, p) 
  annotation(Line(origin={-43,3},
points={{-89,1},{-89,4},{-43,4},{-43,1}},
color={0,0,255}));
  end Electrical;