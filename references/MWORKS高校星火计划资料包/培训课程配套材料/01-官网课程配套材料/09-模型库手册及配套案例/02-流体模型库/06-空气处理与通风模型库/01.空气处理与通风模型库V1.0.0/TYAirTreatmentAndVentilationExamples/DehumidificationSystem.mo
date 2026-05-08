model DehumidificationSystem "除湿系统"
  annotation(Documentation(link = "modelica://TYAirTreatmentAndVentilation/Resources/Examples/DehumidificationSystem.html"), 
    Icon(coordinateSystem(extent = {{-100.0, -100.0}, {100.0, 100.0}}, grid = {2.0, 2.0}), 
    graphics = {Polygon(origin = {-7.105427357601002e-15, 33.0}, lineColor = {0, 94, 138}, fillColor = {0, 94, 138}, 
    fillPattern = FillPattern.Solid, points = {{-64.0, 1.0}, {0.0, 37.0}, {64.0, 1.0}, {0.0, -37.0}}), 
    Line(origin = {0.0, -12.0}, points = {{-62.0, 18.0}, {0.0, -18.0}, {62.0, 18.0}}, color = {0, 94, 138}, 
    thickness = 5.0), Line(origin = {7.105427357601002e-15, -39.99999999999999}, 
    points = {{-62.0, 18.0}, {0.0, -18.0}, {62.0, 18.0}}, color = {0, 94, 138}, thickness = 5.0)}), Diagram(coordinateSystem(extent = {{-100, -100}, {100, 100}}, 
    grid = {2, 2})), experiment(Algorithm = Dassl, InlineIntegrator = false, InlineStepSize = false, Interval = 0.001, StartTime = 0, StopTime = 10, Tolerance = 0.0001), __MWORKS(ContinueSimConfig(SaveContinueFile = "false", SaveBeforeStop = "false", NumberBeforeStop = 1, FixedContinueInterval = "false", ContinueIntervalLength = 0.77, ContinueTimeVector), ResultViewerManager(resultViewers = {
    ResultViewer(name = "Example", executeTrigger = executeTrigger.SimulationFinished, commands = {
    CreatePlot(id = 1, position = [0, 28, 950, 438], y = ["volume_pTX4.X[2]", "volume_pTX2.X[2]"], x_display_unit = "s", y_display_units = ["kg/kg", "kg/kg"], y_axis = [1, 1], legends = ["除湿前 [kg/kg]", "除湿后[kg/kg]"], legend_layout = 1, legend_frame = True, left_title_type = 2, left_title = "水蒸气含量[kg/kg]", bottom_title_type = 2, bottom_title = "时间[s]", right_title_type = 2)})
    })), Protection(access = Access.nonPackageDuplicate));
  final Real[2] xin = {volume_pTX4.X[2] / (1 - volume_pTX4.X[2]) * 100, volume_pTX2.X[2] / (1 - volume_pTX2.X[2]) * 100} "横坐标相对湿度,单位%" annotation(Dialog(group = "可视化变量序列,用于焓湿图动态显示"));
  final Real[2] yin = {volume_pTX4.T - 273.15, volume_pTX2.T - 273.15} "纵坐标对应温度,单位℃" annotation(Dialog(group = "可视化变量序列,用于焓湿图动态显示"));
  TYAirTreatmentAndVentilation.Sources.PressureSource mdotSource(redeclare package Medium = TYAirTreatmentAndVentilation.Media.MoistAir, redeclare model MediumType = TYAirTreatmentAndVentilation.Auxiliaries.Basics.MixtureGasesMedium, T = 303.15, p = 1.013e5, use_Xi = true, Xi = {0.2, 0.09, 0.7, 0.01}) 
    annotation(Placement(transformation(origin = {-207, 45.946}, 
    extent = {{-10, -10}, {10, 10}})));
  TYAirTreatmentAndVentilation.Auxiliaries.Volume_pTX volume_pTX2(redeclare package Medium = TYAirTreatmentAndVentilation.Media.MoistAir, V_tot(displayUnit = "l") = 0.001, redeclare model MediumType = TYAirTreatmentAndVentilation.Auxiliaries.Basics.MixtureGasesMedium, p0 = 1.013e5, Xi_start = {0.2, 0.09, 0.7, 0.01}) 
    annotation(Placement(transformation(origin = {-40, 45.892}, 
    extent = {{-10, -10}, {10, 10}})));
  TYAirTreatmentAndVentilation.Sources.PressureSource pressureSource(redeclare package Medium = TYAirTreatmentAndVentilation.Media.MoistAir, redeclare model MediumType = TYAirTreatmentAndVentilation.Auxiliaries.Basics.MixtureGasesMedium, p = 1.013e5, T = 293.15) 
    annotation(Placement(transformation(origin = {-207, -66.304}, 
    extent = {{-10, -10}, {10, 10}})));
  TYAirTreatmentAndVentilation.Auxiliaries.Volume_pTX room(redeclare package Medium = TYAirTreatmentAndVentilation.Media.MoistAir, V_tot(displayUnit = "m3") = 1, redeclare model MediumType = TYAirTreatmentAndVentilation.Auxiliaries.Basics.MixtureGasesMedium, p0 = 1.013e5) 
    annotation(Placement(transformation(origin = {-60, -66.304}, 
    extent = {{10, -10}, {-10, 10}})));
  TYAirTreatmentAndVentilation.Pipes.Duct duct(D = 0.5, L = 4, redeclare model MediumType = TYAirTreatmentAndVentilation.Auxiliaries.Basics.MixtureGasesMedium, redeclare package Medium = TYAirTreatmentAndVentilation.Media.MoistAir) 
    annotation(Placement(transformation(origin = {-18, 45.946}, 
    extent = {{-10, -10}, {10, 10}})));
  TYAirTreatmentAndVentilation.CompressorsAndFans.IdealFan idealFan(use_mflow_in = true, m_flow = 0.99, redeclare model MediumType = TYAirTreatmentAndVentilation.Auxiliaries.Basics.MixtureGasesMedium, redeclare package Medium = TYAirTreatmentAndVentilation.Media.MoistAir) 
    annotation(Placement(transformation(origin = {-145, 45.892}, 
    extent = {{-10, 10}, {10, -10}}, 
    rotation = 90)));
  TYAirTreatmentAndVentilation.AirTreatment.CooledAirDryer cooledAirDryer(redeclare model MediumType = TYAirTreatmentAndVentilation.Auxiliaries.Basics.MixtureGasesMedium, redeclare package Medium = TYAirTreatmentAndVentilation.Media.MoistAir, area(displayUnit = "m2") = 5) 
    annotation(Placement(transformation(origin = {-62, 45.838}, 
    extent = {{-10, -10}, {10, 10}})));
  TYAirTreatmentAndVentilation.Pipes.Duct duct1(D = 0.5, L = 4, redeclare model MediumType = TYAirTreatmentAndVentilation.Auxiliaries.Basics.MixtureGasesMedium, redeclare package Medium = TYAirTreatmentAndVentilation.Media.MoistAir) 
    annotation(Placement(transformation(origin = {-108, -66.304}, 
    extent = {{10, -10}, {-10, 10}})));
  TYAirTreatmentAndVentilation.Sensors.PressureSensor pressureSensor(redeclare model MediumType = TYAirTreatmentAndVentilation.Auxiliaries.Basics.MixtureGasesMedium, redeclare package Medium = TYAirTreatmentAndVentilation.Media.MoistAir) 
    annotation(Placement(transformation(origin = {-171.5, -34.054}, 
    extent = {{-10, 10}, {10, -10}})));
  TYAirTreatmentAndVentilation.Sensors.PressureSensor pressureSensor1(redeclare model MediumType = TYAirTreatmentAndVentilation.Auxiliaries.Basics.MixtureGasesMedium, redeclare package Medium = TYAirTreatmentAndVentilation.Media.MoistAir) 
    annotation(Placement(transformation(origin = {-120, -34.054}, 
    extent = {{10, 10}, {-10, -10}})));
  Modelica.Blocks.Math.Add add(k2 = 1, k1 = -1) 
    annotation(Placement(transformation(origin = {-145, -10}, 
    extent = {{-10, -10}, {10, 10}}, 
    rotation = 90)));
  Modelica.Blocks.Tables.CombiTable1Ds combiTable1Dv(table = {{280, 3.515674984005}, {320.66666666667, 3.5156749840051}, {389.8, 3.5039454041373}, {528.06666666667, 3.4863510343357}, {633.8, 3.4628918746001}, {816.8, 3.3455960759224}, {1200, 2.7777777777778}, {1398.3333333333, 2.0110918312922}, {1500, 1.1111111111111}}) 
    annotation(Placement(transformation(origin = {-145, 17.946}, 
    extent = {{-10, -10}, {10, 10}}, 
    rotation = 90)));
  TYAirTreatmentAndVentilation.Auxiliaries.FlowSplit flowSplit(N = 2, redeclare package Medium = TYAirTreatmentAndVentilation.Media.MoistAir, redeclare model MediumType = TYAirTreatmentAndVentilation.Auxiliaries.Basics.MixtureGasesMedium) 
    annotation(Placement(transformation(origin = {-176, 45.946}, 
    extent = {{-10, -10}, {10, 10}})));
  TYAirTreatmentAndVentilation.Auxiliaries.FlowSplit flowSplit1(N = 2, redeclare model MediumType = TYAirTreatmentAndVentilation.Auxiliaries.Basics.MixtureGasesMedium, redeclare package Medium = TYAirTreatmentAndVentilation.Media.MoistAir) 
    annotation(Placement(transformation(origin = {-114, 45.892}, 
    extent = {{10, -10}, {-10, 10}})));
  TYAirTreatmentAndVentilation.Auxiliaries.Volume_pTX volume_pTX4(redeclare package Medium = TYAirTreatmentAndVentilation.Media.MoistAir, V_tot(displayUnit = "l") = 0.001, redeclare model MediumType = TYAirTreatmentAndVentilation.Auxiliaries.Basics.MixtureGasesMedium, p0 = 1.013e5, Xi_start = {0.2, 0.09, 0.7, 0.01}) 
    annotation(Placement(transformation(origin = {-88, 45.838}, 
    extent = {{-10, -10}, {10, 10}})));
  TYAirTreatmentAndVentilation.Auxiliaries.PsychrometricChat psychrometricChat(x = xin, y = yin) 
    annotation(Placement(transformation(origin = {24, -110}, 
    extent = {{0, 0}, {200, 200}})));
