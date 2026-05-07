model RopeRollOut1 "绳索卷出系统1"
  annotation(Diagram(coordinateSystem(extent = {{-100, -100}, {100, 100}}, 
    grid = {2, 2})), Icon(coordinateSystem(extent = {{-100, -100}, {100, 100}}, 
    grid = {2, 2}), graphics = {Polygon(origin = {-7.105427357601002e-15, 33}, 
    lineColor = {96, 96, 96}, 
    fillColor = {96, 96, 96}, 
    fillPattern = FillPattern.Solid, 
    points = {{-64, 1}, {0, 37}, {64, 1}, {0, -37}}), Line(origin = {0, -12}, 
    points = {{-62, 18}, {0, -18}, {62, 18}}, 
    color = {96, 96, 96}, 
    thickness = 5), Line(origin = {7.105427357601002e-15, -39.99999999999999}, 
    points = {{-62, 18}, {0, -18}, {62, 18}}, 
    color = {96, 96, 96}, 
    thickness = 5)}), experiment(Algorithm = Dassl, Interval = 0.001, StartTime = 0, StopTime = 1, Tolerance = 0.0001, InlineIntegrator = false, InlineStepSize = false), 
    Documentation(link = "modelica://TYDriveline3D/Resources/html/Example/RopeDrive/RopeRollOut1.html"), Protection(access = Access.nonPackageDuplicate), __MWORKS(ContinueSimConfig(SaveContinueFile = "false", SaveBeforeStop = "false", NumberBeforeStop = 1, FixedContinueInterval = "false", ContinueIntervalLength = 0.5, ContinueTimeVector),ResultViewerManager(resultViewers={
ResultViewer(name="1", executeTrigger=executeTrigger.SimulationFinished, commands={
CreatePlot(id=1, x_display_unit="s", legend_layout=1, left_title="[m]", fix_time_range_value=0, zoom_x=(0, 1), zoom_y_l=(-8, 2)), 
Plot(y=["body2.frame_a.r_0[1]", "body2.frame_a.r_0[2]", "body2.frame_a.r_0[3]"], colors=["4278190335", "4294901760", "4278222848"]), 
CreatePlot(id=-1, x_display_unit="s", legend_layout=1, left_title="[kg]", fix_time_range_value=0, sub_plot=(2, 1), zoom_x=(0, 1), zoom_y_l=(-6, 1)), 
Plot(y=["winch.m"], colors=["4278190335"])})
})));
  inner Modelica.Mechanics.MultiBody.World world(gravityType = Modelica.Mechanics.MultiBody.Types.GravityTypes.UniformGravity) 
    annotation(Placement(transformation(origin = {-69.04139850061023, 23.552619766271953}, 
    extent = {{-10, -10}, {10, 10}})));
  Modelica.Mechanics.MultiBody.Parts.Body body2(r_0(fixed = true, start = {-1.50, -1, 1.01}), 
    v_0(fixed 
    = true, start = {-2, 0, 0}), 
    angles_fixed = true, 
    a_0(start = {0, 0.0, 0}), 
    m = 1, 
    w_0_fixed = true, r_CM = {0, 0, 0}) 

    annotation(Placement(transformation(origin = {76.41457395142672, -12.441558447671978}, 
    extent = {{-10, -10}, {10, 10}})));
  TYDriveline3D.RopeDrive3D.RopeSpring ropeSpr(
    usePreload = false, s_unstretched(start = 1.5)) annotation(Placement(transformation(origin = {25.78010989861465, -13.0743268092539}, 
    extent = {{-10, -10}, {10, 10}})));
  TYDriveline3D.RopeDrive3D.Winch winch(
    coilRot = -1, phi0_b = 2.35619449019234) annotation(Placement(transformation(origin = {-24.671516190436193, -13.2070779056809}, 
    extent = {{-10, -10}, {10, 10}})));
  TYDriveline3D.RopeDrive3D.FixedPreset fixedPreset 
    annotation(Placement(transformation(origin = {-72.24970640112994, -29.217259734463276}, 
    extent = {{-10, -10}, {10, 10}})));
equation
  connect(ropeSpr.frame_b, body2.frame_a) 
    annotation(Line(origin = {50.58007042594345, -5.034950855196964}, 
    points = {{-14.799960527328793, -8.039375954056936}, {15.834503525483271, -8.039375954056936}, {15.834503525483271, -7.406607592475014}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(winch.frame_b, ropeSpr.frame_a) 
    annotation(Line(origin = {-0.4199295740565532, -6.034950855196964}, 
    points = {{-14.25158661637964, -7.172127050483935}, {16.200039472671204, -7.172127050483935}, {16.200039472671204, -7.039375954056936}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(winch.RopePort_b, ropeSpr.RopePort_a) 
    annotation(Line(origin = {0.5480225988700624, -5.785310734463277}, 
    points = {{-15.219538789306256, -0.4217671712176223}, {15.232087299744588, -0.4217671712176223}, {15.232087299744588, -0.28901607479062363}}, 
    color = {0, 0, 0}));
  connect(fixedPreset.frame_b, winch.frame_h) 
    annotation(Line(origin = {-45.45197740112994, -25.785310734463277}, 
    points = {{-16.797729000000004, -3.4319489999999995}, {16.18046121069375, -3.4319489999999995}, {16.18046121069375, 2.6133091927563328}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
end RopeRollOut1;