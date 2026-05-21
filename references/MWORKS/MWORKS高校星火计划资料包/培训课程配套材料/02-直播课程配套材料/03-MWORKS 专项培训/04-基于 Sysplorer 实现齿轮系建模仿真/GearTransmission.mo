model GearTransmission "外啮合直齿齿轮传动"
  inner Modelica.Mechanics.MultiBody.World world(axisLength = 0.05, axisDiameter = 0.001) 
    annotation(Placement(transformation(origin={-124,-44}, 
extent={{-10,-10},{10,10}})));
  parameter TYDriveline3D.GearsDrive.Internal.Types.Module m = 0.005 "齿轮模数" annotation(Dialog(group = "齿轮"));
  parameter Modelica.Units.SI.Distance a = (m * z1 + m * z2) / 2 "齿轮1中心到齿轮2中心的距离" annotation(Dialog(group = "齿轮"));
  parameter Modelica.Units.SI.Length width = 0.05 "齿轮宽度" annotation(Dialog(group = "齿轮"));
  parameter Integer z1 = 20 "齿轮1的轮齿个数" annotation(Dialog(group = "齿轮1"));
  parameter Integer z2 = 40 "齿轮2的轮齿个数" annotation(Dialog(group = "齿轮2"));
  parameter Real x1 = 0 "齿轮1的变位系数" annotation(Dialog(group = "齿轮1"));
  parameter Real x2 = 0 "齿轮2的变位系数" annotation(Dialog(group = "齿轮2"));
  parameter Modelica.Units.NonSI.Angle_deg InitialRotationWheel1 = 90 - 360 / z1 * floor(90 / 360 * z1) "齿轮1旋转轴初始角度" annotation(Dialog(group = "齿轮1"));
  parameter Modelica.Units.NonSI.Angle_deg InitialRotationWheel2 = 270 - 360 / z2 * (floor(270 / 360 * z2) + 0.5) "齿轮2旋转轴初始角度" annotation(Dialog(group = "齿轮2"));

  TYDriveline3D.GearsDrive.SpurGear gear1(m = m, z = z1, width = 0.05, initialRotationGearWheel = InitialRotationWheel1, dHole = 0) annotation(Placement(transformation(origin={8,-44}, 
extent={{10,10},{-10,-10}}, 
rotation=-180)), __MWORKS(BlockSystem(StateMachine)));
  TYDriveline3D.GearsDrive.SpurGear gear2(m = m, z = z2, width = 0.05, initialRotationGearWheel = InitialRotationWheel2, dHole = 0.05) annotation(Placement(transformation(origin={8,36}, 
extent={{10,10},{-10,-10}}, 
rotation=-180)), __MWORKS(BlockSystem(StateMachine)));
  TYDriveline3D.GearsDrive.SpurGearContact gearContact(z1 = z1, z2 = z2, m = m, width = 0.05, x1 = x1, x2 = x2, tipReliefAmplitude2 = 0.001 * m, tipReliefLength2 = 0.01 * m, tipReliefLength1 = 0.05 * m, tipReliefAmplitude1 = 0.01 * m) annotation(Placement(transformation(origin={8,-4}, 
extent={{-10,-10},{10,10}})), __MWORKS(BlockSystem(StateMachine)));
  Modelica.Mechanics.MultiBody.Joints.Revolute revolute2(w(fixed = false, start = 0), animation = false, useAxisFlange = true) 
    annotation(Placement(transformation(origin={-68,36}, 
extent={{-10,-10},{10,10}})), __MWORKS(BlockSystem(StateMachine)));
  Modelica.Mechanics.MultiBody.Joints.Revolute revolute1(w(fixed = false), animation = false, useAxisFlange = true) 
    annotation(Placement(transformation(origin={-68,-44}, 
extent={{-10,-10},{10,10}})), __MWORKS(BlockSystem(StateMachine)));
  Modelica.Mechanics.MultiBody.Parts.Fixed fixed(r = {0, 0.15, 0}, animation = false) 
    annotation(Placement(transformation(origin={-124,36}, 
extent={{-10,-10},{10,10}})));
  Modelica.Mechanics.Rotational.Sources.Speed speed 
    annotation(Placement(transformation(origin={-88,-4}, 
extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Sources.RealExpression realExpression(y=1) 
    annotation(Placement(transformation(origin={-124,-4}, 
extent={{-10,-10},{10,10}})));
  Modelica.Mechanics.Rotational.Components.Damper damper(d = 1000) 
    annotation(Placement(transformation(origin={-68,68}, 
extent={{-10,-10},{10,10}})));
  TYMultibody.Bodies.Body body(r_AG_a={0, 0, 0.05},r_AB_a={0, 0, 0.1},width=0.05) 
    annotation (Placement(transformation(origin={38,64}, 
extent={{-10,-10},{10,10}})));
  TYDriveline3D.GearsDrive.HelicalGear helicalGear(dHole=0.05,initialRotationGearWheel=90 - 360 / 50 * floor(90 / 360 * 50)) 
    annotation (Placement(transformation(origin={84,64}, 
extent={{-10,-10},{10,10}})));
  TYDriveline3D.GearsDrive.HelicalGear helicalGear1(dHole=0.05,initialRotationGearWheel=270 - 360 / 50 * (floor(270 / 360 *50) + 0.5)) 
    annotation (Placement(transformation(origin={84,0}, 
extent={{10,-10},{-10,10}})));
  Modelica.Mechanics.MultiBody.Joints.Revolute revolute3(w(fixed = false, start = 0), animation = false, useAxisFlange = false) 
    annotation(Placement(transformation(origin={120,0}, 
extent={{-10,-10},{10,10}})), __MWORKS(BlockSystem(StateMachine)));
  Modelica.Mechanics.MultiBody.Parts.Fixed fixed1(r = {0, a-0.2, 0.1}, animation = false) 
    annotation(Placement(transformation(origin={150,0}, 
extent={{10,-10},{-10,10}})));
  TYDriveline3D.GearsDrive.HelicalGearContact helicalGearContact(z1=50,z2=50,mn=0.004) 
    annotation (Placement(transformation(origin={84,32}, 
extent={{-10,-10},{10,10}})));
  equation
  connect(revolute2.frame_b, gear2.frame_a) 
    annotation(Line(origin={-30,36}, 
points={{-28,0},{28,0}}, 
color={95,95,95}, 
thickness=0.5));
  connect(revolute1.frame_b, gear1.frame_a) 
    annotation(Line(origin={-30,-44}, 
points={{-28,0},{28,0}}, 
color={95,95,95}, 
thickness=0.5));
  connect(revolute1.frame_a, world.frame_b) 
    annotation(Line(origin={-96,-44}, 
points={{18,0},{-18,0}}, 
color={95,95,95}, 
thickness=0.5));
  connect(revolute2.frame_a, fixed.frame_b) 
    annotation(Line(origin={-96,36}, 
points={{18,0},{-18,0}}, 
color={95,95,95}, 
thickness=0.5));
  connect(speed.w_ref, realExpression.y) 
    annotation(Line(origin={-96,-4}, 
points={{-4,0},{-17,0}}, 
color={0,0,127}));
  connect(speed.flange, revolute1.axis) 
    annotation(Line(origin={-73,-19}, 
points={{-5,15},{5,15},{5,-15}}, 
color={0,0,0}));
  connect(damper.flange_a, revolute2.support) 
    annotation(Line(origin={-84,57}, 
points={{6,11},{-10,11},{-10,-11},{10,-11}}, 
color={0,0,0}));
  connect(damper.flange_b, revolute2.axis) 
    annotation(Line(origin={-63,57}, 
points={{5,11},{15,11},{15,-11},{-5,-11}}, 
color={0,0,0}));
  connect(gear2.frame_GearContact2, gearContact.frame_z2) 
    annotation(Line(origin={8,16}, 
points={{0,10},{0,-10}}, 
color={95,95,95}, 
thickness=0.5));
  connect(gearContact.frame_z1, gear1.frame_GearContact1) 
    annotation(Line(origin={8,-24}, 
points={{0,10},{0,-10}}, 
color={95,95,95}, 
thickness=0.5));
  annotation(Documentation(link = "modelica://TYDriveline3D/Resources/html/Example/GearsDrive/GearTransmission.html"), 
    experiment(Algorithm=Dassl,InlineIntegrator=false,InlineStepSize=false,IntegratorStep=0.0001,Interval=0.01,StartTime=0,StopTime=10,Tolerance=1e-08), __MWORKS(ContinueSimConfig(SaveContinueFile="false",SaveBeforeStop="false",NumberBeforeStop=1,FixedContinueInterval="false",ContinueIntervalLength=10,ContinueTimeVector)), 
    Icon(coordinateSystem(extent = {{-100, -100}, {100, 100}}, 
    grid = {2, 2}), graphics = {Polygon(origin = {-3.55271e-15, 27}, 
    lineColor = {96, 96, 96}, 
    fillColor = {96, 96, 96}, 
    fillPattern = FillPattern.Solid, 
    points = {{-64, 1}, {0, 37}, {64, 1}, {0, -37}}), Line(origin = {3.55271e-15, -18}, 
    points = {{-62, 18}, {0, -18}, {62, 18}}, 
    color = {96, 96, 96}, 
    thickness = 5), Line(origin = {1.06581e-14, -46}, 
    points = {{-62, 18}, {0, -18}, {62, 18}}, 
    color = {96, 96, 96}, 
    thickness = 5)}),Protection(access=Access.nonPackageDuplicate),Diagram(coordinateSystem(extent={{-100,-100},{100,100}}, 
grid={2,2})));
  connect(body.frame_a, gear2.frame_a) 
  annotation(Line(origin={13,50}, 
points={{15,14},{-25,14},{-25,-14},{-15,-14}}, 
color={95,95,95}, 
thickness=0.5));
  connect(body.frame_b, helicalGear.frame_a) 
  annotation(Line(origin={60,64}, 
points={{-12,0},{14,0}}, 
color={95,95,95}, 
thickness=0.5));
  connect(revolute3.frame_a, helicalGear1.frame_a) 
  annotation(Line(origin={109,0}, 
points={{1,0},{-15,0}}, 
color={95,95,95}, 
thickness=0.5));
  connect(revolute3.frame_b, fixed1.frame_b) 
  annotation(Line(origin={135,0}, 
points={{-5,0},{5,0}}, 
color={95,95,95}, 
thickness=0.5));
  connect(helicalGear1.frame_GearContact1, helicalGearContact.frame_z1) 
  annotation(Line(origin={84,16}, 
points={{0,-6},{0,6}}, 
color={95,95,95}, 
thickness=0.5));
  connect(helicalGear.frame_GearContact2, helicalGearContact.frame_z2) 
  annotation(Line(origin={84,48}, 
points={{0,6},{0,-6}}, 
color={95,95,95}, 
thickness=0.5));
  end GearTransmission;