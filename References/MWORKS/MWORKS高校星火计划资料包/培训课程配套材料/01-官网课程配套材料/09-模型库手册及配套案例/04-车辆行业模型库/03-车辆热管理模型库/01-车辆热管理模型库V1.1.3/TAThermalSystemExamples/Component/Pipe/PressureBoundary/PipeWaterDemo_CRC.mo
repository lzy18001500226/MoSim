model PipeWaterDemo_CRC "CRC管道"
  annotation(Icon(coordinateSystem(extent={{-100,-100},{100,100}},
grid={2,2}),graphics = {Bitmap(origin={2,-2},
extent={{-100,-100},{100,100}},
fileName="modelica://TAThermalSystem/Resource/Icons/Example.svg")}),Diagram(coordinateSystem(extent={{-100,-100},{100,100}},
grid={2,2})),Protection(access=Access.nonPackageDuplicate),Documentation(link="modelica://TAThermalSystem/Resource/Doc/PressureBoundaryPipeWaterDemo_CRC.html"),__MWORKS(ResultViewerManager(resultViewers={
ResultViewer(name="1", executeTrigger=executeTrigger.SimulationFinished, commands={
CreatePlot(x_display_unit="s", legend_layout=7, left_title="[kg/s]", fix_time_range_value=0, zoom_x=(0, 1), zoom_y_l=(1.4816, 1.4824)),
Plot(y=["coolingPipeCRC1.pipeSummary.mdot"], colors=["4278190335"])})
})));
  TAThermalSystem.Sources.Coolant.Coolant_pT coolant_pT(















                                                        p=1.1e5
                                                               ) 
    annotation (Placement(transformation(origin={-50,-4.440892098500626e-15},
extent={{10,-10},{-10,10}})),__MWORKS(BlockSystem(StateMachine)));
  TAThermalSystem.Sources.Coolant.Coolant_tank coolant_tank1 
    annotation (Placement(transformation(origin={60,-3.552713678800501e-15},
extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(StateMachine)));
  TAThermalSystem.Pipes.LiquidCoolingPipe.CoolingPipeCRC coolingPipeCRC1 
    annotation (Placement(transformation(origin={-0.06380000000000052,0.9922000000000004},
extent={{-10.0997,-8.82172},{10.0638,9.0078}})),__MWORKS(BlockSystem(StateMachine)));
equation
  connect(coolant_pT.port_a, coolingPipeCRC1.a) 
  annotation(Line(origin={-41.95015000000001,0.1704800000000013},
points={{1.9501500000000078,-0.17048000000000552},{31.87623195615515,-0.17048000000000552},{31.87623195615515,0.7839459696458676}},
color={0,170,255},
thickness=1));
  connect(coolingPipeCRC1.b, coolant_tank1.port_a) 
  annotation(Line(origin={46.04984999999999,0.1704800000000013},
points={{-35.99020986509274,0.7839459696458676},{13.950150000000008,0.7839459696458676},{13.950150000000008,-0.17048000000000485}},
color={0,170,255},
thickness=1));

end PipeWaterDemo_CRC;