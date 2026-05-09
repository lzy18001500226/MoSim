model PressureRegulator "压力调节器"
  annotation(Icon(coordinateSystem(extent = {{-100.0, -100.0}, {100.0, 100.0}}, 
    grid = {2.0, 2.0}), graphics = {Polygon(origin = {-7.105427357601002e-15, 33.0}, 
    lineColor = {167, 98, 0}, 
    fillColor = {167, 98, 0}, 
    fillPattern = FillPattern.Solid, 
    points = {{-64.0, 1.0}, {0.0, 37.0}, {64.0, 1.0}, {0.0, -37.0}}), Line(origin = {0.0, -12.0}, 
    points = {{-62.0, 18.0}, {0.0, -18.0}, {62.0, 18.0}}, 
    color = {167, 98, 0}, 
    thickness = 5.0), Line(origin = {7.105427357601002e-15, -39.99999999999999}, 
    points = {{-62.0, 18.0}, {0.0, -18.0}, {62.0, 18.0}}, 
    color = {167, 98, 0}, 
    thickness = 5.0)}), 
    experiment(Algorithm = Dassl, Interval = 0.001, StartTime = 0, StopTime = 10, Tolerance = 1e-06), 
    Diagram(coordinateSystem(extent = {{-100.0, -100.0}, {100.0, 100.0}}, 
    grid = {2.0, 2.0})), 
    Documentation(link = "modelica://TYThermalHydraulicComponents/Resources/HTML/PressureRegulator.html"),Protection(access=Access.nonPackageDuplicate),__MWORKS(ResultViewerManager(resultViewers={
ResultViewer(name="1", executeTrigger=executeTrigger.SimulationFinished, commands={
CreatePlot(id=1, x_display_unit="s", legend_layout=7, left_title_type=2, left_title="输入信号", bottom_title_type=2, bottom_title="时间/s", fix_time_range_value=0, zoom_x=(0, 10), zoom_y_l=(-0.2, 1.2)), 
Plot(y=["vSymThrottleValve.u"], colors=["4278190335"]), 
CreatePlot(id=-1, x_display_unit="s", legend_layout=13, left_title_type=2, left_title="位移/mm", bottom_title_type=2, bottom_title="时间/s", fix_time_range_value=0, sub_plot=(1, 2), zoom_x=(0, 10), zoom_y_l=(-0.2, 0.8)), 
Plot(y=["massWithStopAndFriction.s"], colors=["4278190335"]), 
CreatePlot(id=-1, x_display_unit="s", legend_layout=7, left_title_type=2, left_title="体积流量（l/min）", bottom_title_type=2, bottom_title="时间/s", fix_time_range_value=0, sub_plot=(2, 2), zoom_x=(0, 10), zoom_y_l=(-20, 140)), 
Plot(y=["annularOrificeSpool.Q"], colors=["4278190335"]), 
CreatePlot(id=-1, x_display_unit="s", legend_layout=7, left_title_type=2, left_title="压力/Bar
", bottom_title_type=2, bottom_title="时间/s", fix_time_range_value=0, sub_plot=(2, 1), zoom_x=(0, 10), zoom_y_l=(-10, 70)), 
Plot(y=["fixedBodyPiston.p"], colors=["4278190335"])})
})));
  TYThermalHydraulicComponents.Pistons.FixedBodyPiston fixedBodyPiston(reverse = true, dr = 0, 
  redeclare model Medium = TYOilMedia.ThermalHydraulicOil.Types._5W30) 
    annotation(Placement(transformation(origin = {-68.0, 20.0}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYThermalHydraulicComponents.DiaphragmLeakageSealings.ViscousFrictionAndLeakage viscousFrictionAndLeakageSpool(reverse = true, dc = 1e-5, L_c = 0.01, 
  redeclare model Medium = TYOilMedia.ThermalHydraulicOil.Types._5W30, InterfaceSwitchA = true, InterfaceSwitchB = true) 
    annotation(Placement(transformation(origin = {-38.0, 20.0}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYThermalHydraulicComponents.SlideValveSpool.AnnularOrificeSpool annularOrificeSpool(dr = 0.004, 
  redeclare model Medium = TYOilMedia.ThermalHydraulicOil.Types._5W30, 
    InterfaceSwitchB = true) 
    annotation(Placement(transformation(origin = {-8.0, 19.999999999999993}, 
    extent = {{10.0, -10.0}, {-10.0, 10.0}})));
  Modelica.Mechanics.Translational.Components.MassWithStopAndFriction massWithStopAndFriction(smax = 0.0007, smin = 0, F_prop = 100, F_Coulomb = 0, F_Stribeck = 0, fexp = 0, m = 0.03) 
    annotation(Placement(transformation(origin = {44.00000000000001, 19.999999999999993}, 
    extent = {{10.0, -10.0}, {-10.0, 10.0}})));
  TYThermalHydraulicComponents.Pistons.SpringPiston springPiston(dr = 0, f_0 = 200, s_0 = 0, k0 = 10000) annotation(Placement(transformation(origin = {74.00000000000001, 19.999999999999993}, 
    extent = {{10.0, -10.0}, {-10.0, 10.0}})));
  TYThermalHydraulicComponents.Sources.Tank tank(p_load = 0, T_load = 293.15) annotation(Placement(transformation(origin = {79.00000000000001, -14.0}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYThermalHydraulicComponents.Auxiliaries.VolumeV volumeV annotation(Placement(transformation(origin = {79.00000000000001, -1.9999999999999964}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYThermalHydraulicComponents.Sources.PressureSource pressureSource(constantPressure = 1e7, 
  redeclare model Medium = TYOilMedia.ThermalHydraulicOil.Types._5W30) 
    annotation(Placement(transformation(origin = {13.0, -28.0}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
    rotation = 90.0)));
  TYThermalHydraulicComponents.Pistons.Piston piston(reverse = true, dr = 0.004, 
  redeclare model Medium = TYOilMedia.ThermalHydraulicOil.Types._5W30) 
    annotation(Placement(transformation(origin = {18.000000000000004, 19.999999999999993}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYThermalHydraulicComponents.Auxiliaries.VolumeV volumeV1(n_ports = 2, 
  redeclare model Medium = TYOilMedia.ThermalHydraulicOil.Types._5W30) 
    annotation(Placement(transformation(origin = {13.0, -4.0000000000000036}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYThermalHydraulicComponents.Auxiliaries.Volume volume(V0 = 0.0001, 
  redeclare model Medium = TYOilMedia.ThermalHydraulicOil.Types._5W30) 
    annotation(Placement(transformation(origin = {-33.06813666717149, -15.999999999999998}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYThermalHydraulics.Valves.FlowValves.VSymThrottleValve vSymThrottleValve(diam = 0.008, 
  redeclare model Medium = TYOilMedia.ThermalHydraulicOil.Types._5W30) annotation(Placement(transformation(origin = {-33.06813666717149, -46.0}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
    rotation = -90.0)));
  TYThermalHydraulicComponents.Sources.Tank tank1(p_load = 0, T_load = 293.15, 
  redeclare model Medium = TYOilMedia.ThermalHydraulicOil.Types._5W30) 
    annotation(Placement(transformation(origin = {-33.06813666717149, -68.0}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYThermalHydraulicComponents.Auxiliaries.SymOrifice symOrifice(diam = 0.0005, 
  redeclare model Medium = TYOilMedia.ThermalHydraulicOil.Types._5W30) 
    annotation(Placement(transformation(origin = {-56.0, -22.0}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYThermalHydraulicComponents.Auxiliaries.VolumeV volumeV2(V0 = 2e-6, 
  redeclare model Medium = TYOilMedia.ThermalHydraulicOil.Types._5W30) 
    annotation(Placement(transformation(origin = {-73.0, -4.0}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  Modelica.Blocks.Sources.TimeTable Signal(table = {{0.0, 0.0}, {5, 1}, {10, 0}}) 
    annotation(Placement(transformation(origin = {-66.0, -42.93978494623656}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
equation
  connect(fixedBodyPiston.flange_b, viscousFrictionAndLeakageSpool.flange_a) 
    annotation(Line(origin = {-53.0, 20.0}, 
    points = {{-5.0, 0.0}, {5.0, 0.0}}, 
    color = {0, 127, 0}));
  connect(viscousFrictionAndLeakageSpool.flange_b, annularOrificeSpool.flange_b) 
    annotation(Line(origin = {-23.0, 20.0}, 
    points = {{-5.0, 0.0}, {5.0, 0.0}}, 
    color = {0, 127, 0}));
  connect(massWithStopAndFriction.flange_a, springPiston.flange_b) 
    annotation(Line(origin = {59.00000000000001, 20.0}, 
    points = {{-5.0, 0.0}, {5.0, 0.0}}, 
    color = {0, 127, 0}));
  connect(volumeV.portV_B[1], springPiston.portV_A) 
    annotation(Line(origin = {79.0, 8.0}, 
    points = {{0.0, -3.0}, {-1.0, -3.0}, {-1.0, 2.0}, {0.0, 2.0}}, 
    color = {255, 170, 0}));
  connect(tank.port_A, volumeV.port_A) 
    annotation(Line(origin = {79.0, -11.0}, 
    points = {{0.0, -3.0}, {0.0, 2.0}}, 
    color = {255, 170, 0}));
  connect(piston.flange_b, massWithStopAndFriction.flange_b) 
    annotation(Line(origin = {31.0, 20.0}, 
    points = {{-3.0, 0.0}, {3.0, 0.0}}, 
    color = {0, 127, 0}));
  connect(annularOrificeSpool.flange_a, piston.flange_a) 
    annotation(Line(origin = {5.0, 20.0}, 
    points = {{-3.0, 0.0}, {3.0, 0.0}}, 
    color = {0, 127, 0}));
  connect(pressureSource.port_B, volumeV1.port_A) 
    annotation(Line(origin = {13.0, -15.0}, 
    points = {{0.0, -5.0}, {0.0, 4.0}}, 
    color = {255, 170, 0}));
  connect(volumeV1.portV_B[1], piston.portV_A) 
    annotation(Line(origin = {13.0, 7.0}, 
    points = {{0.0, -4.0}, {0.0, 3.0}}, 
    color = {255, 170, 0}));
  connect(annularOrificeSpool.portV_A, volumeV1.portV_B[2]) 
    annotation(Line(origin = {6.0, 7.0}, 
    points = {{-7.0, 3.0}, {-7.0, -4.0}, {7.0, -4.0}}, 
    color = {255, 170, 0}));
  connect(volume.port_B, viscousFrictionAndLeakageSpool.port_B) 
    annotation(Line(origin = {-33.0, 1.0}, 
    points = {{0.0, -10.0}, {0.0, 9.0}}, 
    color = {255, 170, 0}));
  connect(volume.port_A, annularOrificeSpool.port_B) 
    annotation(Line(origin = {-21.0, -9.0}, 
    points = {{-12.0, -14.0}, {11.0, -14.0}, {11.0, 19.0}}, 
    color = {255, 170, 0}));
  connect(vSymThrottleValve.port_A, volume.port_A) 
    annotation(Line(origin = {-33.0, -29.0}, 
    points = {{0.0, -7.0}, {0.0, 6.0}}, 
    color = {255, 170, 0}));
  connect(tank1.port_A, vSymThrottleValve.port_B) 
    annotation(Line(origin = {-33.0, -62.0}, 
    points = {{0.0, -6.0}, {0.0, 6.0}}, 
    color = {255, 170, 0}));
  connect(symOrifice.port_B, volume.port_A) 
    annotation(Line(origin = {-41.0, -22.0}, 
    points = {{-5.0, 0.0}, {8.0, 0.0}, {8.0, -1.0}}, 
    color = {255, 170, 0}));
  connect(fixedBodyPiston.portV_A, volumeV2.portV_B[1]) 
    annotation(Line(origin = {-73.0, 7.0}, 
    points = {{0.0, 3.0}, {0.0, -4.0}}, 
    color = {255, 170, 0}));
  connect(volumeV2.port_A, viscousFrictionAndLeakageSpool.port_A) 
    annotation(Line(origin = {-58.0, -3.0}, 
    points = {{-15.0, -8.0}, {15.0, -8.0}, {15.0, 13.0}}, 
    color = {255, 170, 0}));
  connect(volumeV2.port_A, symOrifice.port_A) 
    annotation(Line(origin = {-69.0, -16.0}, 
    points = {{-4.0, 5.0}, {-4.0, -6.0}, {3.0, -6.0}}, 
    color = {255, 170, 0}));
  connect(vSymThrottleValve.u, Signal.y) 
    annotation(Line(origin = {-47.0, -43.0}, 
    points = {{9.0, 0.0}, {-8.0, 0.0}}, 
    color = {0, 0, 127}));
end PressureRegulator;