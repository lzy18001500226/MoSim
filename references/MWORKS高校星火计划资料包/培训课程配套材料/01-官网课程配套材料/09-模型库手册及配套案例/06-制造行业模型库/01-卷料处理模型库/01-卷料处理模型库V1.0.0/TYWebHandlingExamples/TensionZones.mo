model TensionZones "张力区域"
  Modelica.Mechanics.MultiBody.Parts.Fixed fixed(animation = false, shapeType = "sphere", r = {-1, -0.5, 0}) 
    annotation(Placement(transformation(origin = {-78, -65}, 
    extent = {{-10, -10}, {10, 10}}, 
    rotation = 90)));
  TYWebHandling.Sources.WebSink webSink(inTypes = .TYWebHandling.Utilities.Type.inTypes.speedin) 
    annotation(Placement(transformation(origin = {112, -26}, 
    extent = {{-10, -10}, {10, 10}})));
  Modelica.Mechanics.MultiBody.Parts.Fixed fixed1(r = {1, -0.2, 0}, animation = false, shapeType = "sphere") 
    annotation(Placement(transformation(origin = {112, -65}, 
    extent = {{-10, -10}, {10, 10}}, 
    rotation = 90)));
  Modelica.Blocks.Sources.Constant const1(k = 5.01) 
    annotation(Placement(transformation(origin = {142, -32}, 
    extent = {{10, -10}, {-10, 10}})));
  TYWebHandling.Webs.Web_Spring web_spring 
    annotation(Placement(transformation(origin = {-42, -26}, 
    extent = {{-10, -10}, {10, 10}})));
  TYWebHandling.Webs.Web_Spring web_spring1(stateSelect = StateSelect.never) 
    annotation(Placement(transformation(origin = {22, -26}, 
    extent = {{-10, -10}, {10, 10}})));
  Modelica.Mechanics.MultiBody.Parts.Fixed fixed2(r = {-0.3, -0.1, 0}, animation = false, shapeType = "sphere") 
    annotation(Placement(transformation(origin = {-6, -65}, 
    extent = {{-10, -10}, {10, 10}}, 
    rotation = 90)));
  Modelica.Blocks.Sources.RealExpression realExpression(y = 49.9) 
    annotation(Placement(transformation(origin = {-58, 13}, 
    extent = {{-10, -10}, {10, 10}})));
  TYWebHandling.Webs.Web_Spring web_spring2(stateSelect = StateSelect.never) 
    annotation(Placement(transformation(origin = {82, -26}, 
    extent = {{-10, -10}, {10, 10}})));
  Modelica.Mechanics.MultiBody.Parts.Fixed fixed3(r = {0.5, 0, 0}, animation = false, shapeType = "sphere") 
    annotation(Placement(transformation(origin = {52, -65}, 
    extent = {{-10, -10}, {10, 10}}, 
    rotation = 90)));
  TYWebHandling.Rollers.Roller roller(D = 0.2) 
    annotation(Placement(transformation(origin = {-6, -26}, 
    extent = {{-10, -10}, {10, 10}})));
  TYWebHandling.Sources.UnwindDrum unwindDrum 
    annotation(Placement(transformation(origin = {-78, -26}, 
    extent = {{-10, -10}, {10, 10}})));
  Modelica.Mechanics.Rotational.Sources.Torque torque1 
    annotation(Placement(transformation(origin = {-106, -26}, 
    extent = {{-10, -10}, {10, 10}})));
  inner TYWebHandling.WebProperties WP(width = 1, nu = 0) 
    annotation(Placement(transformation(origin = {-78, 60}, 
    extent = {{-10, -10}, {10, 10}})));
  inner Modelica.Mechanics.MultiBody.World world(animateGravity = false, animateWorld = false) 
    annotation(Placement(transformation(origin = {-50, 60}, 
    extent = {{-10, -10}, {10, 10}})));
  Modelica.Mechanics.Rotational.Sources.Speed speed(exact = false) 
    annotation(Placement(transformation(origin = {-22, 13}, 
    extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Sources.Ramp ramp(duration = 1, height = 50) 
    annotation(Placement(transformation(origin = {-146, -26}, 
    extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Sources.RealExpression realExpression1(y = 50) 
    annotation(Placement(transformation(origin = {-14, 30}, 
    extent = {{-10, -10}, {10, 10}})));
  Modelica.Mechanics.Rotational.Sources.Speed speed1(exact = false) 
    annotation(Placement(transformation(origin = {22, 30}, 
    extent = {{-10, -10}, {10, 10}})));
  TYWebHandling.Rollers.NipRoller nipRoller(D1 = 0.2, useSide = false) 
    annotation(Placement(transformation(origin = {52, -26}, 
    extent = {{-10, -10}, {10, 10}})));
equation
  connect(webSink.frame_c, fixed1.frame_b) 
    annotation(Line(origin = {112, -51}, 
    points = {{0, 14.8}, {0, -4}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(const1.y, webSink.vin) 
    annotation(Line(origin = {133, -32}, 
    points = {{-2, 0}, {-10.2, 0}}, 
    color = {0, 0, 127}));
  connect(fixed2.frame_b, roller.frame_c) 
    annotation(Line(origin = {-6, -51}, 
    points = {{0, -4}, {0, 15}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(web_spring.frame_b, roller.frame_a) 
    annotation(Line(origin = {-24, -26}, 
    points = {{-8, 0}, {8, 0}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(web_spring.webPort_b, roller.webPort_b) 
    annotation(Line(origin = {-24, -20}, 
    points = {{-8, 0}, {8, 0}}, 
    color = {96, 96, 96}, 
    thickness = 0.5));
  connect(roller.webPort_a, web_spring1.webPort_a) 
    annotation(Line(origin = {12, -20}, 
    points = {{-8, 0}, {0, 0}}, 
    color = {96, 96, 96}, 
    thickness = 0.5));
  connect(roller.frame_b, web_spring1.frame_a) 
    annotation(Line(origin = {12, -26}, 
    points = {{-8, 0}, {0, 0}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(nipRoller.frame_c, fixed3.frame_b) 
    annotation(Line(origin = {57, -53}, 
    points = {{-5, 17}, {-5, -2}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(web_spring1.frame_b, nipRoller.frame_a) 
    annotation(Line(origin = {42, -26}, 
    points = {{-10, 0}, {0, 0}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(web_spring1.webPort_b, nipRoller.webPort_b) 
    annotation(Line(origin = {42, -20}, 
    points = {{-10, 0}, {0, 0}}, 
    color = {96, 96, 96}, 
    thickness = 0.5));
  connect(nipRoller.frame_b, web_spring2.frame_a) 
    annotation(Line(origin = {72, -26}, 
    points = {{-10, 0}, {0, 0}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(nipRoller.webPort_a, web_spring2.webPort_a) 
    annotation(Line(origin = {72, -20}, 
    points = {{-10, 0}, {0, 0}}, 
    color = {96, 96, 96}, 
    thickness = 0.5));
  connect(web_spring2.frame_b, webSink.frame_a) 
    annotation(Line(origin = {102, -26}, 
    points = {{-10, 0}, {0, 0}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(web_spring.frame_a, unwindDrum.frame_a) 
    annotation(Line(origin = {-60, -26}, 
    points = {{8, 0}, {-8, 0}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(web_spring.webPort_a, unwindDrum.webPort_a) 
    annotation(Line(origin = {-60, -20}, 
    points = {{8, 0}, {-8, 0}}, 
    color = {96, 96, 96}, 
    thickness = 0.5));
  connect(fixed.frame_b, unwindDrum.frame_c) 
    annotation(Line(origin = {-79, -51}, 
    points = {{1, -4}, {1, 15}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(torque1.flange, unwindDrum.flange_a) 
    annotation(Line(origin = {-87, -26}, 
    points = {{-9, 0}, {9, 0}}, 
    color = {0, 0, 0}));
  connect(realExpression.y, speed.w_ref) 
    annotation(Line(origin = {-40, 13}, 
    points = {{-7, 0}, {6, 0}}, 
    color = {0, 0, 127}));
  connect(speed.flange, roller.flange_a) 
    annotation(Line(origin = {-9, -6}, 
    points = {{-3, 19}, {3, 19}, {3, -20}}, 
    color = {0, 0, 0}));
  connect(ramp.y, torque1.tau) 
    annotation(Line(origin = {-126, -26}, 
    points = {{-9, 0}, {8, 0}}, 
    color = {0, 0, 127}));
  connect(realExpression1.y, speed1.w_ref) 
    annotation(Line(origin = {4, 30}, 
    points = {{-7, 0}, {6, 0}}, 
    color = {0, 0, 127}));
  connect(speed1.flange, nipRoller.flange_1) 
    annotation(Line(origin = {42, 0}, 
    points = {{-10, 30}, {10, 30}, {10, -30}}, 
    color = {0, 0, 0}));
  connect(web_spring2.webPort_b, webSink.webPort_b) 
    annotation(Line(origin = {97, -20}, 
    points = {{-5, 0}, {5, 0}}, 
    color = {96, 96, 96}, 
    thickness = 0.5));
  annotation(Diagram(coordinateSystem(extent = {{-178, -100}, {162, 84}}, 
    grid = {2, 2}), graphics = {Rectangle(origin = {-8, -8}, 
    fillColor = {255, 255, 255}, 
    pattern = LinePattern.None, 
    extent = {{-170, 92}, {170, -92}})}), Icon(coordinateSystem(extent = {{-100, -100}, {100, 100}}, 
    grid = {2, 2}), graphics = {Polygon(origin = {-3.55271e-15, 27}, 
    lineColor = {96, 96, 96}, 
    fillColor = {96, 96, 96}, 
    fillPattern = FillPattern.Solid, 
    points = {{-64, 1}, {0, 37}, {64, 1}, {0, -37}}), Line(origin = {3.55271e-15, -18}, 
    points = {{-62, 18}, {0, -18}, {62, 18}}, 
    color = {96, 96, 96}, 
    thickness = 5), Line(origin = {1.06581e-14, -46}, 
    points = {{-62, 18}, {0, -18}, {62, 18}}, 
    color = {96, 96, 96}, 
    thickness = 5)}), __MWORKS(ResultViewerManager(resultViewers={
ResultViewer(name="1", executeTrigger=executeTrigger.SimulationFinished, commands={
CreatePlot(id=4, x_display_unit="s", legend_layout=1, left_title_type=2, left_title="[N]", bottom_title_type=2, right_title_type=2, curve_vernier=True, fix_time_range_value=0, zoom_x=(0, 10), zoom_y_l=(-50, 300)), 
Plot(y=["web_spring.Ft_b"], colors=["4278190335"]), 
CreatePlot(id=-1, x_display_unit="s", legend_layout=1, left_title="[N]", curve_vernier=True, fix_time_range_value=0, sub_plot=(2, 1), zoom_x=(0, 10), zoom_y_l=(0, 1200)), 
Plot(y=["web_spring1.Ft_b"], colors=["4278190335"]), 
CreatePlot(id=-1, x_display_unit="s", legend_layout=1, left_title="[N]", curve_vernier=True, fix_time_range_value=0, sub_plot=(3, 1), zoom_x=(0, 10), zoom_y_l=(0, 2000)), 
Plot(y=["webSink.Ftout"], colors=["4278190335"])})
}),ContinueSimConfig(SaveContinueFile = "false", SaveBeforeStop = "false", NumberBeforeStop = 1, FixedContinueInterval = "false", ContinueIntervalLength = 5, ContinueTimeVector)), experiment(Algorithm = Dassl, InlineIntegrator = false, InlineStepSize = false, StartTime = 0, StopTime = 10, Tolerance = 1e-06, IntegratorStep = 0.0001, Interval = 0.001), 
    Documentation(link = "modelica://TYWebHandling/Resources/html/Examples/TensionZones.html"));
end TensionZones;