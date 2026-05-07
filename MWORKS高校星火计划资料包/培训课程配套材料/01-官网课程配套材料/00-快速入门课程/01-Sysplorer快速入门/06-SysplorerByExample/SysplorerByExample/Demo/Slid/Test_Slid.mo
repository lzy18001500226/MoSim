model Test_Slid
  annotation(__MWORKS(version="2025b"),Diagram(coordinateSystem(extent={{-100,-100},{100,100}},
grid={2,2})));
  Modelica.Mechanics.Translational.Sources.Force force 
    annotation (Placement(transformation(origin = {-130, -20}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Sources.Sine sine(amplitude=10,phase=1.5707963267949,f=1) 
    annotation (Placement(transformation(origin={-194,-20},
extent={{-10,-10},{10,10}})));
  Modelica.Mechanics.Translational.Components.Mass mass(m=1) 
    annotation (Placement(transformation(origin={-14,-20},
extent={{-10,-10},{10,10}})));
  .SysplorerByExample.Demo.Slid.SlidingFriction slidingFriction 
    annotation (Placement(transformation(origin={40,-20},
extent={{-10,-10},{10,10}})));
  Modelica.Mechanics.Translational.Sources.Force force1 
    annotation (Placement(transformation(origin={-130,24},
extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Sources.Sine sine1(amplitude=10,phase=1.5707963267949,f=1) 
    annotation (Placement(transformation(origin={-194,24},
extent={{-10,-10},{10,10}})));
  Modelica.Mechanics.Translational.Components.Mass mass1(m=1) 
    annotation (Placement(transformation(origin={-14,24},
extent={{-10,-10},{10,10}})));
  Modelica.Mechanics.Translational.Components.Mass mass2(m=1) 
    annotation (Placement(transformation(origin={84,-20},
extent={{-10,-10},{10,10}})));
  Modelica.Mechanics.Translational.Components.Mass mass3(m=1) 
    annotation (Placement(transformation(origin={84,24},
extent={{-10,-10},{10,10}})));
  equation
  connect(sine.y, force.f) 
  annotation(Line(origin={-162,-20},
  points={{-21,0},{20,0}},
  color={0,0,127}));
  connect(force.flange, mass.flange_a) 
  annotation(Line(origin={-72,-20},
  points={{-48,0},{48,0}},
  color={0,127,0}));
  connect(mass.flange_b, slidingFriction.flange_a) 
  annotation(Line(origin={13,-20},
  points={{-17,0},{17,0}},
  color={0,127,0}));
  connect(sine1.y, force1.f) 
  annotation(Line(origin={-162,24},
points={{-21,0},{20,0}},
color={0,0,127}));
  connect(force1.flange, mass1.flange_a) 
  annotation(Line(origin={-72,24},
points={{-48,0},{48,0}},
color={0,127,0}));
  connect(slidingFriction.flange_b, mass2.flange_a) 
  annotation(Line(origin={67,-20},
points={{-17,0},{7,0}},
color={0,127,0}));
  connect(mass1.flange_b, mass3.flange_a) 
  annotation(Line(origin={35,24},
  points={{-39,0},{39,0}},
  color={0,127,0}));
  end Test_Slid;