model TankSystem "水箱系统"
  TYThermoFluidSys.Volumes.ExpansionTank expansionTank(
    p_start = 2e5, A = 1e-3 / 0.1, level_start = 0.05, static_head = false, redeclare package Medium = Modelica.Media.Water.StandardWater) 
    annotation(Placement(transformation(origin = {0, 60}, 
    extent = {{-10, -10}, {10, 10}})));
  TYThermoFluidSys.Junctions.Tjunction tjunction(redeclare package Medium = Modelica.Media.Water.StandardWater, flowSituation = TYThermoFluidSys.Utilities.Types.JunctionFlowSituation.Tjoin_Right, dp_1(m_flow_start = 9.63), dp_2(m_flow_start = -9.5), dp_3(m_flow_start = -0.13, dp_start = 400)) 
    annotation(Placement(transformation(origin = {46, 40}, extent = {{-10, -10}, {10, 10}})));
  TYThermoFluidSys.Pipelines.LumpPipe lumpPipe(friction(m_flow(start = {0.13})), L = 0.2, D(displayUnit = "m") = 1e-2, redeclare model HT = TYThermoFluidSys.Pipelines.Basic.HT_OnePhase.ConstantCoefficient(alpha0 = 160), redeclare model DP = TYThermoFluidSys.Pipelines.Basic.DP_OnePhase.ColebrookWhite, mflow_start = 0.13, dynamicMomentum = false, from_dp = false, p_start_in = 1.9e5, p_start_out = 1.6e5, T_start = 300, T_wall_start = 333.15, F = 0, redeclare package Medium = Modelica.Media.Water.StandardWater, A_heat = 0.1, CF_PressureLoss = 30, CF_HeatTransfer = 2) 
    annotation(Placement(transformation(origin = {46, -6}, extent = {{-10, 10}, {10, -10}}, rotation = -90)));
  TYThermoFluidSys.Boundaries.BoundaryTemperature boundaryTemperature(
    T = 333.15) 
    annotation(Placement(transformation(origin = {22, -6}, 
    extent = {{-9.999999999999998, -10}, {10, 10}})));
  TYThermoFluidSys.Junctions.Tjunction tjunction1(
    dp_1(m_flow_start = 9.5), dp_2(m_flow_start = -9.63), dp_3(m_flow_start = 0.15), flowSituation = TYThermoFluidSys.Utilities.Types.JunctionFlowSituation.Tjoin_Left, redeclare package Medium = Modelica.Media.Water.StandardWater) 
    annotation(Placement(transformation(origin = {46, -52}, extent = {{10, 10}, {-10, -10}})));
  TYThermoFluidSys.Machines.SuterPump suterPump(
    nr = 2379, qvr = 0.007, Hr = 55, A = 0.004, redeclare package Medium = Modelica.Media.Water.StandardWater) 
    annotation(Placement(transformation(origin = {-70, -31.599999999999998}, 
    extent = {{-10, -10}, {10, 10}}, 
    rotation = 90)));
  TYThermoFluidSys.Volumes.OnephaseVolume volume(p_start = 2e5, T_start = 293.15, redeclare package Medium = Modelica.Media.Water.StandardWater) 
    annotation(Placement(transformation(origin = {-70, 7}, extent = {{-10, -10}, {10, 10}}, rotation = 90)));
  TYThermoFluidSys.Boundaries.BoundarySpeed boundarySpeed(
    use_w_in = true, w = 255) 
    annotation(Placement(transformation(origin = {-96, -31.799999999999997}, 
    extent = {{-10, -10}, {10, 10}})));
  TYThermoFluidSys.Valves.SimpleControlValve controlValve(
    m_flow_start = 9.63, dp_nominal = 20000, m_flow_nominal = 9.63, dp_start = 12000, redeclare package Medium = Modelica.Media.Water.StandardWater) 
    annotation(Placement(transformation(origin = {-32, 43}, extent = {{-10, -10}, {10, 10}})));
  TYThermoFluidSys.Blocks.RealExpression realExpression(
    y = 1) 
    annotation(Placement(transformation(origin = {-70, 60}, 
    extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Sources.Sine sine(
    offset = 255, amplitude = 15, f = 0.1) 
    annotation(Placement(transformation(origin = {-130, -31.799999999999997}, 
    extent = {{-10, -10}, {10, 10}})));
  TYThermoFluidSys.Pipelines.LumpPipe lumpPipe1(friction(m_flow(start = {0.13})), L = 0.2, D = 1e-2, redeclare model HT = TYThermoFluidSys.Pipelines.Basic.HT_OnePhase.ConstantCoefficient(alpha0 = 160), redeclare model DP = TYThermoFluidSys.Pipelines.Basic.DP_OnePhase.LinearLoss(d0 = 1000, dp0 = 21000, m_flow0 = 9.3), mflow_start = 0.13, dynamicMomentum = false, from_dp = false, p_start_in = 1.9e5, p_start_out = 1.6e5, T_start = 300, T_wall_start = 333.15, F = 0, redeclare package Medium = Modelica.Media.Water.StandardWater, A_heat = 0.1, wallHeatTransfer = false) 
    annotation(Placement(transformation(origin = {84, -24.000000000000004}, 
    extent = {{10, 10}, {-10, -10}}, 
    rotation = 90)));
  TYThermoFluidSys.Valves.SimpleControlValve controlValve1(dp_nominal = 21000, m_flow_nominal = 9.3, m_flow_start = 9.3, redeclare package Medium = Modelica.Media.Water.StandardWater, dp_start = 21000) 
    annotation(Placement(transformation(origin = {84, 16}, 
    extent = {{10, 10}, {-10, -10}}, 
    rotation = 90)));
  TYThermoFluidSys.Blocks.RealExpression realExpression1(y = 1) 
    annotation(Placement(transformation(origin = {114, 16}, 
    extent = {{10, -10}, {-10, 10}})));
equation
  connect(tjunction.port_3, lumpPipe.portA) 
    annotation(Line(origin = {46, 5}, points = {{0, 25}, {0, -1}}, color = {0, 178, 226}));
  connect(lumpPipe.q, boundaryTemperature.port[1]) 
    annotation(Line(origin = {31, -6}, 
    points = {{10, 0}, {1, 0}}, 
    color = {191, 0, 0}));
  connect(lumpPipe.portB, tjunction1.port_3) 
    annotation(Line(origin = {46, -35}, points = {{0, 19}, {0, -7}}, color = {0, 178, 226}));
  connect(tjunction1.port_2, suterPump.port_a) 
    annotation(Line(origin = {-9, -39}, 
    points = {{45, -16}, {-61, -16}, {-61, -1.7999999999999972}}, 
    color = {0, 178, 226}));
  connect(suterPump.port_b, volume.port_a) 
    annotation(Line(origin = {-70, 1.1999999999999993}, 
    points = {{0, -22.399999999999995}, {0, -4.6}}, 
    color = {0, 178, 226}));
  connect(expansionTank.port_b, tjunction.port_1) 
    annotation(Line(
    origin = {21, 41}, points = {{-15.6, 9}, {-15.6, 2}, {14.799999999999997, 2}}, color = {0, 178, 226}));
  connect(boundarySpeed.flange, suterPump.flange_a) 
    annotation(Line(origin = {-85, -31.8}, 
    points = {{-1, 3.552713678800501e-15}, {6, 3.552713678800501e-15}}, 
    color = {0, 0, 0}));
  connect(expansionTank.port_a, controlValve.port_b) 
    annotation(Line(origin = {-13, 47}, points = {{8, 3}, {8, -3}, {-9, -3}, {-9, -4}}, color = {0, 178, 226}));
  connect(controlValve.port_a, volume.port_b) 
    annotation(Line(origin = {-48, 41}, points = {{6, 2}, {-22, 2}, {-22, -24}}, color = {0, 178, 226}));
  connect(realExpression.y, controlValve.opening) 
    annotation(Line(origin = {-37, 55}, 
    points = {{-22, 5}, {5, 5}, {5, -5}}, 
    color = {0, 0, 127}));
  connect(boundarySpeed.w_in, sine.y) 
    annotation(Line(origin = {-121, -31.799999999999997}, 
    points = {{13, 0}, {2, 0}}, 
    color = {0, 0, 127}));
  connect(tjunction.port_2, controlValve1.port_a) 
    annotation(Line(origin = {69, 39}, 
    points = {{-13, 4}, {15, 4}, {15, -13}}, 
    color = {0, 178, 226}));
  connect(controlValve1.opening, realExpression1.y) 
    annotation(Line(origin = {97, 16}, 
    points = {{-6, 0}, {6, 0}}, 
    color = {0, 0, 127}));
  connect(controlValve1.port_b, lumpPipe1.portA) 
    annotation(Line(origin = {84, -4}, 
    points = {{0, 10}, {0, -10.000000000000004}}, 
    color = {0, 178, 226}));
  connect(lumpPipe1.portB, tjunction1.port_1) 
    annotation(Line(origin = {70, -44}, 
    points = {{14, 10}, {14, -11}, {-13.799999999999997, -11}}, 
    color = {0, 178, 226}));
  annotation(Icon(coordinateSystem(extent = {{-100, -100}, {100, 100}}, 
    grid = {2, 2}), graphics = {Polygon(origin = {-7.105427357601002e-15, 33}, 
    lineColor = {0, 94, 138}, 
    fillColor = {0, 94, 138}, 
    fillPattern = FillPattern.Solid, 
    points = {{-64, 1}, {0, 37}, {64, 1}, {0, -37}}), Line(origin = {0, -12}, 
    points = {{-62, 18}, {0, -18}, {62, 18}}, 
    color = {0, 94, 138}, 
    thickness = 5), Line(origin = {7.105427357601002e-15, -39.99999999999999}, 
    points = {{-62, 18}, {0, -18}, {62, 18}}, 
    color = {0, 94, 138}, 
    thickness = 5)}), Diagram(coordinateSystem(extent = {{-100, -100}, {100, 100}}, 
    grid = {2, 2})), experiment(Algorithm = Dassl, NumberOfIntervals = 500, StartTime = 0, StopTime = 100, Tolerance = 1e-07), __MWORKS(ResultViewerManager(resultViewers={
ResultViewer(name="Result", executeTrigger=executeTrigger.SimulationFinished, commands={
CreatePlot(id=2, x_display_unit="s", legend_layout=1, left_title_type=2, left_title="质量流量/[kg/s]", bottom_title_type=2, bottom_title="时间/s", right_title_type=2, fix_time_range_value=0, zoom_x=(0, 100), zoom_y_l=(-2, 12)), 
Plot(legend=["管道(右)质量流量[kg/s]"], y=["lumpPipe1.portA.m_flow"], colors=["4278190335"]), 
CreatePlot(id=-1, x_display_unit="s", legend_layout=1, left_title_type=2, left_title="质量流量/[kg/s]", bottom_title_type=2, bottom_title="时间/s", right_title_type=2, fix_time_range_value=0, sub_plot=(1, 2), zoom_x=(0, 100), zoom_y_l=(-0.05, 0.2)), 
Plot(legend=["管道(右)质量流量[kg/s]"], y=["lumpPipe.m_flow"], colors=["4278190335"]), 
CreatePlot(id=-1, x_display_unit="s", legend_layout=1, left_title_type=2, left_title="功率/W", bottom_title_type=2, bottom_title="时间/s", right_title_type=2, fix_time_range_value=0, sub_plot=(2, 2), zoom_x=(0, 100), zoom_y_l=(0, 12000)), 
Plot(legend=["泵功 [W]"], y=["suterPump.P"], colors=["4278190335"]), 
CreatePlot(id=-1, x_display_unit="s", legend_layout=1, left_title_type=2, left_title="压降/bar", bottom_title_type=2, bottom_title="时间/s", right_title_type=2, fix_time_range_value=0, sub_plot=(2, 1), zoom_x=(0, 100), zoom_y_l=(-0.05, 0.3)), 
Plot(legend=["阀门(右)压降 [bar]"], y=["controlValve1.dp"], colors=["4278190335"])})
})), 
    Documentation(link = "modelica://TYThermoFluidSys/Resources/HTML/TankSystem.html"), Protection(access = Access.nonPackageDuplicate));
end TankSystem;