model TwoLevelGridConnectedAverage "光伏并网发电系统"
  annotation(Documentation(link = "modelica://TYPhotovoltaicPower/Resources/Examples/TwoLevelGridConnectedAverage.html"), 
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
    thickness = 5)}), Diagram(coordinateSystem(extent = {{-100, -100}, {100, 100}}, 
    grid = {2, 2}), graphics = {Rectangle(origin = {-114.867, -51.6829}, 
    lineColor = {0, 0, 0}, 
    fillColor = {255, 255, 255}, 
    pattern = LinePattern.Dash, 
    extent = {{-84.5121, 31.112}, {84.5121, -31.112}}), Text(origin = {-73.0678, -75.75}, 
    lineColor = {0, 0, 128}, 
    extent = {{-36.5863, 7.04456}, {36.5863, -7.04456}}, 
    textString = "MPPT控制", 
    textStyle = {TextStyle.Italic}, 
    textColor = {0, 0, 128}), Rectangle(origin = {99.5149, -52.8801}, 
    lineColor = {0, 0, 0}, 
    fillColor = {255, 255, 255}, 
    pattern = LinePattern.Dash, 
    extent = {{-99.5939, 36.8694}, {99.5939, -36.8694}}), Text(origin = {31.9237, -82.705}, 
    lineColor = {0, 0, 128}, 
    extent = {{-36.5863, 7.04456}, {36.5863, -7.04456}}, 
    textString = "并网控制", 
    textStyle = {TextStyle.Italic}, 
    textColor = {0, 0, 128}), Rectangle(origin = {-12.4991, 59.6377}, 
    lineColor = {0, 0, 0}, 
    fillColor = {255, 255, 255}, 
    pattern = LinePattern.Dash, 
    lineThickness = 0.5, 
    extent = {{-250.424, 63.6823}, {250.424, -63.6823}}), Rectangle(origin = {-12.53, -62.0806}, 
    fillColor = {255, 255, 255}, 
    pattern = LinePattern.Dash, 
    lineThickness = 0.5, 
    extent = {{-250.424, 52.5394}, {250.424, -52.5394}}), Text(origin = {229.793, 55.4417}, 
    rotation = -90, 
    lineColor = {0, 0, 128}, 
    extent = {{-37.3814, -6.83117}, {37.3814, 6.83117}}, 
    textString = "光伏系统", 
    textStyle = {TextStyle.None}, 
    textColor = {0, 0, 128}), Text(origin = {230.444, -62.0806}, 
    rotation = -90, 
    lineColor = {0, 0, 128}, 
    extent = {{50.0041, -7.4813}, {-50.0041, 7.4813}}, 
    textString = "控制系统", 
    textStyle = {TextStyle.None}, 
    textColor = {0, 0, 128})}), experiment(Algorithm = InlineImplicitEuler, InlineIntegrator = true, InlineStepSize = false, Interval = 5e-05, StartTime = 0, StopTime = 1, Tolerance = 1e-08, IntegratorStep = 5e-05), __MWORKS(ContinueSimConfig(SaveContinueFile = "false", SaveBeforeStop = "false", NumberBeforeStop = 1, FixedContinueInterval = "false", ContinueIntervalLength = 0.5, ContinueTimeVector),ResultViewerManager(resultViewers={
ResultViewer(name="1", executeTrigger=executeTrigger.SimulationFinished, commands={
CreatePlot(id=1, x_display_unit="s", legend_layout=1, left_title_type=2, left_title="输出电压[V]", bottom_title_type=2, bottom_title="时间[s]", right_title_type=2, fix_time_range_value=0, zoom_x=(0, 1), zoom_y_l=(285, 315)), 
Plot(legend=["输出电压 [V]"], y=["voltageSensor.v"], colors=["4278190335"]), 
CreatePlot(id=-1, x_display_unit="s", legend_layout=1, left_title_type=2, left_title="功率[W]", bottom_title_type=2, bottom_title="时间[s]", fix_time_range_value=0, sub_plot=(2, 1), zoom_x=(0, 1), zoom_y_l=(92000, 108000)), 
Plot(legend=["最大输出功率 [W]", "实际输出功率[W]"], y=["pVarray1.Power_max", "product1.y"], colors=["4278190335", "4294901760"]), 
CreatePlot(id=-1, x_display_unit="s", legend_layout=1, left_title_type=2, left_title="输出电压[V]", bottom_title_type=2, bottom_title="时间[s]", fix_time_range_value=0, sub_plot=(3, 1), zoom_x=(0, 1), zoom_y_l=(750, 1050)), 
Plot(legend=["Boost升压斩波输出电压[V]"], y=["voltageSensor2.v"], colors=["4278190335"]), 
CreatePlot(id=2, x_display_unit="s", legend_layout=1, left_title_type=2, left_title="并网电压[V]", bottom_title_type=2, bottom_title="时间[s]", right_title_type=2, fix_time_range_value=0, zoom_x=(0, 1), zoom_y_l=(-400, 400)), 
Plot(legend=["A相电压[V]", "B相电压[V]", "C相电压[V]"], y=["threePhaseBridgeInverter.positivePlug.pin[1].v", "threePhaseBridgeInverter.positivePlug.pin[2].v", "threePhaseBridgeInverter.positivePlug.pin[3].v"], colors=["4278190335", "4294901760", "4278222848"]), 
CreatePlot(id=-1, x_display_unit="s", legend_layout=1, left_title_type=2, left_title="并网电流[A]", bottom_title_type=2, bottom_title="时间[s]", right_title_type=2, fix_time_range_value=0, sub_plot=(2, 1), zoom_x=(0, 1), zoom_y_l=(-400, 300)), 
Plot(legend=["A相电流[A]", "B相电流[A]", "C相电流[A]"], y=["threePhaseBridgeInverter.positivePlug.pin[1].i", "threePhaseBridgeInverter.positivePlug.pin[2].i", "threePhaseBridgeInverter.positivePlug.pin[3].i"], colors=["4278190335", "4294901760", "4278222848"])})
})), Protection(access = Access.nonPackageDuplicate));
  //参数
  parameter Modelica.Units.SI.Time Ts = 1e-5 "采样周期";
  parameter Modelica.Units.SI.Frequency f_sample = 1 / Ts "采样频率";
  //实例化
  TYPhotovoltaicPower.Components.Capacitor capacitor(C = 0.01, v_c(start = 290)) 
    annotation(Placement(transformation(origin = {-106.5584, 36.61125}, 
    extent = {{-10, -10}, {10, 10}}, 
    rotation = 270)));
  Modelica.Electrical.Analog.Basic.Resistor resistor2(R = 0.0001) 
    annotation(Placement(transformation(origin = {-106.8261, 64.7463}, 
    extent = {{-10, -10}, {10, 10}}, 
    rotation = 270)));
  Modelica.Electrical.Analog.Sensors.VoltageSensor voltageSensor 
    annotation(Placement(transformation(origin = {-161.5815, 43.1126}, 
    extent = {{-10, -10}, {10, 10}}, 
    rotation = 270)));
  Modelica.Blocks.Math.Product product1 
    annotation(Placement(transformation(origin = {-106.5584, 103.98}, 
    extent = {{-10, -10}, {10, 10}})));
  TYPhotovoltaicPower.PowerConverters.Averaged.AveragedBoost boostConv 
    annotation(Placement(transformation(origin = {-46.4815, 11.7052}, 
    extent = {{-10, -10}, {10, 10}})));
  Modelica.Electrical.Analog.Sensors.CurrentSensor currentSensor1 
    annotation(Placement(transformation(origin = {-132.9125, 82.5473}, 
    extent = {{-10, 10}, {10, -10}})));
  TYPhotovoltaicPower.Sources.HeatSources.TemperatureSource temperatureSource1(n = 1, T = 298.15) 
    annotation(Placement(transformation(origin = {-246.08, 15.715}, 
    extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Sources.Constant step(k = 1000) 
    annotation(Placement(transformation(origin = {-246.08, 73.74}, 
    extent = {{-10, -10}, {10, 10}})));
  TYPhotovoltaicPower.Generators.PVArray pVarray1(Np=47, Ns=10, Rsh0_user=313.3991, Ncell_user=60, Pmax_user=213.15, Voc_user=36.3, Vmp_user=29, Isc_user=7.84, Imp_user=7.35, IL_ref_user=7.8649, Rs0_user=0.39383, Is_user=2.9259e-10, N_user=0.98117, redeclare package SolarType = TYPhotovoltaicPower.Generators.Basics.SolarType.Solar_User) 
    annotation(Placement(transformation(origin = {-216.337, 48.1126}, 
    extent = {{-10, -10}, {10, 10}})));
  TYPhotovoltaicPower.Components.Inductor inductor1(L=0.0016) 
    annotation(Placement(transformation(origin = {-82.988, 82.8231}, 
    extent = {{-10, -10}, {10, 10}})));
  Modelica.Electrical.Analog.Basic.Capacitor capacitor1(C=0.001, v(start=800)) 
    annotation(Placement(transformation(origin = {-12.53, 43.1126}, 
    extent = {{-10, -10}, {10, 10}}, 
    rotation = 270)));
  TYPhotovoltaicPower.PowerTransmissions.PowerGrid powerGrid(V=380 * ones(3)) 
    annotation(Placement(transformation(origin = {134.176, 13.0399}, 
    extent = {{10, -10}, {-10, 10}})));
  Modelica.Blocks.Sources.Constant const1(k=800) 
    annotation(Placement(transformation(origin = {181.47, -42.13}, 
    extent = {{10, -10}, {-10, 10}})));
  Modelica.Blocks.Sources.TimeTable timeTable(table=[0, 0; 500, 0; 501, 150000; 600, 150000; 601, 0; 700, 0; 701, -150000; 800, -150000; 801, 0; 900, 0.0]) 
    annotation(Placement(transformation(origin = {181.47, -72.11}, 
    extent = {{10, -10}, {-10, 10}})));
  Modelica.Electrical.Analog.Sensors.VoltageSensor voltageSensor2 
    annotation(Placement(transformation(origin = {18.04, 43.1126}, 
    extent = {{-10, -10}, {10, 10}}, 
    rotation = -90)));
  TYPhotovoltaicPower.PowerConverters.Averaged.AveragedFullBridgeInverter3ph threePhaseBridgeInverter(Use_limiter=false) 
    annotation(Placement(transformation(origin = {58.51, 13.1699}, 
    extent = {{-10, -10}, {10, 10}})));
  .TYPhotovoltaicPower.Controllers.VoltageModulation pWM_NoModulation1(Use_v_line_max=true, Use_limiter=false, limit=1) 
    annotation(Placement(transformation(origin = {100, -48}, 
    extent = {{10, -10}, {-10, 10}})));
  TYPhotovoltaicPower.Controllers.GridSideController vOC_Q1(f_grid=50, k_Q=10, T_Q=0.15, k_d=30, T_d=0.24, k_q=30, T_q=0.24, k_v=1.44, T_v=18.9e-3, k_PLL=20, T_PLL=0.2e-3, Lc=0) 
    annotation(Placement(transformation(origin = {137.546, -48.13}, 
    extent = {{10, -10}, {-10, 10}})));
  TYPhotovoltaicPower.Controllers.MPPT mPPT(f_sample=f_sample, MPPTSelect="扰动观察法", deltaVref=0.0001, Vrefmax=363, Vrefinit=290) 
    annotation(Placement(transformation(origin = {-143.8887, -58.87}, 
    extent = {{-10, -10}, {10, 10}})));
  TYPhotovoltaicPower.Controllers.VrefRegulator vrefRegulator(kind="占空比", k=5 / 8, T=20) 
    annotation(Placement(transformation(origin = {-106.8261, -48}, 
    extent = {{-10, -10}, {10, 10}})));

equation
  connect(resistor2.n, capacitor.p) 
    annotation(Line(origin = {-106.5815, 50.5473}, 
    points = {{-0.2446, 4.199}, {-0.2446, -3.93605}, {0.0231, -3.93605}}, 
    color = {0, 0, 255}));
  connect(currentSensor1.n, resistor2.p) 
    annotation(Line(origin = {-121.5815, 78.5473}, 
    points = {{-1.331, 4}, {14.7554, 4}, {14.7554, -3.801}}, 
    color = {0, 0, 255}));
  connect(resistor2.p, inductor1.p) 
    annotation(Line(origin = {-36.5815, 53.5473}, 
    points = {{-70.2446, 21.199}, {-70.2446, 29.2758}, {-56.4065, 29.2758}}, 
    color = {0, 0, 255}));
  connect(voltageSensor.p, currentSensor1.p) 
    annotation(Line(origin = {-158.5815, 67.5473}, 
    points = {{-3, -14.4347}, {-3, 15}, {15.669, 15}}, 
    color = {0, 0, 255}));
  connect(voltageSensor.n, capacitor.n) 
    annotation(Line(origin = {-133.5815, 24.54725}, 
    points = {{-28, 8.56535}, {-28, -16.8041}, {27.0231, -16.8041}, {27.0231, 1.864}}, 
    color = {0, 0, 255}));
  connect(currentSensor1.i, product1.u1) 
    annotation(Line(origin = {-119.5815, 130.547}, 
    points = {{-13.331, -37}, {-13.331, -20.5673}, {1.0231, -20.5673}}, 
    color = {0, 0, 127}), __MWORKS(BlockSystem(NamedSignal)));
  connect(voltageSensor.v, product1.u2) 
    annotation(Line(origin = {-141.5815, 99.54725}, 
    points = {{-31, -56.4347}, {-36, -56.4347}, {-36, -1.56725}, {23.0231, -1.56725}}, 
    color = {0, 0, 127}));
  connect(temperatureSource1.port[1], pVarray1.heatPort) 
    annotation(Line(origin = {-233.247, 20.86}, 
    points = {{-2.833, -5.145}, {16.91, -5.145}, {16.91, 17.2526}}, 
    color = {191, 0, 0}));
  connect(step.y, pVarray1.G) 
    annotation(Line(origin = {-258.247, 49.86}, 
    points = {{23.167, 23.88}, {35.5438, 23.88}, {35.5438, 8.2526}}, 
    color = {0, 0, 127}));
  connect(inductor1.n, boostConv.pSupply) 
    annotation(Line(origin = {-61.94, 52.86}, 
    points = {{-10.848, 29.9631}, {-1.30551, 29.9631}, {-1.30551, -37.145}, {5.55597, -37.145}}, 
    color = {0, 0, 255}));
  connect(capacitor1.p, boostConv.pLoad) 
    annotation(Line(origin = {-27.94, 46.86}, 
    points = {{15.41, 6.2526}, {15.41, 35.2666}, {-4.77363, 35.2666}, {-4.77363, -31.1396}, {-8.4715, -31.1396}}, 
    color = {0, 0, 255}));
  connect(capacitor1.n, boostConv.nLoad) 
    annotation(Line(origin = {-27.94, 25.86}, 
    points = {{15.41, 7.2526}, {15.41, -18.04144}, {-8.5115, -18.04144}}, 
    color = {0, 0, 255}));
  connect(boostConv.nSupply, capacitor.n) 
    annotation(Line(origin = {-69.94, 15.86}, 
    points = {{13.54732, -7.99083}, {-36.6184, -7.99083}, {-36.6184, 10.55125}}, 
    color = {0, 0, 255}));
  connect(capacitor1.p, voltageSensor2.p) 
    annotation(Line(origin = {1.06, 45.86}, 
    points = {{-13.59, 7.2526}, {-13.59, 36.2379}, {16.98, 36.2379}, {16.98, 7.2526}}, 
    color = {0, 0, 255}));
  connect(voltageSensor2.n, boostConv.nLoad) 
    annotation(Line(origin = {-9.94, 15.86}, 
    points = {{27.98, 17.2526}, {27.98, -8.04144}, {-26.5115, -8.04144}}, 
    color = {0, 0, 255}));
  connect(voltageSensor2.p, threePhaseBridgeInverter.pin_p) 
    annotation(Line(origin = {49.06, 36.86}, 
    points = {{-31.02, 16.2526}, {-31.02, 45.3038}, {-17.0408, 45.3038}, {-17.0408, -18.8433}, {-0.5683, -18.8433}}, 
    color = {0, 0, 255}));
  connect(voltageSensor2.n, threePhaseBridgeInverter.pin_n) 
    annotation(Line(origin = {49.06, 15.86}, 
    points = {{-31.02, 17.2526}, {-31.02, -7.6314}, {-0.51476, -7.6314}}, 
    color = {0, 0, 255}));
  connect(threePhaseBridgeInverter.positivePlug, powerGrid.plug_p) 
    annotation(Line(origin = {94.51, 25.27}, 
    points = {{-25.8983, -12.1385}, {29.266, -12.1385}, {29.266, -12.2301}}, 
    color = {0, 0, 255}));
  connect(pWM_NoModulation1.Uabc, vOC_Q1.Uc_abc_ref) 
    annotation(Line(origin = {15.4736, -83.708}, 
    points = {{96.5264, 35.708}, {111.0724, 35.708}, {111.0724, 35.578}}, 
    color = {0, 0, 127}));
  connect(powerGrid.i_abc, vOC_Q1.ig_abc) 
    annotation(Line(origin = {26.8658, 7.3181}, 
    points = {{101.31, -5.2782}, {101.31, -43.4481}, {102.68, -43.4481}}, 
    color = {0, 0, 127}), __MWORKS(BlockSystem(NamedSignal)));
  connect(voltageSensor2.v, pWM_NoModulation1.Udc) 
    annotation(Line(origin = {28.455839, -10.9369}, 
    points = {{-21.415839, 54.0495}, {-26.2352, 54.0495}, {-26.2352, -52.5477}, {91.0858, -52.5477}, {91.0858, -45.0631}, {83.544161, -45.0631}}, 
    color = {0, 0, 127}), __MWORKS(BlockSystem(NamedSignal)));
  connect(const1.y, vOC_Q1.Udc_ref) 
    annotation(Line(origin = {155.209, -116.315}, 
    points = {{15.261, 74.185}, {-5.663, 74.185}}, 
    color = {0, 0, 127}));
  connect(timeTable.y, vOC_Q1.Qg_ref) 
    annotation(Line(origin = {147.209, -133.435}, 
    points = {{23.261, 61.325}, {13.5212, 61.325}, {13.5212, 79.305}, {2.337, 79.305}}, 
    color = {0, 0, 127}));
  connect(vOC_Q1.Udc, voltageSensor2.v) 
    annotation(Line(origin = {76.06, -19.14}, 
    points = {{69.486, -16.99}, {69.486, -6.40923}, {-73.7424, -6.40923}, {-73.7424, 62.2526}, {-69.02, 62.2526}}, 
    color = {0, 0, 127}));
  connect(pVarray1.p, currentSensor1.p) 
    annotation(Line(origin = {-184.94, 67.86}, 
    points = {{-21.397, -14.7474}, {-10.4032, -14.7474}, {-10.4032, 14.6873}, {42.0275, 14.6873}}, 
    color = {0, 0, 255}));
  connect(pVarray1.n, capacitor.n) 
    annotation(Line(origin = {-166.94, 24.86}, 
    points = {{-39.397, 18.2526}, {-29.0031, 18.2526}, {-29.0031, -17.2794}, {60.3816, -17.2794}, {60.3816, 1.55125}}, 
    color = {0, 0, 255}));
  connect(powerGrid.Uabc, vOC_Q1.Ug_abc) 
    annotation(Line(origin = {89.47, -30.86}, 
    points = {{42.706, 32.8999}, {48.076, 32.8999}, {48.076, -5.27}}, 
    color = {0, 0, 127}));
  connect(threePhaseBridgeInverter.Vref, pWM_NoModulation1.Uabc_normalized) 
    annotation(Line(origin = {41.51, -24.73}, 
    points = {{16.9401869, 25.8999}, {16.9401869, -23.27}, {47.49, -23.27}}, 
    color = {0, 0, 127}));
  connect(mPPT.Vref, vrefRegulator.Vref) 
    annotation(Line(origin = {-113.9897, -66.741}, 
    points = {{-18.899, 7.871}, {-11.0049, 7.871}, {-11.0049, 13.741}, {-4.6364, 13.741}}, 
    color = {0, 0, 127}));
  connect(vrefRegulator.y, boostConv.D) 
    annotation(Line(origin = {-70.94, -19.14}, 
    points = {{-24.0861, -28.86}, {24.4585, -28.86}, {24.4585, 18.8452}}, 
    color = {0, 0, 127}));
  connect(voltageSensor.v, mPPT.V) 
    annotation(Line(origin = {-166.94, 1.86}, 
    points = {{-5.6415, 41.2526}, {-10.7301, 41.2526}, {-10.7301, -56.73}, {11.0513, -56.73}}, 
    color = {0, 0, 127}));
  connect(voltageSensor.v, vrefRegulator.V) 
    annotation(Line(origin = {-147.94, 4.86}, 
    points = {{-24.6415, 38.2526}, {-29.7301, 38.2526}, {-29.7301, -47.86}, {29.3139, -47.86}}, 
    color = {0, 0, 127}));
  connect(currentSensor1.i, mPPT.I) 
    annotation(Line(origin = {-157.94, 31.86}, 
    points = {{25.0275, 61.6873}, {25.0275, 78.2103}, {-25.7077, 78.2103}, {-25.7077, -94.73}, {2.0513, -94.73}}, 
    color = {0, 0, 127}));
end TwoLevelGridConnectedAverage;