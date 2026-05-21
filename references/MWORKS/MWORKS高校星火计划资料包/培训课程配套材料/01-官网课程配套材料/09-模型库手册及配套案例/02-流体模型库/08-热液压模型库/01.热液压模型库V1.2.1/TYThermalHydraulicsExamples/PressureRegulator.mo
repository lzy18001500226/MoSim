model PressureRegulator "调压系统"
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
    experiment(Algorithm = Dassl, Interval = 0.01, StartTime = 0, StopTime = 10, Tolerance = 1e-05), 
    Diagram(coordinateSystem(extent = {{-100.0, -100.0}, {100.0, 100.0}}, 
      grid = {2.0, 2.0})), 
    Documentation(link = "modelica://TYThermalHydraulics/Resources/HTML/PressureRegulator.html"),Protection(access=Access.nonPackageDuplicate),__MWORKS(ResultViewerManager(resultViewers={
ResultViewer(name="1", executeTrigger=executeTrigger.SimulationFinished, commands={
CreatePlot(id=2, x_display_unit="s", legend_layout=7, left_title_type=2, left_title="压力/Bar", bottom_title_type=2, bottom_title="时间/s", right_title_type=2, fix_time_range_value=0, zoom_x=(0, 10), zoom_y_l=(5, 45)), 
Plot(y=["reducingValvewithFlowforce1.port_A.p"], colors=["4278190335"]), 
CreatePlot(id=-1, x_display_unit="s", legend_layout=7, left_title_type=2, left_title="阀口开度", bottom_title_type=2, bottom_title="时间/s", right_title_type=2, fix_time_range_value=0, sub_plot=(2, 1), zoom_x=(0, 10), zoom_y_l=(-0.2, 1.2)), 
Plot(y=["vSymThrottleValve1.u"], colors=["4278190335"]), 
CreatePlot(id=-1, x_display_unit="s", legend_layout=7, left_title_type=2, left_title="阀口开度", bottom_title_type=2, bottom_title="时间/s", right_title_type=2, fix_time_range_value=0, sub_plot=(2, 2), zoom_x=(0, 10), zoom_y_l=(-0.05, 0.2)), 
Plot(y=["reducingValvewithFlowforce1.reducingValvewithFlowforce.xv"], colors=["4278190335"]), 
CreatePlot(id=-1, x_display_unit="s", legend_layout=7, left_title_type=2, left_title="压力/Bar", bottom_title_type=2, bottom_title="时间/s", right_title_type=2, fix_time_range_value=0, sub_plot=(1, 2), zoom_x=(0, 10), zoom_y_l=(8.8, 10.2)), 
Plot(y=["reducingValvewithFlowforce1.port_B.p"], colors=["4278190335"])})
})));
  TYThermalHydraulics.Sources.PressureSource pressureSource1(inputType_p = 3,redeclare model Medium = TYOilMedia.ThermalHydraulicOil.Types._5W30) 
    annotation (Placement(transformation(origin = {-30.00000000000004, 2.0}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYThermalHydraulics.Auxiliaries.Capacitive.OilVolume2ports oilVolume2port1(pin(start = 9.999999999999999e5), V0(displayUnit = "l") = 0.001,redeclare model Medium = TYOilMedia.ThermalHydraulicOil.Types._5W30) 
    annotation (Placement(transformation(origin = {38.00000000000004, 2.000000000000007}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYThermalHydraulics.Valves.PressureValves.ReducingValvewithFlowforce reducingValvewithFlowforce1(dynamics = "Static", redeclare model Medium= TYOilMedia.ThermalHydraulicOil.Types._5W30  ) 
    annotation (Placement(transformation(origin = {4.0, 2.000000000000007}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
      rotation = 90.0)));
  TYThermalHydraulics.Sources.Tank tank1(redeclare model Medium = TYOilMedia.ThermalHydraulicOil.Types._5W30) 
    annotation (Placement(transformation(origin = {96.00000000000001, -8.0}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  Modelica.Blocks.Continuous.FirstOrder firstOrder2(T = 0.25) 
    annotation (Placement(transformation(origin = {48.00000000000003, -36.0}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  Modelica.Blocks.Sources.TimeTable Signal2(table = {{0.0, 0.5}, {7, 0.5}, {7, 1}, {10, 1}, {10, 0.1}, {15, 0.1}}) 
    annotation (Placement(transformation(origin = {14.000000000000002, -36.0}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYThermalHydraulics.Valves.FlowValves.VSymThrottleValve vSymThrottleValve1(diam = 0.002,redeclare model Medium = TYOilMedia.ThermalHydraulicOil.Types._5W30) 
    annotation (Placement(transformation(origin = {72.00000000000007, 2.000000000000007}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  Modelica.Blocks.Continuous.FirstOrder firstOrder(T = 0.25, y_start = 20) 
    annotation (Placement(transformation(origin = {-55.99999999999999, 4.359337231407}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  Modelica.Blocks.Sources.TimeTable Signal(table = {{0.0, 20}, {2, 40}, {5, 40}, {5, 20}, {10, 20}}) 
    annotation (Placement(transformation(origin = {-90.0, 4.359337231407}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
equation
  connect(pressureSource1.port_B, reducingValvewithFlowforce1.port_A) 
    annotation (Line(origin = {-13.999999999999979, 2.0}, 
      points = {{-8.0, 0.0}, {8.0, 0.0}}, 
      color = {255, 170, 0}));
  connect(reducingValvewithFlowforce1.port_B, oilVolume2port1.port_A) 
    annotation (Line(origin = {22.000000000000025, 2.0}, 
      points = {{-8.0, 0.0}, {8.0, 0.0}}, 
      color = {255, 170, 0}));
  connect(Signal2.y, firstOrder2.u) 
    annotation (Line(origin = {7.000000000000021, -35.999999999999986}, 
      points = {{18.0, 0.0}, {29.0, 0.0}}, 
      color = {0, 0, 127}));
  connect(oilVolume2port1.port_B, vSymThrottleValve1.port_A) 
    annotation (Line(origin = {54.000000000000014, 2.0}, 
      points = {{-8.0, 0.0}, {8.0, 0.0}}, 
      color = {255, 170, 0}));
  connect(vSymThrottleValve1.port_B, tank1.port_A) 
    annotation (Line(origin = {89.00000000000001, -3.0}, 
      points = {{-7.0, 5.0}, {7.0, 5.0}, {7.0, -5.0}}, 
      color = {255, 170, 0}));
  connect(firstOrder2.y, vSymThrottleValve1.u) 
    annotation (Line(origin = {64.00000000000001, -19.0}, 
      points = {{-5.0, -17.0}, {5.0, -17.0}, {5.0, 16.0}}, 
      color = {0, 0, 127}));
  connect(Signal.y, firstOrder.u) 
    annotation (Line(origin = {-104.99999999999993, 4.3593372314069825}, 
      points = {{26.0, 0.0}, {37.0, 0.0}}, 
      color = {0, 0, 127}));
  connect(firstOrder.y, pressureSource1.PressureSignal) 
    annotation (Line(origin = {-43.999999999999986, 4.0}, 
      points = {{-1.0, 0.0}, {8.0, 0.0}}, 
      color = {0, 0, 127}));
end PressureRegulator;