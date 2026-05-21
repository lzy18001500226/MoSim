model RopeRollOut2 "绳索卷出系统2"
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
    thickness = 5)}), experiment(Algorithm = Dassl, Interval = 0.001, StartTime = 0, StopTime = 3, Tolerance = 0.0001, InlineIntegrator = false, InlineStepSize = false), 
    Documentation(link = "modelica://TYDriveline3D/Resources/html/Example/RopeDrive/RopeRollOut2.html"), Protection(access = Access.nonPackageDuplicate), __MWORKS(ContinueSimConfig(SaveContinueFile = "false", SaveBeforeStop = "false", NumberBeforeStop = 1, FixedContinueInterval = "false", ContinueIntervalLength = 0.5, ContinueTimeVector),ResultViewerManager(resultViewers={
ResultViewer(name="1", executeTrigger=executeTrigger.SimulationFinished, commands={
CreatePlot(id=1, x_display_unit="s", legend_layout=1, left_title="[kg]", fix_time_range_value=0, zoom_x=(0, 3), zoom_y_l=(1.4, 2.2)), 
Plot(y=["winch.RopePort_b.m"], colors=["4278190335"]), 
CreatePlot(id=-1, x_display_unit="s", legend_layout=1, left_title="[rad/s]", fix_time_range_value=0, sub_plot=(2, 1), zoom_x=(0, 3), zoom_y_l=(-0.1, 0.6)), 
Plot(y=["winch.om"], colors=["4278190335"])})
})));
  inner Modelica.Mechanics.MultiBody.World world(gravityType = Modelica.Mechanics.MultiBody.Types.GravityTypes.NoGravity) 
    annotation(Placement(transformation(origin = {-53.85495782264412, 25.134540670226755}, 
    extent = {{-10, -10}, {10, 10}})));
  Modelica.Mechanics.MultiBody.Parts.Body body2(r_0(fixed = true, start = {1.50, 0.5, 0}), 
    v_0(fixed 
    = true, start = {0.2, 0, 0}), 
    angles_fixed = true, 
    a_0(start = {0, 0.0, 0}), 
    m = 1, 
    w_0_fixed = true, r_CM = {0, 0, 0}) 

    annotation(Placement(transformation(origin = {80.84395248250017, -10.543253362926215}, 
    extent = {{-10, -10}, {10, 10}})));
  TYDriveline3D.RopeDrive3D.RopeSpring ropeSpr(
    usePreload = false, s_unstretched(start = 1.5)) annotation(Placement(transformation(origin = {40.96655057658076, -11.492405905299098}, 
    extent = {{-10, -10}, {10, 10}})));
  TYDriveline3D.RopeDrive3D.Winch winch(coilRot = 1, phi0_b = 1.5707963267949) annotation(Placement(transformation(origin = {-9.485075512470083, -11.625157001726096}, 
    extent = {{-10, -10}, {10, 10}})));
  TYDriveline3D.RopeDrive3D.FixedPreset fixedPreset 
    annotation(Placement(transformation(origin = {-44.40789849152541, -27.951723011299435}, 
    extent = {{-10, -10}, {10, 10}})));
equation
  connect(ropeSpr.frame_b, body2.frame_a) 
    annotation(Line(origin = {65.76651110390955, -3.4530299512421614}, 
    points = {{-14.799960527328793, -8.039375954056936}, {5.0774413785906205, -8.039375954056936}, {5.0774413785906205, -7.090223411684054}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(winch.frame_b, ropeSpr.frame_a) 
    annotation(Line(origin = {14.766511103909558, -4.453029951242161}, 
    points = {{-14.25158661637964, -7.172127050483935}, {16.200039472671204, -7.172127050483935}, {16.200039472671204, -7.039375954056936}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(winch.RopePort_b, ropeSpr.RopePort_a) 
    annotation(Line(origin = {15.734463276836173, -4.203389830508474}, 
    points = {{-15.219538789306256, -0.4217671712176223}, {15.232087299744588, -0.4217671712176223}, {15.232087299744588, -0.28901607479062363}}, 
    color = {0, 0, 0}));
  connect(fixedPreset.frame_b, winch.frame_h) 
    annotation(Line(origin = {-30.265536723163827, -24.203389830508474}, 
    points = {{-4.142361768361582, -3.7483331807909614}, {16.18046121069375, -3.7483331807909614}, {16.18046121069375, 2.6133091927563328}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
end RopeRollOut2;