model MotorplsBattPlsHVACseries "电池电机串联散热"
  parameter Real BattPump_rpm = 2500 "电池水泵转速（转/分钟）";
  parameter Real MotorPump_rpm = 2000 "电机水泵转速（转/分钟）";
  parameter Real ComprSpd_rpm = 1000 "压缩机转速（转/分钟）";
  parameter Modelica.SIunits.Temperature T_Amb = 298.15 "环境温度";
  parameter Modelica.SIunits.Temperature T_out = 298.15 "外部温度";
  parameter Modelica.SIunits.Temperature T_in = 298.15 "内部温度";
  parameter Modelica.SIunits.Power Q_flowF = 500 "前电机支路总热流量";
  parameter Modelica.SIunits.Power Q_flowR = 500 "后电机支路总热流量";
  parameter Real valve_pos1=1 "散热器侧比例三通阀位置0~1之间";
  parameter Real valve_pos2=0.5 "前后电机侧比例三通阀位置0~1之间";
  annotation(Diagram(coordinateSystem(extent = {{-40, -160}, {870, 260}},
    grid = {2, 2})),
    Icon(coordinateSystem(extent = {{-100.0, -100.0}, {100.0, 100.0}},
    grid = {2.0, 2.0}), graphics = {Bitmap(origin = {0.0, 0.0},
    extent = {{-100.0, -100.0}, {100.0, 100.0}},
    fileName = "modelica://TAThermalSystem/Resource/Icons/Example.svg")}),
    Documentation(link = "modelica://TAThermalSystem/Resource/Doc/MotorplsBattPlsHVACseries.html"
    ),
    experiment(Algorithm=Dassl,NumberOfIntervals=1000,StartTime=0,StopTime=1000,Tolerance=0.0001,InlineIntegrator=false,InlineStepSize=false),
    Protection(access = Access.nonPackageDuplicate), __MWORKS(ContinueSimConfig(SaveContinueFile="false",SaveBeforeStop="false",NumberBeforeStop=1,FixedContinueInterval="false",ContinueIntervalLength=20,ContinueTimeVector),ResultViewerManager(resultViewers={
ResultViewer(name="1", executeTrigger=executeTrigger.SimulationStarted, commands={
CreatePlot(id=1, x_display_unit="s", legend_layout=7, left_title="[degC]", fix_time_range_value=0, zoom_x=(0, 1000), zoom_y_l=(18, 26)),
Plot(y=["evaporatorR134a.hXSummary.Tair_in", "evaporatorR134a.hXSummary.Tair_out"], thicknesses=[2, 2], colors=["4278190335", "4294901760"]),
CreatePlot(id=-1, x_display_unit="s", legend_layout=7, left_title="[degC]", right_title="[degC]", fix_time_range_value=0, sub_plot=(1, 2), zoom_x=(0, 1000), zoom_y_l=(24, 34), zoom_y_r=(24, 34)),
Plot(y=["coolingPipeDS.pipeSummary.T_in", "coolingPipeDS.pipeSummary.T_out"], thicknesses=[2, 2], verticalAxes=[-1, 1], colors=["4278190335", "4294901760"])})
})));
  TAThermalSystem.HeatExchangers.CoolingRadiatorNTU.Water_Air_HXNTU water_air_HXTU1(
    ConsiderMass = false, Across1(displayUnit = "cm2") = 0.0001, Dhyd1(displayUnit = "mm") = 0.01, cearea1(displayUnit = "m2") = 1, ConsiderationFins_cd = false,
    etas2 = 0.8, ConsiderationFins_ab = true, fromDp = false,
  redeclare model Friction_ab = TYBase.Thermal.FluidHeatFlow.PressureLoss.HXPressureDrop.SingularPressureDrop,
    T1_a(start = T_Amb),
    T1_b(start = T_Amb),
    T2_in(start = T_Amb),
    T2_out(start = T_Amb),
    Twall(start = T_Amb),
    Across2 = 0.0001, Dhyd2 = 0.01, cearea2(displayUnit = "m2") = 1,mdot0=0.1,T0=T_Amb) 
    annotation(Placement(transformation(origin = {102.178, -22.8787},
    extent = {{-10, 10}, {10, -10}},
    rotation = 90)));
  TAThermalSystem.Sources.Air.AirSource_mT airSource_mT2(m = 0.1, phi_source = 0.4,
    T = T_Amb,
  redeclare package Medium = TYBase.Media_Extend.Air.MoistAir) 
    annotation(Placement(transformation(origin = {66.1784, 9.12134},
    extent = {{-10, -10}, {10, 10}})));
  TAThermalSystem.Sources.Air.AirSink_pT airSink_pT2(T_sink = T_Amb, phi_sink = 0.4, redeclare package Medium = TYBase.Media_Extend.Air.MoistAir) 
    annotation(Placement(transformation(origin = {66.1784, -35.2413},
    extent = {{-10, -10}, {10, 10}})));
  Modelica.Mechanics.Rotational.Sources.Speed speed1 
    annotation(Placement(transformation(origin = {205.966, -132.08},
    extent = {{-10, -10}, {10, 10}})));



  Modelica.Blocks.Sources.RealExpression realExpression1(y = MotorPump_rpm * Modelica.Constants.pi / 30) 
    annotation(Placement(transformation(origin = {140.966, -131.962},
    extent = {{-10, -10}, {10, 10}})));
  TAThermalSystem.Reservoirs.ExpansionTank expansion_tank(tank1(pInitial = 1e5), T_Amb = T_Amb) 
    annotation(Placement(transformation(origin = {252.008, -100},
    extent = {{-10, -10}, {10, 10}})));
  TAThermalSystem.PumpAndFan.CentrifugalPump centrifugal_pump2(pin_start = 90000, pout_start = 3e5,
    T_inlet(start



    = T_Amb),
    T_outlet(start



    = T_Amb),
    T_start = T_Amb,
    V(displayUnit = "l") = 0.0002) 
    annotation(Placement(transformation(origin = {218.008, -99.9622},
    extent = {{10, -10}, {-10, 10}})));
  TAThermalSystem.Pipes.LiquidCoolingPipe.CoolingPipeCR coolingPipeCR(p0 = 3e5, T0 = T_Amb) annotation(Placement(transformation(origin = {151.908, -98.97},
    extent = {{10.0997, -8.82172}, {-10.0638, 9.0078}})));


  TAThermalSystem.Valves.HydraulicValve.ValveFlowKvCooling zetaFlowCooling2(Tin(start = T_Amb), Tout(start = T_Amb), Kv_curve = {{0.0, 0}, {0.01, 0}, {0.1, 0.1}, {0.2, 0.3}, {0.4, 0.5}, {0.6, 0.6}, {0.8, 0.7}, {1.0, 20}, {1.1, 20}}) annotation(Placement(transformation(origin = {108.008, 80.8752},
    extent = {{-10, -10}, {10, 10}},
    rotation = 90)));
  Modelica.Blocks.Sources.RealExpression realExpression6(y = valve_pos1) 
    annotation(Placement(transformation(origin = {66.1784, 80.8752},
    extent = {{-10, -10}, {10, 10}})));



  TAThermalSystem.Valves.HydraulicValve.ValveFlowKvCooling zetaFlowCooling1(Tin(start = T_Amb), Tout(start = T_Amb), Kv_curve = {{0.0, 0}, {0.01, 0}, {0.1, 0.1}, {0.2, 0.3}, {0.4, 0.5}, {0.6, 0.6}, {0.8, 0.7}, {1.0, 20}, {1.1, 20}}) annotation(Placement(transformation(origin = {23.0928, 80.8752},
    extent = {{-10, -10}, {10, 10}},
    rotation = 90)));
  Modelica.Blocks.Sources.RealExpression realExpression5(y = 1-valve_pos1) 
    annotation(Placement(transformation(origin = {-17.3048, 80.8752},
    extent = {{-10, -10}, {10, 10}})));
  TAThermalSystem.Sources.HeatTransfer.BoundaryHeatFlow boundaryHeatFlow2(Q_flow = Q_flowF) 
    annotation(Placement(transformation(origin = {753.011, 64.9087},
    extent = {{10, -10}, {-10, 10}})));
  TAThermalSystem.Sources.HeatTransfer.BoundaryHeatFlow boundaryHeatFlow3(Q_flow = Q_flowR) 
    annotation(Placement(transformation(origin = {812.833, 60.5461},
    extent = {{10, -10}, {-10, 10}})));
  TAThermalSystem.Valves.HydraulicValve.ValveFlowKvCooling zetaFlowCooling(Tin(start = T_Amb), Tout(start = T_Amb), Kv_curve = {{0.0, 0}, {0.01, 0}, {0.1, 0.1}, {0.2, 0.3}, {0.4, 0.5}, {0.6, 0.6}, {0.8, 0.7}, {1.0, 20}, {1.1, 20}}) annotation(Placement(transformation(origin = {782.931, 104.909},
    extent = {{10, -10}, {-10, 10}},
    rotation = 90)));
  Modelica.Blocks.Sources.RealExpression realExpression(y = 1-valve_pos2) 
    annotation(Placement(transformation(origin = {753.024, 104.909},
    extent = {{-10, -10}, {10, 10}})));
  TAThermalSystem.Valves.HydraulicValve.ValveFlowKvCooling valveFlowKvCooling(Tin(start = T_Amb), Tout(start = T_Amb), Kv_curve = {{0.0, 0}, {0.01, 0}, {0.1, 0.1}, {0.2, 0.3}, {0.4, 0.5}, {0.6, 0.6}, {0.8, 0.7}, {1.0, 20}, {1.1, 20}}) 
    annotation(Placement(transformation(origin = {723.024, 104.909},
    extent = {{10, -10}, {-10, 10}},
    rotation = 90)));
  Modelica.Blocks.Sources.RealExpression realExpression2(y = valve_pos2) 
    annotation(Placement(transformation(origin = {685.117, 104.909},
    extent = {{-10, -10}, {10, 10}})));
  TAThermalSystem.Pipes.LiquidCoolingPipe.CoolingPipe coolingPipeDS1(
    Aheat = 0.18,
    L = 0.2,
    p0 = 1.3e5,
    T0 = T_Amb) 
    annotation(Placement(transformation(origin = {723.1, 64.8617},
    extent = {{-10.0469, -10.0086}, {10.011, 10.0101}},
    rotation = 270)));
  TAThermalSystem.Pipes.LiquidCoolingPipe.CoolingPipe coolingPipeDS2(
    Aheat = 0.18,
    L = 0.2,
    p0 = 1.3e5,
    T0 = T_Amb) 
    annotation(Placement(transformation(origin = {782.921, 60.7449},
    extent = {{-10.0469, -10.0086}, {10.011, 10.0101}},
    rotation = -90)));
  TAThermalSystem.Valves.HydraulicValve.ValveFlowKvCooling zetaFlowCooling7(Tin(start = T_Amb), Tout(start = T_Amb), Kv_curve = {{0.0, 0}, {0.01, 0}, {0.1, 0.1}, {0.2, 0.3}, {0.4, 0.5}, {0.6, 0.6}, {0.8, 0.7}, {1.0, 100}, {1.1, 100}}) annotation(Placement(transformation(origin = {510.8431417967836, 214.0},
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  Modelica.Blocks.Sources.RealExpression realExpression12(y = 0) 
    annotation(Placement(transformation(origin = {524.0, 234.0},
    extent = {{10.0, -10.0}, {-10.0, 10.0}})));
  TAThermalSystem.Valves.HydraulicValve.ValveFlowKvCooling valveFlowKvCooling2(Tin(start = T_Amb), Tout(start = T_Amb), Kv_curve = {{0.0, 0}, {0.01, 0}, {0.1, 0.1}, {0.2, 0.3}, {0.4, 0.5}, {0.6, 0.6}, {0.8, 0.7}, {1.0, 20}, {1.1, 20}}) 
    annotation(Placement(transformation(origin = {451.63145665092225, 189.1202027869802},
    extent = {{10.0, -10.0}, {-10.0, 10.0}},
    rotation = 90.0)));
  Modelica.Blocks.Sources.RealExpression realExpression7(y = 1) 
    annotation(Placement(transformation(origin = {427.63145665092196, 189.1202027869802},
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TAThermalSystem.Valves.HydraulicValve.ValveFlowKvCooling valveFlowKvCooling3(Tin(start = T_Amb), Tout(start = T_Amb), Kv_curve = {{0.0, 0}, {0.01, 0}, {0.1, 0.1}, {0.2, 0.3}, {0.4, 0.5}, {0.6, 0.6}, {0.8, 0.7}, {1.0, 20}, {1.1, 20}}) 
    annotation(Placement(transformation(origin = {582.0640146048361, 189.59757203655903},
    extent = {{10.0, -10.0}, {-10.0, 10.0}},
    rotation = 270.0)));
  Modelica.Blocks.Sources.RealExpression realExpression9(y = 1) 
    annotation(Placement(transformation(origin = {621.2194237075281, 189.59757203655903},
    extent = {{10.0, -10.0}, {-10.0, 10.0}})));
  TYBase.Thermal.FluidHeatFlow.ControlVolumes.CVBasic.ThermalHydraulicCV.BranchPipeCoolingCV branchPipeCoolingCV(p0 = 2.6e5,
    T0 = T_Amb) 
    annotation(Placement(transformation(origin = {451.38459775697606, 214.9008186466771},
    extent = {{-8.169727718157175, -8.435625744212741}, {8.663445506049522, 8.219384140303024}})));
  TYBase.Thermal.FluidHeatFlow.ControlVolumes.CVBasic.ThermalHydraulicCV.BranchPipeCoolingCV branchPipeCoolingCV2(p0 = 2.5e5,
    T0 = T_Amb) 
    annotation(Placement(transformation(origin = {581.8171557108898, 215.37818789625598},
    extent = {{-8.169727718157175, -8.435625744212741}, {8.663445506049522, 8.219384140303024}})));
  TYBase.Thermal.FluidHeatFlow.ControlVolumes.CVBasic.ThermalHydraulicCV.BranchPipeCoolingCV branchPipeCoolingCV4(p0 = 2.799999999999999e5,
    T0 = T_Amb) 
    annotation(Placement(transformation(origin = {107.761, 216.644},
    extent = {{-8.16973, -8.43563}, {8.66345, 8.21938}})));
  TYBase.Thermal.FluidHeatFlow.ControlVolumes.CVBasic.ThermalHydraulicCV.BranchPipeCoolingCV branchPipeCoolingCV5(p0 = 2.899999999999999e5,
    T0 = T_Amb) 
    annotation(Placement(transformation(origin = {108.18, -99.5724},
    extent = {{-8.16973, 8.43563}, {8.66345, -8.21938}})));
  TAThermalSystem.Pipes.LiquidCoolingPipe.CoolingPipeR coolingPipeR(p0 = 2.7e5,
    T0 = T_Amb) 
    annotation(Placement(transformation(origin = {176.51795000000018, 216.68165380492104},
    extent = {{-10.0997, -8.821720000000001}, {10.0638, 9.007800000000001}})));
  Modelica.Blocks.Sources.RealExpression realExpression10(y = ComprSpd_rpm) 
    annotation(Placement(transformation(origin = {193.362, 117.931},
    extent = {{-10, -10}, {10, 10}})));
  Modelica.Mechanics.Rotational.Sources.Speed speed 
    annotation(Placement(transformation(origin = {237.362, 117.931},
    extent = {{-10, -10}, {10, 10}})));
  TAThermalSystem.HeatExchangers.Condenser condenser(
  redeclare package Medium = TYMedia.Helmholtz.R134a,
    n_segRef = 1,
    n_segMtl = 1, HX_Init(T0 = T_Amb, T_air0 = T_Amb), redeclare TYBase.Thermal.FluidHeatFlow.Components.BasicComponents.Records.PropertiesRecords.WallMaterialType.WallMaterialAluminium wallmaterial, CF_RefrigerantSideHeatTransfer = 10, CF_AirSideHeatTransfer = 10, RefrigerantTemperature = 25, RefrigerantMass = 0.117458) 

    annotation(Placement(transformation(origin = {224.612, 61.9308},
    extent = {{10, 10}, {-10, -10}},
    rotation = 90)));
  TAThermalSystem.Sources.Air.AirSink_pT airSink1(T_sink = 293.15,
    phi_sink = 0.4) annotation(Placement(transformation(origin = {250.612, 89.8526},
    extent = {{10, -10}, {-10, 10}})));
  TAThermalSystem.Sources.Air.AirSource_mT airSource1(m = 0.1, T = T_out,
    phi_source = 0.4) annotation(Placement(transformation(origin = {252.612, 39.1545},
    extent = {{10, -10}, {-10, 10}})));
  TAThermalSystem.Compressor.Compressor compressorR134a(
    p0_in = 4.999999999999999e5, p0_out = 9.999999999999999e5,
    MaximumDisplacement = 3.3e-5, redeclare package Medium = TYMedia.Helmholtz.R134a) 
    annotation(Placement(transformation(origin = {260.612, 149.931},
    extent = {{10, -10}, {-10, 10}})));
  Modelica.Blocks.Math.Gain gain(k = Modelica.Constants.pi / 30) 
    annotation(Placement(transformation(origin = {215.362, 117.931},
    extent = {{-6, -6}, {6, 6}})));
  TAThermalSystem.Reservoirs.Reservoir reservoir(redeclare package Medium = TYMedia.Helmholtz.R134a,
    FromDp = false, zeta = 1000, RefrigerantTemperature = 25, RefrigerantMass = 0.238672, RefrigerantMassDistribution = 1) 
    annotation(Placement(transformation(origin = {301.362, 149.831},
    extent = {{10, -10}, {-10, 10}})));
  TAThermalSystem.Sensors.Refrigerant.SuperHeatingSensor superHeatingSensor(h0_in = 2.7e5, h0_out = 2.7e5, redeclare package Medium = TYMedia.Helmholtz.R134a) annotation(Placement(transformation(origin = {342.112, 149.831},
    extent = {{10, -10}, {-10, 10}})));
  TAThermalSystem.Sensors.Refrigerant.SuperCoolingSensor superCoolingSensor(redeclare package Medium = TYMedia.Helmholtz.R134a) 
    annotation(Placement(transformation(origin = {300.649, -5.69805},
    extent = {{-10, -10}, {10, 10}})));
  TAThermalSystem.HeatExchangers.Evaporator evaporatorR134a(HX_Init(T0 = T_Amb, T_air0 = T_Amb), redeclare TYBase.Thermal.FluidHeatFlow.Components.BasicComponents.Records.PropertiesRecords.WallMaterialType.WallMaterialAluminium wallmaterial, redeclare package Medium = TYMedia.Helmholtz.R134a, CF_RefrigerantSideHeatTransfer = 10, CF_AirSideHeatTransfer = 10, RefrigerantTemperature = 25, RefrigerantMass = 0.0734114) annotation(Placement(transformation(origin = {386.612, 97.9308},
    extent = {{-10, -10}, {10, 10}},
    rotation = 90)));
  TAThermalSystem.Valves.RefrigerantValve.ZetaFlow zetaFlow(redeclare package Medium = TYMedia.Helmholtz.R134a,
    Tin(start
    = 298.15),
    Tout(start
    = 298.15),
    Dhyd(displayUnit
    = "mm") =
    0.004,
    zeta = 2000, T0 = 298.15) annotation(Placement(transformation(origin = {392.612, 43.9308},
    extent = {{10, -10}, {-10, 10}},
    rotation = -90)));
  TAThermalSystem.Pipes.LiquidCoolingPipe.CoolingPipeDS coolingPipeDS(n = 1, title = "水管道", Dhyd = 0.025, Aheat = 0.1918,
    p0 = 2.5e5, T0 = T_Amb) 
    annotation(Placement(transformation(origin = {583.6652421532535, 111.97883153853836},
    extent = {{10.0469483144355, -10.008632925201297}, {-10.011048314435497, 10.010082025725545}},
    rotation = -90.0)));
  Modelica.Blocks.Sources.RealExpression realExpression8(y = BattPump_rpm* Modelica.Constants.pi / 30) 
    annotation(Placement(transformation(origin = {549.6738750784547, -14.702803570996679},
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  Modelica.Mechanics.Rotational.Sources.Speed speed4 
    annotation(Placement(transformation(origin = {583.6738750784547, -14.702803570996679},
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TAThermalSystem.PumpAndFan.CentrifugalPump centrifugal_pump4(T_inlet(start = T_Amb), T_outlet(start = T_Amb), T_start = T_Amb, pin_start = 90000, pout_start = 3e5, m_flow_start = 0.1) 
    annotation(Placement(transformation(origin = {583.6738750784547, 42.40857997597351},
    extent = {{-10.0, -10.0}, {10.0, 10.0}},
    rotation = -270.0)));
  TYBase.Battery.Model.BatteryQIn batteryQIn(N_cells = 1, chargeResTable = {{10, 0.2}, {20, 0.2}, {30, 0.2}, {40, 0.2}, {50, 0.2}, {60, 0.2}, {70, 0.2}, {80, 0.2}, {90, 0.2}}, dischargeResTable = {{10, 0.2}, {20, 0.2}, {30, 0.2}, {40, 0.2}, {50, 0.2}, {60, 0.2}, {70, 0.2}, {80, 0.2}, {90, 0.2}}, Ns = 96, Np = 2, QCellNominal = 33, C = 2000) 
    annotation(Placement(transformation(origin = {635.8307332816713, 92.68830074916522},
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYBase.Battery.Component.Ground ground annotation(HideResult = true, Placement(transformation(origin = {658.8899722091775, 28.812306470095365},
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  Modelica.Electrical.Analog.Sources.ConstantCurrent constantCurrent(I = 66 * 2) 
    annotation(Placement(transformation(origin = {635.8307332816713, 53.53340569962002},
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TAThermalSystem.Valves.HydraulicValve.ValveFlowKvCooling zetaFlowCooling6(Tin(start = T_Amb), Tout(start = T_Amb), mdot(start = 0.1)) annotation(Placement(transformation(origin = {510.5147736437889, 161.21759848926388},
    extent = {{10.0, -10.0}, {-10.0, 10.0}})));
  Modelica.Blocks.Sources.RealExpression realExpression11(y = 0) 
    annotation(Placement(transformation(origin = {530.0147736437889, 182.08758579165664},
    extent = {{10.0, -10.0}, {-10.0, 10.0}})));
  TAThermalSystem.Reservoirs.ExpansionTank expansion_tank1(tank1(
    pInitial = 0.9e5),
    T_Amb = T_Amb,
    zetaFlowCooling9(FromDp = false)) 

    annotation(Placement(transformation(origin = {505.8307332816713, 13.308713093976166},
    extent = {{10.0, -10.0}, {-10.0, 10.0}})));
  TYBase.Thermal.FluidHeatFlow.ControlVolumes.CVBasic.ThermalHydraulicCV.BranchPipeCoolingCV branchPipeCoolingCV9(p0 = 1.8e5,
    T0 = T_Amb) 
    annotation(Placement(transformation(origin = {457.0150127227007, 160.37071565267925},
    extent = {{-8.169727718157175, -8.435625744212741}, {8.663445506049522, 8.219384140303024}})));
  TAThermalSystem.HeatExchangers.CoolingRadiatorNTU.ChillerPlateCooling chillerPlate(redeclare model Friction = TYBase.Thermal.FluidHeatFlow.PressureLoss.LiquidPressureDrop.SingularPressureDrop, water(redeclare model Friction = TYBase.Thermal.FluidHeatFlow.PressureLoss.LiquidPressureDrop.SingularPressureDrop),

    p0 = 1.6e5,
    T0 = T_Amb, redeclare package RefMedium = TYMedia.Helmholtz.R134a, simplePipe(RefrigerantTemperature = 15, RefrigerantMass = 0.270458, RefrigerantMassDistribution = 1)) 



    annotation(Placement(transformation(origin = {445.55958570535853, 92.89553836607635},
    extent = {{10, -10}, {-10, 10}},
    rotation = -90)));
  TAThermalSystem.Valves.RefrigerantValve.ZetaFlow zetaFlow1(redeclare package Medium = TYMedia.Helmholtz.R134a,
    Tin(start
    = 298.15),
    Tout(start
    = 298.15),
    Dhyd(displayUnit
    = "mm") =
    0.0005,
    zeta = 2000, T0 = 298.15) annotation(Placement(transformation(origin = {439.55958570535853, 44.2292759515003},
    extent = {{10.0, -10.0}, {-10.0, 10.0}},
    rotation = 270.0)));
  TAThermalSystem.Pipes.LiquidCoolingPipe.CoolingPipeR coolingPipe2(p0 = 1.5e5, T0 = T_Amb, L = 0.1, TA(start = T_Amb), TB(start = T_Amb)) annotation(Placement(transformation(origin={454.893,59.1039},
extent={{10.0997,-8.82172},{-10.0638,9.0078}},
rotation=90)));
  TAThermalSystem.Pipes.LiquidCoolingPipe.CoolingPipeR coolingPipe3(p0 = 1.7e5, T0 = T_Amb, L = 0.1, TA(start = T_Amb), TB(start = T_Amb)) annotation(Placement(transformation(origin={455.97,125.439},
extent={{10.0997,-8.82172},{-10.0638,9.0078}},
rotation=90)));
  TYBase.Thermal.FluidHeatFlow.ControlVolumes.CVBasic.ThermalHydraulicCV.BranchPipeCoolingCV branchPipeCoolingCV3(p0 = 2.3e5,
    T0 = T_Amb) 
    annotation(Placement(transformation(origin = {581.652, 160.578},
    extent = {{-8.16973, -8.43563}, {8.66345, 8.21938}},
    rotation = -90)));
  TAThermalSystem.Sources.Air.AirSource_mT airSource(
    m = 0.2, T = T_in,
    phi_source = 0.4) annotation(Placement(transformation(origin = {356.451, 117.156},
    extent = {{-10, -10}, {10, 10}})));
  TAThermalSystem.Sources.Air.AirSink_pT airSink(redeclare package Medium = TYBase.Media_Extend.Air.MoistAir, T_sink = 293.15,
    phi_sink = 0.2) annotation(Placement(transformation(origin = {356.451, 77.1553},
    extent = {{-10, -10}, {10, 10}})));
/*
initial equation
condenser.refrigerant.p[1]= condenser.refrigerant.p0[1];
evaporatorR134a.refrigerant.p[1] = evaporatorR134a.refrigerant.p0[1];
chillerPlate.wall.T_in = 288.15;
chillerPlate.wall.T_out = 288.15;
coolingPipe1.CV.p= coolingPipe1.CV.p0;
coolingPipeCR.CV.p = coolingPipeCR.CV.p0;
coolingPipeCR1.CV.p = coolingPipeCR1.CV.p0;
*/


equation
  connect(airSink_pT2.port_a, water_air_HXTU1.d) 
    annotation(Line(origin = {106.178, -37.8787},
    points = {{-30, 2.63741}, {-10.1564, 2.63741}, {-10.1564, 5.0368}},
    color = {0, 232, 232},
    thickness = 1));
  connect(water_air_HXTU1.c, airSource_mT2.port_b) 
    annotation(Line(origin = {143.178, -36.8787},
    points = {{-47.0374, 24.1119}, {-47.0374, 46}, {-67, 46}},
    color = {0, 232, 232},
    thickness = 1));
  connect(expansion_tank.b, centrifugal_pump2.a) 
    annotation(Line(origin = {207.803, 18.2083},
    points = {{34.2048, -118.208}, {20.2149, -118.208}, {20.2149, -118.208}},
    color = {0, 170, 255},
    thickness = 1));
  connect(speed1.flange, centrifugal_pump2.flange) 
    annotation(Line(origin = {219.966, -121.042},
    points = {{-4, -11.0378}, {-4, 13}, {-1.95873, 13}, {-1.95873, 11.0799}},
    color = {0, 0, 0}));
  connect(centrifugal_pump2.b, coolingPipeCR.a) 
    annotation(Line(origin = {208.764, -39.7917},
    points = {{-0.879482, -60.2083}, {-46.8456, -60.2083}, {-46.8456, -59.2161}},
    color = {0, 170, 255},
    thickness = 1));
  connect(branchPipeCoolingCV5.c, coolingPipeCR.b) 
    annotation(Line(origin = {135.139, -45.8787},
    points = {{-16.959, -53.6937}, {6.64518, -53.6937}, {6.64518, -53.1291}},
    color = {0, 170, 255},
    thickness = 1));
  connect(realExpression6.y, zetaFlowCooling2.u) 
    annotation(Line(origin = {313.837, 33.2013},
    points = {{-236.659, 47.6739}, {-215.83, 47.6739}},
    color = {0, 0, 127}));


  connect(zetaFlowCooling1.u, realExpression5.y) 
    annotation(Line(origin = {1.69521, 80.6248},
    points = {{11.3976, 0.250413}, {-8, 0.250413}},
    color = {0, 0, 127}));
  connect(realExpression.y, zetaFlowCooling.u) 
    annotation(Line(origin = {753.024, 42.0449},
    points = {{11, 62.8638}, {19.907, 62.8638}},
    color = {0, 0, 127}));
  connect(realExpression2.y, valveFlowKvCooling.u) 
    annotation(Line(origin = {541.117, 104.909},
    points = {{155, -5.68434e-14}, {171.907, -5.68434e-14}},
    color = {0, 0, 127}));
  connect(valveFlowKvCooling.b, coolingPipeDS1.a) 
    annotation(Line(origin = {723.024, 84.7919},
    points = {{0.037774, 9.99335}, {0.037774, -9.97233}, {-0.0706034, -9.97233}},
    color = {0, 170, 255},
    thickness = 1));
  connect(coolingPipeDS2.a, zetaFlowCooling.b) 
    annotation(Line(origin = {783.024, 82.7919},
    points = {{-0.249273, -12.0891}, {-0.249273, 11.9933}, {-0.055266, 11.9933}},
    color = {0, 170, 255},
    thickness = 1));
  connect(boundaryHeatFlow2.port[1], coolingPipeDS1.qa) 
    annotation(Line(origin = {739.024, 64.7919},
    points = {{3.98694, 0.116786}, {-4.80034, 0.116786}, {-4.80034, -0.129022}},
    color = {191, 0, 0},
    thickness = 1));
  connect(coolingPipeDS2.qa, boundaryHeatFlow3.port[1]) 
    annotation(Line(origin = {798.024, 60.7919},
    points = {{-3.97901, -0.245808}, {4.80827, -0.245808}, {4.80827, -0.245808}},
    color = {191, 0, 0},
    thickness = 1));
  connect(zetaFlowCooling1.a, branchPipeCoolingCV5.a) 
    annotation(Line(origin = {65.0076, -14.9622},
    points = {{-41.877, 85.8273}, {-41.877, -84.6101}, {33.1726, -84.6101}},
    color = {0, 170, 255},
    thickness = 1));
  connect(speed1.w_ref, realExpression1.y) 
    annotation(Line(origin = {173.008, -131.962},
    points = {{20.9587, -0.117707}, {-21.0413, -0.117707}, {-21.0413, 2.84217e-14}},
    color = {0, 0, 127}));
  connect(zetaFlowCooling7.u, realExpression12.y) 
    annotation(Line(origin = {516.932134418143, 237.73291853853922},
    points = {{-6.0, -14.0}, {-6.0, -4.0}, {-4.0, -4.0}},
    color = {0, 0, 127}));

  connect(zetaFlowCooling1.b, branchPipeCoolingCV4.a) 
    annotation(Line(origin = {127.008, 154.038},
    points = {{-103.877, -63.0392}, {-103.877, 62.6061}, {-29.2469, 62.6061}},
    color = {0, 170, 255},
    thickness = 1));
  connect(zetaFlowCooling2.b, branchPipeCoolingCV4.b) 
    annotation(Line(origin = {169.008, 154.038},
    points = {{-60.9622, -63.0392}, {-60.9622, 52.6061}, {-61.2469, 52.6061}},
    color = {0, 170, 255},
    thickness = 1));
  connect(realExpression7.y, valveFlowKvCooling2.u) 
    annotation(Line(origin = {278.67629646634185, 139.53890290997984},
    points = {{160.0, 50.0}, {163.0, 50.0}},
    color = {0, 0, 127}));
  connect(realExpression9.y, valveFlowKvCooling3.u) 
    annotation(Line(origin = {404.02322433382193, 220.0162721595587},
    points = {{206.0, -30.0}, {188.0, -30.0}},
    color = {0, 0, 127}));
  connect(zetaFlowCooling7.a, branchPipeCoolingCV.c) 
    annotation(Line(origin = {484.6314566509221, 206.12020278698017},
    points = {{16.0, 8.0}, {-24.0, 8.0}, {-24.0, 9.0}, {-23.0, 9.0}},
    color = {0, 170, 255},
    thickness = 1.0));
  connect(zetaFlowCooling7.b, branchPipeCoolingCV2.a) 
    annotation(Line(origin = {553.2194237075281, 202.597572036559},
    points = {{-32.0, 11.0}, {19.0, 11.0}, {19.0, 13.0}},
    color = {0, 170, 255},
    thickness = 1.0));
  connect(branchPipeCoolingCV.b, valveFlowKvCooling2.a) 
    annotation(Line(origin = {451.6314566509221, 210.12020278698017},
    points = {{0.0, -5.0}, {0.0, -11.0}},
    color = {0, 170, 255},
    thickness = 1.0));
  connect(branchPipeCoolingCV2.b, valveFlowKvCooling3.b) 
    annotation(Line(origin = {582.2194237075281, 210.597572036559},
    points = {{0.0, -5.0}, {0.0, -11.0}},
    color = {0, 170, 255},
    thickness = 1.0));


  connect(branchPipeCoolingCV4.c, coolingPipeR.a) 
    annotation(Line(origin = {85, 217.038},
    points = {{32.7607, -0.393894}, {81.5078, -0.393894}, {81.5078, -0.393894}},
    color = {0, 170, 255},
    thickness = 1));
  connect(coolingPipeR.b, branchPipeCoolingCV.a) 
    annotation(Line(origin = {284.6314566509221, 217.1579768173343},
    points = {{-98.0, -1.0}, {157.0, -1.0}, {157.0, -2.0}},
    color = {0, 170, 255},
    thickness = 1.0));
  connect(coolingPipeDS1.b, expansion_tank.a) 
    annotation(Line(origin = {401.923, -40.1888},
    points = {{321.031, 94.9801}, {321.031, -58}, {-139.915, -58}, {-139.915, -59.8112}},
    color = {0, 170, 255},
    thickness = 1));
  connect(coolingPipeDS2.b, expansion_tank.a) 
    annotation(Line(origin = {431.923, -42.1888},
    points = {{350.852, 92.8633}, {350.852, -56}, {-169.915, -56}, {-169.915, -57.8112}},
    color = {0, 170, 255},
    thickness = 1));
  connect(speed.flange, compressorR134a.flange) 
    annotation(Line(origin = {289.612, 130.931},
    points = {{-42.2497, -13}, {-29, -13}, {-29, 9}},
    color = {0, 0, 0}));
  connect(airSource1.port_b, condenser.air_in) 
    annotation(Line(origin={234.612,29.9308},
points={{8,9.2237},{-4,9.2237},{-4,22}},
color={0,232,232},
thickness=1));
  connect(airSink1.port_a, condenser.air_out) 
    annotation(Line(origin={234.612,65.9308},
points={{6,23.9218},{-4,23.9218},{-4,6}},
color={0,232,232},
thickness=1));
  connect(realExpression10.y, gain.u) 
    annotation(Line(origin = {188.362, 117.931},
    points = {{16, -8.52651e-14}, {19.8, -8.52651e-14}, {19.8, -2.84217e-14}},
    color = {0, 0, 127}));
  connect(gain.y, speed.w_ref) 
    annotation(Line(origin = {217.362, 117.931},
    points = {{4.6, -2.84217e-14}, {8, -2.84217e-14}, {8, -8.52651e-14}},
    color = {0, 0, 127}));
  connect(reservoir.b, compressorR134a.a) 
    annotation(Line(origin = {311.612, 150.291},
    points = {{-20.2497, -0.56}, {-41, -0.56}, {-41, -0.36}},
    color = {0, 128, 0},
    thickness = 1));
  connect(compressorR134a.b, condenser.a1) 
    annotation(Line(origin = {169.612, 94.2908},
    points = {{81, 55.64}, {49, 55.64}, {49, -22.36}},
    color = {0, 128, 0},
    thickness = 1));
  connect(reservoir.port_a, superHeatingSensor.b) 
    annotation(Line(origin = {357.612, 150.093},
    points = {{-46.2497, -0.3626}, {-25.4993, -0.3626}, {-25.4993, -0.2626}},
    color = {0, 128, 0},
    thickness = 1));
  connect(condenser.b1, superCoolingSensor.a) 
    annotation(Line(origin = {261.612, 34.0934},
    points = {{-43, 17.8374}, {-43, -39.7914}, {29.0378, -39.7914}},
    color = {0, 128, 0},
    thickness = 1));
  connect(zetaFlow.b, evaporatorR134a.a1) 
    annotation(Line(origin = {400.612, 35.9308},
    points = {{-8, 18}, {-8, 52}, {-8, 52}},
    color = {0, 128, 0},
    thickness = 1));
  connect(superHeatingSensor.a, evaporatorR134a.b1) 
    annotation(Line(origin = {387.612, 129.093},
    points = {{-35.4993, 20.7374}, {5, 20.7374}, {5, -21.1626}},
    color = {0, 128, 0},
    thickness = 1));
  connect(zetaFlow.a, superCoolingSensor.b) 
    annotation(Line(origin = {359.612, 26.0934},
    points = {{33, 7.8374}, {33, -31.7914}, {-48.9622, -31.7914}},
    color = {0, 128, 0},
    thickness = 1));
  connect(realExpression8.y, speed4.w_ref) 
    annotation(Line(origin = {563.6738750784547, -14.70280357099665},
    points = {{-3.0, 0.0}, {8.0, 0.0}},
    color = {0, 0, 127}));
  connect(speed4.flange, centrifugal_pump4.flange) 
    annotation(Line(origin = {593.8307332816713, -2.949473281188915},
    points = {{0.0, -12.0}, {0.0, 45.0}},
    color = {0, 0, 0}));
  connect(centrifugal_pump4.b, coolingPipeDS.a) 
    annotation(Line(origin = {591.8307332816713, 82.98987985297383},
    points = {{-8.0, -30.0}, {-8.0, 19.0}},
    color = {0, 170, 255},
    thickness = 1.0));
  connect(coolingPipeDS.qa, batteryQIn.Batt_top) 
    annotation(Line(origin = {619.8307332816713, 106.98987985297383},
    points = {{-26.0, 5.0}, {26.0, 5.0}, {26.0, -5.0}},
    color = {191, 0, 0},
    thickness = 1.0));
  connect(batteryQIn.pin_p, constantCurrent.p) 
    annotation(Line(origin = {624.8307332816713, 70.98987985297383},
    points = {{1.0, 22.0}, {-4.0, 22.0}, {-4.0, -17.0}, {1.0, -17.0}},
    color = {0, 0, 255}));
  connect(batteryQIn.pin_n, constantCurrent.n) 
    annotation(Line(origin = {645.8307332816713, 73.98987985297383},
    points = {{0.0, 19.0}, {10.0, 19.0}, {10.0, -20.0}, {0.0, -20.0}},
    color = {0, 0, 255}));
  connect(ground.p, batteryQIn.pin_n) 
    annotation(Line(origin = {652.8307332816713, 65.98987985297383},
    points = {{6.0, -27.0}, {6.0, 27.0}, {-7.0, 27.0}},
    color = {0, 0, 255}));
  connect(zetaFlowCooling6.u, realExpression11.y) 
    annotation(Line(origin = {504.51477364378894, 226.56428254352733},
    points = {{6.0, -55.0}, {6.0, -44.0}, {14.0, -44.0}},
    color = {0, 0, 127}));
  connect(expansion_tank1.b, centrifugal_pump4.a) 
    annotation(Line(origin = {549.8307332816713, 23.152479606974453},
    points = {{-34.0, -10.0}, {34.0, -10.0}, {34.0, 9.0}},
    color = {0, 170, 255},
    thickness = 1.0));
  connect(branchPipeCoolingCV9.c, zetaFlowCooling6.b) 
    annotation(Line(origin = {502.1487651319631, 160.93505528594494},
    points = {{-35.0, -1.0}, {-2.0, -1.0}, {-2.0, 0.0}},
    color = {0, 170, 255},
    thickness = 1.0));
  connect(valveFlowKvCooling2.b, branchPipeCoolingCV9.a) 
    annotation(Line(origin = {430.63399148817416, 171.0},
    points = {{21.0, 8.0}, {23.0, 8.0}, {23.0, 1.0}, {16.0, 1.0}, {16.0, -11.0}},
    color = {0, 170, 255},
    thickness = 1.0));
  connect(chillerPlate.a, zetaFlow1.b) 
    annotation(Line(origin = {382.00000000000006, 67.83740024599938},
    points = {{57.55958570535847, 15.058138120076975}, {57.55958570535847, -13.608124294499078}},
    color = {0, 128, 0},
    thickness = 1));
  connect(superCoolingSensor.b, zetaFlow1.a) 
    annotation(Line(origin = {237.25, 29.0378},
    points = {{73.3997, -34.7358}, {202.31, -34.7358}, {202.31, 5.1915}},
    color = {0, 128, 0},
    thickness = 1));
  connect(chillerPlate.b, superHeatingSensor.a) 
    annotation(Line(origin = {251.087, 134.076},
    points = {{188.473, -31.18}, {188.473, 15.7552}, {101.025, 15.7552}},
    color = {0, 128, 0},
    thickness = 1));
  connect(chillerPlate.d, coolingPipe2.a) 
    annotation(Line(origin={456,79},
points={{-4.44041,3.89554},{-4.44041,-9.88597},{-1.06875,-9.88597}},
color={0,170,255},
thickness=1));
  connect(branchPipeCoolingCV9.b, coolingPipe3.a) 
    annotation(Line(origin={461,144},
points={{-3.98499,6.37072},{-3.98499,-8.55125},{-4.99268,-8.55125}},
color={0,170,255},
thickness=1));
  connect(coolingPipe3.b, chillerPlate.c) 
    annotation(Line(origin={459,112},
points={{-2.99268,3.31519},{-2.99268,-6.10446},{-7.44041,-6.10446},{-7.44041,-9.10446}},
color={0,170,255},
thickness=1));
  connect(water_air_HXTU1.b, zetaFlowCooling2.a) 
    annotation(Line(origin = {108.008, 29},
    points = {{0.037774, -41.8307}, {0.037774, 41.8651}},
    color = {0, 170, 255},
    thickness = 1));
  connect(branchPipeCoolingCV5.b, water_air_HXTU1.a) 
    annotation(Line(origin = {108.008, -61},
    points = {{0.172646, -28.5724}, {0.172646, 28.1071}, {0.172646, 28.1071}},
    color = {0, 170, 255},
    thickness = 1));
  connect(valveFlowKvCooling.a, branchPipeCoolingCV2.c) 
    annotation(Line(origin = {662, 122},
    points = {{61.062, -7.08121}, {61.062, 93.3782}, {-70.1828, 93.3782}},
    color = {0, 170, 255},
    thickness = 1));
  connect(zetaFlowCooling.a, branchPipeCoolingCV2.c) 
    annotation(Line(origin = {692, 122},
    points = {{90.969, -7.08121}, {90.969, 93.3782}, {-100.183, 93.3782}},
    color = {0, 170, 255},
    thickness = 1));
  connect(zetaFlowCooling6.a, branchPipeCoolingCV3.b) 
    annotation(Line(origin = {544, 161},
    points = {{-23.4751, 0.179824}, {27.6521, 0.179824}, {27.6521, -0.422004}},
    color = {0, 170, 255},
    thickness = 1));
  connect(branchPipeCoolingCV3.c, coolingPipeDS.b) 
    annotation(Line(origin = {580, 136},
    points = {{1.65206, 14.578}, {1.65206, -13.8977}, {3.62747, -13.8977}},
    color = {0, 170, 255},
    thickness = 1));
  connect(branchPipeCoolingCV3.a, valveFlowKvCooling3.a) 
    annotation(Line(origin = {579, 175},
    points = {{2.65206, -4.422}, {2.65206, 4.58745}, {3.02624, 4.58745}},
    color = {0, 170, 255},
    thickness = 1));
  connect(airSink.port_a, evaporatorR134a.air_out) 
    annotation(Line(origin = {373.362, 82.0556},
    points = {{-6.911, -4.9003}, {7.24967, -4.9003}, {7.24967, 5.87517}},
    color = {0, 232, 232},
    thickness = 1));
  connect(airSource.port_b, evaporatorR134a.air_in) 
    annotation(Line(origin = {373.362, 112.056},
    points = {{-6.911, 5.1}, {7.24967, 5.1}, {7.24967, -4.12483}},
    color = {0, 232, 232},
    thickness = 1));
  connect(expansion_tank1.a, coolingPipe2.b) 
    annotation(Line(origin={478,33},
points={{17.8307,-19.6913},{-23.0687,-19.6913},{-23.0687,15.9805}},
color={0,170,255},
thickness=1));
end MotorplsBattPlsHVACseries;