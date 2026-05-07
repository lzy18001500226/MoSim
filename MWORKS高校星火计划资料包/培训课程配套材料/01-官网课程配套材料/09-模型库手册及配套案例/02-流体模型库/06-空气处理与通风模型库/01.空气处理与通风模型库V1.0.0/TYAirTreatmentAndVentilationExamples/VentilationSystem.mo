model VentilationSystem "通风系统"
  annotation(Documentation(link = "modelica://TYAirTreatmentAndVentilation/Resources/Examples/VentilationSystem.html"), 
    Icon(coordinateSystem(extent = {{-100.0, -100.0}, {100.0, 100.0}}, grid = {2.0, 2.0}), 
    graphics = {Polygon(origin = {-7.105427357601002e-15, 33.0}, lineColor = {0, 94, 138}, fillColor = {0, 94, 138}, 
    fillPattern = FillPattern.Solid, points = {{-64.0, 1.0}, {0.0, 37.0}, {64.0, 1.0}, {0.0, -37.0}}), 
    Line(origin = {0.0, -12.0}, points = {{-62.0, 18.0}, {0.0, -18.0}, {62.0, 18.0}}, color = {0, 94, 138}, 
    thickness = 5.0), Line(origin = {7.105427357601002e-15, -39.99999999999999}, 
    points = {{-62.0, 18.0}, {0.0, -18.0}, {62.0, 18.0}}, color = {0, 94, 138}, thickness = 5.0)}), Diagram(coordinateSystem(extent = {{-100, -100}, {100, 100}}, 
    grid = {2, 2}), graphics = {Text(origin = {7.954, -82}, 
    lineColor = {0, 0, 0}, 
    extent = {{-58.5, 22}, {58.5, -22}}, 
    textString = "空气通风+温度控制", 
    fontSize = 36, 
    textStyle = {TextStyle.None}, 
    textColor = {0, 0, 0})}), experiment(Algorithm = Dassl, InlineIntegrator = false, InlineStepSize = false, Interval = 0.01, StartTime = 0, StopTime = 25, Tolerance = 0.0001), __MWORKS(ContinueSimConfig(SaveContinueFile = "false", SaveBeforeStop = "false", NumberBeforeStop = 1, FixedContinueInterval = "false", ContinueIntervalLength = 25, ContinueTimeVector), ResultViewerManager(resultViewers = {
    ResultViewer(name = "Example", executeTrigger = executeTrigger.SimulationFinished, commands = {
    CreatePlot(id = 1, position = [0, 28, 950, 437], y = ["volume_pTX8.T"], x_display_unit = "s", y_display_units = ["degC"], y_axis = [1], legends = ["腔室内温度 [degC]"], legend_layout = 1, legend_frame = True, left_title_type = 2, left_title = "温度[degC]", bottom_title_type = 2, bottom_title = "时间[s]", right_title_type = 2)})
    })), Protection(access = Access.nonPackageDuplicate));
  TYAirTreatmentAndVentilation.Sources.PressureSource pressureSource1(redeclare package Medium = Modelica.Media.Air.DryAirNasa, energyDefinition = "T", p = 2e5, redeclare model MediumType = TYAirTreatmentAndVentilation.Auxiliaries.Basics.IdealGasesMedium, use_Xi = false, T = 283.15) 
    annotation(Placement(transformation(origin = {127.954, 66.148}, 
    extent = {{10, -10}, {-10, 10}})));
  TYAirTreatmentAndVentilation.HeatExchangers.GenericHeatExchanger genericHeatExchanger3(redeclare package PrimaryMedium = Modelica.Media.Air.DryAirNasa, thickness_wall(displayUnit = "mm"), Dh_prim(displayUnit = "mm") = 0.104, Dh_sec(displayUnit = "mm") = 0.104, Dhyd_prim(displayUnit = "m"), m_flow0_prim = 1, dp0_prim = 10000, redeclare model Friction_prim = TYAirTreatmentAndVentilation.HeatExchangers.Basics.Dp_NTU.LinearOperatingPointLoss, m_flow0_sec = 1, dp0_sec = 10000, redeclare model Friction_sec = TYAirTreatmentAndVentilation.HeatExchangers.Basics.Dp_NTU.LinearOperatingPointLoss, redeclare model HeatTransfer_prim = TYAirTreatmentAndVentilation.HeatExchangers.Basics.HT_NTU.ConstantCoefficient, redeclare model HeatTransfer_sec = TYAirTreatmentAndVentilation.HeatExchangers.Basics.HT_NTU.ConstantCoefficient, Q_flow_kind = "换热效率", epsset = 0.65, redeclare package SecondaryMedium = Modelica.Media.Air.DryAirNasa) 
    annotation(Placement(transformation(origin = {71.954, 60.148}, 
    extent = {{10, -10}, {-10, 10}})));
  TYAirTreatmentAndVentilation.Sources.PressureSource pressureSource14(use_p_in = false, use_T_in = false, T(displayUnit = "degC") = 283.15, redeclare package Medium = Modelica.Media.Air.DryAirNasa, energyDefinition = "T", p = 100000, redeclare model MediumType = TYAirTreatmentAndVentilation.Auxiliaries.Basics.IdealGasesMedium) 
    annotation(Placement(transformation(origin = {-6.5, 66.148}, 
    extent = {{-10, -10}, {10, 10}})));
  TYAirTreatmentAndVentilation.Auxiliaries.Volume_pTX volume_pTX7(N = 1, redeclare model MediumType = TYAirTreatmentAndVentilation.Auxiliaries.Basics.IdealGasesMedium, V_tot(displayUnit = "l") = 0.001, p0 = 1.013e5, T0 = 293.15, redeclare package Medium = Modelica.Media.Air.DryAirNasa) 
    annotation(Placement(transformation(origin = {-6.5, 12.094}, 
    extent = {{-10, 10}, {10, -10}})));
  TYAirTreatmentAndVentilation.Auxiliaries.Volume_pTX volume_pTX8(N = 1, redeclare model MediumType = TYAirTreatmentAndVentilation.Auxiliaries.Basics.IdealGasesMedium, V_tot(displayUnit = "l") = 0.001, p0 = 1.013e5, T0 = 293.15, redeclare package Medium = Modelica.Media.Air.DryAirNasa) 
    annotation(Placement(transformation(origin = {151.454, 12}, 
    extent = {{10, 10}, {-10, -10}})));
  TYAirTreatmentAndVentilation.Auxiliaries.FlowSplit flowSplit(redeclare model MediumType = TYAirTreatmentAndVentilation.Auxiliaries.Basics.IdealGasesMedium, N = 3, redeclare package Medium = Modelica.Media.Air.DryAirNasa) 
    annotation(Placement(transformation(origin = {113.454, 12.134}, 
    extent = {{10, -10}, {-10, 10}})));
  Modelica.Blocks.Sources.RealExpression realExpression(y = 1 - PID.y) 
    annotation(Placement(transformation(origin = {-94.046, 54.148}, 
    extent = {{-10, -10}, {10, 10}})));
  TYAirTreatmentAndVentilation.Auxiliaries.FlowSplit flowSplit2(redeclare model MediumType = TYAirTreatmentAndVentilation.Auxiliaries.Basics.IdealGasesMedium, N = 2, redeclare package Medium = Modelica.Media.Air.DryAirNasa) 
    annotation(Placement(transformation(origin = {-76.342, 12.174}, 
    extent = {{-10, -10}, {10, 10}})));
  TYAirTreatmentAndVentilation.Sources.PressureSource pressureSource3(energyDefinition = "T", redeclare model MediumType = TYAirTreatmentAndVentilation.Auxiliaries.Basics.IdealGasesMedium, use_Xi = false, T = 323.15, redeclare package Medium = Modelica.Media.Air.DryAirNasa) 
    annotation(Placement(transformation(origin = {221.908, 12}, 
    extent = {{10, -10}, {-10, 10}})));
  TYAirTreatmentAndVentilation.Sensors.TemperatureSensor temperatureSensor(redeclare model MediumType = TYAirTreatmentAndVentilation.Auxiliaries.Basics.IdealGasesMedium, redeclare package Medium = Modelica.Media.Air.DryAirNasa) 
    annotation(Placement(transformation(origin = {7.954, 97.621}, 
    extent = {{10, -10}, {-10, 10}})));
  Modelica.Blocks.Sources.Constant const(k = 273.15 + 24) 
    annotation(Placement(transformation(origin = {-94.046, 129.621}, 
    extent = {{-10, -10}, {10, 10}})));
  TYAirTreatmentAndVentilation.Controllers.LimPID PID(kp = 1 / 20, ki = 1 / 2) 
    annotation(Placement(transformation(origin = {-26.046, 97.621}, 
    extent = {{-10, 10}, {10, -10}}, 
    rotation = -90)));
  TYAirTreatmentAndVentilation.Valves.VariableThrottleValve simpleControlValve(redeclare package Medium = Modelica.Media.Air.DryAirNasa, sc = 1e-6, redeclare model MediumType = TYAirTreatmentAndVentilation.Auxiliaries.Basics.IdealGasesMedium) 
    annotation(Placement(transformation(origin = {-40.046, 12.174}, 
    extent = {{-10, -10}, {10, 10}})));
  TYAirTreatmentAndVentilation.Valves.VariableThrottleValve simpleControlValve1(redeclare package Medium = Modelica.Media.Air.DryAirNasa, sc = 1e-6, redeclare model MediumType = TYAirTreatmentAndVentilation.Auxiliaries.Basics.IdealGasesMedium) 
    annotation(Placement(transformation(origin = {-40.046, -42.273}, 
    extent = {{-10, -10}, {10, 10}})));
  TYAirTreatmentAndVentilation.Valves.ConstantThrottleValve simpleControlValve2(redeclare package Medium = Modelica.Media.Air.DryAirNasa, sc = 1e-6, redeclare model MediumType = TYAirTreatmentAndVentilation.Auxiliaries.Basics.IdealGasesMedium) 
    annotation(Placement(transformation(origin = {186.681, 12.174}, 
    extent = {{-10, -10}, {10, 10}})));
  TYAirTreatmentAndVentilation.Valves.CheckValveWithSpring checkValveWithSpring(redeclare model MediumType = TYAirTreatmentAndVentilation.Auxiliaries.Basics.IdealGasesMedium, redeclare package Medium = Modelica.Media.Air.DryAirNasa) 
    annotation(Placement(transformation(origin = {42, -42.327}, 
    extent = {{-10, -10}, {10, 10}})));
  TYAirTreatmentAndVentilation.Auxiliaries.Volume_pTX volume_pTX1(N = 1, redeclare model MediumType = TYAirTreatmentAndVentilation.Auxiliaries.Basics.IdealGasesMedium, V_tot(displayUnit = "l") = 0.001, p0 = 1.013e5, T0 = 293.15, redeclare package Medium = Modelica.Media.Air.DryAirNasa) 
    annotation(Placement(transformation(origin = {-6.5, -42.327}, 
    extent = {{-10, 10}, {10, -10}})));
  TYAirTreatmentAndVentilation.CompressorsAndFans.IdealFan idealFan(m_flow = 0.025, redeclare package Medium = Modelica.Media.Air.DryAirNasa, redeclare model MediumType = TYAirTreatmentAndVentilation.Auxiliaries.Basics.IdealGasesMedium) 
    annotation(Placement(transformation(origin = {-129.365, 41.647}, 
    extent = {{-10, -10}, {10, 10}}, 
    rotation = -90)));
  TYAirTreatmentAndVentilation.Sources.PressureSource pressureSource(T = 323.15, p = 1.013e5, redeclare model MediumType = TYAirTreatmentAndVentilation.Auxiliaries.Basics.IdealGasesMedium, redeclare package Medium = Modelica.Media.Air.DryAirNasa) 
    annotation(Placement(transformation(origin = {-181.365, 11.647}, 
    extent = {{-10, -10}, {10, 10}})));
  TYAirTreatmentAndVentilation.CompressorsAndFans.IdealFan idealFan1(m_flow = 0.025, redeclare model MediumType = TYAirTreatmentAndVentilation.Auxiliaries.Basics.IdealGasesMedium, redeclare package Medium = Modelica.Media.Air.DryAirNasa) 
    annotation(Placement(transformation(origin = {-128.853, 11.647}, 
    extent = {{-10, -10}, {10, 10}}, 
    rotation = -90)));
  TYAirTreatmentAndVentilation.CompressorsAndFans.IdealFan idealFan2(m_flow = 0.025, redeclare package Medium = Modelica.Media.Air.DryAirNasa, redeclare model MediumType = TYAirTreatmentAndVentilation.Auxiliaries.Basics.IdealGasesMedium) 
    annotation(Placement(transformation(origin = {-128.853, -18.353}, 
    extent = {{-10, -10}, {10, 10}}, 
    rotation = -90)));
  TYAirTreatmentAndVentilation.CompressorsAndFans.IdealFan idealFan3(m_flow = 0.025, redeclare package Medium = Modelica.Media.Air.DryAirNasa, redeclare model MediumType = TYAirTreatmentAndVentilation.Auxiliaries.Basics.IdealGasesMedium) 
    annotation(Placement(transformation(origin = {-128.853, -48.353}, 
    extent = {{-10, -10}, {10, 10}}, 
    rotation = -90)));
