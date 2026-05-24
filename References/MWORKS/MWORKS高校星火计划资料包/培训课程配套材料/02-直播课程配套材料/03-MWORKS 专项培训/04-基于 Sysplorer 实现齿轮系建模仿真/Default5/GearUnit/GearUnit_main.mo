model GearUnit_main
  annotation (cad_toolbox = true,cad_toolbox_model = true,cad_toolbox_icon = "GearUnit_main_20250427172057.png",Diagram(coordinateSystem(extent = {{-300 ,-300},{300 ,300}}, 
grid = {2, 2})),Icon(coordinateSystem(extent = {{-300 ,-300},{300 ,300}}, 
grid = {2, 2}),graphics = {Rectangle(origin = {0, 0}, 
fillColor = {255, 255, 255}, 
fillPattern = FillPattern.Solid, 
lineThickness=5, 
borderPattern=BorderPattern.Engraved, 
extent = {{-300 ,-300},{300 ,300}}),Bitmap(extent = {{-297 ,-297},{297 ,297}}, 
fileName = "Visualizers/GearUnit_main_20250427172057.png"),Text(origin = {0, 220}, 
extent = {{-150 ,100},{150 ,140}}, 
textString = "%name",textColor = {0, 0, 255}, 
horizontalAlignment = LinePattern.None)}));
Default5.GearUnit.Worm1_2_5 Worm1_2_5_1_1 
    annotation (cad_toolbox = true,Placement(transformation(origin={-44,-106}, 
extent={{-30,-30},{30,30}})));

Default5.GearUnit.BevelGear34X2 BevelGear34X2_1_1 
    annotation (cad_toolbox = true,Placement(transformation(origin={-38,0}, 
extent={{-30,-30},{30,30}})));

Default5.GearUnit.Fixed Fixed1_1 
    annotation (cad_toolbox = true,Placement(transformation(origin = {120, 0},extent = {{-30 ,-30},{30 ,30}})));

Default5.GearUnit.First First1 
    annotation (cad_toolbox = true,Placement(transformation(origin = {240, 0},extent = {{-30 ,-30},{30 ,30}})));

Default5.GearUnit.Second Second1 
    annotation (cad_toolbox = true,Placement(transformation(origin={-44,78}, 
extent={{-30,-30},{30,30}})));

  TYMultibody.Joints.Revolute Revolute6(n={-0.68222558634882, 0.73114174366604, 0},animation=false) 
    annotation (cad_toolbox = true,Placement(transformation(origin={60,-86}, 
extent={{-10,-10},{10,10}})));

  TYMultibody.Joints.Revolute Revolute4(n={0, 0, 1},animation=false,useAxisFlange=true) 
    annotation (cad_toolbox = true,Placement(transformation(origin = {180, 30},extent = {{-10 ,-10},{10 ,10}})));

  TYMultibody.Joints.Fixed Fixed1(r={-0.03056920367697, -0.01867525317285, -0.06283598608669}) 
    annotation (cad_toolbox = true,Placement(transformation(origin={204,-78}, 
extent={{-10,-10},{10,10}}, 
rotation=180)));

  TYMultibody.Joints.Revolute Revolute3(n={0.85335544163685, 0.52132954091322, 0},animation=false) 
    annotation (cad_toolbox = true,Placement(transformation(origin={60,0}, 
extent={{10,-10},{-10,10}})));

  TYMultibody.Joints.Revolute Revolute5(n={0, 0, 1},animation=false,useAxisFlange=true) 
    annotation (cad_toolbox = true,Placement(transformation(origin = {60, 30},extent = {{-10 ,-10},{10 ,10}})));

  inner TYMultibody.World world(n={0, -1, 0},animateWorld=false,animateGravity=false) 
    annotation (cad_toolbox = true,Placement(transformation(origin={-138,58}, 
extent={{-10,-10},{10,10}})));
  equation
  connect(Worm1_2_5_1_1.Marker5, Revolute6.frame_a) 
  annotation(Line(origin={40,0}, 
points={{-54,-106},{-12,-106},{-12,-86},{10,-86}}, 
color={95,95,95}, 
thickness=0.5),cad_toolbox=true);
  connect(Fixed1_1.Marker5, Revolute6.frame_b) 
  annotation(Line(origin={80,-7.5}, 
points={{10,-7.5},{0,-7.5},{0,-78.5},{-10,-78.5}}, 
color={95,95,95}, 
thickness=0.5),cad_toolbox=true);
  connect(Fixed1_1.Marker3, Revolute4.frame_a) 
  annotation(Line(origin={160,20}, 
points={{-10,-10},{6.4,-10},{6.4,10},{10,10}}, 
color={95,95,95}, 
thickness=0.5),cad_toolbox=true);
  connect(First1.Marker3, Revolute4.frame_b) 
  annotation(Line(origin={200,15}, 
points={{10,-15},{-6.4,-15},{-6.4,15},{-10,15}}, 
color={95,95,95}, 
thickness=0.5),cad_toolbox=true);
  connect(Fixed1_1.Marker2, Revolute3.frame_a) 
  annotation(Line(origin={80,0}, 
points={{10,0},{-10,0}}, 
color={95,95,95}, 
thickness=0.5),cad_toolbox=true);
  connect(BevelGear34X2_1_1.Marker2, Revolute3.frame_b) 
  annotation(Line(origin={40,45}, 
points={{-48,-45},{10,-45}}, 
color={95,95,95}, 
thickness=0.5),cad_toolbox=true);
  connect(Fixed1_1.Marker4, Revolute5.frame_b) 
  annotation(Line(origin={80,22.5}, 
points={{10,-7.5},{2,-7.5},{2,7.5},{-10,7.5}}, 
color={95,95,95}, 
thickness=0.5),cad_toolbox=true);
  connect(Second1.Marker4, Revolute5.frame_a) 
  annotation(Line(origin={40,105}, 
points={{-54,-27},{-6,-27},{-6,-75},{10,-75}}, 
color={95,95,95}, 
thickness=0.5),cad_toolbox=true);
  connect(Fixed1_1.Marker1, Fixed1.frame_b) 
  annotation(Line(origin={160,-20}, 
points={{-10,10},{20,10},{20,-58},{34,-58}}, 
color={95,95,95}, 
thickness=0.5),cad_toolbox=true);
  end GearUnit_main;