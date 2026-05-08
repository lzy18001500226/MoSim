model SimpleBeltDrive "简单绳索传动"
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
    Diagram(coordinateSystem(extent = {{-100, -100}, {100, 100}}, 
    grid = {2, 2})), 
    experiment(Algorithm = Dassl, StartTime = 0, StopTime = 10, Tolerance = 1e-06, InlineIntegrator = false, InlineStepSize = false, Interval = 0.001), 
    Protection(access = Access.nonPackageDuplicate), 
    Documentation(link = "modelica://TYDriveline3D/Resources/html/Example/RopeDrive/SimpleBeltDrive.html"), __MWORKS(ContinueSimConfig(SaveContinueFile = "false", SaveBeforeStop = "false", NumberBeforeStop = 1, FixedContinueInterval = "false", ContinueIntervalLength = 0.5, ContinueTimeVector),ResultViewerManager(resultViewers={
ResultViewer(name="1", executeTrigger=executeTrigger.SimulationFinished, commands={
CreatePlot(id=3, x_display_unit="s", legend_layout=7, left_title_type=2, left_title="[N]", bottom_title_type=2, right_title_type=2, fix_time_range_value=0, zoom_x=(0, 10), zoom_y_l=(-800, 800)), 
Plot(y=["ropeSpring1.Fi"], colors=["4278190335"]), 
CreatePlot(id=-1, x_display_unit="s", legend_layout=1, left_title="[rad/s]", fix_time_range_value=0, sub_plot=(2, 1), zoom_x=(0, 10), zoom_y_l=(-5, 25)), 
Plot(y=["sheave1.om", "sheave2.om"], colors=["4278190335", "4294901760"])})
})));
  inner Modelica.Mechanics.MultiBody.World world 
    annotation(Placement(transformation(origin = {-144.2276957556329, 35.399582034810834}, 
    extent = {{-10, -10}, {10, 10}})));
  TYDriveline3D.RopeDrive3D.Sheave sheave1(
    phi0_a = 4.71238898038469, 
    coilRot = 1, 
    phi0_b = 1.5707963267949, 
    R = 0.2, 
    I_33 = 0.1, 
    rhol = 0.1, 
    d = 100000, EA = 10000000, r_CM = {0, 0, 0}, m = 1) annotation(Placement(transformation(origin = {-75.22769575563291, 35.4644677519523}, 
    extent = {{-10, -10}, {10, 10}})));
  TYDriveline3D.RopeDrive3D.Sheave sheave2(
    phi0_a = 1.5707963267949, 
    coilRot = 1, 
    phi0_b = -1.5707963267949, 
    R = 0.2, 
    rhol = 0.1, d = 100000, EA = 1000000, r_CM = {0, 0, 0}, m = 1) annotation(Placement(transformation(origin = {62.77230424436709, 35.46446775195233}, 
    extent = {{-10, -10}, {10, 10}})));
  TYDriveline3D.RopeDrive3D.FixedPreset fixed1(r = {-0.5, 1, 0}) 
    annotation(Placement(transformation(origin = {-79.82769575563293, 7.464467751952299}, 
    extent = {{-10, -10}, {10, 10}}, 
    rotation = 90)));
  TYDriveline3D.RopeDrive3D.FixedPreset fixed2(r = {0.5, 1, 0}) 
    annotation(Placement(transformation(origin = {58.1723042443671, 7.464467751952299}, 
    extent = {{-10, -10}, {10, 10}}, 
    rotation = 90)));
  TYDriveline3D.RopeDrive3D.RopeSpring ropeSpring1(usePreload = false, 
    s_unstretched(fixed 
    = false, start 
    = 0.5), 
    F0 = 0, 
    d = 50, 
    rhol = 0.1) 
    annotation(Placement(transformation(origin = {-39.22769575563291, 35.46446775195233}, 
    extent = {{-10, -10}, {10, 10}})));
  TYDriveline3D.RopeDrive3D.RopeSpring ropeSpring2(usePreload = false, 
    s_unstretched(fixed 
    = false, 
    start 

    = 0.5), 
    F0 = 0, 
    d = 50, 
    rhol = 0.1) 
    annotation(Placement(transformation(origin = {-75.22769575563291, -36.600417965189166}, 
    extent = {{10, -10}, {-10, 10}}, 
    rotation = 180)));
  TYDriveline3D.RopeDrive3D.RopeSpring ropeSpring3(usePreload = false, 
    s_unstretched(fixed 
    = true, 
    start 
    = 0.5), 
    F0 = 0, 
    d = 50, 
    rhol = 0.1) 
    annotation(Placement(transformation(origin = {62.77230424436709, -36.600417965189166}, 
    extent = {{10, -10}, {-10, 10}}, 
    rotation = 180)));
  TYDriveline3D.RopeDrive3D.RopeSpring ropeSpring4(usePreload = false, 
    s_unstretched(fixed 
    = false, 
    start 
    = 0.5), 
    F0 = 0, 
    d = 50, 
    rhol = 0.1) annotation(Placement(transformation(origin = {22.772304244367106, 35.46446775195233}, 
    extent = {{-10, -10}, {10, 10}})));
  TYDriveline3D.RopeDrive3D.RopeMass ropeMass(r_0(start = {0, 0.8, 0}, fixed = true), v_0(fixed = true), 
    p_a = 1.0, p_b = 1.0, 
    m(start 
    = 0.1)) 
    annotation(Placement(transformation(origin = {-6.227695755632908, -36.600417965189166}, 
    extent = {{-10, 10}, {10, -10}})));
  Modelica.Mechanics.Rotational.Sources.Speed speed(phi(fixed = false)) 
    annotation(Placement(transformation(origin = {22.772304244367106, -8.600417965189166}, 
    extent = {{-10, -10}, {10, 10}})));
  TYDriveline3D.RopeDrive3D.RopeMass ropeMass1(r_0(start = {0, 1.2, 0}, fixed = true), v_0(fixed = true), 
    p_a = 1.0, p_b = 1.0, 
    m(start 
    = 0.1)) 
    annotation(Placement(transformation(origin = {-8.227695755632908, 35.46446775195233}, 
    extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Sources.RealExpression realExpression(y = 10) 
    annotation(Placement(transformation(origin = {-16.4773267556329, -7.873681965189164}, 
    extent = {{-10, -10}, {10, 10}})));
equation
  connect(fixed1.frame_b, sheave1.frame_housing) 
    annotation(Line(origin = {-82.22769575563291, 20.4644677519523}, 
    points = {{2.3999999999999773, -3}, {2.3999999999999773, 5}, {7, 5}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(fixed2.frame_b, sheave2.frame_housing) 
    annotation(Line(origin = {51.77230424436709, 15.464467751952299}, 
    points = {{6.400000000000006, 2}, {6.400000000000006, 10.000000000000028}, {11, 10.000000000000028}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(ropeSpring1.frame_a, sheave1.frame_b) 
    annotation(Line(origin = {-40.22769575563291, 35.4644677519523}, 
    points = {{-9, 2.842170943040401e-14}, {-25, 2.842170943040401e-14}, {-25, 0}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(ropeSpring2.frame_a, sheave1.frame_a) 
    annotation(Line(origin = {-82.22769575563291, -20.5355322480477}, 
    points = {{-3, -16.064885717141465}, {-20, -16.064885717141465}, {-20, 56}, {-3, 56}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(ropeSpring3.frame_b, sheave2.frame_b) 
    annotation(Line(origin = {36.77230424436709, -42.600417965189166}, 
    points = {{36, 6}, {54, 6}, {54, 78.0648857171415}, {36, 78.0648857171415}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(ropeSpring4.frame_b, sheave2.frame_a) 
    annotation(Line(origin = {42.77230424436709, 35.399582034810834}, 
    points = {{-9.999999999999986, 0.06488571714149316}, {10, 0.06488571714149316}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(ropeSpring2.frame_b, ropeMass.frame_a) 
    annotation(Line(origin = {-35.22769575563291, -36.600417965189166}, 
    points = {{-30, 0}, {29, 0}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(ropeSpring3.frame_a, ropeSpring2.frame_b) 
    annotation(Line(origin = {-6.227695755632908, -36.600417965189166}, 
    points = {{59, 0}, {-59, 0}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(speed.flange, sheave2.flange_a) 
    annotation(Line(origin = {44.47230424436711, 3.2698106005279044}, 
    points = {{-11.700000000000003, -11.87022856571707}, {36, -11.87022856571707}, {36, 22.194657151424423}, {27.299999999999983, 22.194657151424423}}, 
    color = {0, 0, 0}));
  connect(ropeSpring4.frame_a, ropeMass1.frame_a) 
    annotation(Line(origin = {2.772304244367092, 35.399582034810834}, 
    points = {{10.000000000000014, 0.06488571714149316}, {-11, 0.06488571714149316}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(ropeMass1.frame_a, ropeSpring1.frame_b) 
    annotation(Line(origin = {-18.227695755632908, 35.399582034810834}, 
    points = {{10, 0.06488571714149316}, {-11, 0.06488571714149316}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(realExpression.y, speed.w_ref) 
    annotation(Line(origin = {2.772304244367092, -8.600417965189166}, 
    points = {{-8.249630999999994, 0.7267360000000025}, {8.000000000000014, 0.7267360000000025}, {8.000000000000014, 0}}, 
    color = {0, 0, 127}));
  connect(sheave1.RopePort_b, ropeSpring1.RopePort_a) 
    annotation(Line(origin = {-57.287017789531205, 42.137109639144285}, 
    points = {{-7.940677966101703, 0.32735811280801386}, {8.059322033898297, 0.32735811280801386}, {8.059322033898297, 0.3273581128080423}}, 
    color = {0, 0, 0}));
  connect(ropeSpring1.RopePort_b, ropeMass1.RopePort_a) 
    annotation(Line(origin = {-23.287017789531205, 42.137109639144285}, 
    points = {{-5.940677966101703, 0.3273581128080423}, {5.059322033898297, 0.3273581128080423}}, 
    color = {0, 0, 0}));
  connect(ropeMass1.RopePort_b, ropeSpring4.RopePort_a) 
    annotation(Line(origin = {7.712982210468795, 42.137109639144285}, 
    points = {{-5.940677966101703, 0.3273581128080423}, {5.059322033898312, 0.3273581128080423}}, 
    color = {0, 0, 0}));
  connect(ropeSpring4.RopePort_b, sheave2.RopePort_a) 
    annotation(Line(origin = {42.712982210468795, 42.137109639144285}, 
    points = {{-9.940677966101688, 0.3273581128080423}, {10.059322033898297, 0.3273581128080423}}, 
    color = {0, 0, 0}));
  connect(ropeSpring3.RopePort_b, sheave2.RopePort_b) 
    annotation(Line(origin = {88.7129822104688, -0.8628903608557152}, 
    points = {{-15.940677966101703, -42.73752760433345}, {16.80925536139494, -42.73752760433345}, {16.80925536139494, 43.32735811280804}, {-15.940677966101703, 43.32735811280804}}, 
    color = {0, 0, 0}));
  connect(ropeSpring2.RopePort_a, sheave1.RopePort_a) 
    annotation(Line(origin = {-101.2870177895312, -0.8628903608557152}, 
    points = {{16.059322033898297, -42.73752760433345}, {-15.833984897298933, -42.73752760433345}, {-15.833984897298933, 43.327358112808014}, {16.059322033898297, 43.327358112808014}}, 
    color = {0, 0, 0}));
  connect(ropeSpring2.RopePort_b, ropeMass.RopePort_a) 
    annotation(Line(origin = {-40.287017789531205, -43.862890360855715}, 
    points = {{-24.940677966101703, 0.2624723956665491}, {24.059322033898297, 0.2624723956665491}}, 
    color = {0, 0, 0}));
  connect(ropeMass.RopePort_b, ropeSpring3.RopePort_a) 
    annotation(Line(origin = {28.712982210468795, -43.862890360855715}, 
    points = {{-24.940677966101703, 0.2624723956665491}, {24.059322033898297, 0.2624723956665491}}, 
    color = {0, 0, 0}));
end SimpleBeltDrive;