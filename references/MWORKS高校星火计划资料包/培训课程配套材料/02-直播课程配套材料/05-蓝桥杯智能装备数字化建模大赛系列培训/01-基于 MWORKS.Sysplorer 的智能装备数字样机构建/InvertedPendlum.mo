model InvertedPendlum "倒立摆模型"
  annotation(Diagram(coordinateSystem(extent={{-100,-100},{100,100}}, 
grid={2,2})),experiment(Algorithm=Dassl,InlineIntegrator=false,InlineStepSize=false,Interval=0.01,StartTime=0,StopTime=20,Tolerance=0.0001),__MWORKS(ContinueSimConfig(SaveContinueFile="false",SaveBeforeStop="false",NumberBeforeStop=1,FixedContinueInterval="false",ContinueIntervalLength=20,ContinueTimeVector)));
  inner TYMultibody.World world 
    annotation (Placement(transformation(origin={16,-50}, 
extent={{-10,-10},{10,10}})));
  TYMultibody.Joints.Revolute revolute(phi_rel_fixed=true,phi_rel_0=0.261799387799149,useAxisFlange=true) 
    annotation (Placement(transformation(origin={90,-50}, 
extent={{10,-10},{-10,10}})));
  TYMultibody.Bodies.Body body(r_AG_a={0, 0.5, 0},m=0.1,r_AB_a={0,1, 0}) 
    annotation (Placement(transformation(origin={122,-50}, 
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
    annotation (Placement(transformation(origin={-90,-10}, 
extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Sources.Constant const2(k=0.1) 
    annotation (Placement(transformation(origin={-90,-50}, 
extent={{-10,-10},{10,10}})));
  equation
  connect(body.frame_a, revolute.frame_a) 
  annotation(Line(origin={121,-50}, 
points={{-9,0},{-21,0}}, 
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
  connect(const.y, bodyForce.Fx_in) 
  annotation(Line(origin={-53,17}, 
  points={{-26,23},{11,23},{11,-23},{25,-23}}, 
  color={0,0,127}));
  connect(const1.y, bodyForce.Fy_in) 
  annotation(Line(origin={-53,-8}, 
points={{-26,-2},{25,-2}}, 
color={0,0,127}));
  connect(const2.y, bodyForce.Fz_in) 
  annotation(Line(origin={-53,-32}, 
  points={{-26,-18},{11,-18},{11,18},{25,18}}, 
  color={0,0,127}));
  end InvertedPendlum;