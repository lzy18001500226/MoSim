model PlanetWheel "行星齿轮"
  inner Modelica.Mechanics.MultiBody.World world(animateWorld=false,animateGravity=false) annotation(Placement(transformation(origin = {-105, -30}, 
    extent = {{-10, -10}, {10, 10}})));
  TYDriveline3D.GearsDrive.PlanetaryGear planetaryGear(zp = 41, m = 0.008, zs = 19, zr = 101, xp = -0.2, width = 0.1) annotation(Placement(visible = true, transformation(origin = {49.945, -10.05}, extent = {{-10.055, -9.95}, {10.055, 9.95}}, rotation = 0)));
  Modelica.Mechanics.MultiBody.Parts.Fixed wheelSupport(animation = false, r = {0, 0, 0}) annotation(Placement(visible = true, transformation(origin = {50, 70}, extent = {{-10, -10}, {10, 10}}, rotation = -90)));
  Modelica.Mechanics.MultiBody.Joints.Revolute revolute(phi(fixed = false), useAxisFlange = true) 
    annotation(Placement(transformation(origin = {-30, -30}, 
    extent = {{-10, -10}, {10, 10}})));
  Modelica.Mechanics.MultiBody.Joints.Revolute revolute1(useAxisFlange = true) 
    annotation(Placement(transformation(origin = {-30, 40}, 
    extent = {{-10, -10}, {10, 10}})));
  Modelica.Mechanics.Rotational.Sources.Speed speed 
    annotation(Placement(transformation(origin = {-60, 75}, 
    extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Sources.RealExpression realExpression(y = 1) 
    annotation(Placement(transformation(origin = {-96, 75}, 
    extent = {{-10, -10}, {10, 10}})));
  Modelica.Mechanics.Rotational.Components.Damper damper(d = 2500) 
    annotation(Placement(transformation(origin = {-30, 5}, 
    extent = {{-10, -10}, {10, 10}})));
equation
  connect(world.frame_b, revolute.frame_a) 
    annotation(Line(origin = {-82, -30}, 
    points = {{-13, 0}, {42, 0}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(revolute.frame_b, planetaryGear.frame_sun_a) 
    annotation(Line(origin = {-5, -20}, 
    points = {{-15, -10}, {25, -10}, {25, 9.95}, {44.89, 9.95}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(world.frame_b, revolute1.frame_a) 
    annotation(Line(origin = {-82, -10}, 
    points = {{-13, -20}, {2, -20}, {2, 50}, {42, 50}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(revolute1.frame_b, planetaryGear.frame_carrier) 
    annotation(Line(origin = {-5, 2}, 
    points = {{-15, 38}, {25, 38}, {25, -6.08}, {44.89, -6.08}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(speed.w_ref, realExpression.y) 
    annotation(Line(origin = {-68, 75}, 
    points = {{-4, 0}, {-17, 0}}, 
    color = {0, 0, 127}));
  connect(damper.flange_a, revolute.support) 
    annotation(Line(origin = {-39, -6.5}, 
    points = {{-1, 11.5}, {-4, 11.5}, {-4, -2.5}, {3, -2.5}, {3, -13.5}}, 
    color = {0, 0, 0}));
  connect(damper.flange_b, revolute.axis) 
    annotation(Line(origin = {-23, -6.5}, 
    points = {{3, 11.5}, {6, 11.5}, {6, -2.5}, {-7, -2.5}, {-7, -13.5}}, 
    color = {0, 0, 0}));
  connect(speed.flange, revolute1.axis) 
    annotation(Line(origin = {-73, 65}, 
    points = {{23, 10}, {43, 10}, {43, -15}}, 
    color = {0, 0, 0}));
  connect(wheelSupport.frame_b, planetaryGear.frame_ring) 
    annotation(Line(origin = {50, 30}, 
    points = {{0, 30}, {0, -30.1}, {-0.055, -30.1}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  annotation(Documentation(link = "modelica://TYDriveline3D/Resources/html/Example/GearsDrive/PlanetWheel.html"), 
  experiment(Algorithm = Dassl, InlineIntegrator = false, InlineStepSize = false, IntegratorStep = 0.0001, 
    Interval = 0.002, StartTime = 0, StopTime = 2, Tolerance = 1e-06), __MWORKS(ContinueSimConfig(SaveContinueFile = "false", 
SaveBeforeStop = "false", NumberBeforeStop = 1, FixedContinueInterval = "false", ContinueIntervalLength = 2, ContinueTimeVector),ResultViewerManager(resultViewers={
ResultViewer(name="1", executeTrigger=executeTrigger.SimulationFinished, commands={
CreatePlot(id=3, x_display_unit="s", legend_layout=1, left_title_type=2, left_title="[rad/s]", bottom_title_type=2, right_title_type=2, fix_time_range_value=0, zoom_x=(0, 2), zoom_y_l=(-2, 8)), 
Plot(y=["revolute.w", "revolute1.w"], colors=["4278190335", "4294901760"]), 
CreatePlot(id=-1, x_display_unit="s", legend_layout=1, left_title="[N]", fix_time_range_value=0, sub_plot=(2, 1), zoom_x=(0, 2), zoom_y_l=(-150000, 150000)), 
Plot(y=["planetaryGear.spurGearContact1.contactForce[1]", "planetaryGear.spurGearContact1.contactForce[2]", "planetaryGear.spurGearContact1.contactForce[3]"], colors=["4278190335", "4294901760", "4278222848"])})
})), 
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
    thickness = 5)}),Protection(access=Access.nonPackageDuplicate));
end PlanetWheel;