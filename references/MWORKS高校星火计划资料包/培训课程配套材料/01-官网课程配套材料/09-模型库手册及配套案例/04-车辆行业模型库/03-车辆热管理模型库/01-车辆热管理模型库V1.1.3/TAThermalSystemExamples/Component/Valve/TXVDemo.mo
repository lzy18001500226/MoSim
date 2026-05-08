model TXVDemo "膨胀阀案例"

  extends TAThermalSystem.Utilities.Icons.BasicIcons.Example;



  annotation (Documentation(link = "modelica://TAThermalSystem/Resource/Doc/TXVDemo.html"),
    Protection(access=Access.nonPackageDuplicate),
    Diagram(coordinateSystem(extent = {{-100.0, -100.0}, {100.0, 100.0}},
      grid = {2.0, 2.0})),
    experiment(Algorithm = Dassl, NumberOfIntervals = 500, StartTime = 0, StopTime = 120, Tolerance = 0.0001),__MWORKS(ResultViewerManager(resultViewers={
ResultViewer(name="1", executeTrigger=executeTrigger.SimulationStarted, commands={
CreatePlot(id=1, x_display_unit="s", legend_layout=7, left_title="[kg/s]", fix_time_range_value=0, zoom_x=(0, 120), zoom_y_l=(-0.02, 0.08)),
Plot(y=["valve.mdot"], thicknesses=[2], colors=["4278190335"])})
})));
  TAThermalSystem.Sources.Refrigerant.Sink_pT r134aSink3(p(displayUnit = "bar") = 4e5, T = 303.15) 
    annotation (Placement(transformation(origin = {70.00000000000003, 4.440892098500626e-16},
      extent = {{10.0, -10.0}, {-10.0, 10.0}})));



  TAThermalSystem.Sources.Refrigerant.Sink_pT r134aSink4(p(displayUnit = "bar") = 7e5, T = 303.15) 
    annotation (Placement(transformation(origin = {-70.0, 0.0},
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TAThermalSystem.Valves.RefrigerantValve.ValveFlowKv valve(title = "膨胀阀") annotation (Placement(transformation(extent = {{-10.0, 10.0}, {10.0, -10.0}})));

  Modelica.Blocks.Sources.Ramp ramp(duration = 10) 
    annotation (Placement(transformation(origin = {-70.0, -60.0},
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
equation
  connect(ramp.y, valve.u) 
    annotation (Line(origin = {-49.0, -35.0},
      points = {{-10.0, -25.0}, {50.0, -25.0}, {50.0, 25.0}, {49.0, 25.0}},
      color = {0, 0, 127}));
  connect(r134aSink4.port_a, valve.a) 
    annotation (Line(origin = {-35.0, 0.0},
      points = {{-25.0, 0.0}, {25.0, 0.0}},
      color = {0, 128, 0},
      thickness = 1.0));
  connect(valve.b, r134aSink3.port_a) 
    annotation (Line(origin = {35.0, 0.0},
      points = {{-25.0, 0.0}, {25.00000000000003, 4.440892098500626e-16}},
      color = {0, 128, 0},
      thickness = 1.0));
end TXVDemo;