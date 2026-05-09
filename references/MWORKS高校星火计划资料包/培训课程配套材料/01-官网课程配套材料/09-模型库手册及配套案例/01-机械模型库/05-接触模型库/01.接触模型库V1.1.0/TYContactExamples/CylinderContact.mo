model CylinderContact "脚手架碰撞模拟"
  Modelica.Mechanics.MultiBody.Joints.FreeMotion freeMotion1(animation = false, 
    w_rel_a_fixed = false, 
    enforceStates = false, 
    angles_fixed = true, 
    angles_start = {0, 0, 0}, 
    r_rel_a(start = {0, 0.1, -0.01}, each fixed = true)) 
    annotation(Placement(transformation(origin = {-42.0, 22.0}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYMultibody.Bodies.Body cylinder1(m = 2) 
    annotation(Placement(transformation(origin = {0.0, 22.0}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYContact.LineContact.CylinderCylinder_LineContact cylinderToCylinder_LineContact1(diameter_Cy1 = 0.02, length_Cy1 = 0.04, diameter_Cy2 = 0.02, length_Cy2 = 0.05, ContactOut = true, exact = false, k = 1e8, d = 5e4, n1 = 1, n2 = 0, p_max = 0.001, mue_k = 0.1, mue_s = 0.1, mue_r = 0, color1 = {0, 170, 0}, color2 = {85, 255, 255}) 
    annotation(Placement(transformation(origin = {42.00000000000001, 21.99999999999998}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYMultibody.Bodies.RigidTransform rigidTransform 
    annotation(Placement(transformation(origin = {-42.000000000000014, -18.0}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  inner TYMultibody.World world(animateWorld = false, animateGravity = true) 
    annotation(Placement(transformation(origin = {-106.0, 22.0}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYContact.LineContact.CylinderCylinder_CombinedContact cylinderToCylinder_CombinedContact1(diameter_Cy1 = 0.02, length_Cy1 = 0.04, diameter_Cy2 = 0.02, length_Cy2 = 0.1, ContactOut = true, exact = false, d = 3000, n1 = 1, n2 = 0, color1 = {255, 0, 0}, color2 = {0, 0, 255}) 
    annotation(Placement(transformation(origin = {96.0, 49.99999999999999}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYMultibody.Bodies.RigidTransform rigidTransform1(r = {0, -0.2, -0.25}, rotationType = TYMultibody.Types.RotationTypes.RotationAxis, n = {0, 1, 0}, angle = 90) 
    annotation(Placement(transformation(origin = {-42.000000000000014, -58.00000000000001}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYMultibody.Bodies.Body cylinder2(m = 2) 
    annotation(Placement(transformation(origin = {-1.7763568394002505e-15, -18.000000000000007}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYMultibody.Bodies.Body cylinder3(m = 2) 
    annotation(Placement(transformation(origin = {-1.7763568394002505e-15, -58.0}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
equation
  annotation(
    Icon(coordinateSystem(extent = {{-100.0, -100.0}, {100.0, 100.0}}, 
    grid = {2.0, 2.0}), graphics = {Polygon(origin = {-7.105427357601002e-15, 33.0}, 
    lineColor = {96, 96, 96}, 
    fillColor = {96, 96, 96}, 
    fillPattern = FillPattern.Solid, 
    points = {{-64.0, 1.0}, {0.0, 37.0}, {64.0, 1.0}, {0.0, -37.0}}), Line(origin = {0.0, -12.0}, 
    points = {{-62.0, 18.0}, {0.0, -18.0}, {62.0, 18.0}}, 
    color = {96, 96, 96}, 
    thickness = 5.0), Line(origin = {7.105427357601002e-15, -39.99999999999999}, 
    points = {{-62.0, 18.0}, {0.0, -18.0}, {62.0, 18.0}}, 
    color = {96, 96, 96}, 
    thickness = 5.0)}),__MWORKS(ResultViewerManager(resultViewers={
ResultViewer(name="1", executeTrigger=executeTrigger.SimulationFinished, commands={
CreatePlot(id=1, x_display_unit="s", legend_layout=1, left_title_type=2, left_title="位移[m]", bottom_title_type=2, bottom_title="时间/s", fix_time_range_value=0, zoom_x=(0, 0.5), zoom_y_l=(-0.25, 0.15)), 
Plot(y=["cylinder1.r_OG_0[2]"], colors=["4278190335"]), 
CreatePlot(id=-1, x_display_unit="s", legend_layout=1, left_title_type=2, left_title="位移[m]", bottom_title_type=2, bottom_title="时间/s", fix_time_range_value=0, sub_plot=(2, 1), zoom_x=(0, 0.5), zoom_y_l=(-0.35, 0)), 
Plot(y=["cylinder1.r_OG_0[3]"], colors=["4278190335"]), 
CreatePlot(id=-1, x_display_unit="s", legend_layout=1, left_title_type=2, left_title="接触力[N]", bottom_title_type=2, bottom_title="时间/s", fix_time_range_value=0, sub_plot=(3, 1), zoom_x=(0, 0.5), zoom_y_l=(-5000, 25000)), 
Plot(y=["cylinder1.frame_b.f[2]"], colors=["4278190335"])})
})));
  connect(freeMotion1.frame_b, cylinder1.frame_a) 
    annotation(Line(origin = {-20.999999999999993, 22.0}, 
    points = {{-11.000000000000007, 0.0}, {10.999999999999993, 0.0}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(cylinder1.frame_b, cylinderToCylinder_LineContact1.frame_a) 
    annotation(Line(origin = {21.000000000000007, 22.0}, 
    points = {{-11.000000000000007, 0.0}, {11.0, -2.1316282072803006e-14}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(freeMotion1.frame_a, world.frame_b) 
    annotation(Line(origin = {-74.0, 22.0}, 
    points = {{22.0, 0.0}, {-22.0, 0.0}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(world.frame_b, rigidTransform.frame_a) 
    annotation(Line(origin = {-74.0, 2.0}, 
    points = {{-22.0, 20.0}, {-2.0, 20.0}, {-2.0, -20.0}, {21.999999999999986, -20.0}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(cylinder1.frame_b, cylinderToCylinder_CombinedContact1.frame_a) 
    annotation(Line(origin = {53.0, 25.0}, 
    points = {{-43.0, -3.0}, {-33.0, -3.0}, {-33.0, 24.999999999999993}, {33.0, 24.999999999999993}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(world.frame_b, rigidTransform1.frame_a) 
    annotation(Line(origin = {-74.0, -19.0}, 
    points = {{-22.0, 41.0}, {-2.0, 41.0}, {-2.0, -39.00000000000001}, {21.999999999999986, -39.00000000000001}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(cylinderToCylinder_LineContact1.frame_b, cylinder2.frame_b) 
    annotation(Line(origin = {39.0, 2.0}, 
    points = {{13.000000000000007, 19.99999999999998}, {29.0, 19.99999999999998}, {29.0, -20.000000000000007}, {-29.0, -20.000000000000007}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(cylinder2.frame_a, rigidTransform.frame_b) 
    annotation(Line(origin = {-21.0, -18.0}, 
    points = {{10.999999999999998, -7.105427357601002e-15}, {-11.000000000000014, 0.0}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(cylinderToCylinder_CombinedContact1.frame_b, cylinder3.frame_b) 
    annotation(Line(origin = {77.0, -4.0}, 
    points = {{29.0, 53.99999999999999}, {67.0, 53.99999999999999}, {67.0, -54.0}, {-67.0, -54.0}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(cylinder3.frame_a, rigidTransform1.frame_b) 
    annotation(Line(origin = {-21.0, -58.0}, 
    points = {{10.999999999999998, 0.0}, {-11.000000000000014, -7.105427357601002e-15}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  annotation(experiment(StartTime = 0, StopTime = 0.5, Algorithm = Dassl, IntegratorStep = 0.0001, Tolerance = 1e-06, Interval = 0.001), 
    Documentation(link = "modelica://TYContact/Resources/HTML/Examples/CylinderPlaneContact.html"), 
    Diagram(coordinateSystem(extent = {{-100.0, -100.0}, {100.0, 100.0}}, 
    grid = {2.0, 2.0})), Protection(access = Access.nonPackageDuplicate));

end CylinderContact;