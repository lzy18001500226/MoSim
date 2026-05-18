model Ship "无人船视景"
  Real x annotation (Dialog(group = "位姿信息"));
  Real y annotation (Dialog(group = "位姿信息"));
  Real z annotation (Dialog(group = "位姿信息"));
  Real phi annotation (Dialog(group = "位姿信息"));
  Real theta annotation (Dialog(group = "位姿信息"));
  Real psi annotation (Dialog(group = "位姿信息"));



  annotation (Diagram(coordinateSystem(extent={{-100,-100},{120,89.5537}}, 
grid={2,2})), 
    Icon(coordinateSystem(extent={{-100,-100},{100,100}}, 
grid={2,2}),graphics = {Bitmap(origin={0,0}, 
extent={{-100,-100},{100,100}}, 
fileName="modelica://USV/Resources/Icons/%E6%97%A0%E4%BA%BA%E8%89%87%E6%9C%AC%E4%BD%93.svg"), Text(origin={5.25,-147.35}, 
lineColor={0,0,0}, 
extent={{-60,45},{60,-45}}, 
textString="USV Animation", 
textStyle={TextStyle.None}, 
textColor={0,0,0}, 
horizontalAlignment=LinePattern.None)}),Protection(access=Access.diagram));
  Modelica.Mechanics.MultiBody.Joints.Prismatic prismatic(useAxisFlange = true, animation = false) 
    annotation (Placement(transformation(origin={-12.6686,-67.4489}, 
extent={{-10,-10},{10,10}})));
  Modelica.Mechanics.MultiBody.Joints.Prismatic prismatic1(n = {0, -1, 0}, useAxisFlange = true, animation = false) 
    annotation (Placement(transformation(origin={43.3314,-67.4489}, 
extent={{-10,-10},{10,10}})));
  Modelica.Mechanics.MultiBody.Joints.Prismatic prismatic2(n = {0, 0, -1}, useAxisFlange = true, animation = false) 
    annotation (Placement(transformation(origin={99.3314,-67.4489}, 
extent={{-10,-10},{10,10}})));
  Modelica.Mechanics.MultiBody.Joints.Revolute revolute(n = {1, 0, 0}, useAxisFlange = true, animation = false) 
    annotation (Placement(transformation(origin={99.3314,-7.44891}, 
extent={{10,-10},{-10,10}})));
  Modelica.Mechanics.MultiBody.Joints.Revolute revolute1(n = {0, 1, 0}, useAxisFlange = true, animation = false) 
    annotation (Placement(transformation(origin={43.3314,-7.44891}, 
extent={{10,-10},{-10,10}})));
  Modelica.Mechanics.MultiBody.Joints.Revolute revolute2(useAxisFlange = true, animation = false) 
    annotation (Placement(transformation(origin={-12.6686,-7.44891}, 
extent={{10,-10},{-10,10}})));
  Modelica.Mechanics.Translational.Sources.Position position 
    annotation (Placement(transformation(origin={-22.6686,-43.4489}, 
extent={{-10,-10},{10,10}})));
  Modelica.Mechanics.Translational.Sources.Position position1 
    annotation (Placement(transformation(origin={31.3314,-43.4489}, 
extent={{-10,-10},{10,10}})));
  Modelica.Mechanics.Translational.Sources.Position position2 
    annotation (Placement(transformation(origin={85.3314,-43.4489}, 
extent={{-10,-10},{10,10}})));
  Modelica.Mechanics.Rotational.Sources.Position position3 
    annotation (Placement(transformation(origin={9.3314,18.5511}, 
extent={{10,-10},{-10,10}})));
  Modelica.Mechanics.Rotational.Sources.Position position4 
    annotation (Placement(transformation(origin={65.3314,18.5511}, 
extent={{10,-10},{-10,10}})));
  Modelica.Mechanics.Rotational.Sources.Position position5 
    annotation (Placement(transformation(origin={121.331,18.5511}, 
extent={{10,-10},{-10,10}})));
  Modelica.Mechanics.MultiBody.Parts.BodyShape bodyShape(shapeType = "modelica://USV/Resources/Animation/WRT_small.STL", extra = 1, length = 0.001 / 3, width = 0.001 / 3, height = 0.001 / 3,r={0,0,0},r_CM={0,0,0},m=1,color={255,0,0}) 
    annotation (Placement(transformation(origin={43.3314,58.5511}, 
extent={{-10,-10},{10,10}})));
  Modelica.Mechanics.MultiBody.Parts.Fixed fixed(animation = false) 
    annotation (Placement(transformation(origin={-86.6686,-67.4489}, 
extent={{-10,-10},{10,10}})));
  Modelica.Mechanics.MultiBody.Parts.FixedRotation fixedRotation(rotationType = Modelica.Mechanics.MultiBody.Types.RotationTypes.RotationAxis, angle = 0) 
    annotation (Placement(transformation(origin={-49.6686,-67.4489}, 
extent={{-10,-10},{10,10}})));
  inner Modelica.Mechanics.MultiBody.World world 
    annotation (Placement(transformation(origin={-88.8686,45.0011}, 
extent={{-10,-10},{10,10}})));
equation
  // x = 0;
  // y = 0;
  // z = 0;
  // phi = 0;
  // theta = 0;
  // psi = 0;
  position.s_ref = x;
  position1.s_ref = y;
  position2.s_ref = z;
  position5.phi_ref = phi;
  position4.phi_ref = theta;
  position3.phi_ref = psi;

  connect(prismatic.frame_b, prismatic1.frame_a) 
    annotation (Line(origin={15.3314,-67.4489}, 
points={{-18,0},{18,0}}, 
color={95,95,95}, 
thickness=0.5));
  connect(prismatic1.frame_b, prismatic2.frame_a) 
    annotation (Line(origin={71.3314,-67.4489}, 
points={{-18,0},{18,0}}, 
color={95,95,95}, 
thickness=0.5));
  connect(prismatic2.frame_b, revolute.frame_a) 
    annotation (Line(origin={116.331,-46.4489}, 
points={{-7,-21},{7,-21},{7,39},{-7,39}}, 
color={95,95,95}, 
thickness=0.5));
  connect(revolute.frame_b, revolute1.frame_a) 
    annotation (Line(origin={71.3314,-7.44891}, 
points={{18,0},{-18,0}}, 
color={95,95,95}, 
thickness=0.5));
  connect(revolute2.frame_a, revolute1.frame_b) 
    annotation (Line(origin={15.3314,-7.44891}, 
points={{-18,1.42109e-14},{18,1.42109e-14},{18,0}}, 
color={95,95,95}, 
thickness=0.5));
  connect(position.flange, prismatic.axis) 
    annotation (Line(origin={-8.6686,-52.4489}, 
points={{-4,9},{4,9},{4,-9}}, 
color={0,127,0}));
  connect(position1.flange, prismatic1.axis) 
    annotation (Line(origin={46.3314,-52.4489}, 
points={{-5,9},{5,9},{5,-9}}, 
color={0,127,0}));
  connect(position2.flange, prismatic2.axis) 
    annotation (Line(origin={101.331,-52.4489}, 
points={{-6,9},{6,9},{6,-9}}, 
color={0,127,0}));
  connect(position3.flange, revolute2.axis) 
    annotation (Line(origin={-15.6686,10.5511}, 
points={{15,8},{3,8},{3,-8}}, 
color={0,0,0}));
  connect(position4.flange, revolute1.axis) 
    annotation (Line(origin={49.3314,10.5511}, 
points={{6,8},{-6,8},{-6,-8}}, 
color={0,0,0}));
  connect(position5.flange, revolute.axis) 
    annotation (Line(origin={105.331,10.5511}, 
points={{6,8},{-6,8},{-6,-8}}, 
color={0,0,0}));
  connect(revolute2.frame_b, bodyShape.frame_a) 
    annotation (Line(origin={-2.6686,27.5511}, 
points={{-20,-35},{-36,-35},{-36,31},{36,31}}, 
color={95,95,95}, 
thickness=0.5));
  connect(fixed.frame_b, fixedRotation.frame_a) 
    annotation (Line(origin={-67.6686,-67.4489}, 
points={{-9,0},{8,0}}, 
color={95,95,95}, 
thickness=0.5));
  connect(prismatic.frame_a, fixedRotation.frame_b) 
    annotation (Line(origin={-30.6686,-67.4489}, 
points={{8,0},{-9,0}}, 
color={95,95,95}, 
thickness=0.5));
end Ship;