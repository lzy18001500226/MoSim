model Worm1_2_5
  annotation (cad_toolbox = true,cad_toolbox_group = true,cad_toolbox_id = "0:1:1:1./0:1:1:1:19.",cad_relativePath = "Visualizers/Worm1_2_5.dxf",cad_toolbox_icon = "Worm1_2_5_20250427172142.png",Diagram(coordinateSystem(extent = {{-300 ,-300},{300 ,300}}, 
grid = {2, 2})),Icon(coordinateSystem(extent = {{-300 ,-300},{300 ,300}}, 
grid = {2, 2}),graphics = {Rectangle(origin = {0, 0}, 
fillColor = {255, 255, 255}, 
fillPattern = FillPattern.Solid, 
lineThickness=5, 
borderPattern=BorderPattern.Engraved, 
extent = {{-300 ,-300},{300 ,300}}),Bitmap(extent = {{-297 ,-297},{297 ,297}}, 
fileName = "Visualizers/Worm1_2_5_20250427172142.png"),Text(origin = {0, 220}, 
extent = {{-150 ,100},{150 ,140}}, 
textString = "%name",textColor = {0, 0, 255}, 
horizontalAlignment = LinePattern.None),Text(origin = {362.5, 30}, 
extent = {{-52.5 ,-15},{52.5 ,15}}, 
textString = "Marker5",textColor = {128, 128, 128}, 
horizontalAlignment = TextAlignment.Left)}),cad_marker(name = "Marker5", 
is_ref = false, 
is_manual = false, 
positionX = 0.06921615238334, 
positionY = 0.06943979165121, 
positionZ = -0.04159, 
rotationX = -0.2684360347258, 
rotationY = 0.68115420253445, 
rotationZ = 0.68115420253445, 
angle = -2.61708552852018));
  parameter String pkgName = "Default5";
  parameter String modelName = "GearUnit";
  TYMultibody.Bodies.Body body(m = 0.18056464991736,Ixx = 0.00004316169673,Iyy = 0.00003966626088,Izz = 0.00007208714457,Ixy = 0.00003062498318,Ixz = -0.00000010461809,Iyz = 0.00000011735898,shapeType= "modelica://" + pkgName + "/" + modelName + "/Visualizers/Worm1_2_5.dxf",r_shape = {-0.08876791299957, -0.04847680211015, 0.04163792225967}) 
    annotation (cad_toolbox = true,Placement(transformation(origin = {0, 0},extent = {{-10 ,-10},{10 ,10}})));

  TYMultibody.Bodies.RigidTranslation Marker_Marker5(r = {-0.01955176061624, 0.02096298954106, 0.00004792225967}) 
    annotation (cad_toolbox = true,Placement(transformation(origin = {45, 0},extent = {{-10 ,-10},{10 ,10}})));

  TYMultibody.Interfaces.Frame_b Marker5 
    annotation (cad_toolbox = true,Placement(transformation(origin = {200, 0},extent = {{84 ,-16},{116 ,16}})));

equation
  connect (Marker_Marker5.frame_a,body.frame_a) 
  annotation (cad_toolbox = true,Line(origin = {12.5, 0}, 
points = {{-22.5, 0},{22.5, 0},{22.5, 0}}, 
color = {95, 95, 95}, 
thickness = 0.5));

  connect (Marker_Marker5.frame_b,Marker5) 
  annotation (cad_toolbox = true,Line(origin = {177.5, 0}, 
points = {{122.5, 0},{-122.5, 0}}, 
color = {95, 95, 95}, 
thickness = 0.5));

end Worm1_2_5;