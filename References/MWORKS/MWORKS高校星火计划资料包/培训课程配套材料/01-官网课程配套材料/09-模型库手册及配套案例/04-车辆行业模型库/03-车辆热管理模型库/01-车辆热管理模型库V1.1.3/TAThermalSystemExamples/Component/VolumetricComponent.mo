package VolumetricComponent "容积类组件"
  annotation(__MWORKS(version="2025a"));
  model AccumulatorDemo "集液器案例"
    annotation (Documentation(link="modelica://TAThermalSystem/Resource/Doc/AccumulatorDemo.html"),
      Protection(access=Access.nonPackageDuplicate),
      experiment(Algorithm = Dassl, NumberOfIntervals = 500, StartTime = 0, StopTime = 120, Tolerance = 0.0001),__MWORKS(ResultViewerManager(resultViewers={
  ResultViewer(name="1", executeTrigger=executeTrigger.SimulationFinished, commands={
  CreatePlot(id=1, x_display_unit="s", legend_layout=7, left_title="[1]", fix_time_range_value=0, zoom_x=(0, 120), zoom_y_l=(0.4, 1)),
  Plot(y=["reservoir.phaseSeparator.x_out", "reservoir.phaseSeparator.x_in"], colors=["4278190335", "4294901760"]),
  CreatePlot(id=-1, x_display_unit="s", legend_layout=7, left_title="[m]", fix_time_range_value=0, sub_plot=(2, 1), zoom_x=(0, 120), zoom_y_l=(0, 0.16)),
  Plot(y=["reservoir.phaseSeparator.liquidLevel"], colors=["4278190335"])})
  })));
    extends TAThermalSystem.Utilities.Icons.BasicIcons.Example;
    TAThermalSystem.Sources.Refrigerant.Sink_pT r134aSink 
      annotation (Placement(transformation(origin = {70.00000000000001, -0.09999999999999998},
        extent = {{10.0, -10.0}, {-10.0, 10.0}})));
    TAThermalSystem.Sources.Refrigerant.Source_mh r134aSource(h_source = 3e5) annotation (Placement(transformation(origin = {-70.0, -0.1000000000000002},
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));

    TAThermalSystem.Reservoirs.Reservoir reservoir(FromDp = false) 
      annotation (Placement(transformation(extent = {{-10.0, -10.0}, {10.0, 10.0}})));
    TAThermalSystem.Sources.HeatTransfer.FixedTemperature fixedTemperature(T = 278.15) 
      annotation (Placement(transformation(origin = {-30.0, 20.0},
        extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  equation
    connect(r134aSource.port_b, reservoir.port_a) 
      annotation (Line(origin = {-35.0, 0.0},
        points = {{-25.0, 0.0}, {25.0, 0.0}},
        color = {0, 128, 0},
        thickness = 1.0));
    connect(reservoir.b, r134aSink.port_a) 
      annotation (Line(origin = {35.0, 0.0},
        points = {{-25.0, 0.0}, {25.0, 0.0}},
        color = {0, 128, 0},
        thickness = 1.0));
    connect(reservoir.q, fixedTemperature.port) 
      annotation (Line(origin = {-10.0, 15.0},
        points = {{10.0, -5.0}, {10.0, 4.0}, {-10.0, 4.0}, {-10.0, 5.0}},
        color = {191, 0, 0},
        thickness = 1.0));
  end AccumulatorDemo;
  model AirDemo "空气案例"
    extends TAThermalSystem.Utilities.Icons.BasicIcons.Example;
    parameter Integer[:,:] flowScheme = {{1, 2}}
      "换热器中的冷媒流动通道流程,表示为侧面二维矩阵形式" 
      annotation (Evaluate = true, Dialog(group = "流动设计"), editText = false);
    parameter Integer[n_pass] flattubes = {5, 5} "针对管路中的所用流路，对其中每个流程所用的扁管数量分布" 
      annotation (Evaluate = true, Dialog(group = "流动设计"), editText = false);
    parameter Integer n_pass(min = 1) = size(flowScheme, 1) * size(flowScheme, 2) "换热器中流程总数量" 
      annotation (Evaluate = true, Dialog(group = "流动设计"));

    TAThermalSystem.Pipes.AirPass.HXAir hXAir(geoHX = geoHX,
      init(T0 = 308.15),
      final n_seg = 1) 


      annotation (Placement(transformation(extent = {{-10.0, -10.0}, {10.0, 10.0}})));
    TAThermalSystem.Sources.Air.AirSource_mT airSource_mT(T = 263.15) 
      annotation (Placement(transformation(origin = {-60.0, 0.0},
        extent = {{-10.0, -10.0}, {10.0, 10.0}})));
    TAThermalSystem.Sources.Air.AirSink_pT airSink_pT 
      annotation (Placement(transformation(origin = {60.0, 0.0},
        extent = {{10.0, -10.0}, {-10.0, 10.0}})));
    TYBase.Thermal.HeatTransfer.Components.Walls.DynamicWallNoRes dynamicWallNoRes(n = geoHX.n_pass) 
      annotation (Placement(transformation(origin = {0.0, 30.0},
        extent = {{-10.0, -10.0}, {10.0, 10.0}})));
    TAThermalSystem.Sources.HeatTransfer.BoundaryHeatFlow boundaryHeatFlow(n = geoHX.n_pass) 
      annotation (Placement(transformation(origin = {-30.0, 60.0},
        extent = {{-10.0, -10.0}, {10.0, 10.0}})));
    TYBase.Thermal.FluidHeatFlow.Components.BasicComponents.Records.HXRecords.HXGeoHorizontal geoHX(flowScheme = flowScheme, flattubes = flattubes) "换热器几何数据实例化" annotation (choicesAllMatching, Placement(transformation(origin = {40.0, 60.0},
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
    annotation (Protection(access=Access.nonPackageDuplicate),
      Documentation(link="modelica://TAThermalSystem/Resource/Doc/AirDemo.html"),__MWORKS(ResultViewerManager(resultViewers={
  ResultViewer(name="1", executeTrigger=executeTrigger.SimulationFinished, commands={
  CreatePlot(id=1, x_display_unit="s", legend_layout=7, left_title="[bar]", fix_time_range_value=0, zoom_x=(0, 10), zoom_y_l=(8.5226e-05, 8.5226e-05)),
  Plot(y=["hXAir.ploss_f.dp"], colors=["4278190335"])})
  })));
  equation
    connect(airSource_mT.port_b, hXAir.a) 
      annotation (Line(origin = {-30.0, 0.0},
        points = {{-20.0, 0.0}, {20.0, 0.0}},
        color = {0, 232, 232},
        thickness = 1.0));
    connect(hXAir.b, airSink_pT.port_a) 
      annotation (Line(origin = {30.0, 0.0},
        points = {{-20.0, 0.0}, {20.0, 0.0}},
        color = {0, 232, 232},
        thickness = 1.0));
    connect(boundaryHeatFlow.port, dynamicWallNoRes.qa) 
      annotation (Line(origin = {-10.0, 50.0},
        points = {{-10.0, 10.0}, {10.0, 10.0}, {10.0, -10.0}},
        color = {191, 0, 0},
        thickness = 1.0));
    connect(dynamicWallNoRes.qb, hXAir.q) 
      annotation (Line(origin = {0.0, 15.0},
        points = {{0.0, 5.0}, {0.0, -5.0}},
        color = {191, 0, 0},
        thickness = 1.0));
  end AirDemo;
  model ExpansionTankDemo "膨胀水壶案例"
    parameter Real Rev = 1000 "水泵转速";
    parameter Modelica.Units.SI.Temperature T_Amb = 288.15 "环境温度";
    annotation (Icon(coordinateSystem(extent = {{-100.0, -100.0}, {100.0, 100.0}},
      grid = {2.0, 2.0}), graphics = {Bitmap(origin = {0.0, 0.0},
      extent = {{-100.0, -100.0}, {100.0, 100.0}},
      fileName = "modelica://TAThermalSystem/Resource/Icons/Example.svg")}),
      Documentation(link="modelica://TAThermalSystem/Resource/Doc/ExpansionTankDemo.html",info="<html><p>
<br>
</p>
</html>"    ),
      Protection(access=Access.nonPackageDuplicate),__MWORKS(ResultViewerManager(resultViewers={
  ResultViewer(name="1", executeTrigger=executeTrigger.SimulationFinished, commands={
  CreatePlot(id=1, x_display_unit="s", legend_layout=7, left_title="[bar]", fix_time_range_value=0, zoom_x=(0, 10), zoom_y_l=(0.5, 3.5)),
  Plot(y=["expansion_tank1.b.p", "expansion_tank1.a.p"], colors=["4278190335", "4294901760"]),
  CreatePlot(id=-1, x_display_unit="s", legend_layout=7, left_title="[m]", fix_time_range_value=0, sub_plot=(2, 1), zoom_x=(0, 10), zoom_y_l=(0.49998, 0.50014)),
  Plot(y=["expansion_tank1.tank1.H"], colors=["4278190335"])})
  })));
    TAThermalSystem.Reservoirs.ExpansionTank expansion_tank1(T_Amb = T_Amb) 
      annotation (Placement(transformation(origin = {-4.0, 50.000000000000014},
        extent = {{10.0, -10.0}, {-10.0, 10.0}})));
    Modelica.Blocks.Sources.RealExpression realExpression3(y = Rev * Modelica.Constants.pi / 30) 
      annotation (Placement(transformation(origin = {-62.09708737864074, -35.35922330097087},
        extent = {{-10.0, -10.0}, {10.0, 10.0}})));
    Modelica.Mechanics.Rotational.Sources.Speed speed2 
      annotation (Placement(transformation(origin = {-28.097087378640765, -35.35922330097087},
        extent = {{-10.0, -10.0}, {10.0, 10.0}})));
    TAThermalSystem.PumpAndFan.CentrifugalPump centrifugal_pump1(redeclare package Medium = TYBase.Media_Extend.GW50, T_start = T_Amb,
      pout_start = 3e5) annotation (Placement(transformation(origin={-4,-0.91476},
  extent={{10,-10},{-10,10}})));
    TAThermalSystem.Pipes.LiquidCoolingPipe.CoolingPipe coolingPipe1(p0 = 3e5, T0 = T_Amb) 
      annotation (Placement(transformation(origin = {-51.9362, -1.0078000000000031},
        extent = {{10.0997, -8.821720000000001}, {-10.0638, 9.007800000000001}})));
    TAThermalSystem.Pipes.LiquidCoolingPipe.CoolingPipe coolingPipe2(T0 = T_Amb) 
      annotation (Placement(transformation(origin = {43.900299999999994, -1.0078000000000031},
        extent = {{10.0997, -8.821720000000001}, {-10.0638, 9.007800000000001}})));
  equation
    connect(realExpression3.y, speed2.w_ref) 
      annotation (Line(origin = {-48.09708737864074, -35.359223300970854},
        points = {{-3.0, 0.0}, {8.0, 0.0}},
        color = {0, 0, 127}));
    connect(centrifugal_pump1.flange, speed2.flange) 
      annotation (Line(origin={-14,-23},
  points={{10,12.0852},{10,-12.3592},{-4.09709,-12.3592}},
  color={0,0,0}));
    connect(centrifugal_pump1.b, coolingPipe1.a) 
      annotation (Line(origin={-36,9},
  points={{21.8766,-9.95253},{-5.92608,-10.0456}},
  color={0,170,255},
  thickness=1));
    connect(coolingPipe1.b, expansion_tank1.a) 
      annotation (Line(origin = {-44.0, 35.0},
        points = {{-18.0, -36.0}, {-30.0, -36.0}, {-30.0, 15.0}, {30.0, 15.0}},
        color = {0, 170, 255},
        thickness = 1.0));
    connect(expansion_tank1.b, coolingPipe2.a) 
      annotation (Line(origin = {38.0, 30.0},
        points = {{-32.0, 20.0}, {16.0, 20.0}, {16.0, -31.0}},
        color = {0, 170, 255},
        thickness = 1.0));
    connect(centrifugal_pump1.a, coolingPipe2.b) 
      annotation (Line(origin={17,-1},
  points={{-10.9899,0.047466},{16.7769,-0.045574}},
  color={0,170,255},
  thickness=1));
  end ExpansionTankDemo;
  model VolumeElement "容积管件"
    parameter Modelica.SIunits.Pressure p_in =2e5 "输入压力";
    parameter Modelica.SIunits.Pressure p_out = 100000 "输出压力";
    TAThermalSystem.Sources.Coolant.Coolant_tank Coolant_pT1(p(displayUnit = "bar") = p_out, title = "水进口") 
      annotation (Placement(transformation(origin = {77.8000438286717, -2.2288205372205834},
        extent = {{10.0, -10.0}, {-10.0, 10.0}})));
    TAThermalSystem.Pipes.LiquidCoolingPipe.CoolingPipeC volumePipe(p0(displayUnit="bar")=1.8e5, steady=true) 
      annotation (Placement(transformation(origin = {1.3173624847637306, -2.3443388415381157},
        extent = {{-10.0, -8.914760000000001}, {10.0, 8.914760000000001}})));
    TAThermalSystem.Sources.Coolant.Coolant_mT Coolant_mT(title="水出口", mflow=0.1) 
      annotation (Placement(transformation(origin={-75.1653,-2.47515},
  extent={{-10,-10},{10,10}})));
    TAThermalSystem.Pipes.LiquidCoolingPipe.CoolingPipe coolingPipe 
      annotation (Placement(transformation(origin={-36.906,-2.43738},
  extent={{-10.0997,-8.82172},{10.0638,9.0078}})));
    TAThermalSystem.Pipes.LiquidCoolingPipe.CoolingPipe coolingPipe1 
      annotation (Placement(transformation(origin={39.5767,-2.32186},
  extent={{-10.0997,-8.82172},{10.0638,9.0078}})));
    annotation (Icon(coordinateSystem(extent={{-100.0, -100.0}, {100.0, 100.0}}, grid={2.0, 2.0}), graphics={Bitmap(origin = {0.0, 0.0}, extent = {{-100.0, -100.0}, {100.0, 100.0}}, fileName = "modelica://TAThermalSystem/Resource/Icons/Example.svg")}), Protection(access=Access.nonPackageDuplicate), Documentation(link="modelica://TAThermalSystem/Resource/Doc/VolumeElement.html"), Diagram(coordinateSystem(extent={{-100, -100}, {100, 100}}, grid={2, 2})),__MWORKS(ResultViewerManager(resultViewers={
  ResultViewer(name="1", executeTrigger=executeTrigger.SimulationFinished, commands={
  CreatePlot(id=1, x_display_unit="s", legend_layout=7, fix_time_range_value=0, zoom_x=(0, 10), zoom_y_l=(-0.2, 1.2)),
  Plot(y=["volumePipe.a.p", "volumePipe.a.m_flow", "volumePipe.b.p", "volumePipe.b.m_flow"], colors=["4278190335", "4294901760", "4278222848", "4294902015"])})
  })));
  equation
    connect(volumePipe.a, coolingPipe.b) 
    annotation(Line(origin={-18,-2},
    points={{9.40622,-0.475153},{-8.78259,-0.475153}},
    color={0,170,255},
    thickness=1));
    connect(coolingPipe.a, Coolant_mT.port_b) 
    annotation(Line(origin={-56,-2},
  points={{9.08388,-0.475154},{-9.16526,-0.475154}},
  color={0,170,255},
  thickness=1));
    connect(volumePipe.b, coolingPipe1.a) 
    annotation(Line(origin={20,-2},
    points={{-8.62348,-0.475153},{9.56654,-0.475153},{9.56654,-0.359635}},
    color={0,170,255},
    thickness=1));
    connect(coolingPipe1.b, Coolant_pT1.port_a) 
    annotation(Line(origin={64,-2},
    points={{-14.2999,-0.359635},{-14.2999,-0.475153},{13.8,-0.475153},{13.8,-0.228821}},
    color={0,170,255},
    thickness=1));
    end VolumeElement;
  model ReceiverDemo "储液箱案例"
    annotation (Documentation(link="modelica://TAThermalSystem/Resource/Doc/ReservoirDemo.html"
  ), Protection(access=Access.nonPackageDuplicate), experiment(Algorithm=Dassl, NumberOfIntervals=500, StartTime=0, StopTime=120, Tolerance=0.0001), Diagram(coordinateSystem(extent={{-100, -100}, {100, 100}}, grid={2, 2})),__MWORKS(ResultViewerManager(resultViewers={
  ResultViewer(name="1", executeTrigger=executeTrigger.SimulationFinished, commands={
  CreatePlot(id=1, x_display_unit="s", legend_layout=7, left_title_type=2, bottom_title_type=2, right_title_type=2, fix_time_range_value=0, zoom_x=(0, 120), zoom_y_l=(0.38, 0.52)),
  Plot(y=["reservoir.phaseSeparator.x_out", "reservoir.phaseSeparator.x_in"], colors=["4278190335", "4294901760"]),
  CreatePlot(id=-1, x_display_unit="s", legend_layout=7, left_title="[m]", fix_time_range_value=0, sub_plot=(2, 1), zoom_x=(0, 120), zoom_y_l=(0.019, 0.025)),
  Plot(y=["reservoir.phaseSeparator.liquidLevel"], colors=["4278190335"])})
  })));
    extends TAThermalSystem.Utilities.Icons.BasicIcons.Example;
    TAThermalSystem.Sources.Refrigerant.Sink_pT r134aSink(redeclare package Medium = TYMedia.Helmholtz.R134a) 
      annotation (Placement(transformation(origin = {70.00000000000001, -0.09999999999999998},
        extent = {{10.0, -10.0}, {-10.0, 10.0}})));
    TAThermalSystem.Reservoirs.Reservoir_fillinglevel reservoir(redeclare package Medium = TYMedia.Helmholtz.R134a, FromDp=false, H_Out=0.02) 
      annotation (Placement(transformation(extent = {{-10.0, -10.0}, {10.0, 10.0}})));

    TAThermalSystem.Pipes.TwoPhasePipe.SimplePipe simplePipe1(init(initType=TYBase.Utilities.Types.Init.Initial_ph, M0=0.003), redeclare package Medium = TYMedia.Helmholtz.R134a) 

      annotation (Placement(transformation(origin = {-35.00000000000001, -0.10000000000000142},
        extent = {{-10.0, -10.0}, {10.0, 10.0}})));



    TAThermalSystem.Pipes.TwoPhasePipe.SimplePipe simplePipe2(init(initType=TYBase.Utilities.Types.Init.Initial_ph, M0=0.003), redeclare package Medium = TYMedia.Helmholtz.R134a) 

      annotation (Placement(transformation(origin = {35.000000000000014, -0.09999999999999787},
        extent = {{-10.0, -10.0}, {10.0, 10.0}})));
    TAThermalSystem.Sources.Refrigerant.Source_mh r134aSource(h_source = 3e5,redeclare package Medium = TYMedia.Helmholtz.R134a) annotation (Placement(transformation(origin = {-70.0, -0.1000000000000002},
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
    equation
    connect(reservoir.b, simplePipe2.a) 
      annotation (Line(origin = {51.0, 0.0},
        points = {{-41.0, 0.0}, {-26.0, 0.0}},
        color = {0, 128, 0},
        thickness = 1.0));
    connect(simplePipe1.b, reservoir.port_a) 
      annotation (Line(origin = {-18.0, 0.0},
        points = {{-7.000000000000007, -0.10000000000000142}, {8.0, -0.1}},
        color = {0, 128, 0},
        thickness = 1.0));
    connect(simplePipe2.b, r134aSink.port_a) 
      annotation (Line(origin = {53.0, 0.0},
        points = {{-7.999999999999986, -0.09999999999999787}, {7.000000000000014, -0.09999999999999998}},
        color = {0, 128, 0},
        thickness = 1.0));
    connect(r134aSource.port_b, simplePipe1.a) 
    annotation(Line(origin={-52,0},
    points={{-8,-0.1000000000000002},{6.999999999999993,-0.10000000000000142}},
    color={0,128,0},
    thickness=1));
  end ReceiverDemo;
  model IdealSeparator "分离器案例"
    extends TAThermalSystem.Utilities.Icons.BasicIcons.Example;
    TAThermalSystem.Reservoirs.Base.IdealSeparator idealSeparator(V(displayUnit = "l")) 
      annotation (Placement(transformation(origin={-116,66},
  extent={{-10,-10},{10,10}})));
    annotation (experiment(Algorithm = Dassl, NumberOfIntervals = 500, StartTime = 0, StopTime = 10, Tolerance = 0.0001),
      Protection(access=Access.nonPackageDuplicate),Diagram(coordinateSystem(extent={{-100,-100},{100,100}},
  grid={2,2})),Documentation(link="modelica://TAThermalSystem/Resource/Doc/IdealSeparator.html"),__MWORKS(ResultViewerManager(resultViewers={
  ResultViewer(name="1", executeTrigger=executeTrigger.SimulationFinished, commands={
  CreatePlot(id=1, x_display_unit="s", legend_layout=7, left_title="[1]", fix_time_range_value=0, zoom_x=(0, 10), zoom_y_l=(-0.2, 1.2)),
  Plot(y=["idealSeparator.summary.q_Liquid", "idealSeparator.summary.q_Gas"], colors=["4278190335", "4294901760"]),
  CreatePlot(id=-1, x_display_unit="s", legend_layout=7, fix_time_range_value=0, sub_plot=(2, 1), zoom_x=(0, 10), zoom_y_l=(0.4, 1.1)),
  Plot(y=["idealSeparator.summary.fillingLevel"], colors=["4278190335"])})
  })));
    TAThermalSystem.Reservoirs.Base.IdealSeparator idealSeparator1(V(displayUnit = "l")) 
      annotation (Placement(transformation(origin={-116,-30},
  extent={{-10,-10},{10,10}})));
    TAThermalSystem.Sources.Refrigerant.Sink_ph boundary3 
      annotation (Placement(transformation(origin={-152.8188528541496,-26},
  extent={{10,-10},{-10,10}})));
    TAThermalSystem.Sources.Refrigerant.Source_mh source_mh(use_param_input=false,h_source=300000) 
      annotation (Placement(transformation(origin={-152.8188528541496,70},
  extent={{-10,-10},{10,10}})));
    TAThermalSystem.Sources.Refrigerant.Sink_ph boundary1(p0=7.999999999999999e5) 
      annotation (Placement(transformation(origin={-52,-26},
  extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(StateMachine)));
    TAThermalSystem.Sources.Refrigerant.Sink_ph boundary2(p0=8.199999999999999e5) 
      annotation (Placement(transformation(origin={-52,-74},
  extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(StateMachine)));
    TAThermalSystem.Sources.Refrigerant.Sink_ph boundary4(p0=4.999999999999999e5) 
      annotation (Placement(transformation(origin={-64,70},
  extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(StateMachine)));
    TAThermalSystem.Sources.Refrigerant.Sink_ph boundary5(p0=6e5) 
      annotation (Placement(transformation(origin={-54,24},
  extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(StateMachine)));
    TAThermalSystem.Valves.RefrigerantValve.SimpleOrifice simpleOrifice(title=" ", steadyState = true) 
      annotation (Placement(transformation(origin={-90,70},
  extent={{-10,-10},{10,10}})));
    TAThermalSystem.Valves.RefrigerantValve.SimpleOrifice simpleOrifice1(title=" ", steadyState = true) 
      annotation (Placement(transformation(origin={-90,24},
  extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(StateMachine)));
    TAThermalSystem.Valves.RefrigerantValve.SimpleOrifice simpleOrifice2(title=" ", steadyState = true) 
      annotation (Placement(transformation(origin={-88,-26},
  extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(StateMachine)));
    TAThermalSystem.Valves.RefrigerantValve.SimpleOrifice simpleOrifice3(title=" ", steadyState = true) 
      annotation (Placement(transformation(origin={-88,-74},
  extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(StateMachine)));
    TAThermalSystem.Reservoirs.Base.IdealSeparator idealSeparator2(V(displayUnit = "l")) 
      annotation (Placement(transformation(origin={22,66},
  extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(StateMachine)));
    TAThermalSystem.Sources.Refrigerant.Source_mh source_mh1(use_param_input=false,h_source=300000) 
      annotation (Placement(transformation(origin={-14.818852854149611,70},
  extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(StateMachine)));
    TAThermalSystem.Sources.Refrigerant.Sink_ph boundary7(p0=6e5) 
      annotation (Placement(transformation(origin={84,24},
  extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(StateMachine)));
    TAThermalSystem.Valves.RefrigerantValve.SimpleOrifice simpleOrifice5(title=" ", steadyState = true) 
      annotation (Placement(transformation(origin={48,24},
  extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(StateMachine)));
    TAThermalSystem.Reservoirs.Base.IdealSeparator idealSeparator3(V(displayUnit = "l")) 
      annotation (Placement(transformation(origin={22,-30},
  extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(StateMachine)));
    TAThermalSystem.Sources.Refrigerant.Sink_ph boundary6 
      annotation (Placement(transformation(origin={-14.818852854149611,-26},
  extent={{10,-10},{-10,10}})),__MWORKS(BlockSystem(StateMachine)));
    TAThermalSystem.Sources.Refrigerant.Sink_ph boundary8(p0=7.999999999999999e5) 
      annotation (Placement(transformation(origin={86,-26},
  extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(StateMachine)));
    TAThermalSystem.Valves.RefrigerantValve.SimpleOrifice simpleOrifice4(title=" ", steadyState = true) 
      annotation (Placement(transformation(origin={50,-26},
  extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(StateMachine)));
    equation
    connect(idealSeparator1.portInlet, boundary3.a) 
    annotation(Line(origin={-151,-26},
  points={{24.96312849162011,0},{8.181147145850389,0}},
  color={0,128,0},
  thickness=1));
    connect(source_mh.port_b, idealSeparator.portInlet) 
    annotation(Line(origin={-134,70},
  points={{-8.818852854149611,0},{7.963128491620111,0}},
  color={0,128,0},
  thickness=1));
    connect(idealSeparator.portGas, simpleOrifice.port_a) 
    annotation(Line(origin={-103,70},
  points={{-3.1383240223463673,0},{3,0}},
  color={0,128,0},
  thickness=1));
    connect(simpleOrifice.port_b, boundary4.a) 
    annotation(Line(origin={-77,70},
  points={{-3,0},{3,0}},
  color={0,128,0},
  thickness=1));
    connect(boundary5.a, simpleOrifice1.port_b) 
    annotation(Line(origin={-72,24},
  points={{8,0},{-8,0}},
  color={0,128,0},
  thickness=1));
    connect(simpleOrifice1.port_a, idealSeparator.portLiquid) 
    annotation(Line(origin={-108,40},
  points={{8,-16},{-8,-16},{-8,16}},
  color={0,128,0},
  thickness=1));
    connect(idealSeparator1.portGas, simpleOrifice2.port_a) 
    annotation(Line(origin={-93,-26},
  points={{-13.138324022346367,0},{-5,0}},
  color={0,128,0},
  thickness=1));
    connect(simpleOrifice2.port_b, boundary1.a) 
    annotation(Line(origin={-45,-26},
  points={{-33,0},{-17,0}},
  color={0,128,0},
  thickness=1));
    connect(boundary2.a, simpleOrifice3.port_b) 
    annotation(Line(origin={-70,-74},
  points={{8,0},{-8,0}},
  color={0,128,0},
  thickness=1));
    connect(simpleOrifice3.port_a, idealSeparator1.portLiquid) 
    annotation(Line(origin={-107,-57},
  points={{9,-17},{-9,-17},{-9,17}},
  color={0,128,0},
  thickness=1));
    connect(source_mh1.port_b, idealSeparator2.portInlet) 
    annotation(Line(origin={4,70},
  points={{-8.818852854149611,0},{7.963128491620111,0}},
  color={0,128,0},
  thickness=1));
    connect(boundary7.a, simpleOrifice5.port_b) 
    annotation(Line(origin={66,24},
  points={{8,0},{-8,0}},
  color={0,128,0},
  thickness=1));
    connect(simpleOrifice5.port_a, idealSeparator2.portLiquid) 
    annotation(Line(origin={30,40},
  points={{8,-16},{-8,-16},{-8,16}},
  color={0,128,0},
  thickness=1));
    connect(idealSeparator3.portInlet, boundary6.a) 
    annotation(Line(origin={-13,-26},
  points={{24.96312849162011,0},{8.181147145850389,0}},
  color={0,128,0},
  thickness=1));
    connect(idealSeparator3.portGas, simpleOrifice4.port_a) 
    annotation(Line(origin={45,-26},
  points={{-13.138324022346367,0},{-5,0}},
  color={0,128,0},
  thickness=1));
    connect(simpleOrifice4.port_b, boundary8.a) 
    annotation(Line(origin={93,-26},
  points={{-33,0},{-17,0}},
  color={0,128,0},
  thickness=1));
    end IdealSeparator;
  model CabinComponentTest "乘员舱组件测例"
    extends TAThermalSystem.Utilities.Icons.BasicIcons.Example;
    TAThermalSystem.Sources.Air.AirSource_mT airSource_mT(T = 274.15,m=0.2) 
      annotation (Placement(transformation(origin = {-60.0, 0.0},
        extent = {{-10.0, -10.0}, {10.0, 10.0}})));
    TAThermalSystem.Sources.Air.AirSink_pT airSink_pT 
      annotation (Placement(transformation(origin = {60.0, 0.0},
        extent = {{10.0, -10.0}, {-10.0, 10.0}})));
    TAThermalSystem.Heating.CabinHeatNetwork cabinHeatNetwork(table={{0, 0}, {1, 0}}) 
      annotation (Placement(transformation(origin = {0.000000, 0.000000}, extent = {{-10.000000, -10.000000}, {10.000000, 10.000000}})));
    annotation (Protection(access=Access.nonPackageDuplicate),
      Documentation(link="modelica://TAThermalSystem/Resource/Doc/CabinComponentTest.html"),experiment(Algorithm=Dassl,NumberOfIntervals=500,StartTime=0,StopTime=100,Tolerance=0.0001),__MWORKS(ContinueSimConfig(SaveContinueFile="false",SaveBeforeStop="false",NumberBeforeStop=1,FixedContinueInterval="false",ContinueIntervalLength=100,ContinueTimeVector),ResultViewerManager(resultViewers={
  ResultViewer(name="1", executeTrigger=executeTrigger.SimulationFinished, commands={
  CreatePlot(id=1, x_display_unit="s", legend_layout=7, left_title="[degC]", fix_time_range_value=0, zoom_x=(0, 100), zoom_y_l=(10, 40)),
  Plot(y=["cabinHeatNetwork.summary.T"], colors=["4278190335"])})
  })));
  equation
    connect(airSource_mT.port_b, cabinHeatNetwork.a) 
    annotation(Line(origin={-30,0},
    points={{-20,0},{19.799999999999997,0}},
    color={0,232,232},
    thickness=1));
    connect(cabinHeatNetwork.b, airSink_pT.port_a) 
    annotation(Line(origin={30,0},
    points={{-19.799999999999997,2.842170943040401e-15},{20,2.842170943040401e-15},{20,0}},
    color={0,232,232},
    thickness=1));
    end CabinComponentTest;
  end VolumetricComponent;