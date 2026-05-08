model PVMPPTSwitch "光伏发电最大功率点跟踪-开关"
  annotation(Documentation(link = "modelica://TYPhotovoltaicPower/Resources/Examples/PVMPPTSwitch.html"), 
    Icon(coordinateSystem(extent = {{-100, -100}, {100, 100}}, 
    grid = {2, 2}), graphics = {Polygon(origin = {-7.10543e-15, 33}, 
    lineColor = {16, 99, 16}, 
    fillColor = {16, 99, 16}, 
    fillPattern = FillPattern.Solid, 
    points = {{-64, 1}, {0, 37}, {64, 1}, {0, -37}}), Line(origin = {0, -12}, 
    points = {{-62, 18}, {0, -18}, {62, 18}}, 
    color = {16, 99, 16}, 
    thickness = 5), Line(origin = {7.10543e-15, -40}, 
    points = {{-62, 18}, {0, -18}, {62, 18}}, 
    color = {16, 99, 16}, 
    thickness = 5)}), __MWORKS(ContinueSimConfig(SaveContinueFile = "false", SaveBeforeStop = "false", NumberBeforeStop = 1, FixedContinueInterval = "false", ContinueIntervalLength = 2.5, ContinueTimeVector),ResultViewerManager(resultViewers={
ResultViewer(name="1", executeTrigger=executeTrigger.SimulationFinished, commands={
CreatePlot(id=1, x_display_unit="s", legend_layout=1, left_title_type=2, left_title="输出功率[W]", bottom_title_type=2, bottom_title="时间[s]", right_title_type=2, fix_time_range_value=0, zoom_x=(0, 5), zoom_y_l=(90000, 130000)), 
Plot(legend=["输出功率[W]"], y=["product1.y"], colors=["4278190335"]), 
CreatePlot(id=-1, x_display_unit="s", legend_layout=1, left_title_type=2, left_title="光照强度[W/m2]", bottom_title_type=2, bottom_title="时间[s]", right_title_type=2, fix_time_range_value=0, sub_plot=(2, 1), zoom_x=(0, 5), zoom_y_l=(950, 1250)), 
Plot(legend=["光照强度 [W/m2]"], y=["step.y"], colors=["4278190335"]), 
CreatePlot(id=-1, x_display_unit="s", legend_layout=1, left_title_type=2, left_title="输出电压[V]", bottom_title_type=2, bottom_title="sahijian/s", fix_time_range_value=0, sub_plot=(2, 2), zoom_x=(0, 5), zoom_y_l=(285, 325)), 
Plot(legend=["输出电压[V]"], y=["product1.u1"], colors=["4278190335"]), 
CreatePlot(id=-1, x_display_unit="s", legend_layout=1, left_title_type=2, left_title="输出电流[A]", bottom_title_type=2, bottom_title="时间/s", fix_time_range_value=0, sub_plot=(1, 2), zoom_x=(0, 5), zoom_y_l=(280, 440)), 
Plot(legend=["输出电流 [A]"], y=["product1.u2"], colors=["4278190335"])})
})), Protection(access = Access.nonPackageDuplicate));
  //参数
  parameter Modelica.Units.SI.Time Ts = 1e-5 "采样周期";
  parameter Modelica.Units.SI.Frequency f_sample = 1 / Ts "采样频率";
  //实例化
  Modelica.Electrical.Analog.Basic.Ground ground 
    annotation(Placement(transformation(origin = {138.116, -40}, 
    extent = {{-10, -10}, {10, 10}})));
  Modelica.Electrical.Analog.Basic.Resistor resistor2(R = 0.001) 
    annotation(Placement(transformation(origin = {-11.1196, 23.399}, 
    extent = {{-10, -10}, {10, 10}}, 
    rotation = 270)));
  Modelica.Blocks.Discrete.UnitDelay unitDelay(samplePeriod = Ts) 
    annotation(Placement(transformation(origin = {-50.6358, -49.8}, 
    extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Discrete.UnitDelay unitDelay1(samplePeriod = Ts) 
    annotation(Placement(transformation(origin = {-50.6358, -83.0923}, 
    extent = {{-10, -10}, {10, 10}})));
  Modelica.Electrical.Analog.Sensors.VoltageSensor voltageSensor 
    annotation(Placement(transformation(origin = {-65.875, 1.7653}, 
    extent = {{-10, -10}, {10, 10}}, 
    rotation = 270)));
  Modelica.Blocks.Math.Product product1 
    annotation(Placement(transformation(origin = {-7.3125, 66}, 
    extent = {{-10, -10}, {10, 10}})));
  TYPhotovoltaicPower.Controllers.MPPT mPPT(f_sample = f_sample, MPPTSelect = "扰动观察法", deltaVref = 0.0001, Vrefmax = 363, Vrefinit = 296) 
    annotation(Placement(transformation(origin = {-6.0679, -69.0923}, 
    extent = {{-10, -10}, {10, 10}})));
  .TYPhotovoltaicPower.Controllers.VrefRegulator vrefRegulator(k = 10, rising = 1e-5, width = 0, falling = 1e-5, period = 2e-5) 
    annotation(Placement(transformation(origin = {38.5, -54.8}, 
    extent = {{-10, -10}, {10, 10}})));
  TYPhotovoltaicPower.PowerConverters.IdealSwitching.Boost boostConv 
    annotation(Placement(transformation(origin = {62, -20}, 
    extent = {{-10, -10}, {10, 10}})));
  Modelica.Electrical.Analog.Sensors.CurrentSensor currentSensor1 
    annotation(Placement(transformation(origin = {-37.206, 41.2}, 
    extent = {{-10, 10}, {10, -10}})));
  Modelica.Electrical.Analog.Sources.ConstantVoltage rampVoltage(V = 800) 
    annotation(Placement(transformation(origin = {138.116, 4}, 
    extent = {{-7.6162, -7.6162}, {7.6162, 7.6162}}, 
    rotation = 270)));
  TYPhotovoltaicPower.Sources.HeatSources.TemperatureSource temperatureSource1(n = 1, T = 298.15) 
    annotation(Placement(transformation(origin = {-145.5, -23.947}, 
    extent = {{-10, -10}, {10, 10}})));
  TYPhotovoltaicPower.Generators.PVArray pVarray1(Np = 47, Ns = 10, Rsh0_user = 313.0553, Ncell_user = 60, Pmax_user = 213.15, Voc_user = 36.3, Vmp_user = 29, Isc_user = 7.84, Imp_user = 7.35, IL_ref_user = 7.8654, Rs0_user = 0.39381, Is_user = 2.9273e-10, N_user = 1, redeclare package SolarType = TYPhotovoltaicPower.Generators.Basics.SolarType.Solar_User) 
    annotation(Placement(transformation(origin = {-120.63, 6.7653}, 
    extent = {{-10, -10}, {10, 10}})));
  TYPhotovoltaicPower.Components.Inductor inductor(L = 0.0016) 
    annotation(Placement(transformation(origin = {14.9668, 41.2}, 
    extent = {{-10, -10}, {10, 10}})));
  Modelica.Electrical.Analog.Basic.Capacitor capacitor1(C = 0.001, v(start = 800)) 
    annotation(Placement(transformation(origin = {101.671, 4}, 
    extent = {{-10, -10}, {10, 10}}, 
    rotation = 270)));
  TYPhotovoltaicPower.Components.Capacitor capacitor(C = 0.01, v_c(start = 296)) 
    annotation(Placement(transformation(origin = {-11.1196, -6}, 
    extent = {{-10, -10}, {10, 10}}, 
    rotation = 270)));
  Modelica.Blocks.Sources.Step step(offset = 1000, startTime = 2.5, height = 200) 
    annotation(Placement(transformation(origin = {-145.5, 41.2}, 
    extent = {{-10, -10}, {10, 10}})));
  annotation(Diagram(coordinateSystem(extent = {{-100, -100}, {100, 100}}, 
    grid = {2, 2})), experiment(Algorithm = InlineImplicitEuler, InlineIntegrator = true, InlineStepSize = true, IntegratorStep = 5e-05, Interval = 5e-05, StartTime = 0, StopTime = 5, Tolerance = 1e-08));
equation
  connect(unitDelay.y, mPPT.V) 
    annotation(Line(origin = {-46.2608, -62.0923}, 
    points = {{6.625, 12.2923}, {16, 12.2923}, {16, -3}, {28.1929, -3}}, 
    color = {0, 0, 127}));
  connect(unitDelay1.y, mPPT.I) 
    annotation(Line(origin = {-46.2608, -97.0923}, 
    points = {{6.625, 14}, {16, 14}, {16, 24}, {28.1929, 24}}, 
    color = {0, 0, 127}));
  connect(mPPT.Vref, vrefRegulator.Vref) 
    annotation(Line(origin = {33.7392, -69.0923}, 
    points = {{-28.8071, 0}, {-20.1875, 0}, {-20.1875, 9.2923}, {-7.0392, 9.2923}}, 
    color = {0, 0, 127}));
  connect(unitDelay.y, vrefRegulator.V) 
    annotation(Line(origin = {-3.2608, -50.0923}, 
    points = {{-36.375, 0.2923}, {29.9608, 0.2923}}, 
    color = {0, 0, 127}), __MWORKS(BlockSystem(NamedSignal)));
  connect(currentSensor1.n, resistor2.p) 
    annotation(Line(origin = {-25.875, 37.2}, 
    points = {{-1.331, 4}, {14.7554, 4}, {14.7554, -3.801}}, 
    color = {0, 0, 255}));
  connect(voltageSensor.p, currentSensor1.p) 
    annotation(Line(origin = {-62.875, 26.2}, 
    points = {{-3, -14.4347}, {-3, 15}, {15.669, 15}}, 
    color = {0, 0, 255}));
  connect(ground.p, rampVoltage.n) 
    annotation(Line(origin = {150.6708, -24.4}, 
    points = {{-12.5546, -5.6}, {-12.5546, 20.7838}}, 
    color = {0, 0, 255}));
  connect(boostConv.pLoad, rampVoltage.p) 
    annotation(Line(origin = {165.287, 14.4}, 
    points = {{-93.217, -30.40814}, {-82.787, -30.40814}, {-82.787, 27.6}, {-27.1708, 27.6}, {-27.1708, -2.7838}}, 
    color = {0, 0, 255}));
  connect(boostConv.nLoad, rampVoltage.n) 
    annotation(Line(origin = {165.287, -13.6}, 
    points = {{-93.257, -10.31}, {-27.1708, -10.31}, {-27.1708, 9.9838}}, 
    color = {0, 0, 255}));
  connect(temperatureSource1.port[1], pVarray1.heatPort) 
    annotation(Line(origin = {-160.41, -20.4873}, 
    points = {{24.91, -3.4597}, {39.7796, -3.4597}, {39.7796, 17.2526}}, 
    color = {191, 0, 0}));
  connect(pVarray1.p, currentSensor1.p) 
    annotation(Line(origin = {-90.5, 26}, 
    points = {{-20.1304, -14.2347}, {-13, -14.2347}, {-13, 15.2}, {43.294, 15.2}}, 
    color = {0, 0, 255}));
  connect(pVarray1.n, voltageSensor.n) 
    annotation(Line(origin = {-99.5, -3}, 
    points = {{-11.1304, 4.7653}, {-6, 4.7653}, {-6, -21}, {33.625, -21}, {33.625, -5.2347}}, 
    color = {0, 0, 255}));
  connect(resistor2.p, inductor.p) 
    annotation(Line(origin = {22.5, 37}, 
    points = {{-33.6196, -3.601}, {-33.6196, 4.2}, {-17.5332, 4.2}}, 
    color = {0, 0, 255}));
  connect(inductor.n, boostConv.pSupply) 
    annotation(Line(origin = {76.287, 12.8}, 
    points = {{-51.1202, 28.4}, {-39.787, 28.4}, {-39.787, -28.8136}, {-24.1895, -28.8136}}, 
    color = {0, 0, 255}));
  connect(capacitor1.n, rampVoltage.n) 
    annotation(Line(origin = {126.671, -14}, 
    points = {{-25, 8}, {-25, -10}, {11.4454, -10}, {11.4454, 10.3838}}, 
    color = {0, 0, 255}));
  connect(capacitor1.p, rampVoltage.p) 
    annotation(Line(origin = {126.671, 28}, 
    points = {{-25, -14}, {-25, 14}, {11.4454, 14}, {11.4454, -16.3838}}, 
    color = {0, 0, 255}));
  connect(capacitor.p, resistor2.n) 
    annotation(Line(origin = {-11.5, 9}, 
    points = {{0.3804, -5}, {0.3804, 4.399}}, 
    color = {0, 0, 255}));
  connect(voltageSensor.n, capacitor.n) 
    annotation(Line(origin = {-38.5, -16}, 
    points = {{-27.375, 7.7653}, {-27.375, -8}, {27.3804, -8}, {27.3804, -0.2}}, 
    color = {0, 0, 255}));
  connect(capacitor.n, boostConv.nSupply) 
    annotation(Line(origin = {59.5, -20}, 
    points = {{-70.6196, 3.8}, {-70.6196, -3.947}, {-7.528, -3.947}}, 
    color = {0, 0, 255}));
  connect(step.y, pVarray1.G) 
    annotation(Line(origin = {-130.5, 29}, 
    points = {{-4, 12.2}, {3.50339, 12.2}, {3.50339, -12.2347}}, 
    color = {0, 0, 127}));
  connect(vrefRegulator.y1, boostConv.G) 
    annotation(Line(origin = {54.5, -53}, 
    points = {{-4.2, -1.8}, {7.5, -1.8}, {7.5, 20.966}}, 
    color = {255, 0, 255}));
  connect(currentSensor1.i, product1.u2) 
    annotation(Line(origin = {-23.5, 56}, 
    points = {{-13.706, -3.8}, {-13.706, 4}, {4.1875, 4}}, 
    color = {0, 0, 127}));
  connect(voltageSensor.v, product1.u1) 
    annotation(Line(origin = {-46.5, 37}, 
    points = {{-30.375, -35.2347}, {-37, -35.2347}, {-37, 35}, {27.1875, 35}}, 
    color = {0, 0, 127}));
  connect(voltageSensor.v, unitDelay.u) 
    annotation(Line(origin = {-75.5, -33}, 
    points = {{-1.375, 34.7653}, {-8, 34.7653}, {-8, -16.8}, {12.8642, -16.8}}, 
    color = {0, 0, 127}));
  connect(currentSensor1.i, unitDelay1.u) 
    annotation(Line(origin = {-63.5, -35}, 
    points = {{26.294, 87.2}, {26.294, 95}, {-26, 95}, {-26, -48.0923}, {0.8642, -48.0923}}, 
    color = {0, 0, 127}));
end PVMPPTSwitch;