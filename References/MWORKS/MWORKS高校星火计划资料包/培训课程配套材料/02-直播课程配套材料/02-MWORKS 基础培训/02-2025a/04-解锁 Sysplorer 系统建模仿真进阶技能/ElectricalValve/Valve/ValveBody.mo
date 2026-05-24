model ValveBody "阀体"
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
  Modelica.Blocks.Interfaces.RealOutput phi "角位移" 
    annotation (Placement(transformation(origin={92,4}, 
extent={{-10,-10},{10,10}}), 
iconTransformation(origin={110,-60}, 
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
  TYMechanics.Rotational.Components.EndStop endStop 
    annotation (Placement(transformation(origin={8,4}, 
extent={{-10,-10},{10,10}})));
  TYMechanics.Rotational.Components.Inertia inertia1 
    annotation (Placement(transformation(origin={40,-26}, 
extent={{-10,-10},{10,10}}, 
rotation=-90)));
  TYMechanics.Rotational.Sensors.AngleSensor angleSensor 
    annotation (Placement(transformation(origin={62,4}, 
extent={{-10,-10},{10,10}})));
  TYMechanics.Rotational.Components.Fixed fixed 
    annotation (Placement(transformation(origin={-28,-10}, 
extent={{-10,-10},{10,10}}, 
rotation=90)));
  equation
  connect(emf.n, n) 
  annotation(Line(origin={-27,-6}, 
points={{47,26},{47,23},{-7,23},{-7,66}}, 
color={0,0,255}));
  connect(emf.p, p) 
  annotation(Line(origin={-36,48}, 
points={{56,-8},{56,-2},{106,-2},{106,12}}, 
color={0,0,255}));
  connect(endStop.flange_a, emf.support) 
  annotation(Line(origin={-9,17}, 
  points={{7,-13},{-19,-13},{-19,13},{19,13}}, 
  color={96,96,96}));
  connect(angleSensor.phi, phi) 
  annotation(Line(origin={75,2}, 
points={{-5,2},{17,2}}, 
color={0,0,127}));
  connect(endStop.flange_b, angleSensor.flange) 
  annotation(Line(origin={35,4}, 
  points={{-17,0},{17,0}}, 
  color={0,0,0}));
  connect(emf.flange, angleSensor.flange) 
  annotation(Line(origin={41,17}, 
  points={{-11,13},{-1,13},{-1,-13},{11,-13}}, 
  color={0,0,0}));
  connect(inertia1.flange_a, angleSensor.flange) 
  annotation(Line(origin={44,-18}, 
points={{-4,2},{-4,22},{8,22}}, 
color={96,96,96}));
  connect(fixed.flange, emf.support) 
  annotation(Line(origin={-35,-5}, 
points={{7,-5},{7,35},{45,35}}, 
color={0,0,0}));
  end ValveBody;