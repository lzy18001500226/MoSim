model VenturiTube "文丘里管"
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
    experiment(Algorithm = Dassl, Interval = 0.01, StartTime = 0, StopTime = 10, Tolerance = 1e-07), 
    Diagram(coordinateSystem(extent = {{-100.0, -100.0}, {100.0, 100.0}}, 
      grid = {2.0, 2.0})), 
    Documentation(link = "modelica://TYThermalHydraulics/Resources/HTML/VenturiTube.html"),Protection(access=Access.nonPackageDuplicate),__MWORKS(ResultViewerManager(resultViewers={
ResultViewer(name="1", executeTrigger=executeTrigger.SimulationFinished, commands={
CreatePlot(id=1, x="flowSource.flowSource.m_flow", x_display_unit="kg/s", legend_layout=7, left_title_type=2, left_title="压力/Bar
", bottom_title_type=2, bottom_title="质量流量/（kg/s）", fix_time_range_value=0, zoom_x=(0, 0.5), zoom_y_l=(-0.5, 3.5)), 
Plot(y=["progressivePipe.pB", "progressivePipe1.pB", "tank.port_A.p"], colors=["4294901760", "4278222848", "4294902015"])})
})));
  TYThermalHydraulics.Sources.Tank tank(p_load = 3e5, 
    redeclare model Medium = TYOilMedia.ThermalHydraulicOil.Types._5W30) 
    annotation (Placement(transformation(origin = {74.0, 7.996458451612902}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
      rotation = 90.0)));
  TYThermalHydraulics.Pipes.Pipe_C pipe_C(redeclare model Medium = TYOilMedia.ThermalHydraulicOil.Types._5W30) 
    annotation (Placement(transformation(origin = {-40.00000000000002, 7.999999999999993}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYThermalHydraulics.Sources.MHFlowSource flowSource(inputType_MassFlow = 2, constantPressure = 9.999999999999999e5, constantMassflow = 0.02, 
    constantTemperature = 293.15, 
    heightMassflow = 0.5, durationMassflow = 3, 
    redeclare model Medium = TYOilMedia.ThermalHydraulicOil.Types._5W30) 
    annotation (Placement(transformation(origin = {-70.00000000000004, 8.0}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYThermalHydraulics.Resistances.Junctions.ProgressivePipe progressivePipe(dl = 0.03, le = 0.1, 
    redeclare model Medium = TYOilMedia.ThermalHydraulicOil.Types._5W30) 
    annotation (Placement(transformation(origin = {-9.999999999999996, 7.999999999999993}, 
      extent = {{10.0, -10.0}, {-10.0, 10.0}})));
  TYThermalHydraulics.Pipes.Pipe_C pipe_C1(redeclare model Medium = TYOilMedia.ThermalHydraulicOil.Types._5W30) 
    annotation (Placement(transformation(origin = {20.00000000000003, 7.999999999999998}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYThermalHydraulics.Resistances.Junctions.ProgressivePipe progressivePipe1(dl = 0.04, le = 0.1, 
    redeclare model Medium = TYOilMedia.ThermalHydraulicOil.Types._5W30) 
    annotation (Placement(transformation(origin = {50.00000000000006, 7.999999999999998}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
equation
  connect(flowSource.port_B, pipe_C.port_A) 
    annotation (Line(origin = {-56.0, 7.999999999999993}, 
      points = {{-6.0, 0.0}, {6.0, 0.0}}, 
      color = {255, 170, 0}));
  connect(pipe_C.port_B, progressivePipe.port_B) 
    annotation (Line(origin = {-25.0, 8.0}, 
      points = {{-5.0, 0.0}, {5.0, 0.0}}, 
      color = {255, 170, 0}));
  connect(progressivePipe.port_A, pipe_C1.port_A) 
    annotation (Line(origin = {7.0, 8.0}, 
      points = {{-7.0, 0.0}, {3.0, 0.0}}, 
      color = {255, 170, 0}));
  connect(pipe_C1.port_B, progressivePipe1.port_A) 
    annotation (Line(origin = {41.0, 8.0}, 
      points = {{-11.0, 0.0}, {-1.0, 0.0}}, 
      color = {255, 170, 0}));
  connect(progressivePipe1.port_B, tank.port_A) 
    annotation (Line(origin = {72.0, -3.0}, 
      points = {{-12.0, 11.0}, {2.0, 11.0}}, 
      color = {255, 170, 0}));
end VenturiTube;