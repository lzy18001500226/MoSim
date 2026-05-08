model Chiller "chiller测试"
  extends TAThermalSystem.Utilities.Icons.BasicIcons.Example;
  parameter Modelica.SIunits.MassFlowRate m_flow_coolin = 0.1 "冷端输入流量";
  parameter Modelica.SIunits.MassFlowRate m_flow_heatin = 0.2 "热端输入流量";
  parameter Modelica.SIunits.Temperature T_heatin(displayUnit = "degC") = 293.15 "热端温度";
  TAThermalSystem.Sources.Coolant.Coolant_mT Coolant_mT(title = "水出口", mflow = m_flow_heatin, T_source = T_heatin, p0 = 1.5e5) 
    annotation (Placement(transformation(origin = {-47.00054527669576, 27.57492830107095},
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TAThermalSystem.Sources.Coolant.Coolant_tank Coolant_pT(title = "水出口") 
    annotation (Placement(transformation(origin = {37.14713256779397, 26.99759949413892},
      extent = {{10.0, -10.0}, {-10.0, 10.0}})));
  annotation (Icon(coordinateSystem(extent = {{-100.0, -100.0}, {100.0, 100.0}},
    grid = {2.0, 2.0})),
    Protection(access=Access.nonPackageDuplicate),
    Documentation(link="modelica://TAThermalSystem/Resource/Doc/Chiller.html"),experiment(Algorithm=Dassl,InlineIntegrator=false,InlineStepSize=false,NumberOfIntervals=500,StartTime=0,StopTime=120,Tolerance=0.0001),__MWORKS(ContinueSimConfig(SaveContinueFile="false",SaveBeforeStop="false",NumberBeforeStop=1,FixedContinueInterval="false",ContinueIntervalLength=2.4,ContinueTimeVector),ResultViewerManager(resultViewers={
ResultViewer(name="1", executeTrigger=executeTrigger.SimulationFinished, commands={
CreatePlot(id=1, x_display_unit="s", legend_layout=7, left_title="[bar]", fix_time_range_value=0, zoom_x=(0, 120), zoom_y_l=(0, 3.5)),
Plot(y=["chillerPlateCooling.simplePipe.a.p", "chillerPlateCooling.simplePipe.b.p"], colors=["4278190335", "4294901760"]),
CreatePlot(id=-1, x_display_unit="s", legend_layout=7, left_title="[W]", fix_time_range_value=0, sub_plot=(2, 1), zoom_x=(0, 120), zoom_y_l=(-12000, 2000)),
Plot(y=["chillerPlateCooling.water.pipeSummary.Qdot"], colors=["4278190335"])})
})));

  TAThermalSystem.HeatExchangers.CoolingRadiatorNTU.ChillerPlateCooling chillerPlateCooling(RefInit(mdot0 = 0.1, p_in = 5.5e5), redeclare model Friction = TYBase.Thermal.FluidHeatFlow.PressureLoss.LiquidPressureDrop.SingularPressureDrop) 
    annotation (Placement(transformation(origin = {-2.4897146648971473, -12.70869276708693},
      extent = {{10.0, -10.0}, {-10.0, 10.0}})));
  TAThermalSystem.Sources.Refrigerant.Sink_ph flowSink_ph(p0 = 3e5) 
    annotation (Placement(transformation(origin = {-47.00054527669578, -44.39416058394162},
      extent = {{10.0, -10.0}, {-10.0, 10.0}})));
  TAThermalSystem.Sources.Refrigerant.Source_mh r134aSource_mT(h_source = 277.75e3, m = m_flow_coolin) annotation (Placement(transformation(origin = {37.14713256779397, -44.39416058394162},
    extent = {{10.0, -10.0}, {-10.0, 10.0}})));
equation
  connect(Coolant_mT.port_b, chillerPlateCooling.c) 
    annotation (Line(origin = {-26.970839683139175, 11.116641267443304},
      points = {{-10.029705593556585, 16.45828703362765}, {14.481125018242029, 16.45828703362765}, {14.481125018242029, -17.825334034530236}},
      color = {0, 0, 128},
      thickness = 1.0));
  connect(chillerPlateCooling.d, Coolant_pT.port_a) 
    annotation (Line(origin = {35.029160316860825, 10.116641267443304},
      points = {{-27.51887498175797, -16.825334034530236}, {-27.51887498175797, 16.88095822669562}, {2.1179722509331427, 16.88095822669562}},
      color = {0, 0, 128},
      thickness = 1.0));
  connect(chillerPlateCooling.a, r134aSource_mT.port_b) 
    annotation (Line(origin={14,-32},
points={{-6.48971,13.2913},{13.1471,13.2913},{13.1471,-14},{10.1471,-14},{10.1471,-12.3942},{13.1471,-12.3942}},
color={0,128,0},
thickness=1));
  connect(flowSink_ph.a, chillerPlateCooling.b) 
    annotation (Line(origin = {-25.0, -32.0},
      points = {{-12.000545276695782, -12.39416058394162}, {-12.000545276695782, 13.29130723291307}, {12.510285335102854, 13.29130723291307}},
      color = {0, 128, 0},
      thickness = 1.0));
end Chiller;