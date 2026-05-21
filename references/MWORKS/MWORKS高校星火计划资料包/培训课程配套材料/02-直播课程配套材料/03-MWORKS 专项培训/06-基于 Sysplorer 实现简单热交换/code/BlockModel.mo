model BlockModel "框图建模"
  annotation(__MWORKS(version="2025a"),Diagram(coordinateSystem(extent={{-100,-100},{100,100}}, 
grid={2,2})));



parameter Real rou=1000;
parameter Real V=2;
parameter Real cp=1.8;
parameter Real h=1000;
parameter Real A=250;
parameter Real Ti=80;
parameter Real Ts=150;
parameter Real m=20;
//Real T_out(start=75);

  Modelica.Blocks.Sources.Constant const(k=Ts) 
    annotation (Placement(transformation(origin={-248,180}, 
extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Sources.Constant const1(k=Ti) 
    annotation (Placement(transformation(origin={-250,146}, 
extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Sources.Constant const2(k=m) 
    annotation (Placement(transformation(origin={-250,106}, 
extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Math.Gain gain(k=h*A) 
    annotation (Placement(transformation(origin={-80,174}, 
extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Math.Add add(k2=-1) 
    annotation (Placement(transformation(origin={-176,174}, 
extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Math.Product product1 
    annotation (Placement(transformation(origin={-56,124}, 
extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Math.Add add1(k2=-1) 
    annotation (Placement(transformation(origin={-176,140}, 
extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Math.Add add2 
    annotation (Placement(transformation(origin={-264,8}, 
extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Math.Gain gain1(k=cp) 
    annotation (Placement(transformation(origin={-122,140}, 
extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Math.Gain gain2(k=1/(rou*V*cp)) 
    annotation (Placement(transformation(origin={-236,8}, 
extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Continuous.Integrator integrator(y_start=75) 
    annotation (Placement(transformation(origin={-208,8}, 
extent={{-10,-10},{10,10}})));
equation
  connect(const.y, add.u1) 
  annotation(Line(origin={-212,180}, 
points={{-25,0},{24,0}}, 
color={0,0,127}));
  connect(const1.y, add1.u1) 
  annotation(Line(origin={-213,146}, 
points={{-26,0},{25,0}}, 
color={0,0,127}));
  connect(add.y, gain.u) 
  annotation(Line(origin={-137,167}, 
points={{-28,7},{45,7}}, 
color={0,0,127}));
  connect(add1.y, gain1.u) 
  annotation(Line(origin={-134,140}, 
points={{-31,0},{0,0}}, 
color={0,0,127}));
  connect(const2.y, product1.u2) 
  annotation(Line(origin={-153,112}, 
points={{-86,-6},{85,-6},{85,6}}, 
color={0,0,127}));
  connect(gain1.y, product1.u1) 
  annotation(Line(origin={-89,135}, 
points={{-22,5},{21,5},{21,-5}}, 
color={0,0,127}));
  connect(product1.y, add2.u1) 
  annotation(Line(origin={-72,58}, 
points={{27,66},{30,66},{30,-12},{-208,-12},{-208,-44},{-204,-44}}, 
color={0,0,127}));
  connect(gain.y, add2.u2) 
  annotation(Line(origin={-84,77}, 
points={{15,97},{68,97},{68,-9},{-200,-9},{-200,-75},{-192,-75}}, 
color={0,0,127}));
  connect(add2.y, gain2.u) 
  annotation(Line(origin={-242,8}, 
points={{-11,0},{-6,0}}, 
color={0,0,127}));
  connect(gain2.y, integrator.u) 
  annotation(Line(origin={-210,-23}, 
points={{-15,31},{-10,31}}, 
color={0,0,127}));
  connect(integrator.y, add.u2) 
  annotation(Line(origin={-139,91}, 
points={{-58,-83},{-55,-83},{-55,77},{-49,77}}, 
color={0,0,127}));
  connect(integrator.y, add1.u2) 
  annotation(Line(origin={-182,71}, 
points={{-15,-63},{-8,-63},{-8,63},{-6,63}}, 
color={0,0,127}));
  end BlockModel;