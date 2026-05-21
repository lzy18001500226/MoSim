model RopeRelease "变长度绳索释放"

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
    experiment(Algorithm = Dassl, StartTime = 0, StopTime = 3, Tolerance = 1e-06, InlineIntegrator = false, InlineStepSize = false, Interval = 0.001), 
    Protection(access = Access.nonPackageDuplicate), 
    Documentation(link = "modelica://TYDriveline3D/Resources/html/Example/RopeDrive/RopeRelease.html"), __MWORKS(ContinueSimConfig(SaveContinueFile = "false", SaveBeforeStop = "false", NumberBeforeStop = 1, FixedContinueInterval = "false", ContinueIntervalLength = 0.6, ContinueTimeVector),ResultViewerManager(resultViewers={
ResultViewer(name="1", executeTrigger=executeTrigger.SimulationFinished, commands={
CreatePlot(id=1, x_display_unit="s", legend_layout=1, left_title="[m]", fix_time_range_value=0, zoom_x=(0, 3), zoom_y_l=(-2, 3)), 
Plot(y=["ropeMass.frame_a.r_0[1]", "ropeMass.frame_a.r_0[2]", "ropeMass.frame_a.r_0[3]"], colors=["4278190335", "4294901760", "4278222848"]), 
CreatePlot(id=-1, x_display_unit="s", legend_layout=1, left_title="[m]", fix_time_range_value=0, sub_plot=(2, 1), zoom_x=(0, 3), zoom_y_l=(0.018, 0.03)), 
Plot(y=["ropesSMS.sds_first.s_unstretched"], colors=["4278190335"])})
})));


  TYDriveline3D.RopeDrive3D.RopeSpring ropeSpring(d = 50) 
    annotation(Placement(transformation(origin = {5.372881355932208, 10.192090395480225}, 
    extent = {{-10, -10}, {10, 10}})));
  TYDriveline3D.RopeDrive3D.RopeMass ropeMass(r_0(start = {1, 2, 0}, fixed = true), UseRopePort = true, rho1 = 1) 
    annotation(Placement(transformation(origin = {50.372881355932215, 10.192090395480225}, 
    extent = {{-10, -10}, {10, 10}})));

  inner Modelica.Mechanics.MultiBody.World world(gravityType = Modelica.Mechanics.MultiBody.Types.GravityTypes.UniformGravity) 
    annotation(Placement(transformation(origin = {-74, 10.192090395480221}, 
    extent = {{-10, -10}, {10, 10}})));
  TYDriveline3D.RopeDrive3D.RopesSMS ropesSMS(noM = 30) 
    annotation(Placement(transformation(origin = {5.372881355932208, -39.80790960451978}, 
    extent = {{-10, -10}, {10, 10}})));

  TYDriveline3D.RopeDrive3D.FixedPreset fixedPreset(UncLpre = -0.2, r = {0, 2, 0}, UseRopePort = true) 
    annotation(Placement(transformation(origin = {-39.627118644067785, 10.192090395480225}, 
    extent = {{-10, -10}, {10, 10}})));
  TYDriveline3D.RopeDrive3D.FixedPreset fixedPreset1(UncLpre = 0, UseRopePort = true) 
    annotation(Placement(transformation(origin = {-39.6271186440678, -39.80790960451978}, 
    extent = {{-10, -10}, {10, 10}})));
  TYDriveline3D.RopeDrive3D.FixedPreset fixedPreset2(r = {1, 0.5, 0}, UncLpre = 0.2, UseRopePort = true) 
    annotation(Placement(transformation(origin = {50.372881355932215, -39.80790960451978}, 
    extent = {{10, -10}, {-10, 10}})));
equation
  connect(ropeSpring.frame_b, ropeMass.frame_a) 
    annotation(Line(origin = {40.372881355932215, 10.192090395480225}, 
    points = {{-25.000000000000007, 0}, {10, 0}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(fixedPreset.frame_b, ropeSpring.frame_a) 
    annotation(Line(origin = {-9.627118644067785, 10.192090395480225}, 
    points = {{-20, 0}, {4.999999999999993, 0}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(fixedPreset1.frame_b, ropesSMS.frame_a) 
    annotation(Line(origin = {-9.627118644067785, -39.80790960451978}, 
    points = {{-20.000000000000014, 0}, {4.999999999999993, 0}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(fixedPreset1.RopePort_b, ropesSMS.RopePort_a) 
    annotation(Line(origin = {-9.627118644067785, -32.80790960451978}, 
    points = {{-20.000000000000014, 0}, {4.999999999999993, 0}}, 
    color = {0, 0, 0}));
  connect(ropesSMS.frame_b, fixedPreset2.frame_b) 
    annotation(Line(origin = {35.372881355932215, -39.80790960451978}, 
    points = {{-20.000000000000007, 0}, {5, 0}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(ropesSMS.RopePort_b, fixedPreset2.RopePort_b) 
    annotation(Line(origin = {35.372881355932215, -32.80790960451978}, 
    points = {{-20.000000000000007, 0}, {5, 0}}, 
    color = {0, 0, 0}));
  connect(fixedPreset.RopePort_b, ropeSpring.RopePort_a) 
    annotation(Line(origin = {-16.627118644067785, 17.192090395480225}, 
    points = {{-13, 0}, {11.999999999999993, 0}}, 
    color = {0, 0, 0}));
  connect(ropeSpring.RopePort_b, ropeMass.RopePort_a) 
    annotation(Line(origin = {27.372881355932215, 17.192090395480225}, 
    points = {{-12.000000000000007, 0}, {13, 0}}, 
    color = {0, 0, 0}));
end RopeRelease;