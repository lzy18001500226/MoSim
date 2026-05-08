model CabinDemoSimple "简单乘员舱案例"
  extends TAThermalSystem.Utilities.Icons.BasicIcons.Example;
  annotation (Documentation(link="modelica://TAThermalSystem/Resource/Doc/CabinDemoSimple.html"),
    Protection(access=Access.nonPackageDuplicate),
    experiment(Algorithm = Dassl, NumberOfIntervals = 500, StartTime = 0, StopTime = 120, Tolerance = 0.0001),Diagram(coordinateSystem(extent={{-100,-100},{100,100}},
grid={2,2})),__MWORKS(ResultViewerManager(resultViewers={
ResultViewer(name="1", executeTrigger=executeTrigger.SimulationStarted, commands={
CreatePlot(id=1, x_display_unit="s", legend_layout=7, left_title="[degC]", curve_vernier=True, fix_time_range_value=0, zoom_x=(0, 120), zoom_y_l=(24, 36)),
Plot(y=["cabinVolume.summary.T"], thicknesses=[2], colors=["4278190335"]),
CreatePlot(id=-1, x_display_unit="s", legend_layout=7, right_title="[W]", curve_vernier=True, fix_time_range_value=0, sub_plot=(1, 2), zoom_x=(0, 120), zoom_y_l=(0, 1), zoom_y_r=(-1000, 6000)),
Plot(y=["cabinVolume.summary.Q_flow"], thicknesses=[2], verticalAxes=[-1], colors=["4278190335"]),
CreatePlot(id=-1, x_display_unit="s", legend_layout=7, left_title="[W]", curve_vernier=True, fix_time_range_value=0, sub_plot=(2, 2), zoom_x=(0, 120), zoom_y_l=(100, 800)),
Plot(y=["hVACCircuitApplication.compressorR134a.summary.p_refrigerant"], thicknesses=[2], colors=["4278190335"]),
CreatePlot(id=-1, x_display_unit="s", legend_layout=7, left_title="[kg/s]", curve_vernier=True, fix_time_range_value=0, sub_plot=(2, 1), zoom_x=(0, 120), zoom_y_l=(0, 0.7)),
Plot(y=["hVACCircuitApplication.compressorR134a.summary.mdot"], thicknesses=[2], colors=["4278190335"])})
})));
  parameter Modelica.Units.SI.Temperature T_Amb = 308.15 "环境温度";

  TAThermalSystem.Examples.Application.HVACCircuitApplication hVACCircuitApplication(compressorR134a(MaximumDisplacement(displayUnit = "ml") = 3.3e-5), reservoir(zeta = 30,RefrigerantTemperature=35,RefrigerantMass=0.051518,RefrigerantMassDistribution=1), T_Amb = T_Amb,  mdotAir_cond = 1, n_segAirCond = 2, n_segAirEvap = 2,k=0.05,yMax=0.2,evaporatorR134a(RefrigerantTemperature=35,RefrigerantMass=0.0678947),condenser(RefrigerantTemperature=35,RefrigerantMass=0.108631),lumpedPipeR134a(RefrigerantTemperature=35,RefrigerantMass=0.0785818),lumpedPipeR134a1(RefrigerantTemperature=35,RefrigerantMass=0.0785818),lumpedPipeR134a2(RefrigerantTemperature=35,RefrigerantMass=0.0785818),condenser1(RefrigerantTemperature=35,RefrigerantMass=0.0362105),Ti=25) annotation (Placement(transformation(origin = {-9.484872439813156, 32.0},
    extent = {{-20.0, -20.0}, {20.0, 20.0}})));

  Modelica.Blocks.Sources.RealExpression compressorSpeed(y = 3000)
    "压缩机转速rad/s" annotation (Placement(transformation(origin = {67.95883634369058, 39.861782498903935},
      extent = {{10.0, -10.0}, {-10.0, 10.0}})));
  TAThermalSystem.Heating.CabinVolume cabinVolume(Tm = T_Amb,
    n_Passenger = 4, V = 3, T_in(start = T_Amb), T_out(start = T_Amb)) annotation (Placement(transformation(origin={-23.198,-56},
extent={{10,-10},{-10,10}})));
  TAThermalSystem.Sources.HeatTransfer.FixedTemperature T_env(T = T_Amb, n = 1) 
    annotation (Placement(transformation(origin={-43.698,-20},
extent={{-10,-10},{10,10}})));
  TAThermalSystem.Utilities.DynamicDisplay.Single_Display single_Display(
    variable = cabinVolume.cabinVolume.T - 273.15, blockname = "乘员舱温度/°C") annotation (Placement(transformation(origin={45.802,-97},
extent={{-15,3},{21,15}})));
  TAThermalSystem.PumpAndFan.SimpleFan simpleFan(T_nom = T_Amb, T(start = T_Amb),use_paraInput=false) 
    annotation (Placement(transformation(origin={-52.2971,12},
extent={{-10,-10},{10,10}})));
  TAThermalSystem.Pipes.AirPass.AirResist airResist 
    annotation (Placement(transformation(origin={18.8171,-56},
extent={{10,-10},{-10,10}})));
  TAThermalSystem.Pipes.AirPass.AirSplit airSplit 
    annotation (Placement(transformation(origin={-58.8026,-56.9165},
extent={{10,10},{-10,-10}})));
  TAThermalSystem.Sources.Air.AirSink_pT airSink_pT(T_sink=T_Amb) 
    annotation (Placement(transformation(origin={-73.0256,-77.8629},
extent={{-10,-10},{10,10}})));

  //hVACCircuitApplication.condenser1.refrigerant.p[1] = hVACCircuitApplication.condenser1.refrigerant.p0[1];
  //hVACCircuitApplication.evaporatorR134a.refrigerant.p[1] = hVACCircuitApplication.evaporatorR134a.refrigerant.p0[1];
  //hVACCircuitApplication.evaporatorR134a.refrigerant.h[6] = hVACCircuitApplication.evaporatorR134a.refrigerant.h0[6];









