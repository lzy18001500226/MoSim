model SphereandCylinder "球驱动圆柱转动模拟"
  TYMultibody.Joints.Fixed fixed 
    annotation(Placement(transformation(origin = {-88.00000000000009, 0.0}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYMultibody.Joints.Revolute revolute 
    annotation(Placement(transformation(origin = {-51.499999999999986, 0.0}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  Modelica.Mechanics.MultiBody.Joints.FreeMotion freeMotion(r_rel_a(start = {0.2, 0.5, 0}, fixed = true), animation = false, v_rel_a(start = {0, 0, 0})) 
    annotation(Placement(transformation(origin = {-56.999999999999986, 39.999999999999986}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYMultibody.Bodies.BodySphere bodySphere(animation = true) 
    annotation(Placement(transformation(origin = {18.00000000000005, 39.999999999999986}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYMultibody.Bodies.RigidTranslation rigidTranslation(r = {-0.05, 0, 0}) 
    annotation(Placement(transformation(origin = {-14.999999999999986, 39.999999999999986}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYMultibody.Bodies.RigidTranslation rigidTranslation1(r = {-0.05, 0, 0}) 
    annotation(Placement(transformation(origin = {51.00000000000004, 39.999999999999986}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYMultibody.Bodies.RigidTranslation rigidTranslation2(r = {-0.3, 0, 0}) 
    annotation(Placement(transformation(origin = {-4.99999999999995, 0.0}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYMultibody.Bodies.RigidTranslation rigidTranslation3(r = {-0.3, 0, 0}) 
    annotation(Placement(transformation(origin = {62.0, 0.0}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYMultibody.Bodies.BodyCylinder bodyCylinder(length = 0.6, animation = false) 
    annotation(Placement(transformation(origin = {32.000000000000036, 0.0}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYContact.PointContact.SphereCylinder_Contact sphereCylinder_Contact(radius1 = 0.05, diameter2 = 0.1, length2 = 0.6, d = 1e4, k = 1e8, n1 = 1.5, n2 = 0, p_max = 0.001, mue_k = 0.1, mue_s = 0.12) 
    annotation(Placement(transformation(origin = {84.0, 40.0}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  inner TYMultibody.World world(gravityType = TYMultibody.Types.GravityTypes.UniformGravity) 
    annotation(Placement(transformation(origin = {-88.00000000000009, 40.0}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
equation
  connect(fixed.frame_b, revolute.frame_a) 
    annotation(Line(origin = {-63.99999999999994, -1.4210854715202004e-14}, 
    points = {{-14.000000000000142, 1.4210854715202004e-14}, {2.4999999999999574, 1.4210854715202004e-14}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(rigidTranslation.frame_b, bodySphere.frame_a) 
    annotation(Line(origin = {1.0000000000000568, 39.999999999999986}, 
    points = {{-6.000000000000043, 0.0}, {6.999999999999993, 0.0}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(bodySphere.frame_b, rigidTranslation1.frame_a) 
    annotation(Line(origin = {35.00000000000003, 39.999999999999986}, 
    points = {{-6.999999999999979, 0.0}, {6.000000000000014, 0.0}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(freeMotion.frame_b, rigidTranslation.frame_a) 
    annotation(Line(origin = {-35.999999999999915, 39.999999999999986}, 
    points = {{-11.000000000000071, 0.0}, {10.999999999999929, 0.0}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(bodyCylinder.frame_a, rigidTranslation2.frame_b) 
    annotation(Line(origin = {14.000000000000028, 0.0}, 
    points = {{8.000000000000007, 0.0}, {-8.999999999999979, 0.0}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(rigidTranslation3.frame_a, bodyCylinder.frame_b) 
    annotation(Line(origin = {47.00000000000006, 0.0}, 
    points = {{4.999999999999943, 0.0}, {-5.000000000000021, 0.0}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(rigidTranslation1.frame_b, sphereCylinder_Contact.frame_a) 
    annotation(Line(origin = {5.000000000000043, -5.000000000000014}, 
    points = {{56.0, 45.0}, {68.99999999999996, 45.000000000000014}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(rigidTranslation3.frame_b, sphereCylinder_Contact.frame_b) 
    annotation(Line(origin = {117.00000000000004, -19.999999999999986}, 
    points = {{-45.00000000000004, 19.999999999999986}, {-17.000000000000043, 19.999999999999986}, {-17.000000000000043, 59.999999999999986}, {-23.000000000000043, 59.999999999999986}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(revolute.frame_b, rigidTranslation2.frame_a) 
    annotation(Line(origin = {12.000000000000107, 0.0}, 
    points = {{-53.50000000000009, 0.0}, {-27.000000000000057, 0.0}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(world.frame_b, freeMotion.frame_a) 
    annotation(Line(origin = {-81.99999999999994, 39.999999999999986}, 
    points = {{3.999999999999858, 1.4210854715202004e-14}, {14.999999999999957, 0.0}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  annotation(experiment(Algorithm = Dassl, Interval = 0.001, StartTime = 0, StopTime = 3, Tolerance = 1e-06), 
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
    thickness = 5.0)}), 
    Documentation(link = "modelica://TYContact/Resources/HTML/Examples/SphereandCylinder.html"), 
    Protection(access = Access.nonPackageDuplicate),__MWORKS(ResultViewerManager(resultViewers={
ResultViewer(name="1", executeTrigger=executeTrigger.SimulationFinished, commands={
CreatePlot(id=1, x_display_unit="s", legend_layout=1, left_title_type=2, left_title="位移[m]", bottom_title_type=2, bottom_title="时间/s", fix_time_range_value=0, zoom_x=(0, 3), zoom_y_l=(-35, 5)), 
Plot(y=["bodySphere.r_OG_0[2]"], colors=["4278190335"]), 
CreatePlot(id=-1, x_display_unit="s", legend_layout=1, left_title_type=2, left_title="角速度[rad/s]", bottom_title_type=2, bottom_title="时间/s", fix_time_range_value=0, sub_plot=(2, 1), zoom_x=(0, 3), zoom_y_l=(-3.5, 0.5)), 
Plot(y=["bodyCylinder.om_a[3]"], colors=["4278190335"]), 
CreatePlot(id=-1, x_display_unit="s", legend_layout=1, left_title_type=2, left_title="接触力[N]", bottom_title_type=2, bottom_title="时间/s", fix_time_range_value=0, sub_plot=(3, 1), zoom_x=(0, 3), zoom_y_l=(-5000, 25000)), 
Plot(y=["sphereCylinder_Contact.contact_Force[2]"], colors=["4278190335"])})
})));

end SphereandCylinder;