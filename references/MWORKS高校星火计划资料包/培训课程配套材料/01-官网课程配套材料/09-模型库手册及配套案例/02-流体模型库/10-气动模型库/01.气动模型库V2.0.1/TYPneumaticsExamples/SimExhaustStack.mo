model SimExhaustStack "简化版排气系统"
  Modelica.Blocks.Sources.Constant const(k = 600) 
    annotation (Placement(transformation(origin = {-81.99999999999997, -14.130709677419352}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  Modelica.Blocks.Sources.Constant const1(k = 0.5) 
    annotation (Placement(transformation(origin = {-81.99999999999997, 17.86929032258065}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYPneumatics.HeatExchangers.PipeCRwithHeatExchange pipeCRwithHeatExchange(dh = 0.5, length(displayUnit = "mm") = 2, rr = 0.01, TA_init = 873.15, UseVolumeB = false,redeclare model GasType = TYGasMedia.MediaTypes.Air,redeclare model GasMedium = TYGasMedia.MediaProperties.Semi_Perfect.Semi_Perfect) 
    annotation (Placement(transformation(origin = {-9.999999999999956, -4.440892098500626e-16}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
      rotation = 360.0)));
  TYPneumatics.Sources.TemperatureSource temperatureSource 
    annotation (Placement(transformation(origin = {22.27671278987792, 37.96929032258065}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
      rotation = -90.0)));
  TYPneumatics.HeatExchangers.PipeCRwithHeatExchange pipeCRwithHeatExchange1(dh = 0.5, length(displayUnit = "mm") = 2, rr = 0.01, TA_init = 873.15, UseVolumeB = false,redeclare model GasType = TYGasMedia.MediaTypes.Air,redeclare model GasMedium = TYGasMedia.MediaProperties.Semi_Perfect.Semi_Perfect) 
    annotation (Placement(transformation(origin = {54.00000000000003, -0.030709677419357817}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
      rotation = 360.0)));
  TYPneumatics.HeatExchangers.PipeCRwithHeatExchange pipeCRwithHeatExchange3(dh = 0.5, length(displayUnit = "mm") = 2, rr = 0.01, TA_init = 873.15, UseVolumeB = false,redeclare model GasType = TYGasMedia.MediaTypes.Air,redeclare model GasMedium = TYGasMedia.MediaProperties.Semi_Perfect.Semi_Perfect) 
    annotation (Placement(transformation(origin = {22.000000000000043, -0.1307096774193504}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
      rotation = 360.0)));
  TYPneumatics.Sources.Surroundings surroundings1(redeclare model GasType = TYGasMedia.MediaTypes.Air,redeclare model GasMedium = TYGasMedia.MediaProperties.Semi_Perfect.Semi_Perfect) 
    annotation (Placement(transformation(origin = {86.0, 6.938893903907228e-16}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
      rotation = 90.0)));
  annotation (Icon(coordinateSystem(extent = {{-100.0, -100.0}, {100.0, 100.0}}, 
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
    experiment(Algorithm=Dassl,Interval=0.01,StartTime=0,StopTime=10,Tolerance=1e-07), 
    Diagram(coordinateSystem(extent = {{-100.0, -100.0}, {100.0, 100.0}}, 
      grid = {2.0, 2.0})), Protection(access=Access.nonPackageDuplicate), 
    Documentation(link = "modelica://TYPneumatics/Resources/HTML/SimExhaustStack.html"),__MWORKS(ResultViewerManager(resultViewers={
ResultViewer(name="1", executeTrigger=executeTrigger.SimulationFinished, commands={
CreatePlot(id=1, x_display_unit="s", legend_layout=7, left_title_type=2, left_title="温度/degC", bottom_title_type=2, bottom_title="时间/s", fix_time_range_value=0, zoom_x=(0, 10), zoom_y_l=(460, 620)), 
Plot(y=["pipeCRwithHeatExchange.Tin", "pipeCRwithHeatExchange1.Tin", "pipeCRwithHeatExchange3.Tin"], colors=["4278190335", "4294901760", "4278222848"]), 
CreatePlot(id=-1, x_display_unit="s", legend_layout=7, left_title_type=2, left_title="热量/W", bottom_title_type=2, bottom_title="时间/s", fix_time_range_value=0, sub_plot=(2, 1), zoom_x=(0, 10), zoom_y_l=(2500, 5500)), 
Plot(y=["pipeCRwithHeatExchange.dhr", "pipeCRwithHeatExchange1.dhr", "pipeCRwithHeatExchange3.dhr"], colors=["4278190335", "4294901760", "4278222848"]), 
CreatePlot(id=-1, x_display_unit="s", legend_layout=7, left_title_type=2, left_title="热量/W", bottom_title_type=2, bottom_title="时间/s", fix_time_range_value=0, sub_plot=(3, 1), zoom_x=(0, 10), zoom_y_l=(0, 25000)), 
Plot(y=["pipeCRwithHeatExchange.dhc", "pipeCRwithHeatExchange1.dhc", "pipeCRwithHeatExchange3.dhc"], colors=["4278190335", "4294901760", "4278222848"])})
})));
  TYPneumatics.Sources.MHFlowSource mHFlowSource(inputType_MassFlow = 3, inputType_T = 3,redeclare model GasType = TYGasMedia.MediaTypes.Air,redeclare model GasMedium = TYGasMedia.MediaProperties.Semi_Perfect.Semi_Perfect) 
    annotation (Placement(transformation(origin = {-41.99999999999996, -0.13070967741935058}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
equation
  connect(pipeCRwithHeatExchange1.heat_a, temperatureSource.heat_a) 
    annotation (Line(origin = {42.00000000000004, 17.96929032258064}, 
      points = {{12.199999999999989, -14.399999999999999}, {12.199999999999989, 4.0}, {-19.8, 4.0}, {-19.8, 11.983573566842296}}, 
      color = {191, 0, 0}));
  connect(const1.y, mHFlowSource.MassflowSignal) 
    annotation (Line(origin = {-58.99999999999997, 9.86929032258065}, 
      points = {{-12.0, 8.0}, {-1.0, 8.0}, {-1.0, -7.6}, {11.425810000000013, -7.6}}, 
      color = {0, 0, 127}));
  connect(const.y, mHFlowSource.TemperatureSignal) 
    annotation (Line(origin = {-58.99999999999997, -8.13070967741935}, 
      points = {{-12.0, -6.000000000000002}, {-1.0, -6.000000000000002}, {-1.0, 5.60645}, {11.425810000000013, 5.60645}}, 
      color = {0, 0, 127}));
  connect(pipeCRwithHeatExchange.heat_a, temperatureSource.heat_a) 
    annotation (Line(origin = {8.000000000000043, 17.96929032258064}, 
      points = {{-17.799999999999997, -14.36929032258064}, {-17.799999999999997, 4.0}, {14.2, 4.0}, {14.2, 11.983573566842296}}, 
      color = {191, 0, 0}));
  connect(pipeCRwithHeatExchange3.port_B, pipeCRwithHeatExchange1.port_A) 
    annotation (Line(origin = {41.00000000000004, -0.03070967741935604}, 
      points = {{-9.0, -0.09999999999999437}, {2.999999999999986, -1.7763568394002505e-15}}, 
      color = {90, 229, 225}));
  connect(pipeCRwithHeatExchange3.heat_a, temperatureSource.heat_a) 
    annotation (Line(origin = {25.000000000000046, 17.96929032258064}, 
      points = {{-2.8000000000000043, -14.499999999999991}, {-2.8000000000000043, 11.983573566842296}}, 
      color = {191, 0, 0}));
  connect(pipeCRwithHeatExchange.port_B, pipeCRwithHeatExchange3.port_A) 
    annotation (Line(origin = {6.0, 0.0}, 
      points = {{-5.999999999999956, -4.440892098500626e-16}, {6.000000000000043, -4.440892098500626e-16}, {6.000000000000043, -0.1307096774193504}}, 
      color = {90, 229, 225}));
  connect(mHFlowSource.port_B, pipeCRwithHeatExchange.port_A) 
    annotation (Line(origin = {-38.0, 0.0}, 
      points = {{4.034580645161334, -0.09999999999999572}, {18.000000000000043, -4.440892098500626e-16}}, 
      color = {90, 229, 225}));
  connect(pipeCRwithHeatExchange1.port_B, surroundings1.port_A) 
    annotation (Line(origin = {82.0, 0.0}, 
      points = {{-17.99999999999997, -0.030709677419357817}, {-1.0, -0.030709677419357817}, {-1.0, 0.1000000000000007}}, 
      color = {90, 229, 225}));
end SimExhaustStack;