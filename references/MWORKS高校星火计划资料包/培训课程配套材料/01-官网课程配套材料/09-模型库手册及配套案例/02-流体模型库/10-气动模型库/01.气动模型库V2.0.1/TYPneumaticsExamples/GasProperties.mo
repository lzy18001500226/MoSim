model GasProperties "气体属性测试系统"
  TYPneumatics.Sources.PressureSource pressureSource(constantPressure = 7.999999999999999e5, constantTemperature(displayUnit = "degC"), redeclare model GasType = TYGasMedia.MediaTypes.O2_oxygen) 
    annotation (Placement(transformation(origin = {-48.0, 58.0}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
      rotation = -90.0)));
  TYPneumatics.Valves.FlowControlValves.VarThrottleValve varThrottleValve(redeclare model GasType = TYGasMedia.MediaTypes.O2_oxygen, UseVolumeA = false, Volume_A = 5e-6) 
    annotation (Placement(transformation(origin = {-48.0, 18.0}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
      rotation = -90.0)));
  TYPneumatics.Valves.FlowControlValves.VarThrottleValve varThrottleValve1(redeclare model GasType = TYGasMedia.MediaTypes.O2_oxygen, UseVolumeA = false, Volume_A = 5e-6) 
    annotation (Placement(transformation(origin = {-48.0, -43.5}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
      rotation = -90.0)));
  TYPneumatics.Sources.Surroundings surroundings(redeclare model GasType = TYGasMedia.MediaTypes.O2_oxygen) 
    annotation (Placement(transformation(origin={-48,-79}, 
extent={{-10,-10},{10,10}})));
  TYPneumatics.Auxiliaries.GasCylinder gasCylinder(redeclare model GasType = TYGasMedia.MediaTypes.O2_oxygen, pin(start = 0), Tin(displayUnit = "degC"), kth = 500, Text(displayUnit = "K"), V = 0.001) 
    annotation (Placement(transformation(origin = {-16.0, 9.999999999999993}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  Modelica.Blocks.Sources.TimeTable timeTable(table = {{0, 1}, {5, 1}, {5, 0}, {10, 0}}) 
    annotation (Placement(transformation(origin = {-79.99999999999996, 21.0}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  Modelica.Blocks.Sources.TimeTable timeTable1(table = {{0, 0}, {5, 0}, {5, 1}, {10, 1}}) 
    annotation (Placement(transformation(origin = {-79.99999999999997, -40.5}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  annotation (experiment(Algorithm = Dassl, Interval = 0.01, StartTime = 0, StopTime = 10, Tolerance = 1e-05), 
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
      thickness = 5.0)}), 
    Diagram(coordinateSystem(extent={{-100,-100},{100,100}}, 
grid={2,2}),graphics = {Text(origin={-48,91}, 
lineColor={0,0,0}, 
extent={{-23,6},{23,-6}}, 
textString="氧气：O2", 
textStyle={TextStyle.None}, 
textColor={0,0,0}, 
horizontalAlignment=LinePattern.None), Text(origin={51.99999999999993,91}, 
lineColor={0,0,0}, 
extent={{-23,6},{23,-6}}, 
textString="氢气：H2", 
textStyle={TextStyle.None}, 
textColor={0,0,0}, 
horizontalAlignment=LinePattern.None)}), Protection(access=Access.packageDuplicate),Documentation(link="modelica://TYPneumatics/Resources/HTML/GasProperties.html"),__MWORKS(ResultViewerManager(resultViewers={
ResultViewer(name="1", executeTrigger=executeTrigger.SimulationFinished, commands={
CreatePlot(id=2, x_display_unit="s", legend_layout=1, left_title_type=2, left_title="压力/bar", bottom_title_type=2, bottom_title="时间/s", right_title_type=2, fix_time_range_value=0, zoom_x=(0, 10), zoom_y_l=(-2, 10)), 
Plot(y=["gasCylinder.p", "gasCylinder1.p"], colors=["4278190335", "4294901760"]), 
CreatePlot(id=-1, x_display_unit="s", legend_layout=1, left_title_type=2, left_title="温度/degC", bottom_title_type=2, bottom_title="时间/s", right_title_type=2, fix_time_range_value=0, sub_plot=(2, 1), zoom_x=(0, 10), zoom_y_l=(-10, 60)), 
Plot(y=["gasCylinder.Tin", "gasCylinder1.Tin"], colors=["4278190335", "4294901760"]), 
CreatePlot(id=-1, x_display_unit="s", legend_layout=1, left_title_type=2, left_title="质量/kg", bottom_title_type=2, bottom_title="时间/s", right_title_type=2, fix_time_range_value=0, sub_plot=(3, 1), zoom_x=(0, 10), zoom_y_l=(0, 0.012)), 
Plot(y=["gasCylinder.mgas", "gasCylinder1.mgas"], colors=["4278190335", "4294901760"])})
})));
  TYPneumatics.Sources.PressureSource pressureSource1(constantPressure = 7.999999999999999e5, constantTemperature(displayUnit = "degC"), redeclare model GasType = TYGasMedia.MediaTypes.H2_hydrogen) 
    annotation (Placement(transformation(origin = {51.99999999999995, 58.0}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
      rotation = -90.0)));
  TYPneumatics.Valves.FlowControlValves.VarThrottleValve varThrottleValve2(redeclare model GasType = TYGasMedia.MediaTypes.H2_hydrogen, UseVolumeA = false, Volume_A = 5e-6) 
    annotation (Placement(transformation(origin = {51.99999999999996, 15.000000000000007}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
      rotation = -90.0)));
  TYPneumatics.Valves.FlowControlValves.VarThrottleValve varThrottleValve3(redeclare model GasType = TYGasMedia.MediaTypes.H2_hydrogen, UseVolumeA = false, Volume_A = 5e-6) 
    annotation (Placement(transformation(origin = {51.99999999999996, -46.50000000000001}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
      rotation = -90.0)));
  TYPneumatics.Sources.Surroundings surroundings1(redeclare model GasType = TYGasMedia.MediaTypes.H2_hydrogen) 
    annotation (Placement(transformation(origin = {51.99999999999996, -79.0}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYPneumatics.Auxiliaries.GasCylinder gasCylinder1(redeclare model GasType = TYGasMedia.MediaTypes.H2_hydrogen, pin(start = 0), Tin(displayUnit = "degC"), kth = 500, Text(displayUnit = "K"), V = 0.001) 
    annotation (Placement(transformation(origin = {83.99999999999997, 6.999999999999989}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  Modelica.Blocks.Sources.TimeTable timeTable2(table = {{0, 1}, {5, 1}, {5, 0}, {10, 0}}) 
    annotation (Placement(transformation(origin = {20.0, 18.0}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  Modelica.Blocks.Sources.TimeTable timeTable3(table = {{0, 0}, {5, 0}, {5, 1}, {10, 1}}) 
    annotation (Placement(transformation(origin = {19.999999999999986, -43.499999999999986}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
equation
  connect(timeTable.y, varThrottleValve.u) 
    annotation (Line(origin = {-77.0, 21.0}, 
      points = {{8.000000000000043, 0.0}, {23.6, 0.0}}, 
      color = {0, 0, 127}));
  connect(timeTable1.y, varThrottleValve1.u) 
    annotation (Line(origin = {-77.0, -41.0}, 
      points = {{8.000000000000028, 0.5}, {23.6, 0.5}}, 
      color = {0, 0, 127}));
  connect(timeTable2.y, varThrottleValve2.u) 
    annotation (Line(origin = {22.999999999999957, 18.0}, 
      points = {{8.000000000000043, 0.0}, {23.6, 7.105427357601002e-15}}, 
      color = {0, 0, 127}));
  connect(timeTable3.y, varThrottleValve3.u) 
    annotation (Line(origin = {22.999999999999957, -43.999999999999986}, 
      points = {{8.000000000000028, 0.5}, {23.6, 0.4999999999999787}}, 
      color = {0, 0, 127}));
  connect(varThrottleValve.port_A, pressureSource.port_B) 
  annotation(Line(origin={-48,39}, 
  points={{0,-11},{0,11}}, 
  color={28,193,208}));
  connect(varThrottleValve1.port_A, varThrottleValve.port_B) 
  annotation(Line(origin={-48,-13}, 
  points={{0,-20.5},{0,21}}, 
  color={28,193,208}));
  connect(gasCylinder.port_A, varThrottleValve.port_B) 
  annotation(Line(origin={-32,0}, 
  points={{16,-8.881784197001252e-15},{16,-8},{-16,-8},{-16,8}}, 
  color={28,193,208}));
  connect(varThrottleValve1.port_B, surroundings.port_A) 
  annotation(Line(origin={-48,-62}, 
points={{0,8.5},{0,-12},{0.10000000000000142,-12}}, 
color={28,193,208}));
  connect(varThrottleValve2.port_A, pressureSource1.port_B) 
  annotation(Line(origin={52,38}, 
  points={{-4.263256414560601e-14,-12.999999999999993},{-4.263256414560601e-14,12},{-4.973799150320701e-14,12}}, 
  color={28,193,208}));
  connect(varThrottleValve2.port_B, varThrottleValve3.port_A) 
  annotation(Line(origin={52,-16}, 
  points={{-4.263256414560601e-14,21.000000000000007},{-4.263256414560601e-14,-20.500000000000007}}, 
  color={28,193,208}));
  connect(gasCylinder1.port_A, varThrottleValve3.port_A) 
  annotation(Line(origin={68,-20}, 
  points={{15.999999999999972,16.999999999999986},{15.999999999999972,12},{-16.000000000000043,12},{-16.000000000000043,-16.500000000000007}}, 
  color={28,193,208}));
  connect(varThrottleValve3.port_B, surroundings1.port_A) 
  annotation(Line(origin={52,-65}, 
  points={{-4.263256414560601e-14,8.499999999999993},{-4.263256414560601e-14,-9},{0.09999999999995879,-9}}, 
  color={28,193,208}));
end GasProperties;