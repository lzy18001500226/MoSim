model SwingRope "秋千绳系统"
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
    Protection(access = Access.nonPackageDuplicate), 
    experiment(Algorithm=Dassl,StartTime=0,StopTime=10,Tolerance=1e-06,InlineIntegrator=false,InlineStepSize=false,Interval=0.001), Diagram(coordinateSystem(extent = {{-100, -100}, {100, 100}}, grid = {2, 2})), 
    Documentation(link = "modelica://TYDriveline3D/Resources/html/Example/RopeDrive/SwingRope.html"),__MWORKS(ContinueSimConfig(SaveContinueFile="false",SaveBeforeStop="false",NumberBeforeStop=1,FixedContinueInterval="false",ContinueIntervalLength=0.589,ContinueTimeVector),ResultViewerManager(resultViewers={
ResultViewer(name="1", executeTrigger=executeTrigger.SimulationFinished, commands={
CreatePlot(id=1, x_display_unit="s", legend_layout=7, left_title_type=2, left_title="[m]", bottom_title_type=2, right_title_type=2, fix_time_range_value=0, zoom_x=(0, 10), zoom_y_l=(-3, 3)), 
Plot(y=["body.frame_a.r_0[1]", "body.frame_a.r_0[2]", "body.frame_a.r_0[3]"], colors=["4278190335", "4294901760", "4278222848"]), 
CreatePlot(id=-1, x_display_unit="s", legend_layout=1, left_title="[N.m]", fix_time_range_value=0, sub_plot=(2, 1), zoom_x=(0, 10), zoom_y_l=(-4000, 6000)), 
Plot(y=["sheave.tau"], colors=["4278190335"])})
})));
  TYMultibody.Joints.Fixed fixed1(r = {0.5, -1, 1}) 
    annotation(Placement(transformation(origin = {-61.41004332591304, -2.9207329430928155}, 
    extent = {{-10, -10}, {10, 10}})));
  TYMultibody.Joints.Fixed fixed_housing2(r = {1, -0.5, 1}) 
    annotation(Placement(transformation(origin = {-30.713473405068626, -40.92073294309283}, 
    extent = {{-10, -10}, {10, 10}})));
  Modelica.Mechanics.MultiBody.Parts.Body body(
    r_0(fixed = true, start = {1.80, -2, 1.01}), 
    v_0(fixed = true), angles_fixed = true, 
    a_0(start = {0, 0.0, 0}), 
    m = 100, 
    w_0_fixed = true, r_CM = {0, 0, 0}) 
    annotation(Placement(transformation(origin = {81.00081230921708, -2.9207329430928155}, 
    extent = {{-10, -10}, {10, 10}})));
  inner Modelica.Mechanics.MultiBody.World world 
    annotation(Placement(transformation(origin = {-78, 34}, 
    extent = {{-10, -10}, {10, 10}})));
  TYDriveline3D.RopeDrive3D.Sheave sheave(
    phi0_a = 3.14159265358979, showTension = false, coilRot = 1, m = 1, r_CM = {0, 0, 0},d=200,EA=100000


    ) annotation(Placement(transformation(origin = {7.715098023502804, -2.9207329430928155}, 
    extent = {{-10, -10}, {10, 10}})));
  TYDriveline3D.RopeDrive3D.RopeSpring rope1(
    s_unstretched(start = 0.5), diameter = 0.01,d=200,EA=100000


    ) annotation(Placement(transformation(origin = {-26.84747265120511, -2.9207329430928155}, 
    extent = {{-10, -10}, {10, 10}})));
  TYDriveline3D.RopeDrive3D.RopeSpring rope2(
    usePreload = false, s_unstretched(start = 1.5), diameter = 0.01, EA = 100000,d=200


    ) annotation(Placement(transformation(origin = {42.277668698210746, -2.9856186602342945}, 
    extent = {{-10, -10}, {10, 10}})));
equation
  connect(sheave.frame_housing, fixed_housing2.frame_b) 
    annotation(Line(origin = {-8.999187690782918, -26.92073294309283}, 
    points = {{16.714285714285722, 14.000000000000014}, {16.714285714285722, -14}, {-11.714285714285708, -14}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(fixed1.frame_b, rope1.frame_a) 
    annotation(Line(origin = {-43.999187690782904, -2.9207329430928297}, 
    points = {{-7.410855635130133, 1.4210854715202004e-14}, {7.151715039577795, 1.4210854715202004e-14}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(rope1.frame_b, sheave.frame_a) 
    annotation(Line(origin = {-8.999187690782918, -2.9207329430928297}, 
    points = {{-7.848284960422191, 1.4210854715202004e-14}, {6.714285714285722, 1.4210854715202004e-14}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(sheave.frame_b, rope2.frame_a) 
    annotation(Line(origin = {25.000812309217082, -2.9207329430928297}, 
    points = {{-7.285714285714278, 1.4210854715202004e-14}, {7.276856388993664, 1.4210854715202004e-14}, {7.276856388993664, -0.06488571714146474}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(rope2.frame_b, body.frame_a) 
    annotation(Line(origin = {62.00081230921708, -2.9207329430928297}, 
    points = {{-9.723143611006336, -0.06488571714146474}, {9, -0.06488571714146474}, {9, 1.4210854715202004e-14}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(rope1.RopePort_b, sheave.RopePort_a) 
    annotation(Line(origin = {-9.56513997168129, 4.0877734685512905}, 
    points = {{-7.282332679523819, -0.008506411644106038}, {7.280237995184095, -0.008506411644106038}}, 
    color = {0, 0, 0}));
  connect(sheave.RopePort_b, rope2.RopePort_a) 
    annotation(Line(origin = {25.43486002831871, 4.0877734685512905}, 
    points = {{-7.719762004815905, -0.008506411644106038}, {6.842808669892037, -0.008506411644106038}, {6.842808669892037, -0.07339212878558499}}, 
    color = {0, 0, 0}));
end SwingRope;