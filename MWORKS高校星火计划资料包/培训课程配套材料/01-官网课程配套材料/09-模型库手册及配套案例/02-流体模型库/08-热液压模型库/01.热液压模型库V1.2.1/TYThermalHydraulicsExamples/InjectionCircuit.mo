model InjectionCircuit "简化喷射回路"
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
    experiment(Algorithm = Dassl, Interval = 0.01, StartTime = 0, StopTime = 30, Tolerance = 0.0001), 
    Diagram(coordinateSystem(extent = {{-100.0, -100.0}, {100.0, 100.0}}, 
      grid = {2.0, 2.0})), 
    Documentation(link = "modelica://TYThermalHydraulics/Resources/HTML/InjectionCircuit.html"),Protection(access=Access.nonPackageDuplicate),__MWORKS(ResultViewerManager(resultViewers={
ResultViewer(name="1", executeTrigger=executeTrigger.SimulationFinished, commands={
CreatePlot(id=1, x_display_unit="s", legend_layout=7, left_title_type=2, left_title="温度/degC", bottom_title_type=2, bottom_title="时间/s", fix_time_range_value=0, zoom_x=(0, 30), zoom_y_l=(40, 90)), 
Plot(y=["reliefValve.port_A.T", "reliefValve.port_B.T", "pipe_CR2.port_A.T"], colors=["4278190335", "4294901760", "4278222848"])})
})));
  TYThermalHydraulics.Sources.Tank tank(redeclare model Medium = TYOilMedia.ThermalHydraulicOil.Types._5W30) 
    annotation (Placement(transformation(origin = {58.0, 26.000000000000007}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYThermalHydraulics.Pipes.Pipe_C pipe_C(Tin(start = 323.15), d = 0.012, length = 0.4, 
    redeclare model Medium = TYOilMedia.ThermalHydraulicOil.Types._5W30) annotation (Placement(transformation(origin = {-3.999999999999993, 44.00000000000001}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYThermalHydraulics.Sources.MHFlowSource flowSource(inputType_MassFlow = 1, constantPressure = 9.999999999999999e7, constantMassflow = 0.02, 
    constantTemperature = 323.15, 
    redeclare model Medium = TYOilMedia.ThermalHydraulicOil.Types._5W30) 
    annotation (Placement(transformation(origin = {-34.0, 44.000000000000014}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYThermalHydraulics.Valves.FlowValves.SymThrottleValve symThrottleValve(diam = sqrt(4 * 0.018 / Modelica.Constants.pi) / 1000, 
    Cqmax = 1, 
    redeclare model Medium = TYOilMedia.ThermalHydraulicOil.Types._5W30) 
    annotation (Placement(transformation(origin = {40.0, 44.000000000000014}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYThermalHydraulics.Valves.PressureValves.ReliefValve reliefValve(pcrack = 9.999999999999999e7, 
    redeclare model Medium = TYOilMedia.ThermalHydraulicOil.Types._5W30) 
    annotation (Placement(transformation(origin = {20.999999999999996, 15.000000000000009}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYThermalHydraulics.Pipes.Pipe_CR pipe_CR(
    d = 0.01, 
    redeclare model Medium = TYOilMedia.ThermalHydraulicOil.Types._5W30,TA_init=323.15) 
    annotation (Placement(transformation(origin = {6.0, -14.0}, 
      extent = {{10.0, 10.0}, {-10.0, -10.0}})));
  TYThermalHydraulics.Pipes.Pipe_CR pipe_CR1(
    d = 0.01, 
    redeclare model Medium = TYOilMedia.ThermalHydraulicOil.Types._5W30,TA_init=323.15) 
    annotation (Placement(transformation(origin = {-16.0, 4.000000000000007}, 
      extent = {{-10.0, 10.0}, {10.0, -10.0}}, 
      rotation = -90.0)));
  TYThermalHydraulics.Sources.MHFlowSource flowSource1(constantMassflow = 0.02, constantTemperature = 323.15, constantPressure = 0, 
    redeclare model Medium = TYOilMedia.ThermalHydraulicOil.Types._5W30) 
    annotation (Placement(transformation(origin = {-34.0, 15.000000000000007}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYThermalHydraulics.Pipes.Pipe_CR pipe_CR2(
    d = 0.01, 
    redeclare model Medium = TYOilMedia.ThermalHydraulicOil.Types._5W30,TA_init=323.15) 
    annotation (Placement(transformation(origin = {-34.0, -13.999999999999993}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
      rotation = 180.0)));
  TYThermalHydraulics.Sources.Tank tank1(redeclare model Medium = TYOilMedia.ThermalHydraulicOil.Types._5W30) 
    annotation (Placement(transformation(origin = {-52.0, -32.00000000000001}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
equation
  connect(flowSource.port_B, pipe_C.port_A) 
    annotation (Line(origin = {-19.999999999999993, 44.00000000000001}, 
      points = {{-6.0, 0.0}, {6.0, 0.0}}, 
      color = {255, 170, 0}));
  connect(pipe_C.port_B, symThrottleValve.port_A) 
    annotation (Line(origin = {18.0, 44.0}, 
      points = {{-12.0, 0.0}, {12.0, 0.0}}, 
      color = {255, 170, 0}));
  connect(symThrottleValve.port_B, tank.port_A) 
    annotation (Line(origin = {54.0, 35.0}, 
      points = {{-4.0, 9.0}, {4.0, 9.0}, {4.0, -9.0}}, 
      color = {255, 170, 0}));
  connect(pipe_CR.port_A, reliefValve.port_B) 
    annotation (Line(origin = {11.0, -3.999999999999986}, 
      points = {{5.0, -10.0}, {10.0, -10.0}, {10.0, 9.0}}, 
      color = {255, 170, 0}));
  connect(flowSource1.port_B, pipe_CR1.port_A) 
    annotation (Line(origin = {-24.0, 18.000000000000007}, 
      points = {{-2.0, -3.0}, {8.0, -3.0}, {8.0, -4.0}}, 
      color = {255, 170, 0}));
  connect(tank1.port_A, pipe_CR2.port_B) 
    annotation (Line(origin = {-50.0, -22.999999999999993}, 
      points = {{-2.0, -9.0}, {-2.0, 9.0}, {6.0, 9.0}}, 
      color = {255, 170, 0}));
  connect(reliefValve.port_A, pipe_C.port_B) 
    annotation (Line(origin = {9.999999999999996, 35.00000000000001}, 
      points = {{11.0, -10.0}, {11.0, 9.0}, {-4.0, 9.0}}, 
      color = {255, 170, 0}));
  connect(pipe_CR2.port_A, pipe_CR.port_B) 
    annotation (Line(origin = {-14.0, -14.0}, 
      points = {{-10.0, 0.0}, {10.0, 0.0}}, 
      color = {255, 170, 0}));
  connect(pipe_CR2.port_A, pipe_CR1.port_B) 
    annotation (Line(origin = {-20.0, -10.0}, 
      points = {{-4.0, -4.0}, {4.0, -4.0}, {4.0, 4.0}}, 
      color = {255, 170, 0}));
end InjectionCircuit;