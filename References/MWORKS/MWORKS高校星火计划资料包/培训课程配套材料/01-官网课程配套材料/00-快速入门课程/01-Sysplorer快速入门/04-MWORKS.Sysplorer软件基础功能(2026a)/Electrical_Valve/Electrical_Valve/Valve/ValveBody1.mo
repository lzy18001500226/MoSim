model ValveBody1 "阀体"
  annotation(Diagram(coordinateSystem(extent={{-100,-100},{100,100}},
grid={2,2})),Icon(coordinateSystem(extent={{-100,-100},{100,100}},
grid={2,2}),graphics = {Rectangle(origin={0,0},
fillColor={255,255,255},
fillPattern=FillPattern.Solid,
extent={{-100,100},{100,-100}}), Line(origin={0,-29},
points={{0,29},{0,-29}}), Line(origin={0,50},
points={{-80,50},{-80,-50},{80,-50},{80,50}}), Rectangle(origin={-3.55271e-15,-2.22045e-16},
fillColor={255,255,255},
fillPattern=FillPattern.Solid,
extent={{-40,10},{40,-10}}), Polygon(origin={-40,-60},
fillColor={255,255,255},
fillPattern=FillPattern.Solid,
points={{-40,40},{-40,-40},{40,0}}), Polygon(origin={40,-60},
fillColor={255,255,255},
fillPattern=FillPattern.Solid,
points={{40,40},{40,-40},{-40,0}})}));
  Modelica.Mechanics.Rotational.Components.Fixed fixed 
    annotation (Placement(transformation(origin={-28,-10},
extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Interfaces.RealOutput phi "角位移" 
    annotation (Placement(transformation(origin={92,4},
extent={{-10,-10},{10,10}}),
iconTransformation(origin={110,-60},
extent={{-10,-10},{10,10}})));
  Modelica.Mechanics.Rotational.Sensors.AngleSensor angleSensor 
    annotation (Placement(transformation(origin={64,4},
extent={{-10,-10},{10,10}})));
  Modelica.Electrical.Analog.Basic.RotationalEMF emf(useSupport=true) 
    annotation (Placement(transformation(origin={20,30},
extent={{-10,-10},{10,10}})));
  Modelica.Electrical.Analog.Interfaces.NegativePin n "Negative electrical pin" 
    annotation (Placement(transformation(origin={-34,60},
extent={{-10,-10},{10,10}}),
iconTransformation(origin={-80,100},
extent={{-10,-10},{10,10}})));
  Modelica.Electrical.Analog.Interfaces.PositivePin p "Positive electrical pin" 
    annotation (Placement(transformation(origin={70,60},
extent={{-10,-10},{10,10}}),
iconTransformation(origin={80,100},
extent={{-10,-10},{10,10}})));
  TYMechanics.Rotational.Components.EndStop endStop(g_F=6.28318530717959,g_B=0) 
    annotation (Placement(transformation(origin={0,4},
extent={{-10,-10},{10,10}})));
  TYMechanics.Rotational.Components.Inertia inertia1(J=0.1) 
    annotation (Placement(transformation(origin={40,-36},
extent={{-10,-10},{10,10}},
rotation=90)));
equation
  connect(fixed.flange, emf.support) 
  annotation(Line(origin={-21,4},
points={{-7,-14},{-7,26},{31,26}},
color={0,0,0}));
  connect(phi, angleSensor.phi) 
  annotation(Line(origin={84,4},
points={{8,0},{-9,0}},
color={0,0,127}));
  connect(emf.flange, inertia1.flange_b) 
  annotation(Line(origin={54,16},
points={{-24,14},{-14,14},{-14,-42}},
color={0,0,0}));
  connect(angleSensor.flange, emf.flange) 
  annotation(Line(origin={61,-25},
points={{-7,29},{-21,29},{-21,55},{-31,55}},
color={0,0,0}));
  connect(emf.n, n) 
  annotation(Line(origin={-27,-6},
points={{47,26},{47,23},{-7,23},{-7,66}},
color={0,0,255}));
  connect(emf.p, p) 
  annotation(Line(origin={-36,48},
points={{56,-8},{56,-2},{106,-2},{106,12}},
color={0,0,255}));
  connect(endStop.flange_b, emf.flange) 
  annotation(Line(origin={25,17},
  points={{-15,-13},{15,-13},{15,13},{5,13}},
  color={0,0,0}));
  connect(endStop.flange_a, emf.support) 
  annotation(Line(origin={-9,17},
  points={{-1,-13},{-19,-13},{-19,13},{19,13}},
  color={96,96,96}));

end ValveBody1;