model DriveChainSystem "上升驱动链条链轮传动系统"

  inner Modelica.Mechanics.MultiBody.World world 
    annotation(Placement(transformation(origin = {-84, 50}, 
    extent = {{-10, -10}, {10, 10}})));
  TYDriveline3D.ChainDrive.SprocketConstriant fixed1(r = {0, 0, 0}) 
    annotation(Placement(transformation(origin = {-74, -31.9352}, 
    extent = {{-10, -10}, {10, 10}}, 
    rotation = 90)));
  TYDriveline3D.ChainDrive.SprocketConstriant fixed2(r = {1, 1, 0}) 
    annotation(Placement(transformation(origin = {76, -20.0486}, 
    extent = {{-10, -10}, {10, 10}}, 
    rotation = 90)));
  Modelica.Mechanics.Rotational.Sources.Speed speed(phi(fixed = false)) 
    annotation(Placement(transformation(origin = {68, -42.0486}, 
    extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Sources.Ramp ramp(startTime = 0.2, height = -5, offset = 0) 
    annotation(Placement(transformation(origin = {34, -42.0486}, extent = {{-10, -10}, {10, 10}})));
  TYDriveline3D.ChainDrive.Sprocket sprocket(numberOfTeeth = 30, phi0_a = -0.785398163397448, Dr = 0.05, phi0_b = -3.92699081698724, d = 10, useDriveFlange = false,useRotationOutput=true) 
    annotation(Placement(transformation(origin = {-74, 16}, 
    extent = {{-10, -10}, {10, 10}})));
  TYDriveline3D.ChainDrive.Sprocket sprocket1(numberOfTeeth = 30, phi0_b = -0.785398163397448, phi0_a = 2.35619449019234, Dr = 0.05, d = 10) 
    annotation(Placement(transformation(origin = {76, 16}, 
    extent = {{-10, -10}, {10, 10}})));
  Modelica.Mechanics.Rotational.Sources.Speed position 
    annotation(Placement(transformation(origin = {-27.5, 1.9514}, 
    extent = {{-10, -10}, {10, 10}})));
  TYDriveline3D.ChainDrive.ChainForce chainForce 
    annotation(Placement(transformation(origin = {19, -70.0486}, 
    extent = {{-10, 10}, {10, -10}})));
  TYDriveline3D.ChainDrive.ChainForce chainForce1 
    annotation(Placement(transformation(origin = {19, 16}, 
    extent = {{-10, -10}, {10, 10}})));
  .TYDriveline3D.ChainDrive.LoopChainVis LoopChainVis(D1 = 0.242996 * 2, D2 = 0.242996 * 2, h = 0.08, d = 0.08, Ne = 30) 
    annotation(Placement(transformation(origin = {19, -12.0324}, 
    extent = {{-10, -10}, {10, 10}})));
equation
  connect(ramp.y, speed.w_ref) 
    annotation(Line(origin = {-28, -38.0648}, 
    points = {{73, -3.9838}, {84, -3.9838}}, 
    color = {0, 0, 127}));
  connect(fixed1.frame_b, sprocket.frame_c) 
    annotation(Line(origin = {-57.5, 1.93518}, 
    points = {{-16.5, -23.87038}, {-16.5, 4.06482}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(fixed2.frame_b, sprocket1.frame_c) 
    annotation(Line(origin = {92.5, 1.93518}, 
    points = {{-16.5, -11.98378}, {-16.5, 4.06482}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(sprocket1.flange_a, speed.flange) 
    annotation(Line(origin = {84.5, -11.0648}, 
    points = {{-1.1, 17.06482}, {5.5, 17.06482}, {5.5, -30.98378}, {-6.5, -30.98378}}, 
    color = {96, 96, 96}));
  connect(chainForce.frame_a, sprocket.frame_a) 
    annotation(Line(origin = {-63, -27.0486}, 
    points = {{72, -43}, {-27, -43}, {-27, 43.0486}, {-21, 43.0486}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(sprocket.chainPort_a, chainForce.chainPort_a) 
    annotation(Line(origin = {-62, -21.0486}, 
    points = {{-22, 43.0486}, {-36, 43.0486}, {-36, -55}, {71, -55}}, 
    color = {0, 0, 0}));
  connect(chainForce.frame_b, sprocket1.frame_b) 
    annotation(Line(origin = {57, -27.0486}, 
    points = {{-28, -43}, {37, -43}, {37, 43.0486}, {29, 43.0486}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(sprocket1.chainPort_b, chainForce.chainPort_b) 
    annotation(Line(origin = {50, -21.0486}, 
    points = {{36, 43.0486}, {50, 43.0486}, {50, -55}, {-21, -55}}, 
    color = {0, 0, 0}));
  connect(chainForce1.frame_a, sprocket.frame_b) 
    annotation(Line(origin = {-39, 33.9514}, 
    points = {{48, -17.9514}, {-25, -17.9514}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(chainForce1.chainPort_a, sprocket.chainPort_b) 
    annotation(Line(origin = {-39, 39.9514}, 
    points = {{48, -17.9514}, {-25, -17.9514}}, 
    color = {0, 0, 0}));
  connect(chainForce1.frame_b, sprocket1.frame_a) 
    annotation(Line(origin = {54, 33.9514}, 
    points = {{-25, -17.9514}, {12, -17.9514}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(chainForce1.chainPort_b, sprocket1.chainPort_a) 
    annotation(Line(origin = {54, 39.9514}, 
    points = {{-25, -17.9514}, {12, -17.9514}}, 
    color = {0, 0, 0}));
  connect(LoopChainVis.frame_b, sprocket1.frame_c) 
    annotation(Line(origin = {71, -7.0486}, 
    points = {{-42, -4.9838}, {-21, -4.9838}, {-21, 13.0486}, {5, 13.0486}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(LoopChainVis.frame_a, fixed1.frame_b) 
    annotation(Line(origin = {-32, -11.0486}, 
    points = {{41, -0.9838}, {-42, -0.9838}, {-42, -10.8866}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(sprocket.y_out[2], position.w_ref) 
    annotation(Line(origin = {-42, 5.9514}, 
    points = {{-22, 4.0486}, {-2, 4.0486}, {-2, -4}, {2.5, -4}}, 
    color = {0, 0, 127}));
  connect(position.flange, LoopChainVis.flange_a) 
    annotation(Line(origin = {-4, -1.0486}, 
    points = {{-13.5, 3}, {6, 3}, {6, -3.9838}, {13, -3.9838}}, 
    color = {0, 0, 0}));

  annotation(Diagram(coordinateSystem(extent = {{-100, -100}, {100, 100}}, 
    grid = {2, 2}), graphics = {Line(origin = {-1, -12}, 
    points = {{-115, 84}, {-115, -84}, {115, -82}, {115, 84}, {-115, 84}}, 
    color = {255, 255, 255})}), experiment(Algorithm=Dassl,InlineIntegrator=false,InlineStepSize=false,Interval=0.001,StartTime=0,StopTime=10,Tolerance=1e-06), __MWORKS(ContinueSimConfig(SaveContinueFile="false",SaveBeforeStop="false",NumberBeforeStop=1,FixedContinueInterval="false",ContinueIntervalLength=2.5,ContinueTimeVector),ResultViewerManager(resultViewers={
ResultViewer(name="链轮输出输出转速对比", executeTrigger=executeTrigger.SimulationStarted, commands={
CreatePlot(id=1, position=[0, 28, 1437, 742], y=["sprocket.om", "sprocket1.om"], x_display_unit="s", y_display_units=["rad/s", "rad/s"], y_axis=[1, 1], legend_layout=7, legend_frame=True, left_title="[rad/s]", fix_time_range_value=6.95309e-310)})
})), Icon(coordinateSystem(extent = {{-100, -100}, {100, 100}}, 
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
    thickness = 5)}), 
    Documentation(link = "modelica://TYDriveline3D/Resources/html/Example/ChainDrive/DriveChainSystem.html"),Protection(access=Access.nonPackageDuplicate));

end DriveChainSystem;