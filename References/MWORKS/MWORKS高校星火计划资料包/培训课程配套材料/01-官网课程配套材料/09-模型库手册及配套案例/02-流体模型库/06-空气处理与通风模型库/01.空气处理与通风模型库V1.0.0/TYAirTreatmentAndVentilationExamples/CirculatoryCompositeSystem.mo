model CirculatoryCompositeSystem "循环复合系统"
  annotation(Documentation(link = "modelica://TYAirTreatmentAndVentilation/Resources/Examples/CirculatoryCompositeSystem.html"), 
  Icon(coordinateSystem(extent = {{-100, -100}, {100, 100}}, 
    grid = {0.01, 0.01}), graphics = {Polygon(origin = {-7.10543e-15, 33}, 
    lineColor = {0, 94, 138}, 
    fillColor = {0, 94, 138}, 
    fillPattern = FillPattern.Solid, 
    points = {{-64, 1}, {0, 37}, {64, 1}, {0, -37}}), Line(origin = {0, -12}, 
    points = {{-62, 18}, {0, -18}, {62, 18}}, 
    color = {0, 94, 138}, 
    thickness = 5), Line(origin = {7.10543e-15, -40}, 
    points = {{-62, 18}, {0, -18}, {62, 18}}, 
    color = {0, 94, 138}, 
    thickness = 5)}), Diagram(coordinateSystem(extent = {{-100, -100}, {100, 100}}, 
    grid = {2, 2})), experiment(Algorithm = Dassl, InlineIntegrator = false, InlineStepSize = false, Interval = 0.01, StartTime = 0, StopTime = 10, Tolerance = 0.0001), __MWORKS(ContinueSimConfig(SaveContinueFile = "false", SaveBeforeStop = "false", NumberBeforeStop = 1, FixedContinueInterval = "false", ContinueIntervalLength = 0.09, ContinueTimeVector),ResultViewerManager(resultViewers={
ResultViewer(name="1", executeTrigger=executeTrigger.SimulationFinished, commands={
CreatePlot(id=3, x_display_unit="s", legend_layout=1, left_title_type=2, left_title="温度[degC]", bottom_title_type=2, bottom_title="时间[s]", right_title_type=2, fix_time_range_value=0, zoom_x=(0, 10), zoom_y_l=(18, 30)), 
Plot(legend=["室内温度 [degC]"], y=["room.T"], colors=["4278190335"]), 
CreatePlot(id=-1, x_display_unit="s", legend_layout=1, left_title_type=2, left_title="水蒸气含量[1]", bottom_title_type=2, bottom_title="时间/s", right_title_type=2, fix_time_range_value=0, sub_plot=(2, 1), zoom_x=(0, 10), zoom_y_l=(0.008, 0.018)), 
Plot(legend=["加湿前[kg/kg]", "加湿后 [kg/kg]"], y=["volume_pTX4.X[2]", "volume_pTX2.X[2]"], colors=["4278190335", "4294901760"])})
})),Protection(access=Access.nonPackageDuplicate));
  TYAirTreatmentAndVentilation.HeatExchangers.GenericHeatExchanger genericHeatExchanger(redeclare package PrimaryMedium = TYAirTreatmentAndVentilation.Media.MoistAir, redeclare package SecondaryMedium = TYAirTreatmentAndVentilation.Media.MoistAir, epsset=0.85, redeclare model Friction_prim = TYAirTreatmentAndVentilation.HeatExchangers.Basics.Dp_NTU.LinearOperatingPointLoss, redeclare model Friction_sec = TYAirTreatmentAndVentilation.HeatExchangers.Basics.Dp_NTU.LinearOperatingPointLoss, Q_flow_kind="换热效率", redeclare model HeatTransfer_prim = TYAirTreatmentAndVentilation.HeatExchangers.Basics.HT_NTU.ConstantCoefficient, redeclare model HeatTransfer_sec = TYAirTreatmentAndVentilation.HeatExchangers.Basics.HT_NTU.ConstantCoefficient, Dhyd_prim=1, Dhyd_sec=1, L_prim(displayUnit="mm")=0.1, L_sec(displayUnit="mm")=0.1, thickness_wall(displayUnit="mm")=0.001, redeclare function epsFun = TYAirTreatmentAndVentilation.Utilities.Functions.HeatTransfer.counterFlowEps) 
    annotation(Placement(transformation(origin = {-116.5, 34.5}, 
    extent = {{-10, -10}, {10, 10}})));
  TYAirTreatmentAndVentilation.Sources.PressureSource mdotSource(redeclare package Medium = TYAirTreatmentAndVentilation.Media.MoistAir, redeclare model MediumType = TYAirTreatmentAndVentilation.Auxiliaries.Basics.MixtureGasesMedium, T=258.15, p=1.013e5) 
    annotation(Placement(transformation(origin = {-171.5, 40.5}, 
    extent = {{-10, -10}, {10, 10}})));
  TYAirTreatmentAndVentilation.Auxiliaries.Volume_pTX volume_pTX2(redeclare package Medium = TYAirTreatmentAndVentilation.Media.MoistAir, V_tot=0.001, redeclare model MediumType = TYAirTreatmentAndVentilation.Auxiliaries.Basics.MixtureGasesMedium) 
    annotation(Placement(transformation(origin = {35.5, 40.5}, 
    extent = {{-10, -10}, {10, 10}})));
  TYAirTreatmentAndVentilation.HeatExchangers.GenericHeatExchanger genericHeatExchanger1(redeclare package PrimaryMedium = TYAirTreatmentAndVentilation.Media.MoistAir, redeclare package SecondaryMedium = Modelica.Media.Air.DryAirNasa, redeclare model Friction_prim = TYAirTreatmentAndVentilation.HeatExchangers.Basics.Dp_NTU.LinearOperatingPointLoss, redeclare model Friction_sec = TYAirTreatmentAndVentilation.HeatExchangers.Basics.Dp_NTU.LinearOperatingPointLoss, epsset=0.85, Dhyd_prim=1, L_prim(displayUnit="mm")=0.1, L_sec(displayUnit="mm")=0.1, Dhyd_sec=1, thickness_wall(displayUnit="mm")=0.001, redeclare model HeatTransfer_prim = TYAirTreatmentAndVentilation.HeatExchangers.Basics.HT_NTU.ConstantCoefficient, redeclare model HeatTransfer_sec = TYAirTreatmentAndVentilation.HeatExchangers.Basics.HT_NTU.ConstantCoefficient, redeclare function epsFun = TYAirTreatmentAndVentilation.Utilities.Functions.HeatTransfer.counterFlowEps, effectivenessStreamChoice=TYAirTreatmentAndVentilation.Utilities.Types.EffectivenessStreamChoice.Min, Q_flow_kind="换热效率") 
    annotation(Placement(transformation(origin = {64.5, 46.5}, 
    extent = {{-10, 10}, {10, -10}})));
  TYAirTreatmentAndVentilation.Sources.PressureSource pressureSource(redeclare package Medium = TYAirTreatmentAndVentilation.Media.MoistAir, redeclare model MediumType = TYAirTreatmentAndVentilation.Auxiliaries.Basics.MixtureGasesMedium, p=100000, T=293.15) 
    annotation(Placement(transformation(origin = {-171.5, -71.75}, 
    extent = {{-10, -10}, {10, 10}})));
  TYAirTreatmentAndVentilation.Sources.PressureSource mdotSource1(redeclare package Medium = Modelica.Media.Air.DryAirNasa, redeclare model MediumType = TYAirTreatmentAndVentilation.Auxiliaries.Basics.IdealGasesMedium, T=303.15) 
    annotation(Placement(transformation(origin = {156, 77.5}, 
    extent = {{10, -10}, {-10, 10}})));
  TYAirTreatmentAndVentilation.Auxiliaries.Volume_pTX volume_pTX3(redeclare package Medium = Modelica.Media.Air.DryAirNasa, V_tot=0.001, redeclare model MediumType = TYAirTreatmentAndVentilation.Auxiliaries.Basics.IdealGasesMedium) 
    annotation(Placement(transformation(origin = {102.5, 77.5}, 
    extent = {{10, -10}, {-10, 10}})));
  TYAirTreatmentAndVentilation.Sources.PressureSource pressureSource1(redeclare package Medium = Modelica.Media.Air.DryAirNasa, redeclare model MediumType = TYAirTreatmentAndVentilation.Auxiliaries.Basics.IdealGasesMedium, T=303.15) 
    annotation(Placement(transformation(origin = {6.5, 77.5}, 
    extent = {{-10, -10}, {10, 10}})));
  TYAirTreatmentAndVentilation.Auxiliaries.Volume_pTX volume_pTX5(redeclare package Medium = TYAirTreatmentAndVentilation.Media.MoistAir, V_tot=0.392, redeclare model MediumType = TYAirTreatmentAndVentilation.Auxiliaries.Basics.MixtureGasesMedium) 
    annotation(Placement(transformation(origin = {93.5, 40.5}, 
    extent = {{10, -10}, {-10, 10}})));
  TYAirTreatmentAndVentilation.Auxiliaries.Volume_pTX volume_pTX1(redeclare package Medium = TYAirTreatmentAndVentilation.Media.MoistAir, V_tot=0.001, redeclare model MediumType = TYAirTreatmentAndVentilation.Auxiliaries.Basics.MixtureGasesMedium, T0=305.15) 
    annotation(Placement(transformation(origin = {-86.75, 40.5}, 
    extent = {{-10, -10}, {10, 10}})));
  TYAirTreatmentAndVentilation.AirTreatment.Humidifier humidifier(redeclare package Medium = TYAirTreatmentAndVentilation.Media.MoistAir, m_flow_set=1, A(displayUnit="m2")=5, redeclare model MediumType = TYAirTreatmentAndVentilation.Auxiliaries.Basics.MixtureGasesMedium) 
    annotation(Placement(transformation(origin = {6.5, 40.5}, 
    extent = {{-10, -10}, {10, 10}})));
  TYAirTreatmentAndVentilation.Pipes.Duct_RC duct_RC1(redeclare model MediumType = TYAirTreatmentAndVentilation.Auxiliaries.Basics.MixtureGasesMedium, redeclare package Medium = TYAirTreatmentAndVentilation.Media.MoistAir, D=0.5, L=4) 
    annotation(Placement(transformation(origin = {-44.5, -71.75}, 
    extent = {{10, -10}, {-10, 10}})));
  TYAirTreatmentAndVentilation.Auxiliaries.Volume_pTX room(redeclare package Medium = TYAirTreatmentAndVentilation.Media.MoistAir, V_tot(displayUnit="m3")=1.785, redeclare model MediumType = TYAirTreatmentAndVentilation.Auxiliaries.Basics.MixtureGasesMedium) 
    annotation(Placement(transformation(origin = {64.5, -71.75}, 
    extent = {{10, -10}, {-10, 10}})));
  TYAirTreatmentAndVentilation.Pipes.Duct duct(D=0.5, L=4, redeclare model MediumType = TYAirTreatmentAndVentilation.Auxiliaries.Basics.MixtureGasesMedium, redeclare package Medium = TYAirTreatmentAndVentilation.Media.MoistAir) 
    annotation(Placement(transformation(origin = {129.25, 40.5}, 
    extent = {{-10, -10}, {10, 10}})));
  TYAirTreatmentAndVentilation.Auxiliaries.DisplayAirState displayAirState(redeclare package Medium = TYAirTreatmentAndVentilation.Media.MoistAir, redeclare model MediumType = TYAirTreatmentAndVentilation.Auxiliaries.Basics.MixtureGasesMedium) 
    annotation(Placement(transformation(origin = {42, -23}, 
    extent = {{-32, -29}, {32, 29}})));
  TYAirTreatmentAndVentilation.CompressorsAndFans.IdealFan idealFan(use_mflow_in=false, m_flow=1.567, redeclare model MediumType = TYAirTreatmentAndVentilation.Auxiliaries.Basics.MixtureGasesMedium, redeclare package Medium = TYAirTreatmentAndVentilation.Media.MoistAir) 
    annotation(Placement(transformation(origin = {-57, 40.5}, 
    extent = {{-10, -10}, {10, 10}}, 
    rotation = -90)));
  TYAirTreatmentAndVentilation.Auxiliaries.Volume_pTX volume_pTX4(redeclare package Medium = TYAirTreatmentAndVentilation.Media.MoistAir, V_tot=0.001, redeclare model MediumType = TYAirTreatmentAndVentilation.Auxiliaries.Basics.MixtureGasesMedium, T0=293.15) 
    annotation(Placement(transformation(origin = {-22.5, 40.5}, 
    extent = {{-10, -10}, {10, 10}})));
  TYAirTreatmentAndVentilation.CompressorsAndFans.IdealFan idealFan1(use_mflow_in=false, m_flow=1.805, redeclare model MediumType = TYAirTreatmentAndVentilation.Auxiliaries.Basics.IdealGasesMedium, redeclare package Medium = Modelica.Media.Air.DryAirNasa) 
    annotation(Placement(transformation(origin = {129.25, 77.5}, 
    extent = {{10, -10}, {-10, 10}}, 
    rotation = 90)));
