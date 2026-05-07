model Fixed
  annotation (cad_toolbox = true,cad_toolbox_group = true,cad_toolbox_id = "31681626-20fa-49cc-a6f0-8da8b552fe80",cad_relativePath = "Visualizers/Fixed.dxf",cad_toolbox_icon = "Fixed_20250427172142.png",Diagram(coordinateSystem(extent = {{-300 ,-300},{300 ,300}}, 
grid = {2, 2})),Icon(coordinateSystem(extent = {{-300 ,-300},{300 ,300}}, 
grid = {2, 2}),graphics = {Rectangle(origin = {0, 0}, 
fillColor = {255, 255, 255}, 
fillPattern = FillPattern.Solid, 
lineThickness=5, 
borderPattern=BorderPattern.Engraved, 
extent = {{-300 ,-300},{300 ,300}}),Bitmap(extent = {{-297 ,-297},{297 ,297}}, 
fileName = "Visualizers/Fixed_20250427172142.png"),Text(origin = {0, 220}, 
extent = {{-150 ,100},{150 ,140}}, 
textString = "%name",textColor = {0, 0, 255}, 
horizontalAlignment = LinePattern.None),Text(origin = {-362.5, 30}, 
extent = {{-52.5 ,-15},{52.5 ,15}}, 
textString = "Marker2",textColor = {128, 128, 128}, 
horizontalAlignment = TextAlignment.Right),Text(origin = {362.5, -70}, 
extent = {{-52.5 ,-15},{52.5 ,15}}, 
textString = "Marker1",textColor = {128, 128, 128}, 
horizontalAlignment = TextAlignment.Left),Text(origin = {362.5, 130}, 
extent = {{-52.5 ,-15},{52.5 ,15}}, 
textString = "Marker3",textColor = {128, 128, 128}, 
horizontalAlignment = TextAlignment.Left),Text(origin = {-362.5, -120}, 
extent = {{-52.5 ,-15},{52.5 ,15}}, 
textString = "Marker5",textColor = {128, 128, 128}, 
horizontalAlignment = TextAlignment.Right),Text(origin = {-362.5, 180}, 
extent = {{-52.5 ,-15},{52.5 ,15}}, 
textString = "Marker4",textColor = {128, 128, 128}, 
horizontalAlignment = TextAlignment.Right)}),cad_marker(name = "Marker3", 
is_ref = false, 
is_manual = false, 
positionX = 0, 
positionY = 0, 
positionZ = 0.045, 
rotationX = 0, 
rotationY = 0, 
rotationZ = -1, 
angle = 1.5707963267949),cad_marker(name = "Marker5", 
is_ref = true, 
is_manual = false, 
positionX = 0.06921615238334, 
positionY = 0.06943979165121, 
positionZ = -0.04159, 
rotationX = -0.2684360347258, 
rotationY = 0.68115420253445, 
rotationZ = 0.68115420253445, 
angle = -2.61708552852018),cad_marker(name = "Marker1", 
is_ref = false, 
is_manual = false, 
positionX = -0.03056920367697, 
positionY = -0.01867525317285, 
positionZ = -0.06283598608669, 
rotationX = 0, 
rotationY = 0, 
rotationZ = 1, 
angle = 0),cad_marker(name = "Marker2", 
is_ref = false, 
is_manual = false, 
positionX = -0.0126487394026, 
positionY = -0.00772733281367, 
positionZ = -0.06283598608669, 
rotationX = 0.36869307283948, 
rotationY = 0.65729195112986, 
rotationZ = 0.65729195112986, 
angle = 2.43513289925908),cad_marker(name = "Marker4", 
is_ref = true, 
is_manual = false, 
positionX = 0.05411510501839, 
positionY = 0.01790406123897, 
positionZ = 0.0385, 
rotationX = 0, 
rotationY = 0, 
rotationZ = -1, 
angle = 1.5707963267949));
  parameter String pkgName = "Default5";
  parameter String modelName = "GearUnit";
  TYMultibody.Bodies.Body body(m = 0.11200776631496,Ixx = 0.00011741686376,Iyy = 0.00059884786034,Izz = 0.00058423150191,Ixy = -0.00015983066874,Ixz = -0.00002723542955,Iyz = -0.00007483971454,shapeType= "modelica://" + pkgName + "/" + modelName + "/Visualizers/Fixed.dxf",r_shape = {-0.03546693226852, -0.00198699270992, 0.0483742849956}) 
    annotation (cad_toolbox = true,Placement(transformation(origin = {0, 0},extent = {{-10 ,-10},{10 ,10}})));

  TYMultibody.Bodies.RigidTranslation Marker_Marker3(r = {-0.03546693226852, -0.00198699270992, 0.0933742849956}) 
    annotation (cad_toolbox = true,Placement(transformation(origin = {45, 100},extent = {{-10 ,-10},{10 ,10}})));

  TYMultibody.Interfaces.Frame_b Marker3 
    annotation (cad_toolbox = true,Placement(transformation(origin = {200, 100},extent = {{84 ,-16},{116 ,16}})));

  TYMultibody.Bodies.RigidTranslation Marker_Marker5(r = {0.03374922011481, 0.0674527989413, 0.0067842849956}) 
    annotation (cad_toolbox = true,Placement(transformation(origin = {-45, -150},extent = {{10 ,-10},{-10 ,10}})));

  TYMultibody.Interfaces.Frame_b Marker5 
    annotation (cad_toolbox = true,Placement(transformation(origin = {-200, -150},extent = {{-116 ,-16},{-84 ,16}})));

  TYMultibody.Bodies.RigidTranslation Marker_Marker1(r = {-0.06603613594549, -0.02066224588276, -0.01446170109109}) 
    annotation (cad_toolbox = true,Placement(transformation(origin = {45, -100},extent = {{-10 ,-10},{10 ,10}})));

  TYMultibody.Interfaces.Frame_b Marker1 
    annotation (cad_toolbox = true,Placement(transformation(origin = {200, -100},extent = {{84 ,-16},{116 ,16}})));

  TYMultibody.Bodies.RigidTranslation Marker_Marker2(r = {-0.04811567167112, -0.00971432552359, -0.01446170109109}) 
    annotation (cad_toolbox = true,Placement(transformation(origin = {-45, 0},extent = {{10 ,-10},{-10 ,10}})));

  TYMultibody.Interfaces.Frame_b Marker2 
    annotation (cad_toolbox = true,Placement(transformation(origin = {-200, 0},extent = {{-116 ,-16},{-84 ,16}})));

  TYMultibody.Bodies.RigidTranslation Marker_Marker4(r = {0.01864817274987, 0.01591706852905, 0.0868742849956}) 
    annotation (cad_toolbox = true,Placement(transformation(origin = {-45, 150},extent = {{10 ,-10},{-10 ,10}})));

  TYMultibody.Interfaces.Frame_b Marker4 
    annotation (cad_toolbox = true,Placement(transformation(origin = {-200, 150},extent = {{-116 ,-16},{-84 ,16}})));

