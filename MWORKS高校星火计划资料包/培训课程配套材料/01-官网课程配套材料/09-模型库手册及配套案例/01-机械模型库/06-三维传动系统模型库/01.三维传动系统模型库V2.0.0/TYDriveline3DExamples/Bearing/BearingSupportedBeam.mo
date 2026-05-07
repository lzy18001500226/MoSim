model BearingSupportedBeam "滚子轴承支撑简支梁"
  inner Modelica.Mechanics.MultiBody.World world( enableAnimation = true, animateWorld = true, defaultN_to_m = 10000, defaultNm_to_m = 10000, nominalLength = 0.1,gravityType=Modelica.Mechanics.MultiBody.Types.GravityTypes.NoGravity) annotation(Placement(transformation(origin = {-170, 0}, 
    extent = {{-10, -10}, {10, 10}})));
  TYDriveline3D.Bearing.RollerBearings.KOYO_N_209 bearingRight(axialPosition = 0.1 + bearingLeft.B, horisontalPosition = 0, verticalPosition = 0, 
    cylindricalRollers.rollerPart.forceRoller.color = {0, 0, 255}) 
    annotation(Placement(transformation(origin = {90, 0}, 
    extent = {{-20, -20}, {20, 20}})));
  TYDriveline3D.Bearing.RollerBearings.KOYO_N_209 bearingLeft(axialPosition = 0, horisontalPosition = 0, verticalPosition = 0,  animateOuterRing = true) 
    annotation(Placement(transformation(origin = {-80, 0}, 
    extent = {{-20, -20}, {20, 20}})));
  Modelica.Mechanics.MultiBody.Parts.BodyCylinder bodyCylinder(r = {0, 0, 0.069}, lengthDirection = {0, 0, 1}, diameter = 0.045) 
    annotation(Placement(transformation(origin = {-30, 0}, 
    extent = {{-10, -10}, {10, 10}})));
  Modelica.Mechanics.MultiBody.Parts.BodyCylinder bodyCylinder1(r = {0, 0, 0.05}, lengthDirection = {0, 0, 1}, diameter = 0.045) 
    annotation(Placement(transformation(origin = {30, 0}, 
    extent = {{-10, -10}, {10, 10}})));
  Modelica.Mechanics.MultiBody.Joints.Revolute revolute(useAxisFlange = true, animation = false) 
    annotation(Placement(transformation(origin = {-130, 0}, 
    extent = {{-10, -10}, {10, 10}})));
  Modelica.Mechanics.Rotational.Sources.Speed speed 
    annotation(Placement(transformation(origin = {-145, 50}, 
    extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Sources.RealExpression realExpression(y = 2) 
    annotation(Placement(transformation(origin = {-185, 50}, 
    extent = {{-10, -10}, {10, 10}})));
  TYDriveline3D.Utilities.ShaftInitiated shaftInitiated 
    annotation(Placement(transformation(origin = {-145, -50}, 
    extent = {{-10, -10}, {10, 10}})));
  Modelica.Mechanics.MultiBody.Forces.WorldForce force_Static(color = {255, 0, 0}) annotation(Placement(transformation(origin = {-8, 66}, 
    extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Sources.Ramp rampy(height = -1000, duration = 2, startTime = 1) annotation(Placement(transformation(origin = {-52, 66}, 
    extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Sources.RealExpression realExpression1(y = 0) 
    annotation(Placement(transformation(origin = {-52, 96}, 
    extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Sources.RealExpression realExpression2(y = 0) 
    annotation(Placement(transformation(origin = {-52, 36}, 
    extent = {{-10, -10}, {10, 10}})));
equation
  connect(bodyCylinder.frame_b, bodyCylinder1.frame_a) 
    annotation(Line(origin = {0, 0}, 
    points = {{-20, 0}, {20, 0}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(bearingLeft.frame_a, revolute.frame_b) 
    annotation(Line(origin = {-110, 0}, 
    points = {{10, 0}, {-10, 0}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(speed.w_ref, realExpression.y) 
    annotation(Line(origin = {-165, 50}, 
    points = {{8, 0}, {-9, 0}}, 
    color = {0, 0, 127}));
  connect(speed.flange, revolute.axis) 
    annotation(Line(origin = {-132, 30}, 
    points = {{-3, 20}, {2, 20}, {2, -20}}, 
    color = {0, 0, 0}));
  connect(shaftInitiated.frame_to_Shaft, revolute.frame_a) 
    annotation(Line(origin = {-142, -20}, 
    points = {{-3, -20}, {-3, 20}, {2, 20}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(bearingLeft.frame_b, bodyCylinder.frame_a) 
    annotation(Line(origin = {-67, 0}, 
    points = {{7, 0}, {27, 0}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(bodyCylinder1.frame_b, bearingRight.frame_a) 
    annotation(Line(origin = {80, 0}, 
    points = {{-40, 0}, {0, 0}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(force_Static.frame_b, bodyCylinder.frame_b) 
    annotation(Line(origin = {-9, 25}, 
    points = {{11, 41}, {19, 41}, {19, -25}, {-11, -25}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(force_Static.force[2], rampy.y) 
    annotation(Line(origin = {-31, 72}, 
    points = {{11, -6}, {-10, -6}}, 
    color = {0, 0, 127}));
  connect(realExpression1.y, force_Static.force[1]) 
    annotation(Line(origin = {-31, 84}, 
    points = {{-10, 12}, {-3, 12}, {-3, -18}, {11, -18}}, 
    color = {0, 0, 127}));
  connect(realExpression2.y, force_Static.force[3]) 
    annotation(Line(origin = {-31, 54}, 
    points = {{-10, -18}, {-3, -18}, {-3, 12}, {11, 12}}, 
    color = {0, 0, 127}));
  annotation(Documentation(link = "modelica://TYDriveline3D/Resources/html/Example/Bearing/BearingSupportedBeam.html"), 
  experiment(Algorithm = Dassl, InlineIntegrator = false, InlineStepSize = false, IntegratorStep = 0.0001, Interval = 0.001, 
    StartTime = 0, StopTime = 10, Tolerance = 1e-06), __MWORKS(ContinueSimConfig(SaveContinueFile = "false", SaveBeforeStop = "false", 
NumberBeforeStop = 1, FixedContinueInterval = "false", ContinueIntervalLength = 10, ContinueTimeVector),ResultViewerManager(resultViewers={
ResultViewer(name="1", executeTrigger=executeTrigger.SimulationFinished, commands={
CreatePlot(id=3, x_display_unit="s", left_title_type=2, left_title="[rad/s]", bottom_title_type=2, right_title_type=2, fix_time_range_value=0, zoom_x=(0, 10), zoom_y_l=(-1200, 200)), 
Plot(y=["force_Static.force[2]"], colors=["4278190335"]), 
CreatePlot(id=-1, x_display_unit="s", legend_layout=1, left_title="[N]", fix_time_range_value=0, sub_plot=(2, 1), zoom_x=(0, 10), zoom_y_l=(160, 320)), 
Plot(y=["bearingLeft.cylindricalRollers.rollerPart.Q"], colors=["4278190335"])})
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
    thickness = 5)}), Diagram(coordinateSystem(extent = {{-100, -100}, {100, 100}}, 
    grid = {2, 2})),Protection(access=Access.nonPackageDuplicate));
end BearingSupportedBeam;