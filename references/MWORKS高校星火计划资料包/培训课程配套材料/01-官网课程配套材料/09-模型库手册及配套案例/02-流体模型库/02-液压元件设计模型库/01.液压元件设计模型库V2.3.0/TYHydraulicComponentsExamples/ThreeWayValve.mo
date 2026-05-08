model ThreeWayValve "3通阀回路"
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
    experiment(Algorithm = Dassl, Interval = 0.01, StartTime = 0, StopTime = 4, Tolerance = 1e-07), 
    Diagram(coordinateSystem(extent = {{-120.0, -100.0}, {120.0, 100.0}}, 
      grid = {2.0, 2.0})), 
    Documentation(link = "modelica://TYHydraulicComponents/Resources/HTML/ThreeWayValve.html"),Protection(access=Access.nonPackageDuplicate),__MWORKS(ResultViewerManager(resultViewers={
ResultViewer(name="1", executeTrigger=executeTrigger.SimulationFinished, commands={
CreatePlot(id=2, x_display_unit="s", legend_layout=7, left_title_type=2, left_title="力/N", bottom_title_type=2, bottom_title="时间/s", right_title_type=2, fix_time_range_value=0, zoom_x=(0, 4), zoom_y_l=(-150, 150)), 
Plot(y=["force.f"], colors=["4278190335"]), 
CreatePlot(id=-1, x_display_unit="s", legend_layout=7, left_title_type=2, left_title="位移/mm", bottom_title_type=2, bottom_title="时间/s", right_title_type=2, fix_time_range_value=0, sub_plot=(1, 2), zoom_x=(0, 4), zoom_y_l=(-4, 4)), 
Plot(y=["massWithStopAndFriction.s"], colors=["4278190335"]), 
CreatePlot(id=-1, x_display_unit="s", legend_layout=7, left_title_type=2, left_title="压力/bar", bottom_title_type=2, bottom_title="时间/s", right_title_type=2, fix_time_range_value=0, sub_plot=(2, 2), zoom_x=(0, 4), zoom_y_l=(-20, 120)), 
Plot(y=["gasAccumulator.p"], colors=["4278190335"]), 
CreatePlot(id=-1, x_display_unit="s", legend_layout=7, left_title_type=2, left_title="流量/（L/min）", bottom_title_type=2, bottom_title="时间/s", right_title_type=2, fix_time_range_value=0, sub_plot=(2, 1), zoom_x=(0, 4), zoom_y_l=(-100, 500)), 
Plot(y=["volumeV1.portV_B[1].q", "volumeV2.port_A.q"], colors=["4278190335", "4294901760"])})
})));
  TYHydraulicComponents.Pistons.SpringPiston springPiston(dr = 0, f_0 = 1, s_0 = 0, 
    reverse = false, redeclare model Medium = TYOilMedia.HydraulicOil.Partial.Elementary) 
    annotation (Placement(transformation(origin = {-32.0, 18.000000000000007}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYHydraulicComponents.SlideValveSpool.AnnularOrificeSpool annularOrificeSpool(reverse = true, 
    redeclare model Medium = TYOilMedia.HydraulicOil.Partial.Elementary, InterfaceSwitchB = true) 
    annotation (Placement(transformation(origin = {7.105427357601002e-15, 18.0}, 
      extent = {{10.0, -10.0}, {-10.0, 10.0}})));
  Modelica.Mechanics.Translational.Components.MassWithStopAndFriction massWithStopAndFriction(smax = 0.003, smin = -0.003, F_prop = 1000, F_Coulomb = 0, F_Stribeck = 0, fexp = 0, m = 0.1,L=0) 
    annotation (Placement(transformation(origin = {31.999999999999993, 18.0}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYHydraulicComponents.SlideValveSpool.AnnularOrificeSpool annularOrificeSpool1(reverse = false, 
    redeclare model Medium = TYOilMedia.HydraulicOil.Partial.Elementary, InterfaceSwitchB = true) 
    annotation (Placement(transformation(origin = {63.99999999999999, 18.0}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYHydraulicComponents.Pistons.SpringPiston springPiston1(dr = 0, s_0 = 0, f_0 = 1, 
    reverse = true, redeclare model Medium = TYOilMedia.HydraulicOil.Partial.Elementary) annotation (Placement(transformation(origin = {96.0, 17.999999999999986}, 
      extent = {{10.0, -10.0}, {-10.0, 10.0}})));
  TYHydraulicComponents.Auxiliaries.VolumeV volumeV(V0 = 1e-5, 
    redeclare model Medium = TYOilMedia.HydraulicOil.Partial.Elementary) 
    annotation (Placement(transformation(origin = {-37.0, -5.999999999999993}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYHydraulicComponents.Auxiliaries.VolumeV volumeV1(V0 = 1e-5, 
    redeclare model Medium = TYOilMedia.HydraulicOil.Partial.Elementary) 
    annotation (Placement(transformation(origin = {7.016942402441543, -5.999999999999993}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYHydraulicComponents.Auxiliaries.VolumeV volumeV2(V0 = 1e-5, 
    redeclare model Medium = TYOilMedia.HydraulicOil.Partial.Elementary) 
    annotation (Placement(transformation(origin = {56.98305759755845, -5.999999999999993}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYHydraulicComponents.Auxiliaries.VolumeV volumeV3(V0 = 1e-5, 
    redeclare model Medium = TYOilMedia.HydraulicOil.Partial.Elementary) 
    annotation (Placement(transformation(origin = {101.0, -5.999999999999993}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYHydraulicComponents.Sources.PressureSource pressureSource(constantPressure = 0, 
    redeclare model Medium = TYOilMedia.HydraulicOil.Partial.Elementary) 
    annotation (Placement(transformation(origin = {-36.99999999999999, -38.0}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
      rotation = 90.0)));
  TYHydraulicComponents.Sources.PressureSource pressureSource1(constantPressure = 1e7, 
    redeclare model Medium = TYOilMedia.HydraulicOil.Partial.Elementary) 
    annotation (Placement(transformation(origin = {-2.5, -38.0}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
      rotation = 90.0)));
  TYHydraulics.Auxiliaries.Capacitive.GasAccumulator gasAccumulator(V = 0.002, P0 = 0, Pin0 = 10000, 
    redeclare model Medium = TYOilMedia.HydraulicOil.Partial.Elementary, 
    stateinit = "绝热初始化") 
    annotation (Placement(transformation(origin = {31.999999999999993, -29.999999999999986}, 
      extent = {{-10.0, 10.0}, {10.0, -10.0}})));
  TYHydraulicComponents.Sources.PressureSource pressureSource2(constantPressure = 0, 
    redeclare model Medium = TYOilMedia.HydraulicOil.Partial.Elementary) 
    annotation (Placement(transformation(origin = {101.00000000000003, -47.99999999999999}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
      rotation = 90.0)));
  TYHydraulicComponents.Sources.Tank tank(redeclare model Medium = TYOilMedia.HydraulicOil.Partial.Elementary) annotation (Placement(transformation(origin = {70.0, -29.999999999999986}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  Modelica.Mechanics.Translational.Sources.Force force 
    annotation (Placement(transformation(origin = {-64.00000000000001, 18.000000000000007}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  Modelica.Blocks.Sources.TimeTable timeTable(table = {{0.0, 0.0}, {1, -100}, {3, 100}, {4, 0}}) 
    annotation (Placement(transformation(origin = {-96.00000000000001, 18.0}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
equation
  connect(volumeV.port_A, pressureSource.port_B) 
    annotation (Line(origin = {-37.0, -20.999999999999993}, 
      points = {{0.0, 8.0}, {0.0, -9.0}}, 
      color = {0, 127, 255}));
  connect(volumeV.portV_B[1], springPiston.portV_A) 
    annotation (Line(origin = {-37.0, 5.000000000000007}, 
      points = {{0.0, -4.0}, {0.0, 3.0}}, 
      color = {0, 127, 255}));
  connect(volumeV3.portV_B[1], springPiston1.portV_A) 
    annotation (Line(origin = {101.0, 5.000000000000007}, 
      points = {{0.0, -4.0}, {0.0, 3.0}}, 
      color = {0, 127, 255}));
  connect(volumeV3.port_A, pressureSource2.port_B) 
    annotation (Line(origin = {101.0, -25.999999999999993}, 
      points = {{0.0, 13.0}, {0.0, -14.0}}, 
      color = {0, 127, 255}));
  connect(force.flange, springPiston.flange_a) 
    annotation (Line(origin = {-50.0, 18.0}, 
      points = {{-4.0, 0.0}, {8.0, 0.0}}, 
      color = {0, 127, 0}));
  connect(timeTable.y, force.f) 
    annotation (Line(origin = {-91.0, 18.0}, 
      points = {{6.0, 0.0}, {15.0, 0.0}}, 
      color = {0, 0, 127}));
  connect(annularOrificeSpool.portV_A, volumeV1.portV_B[1]) 
    annotation (Line(origin = {7.0, 5.0}, 
      points = {{0.0, 3.0}, {0.0, -4.0}}, 
      color = {0, 127, 255}));
  connect(annularOrificeSpool.port_B, pressureSource1.port_B) 
    annotation (Line(origin = {-5.0, -11.0}, 
      points = {{3.0, 19.0}, {3.0, -19.0}}, 
      color = {0, 127, 255}));
  connect(annularOrificeSpool1.portV_A, volumeV2.portV_B[1]) 
    annotation (Line(origin = {57.0, 5.0}, 
      points = {{0.0, 3.0}, {0.0, -4.0}}, 
      color = {0, 127, 255}));
  connect(tank.port_A, annularOrificeSpool1.port_B) 
    annotation (Line(origin = {68.0, -11.0}, 
      points = {{2.0, -19.0}, {2.0, 19.0}, {-2.0, 19.0}}, 
      color = {0, 127, 255}));
  connect(massWithStopAndFriction.flange_b, annularOrificeSpool1.flange_a) 
    annotation (Line(origin = {48.0, 18.0}, 
      points = {{-6.0, 0.0}, {6.0, 0.0}}, 
      color = {0, 127, 0}));
  connect(massWithStopAndFriction.flange_a, annularOrificeSpool.flange_a) 
    annotation (Line(origin = {16.0, 18.0}, 
      points = {{6.0, 0.0}, {-6.0, 0.0}}, 
      color = {0, 127, 0}));
  connect(annularOrificeSpool.flange_b, springPiston.flange_b) 
    annotation (Line(origin = {-16.0, 18.0}, 
      points = {{6.0, 0.0}, {-6.0, 0.0}}, 
      color = {0, 127, 0}));
  connect(annularOrificeSpool1.flange_b, springPiston1.flange_b) 
    annotation (Line(origin = {80.0, 18.0}, 
      points = {{-6.0, 0.0}, {6.0, 0.0}}, 
      color = {0, 127, 0}));
  connect(volumeV1.port_A, gasAccumulator.port_A) 
    annotation (Line(origin = {20.0, -16.0}, 
      points = {{-13.0, 3.0}, {-13.0, -4.0}, {12.0, -4.0}}, 
      color = {0, 127, 255}));
  connect(volumeV2.port_A, gasAccumulator.port_A) 
    annotation (Line(origin = {45.0, -16.0}, 
      points = {{12.0, 3.0}, {12.0, -4.0}, {-13.0, -4.0}}, 
      color = {0, 127, 255}));
end ThreeWayValve;