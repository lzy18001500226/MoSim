model CarCabinDemo "乘员舱优化案例"
  parameter Modelica.Units.SI.Temperature T_Amb = 303.15 "环境温度";
  annotation(Documentation(link="modelica://TAThermalSystem/Resource/Doc/CarbinDemo.html"),
    Protection(access=Access.nonPackageDuplicate),
    experiment(Algorithm = Dassl, NumberOfIntervals = 500, StartTime = 0, StopTime = 120, Tolerance = 0.0001),
    Diagram(coordinateSystem(extent={{-100,-100},{100,100}},
grid={2,2}),graphics = {Text(origin={-23.9474,-8.59613},
lineColor={0,0,0},
extent={{-10,-3},{10,3}},
textString="车速",
textStyle={TextStyle.Bold},
textColor={0,0,0})}),__MWORKS(ResultViewerManager(resultViewers={
ResultViewer(name="1", executeTrigger=executeTrigger.SimulationStarted, commands={
CreatePlot(id=1, x_display_unit="s", legend_layout=7, left_title="[degC]", curve_vernier=True, fix_time_range_value=0, zoom_x=(0, 120), zoom_y_l=(16, 32)),
Plot(y=["cabinVolume.summary.T"], thicknesses=[2], colors=["4278190335"]),
CreatePlot(id=-1, x_display_unit="s", legend_layout=7, right_title="[W]", curve_vernier=True, fix_time_range_value=0, sub_plot=(1, 2), zoom_x=(0, 120), zoom_y_l=(0, 1), zoom_y_r=(-100, 600)),
Plot(y=["cabinVolume.summary.Q_flow"], thicknesses=[2], verticalAxes=[-1], colors=["4278190335"]),
CreatePlot(id=-1, x_display_unit="s", legend_layout=13, left_title="[W]", curve_vernier=True, fix_time_range_value=0, sub_plot=(2, 2), zoom_x=(0, 120), zoom_y_l=(0, 200)),
Plot(y=["hVACCircuitApplication.compressorR134a.summary.p_refrigerant"], thicknesses=[2], colors=["4278190335"]),
CreatePlot(id=-1, x_display_unit="s", legend_layout=7, left_title="[kg/s]", curve_vernier=True, fix_time_range_value=0, sub_plot=(2, 1), zoom_x=(0, 120), zoom_y_l=(-0.1, 0.7)),
Plot(y=["hVACCircuitApplication.compressorR134a.summary.mdot"], thicknesses=[2], colors=["4278190335"])})
})));
  Modelica.Blocks.Sources.RealExpression compressorSpeed(y = 1000)
    "压缩机转速rad/s" annotation(Placement(transformation(origin={46.4938,47.5595},
extent={{10,-10},{-10,10}})));
  TAThermalSystem.Heating.OptimizedCabinVolume cabinVolume(
    T0 = T_Amb,
    n_Passenger = 5,
  redeclare package Medium = TYBase.Media_Extend.Air.MoistAir, Tset = T_Amb, T_ext = T_Amb) annotation(Placement(transformation(origin = {-19.999999999999993, -42.0},
    extent = {{10.0, -10.0}, {-10.0, 10.0}})));


  TAThermalSystem.PumpAndFan.SimpleFan simpleFan(mdot_nom = 0.05, T(start = T_Amb), T_nom = T_Amb) 
    annotation(Placement(transformation(origin={-60.3088,20},
extent={{-10,-10},{10,10}})));



  TAThermalSystem.Utilities.DynamicDisplay.Single_Display single_Display(
    variable = cabinVolume.cabinVolume.T - 273.15, blockname = "乘员舱温度/°C") annotation(Placement(transformation(origin = {45.0, -79.0},
    extent = {{-15.0, 3.0}, {21.0, 15.0}})));
  Modelica.Blocks.Sources.Constant const(k = 20) 
    annotation(Placement(transformation(origin={-47.6574,-12.5837},
extent={{-10,-10},{10,10}})));
  TAThermalSystem.Pipes.AirPass.AirResist hXAirResis(redeclare package Medium = TYBase.Media_Extend.Air.MoistAir) annotation(Placement(transformation(origin = {22, -42},
    extent = {{10, -10}, {-10, 10}})));
  TAThermalSystem.Examples.Application.HVACCircuitApplication hVACCircuitApplication(
    compressorR134a(EtaMec_spd
    = {{0, 0.6}, {1000, 0.6}, {2000, 0.6}, {3000, 0.6}, {4000, 0.6}, {5000, 0.6}},
    h0_out
    = 400000,
    h0_in
    = 400000,
    p0_out
    = 9.999999999999999e5,
    p0_in
    = 2e5,
    MaximumDisplacement
    (displayUnit
    = "ml") =
    3.3e-5),
    condenser(CF_RefrigerantSideHeatTransfer
    = 10,
    CF_AirSideHeatTransfer
    = 1,RefrigerantTemperature=30,RefrigerantMass=0.115429),
    evaporatorR134a(
    RefrigerantTemperature=30,RefrigerantMass=0.0721431), T_Amb = T_Amb,yMax=0.2,reservoir(RefrigerantTemperature=30,RefrigerantMass=0.0234549,RefrigerantMassDistribution=1),lumpedPipeR134a(RefrigerantTemperature=30,RefrigerantMass=0.0834989),lumpedPipeR134a1(RefrigerantTemperature=30,RefrigerantMass=0.0834989),lumpedPipeR134a2(RefrigerantTemperature=30,RefrigerantMass=0.0834989),condenser1(RefrigerantTemperature=30,RefrigerantMass=0.0384763),SuperHeatSetPoint=15,h0_low=350e3,Ti=10) 
    annotation(Placement(transformation(origin={-20,40},
extent={{-20,-20},{20,20}})));
  TAThermalSystem.Pipes.AirPass.AirSplit airSplit 
    annotation (Placement(transformation(origin={-54.5357,-42.517},
extent={{10,10},{-10,-10}})));
  TAThermalSystem.Sources.Air.AirSink_pT airSink_pT(T_sink=T_Amb) 
    annotation (Placement(transformation(origin={-68.7587,-63.4634},
extent={{-10,-10},{10,10}})));






  extends TAThermalSystem.Utilities.Icons.BasicIcons.Example;

