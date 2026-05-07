model CoolingFan "冷却风扇案例"
  parameter Modelica.Units.SI.Pressure p_in(displayUnit = "bar") = 1.013e5 "进口压力";
  parameter Modelica.Units.SI.Pressure p_out(displayUnit = "bar") = 1.014e5 "出口压力";
  parameter Real Rev = 500 "风扇转速rpm";
  extends TAThermalSystem.Utilities.Icons.BasicIcons.Example;
  annotation (Protection(access=Access.nonPackageDuplicate),
    experiment(Algorithm = Dassl, NumberOfIntervals = 500, StartTime = 0, StopTime = 120, Tolerance = 0.0001),
    Documentation(link="modelica://TAThermalSystem/Resource/Doc/CoolingFan.html"),__MWORKS(ResultViewerManager(resultViewers={
ResultViewer(name="1", executeTrigger=executeTrigger.SimulationFinished, commands={
CreatePlot(id=1, x_display_unit="s", legend_layout=7, left_title="[kg/s]", fix_time_range_value=0, zoom_x=(0, 120), zoom_y_l=(0.2, 1.4)),
Plot(y=["fan1.a.m_flow", "fan.a.m_flow"], colors=["4278190335", "4294901760"])})
})));
  Modelica.Blocks.Sources.RealExpression realExpression3(y = Rev * Modelica.Constants.pi / 30) 
    annotation (Placement(transformation(origin = {-45.0802139037433, -68.39860386179508},
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  Modelica.Mechanics.Rotational.Sources.Speed speed2 
    annotation (Placement(transformation(origin = {-11.080213903743314, -68.39860386179508},
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TAThermalSystem.PumpAndFan.Fan fan(redeclare package Medium = TYBase.Media_Extend.Air.MoistAir) 
    annotation (Placement(transformation(origin = {0.14665565394602398, -32.92161751327116},
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TAThermalSystem.Sources.Air.AirSink_pT airSink_pT(p_sink = p_in) 
    annotation (Placement(transformation(origin = {-60.97942379337695, -32.92161751327116},
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TAThermalSystem.Sources.Air.AirSink_pT airSink_pT1(p_sink = p_out) 
    annotation (Placement(transformation(origin = {54.236176980336054, -32.92161751327116},
      extent = {{10.0, -10.0}, {-10.0, 10.0}})));
  Modelica.Blocks.Sources.RealExpression realExpression4(y = Rev * Modelica.Constants.pi / 30) 
    annotation (Placement(transformation(origin = {-45.0802139037433, 25.433731467546252},
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  Modelica.Mechanics.Rotational.Sources.Speed speed3 
    annotation (Placement(transformation(origin = {-11.080213903743314, 25.433731467546252},
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TAThermalSystem.PumpAndFan.FanA fan1(redeclare package Medium = TYBase.Media_Extend.Air.MoistAir,useEtaTable=true) annotation (Placement(transformation(origin = {0.14665565394602353, 60.91071781607016},
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TAThermalSystem.Sources.Air.AirSink_pT airSink_pT2(p_sink = p_in) 
    annotation (Placement(transformation(origin = {-60.97942379337695, 60.91071781607016},
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TAThermalSystem.Sources.Air.AirSink_pT airSink_pT3(p_sink = p_out) 
    annotation (Placement(transformation(origin = {54.236176980336054, 60.91071781607016},
      extent = {{10.0, -10.0}, {-10.0, 10.0}})));
equation
  connect(realExpression3.y, speed2.w_ref) 
    annotation (Line(origin = {-31.080213903743285, -68.3986038617951},
      points = {{-3.000000000000014, 1.4210854715202004e-14}, {7.999999999999972, 1.4210854715202004e-14}},
      color = {0, 0, 127}));
  connect(fan.shaft, speed2.flange) 
    annotation (Line(origin = {1.9197860962567148, -47.39860386179511},
      points = {{-1.7731304423106908, 4.476986348523951}, {-1.7731304423106908, -23.0}, {-3.0000000000000284, -23.0}, {-3.0000000000000284, -20.99999999999997}},
      color = {0, 0, 0}));
  connect(airSink_pT.port_a, fan.a) 
    annotation (Line(origin = {-30.0, -32.52694610778443},
      points = {{-20.979423793376952, -0.39467140548672575}, {20.146655653946024, -0.39467140548672575}},
      color = {0, 232, 232},
      thickness = 1.0));
  connect(fan.b, airSink_pT1.port_a) 
    annotation (Line(origin = {27.0, -32.52694610778443},
      points = {{-16.853344346053976, -0.39467140548672575}, {17.236176980336054, -0.39467140548672575}},
      color = {0, 232, 232},
      thickness = 1.0));
  connect(realExpression4.y, speed3.w_ref) 
    annotation (Line(origin = {-31.080213903743285, 25.433731467546224},
      points = {{-3.000000000000014, 2.842170943040401e-14}, {7.999999999999972, 2.842170943040401e-14}},
      color = {0, 0, 127}));
  connect(fan1.shaft, speed3.flange) 
    annotation (Line(origin = {1.9197860962567148, 46.43373146754621},
      points = {{-1.7731304423106913, 4.476986348523951}, {-1.7731304423106913, -23.0}, {-3.0000000000000284, -23.0}, {-3.0000000000000284, -20.999999999999957}},
      color = {0, 0, 0}));
  connect(airSink_pT2.port_a, fan1.a) 
    annotation (Line(origin = {-30.0, 61.30538922155687},
      points = {{-20.979423793376952, -0.39467140548671154}, {20.146655653946024, -0.39467140548671154}},
      color = {0, 232, 232},
      thickness = 1.0));
  connect(fan1.b, airSink_pT3.port_a) 
    annotation (Line(origin = {27.0, 61.30538922155687},
      points = {{-16.853344346053976, -0.39467140548671154}, {17.236176980336054, -0.39467140548671154}},
      color = {0, 232, 232},
      thickness = 1.0));
end CoolingFan;