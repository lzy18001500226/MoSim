model SlideCrankLinkage "曲柄滑块系统"
  TYDriveline3D.Mechanisms.SlideCrankLinkage slideCrankLinkage(l1(displayUnit = "mm"), l2(displayUnit = "mm"), om1 = 4) 
    annotation(Placement(transformation(origin={12,5.1}, 
extent={{-10,-10},{10,10}})));
  inner Modelica.Mechanics.MultiBody.World world(nominalLength = 0.5, gravityType = Modelica.Mechanics.MultiBody.Types.GravityTypes.UniformGravity) 
    annotation(Placement(transformation(origin={-82,59.1}, 
extent={{-10,-10},{10,10}})));
  Modelica.Mechanics.MultiBody.Parts.BodyCylinder body(w_0_fixed = false, angles_fixed = false, length(displayUnit = "mm") = 0.1, diameter(displayUnit = "mm") = 0.02, innerDiameter(displayUnit = "mm") = 0, density(displayUnit = "kg/m3") = 7850, r = slideCrankLinkage.r1) 
    annotation(Placement(transformation(origin={-42,0}, 
extent={{10,-10},{-10,10}})));
  Modelica.Mechanics.MultiBody.Parts.BodyCylinder body1(w_0_fixed = false, angles_fixed = false, length(displayUnit = "mm") = 0.2, diameter(displayUnit = "mm") = 0.02, innerDiameter(displayUnit = "mm") = 0, density(displayUnit = "kg/m3") = 7850, r = slideCrankLinkage.r2) 
    annotation(Placement(transformation(origin={-42,39.1}, 
extent={{10,-10},{-10,10}})));
  Modelica.Mechanics.MultiBody.Parts.BodyBox bodyBox(length(displayUnit = "mm") = 0.08, width(displayUnit = "mm") = 0.02, height(displayUnit = "mm") = 0.02, r = {0.08, 0, 0}, r_shape = {-0.04, 0, 0}, density(displayUnit = "kg/m3") = 7850) 
    annotation(Placement(transformation(origin={52,0}, 
extent={{-10,-10},{10,10}})));
  Modelica.Mechanics.MultiBody.Sensors.AbsoluteAngularVelocity absoluteAngularVelocity1(resolveInFrame = Modelica.Mechanics.MultiBody.Types.ResolveInFrameA.world) 
    annotation(Placement(transformation(origin={12,-30.9}, 
extent={{-10,-10},{10,10}})));
  Modelica.Mechanics.MultiBody.Sensors.AbsoluteVelocity absoluteVelocity(resolveInFrame = Modelica.Mechanics.MultiBody.Types.ResolveInFrameA.world) 
    annotation(Placement(transformation(origin={52,25.1}, 
extent={{-10,-10},{10,10}})));
equation
  connect(body.frame_a, slideCrankLinkage.frame_a) 
    annotation(Line(origin={-20,2.1}, 
points={{-12,-2.1},{22,-2.1},{22,-2.1}}, 
color={95,95,95}, 
thickness=0.5));
  connect(body1.frame_a, slideCrankLinkage.frame_b) 
    annotation(Line(origin={0,30.1}, 
points={{-32,9},{2,9},{2,-20.5}}, 
color={95,95,95}, 
thickness=0.5));
  connect(slideCrankLinkage.frame_b1, bodyBox.frame_a) 
    annotation(Line(origin={30,2.1}, 
points={{-8,-2.1},{12,-2.1},{12,-2.1}}, 
color={95,95,95}, 
thickness=0.5));
  connect(absoluteAngularVelocity1.frame_a, slideCrankLinkage.frame_a) 
    annotation(Line(origin={2,-15.9}, 
points={{0,-15},{-18,-15},{-18,15.9},{0,15.9}}, 
color={95,95,95}, 
thickness=0.5));
  connect(absoluteVelocity.frame_a, bodyBox.frame_a) 
    annotation(Line(origin={42,12.1}, 
points={{0,13},{0,-12.1}}, 
color={95,95,95}, 
thickness=0.5));
  annotation(
  Documentation(link = "modelica://TYDriveline3D/Resources/html/Example/Mechanism/SlideCrankLinkage01.html"), 

  Diagram(coordinateSystem(extent = {{-100, -100}, {100, 100}}, 
    grid = {2, 2})), 
    experiment(Algorithm = Mebdfi, InlineIntegrator = false, InlineStepSize = false, Interval = 0.001, StartTime = 0, StopTime = 10, Tolerance = 1e-06), __MWORKS(ContinueSimConfig(SaveContinueFile = "false", SaveBeforeStop = "false", NumberBeforeStop = 1, FixedContinueInterval = "false", ContinueIntervalLength = 10, ContinueTimeVector),ResultViewerManager(resultViewers={
ResultViewer(name="结果曲线", executeTrigger=executeTrigger.SimulationFinished, commands={
CreatePlot(id=3, position=[0, 28, 713, 358], y=["absoluteAngularVelocity1.w[3]"], x_display_unit="s", y_display_units=["rad/s"], y_axis=[1], legend_layout=7, legend_frame=True, left_title_type=2, left_title="[rad/s]", bottom_title_type=2, right_title_type=2, fix_time_range_value=6.95179e-310), 
CreatePlot(id=4, position=[0, 28, 612, 358], y=["absoluteVelocity.v[1]"], x_display_unit="s", y_display_units=["m/s"], y_axis=[1], legend_layout=7, legend_frame=True, left_title_type=2, left_title="[m/s]", bottom_title_type=2, right_title_type=2, fix_time_range_value=6.95179e-310)}), 
ResultViewer(name="1", executeTrigger=executeTrigger.SimulationFinished, commands={
CreatePlot(id=1, x_display_unit="s", legend_layout=1, left_title="[rad/s]", fix_time_range_value=0, zoom_x=(0, 10), zoom_y_l=(0, 20)), 
Plot(y=["absoluteAngularVelocity1.w[3]"], colors=["4278190335"]), 
CreatePlot(id=-1, x_display_unit="s", legend_layout=1, left_title="[m/s]", fix_time_range_value=0, sub_plot=(2, 1), zoom_x=(0, 10), zoom_y_l=(-1, 2)), 
Plot(y=["absoluteVelocity.v[1]"], colors=["4278190335"])})
})), Icon(coordinateSystem(extent = {{-100, -100}, {100, 100}}, 
    grid = {2, 2}), graphics = {Polygon(origin = {0, 27}, 
    lineColor = {96, 96, 96}, 
    fillColor = {96, 96, 96}, 
    fillPattern = FillPattern.Solid, 
    points = {{-64, 1}, {0, 37}, {64, 1}, {0, -37}}), Line(origin = {7.10543e-15, -18}, 
    points = {{-62, 18}, {0, -18}, {62, 18}}, 
    color = {96, 96, 96}, 
    thickness = 5), Line(origin = {1.42109e-14, -46}, 
    points = {{-62, 18}, {0, -18}, {62, 18}}, 
    color = {96, 96, 96}, 
    thickness = 5)}),Protection(access=Access.nonPackageDuplicate));

end SlideCrankLinkage;