model Second
  annotation (cad_toolbox = true,cad_toolbox_group = true,cad_toolbox_id = "b76c971b-10d2-42d6-a470-786e9b821169",cad_relativePath = "Visualizers/Second.dxf",cad_toolbox_icon = "Second_20250427172142.png",Diagram(coordinateSystem(extent = {{-300 ,-300},{300 ,300}}, 
grid = {2, 2})),Icon(coordinateSystem(extent = {{-300 ,-300},{300 ,300}}, 
grid = {2, 2}),graphics = {Rectangle(origin = {0, 0}, 
fillColor = {255, 255, 255}, 
fillPattern = FillPattern.Solid, 
lineThickness=5, 
borderPattern=BorderPattern.Engraved, 
extent = {{-300 ,-300},{300 ,300}}),Bitmap(extent = {{-297 ,-297},{297 ,297}}, 
fileName = "Visualizers/Second_20250427172142.png"),Text(origin = {0, 220}, 
extent = {{-150 ,100},{150 ,140}}, 
textString = "%name",textColor = {0, 0, 255}, 
horizontalAlignment = LinePattern.None),Text(origin = {362.5, 30}, 
extent = {{-52.5 ,-15},{52.5 ,15}}, 
textString = "Marker4",textColor = {128, 128, 128}, 
horizontalAlignment = TextAlignment.Left)}),cad_marker(name = "Marker4", 
is_ref = false, 
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
  TYMultibody.Bodies.Body body(m = 1.0402610683217,Ixx = 0.00119903114407,Iyy = 0.00119902725967,Izz = 0.00048853512555,Ixy = -0.00000000257337,Ixz = 0.00000000882419,Iyz = 0.00000000447767,shapeType= "modelica://" + pkgName + "/" + modelName + "/Visualizers/Second.dxf",r_shape = {-0.05411459597685, -0.01790304454727, 0.02141683803699}) 
    annotation (cad_toolbox = true,Placement(transformation(origin = {0, 0},extent = {{-10 ,-10},{10 ,10}})));

  TYMultibody.Bodies.RigidTranslation Marker_Marker4(r = {0.00000050904154, 0.0000010166917, 0.05991683803699}) 
    annotation (cad_toolbox = true,Placement(transformation(origin = {45, 0},extent = {{-10 ,-10},{10 ,10}})));

  TYMultibody.Interfaces.Frame_b Marker4 
    annotation (cad_toolbox = true,Placement(transformation(origin = {200, 0},extent = {{84 ,-16},{116 ,16}})));

equation
  connect (Marker_Marker4.frame_a,body.frame_a) 
  annotation (cad_toolbox = true,Line(origin = {12.5, 0}, 
points = {{-22.5, 0},{22.5, 0},{22.5, 0}}, 
color = {95, 95, 95}, 
thickness = 0.5));

  connect (Marker_Marker4.frame_b,Marker4) 
  annotation (cad_toolbox = true,Line(origin = {177.5, 0}, 
points = {{122.5, 0},{-122.5, 0}}, 
color = {95, 95, 95}, 
thickness = 0.5));

end Second;