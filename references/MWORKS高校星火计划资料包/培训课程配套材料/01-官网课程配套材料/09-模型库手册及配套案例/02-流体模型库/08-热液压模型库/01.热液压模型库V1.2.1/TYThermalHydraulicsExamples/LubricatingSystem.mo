model LubricatingSystem "润滑系统"
  annotation (Icon(coordinateSystem(extent = {{-100.0, -100.0}, {100.0, 100.0}}, 
    grid = {2.0, 2.0}), graphics = {Polygon(origin = {-7.105427357601002e-15, 33.0}, 
    lineColor = {167, 98, 0}, 
    fillColor = {167, 98, 0}, 
    fillPattern = FillPattern.Solid, 
    points = {{-64.0, 1.0}, {0.0, 37.0}, {64.0, 1.0}, {0.0, -37.0}}), Line(origin = {0.0, -12.0}, 
    points = {{-62.0, 18.0}, {0.0, -18.0}, {62.0, 18.0}}, 
    color = {167, 98, 0}, 
    thickness = 5.0), Line(origin = {7.105427357601002e-15, -39.99999999999999}, 
    points = {{-62.0, 18.0}, {0.0, -18.0}, {62.0, 18.0}}, 
    color = {167, 98, 0}, 
    thickness = 5.0)}), 
    experiment(Algorithm = Dassl, Interval = 0.01, StartTime = 0, StopTime = 5, Tolerance = 0.0001), 
    Diagram(coordinateSystem(extent = {{-100.0, -100.0}, {100.0, 100.0}}, 
      grid = {2.0, 2.0})), 
    Documentation(link = "modelica://TYThermalHydraulics/Resources/HTML/LubricatingSystem.html"),Protection(access=Access.nonPackageDuplicate),__MWORKS(ResultViewerManager(resultViewers={
ResultViewer(name="1", executeTrigger=executeTrigger.SimulationFinished, commands={
CreatePlot(id=1, x_display_unit="s", legend_layout=7, left_title_type=2, left_title="压力/Bar
", bottom_title_type=2, bottom_title="时间/s", fix_time_range_value=0, zoom_x=(0, 5), zoom_y_l=(-0.2, 1)), 
Plot(y=["hydraulicGroovedBushing.port_B.p"], colors=["4278190335"]), 
CreatePlot(id=-1, x_display_unit="s", legend_layout=7, left_title_type=2, left_title="压力/Bar
", bottom_title_type=2, bottom_title="时间/s", fix_time_range_value=0, sub_plot=(2, 1), zoom_x=(0, 5), zoom_y_l=(-0.2, 1.2)), 
Plot(y=["centrifugalPipes_CRC.port_B.p"], colors=["4278190335"]), 
CreatePlot(id=-1, x_display_unit="s", legend_layout=7, left_title_type=2, left_title="流量/(kg/s)", bottom_title_type=2, bottom_title="时间/s", fix_time_range_value=0, sub_plot=(3, 1), zoom_x=(0, 5), zoom_y_l=(-0.0001, 0.0006)), 
Plot(y=["centrifugalPipes_CRC.port_A.m_flow", "centrifugalPipes_CRC1.port_A.m_flow"], colors=["4278190335", "4294901760"])})
})));
  TYThermalHydraulics.Sources.Tank tank(p_load = 100000, 
    redeclare model Medium = TYOilMedia.ThermalHydraulicOil.Types._5W30) 
    annotation (Placement(transformation(origin = {-76.00000000000001, -30.0}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
      rotation = -90.0)));
  TYThermalHydraulics.Pipes.Pipe_C pipe_C1(length = 0.015, d = 0.035, 
    pin(start 
       = 0), 
    redeclare model Medium = TYOilMedia.ThermalHydraulicOil.Types._5W30) 
    annotation (Placement(transformation(origin = {-27.99999999999998, -30.0}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYThermalHydraulics.Resistances.HolesandPipes.HydraulicGroovedBushing hydraulicGroovedBushing(theta = -0.785398163397448, wb = 157.07963267949, ws = 83.7758040957278, 
    redeclare model Medium = TYOilMedia.ThermalHydraulicOil.Types._5W30) 
    annotation (Placement(transformation(origin = {-55.999999999999986, -30.003541548387098}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYThermalHydraulics.Resistances.Junctions.Tjunction90deg tjunction(dm = 0.035, 
    redeclare model Medium = TYOilMedia.ThermalHydraulicOil.Types._5W30) 
    annotation (Placement(transformation(origin = {3.552713678800501e-15, -30.0035415483871}, 
      extent = {{-10.0, 10.0}, {10.0, -10.0}})));
  TYThermalHydraulics.Resistances.Junctions.AxesIntersectingHoles axesIntersectingHoles(d = 0.01, 
    redeclare model Medium = TYOilMedia.ThermalHydraulicOil.Types._5W30) 
    annotation (Placement(transformation(origin = {56.0, -29.999999999999993}, 
      extent = {{-10.0, 10.0}, {10.0, -10.0}})));
  TYThermalHydraulics.Pipes.Pipe_C pipe_C2(length = 0.015, d = 0.035, 
    redeclare model Medium = TYOilMedia.ThermalHydraulicOil.Types._5W30) 
    annotation (Placement(transformation(origin = {28.0, -30.0}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYThermalHydraulics.Valves.FlowValves.SymThrottleValve symThrottleValve(lambda_crit = 100, Cqmax = 1, diam = 0.01, 
    redeclare model Medium = TYOilMedia.ThermalHydraulicOil.Types._5W30) 
    annotation (Placement(transformation(origin = {-1.7763568394002505e-15, 33.996458451612895}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
      rotation = 90.0)));
  TYThermalHydraulics.Sources.Tank tank1(p_load = 100000, 
    redeclare model Medium = TYOilMedia.ThermalHydraulicOil.Types._5W30) 
    annotation (Placement(transformation(origin = {8.881784197001252e-15, 53.996458451612895}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
      rotation = -180.0)));
  TYThermalHydraulics.Resistances.HolesandPipes.CentrifugalPipes_CRC centrifugalPipes_CRC(rposi = 0.0175, rposo = 0.0375, w = 157.07963267949, 
    p_init = 0, 
    redeclare model Medium = TYOilMedia.ThermalHydraulicOil.Types._5W30) 
    annotation (Placement(transformation(origin = {-0.00354154838708709, 1.9964584516128951}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
      rotation = 90.0)));
  TYThermalHydraulics.Sources.Tank tank2(p_load = 100000, 
    redeclare model Medium = TYOilMedia.ThermalHydraulicOil.Types._5W30) 
    annotation (Placement(transformation(origin = {55.98298342541436, 53.996458451612895}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
      rotation = -180.0)));
  TYThermalHydraulics.Resistances.HolesandPipes.CentrifugalPipes_CRC centrifugalPipes_CRC1(rposi = 0.0175, rposo = 0.0375, w = 157.07963267949, 
    p_init = 0, 
    redeclare model Medium = TYOilMedia.ThermalHydraulicOil.Types._5W30) 
    annotation (Placement(transformation(origin = {55.97944187702728, 1.9964584516128987}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
      rotation = 90.0)));
  TYThermalHydraulics.Valves.FlowValves.SymThrottleValve symThrottleValve1(lambda_crit = 100, Cqmax = 1, diam = 0.01, 
    redeclare model Medium = TYOilMedia.ThermalHydraulicOil.Types._5W30) 
    annotation (Placement(transformation(origin = {55.97944187702727, 33.99645845161291}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
      rotation = 90.0)));
equation
  connect(tank.port_A, hydraulicGroovedBushing.port_A) 
    annotation (Line(origin = {-67.99999999999996, -29.999999999999996}, 
      points = {{-8.0, 0.0}, {2.0, 0.0}}, 
      color = {255, 170, 0}));
  connect(hydraulicGroovedBushing.port_B, pipe_C1.port_A) 
    annotation (Line(origin = {-18.99999999999998, -29.999999999999996}, 
      points = {{-27.0, 0.0}, {-19.0, 0.0}}, 
      color = {255, 170, 0}));
  connect(pipe_C1.port_B, tjunction.port_A) 
    annotation (Line(origin = {-13.999999999999929, -30.003541548387098}, 
      points = {{-4.0, 0.0}, {4.0, 0.0}}, 
      color = {255, 170, 0}));
  connect(tjunction.port_B, pipe_C2.port_A) 
    annotation (Line(origin = {14.000000000000064, -30.003541548387098}, 
      points = {{-4.0, 0.0}, {4.0, 0.0}}, 
      color = {255, 170, 0}));
  connect(pipe_C2.port_B, axesIntersectingHoles.port_A) 
    annotation (Line(origin = {42.000000000000064, -30.003541548387098}, 
      points = {{-4.0, 0.0}, {4.0, 0.0}}, 
      color = {255, 170, 0}));
  connect(symThrottleValve.port_B, tank1.port_A) 
    annotation (Line(origin = {6.394884621840902e-14, 48.996458451612895}, 
      points = {{0.0, -5.0}, {0.0, 5.0}}, 
      color = {255, 170, 0}));
  connect(tjunction.port_C, centrifugalPipes_CRC.port_A) 
    annotation (Line(origin = {6.394884621840902e-14, -14.003541548387098}, 
      points = {{0.0, -6.0}, {0.0, 6.0}}, 
      color = {255, 170, 0}));
  connect(centrifugalPipes_CRC.port_B, symThrottleValve.port_A) 
    annotation (Line(origin = {6.394884621840902e-14, 17.996458451612902}, 
      points = {{0.0, -6.0}, {0.0, 6.0}}, 
      color = {255, 170, 0}));
  connect(axesIntersectingHoles.port_B, centrifugalPipes_CRC1.port_A) 
    annotation (Line(origin = {56.00000000000007, -14.003541548387098}, 
      points = {{0.0, -6.0}, {0.0, 6.0}}, 
      color = {255, 170, 0}));
  connect(tank2.port_A, symThrottleValve1.port_B) 
    annotation (Line(origin = {56.00000000000007, 48.996458451612895}, 
      points = {{0.0, 5.0}, {0.0, -5.0}}, 
      color = {255, 170, 0}));
  connect(symThrottleValve1.port_A, centrifugalPipes_CRC1.port_B) 
    annotation (Line(origin = {56.00000000000007, 17.996458451612902}, 
      points = {{0.0, 6.0}, {0.0, -6.0}}, 
      color = {255, 170, 0}));
end LubricatingSystem;