model PneumaticCircuit "气动回路"
  TYPneumatics.Auxiliaries.GasCylinder gasCylinder(pin(start = 9.999999999999999e5), Tin(displayUnit = "degC"), kth = 500, Text(displayUnit = "K"), V = 0.6) 
    annotation (Placement(transformation(origin = {-72.0, 2.0}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYPneumatics.Auxiliaries.GasCylinder gasCylinder1(pin(start = 4.999999999999999e5), Tin(displayUnit = "degC"), kth = 500, Text(displayUnit = "K"), V = 0.4) 
    annotation (Placement(transformation(origin = {26.000000000000014, -34.0}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYPneumatics.Auxiliaries.GasCylinder gasCylinder2(pin(start = 0), Tin(displayUnit = "degC"), kth = 500, Text(displayUnit = "K"), V = 0.1) 
    annotation (Placement(transformation(origin = {17.999999999999993, 52.0}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYPneumatics.Valves.FlowControlValves.ThrottleValve throttleValve(A = 3e-5) 
    annotation (Placement(transformation(origin = {-26.0, 30.0}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYPneumatics.Valves.FlowControlValves.ThrottleValve throttleValve1(A = 0.0003) 
    annotation (Placement(transformation(origin = {-26.0, -14.000000000000007}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYPneumatics.Valves.FlowControlValves.ThrottleValve throttleValve2(A = 3e-5) 
    annotation (Placement(transformation(origin = {26.000000000000014, -14.000000000000007}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  annotation (experiment(Algorithm = Dassl, Interval = 0.1, StartTime = 0, StopTime = 20, Tolerance = 1e-05), 
    Icon(coordinateSystem(extent = {{-100.0, -100.0}, {100.0, 100.0}}, 
      grid = {2.0, 2.0}), graphics = {Polygon(origin = {-7.105427357601002e-15, 33.0}, 
      lineColor = {0, 98, 98}, 
      fillColor = {0, 98, 98}, 
      fillPattern = FillPattern.Solid, 
      points = {{-64.0, 1.0}, {0.0, 37.0}, {64.0, 1.0}, {0.0, -37.0}}), Line(origin = {0.0, -12.0}, 
      points = {{-62.0, 18.0}, {0.0, -18.0}, {62.0, 18.0}}, 
      color = {0, 98, 98}, 
      thickness = 5.0), Line(origin = {7.105427357601002e-15, -39.99999999999999}, 
      points = {{-62.0, 18.0}, {0.0, -18.0}, {62.0, 18.0}}, 
      color = {0, 98, 98}, 
      thickness = 5.0)}), Protection(access=Access.nonPackageDuplicate), 
    Documentation(link = "modelica://TYPneumatics/Resources/HTML/PneumaticCircuit.html"),__MWORKS(ResultViewerManager(resultViewers={
ResultViewer(name="1", executeTrigger=executeTrigger.SimulationFinished, commands={
CreatePlot(id=2, x_display_unit="s", legend_layout=1, left_title_type=2, left_title="压力/bar", bottom_title_type=2, bottom_title="时间/s", right_title_type=2, fix_time_range_value=0, zoom_x=(0, 20), zoom_y_l=(-2, 12)), 
Plot(y=["gasCylinder.p", "gasCylinder1.p", "gasCylinder2.p"], colors=["4278190335", "4294901760", "4278222848"]), 
CreatePlot(id=-1, x_display_unit="s", legend_layout=1, left_title_type=2, left_title="质量流量系数", bottom_title_type=2, bottom_title="时间/s", right_title_type=2, fix_time_range_value=0, sub_plot=(2, 1), zoom_x=(0, 20), zoom_y_l=(-0.01, 0.05)), 
Plot(y=["throttleValve.throttleValve.Cm", "throttleValve1.throttleValve.Cm", "throttleValve2.throttleValve.Cm"], colors=["4278190335", "4294901760", "4278222848"]), 
CreatePlot(id=-1, x_display_unit="s", legend_layout=1, left_title_type=2, left_title="温度/degC
", bottom_title_type=2, bottom_title="时间/s", right_title_type=2, fix_time_range_value=0, sub_plot=(3, 1), zoom_x=(0, 20), zoom_y_l=(-20, 100)), 
Plot(y=["gasCylinder.Tin", "gasCylinder1.Tin", "gasCylinder2.Tin"], colors=["4278190335", "4294901760", "4278222848"])})
})));
equation
  connect(throttleValve1.port_B, throttleValve2.port_A) 
    annotation (Line(origin = {-14.0, -14.0}, 
      points = {{-2.0, -7.105427357601002e-15}, {30.000000000000014, -7.105427357601002e-15}}, 
      color = {90, 229, 225}));
  connect(throttleValve2.port_B, throttleValve.port_B) 
    annotation (Line(origin = {21.0, 8.0}, 
      points = {{15.000000000000014, -22.000000000000007}, {37.0, -22.000000000000007}, {37.0, 22.0}, {-37.0, 22.0}}, 
      color = {90, 229, 225}));
  connect(gasCylinder2.port_A, throttleValve.port_B) 
    annotation (Line(origin = {1.0, 39.0}, 
      points = {{16.999999999999993, 3.0}, {16.999999999999993, -9.0}, {-17.0, -9.0}}, 
      color = {90, 229, 225}));
  connect(gasCylinder1.port_A, throttleValve2.port_A) 
    annotation (Line(origin = {2.0, -47.0}, 
      points = {{24.000000000000014, 3.0}, {24.000000000000014, -5.0}, {0.0, -5.0}, {0.0, 32.99999999999999}, {14.000000000000014, 32.99999999999999}}, 
      color = {90, 229, 225}));
  connect(gasCylinder.port_A, throttleValve1.port_A) 
    annotation (Line(origin = {-60.000000000000014, -9.000000000000002}, 
      points = {{-11.999999999999986, 1.0}, {-11.999999999999986, -5.000000000000005}, {24.000000000000014, -5.000000000000005}}, 
      color = {90, 229, 225}));
  connect(throttleValve.port_A, throttleValve1.port_A) 
    annotation (Line(origin = {-22.0, 8.0}, 
      points = {{-14.0, 22.0}, {-28.0, 22.0}, {-28.0, -22.000000000000007}, {-14.0, -22.000000000000007}}, 
      color = {90, 229, 225}));
end PneumaticCircuit;