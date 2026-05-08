model R134aPipeDemo "R134a制冷剂管道案例"
  annotation(Documentation(link = "modelica://TAThermalSystem/Resource/Doc/R134aPipeDemo.html"
),
    Protection(access=Access.nonPackageDuplicate),
    experiment(Algorithm = Dassl, NumberOfIntervals = 500, StartTime = 0, StopTime = 120, Tolerance = 0.0001),__MWORKS(ResultViewerManager(resultViewers={
ResultViewer(name="1", executeTrigger=executeTrigger.SimulationStarted, commands={
CreatePlot(id=1, x_display_unit="s", legend_layout=7, left_title="[bar]", fix_time_range_value=0, zoom_x=(0, 120), zoom_y_l=(4.3, 5.1)),
Plot(y=["simplePipe1.p[1]"], thicknesses=[2], colors=["4278190335"])})
})));



  extends TAThermalSystem.Utilities.Icons.BasicIcons.Example;
  TAThermalSystem.Sources.Refrigerant.Source_mh r134aSource_mT(h_source = 3e5) annotation(Placement(transformation(origin = {-80.0, -3.552713678800501e-15},
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TAThermalSystem.Sources.Refrigerant.Sink_pT r134aSink2 annotation(Placement(transformation(origin = {78.88662420382165, -0.8560509554140283},
    extent = {{10.0, -10.0}, {-10.0, 10.0}})));
  TAThermalSystem.Pipes.TwoPhasePipe.SimplePipe simplePipe1(init(initType = TYBase.Utilities.Types.Init.Initial_MT, M0 = 0.003), useAcceldp = true ) 

    annotation(Placement(transformation(extent = {{-10.0, -10.0}, {10.0, 10.0}})));
equation
  connect(r134aSource_mT.port_b, simplePipe1.a) 
    annotation(Line(origin = {-39.0, 0.0},
    points = {{-31.0, 0.0}, {29.0, 0.0}},
    color = {0, 128, 0},
    thickness = 1.0));
  connect(simplePipe1.b, r134aSink2.port_a) 
    annotation(Line(origin = {52.0, 0.0},
    points = {{-42.0, 0.0}, {17.0, 0.0}, {17.0, -1.0}},
    color = {0, 128, 0},
    thickness = 1.0));
end R134aPipeDemo;