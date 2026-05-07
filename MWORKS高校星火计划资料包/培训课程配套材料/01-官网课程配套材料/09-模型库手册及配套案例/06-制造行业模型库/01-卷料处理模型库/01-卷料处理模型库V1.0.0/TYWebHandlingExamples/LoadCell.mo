model LoadCell "负载传感器测试"
  inner TYWebHandling.WebProperties WP(th = 0.005, width = 0.3, nu = 0, dr = 0.01, E(displayUnit = "Pa"), wpColor = {255, 255, 255}) 
    annotation(Placement(transformation(origin = {-86, 57}, 
    extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Sources.Ramp ramp(height = 50, duration = 5) 
    annotation(Placement(transformation(origin = {-180, 3}, 
    extent = {{-10, -10}, {10, 10}})));
  TYWebHandling.Sources.UnwindDrum unwindDrum(L = 0.4, roll_color1 = {0, 0, 255}, roll_color2 = {255, 255, 0}, Dinit = 1) 
    annotation(Placement(transformation(origin = {-109, 3}, 
    extent = {{-10, -10}, {10, 10}})));
  Modelica.Mechanics.MultiBody.Parts.Fixed fixed(r = {-1, 0, 0}, animation = false) 
    annotation(Placement(transformation(origin = {-109, -39}, 
    extent = {{-10, 10}, {10, -10}}, 
    rotation = 90)));
  TYWebHandling.Webs.Web_Spring web_spring 
    annotation(Placement(transformation(origin = {-67, 3}, 
    extent = {{-10, -10}, {10, 10}})));
  TYWebHandling.Rollers.Roller roller(D = 0.2, L = 0.4, UseAlternative = true) 
    annotation(Placement(transformation(origin = {-25, 3}, 
    extent = {{-10, -10}, {10, 10}})));
  TYWebHandling.Webs.Web_Spring web_spring1 
    annotation(Placement(transformation(origin = {27, 3}, 
    extent = {{-10, -10}, {10, 10}})));
  TYWebHandling.Rollers.Roller roller1(D = 0.2, L = 0.4, useCylindricalGeometry = false, m = 20, mf = 0) 
    annotation(Placement(transformation(origin = {69, 3}, 
    extent = {{-10, -10}, {10, 10}})));
  TYWebHandling.Webs.Web_Spring web_spring2 
    annotation(Placement(transformation(origin = {117, 3}, 
    extent = {{-10, -10}, {10, 10}})));
  TYWebHandling.Rollers.Roller roller2(L = 0.4, D = 0.2, useCylindricalGeometry = true, UseAlternative = true) 
    annotation(Placement(transformation(origin = {159, 3}, 
    extent = {{-10, -10}, {10, 10}})));
  Modelica.Mechanics.MultiBody.Parts.Fixed fixed3(r = {0.7, 0, 0}, animation = false) 
    annotation(Placement(transformation(origin = {159, -39}, 
    extent = {{-10, 10}, {10, -10}}, 
    rotation = 90)));
  TYWebHandling.Webs.Web_Spring web_spring3 
    annotation(Placement(transformation(origin = {201, 3}, 
    extent = {{-10, -10}, {10, 10}})));
  TYWebHandling.Sources.WebSink webSink 
    annotation(Placement(transformation(origin = {241, 3}, 
    extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Sources.Ramp ramp1(height = 5, duration = 5) 
    annotation(Placement(transformation(origin = {295, -3}, 
    extent = {{10, -10}, {-10, 10}})));
  Modelica.Mechanics.MultiBody.Parts.Fixed fixed4(r = {1, -0.1, 0}, animation = false) 
    annotation(Placement(transformation(origin = {241, -39}, 
    extent = {{-10, 10}, {10, -10}}, 
    rotation = 90)));
  inner Modelica.Mechanics.MultiBody.World world(gravityType = Modelica.Mechanics.MultiBody.Types.GravityTypes.UniformGravity) 
    annotation(Placement(transformation(origin = {-38, 57}, 
    extent = {{-10, -10}, {10, 10}})));
  Modelica.Mechanics.Rotational.Sources.Torque torque1 
    annotation(Placement(transformation(origin = {-151, 3}, 
    extent = {{-10, -10}, {10, 10}})));
  Modelica.Mechanics.MultiBody.Parts.Fixed fixed2(animation = false, r = {-0.3, -0.1, 0}) 
    annotation(Placement(transformation(origin = {-25, -39}, 
    extent = {{-10, 10}, {10, -10}}, 
    rotation = 90)));
  TYWebHandling.Sensors.LoadSensor loadSensor(r = {0, 0.5, 0}) 
    annotation(Placement(transformation(origin = {68, -81}, 
    extent = {{-10, -10}, {10, 10}})));
  TYWebHandling.Sensors.InclineSensor inclineSensor 
    annotation(Placement(transformation(origin = {27, -65}, 
    extent = {{-10, -10}, {10, 10}})));
  TYWebHandling.Sensors.InclineSensor inclineSensor1 
    annotation(Placement(transformation(origin = {117, -47}, 
    extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Math.Cos cos1 
    annotation(Placement(transformation(origin = {51, -144}, 
    extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Math.Sin sin1 
    annotation(Placement(transformation(origin = {51, -191}, 
    extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Math.Sin sin2 
    annotation(Placement(transformation(origin = {137, -161}, 
    extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Math.Cos cos2 
    annotation(Placement(transformation(origin = {146, -109}, 
    extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Math.Product Fx 
    annotation(Placement(transformation(origin = {271, -81}, 
    extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Math.Add add(k2 = -1) 
    annotation(Placement(transformation(origin = {189, -138}, 
    extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Math.Add add1(k2 = -1) 
    annotation(Placement(transformation(origin = {175, -185}, 
    extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Math.Add add2 
    annotation(Placement(transformation(origin = {137, -219}, 
    extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Sources.Constant const(k = 9.80665 * 20) 
    annotation(Placement(transformation(origin = {68, -225}, 
    extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Math.Division division 
    annotation(Placement(transformation(origin = {235.5, -179}, 
    extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Sources.Constant const1(k = 1) 
    annotation(Placement(transformation(origin = {200, -161}, 
    extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Math.Product Fy 
    annotation(Placement(transformation(origin = {271, -185}, 
    extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Math.Division division1 
    annotation(Placement(transformation(origin = {241, -109}, 
    extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Sources.Constant const2(k = 1) 
    annotation(Placement(transformation(origin = {189, -103}, 
    extent = {{-10, -10}, {10, 10}})));
equation
  connect(unwindDrum.frame_c, fixed.frame_b) 
    annotation(Line(origin = {-109, -18}, 
    points = {{0, 11}, {0, -11}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(unwindDrum.webPort_a, web_spring.webPort_a) 
    annotation(Line(origin = {-88, 9}, 
    points = {{-11, 0}, {11, 0}}, 
    color = {96, 96, 96}, 
    thickness = 0.5));
  connect(unwindDrum.frame_a, web_spring.frame_a) 
    annotation(Line(origin = {-88, 3}, 
    points = {{-11, 0}, {11, 0}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(ramp1.y, webSink.vin) 
    annotation(Line(origin = {268, -3}, 
    points = {{16, 0}, {-16.2, 0}}, 
    color = {0, 0, 127}));
  connect(web_spring.webPort_b, roller.webPort_b) 
    annotation(Line(origin = {-46, 9}, 
    points = {{-11, 0}, {11, 0}}, 
    color = {96, 96, 96}, 
    thickness = 0.5));
  connect(roller.webPort_a, web_spring1.webPort_a) 
    annotation(Line(origin = {1, 9}, 
    points = {{-16, 0}, {16, 0}}, 
    color = {96, 96, 96}, 
    thickness = 0.5));
  connect(web_spring1.webPort_b, roller1.webPort_b) 
    annotation(Line(origin = {48, 9}, 
    points = {{-11, 0}, {11, 0}}, 
    color = {96, 96, 96}, 
    thickness = 0.5));
  connect(roller1.webPort_a, web_spring2.webPort_a) 
    annotation(Line(origin = {93, 9}, 
    points = {{-14, 0}, {14, 0}}, 
    color = {96, 96, 96}, 
    thickness = 0.5));
  connect(web_spring2.webPort_b, roller2.webPort_b) 
    annotation(Line(origin = {138, 9}, 
    points = {{-11, 0}, {11, 0}}, 
    color = {96, 96, 96}, 
    thickness = 0.5));
  connect(roller2.webPort_a, web_spring3.webPort_a) 
    annotation(Line(origin = {180, 9}, 
    points = {{-11, 0}, {11, 0}}, 
    color = {96, 96, 96}, 
    thickness = 0.5));
  connect(webSink.frame_a, web_spring3.frame_b) 
    annotation(Line(origin = {221, 3}, 
    points = {{10, 0}, {-10, 0}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(web_spring3.frame_a, roller2.frame_b) 
    annotation(Line(origin = {180, 3}, 
    points = {{11, 0}, {-11, 0}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(roller2.frame_a, web_spring2.frame_b) 
    annotation(Line(origin = {138, 3}, 
    points = {{11, 0}, {-11, 0}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(web_spring2.frame_a, roller1.frame_b) 
    annotation(Line(origin = {93, 3}, 
    points = {{14, 0}, {-14, 0}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(roller1.frame_a, web_spring1.frame_b) 
    annotation(Line(origin = {48, 3}, 
    points = {{11, 0}, {-11, 0}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(web_spring1.frame_a, roller.frame_b) 
    annotation(Line(origin = {1, 3}, 
    points = {{16, 0}, {-16, 0}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(roller.frame_a, web_spring.frame_b) 
    annotation(Line(origin = {-46, 3}, 
    points = {{11, 0}, {-11, 0}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(roller2.frame_c, fixed3.frame_b) 
    annotation(Line(origin = {159, -18}, 
    points = {{0, 11}, {0, -11}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(webSink.frame_c, fixed4.frame_b) 
    annotation(Line(origin = {241, -18}, 
    points = {{0, 10.8}, {0, -11}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(ramp.y, torque1.tau) 
    annotation(Line(origin = {-178, 3}, 
    points = {{9, 0}, {15, 0}}, 
    color = {0, 0, 127}));
  connect(torque1.flange, unwindDrum.flange_a) 
    annotation(Line(origin = {-130, 3}, 
    points = {{-11, 0}, {21, 0}}, 
    color = {0, 0, 0}));
  connect(roller.frame_c, fixed2.frame_b) 
    annotation(Line(origin = {-24, -22}, 
    points = {{-1, 15}, {-1, -7}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(roller1.frame_c, loadSensor.frame_b) 
    annotation(Line(origin = {69, -22}, 
    points = {{0, 15}, {0, -49}, {-1, -49}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(inclineSensor.frame_a, web_spring1.frame_a) 
    annotation(Line(origin = {17, -25}, 
    points = {{0, -40}, {-11, -40}, {-11, 28}, {0, 28}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(inclineSensor.frame_b, web_spring1.frame_b) 
    annotation(Line(origin = {37, -25}, 
    points = {{0, -40}, {13, -40}, {13, 28}, {0, 28}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(inclineSensor1.frame_a, web_spring2.frame_a) 
    annotation(Line(origin = {107, -31}, 
    points = {{0, -16}, {-5, -16}, {-5, 34}, {0, 34}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(inclineSensor1.frame_b, web_spring2.frame_b) 
    annotation(Line(origin = {127, -31}, 
    points = {{0, -16}, {7, -16}, {7, 34}, {0, 34}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(inclineSensor.phi_rel, cos1.u) 
    annotation(Line(origin = {16.5, -93.5}, 
    points = {{10.5, 17.5}, {10.5, -50.5}, {22.5, -50.5}}, 
    color = {0, 0, 127}));
  connect(sin1.u, inclineSensor.phi_rel) 
    annotation(Line(origin = {16.5, -111.5}, 
    points = {{22.5, -79.5}, {10.5, -79.5}, {10.5, 35.5}}, 
    color = {0, 0, 127}), __MWORKS(BlockSystem(NamedSignal)));
  connect(cos2.u, inclineSensor1.phi_rel) 
    annotation(Line(origin = {108.5, -93.5}, 
    points = {{25.5, -15.5}, {8.5, -15.5}, {8.5, 35.5}}, 
    color = {0, 0, 127}));
  connect(sin2.u, inclineSensor1.phi_rel) 
    annotation(Line(origin = {108.5, -111.5}, 
    points = {{16.5, -49.5}, {8.5, -49.5}, {8.5, 53.5}}, 
    color = {0, 0, 127}), __MWORKS(BlockSystem(NamedSignal)));
  connect(cos2.y, add.u1) 
    annotation(Line(origin = {153, -131}, 
    points = {{4, 22}, {15, 22}, {15, -1}, {24, -1}}, 
    color = {0, 0, 127}));
  connect(cos1.y, add.u2) 
    annotation(Line(origin = {108, -137}, 
    points = {{-46, -7}, {69, -7}}, 
    color = {0, 0, 127}));
  connect(sin2.y, add1.u1) 
    annotation(Line(origin = {153, -170}, 
    points = {{-5, 9}, {5, 9}, {5, -9}, {10, -9}}, 
    color = {0, 0, 127}));
  connect(sin1.y, add1.u2) 
    annotation(Line(origin = {108, -176}, 
    points = {{-46, -15}, {55, -15}}, 
    color = {0, 0, 127}));
  connect(const.y, add2.u2) 
    annotation(Line(origin = {84, -225}, 
    points = {{-5, 0}, {41, 0}}, 
    color = {0, 0, 127}));
  connect(add1.y, division.u2) 
    annotation(Line(origin = {202, -188}, 
    points = {{-16, 3}, {21.5, 3}}, 
    color = {0, 0, 127}));
  connect(const1.y, division.u1) 
    annotation(Line(origin = {212, -170}, 
    points = {{-1, 9}, {6, 9}, {6, -3}, {11.5, -3}}, 
    color = {0, 0, 127}));
  connect(add2.y, Fy.u2) 
    annotation(Line(origin = {204, -208}, 
    points = {{-56, -11}, {49, -11}, {49, 17}, {55, 17}}, 
    color = {0, 0, 127}));
  connect(division.y, Fy.u1) 
    annotation(Line(origin = {251, -182}, 
    points = {{-4.5, 3}, {8, 3}}, 
    color = {0, 0, 127}));
  connect(loadSensor.Fx, Fx.u1) 
    annotation(Line(origin = {142.5, -50.5}, 
    points = {{-64.5, -24.5}, {116.5, -24.5}}, 
    color = {0, 0, 127}));
  connect(loadSensor.Fy, add2.u1) 
    annotation(Line(origin = {94.5, -99.5}, 
    points = {{-16.5, 20.5}, {-3.5, 20.5}, {-3.5, -113.5}, {30.5, -113.5}}, 
    color = {0, 0, 127}));
  connect(const2.y, division1.u1) 
    annotation(Line(origin = {212, -128}, 
    points = {{-12, 25}, {17, 25}}, 
    color = {0, 0, 127}));
  connect(add.y, division1.u2) 
    annotation(Line(origin = {203, -143}, 
    points = {{-3, 5}, {19, 5}, {19, 28}, {26, 28}}, 
    color = {0, 0, 127}));
  connect(division1.y, Fx.u2) 
    annotation(Line(origin={251,-134}, 
points={{1,25},{3,25},{3,47},{8,47}}, 
color={0,0,127}));
  connect(web_spring3.webPort_b, webSink.webPort_b) 
    annotation(Line(origin = {221, 9}, 
    points = {{-10, 0}, {10, 0}}, 
    color = {96, 96, 96}, 
    thickness = 0.5));
  annotation(Diagram(coordinateSystem(extent = {{-300, -320}, {430, 120}}, 
    grid = {2, 2}), graphics = {Rectangle(origin = {65, -100}, 
    fillColor = {255, 255, 255}, 
    pattern = LinePattern.None, 
    extent = {{-365, 220}, {365, -220}})}), experiment(Algorithm = Dassl, InlineIntegrator = false, InlineStepSize = false, Interval = 0.001, StartTime = 0, StopTime = 10, Tolerance = 0.0001), __MWORKS(ContinueSimConfig(SaveContinueFile = "false", SaveBeforeStop = "false", NumberBeforeStop = 1, FixedContinueInterval = "false", ContinueIntervalLength = 2, ContinueTimeVector),ResultViewerManager(resultViewers={
ResultViewer(name="1", executeTrigger=executeTrigger.SimulationFinished, commands={
CreatePlot(id=3, x_display_unit="s", legend_layout=7, left_title_type=2, bottom_title_type=2, right_title_type=2, fix_time_range_value=0, zoom_x=(0, 10), zoom_y_l=(-50, 300)), 
Plot(y=["web_spring1.Ft_b", "Fx.y"], colors=["4278190335", "4294901760"]), 
CreatePlot(id=-1, x_display_unit="s", legend_layout=1, fix_time_range_value=0, sub_plot=(2, 1), zoom_x=(0, 10), zoom_y_l=(-50, 300)), 
Plot(y=["web_spring2.Ft_b", "Fy.y"], colors=["4278190335", "4294901760"])})
})), 
    Documentation(link = "modelica://TYWebHandling/Resources/html/Examples/LoadCell.html"), Icon(coordinateSystem(extent = {{-100, -100}, {100, 100}}, 
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
    thickness = 5)}));
end LoadCell;