model WebLineSystem "卷料生产线系统"
  Modelica.Mechanics.MultiBody.Parts.Fixed fixed(animation = false, shapeType = "sphere", r = {-1, 0, 0}) 
    annotation(Placement(transformation(origin = {-144, -37}, 
    extent = {{-10, -10}, {10, 10}}, 
    rotation = 90)));
  TYWebHandling.Sources.WebSink webSink(inTypes = .TYWebHandling.Utilities.Type.inTypes.speedin) 
    annotation(Placement(transformation(origin = {164, 2}, 
    extent = {{-10, -10}, {10, 10}})));
  Modelica.Mechanics.MultiBody.Parts.Fixed fixed1(r = {1.5, 0, 0}, animation = false, shapeType = "sphere") 
    annotation(Placement(transformation(origin = {164, -37}, 
    extent = {{-10, -10}, {10, 10}}, 
    rotation = 90)));
  Modelica.Blocks.Sources.Constant const1(k = 1) 
    annotation(Placement(transformation(origin = {194, -4}, 
    extent = {{10, -10}, {-10, 10}})));
  TYWebHandling.Webs.Web_Spring web_spring 
    annotation(Placement(transformation(origin = {-108, 2}, 
    extent = {{-10, -10}, {10, 10}})));
  Modelica.Mechanics.MultiBody.Parts.Fixed fixed2(r = {-0.5, 0, 0}, animation = false, shapeType = "sphere") 
    annotation(Placement(transformation(origin = {-72, -37}, 
    extent = {{-10, -10}, {10, 10}}, 
    rotation = 90)));
  TYWebHandling.Webs.Web_Spring web_spring2(stateSelect = StateSelect.prefer) 
    annotation(Placement(transformation(origin = {16, 2}, 
    extent = {{-10, -10}, {10, 10}})));
  Modelica.Mechanics.MultiBody.Parts.Fixed fixed3(r = {0, -0.1, 0}, animation = false, shapeType = "sphere") 
    annotation(Placement(transformation(origin = {-14, -37}, 
    extent = {{-10, -10}, {10, 10}}, 
    rotation = 90)));
  TYWebHandling.Rollers.Roller roller(D = 0.2, stateSelect = StateSelect.avoid) 
    annotation(Placement(transformation(origin = {-72, 2}, 
    extent = {{-10, -10}, {10, 10}})));
  inner TYWebHandling.WebProperties WP(width = 1, nu = 0, th = 0.01) 
    annotation(Placement(transformation(origin = {-84, 84}, 
    extent = {{-10, -10}, {10, 10}})));
  inner Modelica.Mechanics.MultiBody.World world(animateGravity = false, animateWorld = false) 
    annotation(Placement(transformation(origin = {-56, 84}, 
    extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Sources.RealExpression realExpression1(y = 20) 
    annotation(Placement(transformation(origin = {-80, 43}, 
    extent = {{-10, -10}, {10, 10}})));
  Modelica.Mechanics.Rotational.Sources.Speed speed1(exact = false) 
    annotation(Placement(transformation(origin = {-44, 43}, 
    extent = {{-10, -10}, {10, 10}})));
  TYWebHandling.Webs.Web_Spring web_spring3(stateSelect = StateSelect.prefer) 
    annotation(Placement(transformation(origin = {76, 2}, 
    extent = {{-10, -10}, {10, 10}})));
  Modelica.Mechanics.MultiBody.Parts.Fixed fixed4(r = {0.5, -0.1, 0}, animation = false, shapeType = "sphere") 
    annotation(Placement(transformation(origin = {46, -37}, 
    extent = {{-10, -10}, {10, 10}}, 
    rotation = 90)));
  TYWebHandling.Rollers.Roller roller1(D = 0.2) 
    annotation(Placement(transformation(origin = {106, 2}, 
    extent = {{-10, -10}, {10, 10}})));
  TYWebHandling.Webs.Web_Spring web_spring4(stateSelect = StateSelect.prefer) 
    annotation(Placement(transformation(origin = {136, 2}, 
    extent = {{-10, -10}, {10, 10}})));
  Modelica.Mechanics.MultiBody.Parts.Fixed fixed5(r = {1, 0, 0}, animation = false, shapeType = "sphere") 
    annotation(Placement(transformation(origin = {106, -37}, 
    extent = {{-10, -10}, {10, 10}}, 
    rotation = 90)));
  TYWebHandling.Sources.WebSource webSource 
    annotation(Placement(transformation(origin = {-144, 2}, 
    extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Sources.Constant const2(k = 2000) 
    annotation(Placement(transformation(origin = {-195, 8}, 
    extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Sources.Constant const3(k = 1) 
    annotation(Placement(transformation(origin = {-195, -22}, 
    extent = {{-10, -10}, {10, 10}})));
  Modelica.Mechanics.Rotational.Sources.Speed speed2(exact = false) 
    annotation(Placement(transformation(origin = {36, 74}, 
    extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Sources.Ramp ramp(offset = 20, duration = 1, height = 0.001) 
    annotation(Placement(transformation(origin = {-7, 74}, 
    extent = {{-10, -10}, {10, 10}})));
  TYWebHandling.Rollers.SWrapRoller sWrapRoller(frame_color = {255, 170, 0}, ry1 = 0, ry2 = 0.151, D2 = 0.1, Din1 = 0.1, Din2 = 0.05, UseAlternative = false, frame_w = 0.05) 
    annotation(Placement(transformation(origin = {-14, 2}, 
    extent = {{-10, -10}, {10, 10}})));
  TYWebHandling.Rollers.SWrapRoller sWrapRoller1(frame_color = {255, 170, 0}, ry1 = 0, ry2 = 0.151, D2 = 0.1, Din1 = 0.1, Din2 = 0.05, UseAlternative = true, frame_w = 0.05) 
    annotation(Placement(transformation(origin = {46, 2}, 
    extent = {{-10, -10}, {10, 10}})));
  TYWebHandling.Webs.Web_Spring web_spring1 
    annotation(Placement(transformation(origin = {-43, 2}, 
    extent = {{-10, -10}, {10, 10}})));
equation
  connect(webSink.frame_c, fixed1.frame_b) 
    annotation(Line(origin = {164, -23}, 
    points = {{0, 14.8}, {0, -4}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(const1.y, webSink.vin) 
    annotation(Line(origin = {185, -4}, 
    points = {{-2, 0}, {-10.2, 0}}, 
    color = {0, 0, 127}));
  connect(fixed2.frame_b, roller.frame_c) 
    annotation(Line(origin = {-72, -23}, 
    points = {{0, -4}, {0, 15}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(web_spring.frame_b, roller.frame_a) 
    annotation(Line(origin = {-90, 2}, 
    points = {{-8, 0}, {8, 0}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(web_spring.webPort_b, roller.webPort_b) 
    annotation(Line(origin = {-90, 8}, 
    points = {{-8, 0}, {8, 0}}, 
    color = {96, 96, 96}, 
    thickness = 0.5));
  connect(realExpression1.y, speed1.w_ref) 
    annotation(Line(origin = {-62, 43}, 
    points = {{-7, 0}, {6, 0}}, 
    color = {0, 0, 127}));
  connect(web_spring3.frame_b, roller1.frame_a) 
    annotation(Line(origin = {91, 2}, 
    points = {{-5, -8.88178e-16}, {5, -8.88178e-16}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(web_spring3.webPort_b, roller1.webPort_b) 
    annotation(Line(origin = {91, 8}, 
    points = {{-5, -8.88178e-16}, {5, -8.88178e-16}}, 
    color = {96, 96, 96}, 
    thickness = 0.5));
  connect(roller1.frame_b, web_spring4.frame_a) 
    annotation(Line(origin = {121, 2}, 
    points = {{-5, -8.88178e-16}, {5, -3.55271e-15}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(web_spring4.webPort_a, roller1.webPort_a) 
    annotation(Line(origin = {121, 8}, 
    points = {{5, -3.55271e-15}, {-5, -3.55271e-15}, {-5, -8.88178e-16}}, 
    color = {96, 96, 96}, 
    thickness = 0.5));
  connect(web_spring4.frame_b, webSink.frame_a) 
    annotation(Line(origin = {150, 2}, 
    points = {{-4, -3.55271e-15}, {4, -3.55271e-15}, {4, -2.66454e-15}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(fixed5.frame_b, roller1.frame_c) 
    annotation(Line(origin = {106, -17}, 
    points = {{0, -10}, {0, 9}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(const3.y, webSource.vin) 
    annotation(Line(origin = {-175, -11.5}, 
    points = {{-9, -10.5}, {-2.5, -10.5}, {-2.5, 7.5}, {19.8, 7.5}}, 
    color = {0, 0, 127}));
  connect(const2.y, webSource.Ftin) 
    annotation(Line(origin = {-175, 8.5}, 
    points = {{-9, -0.5}, {19.8, -0.5}}, 
    color = {0, 0, 127}));
  connect(fixed.frame_b, webSource.frame_c) 
    annotation(Line(origin = {-144, -17}, 
    points = {{0, -10}, {0, 9}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(webSource.frame_a, web_spring.frame_a) 
    annotation(Line(origin = {-126, 2}, 
    points = {{-8, -2.22045e-16}, {8, -2.22045e-16}, {8, 0}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(webSource.webPort_a, web_spring.webPort_a) 
    annotation(Line(origin = {-126, 8}, 
    points = {{-8, 0}, {8, 0}}, 
    color = {96, 96, 96}, 
    thickness = 0.5));
  connect(ramp.y, speed2.w_ref) 
    annotation(Line(origin = {16, 77}, 
    points = {{-12, -3}, {8, -3}}, 
    color = {0, 0, 127}));
  connect(fixed3.frame_b, sWrapRoller.frame_c) 
    annotation(Line(origin = {-14, -17}, 
    points = {{0, -10}, {0, 9}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(sWrapRoller.frame_b, web_spring2.frame_a) 
    annotation(Line(origin = {1, 2}, 
    points = {{-5, 0}, {5, 0}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(sWrapRoller.webPort_a, web_spring2.webPort_a) 
    annotation(Line(origin = {1, 8}, 
    points = {{-5, 0}, {5, 0}}, 
    color = {96, 96, 96}, 
    thickness = 0.5));
  connect(speed1.flange, sWrapRoller.flange_2) 
    annotation(Line(origin = {-24, 25}, 
    points = {{-10, 18}, {10, 18}, {10, -18.6}}, 
    color = {0, 0, 0}));
  connect(web_spring2.frame_b, sWrapRoller1.frame_a) 
    annotation(Line(origin = {31, 2}, 
    points = {{-5, 0}, {5, 0}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(web_spring2.webPort_b, sWrapRoller1.webPort_b) 
    annotation(Line(origin = {31, 8}, 
    points = {{-5, 0}, {5, 0}}, 
    color = {96, 96, 96}, 
    thickness = 0.5));
  connect(web_spring3.webPort_a, sWrapRoller1.webPort_a) 
    annotation(Line(origin = {61, 8}, 
    points = {{5, 0}, {-5, 0}}, 
    color = {96, 96, 96}, 
    thickness = 0.5));
  connect(web_spring3.frame_a, sWrapRoller1.frame_b) 
    annotation(Line(origin = {61, 2}, 
    points = {{5, 0}, {-5, 0}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(fixed4.frame_b, sWrapRoller1.frame_c) 
    annotation(Line(origin = {46, -17}, 
    points = {{0, -10}, {0, 9}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(speed2.flange, sWrapRoller1.flange_2) 
    annotation(Line(origin = {46, 40}, 
    points = {{0, 34}, {0, -33.6}}, 
    color = {0, 0, 0}));
  connect(roller.frame_b, web_spring1.frame_a) 
    annotation(Line(origin = {-57, 2}, 
    points = {{-5, 0}, {4, 4.44089e-16}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(roller.webPort_a, web_spring1.webPort_a) 
    annotation(Line(origin = {-57, 8}, 
    points = {{-5, 0}, {4, 0}}, 
    color = {96, 96, 96}, 
    thickness = 0.5));
  connect(sWrapRoller.frame_a, web_spring1.frame_b) 
    annotation(Line(origin = {-28, 2}, 
    points = {{4, 0}, {-5, 4.44089e-16}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(sWrapRoller.webPort_b, web_spring1.webPort_b) 
    annotation(Line(origin = {-28, 8}, 
    points = {{4, 0}, {-5, 0}}, 
    color = {96, 96, 96}, 
    thickness = 0.5));
  connect(web_spring4.webPort_b, webSink.webPort_b) 
    annotation(Line(origin = {150, 8}, 
    points = {{-4, 0}, {4, 0}}, 
    color = {96, 96, 96}, 
    thickness = 0.5));
  annotation(Diagram(coordinateSystem(extent = {{-220, -100}, {224, 106}}, 
    grid = {2, 2})), Icon(coordinateSystem(extent = {{-100, -100}, {100, 100}}, 
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
CreatePlot(id=1, x_display_unit="s", legend_layout=1, left_title_type=2, left_title="[N]", bottom_title_type=2, right_title_type=2, fix_time_range_value=0, zoom_x=(0, 10), zoom_y_l=(-500, 2500)), 
Plot(y=["web_spring.Ft_b"], colors=["4278190335"]), 
CreatePlot(id=-1, x_display_unit="s", legend_layout=1, left_title="[N]", fix_time_range_value=0, sub_plot=(1, 2), zoom_x=(0, 10), zoom_y_l=(-500, 2500)), 
Plot(y=["web_spring1.Ft_b"], colors=["4278190335"]), 
CreatePlot(id=-1, x_display_unit="s", legend_layout=1, left_title="[N]", fix_time_range_value=0, sub_plot=(2, 2), zoom_x=(0, 10), zoom_y_l=(-500, 2500)), 
Plot(y=["webSink.Ftout"], colors=["4278190335"]), 
CreatePlot(id=-1, x_display_unit="s", legend_layout=1, left_title="[N]", fix_time_range_value=0, sub_plot=(2, 1), zoom_x=(0, 10), zoom_y_l=(-500, 2500)), 
Plot(y=["web_spring.Fi"], colors=["4278190335"]), 
CreatePlot(id=-1, x_display_unit="s", legend_layout=1, left_title="[m/s]", fix_time_range_value=0, sub_plot=(3, 2), zoom_x=(0, 10), zoom_y_l=(-3, 5)), 
Plot(y=["webSink.vin"], colors=["4278190335"]), 
CreatePlot(id=-1, x_display_unit="s", legend_layout=1, left_title="[N]", fix_time_range_value=0, sub_plot=(3, 1), zoom_x=(0, 10), zoom_y_l=(-500, 2500)), 
Plot(y=["web_spring3.Fi"], colors=["4278190335"])})
}),ContinueSimConfig(SaveContinueFile = "false", SaveBeforeStop = "false", NumberBeforeStop = 1, FixedContinueInterval = "false", ContinueIntervalLength = 5, ContinueTimeVector)), experiment(Algorithm = Dassl, InlineIntegrator = false, InlineStepSize = false, StartTime = 0, StopTime = 10, Tolerance = 0.0001, Interval = 0.001), 
    Documentation(link = "modelica://TYWebHandling/Resources/html/Examples/WebLineSystem.html"));
end WebLineSystem;