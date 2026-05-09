model HtrLoop "PTC制热回路"
  parameter Real HtrPump_rpm = 1000 "暖芯水泵转速（转/分钟）";
  parameter Real BattPump_rpm = 1000 "电池水泵转速（转/分钟）";
  parameter SI.Temperature T_out = 283.15 "外部温度";
  parameter SI.Temperature T_in = 283.15 "内部温度";
  parameter SI.Temperature T_Amb = 283.15 "环境温度";
  parameter SI.Power Q_flow = 1000 "PTC制热量";
  parameter Real valve_pos=0.5 "比例三通阀位置0~1之间";
  annotation(experiment(Algorithm=Dassl,StartTime=0,StopTime=1000,Tolerance=0.0001,Interval=1),
    Icon(coordinateSystem(extent = {{-100.0, -100.0}, {100.0, 100.0}},
    grid = {2.0, 2.0}), graphics = {Bitmap(origin = {0.0, 0.0},
    extent = {{-100.0, -100.0}, {100.0, 100.0}},
    fileName = "modelica://TAThermalSystem/Resource/Icons/Example.svg")}),
    Protection(access=Access.nonPackageDuplicate),
    Diagram(coordinateSystem(extent={{128,-100},{560,120}},
grid={2,2})),
    Documentation(link="modelica://TAThermalSystem/Resource/Doc/HtrLoop.html"
),__MWORKS(ContinueSimConfig(SaveContinueFile="false",SaveBeforeStop="false",NumberBeforeStop=1,FixedContinueInterval="false",ContinueIntervalLength=0.4),ResultViewerManager(resultViewers={
ResultViewer(name="1", executeTrigger=executeTrigger.SimulationStarted, commands={
CreatePlot(id=1, x_display_unit="s", legend_layout=7, left_title="[degC]", fix_time_range_value=0, zoom_x=(0, 1000), zoom_y_l=(5, 35)),
Plot(y=["water_air_HXTU2.hXSummary.Ta_in", "water_air_HXTU2.hXSummary.Tb_out", "water_air_HXTU2.hXSummary.Tc_in", "water_air_HXTU2.hXSummary.Td_out"], thicknesses=[2, 2, 2, 2], colors=["4278190335", "4294901760", "4278222848", "4294902015"]),
CreatePlot(id=-1, x_display_unit="s", legend_layout=7, left_title="[degC]", fix_time_range_value=0, sub_plot=(1, 2), zoom_x=(0, 1000), zoom_y_l=(0, 70)),
Plot(y=["coolingPipeDS.pipeSummary.T_in", "coolingPipeDS.pipeSummary.T_out", "batteryQIn.Batt_top[1].T"], thicknesses=[2, 2, 2], colors=["4278190335", "4294901760", "4278222848"])})
})));
  import SI = Modelica.SIunits;
  annotation(Diagram(coordinateSystem(extent = {{-290.0, -290.0}, {530.0, 100.0}},
    grid = {2.0, 2.0})));
  TAThermalSystem.Pipes.LiquidCoolingPipe.CoolingPipeDS coolingPipeDS(n = 3, title = "水管道", Dhyd = 0.025, Aheat = 0.1918,
    p0 = 2.5e5, T0 = T_Amb) 
    annotation(Placement(transformation(origin = {461.83450887158216, 40.82635193156388},
    extent = {{10.0469483144355, -10.008632925201297}, {-10.011048314435497, 10.010082025725545}},
    rotation = -90.0)));
  Modelica.Blocks.Sources.RealExpression realExpression7(y = BattPump_rpm* Modelica.Constants.pi / 30) 
    annotation(Placement(transformation(origin = {427.84314179678347, -85.85528317797113},
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  Modelica.Mechanics.Rotational.Sources.Speed speed4 
    annotation(Placement(transformation(origin = {461.84314179678347, -85.85528317797113},
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TAThermalSystem.PumpAndFan.CentrifugalPump centrifugal_pump4(T_inlet(start = T_Amb), T_outlet(start = T_Amb), T_start = T_Amb, pin_start = 90000, pout_start = 3e5, m_flow_start = 0.1) 
    annotation(Placement(transformation(origin = {461.84314179678347, -28.743899631000968},
    extent = {{-10.0, -10.0}, {10.0, 10.0}},
    rotation = -270.0)));
  TYBase.Battery.Model.BatteryQIn batteryQIn(N_cells = 3, chargeResTable = {{10, 0.2}, {20, 0.2}, {30, 0.2}, {40, 0.2}, {50, 0.2}, {60, 0.2}, {70, 0.2}, {80, 0.2}, {90, 0.2}}, dischargeResTable = {{10, 0.2}, {20, 0.2}, {30, 0.2}, {40, 0.2}, {50, 0.2}, {60, 0.2}, {70, 0.2}, {80, 0.2}, {90, 0.2}}, Ns = 96, Np = 2, QCellNominal = 33, C = 2000) 
    annotation(Placement(transformation(origin = {514.0, 21.535821142190734},
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYBase.Battery.Component.Ground ground annotation(HideResult = true, Placement(transformation(origin = {537.0592389275064, -42.34017313687912},
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  Modelica.Electrical.Analog.Sources.ConstantCurrent constantCurrent(I = 66 * 2) 
    annotation(Placement(transformation(origin = {514.0, -17.619073907354434},
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  Modelica.Blocks.Sources.RealExpression realExpression9(y = HtrPump_rpm* Modelica.Constants.pi / 30) 
    annotation(Placement(transformation(origin = {153.00000000000006, 47.49910621292886},
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  Modelica.Mechanics.Rotational.Sources.Speed speed5 
    annotation(Placement(transformation(origin = {187.00000000000003, 47.49910621292886},
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TAThermalSystem.PumpAndFan.CentrifugalPump centrifugal_pump5(T_inlet(start = T_Amb), T_outlet(start = T_Amb), T_start = T_Amb, pin_start = 90000, pout_start = 3e5, m_flow_start = 0.1) 
    annotation(Placement(transformation(origin = {224.95392582812806, 47.499106212928865},
    extent = {{-10.0, -10.0}, {10.0, 10.0}},
    rotation = 270.0)));
  TAThermalSystem.Valves.HydraulicValve.ValveFlowKvCooling valveFlowKvCooling4(Tin(start = T_Amb), Tout(start = T_Amb), Kv_curve = {{0.0, 0}, {0.01, 0.1}, {0.1, 1}, {0.2, 3}, {0.4, 5}, {0.6, 6}, {0.8, 7}, {1.0, 20}, {1.1, 20}}) 
    annotation(Placement(transformation(origin = {278.51293538889513, -15.1269298161921},
    extent = {{-10.0, -10.0}, {10.0, 10.0}},
    rotation = 90.0)));
  TAThermalSystem.Valves.HydraulicValve.ValveFlowKvCooling valveFlowKvCooling5(Tin(start = T_Amb), Tout(start = T_Amb), Kv_curve = {{0.0, 0}, {0.01, 0.1}, {0.1, 1}, {0.2, 3}, {0.4, 5}, {0.6, 6}, {0.8, 7}, {1.0, 20}, {1.1, 20}}) 
    annotation(Placement(transformation(origin = {304.3608365469133, -57.88154054335247},
    extent = {{10.0, -10.0}, {-10.0, 10.0}},
    rotation = 180.0)));
  Modelica.Blocks.Sources.RealExpression realExpression13(y = valve_pos) 
    annotation(Placement(transformation(origin = {281.63964983317715, -90.0003582720733},
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  Modelica.Blocks.Sources.RealExpression realExpression14(y = 1-valve_pos) 
    annotation(Placement(transformation(origin = {251.97100168556452, -15.1269298161921},
    extent = {{-10.028998314435484, -8.327504942257882}, {10.028998314435512, 8.327504942257882}})));
  TAThermalSystem.Reservoirs.ExpansionTank expansion_tank1(tank1(
    pInitial = 0.9e5),
    T_Amb = T_Amb,
    zetaFlowCooling9(FromDp = false),zeta=200) 

    annotation(Placement(transformation(origin = {384.0000000000001, -57.84376651299833},
    extent = {{10.0, -10.0}, {-10.0, 10.0}})));
  TAThermalSystem.Pipes.LiquidCoolingPipe.CoolingPipeR coolingPipe(p0 = 2.2e5, T0 = T_Amb) annotation(Placement(transformation(origin = {239.86065193929176, -57.974580543352474},
    extent = {{-10.0997, -8.821720000000001}, {10.0638, 9.007800000000001}})));

  TAThermalSystem.Pipes.LiquidCoolingPipe.CoolingPipe coolingPipe1(useHeatTransfer = false, p0 = 90000, T0 = T_Amb) 
    annotation(Placement(transformation(origin = {248.0997, 82.2747432033189},
    extent = {{10.0997, -8.821720000000001}, {-10.0638, 9.007800000000001}})));
  TAThermalSystem.Sources.Air.AirSource_mT airSource2(
    m = 0.2, T = T_in,
    phi_source = 0.4) annotation(Placement(transformation(origin = {180.9999999999999, -56.79630054335247},
    extent = {{-10, -10}, {10, 10}})));
  TAThermalSystem.Sources.Air.AirSink_pT airSink2(redeclare package Medium = TYBase.Media_Extend.Air.MoistAir, T_sink = T_in,
    phi_sink = 0.2) annotation(Placement(transformation(origin = {180.9999999999999, -15.1269298161921},
    extent = {{-10, -10}, {10, 10}})));
  TAThermalSystem.Sources.HeatTransfer.BoundaryHeatFlow boundaryHeatFlow7(Q_flow = Q_flow, n = 1) 
    annotation(Placement(transformation(origin = {180.9999999999999, 15.499106212928844},
    extent = {{10.0, -10.0}, {-10.0, 10.0}},
    rotation = 180.0)));
  TAThermalSystem.HeatExchangers.CoolingRadiatorNTU.Water_Air_HXNTU water_air_HXTU2(
    ConsiderMass = false, redeclare model Friction_ab = TYBase.Thermal.FluidHeatFlow.PressureLoss.HXPressureDrop.SingularPressureDrop, Across1(displayUnit = "cm2") = 0.01, Dhyd1(displayUnit = "mm") = 0.01, cearea1(displayUnit = "m2") = 5, ConsiderationFins_cd = false,
    etas2 = 0.8, ConsiderationFins_ab = false,  fromDp = false,
    T1_a(start = T_Amb), T1_b(start = T_Amb), T2_in(start = T_Amb), T2_out(start = T_Amb), Twall(start = T_Amb),
    L = 2, Across2 = 0.05, cearea2(displayUnit = "m2") = 8) 
    annotation(Placement(transformation(origin = {219.08295797427448, -34.74389963100096},
    extent = {{-10.0, -10.0}, {10.0, 10.0}},
    rotation = 270.0)));
  TAThermalSystem.Pipes.LiquidCoolingPipe.CoolingPipeCR coolingPipeCR(p0 = 2.5e5, T0 = T_Amb) annotation(Placement(transformation(origin = {225.04696582812807, 14.922066152787217},
    extent = {{10.0997, -8.821720000000001}, {-10.0638, 9.007800000000001}},
    rotation = 90.0)));



  TAThermalSystem.Pipes.LiquidCoolingPipe.CoolingPipeR coolingPipeC(T0 = T_Amb) annotation(Placement(transformation(origin = {354.97089489932324, 11.978892636597287},
    extent = {{-10.0997, -8.821720000000001}, {10.0638, 9.007800000000001}},
    rotation = 90)));
  TYBase.Thermal.FluidHeatFlow.ControlVolumes.CVBasic.ThermalHydraulicCV.BranchPipeCoolingCV branchPipeCoolingCV6(p0 = 1.5e5,
    T0 = T_Amb) 
    annotation(Placement(transformation(origin = {355.5134856242171, -57.338886398874365},
    extent = {{-8.169727718157175, 8.435625744212741}, {8.663445506049522, -8.219384140303024}})));
  TYBase.Thermal.FluidHeatFlow.ControlVolumes.CVBasic.ThermalHydraulicCV.BranchPipeCoolingCV branchPipeCoolingCV7(p0 = 2e5,
    T0 = T_Amb) 
    annotation(Placement(transformation(origin = {277.96136440288103, -59.419053796018325},
    extent = {{-8.169727718157175, 8.435625744212741}, {8.663445506049522, -8.219384140303024}})));
  TYBase.Thermal.FluidHeatFlow.ControlVolumes.CVBasic.ThermalHydraulicCV.BranchPipeCoolingCV branchPipeCoolingCV8(p0 = 100000,
    T0 = T_Amb) 
    annotation(Placement(transformation(origin = {279.15810959131153, 82.37948961621989},
    extent = {{-8.169727718157175, -8.435625744212741}, {8.663445506049522, 8.219384140303024}})));
  TYBase.Thermal.FluidHeatFlow.ControlVolumes.CVBasic.ThermalHydraulicCV.BranchPipeCoolingCV branchPipeCoolingCV9(p0 = 1.4e5,
    T0 = T_Amb) 
    annotation(Placement(transformation(origin = {355.12916939327374, 81.26077167206894},
    extent = {{-8.169727718157175, -8.435625744212741}, {8.663445506049522, 8.219384140303024}})));
equation
  connect(realExpression7.y, speed4.w_ref) 
    annotation(Line(origin = {441.84314179678347, -85.85528317797112},
    points = {{-3.0, 0.0}, {8.0, 0.0}},
    color = {0, 0, 127}));
  connect(speed4.flange, centrifugal_pump4.flange) 
    annotation(Line(origin = {472, -74.10195288816338},
    points = {{-0.15685820321652955, -11.75333028980775}, {18, -11.75333028980775}, {18, 45.35805325716241}, {-0.15685820321652955, 45.35805325716241}},
    color = {0, 0, 0}));
  connect(centrifugal_pump4.b, coolingPipeDS.a) 
    annotation(Line(origin = {470.0, 11.837400245999376},
    points = {{-8.0, -30.0}, {-8.0, 19.0}},
    color = {0, 170, 255},
    thickness = 1.0));
  connect(coolingPipeDS.qa, batteryQIn.Batt_top) 
    annotation(Line(origin = {498.0, 35.837400245999376},
    points = {{-26.0, 5.0}, {26.0, 5.0}, {26.0, -5.0}},
    color = {191, 0, 0},
    thickness = 1.0));
  connect(batteryQIn.pin_p, constantCurrent.p) 
    annotation(Line(origin = {503.0, -0.16259975400062743},
    points = {{1.0, 22.0}, {-4.0, 22.0}, {-4.0, -17.0}, {1.0, -17.0}},
    color = {0, 0, 255}));
  connect(batteryQIn.pin_n, constantCurrent.n) 
    annotation(Line(origin = {524.0, 2.8374002459993726},
    points = {{0.0, 19.0}, {10.0, 19.0}, {10.0, -20.0}, {0.0, -20.0}},
    color = {0, 0, 255}));
  connect(ground.p, batteryQIn.pin_n) 
    annotation(Line(origin = {531.0, -5.162599754000627},
    points = {{6.0, -27.0}, {6.0, 27.0}, {-7.0, 27.0}},
    color = {0, 0, 255}));
  connect(realExpression9.y, speed5.w_ref) 
    annotation(Line(origin = {167.00000000000009, 47.499106212928865},
    points = {{-3.0, 0.0}, {8.0, 0.0}},
    color = {0, 0, 127}));
  connect(centrifugal_pump5.flange, speed5.flange) 
    annotation(Line(origin = {219.9539258281281, 22.499106212928833},
    points = {{-5.0, 25.0}, {-23.0, 25.0}},
    color = {0, 0, 0}));
  connect(valveFlowKvCooling4.u, realExpression14.y) 
    annotation(Line(origin = {253.48934187562264, -35},
    points = {{15.023593513272488, 19.8730701838079}, {9.513557955820943, 19.8730701838079}},
    color = {0, 0, 127}));
  connect(valveFlowKvCooling5.u, realExpression13.y) 
    annotation(Line(origin = {284.0, -69.0},
    points = {{20.0, 1.0}, {20.0, -21.0}, {9.0, -21.0}},
    color = {0, 0, 127}));
  connect(expansion_tank1.b, centrifugal_pump4.a) 
    annotation(Line(origin = {428.0, -48.0},
    points = {{-34.0, -10.0}, {34.0, -10.0}, {34.0, 9.0}},
    color = {0, 170, 255},
    thickness = 1.0));
  connect(water_air_HXTU2.c, airSource2.port_b) 
    annotation(Line(origin = {202.08295797427448, -50.124825723646524},
    points = {{10.962597554546448, 5.269020518979502}, {10.962597554546448, -6.671474819705949}, {-11.082957974274592, -6.671474819705949}},
    color = {0, 232, 232},
    thickness = 1));
  connect(water_air_HXTU2.d, airSink2.port_a) 
    annotation(Line(origin = {202, -5},
    points = {{10.926591933836619, -19.780698551065278}, {10.926591933836619, -10.1269298161921}, {-11.000000000000114, -10.1269298161921}},
    color = {0, 232, 232},
    thickness = 1));
  connect(water_air_HXTU2.b, coolingPipe.a) 
    annotation(Line(origin = {228.0, -43.0},
    points = {{-3.0, -2.0}, {-3.0, -15.0}, {2.0, -15.0}},
    color = {0, 170, 255},
    thickness = 1.0));
  connect(centrifugal_pump5.b, coolingPipeCR.a) 
    annotation(Line(origin = {225.0, 32.0},
    points = {{0.0, 5.0}, {0.0, -7.0}},
    color = {0, 170, 255},
    thickness = 1.0));
  connect(coolingPipeCR.b, water_air_HXTU2.a) 
    annotation(Line(origin = {225.0, -10.0},
    points = {{0.0, 15.0}, {0.0, -15.0}},
    color = {0, 170, 255},
    thickness = 1.0));
  connect(coolingPipe1.b, centrifugal_pump5.a) 
    annotation(Line(origin = {232.0, 70.0},
    points = {{6.0, 12.0}, {-8.0, 12.0}, {-8.0, -12.0}, {-7.0, -12.0}},
    color = {0, 170, 255},
    thickness = 1.0));
  connect(valveFlowKvCooling5.b, branchPipeCoolingCV6.a) 
    annotation(Line(origin = {323.0, -58.0},
    points = {{-9.0, 0.0}, {23.0, 0.0}, {23.0, 1.0}},
    color = {0, 170, 255},
    thickness = 1.0));
  connect(branchPipeCoolingCV6.c, expansion_tank1.a) 
    annotation(Line(origin = {368.0, -58.0},
    points = {{-2.0, 1.0}, {6.0, 1.0}, {6.0, 0.0}},
    color = {0, 170, 255},
    thickness = 1.0));
  connect(branchPipeCoolingCV6.b, coolingPipeC.a) 
    annotation(Line(origin = {356, -25},
    points = {{-0.48651437578291734, -22.338886398874365}, {-0.48651437578291734, 26.96877459275243}, {-0.9913310703226443, 26.96877459275243}},
    color = {0, 170, 255},
    thickness = 1));
  connect(coolingPipe.b, branchPipeCoolingCV7.a) 
    annotation(Line(origin = {253.0, -58.0},
    points = {{-3.0, 0.0}, {15.0, 0.0}, {15.0, -1.0}},
    color = {0, 170, 255},
    thickness = 1.0));
  connect(branchPipeCoolingCV7.c, valveFlowKvCooling5.a) 
    annotation(Line(origin = {285.0, -58.0},
    points = {{3.0, -1.0}, {9.0, -1.0}, {9.0, 0.0}},
    color = {0, 170, 255},
    thickness = 1.0));
  connect(branchPipeCoolingCV7.b, valveFlowKvCooling4.a) 
    annotation(Line(origin = {275.48934187562264, -37.0},
    points = {{2.0, -12.0}, {2.0, 12.0}, {3.0, 12.0}},
    color = {0, 170, 255},
    thickness = 1.0));
  connect(branchPipeCoolingCV9.b, coolingPipeC.b) 
    annotation(Line(origin = {356, 46},
    points = {{-0.8708306067262583, 25.26077167206894}, {-0.8708306067262583, -23.897667228495457}, {-0.9913310703226443, -23.897667228495457}},
    color = {0, 170, 255},
    thickness = 1));
  connect(valveFlowKvCooling4.b, branchPipeCoolingCV8.b) 
    annotation(Line(origin = {273.0, 34.0},
    points = {{6.0, -39.0}, {6.0, 38.0}},
    color = {0, 170, 255},
    thickness = 1.0));
  connect(branchPipeCoolingCV8.a, coolingPipe1.a) 
    annotation(Line(origin = {264.0, 82.0},
    points = {{5.0, 0.0}, {-6.0, 0.0}},
    color = {0, 170, 255},
    thickness = 1.0));
  connect(branchPipeCoolingCV8.c, branchPipeCoolingCV9.a) 
    annotation(Line(origin = {317.0, 82.0},
    points = {{-28.0, 0.0}, {28.0, 0.0}, {28.0, -1.0}},
    color = {0, 170, 255},
    thickness = 1.0));
  connect(boundaryHeatFlow7.port[1], coolingPipeCR.qa) 
    annotation(Line(origin = {203, 15},
    points = {{-12.000000000000114, 0.4991062129288437}, {12.046965828128066, 0.4991062129288437}, {12.046965828128066, -0.07793384721278329}},
    color = {191, 0, 0},
    thickness = 1));
  connect(coolingPipeDS.b, branchPipeCoolingCV9.c) 
  annotation(Line(origin={413,66},
  points={{48.7967,-15.0502},{48.7967,15.2608},{-47.8708,15.2608}},
  color={0,170,255},
  thickness=1));
end HtrLoop;