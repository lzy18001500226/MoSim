model sys1 "混合仿真"
  annotation(__MWORKS(version="2025a"),experiment(Algorithm=Euler,InlineIntegrator=false,InlineStepSize=false,IntegratorStep=0.001,Interval=0.001,StartTime=0,StopTime=1,Tolerance=0.0001));
  SimplePID simplePID 
    annotation (Placement(transformation(origin = {-110, 20}, extent = {{-10, -10}, {10, 10}})),__MWORKS(SECInstance=true));
  Modelica.Blocks.Sources.Constant const(k=1) 
    annotation (Placement(transformation(origin={-224,20}, 
extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Math.Feedback feedback 
    annotation (Placement(transformation(origin={-167,20}, 
extent={{-10,-10},{10,10}})));
  Modelica.Mechanics.Rotational.Components.Inertia inertia(J=1) 
    annotation (Placement(transformation(origin = {-20, 20}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Mechanics.Rotational.Sources.Torque torque 
    annotation (Placement(transformation(origin = {-60, 20}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Mechanics.Rotational.Sensors.SpeedSensor speedSensor 
    annotation (Placement(transformation(origin={-80,-30}, 
extent={{10,-10},{-10,10}})));
equation
  connect(const.y, feedback.u1) 
  annotation(Line(origin={-194,20}, 
  points={{-19,0},{19,0}}, 
  color={0,0,127}));
  connect(simplePID.inport, feedback.y) 
  annotation(Line(origin={-140,20}, 
  points={{18.2,0},{-18,0}}, 
  color={0,0,0}));
  connect(simplePID.outport, torque.tau) 
  annotation(Line(origin={-85,20}, 
  points={{-13.2,0},{13,0}}, 
  color={0,0,0}));
  connect(torque.flange, inertia.flange_a) 
  annotation(Line(origin={-40,20}, 
  points={{-10,0},{10,0}}, 
  color={0,0,0}));
  connect(inertia.flange_b, speedSensor.flange) 
  annotation(Line(origin={-24,-5}, 
  points={{14,25},{46,25},{46,-25},{-46,-25}}, 
  color={0,0,0}));
  connect(speedSensor.w, feedback.u2) 
  annotation(Line(origin={-129,-9}, 
  points={{38,-21},{-38,-21},{-38,21}}, 
  color={0,0,127}));

end sys1;