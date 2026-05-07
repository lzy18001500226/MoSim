model First
  annotation (cad_toolbox = true,cad_toolbox_group = true,cad_toolbox_id = "ec791868-bb99-4819-8beb-e27a53065c29",cad_relativePath = "Visualizers/First.dxf",cad_toolbox_icon = "First_20250427172142.png",Diagram(coordinateSystem(extent = {{-300 ,-300},{300 ,300}}, 
grid = {2, 2})),Icon(coordinateSystem(extent = {{-300 ,-300},{300 ,300}}, 
grid = {2, 2}),graphics = {Rectangle(origin = {0, 0}, 
fillColor = {255, 255, 255}, 
fillPattern = FillPattern.Solid, 
lineThickness=5, 
borderPattern=BorderPattern.Engraved, 
extent = {{-300 ,-300},{300 ,300}}),Bitmap(extent = {{-297 ,-297},{297 ,297}}, 
fileName = "Visualizers/First_20250427172142.png"),Text(origin = {0, 220}, 
extent = {{-150 ,100},{150 ,140}}, 
textString = "%name",textColor = {0, 0, 255}, 
horizontalAlignment = LinePattern.None),Text(origin = {-362.5, 30}, 
extent = {{-52.5 ,-15},{52.5 ,15}}, 
textString = "Marker3",textColor = {128, 128, 128}, 
horizontalAlignment = TextAlignment.Right)}),cad_marker(name = "Marker3", 
is_ref = true, 
is_manual = false, 
positionX = 0, 
positionY = 0, 
positionZ = 0.045, 
rotationX = 0, 
rotationY = 0, 
rotationZ = -1, 
angle = 1.5707963267949));
  parameter String pkgName = "Default5";
  parameter String modelName = "GearUnit";
  TYMultibody.Bodies.Body body(m = 0.92302703012532,Ixx = 0.00045321318368,Iyy = 0.00045321318799,Izz = 0.00049503174839,Ixy = -0.00000000000017,Ixz = 0.00000000002843,Iyz = 0.00000000004917,shapeType= "modelica://" + pkgName + "/" + modelName + "/Visualizers/First.dxf",r_shape = {-0.00000000609625, 0.00000000971598, -0.01143099005937}) 
    annotation (cad_toolbox = true,Placement(transformation(origin = {0, 0},extent = {{-10 ,-10},{10 ,10}})));

  TYMultibody.Bodies.RigidTranslation Marker_Marker3(r = {-0.00000000609625, 0.00000000971598, 0.03356900994063}) 
    annotation (cad_toolbox = true,Placement(transformation(origin = {-45, 0},extent = {{10 ,-10},{-10 ,10}})));

  TYMultibody.Interfaces.Frame_b Marker3 
    annotation (cad_toolbox = true,Placement(transformation(origin = {-200, 0},extent = {{-116 ,-16},{-84 ,16}})));

equation
  connect (Marker_Marker3.frame_a,body.frame_a) 
  annotation (cad_toolbox = true,Line(origin = {-22.5, 0}, 
points = {{12.5, 0},{-12.5, 0}}, 
color = {95, 95, 95}, 
thickness = 0.5));

  connect (Marker_Marker3.frame_b,Marker3) 
  annotation (cad_toolbox = true,Line(origin = {-177.5, 0}, 
points = {{-122.5, 0},{122.5, 0}}, 
color = {95, 95, 95}, 
thickness = 0.5));

end First;