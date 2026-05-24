model ACR290 "二次回路制冷R290"
 extends TAThermalSystem.Utilities.Icons.BasicIcons.Example;
  parameter Real ComprSpd_rpm = 4000 "压缩机转速（转/分钟）";
  parameter Real PumpH_rpm = 2000 "高温侧水泵转速（转/分钟）";
  parameter Real PumpL_rpm = 2000 "低温侧水泵转速（转/分钟）";
  parameter Modelica.Units.SI.Temperature TempSC(displayUnit = "K") = 10 "过冷度设置";
  annotation(Diagram(coordinateSystem(extent={{-100,-100},{100,100}},
grid={2,2})),experiment(Algorithm=Dassl,InlineIntegrator=false,InlineStepSize=false,NumberOfIntervals=5000,StartTime=0,StopTime=1000,Tolerance=0.0001)
,__MWORKS(ContinueSimConfig(SaveContinueFile="false",SaveBeforeStop="false",NumberBeforeStop=1,FixedContinueInterval="false",ContinueIntervalLength=1000,ContinueTimeVector),ResultViewerManager(resultViewers={
ResultViewer(name="1", executeTrigger=executeTrigger.SimulationStarted, commands={
CreatePlot(id=1, x_display_unit="s", legend_layout=7, left_title="[W]", curve_vernier=True, fix_time_range_value=0, zoom_x=(0, 1000), zoom_y_l=(-200000, 1.2e+06)),
Plot(y=["chillerPlateCooling1.hXSummary.Qdot_abTotal", "chillerPlateCooling2.hXSummary.Qdot_abTotal"], thicknesses=[2, 2], colors=["4278190335", "4294901760"]),
CreatePlot(id=-1, x_display_unit="s", legend_layout=7, left_title="[bar]", curve_vernier=True, fix_time_range_value=0, sub_plot=(2, 1), zoom_x=(0, 1000), zoom_y_l=(0, 25)),
Plot(y=["valve.a.p", "valve.b.p"], thicknesses=[2, 2], colors=["4278190335", "4294901760"]),
CreatePlot(id=-1, x_display_unit="s", legend_layout=7, left_title="[kg/s]", curve_vernier=True, fix_time_range_value=0, sub_plot=(3, 1), zoom_x=(0, 1000), zoom_y_l=(0, 0.14)),
Plot(y=["compressor.mdot"], thicknesses=[2], colors=["4278190335"])})
}))
,Protection(access=Access.nonPackageDuplicate),Documentation(link="modelica://TAThermalSystem/Resource/Doc/ACR290.html"));
  Real[4] xin ={compressor.hout, chillerPlateCooling1.simplePipe.h_out, chillerPlateCooling2.simplePipe.h_in, compressor.hin} "横坐标比焓变量,单位kJ/kg" annotation(Dialog(group = "可视化变量序列,用于ph相图动态显示"));
  Real[4] yin ={compressor.pout,chillerPlateCooling1.hXSummary.pb, chillerPlateCooling2.hXSummary.pa, compressor.pin} "纵坐标对应压力变量,单位Pa" annotation(Dialog(group = "可视化变量序列,用于ph相图动态显示"));
  parameter Modelica.Units.SI.Temperature T_Amb=308.15;
  TAThermalSystem.HeatExchangers.CoolingRadiatorNTU.ChillerPlateCooling chillerPlateCooling2(RefInit(mdot0=0.1, p_in=3.5e5, p_out=3e5), redeclare model Friction = TYBase.Thermal.FluidHeatFlow.PressureLoss.LiquidPressureDrop.SingularPressureDrop, redeclare package RefMedium = TYMedia.Helmholtz.Propane, hXSummary(pa(start=chillerPlateCooling2.RefInit.p_in), pb(start=chillerPlateCooling2.RefInit.p_out)), T0=T_Amb, n=2) 
    annotation (Placement(transformation(origin={-131.097,13.9885},
extent={{-10,-10},{10,10}},
rotation=90)));
  TAThermalSystem.Pipes.TwoPhasePipe.PipeAdiabatic pipeAdiabatic(RefrigerantTemperature=35,RefrigerantMass=0.01,RefrigerantMassDistribution=2,init(initType = TYBase.Utilities.Types.Init.Initial_MT),redeclare package Medium = TYMedia.Helmholtz.Propane) 
    annotation(Placement(transformation(origin={-19.3767,72.8983},
extent={{-10,-10},{10,10}})));
  TAThermalSystem.Compressor.Compressor compressor(redeclare package Medium = TYMedia.Helmholtz.Propane) annotation(Placement(transformation(origin={-62.2127,73.0384},
extent={{-10,-10},{10,10}})));
  TAThermalSystem.Pipes.TwoPhasePipe.PipeAdiabatic pipeAdiabatic1(RefrigerantTemperature=35,RefrigerantMass=0.01,RefrigerantMassDistribution=2,init(initType = TYBase.Utilities.Types.Init.Initial_MT),redeclare package Medium = TYMedia.Helmholtz.Propane) 
    annotation(Placement(transformation(origin={-87.1123,73.4125},
extent={{-10,-10},{10,10}})));
  Modelica.Mechanics.Rotational.Sources.Speed speed 
    annotation(Placement(transformation(origin={-49.9998,40.2401},
extent={{10,-10},{-10,10}})));
  Modelica.Blocks.Sources.RealExpression realExpression1(y = ComprSpd_rpm) 
    annotation(Placement(transformation(origin={19.7728,39.8015},
extent={{10,-10},{-10,10}})));
  TAThermalSystem.Reservoirs.Reservoir_fillinglevel reservoir( RefrigerantTemperature=35, RefrigerantMass=0.051518, RefrigerantMassDistribution=1, H=0.4,redeclare package Medium = TYMedia.Helmholtz.Propane,H_Out=0.35,FillingLevel0=0.6) 
    annotation(Placement(transformation(origin={-111.772,73.1197},
extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Math.Gain gain1(k = Modelica.Constants.pi / 30) 
    annotation(Placement(transformation(origin={-14,40.2401},
extent={{10,-10},{-10,10}})));
  TAThermalSystem.Sensors.Refrigerant.PTSensor pTSensor(redeclare package Medium = TYMedia.Helmholtz.Propane) 
    annotation (Placement(transformation(origin={12.1463,73.1889},
extent={{-10,-10},{10,10}})));
  TAThermalSystem.HeatExchangers.CoolingRadiatorNTU.ChillerPlateCooling chillerPlateCooling1(RefInit(mdot0 = 0.1, p_in = 5.5e5, T0 = T_Amb, T_air0 = T_Amb), redeclare model Friction = TYBase.Thermal.FluidHeatFlow.PressureLoss.LiquidPressureDrop.SingularPressureDrop,redeclare package RefMedium = TYMedia.Helmholtz.Propane,hXSummary(pa(start=chillerPlateCooling1.RefInit.p_in),pb(start=chillerPlateCooling1.RefInit.p_out)),T0=T_Amb,n=2) 
    annotation (Placement(transformation(origin={60.2273,5.19791},
extent={{-10,-10},{10,10}},
rotation=-90)));
  TAThermalSystem.Sensors.Refrigerant.SuperCoolingSensor superCoolingSensor(redeclare package Medium = TYMedia.Helmholtz.Propane) 
    annotation(Placement(transformation(origin={21.2981,-39.996},
extent={{10,10},{-10,-10}})));
  TAThermalSystem.Pipes.TwoPhasePipe.PipeAdiabatic pipeAdiabatic3(redeclare package Medium = TYMedia.Helmholtz.Propane) 
    annotation(Placement(transformation(origin={-29.4222,-39.6164},
extent={{10,10},{-10,-10}})));
  Modelica.Blocks.Sources.Constant SetPoint_SC(k = TempSC)
    "过冷度设置值" annotation(Placement(transformation(origin={38.7789,-80.1066},
extent={{10,-10},{-10,10}})));
  TAThermalSystem.Valves.RefrigerantValve.ValveFlowKv valve(
  redeclare package Medium = TYMedia.Helmholtz.Propane,
    mdot(start = 0.1, fixed = false),





    Kv_curve = {{0.0, 0.001}, {0.01, 0.001}, {0.1, 0.1}, {0.2, 0.3}, {0.4, 0.5}, {0.6, 0.6}, {0.8, 0.7}, {1.0, 1}, {1.1, 1}}, use_yd0 = false) 
    annotation(Placement(transformation(origin={-73.9255,-39.438},
extent={{17.2553,15.0595},{-17.2553,-15.0595}})));
  Modelica.Blocks.Nonlinear.DeadZone deadZone1(uMax = 0.5) 
    annotation(Placement(transformation(origin={-28.1298,-74.2576},
extent={{10,-10},{-10,10}})));
  Modelica.Blocks.Math.Add add1(k2 = -1) 
    annotation(Placement(transformation(origin={3.57812,-74.4226},
extent={{10,-10},{-10,10}})));
  TYBase.Blocks.PIDsimple PID4(     controllerType = Modelica.Blocks.Types.SimpleController.PI,yMin=0.05,y_start=0.1,k=0.1,Ti=1) annotation(Placement(transformation(origin={-56.176,-74.3055},
extent={{10,-10},{-10,10}})));
  TAThermalSystem.Utilities.DynamicDisplay.ph_R290 ph_R290_1(x = xin, y = yin) 
    annotation(Placement(transformation(origin={-186.734,95.5565},
extent={{0,0},{259.364,196.887}})));
  Modelica.Mechanics.Rotational.Sources.Speed speed2 
    annotation (Placement(transformation(origin={128.41,-71.7995},
extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Sources.RealExpression realExpression3(y = PumpH_rpm* Modelica.Constants.pi / 30) 
    annotation (Placement(transformation(origin={91.7101,-72.8631},
extent={{-10,-10},{10,10}})));
  TAThermalSystem.Reservoirs.ExpansionTank expansion_tank1(tank1(pInitial = 1e5), T_Amb = T_Amb,volume=0.0005,initialFillingLevel=0.5) 
    annotation (Placement(transformation(origin={172.522,-38.7874},
extent={{-10,-10},{10,10}})));
  TAThermalSystem.PumpAndFan.CentrifugalPump centrifugal_pump1(
    T_inlet(start



       = T_Amb),
    T_outlet(start



       = T_Amb),
    T_start = T_Amb,
    V(displayUnit = "l") = 0.0002,pout_start=3e5) 
    annotation (Placement(transformation(origin={138.615,-38.5802},
extent={{10,-10},{-10,10}})));
  TAThermalSystem.HeatExchangers.CoolingRadiatorNTU.Water_Air_HXNTU water_air_HXTU2(
    ConsiderMass = false, Across1(displayUnit = "cm2") = 0.0001, Dhyd1(displayUnit = "mm") = 0.01, cearea1(displayUnit = "m2") = 1, ConsiderationFins_cd = false,
    etas2 = 0.8, ConsiderationFins_ab = true, fromDp = false,
    redeclare model Friction_ab = TYBase.Thermal.FluidHeatFlow.PressureLoss.HXPressureDrop.SingularPressureDrop,
    T1_a(start = T_Amb),
    T1_b(start = T_Amb),
    T2_in(start = T_Amb),
    T2_out(start = T_Amb),
    Twall(start = T_Amb),
    Across2 = 0.0001, Dhyd2 = 0.01, cearea2(displayUnit = "m2") = 1) 
    annotation (Placement(transformation(origin={251.785,-0.239264},
extent={{10,-10},{-10,10}},
rotation=90)));
  TAThermalSystem.Sources.Air.AirSource_mT airSource_mT1(m = 1, phi_source = 0.4,
    T = T_Amb,
    redeclare package Medium = TYBase.Media_Extend.Air.MoistAir) 
    annotation (Placement(transformation(origin={289.775,-21.0971},
extent={{10,-10},{-10,10}})));
  TAThermalSystem.Sources.Air.AirSink_pT airSink_pT1(T_sink = T_Amb, phi_sink = 0.4, redeclare package Medium = TYBase.Media_Extend.Air.MoistAir) 
    annotation (Placement(transformation(origin={287.375,20.6874},
extent={{10,-10},{-10,10}})));
  TAThermalSystem.Pipes.LiquidCoolingPipe.CoolingPipeCR coolingPipeCR3(p0=2.5e5, T0=T_Amb, redeclare model Friction = .TAThermalSystem.Utilities.PressureDrop.UserDefined)   annotation(Placement(transformation(origin={169.073,77.0094},
extent={{-10.0997,-8.82172},{10.0638,9.0078}})));
  TAThermalSystem.HeatExchangers.CoolingRadiatorNTU.Water_Air_HXNTU water_air_HXTU1(
    ConsiderMass = false, Across1(displayUnit = "cm2") = 0.0001, Dhyd1(displayUnit = "mm") = 0.01, cearea1(displayUnit = "m2") = 2, ConsiderationFins_cd = false,
    etas2 = 0.8, ConsiderationFins_ab = true, fromDp = false,
    redeclare model Friction_ab = TYBase.Thermal.FluidHeatFlow.PressureLoss.HXPressureDrop.SingularPressureDrop,
    T1_a(start = T_Amb),
    T1_b(start = T_Amb),
    T2_in(start = T_Amb),
    T2_out(start = T_Amb),
    Twall(start = T_Amb),
    Across2 = 0.0001, Dhyd2 = 0.01, cearea2(displayUnit = "m2") = 2,T0=T_Amb) 
    annotation (Placement(transformation(origin={-295.927,21.6312},
extent={{-10,10},{10,-10}},
rotation=90)));
  TAThermalSystem.Sources.Air.AirSource_mT airSource_mT2(m = 0.1, phi_source = 0.4,
    T = T_Amb,
    redeclare package Medium = TYBase.Media_Extend.Air.MoistAir) 
    annotation (Placement(transformation(origin={-331.927,53.6313},
extent={{-10,-10},{10,10}})));
  TAThermalSystem.Sources.Air.AirSink_pT airSink_pT2(T_sink = T_Amb, phi_sink = 0.4, redeclare package Medium = TYBase.Media_Extend.Air.MoistAir) 
    annotation (Placement(transformation(origin={-331.927,2.07433},
extent={{-10,-10},{10,10}})));
  Modelica.Mechanics.Rotational.Sources.Speed speed1 
    annotation (Placement(transformation(origin={-199.242,33.1093},
extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Sources.RealExpression realExpression2(y = PumpL_rpm * Modelica.Constants.pi / 30) 
    annotation (Placement(transformation(origin={-236.744,32.34},
extent={{-10,-10},{10,10}})));
  TAThermalSystem.Reservoirs.ExpansionTank expansion_tank(tank1(pInitial = 1e5), T_Amb = T_Amb,initialFillingLevel=0.1,volume=0.0005) 
    annotation (Placement(transformation(origin={-220.025,69.0331},
extent={{10,-10},{-10,10}})));
  TAThermalSystem.PumpAndFan.CentrifugalPump centrifugal_pump2(
    T_inlet(start = T_Amb),
    T_outlet(start = T_Amb),
    T_start = T_Amb,
    V(displayUnit = "l") = 0.0002,pout_start=3e5) 
    annotation (Placement(transformation(origin={-188.615,68.8622},
extent={{-10,-10},{10,10}})));
  TAThermalSystem.Pipes.LiquidCoolingPipe.CoolingPipeCR coolingPipeCR(p0=2.799999999999999e5, T0=T_Amb, redeclare model Friction = .TAThermalSystem.Utilities.PressureDrop.UserDefined)   annotation(Placement(transformation(origin={-210.457,-37.4419},
extent={{10.0997,-8.82172},{-10.0638,9.0078}})));
  equation
  connect(compressor.b, pipeAdiabatic.a) 
  annotation(Line(origin={-149.982,39.1189},
points={{97.7689,33.9195},{120.6049,33.9195},{120.6049,33.7794}},
color={0,128,0},
thickness=1));
  connect(pipeAdiabatic1.b, compressor.a) 
  annotation(Line(origin={-149.982,-0.881134},
points={{72.8697,74.293634},{77.7693,74.293634},{77.7693,73.919534}},
color={0,128,0},
thickness=1));
  connect(compressor.flange, speed.flange) 
  annotation(Line(origin={-131.982,19.1189},
points={{69.7693,43.9195},{69.7693,21.1212},{71.9822,21.1212}},
color={0,0,0}));
  connect(speed.w_ref, gain1.y) 
  annotation(Line(origin={-98.0602,26.6678},
points={{60.0604,13.5723},{73.0602,13.5723}},
color={0,0,127}));
  connect(gain1.u, realExpression1.y) 
  annotation(Line(origin={-54.4574,26.5452},
points={{52.4574,13.6949},{63.2301,13.6949},{63.2301,13.2563}},
color={0,0,127}));
  connect(pipeAdiabatic.b, pTSensor.a) 
  annotation(Line(origin={-3.5016,73.4528},
points={{-5.8751,-0.5545},{5.6479,-0.5545},{5.6479,-0.2639}},
color={0,128,0},
thickness=1));
  connect(pTSensor.b, chillerPlateCooling1.a) 
  annotation(Line(origin={38,44},
  points={{-15.8537,29.1889},{16.2273,29.1889},{16.2273,-28.8021}},
  color={0,128,0},
  thickness=1));
  connect(chillerPlateCooling2.b, reservoir.port_a) 
  annotation(Line(origin={-123,49},
  points={{-2.097,-25.0115},{-2.097,24.0197},{1.22816,24.0197}},
  color={0,128,0},
  thickness=1));
  connect(reservoir.b, pipeAdiabatic1.a) 
  annotation(Line(origin={-99,73},
  points={{-2.77184,0.0197054},{1.88766,0.0197054},{1.88766,0.4125}},
  color={0,128,0},
  thickness=1));
  connect(SetPoint_SC.y, add1.u2) 
  annotation(Line(origin={-172.63,-87.3116},
points={{200.409,7.205},{188.2082,7.205},{188.2082,6.889}},
color={0,0,127}));
  connect(add1.y, deadZone1.u) 
  annotation(Line(origin={-134.63,-69.3116},
points={{127.208,-5.111},{118.501,-5.111},{118.501,-4.946}},
color={0,0,127}));
  connect(deadZone1.y, PID4.u) 
  annotation(Line(origin={-104.63,-69.3116},
points={{65.5006,-4.946},{60.4544,-4.946},{60.4544,-4.9939}},
color={0,0,127}));
  connect(PID4.y, valve.u) 
  annotation(Line(origin={-84.2239,-110.485},
points={{17.0685,36.2203},{10.2984,36.2203},{10.2984,55.9871}},
color={0,0,127}));
  connect(pipeAdiabatic3.b, valve.a) 
  annotation(Line(origin={-48.9921,-38.9096},
points={{9.56994,-0.706754},{-7.6781,-0.706754},{-7.6781,-0.5284}},
color={0,128,0},
thickness=1));
  connect(superCoolingSensor.outPort, add1.u1) 
  annotation(Line(origin={-76.9921,-42.9096},
points={{98.2902,-8.48641},{98.2902,-25.513},{92.5702,-25.513}},
color={0,0,127}));
  connect(chillerPlateCooling1.b, superCoolingSensor.a) 
  annotation(Line(origin={36,-21},
points={{18.2273,16.19791},{18.2273,-18.996},{-4.70191,-18.996}},
color={0,128,0},
thickness=1));
  connect(superCoolingSensor.b, pipeAdiabatic3.a) 
  annotation(Line(origin={-11,-38},
points={{22.2981,-1.99601},{-8.42216,-1.99601},{-8.42216,-1.61635}},
color={0,128,0},
thickness=1));
  connect(valve.b, chillerPlateCooling2.a) 
  annotation(Line(origin={-108,-18},
  points={{16.8192,-21.438},{-17.097,-21.438},{-17.097,21.9885}},
  color={0,128,0},
  thickness=1));
  connect(speed2.flange, centrifugal_pump1.flange) 
  annotation(Line(origin={121.776,-61.1946},
points={{16.634,-10.6049},{16.634,12.6144},{16.839,12.6144}},
color={0,0,0}));
  connect(airSink_pT1.port_a, water_air_HXTU2.d) 
  annotation(Line(origin={272.965,-32.4957},
points={{4.41,53.1831},{-15.0236,53.1831},{-15.0236,42.2196}},
color={0,232,232},
thickness=1));
  connect(water_air_HXTU2.c, airSource_mT1.port_b) 
  annotation(Line(origin={309.965,-31.4957},
points={{-52.1426,21.1445},{-52.1426,10.3985},{-30.19,10.3985}},
color={0,232,232},
thickness=1));
  connect(expansion_tank1.b, centrifugal_pump1.a) 
  annotation(Line(origin={137.918,-48.0624},
points={{24.604,9.275},{10.7071,9.275},{10.7071,9.44443}},
color={0,170,255},
thickness=1));
  connect(coolingPipeCR3.b, water_air_HXTU2.a) 
  annotation(Line(origin={193.918,42.9376},
points={{-14.7216,34.034},{51.8652,34.034},{51.8652,-33.1627}},
color={0,170,255},
thickness=1));
  connect(realExpression3.y, speed2.w_ref) 
  annotation(Line(origin={109.928,-72.5655},
points={{-7.2175,-0.2976},{6.482,-0.2976},{6.482,0.766}},
color={0,0,127}));
  connect(centrifugal_pump1.b, chillerPlateCooling1.c) 
  annotation(Line(origin={96,-16},
points={{32.4911,-22.6179},{-29.7727,-22.6179},{-29.7727,11.19791}},
color={0,170,255},
thickness=1));
  connect(chillerPlateCooling1.d, coolingPipeCR3.a) 
  annotation(Line(origin={112,52},
points={{-45.7727,-36.80209},{-45.7727,24.9717},{47.0625,24.9717}},
color={0,170,255},
thickness=1));
  connect(water_air_HXTU2.b, expansion_tank1.a) 
  annotation(Line(origin={214,-25},
  points={{31.9181,14.7128},{31.9181,-13.7874},{-31.478,-13.7874}},
  color={0,170,255},
  thickness=1));
  connect(airSink_pT2.port_a, water_air_HXTU1.d) 
  annotation(Line(origin={-291.927,6.63129},
points={{-30,-4.55696},{-10.1564,-4.55696},{-10.1564,5.03671}},
color={0,232,232},
thickness=1));
  connect(water_air_HXTU1.c, airSource_mT2.port_b) 
  annotation(Line(origin={-254.927,7.63129},
points={{-47.0374,24.1118},{-47.0374,46},{-67,46}},
color={0,232,232},
thickness=1));
  connect(speed1.flange, centrifugal_pump2.flange) 
  annotation(Line(origin={-185.242,44.1471},
points={{-4,-11.0378},{-4,14.7151},{-3.373,14.7151}},
color={0,0,0}));
  connect(speed1.w_ref, realExpression2.y) 
  annotation(Line(origin={-232.201,33.227},
points={{20.959,-0.1177},{6.457,-0.1177},{6.457,-0.887}},
color={0,0,127}));
  connect(expansion_tank.b, centrifugal_pump2.a) 
  annotation(Line(origin={-204.215,68.4571},
points={{-5.81,0.576},{5.58988,0.576},{5.58988,0.367326}},
color={0,170,255},
thickness=1));
  connect(coolingPipeCR.b, water_air_HXTU1.a) 
  annotation(Line(origin={-255.215,-12.5429},
points={{34.6346,-24.9368},{-34.7102,-24.9368},{-34.7102,24.1599}},
color={0,170,255},
thickness=1));
  connect(centrifugal_pump2.b, chillerPlateCooling2.c) 
  annotation(Line(origin={-170,39},
points={{-8.4918,29.8244},{32.903,29.8244},{32.903,-15.0115}},
color={0,170,255},
thickness=1));
  connect(chillerPlateCooling2.d, coolingPipeCR.a) 
  annotation(Line(origin={-181,-24},
points={{43.903,27.9885},{43.903,-13.4797},{-19.4471,-13.4797}},
color={0,170,255},
thickness=1));
  connect(water_air_HXTU1.b, expansion_tank.a) 
  annotation(Line(origin={-260,50},
  points={{-30.0603,-18.3209},{-30.0603,19.0331},{29.9748,19.0331}},
  color={0,170,255},
  thickness=1));
  end ACR290;