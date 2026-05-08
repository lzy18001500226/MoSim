model HeatPumpCircuitR290 "R290热泵回路"
  extends TAThermalSystem.Utilities.Icons.BasicIcons.Example;
  parameter Modelica.SIunits.Temperature T_Amb = 273.15 "环境温度";
  parameter Modelica.SIunits.Temperature T_InCond = 283.15 "内冷进口温度";
  parameter Modelica.Units.SI.Temperature TempSC(displayUnit = "K") = 5 "过冷度设置";
  parameter Real ComprSpd_rpm= 4000 "压缩机转速（转/分钟）";
  Real[4] xin ={compressor.hout, condenser.refrigerant.h_out, evaporator.refrigerant.h_in, compressor.hin} "横坐标比焓变量,单位kJ/kg" annotation(Dialog(group = "可视化变量序列,用于ph相图动态显示"));
  Real[4] yin ={compressor.pout, condenser.refrigerant.b.p, evaporator.refrigerant.a.p, compressor.pin} "纵坐标对应压力变量,单位Pa" annotation(Dialog(group = "可视化变量序列,用于ph相图动态显示"));

  TAThermalSystem.Compressor.Compressor compressor(redeclare package Medium = TYMedia.Helmholtz.Propane) annotation(Placement(transformation(origin = {2.73367, 74.0905},
    extent = {{-10, -10}, {10, 10}})));

  TAThermalSystem.HeatExchangers.Condenser condenser(title = "内置冷凝器", CF_RefrigerantSideHeatTransfer = 10, CF_AirSideHeatTransfer = 10, redeclare package Medium = TYMedia.Helmholtz.Propane) annotation(Placement(transformation(origin = {97.7588, -12.0201},
    extent = {{-10, -10}, {10, 10}},
    rotation = 270)));

  TAThermalSystem.Pipes.TwoPhasePipe.PipeAdiabatic pipeAdiabatic1(redeclare package Medium = TYMedia.Helmholtz.Propane) 
    annotation(Placement(transformation(origin = {-37.2262, 74.613},
    extent = {{-10, -10}, {10, 10}})));
  TAThermalSystem.HeatExchangers.Evaporator evaporator(
    CF_RefrigerantSideHeatTransfer = 10,
    title = "外置蒸发器", CF_AirSideHeatTransfer = 10, redeclare record HXGeo = TYBase.Thermal.FluidHeatFlow.Components.BasicComponents.Records.HXRecords.HXGeoVertical, redeclare package Medium = TYMedia.Helmholtz.Propane) annotation(Placement(transformation(origin = {-90.0302, -24.1608},
    extent = {{10, 10}, {-10, -10}},
    rotation = -90)));

  TAThermalSystem.Pipes.TwoPhasePipe.PipeAdiabatic pipeAdiabatic2(redeclare package Medium = TYMedia.Helmholtz.Propane) 
    annotation(Placement(transformation(origin = {91.7588, 27.9799},
    extent = {{10, 10}, {-10, -10}},
    rotation = 90)));
  TAThermalSystem.Sources.Air.AirSource_mT airSource(T = T_InCond) 
    annotation(Placement(transformation(origin = {117.759, -32.0201},
    extent = {{10, -10}, {-10, 10}})));
  TAThermalSystem.Sources.Air.AirSink_pT airSink(T_sink = 273.15) 
    annotation(Placement(transformation(origin = {117.759, 7.9799},
    extent = {{10, -10}, {-10, 10}})));
  TAThermalSystem.Sources.Air.AirSource_mT airSource1(T = T_Amb,m=1) 
    annotation(Placement(transformation(origin = {-135.417, 0.110553},
    extent = {{-10, -10}, {10, 10}})));
  TAThermalSystem.Sources.Air.AirSink_pT airSink1(T_sink = 273.15) 
    annotation(Placement(transformation(origin = {-133.256, -51.6683},
    extent = {{-10, -10}, {10, 10}})));



  Modelica.Mechanics.Rotational.Sources.Speed speed 
    annotation(Placement(transformation(origin={16,46},
extent={{10,-10},{-10,10}})));
  Modelica.Blocks.Sources.RealExpression realExpression1(y = ComprSpd_rpm) 
    annotation(Placement(transformation(origin={78.77593,45.2508},
extent={{10,-10},{-10,10}})));
  annotation(Protection(access=Access.nonPackageDuplicate),
    experiment(Algorithm=Dassl,NumberOfIntervals=1200,StartTime=0,StopTime=1200,Tolerance=0.0001,InlineIntegrator=false,InlineStepSize=false),
    __MWorks(ContinueSimConfig(SaveContinueFile="false",SaveBeforeStop="false",NumberBeforeStop=1,FixedContinueInterval="false",ContinueIntervalLength=3,ContinueTimeVector),ResultViewerManager(resultViewers={
ResultViewer(name="1", executeTrigger=executeTrigger.SimulationStarted, commands={
CreatePlot(id=1, x_display_unit="s", legend_layout=7, left_title="[W]", fix_time_range_value=0, zoom_x=(0, 1200), zoom_y_l=(-10000, 40000)),
Plot(y=["evaporator.hXSummary.Qdot_airTotal"], thicknesses=[2], colors=["4278190335"]),
CreatePlot(id=-1, x_display_unit="s", legend_layout=7, right_title="[W]", fix_time_range_value=0, sub_plot=(1, 2), zoom_x=(0, 1200), zoom_y_l=(0, 1), zoom_y_r=(2000, 6000)),
Plot(y=["condenser.hXSummary.Qdot_airTotal"], thicknesses=[2], verticalAxes=[-1], colors=["4278190335"]),
CreatePlot(id=-1, x_display_unit="s", legend_layout=7, left_title="[bar]", fix_time_range_value=0, sub_plot=(2, 2), zoom_x=(0, 1200), zoom_y_l=(-5, 30)),
Plot(y=["valve.a.p", "valve.b.p"], thicknesses=[2, 2], colors=["4278190335", "4294901760"]),
CreatePlot(id=-1, x_display_unit="s", legend_layout=7, left_title="[kg/s]", fix_time_range_value=0, sub_plot=(2, 1), zoom_x=(0, 1200), zoom_y_l=(0, 0.1)),
Plot(y=["compressor.mdot"], thicknesses=[2], colors=["4278190335"])})
})),
    Documentation(link="modelica://TAThermalSystem/Resource/Doc/HeatPumpCircuitR290.html"), Diagram(coordinateSystem(extent = {{-100, -100}, {100, 100}},
    grid = {2, 2})));


  Modelica.Blocks.Math.Gain gain1(k = Modelica.Constants.pi / 30) 
    annotation(Placement(transformation(origin={44.13373,45.6254},
extent={{10,-10},{-10,10}})));
  TAThermalSystem.Reservoirs.Reservoir_fillinglevel reservoir1(RefrigerantTemperature = 35, RefrigerantMass = 0.051518, RefrigerantMassDistribution = 1, H = 0.2, redeclare package Medium = TYMedia.Helmholtz.Propane, H_Out = 0.15,FillingLevel0=0.5) 
    annotation(Placement(transformation(origin = {-67.4707, 74.122},
    extent = {{-10, -10}, {10, 10}})));
  TAThermalSystem.Utilities.DynamicDisplay.ph_R290 ph_R290_1(x = xin, y = yin) 
    annotation(Placement(transformation(origin = {147.552, -103.728},
    extent = {{0, 0}, {259.364, 196.887}})));
  TAThermalSystem.Sensors.Refrigerant.SuperCoolingSensor superCoolingSensor(redeclare package Medium = TYMedia.Helmholtz.Propane) 
    annotation(Placement(transformation(origin={59.9517,-68.2787},
extent={{10,10},{-10,-10}})));
  TAThermalSystem.Pipes.TwoPhasePipe.PipeAdiabatic pipeAdiabatic3(redeclare package Medium = TYMedia.Helmholtz.Propane) 
    annotation(Placement(transformation(origin = {8.49126, -68.7652},
    extent = {{10, 10}, {-10, -10}})));
  Modelica.Blocks.Sources.Constant SetPoint_SC(k = TempSC)
    "过冷度设置值" annotation(Placement(transformation(origin = {77.771, -111.197},
    extent = {{10, -10}, {-10, 10}})));
  TAThermalSystem.Valves.RefrigerantValve.ValveFlowKv valve(
  redeclare package Medium = TYMedia.Helmholtz.Propane,
    mdot(start = 0.1, fixed = false),





    Kv_curve = {{0.0, 0.001}, {0.01, 0.001}, {0.1, 0.1}, {0.2, 0.3}, {0.4, 0.5}, {0.6, 0.6}, {0.8, 0.7}, {1.0, 1}, {1.1, 1}}, use_yd0 = false) 
    annotation(Placement(transformation(origin = {-34.9334, -70.5284},
    extent = {{17.2553, 15.0595}, {-17.2553, -15.0595}})));
  Modelica.Blocks.Nonlinear.DeadZone deadZone1(uMax = 0.1) 
    annotation(Placement(transformation(origin = {10.8623, -105.348},
    extent = {{10, -10}, {-10, 10}})));
  Modelica.Blocks.Math.Add add1(k2 = -1) 
    annotation(Placement(transformation(origin = {42.5702, -105.513},
    extent = {{10, -10}, {-10, 10}})));
  TYBase.Blocks.PIDsimple PID4(     controllerType = Modelica.Blocks.Types.SimpleController.PI,yMin=0.04,y_start=0.1,k=0.1,Ti=1) annotation(Placement(transformation(origin = {-17.1839, -105.3959},
    extent = {{10, -10}, {-10, 10}})));