equation
  connect(duct.port_b, room.a[1]) 
    annotation(Line(origin = {49, 4.946}, 
    points = {{-57, 41}, {-37, 41}, {-37, -71.304}, {-103.161, -71.304}}, 
    color = {0, 127, 255}));
  connect(cooledAirDryer.port_b, volume_pTX2.a[1]) 
    annotation(Line(origin = {-52.0938, 46.321}, 
    points = {{0.0938, -0.483}, {6.2548, -0.483}}, 
    color = {0, 127, 255}));
  connect(duct1.port_a, room.b[1]) 
    annotation(Line(origin = {-88, -66.554}, 
    points = {{-10, 0.25}, {22.161, 0.25}, {22.161, 0.21}}, 
    color = {0, 127, 255}));
  connect(pressureSensor.p, add.u1) 
    annotation(Line(origin = {-166.5, 131.946}, 
    points = {{6, -166}, {15.5, -166}, {15.5, -153.946}}, 
    color = {0, 0, 127}));
  connect(add.u2, pressureSensor1.p) 
    annotation(Line(origin = {-131.5, 123.946}, 
    points = {{-7.5, -145.946}, {-7.5, -158}, {0.5, -158}}, 
    color = {0, 0, 127}));
  connect(add.y, combiTable1Dv.u) 
    annotation(Line(origin = {-150.25, 94.946}, 
    points = {{5.25, -93.946}, {5.25, -89}}, 
    color = {0, 0, 127}));
  connect(combiTable1Dv.y[1], idealFan.massFlow) 
    annotation(Line(origin = {-159, 50.946}, 
    points = {{14, -22}, {14, -13.754}}, 
    color = {0, 0, 127}));
  connect(flowSplit.port_b[1], idealFan.port_a) 
    annotation(Line(origin = {-166, 41.946}, 
    points = {{0, 4}, {11, 4}, {11, 3.946}}, 
    color = {0, 127, 255}));
  connect(idealFan.port_b, flowSplit1.port_b[1]) 
    annotation(Line(origin = {-149, 41.946}, 
    points = {{14, 3.946}, {25, 3.946}}, 
    color = {0, 127, 255}));
  connect(pressureSensor.port_a, flowSplit.port_b[2]) 
    annotation(Line(origin = {-190, 84.946}, 
    points = {{18.5, -109}, {18.5, -39}, {24, -39}}, 
    color = {0, 127, 255}));
  connect(pressureSensor1.port_a, flowSplit1.port_b[2]) 
    annotation(Line(origin = {-143, 76.946}, 
    points = {{23, -101}, {23, -31.054}, {19, -31.054}}, 
    color = {0, 127, 255}));
  connect(volume_pTX2.b[1], duct.port_a) 
    annotation(Line(origin = {-41, 45.946}, 
    points = {{6.839, -0.094}, {13, -0.094}, {13, 0}}, 
    color = {0, 127, 255}));
  connect(flowSplit1.port_a, volume_pTX4.a[1]) 
    annotation(Line(origin = {-99, 45.696}, 
    points = {{-5, 0.196}, {5.161, 0.196}, {5.161, 0.088}}, 
    color = {0, 127, 255}));
  connect(volume_pTX4.b[1], cooledAirDryer.port_a) 
    annotation(Line(origin = {-77, 45.696}, 
    points = {{-5.161, 0.102}, {5, 0.102}, {5, 0.142}}, 
    color = {0, 127, 255}));
  connect(mdotSource.fluidPort, flowSplit.port_a) 
    annotation(Line(origin = {-208, 45.838}, 
    points = {{9.148, 0.108}, {22, 0.108}}, 
    color = {0, 127, 255}));
  connect(pressureSource.fluidPort, duct1.port_b) 
    annotation(Line(origin = {-174, -66.162}, 
    points = {{-24.852, -0.142}, {56, -0.142}}, 
    color = {0, 127, 255}));
end DehumidificationSystem;