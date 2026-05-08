model CoolingPump "冷却水泵案例"
  parameter Modelica.Units.SI.Pressure p_out(displayUnit = "bar") = 4.999999999999999e5 "出口压力";
  parameter Real Rev = 1000 "压缩机转速";
  extends TAThermalSystem.Utilities.Icons.BasicIcons.Example;
  annotation (Protection(access=Access.nonPackageDuplicate),
    experiment(Algorithm = Dassl, NumberOfIntervals = 500, StartTime = 0, StopTime = 120, Tolerance = 0.0001),
    Documentation(link="modelica://TAThermalSystem/Resource/Doc/CoolingPump.html"),__MWORKS(ResultViewerManager(resultViewers={
ResultViewer(name="1", executeTrigger=executeTrigger.SimulationFinished, commands={
CreatePlot(id=1, x_display_unit="s", legend_layout=7, left_title="[kg/s]", fix_time_range_value=0, zoom_x=(0, 120), zoom_y_l=(1.7813, 1.782)),
Plot(y=["pumpCooling2.m_flow"], colors=["4278190335"])})
})));
  Modelica.Blocks.Sources.RealExpression realExpression3(y = Rev * Modelica.Constants.pi / 30) 
    annotation (Placement(transformation(origin = {-45.0802139037433, -35.87165775401065},
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  Modelica.Mechanics.Rotational.Sources.Speed speed2 
    annotation (Placement(transformation(origin = {-11.080213903743314, -35.87165775401065},
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TAThermalSystem.PumpAndFan.PumpCooling pumpCooling2(
    V(displayUnit = "l") = 0.0001,
    redeclare package Medium = TYBase.Media_Extend.GW50) annotation (Placement(transformation(origin = {4.919786096256686, 16.128342245989323},
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TAThermalSystem.Sources.Coolant.Coolant_pT Coolant_pT4(p = 100000) 
    annotation (Placement(transformation(origin = {-25.0802139037433, 16.128342245989323},
      extent = {{10.0, -10.0}, {-10.0, 10.0}})));
  TAThermalSystem.Sources.Coolant.Coolant_pT Coolant_pT5(p = p_out) 
    annotation (Placement(transformation(origin = {34.919786096256686, 16.128342245989323},
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
equation
  connect(realExpression3.y, speed2.w_ref) 
    annotation (Line(origin = {-31.080213903743285, -35.87165775401066},
      points = {{-3.0, 0.0}, {8.0, 0.0}},
      color = {0, 0, 127}));
  connect(pumpCooling2.flange, speed2.flange) 
    annotation (Line(origin = {1.9197860962567148, -14.871657754010677},
      points = {{3.0, 21.0}, {3.0, -23.0}, {-3.0, -23.0}, {-3.0, -21.0}},
      color = {0, 0, 0}));
  connect(Coolant_pT4.port_a, pumpCooling2.a) 
    annotation (Line(origin = {-10.080213903743285, 16.128342245989337},
      points = {{-25.0, 0.0}, {5.0, 0.0}},
      color = {0, 0, 128},
      thickness = 1.0));
  connect(pumpCooling2.b, Coolant_pT5.port_a) 
    annotation (Line(origin = {19.919786096256715, 16.128342245989337},
      points = {{-5.0, 0.0}, {25.0, 0.0}},
      color = {0, 0, 128},
      thickness = 1.0));
end CoolingPump;