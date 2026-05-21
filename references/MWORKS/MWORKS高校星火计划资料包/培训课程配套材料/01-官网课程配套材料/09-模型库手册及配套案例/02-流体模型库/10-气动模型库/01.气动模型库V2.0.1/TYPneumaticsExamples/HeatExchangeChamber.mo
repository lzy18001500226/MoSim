model HeatExchangeChamber "热交换室"
  TYPneumatics.Sources.PressureSource pressureSource(constantPressure = 5.987e5, constantTemperature(displayUnit = "degC"), redeclare model GasType = TYGasMedia.MediaTypes.Air) 
    annotation (Placement(transformation(origin={-63.99999999999997,56}, 
extent={{-10,-10},{10,10}}, 
rotation=-90)));
  TYPneumatics.Valves.FlowControlValves.VarThrottleValve varThrottleValve(redeclare model GasType = TYGasMedia.MediaTypes.Air, UseVolumeA = false, Volume_A = 5e-6) 
    annotation (Placement(transformation(origin={-63.99999999999997,8.999999999999995}, 
extent={{-10,-10},{10,10}}, 
rotation=-90)));
  TYPneumatics.Valves.FlowControlValves.VarThrottleValve varThrottleValve1(redeclare model GasType = TYGasMedia.MediaTypes.Air, UseVolumeA = false, Volume_A = 5e-6) 
    annotation (Placement(transformation(origin={-63.99999999999997,-52.500000000000014}, 
extent={{-10,-10},{10,10}}, 
rotation=-90)));
  TYPneumatics.Sources.Surroundings surroundings(redeclare model GasType = TYGasMedia.MediaTypes.Air) 
    annotation (Placement(transformation(origin={-63.99999999999997,-85}, 
extent={{-10,-10},{10,10}})));
  TYPneumatics.Auxiliaries.GasCylinder gasCylinder(redeclare model GasType = TYGasMedia.MediaTypes.Air, pin(start = 0, fixed = false), Tin(displayUnit = "degC", start = 293), kth = 500, Text(displayUnit = "K") = 293, V = 0.001, Model = "Polytropic Model") 
    annotation (Placement(transformation(origin={-27.999999999999943,-2.000000000000007}, 
extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Sources.TimeTable timeTable(table = {{0, 1}, {5, 1}, {5, 0}, {10, 0}}) 
    annotation (Placement(transformation(origin={-100,11.999999999999998}, 
extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Sources.TimeTable timeTable1(table = {{0, 0}, {5, 0}, {5, 1}, {10, 1}}) 
    annotation (Placement(transformation(origin={-101.99999999999994,-49.500000000000014}, 
extent={{-10,-10},{10,10}})));
  TYPneumatics.Sources.PressureSource pressureSource1(constantPressure = 5.987e5, constantTemperature(displayUnit = "degC"), redeclare model GasType = TYGasMedia.MediaTypes.Air) 
    annotation (Placement(transformation(origin={66.00000000000003,56}, 
extent={{-10,-10},{10,10}}, 
rotation=-90)));
  TYPneumatics.Valves.FlowControlValves.VarThrottleValve varThrottleValve2(redeclare model GasType = TYGasMedia.MediaTypes.Air, UseVolumeA = false, Volume_A = 5e-6) 
    annotation (Placement(transformation(origin={66.00000000000003,8.999999999999995}, 
extent={{-10,-10},{10,10}}, 
rotation=-90)));
  TYPneumatics.Valves.FlowControlValves.VarThrottleValve varThrottleValve3(redeclare model GasType = TYGasMedia.MediaTypes.Air, UseVolumeA = false, Volume_A = 5e-6) 
    annotation (Placement(transformation(origin={66.00000000000003,-52.50000000000001}, 
extent={{-10,-10},{10,10}}, 
rotation=-90)));
  TYPneumatics.Sources.Surroundings surroundings1(redeclare model GasType = TYGasMedia.MediaTypes.Air) 
    annotation (Placement(transformation(origin={66.00000000000003,-85}, 
extent={{-10,-10},{10,10}})));
  TYPneumatics.Auxiliaries.GasCylinder gasCylinder1(redeclare model GasType = TYGasMedia.MediaTypes.Air, pin(start = 0, fixed = false), Tin(displayUnit = "degC", start = 293), kth = 500, Text(displayUnit = "K") = 293, V = 0.001, Model = "Thermal Exchange Model") 
    annotation (Placement(transformation(origin={102.00000000000006,-2.0000000000000053}, 
extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Sources.TimeTable timeTable2(table = {{0, 1}, {5, 1}, {5, 0}, {10, 0}}) 
    annotation (Placement(transformation(origin={30,12.000000000000002}, 
extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Sources.TimeTable timeTable3(table = {{0, 0}, {5, 0}, {5, 1}, {10, 1}}) 
    annotation (Placement(transformation(origin={28.000000000000057,-49.50000000000001}, 
extent={{-10,-10},{10,10}})));
  annotation (Icon(coordinateSystem(extent={{-100,-100},{100,100}}, 
grid={2,2}),graphics = {Polygon(origin={-7.105427357601002e-15,33}, 
lineColor={0,98,98}, 
fillColor={0,98,98}, 
fillPattern=FillPattern.Solid, 
points={{-64,1},{0,37},{64,1},{0,-37}}), Line(origin={0,-12}, 
points={{-62,18},{0,-18},{62,18}}, 
color={0,98,98}, 
thickness=5), Line(origin={7.105427357601002e-15,-39.99999999999999}, 
points={{-62,18},{0,-18},{62,18}}, 
color={0,98,98}, 
thickness=5)}), 
    experiment(Algorithm = Dassl, Interval = 0.01, StartTime = 0, StopTime = 10, Tolerance = 1e-05), Protection(access=Access.nonPackageDuplicate), 
    Documentation(link="modelica://TYPneumatics/Resources/HTML/HeatExchangeChamber.html"),Diagram(coordinateSystem(extent={{-140,-100},{140,100}}, 
grid={2,2}),graphics = {Text(origin={-63.99999999999997,84.99999999999997}, 
lineColor={0,0,0}, 
extent={{-36,7},{36,-7}}, 
textString="多变模式", 
textStyle={TextStyle.None}, 
textColor={0,0,0}, 
horizontalAlignment=LinePattern.None), Text(origin={69.99999999999993,82.99999999999997}, 
lineColor={0,0,0}, 
extent={{-36,7},{36,-7}}, 
textString="热交换模式", 
textStyle={TextStyle.None}, 
textColor={0,0,0}, 
horizontalAlignment=LinePattern.None)}),__MWORKS(ResultViewerManager(resultViewers={
ResultViewer(name="1", executeTrigger=executeTrigger.SimulationFinished, commands={
CreatePlot(id=1, x_display_unit="s", legend_layout=1, left_title_type=2, left_title="压力/bar", bottom_title_type=2, bottom_title="时间/s", right_title_type=2, fix_time_range_value=0, zoom_x=(0, 10), zoom_y_l=(-1, 7)), 
Plot(y=["gasCylinder.pin"], colors=["4278190335"]), 
CreatePlot(id=-1, x_display_unit="s", legend_layout=1, left_title_type=2, left_title="温度/degC", bottom_title_type=2, bottom_title="时间/s", right_title_type=2, fix_time_range_value=0, sub_plot=(2, 1), zoom_x=(0, 10), zoom_y_l=(0, 250)), 
Plot(y=["gasCylinder.Tin"], colors=["4278190335"]), 
CreatePlot(id=-1, x_display_unit="s", legend_layout=7, left_title_type=2, left_title="温度/degC", bottom_title_type=2, bottom_title="时间/s", fix_time_range_value=0, sub_plot=(2, 2), zoom_x=(0, 10), zoom_y_l=(10, 30)), 
Plot(y=["gasCylinder1.Tin"], colors=["4278190335"]), 
CreatePlot(id=-1, x_display_unit="s", legend_layout=7, left_title_type=2, left_title="压力/Bar", bottom_title_type=2, bottom_title="时间/s", fix_time_range_value=0, sub_plot=(1, 2), zoom_x=(0, 10), zoom_y_l=(-1, 7)), 
Plot(y=["gasCylinder1.pin"], colors=["4278190335"])})
})));
equation
  connect(timeTable.y, varThrottleValve.u) 
    annotation (Line(origin={-92.99999999999999,11.999999999999991}, 
points={{3.999999999999986,7.105427357601002e-15},{23.60000000000001,7.105427357601002e-15},{23.60000000000001,3.552713678800501e-15}}, 
color={0,0,127}));
  connect(timeTable1.y, varThrottleValve1.u) 
    annotation (Line(origin={-92.99999999999999,-50.000000000000014}, 
points={{2.0000000000000426,0.5},{23.60000000000001,0.5}}, 
color={0,0,127}));
  connect(pressureSource.port_B, varThrottleValve.port_A) 
  annotation(Line(origin={-63.99999999999994,33.999999999999986}, 
points={{-2.842170943040401e-14,14.000000000000014},{-2.842170943040401e-14,-14.999999999999993}}, 
color={28,193,208}));
  connect(varThrottleValve.port_B, varThrottleValve1.port_A) 
  annotation(Line(origin={-63.99999999999994,-22.000000000000007}, 
points={{-2.842170943040401e-14,21},{-2.842170943040401e-14,-20.500000000000007}}, 
color={28,193,208}));
  connect(gasCylinder.port_A, varThrottleValve1.port_A) 
  annotation(Line(origin={-45.99999999999994,-27.000000000000007}, 
points={{18,14.999999999999998},{18,1},{-18.00000000000003,1},{-18.00000000000003,-15.500000000000007}}, 
color={28,193,208}));
  connect(varThrottleValve1.port_B, surroundings.port_A) 
  annotation(Line(origin={-63.99999999999994,-71.00000000000001}, 
points={{-2.842170943040401e-14,8.5},{-2.842170943040401e-14,-8.999999999999986},{0.099999999999973,-8.999999999999986}}, 
color={28,193,208}));
  connect(timeTable2.y, varThrottleValve2.u) 
  annotation(Line(origin={37.000000000000014,11.999999999999995}, 
points={{3.999999999999986,7.105427357601002e-15},{23.600000000000016,7.105427357601002e-15},{23.600000000000016,0}}, 
color={0,0,127}));
  connect(timeTable3.y, varThrottleValve3.u) 
  annotation(Line(origin={37.000000000000014,-50.00000000000001}, 
points={{2.0000000000000426,0.5},{23.600000000000016,0.5}}, 
color={0,0,127}));
  connect(pressureSource1.port_B, varThrottleValve2.port_A) 
  annotation(Line(origin={66.00000000000006,33.99999999999999}, 
points={{-2.842170943040401e-14,14.000000000000007},{-2.842170943040401e-14,-15}}, 
color={28,193,208}));
  connect(varThrottleValve2.port_B, varThrottleValve3.port_A) 
  annotation(Line(origin={66.00000000000006,-22.000000000000007}, 
points={{-2.842170943040401e-14,21},{-2.842170943040401e-14,-20.5}}, 
color={28,193,208}));
  connect(gasCylinder1.port_A, varThrottleValve3.port_A) 
  annotation(Line(origin={84.00000000000006,-27.000000000000007}, 
points={{18,15},{18,1},{-18.00000000000003,1},{-18.00000000000003,-15.5}}, 
color={28,193,208}));
  connect(varThrottleValve3.port_B, surroundings1.port_A) 
  annotation(Line(origin={66.00000000000006,-71}, 
points={{-2.842170943040401e-14,8.499999999999993},{-2.842170943040401e-14,-9},{0.0999999999999659,-9}}, 
color={28,193,208}));
end HeatExchangeChamber;