model CabinHeatExchangeNetwork "乘员舱换热网络案例"
  parameter Modelica.Units.SI.Temperature T_Amb = 303.15 "环境温度";
  annotation(Documentation(link="modelica://TAThermalSystem/Resource/Doc/CabinHeatExchangeNetwork.html"
),
    Protection(access=Access.nonPackageDuplicate),
    experiment(Algorithm = Dassl, NumberOfIntervals = 500, StartTime = 0, StopTime = 120, Tolerance = 0.0001),Diagram(coordinateSystem(extent={{-100,-100},{100,100}},
grid={2,2})),__MWORKS(ResultViewerManager(resultViewers={
ResultViewer(name="1", executeTrigger=executeTrigger.SimulationStarted, commands={
CreatePlot(id=1, x_display_unit="s", legend_layout=7, left_title="[degC]", fix_time_range_value=0, zoom_x=(0, 120), zoom_y_l=(10, 35)),
Plot(y=["cabinVolume.summary.T"], thicknesses=[2], colors=["4278190335"]),
CreatePlot(id=-1, x_display_unit="s", legend_layout=7, left_title="[W]", fix_time_range_value=0, sub_plot=(1, 2), zoom_x=(0, 120), zoom_y_l=(0, 3000)),
Plot(y=["cabinVolume.summary.Q_flow"], thicknesses=[2], colors=["4278190335"]),
CreatePlot(id=-1, x_display_unit="s", legend_layout=7, left_title="[kg/s]", fix_time_range_value=0, sub_plot=(2, 1), zoom_x=(0, 120), zoom_y_l=(0, 0.7)),
Plot(y=["hVACCircuitApplication.compressorR134a.summary.mdot"], thicknesses=[2], colors=["4278190335"]),
CreatePlot(id=-1, x_display_unit="s", legend_layout=7, left_title="[W]", curve_vernier=True, fix_time_range_value=0, sub_plot=(2, 2), zoom_x=(0, 120), zoom_y_l=(50, 450)),
Plot(y=["hVACCircuitApplication.compressorR134a.summary.p_refrigerant"], thicknesses=[2], colors=["4278190335"])})
})));


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
    CF_RefrigerantSideHeatTransfer
    = 5,RefrigerantTemperature=30,RefrigerantMass=0.0721431,CF_AirSideHeatTransfer=5), T_Amb = T_Amb,yMax=0.2,reservoir(RefrigerantTemperature=30,RefrigerantMass=0.0234549,RefrigerantMassDistribution=1),lumpedPipeR134a(RefrigerantTemperature=30,RefrigerantMass=0.0834989),lumpedPipeR134a1(RefrigerantTemperature=30,RefrigerantMass=0.0834989),lumpedPipeR134a2(RefrigerantTemperature=30,RefrigerantMass=0.0834989),condenser1(RefrigerantTemperature=30,RefrigerantMass=0.0384763),SuperHeatSetPoint=5,h0_low=350e3,Ti=10) 
    annotation(Placement(transformation(origin = {-10.0, 32.0},
    extent = {{-20.0, -20.0}, {20.0, 20.0}})));

  Modelica.Blocks.Sources.RealExpression compressorSpeed(y = 2000)
    "压缩机转速rpm" annotation(Placement(transformation(origin = {64.0, 40.0},
    extent = {{10.0, -10.0}, {-10.0, 10.0}})));
  TAThermalSystem.Heating.CabinHeatNetwork cabinVolume(n_Passenger = 5, T_ext = T_Amb, T_interior = T_Amb) annotation(Placement(transformation(origin = {-19.999999999999996, -38.0},
    extent = {{10.0, -10.0}, {-10.0, 10.0}})));
  TAThermalSystem.PumpAndFan.SimpleFan simpleFan(mdot_nom = 0.25, T_nom = T_Amb, T(start = T_Amb)) 
    annotation(Placement(transformation(origin={-49.5563,12.2713},
extent={{-10,-10},{10,10}})));



  TAThermalSystem.Utilities.DynamicDisplay.Single_Display single_Display(
    variable = cabinVolume.cabinVolume.T - 273.15, blockname = "乘员舱温度/°C") annotation(Placement(transformation(origin = {45.0, -79.0},
    extent = {{-15.0, 3.0}, {21.0, 15.0}})));
  TAThermalSystem.Pipes.AirPass.AirSplit airSplit 
    annotation (Placement(transformation(origin={-47.9565,-38.3555},
extent={{10,10},{-10,-10}})));
  TAThermalSystem.Sources.Air.AirSink_pT airSink_pT(T_sink=T_Amb) 
    annotation (Placement(transformation(origin={-62.1795,-59.3019},
extent={{-10,-10},{10,10}})));






  extends TAThermalSystem.Utilities.Icons.BasicIcons.Example;
equation
  connect(hVACCircuitApplication.speed_in_rpm, compressorSpeed.y) 
    annotation(Line(origin = {32.0, 40.0},
    points = {{-22.0, 0.0}, {21.0, 0.0}},
    color = {0, 0, 127}));
  connect(airSink_pT.port_a, airSplit.b2) 
  annotation(Line(origin={-49.9675,-54.0855},
points={{-2.212,-5.2164},{2.011,-5.2164},{2.011,5.73}},
color={0,232,232},
thickness=1));
  connect(cabinVolume.a, hVACCircuitApplication.air_out1) 
  annotation(Line(origin={-4,-13},
points={{-5.8,-25},{55.6425,-25},{55.6425,25},{6,25}},
color={0,232,232},
thickness=1));
  connect(cabinVolume.b, airSplit.a) 
  annotation(Line(origin={-34,-38},
  points={{3.8,0},{-3.95645,0},{-3.95645,-0.355526}},
  color={0,232,232},
  thickness=1));
  connect(airSplit.b1, simpleFan.a) 
  annotation(Line(origin={-59,-13},
points={{1.04355,-25.3555},{-23.3431,-25.3555},{-23.3431,25.2713},{-0.556347,25.2713}},
color={0,232,232},
thickness=1));
  connect(simpleFan.b, hVACCircuitApplication.air_in1) 
  annotation(Line(origin={-31,12},
  points={{-8.55635,0.271271},{9,0.271271},{9,0}},
  color={0,232,232},
  thickness=1));
end CabinHeatExchangeNetwork;