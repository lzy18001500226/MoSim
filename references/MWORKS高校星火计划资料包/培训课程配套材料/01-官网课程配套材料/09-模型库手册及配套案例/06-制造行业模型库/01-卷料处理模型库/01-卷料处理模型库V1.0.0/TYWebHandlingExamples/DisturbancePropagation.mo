model DisturbancePropagation "卷辊速度扰动"

  parameter Modelica.Units.SI.Diameter D = 0.2"卷辊的外直径";
  parameter Modelica.Units.SI.Velocity V = 1"卷料的速度输入";
  parameter Modelica.Units.SI.Force T = 100"卷料的张力输入";

  inner TYWebHandling.WebProperties WP(th = 0.001, nu = 0, th_vis = 0.02, ShowExtremeTension = true, T_min = 90, T_max = 110) 
    annotation(Placement(transformation(origin = {-162, 136}, 
    extent = {{-10, -10}, {10, 10}})));
  inner Modelica.Mechanics.MultiBody.World world 
    annotation(Placement(transformation(origin = {-114, 136}, 
    extent = {{-10, -10}, {10, 10}})));
  TYWebHandling.Rollers.Roller roller(D = D) 
    annotation(Placement(transformation(origin = {-2, 0}, 
    extent = {{-10, -10}, {10, 10}})));
  TYWebHandling.Rollers.SlipRoller slipRoller(D = D) 
    annotation(Placement(transformation(origin = {163, 0}, 
    extent = {{-10, -10}, {10, 10}})));
  TYWebHandling.Sources.WebSource webSource 
    annotation(Placement(transformation(origin = {-80, 0}, 
    extent = {{-10, -10}, {10, 10}})));
  TYWebHandling.Sources.WebSink webSink(inTypes = TYWebHandling.Utilities.Type.inTypes.Tensionin) 
    annotation(Placement(transformation(origin = {336, -2.22045e-16}, 
    extent = {{-10, -10}, {10, 10}})));
  TYWebHandling.Webs.Web_Spring web_Spring1 
    annotation(Placement(transformation(origin = {-42, 0}, 
    extent = {{-10, -10}, {10, 10}})));
  TYWebHandling.Webs.Web_Spring web_Spring2 
    annotation(Placement(transformation(origin = {39.25, 0}, 
    extent = {{-10, -10}, {10, 10}})));
  TYWebHandling.Rollers.Roller roller1(D = D, UseAlternative = true) 
    annotation(Placement(transformation(origin = {80.5, 0}, 
    extent = {{-10, -10}, {10, 10}})));
  TYWebHandling.Webs.Web_Spring web_Spring3 
    annotation(Placement(transformation(origin = {121.75, 0}, 
    extent = {{-10, -10}, {10, 10}})));
  TYWebHandling.Webs.Web_Spring web_Spring4 
    annotation(Placement(transformation(origin = {204.25, 0}, 
    extent = {{-10, -10}, {10, 10}})));
  TYWebHandling.Rollers.Roller roller2(UseAlternative = true, D = D) 
    annotation(Placement(transformation(origin = {245.5, 0}, 
    extent = {{-10, -10}, {10, 10}})));
  Modelica.Mechanics.MultiBody.Parts.Fixed fixed(r = {0, 2, 0}, animation = false) 
    annotation(Placement(transformation(origin = {-80, -58}, 
    extent = {{-10, -10}, {10, 10}}, 
    rotation = 90)));
  Modelica.Mechanics.MultiBody.Parts.Fixed fixed1(r = {0.5, 2.5, 0}, animation = false) 
    annotation(Placement(transformation(origin = {-2, -58}, 
    extent = {{-10, -10}, {10, 10}}, 
    rotation = 90)));
  Modelica.Mechanics.MultiBody.Parts.Fixed fixed2(r = {1, 2, 0}, animation = false) 
    annotation(Placement(transformation(origin = {80.5, -58}, 
    extent = {{-10, -10}, {10, 10}}, 
    rotation = 90)));
  Modelica.Mechanics.MultiBody.Parts.Fixed fixed3(r = {1.5, 2.5, 0}, animation = false) 
    annotation(Placement(transformation(origin = {163, -58}, 
    extent = {{-10, -10}, {10, 10}}, 
    rotation = 90)));
  Modelica.Mechanics.MultiBody.Parts.Fixed fixed4(r = {2, 2, 0}, animation = false) 
    annotation(Placement(transformation(origin = {245.5, -58}, 
    extent = {{-10, -10}, {10, 10}}, 
    rotation = 90)));
  TYWebHandling.Webs.Web_Spring web_Spring5 
    annotation(Placement(transformation(origin = {290.75, 0}, 
    extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Sources.Constant const(k = T) 
    annotation(Placement(transformation(origin = {-160, 30}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Sources.Constant const1(k = V) 
    annotation(Placement(transformation(origin = {-160, -6}, 
    extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Sources.Constant const2(k = T) 
    annotation(Placement(transformation(origin = {388, 6}, 
    extent = {{10, -10}, {-10, 10}})));
  Modelica.Mechanics.MultiBody.Parts.Fixed fixed5(r = {2.5, 2.5, 0}, animation = false) 
    annotation(Placement(transformation(origin = {336, -58}, 
    extent = {{-10, -10}, {10, 10}}, 
    rotation = 90)));
  Modelica.Mechanics.Rotational.Sources.Speed speed 
    annotation(Placement(transformation(origin = {-40, 70}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Sources.Constant const3(k = 2 * V / D) 
    annotation(Placement(transformation(origin = {-80, 70}, 
    extent = {{-10, -10}, {10, 10}})));
  Modelica.Mechanics.Rotational.Sources.Speed speed1 
    annotation(Placement(transformation(origin = {56, 70}, 
    extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Sources.Constant const4(k = 2 * V / D) 
    annotation(Placement(transformation(origin = {16, 70}, 
    extent = {{-10, -10}, {10, 10}})));
  Modelica.Mechanics.Rotational.Sources.Speed speed2 
    annotation(Placement(transformation(origin = {136, 70}, 
    extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Sources.Constant const5(k = 2 * V / D) 
    annotation(Placement(transformation(origin = {96, 70}, 
    extent = {{-10, -10}, {10, 10}})));
  Modelica.Mechanics.Rotational.Sources.Speed speed3 
    annotation(Placement(transformation(origin = {290.75, 70}, 
    extent = {{10, -10}, {-10, 10}})));
  Modelica.Blocks.Sources.Sine sine(amplitude = 0.0001, startTime = 5, f = 0.5, offset = 2 * V / D) 
    annotation(Placement(transformation(origin = {336, 70}, 
    extent = {{10, -10}, {-10, 10}})));
equation
  connect(webSource.webPort_a, web_Spring1.webPort_a) 
    annotation(Line(origin = {-61, 6}, 
    points = {{-9, 0}, {9, 0}}, 
    color = {96, 96, 96}, 
    thickness = 0.5));
  connect(roller.webPort_b, web_Spring1.webPort_b) 
    annotation(Line(origin = {-22, 6}, 
    points = {{10, 0}, {-10, 0}}, 
    color = {96, 96, 96}, 
    thickness = 0.5));
  connect(webSource.frame_c, fixed.frame_b) 
    annotation(Line(origin = {-80, -29}, 
    points = {{0, 19}, {0, -19}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(roller.frame_c, fixed1.frame_b) 
    annotation(Line(origin = {-2, -29}, 
    points = {{-1.77636e-15, 19}, {-1.77636e-15, -19}, {0, -19}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(roller1.frame_c, fixed2.frame_b) 
    annotation(Line(origin = {81, -29}, 
    points = {{-0.5, 19}, {-0.5, -19}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(slipRoller.frame_c, fixed3.frame_b) 
    annotation(Line(origin = {163, -29}, 
    points = {{0, 19}, {0, -19}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(roller2.frame_c, fixed4.frame_b) 
    annotation(Line(origin = {246, -29}, 
    points = {{-0.5, 19}, {-0.5, -19}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(roller.webPort_a, web_Spring2.webPort_a) 
    annotation(Line(origin = {19, 6}, 
    points = {{-11, 0}, {10.25, 0}}, 
    color = {96, 96, 96}, 
    thickness = 0.5));
  connect(web_Spring2.webPort_b, roller1.webPort_b) 
    annotation(Line(origin = {60, 6}, 
    points = {{-10.75, 0}, {10.5, 0}}, 
    color = {96, 96, 96}, 
    thickness = 0.5));
  connect(roller1.webPort_a, web_Spring3.webPort_a) 
    annotation(Line(origin = {101, 6}, 
    points = {{-10.5, 0}, {10.75, 0}}, 
    color = {96, 96, 96}, 
    thickness = 0.5));
  connect(web_Spring3.webPort_b, slipRoller.webPort_b) 
    annotation(Line(origin = {142, 6}, 
    points = {{-10.25, 0}, {11, 0}}, 
    color = {96, 96, 96}, 
    thickness = 0.5));
  connect(slipRoller.webPort_a, web_Spring4.webPort_a) 
    annotation(Line(origin = {184, 6}, 
    points = {{-11, 0}, {10.25, 0}}, 
    color = {96, 96, 96}, 
    thickness = 0.5));
  connect(web_Spring4.webPort_b, roller2.webPort_b) 
    annotation(Line(origin = {225, 6}, 
    points = {{-10.75, 0}, {10.5, 0}}, 
    color = {96, 96, 96}, 
    thickness = 0.5));
  connect(roller2.webPort_a, web_Spring5.webPort_a) 
    annotation(Line(origin = {268, 6}, 
    points = {{-12.5, 0}, {12.75, 0}}, 
    color = {96, 96, 96}, 
    thickness = 0.5));
  connect(webSink.frame_a, web_Spring5.frame_b) 
    annotation(Line(origin = {313, 0}, 
    points = {{13, -2.88658e-16}, {-12.25, 0}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(roller2.frame_b, web_Spring5.frame_a) 
    annotation(Line(origin = {268, 0}, 
    points = {{-12.5, 0}, {12.75, 0}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(web_Spring4.frame_b, roller2.frame_a) 
    annotation(Line(origin = {225, 0}, 
    points = {{-10.75, 0}, {10.5, 0}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(slipRoller.frame_b, web_Spring4.frame_a) 
    annotation(Line(origin = {184, 0}, 
    points = {{-11, 0}, {10.25, 0}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(slipRoller.frame_a, web_Spring3.frame_b) 
    annotation(Line(origin = {142, 0}, 
    points = {{11, 0}, {-10.25, 0}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(web_Spring3.frame_a, roller1.frame_b) 
    annotation(Line(origin = {101, 0}, 
    points = {{10.75, 0}, {-10.5, 0}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(roller1.frame_a, web_Spring2.frame_b) 
    annotation(Line(origin = {60, 0}, 
    points = {{10.5, 0}, {-10.75, 0}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(web_Spring2.frame_a, roller.frame_b) 
    annotation(Line(origin = {19, 0}, 
    points = {{10.25, 0}, {-11, 0}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(roller.frame_a, web_Spring1.frame_b) 
    annotation(Line(origin = {-22, 0}, 
    points = {{10, 0}, {-10, 0}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(web_Spring1.frame_a, webSource.frame_a) 
    annotation(Line(origin = {-61, 0}, 
    points = {{9, 0}, {-9, 0}, {-9, -1.44329e-16}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(const1.y, webSource.vin) 
    annotation(Line(origin = {-120, -6}, 
    points = {{-29, 0}, {28.8, 0}}, 
    color = {0, 0, 127}));
  connect(const.y, webSource.Ftin) 
    annotation(Line(origin = {-120, 18}, 
    points = {{-29, 12}, {-8, 12}, {-8, -12}, {28.8, -12}}, 
    color = {0, 0, 127}));
  connect(fixed5.frame_b, webSink.frame_c) 
    annotation(Line(origin = {336, -29}, 
    points = {{5.68434e-14, -19}, {5.68434e-14, 18.8}, {0, 18.8}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(webSink.Ftin, const2.y) 
    annotation(Line(origin = {362, 6}, 
    points = {{-15.2, 0}, {15, 0}}, 
    color = {0, 0, 127}));
  connect(speed.w_ref, const3.y) 
    annotation(Line(origin = {-77, 70}, 
    points = {{25, 0}, {8, 0}}, 
    color = {0, 0, 127}));
  connect(speed1.w_ref, const4.y) 
    annotation(Line(origin = {19, 70}, 
    points = {{25, 0}, {8, 0}}, 
    color = {0, 0, 127}));
  connect(speed2.w_ref, const5.y) 
    annotation(Line(origin = {99, 70}, 
    points = {{25, 0}, {8, 0}}, 
    color = {0, 0, 127}));
  connect(sine.y, speed3.w_ref) 
    annotation(Line(origin = {314, 70}, 
    points = {{11, 0}, {-11.25, 0}}, 
    color = {0, 0, 127}));
  connect(speed3.flange, roller2.flange_a) 
    annotation(Line(origin = {263, 35}, 
    points = {{17.75, 35}, {-17.5, 35}, {-17.5, -35}}, 
    color = {0, 0, 0}));
  connect(speed2.flange, slipRoller.flange_a) 
    annotation(Line(origin = {155, 35}, 
    points = {{-9, 35}, {8, 35}, {8, -35}}, 
    color = {0, 0, 0}));
  connect(speed1.flange, roller1.flange_a) 
    annotation(Line(origin = {73, 35}, 
    points = {{-7, 35}, {7.5, 35}, {7.5, -35}}, 
    color = {0, 0, 0}));
  connect(speed.flange, roller.flange_a) 
    annotation(Line(origin = {-16, 35}, 
    points = {{-14, 35}, {14, 35}, {14, -35}}, 
    color = {0, 0, 0}));
  connect(web_Spring5.webPort_b, webSink.webPort_b) 
    annotation(Line(origin = {313, 6}, 
    points = {{-12.25, 0}, {13, 0}}, 
    color = {96, 96, 96}, 
    thickness = 0.5));
  annotation(Diagram(coordinateSystem(extent = {{-186, -100}, {408, 164}}, 
    grid = {2, 2}), graphics = {Rectangle(origin = {111, 32}, 
    fillColor = {255, 255, 255}, 
    pattern = LinePattern.None, 
    extent = {{-299, 132}, {299, -132}})}), 
    Icon(coordinateSystem(extent = {{-100, -100}, {100, 100}}, 
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
    thickness = 5)}), 
    experiment(Algorithm = Dassl, InlineIntegrator = false, InlineStepSize = false, IntegratorStep = 0.0001, StartTime = 0, StopTime = 20, Tolerance = 1e-06, Interval = 0.001), __MWORKS(ContinueSimConfig(SaveContinueFile = "false", SaveBeforeStop = "false", NumberBeforeStop = 1, FixedContinueInterval = "false", ContinueIntervalLength = 20, ContinueTimeVector),ResultViewerManager(resultViewers={
ResultViewer(name="1", executeTrigger=executeTrigger.SimulationFinished, commands={
CreatePlot(id=1, x_display_unit="s", legend_layout=1, left_title_type=2, left_title="[N]", bottom_title_type=2, right_title_type=2, fix_time_range_value=0, zoom_x=(0, 10), zoom_y_l=(-20, 120)), 
Plot(y=["web_Spring2.Ft_b"], colors=["4278190335"]), 
CreatePlot(id=-1, x_display_unit="s", legend_layout=1, left_title_type=2, left_title="[N]", bottom_title_type=2, right_title_type=2, fix_time_range_value=0, sub_plot=(1, 2), zoom_x=(0, 10), zoom_y_l=(-20, 120)), 
Plot(y=["web_Spring3.Fi"], colors=["4278190335"]), 
CreatePlot(id=-1, x_display_unit="s", legend_layout=1, left_title_type=2, left_title="[N]", bottom_title_type=2, right_title_type=2, fix_time_range_value=0, sub_plot=(2, 2), zoom_x=(0, 10), zoom_y_l=(-20, 120)), 
Plot(y=["web_Spring4.Ft_b"], colors=["4278190335"]), 
CreatePlot(id=-1, x_display_unit="s", legend_layout=1, left_title_type=2, left_title="[N]", bottom_title_type=2, right_title_type=2, fix_time_range_value=0, sub_plot=(2, 1), zoom_x=(0, 10), zoom_y_l=(-20, 120)), 
Plot(y=["web_Spring3.Ft_b"], colors=["4278190335"])})
})), 
    Documentation(link = "modelica://TYWebHandling/Resources/html/Examples/DisturbancePropagation.html"));
end DisturbancePropagation;