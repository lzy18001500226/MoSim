model MotorplsBattPlsHVACparallel "热管理系统(电池主动制冷)"
  parameter Real BattPump_rpm = 1000 "电池水泵转速（转/分钟）";
  parameter Real MotorPump_rpm = 2000 "电机水泵转速（转/分钟）";
  parameter Real ComprSpd_rpm = 4000 "压缩机转速（转/分钟）";
  parameter Modelica.Units.SI.Temperature T_Amb = 313.15 "环境温度";
  parameter Modelica.Units.SI.Temperature T_out = 313.15 "外部温度";
  parameter Modelica.Units.SI.Temperature T_in = 313.15 "内部温度";
  parameter Real valve_pos1=1 "散热器侧比比例三通阀位置0~1之间";
  parameter Real valve_pos2=0.5 "前后电机侧比例三通阀位置0~1之间";
  annotation (Diagram(coordinateSystem(extent = {{-80, -170}, {870, 290}}, grid = {2, 2})), Icon(coordinateSystem(extent = {{-100.0, -100.0}, {100.0, 100.0}}, grid = {2.0, 2.0}),
  graphics = {Bitmap(origin = {0.0, 0.0}, extent = {{-100.0, -100.0}, {100.0, 100.0}}, fileName = "modelica://TAThermalSystem/Resource/Icons/Example.svg")}),
  Documentation(link="modelica://TAThermalSystem/Resource/Doc/MotorplsBattPlsHVACparallel.html"), experiment(Algorithm=Dassl,StartTime=0,StopTime=1000,Tolerance=0.0001,Interval=1,InlineIntegrator=false,InlineStepSize=false), Protection(access=Access.nonPackageDuplicate),__MWORKS(ResultViewerManager(resultViewers={
ResultViewer(name="1", executeTrigger=executeTrigger.SimulationStarted, commands={
CreatePlot(id=1, x_display_unit="s", legend_layout=7, left_title="[degC]", curve_vernier=True, fix_time_range_value=0, zoom_x=(0, 1000), zoom_y_l=(15, 45)),
Plot(y=["evaporatorR134a.hXSummary.Tair_in", "evaporatorR134a.hXSummary.Tair_out"], thicknesses=[2, 2], colors=["4278190335", "4294901760"]),
CreatePlot(id=-1, x_display_unit="s", legend_layout=7, left_title="[degC]", curve_vernier=True, fix_time_range_value=0, sub_plot=(1, 2), zoom_x=(0, 1000), zoom_y_l=(10, 45)),
Plot(y=["coolingPipe2.pipeSummary.T_in", "coolingPipe2.pipeSummary.T_out"], thicknesses=[2, 2], colors=["4278190335", "4294901760"])})
})) );
  TAThermalSystem.HeatExchangers.CoolingRadiatorNTU.Water_Air_HXNTU water_air_HXTU1(
    ConsiderMass = false, Across1(displayUnit = "cm2") = 0.002, Dhyd1(displayUnit = "mm") = 0.01, cearea1(displayUnit = "m2") = 6, ConsiderationFins_cd = false,
    etas2 = 0.8, ConsiderationFins_ab = true, fromDp = false,
    redeclare model Friction_ab = TYBase.Thermal.FluidHeatFlow.PressureLoss.HXPressureDrop.SingularPressureDrop,
    T1_a(start = T_Amb),
    T1_b(start = T_Amb),
    T2_in(start = T_Amb),
    T2_out(start = T_Amb),
    Twall(start = T_Amb),
    Across2 = 0.1, Dhyd2 = 0.005, cearea2(displayUnit = "m2") = 10,T0=T_Amb) 
    annotation (Placement(transformation(origin = {64.17086364916227, -24.91643297601535},
      extent = {{-10.0, 10.0}, {10.0, -10.0}},
      rotation = 90.0)));
  TAThermalSystem.Sources.Air.AirSource_mT airSource_mT2(m = 0.1, phi_source = 0.4,
    T = T_Amb,
    redeclare package Medium = TYBase.Media_Extend.Air.MoistAir) 
    annotation (Placement(transformation(origin = {28.170863649162236, 7.083567023984656},
      extent = {{-10.0, -9.999999999999996}, {10.0, 10.0}})));
  TAThermalSystem.Sources.Air.AirSink_pT airSink_pT2(T_sink = T_Amb, phi_sink = 0.4, redeclare package Medium = TYBase.Media_Extend.Air.MoistAir) 
    annotation (Placement(transformation(origin = {28.170863649162236, -37.27902669626182},
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  Modelica.Mechanics.Rotational.Sources.Speed speed1 
    annotation (Placement(transformation(origin = {167.9587261146496, -134.11770700636941},
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));



  Modelica.Blocks.Sources.RealExpression realExpression1(y = MotorPump_rpm * Modelica.Constants.pi / 30) 
    annotation (Placement(transformation(origin = {102.95872611464958, -134.0},
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TAThermalSystem.Reservoirs.ExpansionTank expansion_tank(tank1(pInitial = 1e5), T_Amb = T_Amb) 
    annotation (Placement(transformation(origin = {213.99999999999997, -102.03777403035414},
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TAThermalSystem.PumpAndFan.CentrifugalPump centrifugal_pump2(
    T_inlet(start



       = T_Amb),
    T_outlet(start



       = T_Amb),
    T_start = T_Amb,
    V(displayUnit = "l") = 0.0002,pout_start=3e5) 
    annotation (Placement(transformation(origin = {180.0, -102.00000000000001},
      extent = {{10.0, -10.0}, {-10.0, 10.0}})));
  TAThermalSystem.Valves.HydraulicValve.ValveFlowKvCooling zetaFlowCooling2(Kv_curve = {{0.0, 0}, {0.01, 0}, {0.1, 0.1}, {0.2, 0.3}, {0.4, 0.5}, {0.6, 0.6}, {0.8, 0.7}, {1.0, 20}, {1.1, 20}}, T0 = T_Amb) annotation (Placement(transformation(origin = {70.0, 78.83740024599936},
    extent = {{-10.0, -10.0}, {10.0, 10.0}},
    rotation = 90.0)));
  Modelica.Blocks.Sources.RealExpression realExpression6(y = valve_pos1) 
    annotation (Placement(transformation(origin = {28.170863649162243, 78.83740024599936},
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));



  TAThermalSystem.Valves.HydraulicValve.ValveFlowKvCooling zetaFlowCooling1(Kv_curve = {{0.0, 0.01}, {0.01, 0.01}, {0.1, 0.1}, {0.2, 0.3}, {0.4, 0.5}, {0.6, 0.6}, {0.8, 0.7}, {1.0, 20}, {1.1, 20}}, T0 = T_Amb) annotation (Placement(transformation(origin = {-14.91476, 78.83740024599936},
    extent = {{-10.0, -10.0}, {10.0, 10.0}},
    rotation = 90.0)));
  Modelica.Blocks.Sources.RealExpression realExpression5(y = 1-valve_pos1) 
    annotation (Placement(transformation(origin = {-55.31237305732479, 78.83740024599936},
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TAThermalSystem.Sources.HeatTransfer.BoundaryHeatFlow boundaryHeatFlow2(Q_flow = 500) 
    annotation (Placement(transformation(origin = {762.0799775677539, -21.892555049073017},
      extent = {{10.0, -10.0}, {-10.0, 10.0}})));
  TAThermalSystem.Sources.HeatTransfer.BoundaryHeatFlow boundaryHeatFlow3(Q_flow = 500) 
    annotation (Placement(transformation(origin = {821.9013074813198, -26.25514876931964},
      extent = {{10.0, -10.0}, {-10.0, 10.0}})));
  TAThermalSystem.Pipes.LiquidCoolingPipe.CoolingPipe coolingPipeDS1(
    Aheat = 0.18,
    L = 0.2,
    p0 = 1.3e5,
    T0 = T_Amb) 
    annotation (Placement(transformation(origin = {732.1685880607087, -21.939503363508493},
      extent = {{-10.0469483144355, -10.008632925201297}, {10.011048314435497, 10.010082025725545}},
      rotation = 270.0)));
  TAThermalSystem.Pipes.LiquidCoolingPipe.CoolingPipe coolingPipeDS2(
    Aheat = 0.18,
    L = 0.2,
    p0 = 1.3e5,
    T0 = T_Amb) 
    annotation (Placement(transformation(origin = {791.9899179742746, -26.056289169534665},
      extent = {{-10.0469483144355, -10.008632925201297}, {10.011048314435497, 10.010082025725545}},
      rotation = -90.0)));
  TAThermalSystem.Valves.HydraulicValve.ValveFlowKvCooling zetaFlowCooling7(Kv_curve = {{0.0, 0}, {0.01, 0}, {0.1, 0.1}, {0.2, 0.3}, {0.4, 0.5}, {0.6, 0.6}, {0.8, 0.7}, {1.0, 100}, {1.1, 100}}, T0 = T_Amb) annotation (Placement(transformation(origin = {510.8431417967836, 214.0},
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  Modelica.Blocks.Sources.RealExpression realExpression12(y = 1) 
    annotation (Placement(transformation(origin = {524.0, 234.0},
      extent = {{10.0, -10.0}, {-10.0, 10.0}})));
  Modelica.Blocks.Sources.RealExpression realExpression8(y = BattPump_rpm* Modelica.Constants.pi / 30) 
    annotation (Placement(transformation(origin = {504.54850647893045, 44.83740024599936},
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  Modelica.Mechanics.Rotational.Sources.Speed speed4 
    annotation (Placement(transformation(origin = {538.5485064789304, 44.83740024599936},
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TAThermalSystem.Pipes.LiquidCoolingPipe.CoolingPipe coolingPipeDS6(Aheat = 0.18, L = 0.2, p0 = 2e5, useHeatTransfer = false, T0 = T_Amb) 

    annotation (Placement(transformation(origin = {452.9889516855646, 74.01008202572554},
      extent = {{10.0469483144355, -10.008632925201297}, {-10.011048314435497, 10.010082025725545}},
      rotation = -180.0)));
  TAThermalSystem.Reservoirs.ExpansionTank expansion_tank1(tank1(pInitial = 1.5e5),
    T_Amb = T_Amb) annotation (Placement(transformation(origin = {510.8431417967836, 73.9622259696459},
      extent = {{10.0, -10.0}, {-10.0, 10.0}})));
  TAThermalSystem.PumpAndFan.CentrifugalPump centrifugal_pump3(
    T_inlet(start



       = T_Amb),
    T_outlet(start



       = T_Amb),
    T_start = T_Amb,
    V(displayUnit



       = "l") =
    0.0002) 
    annotation (Placement(transformation(origin = {558.0, 74.01871495092684},
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TAThermalSystem.Valves.HydraulicValve.ValveFlowKvCooling valveFlowKvCooling2(Kv_curve = {{0.0, 0}, {0.01, 0}, {0.1, 0.1}, {0.2, 0.3}, {0.4, 0.5}, {0.6, 0.6}, {0.8, 0.7}, {1.0, 20}, {1.1, 20}}, T0 = T_Amb) 
    annotation (Placement(transformation(origin = {435.00000000000017, 190.00000000000003},
      extent = {{10.0, -10.0}, {-10.0, 10.0}},
      rotation = 90.0)));
  Modelica.Blocks.Sources.RealExpression realExpression7(y = 0) 
    annotation (Placement(transformation(origin = {410.9999999999999, 190.00000000000003},
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TAThermalSystem.Valves.HydraulicValve.ValveFlowKvCooling valveFlowKvCooling3(Kv_curve = {{0.0, 0}, {0.01, 0}, {0.1, 0.1}, {0.2, 0.3}, {0.4, 0.5}, {0.6, 0.6}, {0.8, 0.7}, {1.0, 20}, {1.1, 20}}, T0 = T_Amb) 
    annotation (Placement(transformation(origin = {578.8445908973079, 190.00000000000003},
      extent = {{10.0, -10.0}, {-10.0, 10.0}},
      rotation = 270.0)));
  Modelica.Blocks.Sources.RealExpression realExpression9(y = 0) 
    annotation (Placement(transformation(origin = {618.0, 190.00000000000003},
      extent = {{10.0, -10.0}, {-10.0, 10.0}})));
  TYBase.Thermal.FluidHeatFlow.ControlVolumes.CVBasic.ThermalHydraulicCV.BranchPipeCoolingCV branchPipeCoolingCV(p0 = 2.45e5,
    T0 = T_Amb) 
    annotation (Placement(transformation(origin = {434.753141106054, 213.96222596964586},
      extent = {{-8.169727718157175, -8.435625744212741}, {8.663445506049522, 8.219384140303024}})));
  TYBase.Thermal.FluidHeatFlow.ControlVolumes.CVBasic.ThermalHydraulicCV.BranchPipeCoolingCV branchPipeCoolingCV1(p0 = 2e5,
    T0 = T_Amb) 
    annotation (Placement(transformation(origin = {435.0377740303543, 150.69962621564517},
      extent = {{-8.169727718157175, -8.435625744212741}, {8.663445506049522, 8.219384140303024}},
      rotation = 90.0)));
  TYBase.Thermal.FluidHeatFlow.ControlVolumes.CVBasic.ThermalHydraulicCV.BranchPipeCoolingCV branchPipeCoolingCV2(p0 = 2.3e5,
    T0 = T_Amb) 
    annotation (Placement(transformation(origin = {578.5977320033617, 213.96222596964586},
      extent = {{-8.169727718157175, -8.435625744212741}, {8.663445506049522, 8.219384140303024}})));
  TYBase.Thermal.FluidHeatFlow.ControlVolumes.CVBasic.ThermalHydraulicCV.BranchPipeCoolingCV branchPipeCoolingCV3(p0 = 2.3e5,
    T0 = T_Amb) 
    annotation (Placement(transformation(origin = {578.9527116992626, 150.9087110792372},
      extent = {{-8.169727718157175, -8.435625744212741}, {8.663445506049522, 8.219384140303024}},
      rotation = -90)));
  TYBase.Thermal.FluidHeatFlow.ControlVolumes.CVBasic.ThermalHydraulicCV.BranchPipeCoolingCV branchPipeCoolingCV4(p0 = 2.6e5,
    T0 = T_Amb) 
    annotation (Placement(transformation(origin = {69.75314110605383, 214.60610574421273},
      extent = {{-8.169727718157175, -8.435625744212741}, {8.663445506049522, 8.219384140303024}})));
  TYBase.Thermal.FluidHeatFlow.ControlVolumes.CVBasic.ThermalHydraulicCV.BranchPipeCoolingCV branchPipeCoolingCV5(p0 = 2.7e5,
    T0 = T_Amb) 
    annotation (Placement(transformation(origin = {70.17264553337003, -101.61013585969698},
      extent = {{-8.169727718157175, 8.435625744212741}, {8.663445506049522, -8.219384140303024}})));
  TAThermalSystem.Pipes.LiquidCoolingPipe.CoolingPipeR coolingPipeR(p0 = 2.55e5,
    T0 = T_Amb) 
    annotation (Placement(transformation(origin = {252.51795000000016, 214.64387977456687},
      extent = {{-10.0997, -8.821720000000001}, {10.0638, 9.007800000000001}})));
  Modelica.Blocks.Sources.RealExpression realExpression10(y = ComprSpd_rpm) 
    annotation (Placement(transformation(origin = {211.00000000000003, 120.83740024599936},
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TAThermalSystem.HeatExchangers.Condenser condenser(


                                                      n_segRef = 2, n_segMtl = 2, HX_Init(T0 = T_Amb, T_air0 = T_Amb),n_segAir=2,redeclare record HXGeo = TYBase.Thermal.FluidHeatFlow.Components.BasicComponents.Records.HXRecords.HXGeoHorizontal,CF_AirSideHeatTransfer=10,RefrigerantTemperature=40,RefrigerantMass=0.15246,CF_RefrigerantSideHeatTransfer=10,redeclare package Medium = TYMedia.Helmholtz.R134a
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   ) 

    annotation (Placement(transformation(origin = {201.0000000000001, 62.83740024599935},
      extent = {{10.0, 10.0}, {-10.0, -10.0}},
      rotation = 90.0)));
  TAThermalSystem.Sources.Air.AirSink_pT airSink1(


                                                  T_sink = 293.15,
    phi_sink = 0.4
                  ) annotation (Placement(transformation(origin = {227.0000000000001, 90.75919687487031},
      extent = {{10.0, -10.0}, {-10.0, 10.0}})));
  TAThermalSystem.Sources.Air.AirSource_mT airSource1(


                                                      m = 0.5, T = T_out,
    phi_source = 0.4
                    ) annotation (Placement(transformation(origin = {229.00000000000017, 40.06114332332085},
      extent = {{10.0, -10.0}, {-10.0, 10.0}})));
  TAThermalSystem.Compressor.Compressor compressorR134a(


                                                        p0_in = 6e5, p0_out = 9.999999999999999e5, MaximumDisplacement = 5.5e-5,redeclare package Medium = TYMedia.Helmholtz.R134a
                                                                                                                               ) 
    annotation (Placement(transformation(origin = {265.2302508245758, 150.83740024599933},
      extent = {{10.0, -10.0}, {-10.0, 10.0}})));
  TAThermalSystem.Reservoirs.Reservoir_fillinglevel reservoir(






    FromDp = false, zeta = 1000,RefrigerantTemperature=40,RefrigerantMass=0.1012,RefrigerantMassDistribution=1,FillingLevel0=0.2,redeclare package Medium = TYMedia.Helmholtz.R134a
                                                                                                                                ) 
    annotation (Placement(transformation(origin = {306.6151254122879, 150.83740024599933},
      extent = {{10.0, -10.0}, {-10.0, 10.0}})));
  TAThermalSystem.HeatExchangers.CoolingRadiatorNTU.ChillerPlateCooling chillerPlate(





                                                                                     redeclare model Friction = TYBase.Thermal.FluidHeatFlow.PressureLoss.LiquidPressureDrop.SingularPressureDrop, water(redeclare model Friction = TYBase.Thermal.FluidHeatFlow.PressureLoss.LiquidPressureDrop.SingularPressureDrop), CF_RefrigerantSideHeatTransfer = 100, CF_WaterSideHeatTransfer = 100, T0 = T_Amb, RefInit(T0 = T_Amb, T_air0 = T_Amb),simplePipe(RefrigerantMassDistribution=2,RefrigerantTemperature=40,RefrigerantMass=0.351053),redeclare package RefMedium = TYMedia.Helmholtz.R134a
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      ) 
    annotation (Placement(transformation(origin = {429.0377740303542, 98.83740024599936},
      extent = {{10.0, -10.0}, {-10.0, 10.0}},
      rotation = -90.0)));
  TAThermalSystem.Valves.RefrigerantValve.ZetaFlow zetaFlow1(





                                                              Tin(start = T_Amb), Tout(start = T_Amb), Dhyd(displayUnit = "mm") = 0.004, zeta = 5000,redeclare package Medium = TYMedia.Helmholtz.R134a
                                                                                                                                                    ) annotation (Placement(transformation(origin = {423.0377740303542, 44.83740024599936},
    extent = {{10.0, -10.0}, {-10.0, 10.0}},
    rotation = 270.0)));
  TAThermalSystem.Sensors.Refrigerant.SuperHeatingSensor superHeatingSensor(





                                                                            h0_in = 3e5, h0_out = 3e5,redeclare package Medium = TYMedia.Helmholtz.R134a
                                                                                                     ) annotation (Placement(transformation(origin = {348.0, 150.73740024599934},
    extent = {{10.0, -10.0}, {-10.0, 10.0}})));
  TAThermalSystem.Sensors.Refrigerant.SuperCoolingSensor superCoolingSensor(redeclare package Medium = TYMedia.Helmholtz.R134a) 
    annotation (Placement(transformation(origin = {292.0, 18.0},
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TAThermalSystem.Sources.Air.AirSource_mT airSource(






    m = 0.2, T = T_in,
    phi_source = 0.4
                    ) annotation (Placement(transformation(origin = {333.00000000000006, 118.83740024599935},
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TAThermalSystem.Sources.Air.AirSink_pT airSink(





                                                 redeclare package Medium = TYBase.Media_Extend.Air.MoistAir, T_sink = 293.15,
    phi_sink = 0.2
                  ) annotation (Placement(transformation(origin = {333.00000000000006, 78.83740024599936},
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TAThermalSystem.HeatExchangers.Evaporator evaporatorR134a(





                                                            HX_Init(T0 = T_Amb, T_air0 = T_Amb),CF_AirSideHeatTransfer=10,RefrigerantTemperature=40,RefrigerantMass=0.0952875,CF_RefrigerantSideHeatTransfer=10,redeclare package Medium = TYMedia.Helmholtz.R134a
                                                                                                                                                                                                                                                                                                                                                 ) annotation (Placement(transformation(origin = {363.0000000000001, 98.83740024599936},
    extent = {{-10.0, -10.0}, {10.0, 10.0}},
    rotation = 90.0)));
  TAThermalSystem.Valves.RefrigerantValve.ZetaFlow zetaFlow(





                                                             Tin(start = T_Amb), Tout(start = T_Amb), Dhyd(displayUnit = "mm") = 0.005, zeta = 1000,redeclare package Medium = TYMedia.Helmholtz.R134a
                                                                                                                                                   ) annotation (Placement(transformation(origin = {369.00000000000006, 44.83740024599936},
    extent = {{10.0, -10.0}, {-10.0, 10.0}},
    rotation = -90.0)));
  TYBase.Battery.Model.BatteryQIn batteryQIn(





                                             N_cells = 3, chargeResTable = {{10, 0.2}, {20, 0.2}, {30, 0.2}, {40, 0.2}, {50, 0.2}, {60, 0.2}, {70, 0.2}, {80, 0.2}, {90, 0.2}}, dischargeResTable = {{10, 0.2}, {20, 0.2}, {30, 0.2}, {40, 0.2}, {50, 0.2}, {60, 0.2}, {70, 0.2}, {80, 0.2}, {90, 0.2}}, Ns = 96, Np = 2, QCellNominal = 33, C = 2000
                                                                                                                                                                                                                                                                                                                                                     ) 
    annotation (Placement(transformation(origin = {630.0, 95.29131354179582},
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYBase.Battery.Component.Ground ground annotation (HideResult = true, Placement(transformation(origin = {653.0592389275065, 34.96140596692946},
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  Modelica.Electrical.Analog.Sources.ConstantCurrent constantCurrent(





                                                                     I = 66 * 2
                                                                               ) 
    annotation (Placement(transformation(origin = {630.0, 59.68250519645417},
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TAThermalSystem.Pipes.LiquidCoolingPipe.CoolingPipeDS coolingPipe2(





                                                     T0 = T_Amb, p0 = 2.5e5, n = 3
                                                                                  ) annotation (Placement(transformation(origin={579.011,114.578},
extent={{10.0997,-8.82172},{-10.0638,9.0078}},
rotation=-90)));

  TAThermalSystem.Valves.HydraulicValve.ValveFlowKvCooling valveFlowKvCooling4(





                                                               Kv_curve = {{0.0, 0}, {0.01, 0}, {0.1, 0.1}, {0.2, 0.3}, {0.4, 0.5}, {0.6, 0.6}, {0.8, 0.7}, {1.0, 20}, {1.1, 20}}, T0 = T_Amb
                                                                                                                                                                                             ) 
    annotation (Placement(transformation(origin = {731.2391270442824, 69.47167519860679},
      extent = {{10.0, 10.0}, {-10.0, -10.0}},
      rotation = -270.0)));
  TAThermalSystem.Valves.HydraulicValve.ValveFlowKvCooling valveFlowKvCooling5(





                                                               Kv_curve = {{0.0, 0}, {0.01, 0}, {0.1, 0.1}, {0.2, 0.3}, {0.4, 0.5}, {0.6, 0.6}, {0.8, 0.7}, {1.0, 20}, {1.1, 20}}, T0 = T_Amb
                                                                                                                                                                                             ) 
    annotation (Placement(transformation(origin = {792.6593762084676, 68.7920849875837},
      extent = {{10.0, 10.0}, {-10.0, -10.0}},
      rotation = -270.0)));
  Modelica.Blocks.Sources.RealExpression realExpression11(





                                                          y = valve_pos2
                                                               ) 
    annotation (Placement(transformation(origin = {764.85697085237, 69.86721557679284},
      extent = {{10.0, -10.0}, {-10.0, 10.0}})));
  Modelica.Blocks.Sources.RealExpression realExpression13(





                                                          y = 1-valve_pos2
                                                               ) 
    annotation (Placement(transformation(origin = {834.1880275802761, 69.5831657439558},
      extent = {{10.0, -10.0}, {-10.0, 10.0}})));
  TAThermalSystem.Valves.HydraulicValve.ValveFlowKvCooling zetaFlowCooling8(





                                                            Kv_curve = {{0.0, 0}, {0.01, 0}, {0.1, 0.1}, {0.2, 0.3}, {0.4, 0.5}, {0.6, 0.6}, {0.8, 0.7}, {1.0, 100}, {1.1, 100}}, T0 = T_Amb
                                                                                                                                                                                            ) annotation (Placement(transformation(origin = {510.8431417967836, 150.94648510959135},
    extent = {{10, -10}, {-10, 10}})));
  Modelica.Blocks.Sources.RealExpression realExpression14(





                                                          y = 1
                                                               ) 
    annotation (Placement(transformation(origin = {524.0, 170.73740024599937},
      extent = {{10.0, -10.0}, {-10.0, 10.0}})));
  TAThermalSystem.Pipes.LiquidCoolingPipe.CoolingPipeC coolingPipe1(





/* 
initial equation
  condenser.refrigerant.p[1] = condenser.refrigerant.p0[1];
  evaporatorR134a.refrigerant.p[1] = evaporatorR134a.refrigerant.p0[1];
  condenser.refrigerant.h[3] = condenser.refrigerant.h0[3];
  chillerPlate.wall.T_in = T_Amb;
  chillerPlate.wall.T_out = T_Amb;
 
batteryQIn.heatCapacitor1[1].T= batteryQIn.T0;
batteryQIn.heatCapacitor1[2].T= batteryQIn.T0;
batteryQIn.heatCapacitor1[3].T= batteryQIn.T0;
batteryQIn.heatCapacitor2[1].T= batteryQIn.T0;
batteryQIn.heatCapacitor2[2].T= batteryQIn.T0;
batteryQIn.heatCapacitor2[3].T= batteryQIn.T0;
batteryQIn.heatCapacitor[1].T = batteryQIn.T0;
batteryQIn.heatCapacitor[2].T = batteryQIn.T0;
batteryQIn.heatCapacitor[3].T= batteryQIn.T0;
branchPipeCoolingCV.T= branchPipeCoolingCV.T0;
branchPipeCoolingCV.p= branchPipeCoolingCV.p0;
branchPipeCoolingCV1.T= branchPipeCoolingCV1.T0;
branchPipeCoolingCV1.p= branchPipeCoolingCV1.p0;
branchPipeCoolingCV2.T= branchPipeCoolingCV2.T0;
branchPipeCoolingCV2.p= branchPipeCoolingCV2.p0;
branchPipeCoolingCV3.T= branchPipeCoolingCV3.T0;
branchPipeCoolingCV4.T= branchPipeCoolingCV4.T0;
branchPipeCoolingCV4.p= branchPipeCoolingCV4.p0;
branchPipeCoolingCV5.T= branchPipeCoolingCV5.T0;
chillerPlate.simplePipe.h[1]= chillerPlate.simplePipe.h0[1];
chillerPlate.simplePipe.h[2]= chillerPlate.simplePipe.h0[2];
chillerPlate.simplePipe.p[1]= chillerPlate.simplePipe.p0[1];
chillerPlate.simplePipe.p[2]= chillerPlate.simplePipe.p0[2];
chillerPlate.wall.T_in= 288.15;
chillerPlate.wall.T_out= 288.15;
chillerPlate.water.pipe[1].CV.p= chillerPlate.water.pipe[1].CV.p0;
chillerPlate.water.pipe[2].CV.p= chillerPlate.water.pipe[2].CV.p0;
condenser.refrigerant.h[1]= condenser.refrigerant.h0[1];
condenser.refrigerant.h[2]= condenser.refrigerant.h0[2];
condenser.refrigerant.h[3]= condenser.refrigerant.h0[3];
condenser.refrigerant.p[1]= condenser.refrigerant.p0[1];
condenser.refrigerant.p[2]= condenser.refrigerant.p0[2];
condenser.refrigerant.p[3]= condenser.refrigerant.p0[3];
coolingPipe2.pipe[1].CV.p= coolingPipe2.pipe[1].CV.p0;
coolingPipe2.pipe[2].CV.p= coolingPipe2.pipe[2].CV.p0;
coolingPipe2.pipe[3].CV.p= coolingPipe2.pipe[3].CV.p0;
coolingPipeBaseCR3.CV.p= coolingPipeBaseCR3.CV.p0;
coolingPipeBaseCR4.CV.p= coolingPipeBaseCR4.CV.p0;
coolingPipeCR.CV.p= coolingPipeCR.CV.p0;
coolingPipeDS2.CV.p= coolingPipeDS2.CV.p0;
coolingPipeDS6.CV.p= coolingPipeDS6.CV.p0;
evaporatorR134a.refrigerant.h[1]= evaporatorR134a.refrigerant.h0[1];
evaporatorR134a.refrigerant.h[2] = evaporatorR134a.refrigerant.h0[2];
evaporatorR134a.refrigerant.h[3]= evaporatorR134a.refrigerant.h0[3];
evaporatorR134a.refrigerant.h[4]= evaporatorR134a.refrigerant.h0[4];
evaporatorR134a.refrigerant.h[5]= evaporatorR134a.refrigerant.h0[5];
evaporatorR134a.refrigerant.h[6]= evaporatorR134a.refrigerant.h0[6];
evaporatorR134a.refrigerant.p[1] = evaporatorR134a.refrigerant.p0[1];
evaporatorR134a.refrigerant.p[2]= evaporatorR134a.refrigerant.p0[2];
evaporatorR134a.refrigerant.p[3]= evaporatorR134a.refrigerant.p0[3];
evaporatorR134a.refrigerant.p[4]= evaporatorR134a.refrigerant.p0[4];
evaporatorR134a.refrigerant.p[5]= evaporatorR134a.refrigerant.p0[5];
evaporatorR134a.refrigerant.p[6]= evaporatorR134a.refrigerant.p0[6];
water_air_HXTU1.c.p= 1.0e5;
*/                                                  p0
                                                       = 2.649999999999999e5, T0 = T_Amb, TA(start = T_Amb), TB(start = T_Amb)
                                                                                                                              ) annotation (Placement(transformation(origin = {69.96844388744302, 26.32084557503106},
    extent = {{-10.0997, -8.821720000000001}, {10.0638, 9.007800000000001}},
    rotation = 90.0)));
  TAThermalSystem.Sources.Mechanics.RotationalInputSource rotationalInputSource 
    annotation (Placement(transformation(origin={240,120.83740024599936},
extent={{-8,-6},{10,6}})));
  equation
  connect(airSink_pT2.port_a, water_air_HXTU1.d) 
    annotation (Line(origin = {68.17086364916224, -39.91643297601535},
      points = {{-30.0, 3.0}, {-10.0, 3.0}, {-10.0, 5.0}},
      color = {0, 232, 232},
      thickness = 1.0));
  connect(water_air_HXTU1.c, airSource_mT2.port_b) 
    annotation (Line(origin = {105.17086364916224, -38.91643297601535},
      points = {{-47.0, 24.0}, {-47.0, 47.0}, {-67.0, 47.0}, {-67.0, 46.0}},
      color = {0, 232, 232},
      thickness = 1.0));
  connect(expansion_tank.b, centrifugal_pump2.a) 
    annotation (Line(origin = {169.7952261146496, 16.170479999999998},
      points = {{34.0, -118.0}, {20.0, -118.0}},
      color = {0, 170, 255},
      thickness = 1.0));
  connect(speed1.flange, centrifugal_pump2.flange) 
    annotation (Line(origin = {181.9587261146496, -123.07993297601536},
      points = {{-4.0, -11.0}, {-4.0, 11.0}, {-2.0, 11.0}},
      color = {0, 0, 0}));
  connect(realExpression6.y, zetaFlowCooling2.u) 
    annotation (Line(origin = {275.82952, 31.163500000000077},
      points = {{-237.0, 48.0}, {-216.0, 48.0}},
      color = {0, 0, 127}));


  connect(zetaFlowCooling1.u, realExpression5.y) 
    annotation (Line(origin = {-36.31237305732482, 78.58698726998396},
      points = {{11.0, 0.0}, {-8.0, 0.0}},
      color = {0, 0, 127}));
  connect(boundaryHeatFlow2.port[1], coolingPipeDS1.qa) 
    annotation (Line(origin = {748.0930400000003, -22.009340855099254},
      points = {{4.0, 0.0}, {-5.0, 0.0}},
      color = {191, 0, 0},
      thickness = 1.0));
  connect(coolingPipeDS2.qa, boundaryHeatFlow3.port[1]) 
    annotation (Line(origin = {807.0930400000003, -26.009340855099254},
      points = {{-4.0, 0.0}, {5.0, 0.0}},
      color = {191, 0, 0},
      thickness = 1.0));
  connect(zetaFlowCooling1.a, branchPipeCoolingCV5.a) 
    annotation (Line(origin = {27.0, -17.0},
      points = {{-42.0, 86.0}, {-42.0, -85.0}, {33.0, -85.0}},
      color = {0, 170, 255},
      thickness = 1.0));
  connect(speed1.w_ref, realExpression1.y) 
    annotation (Line(origin = {135.0, -134.0},
      points = {{21.0, 0.0}, {-21.0, 0.0}},
      color = {0, 0, 127}));
  connect(zetaFlowCooling7.u, realExpression12.y) 
    annotation (Line(origin = {516.932134418143, 237.73291853853922},
      points = {{-6.0, -14.0}, {-6.0, -4.0}, {-4.0, -4.0}},
      color = {0, 0, 127}));
  connect(zetaFlowCooling1.b, branchPipeCoolingCV4.a) 
    annotation (Line(origin = {89.0, 152.0},
      points = {{-104.0, -63.0}, {-104.0, 63.0}, {-29.0, 63.0}},
      color = {0, 170, 255},
      thickness = 1.0));
  connect(zetaFlowCooling2.b, branchPipeCoolingCV4.b) 
    annotation (Line(origin = {131.0, 152.0},
      points = {{-61.0, -63.0}, {-61.0, 53.0}},
      color = {0, 170, 255},
      thickness = 1.0));
  connect(realExpression8.y, speed4.w_ref) 
    annotation (Line(origin = {518.5485064789304, 44.83740024599936},
      points = {{-3.0, 0.0}, {8.0, 0.0}},
      color = {0, 0, 127}));


  connect(coolingPipeDS6.b, expansion_tank1.a) 
    annotation (Line(origin = {482.0, 74.0},
      points = {{-19.0, 0.0}, {19.0, 0.0}},
      color = {0, 170, 255},
      thickness = 1.0));


  connect(speed4.flange, centrifugal_pump3.flange) 
    annotation (Line(origin = {554.0, 55.0},
      points = {{-5.0, -10.0}, {4.0, -10.0}, {4.0, 9.0}},
      color = {0, 0, 0}));
  connect(realExpression7.y, valveFlowKvCooling2.u) 
    annotation (Line(origin = {262.0448398154198, 140.41870012299967},
      points = {{160.0, 50.0}, {163.0, 50.0}},
      color = {0, 0, 127}));
  connect(realExpression9.y, valveFlowKvCooling3.u) 
    annotation (Line(origin = {400.8038006262938, 220.4187001229997},
      points = {{206.0, -30.0}, {188.0, -30.0}},
      color = {0, 0, 127}));
  connect(zetaFlowCooling7.a, branchPipeCoolingCV.c) 
    annotation (Line(origin = {468, 207},
      points = {{32.83302375293874, 6.962225969645857}, {-23.246858893946012, 6.962225969645857}},
      color = {0, 170, 255},
      thickness = 1));
  connect(zetaFlowCooling7.b, branchPipeCoolingCV2.a) 
    annotation (Line(origin = {550, 203},
      points = {{-29.033418068309174, 10.962225969645857}, {18.59773200336167, 10.962225969645857}},
      color = {0, 170, 255},
      thickness = 1));
  connect(valveFlowKvCooling3.a, branchPipeCoolingCV3.a) 
    annotation (Line(origin = {579, 162},
      points = {{-0.1931831330463183, 17.98988195615516}, {-0.1931831330463183, -1.0912889207627927}, {-0.0472883007373639, -1.0912889207627927}},
      color = {0, 170, 255},
      thickness = 1));
  connect(branchPipeCoolingCV.b, valveFlowKvCooling2.a) 
    annotation (Line(origin = {435, 211},
      points = {{-0.2468588939460119, -7.037774030354143}, {-0.2468588939460119, -10.989881956155102}, {0.03777403035428506, -10.989881956155102}},
      color = {0, 170, 255},
      thickness = 1));
  connect(branchPipeCoolingCV1.c, valveFlowKvCooling2.b) 
    annotation (Line(origin = {435.0, 170.0},
      points = {{0.0, -9.0}, {0.0, 10.0}},
      color = {0, 170, 255},
      thickness = 1.0));
  connect(branchPipeCoolingCV2.b, valveFlowKvCooling3.b) 
    annotation (Line(origin = {579, 211},
      points = {{-0.40226799663832935, -7.037774030354143}, {-0.40226799663832935, -10.87655986509273}, {-0.1931831330463183, -10.87655986509273}},
      color = {0, 170, 255},
      thickness = 1));
  connect(branchPipeCoolingCV4.c, coolingPipeR.a) 
    annotation (Line(origin = {161.0, 215.0},
      points = {{-81.0, 0.0}, {82.0, 0.0}},
      color = {0, 170, 255},
      thickness = 1.0));
  connect(coolingPipeR.b, branchPipeCoolingCV.a) 
    annotation (Line(origin = {344, 216},
      points = {{-81.3586098650926, -1.3938942557872736}, {80.75314110605399, -1.3938942557872736}, {80.75314110605399, -2.037774030354143}},
      color = {0, 170, 255},
      thickness = 1));
  connect(airSource1.port_b, condenser.air_in) 
    annotation (Line(origin = {211.0, 30.83740024599939},
      points = {{8.0, 9.0}, {2.0, 9.0}, {2.0, 22.0}, {-4.0, 22.0}},
      color = {0, 232, 232},
      thickness = 1.0));
  connect(airSink1.port_a, condenser.air_out) 
    annotation (Line(origin = {211.0, 66.83740024599938},
      points = {{6.0, 24.0}, {6.0, 6.0}, {-4.0, 6.0}},
      color = {0, 232, 232},
      thickness = 1.0));
  connect(reservoir.b, compressorR134a.a) 
    annotation (Line(origin = {288.0, 151.19740024599938},
      points = {{9.0, 0.0}, {-13.0, 0.0}},
      color = {0, 128, 0},
      thickness = 1.0));
  connect(compressorR134a.b, condenser.a1) 
    annotation (Line(origin = {146.00000000000006, 95.19740024599938},
      points = {{109.0, 56.0}, {50.0, 56.0}, {50.0, -22.0}, {49.0, -22.0}},
      color = {0, 128, 0},
      thickness = 1.0));
  connect(chillerPlate.a, zetaFlow1.b) 
    annotation (Line(origin = {382.00000000000006, 67.83740024599938},
      points = {{41.0, 21.0}, {41.0, -13.0}},
      color = {0, 128, 0},
      thickness = 1.0));
  connect(reservoir.port_a, superHeatingSensor.b) 
    annotation (Line(origin = {334.0, 151.0},
      points = {{-17.0, 0.0}, {4.0, 0.0}},
      color = {0, 128, 0},
      thickness = 1.0));
  connect(chillerPlate.b, superHeatingSensor.a) 
    annotation (Line(origin = {391.0, 130.0},
      points = {{32.0, -21.0}, {32.0, 21.0}, {-33.0, 21.0}},
      color = {0, 128, 0},
      thickness = 1.0));
  connect(condenser.b1, superCoolingSensor.a) 
    annotation (Line(origin = {238.0, 35.0},
      points = {{-43.0, 18.0}, {-43.0, -17.0}, {44.0, -17.0}},
      color = {0, 128, 0},
      thickness = 1.0));
  connect(superCoolingSensor.b, zetaFlow1.a) 
    annotation (Line(origin = {363.0, 27.0},
      points = {{-61.0, -9.0}, {60.0, -9.0}, {60.0, 8.0}},
      color = {0, 128, 0},
      thickness = 1.0));
  connect(airSource.port_b, evaporatorR134a.air_in) 
    annotation (Line(origin = {350.00000000000006, 113.83740024599936},
      points = {{-7.0, 5.0}, {-7.0, -5.0}, {7.0, -5.0}},
      color = {0, 232, 232},
      thickness = 1.0));
  connect(evaporatorR134a.air_out, airSink.port_a) 
    annotation (Line(origin = {350.00000000000006, 83.83740024599938},
      points = {{7.0, 5.0}, {-7.0, 5.0}, {-7.0, -5.0}},
      color = {0, 232, 232},
      thickness = 1.0));
  connect(zetaFlow.b, evaporatorR134a.a1) 
    annotation (Line(origin = {377.00000000000006, 36.83740024599939},
      points = {{-8.0, 18.0}, {-8.0, 52.0}},
      color = {0, 128, 0},
      thickness = 1.0));
  connect(superHeatingSensor.a, evaporatorR134a.b1) 
    annotation (Line(origin = {364.0, 130.0},
      points = {{-6.0, 21.0}, {4.0, 21.0}, {4.0, -20.0}, {5.0, -20.0}, {5.0, -21.0}},
      color = {0, 128, 0},
      thickness = 1.0));
  connect(zetaFlow.a, superCoolingSensor.b) 
    annotation (Line(origin = {336.0, 27.0},
      points = {{33.0, 8.0}, {32.0, 8.0}, {32.0, -9.0}, {-34.0, -9.0}},
      color = {0, 128, 0},
      thickness = 1.0));
  connect(branchPipeCoolingCV1.a, chillerPlate.c) 
    annotation (Line(origin = {435.0, 125.0},
      points = {{0.0, 16.0}, {0.0, -16.0}},
      color = {0, 170, 255},
      thickness = 1.0));
  connect(chillerPlate.d, coolingPipeDS6.a) 
    annotation (Line(origin = {439.0, 82.0},
      points = {{-4.0, 7.0}, {-4.0, -8.0}, {4.0, -8.0}},
      color = {0, 170, 255},
      thickness = 1.0));
  connect(batteryQIn.pin_p, constantCurrent.p) 
    annotation (Line(origin = {619.0, 77.13897934980798},
      points = {{1.0, 18.0}, {-4.0, 18.0}, {-4.0, -17.0}, {1.0, -17.0}},
      color = {0, 0, 255}));
  connect(batteryQIn.pin_n, constantCurrent.n) 
    annotation (Line(origin = {640.0, 80.13897934980798},
      points = {{0.0, 15.0}, {0.0, -20.0}},
      color = {0, 0, 255}));
  connect(ground.p, batteryQIn.pin_n) 
    annotation (Line(origin = {647.0, 72.13897934980797},
      points = {{6.0, -27.0}, {6.0, 23.0}, {-7.0, 23.0}},
      color = {0, 0, 255}));
  connect(water_air_HXTU1.a, branchPipeCoolingCV5.b) 
    annotation (Line(origin = {70.0, -63.0},
      points = {{0.0, 28.0}, {0.0, -29.0}},
      color = {0, 170, 255},
      thickness = 1.0));
  connect(expansion_tank1.b, centrifugal_pump3.a) 
    annotation (Line(origin = {535.0, 74.0},
      points = {{-14.0, 0.0}, {13.0, 0.0}},
      color = {0, 170, 255},
      thickness = 1.0));
  connect(centrifugal_pump3.b, coolingPipe2.a) 
    annotation (Line(origin={577,88},
points={{-8.87656,-14.0191},{2.07021,-14.0191},{2.07021,16.5152}},
color={0,170,255},
thickness=1));
  connect(coolingPipe2.b, branchPipeCoolingCV3.c) 
    annotation (Line(origin={582,132},
points={{-2.92979,-7.24539},{-2.92979,8.90871},{-3.04729,8.90871}},
color={0,170,255},
thickness=1));
  connect(valveFlowKvCooling4.b, coolingPipeDS1.a) 
    annotation (Line(origin = {732.0, 24.0},
      points = {{-1.0, 35.0}, {-1.0, -36.0}, {0.0, -36.0}},
      color = {0, 170, 255},
      thickness = 1.0));
  connect(valveFlowKvCooling5.b, coolingPipeDS2.a) 
    annotation (Line(origin = {793.0, 21.0},
      points = {{0.0, 38.0}, {0.0, -37.0}, {-1.0, -37.0}},
      color = {0, 170, 255},
      thickness = 1.0));
  connect(realExpression11.y, valveFlowKvCooling4.u) 
    annotation (Line(origin = {748.0, 73.0},
      points = {{6.0, -3.0}, {-7.0, -3.0}, {-7.0, -4.0}},
      color = {0, 0, 127}));
  connect(realExpression13.y, valveFlowKvCooling5.u) 
    annotation (Line(origin = {813.0, 70.0},
      points = {{10.0, 0.0}, {-10.0, 0.0}, {-10.0, -1.0}},
      color = {0, 0, 127}));
  connect(coolingPipe2.qa, batteryQIn.Batt_top) 
    annotation (Line(origin={603,105},
points={{-14.9897,9.57792},{40,9.57792},{40,-0.858686},{37,-0.858686}},
color={191,0,0},
thickness=1));
  connect(zetaFlowCooling8.u, realExpression14.y) 
    annotation (Line(origin = {516.932134418143, 174.47031878453856},
      points = {{-6.088992621359466, -13.523833674947213}, {-6.088992621359466, -3.732918538539195}, {-3.9321344181430504, -3.732918538539195}},
      color = {0, 0, 127}));
  connect(branchPipeCoolingCV3.b, zetaFlowCooling8.a) 
    annotation (Line(origin = {545, 152},
      points = {{23.952711699262636, -1.0912889207627927}, {-24.146740159371575, -1.0912889207627927}},
      color = {0, 170, 255},
      thickness = 1));
  connect(zetaFlowCooling8.b, branchPipeCoolingCV1.b) 
    annotation (Line(origin = {473, 152},
      points = {{27.719701661876343, -1.0912889207627927}, {-27.962225969645715, -1.0912889207627927}, {-27.962225969645715, -1.3003737843548322}},
      color = {0, 170, 255},
      thickness = 1));
  connect(coolingPipe1.a, water_air_HXTU1.b) 
    annotation (Line(origin = {69.0, 1.0},
      points = {{1.0, 15.0}, {1.0, -16.0}},
      color = {0, 170, 255},
      thickness = 1.0));
  connect(coolingPipe1.b, zetaFlowCooling2.a) 
    annotation (Line(origin = {69.0, 53.0},
      points = {{1.0, -17.0}, {1.0, 16.0}},
      color = {0, 170, 255},
      thickness = 1.0));
  connect(realExpression10.y, rotationalInputSource.u) 
  annotation(Line(origin={228,121},
  points={{-5.999999999999972,-0.16259975400063809},{5,-0.16259975400063809}},
  color={0,0,127}));
  connect(rotationalInputSource.flange, compressorR134a.flange) 
  annotation(Line(origin={258,131},
  points={{-8,-10.162599754000638},{7.230250824575819,-10.162599754000638},{7.230250824575819,9.837400245999333}},
  color={0,0,0}));
  connect(coolingPipeDS1.b, expansion_tank.a) 
  annotation(Line(origin={478,-67},
  points={{254.022,34.9901},{254.022,-35.0378},{-254,-35.0378}},
  color={0,170,255},
  thickness=1));
  connect(coolingPipeDS2.b, expansion_tank.a) 
  annotation(Line(origin={508,-69},
  points={{283.844,32.8733},{283.844,-33.0378},{-284,-33.0378}},
  color={0,170,255},
  thickness=1));
  connect(branchPipeCoolingCV2.c, valveFlowKvCooling4.a) 
  annotation(Line(origin={660,147},
  points={{-71.4023,66.9622},{71.2014,66.9622},{71.2014,-67.5182}},
  color={0,170,255},
  thickness=1));
  connect(valveFlowKvCooling5.a, branchPipeCoolingCV2.c) 
  annotation(Line(origin={691,146},
  points={{101.622,-67.1978},{101.622,67.9622},{-102.402,67.9622}},
  color={0,170,255},
  thickness=1));
  connect(centrifugal_pump2.b, branchPipeCoolingCV5.c) 
  annotation(Line(origin={125,-102},
  points={{44.8766,-0.037774},{-44.8274,-0.037774},{-44.8274,0.389864}},
  color={0,170,255},
  thickness=1));
  end MotorplsBattPlsHVACparallel;