equation
  connect(const.y, cabinVolume.airspeed) 
    annotation(Line(origin={-44,-23},
points={{7.34257,10.4163},{11.8351,10.4163},{11.8351,-12},{13,-12}},
color={0,0,127}));
  connect(hXAirResis.b, cabinVolume.a) 
    annotation(Line(origin = {1, -40},
    points = {{11, -2}, {-10.999999999999993, -2}},
    color = {0, 232, 232},
    thickness = 1));
  connect(compressorSpeed.y, hVACCircuitApplication.speed_in_rpm) 
  annotation(Line(origin={27,40},
points={{8.49378,7.5595},{-27,7.5595},{-27,8}},
color={0,0,127}));
  connect(airSink_pT.port_a, airSplit.b2) 
  annotation(Line(origin={-56.5467,-58.247},
points={{-2.212,-5.2164},{2.011,-5.2164},{2.011,5.73}},
color={0,232,232},
thickness=1));
  connect(airSplit.a, cabinVolume.b) 
  annotation(Line(origin={-37,-42},
  points={{-7.53567,-0.517003},{7,-0.517003},{7,0}},
  color={0,232,232},
  thickness=1));
  connect(airSplit.b1, simpleFan.a) 
  annotation(Line(origin={-67,-11},
points={{2.46433,-31.517},{-18.3431,-31.517},{-18.3431,31},{-3.30882,31}},
color={0,232,232},
thickness=1));
  connect(hVACCircuitApplication.air_in1, simpleFan.b) 
  annotation(Line(origin={-41,20},
  points={{9,0},{-9.30882,0}},
  color={0,232,232},
  thickness=1));
  connect(hVACCircuitApplication.air_out1, hXAirResis.a) 
  annotation(Line(origin={12,-11},
points={{-20,31},{33.0841,31},{33.0841,-31},{20,-31}},
color={0,232,232},
thickness=1));
  end CarCabinDemo;