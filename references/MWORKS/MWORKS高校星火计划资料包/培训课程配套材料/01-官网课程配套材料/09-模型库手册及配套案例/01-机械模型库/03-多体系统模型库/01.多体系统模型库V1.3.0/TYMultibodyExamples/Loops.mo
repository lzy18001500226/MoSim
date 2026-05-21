package Loops "闭环结构动力学系统"
  annotation(__MWORKS(version="2025a"));
  model Four_bar_Mechanism "四杆曲柄滑块结构"

    inner TYMultibody.World world 
      annotation(Placement(transformation(origin = {36.0, -58.0}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
    TYMultibody.Joints.Revolute revolute2 
      annotation(Placement(transformation(origin = {8.000000000000002, 10.0}, 
      extent = {{-10.0, 10.0}, {10.0, -10.0}}, 
      rotation = 90.0)));
    TYMultibody.Bodies.Body body2(r_AB_a = {0.8, 0.2, 0}, r_AG_a = {0.4, 0.1, 0}) 
      annotation(Placement(transformation(origin = {27.999999999999986, 38.0}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
    TYMultibody.Joints.RevolutePlanarCut revolute3 annotation(Placement(transformation(origin = {60.0, 38.0}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
    TYMultibody.Joints.Prismatic prismatic1 
      annotation(Placement(transformation(origin = {92.00000000000003, 38.0}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
    TYMultibody.Bodies.Body body3(r_AB_a = {0.5, 0, 0}, r_AG_a = {0.25, 0, 0}) 
      annotation(Placement(transformation(origin = {124.00000000000006, 38.0}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
    TYMultibody.Joints.Fixed fixed(r = {-1.3, -0.2, 0}) 
      annotation(Placement(transformation(origin = {8.000000000000007, -26.000000000000004}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
      rotation = 90.0)));
    TYMultibody.Joints.Revolute revolute4 
      annotation(Placement(transformation(origin = {74.0, -58.0}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
    TYMultibody.Joints.Prismatic prismatic 
      annotation(Placement(transformation(origin = {-174.0, 38.0}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
    TYMultibody.Joints.RevolutePlanarCut revolute annotation(Placement(transformation(origin = {-138.0, 38.0}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
    TYMultibody.Bodies.Body body(r_AB_a = {0.4, 0.4, 0}) 
      annotation(Placement(transformation(origin = {-102.00000000000001, 38.0}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
    TYMultibody.Joints.Revolute revolute1 
      annotation(Placement(transformation(origin = {-66.00000000000003, 38.0}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
    TYMultibody.Bodies.Body body1(r_AB_a = {0.3, -0.3, 0}) 
      annotation(Placement(transformation(origin = {-24.000000000000014, 38.0}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
    TYMultibody.Joints.Fixed fixed1(r = {-1.5, -0.3, 0}, ShowFrame = true) 
      annotation(Placement(transformation(origin = {-209.9999999999999, 38.0}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
    annotation(Icon(coordinateSystem(extent = {{-100.0, -100.0}, {100.0, 100.0}}, 
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
      Protection(access = Access.nonPackageDuplicate), experiment(Algorithm = Dassl, Interval = 0.001, StartTime = 0, StopTime = 3, Tolerance = 1e-06), __MWORKS(ContinueSimConfig(SaveContinueFile = "false", SaveBeforeStop = "false", NumberBeforeStop = 1, FixedContinueInterval = "false", ContinueIntervalLength = 0.001, ContinueTimeVector),ResultViewerManager(resultViewers={
ResultViewer(name="1", executeTrigger=executeTrigger.SimulationFinished, commands={
CreatePlot(id=1, x_display_unit="s", legend_layout=1, left_title="[m]", fix_time_range_value=0, zoom_x=(0, 3), zoom_y_l=(-0.5, 2)), 
Plot(y=["prismatic1.s_rel"], colors=["4278190335"]), 
CreatePlot(id=-1, x_display_unit="s", legend_layout=1, left_title="[m]", fix_time_range_value=0, sub_plot=(2, 1), zoom_x=(0, 3), zoom_y_l=(-0.8, 0.2)), 
Plot(y=["prismatic.s_rel"], colors=["4278190335"])})
})), 
      Documentation(link = "modelica://TYMultibody/Resources/html/Examples/Four_bar_Mechanism.html"), Diagram(coordinateSystem(extent = {{-100, -100}, {100, 100}}, 
      grid = {2, 2}), graphics = {Line(origin = {-32, 13}, 
      points = {{-192, 93}, {-190, -91}, {192, -93}, {192, 91}, {-192, 93}}, 
      color = {255, 255, 255})}));
  equation
    connect(body2.frame_a, revolute2.frame_b) 
      annotation(Line(origin = {19.0, 30.0}, 
      points = {{-1.0, 8.0}, {-11.0, 8.0}, {-11.0, -10.0}}, 
      color = {95, 95, 95}, 
      thickness = 0.5));
    connect(body2.frame_b, revolute3.frame_a) 
      annotation(Line(origin = {44.0, 39.0}, 
      points = {{-6.0, -1.0}, {6.0, -1.0}}, 
      color = {95, 95, 95}, 
      thickness = 0.5));
    connect(revolute3.frame_b, prismatic1.frame_a) 
      annotation(Line(origin = {76.0, 38.0}, 
      points = {{-6.0, 0.0}, {6.0, 0.0}}, 
      color = {95, 95, 95}, 
      thickness = 0.5));
    connect(prismatic1.frame_b, body3.frame_a) 
      annotation(Line(origin = {111.0, 39.0}, 
      points = {{-9.0, -1.0}, {3.0, -1.0}}, 
      color = {95, 95, 95}, 
      thickness = 0.5));
    connect(fixed.frame_b, revolute2.frame_a) 
      annotation(Line(origin = {-10.0, -29.0}, 
      points = {{18.0, 13.0}, {18.0, 29.0}}, 
      color = {95, 95, 95}, 
      thickness = 0.5));
    connect(world.frame_b, revolute4.frame_a) 
      annotation(Line(origin = {58.0, -58.0}, 
      points = {{-12.0, 0.0}, {6.0, 0.0}}, 
      color = {95, 95, 95}, 
      thickness = 0.5));
    connect(revolute4.frame_b, body3.frame_b) 
      annotation(Line(origin = {115.0, -10.0}, 
      points = {{-31.0, -48.0}, {31.0, -48.0}, {31.0, 48.0}, {19.0, 48.0}}, 
      color = {95, 95, 95}, 
      thickness = 0.5));
    connect(body1.frame_b, revolute2.frame_b) 
      annotation(Line(origin = {-3.0, 29.0}, 
      points = {{-11.0, 9.0}, {11.0, 9.0}, {11.0, -9.0}}, 
      color = {95, 95, 95}, 
      thickness = 0.5));
    connect(revolute1.frame_b, body1.frame_a) 
      annotation(Line(origin = {-45.0, 38.0}, 
      points = {{-11.0, 0.0}, {11.0, 0.0}}, 
      color = {95, 95, 95}, 
      thickness = 0.5));
    connect(body.frame_b, revolute1.frame_a) 
      annotation(Line(origin = {-84.0, 38.0}, 
      points = {{-8.0, 0.0}, {8.0, 0.0}}, 
      color = {95, 95, 95}, 
      thickness = 0.5));
    connect(revolute.frame_b, body.frame_a) 
      annotation(Line(origin = {-120.0, 38.0}, 
      points = {{-8.0, 0.0}, {8.0, 0.0}}, 
      color = {95, 95, 95}, 
      thickness = 0.5));
    connect(prismatic.frame_b, revolute.frame_a) 
      annotation(Line(origin = {-156.0, 38.0}, 
      points = {{-8.0, 0.0}, {8.0, 0.0}}, 
      color = {95, 95, 95}, 
      thickness = 0.5));
    connect(fixed1.frame_b, prismatic.frame_a) 
      annotation(Line(origin = {-192.0, 38.0}, 
      points = {{-8.0, 0.0}, {8.0, 0.0}}, 
      color = {95, 95, 95}, 
      thickness = 0.5));
  end Four_bar_Mechanism;
  model Two_bar_Mechanism "二杆曲柄滑块结构"

    inner TYMultibody.World world 
      annotation(Placement(transformation(origin = {-2.0, -49.99999999999999}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
    TYMultibody.Bodies.Body body(r_AB_a = {0, 0.6, 0}, r_AG_a = {0, 0.3, 0}, m = 1) 
      annotation(Placement(transformation(origin = {57.99999999999999, -50.0}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
    TYMultibody.Joints.Revolute revolute(om_rel_0 = 0) 
      annotation(Placement(transformation(origin = {27.999999999999993, -49.99999999999999}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
    TYMultibody.Joints.Revolute revolute1(om_rel_0 = 0.5) 
      annotation(Placement(transformation(origin = {58.0, 40.000000000000014}, 
      extent = {{10.0, -10.0}, {-10.0, 10.0}})));
    TYMultibody.Joints.Fixed fixed(r = {-0.8, 0.2, 0}) 
      annotation(Placement(transformation(origin = {-80.0, 2.0}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
    TYMultibody.Joints.Prismatic prismatic 
      annotation(Placement(transformation(origin = {-52.0, 2.0}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
    TYMultibody.Joints.RevolutePlanarCut revolute2 annotation(Placement(transformation(origin = {-16.0, 2.0}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
    TYMultibody.Bodies.Body body1(r_AB_a = {0.7, 0.4, 0}, r_AG_a = {0.35, 0.2, 0}, m = 1) 
      annotation(Placement(transformation(origin = {27.999999999999993, 26.0}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
    annotation(Icon(coordinateSystem(extent = {{-100.0, -100.0}, {100.0, 100.0}}, 
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
      Protection(access = Access.nonPackageDuplicate), Diagram(coordinateSystem(extent = {{-100, -100}, {100, 100}}, 
      grid = {2, 2}), graphics = {Line(origin = {2, 0}, 
      points = {{-108, 80}, {-108, -80}, {108, -80}, {108, 80}, {-108, 80}}, 
      color = {255, 255, 255})}), 
      Documentation(link = "modelica://TYMultibody/Resources/html/Examples/Two_bar_Mechanism.html"), experiment(Algorithm = Dassl, Interval = 0.001, StartTime = 0, StopTime = 3, Tolerance = 1e-06), __MWORKS(ContinueSimConfig(SaveContinueFile = "false", SaveBeforeStop = "false", NumberBeforeStop = 1, FixedContinueInterval = "false", ContinueIntervalLength = 0.001, ContinueTimeVector),ResultViewerManager(resultViewers={
ResultViewer(name="1", executeTrigger=executeTrigger.SimulationFinished, commands={
CreatePlot(id=1, x_display_unit="s", legend_layout=1, left_title="[m]", fix_time_range_value=0, zoom_x=(0, 3), zoom_y_l=(-0.6, 0.8)), 
Plot(y=["prismatic.s_rel"], colors=["4278190335"])})
})));
  equation
    connect(revolute.frame_b, body.frame_a) 
      annotation(Line(origin = {42.999999999999986, -49.99999999999999}, 
      points = {{-5.0, 0.0}, {5.0, 0.0}}, 
      color = {95, 95, 95}, 
      thickness = 0.5));
    connect(world.frame_b, revolute.frame_a) 
      annotation(Line(origin = {12.999999999999986, -50.99999999999999}, 
      points = {{-5.0, 1.0}, {5.0, 1.0}}, 
      color = {95, 95, 95}, 
      thickness = 0.5));
    connect(body.frame_b, revolute1.frame_a) 
      annotation(Line(origin = {72.99999999999999, -49.99999999999999}, 
      points = {{-5.0, 0.0}, {9.0, 0.0}, {9.0, 90.0}, {-5.0, 90.0}}, 
      color = {95, 95, 95}, 
      thickness = 0.5));
    connect(fixed.frame_b, prismatic.frame_a) 
      annotation(Line(origin = {-66.0, 2.0}, 
      points = {{-4.0, 0.0}, {4.0, 0.0}}, 
      color = {95, 95, 95}, 
      thickness = 0.5));
    connect(prismatic.frame_b, revolute2.frame_a) 
      annotation(Line(origin = {-34.0, 2.0}, 
      points = {{-8.0, 0.0}, {8.0, 0.0}}, 
      color = {95, 95, 95}, 
      thickness = 0.5));
    connect(body1.frame_b, revolute1.frame_b) 
      annotation(Line(origin = {43.0, 33.0}, 
      points = {{-5.0, -7.0}, {5.0, -7.0}, {5.0, 7.0}}, 
      color = {95, 95, 95}, 
      thickness = 0.5));
    connect(revolute2.frame_b, body1.frame_a) 
      annotation(Line(origin = {6.0, 14.0}, 
      points = {{-12.0, -12.0}, {12.0, -12.0}, {12.0, 12.0}}, 
      color = {95, 95, 95}, 
      thickness = 0.5));
  end Two_bar_Mechanism;
  model Four_Bar_Planner "平面四连杆机构"
    annotation(Diagram(coordinateSystem(extent = {{-100, -100}, {100, 100}}, 
      grid = {2, 2}), graphics = {Text(origin = {20.000000000000014, 26}, 
      lineColor = {255, 0, 0}, 
      extent = {{0, 8}, {0, -8}}, 
      fontSize = 14, 
      textColor = {255, 0, 0}), Line(origin = {5, 11}, 
      points = {{-99, 77}, {-99, -77}, {99, -75}, {97, 77}, {-99, 77}}, 
      color = {255, 255, 255})}), 
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
      Protection(access = Access.nonPackageDuplicate), 
      Documentation(link = "modelica://TYMultibody/Resources/html/Examples/Four_Bar_Planner.html"), 
      experiment(Algorithm = Dassl, Interval = 0.001, StartTime = 0, StopTime = 3, Tolerance = 1e-06), __MWORKS(ContinueSimConfig(SaveContinueFile = "false", SaveBeforeStop = "false", NumberBeforeStop = 1, FixedContinueInterval = "false", ContinueIntervalLength = 0.001, ContinueTimeVector),ResultViewerManager(resultViewers={
ResultViewer(name="1", executeTrigger=executeTrigger.SimulationFinished, commands={
CreatePlot(id=1, x_display_unit="s", legend_layout=1, left_title="[m]", fix_time_range_value=0, zoom_x=(0, 3), zoom_y_l=(-0.2, 1.2)), 
Plot(y=["body7.r_OG_0[1]", "body7.r_OG_0[2]", "body7.r_OG_0[3]"], colors=["4278190335", "4294901760", "4278222848"]), 
CreatePlot(id=-1, x_display_unit="s", legend_layout=1, left_title="[deg]", fix_time_range_value=0, sub_plot=(2, 1), zoom_x=(0, 3), zoom_y_l=(-60, 10)), 
Plot(y=["revolute3.phi_rel"], colors=["4278190335"])})
})));
    TYMultibody.Joints.Revolute revolute1(
      animation = true, 
      n = {0, 0, 1}, 
      stateSelect = StateSelect.always, 
      useAxisFlange = true) annotation(Placement(transformation(origin = {-20, -14}, 
      extent = {{-10, -10}, {10, 10}})));
    TYMultibody.Joints.Revolute revolute2(animation = true, n = {0, 0, 1}) annotation(Placement(transformation(origin = {60.000000000000014, -14}, 
      extent = {{-10, -10}, {10, 10}})));
    TYMultibody.Joints.Revolute revolute3(animation = true, n = {0, 0, 1}) annotation(Placement(transformation(origin = {-20, 46}, 
      extent = {{-10, -10}, {10, 10}})));
    inner TYMultibody.World world(enableAnimation = true) annotation(Placement(transformation(origin = {-69.99999999999999, -14}, 
      extent = {{-10, -10}, {10, 10}})));
    Modelica.Mechanics.Rotational.Components.Damper damper(d = 0.1) 
      annotation(Placement(transformation(origin = {-20, -42.000000000000014}, 
      extent = {{-10, -10}, {10, 10}})));
    TYMultibody.Bodies.Body body(r_AB_a = {0.4, 0, 0}, r_AG_a = {0.2, 0, 0}, shapeType = "box", width = 0.5 * world.defaultJointLength) 
      annotation(Placement(transformation(origin = {20.000000000000007, -14}, 
      extent = {{-10, -10}, {10, 10}})));
    TYMultibody.Bodies.Body body5(r_AB_a = {0.1, 1.1, 0}, r_AG_a = {0.05, 0.55, 0}, width = body.width, shapeType = "box") 
      annotation(Placement(transformation(origin = {76.00000000000001, 10.000000000000007}, 
      extent = {{-10, -10}, {10, 10}}, 
      rotation = 90)));
    TYMultibody.Bodies.Body body6(r_AB_a = {-0.15, 1, 0}, r_AG_a = {-0.075, 0.5, 0}, width = body.width, shapeType = "box") 
      annotation(Placement(transformation(origin = {-45.999999999999986, 24}, 
      extent = {{-10, -10}, {10, 10}}, 
      rotation = 90)));
    TYMultibody.Bodies.Body body7(r_AB_a = body.r_AB_a + body5.r_AB_a - body6.r_AB_a, r_AG_a = (body.r_AB_a + body5.r_AB_a - body6.r_AB_a) / 2, width = body.width, shapeType = "box") 
      annotation(Placement(transformation(origin = {20.000000000000007, 46}, 
      extent = {{-10, -10}, {10, 10}})));
    TYMultibody.Joints.RevolutePlanarCut revolute 
      annotation(Placement(transformation(origin = {60.000000000000014, 46}, 
      extent = {{-10, -10}, {10, 10}})));
  equation
    connect(world.frame_b, revolute1.frame_a) 
      annotation(Line(origin = {-44.999999999999986, -14}, 
      points = {{-15, 0}, {14.999999999999986, 0}}, 
      color = {95, 95, 95}, 
      thickness = 0.5));
    connect(damper.flange_a, revolute1.support) 
      annotation(Line(origin = {-28.999999999999986, -34}, 
      points = {{-1.0000000000000142, -8.000000000000014}, {-1.0000000000000142, 2}, {1.9999999999999858, 2}, {1.9999999999999858, 10}}, 
      color = {0, 0, 0}));
    connect(revolute1.axis, damper.flange_b) 
      annotation(Line(origin = {-14.999999999999986, -34}, 
      points = {{1.9999999999999858, 10}, {4.999999999999986, 10}, {4.999999999999986, -8.000000000000014}}, 
      color = {0, 0, 0}));
    connect(body.frame_a, revolute1.frame_b) 
      annotation(Line(origin = {1.4210854715202004e-14, -29}, 
      points = {{9.999999999999993, 15}, {-10.000000000000014, 15}}, 
      color = {95, 95, 95}, 
      thickness = 0.5));
    connect(body.frame_b, revolute2.frame_a) 
      annotation(Line(origin = {40.000000000000014, -29}, 
      points = {{-10.000000000000007, 15}, {10, 15}}, 
      color = {95, 95, 95}, 
      thickness = 0.5));
    connect(revolute2.frame_b, body5.frame_a) 
      annotation(Line(origin = {73.00000000000001, -7}, 
      points = {{-3, -7}, {3, -7}, {3, 7.000000000000007}}, 
      color = {95, 95, 95}, 
      thickness = 0.5));
    connect(body6.frame_b, revolute3.frame_a) 
      annotation(Line(origin = {-51.999999999999986, 40}, 
      points = {{6, -6}, {6, 6}, {21.999999999999986, 6}}, 
      color = {95, 95, 95}, 
      thickness = 0.5));
    connect(body6.frame_a, world.frame_b) 
      annotation(Line(origin = {-66.99999999999999, 0}, 
      points = {{21, 14}, {21, -14}, {7, -14}}, 
      color = {95, 95, 95}, 
      thickness = 0.5));
    connect(revolute3.frame_b, body7.frame_a) 
      annotation(Line(origin = {1.4210854715202004e-14, 46}, 
      points = {{-10.000000000000014, 0}, {9.999999999999993, 0}}, 
      color = {95, 95, 95}, 
      thickness = 0.5));
    connect(body7.frame_b, revolute.frame_a) 
      annotation(Line(origin = {41.000000000000014, 45}, 
      points = {{-11.000000000000007, 1}, {9, 1}}, 
      color = {95, 95, 95}, 
      thickness = 0.5));
    connect(revolute.frame_b, body5.frame_b) 
      annotation(Line(origin = {73.00000000000001, 33}, 
      points = {{-3, 13}, {3, 13}, {3, -12.999999999999993}}, 
      color = {95, 95, 95}, 
      thickness = 0.5));
  end Four_Bar_Planner;

end Loops;