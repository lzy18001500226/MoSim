model InvertedPendlum1 "倒立摆模型"
  annotation(Diagram(coordinateSystem(extent={{-100,-100},{100,100}}, 
grid={2,2})),experiment(Algorithm=Dassl,InlineIntegrator=false,InlineStepSize=false,Interval=0.01,StartTime=0,StopTime=25,Tolerance=0.0001),__MWORKS(ContinueSimConfig(SaveContinueFile="false",SaveBeforeStop="false",NumberBeforeStop=1,FixedContinueInterval="false",ContinueIntervalLength=25,ContinueTimeVector)));
  inner TYMultibody.World world 
    annotation (Placement(transformation(origin={16,-50}, 
extent={{-10,-10},{10,10}})));
  TYMultibody.Joints.Revolute revolute(phi_rel_fixed=true,phi_rel_0=0.261799387799149,useAxisFlange=true) 
    annotation (Placement(transformation(origin={90,-50}, 
extent={{10,-10},{-10,10}})));
  TYMultibody.Bodies.Body body(r_AG_a={0, 0.5, 0},m=0.1,r_AB_a={0,1, 0}) 
    annotation (Placement(transformation(origin={136.633,-50.1798}, 
extent={{-10,-10},{10,10}})));
  TYMultibody.Bodies.Body body1(m=2,shapeType="box", r_shape = {-0.125, 0, 0}, length = 0.25, width = 0.125, ShapeColor = {0, 180, 0}) 
    annotation (Placement(transformation(origin={16,-10}, 
extent={{10,-10},{-10,10}})));
  TYMultibody.Forces.BodyForce bodyForce(useVariableForce=true) 
    annotation (Placement(transformation(origin={-18,-10}, 
extent={{-10,-10},{10,10}})));
  TYMultibody.Joints.Prismatic prismatic 
    annotation (Placement(transformation(origin={58,-50}, 
extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Sources.Constant const(k=0) 
    annotation (Placement(transformation(origin = {-90, 40}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Sources.Constant const1(k=0) 
    annotation (Placement(transformation(origin={-96.6607,-14.0824}, 
extent={{-10,-10},{10,10}})));
  TYMultibody.Sensors.AbsoluteVelocity absoluteVelocity 
    annotation (Placement(transformation(origin={109.696,48.968}, 
extent={{-10,-10},{10,10}})));
  TYMultibody.Sensors.AbsolutePosition absolutePosition 
    annotation (Placement(transformation(origin={110.358,20.1228}, 
extent={{-10,-10},{10,10}})));
  TYMechanics.Rotational.Sensors.AngleVelocitySensor angleVelocitySensor 
    annotation (Placement(transformation(origin={113.313,-82.4942}, 
extent={{-10,-10},{10,10}})));
  TYMechanics.Rotational.Sensors.AngleSensor angleSensor 
    annotation (Placement(transformation(origin={114.534,-102.791}, 
extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Math.Feedback feedback 
    annotation (Placement(transformation(origin={-213.065,-57.7149}, 
extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Continuous.Integrator integrator 
    annotation (Placement(transformation(origin={-174.815,-57.7601}, 
extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Math.Product gain 
    annotation (Placement(transformation(origin={-135.65,-51.6339}, 
extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Math.Sum sum1(nin=4) 
    annotation (Placement(transformation(origin={-30.3835,-188.657}, 
extent={{10,-10},{-10,10}})));
  Modelica.Blocks.Math.Product gain1 
    annotation (Placement(transformation(origin={70.5401,-129.61}, 
extent={{10,-10},{-10,10}})));
  Modelica.Blocks.Math.Product gain2 
    annotation (Placement(transformation(origin={71.0796,-171.535}, 
extent={{10,-10},{-10,10}})));
  Modelica.Blocks.Math.Product gain3 
    annotation (Placement(transformation(origin={72.402,-205.917}, 
extent={{10,-10},{-10,10}})));
  Modelica.Blocks.Math.Product gain4 
    annotation (Placement(transformation(origin={72.402,-241.621}, 
extent={{10,-10},{-10,10}})));
  Modelica.Blocks.Math.Feedback feedback1 
    annotation (Placement(transformation(origin={-89.4939,-51.7749}, 
extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Sources.TimeTable timeTable(table={{0.0, 1}, {1, 1}, {8, 1}, {8, -1}, {16, -1}, {16, 0}, {17, 0}}) 
    annotation (Placement(transformation(origin={-252.888,-57.5272}, 
extent={{-10,-10},{10,10}})));
  SyslabWorkspace.FromWorkspace.FromWorkspace_Scale fromWorkspace_Scale(varName="k1") 
    annotation (Placement(transformation(origin={-177.447,-12.4744}, 
extent={{-10,-10},{10,10}})));
  SyslabWorkspace.FromWorkspace.FromWorkspace_Vector fromWorkspace_Vector(row_dims=4,varName="K") 
    annotation (Placement(transformation(origin={293.616,-178.473}, 
extent={{10,-10},{-10,10}})));
  SyslabWorkspace.ToWorkspace.ToWorkspace_Scale toWorkspace_Scale(varName="v") 
    annotation (Placement(transformation(origin={275.103,48.9143}, 
extent={{-10,-10},{10,10}})));
  SyslabWorkspace.ToWorkspace.ToWorkspace_Scale toWorkspace_Scale1(varName="x") 
    annotation (Placement(transformation(origin={242.928,19.862}, 
extent={{-10,-10},{10,10}})));
  SyslabWorkspace.ToWorkspace.ToWorkspace_Scale toWorkspace_Scale2(varName="w") 
    annotation (Placement(transformation(origin={273.169,-82.1836}, 
extent={{-10,-10},{10,10}})));
  SyslabWorkspace.ToWorkspace.ToWorkspace_Scale toWorkspace_Scale3(varName="phi") 
    annotation (Placement(transformation(origin={245.347,-104.09}, 
extent={{-10,-10},{10,10}})));
  equation
  connect(body.frame_a, revolute.frame_a) 
  annotation(Line(origin={121,-50}, 
points={{5.63272,-0.179762},{-21,-0.179762},{-21,0}}, 
color={95,95,95}, 
thickness=0.5));
  connect(revolute.frame_b, prismatic.frame_b) 
  annotation(Line(origin={79,-50}, 
points={{1,0},{-11,0}}, 
color={95,95,95}, 
thickness=0.5));
  connect(body1.frame_a, prismatic.frame_b) 
  annotation(Line(origin={42,-57}, 
points={{-16,47},{32,47},{32,7},{26,7}}, 
color={95,95,95}, 
thickness=0.5));
  connect(world.frame_b, prismatic.frame_a) 
  annotation(Line(origin={31,-50}, 
points={{-5,0},{17,0}}, 
color={95,95,95}, 
thickness=0.5));
  connect(bodyForce.frame_b, body1.frame_b) 
  annotation(Line(origin={-8,-10}, 
points={{0,0},{14,0}}, 
color={95,95,95}, 
thickness=0.5));
  connect(const.y, bodyForce.Fy_in) 
  annotation(Line(origin={-53,17}, 
points={{-26,23},{0.54839,23},{0.54839,-27},{25,-27}}, 
color={0,0,127}),__MWORKS(BlockSystem(NamedSignal)));
  connect(const1.y, bodyForce.Fz_in) 
  annotation(Line(origin={-53,-8}, 
points={{-32.6607,-6.08237},{25,-6.08237},{25,-6}}, 
color={0,0,127}));
  connect(absolutePosition.frame_a, prismatic.frame_b) 
  annotation(Line(origin={85,-16}, 
points={{15.3583,36.1228},{-10.7405,36.1228},{-10.7405,-34},{-17,-34}}, 
color={95,95,95}, 
thickness=0.5));
  connect(absoluteVelocity.frame_a, prismatic.frame_b) 
  annotation(Line(origin={84,-1}, 
  points={{15.6957,49.968},{-9.74046,49.968},{-9.74046,-49},{-16,-49}}, 
  color={95,95,95}, 
  thickness=0.5));
  connect(angleVelocitySensor.flange, revolute.axis) 
  annotation(Line(origin={93,-71}, 
  points={{10.3134,-11.4942},{-10,-11.4942},{-10,11}}, 
  color={96,96,96}));
  connect(angleSensor.flange, revolute.axis) 
  annotation(Line(origin={94,-88}, 
points={{10.534,-14.7914},{-11,-14.7914},{-11,28}}, 
color={96,96,96}));
  connect(integrator.u, feedback.y) 
  annotation(Line(origin={-271.997,-58.9356}, 
points={{85.1819,1.17546},{67.932,1.17546},{67.932,1.22072}}, 
color={0,0,127}));
  connect(absolutePosition.r[1], feedback.u2) 
  annotation(Line(origin={-10,-151}, 
points={{131.358,171.1228},{228.193,171.1228},{228.193,-113.257},{-203.065,-113.257},{-203.065,85.2851}}, 
color={0,0,127}));
  connect(gain1.y, sum1.u[1]) 
  annotation(Line(origin={-12,-184}, 
points={{71.5401,54.3901},{4.54857,54.3901},{4.54857,-4.65724},{-6.38353,-4.65724}}, 
color={0,0,127}));
  connect(gain2.y, sum1.u[2]) 
  annotation(Line(origin={-8,-205}, 
points={{68.0796,33.4651},{0.548574,33.4651},{0.548574,16.3428},{-10.3835,16.3428}}, 
color={0,0,127}));
  connect(gain3.y, sum1.u[3]) 
  annotation(Line(origin={-8,-222}, 
points={{69.402,16.0831},{0.533291,16.0831},{0.533291,33.3428},{-10.3835,33.3428}}, 
color={0,0,127}));
  connect(gain4.y, sum1.u[4]) 
  annotation(Line(origin={-8,-240}, 
points={{69.402,-1.62091},{0.530594,-1.62091},{0.530594,51.3428},{-10.3835,51.3428}}, 
color={0,0,127}));
  connect(feedback1.u1, gain.y) 
  annotation(Line(origin={-168.966,-56.0968}, 
points={{71.4721,4.32186},{44.316,4.32186},{44.316,4.46291}}, 
color={0,0,127}));
  connect(feedback1.u2, sum1.y) 
  annotation(Line(origin={-122,-139}, 
points={{32.5061,79.2251},{32.5061,-49.657},{80.6165,-49.657}}, 
color={0,0,127}));
  connect(feedback.u1, timeTable.y) 
  annotation(Line(origin={-338,-57}, 
points={{116.935,-0.714873},{96.1123,-0.714873},{96.1123,-0.527151}}, 
color={0,0,127}),__MWORKS(BlockSystem(NamedSignal)));
  connect(feedback1.y, bodyForce.Fx_in) 
  annotation(Line(origin={-56,-32}, 
points={{-24.4939,-19.7749},{9.67116,-19.7749},{9.67116,26},{28,26}}, 
color={0,0,127}));
  connect(gain1.u1, angleSensor.phi) 
  annotation(Line(origin={113,-113}, 
  points={{-30.4599,-10.61},{31.2972,-10.61},{31.2972,10.209},{9.534,10.209}}, 
  color={0,0,127}));
  connect(gain2.u1, angleVelocitySensor.om) 
  annotation(Line(origin={128,-124}, 
  points={{-44.9204,-41.535},{45.7103,-41.535},{45.7103,41.5058},{-6.687,41.5058}}, 
  color={0,0,127}));
  connect(gain3.u1, absolutePosition.r[1]) 
  annotation(Line(origin={140,-90}, 
points={{-55.598,-109.917},{78.1802,-109.917},{78.1802,110.1228},{-18.642,110.1228}}, 
color={0,0,127}));
  connect(gain4.u1, absoluteVelocity.v[1]) 
  annotation(Line(origin={151,-93}, 
  points={{-66.598,-142.621},{67.3175,-142.621},{67.3175,141.968},{-30.304,141.968}}, 
  color={0,0,127}));
  connect(gain.u2, integrator.y) 
  annotation(Line(origin={-156,-58}, 
  points={{8.35,0.3661},{-7.815,0.3661},{-7.815,0.2399}}, 
  color={0,0,127}));
  connect(fromWorkspace_Scale.outputs, gain.u1) 
  annotation(Line(origin={-193,-2}, 
points={{26.5535,-10.4744},{38.2642,-10.4744},{38.2642,-43.6339},{45.35,-43.6339}}, 
color={0,0,127}));
  connect(fromWorkspace_Vector.outputs[1], gain1.u2) 
  annotation(Line(origin={183,-157}, 
  points={{99.616,-21.473},{55.7016,-21.473},{55.7016,21.39},{-100.4599,21.39}}, 
  color={0,0,127}));
  connect(fromWorkspace_Vector.outputs[2], gain2.u2) 
  annotation(Line(origin={183,-178}, 
  points={{99.616,-0.473},{-99.9204,-0.473},{-99.9204,0.465}}, 
  color={0,0,127}));
  connect(fromWorkspace_Vector.outputs[3], gain3.u2) 
  annotation(Line(origin={184,-195}, 
points={{98.616,16.527},{54.7099,16.527},{54.7099,-16.917},{-99.598,-16.917}}, 
color={0,0,127}));
  connect(fromWorkspace_Vector.outputs[4], gain4.u2) 
  annotation(Line(origin={184,-213}, 
points={{98.616,34.527},{54.7099,34.527},{54.7099,-34.621},{-99.598,-34.621}}, 
color={0,0,127}));
  connect(toWorkspace_Scale.dataInput, absoluteVelocity.v[1]) 
  annotation(Line(origin={192,50}, 
points={{72.1035,-1.08569},{-71.304,-1.08569},{-71.304,-1.032}}, 
color={0,0,127}));
  connect(toWorkspace_Scale1.dataInput, absolutePosition.r[1]) 
  annotation(Line(origin={192,21}, 
points={{39.9281,-1.13796},{-70.642,-1.13796},{-70.642,-0.8772}}, 
color={0,0,127}));
  connect(toWorkspace_Scale2.dataInput, angleVelocitySensor.om) 
  annotation(Line(origin={195,-81}, 
points={{67.1691,-1.18364},{-73.687,-1.18364},{-73.687,-1.4942}}, 
color={0,0,127}),__MWORKS(BlockSystem(NamedSignal)));
  connect(toWorkspace_Scale3.dataInput, angleSensor.phi) 
  annotation(Line(origin={192,-106}, 
points={{42.3473,1.91002},{-69.466,1.91002},{-69.466,3.209}}, 
color={0,0,127}),__MWORKS(BlockSystem(NamedSignal)));
  end InvertedPendlum1;