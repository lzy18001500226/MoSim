model RopeDriveWithTensioner "带张力控制的绳索传动系统"
  inner Modelica.Mechanics.MultiBody.World world(animateWorld = false, animateGravity = false) 
    annotation(Placement(transformation(origin = {-139.0, 80.0}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  annotation(Icon(coordinateSystem(extent = {{-100, -100}, {100, 100}}, 
    grid = {2, 2}), graphics = {Polygon(origin = {-4.429378531073451, 20.672316384180785}, 
    lineColor = {96, 96, 96}, 
    fillColor = {96, 96, 96}, 
    fillPattern = FillPattern.Solid, 
    points = {{-64, 1}, {0, 37}, {64, 1}, {0, -37}}), Line(origin = {-4.429378531073444, -24.327683615819215}, 
    points = {{-62, 18}, {0, -18}, {62, 18}}, 
    color = {96, 96, 96}, 
    thickness = 5), Line(origin = {-4.429378531073437, -52.32768361581921}, 
    points = {{-62, 18}, {0, -18}, {62, 18}}, 
    color = {96, 96, 96}, 
    thickness = 5)}), 
    Diagram(coordinateSystem(extent = {{-200.0, -200.0}, {200.0, 200.0}}, grid = {2.0, 2.0})), 
    Documentation(link = "modelica://TYDriveline3D/Resources/html/Example/RopeDrive/RopeDriveWithTensioner.html"), 
    experiment(Algorithm = Dassl, Interval = 0.001, StartTime = 0, StopTime = 10, Tolerance = 0.0001, InlineIntegrator = false, InlineStepSize = false), Protection(access = Access.nonPackageDuplicate), __MWORKS(ContinueSimConfig(SaveContinueFile = "false", SaveBeforeStop = "false", NumberBeforeStop = 1, FixedContinueInterval = "false", ContinueIntervalLength = 0.5, ContinueTimeVector),ResultViewerManager(resultViewers={
ResultViewer(name="1", executeTrigger=executeTrigger.SimulationFinished, commands={
CreatePlot(id=1, x_display_unit="s", legend_layout=1, left_title="[N]", fix_time_range_value=0, zoom_x=(0, 10), zoom_y_l=(-25000, 5000)), 
Plot(y=["ropeSpring1.Fi"], colors=["4278190335"]), 
CreatePlot(id=-1, x_display_unit="s", legend_layout=1, left_title="[rad/s]", fix_time_range_value=0, sub_plot=(2, 1), zoom_x=(0, 10), zoom_y_l=(-50, 30)), 
Plot(y=["sheave1.om", "sheave2.om", "sheave.om"], colors=["4278190335", "4294901760", "4278222848"])})
})));

  TYDriveline3D.RopeDrive3D.Sheave sheave1(
    phi0_a = 4.87927736346039, 
    coilRot = 1, 
    phi0_b = 1.5707963267949, 
    R = 0.2, 
    I_33 = 0.1, 
    rhol = 0.1, 
    d = 1000, r_CM = {0, 0, 0}, m = 1) annotation(Placement(transformation(origin = {-70.0, 80.06488571714146}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYDriveline3D.RopeDrive3D.Sheave sheave2(phi0_a = 1.5707963267949, 
    coilRot = 1, 
    phi0_b = -1.73768470987059, 
    R = 0.2, 
    rhol = 0.1, 
    d = 1000, 
    I_33 = 0.1, r_CM = {0, 0, 0}, m = 1) annotation(Placement(transformation(origin = {68.0, 80.06488571714148}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));


  TYDriveline3D.RopeDrive3D.FixedPreset fixed1(r = {-0.5, 0, 0}) 
    annotation(Placement(transformation(origin = {-70, 52.06488571714147}, 
    extent = {{-10, -10}, {10, 10}}, 
    rotation = 90)));
  TYDriveline3D.RopeDrive3D.FixedPreset fixed2(r = {0.5, 0, 0}) 
    annotation(Placement(transformation(origin = {68, 52.06488571714147}, 
    extent = {{-10, -10}, {10, 10}}, 
    rotation = 90)));
  Modelica.Mechanics.Rotational.Sources.Speed speed(phi(fixed = false), 
    exact = false) 
    annotation(Placement(transformation(origin = {63.400000000000006, 35.99999999999999}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  Modelica.Blocks.Sources.Ramp ramp(startTime = 0.1, 
    height = -10, 
    duration = 1.9) 
    annotation(Placement(transformation(origin = {28.00000000000002, 35.99999999999999}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYDriveline3D.RopeDrive3D.FixedPreset fixed3(r = {0, -0.1, 0}, animation = false) 
    annotation(Placement(transformation(origin = {-10.45268687528911, -62.683555551283526}, 
    extent = {{-10, -10}, {10, 10}}, 
    rotation = 90)));
  TYDriveline3D.RopeDrive3D.Sheave sheave(
    R = 0.1, rhol = 0.1, d = 1000, phi0_b = 1.4039079437192, phi0_a = 1.73768470987059, r_CM = {0, 0, 0}, m = 1) annotation(Placement(transformation(origin = {-10.0, -8.064885717141486}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  Modelica.Mechanics.MultiBody.Joints.Prismatic prismatic(useAxisFlange = true, s(fixed = true, 
    start 
    = -0.2), 
    n = {0, 1, 0}, animation = false) annotation(Placement(transformation(origin = {-10.452686875289118, -36.71599840985427}, 
    extent = {{-10, -10}, {10, 10}}, 
    rotation = 90)));
  TYDriveline3D.RopeDrive3D.RopeSpring ropeSpring(usePreload = false, rhol = 0.1, d = 500) 
    annotation(Placement(transformation(origin = {0.0, 80.0}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYDriveline3D.RopeDrive3D.RopeSpring ropeSpring1(usePreload = false, s_unstretched(fixed = true, start = 0.4565), d = 500, rhol = 0.1) 
    annotation(Placement(transformation(origin = {-67.3, -8.064885717141507}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYDriveline3D.RopeDrive3D.RopeSpring ropeSpring2(usePreload = false, s_unstretched(fixed = true, start = 0.4565), rhol = 0.1, d = 500) 
    annotation(Placement(transformation(origin = {47.300000000000026, -8.064885717141486}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  Modelica.Mechanics.Translational.Components.SpringDamper springDamper(c = 1e4, d = 2000) 
    annotation(Placement(transformation(origin = {-67.29999999999998, -34.03244285857076}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
    rotation = 90.0)));
equation
  connect(fixed1.frame_b, sheave1.frame_housing) 
    annotation(Line(origin = {-77, 65.06488571714146}, 
    points = {{7, -2.999999999999993}, {7, 5}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(fixed2.frame_b, sheave2.frame_housing) 
    annotation(Line(origin = {57, 60.064885717141465}, 
    points = {{11, 2.000000000000007}, {11, 10.000000000000014}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(speed.flange, sheave2.flange_a) 
    annotation(Line(origin = {49.70000000000002, 47.87022856571708}, 
    points = {{24.0, -12.0}, {36.0, -12.0}, {36.0, 22.0}, {26.0, 22.0}}, 
    color = {0, 0, 0}));
  connect(ramp.y, speed.w_ref) 
    annotation(Line(origin = {-3.0, 36.0}, 
    points = {{42.0, 0.0}, {54.0, 0.0}}, 
    color = {0, 0, 127}));
  connect(fixed3.frame_b, prismatic.frame_a) 
    annotation(Line(origin = {-10.852686875289109, -49.68355555128352}, 
    points = {{0.3999999999999986, -3.000000000000007}, {0.3999999999999986, 2.9675571414292463}, {0.3999999999999915, 2.9675571414292463}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(prismatic.frame_b, sheave.frame_housing) 
    annotation(Line(origin = {-15, -21}, 
    points = {{4.5473131247108824, -5.715998409854272}, {4.5473131247108824, 2.935114282858514}, {5, 2.935114282858514}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(ropeSpring.frame_a, sheave1.frame_b) 
    annotation(Line(origin = {-35.0, 80.0}, 
    points = {{25.0, 0.0}, {-25.0, 0.0}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(ropeSpring.frame_b, sheave2.frame_a) 
    annotation(Line(origin = {34.0, 80.0}, 
    points = {{-24.0, 0.0}, {24.0, 0.0}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(ropeSpring1.frame_b, sheave.frame_a) 
    annotation(Line(origin = {-38.0, -8.0}, 
    points = {{-19.0, 0.0}, {18.0, 0.0}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(sheave.frame_b, ropeSpring2.frame_a) 
    annotation(Line(origin = {19.0, -8.0}, 
    points = {{-19.0, 0.0}, {18.0, 0.0}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(ropeSpring2.frame_b, sheave2.frame_b) 
    annotation(Line(origin = {68.0, 36.0}, 
    points = {{-11.0, -44.0}, {30.0, -44.0}, {30.0, 44.0}, {10.0, 44.0}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(ropeSpring1.frame_a, sheave1.frame_a) 
    annotation(Line(origin = {-78.0, 36.0}, 
    points = {{1.0, -44.0}, {-20.0, -44.0}, {-20.0, 44.0}, {-2.0, 44.0}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(springDamper.flange_a, prismatic.support) 
    annotation(Line(origin = {-40, -40}, 
    points = {{-27.299999999999983, -4.032442858570761}, {-27.299999999999983, -10}, {-8, -10}, {-8, -0.7159984098542722}, {23.547313124710882, -0.7159984098542722}}, 
    color = {0, 127, 0}));
  connect(springDamper.flange_b, prismatic.axis) 
    annotation(Line(origin = {-40, -22}, 
    points = {{-27.299999999999983, -2.032442858570761}, {-27.299999999999983, 4}, {-8, 4}, {-8, -6.715998409854272}, {23.547313124710882, -6.715998409854272}}, 
    color = {0, 127, 0}));
  connect(sheave1.RopePort_b, ropeSpring.RopePort_a) 
    annotation(Line(origin = {-35, 87}, 
    points = {{-25, 0.06488571714146474}, {25, 0.06488571714146474}, {25, 0}}, 
    color = {0, 0, 0}));
  connect(ropeSpring.RopePort_b, sheave2.RopePort_a) 
    annotation(Line(origin = {34, 87}, 
    points = {{-24, 0}, {24, 0}, {24, 0.06488571714147895}}, 
    color = {0, 0, 0}));
  connect(sheave.RopePort_b, ropeSpring2.RopePort_a) 
    annotation(Line(origin = {19, -1}, 
    points = {{-19, -0.06488571714148605}, {18.300000000000026, -0.06488571714148605}}, 
    color = {0, 0, 0}));
  connect(ropeSpring2.RopePort_b, sheave2.RopePort_b) 
    annotation(Line(origin = {85, 43}, 
    points = {{-27.699999999999974, -44.064885717141486}, {27.46537355833655, -44.064885717141486}, {27.46537355833655, 44.06488571714148}, {-7, 44.06488571714148}}, 
    color = {0, 0, 0}));
  connect(ropeSpring1.RopePort_b, sheave.RopePort_a) 
    annotation(Line(origin = {-39, -1}, 
    points = {{-18.299999999999997, -0.06488571714150737}, {19, -0.06488571714150737}, {19, -0.06488571714148605}}, 
    color = {0, 0, 0}));
  connect(ropeSpring1.RopePort_a, sheave1.RopePort_a) 
    annotation(Line(origin = {-90, 43}, 
    points = {{12.700000000000003, -44.06488571714151}, {-12.706989735487383, -44.06488571714151}, {-12.706989735487383, 44.064885717141465}, {10, 44.064885717141465}}, 
    color = {0, 0, 0}));
end RopeDriveWithTensioner;