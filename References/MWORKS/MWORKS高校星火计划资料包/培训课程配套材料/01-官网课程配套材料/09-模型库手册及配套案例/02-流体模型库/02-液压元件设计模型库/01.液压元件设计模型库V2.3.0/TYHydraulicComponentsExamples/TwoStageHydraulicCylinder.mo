model TwoStageHydraulicCylinder "二级液压缸"
  annotation(Documentation(link = "modelica://TYHydraulicComponents/Resources/HTML/TwoStageHydraulicCylinder.html"), Diagram(coordinateSystem(extent = {{-120, -100}, {120, 100}}, 
    grid = {2, 2})), experiment(Algorithm = Dassl, InlineIntegrator = false, InlineStepSize = false, StartTime = 0, StopTime = 80, Tolerance = 0.0001, Interval = 0.01), __MWORKS(ContinueSimConfig(SaveContinueFile = "false", SaveBeforeStop = "false", NumberBeforeStop = 1, FixedContinueInterval = "false", ContinueIntervalLength = 26.67, ContinueTimeVector),ResultViewerManager(resultViewers={
ResultViewer(name="play", executeTrigger=executeTrigger.SimulationFinished, commands={
CreatePlot(id=1, x_display_unit="s", legend_layout=7, left_title_type=2, left_title="压力[bar]", bottom_title_type=2, bottom_title="时间[s]", right_title_type=2, fix_time_range_value=0, zoom_x=(0, 80), zoom_y_l=(-50, 250)), 
Plot(legends=["液压缸入口压力[bar]", "液压缸出口压力[bar]"], y=["fixedBodyPiston.p", "fixedBodyPiston1.p"], colors=["4278190335", "4294901760"]), 
CreatePlot(id=2, x_display_unit="s", legend_layout=7, left_title_type=2, left_title="位移[m]", bottom_title_type=2, bottom_title="时间[s]", right_title_type=2, fix_time_range_value=0, zoom_x=(0, 80), zoom_y_l=(-0.2, 1.2)), 
Plot(legends=["液压缸位移 [m]"], y=["mass.s"], colors=["4278190335"]), 
CreatePlot(id=3, x_display_unit="s", legend_layout=7, left_title_type=2, left_title="体积流量[l/min]", bottom_title_type=2, bottom_title="时间[s]", right_title_type=2, fix_time_range_value=0, zoom_x=(0, 80), zoom_y_l=(-60, 80)), 
Plot(legends=["液压缸第一级流量 [l/min]", "液压缸第二级流量 [l/min]"], y=["fixedBodyPiston.q", "fixedBodyPiston2.q"], colors=["4278190335", "4294901760"])})
}),CategorizeSampleTime), Icon(coordinateSystem(extent = {{-100, -100}, {100, 100}}, 
    grid = {2, 2}), graphics = {Polygon(origin = {0, 31}, 
    lineColor = {0, 0, 255}, 
    fillColor = {0, 0, 255}, 
    fillPattern = FillPattern.Solid, 
    points = {{-64, 1}, {0, 37}, {64, 1}, {0, -37}}), Line(origin = {7.10543e-15, -14}, 
    points = {{-62, 18}, {0, -18}, {62, 18}}, 
    color = {0, 0, 255}, 
    thickness = 5), Line(origin = {1.42109e-14, -42}, 
    points = {{-62, 18}, {0, -18}, {62, 18}}, 
    color = {0, 0, 255}, 
    thickness = 5)}),Protection(access=Access.nonPackageDuplicate));
  TYHydraulicComponents.Pistons.FixedBodyPiston fixedBodyPiston(dr = 0, ds = 0.2) 
    annotation(Placement(transformation(origin = {-102.82, 71}, 
    extent = {{-10, -10}, {10, 10}})));
  TYHydraulicComponents.Pistons.FixedBodyPiston fixedBodyPiston1(useSupportT = false, reverse = true, dr = 0.18, ds = 0.2) 
    annotation(Placement(transformation(origin = {-70.8199, 71}, 
    extent = {{10, -10}, {-10, 10}})));
  TYHydraulicComponents.Pistons.FixedBodyPiston fixedBodyPiston2(InterfaceSwitch = false, useSupportT = true, ds = 0.16, dr = 0) 
    annotation(Placement(transformation(origin={-22,80}, 
extent={{-10,-10},{10,10}})));
  TYHydraulicComponents.Pistons.FixedBodyPiston fixedBodyPiston3(useSupportT = true, reverse = true, ds = 0.16, dr = 0.08) 
    annotation(Placement(transformation(origin={9.8199,80}, 
extent={{10,-10},{-10,10}})));
  TYMechanics.Translational.Components.Mass mass(m = 100) 
    annotation(Placement(transformation(origin={70,71}, 
extent={{-10,-10},{10,10}})));
  TYMechanics.Translational.Components.Fixed fixed 
    annotation(Placement(transformation(origin={112,48}, 
extent={{-10,-10},{10,10}}, 
rotation=90)));
  TYMechanics.Translational.Components.SpringDamper springDamper(d = 20000, k = 10000) 
    annotation(Placement(transformation(origin={98,71}, 
extent={{-10,-10},{10,10}})));
  TYHydraulicComponents.Auxiliaries.VolumeV volumeV(n_ports = 2) 
    annotation(Placement(transformation(origin = {-107.82, 8}, 
    extent = {{-10, -10}, {10, 10}})));
  TYHydraulicComponents.Auxiliaries.VolumeV volumeV2(n_ports = 2) 
    annotation(Placement(transformation(origin = {16, 26}, 
    extent = {{-10, -10}, {10, 10}})));
  TYHydraulicComponents.Sources.Tank tank(p_load = 4.999999999999999e5) 
    annotation(Placement(transformation(origin = {16.0301, -83}, 
    extent = {{-10, -10}, {10, 10}})));
  TYMechanics.Translational.Components.DoubleMassWithStop mAS30_1(fstick = 0, rvisc = 0, xmin = 0, xmax = 0.4, xmin2 = 0, xmax2 = 0.5, Kb = 1e11, Db = 1000000) 
    annotation(Placement(transformation(origin={41.6398,74.4}, 
extent={{-10,10},{10,-10}})));
  TYHydraulics.Valves.DirectionalValves.DirectionalValve34_O directionalValve34_O(ratedcurrent = 0.001, dpnom(displayUnit = "bar") = 10000) 
    annotation(Placement(transformation(origin = {-41.9199, -30}, 
    extent = {{-26.9, -10}, {14.8, 10}})));
  TYHydraulics.Sources.PressureSource pressureSource(constantPressure = 2e7) 
    annotation(Placement(transformation(origin = {-113.9699, -82}, 
    extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Sources.RealExpression realExpression(y = if time < 2 then 0 else if time < 30 then -1 else if time < 35 then 0 else if time < 80 then 1 else 0) 
    annotation(Placement(transformation(origin = {5.1801, -31.8}, 
    extent = {{10, -10}, {-10, 10}})));
  TYHydraulics.Valves.FlowValves.SymThrottleValve symThrottleValve(UseVolumeB = true) 
    annotation(Placement(transformation(origin = {-75.9699, -82}, 
    extent = {{-10, -10}, {10, 10}})));
  TYHydraulics.Valves.FlowValves.SymThrottleValve symThrottleValve1(UseVolumeB = true) 
    annotation(Placement(transformation(origin = {-29.9699, -82}, 
    extent = {{10, -10}, {-10, 10}})));
equation
  connect(springDamper.flange_b, fixed.flange) 
    annotation(Line(origin={120,57}, 
points={{-21.9999,14},{-8,14},{-8,-9}}, 
color={0,127,0}));
  connect(springDamper.flange_a, mass.flange_b) 
    annotation(Line(origin={85,77}, 
points={{13,-6},{-15,-6}}, 
color={0,127,0}));
  connect(fixedBodyPiston2.support_b, fixedBodyPiston3.support_b) 
    annotation(Line(origin={3,71}, 
points={{-15,0},{-3.1801,0}}, 
color={0,127,0}));
  connect(fixedBodyPiston1.flange_b, fixedBodyPiston.flange_b) 
    annotation(Line(origin = {-95.8199, 71}, 
    points = {{14.783, 0}, {3.21704, 0}}, 
    color = {0, 127, 0}));
  connect(volumeV.portV_B[1], fixedBodyPiston.portV_A) 
    annotation(Line(origin = {-107.82, 55}, 
    points = {{0, -40}, {0, 6}}, 
    color = {0, 127, 255}));
  connect(volumeV2.portV_B[2], fixedBodyPiston3.portV_A) 
    annotation(Line(origin={-14,53}, 
points={{30,-20},{30,17},{28.8199,17}}, 
color={0,127,255}));
  connect(volumeV2.portV_B[1], fixedBodyPiston1.portV_A) 
    annotation(Line(origin = {-52.8199, 49}, 
    points = {{68.8199, -16}, {68.8199, -1}, {-13, -1}, {-13, 12}}, 
    color = {0, 127, 255}));
  connect(volumeV.portV_B[2], fixedBodyPiston2.portV_A) 
    annotation(Line(origin={-82.8199,43}, 
points={{-25.0001,-28},{55.8199,-28},{55.8199,27}}, 
color={0,127,255}));
  connect(fixedBodyPiston2.flange_b, fixedBodyPiston3.flange_b) 
    annotation(Line(origin={3,80}, 
points={{-14.783,0},{-3.39714,0}}, 
color={0,127,0}));
  connect(fixedBodyPiston1.flange_a, fixedBodyPiston2.support_a) 
    annotation(Line(origin={-52.8199,72}, 
points={{-7.91026,-1},{20.8199,-1}}, 
color={0,127,0}));
  connect(volumeV.port_A, directionalValve34_O.port_A) 
    annotation(Line(origin = {-111.82, -9}, 
    points = {{4, 10}, {4, -1}, {61.9, -1}, {61.9, -11}}, 
    color = {0, 127, 255}));
  connect(directionalValve34_O.port_B, volumeV2.port_A) 
    annotation(Line(origin = {-42.8199, 2}, 
    points = {{-3.1, -22}, {-3.1, -12}, {58.8199, -12}, {58.8199, 17}}, 
    color = {0, 127, 255}));
  connect(directionalValve34_O.Signal, realExpression.y) 
    annotation(Line(origin = {-10.9699, -32}, 
    points = {{-14.95, 0.2}, {5.15, 0.2}}, 
    color = {0, 0, 127}));
  connect(symThrottleValve.port_A, pressureSource.port_B) 
    annotation(Line(origin = {-95.9699, -82}, 
    points = {{10, 0}, {-11, 0}}, 
    color = {0, 127, 255}));
  connect(symThrottleValve.port_B, directionalValve34_O.port_P) 
    annotation(Line(origin = {-60.9699, -61}, 
    points = {{-5, -21}, {11.05, -21}, {11.05, 21}}, 
    color = {0, 127, 255}));
  connect(tank.port_A, symThrottleValve1.port_A) 
    annotation(Line(origin = {-10.9699, -83}, 
    points = {{26.9699, 0.055914}, {-9, 0.055914}, {-9, 1}}, 
    color = {0, 127, 255}));
  connect(symThrottleValve1.port_B, directionalValve34_O.port_T) 
    annotation(Line(origin = {-34.9699, -61}, 
    points = {{-5, -21}, {-10.95, -21}, {-10.95, 21}}, 
    color = {0, 127, 255}));
  connect(fixedBodyPiston3.flange_a, mAS30_1.flange_a1) 
    annotation(Line(origin={26,78}, 
points={{-6.09036,2},{0,2},{0,-3.6},{15.6398,-3.6}}, 
color={0,127,0}));
  connect(mAS30_1.flange_b1, mass.flange_a) 
    annotation(Line(origin={56,74}, 
points={{-14.3602,0.4},{0,0.4},{0,-3},{14,-3}}, 
color={0,127,0}));
  connect(mAS30_1.flange_a2, fixedBodyPiston3.support_a) 
    annotation(Line(origin={26,71}, 
points={{15.6398,3.4},{-6.1801,3.4},{-6.1801,0}}, 
color={0,127,0}));

end TwoStageHydraulicCylinder;