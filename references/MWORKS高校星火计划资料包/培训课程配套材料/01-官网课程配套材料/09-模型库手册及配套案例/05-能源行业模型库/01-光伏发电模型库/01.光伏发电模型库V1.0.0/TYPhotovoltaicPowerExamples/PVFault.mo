model PVFault "光伏板故障模拟"
  annotation(Documentation(link = "modelica://TYPhotovoltaicPower/Resources/Examples/PVFault.html"), 
    Icon(coordinateSystem(extent = {{-100.0, -100.0}, {100.0, 100.0}}, 
    grid = {2.0, 2.0}), graphics = {Polygon(origin = {-7.105427357601002e-15, 33.0}, 
    lineColor = {16, 99, 16}, 
    fillColor = {16, 99, 16}, 
    fillPattern = FillPattern.Solid, 
    points = {{-64.0, 1.0}, {0.0, 37.0}, {64.0, 1.0}, {0.0, -37.0}}), Line(origin = {0.0, -12.0}, 
    points = {{-62.0, 18.0}, {0.0, -18.0}, {62.0, 18.0}}, 
    color = {16, 99, 16}, 
    thickness = 5.0), Line(origin = {7.105427357601002e-15, -39.99999999999999}, 
    points = {{-62.0, 18.0}, {0.0, -18.0}, {62.0, 18.0}}, 
    color = {16, 99, 16}, 
    thickness = 5.0)}), Diagram(coordinateSystem(extent = {{-100, -100}, {100, 100}}, 
    grid = {2, 2}), graphics = {Text(origin = {-84.131, 119.357}, 
    lineColor = {0, 0, 128}, 
    extent = {{-50, 7}, {50, -7}}, 
    textString = "断路故障模拟", 
    textStyle = {TextStyle.Italic}, 
    textColor = {0, 0, 128}), Text(origin = {149.869, 119.357}, 
    lineColor = {0, 0, 128}, 
    extent = {{-50, 7}, {50, -7}}, 
    textString = "短路故障模拟", 
    textStyle = {TextStyle.Italic}, 
    textColor = {0, 0, 128}), Text(origin = {-325.32637, 117.357}, 
    lineColor = {0, 0, 128}, 
    extent = {{-50, 7}, {50, -7}}, 
    textString = "无故障", 
    textStyle = {TextStyle.Italic}, 
    textColor = {0, 0, 128}), Rectangle(origin = {-325, -27.36515}, 
    fillColor = {255, 255, 255}, 
    pattern = LinePattern.Dash, 
    lineThickness = 0.5, 
    extent = {{-115, 162.63485}, {115, -162.63485}}), Rectangle(origin = {-88, -27.36515}, 
    fillColor = {255, 255, 255}, 
    pattern = LinePattern.Dash, 
    lineThickness = 0.5, 
    extent = {{-115, 162.63485}, {115, -162.63485}}), Rectangle(origin = {151, -27.36515}, 
    fillColor = {255, 255, 255}, 
    pattern = LinePattern.Dash, 
    lineThickness = 0.5, 
    extent = {{-115, 162.63485}, {115, -162.63485}})}), __MWORKS(ResultViewerManager(resultViewers={
ResultViewer(name="1", executeTrigger=executeTrigger.SimulationFinished, commands={
CreatePlot(id=1, x_display_unit="s", legend_layout=1, left_title_type=2, left_title="输出功率[W]", bottom_title_type=2, bottom_title="时间[s]", right_title_type=2, fix_time_range_value=0, zoom_x=(0, 100), zoom_y_l=(-500, 2500)), 
Plot(legend=["无故障输出功率[W]", "断路故障输出功率[W]", "断路故障对比工况输出功率[W]"], y=["product5.y", "product1.y", "product2.y"], colors=["4278190335", "4294901760", "4278222848"]), 
CreatePlot(id=-1, x_display_unit="s", legend_layout=1, left_title_type=2, left_title="输出功率[W]", bottom_title_type=2, bottom_title="时间/s", fix_time_range_value=0, sub_plot=(2, 1), zoom_x=(0, 100), zoom_y_l=(-500, 2500)), 
Plot(legend=["无故障输出功率[W]", "短路故障输出功率[W]", "断路故障对比输出功率[W]"], y=["product5.y", "product3.y", "product4.y"], colors=["4278190335", "4294901760", "4278222848"])})
}),ContinueSimConfig(SaveContinueFile = "false", SaveBeforeStop = "false", NumberBeforeStop = 1, FixedContinueInterval = "false", ContinueIntervalLength = 100, ContinueTimeVector)), experiment(Algorithm = Cvode, InlineIntegrator = false, InlineStepSize = false, Interval = 0.001, StartTime = 0, StopTime = 100, Tolerance = 0.0001), Protection(access = Access.nonPackageDuplicate));
  TYPhotovoltaicPower.Generators.SPPVArray sPPVArray(m = 3, n = 3, FaultType = {0, 2, 0}, FaultNum = {0, 0, 0}, redeclare package SolarType = TYPhotovoltaicPower.Generators.Basics.SolarType.Solar_User) 
    annotation(Placement(transformation(origin = {-94, 82}, 
    extent = {{-10, -10}, {10, 10}})));
  Modelica.Electrical.Analog.Basic.Ground ground1 
    annotation(Placement(transformation(origin = {-49.9996, 38}, 
    extent = {{-10, -10}, {10, 10}})));
  Modelica.Electrical.Analog.Sources.RampVoltage rampVoltage(duration = 100, V = 36 * 3) 
    annotation(Placement(transformation(origin = {-42.131, 79.973}, 
    extent = {{-7.6162, -7.6162}, {7.6162, 7.6162}}, 
    rotation = 270)));
  Modelica.Electrical.Analog.Sensors.VoltageSensor Vo 
    annotation(Placement(transformation(origin = {-18.8742, 79.973}, 
    extent = {{5.51285, -5.51285}, {-5.51285, 5.51285}}, 
    rotation = -270)));
  Modelica.Electrical.Analog.Sensors.CurrentSensor Io 
    annotation(Placement(transformation(origin = {-54.663, 97.64}, 
    extent = {{-5.33663, 5.33663}, {5.33663, -5.33663}})));
  Modelica.Blocks.Math.Product product1 
    annotation(Placement(transformation(origin = {8.4875, 100.947}, 
    extent = {{-5.51285, -5.51285}, {5.51285, 5.51285}})));
  TYPhotovoltaicPower.Environment.Illumination illumination(N_SubArray = 9, SolarInputType = "外部输入") 
    annotation(Placement(transformation(origin = {-148, 82}, 
    extent = {{-10, -10}, {10, 10}})));
  TYPhotovoltaicPower.Sources.HeatSources.TemperatureSource[3] temperatureSource1(n = 3, T = 298.15) 
    annotation(Placement(transformation(origin = {-148, 38}, 
    extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Sources.Constant const(k = 1000) 
    annotation(Placement(transformation(origin = {-184, 77}, 
    extent = {{-10, -10}, {10, 10}})));
  TYPhotovoltaicPower.Generators.SPPVArray sPPVArray1(m = 3, n = 2) 
    annotation(Placement(transformation(origin = {-94, -49.6433}, 
    extent = {{-10, -10}, {10, 10}})));
  Modelica.Electrical.Analog.Basic.Ground ground2 
    annotation(Placement(transformation(origin = {-49.9996, -93.6433}, 
    extent = {{-10, -10}, {10, 10}})));
  Modelica.Electrical.Analog.Sources.RampVoltage rampVoltage1(duration = 100, V = 36 * 3) 
    annotation(Placement(transformation(origin = {-42.131, -51.6704}, 
    extent = {{-7.6162, -7.6162}, {7.6162, 7.6162}}, 
    rotation = 270)));
  Modelica.Electrical.Analog.Sensors.VoltageSensor Vo1 
    annotation(Placement(transformation(origin = {-18.8742, -51.6704}, 
    extent = {{5.51285, -5.51285}, {-5.51285, 5.51285}}, 
    rotation = -270)));
  Modelica.Electrical.Analog.Sensors.CurrentSensor Io1 
    annotation(Placement(transformation(origin = {-54.663, -34.0037}, 
    extent = {{-5.33663, 5.33663}, {5.33663, -5.33663}})));
  Modelica.Blocks.Math.Product product2 
    annotation(Placement(transformation(origin = {8.4875, -34.1799}, 
    extent = {{-5.51285, -5.51285}, {5.51285, 5.51285}})));
  TYPhotovoltaicPower.Environment.Illumination illumination1(N_SubArray = 6, SolarInputType = "外部输入") 
    annotation(Placement(transformation(origin = {-148, -49.6433}, 
    extent = {{-10, -10}, {10, 10}})));
  TYPhotovoltaicPower.Sources.HeatSources.TemperatureSource[3] temperatureSource2(n = 2, T = 298.15) 
    annotation(Placement(transformation(origin = {-148, -93.6433}, 
    extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Sources.Constant const1(k = 1000) 
    annotation(Placement(transformation(origin = {-184, -54.6433}, 
    extent = {{-10, -10}, {10, 10}})));
  TYPhotovoltaicPower.Generators.SPPVArray sPPVArray2(m = 3, n = 3, FaultType = {0, 1, 0}, FaultNum = {0, 1, 0}) 
    annotation(Placement(transformation(origin = {140, 82}, 
    extent = {{-10, -10}, {10, 10}})));
  Modelica.Electrical.Analog.Basic.Ground ground3 
    annotation(Placement(transformation(origin = {184, 38}, 
    extent = {{-10, -10}, {10, 10}})));
  Modelica.Electrical.Analog.Sources.RampVoltage rampVoltage2(duration = 80, V = 87) 
    annotation(Placement(transformation(origin = {191.869, 79.973}, 
    extent = {{-7.6162, -7.6162}, {7.6162, 7.6162}}, 
    rotation = 270)));
  Modelica.Electrical.Analog.Sensors.VoltageSensor Vo2 
    annotation(Placement(transformation(origin = {215.1258, 79.973}, 
    extent = {{5.51285, -5.51285}, {-5.51285, 5.51285}}, 
    rotation = -270)));
  Modelica.Electrical.Analog.Sensors.CurrentSensor Io2 
    annotation(Placement(transformation(origin = {179.337, 97.64}, 
    extent = {{-5.33663, 5.33663}, {5.33663, -5.33663}})));
  Modelica.Blocks.Math.Product product3 
    annotation(Placement(transformation(origin = {242.4875, 100.947}, 
    extent = {{-5.51285, -5.51285}, {5.51285, 5.51285}})));
  TYPhotovoltaicPower.Environment.Illumination illumination2(N_SubArray = 9, SolarInputType = "外部输入") 
    annotation(Placement(transformation(origin = {86, 82}, 
    extent = {{-10, -10}, {10, 10}})));
  TYPhotovoltaicPower.Sources.HeatSources.TemperatureSource[3] temperatureSource3(n = 3, T = 298.15) 
    annotation(Placement(transformation(origin = {86, 38}, 
    extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Sources.Constant const2(k = 1000) 
    annotation(Placement(transformation(origin = {50, 77}, 
    extent = {{-10, -10}, {10, 10}})));
  TYPhotovoltaicPower.Generators.SPPVArray sPPVArray3(m = 3, n = 2, FaultType = {0, 0}, FaultNum = {0, 0}) 
    annotation(Placement(transformation(origin = {140, -16}, 
    extent = {{-10, -10}, {10, 10}})));
  Modelica.Electrical.Analog.Basic.Ground ground4 
    annotation(Placement(transformation(origin = {184, -60}, 
    extent = {{-10, -10}, {10, 10}})));
  Modelica.Electrical.Analog.Sources.RampVoltage rampVoltage3(duration = 80, V = 87) 
    annotation(Placement(transformation(origin = {191.869, -18.0271}, 
    extent = {{-7.6162, -7.6162}, {7.6162, 7.6162}}, 
    rotation = 270)));
  Modelica.Electrical.Analog.Sensors.VoltageSensor Vo3 
    annotation(Placement(transformation(origin = {215.1258, -18.0271}, 
    extent = {{5.51285, -5.51285}, {-5.51285, 5.51285}}, 
    rotation = -270)));
  Modelica.Electrical.Analog.Sensors.CurrentSensor Io3 
    annotation(Placement(transformation(origin = {179.337, -0.3604}, 
    extent = {{-5.33663, 5.33663}, {5.33663, -5.33663}})));
  Modelica.Blocks.Math.Product product4 
    annotation(Placement(transformation(origin = {242.4875, 2.9473}, 
    extent = {{-5.51285, -5.51285}, {5.51285, 5.51285}})));
  TYPhotovoltaicPower.Environment.Illumination illumination3(N_SubArray = 6, SolarInputType = "外部输入") 
    annotation(Placement(transformation(origin = {86, -16}, 
    extent = {{-10, -10}, {10, 10}})));
  TYPhotovoltaicPower.Sources.HeatSources.TemperatureSource[3] temperatureSource4(n = 2, T = 298.15) 
    annotation(Placement(transformation(origin = {86, -60}, 
    extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Sources.Constant const3(k = 1000) 
    annotation(Placement(transformation(origin = {50, -21}, 
    extent = {{-10, -10}, {10, 10}})));
  TYPhotovoltaicPower.Generators.SPPVArray sPPVArray4(m = 2, n = 1, FaultType = {0}, FaultNum = {0}) 
    annotation(Placement(transformation(origin = {140, -93.6433}, 
    extent = {{-10, -10}, {10, 10}})));
  TYPhotovoltaicPower.Environment.Illumination illumination4(N_SubArray = 2, SolarInputType = "外部输入") 
    annotation(Placement(transformation(origin = {86, -93.6433}, 
    extent = {{-10, -10}, {10, 10}})));
  TYPhotovoltaicPower.Sources.HeatSources.TemperatureSource[2] temperatureSource5(n = 1, T = 298.15) 
    annotation(Placement(transformation(origin = {86, -137.6433}, 
    extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Sources.Constant const4(k = 1000) 
    annotation(Placement(transformation(origin = {50, -98.6433}, 
    extent = {{-10, -10}, {10, 10}})));
  TYPhotovoltaicPower.Generators.SPPVArray sPPVArray5(m = 3, n = 3, FaultType = {0, 0, 0}, FaultNum = {0, 0, 0}, redeclare package SolarType = TYPhotovoltaicPower.Generators.Basics.SolarType.Solar_User) 
    annotation(Placement(transformation(origin = {-320, 10.255}, 
    extent = {{-10, -10}, {10, 10}})));
  Modelica.Electrical.Analog.Basic.Ground ground5 
    annotation(Placement(transformation(origin = {-276, -33.74499}, 
    extent = {{-10, -10}, {10, 10}})));
  Modelica.Electrical.Analog.Sources.RampVoltage rampVoltage4(duration = 100, V = 36 * 3) 
    annotation(Placement(transformation(origin = {-268.131, 8.22801}, 
    extent = {{-7.6162, -7.6162}, {7.6162, 7.6162}}, 
    rotation = 270)));
  Modelica.Electrical.Analog.Sensors.VoltageSensor Vo4 
    annotation(Placement(transformation(origin = {-244.874, 8.22801}, 
    extent = {{5.51285, -5.51285}, {-5.51285, 5.51285}}, 
    rotation = -270)));
  Modelica.Electrical.Analog.Sensors.CurrentSensor Io4 
    annotation(Placement(transformation(origin = {-280.663, 25.89501}, 
    extent = {{-5.33663, 5.33663}, {5.33663, -5.33663}})));
  Modelica.Blocks.Math.Product product5 
    annotation(Placement(transformation(origin = {-217.513, 29.20201}, 
    extent = {{-5.51285, -5.51285}, {5.51285, 5.51285}})));
  TYPhotovoltaicPower.Environment.Illumination illumination5(N_SubArray = 9, SolarInputType = "外部输入") 
    annotation(Placement(transformation(origin = {-374, 10.255}, 
    extent = {{-10, -10}, {10, 10}})));
  TYPhotovoltaicPower.Sources.HeatSources.TemperatureSource[3] temperatureSource6(n = 3, T = 298.15) 
    annotation(Placement(transformation(origin = {-374, -33.74499}, 
    extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Sources.Constant const5(k = 1000) 
    annotation(Placement(transformation(origin = {-410, 5.25501}, 
    extent = {{-10, -10}, {10, 10}})));
equation
  connect(Io.n, rampVoltage.p) 
    annotation(Line(origin = {-23.7801, 93.6695}, 
    points = {{-25.54627, 3.9705}, {-18.3509, 3.9705}, {-18.3509, -6.0803}}, 
    color = {0, 0, 255}));
  connect(Vo.p, rampVoltage.p) 
    annotation(Line(origin = {-2.7801, 88.6695}, 
    points = {{-16.0941, -3.18365}, {-16.0941, 9}, {-39.3509, 9}, {-39.3509, -1.0803}}, 
    color = {0, 0, 255}));
  connect(Vo.n, ground1.p) 
    annotation(Line(origin = {-25.7801, 58.6695}, 
    points = {{6.9059, 15.79065}, {6.9059, 3}, {-24.2195, 3}, {-24.2195, -10.6695}}, 
    color = {0, 0, 255}));
  connect(rampVoltage.n, ground1.p) 
    annotation(Line(origin = {-38.7801, 58.6695}, 
    points = {{-3.3509, 13.6873}, {-3.3509, 3}, {-11.2195, 3}, {-11.2195, -10.6695}}, 
    color = {0, 0, 255}));
  connect(Io.i, product1.u1) 
    annotation(Line(origin = {-9.7801, 108.67}, 
    points = {{-44.8829, -5.15971}, {11.6522, -5.15971}, {11.6522, -4.41529}}, 
    color = {0, 0, 127}));
  connect(Vo.v, product1.u2) 
    annotation(Line(origin = {17.2199, 88.6695}, 
    points = {{-30.029965, -8.6965}, {-30.029965, 8.96979}, {-15.3478, 8.96979}}, 
    color = {0, 0, 127}));
  connect(sPPVArray.pin_p, Io.p) 
    annotation(Line(origin = {-72, 92}, 
    points = {{-12, -6}, {-2, -6}, {-2, 5.64}, {12.0004, 5.64}}, 
    color = {0, 0, 255}));
  connect(sPPVArray.pin_n, ground1.p) 
    annotation(Line(origin = {-67, 63}, 
    points = {{-17, 15}, {3, 15}, {3, -1}, {17.0004, -1}, {17.0004, -15}}, 
    color = {0, 0, 255}));
  connect(illumination.SolarAngle, sPPVArray.SolarAngle) 
    annotation(Line(origin = {-151, 162}, 
    points = {{14, -75}, {45, -75}, {45, -73.6}}, 
    color = {0, 0, 127}));
  connect(illumination.ShieldRate, sPPVArray.ShieldRate) 
    annotation(Line(origin = {-153, 156.9997}, 
    points = {{16, -74.9997}, {47, -74.9997}}, 
    color = {0, 0, 127}));
  connect(illumination.Solar, sPPVArray.Solar) 
    annotation(Line(origin = {-156, 150.9997}, 
    points = {{19, -73.9997}, {50, -73.9997}, {50, -74.9997}}, 
    color = {0, 0, 127}));
  connect(temperatureSource1.port, sPPVArray.heatPort) 
    annotation(Line(origin = {-151, 136.9997}, 
    points = {{13, -98.9997}, {57, -98.9997}, {57, -64.9997}}, 
    color = {191, 0, 0}));
  connect(illumination.SolarInput, const.y) 
    annotation(Line(origin = {-171, 77}, 
    points = {{11, 0}, {-2, 0}}, 
    color = {0, 0, 127}));
  connect(Io1.n, rampVoltage1.p) 
    annotation(Line(origin = {-23.7801, -37.9738}, 
    points = {{-25.54627, 3.9701}, {-18.3509, 3.9701}, {-18.3509, -6.0804}}, 
    color = {0, 0, 255}));
  connect(Vo1.p, rampVoltage1.p) 
    annotation(Line(origin = {-2.7801, -42.9738}, 
    points = {{-16.0941, -3.18375}, {-16.0941, 9}, {-39.3509, 9}, {-39.3509, -1.0804}}, 
    color = {0, 0, 255}));
  connect(Vo1.n, ground2.p) 
    annotation(Line(origin = {-25.7801, -72.9738}, 
    points = {{6.9059, 15.7905}, {6.9059, 3}, {-24.2195, 3}, {-24.2195, -10.6695}}, 
    color = {0, 0, 255}));
  connect(rampVoltage1.n, ground2.p) 
    annotation(Line(origin = {-38.7801, -72.9738}, 
    points = {{-3.3509, 13.6872}, {-3.3509, 3}, {-11.2195, 3}, {-11.2195, -10.6695}}, 
    color = {0, 0, 255}));
  connect(Io1.i, product2.u1) 
    annotation(Line(origin = {-9.7801, 10.67}, 
    points = {{-44.8829, -38.803407}, {11.6522, -38.803407}, {11.6522, -41.5422}}, 
    color = {0, 0, 127}));
  connect(Vo1.v, product2.u2) 
    annotation(Line(origin = {17.2199, -9.3305}, 
    points = {{-30.029965, -42.3399}, {-30.029965, -28.1571}, {-15.3478, -28.1571}}, 
    color = {0, 0, 127}));
  connect(sPPVArray1.pin_p, Io1.p) 
    annotation(Line(origin = {-72, -39.6433}, 
    points = {{-12, -6}, {-2, -6}, {-2, 5.6396}, {12.0004, 5.6396}}, 
    color = {0, 0, 255}));
  connect(sPPVArray1.pin_n, ground2.p) 
    annotation(Line(origin = {-67, -68.6433}, 
    points = {{-17, 15}, {3, 15}, {3, -1}, {17.0004, -1}, {17.0004, -15}}, 
    color = {0, 0, 255}));
  connect(illumination1.SolarAngle, sPPVArray1.SolarAngle) 
    annotation(Line(origin = {-151, 30.3567}, 
    points = {{14, -75}, {45, -75}, {45, -73.6}}, 
    color = {0, 0, 127}));
  connect(illumination1.ShieldRate, sPPVArray1.ShieldRate) 
    annotation(Line(origin = {-153, 25.3567}, 
    points = {{16, -75}, {47, -75}}, 
    color = {0, 0, 127}));
  connect(illumination1.Solar, sPPVArray1.Solar) 
    annotation(Line(origin = {-156, 19.3567}, 
    points = {{19, -74}, {50, -74}, {50, -75}}, 
    color = {0, 0, 127}));
  connect(illumination1.SolarInput, const1.y) 
    annotation(Line(origin = {-171, -54.6433}, 
    points = {{11, 0}, {-2, 0}}, 
    color = {0, 0, 127}));
  connect(Io2.n, rampVoltage2.p) 
    annotation(Line(origin = {210.22, 93.6695}, 
    points = {{-25.5464, 3.9705}, {-18.351, 3.9705}, {-18.351, -6.0803}}, 
    color = {0, 0, 255}));
  connect(Vo2.p, rampVoltage2.p) 
    annotation(Line(origin = {231.22, 88.6695}, 
    points = {{-16.0942, -3.18365}, {-16.0942, 9}, {-39.351, 9}, {-39.351, -1.0803}}, 
    color = {0, 0, 255}));
  connect(Vo2.n, ground3.p) 
    annotation(Line(origin = {208.22, 58.6695}, 
    points = {{6.9058, 15.79065}, {6.9058, 3}, {-24.22, 3}, {-24.22, -10.6695}}, 
    color = {0, 0, 255}));
  connect(rampVoltage2.n, ground3.p) 
    annotation(Line(origin = {195.22, 58.6695}, 
    points = {{-3.351, 13.6873}, {-3.351, 3}, {-11.22, 3}, {-11.22, -10.6695}}, 
    color = {0, 0, 255}));
  connect(Io2.i, product3.u1) 
    annotation(Line(origin = {224.22, 108.67}, 
    points = {{-44.883, -5.15971}, {11.6521, -5.15971}, {11.6521, -4.41529}}, 
    color = {0, 0, 127}));
  connect(Vo2.v, product3.u2) 
    annotation(Line(origin = {251.22, 88.6695}, 
    points = {{-30.0301, -8.6965}, {-30.0301, 8.96979}, {-15.3479, 8.96979}}, 
    color = {0, 0, 127}));
  connect(sPPVArray2.pin_p, Io2.p) 
    annotation(Line(origin = {162, 92}, 
    points = {{-12, -6}, {-2, -6}, {-2, 5.64}, {12.0004, 5.64}}, 
    color = {0, 0, 255}));
  connect(sPPVArray2.pin_n, ground3.p) 
    annotation(Line(origin = {167, 63}, 
    points = {{-17, 15}, {3, 15}, {3, -1}, {17, -1}, {17, -15}}, 
    color = {0, 0, 255}));
  connect(illumination2.SolarAngle, sPPVArray2.SolarAngle) 
    annotation(Line(origin = {83.0004, 162}, 
    points = {{13.9996, -75}, {44.9996, -75}, {44.9996, -73.6}}, 
    color = {0, 0, 127}));
  connect(illumination2.ShieldRate, sPPVArray2.ShieldRate) 
    annotation(Line(origin = {81.0004, 156.9997}, 
    points = {{15.9996, -74.9997}, {46.9996, -74.9997}}, 
    color = {0, 0, 127}));
  connect(illumination2.Solar, sPPVArray2.Solar) 
    annotation(Line(origin = {78.0004, 150.9997}, 
    points = {{18.9996, -73.9997}, {49.9996, -73.9997}, {49.9996, -74.9997}}, 
    color = {0, 0, 127}));
  connect(temperatureSource3.port, sPPVArray2.heatPort) 
    annotation(Line(origin = {83.0004, 136.9997}, 
    points = {{12.9996, -98.9997}, {56.9996, -98.9997}, {56.9996, -64.9997}}, 
    color = {191, 0, 0}));
  connect(illumination2.SolarInput, const2.y) 
    annotation(Line(origin = {63.0004, 77}, 
    points = {{10.9996, 0}, {-2.0004, 0}}, 
    color = {0, 0, 127}));
  connect(Io3.n, rampVoltage3.p) 
    annotation(Line(origin = {210.22, -4.3305}, 
    points = {{-25.5464, 3.9701}, {-18.351, 3.9701}, {-18.351, -6.0804}}, 
    color = {0, 0, 255}));
  connect(Vo3.p, rampVoltage3.p) 
    annotation(Line(origin = {231.22, -9.3305}, 
    points = {{-16.0942, -3.18375}, {-16.0942, 9}, {-39.351, 9}, {-39.351, -1.0804}}, 
    color = {0, 0, 255}));
  connect(Vo3.n, ground4.p) 
    annotation(Line(origin = {208.22, -39.3305}, 
    points = {{6.9058, 15.79055}, {6.9058, 3}, {-24.22, 3}, {-24.22, -10.6695}}, 
    color = {0, 0, 255}));
  connect(rampVoltage3.n, ground4.p) 
    annotation(Line(origin = {195.22, -39.3305}, 
    points = {{-3.351, 13.6872}, {-3.351, 3}, {-11.22, 3}, {-11.22, -10.6695}}, 
    color = {0, 0, 255}));
  connect(Io3.i, product4.u1) 
    annotation(Line(origin = {224.22, 10.67}, 
    points = {{-44.883, -5.160107}, {11.6521, -5.160107}, {11.6521, -4.41499}}, 
    color = {0, 0, 127}));
  connect(Vo3.v, product4.u2) 
    annotation(Line(origin = {251.22, -9.3305}, 
    points = {{-30.0301, -8.6966}, {-30.0301, 8.97009}, {-15.3479, 8.97009}}, 
    color = {0, 0, 127}));
  connect(sPPVArray3.pin_p, Io3.p) 
    annotation(Line(origin = {162, -6}, 
    points = {{-12, -6}, {-2, -6}, {-2, 5.6396}, {12.0004, 5.6396}}, 
    color = {0, 0, 255}));
  connect(sPPVArray3.pin_n, ground4.p) 
    annotation(Line(origin = {167, -35}, 
    points = {{-17, 15}, {3, 15}, {3, -1}, {17, -1}, {17, -15}}, 
    color = {0, 0, 255}));
  connect(illumination3.SolarAngle, sPPVArray3.SolarAngle) 
    annotation(Line(origin = {83.0004, 64}, 
    points = {{13.9996, -75}, {44.9996, -75}, {44.9996, -73.6}}, 
    color = {0, 0, 127}));
  connect(illumination3.ShieldRate, sPPVArray3.ShieldRate) 
    annotation(Line(origin = {81.0004, 59}, 
    points = {{15.9996, -75}, {46.9996, -75}}, 
    color = {0, 0, 127}));
  connect(illumination3.Solar, sPPVArray3.Solar) 
    annotation(Line(origin = {78.0004, 53}, 
    points = {{18.9996, -74}, {49.9996, -74}, {49.9996, -75}}, 
    color = {0, 0, 127}));
  connect(temperatureSource4.port, sPPVArray3.heatPort) 
    annotation(Line(origin = {83.0004, 39}, 
    points = {{12.9996, -99}, {56.9996, -99}, {56.9996, -65}}, 
    color = {191, 0, 0}));
  connect(illumination3.SolarInput, const3.y) 
    annotation(Line(origin = {63.0004, -21}, 
    points = {{10.9996, 0}, {-2.0004, 0}}, 
    color = {0, 0, 127}));
  connect(illumination4.SolarAngle, sPPVArray4.SolarAngle) 
    annotation(Line(origin = {83.0004, -13.6433}, 
    points = {{13.9996, -75}, {44.9996, -75}, {44.9996, -73.6}}, 
    color = {0, 0, 127}));
  connect(illumination4.ShieldRate, sPPVArray4.ShieldRate) 
    annotation(Line(origin = {81.0004, -18.6433}, 
    points = {{15.9996, -75}, {46.9996, -75}}, 
    color = {0, 0, 127}));
  connect(illumination4.Solar, sPPVArray4.Solar) 
    annotation(Line(origin = {78.0004, -24.6433}, 
    points = {{18.9996, -74}, {49.9996, -74}, {49.9996, -75}}, 
    color = {0, 0, 127}));
  connect(temperatureSource5.port, sPPVArray4.heatPort) 
    annotation(Line(origin = {83.0004, -38.6433}, 
    points = {{12.9996, -99}, {56.9996, -99}, {56.9996, -65}}, 
    color = {191, 0, 0}));
  connect(illumination4.SolarInput, const4.y) 
    annotation(Line(origin = {63.0004, -98.6433}, 
    points = {{10.9996, 0}, {-2.0004, 0}}, 
    color = {0, 0, 127}));
  connect(sPPVArray4.pin_p, Io3.p) 
    annotation(Line(origin = {161.869, -44.6433}, 
    points = {{-11.869, -45}, {-2, -45}, {-2, 44.2829}, {12.1314, 44.2829}}, 
    color = {0, 0, 255}));
  connect(sPPVArray3.pin_n, sPPVArray4.pin_n) 
    annotation(Line(origin = {149.869, -58.6433}, 
    points = {{0.131, 38.6433}, {20, 38.6433}, {20, -39}, {0.131, -39}}, 
    color = {0, 0, 255}));
  connect(temperatureSource2.port, sPPVArray1.heatPort) 
    annotation(Line(origin = {-116, -76.6433}, 
    points = {{-22, -17}, {22, -17}, {22, 17}}, 
    color = {191, 0, 0}));
  connect(Io4.n, rampVoltage4.p) 
    annotation(Line(origin = {-249.7801, 21.9245}, 
    points = {{-25.5463, 3.9705}, {-18.3509, 3.9705}, {-18.3509, -6.0803}}, 
    color = {0, 0, 255}));
  connect(Vo4.p, rampVoltage4.p) 
    annotation(Line(origin = {-228.78, 16.9245}, 
    points = {{-16.0941, -3.18365}, {-16.0941, 9}, {-39.3509, 9}, {-39.3509, -1.0803}}, 
    color = {0, 0, 255}));
  connect(Vo4.n, ground5.p) 
    annotation(Line(origin = {-251.7801, -13.0755}, 
    points = {{6.9059, 15.79065}, {6.9059, 3}, {-24.2195, 3}, {-24.2195, -10.6695}}, 
    color = {0, 0, 255}));
  connect(rampVoltage4.n, ground5.p) 
    annotation(Line(origin = {-264.7801, -13.0755}, 
    points = {{-3.3509, 13.6873}, {-3.3509, 3}, {-11.2195, 3}, {-11.2195, -10.6695}}, 
    color = {0, 0, 255}));
  connect(Io4.i, product5.u1) 
    annotation(Line(origin = {-235.78, 36.92501}, 
    points = {{-44.8829, -5.15971}, {11.6522, -5.15971}, {11.6522, -4.41529}}, 
    color = {0, 0, 127}));
  connect(Vo4.v, product5.u2) 
    annotation(Line(origin = {-208.78, 16.9245}, 
    points = {{-30.03, -8.6965}, {-28, -8.6965}, {-28, 8.96979}, {-15.3478, 8.96979}}, 
    color = {0, 0, 127}));
  connect(sPPVArray5.pin_p, Io4.p) 
    annotation(Line(origin = {-298, 20.25501}, 
    points = {{-12, -6}, {-2, -6}, {-2, 5.64}, {12.0004, 5.64}}, 
    color = {0, 0, 255}));
  connect(sPPVArray5.pin_n, ground5.p) 
    annotation(Line(origin = {-293, -8.74499}, 
    points = {{-17, 15}, {3, 15}, {3, -1}, {17.0004, -1}, {17.0004, -15}}, 
    color = {0, 0, 255}));
  connect(illumination5.SolarAngle, sPPVArray5.SolarAngle) 
    annotation(Line(origin = {-377, 90.25501}, 
    points = {{14, -75}, {45, -75}, {45, -73.6}}, 
    color = {0, 0, 127}));
  connect(illumination5.ShieldRate, sPPVArray5.ShieldRate) 
    annotation(Line(origin = {-379, 85.2547}, 
    points = {{16, -74.9997}, {47, -74.9997}}, 
    color = {0, 0, 127}));
  connect(illumination5.Solar, sPPVArray5.Solar) 
    annotation(Line(origin = {-382, 79.2547}, 
    points = {{19, -73.9997}, {50, -73.9997}, {50, -74.9997}}, 
    color = {0, 0, 127}));
  connect(temperatureSource6.port, sPPVArray5.heatPort) 
    annotation(Line(origin = {-377, 65.2547}, 
    points = {{13, -98.9997}, {57, -98.9997}, {57, -64.9997}}, 
    color = {191, 0, 0}));
  connect(illumination5.SolarInput, const5.y) 
    annotation(Line(origin = {-397, 5.25501}, 
    points = {{11, 0}, {-2, 0}}, 
    color = {0, 0, 127}));
end PVFault;