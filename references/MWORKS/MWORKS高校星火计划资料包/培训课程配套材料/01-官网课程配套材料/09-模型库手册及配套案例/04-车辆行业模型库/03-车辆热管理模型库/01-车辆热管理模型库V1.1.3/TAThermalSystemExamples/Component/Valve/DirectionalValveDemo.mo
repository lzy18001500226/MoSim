model DirectionalValveDemo "电控换向阀案例"
  extends TAThermalSystem.Utilities.Icons.BasicIcons.Example;
  TAThermalSystem.Valves.HydraulicValve.DirectionalValves.DV2P3W dV2P3W 
    annotation(Placement(transformation(origin = {3.0531029999999992, 2.147118},
    extent = {{-21.961246, -8}, {11.85504, 7.852882}})));
  Modelica.Blocks.Sources.Ramp ramp(height = 40, duration = 10, startTime = 2) 
    annotation(Placement(transformation(origin = {-70.000000, 0.000000}, extent = {{-10.000000, -10.000000}, {10.000000, 10.000000}})));
  TAThermalSystem.Sources.Coolant.Coolant_pT coolant_pT 
    annotation(Placement(transformation(origin = {-30, -30},
    extent = {{10, -10}, {-10, 10}})));
  TAThermalSystem.Sources.Coolant.Coolant_tank coolant_tank 
    annotation(Placement(transformation(origin = {10.000000, -30.000000}, extent = {{-10.000000, -10.000000}, {10.000000, 10.000000}})));
  TAThermalSystem.Sources.Coolant.Coolant_pT coolant_pT1(p = 4.999999999999999e5) 
    annotation(Placement(transformation(origin = {-30.000000000000004, 34.147118},
    extent = {{10, -10}, {-10, 10}})), __MWORKS(BlockSystem(StateMachine)));
  annotation(Diagram(coordinateSystem(extent={{-100,-100},{100,100}},
grid={2,2})), experiment(Algorithm = Dassl, Interval = 0.01, StartTime = 0, StopTime = 20, Tolerance = 0.0001), __MWORKS(ContinueSimConfig(SaveContinueFile = "false", SaveBeforeStop = "false", NumberBeforeStop = 1, FixedContinueInterval = "false", ContinueIntervalLength = 20, ContinueTimeVector),ResultViewerManager(resultViewers={
ResultViewer(name="1", executeTrigger=executeTrigger.SimulationFinished, commands={
CreatePlot(id=1, x_display_unit="s", legend_layout=7, left_title="[kg/s]", fix_time_range_value=0, zoom_x=(0, 20), zoom_y_l=(-0.04, 0.04)),
Plot(y=["dV2P3W.A.m_flow", "dV2P3W.P.m_flow", "dV2P3W.T.m_flow"], colors=["4278190335", "4294901760", "4278222848"])})
})),Protection(access=Access.nonPackageDuplicate),Documentation(link="modelica://TAThermalSystem/Resource/Doc/DirectionalValveDemo.html"
));
equation
  connect(ramp.y, dV2P3W.signal) 
    annotation(Line(origin = {-39, 0},
    points = {{-20, 0}, {19.817666335779574, 0}, {19.817666335779574, 0.6693571687084017}},
    color = {0, 0, 127}));
  connect(coolant_pT.port_a, dV2P3W.P) 
    annotation(Line(origin = {-10, -18},
    points = {{-10, -12}, {10.230245704558278, -12}, {10.230245704558278, 12.147117999999999}},
    color = {0, 170, 255},
    thickness = 1));
  connect(coolant_tank.port_a, dV2P3W.T) 
    annotation(Line(origin = {8, -18},
    points = {{2, -12}, {2, 12.147117999999999}, {-2.946897082824, 12.147117999999999}},
    color = {0, 170, 255},
    thickness = 1));
  connect(coolant_pT1.port_a, dV2P3W.A) 
    annotation(Line(origin = {-10, 22},
    points = {{-10.000000000000004, 12.147117999999999}, {10.350881431321273, 12.147117999999999}, {10.350881431321273, -11.647021052136814}},
    color = {0, 170, 255},
    thickness = 1));
  end DirectionalValveDemo;