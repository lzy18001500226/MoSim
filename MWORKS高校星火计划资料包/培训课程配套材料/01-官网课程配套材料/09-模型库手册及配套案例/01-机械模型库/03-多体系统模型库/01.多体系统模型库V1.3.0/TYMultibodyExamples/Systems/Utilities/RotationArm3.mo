model RotationArm3 "转动臂3"
 annotation(Icon(coordinateSystem(extent={{-100,-100},{100,100}}, 
grid={2,2}),graphics = {Rectangle(origin={0,0}, 
fillColor={255,255,255}, 
fillPattern=FillPattern.Solid, 
lineThickness=5, 
borderPattern=BorderPattern.Engraved, 
extent={{-100,-100},{100,100}}), Text(origin={0,0}, 
lineColor={0,0,255}, 
extent={{-150,100},{150,140}}, 
textString="%name", 
textStyle={TextStyle.None}, 
textColor={0,0,255}), Bitmap(origin={0,0}, 
extent={{-97,-97},{97,97}}, 
fileName="modelica://TYMultibody/Resources/Visualizers/System_Robot/Part7_20241217153104.png", 
imageSource="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"
)}));

  TYMultibody.Bodies.Body body(m = 0.59077985152986,Ixx = 0.00029956228817,Iyy = 0.00029263699378,Izz = 0.00026403243682,Ixy = 0.00000096277882,Ixz = -0.00001852275371,Iyz = 0.00001526157788,shapeType= "Resources/Visualizers/System_Robot/Part7.dxf",r_shape = {0.56874220019276, -0.1777050042041, -0.30656916893963}) 
    annotation (cad_toolbox = true,Placement(transformation(origin={44,0}, 
extent={{-10,-10},{10,10}}, 
rotation=360)));

  TYMultibody.Bodies.RigidTranslation Marker_Marker7(r = {-0.00007209825556, 0.00004831254131, -0.00004493984061}) 
    annotation (cad_toolbox = true,Placement(transformation(origin = {-45, 0},extent = {{10 ,-10},{-10 ,10}})));

  TYMultibody.Interfaces.Frame_b Marker7 
    annotation (cad_toolbox = true,Placement(transformation(origin={0,0}, 
extent={{-116,-16},{-84,16}})));

  TYMultibody.Bodies.RigidTranslation Marker_Marker8(r = {-0.03219196729392, 0.01299124859432, 0.03017067794603}) 
    annotation (cad_toolbox = true,Placement(transformation(origin={56,60}, 
extent={{10,-10},{-10,10}}, 
rotation=180)));

  TYMultibody.Interfaces.Frame_b Marker8 
    annotation (cad_toolbox = true,Placement(transformation(origin={200,60}, 
extent={{-116,-16},{-84,16}})));

  TYMultibody.Bodies.RigidTranslation Marker_Marker9(r = {-0.0093405369549, -0.01896602983505, -0.04084616490814}) 
    annotation (cad_toolbox = true,Placement(transformation(origin={60,-66}, 
extent={{10,-10},{-10,10}}, 
rotation=180)));

  TYMultibody.Interfaces.Frame_b Marker9 
    annotation (cad_toolbox = true,Placement(transformation(origin={0,-60}, 
extent={{84,-16},{116,16}})));

equation
  connect (Marker_Marker7.frame_a,body.frame_a) 
  annotation (cad_toolbox = true,Line(origin={-22.5,0}, 
points={{-12.5,0},{56.5,0}}, 
color={95,95,95}, 
thickness=0.5));

  connect (Marker_Marker7.frame_b,Marker7) 
  annotation (cad_toolbox = true,Line(origin = {-177.5, -50}, 
points = {{-122.5, -50},{122.5, 50}}, 
color = {95, 95, 95}, 
thickness = 0.5));

  connect (Marker_Marker9.frame_a,body.frame_a) 
  annotation (cad_toolbox = true,Line(origin={-22.5,-75}, 
points={{72.5,9},{24.5,9},{24.5,75},{56.5,75}}, 
color={95,95,95}, 
thickness=0.5));

  connect (Marker_Marker9.frame_b,Marker9) 
  annotation (cad_toolbox = true,Line(origin={122.5,-75}, 
points={{-52.5,9},{-22.5,9},{-22.5,15}}, 
color={95,95,95}, 
thickness=0.5));

  connect (Marker_Marker8.frame_a,body.frame_a) 
  annotation (cad_toolbox = true,Line(origin={-22.5,75}, 
points={{68.5,-15},{24.5,-15},{24.5,-75},{56.5,-75}}, 
color={95,95,95}, 
thickness=0.5));

  connect (Marker_Marker8.frame_b,Marker8) 
  annotation (cad_toolbox = true,Line(origin={-177.5,125}, 
points={{243.5,-65},{277.5,-65}}, 
color={95,95,95}, 
thickness=0.5));

end RotationArm3;