equation
  connect(volume_pTX2.b[1], genericHeatExchanger1.portA_primary) 
    annotation(Line(origin = {45.5, 40.5}, 
    points = {{-4.161, -0.04}, {9, -0.04}, {9, 0}}, 
    color = {0, 127, 255}));
  connect(genericHeatExchanger1.portB_primary, volume_pTX5.b[1]) 
    annotation(Line(origin = {83.5, 40.5}, 
    points = {{-9, 0}, {4.161, 0}, {4.161, -0.04}}, 
    color = {0, 127, 255}));
  connect(volume_pTX3.b[1], genericHeatExchanger1.portA_secondary) 
    annotation(Line(origin = {51.5, 66.5}, 
    points = {{45.161, 10.96}, {29, 10.96}, {29, -14}, {23, -14}}, 
    color = {0, 127, 255}));
  connect(genericHeatExchanger1.portB_secondary, pressureSource1.fluidPort) 
    annotation(Line(origin = {94.5, 66.5}, 
    points = {{-40, -14}, {-51, -14}, {-51, 11}, {-79.852, 11}}, 
    color = {0, 127, 255}));
  connect(pressureSource.fluidPort, genericHeatExchanger.portB_secondary) 
    annotation(Line(origin = {-164.5, -6.5}, 
    points = {{1.148, -65.25}, {26.5, -65.25}, {26.5, 35}, {38, 35}}, 
    color = {0, 127, 255}));
  connect(genericHeatExchanger.portB_primary, volume_pTX1.a[1]) 
    annotation(Line(origin = {-110.5, 40.5}, 
    points = {{4, 0}, {17.911, 0}, {17.911, -0.054}}, 
    color = {0, 127, 255}));
  connect(humidifier.port_b, volume_pTX2.a[1]) 
    annotation(Line(origin = {-11.5, 40.5}, 
    points = {{28, 0}, {41.161, 0}, {41.161, -0.054}}, 
    color = {0, 127, 255}));
  connect(duct_RC1.port_a, room.b[1]) 
    annotation(Line(origin = {125.5, -71.75}, 
    points = {{-160, 0}, {-66.839, 0}, {-66.839, -0.04}}, 
    color = {0, 127, 255}));
  connect(volume_pTX5.a[1], duct.port_a) 
    annotation(Line(origin = {122.5, 40.5}, 
    points = {{-23.161, -0.054}, {-3.25, -0.054}, {-3.25, 0}}, 
    color = {0, 127, 255}));
  connect(duct.port_b, room.a[1]) 
    annotation(Line(origin = {163.5, -0.5}, 
    points = {{-24.25, 41}, {-12, 41}, {-12, -71.304}, {-93.161, -71.304}}, 
    color = {0, 127, 255}));
  connect(room.b[1], displayAirState.port_a) 
    annotation(Line(origin = {136.5, 21.25}, 
    points = {{-77.839, -93.04}, {-81.5, -93.04}, {-81.5, -79.25}}, 
    color = {0, 127, 255}));
  connect(volume_pTX1.b[1], idealFan.port_a) 
    annotation(Line(origin = {-65.5, 40.5}, 
    points = {{-15.411, -0.04}, {-1.5, -0.04}, {-1.5, 0}}, 
    color = {0, 127, 255}));
  connect(idealFan.port_b, volume_pTX4.a[1]) 
    annotation(Line(origin = {-35.5, 40.5}, 
    points = {{-11.5, 0}, {7.161, 0}, {7.161, -0.054}}, 
    color = {0, 127, 255}));
  connect(volume_pTX4.b[1], humidifier.port_a) 
    annotation(Line(origin = {-7.5, 40.5}, 
    points = {{-9.161, -0.04}, {4, -0.04}, {4, 0}}, 
    color = {0, 127, 255}));
  connect(volume_pTX3.a[1], idealFan1.port_b) 
    annotation(Line(origin = {100.5, 59.5}, 
    points = {{7.839, 17.946}, {18.75, 17.946}, {18.75, 18}}, 
    color = {0, 127, 255}));
  connect(idealFan1.port_a, mdotSource1.fluidPort) 
    annotation(Line(origin = {149.5, 59.5}, 
    points = {{-10.25, 18}, {-1.648, 18}}, 
    color = {0, 127, 255}));
  connect(mdotSource.fluidPort, genericHeatExchanger.portA_primary) 
    annotation(Line(origin = {-145, 41}, 
    points = {{-18.352, -0.5}, {18.5, -0.5}}, 
    color = {0, 127, 255}));
  connect(genericHeatExchanger.portA_secondary, duct_RC1.port_b) 
    annotation(Line(origin = {-80, -22}, 
    points = {{-26.5, 50.5}, {-16, 50.5}, {-16, -49.75}, {25.5, -49.75}}, 
    color = {0, 127, 255}));
end CirculatoryCompositeSystem;