equation
  connect (Marker_Marker2.frame_a,body.frame_a) 
  annotation (cad_toolbox = true,Line(origin = {-22.5, 0}, 
points = {{12.5, 0},{-12.5, 0}}, 
color = {95, 95, 95}, 
thickness = 0.5));

  connect (Marker_Marker2.frame_b,Marker2) 
  annotation (cad_toolbox = true,Line(origin = {-177.5, 0}, 
points = {{-122.5, 0},{122.5, 0}}, 
color = {95, 95, 95}, 
thickness = 0.5));

  connect (Marker_Marker1.frame_a,body.frame_a) 
  annotation (cad_toolbox = true,Line(origin = {12.5, -50}, 
points = {{-22.5, 50},{22.5, 50},{22.5, -50}}, 
color = {95, 95, 95}, 
thickness = 0.5));

  connect (Marker_Marker1.frame_b,Marker1) 
  annotation (cad_toolbox = true,Line(origin = {177.5, -100}, 
points = {{122.5, 0},{-122.5, 0}}, 
color = {95, 95, 95}, 
thickness = 0.5));

  connect (Marker_Marker3.frame_a,body.frame_a) 
  annotation (cad_toolbox = true,Line(origin = {12.5, 50}, 
points = {{-22.5, -50},{22.5, -50},{22.5, 50}}, 
color = {95, 95, 95}, 
thickness = 0.5));

  connect (Marker_Marker3.frame_b,Marker3) 
  annotation (cad_toolbox = true,Line(origin = {177.5, 100}, 
points = {{122.5, 0},{-122.5, 0}}, 
color = {95, 95, 95}, 
thickness = 0.5));

  connect (Marker_Marker5.frame_a,body.frame_a) 
  annotation (cad_toolbox = true,Line(origin = {-22.5, -75}, 
points = {{12.5, 75},{12.5, -75},{-12.5, -75}}, 
color = {95, 95, 95}, 
thickness = 0.5));

  connect (Marker_Marker5.frame_b,Marker5) 
  annotation (cad_toolbox = true,Line(origin = {-177.5, -150}, 
points = {{-122.5, 0},{122.5, 0}}, 
color = {95, 95, 95}, 
thickness = 0.5));

  connect (Marker_Marker4.frame_a,body.frame_a) 
  annotation (cad_toolbox = true,Line(origin = {-22.5, 75}, 
points = {{12.5, -75},{12.5, 75},{-12.5, 75}}, 
color = {95, 95, 95}, 
thickness = 0.5));

  connect (Marker_Marker4.frame_b,Marker4) 
  annotation (cad_toolbox = true,Line(origin = {-177.5, 150}, 
points = {{-122.5, 0},{122.5, 0}}, 
color = {95, 95, 95}, 
thickness = 0.5));

end Fixed;