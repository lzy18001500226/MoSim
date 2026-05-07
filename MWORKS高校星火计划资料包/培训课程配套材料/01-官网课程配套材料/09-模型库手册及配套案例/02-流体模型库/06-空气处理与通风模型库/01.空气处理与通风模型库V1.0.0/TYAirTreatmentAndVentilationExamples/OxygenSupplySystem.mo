model OxygenSupplySystem "氧气供给系统"
  annotation(Documentation(link = "modelica://TYAirTreatmentAndVentilation/Resources/Examples/OxygenSupplySystem.html"), 
    Icon(coordinateSystem(extent = {{-100.0, -100.0}, {100.0, 100.0}}, grid = {2.0, 2.0}), 
    graphics = {Polygon(origin = {-7.105427357601002e-15, 33.0}, lineColor = {0, 94, 138}, fillColor = {0, 94, 138}, 
    fillPattern = FillPattern.Solid, points = {{-64.0, 1.0}, {0.0, 37.0}, {64.0, 1.0}, {0.0, -37.0}}), 
    Line(origin = {0.0, -12.0}, points = {{-62.0, 18.0}, {0.0, -18.0}, {62.0, 18.0}}, color = {0, 94, 138}, 
    thickness = 5.0), Line(origin = {7.105427357601002e-15, -39.99999999999999}, 
    points = {{-62.0, 18.0}, {0.0, -18.0}, {62.0, 18.0}}, color = {0, 94, 138}, thickness = 5.0)}), Diagram(coordinateSystem(extent = {{-100, -100}, {100, 100}}, 
    grid = {2, 2}), graphics = {Text(origin = {112.171, -86}, 
    lineColor = {0, 0, 0}, 
    extent = {{-81, 16.5}, {81, -16.5}}, 
    textString = "氧气消耗，二氧化碳产生", 
    fontSize = 36, 
    textStyle = {TextStyle.None}, 
    textColor = {0, 0, 0}), Text(origin = {-68.5, -86}, 
    lineColor = {0, 0, 0}, 
    extent = {{-58.5, 22}, {58.5, -22}}, 
    textString = "空气循环+CO2去除", 
    fontSize = 36, 
    textStyle = {TextStyle.None}, 
    textColor = {0, 0, 0}), Text(origin = {-66.171, 96}, 
    lineColor = {0, 0, 0}, 
    extent = {{-48, 10}, {48, -10}}, 
    textString = "氧气供给", 
    fontSize = 36, 
    textStyle = {TextStyle.None}, 
    textColor = {0, 0, 0})}), experiment(Algorithm = Dassl, InlineIntegrator = false, InlineStepSize = false, Interval = 0.01, StartTime = 0, StopTime = 500, Tolerance = 1e-08), __MWORKS(ContinueSimConfig(SaveContinueFile = "false", SaveBeforeStop = "false", NumberBeforeStop = 1, FixedContinueInterval = "false", ContinueIntervalLength = 0.5, ContinueTimeVector),ResultViewerManager(resultViewers={
ResultViewer(name="1", executeTrigger=executeTrigger.SimulationFinished, commands={
CreatePlot(id=3, x_display_unit="s", legend_layout=1, left_title_type=2, left_title="组分[kg/kg]", bottom_title_type=2, bottom_title="时间/s", right_title_type=2, fix_time_range_value=0, zoom_x=(0, 500), zoom_y_l=(0.1975, 0.2005)), 
Plot(legend=["腔室内氧气含量[kg/kg]"], y=["volume_pTX.X[1]"], colors=["4278190335"]), 
CreatePlot(id=-1, x_display_unit="s", legend_layout=1, left_title_type=2, left_title="组分[kg/kg]", bottom_title_type=2, bottom_title="时间/s", fix_time_range_value=0, sub_plot=(2, 1), zoom_x=(0, 500), zoom_y_l=(0.009, 0.014)), 
Plot(legend=["腔室内二氧化碳含碳量 [kg/kg]"], y=["volume_pTX.X[4]"], colors=["4278190335"])})
})), Protection(access = Access.nonPackageDuplicate));
  TYAirTreatmentAndVentilation.Auxiliaries.Volume_pTX volume_pTX(redeclare package Medium = TYAirTreatmentAndVentilation.Media.MoistAir, S = 2, redeclare model MediumType = TYAirTreatmentAndVentilation.Auxiliaries.Basics.MixtureGasesMedium, N = 4, V_tot(displayUnit = "l") = 0.1, T0 = 298.15) 
    annotation(Placement(transformation(origin = {41.171, 15}, 
    extent = {{-10, -10}, {10, 10}})));
  TYAirTreatmentAndVentilation.Auxiliaries.GeneralLoad generalLoad1(redeclare package Medium = TYAirTreatmentAndVentilation.Media.MoistAir, m_Water = -0.0001, m_CO2 = 0.0001, redeclare model MediumType = TYAirTreatmentAndVentilation.Auxiliaries.Basics.MixtureGasesMedium, m_O2 = -0.0001, m_in = 0.01) 
    annotation(Placement(transformation(origin = {167.671, 15}, 
    extent = {{-10, -10}, {10, 10}}, 
    rotation = 90)));
  TYAirTreatmentAndVentilation.Sources.MdotSource mdotSource(redeclare model MediumType = TYAirTreatmentAndVentilation.Auxiliaries.Basics.MixtureGasesMedium, redeclare package Medium = TYAirTreatmentAndVentilation.Media.MoistAir, use_Xi = true, Xi = {1, 0, 0, 0}, m_flow = 0.0001) 
    annotation(Placement(transformation(origin = {-230.171, 75}, 
    extent = {{-10, -10}, {10, 10}})));
  TYAirTreatmentAndVentilation.Auxiliaries.Volume_pTX volume_pTX1(redeclare model MediumType = TYAirTreatmentAndVentilation.Auxiliaries.Basics.MixtureGasesMedium, redeclare package Medium = TYAirTreatmentAndVentilation.Media.MoistAir) 
    annotation(Placement(transformation(origin = {-198.171, 74.946}, 
    extent = {{-10, -10}, {10, 10}})));
  TYAirTreatmentAndVentilation.Valves.SolenoidValves solenoidValves(redeclare model MediumType = TYAirTreatmentAndVentilation.Auxiliaries.Basics.MixtureGasesMedium, redeclare package Medium = TYAirTreatmentAndVentilation.Media.MoistAir) 
    annotation(Placement(transformation(origin = {-166.171, 74.946}, 
    extent = {{-10, -10}, {10, 10}})));
  TYAirTreatmentAndVentilation.Valves.PressureRegulator pressureRegulator(sc(displayUnit = "m3/(s.Pa)") = 1e-4, redeclare model MediumType = TYAirTreatmentAndVentilation.Auxiliaries.Basics.MixtureGasesMedium, redeclare package Medium = TYAirTreatmentAndVentilation.Media.MoistAir) 
    annotation(Placement(transformation(origin = {-104.171, 74.892}, 
    extent = {{-10, -10}, {10, 10}})));
  TYAirTreatmentAndVentilation.Auxiliaries.Volume_pTX volume_pTX2(redeclare model MediumType = TYAirTreatmentAndVentilation.Auxiliaries.Basics.MixtureGasesMedium, redeclare package Medium = TYAirTreatmentAndVentilation.Media.MoistAir) 
    annotation(Placement(transformation(origin = {-135.171, 75}, 
    extent = {{-10, -10}, {10, 10}})));
  TYAirTreatmentAndVentilation.Valves.ConstantThrottleValve constantThrottleValve2(redeclare package Medium = TYAirTreatmentAndVentilation.Media.MoistAir, redeclare model MediumType = TYAirTreatmentAndVentilation.Auxiliaries.Basics.MixtureGasesMedium, flowset = "C-b", sc(displayUnit = "m3/(s.Pa)") = 1e-4) 
    annotation(Placement(transformation(origin = {-42.829, 75}, 
    extent = {{-10, -10}, {10, 10}})));
  TYAirTreatmentAndVentilation.Auxiliaries.Volume_pTX volume_pTX3(redeclare model MediumType = TYAirTreatmentAndVentilation.Auxiliaries.Basics.MixtureGasesMedium, redeclare package Medium = TYAirTreatmentAndVentilation.Media.MoistAir) 
    annotation(Placement(transformation(origin = {-68.5, 74.892}, 
    extent = {{-10, -10}, {10, 10}})));
  TYAirTreatmentAndVentilation.Sources.PressureSource pressureSource3(redeclare package Medium = TYAirTreatmentAndVentilation.Media.MoistAir, energyDefinition = "T", p = 1.013e5, redeclare model MediumType = TYAirTreatmentAndVentilation.Auxiliaries.Basics.MixtureGasesMedium, use_Xi = false) 
    annotation(Placement(transformation(origin = {-135.171, 48.892}, 
    extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Sources.BooleanStep booleanStep1 
    annotation(Placement(transformation(origin = {-198.171, 105}, 
    extent = {{-10, -10}, {10, 10}})));
  TYAirTreatmentAndVentilation.AirTreatment.Co2Purifier co2Purifier(redeclare model MediumType = TYAirTreatmentAndVentilation.Auxiliaries.Basics.MixtureGasesMedium, redeclare package Medium = TYAirTreatmentAndVentilation.Media.MoistAir, C = {0.4777911, 9.105036, 755.0536}) 
    annotation(Placement(transformation(origin = {-42.829, -63}, 
    extent = {{10, -10}, {-10, 10}})));
  Modelica.Blocks.Sources.BooleanStep booleanStep2(startTime = 300) 
    annotation(Placement(transformation(origin = {-91.329, -25}, 
    extent = {{-10, -10}, {10, 10}})));
  TYAirTreatmentAndVentilation.CompressorsAndFans.IdealFan idealFan(redeclare model MediumType = TYAirTreatmentAndVentilation.Auxiliaries.Basics.MixtureGasesMedium, redeclare package Medium = TYAirTreatmentAndVentilation.Media.MoistAir, m_flow = 0.01) 
    annotation(Placement(transformation(origin = {-4.829, -62.946}, 
    extent = {{-10, -10}, {10, 10}}, 
    rotation = 90)));
  TYAirTreatmentAndVentilation.Pipes.Duct duct(D = 1, redeclare model MediumType = TYAirTreatmentAndVentilation.Auxiliaries.Basics.MixtureGasesMedium, redeclare package Medium = TYAirTreatmentAndVentilation.Media.MoistAir) 
    annotation(Placement(transformation(origin = {9.171, 33}, 
    extent = {{-10, -10}, {10, 10}})));
  TYAirTreatmentAndVentilation.Sources.PressureSource pressureSource1(redeclare package Medium = TYAirTreatmentAndVentilation.Media.MoistAir, energyDefinition = "T", p = 1.013e5, redeclare model MediumType = TYAirTreatmentAndVentilation.Auxiliaries.Basics.MixtureGasesMedium, use_Xi = false) 
    annotation(Placement(transformation(origin = {-32.829, 33}, 
    extent = {{-10, -10}, {10, 10}})));
  TYAirTreatmentAndVentilation.Auxiliaries.Volume_pTX volume_pTX4(redeclare package Medium = TYAirTreatmentAndVentilation.Media.MoistAir, S = 1, redeclare model MediumType = TYAirTreatmentAndVentilation.Auxiliaries.Basics.MixtureGasesMedium, N = 1, V_tot(displayUnit = "l") = 0.1, T0 = 298.15) 
    annotation(Placement(transformation(origin = {-80.829, -63}, 
    extent = {{10, -10}, {-10, 10}})));
  TYAirTreatmentAndVentilation.Valves.ConstantThrottleValve constantThrottleValve1(redeclare package Medium = TYAirTreatmentAndVentilation.Media.MoistAir, redeclare model MediumType = TYAirTreatmentAndVentilation.Auxiliaries.Basics.MixtureGasesMedium, flowset = "C-b", sc(displayUnit = "m3/(s.Pa)") = 1e-4) 
    annotation(Placement(transformation(origin = {-117, -63.054}, 
    extent = {{10, -10}, {-10, 10}})));
equation
  connect(volume_pTX.b[2], generalLoad1.port_a) 
    annotation(Line(origin = {79.171, 16}, 
    points = {{-32.161, -1.04}, {-32.161, -77}, {88.5, -77}, {88.5, -8.4}}, 
    color = {0, 127, 255}));
  connect(mdotSource.fluidPort, volume_pTX1.a[1]) 
    annotation(Line(origin = {-214.171, 74.892}, 
    points = {{-8, 0.108}, {10.161, 0.108}, {10.161, 0}}, 
    color = {0, 127, 255}));
  connect(volume_pTX1.b[1], solenoidValves.port_a) 
    annotation(Line(origin = {-184.171, 74.892}, 
    points = {{-8.161, 0.014}, {8, 0.014}, {8, 0.054}}, 
    color = {0, 127, 255}));
  connect(solenoidValves.port_b, volume_pTX2.a[1]) 
    annotation(Line(origin = {-148.171, 74.892}, 
    points = {{-8, 0.054}, {7.161, 0.054}}, 
    color = {0, 127, 255}));
  connect(volume_pTX2.b[1], pressureRegulator.port_a) 
    annotation(Line(origin = {-122.171, 74.892}, 
    points = {{-7.161, 0.068}, {8, 0.068}, {8, 0}}, 
    color = {0, 127, 255}));
  connect(pressureRegulator.port_b, volume_pTX3.a[1]) 
    annotation(Line(origin = {-83.829, 74.892}, 
    points = {{-10.342, 0}, {9.49, 0}, {9.49, -0.054}}, 
    color = {0, 127, 255}));
  connect(volume_pTX3.b[1], constantThrottleValve2.port_a) 
    annotation(Line(origin = {-52.829, 74.892}, 
    points = {{-9.832, -0.04}, {0, -0.04}, {0, 0.108}}, 
    color = {0, 127, 255}));
  connect(pressureSource3.fluidPort, pressureRegulator.port_R) 
    annotation(Line(origin = {-115.829, 56.892}, 
    points = {{-11.194, -8}, {11.658, -8}, {11.658, 8}}, 
    color = {0, 127, 255}));
  connect(volume_pTX.b[1], generalLoad1.port_b) 
    annotation(Line(origin = {79.171, 48}, 
    points = {{-32.161, -33.04}, {-32.161, 27}, {88.5, 27}, {88.5, -25.6}}, 
    color = {0, 127, 255}));
  connect(booleanStep1.y, solenoidValves.opening) 
    annotation(Line(origin = {-176.829, 94}, 
    points = {{-10.342, 11}, {10.658, 11}, {10.658, -11.054}}, 
    color = {255, 0, 255}));
  connect(booleanStep2.y, co2Purifier.b_replace) 
    annotation(Line(origin = {-106.329, -39}, 
    points = {{26, 14}, {63.536, 14}, {63.536, -14.036}}, 
    color = {255, 0, 255}));
  connect(constantThrottleValve2.port_b, volume_pTX.a[1]) 
    annotation(Line(origin = {1.171, 52}, 
    points = {{-34, 23}, {34.161, 23}, {34.161, -37.054}}, 
    color = {0, 127, 255}));
  connect(co2Purifier.port_a, idealFan.port_b) 
    annotation(Line(origin = {-23.829, -63}, 
    points = {{-9, 0}, {9, 0}, {9, 0.054}}, 
    color = {0, 127, 255}));
  connect(idealFan.port_a, volume_pTX.a[3]) 
    annotation(Line(origin = {20.171, -24}, 
    points = {{-15, -38.946}, {15.161, -38.946}, {15.161, 38.946}}, 
    color = {0, 127, 255}));
  connect(duct.port_a, pressureSource1.fluidPort) 
    annotation(Line(origin = {-12.829, 33}, 
    points = {{12, 0}, {-11.852, 0}}, 
    color = {0, 127, 255}));
  connect(volume_pTX4.a[1], co2Purifier.port_b) 
    annotation(Line(origin = {-63.829, -63}, 
    points = {{-11.161, -0.054}, {11, -0.054}, {11, 0}}, 
    color = {0, 127, 255}));
  connect(volume_pTX4.b[1], constantThrottleValve1.port_a) 
    annotation(Line(origin = {-96.829, -63}, 
    points = {{10.161, -0.04}, {-10.171, -0.04}, {-10.171, -0.054}}, 
    color = {0, 127, 255}));
  connect(constantThrottleValve1.port_b, volume_pTX.a[4]) 
    annotation(Line(origin = {-64.829, -24}, 
    points = {{-62.171, -39.054}, {-100, -39.054}, {-100, 38.946}, {100.161, 38.946}}, 
    color = {0, 127, 255}));
  connect(duct.port_b, volume_pTX.a[2]) 
    annotation(Line(origin = {27, 24}, 
    points = {{-7.829, 9}, {8.332, 9}, {8.332, -9.054}}, 
    color = {0, 127, 255}));
end OxygenSupplySystem;