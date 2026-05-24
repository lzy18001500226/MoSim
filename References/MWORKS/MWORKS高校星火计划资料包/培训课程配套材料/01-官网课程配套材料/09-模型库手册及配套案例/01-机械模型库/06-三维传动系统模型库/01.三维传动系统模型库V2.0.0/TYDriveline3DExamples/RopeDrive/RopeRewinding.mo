model RopeRewinding "绳索收卷系统"
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
    thickness = 5)}), experiment(Algorithm = Dassl, Interval = 0.001, StartTime = 0, StopTime = 4, Tolerance = 0.0001, InlineIntegrator = false, InlineStepSize = false), 
    Documentation(link = "modelica://TYDriveline3D/Resources/html/Example/RopeDrive/RopeRewinding.html"), Protection(access = Access.nonPackageDuplicate), __MWORKS(ContinueSimConfig(SaveContinueFile = "false", SaveBeforeStop = "false", NumberBeforeStop = 1, FixedContinueInterval = "false", ContinueIntervalLength = 0.5, ContinueTimeVector),ResultViewerManager(resultViewers={
ResultViewer(name="1", executeTrigger=executeTrigger.SimulationFinished, commands={
CreatePlot(id=1, x_display_unit="s", legend_layout=1, left_title="[m]", fix_time_range_value=0, zoom_x=(0, 4), zoom_y_l=(-2.5, 1)), 
Plot(y=["body.frame_a.r_0[1]", "body.frame_a.r_0[2]", "body.frame_a.r_0[3]"], colors=["4278190335", "4294901760", "4278222848"]), 
CreatePlot(id=-1, x_display_unit="s", legend_layout=1, left_title="[rad/s]", fix_time_range_value=0, sub_plot=(2, 1), zoom_x=(0, 4), zoom_y_l=(-1.2, 0.2)), 
Plot(y=["winch_Inertia.om"], colors=["4278190335"])})
})));
  inner Modelica.Mechanics.MultiBody.World world(gravityType = Modelica.Mechanics.MultiBody.Types.GravityTypes.UniformGravity) 
    annotation(Placement(transformation(origin = {-54.947921356285605, 49.3523115998621}, 
    extent = {{-10, -10}, {10, 10}})));
  Modelica.Mechanics.MultiBody.Parts.Body body(r_0(fixed = true, start = {-0.80, -2, 0.5}), 
    v_0(fixed 
    = false, start = {0, 0, 0}), 
    angles_fixed = true, 
    a_0(start = {0, 0.0, 0}), 
    m = 1, 
    w_0_fixed = true, r_CM = {0, 0, 0}) 

    annotation(Placement(transformation(origin = {84.64056265199171, 17.29855454667831}, 
    extent = {{-10, -10}, {10, 10}})));
  TYDriveline3D.RopeDrive3D.FixedPreset fixed 
    annotation(Placement(transformation(origin = {-65.92202278531072, -1.6918360056497086}, 
    extent = {{-10, -10}, {10, 10}})));
  TYDriveline3D.RopeDrive3D.Winch_Inertia winch_Inertia(coilRot = -1, phi0_b = 2.35619449019234, showTension = true, m0 = 1) 
    annotation(Placement(transformation(origin = {-24.045197785310705, 16.45197699435029}, 
    extent = {{-10, -10}, {10, 10}})));
  Modelica.Mechanics.Rotational.Sources.Speed speed 
    annotation(Placement(transformation(origin = {-25.943502418079078, -35.11864358757061}, 
    extent = {{-10, -10}, {10, 10}})));
  TYDriveline3D.RopeDrive3D.RopesSMS ropesSMS(noM = 3) 
    annotation(Placement(transformation(origin = {46.50847439548025, 17.08474545197741}, 
    extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Sources.Ramp ramp(height = -1, duration = 2) 
    annotation(Placement(transformation(origin = {-62.327684, -35.118643638418085}, 
    extent = {{-10, -10}, {10, 10}})));
equation

  connect(fixed.frame_b, winch_Inertia.frame_h) 
    annotation(Line(origin = {-42.12429378531071, 2.740112994350291}, 
    points = {{-13.797729000000004, -4.4319489999999995}, {13.479096000000013, -4.4319489999999995}, {13.479096000000013, 3.7469403639739554}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(speed.flange, winch_Inertia.flange_b) 
    annotation(Line(origin = {4.875706214689288, -6.259887005649709}, 
    points = {{-20.819208632768365, -28.8587565819209}, {2.0847457627118544, -28.8587565819209}, {2.0847457627118544, 12.746940363973955}, {-23.11350937856737, 12.746940363973955}}, 
    color = {0, 0, 0}));
  connect(winch_Inertia.frame_b, ropesSMS.frame_a) 
    annotation(Line(origin = {10.875706214689288, 17.74011299435029}, 
    points = {{-24.920903999999993, -1.2881360000000015}, {25.63276818079096, -1.2881360000000015}, {25.63276818079096, -0.6553675423728826}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(winch_Inertia.RopePort_b, ropesSMS.RopePort_a) 
    annotation(Line(origin = {10.875706214689288, 24.74011299435029}, 
    points = {{-24.920903999999993, -1.2881360000000015}, {25.63276818079096, -1.2881360000000015}, {25.63276818079096, -0.6553675423728826}}, 
    color = {0, 0, 0}));
  connect(body.frame_a, ropesSMS.frame_b) 
    annotation(Line(origin = {64.87570621468929, 16.74011299435029}, 
    points = {{9.764856437302427, 0.55844155232802}, {-8.367231819209039, 0.55844155232802}, {-8.367231819209039, 0.34463245762711736}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(ramp.y, speed.w_ref) 
    annotation(Line(origin = {-73, -35}, 
    points = {{21.672316000000002, -0.11864363841808512}, {35.05649758192092, -0.11864363841808512}, {35.05649758192092, -0.11864358757060955}}, 
    color = {0, 0, 127}), __MWORKS(BlockSystem(NamedSignal)));
end RopeRewinding;