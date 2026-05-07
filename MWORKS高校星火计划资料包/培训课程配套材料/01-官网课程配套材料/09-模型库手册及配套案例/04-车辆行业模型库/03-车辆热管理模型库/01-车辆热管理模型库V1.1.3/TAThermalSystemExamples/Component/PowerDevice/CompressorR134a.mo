model CompressorR134a "R134a压缩机案例"
  parameter Modelica.Units.SI.Pressure p_out = 4.999999999999999e5 "出口压力";
  parameter Real Rev = 2000 "转速";
  extends TAThermalSystem.Utilities.Icons.BasicIcons.Example;
  Modelica.Blocks.Sources.RealExpression realExpression1(y = Rev * Modelica.Constants.pi / 30) 
    annotation (Placement(transformation(origin = {-43.999999999999986, -40.0},
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  Modelica.Mechanics.Rotational.Sources.Speed speed(useSupport = false) 
    annotation (Placement(transformation(origin = {-10.0, -40.0},
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TAThermalSystem.Sources.Refrigerant.Sink_pT r134aSink(p(displayUnit = "bar") = p_out) 
    annotation (Placement(transformation(origin = {42.0, 0.0},
      extent = {{10.0, -10.0}, {-10.0, 10.0}})));



  annotation (Documentation(link="modelica://TAThermalSystem/Resource/Doc/CompressorR134a.html"),
    Protection(access=Access.nonPackageDuplicate),
    experiment(Algorithm = Dassl, NumberOfIntervals = 500, StartTime = 0, StopTime = 120, Tolerance = 0.0001),__MWORKS(ResultViewerManager(resultViewers={
ResultViewer(name="1", executeTrigger=executeTrigger.SimulationFinished, commands={
CreatePlot(id=1, x_display_unit="s", legend_layout=7, left_title="[kg/s]", fix_time_range_value=0, zoom_x=(0, 120), zoom_y_l=(0.0034301, 0.0034309)),
Plot(y=["compressorR134a.summary.mdot"], colors=["4278190335"]),
CreatePlot(id=-1, x_display_unit="s", legend_layout=7, left_title="[W]", fix_time_range_value=0, sub_plot=(2, 1), zoom_x=(0, 120), zoom_y_l=(200.21, 200.29)),
Plot(y=["compressorR134a.summary.p_refrigerant"], colors=["4278190335"])})
})));
  TAThermalSystem.Sources.Refrigerant.Sink_pT r134aSink1(p(displayUnit = "bar") = 100000) 
    annotation (Placement(transformation(origin = {-44.0, 0.0},
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TAThermalSystem.Compressor.Compressor compressorR134a(
    use_interpolation = false, EtaVol_spd = {{0, 0.8}, {1000, 0.7}, {2000, 0.7}, {3000, 0.7}, {4000, 0.5}, {5000, 0.5}}, EtaIsen_spd = {{0, 0.8}, {1000, 0.7}, {2000, 0.7}, {3000, 0.7}, {4000, 0.5}, {5000, 0.5}},
    EtaMec_spd = {{0, 0.8}, {1000, 0.7}, {2000, 0.7}, {3000, 0.7}, {4000, 0.5}, {5000, 0.5}}) 
    annotation (Placement(transformation(extent = {{-10.0, -10.0}, {10.0, 10.0}})));
equation
  connect(realExpression1.y, speed.w_ref) 
    annotation (Line(origin = {-49.0, -45.0},
      points = {{16.0, 5.0}, {27.0, 5.0}},
      color = {0, 0, 127}));
  connect(compressorR134a.flange, speed.flange) 
    annotation (Line(origin = {0.0, -25.0},
      points = {{0.0, 15.0}, {0.0, -15.0}},
      color = {0, 0, 0}));
  connect(compressorR134a.a, r134aSink1.port_a) 
    annotation (Line(origin = {-22.0, 0.0},
      points = {{12.0, 0.0}, {-12.0, 0.0}},
      color = {0, 128, 0},
      thickness = 1.0));
  connect(compressorR134a.b, r134aSink.port_a) 
    annotation (Line(origin = {21.0, 0.0},
      points = {{-11.0, 0.0}, {11.0, 0.0}},
      color = {0, 128, 0},
      thickness = 1.0));
end CompressorR134a;