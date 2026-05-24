model PVMPPTAveraged "光伏发电最大功率点跟踪-平均值"
  annotation(Documentation(link = "modelica://TYPhotovoltaicPower/Resources/Examples/PVMPPTAveraged.html"), 
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
CreatePlot(id=1, x_display_unit="s", legend_layout=1, left_title_type=2, left_title="输出功率[W]", bottom_title_type=2, bottom_title="时间[s]", right_title_type=2, fix_time_range_value=0, zoom_x=(0, 5), zoom_y_l=(95000, 125000)), 
Plot(legend=["输出功率[W]"], y=["product1.y"], colors=["4278190335"]), 
CreatePlot(id=-1, x_display_unit="s", legend_layout=1, left_title_type=2, left_title="输出电压[V]", bottom_title_type=2, bottom_title="时间[s]", fix_time_range_value=0, sub_plot=(2, 2), zoom_x=(0, 5), zoom_y_l=(285, 325)), 
Plot(legend=["输出电压 [V]"], y=["product1.u1"], colors=["4278190335"]), 
CreatePlot(id=-1, x_display_unit="s", legend_layout=1, left_title_type=2, left_title="输出电流[A]", bottom_title_type=2, bottom_title="时间[s]", fix_time_range_value=0, sub_plot=(1, 2), zoom_x=(0, 5), zoom_y_l=(280, 440)), 
Plot(legend=["输出电流 [A]"], y=["product1.u2"], colors=["4278190335"]), 
CreatePlot(id=-1, x_display_unit="s", legend_layout=1, left_title_type=2, left_title="光照强度[W/m2]", bottom_title_type=2, bottom_title="时间[s]", right_title_type=2, fix_time_range_value=0, sub_plot=(2, 1), zoom_x=(0, 5), zoom_y_l=(950, 1250)), 
Plot(legend=["光照强度 [W/m2]"], y=["step.y"], colors=["4278190335"])})
})), Protection(access = Access.nonPackageDuplicate));
  //参数
  parameter Modelica.Units.SI.Time Ts = 1e-5 "采样周期";
  parameter Modelica.Units.SI.Frequency f_sample = 1 / Ts "采样频率";
  //实例化
  TYPhotovoltaicPower.Components.Capacitor capacitor(C = 0.01, v_c(start = 296)) 
    annotation(Placement(transformation(origin = {-3.3519, -9.63085}, 
    extent = {{-10, -10}, {10, 10}}, 
    rotation = 270)));
  Modelica.Electrical.Analog.Basic.Ground ground 
    annotation(Placement(transformation(origin = {123.0018, -46.8948}, 
    extent = {{-10, -10}, {10, 10}})));
  Modelica.Electrical.Analog.Basic.Resistor resistor2(R = 0.0001) 
    annotation(Placement(transformation(origin = {-3.6196, 18.5042}, 
    extent = {{-10, -10}, {10, 10}}, 
    rotation = 270)));
  Modelica.Electrical.Analog.Sensors.VoltageSensor voltageSensor 
    annotation(Placement(transformation(origin = {-58.375, -3.12955}, 
    extent = {{-10, -10}, {10, 10}}, 
    rotation = 270)));
  Modelica.Blocks.Math.Product product1 
    annotation(Placement(transformation(origin = {2.97292, 59.1052}, 
    extent = {{-10, -10}, {10, 10}})));
  TYPhotovoltaicPower.PowerConverters.Averaged.AveragedBoost boostConv 
    annotation(Placement(transformation(origin = {60, -24.8948}, 
    extent = {{-10, -10}, {10, 10}})));
  Modelica.Electrical.Analog.Sensors.CurrentSensor currentSensor1 
    annotation(Placement(transformation(origin = {-29.706, 36.3052}, 
    extent = {{-10, 10}, {10, -10}})));
  Modelica.Electrical.Analog.Sources.ConstantVoltage rampVoltage(V = 800) 
    annotation(Placement(transformation(origin = {123.0018, 2.44915}, 
    extent = {{-7.6162, -7.6162}, {7.6162, 7.6162}}, 
    rotation = 270)));
  TYPhotovoltaicPower.Sources.HeatSources.TemperatureSource temperatureSource1(n = 1, T = 298.15) 
    annotation(Placement(transformation(origin = {-136, -28.7309}, 
    extent = {{-10, -10}, {10, 10}})));
  TYPhotovoltaicPower.Generators.PVArray pVarray1(Np = 47, Ns = 10, Rsh0_user = 313.0553, Ncell_user = 60, Pmax_user = 213.15, Voc_user = 36.3, Vmp_user = 29, Isc_user = 7.84, Imp_user = 7.35, IL_ref_user = 7.8654, Rs0_user = 0.39381, Is_user = 2.9273e-10, N_user = 1, redeclare package SolarType = TYPhotovoltaicPower.Generators.Basics.SolarType.Solar_User) 
    annotation(Placement(transformation(origin = {-102, 1.87045}, 
    extent = {{-10, -10}, {10, 10}})));
  TYPhotovoltaicPower.Components.Inductor inductor(L = 0.0016) 
    annotation(Placement(transformation(origin = {22.4668, 36.3052}, 
    extent = {{-10, -10}, {10, 10}})));
  Modelica.Electrical.Analog.Basic.Capacitor capacitor1(C = 0.001, v(start = 800)) 
    annotation(Placement(transformation(origin = {98, 0.06535}, 
    extent = {{-10, -10}, {10, 10}}, 
    rotation = 270)));
  TYPhotovoltaicPower.Controllers.MPPT mPPT(f_sample = f_sample, MPPTSelect = "扰动观察法", deltaVref = 0.0001, Vrefmax = 363, Vrefinit = 296) 
    annotation(Placement(transformation(origin = {-3.6196, -72.8948}, 
    extent = {{-10, -10}, {10, 10}})));
  .TYPhotovoltaicPower.Controllers.VrefRegulator vrefRegulator(kind = "占空比", T = 20, k = 5 / 8) 
    annotation(Placement(transformation(origin = {36, -58}, 
    extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Sources.Step step(offset = 1000, startTime = 2.5, height = 200) 
    annotation(Placement(transformation(origin = {-136, 19.1052}, 
    extent = {{-10, -10}, {10, 10}})));
  annotation(Diagram(coordinateSystem(extent = {{-100, -100}, {100, 100}}, 
    grid = {2, 2})), experiment(Algorithm = InlineImplicitEuler, InlineIntegrator = true, InlineStepSize = true, IntegratorStep = 5e-05, Interval = 5e-05, StartTime = 0, StopTime = 5, Tolerance = 1e-08));

equation
  connect(resistor2.n, capacitor.p) 
    annotation(Line(origin = {-3.375, 4.30515}, 
    points = {{-0.2446, 4.199}, {-0.2446, -3.936}, {0.0231, -3.936}}, 
    color = {0, 0, 255}));
  connect(currentSensor1.n, resistor2.p) 
    annotation(Line(origin = {-18.375, 32.3052}, 
    points = {{-1.331, 4}, {14.7554, 4}, {14.7554, -3.801}}, 
    color = {0, 0, 255}));
  connect(resistor2.p, inductor.p) 
    annotation(Line(origin = {66.625, 7.30515}, 
    points = {{-70.2446, 21.199}, {-70.2446, 29}, {-54.1582, 29}}, 
    color = {0, 0, 255}));
  connect(voltageSensor.p, currentSensor1.p) 
    annotation(Line(origin = {-55.375, 21.3052}, 
    points = {{-3, -14.4347}, {-3, 15}, {15.669, 15}}, 
    color = {0, 0, 255}));
  connect(voltageSensor.n, capacitor.n) 
    annotation(Line(origin = {-30.375, -21.6948}, 
    points = {{-28, 8.5653}, {-28, -8}, {27.0231, -8}, {27.0231, 1.864}}, 
    color = {0, 0, 255}));
  connect(boostConv.nLoad, rampVoltage.n) 
    annotation(Line(origin = {174, -19.2948}, 
    points = {{-103.97, -9.48664}, {-50.9982, -9.48664}, {-50.9982, 14.1278}}, 
    color = {0, 0, 255}));
  connect(temperatureSource1.port[1], pVarray1.heatPort) 
    annotation(Line(origin = {-152.91, -25.3821}, 
    points = {{26.91, -3.34873}, {50.91, -3.34873}, {50.91, 17.2526}}, 
    color = {191, 0, 0}));
  connect(pVarray1.p, currentSensor1.p) 
    annotation(Line(origin = {-83, 21.1052}, 
    points = {{-9, -14.2347}, {-3, -14.2347}, {-3, 15.2}, {43.294, 15.2}}, 
    color = {0, 0, 255}));
  connect(pVarray1.n, voltageSensor.n) 
    annotation(Line(origin = {-92, -7.89485}, 
    points = {{0, 4.7653}, {6, 4.7653}, {6, -21}, {33.625, -21}, {33.625, -5.2347}}, 
    color = {0, 0, 255}));
  connect(inductor.n, boostConv.pSupply) 
    annotation(Line(origin = {115, 7.10515}, 
    points = {{-82.3332, 29.2}, {-73, 29.2}, {-73, -27.9902}, {-64.90253, -27.9902}}, 
    color = {0, 0, 255}));
  connect(capacitor1.p, boostConv.pLoad) 
    annotation(Line(origin = {155, -0.89485}, 
    points = {{-57, 10.9602}, {-57, 36}, {-79, 36}, {-79, -19.98478}, {-84.93, -19.98478}}, 
    color = {0, 0, 255}));
  connect(capacitor1.n, boostConv.nLoad) 
    annotation(Line(origin = {155, -24.8948}, 
    points = {{-57, 14.9602}, {-57, -3.88664}, {-84.97, -3.88664}}, 
    color = {0, 0, 255}));
  connect(capacitor.n, boostConv.nSupply) 
    annotation(Line(origin = {83, -30.8948}, 
    points = {{-86.3519, 11.064}, {-86.3519, 2.16397}, {-32.91118, 2.16397}}, 
    color = {0, 0, 255}));
  connect(ground.p, rampVoltage.n) 
    annotation(Line(origin = {217, -46.8948}, 
    points = {{-93.9982, 10}, {-93.9982, 41.7278}}, 
    color = {0, 0, 255}));
  connect(mPPT.Vref, vrefRegulator.Vref) 
    annotation(Line(origin = {34.9729, -72.41815}, 
    points = {{-27.5925, -0.4767}, {-20.9729, -0.4767}, {-20.9729, 9.41815}, {-10.7729, 9.41815}}, 
    color = {0, 0, 127}));
  connect(rampVoltage.p, boostConv.pLoad) 
    annotation(Line(origin = {175, 18.1052}, 
    points = {{-51.9982, -8.0398}, {-51.9982, 17}, {-99, 17}, {-99, -38.98478}, {-104.93, -38.98478}}, 
    color = {0, 0, 255}));
  connect(currentSensor1.i, product1.u2) 
    annotation(Line(origin = {-19, 50.1052}, 
    points = {{-10.706, -2.8}, {-10.706, 3}, {9.97292, 3}}, 
    color = {0, 0, 127}));
  connect(voltageSensor.v, product1.u1) 
    annotation(Line(origin = {-39, 31.1052}, 
    points = {{-30.375, -34.2347}, {-35, -34.2347}, {-35, 34}, {29.9729, 34}}, 
    color = {0, 0, 127}));
  connect(vrefRegulator.y, boostConv.D) 
    annotation(Line(origin = {54, -53.8948}, 
    points = {{-6.2, -4.10515}, {6, -4.10515}, {6, 17}}, 
    color = {0, 0, 127}));
  connect(voltageSensor.v, vrefRegulator.V) 
    annotation(Line(origin = {-25, -34.8948}, 
    points = {{-44.375, 31.7653}, {-49, 31.7653}, {-49, -18.1052}, {49.2, -18.1052}}, 
    color = {0, 0, 127}));
  connect(voltageSensor.v, mPPT.V) 
    annotation(Line(origin = {-44, -46.8948}, 
    points = {{-25.375, 43.7653}, {-30, 43.7653}, {-30, -22}, {28.3804, -22}}, 
    color = {0, 0, 127}));
  connect(currentSensor1.i, mPPT.I) 
    annotation(Line(origin = {-46, -22.8948}, 
    points = {{16.294, 70.2}, {16.294, 76}, {-32, 76}, {-32, -54}, {30.3804, -54}}, 
    color = {0, 0, 127}));
  connect(step.y, pVarray1.G) 
    annotation(Line(origin = {-117, 15.1052}, 
    points = {{-8, 4}, {8.63379, 4}, {8.63379, -3.2347}}, 
    color = {0, 0, 127}));
end PVMPPTAveraged;