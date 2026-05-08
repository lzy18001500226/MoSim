model HydraulicJack "液压千斤顶回路"
  annotation (Icon(coordinateSystem(extent = {{-100.0, -100.0}, {100.0, 100.0}}, 
    grid = {2.0, 2.0}), graphics = {Polygon(origin = {-7.105427357601002e-15, 33.0}, 
    lineColor = {0, 0, 255}, 
    fillColor = {0, 0, 255}, 
    fillPattern = FillPattern.Solid, 
    points = {{-64.0, 1.0}, {0.0, 37.0}, {64.0, 1.0}, {0.0, -37.0}}), Line(origin = {0.0, -12.0}, 
    points = {{-62.0, 18.0}, {0.0, -18.0}, {62.0, 18.0}}, 
    color = {0, 0, 255}, 
    thickness = 5.0), Line(origin = {7.105427357601002e-15, -39.99999999999999}, 
    points = {{-62.0, 18.0}, {0.0, -18.0}, {62.0, 18.0}}, 
    color = {0, 0, 255}, 
    thickness = 5.0)}), 
    experiment(Algorithm = Dassl, Interval = 0.005, StartTime = 0, StopTime = 5, Tolerance = 1e-07), 
    Diagram(coordinateSystem(extent = {{-100.0, -100.0}, {100.0, 100.0}}, 
      grid = {2.0, 2.0})), 
    Documentation(link = "modelica://TYHydraulicComponents/Resources/HTML/HydraulicJack.html"),Protection(access=Access.nonPackageDuplicate),__MWORKS(ResultViewerManager(resultViewers={
ResultViewer(name="1", executeTrigger=executeTrigger.SimulationFinished, commands={
CreatePlot(id=1, x_display_unit="s", legend_layout=7, left_title_type=2, left_title="控制信号", bottom_title_type=2, bottom_title="时间/s", right_title_type=2, fix_time_range_value=0, zoom_x=(0, 5), zoom_y_l=(-30, 30)), 
Plot(y=["directionalValve34_H.Signal"], colors=["4278190335"]), 
CreatePlot(id=-1, x_display_unit="s", legend_layout=7, left_title_type=2, left_title="压力[bar]", bottom_title_type=2, bottom_title="时间/s", right_title_type=2, fix_time_range_value=0, sub_plot=(1, 2), zoom_x=(0, 5), zoom_y_l=(-50, 250)), 
Plot(y=["volumeV.p", "volumeV1.p"], colors=["4278190335", "4294901760"]), 
CreatePlot(id=-1, x_display_unit="s", legend_layout=7, left_title_type=2, left_title="泄露流量[l/min]", bottom_title_type=2, bottom_title="时间/s", right_title_type=2, fix_time_range_value=0, sub_plot=(2, 2), zoom_x=(0, 5), zoom_y_l=(-0.03, 0.03)), 
Plot(y=["viscousFrictionAndLeakageSpool.q"], colors=["4278190335"]), 
CreatePlot(id=-1, x_display_unit="s", legend_layout=7, left_title_type=2, left_title="位移[m]", bottom_title_type=2, bottom_title="时间/s", right_title_type=2, fix_time_range_value=0, sub_plot=(2, 1), zoom_x=(0, 5), zoom_y_l=(-0.06, 0.06)), 
Plot(y=["massWithStopAndFriction.s"], colors=["4278190335"])})
})));
  TYHydraulicComponents.Pistons.FixedBodyPiston fixedBodyPiston(ds = 0.04, 
    dr = 0, 
    redeclare model Medium = TYOilMedia.HydraulicOil.Partial.Advanced) 
    annotation (Placement(transformation(origin = {-30.0, 36.0}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYHydraulicComponents.Pistons.FixedBodyPiston fixedBodyPiston1(reverse = true, ds = 0.04, dr = 0.015, len0 = 0.05, redeclare model Medium = TYOilMedia.HydraulicOil.Partial.Advanced) annotation (Placement(transformation(origin = {36.1118120046279, 35.999999999999986}, 
    extent = {{10.0, -10.0}, {-10.0, 10.0}})));
  TYHydraulicComponents.Auxiliaries.VolumeV volumeV1(redeclare model Medium = TYOilMedia.HydraulicOil.Partial.Advanced) annotation (Placement(transformation(origin = {41.1118120046279, 10.0}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYHydraulics.Valves.DirectionalValves.DirectionalValve34_O directionalValve34_H(
    dpnom = 6.999999999999999e6, qnom = 0.000583333333333333, 
    dynamics = "2nd order", 
    redeclare model Medium = TYOilMedia.HydraulicOil.Partial.Advanced) 
    annotation (Placement(transformation(origin = {12.049999999999999, -30.0}, 
      extent = {{-26.900000000000002, -10.0}, {14.8, 10.0}})));
  TYHydraulics.Sources.PressureSource pressureSource(constantPressure = 2e7, redeclare model Medium = TYOilMedia.HydraulicOil.Partial.Advanced) 
    annotation (Placement(transformation(origin = {4.049999999999997, -65.99999999999997}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
      rotation = 90.0)));
  TYHydraulics.Sources.Tank tank(p_load = 0, redeclare model Medium = TYOilMedia.HydraulicOil.Partial.Advanced) 
    annotation (Placement(transformation(origin = {16.85, -58.0}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  Modelica.Mechanics.Translational.Components.MassWithStopAndFriction massWithStopAndFriction(smax = 0.05, smin = -0.05, F_prop = 1000, F_Coulomb = 0, F_Stribeck = 0, fexp = 0,L=0,m=1) 
    annotation (Placement(transformation(origin = {64.0, 35.999999999999986}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYHydraulicComponents.DiaphragmLeakageSealings.ViscousFrictionAndLeakage viscousFrictionAndLeakageSpool(ds = 0.04, dc = 2e-5, L_c = 0.01, redeclare model Medium = TYOilMedia.HydraulicOil.Partial.Advanced, 
    InterfaceSwitchA = true, InterfaceSwitchB = true) 
    annotation (Placement(transformation(origin = {3.05590600231395, 35.999999999999986}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYHydraulicComponents.Auxiliaries.VolumeV volumeV(redeclare model Medium = TYOilMedia.HydraulicOil.Partial.Advanced) annotation (Placement(transformation(origin = {-35.0, 10.0}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  Modelica.Blocks.Sources.TimeTable timeTable(table = {{0.0, 0.0}, {1, 0}, {1, 20}, {3, 20}, {3, -20}, {4, -20}, {10, -20}}) 
    annotation (Placement(transformation(origin = {52.0, -31.800000000000004}, 
      extent = {{10.0, -10.0}, {-10.0, 10.0}})));
equation
  connect(fixedBodyPiston.flange_b, viscousFrictionAndLeakageSpool.flange_a) 
    annotation (Line(origin = {-13.0, 36.0}, 
      points = {{-7.0, 0.0}, {6.0, 0.0}}, 
      color = {0, 127, 0}));
  connect(volumeV.portV_B[1], fixedBodyPiston.portV_A) 
    annotation (Line(origin = {-35.0, 22.0}, 
      points = {{0.0, -5.0}, {0.0, 4.0}}, 
      color = {0, 127, 255}));
  connect(volumeV.port_A, viscousFrictionAndLeakageSpool.port_A) 
    annotation (Line(origin = {-18.0, 15.0}, 
      points = {{-17.0, -12.0}, {16.0, -12.0}, {16.0, 11.0}}, 
      color = {0, 127, 255}));
  connect(volumeV.port_A, directionalValve34_H.port_A) 
    annotation (Line(origin = {-15.0, -8.0}, 
      points = {{-20.0, 11.0}, {-20.0, -12.0}, {19.0, -12.0}}, 
      color = {0, 127, 255}));
  connect(fixedBodyPiston1.portV_A, volumeV1.portV_B[1]) 
    annotation (Line(origin = {41.0, 21.0}, 
      points = {{0.0, 5.0}, {0.0, -4.0}}, 
      color = {0, 127, 255}));
  connect(viscousFrictionAndLeakageSpool.port_B, volumeV1.port_A) 
    annotation (Line(origin = {25.0, 15.0}, 
      points = {{-17.0, 11.0}, {-17.0, -12.0}, {16.0, -12.0}}, 
      color = {0, 127, 255}));
  connect(volumeV1.port_A, directionalValve34_H.port_B) 
    annotation (Line(origin = {25.0, -8.0}, 
      points = {{16.0, 11.0}, {16.0, -12.0}, {-17.0, -12.0}}, 
      color = {0, 127, 255}));
  connect(fixedBodyPiston1.flange_a, massWithStopAndFriction.flange_a) 
    annotation (Line(origin = {50.0, 36.0}, 
      points = {{-4.0, 0.0}, {4.0, 0.0}}, 
      color = {0, 127, 0}));
  connect(viscousFrictionAndLeakageSpool.flange_b, fixedBodyPiston1.flange_b) 
    annotation (Line(origin = {20.0, 36.0}, 
      points = {{-7.0, 0.0}, {6.0, 0.0}}, 
      color = {0, 127, 0}));
  connect(pressureSource.port_B, directionalValve34_H.port_P) 
    annotation (Line(origin = {4.0, -49.0}, 
      points = {{0.0, -10.0}, {0.0, 9.0}}, 
      color = {0, 127, 255}));
  connect(directionalValve34_H.port_T, tank.port_A) 
    annotation (Line(origin = {13.0, -49.0}, 
      points = {{-5.0, 9.0}, {-5.0, 3.0}, {4.0, 3.0}, {4.0, -9.0}}, 
      color = {0, 127, 255}));
  connect(directionalValve34_H.Signal, timeTable.y) 
    annotation (Line(origin = {35.0, -32.0}, 
      points = {{-7.0, 0.0}, {6.0, 0.0}}, 
      color = {0, 0, 127}));
end HydraulicJack;