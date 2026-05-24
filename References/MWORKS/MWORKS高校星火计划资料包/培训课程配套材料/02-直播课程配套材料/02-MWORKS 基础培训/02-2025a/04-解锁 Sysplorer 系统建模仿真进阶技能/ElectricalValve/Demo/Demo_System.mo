model Demo_System "系统示例"
  annotation(__MWORKS(version="2025a"),experiment(Algorithm=Dassl,InlineIntegrator=false,InlineStepSize=false,Interval=0.001,StartTime=0,StopTime=1,Tolerance=0.0001),Diagram(coordinateSystem(extent={{-100,-100},{100,100}}, 
grid={2,2})));
  Modelica.Blocks.Tables.CombiTable1Ds combiTable1Ds(table={{0.0, 0}, {2*3.14, 50}}) 
    annotation (Placement(transformation(origin={-96.1797,-90.8983}, 
extent={{-10,-10},{10,10}})));
  Valve.Electrical electrical(resistor(R=50),inductor(L=1.2e-4)) 
    annotation (Placement(transformation(origin={-126,-58}, 
extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Math.Add add(k2=-1) 
    annotation (Placement(transformation(origin={-192,-44}, 
extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Sources.Constant const(k=5) 
    annotation (Placement(transformation(origin={-220,-38}, 
extent={{-10,-10},{10,10}})));
  Controller.PID_Controller pID_Controller(gain(k=60),integrator(k=2),derivative(k=0.1)) 
    annotation (Placement(transformation(origin={-159,-44}, 
extent={{-10,-10},{10,10}})));
  Valve.ValveBody valveBody1_1(emf(k=10),endStop(g_F=6.28318530717959),inertia1(J=0.1)) 
    annotation (Placement(transformation(origin={-125.849,-84.9458}, 
extent={{-10,-10},{10,10}})));
  equation
  connect(add.u1, const.y) 
  annotation(Line(origin={-220,-38}, 
points={{16,0},{11,0}}, 
color={0,0,127}));
  connect(combiTable1Ds.y[1], add.u2) 
  annotation(Line(origin={-145,-71}, 
points={{59.8203,-19.8983},{73,-19.8983},{73,-43},{-63,-43},{-63,21},{-59,21}}, 
color={0,0,127}));
  connect(add.y, pID_Controller.u) 
  annotation(Line(origin={-175,-44}, 
  points={{-6,0},{5,0}}, 
  color={0,0,127}));
  connect(pID_Controller.y, electrical.v) 
  annotation(Line(origin={-137,-45}, 
  points={{-11,1},{11,1},{11,-2}}, 
  color={0,0,127}));
  connect(valveBody1_1.phi, combiTable1Ds.u) 
  annotation(Line(origin={-111,-91}, 
points={{-3.84866,0.0542111},{2.82034,0.101711}}, 
color={0,0,127}));
  connect(valveBody1_1.n, electrical.p) 
  annotation(Line(origin={-134,-71}, 
points={{0.151342,-3.94579},{0.151342,3},{0,3}}, 
color={0,0,255}));
  connect(valveBody1_1.p, electrical.n) 
  annotation(Line(origin={-118,-71}, 
points={{0.151342,-3.94579},{0.151342,3},{0,3}}, 
color={0,0,255}));
  end Demo_System;