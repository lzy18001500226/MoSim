model SingularPressureDrop "SingularPressureDrop压降方式"
  parameter Modelica.Units.SI.MassFlowRate m_flow_in = 0.618 "输入流量";
  parameter Modelica.Units.SI.Temperature T_heatin = 343.15 "壁面边界温度";
  TAThermalSystem.Sources.Coolant.Coolant_mT Coolant_mT(title = "冷却液源", mflow = m_flow_in) 
    annotation (Placement(transformation(origin = {-60.197304251025066, -0.504693663049621},
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TAThermalSystem.Sources.Coolant.Coolant_pT Coolant_pT(title = "水出口", p = 4.999999999999999e5) 
    annotation (Placement(transformation(origin = {51.894271204349906, -1.3911101083070094},
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TAThermalSystem.Sources.HeatTransfer.FixedTemperature fixedTemperature(T = T_heatin,
    n = 1) annotation (Placement(transformation(origin = {-21.74757281553398, 39.14563106796117},
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TAThermalSystem.Pipes.LiquidCoolingPipe.CoolingPipeCR coolingPipeBase2(useHeatTransfer = true, redeclare model Friction = TYBase.Thermal.FluidHeatFlow.PressureLoss.LiquidPressureDrop.SingularPressureDrop, redeclare Integer calType = 2, h_conv_set = 75,
    CF_PressureLoss = 1,
    fromDp = false) annotation (Placement(transformation(origin = {-0.6808510638297873, -1.0212765957446805},
      extent = {{-10.0997, -8.821720000000001}, {10.0638, 9.007800000000001}})));



  Modelica.Units.SI.Pressure p_3 "进口压力";
  Modelica.Units.SI.Pressure p_1 "出口压力";
  annotation (Icon(coordinateSystem(extent = {{-100.0, -100.0}, {100.0, 100.0}},
    grid = {2.0, 2.0}), graphics = {Bitmap(origin = {0.0, 0.0},
    extent = {{-100.0, -100.0}, {100.0, 100.0}},
    fileName = "modelica://TAThermalSystem/Resource/Icons/Example.svg")}),
    Protection(access=Access.nonPackageDuplicate),
    experiment(Algorithm = Dassl, NumberOfIntervals = 500, StartTime = 0, StopTime = 10, Tolerance = 0.0001),
    Documentation(link = "modelica://TAThermalSystem/Resource/Doc/FlowBoundarySingularPressureDrop.html"),__MWORKS(ResultViewerManager(resultViewers={
ResultViewer(name="1", executeTrigger=executeTrigger.SimulationFinished, commands={
CreatePlot(id=1, x_display_unit="s", legend_layout=7, left_title="[bar]", fix_time_range_value=0, zoom_x=(0, 10), zoom_y_l=(4.995, 5.02)),
Plot(y=["p_3", "p_1"], colors=["4278190335", "4294901760"])})
})));
equation
  p_3 = coolingPipeBase2.pipeSummary.p_in;
  p_1 = coolingPipeBase2.pipeSummary.p_out;
  connect(fixedTemperature.port[1], coolingPipeBase2.qa) 
    annotation (Line(origin = {-6.0, 20.0},
      points = {{-6.0, 19.0}, {5.0, 19.0}, {5.0, -11.0}},
      color = {191, 0, 0},
      thickness = 1.0));
  connect(Coolant_mT.port_b, coolingPipeBase2.a) 
    annotation (Line(origin = {-30.0, -1.0},
      points = {{-20.0, 0.0}, {19.0, 0.0}},
      color = {0, 170, 255},
      thickness = 1.0));
  connect(coolingPipeBase2.b, Coolant_pT.port_a) 
    annotation (Line(origin = {23.0, -1.0},
      points = {{-14.0, 0.0}, {19.0, 0.0}},
      color = {0, 170, 255},
      thickness = 1.0));
end SingularPressureDrop;