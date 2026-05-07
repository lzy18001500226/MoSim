model MultiLoopHIL"水回路多回路"
extends TAThermalSystem.Utilities.Icons.BasicIcons.Example;
  parameter Modelica.SIunits.Temperature T_Amb = 303.15 "环境温度";
  parameter Real PumpSpd_rpm = 500"水泵转速设置（转/分钟）";
  parameter Modelica.SIunits.Power Q_flow = 1000 "发热量";
  parameter Real FanSpd_rpm = 1000"风扇转速设置（转/分钟）";
  parameter Real T_High = 50 "温度临界值上限degC，使散热回路Off转为On";
  parameter Real T_Low = 45 "温度临界值下限degC，使散热回路On转为Off";
  annotation(Diagram(coordinateSystem(extent={{-100,-100},{100,100}},
grid={2,2})),experiment(Algorithm=Euler,InlineIntegrator=false,InlineStepSize=false,IntegratorStep=0.01,Interval=0.01,StartTime=0,StopTime=200,Tolerance=0.0001),Documentation(link="modelica://TAThermalSystem/Resource/Doc/MultiLoopHIL.html"),Protection(access=Access.nonPackageDuplicate),__MWORKS(ResultViewerManager(resultViewers={
ResultViewer(name="1", executeTrigger=executeTrigger.SimulationStarted, commands={
CreatePlot(id=1, x_display_unit="s", legend_layout=7, left_title="[W]", fix_time_range_value=0, zoom_x=(0, 200), zoom_y_l=(-4000, 1000)),
Plot(y=["water_air_HXTU1.hXSummary.Qdot_abTotal"], thicknesses=[2], colors=["4278190335"]),
CreatePlot(id=-1, x_display_unit="s", legend_layout=13, left_title="[kg/s]", fix_time_range_value=0, sub_plot=(2, 1), zoom_x=(0, 200), zoom_y_l=(0.08, 0.18)),
Plot(y=["centrifugal_pump2.m_flow"], thicknesses=[2], colors=["4278190335"])})
})));
  TAThermalSystem.HeatExchangers.CoolingRadiatorNTU.Water_Air_HXNTU water_air_HXTU1(
    ConsiderMass = false, Across1(displayUnit = "cm2"), Dhyd1(displayUnit = "mm"), cearea1
    (displayUnit = "m2") = 0.1,
    ConsiderationFins_cd = false,
    etas2 = 0.8, ConsiderationFins_ab = true, fromDp = false,
    cearea2(displayUnit= "m2") = 0.1,redeclare model Friction_ab = TYBase.Thermal.FluidHeatFlow.PressureLoss.HXPressureDrop.PressureDropRT,T0=T_Amb) 
    annotation (Placement(transformation(origin={27.3758,14.4141},
extent={{-10,10},{10,-10}})));
  TAThermalSystem.Sources.Air.AirSink_pT airSink_pT2( phi_sink = 0.4, redeclare package Medium = TYBase.Media_Extend.Air.MoistAir,T_sink=T_Amb) 
    annotation (Placement(transformation(origin={-2.82506,38.9743},
extent={{-10,-10},{10,10}})));
  TAThermalSystem.Sources.Air.AirSink_pT airSink_pT1(
phi_sink = 0.4, redeclare package Medium = TYBase.Media_Extend.Air.MoistAir,T_sink=T_Amb) 
    annotation (Placement(transformation(origin={102.805,39.7081},
extent={{10,-10},{-10,10}})),__MWORKS(BlockSystem(StateMachine)));
  TAThermalSystem.PumpAndFan.Fan2Table fan2Table 
    annotation (Placement(transformation(origin={71.0561,39.3012},
extent={{10,10},{-10,-10}})));
  TAThermalSystem.Sources.Mechanics.RotationalInputSource rotationalInputSource 
    annotation (Placement(transformation(origin={56.9365,63.22},
extent={{-8,-6},{10,6}})));
  Modelica.Blocks.Sources.RealExpression realExpression(y=FanSpd_rpm) 
    annotation (Placement(transformation(origin={20.4315,63.3205},
extent={{-10,-10},{10,10}})));
  TAThermalSystem.PumpAndFan.CentrifugalPump centrifugal_pump2(pout_start=2e5,T_inlet(start=T_Amb),T_outlet(start=T_Amb),T_start=T_Amb) annotation (Placement(transformation(origin={31.1282,-98.864},
extent={{10,-10},{-10,10}})));
  TAThermalSystem.Sources.Mechanics.RotationalInputSource rotationalInputSource1 
    annotation (Placement(transformation(origin={20.942,-125.119},
extent={{-8,-6},{10,6}})),__MWORKS(BlockSystem(StateMachine)));
  Modelica.Blocks.Sources.RealExpression realExpression2(y=PumpSpd_rpm) 
    annotation (Placement(transformation(origin={-10.4456,-126.148},
extent={{-10,-10},{10,10}})));
  TAThermalSystem.Valves.HydraulicValve.ValveFlowKvCooling valveFlowKvCooling(Kv_curve={{0.0, 0.1}, {0.01, 0.1}, {0.1, 5}, {0.2, 7}, {0.4, 8}, {0.6, 9}, {0.8, 10}, {1.0, 20}, {1.1, 20}},T0=T_Amb) 
    annotation (Placement(transformation(origin={-19.6646,8.47603},
extent={{-10,-10},{10,10}})));
  TAThermalSystem.Valves.HydraulicValve.ValveFlowKvCooling valveFlowKvCooling1(Kv_curve={{0.0, 0.1}, {0.01, 0.1}, {0.1, 5}, {0.2, 7}, {0.4, 8}, {0.6, 9}, {0.8, 10}, {1.0, 20}, {1.1, 20}},T0=T_Amb) 
    annotation (Placement(transformation(origin={-18.4082,-23.0753},
extent={{-10,-10},{10,10}})));
  TYBase.Thermal.FluidHeatFlow.ControlVolumes.CVBasic.ThermalHydraulicCV.BranchPipeCoolingCVHIL branchPipeCoolingCV(p0=1.8e5,T0=T_Amb) 
    annotation (Placement(transformation(origin={-48.4463,-23.6184},
extent={{-8.16973,-8.43563},{8.66345,8.21938}},
rotation=90)));
  TAThermalSystem.Pipes.LiquidCoolingPipeHIL.CoolingPipe coolingPipeDS2(title="水管道", Dhyd=0.025, Aheat=0.1918, L(displayUnit="mm")=0.46, redeclare model Friction = .TAThermalSystem.Utilities.PressureDrop.TableForZeta, T0=T_Amb) annotation (Placement(transformation(origin={54.9497,8.74764},
extent={{-10.0469,-10.0086},{10.011,10.0101}})),__MWORKS(BlockSystem(StateMachine)));
  TAThermalSystem.Pipes.LiquidCoolingPipeHIL.CoolingPipe coolingPipeDS1(title="水管道", Dhyd=0.025, Aheat=0.1918, L(displayUnit="mm")=0.46, redeclare model Friction = .TAThermalSystem.Utilities.PressureDrop.TableForZeta, T0=T_Amb) annotation (Placement(transformation(origin={55.9669,-21.5665},
extent={{-10.0469,-10.0086},{10.011,10.0101}})),__MWORKS(BlockSystem(StateMachine)));
  TAThermalSystem.Pipes.LiquidCoolingPipeHIL.CoolingPipeCR coolingPipeDS3(title="水管道", Dhyd=0.025, Aheat=0.1918, L(displayUnit="mm")=0.46, redeclare model Friction = .TAThermalSystem.Utilities.PressureDrop.TableForZeta, T0=T_Amb) annotation (Placement(transformation(origin={-7.19753,-98.8822},
extent={{10.0469,-10.0086},{-10.011,10.0101}})),__MWORKS(BlockSystem(StateMachine)));
  TAThermalSystem.Reservoirs.ExpansionTank_NPorts expansionTankNports(closedTank=true,T_liquidInit=T_Amb,T_airInit=T_Amb) 
    annotation (Placement(transformation(origin={54.0298,-79.8799},
extent={{-10,-10},{10,10}})));
  TAThermalSystem.Sources.HeatTransfer.BoundaryHeatFlow boundaryHeatFlow1(Q_flow = 0, n = 1,use_Qflow_in=true) 
    annotation (Placement(transformation(origin={-6.21163,-68.2833},
extent={{10,-10},{-10,10}},
rotation=90)),__MWORKS(BlockSystem(StateMachine)));
  Modelica.Blocks.Sources.RealExpression realExpression4(y=Q_flow) 
    annotation (Placement(transformation(origin={-22.653,-46.0659},
extent={{-10,-10},{10,10}})));
  TAThermalSystem.Sensors.Coolant.PTSensorCoolant pTSensorCoolant1 
    annotation (Placement(transformation(origin={-34.8149,-98.2605},
extent={{10,-10},{-10,10}})),__MWORKS(BlockSystem(StateMachine)));
  Modelica.Blocks.Logical.Hysteresis hysteresis(uHigh=T_High,uLow=T_Low) 
    annotation (Placement(transformation(origin={-147.425,-15.9388},
extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Logical.Switch switch1 
    annotation (Placement(transformation(origin={-103.697,-15.3847},
extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Sources.RealExpression realExpression5(y=0) 
    annotation (Placement(transformation(origin={-163.317,27.7438},
extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Sources.RealExpression realExpression6(y=1) 
    annotation (Placement(transformation(origin={-161.884,-80.534},
extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Nonlinear.SlewRateLimiter slewRateLimiter(Rising=0.5) 
    annotation (Placement(transformation(origin={-72.1124,-14.4758},
extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Logical.Switch switch2 
    annotation (Placement(transformation(origin={-101.178,39.2497},
extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Nonlinear.SlewRateLimiter slewRateLimiter1(Rising=0.5) 
    annotation (Placement(transformation(origin={-69.2592,37.5335},
extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Nonlinear.FixedDelay fixedDelay 
    annotation (Placement(transformation(origin={-89.2053,-57.9375},
extent={{10,-10},{-10,10}})));
  equation
  connect(airSink_pT2.port_a, water_air_HXTU1.d) 
  annotation(Line(origin={70.227,-25.2235},
points={{-63.0521,64.1978},{-52.8144,64.1978},{-52.8144,45.794}},
color={0,232,232},
thickness=1));
  connect(airSink_pT1.port_a, fan2Table.a) 
  annotation(Line(origin={55.4975,101.067},
points={{37.3074,-61.3587},{25.5586,-61.3587},{25.5586,-61.7656}},
color={0,232,232},
thickness=1));
  connect(fan2Table.b, water_air_HXTU1.c) 
  annotation(Line(origin={-22.7776,10.693},
points={{83.8337,28.6082},{60.2653,28.6082},{60.2653,9.7585}},
color={0,232,232},
thickness=1));
  connect(rotationalInputSource.flange, fan2Table.shaft) 
  annotation(Line(origin={71.8066,68.6668},
points={{-4.87013,-5.44676},{-0.750488,-5.44676},{-0.750488,-19.3656}},
color={0,0,0}));
  connect(realExpression.y, rotationalInputSource.u) 
  annotation(Line(origin={40.5825,59.1581},
points={{-9.151,4.1624},{9.354,4.1624},{9.354,4.0619}},
color={0,0,127}));
  connect(rotationalInputSource1.flange, centrifugal_pump2.flange) 
  annotation(Line(origin={68.5534,-133.666},
points={{-37.61136,8.547},{-37.61136,24.802},{-37.4252,24.802}},
color={0,0,0}));
  connect(branchPipeCoolingCV.b, valveFlowKvCooling1.a) 
  annotation(Line(origin={-17,-23},
points={{-21.4463,-0.618399},{-11.4183,-0.618399},{-11.4183,-0.113074}},
color={0,170,255},
thickness=1));
  connect(branchPipeCoolingCV.c, valveFlowKvCooling.a) 
  annotation(Line(origin={-39,-3},
  points={{-9.4463,-10.6184},{-9.4463,11.4383},{9.32523,11.4383}},
  color={0,170,255},
  thickness=1));
  connect(valveFlowKvCooling1.b, coolingPipeDS1.a) 
  annotation(Line(origin={18,-22},
points={{-26.2848,-1.11307},{28.0091,-1.11307},{28.0091,0.287338}},
color={0,170,255},
thickness=1));
  connect(water_air_HXTU1.b, coolingPipeDS2.a) 
  annotation(Line(origin={32,9},
points={{5.42372,-0.45281},{12.9919,-0.45281},{12.9919,-0.398486}},
color={0,170,255},
thickness=1));
  connect(expansionTankNports.portLiq[1], centrifugal_pump2.a) 
  annotation(Line(origin={47.3739,-93.2455},
points={{6.6559,3.3656},{6.6559,-5.65627},{-6.23555,-5.65627}},
color={0,170,255},
thickness=1));
  connect(water_air_HXTU1.a, valveFlowKvCooling.b) 
  annotation(Line(origin={4,8},
  points={{13.3616,0.412318},{-13.5412,0.412318},{-13.5412,0.438256}},
  color={0,170,255},
  thickness=1));
  connect(realExpression4.y, boundaryHeatFlow1.Q_flow_in) 
  annotation(Line(origin={112.977,-13.6811},
points={{-124.63,-32.3848},{-119.189,-32.3848},{-119.189,-44.6022}},
color={0,0,127}));
  connect(boundaryHeatFlow1.port[1], coolingPipeDS3.qa) 
  annotation(Line(origin={118.973,-85.9991},
points={{-125.1848,7.7158},{-125.1848,-1.75897},{-126.171,-1.75897}},
color={191,0,0},
thickness=1));
  connect(hysteresis.y, switch1.u2) 
  annotation(Line(origin={-121,-17},
points={{-15.4253,1.06115},{5.30291,1.06115},{5.30291,1.61533}},
color={255,0,255}));
  connect(realExpression6.y, switch1.u3) 
  annotation(Line(origin={-118,-42},
points={{-32.884,-38.534},{2.30291,-38.534},{2.30291,18.6153}},
color={0,0,127}));
  connect(realExpression5.y, switch1.u1) 
  annotation(Line(origin={-118,0},
points={{-34.3172,27.7438},{2.30291,27.7438},{2.30291,-7.38467}},
color={0,0,127}));
  connect(switch1.y, slewRateLimiter.u) 
  annotation(Line(origin={-87,-20},
points={{-5.69709,4.61533},{2.88757,4.61533},{2.88757,5.5242}},
color={0,0,127}));
  connect(slewRateLimiter.y, valveFlowKvCooling1.u) 
  annotation(Line(origin={-39,-18},
points={{-22.1124,3.5242},{-22.1124,6.5843},{20.5918,6.5843},{20.5918,4.9247}},
color={0,0,127}));
  connect(switch2.y, slewRateLimiter1.u) 
  annotation(Line(origin={-81,39},
points={{-9.17825,0.249689},{-0.259153,0.249689},{-0.259153,-1.46651}},
color={0,0,127}));
  connect(slewRateLimiter1.y, valveFlowKvCooling.u) 
  annotation(Line(origin={-37,28},
points={{-21.2592,9.53349},{17.3354,9.53349},{17.3354,-9.52397}},
color={0,0,127}));
  connect(hysteresis.y, switch2.u2) 
  annotation(Line(origin={-119,11},
points={{-17.4253,-26.9388},{-7.79762,-26.9388},{-7.79762,28.2497},{5.82175,28.2497}},
color={255,0,255}));
  connect(realExpression6.y, switch2.u1) 
  annotation(Line(origin={-116,-6},
points={{-34.884,-74.534},{-10.1856,-74.534},{-10.1856,53.2497},{2.82175,53.2497}},
color={0,0,127}));
  connect(realExpression5.y, switch2.u3) 
  annotation(Line(origin={-116,20},
points={{-36.3172,7.74381},{2.82175,7.74381},{2.82175,11.2497}},
color={0,0,127}));
  connect(pTSensorCoolant1.outPortT, fixedDelay.u) 
  annotation(Line(origin={-53,-50},
points={{24.1851,-36.8605},{24.1851,-7.9375},{-24.2053,-7.9375}},
color={0,0,127}));
  connect(fixedDelay.y, hysteresis.u) 
  annotation(Line(origin={-126,-38},
points={{25.7947,-19.9375},{-48.9464,-19.9375},{-48.9464,22.0612},{-33.4253,22.0612}},
color={0,0,127}));
  connect(rotationalInputSource1.u, realExpression2.y) 
  annotation(Line(origin={-9.1124,-124.628},
points={{23.05444,-0.491},{9.6668,-0.491},{9.6668,-1.52}},
color={0,0,127}));
  connect(coolingPipeDS1.b, centrifugal_pump2.a) 
  annotation(Line(origin={55,-60},
points={{11.0372,38.2874},{28.4758,38.2874},{28.4758,-38.9018},{-13.8617,-38.9018}},
color={0,170,255},
thickness=1));
  connect(coolingPipeDS2.b, centrifugal_pump2.a) 
  annotation(Line(origin={55,-45},
points={{10.02,53.6015},{27.7951,53.6015},{27.7951,-53.9018},{-13.8617,-53.9018}},
color={0,170,255},
thickness=1));
  connect(centrifugal_pump2.b, coolingPipeDS3.a) 
  annotation(Line(origin={12,-99},
  points={{9.00476,0.098226},{-9.23974,0.098226},{-9.23974,-0.0283065}},
  color={0,170,255},
  thickness=1));
  connect(coolingPipeDS3.b, pTSensorCoolant1.a) 
  annotation(Line(origin={-21,-99},
  points={{3.73214,-0.0283065},{-3.80482,-0.0283065},{-3.80482,0.701716}},
  color={0,170,255},
  thickness=1));
  connect(pTSensorCoolant1.b, branchPipeCoolingCV.a) 
  annotation(Line(origin={-47,-66},
  points={{2.06162,-32.2983},{-1.4463,-32.2983},{-1.4463,32.3816}},
  color={0,170,255},
  thickness=1));
  end MultiLoopHIL;