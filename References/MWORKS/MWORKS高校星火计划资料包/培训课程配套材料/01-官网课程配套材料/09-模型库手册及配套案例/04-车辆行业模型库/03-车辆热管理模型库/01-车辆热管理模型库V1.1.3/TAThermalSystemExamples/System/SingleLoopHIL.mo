model SingleLoopHIL "水回路单回路"
  parameter Modelica.SIunits.Temperature T_Amb = 303.15 "环境温度";
  parameter Real PumpSpd_rpm = 500"水泵转速设置（转/分钟）";
  parameter Real nPumpMax = 4000"水泵最高转速（转/分钟）";
  parameter Real nPumpMin = 1"水泵最低转速（转/分钟）";
  parameter Modelica.SIunits.Power Q_flow1 = 500 "发热量";
  parameter Modelica.SIunits.Power Q_flow2 = 500 "发热量";
  parameter Real Rev_Fan = 1000"风扇转速设置（转/分钟）";
  annotation (Diagram(coordinateSystem(extent={{-80,-170},{400,130}},
grid={2,2})),
    Icon(coordinateSystem(extent={{-100,-100},{100,100}},
grid={2,2}),graphics = {Bitmap(origin={0,1.7763568394002505e-15},
extent={{-100,-100},{100,100}},
fileName="modelica://TAThermalSystem/Resource/Icons/Example.svg")}),
    Documentation(link="modelica://TAThermalSystem/Resource/Doc/SingleLoopHIL.html"),
    experiment(Algorithm=Euler,StartTime=0,StopTime=200,Tolerance=0.0001,Interval=0.01,IntegratorStep=0.001,InlineIntegrator=false,InlineStepSize=false),
    Protection(access = Access.nonPackageDuplicate),__MWORKS(ContinueSimConfig(SaveContinueFile="false",SaveBeforeStop="false",NumberBeforeStop=1,FixedContinueInterval="false",ContinueIntervalLength=0.04,ContinueTimeVector),ResultViewerManager(resultViewers={
ResultViewer(name="1", executeTrigger=executeTrigger.SimulationStarted, commands={
CreatePlot(id=1, x_display_unit="s", legend_layout=7, left_title="[W]", fix_time_range_value=0, zoom_x=(0, 200), zoom_y_l=(-1200, 200)),
Plot(y=["water_air_HXTU1.hXSummary.Qdot_abTotal"], thicknesses=[2], colors=["4278190335"]),
CreatePlot(id=-1, x_display_unit="s", legend_layout=7, left_title="[kg/s]", fix_time_range_value=0, sub_plot=(2, 1), zoom_x=(0, 200), zoom_y_l=(0.05, 0.35)),
Plot(y=["centrifugal_pump2.m_flow"], thicknesses=[2], colors=["4278190335"]),
CreatePlot(id=-1, x_display_unit="s", legend_layout=7, fix_time_range_value=0, sub_plot=(3, 1), zoom_x=(0, 200), zoom_y_l=(29, 34)),
Plot(y=["pTSensorCoolant1.outPortT", "pTSensorCoolant.outPortT"], thicknesses=[2, 2], colors=["4278190335", "4294901760"])})
})));
  TAThermalSystem.HeatExchangers.CoolingRadiatorNTU.Water_Air_HXNTU water_air_HXTU1(
    ConsiderMass = false, Across1(displayUnit = "cm2"), Dhyd1(displayUnit = "mm"), cearea1
    (
      displayUnit = "m2") =
    0.1,
    ConsiderationFins_cd = false,
    etas2 = 0.8, ConsiderationFins_ab = true, fromDp = false,

    T1_a(start = T_Amb),
    T1_b(start = T_Amb),
    T2_in(start = T_Amb),
    T2_out(start = T_Amb),
    Twall(start = T_Amb),
    cearea2(displayUnit
       = "m2") =
    0.1,redeclare model Friction_ab = TYBase.Thermal.FluidHeatFlow.PressureLoss.HXPressureDrop.PressureDropRT) 
    annotation (Placement(transformation(origin={271.673,-22.9927},
extent={{-10,-10},{10,10}},
rotation=-90)));
  TAThermalSystem.Sources.Air.AirSink_pT airSink_pT2(T_sink = T_Amb, phi_sink = 0.4, redeclare package Medium = TYBase.Media_Extend.Air.MoistAir) 
    annotation (Placement(transformation(origin={216.294,-0.770618},
extent={{-10,-10},{10,10}})));
  TAThermalSystem.PumpAndFan.CentrifugalPump centrifugal_pump2(









    T_inlet(start



       = T_Amb),
    T_outlet(start



       = T_Amb),
    T_start = T_Amb
                   ) annotation (Placement(transformation(origin={163.757,-110.69},
extent={{10,-10},{-10,10}})));
  TAThermalSystem.Pipes.LiquidCoolingPipeHIL.CoolingPipeCR coolingPipeDS1(title="水管道", Dhyd=0.025, Aheat=0.1918, T0=T_Amb, L(displayUnit="mm")=0.46, redeclare model Friction = .TAThermalSystem.Utilities.PressureDrop.TableForZeta) annotation (Placement(transformation(origin={157.192,28.7504},
extent={{-10.0469,-10.0086},{10.011,10.0101}})),__MWORKS(BlockSystem(StateMachine)));
  TAThermalSystem.Sources.HeatTransfer.BoundaryHeatFlow boundaryHeatFlow1(





                                                          Q_flow = Q_flow1, n = 1,use_Qflow_in=true
                                                                                                   ) 
    annotation (Placement(transformation(origin={157.145,60.723},
extent={{10,-10},{-10,10}},
rotation=90)),__MWORKS(BlockSystem(StateMachine)));
  TAThermalSystem.Sources.Air.AirSink_pT airSink_pT1(








                                     T_sink = T_Amb, phi_sink = 0.4, redeclare package Medium = TYBase.Media_Extend.Air.MoistAir
                                                                                                                                ) 
    annotation (Placement(transformation(origin={216.425,-43.072},
extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(StateMachine)));
  TAThermalSystem.PumpAndFan.Fan2Table fan2Table 
    annotation (Placement(transformation(origin={240.256,-43.072},
extent={{-10,-10},{10,10}})));
  TAThermalSystem.Sources.Mechanics.RotationalInputSource rotationalInputSource 
    annotation (Placement(transformation(origin={224.256,-70.1556},
extent={{-8,-6},{10,6}})));
  Modelica.Blocks.Nonlinear.Limiter limiter(











                                            uMax=nPumpMax,uMin=nPumpMin
                                                                       ) 
    annotation (Placement(transformation(origin={106.269,-140.572},
extent={{-10,-10},{10,10}})));
  TAThermalSystem.Sensors.Coolant.PTSensorCoolant pTSensorCoolant 
    annotation (Placement(transformation(origin={195.87,28.8216},
extent={{-10,-10},{10,10}})));
  TAThermalSystem.Sensors.Coolant.PTSensorCoolant pTSensorCoolant1 
    annotation (Placement(transformation(origin={119.568,27.6094},
extent={{-10,-10},{10,10}})));
  TAThermalSystem.Pipes.LiquidCoolingPipeHIL.CoolingPipeCR coolingPipeDS2(title="水管道", Dhyd=0.025, Aheat=0.1918, T0=T_Amb, L(displayUnit="mm")=0.46, redeclare model Friction = .TAThermalSystem.Utilities.PressureDrop.TableForZeta) annotation (Placement(transformation(origin={231.163,28.7504},
extent={{-10.0469,-10.0086},{10.011,10.0101}})),__MWORKS(BlockSystem(StateMachine)));
  TAThermalSystem.Sources.HeatTransfer.BoundaryHeatFlow boundaryHeatFlow2(











                                                          Q_flow = Q_flow2, n = 1,use_Qflow_in=true
                                                                                 ) 
    annotation (Placement(transformation(origin={231.116,60.723},
extent={{10,-10},{-10,10}},
rotation=90)),__MWORKS(BlockSystem(StateMachine)));
  TAThermalSystem.Sources.Mechanics.RotationalInputSource rotationalInputSource1 
    annotation (Placement(transformation(origin={149.039,-140.572},
extent={{-8,-6},{10,6}})),__MWORKS(BlockSystem(StateMachine)));
  Modelica.Blocks.Sources.RealExpression realExpression(y=Rev_Fan) 
    annotation (Placement(transformation(origin={188.612,-70.1782},
extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Sources.RealExpression realExpression1(y=Q_flow1) 
    annotation (Placement(transformation(origin={134.28,84.8481},
extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Sources.RealExpression realExpression2(y=PumpSpd_rpm) 
    annotation (Placement(transformation(origin={61.9175,-140.892},
extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Sources.RealExpression realExpression3(y=Q_flow2) 
    annotation (Placement(transformation(origin={204.418,85.783},
extent={{-10,-10},{10,10}})));
  TAThermalSystem.Reservoirs.ExpansionTank_NPorts expansionTankNports(closedTank=true) 
    annotation (Placement(transformation(origin={192.733,-93.9811},
extent={{-10,-10},{10,10}})));

  equation
  connect(airSink_pT2.port_a, water_air_HXTU1.d) 
    annotation (Line(origin={291.705,-45.8727},
points={{-65.4113,45.1021},{-26.1882,45.1021},{-26.1882,32.8432}},
color={0,232,232},
thickness=1));
  connect(boundaryHeatFlow1.port[1], coolingPipeDS1.qa) 
  annotation(Line(origin={157.145,45.7418},
points={{0,4.98129},{0,-5.86726},{0.0468544,-5.86726}},
color={191,0,0},
thickness=1));
  connect(airSink_pT1.port_a, fan2Table.a) 
  annotation(Line(origin={222.256,-43.1556},
points={{4.16876,0.0836},{8,0.0836}},
color={0,232,232},
thickness=1));
  connect(fan2Table.b, water_air_HXTU1.c) 
  annotation(Line(origin={260.534,-9.95629},
points={{-10.2784,-33.1157},{5.10165,-33.1157},{5.10165,-23.1483}},
color={0,232,232},
thickness=1));
  connect(rotationalInputSource.flange, fan2Table.shaft) 
  annotation(Line(origin={237.256,-61.1556},
points={{-3,-9},{3,-9},{3,8.08357}},
color={0,0,0}));
  connect(coolingPipeDS1.b, pTSensorCoolant.a) 
  annotation(Line(origin={185.174,28.5207},
points={{-17.9117,0.0835741},{0.685503,0.0835741},{0.685503,0.263123}},
color={0,170,255},
thickness=1));
  connect(boundaryHeatFlow2.port[1], coolingPipeDS2.qa) 
  annotation(Line(origin={231.116,45.7418},
points={{0,4.98129},{0,-5.86726},{0.0468544,-5.86726}},
color={191,0,0},
thickness=1));
  connect(pTSensorCoolant.b, coolingPipeDS2.a) 
  annotation(Line(origin={214.174,28.5207},
points={{-8.18094,0.263123},{7.03121,0.263123},{7.03121,0.0835741}},
color={0,170,255},
thickness=1));
  connect(rotationalInputSource1.flange, centrifugal_pump2.flange) 
  annotation(Line(origin={146.757,-130.572},
points={{12.2816,-10},{17,-10},{17,9.88154}},
color={0,0,0}));
  connect(limiter.y, rotationalInputSource1.u) 
  annotation(Line(origin={129.269,-140.572},
points={{-12,0},{12.7698,0}},
color={0,0,127}));
  connect(realExpression2.y, limiter.u) 
  annotation(Line(origin={83.2693,-140.572},
points={{-10.3518,-0.32},{11,-0.32},{11,0}},
color={0,0,127}));
  connect(realExpression.y, rotationalInputSource.u) 
  annotation(Line(origin={209.256,-70.1556},
points={{-9.6434,-0.0226},{8,-0.0226},{8,0}},
color={0,0,127}));
  connect(realExpression1.y, boundaryHeatFlow1.Q_flow_in) 
  annotation(Line(origin={151.174,77.5207},
points={{-5.894,7.3274},{5.971,7.3274},{5.971,-6.79763}},
color={0,0,127}));
  connect(realExpression3.y, boundaryHeatFlow2.Q_flow_in) 
  annotation(Line(origin={223.174,78.5207},
points={{-7.756,7.2623},{7.942,7.2623},{7.942,-7.79763}},
color={0,0,127}));
  connect(expansionTankNports.portLiq[1], centrifugal_pump2.a) 
  annotation(Line(origin={182.757,-107.572},
points={{9.976,3.5907},{9.976,-3.15623},{-8.98988,-3.15623}},
color={0,170,255},
thickness=1));
  connect(coolingPipeDS2.b, water_air_HXTU1.a) 
  annotation(Line(origin={259,8},
  points={{-17.7671,20.6042},{18.6751,20.6042},{18.6751,-20.9785}},
  color={0,170,255},
  thickness=1));
  connect(water_air_HXTU1.b, centrifugal_pump2.a) 
  annotation(Line(origin={226,-72},
  points={{51.5402,38.9594},{51.5402,-38.728},{-52.2324,-38.728}},
  color={0,170,255},
  thickness=1));
  connect(pTSensorCoolant1.b, coolingPipeDS1.a) 
  annotation(Line(origin={138,28},
  points={{-8.30807,-0.428406},{9.23421,-0.428406},{9.23421,0.604274}},
  color={0,170,255},
  thickness=1));
  connect(centrifugal_pump2.b, pTSensorCoolant1.a) 
  annotation(Line(origin={132,-42},
points={{21.6336,-68.7278},{-50.4512,-68.7278},{-50.4512,69.5716},{-22.4416,69.5716}},
color={0,170,255},
thickness=1));
  end SingleLoopHIL;