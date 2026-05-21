model FrontGrilleDemo "进气格栅案例"
  extends TAThermalSystem.Utilities.Icons.BasicIcons.Example;
  TAThermalSystem.Pipes.AirPass.FrontGrille frontGrille 
    annotation (Placement(transformation(origin={30,-36},
extent={{-28,-24},{28,24}})));
  inner TAThermalSystem.Pipes.AirPass.HEATStack hEATStack 
    annotation (Placement(transformation(origin={-50,28},
extent={{-24,-24},{24,24}})));
  Modelica.Blocks.Sources.RealExpression realExpression(y=1) 
    annotation (Placement(transformation(origin={-64,-36},
extent={{-10,-10},{10,10}})));
  annotation(Protection(access=Access.nonPackageDuplicate),__MWORKS(ResultViewerManager(resultViewers={
ResultViewer(name="res", executeTrigger=executeTrigger.SimulationFinished, commands={
CreatePlot(x_display_unit="s", legend_layout=7, left_title="[kg/s]", fix_time_range_value=0, zoom_x=(0, 1), zoom_y_l=(0.05742, 0.057428)),
Plot(y=["frontGrille.mdot"], colors=["4278190335"])})
})),Documentation(link="modelica://TAThermalSystem/Resource/Doc/FrontGrilleDemo.html"
));
equation
  connect(frontGrille.kdp, realExpression.y) 
  annotation(Line(origin={-26,-36},
  points={{26.88,0},{-27,0}},
  color={0,0,127}));

end FrontGrilleDemo;