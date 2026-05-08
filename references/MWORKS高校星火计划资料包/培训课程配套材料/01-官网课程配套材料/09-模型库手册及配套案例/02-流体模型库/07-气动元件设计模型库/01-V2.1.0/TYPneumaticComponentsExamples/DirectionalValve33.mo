model DirectionalValve33 "三位三通换向阀"
  annotation (Documentation(link = "modelica://TYPneumaticComponents/Resources/HTML/DirectionalValve33.html"), Diagram(coordinateSystem(extent = {{-120.0, -100.0}, {120.0, 100.0}}, 
    grid = {2.0, 2.0})), 
    Icon(coordinateSystem(extent = {{-100.0, -100.0}, {100.0, 100.0}}, 
      grid = {2.0, 2.0}), graphics = {Polygon(origin = {-7.105427357601002e-15, 33.0}, 
      lineColor = {0, 98, 98}, 
      fillColor = {0, 98, 98}, 
      fillPattern = FillPattern.Solid, 
      points = {{-64.0, 1.0}, {0.0, 37.0}, {64.0, 1.0}, {0.0, -37.0}}), Line(origin = {0.0, -12.0}, 
      points = {{-62.0, 18.0}, {0.0, -18.0}, {62.0, 18.0}}, 
      color = {0, 98, 98}, 
      thickness = 5.0), Line(origin = {7.105427357601002e-15, -39.99999999999999}, 
      points = {{-62.0, 18.0}, {0.0, -18.0}, {62.0, 18.0}}, 
      color = {0, 98, 98}, 
      thickness = 5.0)}), 
    experiment(StartTime = 0, StopTime = 5, Interval = 0.01, Algorithm = "Dassl", Tolerance = 0.0001, DoublePrecision = true, StoreEventValue = true),Protection(access=Access.nonPackageDuplicate),__MWORKS(ResultViewerManager(resultViewers={
ResultViewer(name="1", executeTrigger=executeTrigger.SimulationFinished, commands={
CreatePlot(id=1, x_display_unit="s", legend_layout=7, left_title_type=2, left_title="力[N]", bottom_title_type=2, bottom_title="时间/s
", fix_time_range_value=0, zoom_x=(0, 5), zoom_y_l=(-400, 400)), 
Plot(y=["force.f"], colors=["4278190335"]), 
CreatePlot(id=-1, x_display_unit="s", legend_layout=7, left_title_type=2, left_title="位移[mm]", bottom_title_type=2, bottom_title="时间/s
", fix_time_range_value=0, sub_plot=(2, 1), zoom_x=(0, 5), zoom_y_l=(-3, 3)), 
Plot(y=["massWithStopAndFriction.s"], colors=["4278190335"]), 
CreatePlot(id=2, x="massWithStopAndFriction.s", x_display_unit="mm", legend_layout=7, left_title_type=2, left_title="质量流量[kg/s]", bottom_title_type=2, bottom_title="阀芯位移/mm", fix_time_range_value=0, zoom_x=(-2, 2), zoom_y_l=(-0.02, 0.03)), 
Plot(y=["gasVolumeV1.m_flow_B"], colors=["4294901760"])})
})));
  Modelica.Blocks.Sources.TimeTable timeTable(table = {{0.0, 0.0}, {1, 0}, {2, -300}, {4, 300}, {5, 0}, {6, 0}}) 
    annotation (Placement(transformation(origin = {-96.00000000000001, 32.0}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  Modelica.Mechanics.Translational.Sources.Force force 
    annotation (Placement(transformation(origin = {-62.0, 32.0}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYPneumaticComponents.Pistons.SpringPiston springPiston(len0 = 0.05, f_0 = 20, s_0 = 0, k0 = 50000, reverse = true) 
    annotation (Placement(transformation(origin = {-27.999999999999986, 32.0}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYPneumaticComponents.SlideValveSpool.AnnularOrificeSpool annularOrificeSpool(reverse = false, InterfaceSwitchB = true) 
    annotation (Placement(transformation(origin = {-5.329070518200751e-15, 32.0}, 
      extent = {{10.0, -10.0}, {-10.0, 10.0}})));
  Modelica.Mechanics.Translational.Components.MassWithStopAndFriction massWithStopAndFriction(m = 0.05, F_prop = 0, F_Coulomb = 0, F_Stribeck = 0, smax = 0.002, smin = -0.002) 
    annotation (Placement(transformation(origin = {28.0, 32.0}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYPneumaticComponents.SlideValveSpool.AnnularOrificeSpool annularOrificeSpool1(reverse = true, InterfaceSwitchB = true) 
    annotation (Placement(transformation(origin = {56.000000000000014, 32.0}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYPneumaticComponents.Pistons.SpringPiston springPiston1(reverse = false, len0 = 0.05, f_0 = 20, s_0 = 0, k0 = 50000, InterfaceSwitch = true) 
    annotation (Placement(transformation(origin = {90.00000000000003, 32.0}, 
      extent = {{10.0, -10.0}, {-10.0, 10.0}})));
  TYPneumaticComponents.Auxiliaries.GasVolumeV gasVolumeV(T(start = 293), V0(displayUnit = "l") = 0.001, kth = 500, Model = "Thermal Exchange Model") 
    annotation (Placement(transformation(origin = {-33.23076154806492, 8.000000000000007}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYPneumaticComponents.Sources.Surroundings surroundings 
    annotation (Placement(transformation(origin = {-2.037228254663372, 8.000000000000007}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYPneumaticComponents.FlowControlValves.CqOrifice cqOrifice(A = 1e-6) 
    annotation (Placement(transformation(origin={16.00559300873907,-24}, 
extent={{-10,-10},{10,10}})));
  TYPneumaticComponents.Auxiliaries.GasVolumeV gasVolumeV1(n_ports = 2, T(start = 293), kth = 500, V0(displayUnit = "l") = 0.001, Model = "Thermal Exchange Model") 
    annotation (Placement(transformation(origin={48.969238451935084,-10.000000000000021}, 
extent={{-10,-10},{10,10}})));
  TYPneumaticComponents.Sources.PressureSource pressureSource(constantPressure = 5.987e5) 
    annotation (Placement(transformation(origin={80,-2}, 
extent={{-10,-10},{10,10}}, 
rotation=90)));
  TYPneumatics.Valves.FlowControlValves.VarThrottleValve varThrottleValve 
    annotation (Placement(transformation(origin = {49.00279650436953, -46.000000000000014}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
      rotation = -90.0)));
  TYPneumaticComponents.Sources.Surroundings surroundings1 
    annotation (Placement(transformation(origin = {49.00279650436953, -70.00000000000003}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  Modelica.Blocks.Sources.Constant const 
    annotation (Placement(transformation(origin = {16.00559300873907, -43.00000000000002}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
equation
  connect(force.flange, springPiston.flange_a) 
    annotation (Line(origin = {-45.000000000000014, 32.0}, 
      points = {{-6.999999999999986, 0.0}, {6.910260869565228, 0.0}}, 
      color = {0, 127, 0}));
  connect(springPiston.flange_b, annularOrificeSpool.flange_b) 
    annotation (Line(origin = {-13.999999999999993, 32.0}, 
      points = {{-3.782956521739095, 0.0}, {3.782956521739088, 0.0}}, 
      color = {0, 127, 0}));
  connect(annularOrificeSpool.flange_a, massWithStopAndFriction.flange_a) 
    annotation (Line(origin = {14.00000000000001, 32.0}, 
      points = {{-3.9102608695652155, 0.0}, {3.9999999999999893, 0.0}}, 
      color = {0, 127, 0}));
  connect(gasVolumeV.portV_B[1], springPiston.portV_A) 
    annotation (Line(origin = {-32.99999999999999, 14.000000000000004}, 
      points = {{-0.20000000000000995, 0.9468164794007574}, {-0.19999999999999574, 7.9999999999999964}}, 
      color = {90, 229, 225}));
  connect(surroundings.port_A, annularOrificeSpool.port_B) 
    annotation (Line(origin = {-1.9999999999999893, 17.000000000000004}, 
      points = {{-9.547918011776346e-15, -4.015051227968694}, {-1.5987211554602254e-14, 4.9999999999999964}}, 
      color = {90, 229, 225}));
  connect(annularOrificeSpool1.flange_b, springPiston1.flange_b) 
    annotation (Line(origin = {73.0, 32.0}, 
      points = {{-6.782956521739081, 0.0}, {6.7829565217391234, 0.0}}, 
      color = {0, 127, 0}));
  connect(varThrottleValve.port_B, surroundings1.port_A) 
    annotation (Line(origin = {49.00559300873906, -61.000000000000014}, 
      points = {{-0.0027965043695346026, 5.0}, {0.034431750293840935, -4.015051227968712}}, 
      color = {90, 229, 225}, 
      thickness = 0.5));
  connect(const.y, varThrottleValve.u) 
    annotation (Line(origin = {35.00559300873907, -43.00000000000001}, 
      points = {{-8.0, -1.4210854715202004e-14}, {8.59720349563046, -7.105427357601002e-15}}, 
      color = {0, 0, 127}));
  connect(gasVolumeV1.port_A, varThrottleValve.port_A) 
    annotation (Line(origin={49.00000000000001,-27.999999999999993}, 
points={{-0.002796504369541708,10.977677902621693},{-0.002796504369541708,-8.000000000000021},{0.0027965043695203917,-8.000000000000021}}, 
color={90,229,225}));
  connect(massWithStopAndFriction.flange_b, annularOrificeSpool1.flange_a) 
    annotation (Line(origin = {42.00000000000001, 32.0}, 
      points = {{-4.000000000000007, 0.0}, {3.9102608695652066, 0.0}}, 
      color = {0, 127, 0}));
  connect(timeTable.y, force.f) 
    annotation (Line(origin = {-98.99999999999997, 32.0}, 
      points = {{13.999999999999957, 0.0}, {24.99999999999997, 0.0}}, 
      color = {0, 0, 127}));
  connect(annularOrificeSpool.portV_A, gasVolumeV1.portV_B[1]) 
    annotation (Line(origin={28.000000000000004,7.999999999999947}, 
points={{-21.000000000000007,14.000000000000053},{-21.000000000000007,2},{20.999999999999996,2},{20.999999999999996,-11.053183520599214}}, 
color={28,193,208}));
  connect(annularOrificeSpool1.portV_A, gasVolumeV1.portV_B[2]) 
    annotation (Line(origin={49,7.999999999999947}, 
points={{1.4210854715202004e-14,14.000000000000053},{1.4210854715202004e-14,-11.053183520599214},{0,-11.053183520599214}}, 
color={28,193,208}));
  connect(gasVolumeV.port_A, cqOrifice.port_A) 
  annotation(Line(origin={-14,-11}, 
points={{-19.202796504369537,11.977677902621728},{-19.202796504369537,-13},{20.00559300873907,-13}}, 
color={28,193,208}));
  connect(cqOrifice.port_B, varThrottleValve.port_A) 
  annotation(Line(origin={38,-29}, 
points={{-11.99440699126093,5},{11.002796504369527,5},{11.002796504369527,-7.000000000000014}}, 
color={28,193,208}));
  connect(springPiston1.port_A, varThrottleValve.port_A) 
  annotation(Line(origin={72,-7}, 
  points={{23.20000000000003,29},{23.20000000000003,-17},{-22.997203495630473,-17},{-22.997203495630473,-29.000000000000014}}, 
  color={28,193,208}));
  connect(annularOrificeSpool1.port_B, pressureSource.port_B) 
  annotation(Line(origin={69,14}, 
  points={{-10.999999999999986,8},{-10.999999999999986,0},{11,0},{11,-8}}, 
  color={28,193,208}));
end DirectionalValve33;