equation
  connect(genericHeatExchanger3.portA_primary, pressureSource1.fluidPort) 
    annotation(Line(origin = {90.5, 66.094}, 
    points = {{-8.546, 0.054}, {29.306, 0.054}}, 
    color = {0, 127, 255}));
  connect(pressureSource14.fluidPort, genericHeatExchanger3.portB_primary) 
    annotation(Line(origin = {-16.5, 66.094}, 
    points = {{18.148, 0.054}, {78.454, 0.054}}, 
    color = {0, 127, 255}));
  connect(flowSplit.port_a, volume_pTX8.b[1]) 
    annotation(Line(origin = {134.454, 12.094}, 
    points = {{-11, 0.04}, {11.161, 0.04}, {11.161, -0.054}}, 
    color = {0, 127, 255}));
  connect(genericHeatExchanger3.portB_secondary, flowSplit.port_b[1]) 
    annotation(Line(origin = {57.5, 33.094}, 
    points = {{24.454, 21.054}, {45.954, 21.054}, {45.954, -20.96}}, 
    color = {0, 127, 255}));
  connect(temperatureSensor.T, PID.u2) 
    annotation(Line(origin = {-13.046, 97.621}, 
    points = {{14, 0}, {-1, 0}}, 
    color = {0, 0, 127}));
  connect(const.y, PID.u) 
    annotation(Line(origin = {-61.046, 119.621}, 
    points = {{-22, 10}, {35, 10}, {35, -10}}, 
    color = {0, 0, 127}));
  connect(flowSplit2.port_b[1], simpleControlValve.port_a) 
    annotation(Line(origin = {-58.046, 12.621}, 
    points = {{-8.296, -0.447}, {8, -0.447}}, 
    color = {0, 127, 255}));
  connect(simpleControlValve.port_b, volume_pTX7.a[1]) 
    annotation(Line(origin = {-21.046, 12.621}, 
    points = {{-9, -0.447}, {8.707, -0.447}, {8.707, -0.473}}, 
    color = {0, 127, 255}));
  connect(flowSplit2.port_b[2], simpleControlValve1.port_a) 
    annotation(Line(origin = {-58.046, -15.379}, 
    points = {{-8.296, 27.553}, {-2, 27.553}, {-2, -26.894}, {8, -26.894}}, 
    color = {0, 127, 255}));
  connect(volume_pTX8.a[1], simpleControlValve2.port_a) 
    annotation(Line(origin = {166.908, 11.621}, 
    points = {{-9.615, 0.433}, {9.773, 0.433}, {9.773, 0.553}}, 
    color = {0, 127, 255}));
  connect(simpleControlValve2.port_b, pressureSource3.fluidPort) 
    annotation(Line(origin = {204.908, 11.621}, 
    points = {{-8.227, 0.553}, {8.852, 0.553}, {8.852, 0.379}}, 
    color = {0, 127, 255}));
  connect(simpleControlValve1.port_b, volume_pTX1.a[1]) 
    annotation(Line(origin = {-18.046, -42.379}, 
    points = {{-12, 0.106}, {5.707, 0.106}, {5.707, 0.106}}, 
    color = {0, 127, 255}));
  connect(volume_pTX1.b[1], checkValveWithSpring.port_a) 
    annotation(Line(origin = {14.954, -42.379}, 
    points = {{-15.615, 0.092}, {17.046, 0.092}, {17.046, 0.052}}, 
    color = {0, 127, 255}));
  connect(checkValveWithSpring.port_b, flowSplit.port_b[2]) 
    annotation(Line(origin = {53.954, -15.379}, 
    points = {{-1.954, -26.948}, {49.5, -26.948}, {49.5, 27.513}}, 
    color = {0, 127, 255}));
  connect(volume_pTX7.b[1], genericHeatExchanger3.portA_secondary) 
    annotation(Line(origin = {30.954, 33.621}, 
    points = {{-31.615, -21.487}, {5, -21.487}, {5, 20.527}, {31, 20.527}}, 
    color = {0, 127, 255}));
  connect(PID.y, simpleControlValve1.opening) 
    annotation(Line(origin = {-34.046, 25.621}, 
    points = {{8, 61}, {8, -48}, {-6, -48}, {-6, -59.894}}, 
    color = {0, 0, 127}));
  connect(realExpression.y, simpleControlValve.opening) 
    annotation(Line(origin = {-61.046, 36.621}, 
    points = {{-22, 17.527}, {21, 17.527}, {21, -16.447}}, 
    color = {0, 0, 127}));
  connect(temperatureSensor.port_a, flowSplit.port_b[3]) 
    annotation(Line(origin = {55.635, 49.647}, 
    points = {{-47.681, 37.974}, {-47.681, 34}, {47.819, 34}, {47.819, -37.513}}, 
    color = {0, 127, 255}));
  connect(pressureSource.fluidPort, idealFan1.port_a) 
    annotation(Line(origin = {-163.365, 11.647}, 
    points = {{-9.852, 0}, {24.512, 0}}, 
    color = {0, 127, 255}));
  connect(pressureSource.fluidPort, idealFan.port_a) 
    annotation(Line(origin = {-163.365, 26.647}, 
    points = {{-9.852, -15}, {0, -15}, {0, 15}, {24, 15}}, 
    color = {0, 127, 255}));
  connect(pressureSource.fluidPort, idealFan2.port_a) 
    annotation(Line(origin = {-163.365, -3.353}, 
    points = {{-9.852, 15}, {0, 15}, {0, -15}, {24.512, -15}}, 
    color = {0, 127, 255}));
  connect(idealFan.port_b, flowSplit2.port_a) 
    annotation(Line(origin = {-110.365, 20.647}, 
    points = {{-9, 21}, {24.023, 21}, {24.023, -8.473}}, 
    color = {0, 127, 255}));
  connect(idealFan1.port_b, flowSplit2.port_a) 
    annotation(Line(origin = {-110.365, 5.647}, 
    points = {{-8.488, 6}, {24.023, 6}, {24.023, 6.527}}, 
    color = {0, 127, 255}));
  connect(idealFan2.port_b, flowSplit2.port_a) 
    annotation(Line(origin = {-110.365, -9.353}, 
    points = {{-8.488, -9}, {24.023, -9}, {24.023, 21.527}}, 
    color = {0, 127, 255}));
  connect(pressureSource.fluidPort, idealFan3.port_a) 
    annotation(Line(origin = {-156.365, -15.353}, 
    points = {{-16.852, 27}, {-7, 27}, {-7, -33}, {17.512, -33}}, 
    color = {0, 127, 255}));
  connect(idealFan3.port_b, flowSplit2.port_a) 
    annotation(Line(origin = {-102.365, -15.353}, 
    points = {{-16.488, -33}, {16.023, -33}, {16.023, 27.527}}, 
    color = {0, 127, 255}));
end VentilationSystem;