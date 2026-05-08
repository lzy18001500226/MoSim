model Catenary "悬链线系统"


  Modelica.Mechanics.MultiBody.Joints.Prismatic prismatic(useAxisFlange = true, animation = true) 
    annotation(Placement(transformation(origin = {6, -0.306849}, 
    extent = {{10, -10}, {-10, 10}})));
  TYDriveline3D.RopeDrive3D.FixedPreset fixed1(r = {2, 0, 0}) 
    annotation(Placement(transformation(origin = {54.50851582588584, 0}, 
    extent = {{10, -10}, {-10, 10}})));
  Modelica.Mechanics.Translational.Sources.Position position 
    annotation(Placement(transformation(origin = {19.508515825885844, 37.440675539653775}, 
    extent = {{10, -10}, {-10, 10}})));
  Modelica.Blocks.Sources.Ramp ramp(height = -1, duration = 2) 
    annotation(Placement(transformation(origin = {54.508515825885844, 37.440675539653775}, 
    extent = {{10, -10}, {-10, 10}})));
  TYDriveline3D.RopeDrive3D.FixedPreset fixedPreset(r = {0, 0, 0}) 
    annotation(Placement(transformation(origin = {-70.0, 0.0}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYDriveline3D.RopeDrive3D.RopesSMS ropesSMS(F0 = 0, EA = 1000, d = 11, noM = 10, UnloadedL0 = 1) 
    annotation(Placement(transformation(origin = {-30.678099649953687, -0.3389849571560901}, 
    extent = {{-10, -10}, {10, 10}})));
  inner Modelica.Mechanics.MultiBody.World world 
    annotation(Placement(transformation(origin = {-66.746052, 38.406946}, extent = {{-10.000000, -10.000000}, {10.000000, 10.000000}})));
equation
  connect(ramp.y, position.s_ref) 
    annotation(Line(origin = {37.508515825885844, 37.440675539653775}, 
    points = {{6, 0}, {-6, 0}}, 
    color = {0, 0, 127}));
  connect(fixed1.frame_b, prismatic.frame_a) 
    annotation(Line(origin = {26, 0}, 
    points = {{18.5085, 0}, {-10, 0}, {-10, -0.306849}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(fixedPreset.frame_b, ropesSMS.frame_a) 
    annotation(Line(origin = {-49, -1}, 
    points = {{-11, 1}, {8.321900350046313, 1}, {8.321900350046313, 0.6610150428439099}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(ropesSMS.frame_b, prismatic.frame_b) 
    annotation(Line(origin = {-11, -1}, 
    points = {{-9.6781, 0.661015}, {7, 0.661015}, {7, 0.693151}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(position.flange, prismatic.axis) 
    annotation(Line(origin = {4, 24}, 
    points = {{5.50852, 13.4407}, {-6, 13.4407}, {-6, -18.3068}}, 
    color = {96, 96, 96}));

  annotation(Icon(coordinateSystem(extent = {{-100.0, -100.0}, {100.0, 100.0}}, 
    grid = {2.0, 2.0}), graphics = {Polygon(origin = {-7.105427357601002e-15, 33.0}, 
    lineColor = {96, 96, 96}, 
    fillColor = {96, 96, 96}, 
    fillPattern = FillPattern.Solid, 
    points = {{-64.0, 1.0}, {0.0, 37.0}, {64.0, 1.0}, {0.0, -37.0}}), Line(origin = {0.0, -12.0}, 
    points = {{-62.0, 18.0}, {0.0, -18.0}, {62.0, 18.0}}, 
    color = {96, 96, 96}, 
    thickness = 5.0), Line(origin = {7.105427357601002e-15, -39.99999999999999}, 
    points = {{-62.0, 18.0}, {0.0, -18.0}, {62.0, 18.0}}, 
    color = {96, 96, 96}, 
    thickness = 5.0)}), 
    experiment(Algorithm=Dassl,StartTime=0,StopTime=5,Tolerance=1e-06,InlineIntegrator=false,InlineStepSize=false,Interval=0.001), 
    Protection(access = Access.nonPackageDuplicate), 
    Documentation(link = "modelica://TYDriveline3D/Resources/html/Example/RopeDrive/Catenary.html"),__MWORKS(ContinueSimConfig(SaveContinueFile="false",SaveBeforeStop="false",NumberBeforeStop=1,FixedContinueInterval="false",ContinueIntervalLength=0.715,ContinueTimeVector),ResultViewerManager(resultViewers={
ResultViewer(name="1", executeTrigger=executeTrigger.SimulationFinished, commands={
CreatePlot(id=1, x_display_unit="s", legend_layout=1, left_title="[m]", fix_time_range_value=0, zoom_x=(0, 5), zoom_y_l=(-1.2, 0.2)), 
Plot(y=["prismatic.s"], colors=["4278190335"]), 
CreatePlot(id=-1, x_display_unit="s", legend_layout=1, left_title="[N]", fix_time_range_value=0, sub_plot=(2, 1), zoom_x=(0, 5), zoom_y_l=(-40, 60)), 
Plot(y=["ropesSMS.sds_first.Fi", "ropesSMS.sds_last.Fi"], colors=["4278190335", "4294901760"])})
})));

end Catenary;