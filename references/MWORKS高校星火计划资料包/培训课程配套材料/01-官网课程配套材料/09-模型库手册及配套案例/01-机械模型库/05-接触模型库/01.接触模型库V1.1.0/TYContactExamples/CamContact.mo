model CamContact "轮系进给机构"
  inner TYMultibody.World world1(gravityType = TYMultibody.Types.GravityTypes.NoGravity) 
    annotation(Placement(transformation(origin = {-74.0, 59.99999999999999}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYMultibody.Bodies.BodySphere Sphere1(diameter = 1, r_OA_0(fixed = false), animation = false) 
    annotation(Placement(transformation(origin = {74.00000000000007, 59.99999999999999}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYMultibody.Joints.Revolute revolute1(useAxisFlange = true, phi_rel_fixed = false, om_rel_fixed = false) 
    annotation(Placement(transformation(origin = {6.000000000000192, 59.99999999999999}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYMultibody.Bodies.RigidTranslation rigidTranslation1(r = {-0.75, 0, 0}) 
    annotation(Placement(transformation(origin = {40.0000000000001, 59.99999999999999}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYMechanics.Rotational.Sources.AngleVelocity angleVelocity 
    annotation(Placement(transformation(origin = {-9.99999999999999, 34.000000000000036}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  Modelica.Blocks.Sources.Constant const(k = 10) 
    annotation(Placement(transformation(origin = {-39.999999999999986, 34.000000000000036}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYMultibody.Bodies.RigidTranslation rigidTranslation2(r = {0.25, 0, 0}) 
    annotation(Placement(transformation(origin = {-27.999999999999872, 59.99999999999999}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYMultibody.Bodies.RigidTranslation rigidTranslation5(r = {-0.5, 0, 0}) 
    annotation(Placement(transformation(origin = {108.0, 59.99999999999999}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYContact.PointContact.SphereSphere_Contact sphereSphere_Contact(radius1 = 0.5, radius2 = 0.1, k = 1e9, d = 1e4, animation_BCS1 = false, animation_BCS2 = false) 
    annotation(Placement(transformation(origin = {141.99999999999997, 59.99999999999999}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYMultibody.Bodies.RigidTranslation rigidTranslation6(r = {-0.1, 0, 0}) 
    annotation(Placement(transformation(origin = {108.0, -13.999999999999986}, 
    extent = {{10.0, -10.0}, {-10.0, 10.0}})));
  TYMultibody.Bodies.BodySphere Sphere2(r_OA_0(start = {0.6, 0, 0}, fixed = true), diameter = 0.2, animation = false) 
    annotation(Placement(transformation(origin = {51.99999999999994, -13.999999999999986}, 
    extent = {{10.0, -10.0}, {-10.0, 10.0}})));
  TYMultibody.Joints.Prismatic prismatic(s_rel_fixed = false, v_rel_fixed = false, useAxisFlange = true) 
    annotation(Placement(transformation(origin = {6.000000000000185, -13.999999999999968}, 
    extent = {{10.0, -10.0}, {-10.0, 10.0}})));
  TYMechanics.Translational.Components.SpringDamper springDamper(k = 1e7, d = 1e4, s_rel0 = 0.4) 
    annotation(Placement(transformation(origin = {6.000000000000121, -45.99999999999997}, 
    extent = {{10.0, -10.0}, {-10.0, 10.0}})));
  TYMultibody.Joints.Fixed fixed(r = {1.2, 0, 0}) 
    annotation(Placement(transformation(origin = {-74.0, -13.999999999999966}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
equation
  connect(revolute1.frame_b, rigidTranslation1.frame_a) 
    annotation(Line(origin = {29.00000000000015, 60.00000000000002}, 
    points = {{-12.999999999999957, -2.842170943040401e-14}, {0.9999999999999503, -2.842170943040401e-14}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(rigidTranslation1.frame_b, Sphere1.frame_a) 
    annotation(Line(origin = {61.00000000000017, 45.00000000000002}, 
    points = {{-11.000000000000071, 14.999999999999972}, {2.9999999999999005, 14.999999999999972}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(angleVelocity.flange, revolute1.axis) 
    annotation(Line(origin = {7.000000000000142, 40.00000000000002}, 
    points = {{-7.0000000000001315, -5.999999999999986}, {6.00000000000005, -5.999999999999986}, {6.00000000000005, 9.999999999999972}}, 
    color = {0, 0, 0}));
  connect(const.y, angleVelocity.om_ref) 
    annotation(Line(origin = {-24.000000000000043, 34.000000000000014}, 
    points = {{-4.999999999999943, 2.1316282072803006e-14}, {4.000000000000053, 2.1316282072803006e-14}}, 
    color = {0, 0, 127}));
  connect(world1.frame_b, rigidTranslation2.frame_a) 
    annotation(Line(origin = {-44.999999999999886, 60.00000000000002}, 
    points = {{-19.000000000000114, -2.842170943040401e-14}, {7.000000000000014, -2.842170943040401e-14}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(rigidTranslation2.frame_b, revolute1.frame_a) 
    annotation(Line(origin = {-10.9999999999999, 60.00000000000002}, 
    points = {{-6.999999999999972, -2.842170943040401e-14}, {7.000000000000092, -2.842170943040401e-14}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(Sphere1.frame_b, rigidTranslation5.frame_a) 
    annotation(Line(origin = {171.0000000000001, 59.99999999999999}, 
    points = {{-87.00000000000004, 0.0}, {-73.00000000000011, 0.0}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(rigidTranslation5.frame_b, sphereSphere_Contact.frame_a) 
    annotation(Line(origin = {132.00000000000006, 60.000000000000014}, 
    points = {{-14.000000000000057, -2.1316282072803006e-14}, {-8.526512829121202e-14, -2.1316282072803006e-14}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(rigidTranslation6.frame_a, sphereSphere_Contact.frame_b) 
    annotation(Line(origin = {156.99999999999997, 16.00000000000002}, 
    points = {{-38.99999999999997, -30.000000000000007}, {9.000000000000028, -30.000000000000007}, {9.000000000000028, 43.99999999999997}, {-5.0, 43.99999999999997}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(rigidTranslation6.frame_b, Sphere2.frame_a) 
    annotation(Line(origin = {211.00000000000014, 78.00000000000003}, 
    points = {{-113.00000000000014, -92.00000000000001}, {-149.0000000000002, -92.00000000000001}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(Sphere2.frame_b, prismatic.frame_a) 
    annotation(Line(origin = {-15.000000000000071, -48.0}, 
    points = {{57.000000000000014, 34.000000000000014}, {31.000000000000256, 34.00000000000003}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(springDamper.flange_a, prismatic.support) 
    annotation(Line(origin = {-7.000000000000071, -76.0}, 
    points = {{23.000000000000192, 30.00000000000003}, {43.000000000000114, 30.00000000000003}, {43.000000000000114, 52.00000000000003}, {20.000000000000256, 52.00000000000003}}, 
    color = {0, 0, 0}));
  connect(prismatic.axis, springDamper.flange_b) 
    annotation(Line(origin = {20.99999999999993, -76.0}, 
    points = {{-21.999999999999744, 52.00000000000003}, {-40.999999999999886, 52.00000000000003}, {-40.999999999999886, 30.00000000000003}, {-24.999999999999808, 30.00000000000003}}, 
    color = {96, 96, 96}));
  connect(fixed.frame_b, prismatic.frame_b) 
    annotation(Line(origin = {-34.0, -13.999999999999972}, 
    points = {{-30.0, 5.329070518200751e-15}, {30.000000000000185, 3.552713678800501e-15}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  annotation(Diagram(coordinateSystem(extent = {{-100.0, -104.0}, {192.0, 100.0}}, 
    grid = {2.0, 2.0})), 
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
    Documentation(link = "modelica://TYContact/Resources/HTML/Examples/CamContact.html"), 
    Protection(access = Access.nonPackageDuplicate), experiment(Algorithm = Dassl, IntegratorStep = 1e-06, Interval = 0.001, StartTime = 0, StopTime = 3, Tolerance = 1e-06), __MWORKS(ContinueSimConfig(SaveContinueFile = "false", SaveBeforeStop = "false", NumberBeforeStop = 1, FixedContinueInterval = "false", ContinueIntervalLength = 0.3, ContinueTimeVector),ResultViewerManager(resultViewers={
ResultViewer(name="1", executeTrigger=executeTrigger.SimulationFinished, commands={
CreatePlot(id=1, x_display_unit="s", legend_layout=1, left_title_type=2, left_title="转速[rad/s]", bottom_title_type=2, bottom_title="时间/s", fix_time_range_value=0, zoom_x=(0, 3), zoom_y_l=(-30, 50)), 
Plot(y=["revolute1.om_rel"], colors=["4278190335"]), 
CreatePlot(id=-1, x_display_unit="s", legend_layout=1, left_title_type=2, left_title="位移[m]", bottom_title_type=2, bottom_title="时间/s", fix_time_range_value=0, sub_plot=(2, 1), zoom_x=(0, 3), zoom_y_l=(0.6, 1.1)), 
Plot(y=["Sphere2.r_OG_0[1]"], colors=["4278190335"]), 
CreatePlot(id=-1, x_display_unit="s", legend_layout=1, left_title_type=2, left_title="接触状态", bottom_title_type=2, bottom_title="时间/s", fix_time_range_value=0, sub_plot=(3, 1), zoom_x=(0, 3), zoom_y_l=(-0.2, 1.2)), 
Plot(y=["sphereSphere_Contact.contact"], colors=["4278190335"])})
})));

end CamContact;