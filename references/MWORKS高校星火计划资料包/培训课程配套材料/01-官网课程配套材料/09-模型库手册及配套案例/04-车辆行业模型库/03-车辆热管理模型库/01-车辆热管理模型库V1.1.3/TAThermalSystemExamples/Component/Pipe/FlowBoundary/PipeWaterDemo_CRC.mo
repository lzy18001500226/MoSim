model PipeWaterDemo_CRC "CRC管道"
  annotation(Diagram(coordinateSystem(extent={{-100,-100},{100,100}},
  grid={2,2})),Icon(coordinateSystem(extent={{-100,-100},{100,100}},
grid={2,2}),graphics = {Bitmap(origin={0,-5.329070518200751e-15},
extent={{-100,-100},{100,100}},
fileName="modelica://TAThermalSystem/Resource/Icons/Example.svg")}),Protection(access=Access.nonPackageDuplicate),Documentation(link="modelica://TAThermalSystem/Resource/Doc/FlowBoundaryPipeWaterDemo_CRC.html"),__MWORKS(ResultViewerManager(resultViewers={
ResultViewer(name="1", executeTrigger=executeTrigger.SimulationFinished, commands={
CreatePlot(id=1, x_display_unit="s", legend_layout=7, left_title="[bar]", fix_time_range_value=0, zoom_x=(0, 1), zoom_y_l=(1.012, 1.024)),
Plot(y=["coolingPipeCRC.pipeSummary.p_out", "coolingPipeCRC.pipeSummary.p_in"], colors=["4278190335", "4294901760"])})
})),experiment(Algorithm=Dassl,InlineIntegrator=false,InlineStepSize=false,NumberOfIntervals=500,StartTime=0,StopTime=100,StoreEventValue=0,Tolerance=0.0001));
  TAThermalSystem.Sources.Coolant.Coolant_mT coolant_mT 
    annotation (Placement(transformation(origin={-53.8365,-0.9922000000000005},
extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(StateMachine)));
  TAThermalSystem.Sources.Coolant.Coolant_tank coolant_tank 
    annotation (Placement(transformation(origin={50,-0.9921999999999986},
extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(StateMachine)));

  TAThermalSystem.Pipes.LiquidCoolingPipe.CoolingPipeCRC coolingPipeCRC 
    annotation (Placement(transformation(origin={-1.9002999999999997,0},
extent={{-10.0997,-8.82172},{10.0638,9.0078}})),__MWORKS(BlockSystem(StateMachine)));
equation

  connect(coolant_mT.port_b, coolingPipeCRC.a) 
  annotation(Line(origin={-55,0},
points={{11.163499999999999,-0.9922000000000011},{43.08958195615514,-0.9922000000000011},{43.08958195615514,-0.037774030354131516}},
color={0,170,255},
thickness=1));
  connect(coolingPipeCRC.b, coolant_tank.port_a) 
  annotation(Line(origin={45,-5},
points={{-36.776859865092746,4.962225969645869},{5,4.962225969645869},{5,4.007800000000001}},
color={0,170,255},
thickness=1));

end PipeWaterDemo_CRC;