initial equation
equation
  connect(compressorSpeed.y, hVACCircuitApplication.speed_in_rpm) 
    annotation (Line(origin = {34.0, 37.0},
      points = {{23.0, 3.0}, {-23.0, 3.0}},
      color = {0, 0, 127}));
  connect(T_env.port[1], cabinVolume.qa) 
  annotation(Line(origin={-185.198,53},
points={{151.5,-73},{162,-73},{162,-99}},
color={191,0,0},
thickness=1));
  connect(cabinVolume.a, airResist.b) 
  annotation(Line(origin={-1.69805,-56},
points={{-11.5,0},{10.515128,0}},
color={0,232,232},
thickness=1));
  connect(airSink_pT.port_a, airSplit.b2) 
  annotation(Line(origin={-60.8136,-72.6465},
points={{-2.212,-5.2164},{2.011,-5.2164},{2.011,5.73}},
color={0,232,232},
thickness=1));
  connect(simpleFan.b, hVACCircuitApplication.air_in1) 
  annotation(Line(origin={-32,12},
  points={{-10.2971,0},{10.5151,0}},
  color={0,232,232},
  thickness=1));
  connect(airSplit.a, cabinVolume.b) 
  annotation(Line(origin={-40.698,-56},
points={{-8.10456,-0.916457},{7.5,-0.916457},{7.5,0}},
color={0,232,232},
thickness=1));
  connect(airSplit.b1, simpleFan.a) 
  annotation(Line(origin={-76,-22},
points={{7.19739,-34.9165},{-7.43836,-34.9165},{-7.43836,34},{13.7029,34}},
color={0,232,232},
thickness=1));
  connect(hVACCircuitApplication.air_out1, airResist.a) 
  annotation(Line(origin={7,-22},
points={{-4.48487,34},{37.267,34},{37.267,-34},{21.8171,-34}},
color={0,232,232},
thickness=1));
  end CabinDemoSimple;