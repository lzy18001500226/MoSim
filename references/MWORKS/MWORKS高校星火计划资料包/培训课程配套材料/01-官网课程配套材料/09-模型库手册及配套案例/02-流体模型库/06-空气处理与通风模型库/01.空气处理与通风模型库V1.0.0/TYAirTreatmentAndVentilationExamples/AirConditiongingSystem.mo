model AirConditiongingSystem "空调系统"
  annotation(Documentation(link = "modelica://TYAirTreatmentAndVentilation/Resources/Examples/AirConditiongingSystem.html"), 
    Icon(coordinateSystem(extent = {{-100.0, -100.0}, {100.0, 100.0}}, grid = {2.0, 2.0}), 
    graphics = {Polygon(origin = {-7.105427357601002e-15, 33.0}, lineColor = {0, 94, 138}, fillColor = {0, 94, 138}, 
    fillPattern = FillPattern.Solid, points = {{-64.0, 1.0}, {0.0, 37.0}, {64.0, 1.0}, {0.0, -37.0}}), 
    Line(origin = {0.0, -12.0}, points = {{-62.0, 18.0}, {0.0, -18.0}, {62.0, 18.0}}, color = {0, 94, 138}, 
    thickness = 5.0), Line(origin = {7.105427357601002e-15, -39.99999999999999}, 
    points = {{-62.0, 18.0}, {0.0, -18.0}, {62.0, 18.0}}, color = {0, 94, 138}, thickness = 5.0)}), Diagram(coordinateSystem(extent = {{-100, -100}, {100, 100}}, 
    grid = {2, 2}), graphics = {Text(origin = {115, -80}, 
    lineColor = {0, 0, 0}, 
    extent = {{-38, 6}, {38, -6}}, 
    textString = "压焓图", 
    textStyle = {TextStyle.None}, 
    textColor = {0, 0, 0}, 
    horizontalAlignment = LinePattern.None)}), experiment(Algorithm = Dassl, InlineIntegrator = false, InlineStepSize = false, Interval = 0.1, StartTime = 0, StopTime = 200, Tolerance = 0.0001), __MWORKS(ContinueSimConfig(SaveContinueFile = "false", SaveBeforeStop = "false", NumberBeforeStop = 1, FixedContinueInterval = "false", ContinueIntervalLength = 0.9, ContinueTimeVector),ResultViewerManager(resultViewers={
ResultViewer(name="1", executeTrigger=executeTrigger.SimulationFinished, commands={
CreatePlot(id=1, x_display_unit="s", legend_layout=1, left_title_type=2, left_title="换热量[W]", bottom_title_type=2, bottom_title="时间[s]", right_title_type=2, fix_time_range_value=0, zoom_x=(0, 200), zoom_y_l=(-1400, 200)), 
Plot(legend=["换热量 [W]"], y=["evaporator.Qdot"], colors=["4278190335"]), 
CreatePlot(id=-1, x_display_unit="s", legend_layout=1, left_title_type=2, left_title="气化率[1]", bottom_title_type=2, bottom_title="时间/s", fix_time_range_value=0, sub_plot=(2, 1), zoom_x=(0, 200), zoom_y_l=(-0.2, 1.2)), 
Plot(legend=["压气机出口气化率 [1]", "冷凝器出口气化率 [1]", "膨胀阀出口气化率 [1]", "蒸发器出口气化率 [1]"], y=["twophaseVolume3.quality", "twophaseVolume.quality", "twophaseVolume2.quality", "twophaseVolume1.quality"], colors=["4278190335", "4294901760", "4278222848", "4294902015"])})
})), Protection(access = Access.nonPackageDuplicate));
  final Real[4] xin = {scrollCompressor.port_b.h_outflow, condenser.port_b.h_outflow, simpleControlValve.port_b.h_outflow, evaporator.port_b.h_outflow} "横坐标比焓变量,单位kJ/kg" annotation(Dialog(group = "可视化变量序列,用于ph相图动态显示"));
  final Real[4] yin = {scrollCompressor.port_b.p, condenser.port_b.p, simpleControlValve.port_b.p, evaporator.port_b.p} "纵坐标对应压力变量,单位Pa" annotation(Dialog(group = "可视化变量序列,用于ph相图动态显示"));
  Modelica.Mechanics.Rotational.Sources.Speed speed 
    annotation(Placement(transformation(origin = {-158, -70}, 
    extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Sources.Constant const(k = 2000) 
    annotation(Placement(transformation(origin = {-221, -70}, 
    extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Sources.Constant const1(k = 1) 
    annotation(Placement(transformation(origin = {-143, 90}, 
    extent = {{-10, -10}, {10, 10}})));
  TYThermoFluidSys.Valves.SimpleControlValve simpleControlValve(redeclare package Medium = TYMedia.Helmholtz.R134a, dp_nominal = 1.5e6, m_flow_nominal = 0.01) 
    annotation(Placement(transformation(origin = {-118, 62}, 
    extent = {{-10, -10}, {10, 10}})));
  TYThermoFluidSys.Volumes.TwophaseVolume twophaseVolume(redeclare package Medium = TYMedia.Helmholtz.R134a, V(displayUnit = "l") = 0.0002, p_start = 4.999999999999999e5, T_start = 273.15, initFromEnthalpy = false, h_start = 100e3, initOpt = TYThermoFluidSys.Utilities.Types.InitOptions.initialValues) 
    annotation(Placement(transformation(origin = {-158, 62}, 
    extent = {{-10, -10}, {10, 10}})));
  TYAirTreatmentAndVentilation.CompressorsAndFans.SimpleCompressor scrollCompressor(redeclare package Medium = TYMedia.Helmholtz.R134a, VCyl(displayUnit = "ml") = 2e-5, IsSet = 0.7, VolSet = 0.95) 
    annotation(Placement(transformation(origin = {-118, -38}, 
    extent = {{10, -10}, {-10, 10}})));
  TYThermoFluidSys.Volumes.TwophaseVolume twophaseVolume1(redeclare package Medium = TYMedia.Helmholtz.R134a, V(displayUnit = "l") = 0.0002, T_start = 278.15, initFromEnthalpy = false, h_start = 100e3, p_start = 3e5, initOpt = TYThermoFluidSys.Utilities.Types.InitOptions.initialValues) 
    annotation(Placement(transformation(origin = {-87, -38}, 
    extent = {{10, -10}, {-10, 10}})));
  Modelica.Blocks.Math.Gain gain(k = 6.28 / 60) 
    annotation(Placement(transformation(origin = {-189.5, -70}, 
    extent = {{-10, -10}, {10, 10}})));
  TYThermoFluidSys.Volumes.TwophaseVolume twophaseVolume2(redeclare package Medium = TYMedia.Helmholtz.R134a, V(displayUnit = "l") = 0.0002, p_start = 3e5, T_start = 279.15, initFromEnthalpy = false, h_start = 100e3, initOpt = TYThermoFluidSys.Utilities.Types.InitOptions.initialValues) 
    annotation(Placement(transformation(origin = {-87, 62}, 
    extent = {{-10, -10}, {10, 10}})));
  TYThermoFluidSys.Volumes.TwophaseVolume twophaseVolume3(redeclare package Medium = TYMedia.Helmholtz.R134a, V(displayUnit = "l") = 0.0002, p_start = 6e5, T_start = 295.15, T(fixed = false), initFromEnthalpy = false, h_start = 300e3, initOpt = TYThermoFluidSys.Utilities.Types.InitOptions.initialValues) 
    annotation(Placement(transformation(origin = {-158, -38}, 
    extent = {{10, -10}, {-10, 10}})));
  TYAirTreatmentAndVentilation.HeatExchangers.FinandTubeHeatExchanger condenser(redeclare package Medium_tube = TYMedia.Helmholtz.R134a, PipeFuildType = "两相", numTubesPerTubeRows = 2, o = 1, finThickness = 0.001, finSpacing = 0.015, th(displayUnit = "mm") = 0.001, numTubeRows = 4, di = 0.01, depth = 0.3, width = 0.8, height = 0.8, redeclare package Medium_wall = TYMedia.Solid.Steel_304, n = 3, redeclare package Medium_fin = Modelica.Media.Air.DryAirNasa, T_fin_start = 293.15, T_start = 293.15, fin_p_start_in = 1.013e5, fin_p_start_out = 80000, pipe_p_start_in = 6e5, pipe_p_start_out = 4.999999999999999e5, pipe_T_start_in = 293.15, pipe_T_start_out = 293.15, Cp_input = 500, rho_input = 7900, redeclare model HT = TYAirTreatmentAndVentilation.HeatExchangers.Basics.Pipes_HEX.HT_HEX.ConstantCoefficient(alpha0 = 1000), redeclare model DP = TYAirTreatmentAndVentilation.HeatExchangers.Basics.Pipes_HEX.Dp_HEX.LinearPressureDrop, use_Medium_wall = false, lambda_input = 15, pipe_T_wall_start = 293.15) 
    annotation(Placement(transformation(origin = {-177, 12}, 
    extent = {{-10, -10}, {10, 10}}, 
    rotation = 90)));
  TYAirTreatmentAndVentilation.HeatExchangers.FinandTubeHeatExchanger evaporator(redeclare package Medium_tube = TYMedia.Helmholtz.R134a, redeclare package Medium_fin = Modelica.Media.Air.DryAirNasa, PipeFuildType = "两相", numTubesPerTubeRows = 2, o = 1, finThickness = 0.001, finSpacing = 0.015, th(displayUnit = "mm") = 0.001, numTubeRows = 3, di = 0.01, depth = 0.3, width = 0.8, height = 0.8, n = 3, T_fin_start = 293.15, T_start = 293.15, fin_p_start_in = 1.013e5, fin_p_start_out = 80000, pipe_p_start_in = 3e5, pipe_p_start_out = 3e5, pipe_T_start_in = 293.15, pipe_T_start_out = 293.15, Cp_input = 500, rho_input = 7900, redeclare model HT = TYAirTreatmentAndVentilation.HeatExchangers.Basics.Pipes_HEX.HT_HEX.ConstantCoefficient(alpha0 = 1000), redeclare model DP = TYAirTreatmentAndVentilation.HeatExchangers.Basics.Pipes_HEX.Dp_HEX.LinearPressureDrop, pipe_T_wall_start = 293.15) 
    annotation(Placement(transformation(origin = {-73, 12}, 
    extent = {{-10, 10}, {10, -10}}, 
    rotation = -90)));
  TYAirTreatmentAndVentilation.Sources.PressureSource pressureSource(redeclare model MediumType = TYAirTreatmentAndVentilation.Auxiliaries.Basics.IdealGasesMedium, T = 294.15, redeclare package Medium = Modelica.Media.Air.DryAirNasa) 
    annotation(Placement(transformation(origin = {-147.5, 12}, 
    extent = {{10, -10}, {-10, 10}})));
  TYAirTreatmentAndVentilation.Sources.PressureSource pressureSource1(redeclare model MediumType = TYAirTreatmentAndVentilation.Auxiliaries.Basics.IdealGasesMedium, redeclare package Medium = Modelica.Media.Air.DryAirNasa, T = 308.15) 
    annotation(Placement(transformation(origin = {-13, 12}, 
    extent = {{10, -10}, {-10, 10}})));
  TYAirTreatmentAndVentilation.Auxiliaries.ph_R134a ph_R134a2(x = xin, y = yin, minX = 150e3, maxX = 500e3, minY = 1e5, maxY = 50e5, bitmapSizeX = 1350, bitmapSizeY = 860, bitmapMinX = 138, bitmapMaxX = 1324, bitmapMinY = 60, bitmapMaxY = 837) 
    annotation(Placement(transformation(origin = {7, -99}, 
    extent = {{0, 0}, {199, 199}})));
  Modelica.Blocks.Sources.RealExpression COP(y = abs(evaporator.Qdot / max(1, scrollCompressor.P_wh))) 
    annotation(Placement(transformation(origin = {118, 90}, 
    extent = {{-25, -20}, {25, 20}})));
  TYAirTreatmentAndVentilation.CompressorsAndFans.IdealFan idealFan(m_flow = 1, redeclare model MediumType = TYAirTreatmentAndVentilation.Auxiliaries.Basics.IdealGasesMedium, redeclare package Medium = Modelica.Media.Air.DryAirNasa) 
    annotation(Placement(transformation(origin = {-211, 12}, 
    extent = {{10, -10}, {-10, 10}}, 
    rotation = -90)));
  TYAirTreatmentAndVentilation.Sources.PressureSource pressureSource2(redeclare model MediumType = TYAirTreatmentAndVentilation.Auxiliaries.Basics.IdealGasesMedium, T = 294.15, redeclare package Medium = Modelica.Media.Air.DryAirNasa) 
    annotation(Placement(transformation(origin = {-245, 12}, 
    extent = {{-10, -10}, {10, 10}})));
  TYAirTreatmentAndVentilation.Sources.PressureSource pressureSource3(redeclare package Medium = Modelica.Media.Air.DryAirNasa, redeclare model MediumType = TYAirTreatmentAndVentilation.Auxiliaries.Basics.IdealGasesMedium, T = 294.15) 
    annotation(Placement(transformation(origin = {-109, 12}, 
    extent = {{-10, -10}, {10, 10}})));
  TYAirTreatmentAndVentilation.CompressorsAndFans.IdealFan idealFan1(m_flow = 1, redeclare model MediumType = TYAirTreatmentAndVentilation.Auxiliaries.Basics.IdealGasesMedium, redeclare package Medium = Modelica.Media.Air.DryAirNasa) 
    annotation(Placement(transformation(origin = {-43, 12}, 
    extent = {{-10, -10}, {10, 10}}, 
    rotation = 90)));
equation
  connect(const1.y, simpleControlValve.opening) 
    annotation(Line(origin = {-138, 83}, 
    points = {{6, 7}, {20, 7}, {20, -14}}, 
    color = {0, 0, 127}));
  connect(speed.flange, scrollCompressor.flange_a) 
    annotation(Line(origin = {-149, -77}, 
    points = {{1, 7}, {31, 7}, {31, 29}}, 
    color = {0, 0, 0}));
  connect(const.y, gain.u) 
    annotation(Line(origin = {-206, -70}, 
    points = {{-4, 0}, {4.5, 0}}, 
    color = {0, 0, 127}));
  connect(speed.w_ref, gain.y) 
    annotation(Line(origin = {-174, -70}, 
    points = {{4, 0}, {-4.5, 0}}, 
    color = {0, 0, 127}));
  connect(condenser.air_out, pressureSource.fluidPort) 
    annotation(Line(origin = {-160, 12}, 
    points = {{-9, 0}, {4.352, 0}}, 
    color = {0, 127, 255}));
  connect(idealFan.port_b, condenser.air_in) 
    annotation(Line(origin = {-196, 12}, 
    points = {{-5, 0}, {11, 0}}, 
    color = {0, 127, 255}));
  connect(pressureSource2.fluidPort, idealFan.port_a) 
    annotation(Line(origin = {-229, 12}, 
    points = {{-7.852, 0}, {8, 0}}, 
    color = {0, 127, 255}));
  connect(pressureSource3.fluidPort, evaporator.air_in) 
    annotation(Line(origin = {-91, 12}, 
    points = {{-9.852, 0}, {10, 0}}, 
    color = {0, 127, 255}));
  connect(idealFan1.port_a, pressureSource1.fluidPort) 
    annotation(Line(origin = {-27, 12}, 
    points = {{-6, 0}, {5.852, 0}}, 
    color = {0, 127, 255}));
  connect(evaporator.air_out, idealFan1.port_b) 
    annotation(Line(origin = {-59, 12}, 
    points = {{-6, 0}, {6, 0}}, 
    color = {0, 127, 255}));
  connect(twophaseVolume3.port_b, condenser.port_a) 
    annotation(Line(origin = {-172, -18}, 
    points = {{4, -20}, {-5, -20}, {-5, 20}}, 
    color = {0, 127, 255}));
  connect(condenser.port_b, twophaseVolume.port_a) 
    annotation(Line(origin = {-173, 42}, 
    points = {{-4, -20}, {-4, 20}, {4.6, 20}}, 
    color = {0, 127, 255}));
  connect(twophaseVolume.port_b, simpleControlValve.port_a) 
    annotation(Line(origin = {-138, 62}, 
    points = {{-10, 0}, {10, 0}}, 
    color = {0, 127, 255}));
  connect(simpleControlValve.port_b, twophaseVolume2.port_a) 
    annotation(Line(origin = {-103, 62}, 
    points = {{-5, 0}, {5.6, 0}}, 
    color = {0, 127, 255}));
  connect(twophaseVolume2.port_b, evaporator.port_a) 
    annotation(Line(origin = {-75, 42}, 
    points = {{-2, 20}, {2, 20}, {2, -20}}, 
    color = {0, 127, 255}));
  connect(evaporator.port_b, twophaseVolume1.port_a) 
    annotation(Line(origin = {-75, -18}, 
    points = {{2, 20}, {2, -20}, {-1.6, -20}}, 
    color = {0, 127, 255}));
  connect(twophaseVolume1.port_b, scrollCompressor.port_a) 
    annotation(Line(origin = {-102, -38}, 
    points = {{5, 0}, {-6, 0}}, 
    color = {0, 127, 255}));
  connect(scrollCompressor.port_b, twophaseVolume3.port_a) 
    annotation(Line(origin = {-138, -38}, 
    points = {{10, 0}, {-9.6, 0}}, 
    color = {0, 127, 255}));
end AirConditiongingSystem;