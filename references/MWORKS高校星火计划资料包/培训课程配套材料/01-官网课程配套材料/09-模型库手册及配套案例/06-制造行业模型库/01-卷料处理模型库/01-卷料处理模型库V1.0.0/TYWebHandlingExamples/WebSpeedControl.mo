model WebSpeedControl "卷料区域速度控制"

  parameter Modelica.SIunits.Length th(displayUnit = "mm") = 0.005 "卷料的厚度";
  inner TYWebHandling.WebProperties WP(th = th, width = 1, nu = 0, dr = 0.01, E(displayUnit = "Pa"), wpColor = {255, 255, 255}) 
    annotation(Placement(transformation(origin = {-130, 54}, 
    extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Sources.Ramp ramp(height = 40, duration = 4) 
    annotation(Placement(transformation(origin = {-178, -24}, 
    extent = {{-10, -10}, {10, 10}})));
  TYWebHandling.Sources.UnwindDrum unwindDrum(Dinit = 1, roll_color1 = {0, 0, 255}, roll_color2 = {255, 255, 127}) 
    annotation(Placement(transformation(origin = {-110, -24}, 
    extent = {{-10, -10}, {10, 10}})));
  Modelica.Mechanics.MultiBody.Parts.Fixed fixed(r = {0, 0, 0}, animation = false) 
    annotation(Placement(transformation(origin = {-110, -66}, 
    extent = {{-10, 10}, {10, -10}}, 
    rotation = 90)));
  TYWebHandling.Webs.Web_Spring web_spring 
    annotation(Placement(transformation(origin = {-68, -24}, 
    extent = {{-10, -10}, {10, 10}})));
  TYWebHandling.Rollers.Roller roller(D = 0.2, L = 1.2, d = 0.01, roll_color1 = {0, 0, 255}, roll_color2 = {255, 255, 127}) 
    annotation(Placement(transformation(origin = {-26, -24}, 
    extent = {{-10, -10}, {10, 10}})));
  TYWebHandling.Webs.Web_Spring web_spring1 
    annotation(Placement(transformation(origin = {26, -24}, 
    extent = {{-10, -10}, {10, 10}})));
  TYWebHandling.Rollers.Roller roller1(D = 0.2, L = 1.2, d = 0.01, roll_color1 = {0, 0, 255}, roll_color2 = {255, 255, 127}) 
    annotation(Placement(transformation(origin = {68, -24}, 
    extent = {{-10, -10}, {10, 10}})));
  Modelica.Mechanics.MultiBody.Parts.Fixed fixed2(animation = false, r = {2, 1, 0}) 
    annotation(Placement(transformation(origin = {68, -66}, 
    extent = {{-10, 10}, {10, -10}}, 
    rotation = 90)));
  TYWebHandling.Webs.Web_Spring web_spring3 
    annotation(Placement(transformation(origin = {110, -24}, 
    extent = {{-10, -10}, {10, 10}})));
  Modelica.Mechanics.MultiBody.Parts.Fixed fixed4(r = {3, 0, 0}, animation = false) 
    annotation(Placement(transformation(origin = {150, -66}, 
    extent = {{-10, 10}, {10, -10}}, 
    rotation = 90)));
  Modelica.Mechanics.MultiBody.Parts.Fixed fixed1(r = {1, 1, 0}, animation = false) 
    annotation(Placement(transformation(origin = {-26, -66}, 
    extent = {{-10, 10}, {10, -10}}, 
    rotation = 90)));
  TYWebHandling.Sources.WindDrum windDrum(Dinit = 0.1, roll_color1 = {0, 0, 255}, roll_color2 = {255, 255, 127}) 
    annotation(Placement(transformation(origin = {150, -24}, 
    extent = {{-10, -10}, {10, 10}})));
  Modelica.Mechanics.Rotational.Sources.Speed speed(exact = true) 
    annotation(Placement(transformation(origin = {190, -24}, 
    extent = {{10, -10}, {-10, 10}})));
  Modelica.Mechanics.Rotational.Sensors.SpeedSensor speedSensor 
    annotation(Placement(transformation(origin = {86, 18}, 
    extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Math.Gain gain(k = 0.1 + th / 2) 
    annotation(Placement(transformation(origin = {122, 18}, 
    extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Sources.Ramp ramp1(height = 5, duration = 3) 
    annotation(Placement(transformation(origin = {110, 52}, 
    extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Continuous.LimPID PID(k = 200, yMax = 100) 
    annotation(Placement(transformation(origin = {170, 52}, 
    extent = {{-10, -10}, {10, 10}})));
  inner Modelica.Mechanics.MultiBody.World world 
    annotation(Placement(transformation(origin = {-98, 54}, 
    extent = {{-10, -10}, {10, 10}})));
  Modelica.Mechanics.Rotational.Sources.Torque torque1 
    annotation(Placement(transformation(origin = {-144, -24}, 
    extent = {{-10, -10}, {10, 10}})));
equation
  connect(unwindDrum.frame_c, fixed.frame_b) 
    annotation(Line(origin = {-110, -45}, 
    points = {{0, 11}, {0, -11}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(unwindDrum.webPort_a, web_spring.webPort_a) 
    annotation(Line(origin = {-89, -18}, 
    points = {{-11, 0}, {11, 0}}, 
    color = {96, 96, 96}, 
    thickness = 0.5));
  connect(unwindDrum.frame_a, web_spring.frame_a) 
    annotation(Line(origin = {-89, -24}, 
    points = {{-11, 0}, {11, 0}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(web_spring.webPort_b, roller.webPort_b) 
    annotation(Line(origin = {-47, -18}, 
    points = {{-11, 0}, {11, 0}}, 
    color = {96, 96, 96}, 
    thickness = 0.5));
  connect(roller.webPort_a, web_spring1.webPort_a) 
    annotation(Line(origin = {0, -18}, 
    points = {{-16, 0}, {16, 0}}, 
    color = {96, 96, 96}, 
    thickness = 0.5));
  connect(web_spring1.webPort_b, roller1.webPort_b) 
    annotation(Line(origin = {47, -18}, 
    points = {{-11, 0}, {11, 0}}, 
    color = {96, 96, 96}, 
    thickness = 0.5));
  connect(roller1.frame_a, web_spring1.frame_b) 
    annotation(Line(origin = {47, -24}, 
    points = {{11, 0}, {-11, 0}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(web_spring1.frame_a, roller.frame_b) 
    annotation(Line(origin = {0, -24}, 
    points = {{16, 0}, {-16, 0}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(roller.frame_a, web_spring.frame_b) 
    annotation(Line(origin = {-47, -24}, 
    points = {{11, 0}, {-11, 0}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(roller1.frame_c, fixed2.frame_b) 
    annotation(Line(origin = {68, -45}, 
    points = {{0, 11}, {0, -11}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(roller1.webPort_a, web_spring3.webPort_a) 
    annotation(Line(origin = {134, -18}, 
    points = {{-56, 0}, {-34, 0}}, 
    color = {96, 96, 96}, 
    thickness = 0.5));
  connect(roller1.frame_b, web_spring3.frame_a) 
    annotation(Line(origin = {134, -24}, 
    points = {{-56, 0}, {-34, 0}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(roller.frame_c, fixed1.frame_b) 
    annotation(Line(origin = {-26, -45}, 
    points = {{0, 11}, {0, -11}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(windDrum.frame_c, fixed4.frame_b) 
    annotation(Line(origin = {150, -45}, 
    points = {{0, 11}, {0, -11}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(windDrum.webPort_b, web_spring3.webPort_b) 
    annotation(Line(origin = {130, -18}, 
    points = {{10, 0}, {-10, 0}}, 
    color = {96, 96, 96}, 
    thickness = 0.5));
  connect(web_spring3.frame_b, windDrum.frame_a) 
    annotation(Line(origin = {130, -24}, 
    points = {{-10, 0}, {10, 0}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(speed.flange, windDrum.flange_a) 
    annotation(Line(origin = {168, -23}, 
    points = {{12, -1}, {-18, -1}}, 
    color = {0, 0, 0}));
  connect(speedSensor.flange, roller1.flange_a) 
    annotation(Line(origin = {72, -3}, 
    points = {{4, 21}, {-4, 21}, {-4, -21}}, 
    color = {0, 0, 0}));
  connect(speedSensor.w, gain.u) 
    annotation(Line(origin = {111, 18}, 
    points = {{-14, 0}, {-1, 0}}, 
    color = {0, 0, 127}));
  connect(ramp1.y, PID.u_s) 
    annotation(Line(origin = {140, 52}, 
    points = {{-19, 0}, {18, 0}}, 
    color = {0, 0, 127}));
  connect(gain.y, PID.u_m) 
    annotation(Line(origin = {152, 29}, 
    points = {{-19, -11}, {18, -11}, {18, 11}}, 
    color = {0, 0, 127}));
  connect(PID.y, speed.w_ref) 
    annotation(Line(origin = {206, 14}, 
    points = {{-25, 38}, {24, 38}, {24, -38}, {-4, -38}}, 
    color = {0, 0, 127}));
  connect(ramp.y, torque1.tau) 
    annotation(Line(origin = {-161, -24}, 
    points = {{-6, 0}, {5, 0}}, 
    color = {0, 0, 127}));
  connect(torque1.flange, unwindDrum.flange_a) 
    annotation(Line(origin = {-122, -24}, 
    points = {{-12, 0}, {12, 0}}, 
    color = {0, 0, 0}));
  annotation(Diagram(coordinateSystem(extent = {{-224, -100}, {250, 100}}, 
    grid = {2, 2}), graphics = {Rectangle(origin = {13, 0}, 
    lineColor = {255, 255, 255}, 
    fillColor = {255, 255, 255}, 
    pattern = LinePattern.None, 
    extent = {{-237, 100}, {237, -100}})}), Icon(coordinateSystem(extent = {{-100, -100}, {100, 100}}, 
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
    thickness = 5)}), experiment(Algorithm = Dassl, InlineIntegrator = false, InlineStepSize = false, Interval = 0.001, StartTime = 0, StopTime = 20, Tolerance = 1e-05), __MWORKS(ContinueSimConfig(SaveContinueFile = "false", SaveBeforeStop = "false", NumberBeforeStop = 1, FixedContinueInterval = "false", ContinueIntervalLength = 2, ContinueTimeVector),ResultViewerManager(resultViewers={
ResultViewer(name="1", executeTrigger=executeTrigger.SimulationFinished, commands={
CreatePlot(id=1, x_display_unit="s", legend_layout=1, left_title_type=2, left_title="收卷辊瞬时半径 [m]", bottom_title_type=2, right_title_type=2, fix_time_range_value=0, zoom_x=(0, 20), zoom_y_l=(0, 0.5)), 
Plot(legend=[" windDrum.Rtime [m]"], y=["windDrum.Rtime"], colors=["4278190335"]), 
CreatePlot(id=-1, x_display_unit="s", legend_layout=1, left_title="[rad/s]", fix_time_range_value=0, sub_plot=(1, 2), zoom_x=(0, 20), zoom_y_l=(-50, 10)), 
Plot(y=["windDrum.w"], colors=["4278190335"]), 
CreatePlot(id=-1, x_display_unit="s", legend_layout=1, left_title="[m]", fix_time_range_value=0, sub_plot=(2, 2), zoom_x=(0, 20), zoom_y_l=(0.3, 0.55)), 
Plot(y=["unwindDrum.Rtime"], colors=["4278190335"]), 
CreatePlot(id=-1, x_display_unit="s", legend_layout=1, left_title="[m/s]", fix_time_range_value=0, sub_plot=(2, 1), zoom_x=(0, 20), zoom_y_l=(-1, 6)), 
Plot(y=["web_spring1.v_b"], colors=["4278190335"]), 
CreatePlot(id=-1, x_display_unit="s", legend_layout=1, left_title="[N]", fix_time_range_value=0, sub_plot=(3, 2), zoom_x=(0, 20), zoom_y_l=(-200, 1200)), 
Plot(y=["web_spring1.Fi"], colors=["4278190335"]), 
CreatePlot(id=-1, x_display_unit="s", legend_layout=1, left_title="[N]", fix_time_range_value=0, sub_plot=(3, 1), zoom_x=(0, 20), zoom_y_l=(-200, 1000)), 
Plot(y=["web_spring.Fi"], colors=["4278190335"]), 
CreatePlot(id=-1, x_display_unit="s", legend_layout=1, left_title="[N]", fix_time_range_value=0, sub_plot=(4, 2), zoom_x=(0, 20), zoom_y_l=(-200, 1200)), 
Plot(y=["web_spring3.Fi"], colors=["4278190335"]), 
CreatePlot(id=-1, x_display_unit="s", legend_layout=1, left_title="[N.m]", fix_time_range_value=0, sub_plot=(4, 1), zoom_x=(0, 20), zoom_y_l=(-10, 50)), 
Plot(y=["ramp.y"], colors=["4278190335"])})
})), 
    Documentation(link = "modelica://TYWebHandling/Resources/html/Examples/WebSpeedControl.html"));
end WebSpeedControl;