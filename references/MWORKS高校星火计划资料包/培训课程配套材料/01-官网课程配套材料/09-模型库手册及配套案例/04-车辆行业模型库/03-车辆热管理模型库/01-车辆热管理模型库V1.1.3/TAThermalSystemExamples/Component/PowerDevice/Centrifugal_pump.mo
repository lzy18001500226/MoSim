model Centrifugal_pump "离心水泵"
  parameter Real Rev = 2000 "水泵转速";
  parameter Modelica.Units.SI.Pressure p_in(displayUnit = "bar") = 1.1e5 "出口压力";
  parameter Modelica.Units.SI.Pressure p_out(displayUnit = "bar") = 1.2e5 "出口压力";
  annotation (Icon(coordinateSystem(extent = {{-100.0, -100.0}, {100.0, 100.0}},
    grid = {2.0, 2.0}), graphics = {Bitmap(origin = {0.0, 0.0},
    extent = {{-100.0, -100.0}, {100.0, 100.0}},
    fileName = "modelica://TAThermalSystem/Resource/Icons/Example.svg")}),
    Documentation(link="modelica://TAThermalSystem/Resource/Doc/Centrifugal.html"),
    Protection(access=Access.nonPackageDuplicate),__MWORKS(ResultViewerManager(resultViewers={
ResultViewer(name="1", executeTrigger=executeTrigger.SimulationFinished, commands={
CreatePlot(id=1, x_display_unit="s", legend_layout=7, left_title="[kg/s]", fix_time_range_value=0, zoom_x=(0, 10), zoom_y_l=(-1.5, 1.5)),
Plot(y=["centrifugal_pump2.a.m_flow", "centrifugal_pump2.b.m_flow"], colors=["4278190335", "4294901760"])})
})));
  Modelica.Blocks.Sources.RealExpression realExpression3(y = Rev) 
    annotation (Placement(transformation(origin={-54,-31.397},
extent={{-10,-10},{10,10}})));
  TAThermalSystem.Sources.Coolant.Coolant_pT coolant_pT(p = p_out) 
    annotation (Placement(transformation(origin={-54.0971,11.9622},
extent={{10,-10},{-10,10}})));
  TAThermalSystem.PumpAndFan.CentrifugalPump centrifugal_pump2(redeclare package Medium = TYBase.Media_Extend.GW50, T_start = 288.15) 
    annotation (Placement(transformation(origin={0,12},
extent={{10,-10},{-10,10}})));
  TAThermalSystem.Sources.Coolant.Coolant_pT coolant_pT1(p = p_in) 
    annotation (Placement(transformation(origin={54.0971,11.9622},
extent={{-10,-10},{10,10}})));
  TAThermalSystem.Sensors.PowerOutput powerOutput 
    annotation (Placement(transformation(origin={-0.0327965,-19.397},
extent={{10,-10},{-10,10}},
rotation=-90)));
  TAThermalSystem.Sources.Mechanics.RotationalInputSource rotationalInputSource 
    annotation (Placement(transformation(origin={-27,-31.397},
extent={{-8,-6},{10,6}})));
equation
  connect(coolant_pT1.port_a, centrifugal_pump2.a) 
    annotation (Line(origin={27.0971,11.9622},
points={{17,-1.42109e-14},{-17.087,-1.42109e-14},{-17.087,-1.59872e-14}},
color={0,170,255},
thickness=1));
  connect(coolant_pT.port_a, centrifugal_pump2.b) 
    annotation (Line(origin={-26.9029,11.9622},
points={{-17.1942,2.84217e-14},{16.7795,2.84217e-14},{16.7795,-1.59872e-14}},
color={0,170,255},
thickness=1));
  connect(centrifugal_pump2.flange, powerOutput.flangeB) 
  annotation(Line(origin={15,-3.397},
points={{-15,5.397},{-15,-6.12826},{-15,-6.12826}},
color={0,0,0}));
  connect(realExpression3.y, rotationalInputSource.u) 
  annotation(Line(origin={-38,-31.397},
points={{-5,-1.42109e-14},{4,-1.42109e-14}},
color={0,0,127}));
  connect(rotationalInputSource.flange, powerOutput.flangeA) 
  annotation(Line(origin={7,-30.397},
points={{-24,-1},{-6.89868,-1},{-6.89868,0.964275}},
color={0,0,0}));

end Centrifugal_pump;