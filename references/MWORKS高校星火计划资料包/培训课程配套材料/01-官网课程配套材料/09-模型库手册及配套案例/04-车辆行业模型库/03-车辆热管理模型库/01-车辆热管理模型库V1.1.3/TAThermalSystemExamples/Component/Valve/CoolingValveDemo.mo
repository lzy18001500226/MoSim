model CoolingValveDemo "冷却阀门案例"

  extends TAThermalSystem.Utilities.Icons.BasicIcons.Example;



  annotation (Documentation(link = "modelica://TAThermalSystem/Resource/Doc/CoolingValveDemo.html"),
    Protection(access=Access.nonPackageDuplicate),
    Diagram(coordinateSystem(extent = {{-100.0, -100.0}, {100.0, 100.0}},
      grid = {2.0, 2.0})),
    experiment(Algorithm = Dassl, NumberOfIntervals = 500, StartTime = 0, StopTime = 120, Tolerance = 0.0001),__MWORKS(ResultViewerManager(resultViewers={
ResultViewer(name="1", executeTrigger=executeTrigger.SimulationStarted, commands={
CreatePlot(id=1, x_display_unit="s", legend_layout=7, left_title="[kg/s]", fix_time_range_value=0, zoom_x=(0, 120), zoom_y_l=(-0.1, 0.5)),
Plot(y=["valveFlowKvCooling.mdot"], thicknesses=[2], colors=["4278190335"])})
})));
  TAThermalSystem.Valves.HydraulicValve.ValveFlowKvCooling valveFlowKvCooling(Kv_curve = {{0.0, 0}, {0.01, 0}, {0.1, 0.1}, {0.2, 0.3}, {0.4, 0.5}, {0.6, 0.6}, {0.8, 0.7}, {1.0, 0.7}, {1.1, 0.7}}) 
    annotation (Placement(transformation(origin={-5.55112e-17,0},
extent={{-10,10},{10,-10}})));
  Modelica.Blocks.Sources.Step step(startTime = 1) 
    annotation (Placement(transformation(origin={-30,-28},
extent={{-10,-10},{10,10}})));
  TAThermalSystem.Sources.Coolant.Coolant_pT Coolant_pT 
    annotation (Placement(transformation(origin={50,3.55271e-15},
extent={{-10,-10},{10,10}})));
  TAThermalSystem.Sources.Coolant.Coolant_pT Coolant_pT1(p = 4.999999999999999e5) 
    annotation (Placement(transformation(origin={-50,3.55271e-15},
extent={{10,-10},{-10,10}})));
equation
  connect(step.y, valveFlowKvCooling.u) 
    annotation (Line(origin={-29,-19},
points={{10,-9},{29,-9},{29,9}},
color={0,0,127}));
  connect(Coolant_pT1.port_a, valveFlowKvCooling.a) 
    annotation (Line(origin={-25,3.55271e-15},
points={{-15,0},{14.9899,0},{14.9899,0.037774}},
color={0,0,128},
thickness=1));
  connect(valveFlowKvCooling.b, Coolant_pT.port_a) 
    annotation (Line(origin={25,3.55271e-15},
points={{-14.8766,0.037774},{15,0.037774},{15,0}},
color={0,0,128},
thickness=1));
end CoolingValveDemo;