model WebTensionControl "卷料张力控制"

  parameter Modelica.Units.SI.Radius R = 0.5 "浮辊框架的长度";
  parameter Modelica.Units.SI.Mass M1 = 5 "浮辊质量";
  parameter Modelica.Units.SI.Mass M2 = 10 "浮辊框架的质量";
  parameter Modelica.Units.SI.RotationalSpringConstant k = 2000 "扭转弹簧刚度";
  parameter Modelica.Units.SI.Acceleration g = 9.81 "重力加速度";
  inner TYWebHandling.WebProperties WP(th = 0.005, width = 0.15, nu = 0, dr = 0.01, E(displayUnit = "Pa"), wpColor = {255, 255, 255}, ShowExtremeTension = false) 
    annotation(Placement(transformation(origin = {-215, 101}, 
    extent = {{-10, -10}, {10, 10}})));
  TYWebHandling.Sources.UnwindDrum unwindDrum(Dinit = 0.5, roll_color1 = {0, 0, 255}, roll_color2 = {255, 255, 127}, L = 0.2) 
    annotation(Placement(transformation(origin = {-161, 47}, 
    extent = {{-10, -10}, {10, 10}})));
  Modelica.Mechanics.MultiBody.Parts.Fixed fixed(r = {0, 0, 0}, animation = false) 
    annotation(Placement(transformation(origin = {-161, 5}, 
    extent = {{-10, 10}, {10, -10}}, 
    rotation = 90)));
  TYWebHandling.Webs.Web_Spring web_spring1(stateSelect = StateSelect.never) 
    annotation(Placement(transformation(origin = {-119, 47}, 
    extent = {{-10, -10}, {10, 10}})));
  TYWebHandling.Rollers.Roller roller(D = 0.1, d = 0, roll_color1 = {0, 0, 255}, roll_color2 = {255, 255, 127}, L = 0.2, stateSelect = StateSelect.never) 
    annotation(Placement(transformation(origin = {-77, 47}, 
    extent = {{-10, -10}, {10, 10}})));
  TYWebHandling.Webs.Web_Spring web_spring2(stateSelect = StateSelect.never) 
    annotation(Placement(transformation(origin = {-30, 47}, 
    extent = {{-10, -10}, {10, 10}})));
  TYWebHandling.Rollers.Roller roller1(D = 0.1, d = 0, roll_color1 = {0, 0, 255}, roll_color2 = {255, 255, 127}, L = 0.2, useCylindricalGeometry = false, m = M1, addFrameOffset = true, rf = {-R, 0}, mf = M2, UseAlternative = true, stateSelect = StateSelect.prefer) 
    annotation(Placement(transformation(origin = {17, 47}, 
    extent = {{-10, -10}, {10, 10}})));
  Modelica.Mechanics.MultiBody.Parts.Fixed fixed2(animation = false, r = {1.6, -0.2, 0}) 
    annotation(Placement(transformation(origin = {73, -51}, 
    extent = {{-10, 10}, {10, -10}}, 
    rotation = 90)));
  TYWebHandling.Webs.Web_Spring web_spring3 
    annotation(Placement(transformation(origin = {55, 47}, 
    extent = {{-10, -10}, {10, 10}})));
  Modelica.Mechanics.MultiBody.Parts.Fixed fixed4(r = {1.5, 0.4, 0}, animation = false) 
    annotation(Placement(transformation(origin = {165, 5}, 
    extent = {{-10, 10}, {10, -10}}, 
    rotation = 90)));
  Modelica.Mechanics.MultiBody.Parts.Fixed fixed1(r = {1, 0.35, 0}, animation = false) 
    annotation(Placement(transformation(origin = {-77, 5}, 
    extent = {{-10, 10}, {10, -10}}, 
    rotation = 90)));
  Modelica.Blocks.Math.Gain gain(k = -k / (2 * R)) 
    annotation(Placement(transformation(origin = {-91, -51}, 
    extent = {{10, -10}, {-10, 10}})));
  Modelica.Blocks.Sources.Ramp ramp1(height = 200, duration = 1) 
    annotation(Placement(transformation(origin = {-119, -81}, 
    extent = {{10, -10}, {-10, 10}})));
  TYMechanics.Rotational.Sources.Torque torque 
    annotation(Placement(transformation(origin = {-215, 47}, 
    extent = {{-10, -10}, {10, 10}})));
  inner Modelica.Mechanics.MultiBody.World world(animateWorld = false, animateGravity = false) 
    annotation(Placement(transformation(origin = {-183, 101}, 
    extent = {{-10, -10}, {10, 10}})));
  TYMultibody.Joints.Revolute revolute(useAxisFlange = true) 
    annotation(Placement(transformation(origin = {37, -5}, 
    extent = {{10, -10}, {-10, 10}})));
  Modelica.Blocks.Continuous.PID PID1(k = 10, Ti = 2, initType = Modelica.Blocks.Types.Init.InitialState) 
    annotation(Placement(transformation(origin = {-183, -51}, 
    extent = {{10, -10}, {-10, 10}})));
  Modelica.Blocks.Math.Feedback feedback 
    annotation(Placement(transformation(origin = {-145, -51}, 
    extent = {{10, -10}, {-10, 10}})));
  TYMechanics.Rotational.Sensors.AngleSensor angleSensor 
    annotation(Placement(transformation(origin = {-30, -51}, 
    extent = {{10, -10}, {-10, 10}})));
  TYWebHandling.Webs.Web_Spring web_spring4 
    annotation(Placement(transformation(origin = {127, 47}, 
    extent = {{-10, -10}, {10, 10}})));
  TYWebHandling.Rollers.Roller roller2(D = 0.1, d = 0, roll_color1 = {0, 0, 255}, roll_color2 = {255, 255, 127}, L = 0.2, stateSelect = StateSelect.default) 
    annotation(Placement(transformation(origin = {93, 47}, 
    extent = {{-10, -10}, {10, 10}})));
  Modelica.Mechanics.MultiBody.Parts.Fixed fixed3(r = {1.2, 0.35, 0}, animation = false) 
    annotation(Placement(transformation(origin = {93, 5}, 
    extent = {{-10, 10}, {10, -10}}, 
    rotation = 90)));
  TYWebHandling.Sources.WebSink webSink 
    annotation(Placement(transformation(origin = {165, 47}, 
    extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Sources.Ramp ramp2(height = 3, duration = 2) 
    annotation(Placement(transformation(origin = {217, 41}, 
    extent = {{10, -10}, {-10, 10}})));
  Modelica.Blocks.Math.Gain gain1(k = -1) 
    annotation(Placement(transformation(origin = {-243, -51}, 
    extent = {{10, -10}, {-10, 10}})));
  TYMechanics.Rotational.Components.SpringDamper springDamper(phi_rel0 = -R * g / k * (M1 + M2 / 2), k = k, d = 0.01 * k, stateSelect = StateSelect.prefer, phi_rel(fixed = false, start = 0)) 
    annotation(Placement(transformation(origin = {37, -81}, 
    extent = {{10, -10}, {-10, 10}})));

equation
  connect(unwindDrum.frame_c, fixed.frame_b) 
    annotation(Line(origin = {-161, 26}, 
    points = {{0, 11}, {0, -11}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(unwindDrum.webPort_a, web_spring1.webPort_a) 
    annotation(Line(origin = {-140, 53}, 
    points = {{-11, 0}, {11, 0}}, 
    color = {96, 96, 96}, 
    thickness = 0.5));
  connect(unwindDrum.frame_a, web_spring1.frame_a) 
    annotation(Line(origin = {-140, 47}, 
    points = {{-11, 0}, {11, 0}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(web_spring1.webPort_b, roller.webPort_b) 
    annotation(Line(origin = {-98, 53}, 
    points = {{-11, 0}, {11, 0}}, 
    color = {96, 96, 96}, 
    thickness = 0.5));
  connect(roller.webPort_a, web_spring2.webPort_a) 
    annotation(Line(origin = {-51, 53}, 
    points = {{-16, 0}, {11, 0}}, 
    color = {96, 96, 96}, 
    thickness = 0.5));
  connect(web_spring2.webPort_b, roller1.webPort_b) 
    annotation(Line(origin = {-4, 53}, 
    points = {{-16, 0}, {11, 0}}, 
    color = {96, 96, 96}, 
    thickness = 0.5));
  connect(roller1.frame_a, web_spring2.frame_b) 
    annotation(Line(origin = {-4, 47}, 
    points = {{11, 0}, {-16, 0}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(web_spring2.frame_a, roller.frame_b) 
    annotation(Line(origin = {-51, 47}, 
    points = {{11, 0}, {-16, 0}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(roller.frame_a, web_spring1.frame_b) 
    annotation(Line(origin = {-98, 47}, 
    points = {{11, 0}, {-11, 0}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(roller.frame_c, fixed1.frame_b) 
    annotation(Line(origin = {-77, 26}, 
    points = {{0, 11}, {0, -11}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(torque.flange, unwindDrum.flange_a) 
    annotation(Line(origin = {-173, 47}, 
    points = {{-32, 0}, {12, 0}}, 
    color = {0, 0, 0}));
  connect(roller1.frame_c, revolute.frame_b) 
    annotation(Line(origin = {21, 15}, 
    points = {{-4, 22}, {-4, -20}, {6, -20}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(revolute.frame_a, fixed2.frame_b) 
    annotation(Line(origin = {61, -23}, 
    points = {{-14, 18}, {12, 18}, {12, -18}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(PID1.u, feedback.y) 
    annotation(Line(origin = {-162, -51}, 
    points = {{-9, 0}, {8, 0}}, 
    color = {0, 0, 127}));
  connect(feedback.u2, ramp1.y) 
    annotation(Line(origin = {-137, -70}, 
    points = {{-8, 11}, {-8, -11}, {7, -11}}, 
    color = {0, 0, 127}));
  connect(feedback.u1, gain.y) 
    annotation(Line(origin = {-112, -51}, 
    points = {{-25, 0}, {10, 0}}, 
    color = {0, 0, 127}));
  connect(angleSensor.flange, revolute.axis) 
    annotation(Line(origin = {6, -34}, 
    points = {{-26, -17}, {11, -17}, {11, 19}, {24, 19}}, 
    color = {96, 96, 96}));
  connect(roller2.frame_c, fixed3.frame_b) 
    annotation(Line(origin = {-67, 36}, 
    points = {{160, 1}, {160, -21}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(roller1.webPort_a, web_spring3.webPort_a) 
    annotation(Line(origin = {38, 53}, 
    points = {{-11, 0}, {7, 0}}, 
    color = {96, 96, 96}, 
    thickness = 0.5));
  connect(roller1.frame_b, web_spring3.frame_a) 
    annotation(Line(origin = {38, 47}, 
    points = {{-11, 0}, {7, 0}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(web_spring3.webPort_b, roller2.webPort_b) 
    annotation(Line(origin = {76, 53}, 
    points = {{-11, 0}, {7, 0}}, 
    color = {96, 96, 96}, 
    thickness = 0.5));
  connect(web_spring3.frame_b, roller2.frame_a) 
    annotation(Line(origin = {76, 47}, 
    points = {{-11, 0}, {7, 0}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(roller2.webPort_a, web_spring4.webPort_a) 
    annotation(Line(origin = {110, 53}, 
    points = {{-7, 0}, {7, 0}}, 
    color = {96, 96, 96}, 
    thickness = 0.5));
  connect(roller2.frame_b, web_spring4.frame_a) 
    annotation(Line(origin = {110, 47}, 
    points = {{-7, 0}, {7, 0}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(web_spring4.frame_b, webSink.frame_a) 
    annotation(Line(origin = {146, 47}, 
    points = {{-9, 0}, {9, 0}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(webSink.vin, ramp2.y) 
    annotation(Line(origin = {191, 41}, 
    points = {{-15.2, 0}, {15, 0}}, 
    color = {0, 0, 127}));
  connect(PID1.y, gain1.u) 
    annotation(Line(origin = {-212, -51}, 
    points = {{18, 0}, {-19, 0}}, 
    color = {0, 0, 127}));
  connect(gain1.y, torque.tau_ref) 
    annotation(Line(origin = {-236, -2}, 
    points = {{-18, -49}, {-31, -49}, {-31, 49}, {11, 49}}, 
    color = {0, 0, 127}));
  connect(webSink.frame_c, fixed4.frame_b) 
    annotation(Line(origin = {165, 26}, 
    points = {{0, 10.8}, {0, -11}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(gain.u, angleSensor.phi) 
    annotation(Line(origin = {-48, -38}, 
    points = {{-31, -13}, {10, -13}}, 
    color = {0, 0, 127}));
  connect(springDamper.flange_a, revolute.support) 
    annotation(Line(origin = {47, -48}, 
    points = {{0, -33}, {3, -33}, {3, -19}, {-3, -19}, {-3, 33}}, 
    color = {96, 96, 96}));
  connect(springDamper.flange_b, revolute.axis) 
    annotation(Line(origin = {27, -48}, 
    points = {{0, -33}, {-3, -33}, {-3, -19}, {3, -19}, {3, 33}}, 
    color = {0, 0, 0}));
  connect(web_spring4.webPort_b, webSink.webPort_b) 
    annotation(Line(origin = {146, 53}, 
    points = {{-9, 0}, {9, 0}}, 
    color = {96, 96, 96}, 
    thickness = 0.5));
  annotation(Diagram(coordinateSystem(extent = {{-274, -104}, {238, 126}}, 
    grid = {2, 2}), graphics = {Rectangle(origin = {-18, 11}, 
    lineColor = {255, 255, 255}, 
    fillColor = {255, 255, 255}, 
    pattern = LinePattern.None, 
    extent = {{-256, 115}, {256, -115}})}), Icon(coordinateSystem(extent = {{-100, -100}, {100, 100}}, 
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
    thickness = 5)}), experiment(Algorithm = Dassl, InlineIntegrator = false, InlineStepSize = false, Interval = 0.001, StartTime = 0, StopTime = 10, Tolerance = 1e-06, IntegratorStep = 0.0001), __MWORKS(ResultViewerManager(resultViewers={
ResultViewer(name="1", executeTrigger=executeTrigger.SimulationFinished, commands={
CreatePlot(id=4, x_display_unit="s", legend_layout=1, left_title_type=2, left_title="[N]", bottom_title_type=2, right_title_type=2, curve_vernier=True, fix_time_range_value=0, zoom_x=(0, 10), zoom_y_l=(-50, 250)), 
Plot(y=["webSink.Ftout"], colors=["4278190335"]), 
CreatePlot(id=-1, x_display_unit="s", legend_layout=1, left_title="[rad]", curve_vernier=True, fix_time_range_value=0, sub_plot=(2, 1), zoom_x=(0, 10), zoom_y_l=(-0.12, 0.02)), 
Plot(y=["gain.u"], colors=["4278190335"]), 
CreatePlot(id=-1, x_display_unit="s", legend_layout=1, left_title="[N.m]", curve_vernier=True, fix_time_range_value=0, sub_plot=(3, 1), zoom_x=(0, 10), zoom_y_l=(-60, 100)), 
Plot(y=["torque.T"], colors=["4278190335"])})
}),ContinueSimConfig(SaveContinueFile = "false", SaveBeforeStop = "false", NumberBeforeStop = 1, FixedContinueInterval = "false", ContinueIntervalLength = 5, ContinueTimeVector)), 
    Documentation(link = "modelica://TYWebHandling/Resources/html/Examples/WebTensionControl.html"));
end WebTensionControl;