model BevelGear34X2
  annotation (cad_toolbox = true,cad_toolbox_group = true,cad_toolbox_id = "0:1:1:1./0:1:1:1:24.",cad_relativePath = "Visualizers/BevelGear34X2.dxf",cad_toolbox_icon = "BevelGear34X2_20250427172142.png",Diagram(coordinateSystem(extent = {{-300 ,-300},{300 ,300}}, 
grid = {2, 2})),Icon(coordinateSystem(extent = {{-300 ,-300},{300 ,300}}, 
grid = {2, 2}),graphics = {Rectangle(origin = {0, 0}, 
fillColor = {255, 255, 255}, 
fillPattern = FillPattern.Solid, 
lineThickness=5, 
borderPattern=BorderPattern.Engraved, 
extent = {{-300 ,-300},{300 ,300}}),Bitmap(extent = {{-297 ,-297},{297 ,297}}, 
fileName = "Visualizers/BevelGear34X2_20250427172142.png"),Text(origin = {0, 220}, 
extent = {{-150 ,100},{150 ,140}}, 
textString = "%name",textColor = {0, 0, 255}, 
horizontalAlignment = LinePattern.None),Text(origin = {362.5, 30}, 
extent = {{-52.5 ,-15},{52.5 ,15}}, 
textString = "Marker2",textColor = {128, 128, 128}, 
horizontalAlignment = TextAlignment.Left)}),cad_marker(name = "Marker2", 
is_ref = true, 
is_manual = false, 
positionX = -0.0126487394026, 
positionY = -0.00772733281367, 
positionZ = -0.06283598608669, 
rotationX = 0.36869307283948, 
rotationY = 0.65729195112986, 
rotationZ = 0.65729195112986, 
angle = 2.43513289925908));
  parameter String pkgName = "Default5";
  parameter String modelName = "GearUnit";
  TYMultibody.Bodies.Body body(m = 0.27827629214418,Ixx = 0.00012359716777,Iyy = 0.00009253423035,Izz = 0.00007403806794,Ixy = 0.00003027678618,Ixz = -0.00000000010634,Iyz = 0.0000000000639,shapeType= "modelica://" + pkgName + "/" + modelName + "/Visualizers/BevelGear34X2.dxf",r_shape = {0.01625353037091, 0.0099295661314, 0.06283598502049}) 
    annotation (cad_toolbox = true,Placement(transformation(origin = {0, 0},extent = {{-10 ,-10},{10 ,10}})));

  TYMultibody.Bodies.RigidTranslation Marker_Marker2(r = {0.00360479096832, 0.00220223331774, -0.0000000010662}) 
    annotation (cad_toolbox = true,Placement(transformation(origin = {45, 0},extent = {{-10 ,-10},{10 ,10}})));

  TYMultibody.Interfaces.Frame_b Marker2 
    annotation (cad_toolbox = true,Placement(transformation(origin = {200, 0},extent = {{84 ,-16},{116 ,16}})));

equation
  connect (Marker_Marker2.frame_a,body.frame_a) 
  annotation (cad_toolbox = true,Line(origin = {12.5, 0}, 
points = {{-22.5, 0},{22.5, 0},{22.5, 0}}, 
color = {95, 95, 95}, 
thickness = 0.5));

  connect (Marker_Marker2.frame_b,Marker2) 
  annotation (cad_toolbox = true,Line(origin = {177.5, 0}, 
points = {{122.5, 0},{-122.5, 0}}, 
color = {95, 95, 95}, 
thickness = 0.5));

end BevelGear34X2;