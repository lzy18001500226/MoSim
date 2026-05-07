model MotorCool "热管理系统(电机散热)"
  parameter Real PumpSpd_rpm= 2000 "水泵转速（转/分钟）";
  parameter Modelica.SIunits.Temperature T_Amb = 303.15 "环境温度";
  parameter Modelica.SIunits.Power Q_flowF = 500 "前电机支路总热流量";
  parameter Modelica.SIunits.Power Q_flowR = 500 "后电机支路总热流量";
  parameter Modelica.SIunits.Power Q_flowP = 100 "管路热流量";
  parameter Real valve_pos1=1 "散热器侧比例三通阀位置0~1之间";
  parameter Real valve_pos2=0.5 "前后电机侧比例三通阀位置0~1之间";
  annotation (Diagram(coordinateSystem(extent={{-80,-170},{870,290}},
grid={2,2})), Icon(coordinateSystem(extent = {{-100.0, -100.0}, {100.0, 100.0}}, grid = {2.0, 2.0}), graphics = {Bitmap(origin = {0.0, 0.0}, extent = {{-100.0, -100.0}, {100.0, 100.0}}, fileName = "modelica://TAThermalSystem/Resource/Icons/Example.svg")}), Documentation(link="modelica://TAThermalSystem/Resource/Doc/MotorCool.html"), experiment(Algorithm = Dassl, StartTime = 0, StopTime = 1000, Tolerance = 0.0001, Interval = 1), Protection(access=Access.nonPackageDuplicate), __MWORKS(ContinueSimConfig(SaveContinueFile = "false", SaveBeforeStop = "false", NumberBeforeStop = 1, FixedContinueInterval = "false", ContinueIntervalLength = 0.4),ResultViewerManager(resultViewers={
ResultViewer(name="1", executeTrigger=executeTrigger.SimulationStarted, commands={
CreatePlot(id=1, x_display_unit="s", legend_layout=7, left_title="[degC]", curve_vernier=True, fix_time_range_value=0, zoom_x=(0, 1000), zoom_y_l=(28, 44)),
Plot(y=["water_air_HXTU1.hXSummary.Ta_in", "water_air_HXTU1.hXSummary.Tb_out", "coolingPipeDS.pipeSummary.T_out", "coolingPipeDS1.pipeSummary.T_out", "expansion_tank.tank1.T_out"], thicknesses=[2, 2, 2, 2, 2], colors=["4278190335", "4294901760", "4278222848", "4294902015", "4278190080"]),
CreatePlot(id=-1, x_display_unit="s", legend_layout=7, right_title="[W]", curve_vernier=True, fix_time_range_value=0, sub_plot=(1, 2), zoom_x=(0, 1000), zoom_y_l=(0, 1), zoom_y_r=(-1400, 200)),
Plot(y=["water_air_HXTU1.hXSummary.Qdot_abTotal"], thicknesses=[2], verticalAxes=[-1], colors=["4278190335"])})
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
    Across2 = 0.0001, Dhyd2 = 0.01, cearea2(displayUnit = "m2") = 1) 
    annotation (Placement(transformation(origin={264.067,22.9038},
extent={{-10,10},{10,-10}},
rotation=90)));
  TAThermalSystem.Sources.Air.AirSource_mT airSource_mT2(m = 0.1, phi_source = 0.4,
    T = T_Amb,
    redeclare package Medium = TYBase.Media_Extend.Air.MoistAir) 
    annotation (Placement(transformation(origin={228.067,54.9038},
extent={{-10,-10},{10,10}})));
  TAThermalSystem.Sources.Air.AirSink_pT airSink_pT2(T_sink = T_Amb, phi_sink = 0.4, redeclare package Medium = TYBase.Media_Extend.Air.MoistAir) 
    annotation (Placement(transformation(origin={228.067,10.5412},
extent={{-10,-10},{10,10}})));
  Modelica.Mechanics.Rotational.Sources.Speed speed1 
    annotation (Placement(transformation(origin={372.191,-86.2975},
extent={{-10,-10},{10,10}})));

  Modelica.Blocks.Sources.RealExpression realExpression1(y = PumpSpd_rpm * Modelica.Constants.pi / 30) 
    annotation (Placement(transformation(origin={307.191,-86.1798},
extent={{-10,-10},{10,10}})));
  TAThermalSystem.Reservoirs.ExpansionTank expansion_tank(tank1(pInitial = 1e5), T_Amb = T_Amb) 
    annotation (Placement(transformation(origin={418.232,-54.2175},
extent={{-10,-10},{10,10}})));
  TAThermalSystem.PumpAndFan.CentrifugalPump centrifugal_pump2(
    T_inlet(start



       = T_Amb),
    T_outlet(start



       = T_Amb),
    T_start = T_Amb,
    V(displayUnit = "l") = 0.0002,pout_start=3e5) 
    annotation (Placement(transformation(origin={384.232,-54.1798},
extent={{10,-10},{-10,10}})));
  TAThermalSystem.Pipes.LiquidCoolingPipe.CoolingPipeCR coolingPipeCR(p0 = 2.799999999999999e5, T0 = T_Amb) annotation (Placement(transformation(origin={318.133,-53.1876},
extent={{10.0997,-8.82172},{-10.0638,9.0078}})));

  TAThermalSystem.Valves.HydraulicValve.ValveFlowKvCooling zetaFlowCooling2(Kv_curve = {{0.0, 0}, {0.01, 0}, {0.1, 0.1}, {0.2, 0.3}, {0.4, 0.5}, {0.6, 0.6}, {0.8, 0.7}, {1.0, 20}, {1.1, 20}}, T0 = T_Amb) annotation (Placement(transformation(origin={269.896,126.658},
extent={{-10,-10},{10,10}},
rotation=90)));
  Modelica.Blocks.Sources.RealExpression realExpression6(y = valve_pos1) 
    annotation (Placement(transformation(origin={228.067,126.658},
extent={{-10,-10},{10,10}})));

  TAThermalSystem.Valves.HydraulicValve.ValveFlowKvCooling zetaFlowCooling1(Kv_curve = {{0.0, 0.01}, {0.01, 0.01}, {0.1, 0.1}, {0.2, 0.3}, {0.4, 0.5}, {0.6, 0.6}, {0.8, 0.7}, {1.0, 20}, {1.1, 20}}, T0 = T_Amb) annotation (Placement(transformation(origin={189.317,126.658},
extent={{-10,-10},{10,10}},
rotation=90)));
  Modelica.Blocks.Sources.RealExpression realExpression5(y = 1-valve_pos1) 
    annotation (Placement(transformation(origin={148.92,126.658},
extent={{-10,-10},{10,10}})));
  TAThermalSystem.Sources.HeatTransfer.BoundaryHeatFlow boundaryHeatFlow2(Q_flow = Q_flowF) 
    annotation (Placement(transformation(origin={596.815,29.7369},
extent={{10,-10},{-10,10}})));
  TAThermalSystem.Sources.HeatTransfer.BoundaryHeatFlow boundaryHeatFlow3(Q_flow = Q_flowR) 
    annotation (Placement(transformation(origin={656.636,25.3743},
extent={{10,-10},{-10,10}})));
  TAThermalSystem.Pipes.LiquidCoolingPipe.CoolingPipe coolingPipeDS1(
    Aheat = 0.18,
    L = 0.2,
    p0 = 1.3e5,
    T0 = T_Amb) 
    annotation (Placement(transformation(origin={566.903,29.6899},
extent={{-10.0469,-10.0086},{10.011,10.0101}},
rotation=270)));
  TAThermalSystem.Pipes.LiquidCoolingPipe.CoolingPipe coolingPipeDS2(
    Aheat = 0.18,
    L = 0.2,
    p0 = 1.3e5,
    T0 = T_Amb) 
    annotation (Placement(transformation(origin={626.725,25.5732},
extent={{-10.0469,-10.0086},{10.011,10.0101}},
rotation=-90)));
  TYBase.Thermal.FluidHeatFlow.ControlVolumes.CVBasic.ThermalHydraulicCV.BranchPipeCoolingCV branchPipeCoolingCV4(p0 = 2.6e5,
    T0 = T_Amb) 
    annotation (Placement(transformation(origin={269.649,186.975},
extent={{-8.16973,-8.43563},{8.66345,8.21938}})));
  TYBase.Thermal.FluidHeatFlow.ControlVolumes.CVBasic.ThermalHydraulicCV.BranchPipeCoolingCV branchPipeCoolingCV5(p0 = 2.7e5,
    T0 = T_Amb) 
    annotation (Placement(transformation(origin={270.069,-53.2254},
extent={{-8.16973,8.43563},{8.66345,-8.21938}})));
  TAThermalSystem.Valves.HydraulicValve.ValveFlowKvCooling valveFlowKvCooling4(





                                                               Kv_curve = {{0.0, 0}, {0.01, 0}, {0.1, 0.1}, {0.2, 0.3}, {0.4, 0.5}, {0.6, 0.6}, {0.8, 0.7}, {1.0, 20}, {1.1, 20}}, T0 = T_Amb
                                                                                                                                                                                             ) 
    annotation (Placement(transformation(origin={565.974,121.101},
extent={{10,10},{-10,-10}},
rotation=-270)));
  TAThermalSystem.Valves.HydraulicValve.ValveFlowKvCooling valveFlowKvCooling5(





                                                               Kv_curve = {{0.0, 0}, {0.01, 0}, {0.1, 0.1}, {0.2, 0.3}, {0.4, 0.5}, {0.6, 0.6}, {0.8, 0.7}, {1.0, 20}, {1.1, 20}}, T0 = T_Amb
                                                                                                                                                                                             ) 
    annotation (Placement(transformation(origin={627.394,120.422},
extent={{10,10},{-10,-10}},
rotation=-270)));
  Modelica.Blocks.Sources.RealExpression realExpression11(





                                                          y = valve_pos2
                                                               ) 
    annotation (Placement(transformation(origin={599.592,121.497},
extent={{10,-10},{-10,10}})));
  Modelica.Blocks.Sources.RealExpression realExpression13(





                                                          y = 1-valve_pos2
                                                               ) 
    annotation (Placement(transformation(origin={668.923,121.213},
extent={{10,-10},{-10,10}})));
  TAThermalSystem.Pipes.LiquidCoolingPipe.CoolingPipeC coolingPipe1(p0= 2.649999999999999e5, T0 = T_Amb, TA(start = T_Amb), TB(start = T_Amb)                                                                                                                             ) annotation (Placement(transformation(origin={269.865,74.1411},
extent={{-10.0997,-8.82172},{10.0638,9.0078}},
rotation=90)));
  TAThermalSystem.Pipes.LiquidCoolingPipe.CoolingPipe coolingPipeDS(title = "水管道", Dhyd = 0.025, Aheat = 0.1918,
    p0 = 1.6e5,
    T0 = T_Amb)      annotation(Placement(transformation(origin = {415.493, 189.132},
extent={{-10.0469,-10.0086},{10.011,10.0101}})));
  TAThermalSystem.Sources.HeatTransfer.BoundaryHeatFlow boundaryHeatFlow4(Q_flow = Q_flowP, n = 1) 
    annotation (Placement(transformation(origin={416.009,218.856},
extent={{10,-10},{-10,10}},
rotation=90)));
  TAThermalSystem.Pipes.LiquidCoolingPipe.CoolingPipeR coolingPipeR(p0 = 1.7e5,
    T0 = T_Amb) 
    annotation(Placement(transformation(origin={357.064,187.881},
extent={{-10.0997,-8.82172},{10.0638,9.0078}})));
  equation
  connect(airSink_pT2.port_a, water_air_HXTU1.d) 
    annotation (Line(origin={268.067,7.90379},
points={{-30,2.63741},{-10.1564,2.63741},{-10.1564,5.03681}},
color={0,232,232},
thickness=1));
  connect(water_air_HXTU1.c, airSource_mT2.port_b) 
    annotation (Line(origin={305.067,8.90379},
points={{-47.0374,24.1119},{-47.0374,46},{-67,46}},
color={0,232,232},
thickness=1));
  connect(expansion_tank.b, centrifugal_pump2.a) 
    annotation (Line(origin={374.027,63.9907},
points={{34.2048,-118.208},{20.2149,-118.208}},
color={0,170,255},
thickness=1));
  connect(speed1.flange, centrifugal_pump2.flange) 
    annotation (Line(origin={386.191,-75.2597},
points={{-4,-11.0378},{-4,11.0799},{-1.95873,11.0799}},
color={0,0,0}));
  connect(centrifugal_pump2.b, coolingPipeCR.a) 
    annotation (Line(origin={374.988,5.9907},
points={{-0.879482,-60.2083},{-46.8456,-60.2083},{-46.8456,-59.2161}},
color={0,170,255},
thickness=1));
  connect(branchPipeCoolingCV5.c, coolingPipeCR.b) 
    annotation (Line(origin={301.364,-0.0962083},
points={{-21.2954,-53.1292},{6.64556,-53.1292}},
color={0,170,255},
thickness=1));
  connect(realExpression6.y, zetaFlowCooling2.u) 
    annotation (Line(origin={475.726,78.9837},
points={{-236.659,47.6743},{-215.83,47.6743}},
color={0,0,127}));
  connect(zetaFlowCooling1.u, realExpression5.y) 
    annotation (Line(origin={167.92,126.407},
points={{11.3976,0.250413},{-8,0.250413}},
color={0,0,127}));
  connect(boundaryHeatFlow2.port[1], coolingPipeDS1.qa) 
    annotation (Line(origin={582.828,29.6201},
points={{3.987,0.1168},{-4.80087,0.1168},{-4.80087,-0.129059}},
color={191,0,0},
thickness=1));
  connect(coolingPipeDS2.qa, boundaryHeatFlow3.port[1]) 
    annotation (Line(origin={641.828,25.6201},
points={{-3.97887,-0.245759},{4.808,-0.245759},{4.808,-0.2458}},
color={191,0,0},
thickness=1));
  connect(zetaFlowCooling1.a, branchPipeCoolingCV5.a) 
    annotation (Line(origin={231.232,30.8202},
points={{-41.8772,85.8277},{-41.8772,-84.0456},{28.8366,-84.0456}},
color={0,170,255},
thickness=1));
  connect(speed1.w_ref, realExpression1.y) 
    annotation (Line(origin={339.232,-86.1798},
points={{20.9587,-0.117707},{-21.0413,-0.117707},{-21.0413,0}},
color={0,0,127}));
  connect(zetaFlowCooling1.b, branchPipeCoolingCV4.a) 
    annotation (Line(origin={293.232,199.82},
points={{-103.877,-63.0392},{-103.877,-12.845},{-33.5831,-12.845}},
color={0,170,255},
thickness=1));
  connect(zetaFlowCooling2.b, branchPipeCoolingCV4.b) 
    annotation (Line(origin={335.232,199.82},
points={{-65.2984,-63.0386},{-65.2984,-22.845},{-65.583,-22.845}},
color={0,170,255},
thickness=1));
  connect(coolingPipeDS1.b, expansion_tank.a) 
    annotation (Line(origin={682.155,5.59372},
points={{-115.398,14.0259},{-115.398,-59.8113},{-253.923,-59.8113}},
color={0,170,255},
thickness=1));
  connect(coolingPipeDS2.b, expansion_tank.a) 
    annotation (Line(origin={712.155,3.59372},
points={{-85.5761,11.9092},{-85.5761,-57.8113},{-283.923,-57.8113}},
color={0,170,255},
thickness=1));
  connect(water_air_HXTU1.a, branchPipeCoolingCV5.b) 
    annotation (Line(origin={274.232,-15.1798},
points={{-4.16336,28.0694},{-4.16336,-28.0456}},
color={0,170,255},
thickness=1));
  connect(valveFlowKvCooling4.b, coolingPipeDS1.a) 
    annotation (Line(origin={566.735,75.6294},
points={{-0.798774,35.3483},{-0.798774,-35.9817},{0.0218741,-35.9817}},
color={0,170,255},
thickness=1));
  connect(valveFlowKvCooling5.b, coolingPipeDS2.a) 
    annotation (Line(origin={627.735,72.6294},
points={{-0.378774,37.6687},{-0.378774,-37.0984},{-1.15613,-37.0984}},
color={0,170,255},
thickness=1));
  connect(realExpression11.y, valveFlowKvCooling4.u) 
    annotation (Line(origin={582.735,124.629},
points={{5.857,-3.1327},{-6.761,-3.1327},{-6.761,-3.5283}},
color={0,0,127}));
  connect(realExpression13.y, valveFlowKvCooling5.u) 
    annotation (Line(origin={647.735,121.629},
points={{10.188,-0.4168},{-10.341,-0.4168},{-10.341,-1.2079}},
color={0,0,127}));
  connect(coolingPipe1.a, water_air_HXTU1.b) 
    annotation (Line(origin={268.896,48.8202},
points={{1.00677,15.3108},{1.03791,-15.8685}},
color={0,170,255},
thickness=1));
  connect(coolingPipe1.b, zetaFlowCooling2.a) 
    annotation (Line(origin={268.896,100.82},
points={{1.00677,-16.5555},{1.03777,15.8279}},
color={0,170,255},
thickness=1));
  connect(boundaryHeatFlow4.port[1], coolingPipeDS.qa) 
  annotation(Line(origin={416.009,203.875},
points={{0,4.981},{0,-3.61875},{-0.316787,-3.61875}},
color={191,0,0},
thickness=1));
  connect(valveFlowKvCooling5.a, coolingPipeDS.b) 
  annotation(Line(origin={527,159},
points={{100.356,-28.5679},{100.356,29.986},{-101.436,29.986}},
color={0,170,255},
thickness=1));
  connect(valveFlowKvCooling4.a, coolingPipeDS.b) 
  annotation(Line(origin={528,159},
points={{37.9362,-27.8889},{37.9362,29.986},{-102.436,29.986}},
color={0,170,255},
thickness=1));
  connect(branchPipeCoolingCV4.c, coolingPipeR.a) 
  annotation(Line(origin={375,187},
points={{-95.351,-0.0250042},{-27.9463,-0.0250042},{-27.9463,0.843586}},
color={0,170,255},
thickness=1));
  connect(coolingPipeR.b, coolingPipeDS.a) 
  annotation(Line(origin={386,188},
  points={{-18.8127,-0.156414},{19.5356,-0.156414},{19.5356,0.985996}},
  color={0,170,255},
  thickness=1));
  end MotorCool;