equation
  connect(pipeAdiabatic1.b, compressor.a) 
    annotation(Line(origin = {-80, 4},
    points = {{52.7738, 70.613}, {72.7337, 70.613}, {72.7337, 70.0905}},
    color = {0, 128, 0},
    thickness = 1));
  connect(pipeAdiabatic2.b, condenser.a1) 
    annotation(Line(origin = {92.7588, -42.0201},
    points = {{-1, 60}, {-1, 40}},
    color = {0, 128, 0},
    thickness = 1));
  connect(compressor.flange, speed.flange) 
    annotation(Line(origin={-62,24},
points={{64.73367,40.0905},{64.73367,22},{68,22}},
color={0,0,0}));

  connect(airSource1.port_b, evaporator.air_in) 
    annotation(Line(origin = {-48, -82},
    points = {{-77.4171, 82.1106}, {-48.0302, 82.1106}, {-48.0302, 67.8392}},
    color = {0, 232, 232},
    thickness = 1));
  connect(evaporator.air_out, airSink1.port_a) 
    annotation(Line(origin = {-23, -82},
    points = {{-73.0302, 47.8392}, {-73.0302, 30.3317}, {-100.256, 30.3317}},
    color = {0, 232, 232},
    thickness = 1));
  connect(airSink.port_a, condenser.air_out) 
    annotation(Line(origin = {105.759, 2.9799},
    points = {{2, 5}, {-2, 5}, {-2, -5}},
    color = {0, 232, 232},
    thickness = 1));
  connect(condenser.air_in, airSource.port_b) 
    annotation(Line(origin = {105.759, -27.0201},
    points = {{-2, 5}, {-2, -5}, {2, -5}},
    color = {0, 232, 232},
    thickness = 1));
  connect(speed.w_ref, gain1.y) 
    annotation(Line(origin={-6.08027,46},
points={{34.08027,0},{39.214,0},{39.214,-0.3746}},
color={0,0,127}));
  connect(gain1.u, realExpression1.y) 
    annotation(Line(origin={36.91973,46},
points={{19.214,-0.3746},{30.8562,-0.3746},{30.8562,-0.7492}},
color={0,0,127}));
  connect(compressor.b, pipeAdiabatic2.a) 
    annotation(Line(origin = {50, 56},
    points = {{-37.2663, 18.0905}, {41.7588, 18.0905}, {41.7588, -18.0201}},
    color = {0, 128, 0},
    thickness = 1));
  connect(reservoir1.b, pipeAdiabatic1.a) 
    annotation(Line(origin = {-55, 74},
    points = {{-2.47073, 0.02199}, {7.7738, 0.02199}, {7.7738, 0.613}},
    color = {0, 128, 0},
    thickness = 1));
  connect(reservoir1.port_a, evaporator.b1) 
    annotation(Line(origin = {-84, 30},
    points = {{6.52927, 44.022}, {-0.0302, 44.022}, {-0.0302, -44.1608}},
    color = {0, 128, 0},
    thickness = 1));
  connect(condenser.b1, superCoolingSensor.a) 
    annotation(Line(origin={75,-42},
points={{16.7588,19.9799},{16.7588,-26.2787},{-5.04834,-26.2787}},
color={0,128,0},
thickness=1));
  connect(superCoolingSensor.b, pipeAdiabatic3.a) 
    annotation(Line(origin={28,-67},
points={{21.9517,-1.27868},{-9.50874,-1.27868},{-9.50874,-1.7652}},
color={0,128,0},
thickness=1));
  connect(SetPoint_SC.y, add1.u2) 
    annotation(Line(origin = {-133.638, -118.402},
    points = {{200.409, 7.20514}, {188.208, 7.20514}, {188.208, 6.88936}},
    color = {0, 0, 127}));
  connect(add1.y, deadZone1.u) 
    annotation(Line(origin = {-95.6383, -100.402},
    points = {{127.208, -5.11064}, {118.501, -5.11064}, {118.501, -4.94648}},
    color = {0, 0, 127}));
  connect(deadZone1.y, PID4.u) 
    annotation(Line(origin = {-65.6383, -100.402},
    points = {{65.5006, -4.94648}, {60.4544, -4.94648}, {60.4544, -4.9939}},
    color = {0, 0, 127}));
  connect(PID4.y, valve.u) 
    annotation(Line(origin = {-45.2318, -141.575},
    points = {{17.0685, 36.2203}, {10.2984, 36.2203}, {10.2984, 55.9871}},
    color = {0, 0, 127}));
  connect(pipeAdiabatic3.b, valve.a) 
    annotation(Line(origin = {-10, -70},
    points = {{8.49126, 1.2348}, {-7.6781, 1.2348}, {-7.6781, -0.5284}},
    color = {0, 128, 0},
    thickness = 1));
  connect(superCoolingSensor.outPort, add1.u1) 
    annotation(Line(origin={-38,-74},
points={{97.9517,-5.67868},{97.9517,-25.513},{92.5702,-25.513}},
color={0,0,127}));
  connect(valve.b, evaporator.a1) 
    annotation(Line(origin = {-68, -52},
    points = {{15.8113, -18.5284}, {-16.0302, -18.5284}, {-16.0302, 17.8392}},
    color = {0, 128, 0},
    thickness = 1));
end HeatPumpCircuitR290;