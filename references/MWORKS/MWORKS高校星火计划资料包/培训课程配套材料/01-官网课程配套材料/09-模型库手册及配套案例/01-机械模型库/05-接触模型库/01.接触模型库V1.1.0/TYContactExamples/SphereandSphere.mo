model SphereandSphere "小球碰撞模拟"
  Modelica.Mechanics.MultiBody.Joints.FreeMotion freeMotion(r_rel_a(fixed = true, start = {0, 0, 0}), v_rel_a(fixed = true, start = {0.3, 0, 0.3}), animation = false) 
    annotation(Placement(transformation(origin = {-47.0, 25.999999999999996}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  Modelica.Mechanics.MultiBody.Joints.FreeMotion freeMotion1(r_rel_a(fixed = true, start = {1, 0, 1}), v_rel_a(fixed = true, start = {0, 0, 0}), animation = false) 
    annotation(Placement(transformation(origin = {-47.0, -20.0}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYContact.PointContact.SphereSphere_Contact contact_spheretosphere1(k = 1e8, d = 1e4, radius1 = 0.1, radius2 = 0.1, color1 = {0, 0, 255}, 
    n1 = 1, n2 = 0, p_max = 0.0001) 
    annotation(Placement(transformation(origin = {85.00000000000003, 26.0}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYMultibody.Bodies.BodySphere Sphere1(animation = false, diameter = 0.2) 
    annotation(Placement(transformation(origin = {18.999999999999993, 26.0}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYMultibody.Bodies.RigidTranslation rigidTranslation(r = {-0.1, 0, 0}) 
    annotation(Placement(transformation(origin = {-13.999999999999996, 26.000000000000004}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYMultibody.Bodies.RigidTranslation rigidTranslation1(r = {-0.1, 0, 0}) 
    annotation(Placement(transformation(origin = {52.00000000000001, 26.0}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYMultibody.Bodies.BodySphere Sphere2(animation = false, diameter = 0.2) 
    annotation(Placement(transformation(origin = {18.999999999999993, -20.0}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYMultibody.Bodies.RigidTranslation rigidTranslation2(r = {-0.1, 0, 0}) 
    annotation(Placement(transformation(origin = {-13.999999999999998, -20.0}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYMultibody.Bodies.RigidTranslation rigidTranslation3(r = {-0.1, 0, 0}) 
    annotation(Placement(transformation(origin = {52.00000000000001, -20.0}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  inner TYMultibody.World world(gravityType = TYMultibody.Types.GravityTypes.NoGravity) 
    annotation(Placement(transformation(origin = {-110.0, 25.999999999999996}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
equation
  connect(freeMotion.frame_b, rigidTranslation.frame_a) 
    annotation(Line(origin = {-30.0, 26.0}, 
    points = {{-7.0, -3.552713678800501e-15}, {6.0000000000000036, 3.552713678800501e-15}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(freeMotion1.frame_b, rigidTranslation2.frame_a) 
    annotation(Line(origin = {-30.0, -20.0}, 
    points = {{-7.0, 0.0}, {6.0, 0.0}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(rigidTranslation.frame_b, Sphere1.frame_a) 
    annotation(Line(origin = {2.0, 26.0}, 
    points = {{-5.9999999999999964, 3.552713678800501e-15}, {6.999999999999993, 0.0}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(rigidTranslation2.frame_b, Sphere2.frame_a) 
    annotation(Line(origin = {2.0, -20.0}, 
    points = {{-5.999999999999998, 0.0}, {6.999999999999993, 0.0}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(Sphere2.frame_b, rigidTranslation3.frame_a) 
    annotation(Line(origin = {36.0, -20.0}, 
    points = {{-7.000000000000007, 0.0}, {6.000000000000007, 0.0}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(Sphere1.frame_b, rigidTranslation1.frame_a) 
    annotation(Line(origin = {36.0, 26.0}, 
    points = {{-7.000000000000007, 0.0}, {6.000000000000007, 0.0}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(rigidTranslation1.frame_b, contact_spheretosphere1.frame_a) 
    annotation(Line(origin = {70.0, 13.0}, 
    points = {{-7.999999999999993, 13.0}, {5.000000000000028, 13.0}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(rigidTranslation3.frame_b, contact_spheretosphere1.frame_b) 
    annotation(Line(origin = {80.0, -10.0}, 
    points = {{-17.999999999999993, -10.0}, {20.0, -10.0}, {20.0, 36.0}, {15.000000000000028, 36.0}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(world.frame_b, freeMotion.frame_a) 
    annotation(Line(origin = {-78.0, 26.0}, 
    points = {{-22.0, -3.552713678800501e-15}, {21.0, -3.552713678800501e-15}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(freeMotion1.frame_a, world.frame_b) 
    annotation(Line(origin = {-78.0, 3.0}, 
    points = {{21.0, -23.0}, {2.0, -23.0}, {2.0, 22.999999999999996}, {-22.0, 22.999999999999996}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  annotation(experiment(Algorithm = Dassl, Interval = 0.001, StartTime = 0, StopTime = 5, Tolerance = 1e-06), 
    Documentation(link = "modelica://TYContact/Resources/HTML/Examples/SphereandSphere.html"), 
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
    thickness = 5.0)}), Protection(access = Access.nonPackageDuplicate),__MWORKS(ResultViewerManager(resultViewers={
ResultViewer(name="1", executeTrigger=executeTrigger.SimulationFinished, commands={
CreatePlot(id=1, x_display_unit="s", legend_layout=1, left_title_type=2, left_title="位移[m]", bottom_title_type=2, bottom_title="时间s/", fix_time_range_value=0, zoom_x=(0, 5), zoom_y_l=(-0.2, 1.2)), 
Plot(y=["Sphere1.r_OG_0[1]"], colors=["4278190335"]), 
CreatePlot(id=-1, x_display_unit="s", legend_layout=1, left_title_type=2, left_title="位移[m]", bottom_title_type=2, bottom_title="时间/s", fix_time_range_value=0, sub_plot=(2, 1), zoom_x=(0, 5), zoom_y_l=(0.9, 1.7)), 
Plot(y=["Sphere2.r_OG_0[1]"], colors=["4278190335"]), 
CreatePlot(id=-1, x_display_unit="s", legend_layout=1, left_title_type=2, left_title="接触力[N]", bottom_title_type=2, bottom_title="时间/s", fix_time_range_value=0, sub_plot=(3, 1), zoom_x=(0, 5), zoom_y_l=(-1000, 4000)), 
Plot(y=["Sphere2.frame_b.f[1]"], colors=["4278190335"])})
})));


end SphereandSphere;