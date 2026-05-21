model MotorplsBattPlsHVAC "电池、暖芯PTC制热"
  parameter Real BattPump_rpm = 2000 "电池水泵转速（转/分钟）";
  parameter Real MotorPump_rpm = 3000 "电机水泵转速（转/分钟）";
  parameter Real HtrPump_rpm = 1000 "暖芯水泵转速（转/分钟）";
  parameter Real ComprSpd_rpm = 600 "压缩机转速（转/分钟）";
  parameter Modelica.Units.SI.Temperature T_Amb = 288.15 "环境温度";
  parameter Modelica.Units.SI.Temperature T_out = 288.15 "外部温度";
  parameter Modelica.Units.SI.Temperature T_in = 288.15 "内部温度";
  parameter Modelica.Units.SI.Power Q_flow = 2000 "PTC制热量";
  parameter Modelica.SIunits.Power Q_flowF = 500 "前电机支路总热流量";
  parameter Modelica.SIunits.Power Q_flowR = 500 "后电机支路总热流量";
  parameter Real valve_pos1=1 "散热器侧比例三通阀位置0~1之间";
  parameter Real valve_pos2=0.5 "前后电机侧比例三通阀位置0~1之间";
  parameter Real valve_pos3=0.5 "暖芯侧比例三通阀位置0~1之间";
  annotation(Diagram(coordinateSystem(extent={{-160,-170},{870,290}},
grid={2,2})),
    Icon(coordinateSystem(extent = {{-100.0, -100.0}, {100.0, 100.0}},
    grid = {2.0, 2.0}), graphics = {Bitmap(origin = {0.0, 0.0},
    extent = {{-100.0, -100.0}, {100.0, 100.0}},
    fileName = "modelica://TAThermalSystem/Resource/Icons/Example.svg")}),
    Documentation(link="modelica://TAThermalSystem/Resource/Doc/MotorplsBattPlsHVAC.html"),
    experiment(Algorithm=Dassl,NumberOfIntervals=1000,StartTime=0,StopTime=1000,Tolerance=0.0001,InlineIntegrator=false,InlineStepSize=false),
    Protection(access=Access.nonPackageDuplicate),__MWORKS(ContinueSimConfig(SaveContinueFile="false",SaveBeforeStop="false",NumberBeforeStop=1,FixedContinueInterval="false",ContinueIntervalLength=20,ContinueTimeVector),ResultViewerManager(resultViewers={
ResultViewer(name="1", executeTrigger=executeTrigger.SimulationStarted, commands={
CreatePlot(id=1, x_display_unit="s", legend_layout=7, left_title="[degC]", fix_time_range_value=0, zoom_x=(0, 1000), zoom_y_l=(0, 50)),
Plot(y=["water_air_HXTU2.hXSummary.Ta_in", "water_air_HXTU2.hXSummary.Tb_out", "water_air_HXTU2.hXSummary.Tc_in", "water_air_HXTU2.hXSummary.Td_out", "cabinVolume.summary.T"], thicknesses=[2, 2, 2, 2, 2], colors=["4278190335", "4294901760", "4278222848", "4294902015", "4278190080"]),
CreatePlot(id=-1, x_display_unit="s", legend_layout=7, left_title="[degC]", right_title="[degC]", fix_time_range_value=0, sub_plot=(1, 2), zoom_x=(0, 1000), zoom_y_l=(10, 45), zoom_y_r=(10, 45)),
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
    Across2 = 0.0001, Dhyd2 = 0.01, cearea2(displayUnit = "m2") = 1,T0=T_Amb) 
    annotation(Placement(transformation(origin = {-11.829136350837729, -22.878658945661208},
    extent = {{-10.0, 10.0}, {10.0, -10.0}},
    rotation = 90.0)));
  TAThermalSystem.Sources.Air.AirSource_mT airSource_mT2(m = 0.1, phi_source = 0.4,
    T = T_Amb,
  redeclare package Medium = TYBase.Media_Extend.Air.MoistAir) 
    annotation(Placement(transformation(origin = {-47.829136350837764, 9.121341054338785},
    extent = {{-10.0, -9.999999999999996}, {10.0, 10.0}})));
  TAThermalSystem.Sources.Air.AirSink_pT airSink_pT2(T_sink = T_Amb, phi_sink = 0.4, redeclare package Medium = TYBase.Media_Extend.Air.MoistAir) 
    annotation(Placement(transformation(origin = {-47.829136350837764, -35.241252665907666},
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  Modelica.Mechanics.Rotational.Sources.Speed speed1 
    annotation(Placement(transformation(origin = {91.95872611464961, -132.07993297601524},
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));



  Modelica.Blocks.Sources.RealExpression realExpression1(y = MotorPump_rpm * Modelica.Constants.pi / 30) 
    annotation(Placement(transformation(origin = {26.958726114649608, -131.96222596964583},
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TAThermalSystem.Reservoirs.ExpansionTank expansion_tank(tank1(pInitial = 1e5), T_Amb = T_Amb) 
    annotation(Placement(transformation(origin = {137.99999999999997, -99.99999999999999},
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TAThermalSystem.PumpAndFan.CentrifugalPump centrifugal_pump2(pin_start = 90000, pout_start = 3e5,
    T_inlet(start



    = T_Amb),
    T_outlet(start



    = T_Amb),
    T_start = T_Amb,
    V(displayUnit = "l") = 0.0002) 
    annotation(Placement(transformation(origin = {104.0, -99.96222596964587},
    extent = {{10.0, -10.0}, {-10.0, 10.0}})));
  TAThermalSystem.Pipes.LiquidCoolingPipe.CoolingPipeCR coolingPipeCR(p0 = 3e5, T0 = T_Amb) annotation(Placement(transformation(origin = {37.90029999999999, -98.97002596964585},
    extent = {{10.0997, -8.821720000000001}, {-10.0638, 9.007800000000001}})));


  TAThermalSystem.Valves.HydraulicValve.ValveFlowKvCooling zetaFlowCooling2(Tin(start = T_Amb), Tout(start = T_Amb), Kv_curve = {{0.0, 0}, {0.01, 0}, {0.1, 0.1}, {0.2, 0.3}, {0.4, 0.5}, {0.6, 0.6}, {0.8, 0.7}, {1.0, 20}, {1.1, 20}}) annotation(Placement(transformation(origin = {-6.0, 80.8751742763535},
    extent = {{-10.0, -10.0}, {10.0, 10.0}},
    rotation = 90.0)));
  Modelica.Blocks.Sources.RealExpression realExpression6(y = valve_pos1) 
    annotation(Placement(transformation(origin = {-47.82913635083776, 80.8751742763535},
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));



  TAThermalSystem.Valves.HydraulicValve.ValveFlowKvCooling zetaFlowCooling1(Tin(start = T_Amb), Tout(start = T_Amb), Kv_curve = {{0.0, 0}, {0.01, 0}, {0.1, 0.1}, {0.2, 0.3}, {0.4, 0.5}, {0.6, 0.6}, {0.8, 0.7}, {1.0, 20}, {1.1, 20}}) annotation(Placement(transformation(origin = {-90.91475999999997, 80.8751742763535},
    extent = {{-10.0, -10.0}, {10.0, 10.0}},
    rotation = 90.0)));
  Modelica.Blocks.Sources.RealExpression realExpression5(y = 1-valve_pos1) 
    annotation(Placement(transformation(origin = {-131.3123730573248, 80.8751742763535},
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TAThermalSystem.Sources.HeatTransfer.BoundaryHeatFlow boundaryHeatFlow2(Q_flow = Q_flowF) 
    annotation(Placement(transformation(origin = {762.0799775677539, -21.892555049073017},
    extent = {{10.0, -10.0}, {-10.0, 10.0}})));
  TAThermalSystem.Sources.HeatTransfer.BoundaryHeatFlow boundaryHeatFlow3(Q_flow = Q_flowR) 
    annotation(Placement(transformation(origin = {821.9013074813198, -26.25514876931964},
    extent = {{10.0, -10.0}, {-10.0, 10.0}})));
  TAThermalSystem.Valves.HydraulicValve.ValveFlowKvCooling zetaFlowCooling(Tin(start = T_Amb), Tout(start = T_Amb), Kv_curve = {{0.0, 0}, {0.01, 0}, {0.1, 0.1}, {0.2, 0.3}, {0.4, 0.5}, {0.6, 0.6}, {0.8, 0.7}, {1.0, 20}, {1.1, 20}}) annotation(Placement(transformation(origin = {792.0, 18.107444950926862},
    extent = {{10.0, -10.0}, {-10.0, 10.0}},
    rotation = 90.0)));
  Modelica.Blocks.Sources.RealExpression realExpression(y = 1-valve_pos2) 
    annotation(Placement(transformation(origin = {762.0930400000003, 18.107444950926865},
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TAThermalSystem.Valves.HydraulicValve.ValveFlowKvCooling valveFlowKvCooling(Tin(start = T_Amb), Tout(start = T_Amb), Kv_curve = {{0.0, 0}, {0.01, 0}, {0.1, 0.1}, {0.2, 0.3}, {0.4, 0.5}, {0.6, 0.6}, {0.8, 0.7}, {1.0, 20}, {1.1, 20}}) 
    annotation(Placement(transformation(origin = {732.0930400000001, 18.107444950926862},
    extent = {{10.0, -10.0}, {-10.0, 10.0}},
    rotation = 90.0)));
  Modelica.Blocks.Sources.RealExpression realExpression2(y = valve_pos2) 
    annotation(Placement(transformation(origin = {694.1860800000003, 18.107444950926865},
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TAThermalSystem.Pipes.LiquidCoolingPipe.CoolingPipe coolingPipeDS1(
    Aheat = 0.18,
    L = 0.2,
    p0 = 1.3e5,
    T0 = T_Amb) 
    annotation(Placement(transformation(origin = {732.1685880607087, -21.939503363508493},
    extent = {{-10.0469483144355, -10.008632925201297}, {10.011048314435497, 10.010082025725545}},
    rotation = 270.0)));
  TAThermalSystem.Pipes.LiquidCoolingPipe.CoolingPipe coolingPipeDS2(
    Aheat = 0.18,
    L = 0.2,
    p0 = 1.3e5,
    T0 = T_Amb) 
    annotation(Placement(transformation(origin = {791.9899179742746, -26.056289169534665},
    extent = {{-10.0469483144355, -10.008632925201297}, {10.011048314435497, 10.010082025725545}},
    rotation = -90.0)));
  TAThermalSystem.Valves.HydraulicValve.ValveFlowKvCooling zetaFlowCooling7(Tin(start = T_Amb), Tout(start = T_Amb), Kv_curve = {{0.0, 0}, {0.01, 0}, {0.1, 0.1}, {0.2, 0.3}, {0.4, 0.5}, {0.6, 0.6}, {0.8, 0.7}, {1.0, 100}, {1.1, 100}}) annotation(Placement(transformation(origin = {510.8431417967836, 214.0},
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  Modelica.Blocks.Sources.RealExpression realExpression12(y = 1) 
    annotation(Placement(transformation(origin = {524.0, 234.0},
    extent = {{10.0, -10.0}, {-10.0, 10.0}})));
  TAThermalSystem.Valves.HydraulicValve.ValveFlowKvCooling valveFlowKvCooling2(Tin(start = T_Amb), Tout(start = T_Amb), Kv_curve = {{0.0, 0}, {0.01, 0}, {0.1, 0.1}, {0.2, 0.3}, {0.4, 0.5}, {0.6, 0.6}, {0.8, 0.7}, {1.0, 20}, {1.1, 20}}) 
    annotation(Placement(transformation(origin = {451.63145665092225, 189.1202027869802},
    extent = {{10.0, -10.0}, {-10.0, 10.0}},
    rotation = 90.0)));
  Modelica.Blocks.Sources.RealExpression realExpression7(y = 0) 
    annotation(Placement(transformation(origin = {427.63145665092196, 189.1202027869802},
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TAThermalSystem.Valves.HydraulicValve.ValveFlowKvCooling valveFlowKvCooling3(Tin(start = T_Amb), Tout(start = T_Amb), Kv_curve = {{0.0, 0}, {0.01, 0}, {0.1, 0.1}, {0.2, 0.3}, {0.4, 0.5}, {0.6, 0.6}, {0.8, 0.7}, {1.0, 20}, {1.1, 20}}) 
    annotation(Placement(transformation(origin = {582.0640146048361, 189.59757203655903},
    extent = {{10.0, -10.0}, {-10.0, 10.0}},
    rotation = 270.0)));
  Modelica.Blocks.Sources.RealExpression realExpression9(y = 0) 
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
    annotation(Placement(transformation(origin = {-6.246858893946168, 216.64387977456684},
    extent = {{-8.169727718157175, -8.435625744212741}, {8.663445506049522, 8.219384140303024}})));
  TYBase.Thermal.FluidHeatFlow.ControlVolumes.CVBasic.ThermalHydraulicCV.BranchPipeCoolingCV branchPipeCoolingCV5(p0 = 2.899999999999999e5,
    T0 = T_Amb) 
    annotation(Placement(transformation(origin = {-5.827354466629913, -99.57236182934282},
    extent = {{-8.169727718157175, 8.435625744212741}, {8.663445506049522, -8.219384140303024}})));
  TAThermalSystem.Pipes.LiquidCoolingPipe.CoolingPipeR coolingPipeR(p0 = 2.7e5,
    T0 = T_Amb) 
    annotation(Placement(transformation(origin = {176.51795000000018, 216.68165380492104},
    extent = {{-10.0997, -8.821720000000001}, {10.0638, 9.007800000000001}})));
  Modelica.Blocks.Sources.RealExpression realExpression10(y = ComprSpd_rpm) 
    annotation(Placement(transformation(origin = {9.999999999999886, 120.87517427635349},
    extent = {{-10, -10}, {10, 10}})));
  Modelica.Mechanics.Rotational.Sources.Speed speed 
    annotation(Placement(transformation(origin = {54.00000000000003, 120.87517427635349},
    extent = {{-10, -10}, {10, 10}})));
  TAThermalSystem.HeatExchangers.Condenser condenser(
  redeclare package Medium = TYMedia.Helmholtz.R134a,
    n_segRef = 1,
    n_segMtl = 1, HX_Init(T0 = T_Amb, T_air0 = T_Amb),redeclare TYBase.Thermal.FluidHeatFlow.Components.BasicComponents.Records.PropertiesRecords.WallMaterialType.WallMaterialAluminium wallmaterial,CF_RefrigerantSideHeatTransfer=10,CF_AirSideHeatTransfer=10,RefrigerantTemperature=15,RefrigerantMass=0.117458) 

    annotation(Placement(transformation(origin = {41.24967211432738, 64.87517427635349},
    extent = {{10.0, 10.0}, {-10.0, -10.0}},
    rotation = 90.0)));
  TAThermalSystem.Sources.Air.AirSink_pT airSink1(T_sink = 293.15,
    phi_sink = 0.4) annotation(Placement(transformation(origin = {67.24967211432738, 92.79697090522448},
    extent = {{10.0, -10.0}, {-10.0, 10.0}})));
  TAThermalSystem.Sources.Air.AirSource_mT airSource1(m = 0.1, T = T_out,
    phi_source = 0.4) annotation(Placement(transformation(origin = {69.24967211432738, 42.09891735367499},
    extent = {{10.0, -10.0}, {-10.0, 10.0}})));
  TAThermalSystem.Compressor.Compressor compressorR134a(
    p0_in = 4.999999999999999e5, p0_out = 9.999999999999999e5,
    MaximumDisplacement = 3.3e-5,redeclare package Medium = TYMedia.Helmholtz.R134a) 
    annotation(Placement(transformation(origin = {77.24967211432732, 152.87517427635345},
    extent = {{10.0, -10.0}, {-10.0, 10.0}})));
  Modelica.Blocks.Math.Gain gain(k = Modelica.Constants.pi / 30) 
    annotation(Placement(transformation(origin = {32, 120.87517427635355},
    extent = {{-6, -6}, {6, 6}})));
  TAThermalSystem.Reservoirs.Reservoir reservoir(redeclare package Medium = TYMedia.Helmholtz.R134a,
    FromDp = false, zeta = 1000,RefrigerantTemperature=15,RefrigerantMass=0.238672,RefrigerantMassDistribution=1) 
    annotation(Placement(transformation(origin = {117.99999999999997, 152.77517427635345},
    extent = {{10.0, -10.0}, {-10.0, 10.0}})));
  TAThermalSystem.Sensors.Refrigerant.SuperHeatingSensor superHeatingSensor(h0_in = 2.7e5, h0_out = 2.7e5,redeclare package Medium = TYMedia.Helmholtz.R134a) annotation(Placement(transformation(origin = {158.75032788567256, 152.77517427635345},
    extent = {{10.0, -10.0}, {-10.0, 10.0}})));
  TAThermalSystem.Sensors.Refrigerant.SuperCoolingSensor superCoolingSensor(redeclare package Medium = TYMedia.Helmholtz.R134a) 
    annotation(Placement(transformation(origin = {118.0, -19.854781018718846},
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TAThermalSystem.HeatExchangers.Evaporator evaporatorR134a(HX_Init(T0 = T_Amb, T_air0 = T_Amb),redeclare TYBase.Thermal.FluidHeatFlow.Components.BasicComponents.Records.PropertiesRecords.WallMaterialType.WallMaterialAluminium wallmaterial,redeclare package Medium = TYMedia.Helmholtz.R134a,CF_RefrigerantSideHeatTransfer=10,CF_AirSideHeatTransfer=10,RefrigerantTemperature=15,RefrigerantMass=0.0734114) annotation(Placement(transformation(origin = {203.24967211432738, 100.8751742763535},
    extent = {{-10.0, -10.0}, {10.0, 10.0}},
    rotation = 90.0)));
  TAThermalSystem.Valves.RefrigerantValve.ZetaFlow zetaFlow(redeclare package Medium = TYMedia.Helmholtz.R134a,
    Tin(start
    = 293.15),
    Tout(start
    = 293.15),
    Dhyd(displayUnit
    = "mm") =
    0.005,
    zeta = 2000) annotation(Placement(transformation(origin = {209.24967211432735, 46.875174276353505},
    extent = {{10.0, -10.0}, {-10.0, 10.0}},
    rotation = -90.0)));
  TAThermalSystem.PumpAndFan.SimpleFan simpleFan(mdot_nom = 0.1,
    T(start



    = T_Amb)) 
    annotation(Placement(transformation(origin={237.33,63.0736},
extent={{10,-10},{-10,10}})));
  TAThermalSystem.Heating.CabinHeatNetwork cabinVolume(n_Passenger = 4, V = 1,T_interior=T_Amb,T_ext=T_Amb) 
    annotation(Placement(transformation(origin={285.326,62.7209},
extent={{10,-10},{-10,10}})));
  TAThermalSystem.Pipes.AirPass.HXAirResis hXAirResis(n_channels = 50,
  redeclare package Medium = TYBase.Media_Extend.Air.MoistAir,
    T_in(start



    = T_Amb),
    T_out(start



    = T_Amb),
    Tw(start



    = T_Amb)) 
    annotation(Placement(transformation(origin={318.588,62.7209},
extent={{10,-10},{-10,10}})));
  TAThermalSystem.Utilities.DynamicDisplay.Single_Display single_Display1(
    variable = cabinVolume.cabinVolume.T - 273.15, blockname = "乘员舱温度/°C") annotation(Placement(transformation(origin={284.801,24.0301},
extent={{-15,3},{21,15}})));
  TAThermalSystem.Pipes.LiquidCoolingPipe.CoolingPipeDS coolingPipeDS(n = 1, title = "水管道", Dhyd = 0.025, Aheat = 0.1918,
    p0 = 2.5e5, T0 = T_Amb) 
    annotation(Placement(transformation(origin = {583.6652421532535, 111.97883153853836},
    extent = {{10.0469483144355, -10.008632925201297}, {-10.011048314435497, 10.010082025725545}},
    rotation = -90.0)));
  Modelica.Blocks.Sources.RealExpression realExpression8(y = BattPump_rpm*Modelica.Constants.pi / 30) 
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
  Modelica.Electrical.Analog.Sources.ConstantCurrent constantCurrent(I = 66 * 2*0) 
    annotation(Placement(transformation(origin = {635.8307332816713, 53.53340569962002},
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TAThermalSystem.Valves.HydraulicValve.ValveFlowKvCooling zetaFlowCooling6(Tin(start = T_Amb), Tout(start = T_Amb), mdot(start = 0.1)) annotation(Placement(transformation(origin = {510.5147736437889, 161.21759848926388},
    extent = {{10.0, -10.0}, {-10.0, 10.0}})));
  Modelica.Blocks.Sources.RealExpression realExpression11(y = 1) 
    annotation(Placement(transformation(origin = {530.0147736437889, 182.08758579165664},
    extent = {{10.0, -10.0}, {-10.0, 10.0}})));
  Modelica.Blocks.Sources.RealExpression realExpression13(y = HtrPump_rpm* Modelica.Constants.pi / 30) 
    annotation(Placement(transformation(origin = {274.8307332816713, 118.65158581990337},
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  Modelica.Mechanics.Rotational.Sources.Speed speed5 
    annotation(Placement(transformation(origin = {308.8307332816713, 118.65158581990337},
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TAThermalSystem.PumpAndFan.CentrifugalPump centrifugal_pump5(T_inlet(start = T_Amb), T_outlet(start = T_Amb), T_start = T_Amb, pin_start = 90000, pout_start = 3e5, m_flow_start = 0.1) 
    annotation(Placement(transformation(origin = {346.78465910979935, 118.65158581990332},
    extent = {{-10.0, -10.0}, {10.0, 10.0}},
    rotation = 270.0)));
  TAThermalSystem.Valves.HydraulicValve.ValveFlowKvCooling valveFlowKvCooling4(Tin(start = T_Amb), Tout(start = T_Amb), Kv_curve = {{0.0, 0}, {0.01, 0}, {0.1, 1}, {0.2, 3}, {0.4, 5}, {0.6, 6}, {0.8, 7}, {1.0, 20}, {1.1, 20}}) 
    annotation(Placement(transformation(origin = {391.628586525727, 54.573884389299664},
    extent = {{-10.0, -10.0}, {10.0, 10.0}},
    rotation = 90.0)));
  TAThermalSystem.Valves.HydraulicValve.ValveFlowKvCooling valveFlowKvCooling5(Tin(start = T_Amb), Tout(start = T_Amb), Kv_curve = {{0.0, 0}, {0.01, 0}, {0.1, 1}, {0.2, 3}, {0.4, 5}, {0.6, 6}, {0.8, 7}, {1.0, 20}, {1.1, 20}}) 
    annotation(Placement(transformation(origin = {426.19156982858453, 13.270939063621995},
    extent = {{10.0, -10.0}, {-10.0, 10.0}},
    rotation = 180.0)));
  Modelica.Blocks.Sources.RealExpression realExpression14(y = 1-valve_pos3) 
    annotation(Placement(transformation(origin = {404.3501803278682, -11.809500960940186},
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  Modelica.Blocks.Sources.RealExpression realExpression15(y = valve_pos3) 
    annotation(Placement(transformation(origin = {365.65212361071394, 54.365342302811925},
    extent = {{-10.028998314435484, -8.327504942257882}, {10.028998314435512, 8.327504942257882}})));
  TAThermalSystem.Reservoirs.ExpansionTank expansion_tank1(tank1(
    pInitial = 0.9e5),
    T_Amb = T_Amb,
    zetaFlowCooling9(FromDp = false)) 

    annotation(Placement(transformation(origin = {505.8307332816713, 13.308713093976166},
    extent = {{10.0, -10.0}, {-10.0, 10.0}})));
  TAThermalSystem.Pipes.LiquidCoolingPipe.CoolingPipeR coolingPipe(p0 = 1.9e5, T0 = T_Amb) annotation(Placement(transformation(origin = {361.69138522096296, 13.177899063622021},
    extent = {{-10.0997, -8.821720000000001}, {10.0638, 9.007800000000001}})));
  TAThermalSystem.Pipes.LiquidCoolingPipe.CoolingPipe coolingPipe1(p0 = 90000, T0 = T_Amb) 
    annotation(Placement(transformation(origin = {362.18821780709675, 161.6533267520288},
    extent = {{10.0997, -8.821720000000001}, {-10.0638, 9.007800000000001}})));
  TAThermalSystem.Sources.HeatTransfer.BoundaryHeatFlow boundaryHeatFlow7(Q_flow = Q_flow, n = 1) 
    annotation(Placement(transformation(origin = {302.8307332816711, 86.65158581990332},
    extent = {{10.0, -10.0}, {-10.0, 10.0}},
    rotation = 180.0)));
  TAThermalSystem.HeatExchangers.CoolingRadiatorNTU.Water_Air_HXNTU water_air_HXTU2(
    ConsiderMass = false, redeclare model Friction_ab = TYBase.Thermal.FluidHeatFlow.PressureLoss.HXPressureDrop.SingularPressureDrop, Across1(displayUnit = "cm2") = 0.01, Dhyd1(displayUnit = "mm") = 0.1, cearea1(displayUnit = "m2") = 4, ConsiderationFins_cd = false,
    etas2 = 0.8, ConsiderationFins_ab = false, fromDp = false,
    T1_a(start = T_Amb), T1_b(start = T_Amb), T2_in(start = T_Amb), T2_out(start = T_Amb), Twall(start = T_Amb),
    L = 5, Across2 = 0.01, cearea2(displayUnit = "m2") = 4) 
    annotation(Placement(transformation(origin = {340.91369125594576, 36.408579975973495},
    extent = {{-10.0, -10.0}, {10.0, 10.0}},
    rotation = 270.0)));
  TAThermalSystem.Pipes.LiquidCoolingPipe.CoolingPipeCR coolingPipeCR1(p0 = 2.5e5, T0 = T_Amb) annotation(Placement(transformation(origin = {346.8776991097992, 86.07454575976166},
    extent = {{10.0997, -8.821720000000001}, {-10.0638, 9.007800000000001}},
    rotation = 90.0)));
  TYBase.Thermal.FluidHeatFlow.ControlVolumes.CVBasic.ThermalHydraulicCV.BranchPipeCoolingCV branchPipeCoolingCV6(p0 = 1.4e5,
    T0 = T_Amb) 
    annotation(Placement(transformation(origin = {459.25142000213845, 14.693390421119949},
    extent = {{-8.169727718157175, 8.435625744212741}, {8.663445506049522, -8.219384140303024}})));
  TYBase.Thermal.FluidHeatFlow.ControlVolumes.CVBasic.ThermalHydraulicCV.BranchPipeCoolingCV branchPipeCoolingCV7(p0 = 1.8e5,
    T0 = T_Amb) 
    annotation(Placement(transformation(origin = {392.1574937699173, 11.369873243592595},
    extent = {{-8.169727718157175, 8.435625744212741}, {8.663445506049522, -8.219384140303024}})));
  TYBase.Thermal.FluidHeatFlow.ControlVolumes.CVBasic.ThermalHydraulicCV.BranchPipeCoolingCV branchPipeCoolingCV8(p0 = 100000,
    T0 = T_Amb) 
    annotation(Placement(transformation(origin = {391.31107352976454, 161.7580731649298},
    extent = {{-8.169727718157175, -8.435625744212741}, {8.663445506049522, 8.219384140303024}})));
  TYBase.Thermal.FluidHeatFlow.ControlVolumes.CVBasic.ThermalHydraulicCV.BranchPipeCoolingCV branchPipeCoolingCV9(p0 = 1.8e5,
    T0 = T_Amb) 
    annotation(Placement(transformation(origin = {457.0150127227007, 160.37071565267925},
    extent = {{-8.169727718157175, -8.435625744212741}, {8.663445506049522, 8.219384140303024}})));
  TAThermalSystem.HeatExchangers.CoolingRadiatorNTU.ChillerPlateCooling chillerPlate(redeclare model Friction = TYBase.Thermal.FluidHeatFlow.PressureLoss.LiquidPressureDrop.SingularPressureDrop, water(redeclare model Friction = TYBase.Thermal.FluidHeatFlow.PressureLoss.LiquidPressureDrop.SingularPressureDrop),

    p0 = 1.6e5,
    T0 = T_Amb,redeclare package RefMedium = TYMedia.Helmholtz.R134a,simplePipe(RefrigerantTemperature=15,RefrigerantMass=0.270458,RefrigerantMassDistribution=1)) 



    annotation(Placement(transformation(origin = {445.55958570535853, 92.89553836607635},
    extent = {{10, -10}, {-10, 10}},
    rotation = -90)));
  TAThermalSystem.Valves.RefrigerantValve.ZetaFlow zetaFlow1(redeclare package Medium = TYMedia.Helmholtz.R134a,
    Tin(start
    = 293.15),
    Tout(start
    = 293.15),
    Dhyd(displayUnit
    = "mm") =
    0.0005,
    zeta = 2000) annotation(Placement(transformation(origin = {439.55958570535853, 44.2292759515003},
    extent = {{10.0, -10.0}, {-10.0, 10.0}},
    rotation = 270.0)));
  TAThermalSystem.Pipes.LiquidCoolingPipe.CoolingPipeR coolingPipe2(p0 = 1.5e5, T0 = T_Amb, L = 0.1, TA(start = T_Amb), TB(start = T_Amb)) annotation(Placement(transformation(origin = {459.33979551534605, 62.3375967174169},
    extent = {{10.0997, -8.821720000000001}, {-10.0638, 9.007800000000001}},
    rotation = 90.0)));
  TAThermalSystem.Pipes.LiquidCoolingPipe.CoolingPipeR coolingPipe3(p0 = 1.7e5, T0 = T_Amb, L = 0.1, TA(start = T_Amb), TB(start = T_Amb)) annotation(Placement(transformation(origin = {461.2242841503515, 123.41758001473582},
    extent = {{10.0997, -8.821720000000001}, {-10.0638, 9.007800000000001}},
    rotation = 90.0)));
  TYBase.Thermal.FluidHeatFlow.ControlVolumes.CVBasic.ThermalHydraulicCV.BranchPipeCoolingCV branchPipeCoolingCV3(p0 = 2.3e5,
    T0 = T_Amb) 
    annotation (Placement(transformation(origin={581.652,160.578},
extent={{-8.16973,-8.43563},{8.66345,8.21938}},
rotation=-90)));
  TAThermalSystem.Pipes.AirPass.AirSplit airSplit 
    annotation (Placement(transformation(origin={260.452,63.1164},
extent={{10,10},{-10,-10}})));
  TAThermalSystem.Sources.Air.AirSink_pT airSink_pT(T_sink=T_Amb) 
    annotation (Placement(transformation(origin={246.229,42.17},
extent={{-10,-10},{10,10}})));
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
    annotation(Line(origin = {-7.829136350837729, -37.87865894566121},
    points = {{-30.0, 3.0}, {-10.0, 3.0}, {-10.0, 5.0}},
    color = {0, 232, 232},
    thickness = 1.0));
  connect(water_air_HXTU1.c, airSource_mT2.port_b) 
    annotation(Line(origin = {29.17086364916227, -36.87865894566121},
    points = {{-47.0, 24.0}, {-47.0, 47.0}, {-67.0, 47.0}, {-67.0, 46.0}},
    color = {0, 232, 232},
    thickness = 1.0));
  connect(expansion_tank.b, centrifugal_pump2.a) 
    annotation(Line(origin = {93.79522611464964, 18.20825403035414},
    points = {{34.0, -118.0}, {20.0, -118.0}},
    color = {0, 170, 255},
    thickness = 1.0));
  connect(speed1.flange, centrifugal_pump2.flange) 
    annotation(Line(origin = {105.95872611464964, -121.04215894566121},
    points = {{-4.0, -11.0}, {-4.0, 13.0}, {-2.0, 13.0}, {-2.0, 11.0}},
    color = {0, 0, 0}));
  connect(centrifugal_pump2.b, coolingPipeCR.a) 
    annotation(Line(origin = {94.7560417849883, -39.79174596964586},
    points = {{-1.0, -60.0}, {-47.0, -60.0}, {-47.0, -59.0}},
    color = {0, 170, 255},
    thickness = 1.0));
  connect(branchPipeCoolingCV5.c, coolingPipeCR.b) 
    annotation(Line(origin = {21.131679319500975, -45.87865894566123},
    points = {{-17.0, -54.0}, {7.0, -54.0}, {7.0, -53.0}},
    color = {0, 170, 255},
    thickness = 1.0));
  connect(realExpression6.y, zetaFlowCooling2.u) 
    annotation(Line(origin = {199.82952000000003, 33.20127403035422},
    points = {{-237.0, 48.0}, {-216.0, 48.0}},
    color = {0, 0, 127}));


  connect(zetaFlowCooling1.u, realExpression5.y) 
    annotation(Line(origin = {-112.31237305732482, 80.62476130033811},
    points = {{11.0, 0.0}, {-8.0, 0.0}},
    color = {0, 0, 127}));
  connect(realExpression.y, zetaFlowCooling.u) 
    annotation(Line(origin = {762.0930400000003, -44.756355049073136},
    points = {{11.0, 63.0}, {20.0, 63.0}},
    color = {0, 0, 127}));
  connect(realExpression2.y, valveFlowKvCooling.u) 
    annotation(Line(origin = {550.1860800000004, 18.10744495092692},
    points = {{155.0, 0.0}, {172.0, 0.0}},
    color = {0, 0, 127}));
  connect(valveFlowKvCooling.b, coolingPipeDS1.a) 
    annotation(Line(origin = {732.0930400000003, -2.0093408550991967},
    points = {{0.0, 10.0}, {0.0, -10.0}},
    color = {0, 170, 255},
    thickness = 1.0));
  connect(coolingPipeDS2.a, zetaFlowCooling.b) 
    annotation(Line(origin = {792.0930400000003, -4.009340855099197},
    points = {{0.0, -12.0}, {0.0, 12.0}},
    color = {0, 170, 255},
    thickness = 1.0));
  connect(boundaryHeatFlow2.port[1], coolingPipeDS1.qa) 
    annotation(Line(origin = {748.0930400000003, -22.009340855099254},
    points = {{4.0, 0.0}, {-5.0, 0.0}},
    color = {191, 0, 0},
    thickness = 1.0));
  connect(coolingPipeDS2.qa, boundaryHeatFlow3.port[1]) 
    annotation(Line(origin = {807.0930400000003, -26.009340855099254},
    points = {{-4.0, 0.0}, {5.0, 0.0}},
    color = {191, 0, 0},
    thickness = 1.0));
  connect(zetaFlowCooling1.a, branchPipeCoolingCV5.a) 
    annotation(Line(origin = {-48.99999999999997, -14.962225969645857},
    points = {{-42.0, 86.0}, {-42.0, -85.0}, {33.0, -85.0}},
    color = {0, 170, 255},
    thickness = 1.0));
  connect(speed1.w_ref, realExpression1.y) 
    annotation(Line(origin = {59.00000000000003, -131.96222596964586},
    points = {{21.0, 0.0}, {-21.0, 0.0}},
    color = {0, 0, 127}));
  connect(zetaFlowCooling7.u, realExpression12.y) 
    annotation(Line(origin = {516.932134418143, 237.73291853853922},
    points = {{-6.0, -14.0}, {-6.0, -4.0}, {-4.0, -4.0}},
    color = {0, 0, 127}));

  connect(zetaFlowCooling1.b, branchPipeCoolingCV4.a) 
    annotation(Line(origin = {13.000000000000028, 154.03777403035411},
    points = {{-104.0, -63.0}, {-104.0, 63.0}, {-29.0, 63.0}},
    color = {0, 170, 255},
    thickness = 1.0));
  connect(zetaFlowCooling2.b, branchPipeCoolingCV4.b) 
    annotation(Line(origin = {55.00000000000003, 154.03777403035411},
    points = {{-61.0, -63.0}, {-61.0, 53.0}},
    color = {0, 170, 255},
    thickness = 1.0));
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
    annotation(Line(origin = {85.00000000000003, 217.03777403035411},
    points = {{-81.0, 0.0}, {82.0, 0.0}},
    color = {0, 170, 255},
    thickness = 1.0));
  connect(coolingPipeR.b, branchPipeCoolingCV.a) 
    annotation(Line(origin = {284.6314566509221, 217.1579768173343},
    points = {{-98.0, -1.0}, {157.0, -1.0}, {157.0, -2.0}},
    color = {0, 170, 255},
    thickness = 1.0));
  connect(coolingPipeDS1.b, expansion_tank.a) 
    annotation(Line(origin = {401.9225600000002, -40.18876101871902},
    points = {{330.0, 8.0}, {330.0, -58.0}, {-254.0, -58.0}, {-254.0, -60.0}},
    color = {0, 170, 255},
    thickness = 1.0));
  connect(coolingPipeDS2.b, expansion_tank.a) 
    annotation(Line(origin = {431.9225600000002, -42.18876101871902},
    points = {{360.0, 6.0}, {360.0, -56.0}, {-284.0, -56.0}, {-284.0, -58.0}},
    color = {0, 170, 255},
    thickness = 1.0));
  connect(speed.flange, compressorR134a.flange) 
    annotation(Line(origin = {106.24967211432735, 133.87517427635353},
    points = {{-42.249672114327325, -13.000000000000043}, {-29.00000000000003, -13.000000000000043}, {-29.00000000000003, 8.999999999999915}},
    color = {0, 0, 0}));
  connect(airSource1.port_b, condenser.air_in) 
    annotation(Line(origin = {51.249672114327296, 32.875174276353505},
    points = {{8.0, 9.0}, {8.0, 22.0}, {-4.0, 22.0}},
    color = {0, 232, 232},
    thickness = 1.0));
  connect(airSink1.port_a, condenser.air_out) 
    annotation(Line(origin = {51.249672114327296, 68.87517427635352},
    points = {{6.0, 24.0}, {6.0, 8.0}, {-4.0, 8.0}, {-4.0, 6.0}},
    color = {0, 232, 232},
    thickness = 1.0));
  connect(realExpression10.y, gain.u) 
    annotation(Line(origin = {4.999999999999943, 120.87517427635358},
    points = {{15.999999999999943, -8.526512829121202e-14}, {19.800000000000054, -8.526512829121202e-14}, {19.800000000000054, -2.842170943040401e-14}},
    color = {0, 0, 127}));
  connect(gain.y, speed.w_ref) 
    annotation(Line(origin = {33.99999999999994, 120.87517427635358},
    points = {{4.600000000000051, -2.842170943040401e-14}, {8.000000000000085, -2.842170943040401e-14}, {8.000000000000085, -8.526512829121202e-14}},
    color = {0, 0, 127}));
  connect(reservoir.b, compressorR134a.a) 
    annotation(Line(origin = {128.2496721143273, 153.23517427635355},
    points = {{-20.0, -1.0}, {-41.0, -1.0}, {-41.0, 0.0}},
    color = {0, 128, 0},
    thickness = 1.0));
  connect(compressorR134a.b, condenser.a1) 
    annotation(Line(origin = {-13.750327885672647, 97.23517427635355},
    points = {{81.0, 56.0}, {50.0, 56.0}, {50.0, -22.0}, {49.0, -22.0}},
    color = {0, 128, 0},
    thickness = 1.0));
  connect(reservoir.port_a, superHeatingSensor.b) 
    annotation(Line(origin = {174.2496721143273, 153.03777403035411},
    points = {{-46.0, 0.0}, {-25.0, 0.0}},
    color = {0, 128, 0},
    thickness = 1.0));
  connect(condenser.b1, superCoolingSensor.a) 
    annotation(Line(origin = {78.2496721143273, 37.037774030354115},
    points = {{-43.0, 18.0}, {-43.0, -57.0}, {30.0, -57.0}},
    color = {0, 128, 0},
    thickness = 1.0));
  connect(zetaFlow.b, evaporatorR134a.a1) 
    annotation(Line(origin = {217.24967211432735, 38.875174276353505},
    points = {{-8.0, 18.0}, {-8.0, 52.0}},
    color = {0, 128, 0},
    thickness = 1.0));
  connect(superHeatingSensor.a, evaporatorR134a.b1) 
    annotation(Line(origin = {204.2496721143273, 132.03777403035411},
    points = {{-35.0, 21.0}, {5.0, 21.0}, {5.0, -21.0}},
    color = {0, 128, 0},
    thickness = 1.0));
  connect(zetaFlow.a, superCoolingSensor.b) 
    annotation(Line(origin = {176.2496721143273, 29.037774030354115},
    points = {{33.0, 8.0}, {32.0, 8.0}, {32.0, -49.0}, {-48.0, -49.0}},
    color = {0, 128, 0},
    thickness = 1.0));
  connect(hXAirResis.b, cabinVolume.a) 
    annotation(Line(origin={238.326,47.6202},
points={{70.262,15.1007},{57.2,15.1007}},
color={0,232,232},
thickness=1));
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
  connect(realExpression13.y, speed5.w_ref) 
    annotation(Line(origin = {288.8307332816713, 118.65158581990335},
    points = {{-3.0, 0.0}, {8.0, 0.0}},
    color = {0, 0, 127}));
  connect(centrifugal_pump5.flange, speed5.flange) 
    annotation(Line(origin = {341.78465910979924, 93.65158581990329},
    points = {{-5.0, 25.0}, {-23.0, 25.0}},
    color = {0, 0, 0}));
  connect(valveFlowKvCooling4.u, realExpression15.y) 
    annotation(Line(origin = {369.51341355136304, 34.70081420549173},
    points = {{12.0, 20.0}, {7.0, 20.0}},
    color = {0, 0, 127}));
  connect(valveFlowKvCooling5.u, realExpression14.y) 
    annotation(Line(origin = {405.8307332816712, 2.1524796069744525},
    points = {{20.0, 1.0}, {20.0, -14.0}, {10.0, -14.0}},
    color = {0, 0, 127}));
  connect(expansion_tank1.b, centrifugal_pump4.a) 
    annotation(Line(origin = {549.8307332816713, 23.152479606974453},
    points = {{-34.0, -10.0}, {34.0, -10.0}, {34.0, 9.0}},
    color = {0, 170, 255},
    thickness = 1.0));
  connect(water_air_HXTU2.b, coolingPipe.a) 
    annotation(Line(origin = {349.8307332816712, 28.152479606974453},
    points = {{-3.0, -2.0}, {-3.0, -15.0}, {2.0, -15.0}},
    color = {0, 170, 255},
    thickness = 1.0));
  connect(coolingPipeCR1.qa, boundaryHeatFlow7.port[1]) 
    annotation(Line(origin = {332.8307332816712, 87.15247960697445},
    points = {{4.0, -1.0}, {-20.0, -1.0}},
    color = {191, 0, 0},
    thickness = 1.0));
  connect(centrifugal_pump5.b, coolingPipeCR1.a) 
    annotation(Line(origin = {346.8307332816712, 103.15247960697445},
    points = {{0.0, 5.0}, {0.0, -7.0}},
    color = {0, 170, 255},
    thickness = 1.0));
  connect(coolingPipeCR1.b, water_air_HXTU2.a) 
    annotation(Line(origin = {346.8307332816712, 61.15247960697445},
    points = {{0.0, 15.0}, {0.0, -15.0}},
    color = {0, 170, 255},
    thickness = 1.0));
  connect(coolingPipe1.b, centrifugal_pump5.a) 
    annotation(Line(origin = {353.8307332816712, 141.15247960697445},
    points = {{-2.0, 20.0}, {-8.0, 20.0}, {-8.0, -12.0}, {-7.0, -12.0}},
    color = {0, 170, 255},
    thickness = 1.0));
  connect(valveFlowKvCooling5.b, branchPipeCoolingCV6.a) 
    annotation(Line(origin = {444.8307332816713, 13.152479606974453},
    points = {{-9.0, 0.0}, {4.0, 0.0}, {4.0, 2.0}},
    color = {0, 170, 255},
    thickness = 1.0));
  connect(branchPipeCoolingCV6.c, expansion_tank1.a) 
    annotation(Line(origin = {489.8307332816713, 13.152479606974453},
    points = {{-21.0, 2.0}, {6.0, 2.0}, {6.0, 0.0}},
    color = {0, 170, 255},
    thickness = 1.0));
  connect(coolingPipe.b, branchPipeCoolingCV7.a) 
    annotation(Line(origin = {374.8307332816712, 13.152479606974453},
    points = {{-3.0, 0.0}, {7.0, 0.0}, {7.0, -2.0}},
    color = {0, 170, 255},
    thickness = 1.0));
  connect(branchPipeCoolingCV7.c, valveFlowKvCooling5.a) 
    annotation(Line(origin = {406.8307332816712, 13.152479606974453},
    points = {{-5.0, -2.0}, {-5.0, 0.0}, {9.0, 0.0}},
    color = {0, 170, 255},
    thickness = 1.0));
  connect(branchPipeCoolingCV7.b, valveFlowKvCooling4.a) 
    annotation(Line(origin = {391.51341355136304, 32.70081420549173},
    points = {{1.0, -11.0}, {1.0, 12.0}, {0.0, 12.0}},
    color = {0, 170, 255},
    thickness = 1.0));
  connect(branchPipeCoolingCV9.c, zetaFlowCooling6.b) 
    annotation(Line(origin = {502.1487651319631, 160.93505528594494},
    points = {{-35.0, -1.0}, {-2.0, -1.0}, {-2.0, 0.0}},
    color = {0, 170, 255},
    thickness = 1.0));
  connect(valveFlowKvCooling4.b, branchPipeCoolingCV8.b) 
    annotation(Line(origin = {394.8307332816712, 105.15247960697445},
    points = {{-3.0, -40.0}, {-3.0, 47.0}, {-4.0, 47.0}},
    color = {0, 170, 255},
    thickness = 1.0));
  connect(branchPipeCoolingCV8.a, coolingPipe1.a) 
    annotation(Line(origin = {385.8307332816712, 153.15247960697445},
    points = {{-5.0, 9.0}, {-14.0, 9.0}, {-14.0, 8.0}},
    color = {0, 170, 255},
    thickness = 1.0));
  connect(branchPipeCoolingCV8.c, branchPipeCoolingCV9.a) 
    annotation(Line(origin = {412.73650070902505, 153.48298194094133},
    points = {{-11.0, 8.0}, {34.0, 8.0}, {34.0, 7.0}},
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
    annotation(Line(origin = {203.2496721143273, 29.037774030354115},
    points = {{-75.0, -49.0}, {236.0, -49.0}, {236.0, 5.0}},
    color = {0, 128, 0},
    thickness = 1.0));
  connect(chillerPlate.b, superHeatingSensor.a) 
    annotation(Line(origin = {217.08706202680955, 134.07554806070823},
    points = {{222.47252367854898, -31.180009694631877}, {222.47252367854898, 18.699626215645225}, {-48.336734141136986, 18.699626215645225}},
    color = {0, 128, 0},
    thickness = 1));
  connect(chillerPlate.d, coolingPipe2.a) 
    annotation(Line(origin = {456, 79},
    points = {{-4.440414294641471, 3.8955383660763516}, {-4.440414294641471, -3.6522852387382443}, {3.377569545700169, -3.6522852387382443}, {3.377569545700169, -6.652285238738244}},
    color = {0, 170, 255},
    thickness = 1));
  connect(coolingPipe2.b, branchPipeCoolingCV6.b) 
    annotation(Line(origin = {459.0, 39.0},
    points = {{0.0, 13.0}, {0.0, -14.0}},
    color = {0, 170, 255},
    thickness = 1.0));
  connect(branchPipeCoolingCV9.b, coolingPipe3.a) 
    annotation(Line(origin = {461.0, 144.0},
    points = {{-4.0, 6.0}, {-4.0, -11.0}, {0.0, -11.0}},
    color = {0, 170, 255},
    thickness = 1.0));
  connect(coolingPipe3.b, chillerPlate.c) 
    annotation(Line(origin = {459, 112},
    points = {{2.262058180705594, 1.2941398798285633}, {2.262058180705594, -6.104461633923648}, {-7.440414294641471, -6.104461633923648}, {-7.440414294641471, -9.104461633923648}},
    color = {0, 170, 255},
    thickness = 1));
  connect(water_air_HXTU1.b, zetaFlowCooling2.a) 
    annotation(Line(origin = {-6.0, 29.0},
    points = {{0.0, -42.0}, {0.0, 42.0}},
    color = {0, 170, 255},
    thickness = 1.0));
  connect(branchPipeCoolingCV5.b, water_air_HXTU1.a) 
    annotation(Line(origin = {-6.0, -61.0},
    points = {{0.17264553337008692, -28.572361829342825}, {0.17264553337003097, 28.107131955407866}},
    color = {0, 170, 255},
    thickness = 1.0));
  connect(evaporatorR134a.air_out, water_air_HXTU2.c) 
  annotation(Line(origin={266,57},
points={{-68.75032788567262,33.875174276353505},{-68.75032788567262,-51},{68.87628881049221,-51},{68.87628881049221,-30.70332559769257}},
color={0,232,232},
thickness=1));
  connect(valveFlowKvCooling.a, branchPipeCoolingCV2.c) 
  annotation(Line(origin={662,122},
  points={{70.13081403035426,-93.88243700522828},{70.13081403035426,93.37818789625598},{-70.18284428911022,93.37818789625598}},
  color={0,170,255},
  thickness=1));
  connect(zetaFlowCooling.a, branchPipeCoolingCV2.c) 
  annotation(Line(origin={692,122},
points={{100.03777403035417,-93.88243700522828},{100.03777403035417,93.37818789625598},{-100.18284428911022,93.37818789625598}},
color={0,170,255},
thickness=1));
  connect(zetaFlowCooling6.a, branchPipeCoolingCV3.b) 
  annotation(Line(origin={544,161},
points={{-23.4751,0.179824},{27.6521,0.179824},{27.6521,-0.422004}},
color={0,170,255},
thickness=1));
  connect(branchPipeCoolingCV3.c, coolingPipeDS.b) 
  annotation(Line(origin={580,136},
points={{1.65206,14.578},{1.65206,-13.8977},{3.62747,-13.8977}},
color={0,170,255},
thickness=1));
  connect(branchPipeCoolingCV3.a, valveFlowKvCooling3.a) 
  annotation(Line(origin={579,175},
points={{2.65206,-4.422},{2.65206,4.58745},{3.02624,4.58745}},
color={0,170,255},
thickness=1));
  connect(airSink_pT.port_a, airSplit.b2) 
  annotation(Line(origin={258.441,47.3864},
points={{-2.2113,-5.2164},{2.0116,-5.2164},{2.0116,5.73}},
color={0,232,232},
thickness=1));
  connect(water_air_HXTU2.d, hXAirResis.a) 
  annotation(Line(origin={332,55},
  points={{2.75733,-8.62822},{2.75733,7.7209},{-3.41248,7.7209}},
  color={0,232,232},
  thickness=1));
  connect(cabinVolume.b, airSplit.a) 
  annotation(Line(origin={273,63},
  points={{2.12552,-0.2791},{-2.54781,-0.2791},{-2.54781,0.116448}},
  color={0,232,232},
  thickness=1));
  connect(airSplit.b1, simpleFan.a) 
  annotation(Line(origin={249,63},
  points={{1.45219,0.116448},{-1.67014,0.116448},{-1.67014,0.0736}},
  color={0,232,232},
  thickness=1));
  connect(simpleFan.b, evaporatorR134a.air_in) 
  annotation(Line(origin={212,87},
points={{15.3299,-23.9264},{13.303,-23.9264},{13.303,30.006},{-14.7503,30.006},{-14.7503,23.8752}},
color={0,232,232},
thickness=1));
  end MotorplsBattPlsHVAC;