model HeatPumpCircuit "热泵回路"
  extends TAThermalSystem.Utilities.Icons.BasicIcons.Example;
  parameter Modelica.SIunits.Temperature T_Amb = 273.15 "环境温度";
  parameter Modelica.SIunits.Temperature T_InCond = 283.15 "内冷进口温度";
  parameter Real ComprSpd_rpm=2000 "压缩机转速（转/分钟）";
  Real[4] xin = {compressorR134a.hout, condenser.refrigerant.h_out, evaporator.refrigerant.h_in, compressorR134a.hin} "横坐标比焓变量,单位kJ/kg" annotation(Dialog(group = "可视化变量序列,用于ph相图动态显示"));
  Real[4] yin = {compressorR134a.pout, condenser.refrigerant.b.p, evaporator.refrigerant.a.p, compressorR134a.pin} "纵坐标对应压力变量,单位Pa" annotation(Dialog(group = "可视化变量序列,用于ph相图动态显示"));
   parameter Modelica.Units.SI.Temperature TempSC(displayUnit = "K") = 5 "过冷度设置";

  TAThermalSystem.Pipes.TwoPhasePipe.PipeAdiabatic pipeAdiabatic(RefrigerantTemperature=35,RefrigerantMass=0.105584,RefrigerantMassDistribution=2,init(initType = TYBase.Utilities.Types.Init.Initial_MT),redeclare package Medium = TYMedia.Helmholtz.R134a) 
    annotation(Placement(transformation(origin = {-80.0, 64.0},
    extent = {{-10.0, -10.0}, {10.0, 10.0}},
    rotation = 90.0)));
  TAThermalSystem.Compressor.Compressor compressorR134a(redeclare package Medium = TYMedia.Helmholtz.R134a) annotation(Placement(transformation(origin = {-80.0, 24.0},
    extent = {{-10.0, -10.0}, {10.0, 10.0}},
    rotation = 90.0)));

  TAThermalSystem.HeatExchangers.Condenser condenser(title = "内置冷凝器", CF_RefrigerantSideHeatTransfer = 10, CF_AirSideHeatTransfer = 10,RefrigerantTemperature=35,RefrigerantMass=0.145959,redeclare package Medium = TYMedia.Helmholtz.R134a) annotation(Placement(transformation(origin={79.2042,42.5919},
extent={{-10,-10},{10,10}},
rotation=270)));

  TAThermalSystem.Pipes.TwoPhasePipe.PipeAdiabatic pipeAdiabatic1(RefrigerantTemperature=35,RefrigerantMass=0.105584,RefrigerantMassDistribution=2,init(initType = TYBase.Utilities.Types.Init.Initial_MT),redeclare package Medium = TYMedia.Helmholtz.R134a) 
    annotation(Placement(transformation(origin = {-80.0, -15.999999999999998},
    extent = {{-10.0, -10.0}, {10.0, 10.0}},
    rotation = 90.0)));
  TAThermalSystem.HeatExchangers.Evaporator evaporator(
    CF_RefrigerantSideHeatTransfer = 10,
    title = "外置蒸发器", CF_AirSideHeatTransfer = 10,RefrigerantTemperature=35,RefrigerantMass=0.0912242,redeclare record HXGeo = TYBase.Thermal.FluidHeatFlow.Components.BasicComponents.Records.HXRecords.HXGeoVertical,redeclare package Medium = TYMedia.Helmholtz.R134a) annotation(Placement(transformation(origin = {0.0, -76.0},
    extent = {{10.0, 10.0}, {-10.0, -10.0}})));

  TAThermalSystem.Sources.Air.AirSource_mT airSource(T=T_InCond) 
    annotation(Placement(transformation(origin={99.2042,22.5919},
extent={{10,-10},{-10,10}})));
  TAThermalSystem.Sources.Air.AirSink_pT airSink(T_sink = 308.15) 
    annotation(Placement(transformation(origin={99.2042,62.5919},
extent={{10,-10},{-10,10}})));
  TAThermalSystem.Valves.RefrigerantValve.ValveFlowKv simpleEXV(T0=308.15, redeclare package Medium = TYMedia.Helmholtz.R134a) 
    annotation(Placement(transformation(origin={46,-70},
extent={{10,-10},{-10,10}})));
  TAThermalSystem.Sources.Air.AirSource_mT airSource1(T = T_Amb) 
    annotation(Placement(transformation(origin = {-24.00000000000002, -90.0},
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TAThermalSystem.Sources.Air.AirSink_pT airSink1(T_sink = 308.15) 
    annotation(Placement(transformation(origin = {26.000000000000004, -90.0},
    extent = {{10.0, -10.0}, {-10.0, 10.0}})));



  Modelica.Mechanics.Rotational.Sources.Speed speed 
    annotation(Placement(transformation(origin = {-43.999999999999986, 24.0},
    extent = {{10.0, -10.0}, {-10.0, 10.0}})));
  Modelica.Blocks.Sources.RealExpression realExpression1(y = ComprSpd_rpm) 
    annotation(Placement(transformation(origin = {42.0, 24.0},
    extent = {{10.0, -10.0}, {-10.0, 10.0}})));
  TAThermalSystem.Reservoirs.Reservoir_fillinglevel reservoir( RefrigerantTemperature=35, RefrigerantMass=0.051518, RefrigerantMassDistribution=1, H=0.2,redeclare package Medium = TYMedia.Helmholtz.R134a) 
    annotation(Placement(transformation(origin={-65.7588,-70.0705},
extent={{10,-10},{-10,10}})));
  annotation(Protection(access=Access.nonPackageDuplicate),
    experiment(Algorithm=Dassl,NumberOfIntervals=500,StartTime=0,StopTime=120,Tolerance=0.0001),
    __MWorks(ContinueSimConfig(SaveContinueFile="false",SaveBeforeStop="false",NumberBeforeStop=1,FixedContinueInterval="false",ContinueIntervalLength=0.24,ContinueTimeVector),ResultViewerManager(resultViewers={
ResultViewer(name="1", executeTrigger=executeTrigger.SimulationStarted, commands={
CreatePlot(id=1, x_display_unit="s", legend_layout=7, left_title="[W]", fix_time_range_value=0, zoom_x=(0, 0.48), zoom_y_l=(-100000, 600000)),
Plot(y=["evaporator.hXSummary.Qdot_refTotal"], thicknesses=[2], colors=["4278190335"]),
CreatePlot(id=-1, x_display_unit="s", legend_layout=7, right_title="[W]", fix_time_range_value=0, sub_plot=(1, 2), zoom_x=(0, 0.48), zoom_y_l=(0, 1), zoom_y_r=(-200000, 1e+06)),
Plot(y=["condenser.hXSummary.Qdot_refTotal"], thicknesses=[2], verticalAxes=[-1], colors=["4278190335"]),
CreatePlot(id=-1, x_display_unit="s", legend_layout=7, left_title="[W]", fix_time_range_value=0, sub_plot=(2, 2), zoom_x=(0, 0.48), zoom_y_l=(100, 400)),
Plot(y=["compressorR134a.summary.p_refrigerant"], thicknesses=[2], colors=["4278190335"]),
CreatePlot(id=-1, x_display_unit="s", legend_layout=7, left_title="[kg/s]", fix_time_range_value=0, sub_plot=(2, 1), zoom_x=(0, 0.48), zoom_y_l=(0, 0.5)),
Plot(y=["compressorR134a.summary.mdot"], thicknesses=[2], colors=["4278190335"])})
})),
    Documentation(link="modelica://TAThermalSystem/Resource/Doc/HeatPumpCircuit.html"),Diagram(coordinateSystem(extent={{-100,-100},{100,100}},
grid={2,2})));


  TAThermalSystem.Utilities.DynamicDisplay.ph_R134a ph_R134a1(x = xin, y = yin) 
    annotation(Placement(transformation(origin = {114.00000000000003, -99.0},
    extent = {{-1.4210854715202004e-14, 0.0}, {199.0, 199.0}})));
  Modelica.Blocks.Math.Gain gain1(k = Modelica.Constants.pi / 30) 
    annotation(Placement(transformation(origin = {-7.999999999999998, 24.000000000000007},
    extent = {{10.0, -10.0}, {-10.0, 10.0}})));
  TAThermalSystem.Sensors.Refrigerant.SuperCoolingSensor superCoolingSensor(redeclare package Medium = TYMedia.Helmholtz.R134a) 
    annotation (Placement(transformation(origin={73.1187,-5.67789},
extent={{10,-10},{-10,10}},
rotation=90)));
  Modelica.Blocks.Continuous.LimPID PID(k=0.02,Ti=10,yMax=0.5,yMin=0.001,initType=Modelica.Blocks.Types.Init.InitialOutput,controllerType=Modelica.Blocks.Types.SimpleController.PI,y_start=0.05) 
    annotation (Placement(transformation(origin={46.2586,-27.8263},
extent={{-10,-10},{10,10}},
rotation=-90)));
  Modelica.Blocks.Sources.RealExpression realExpression(y=TempSC) 
    annotation (Placement(transformation(origin={4.62861,-27.9784},
extent={{-10,-10},{10,10}})));
  equation
  connect(compressorR134a.b, pipeAdiabatic.a) 
    annotation(Line(origin = {-80.00000000000001, 43.99999999999999},
    points = {{0.0, -10.0}, {0.0, 10.0}},
    color = {0, 128, 0},
    thickness = 1.0));
  connect(pipeAdiabatic1.b, compressorR134a.a) 
    annotation(Line(origin = {-80.00000000000001, 3.9999999999999964},
    points = {{0.0, -10.0}, {0.0, 10.0}},
    color = {0, 128, 0},
    thickness = 1.0));
  connect(compressorR134a.flange, speed.flange) 
    annotation(Line(origin = {-62.000000000000014, 23.999999999999993},
    points = {{-8.0, 0.0}, {8.0, 0.0}},
    color = {0, 0, 0}));

  connect(evaporator.b1, reservoir.port_a) 
    annotation(Line(origin={-33,-70},
points={{23,0},{-22.7588,0},{-22.7588,-0.170506}},
color={0,128,0},
thickness=1));
  connect(reservoir.b, pipeAdiabatic1.a) 
    annotation(Line(origin={-71,-48},
points={{-4.75881,-22.1705},{-9,-22.1705},{-9,22}},
color={0,128,0},
thickness=1));
  connect(airSource1.port_b, evaporator.air_in) 
    annotation(Line(origin={-12,-86},
points={{-2,-4},{-2,4},{2,4}},
color={0,232,232},
thickness=1));
  connect(evaporator.air_out, airSink1.port_a) 
    annotation(Line(origin = {13.0, -86.0},
    points = {{-3.0, 4.0}, {-3.0, -4.0}, {3.0, -4.0}},
    color = {0, 232, 232},
    thickness = 1.0));
  connect(airSink.port_a, condenser.air_out) 
    annotation(Line(origin={87.2042,57.5919},
points={{2,5},{-2,5},{-2,-5}},
color={0,232,232},
thickness=1));
  connect(condenser.air_in, airSource.port_b) 
    annotation(Line(origin={87.2042,27.5919},
points={{-2,5},{-2,-5},{2,-5}},
color={0,232,232},
thickness=1));
  connect(speed.w_ref, gain1.y) 
    annotation(Line(origin = {-26.0, 24.0},
    points = {{-6.000000000000014, -7.105427357601002e-15}, {7.0, 7.105427357601002e-15}},
    color = {0, 0, 127}));
  connect(gain1.u, realExpression1.y) 
    annotation(Line(origin = {17.0, 24.0},
    points = {{-12.999999999999998, 7.105427357601002e-15}, {13.999999999999986, -7.105427357601002e-15}},
    color = {0, 0, 127}));
  connect(pipeAdiabatic.b, condenser.a1) 
  annotation(Line(origin={-2,48},
points={{-78,26},{-78,42.713},{75.2042,42.713},{75.2042,4.59193}},
color={0,128,0},
thickness=1));
  connect(simpleEXV.b, evaporator.a1) 
  annotation(Line(origin={23,-70},
points={{13,0},{-13,0}},
color={0,128,0},
thickness=1));
  connect(superCoolingSensor.outPort, PID.u_s) 
  annotation(Line(origin={63.5576,-16.6896},
points={{-1.8389,11.0117},{-17.299,11.0117},{-17.299,0.8633}},
color={0,0,127}));
  connect(realExpression.y, PID.u_m) 
  annotation(Line(origin={38.0786,-43.8549},
points={{-22.45,15.8765},{-3.82,15.8765},{-3.82,16.0286}},
color={0,0,127}));
  connect(condenser.b1, superCoolingSensor.a) 
  annotation(Line(origin={73,18},
points={{0.2042,14.5919},{0.1187,-13.67789}},
color={0,128,0},
thickness=1));
  connect(superCoolingSensor.b, simpleEXV.a) 
  annotation(Line(origin={65,-43},
points={{8.1187,27.3221},{8.1187,-27},{-9,-27}},
color={0,128,0},
thickness=1));
  connect(PID.y, simpleEXV.u) 
  annotation(Line(origin={37,-53},
points={{9.2586,14.1737},{9.2586,-7},{9,-7}},
color={0,0,127}));
end HeatPumpCircuit;