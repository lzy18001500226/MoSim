model CheckValve "单向阀"
  annotation (Documentation(link = "modelica://TYPneumaticComponents/Resources/HTML/CheckValve.html"), Icon(coordinateSystem(extent = {{-100.0, -100.0}, {100.0, 100.0}}, 
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
    experiment(Algorithm = Dassl, Interval = 0.001, StartTime = 0, StopTime = 1, Tolerance = 1e-07), 
    Diagram(coordinateSystem(extent = {{-120.0, -100.0}, {120.0, 100.0}}, 
      grid = {2.0, 2.0})),Protection(access=Access.nonPackageDuplicate),__MWORKS(ResultViewerManager(resultViewers={
ResultViewer(name="1", executeTrigger=executeTrigger.SimulationFinished, commands={
CreatePlot(id=1, x_display_unit="s", legend_layout=7, left_title_type=2, left_title="压力/Bar", bottom_title_type=2, bottom_title="时间/s", fix_time_range_value=0, zoom_x=(0, 1), zoom_y_l=(0, 12)), 
Plot(y=["pressureSource.p", "pressureSource2.p"], colors=["4278190335", "4294901760"]), 
CreatePlot(id=-1, x_display_unit="s", legend_layout=7, left_title_type=2, left_title="位移/m", bottom_title_type=2, bottom_title="时间/s", fix_time_range_value=0, sub_plot=(2, 1), zoom_x=(0, 1), zoom_y_l=(-0.01, 0.06)), 
Plot(y=["massWithStopAndFriction.s", "massWithStopAndFriction1.s"], colors=["4278190335", "4294901760"]), 
CreatePlot(id=-1, x_display_unit="s", legend_layout=7, left_title_type=2, left_title="质量流量(kg/s)", bottom_title_type=2, bottom_title="时间/s", fix_time_range_value=0, sub_plot=(3, 1), zoom_x=(0, 1), zoom_y_l=(-0.04, 0.06)), 
Plot(y=["plainSeatPoppet.m_flow_A", "plainSeatPoppet1.m_flow_A"], colors=["4278190335", "4294901760"])})
})));
  Modelica.Mechanics.Translational.Components.MassWithStopAndFriction massWithStopAndFriction(m = 0.01, F_prop = 1, v(start = 0), F_Coulomb = 0, F_Stribeck = 0, smax = 0.05, smin = 0) 
    annotation (Placement(transformation(origin = {-52.0, 35.99999999999994}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYPneumaticComponents.Pistons.Piston piston(dr = 0, reverse = true, 
    redeclare model GasMedium = TYGasMedia.MediaProperties.Semi_Perfect.Semi_Perfect, InterfaceSwitch = true) annotation (Placement(transformation(origin = {-19.999999999999957, 35.99999999999994}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYPneumaticComponents.ConicalValveSpool.PlainSeatPoppet plainSeatPoppet(reverse = false, 
    redeclare model GasMedium = TYGasMedia.MediaProperties.Semi_Perfect.Semi_Perfect, InterfaceSwitchA = true, InterfaceSwitchB = true) annotation (Placement(transformation(origin = {12.000000000000046, 35.99999999999994}, 
      extent = {{10.0, -10.0}, {-10.0, 10.0}})));
  TYPneumaticComponents.Sources.PressureSource pressureSource(constantPressure = 4.999999999999999e5, 
    redeclare model GasMedium = TYGasMedia.MediaProperties.Semi_Perfect.Semi_Perfect) annotation (Placement(transformation(origin = {4.000000000000032, -1.6406627685930175}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
      rotation = 90.0)));
  Modelica.Mechanics.Translational.Components.MassWithStopAndFriction massWithStopAndFriction1(m = 0.01, F_prop = 1, v(start = 0), F_Coulomb = 0, F_Stribeck = 0, smax = 0.05, smin = 0) 
    annotation (Placement(transformation(origin = {-29.999999999999957, -38.000000000000014}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  Modelica.Mechanics.Translational.Components.Fixed fixed1 
    annotation (Placement(transformation(origin = {-82.0, -38.000000000000014}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYPneumaticComponents.Pistons.Piston piston1(dr = 0, reverse = true, 
    redeclare model GasMedium = TYGasMedia.MediaProperties.Semi_Perfect.Semi_Perfect, InterfaceSwitch = true) annotation (Placement(transformation(origin = {-4.99999999999995, -38.000000000000014}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYPneumaticComponents.ConicalValveSpool.PlainSeatPoppet plainSeatPoppet1(reverse = false, 
    redeclare model GasMedium = TYGasMedia.MediaProperties.Semi_Perfect.Semi_Perfect, InterfaceSwitchA = true, InterfaceSwitchB = true) annotation (Placement(transformation(origin = {27.000000000000075, -38.00000000000003}, 
      extent = {{10.0, -10.0}, {-10.0, 10.0}})));
  TYPneumaticComponents.Sources.PressureSource pressureSource1(constantPressure = 4.999999999999999e5, 
    redeclare model GasMedium = TYGasMedia.MediaProperties.Semi_Perfect.Semi_Perfect) annotation (Placement(transformation(origin = {18.00000000000003, -76.00000000000004}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
      rotation = 90.0)));
  TYPneumaticComponents.Sources.PressureSource pressureSource2(inputType_p = 3, inputType_T = 1, 
    redeclare model GasMedium = TYGasMedia.MediaProperties.Semi_Perfect.Semi_Perfect) annotation (Placement(transformation(origin = {74.00000000000003, 6.000000000000028}, 
      extent = {{10.0, -10.0}, {-10.0, 10.0}})));
  Modelica.Blocks.Sources.TimeTable timeTable(table = {{0.0, 1}, {0.5, 10}, {1, 1}}) 
    annotation (Placement(transformation(origin = {100.0, 8.359337231406982}, 
      extent = {{10.0, -10.0}, {-10.0, 10.0}})));
  Modelica.Mechanics.Translational.Components.Spring spring(c = 1000) 
    annotation (Placement(transformation(origin = {-55.999999999999986, -38.000000000000014}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
equation
  connect(massWithStopAndFriction.flange_b, piston.flange_a) 
    annotation (Line(origin = {-35.99999999999997, 36.0}, 
      points = {{-6.000000000000028, -5.684341886080802e-14}, {5.910260869565214, -5.684341886080802e-14}}, 
      color = {0, 127, 0}));
  connect(piston.flange_b, plainSeatPoppet.flange_b) 
    annotation (Line(origin = {-3.9999999999999716, 36.0}, 
      points = {{-5.782956521739086, -5.684341886080802e-14}, {5.782956521739118, -5.684341886080802e-14}}, 
      color = {0, 127, 0}));
  connect(massWithStopAndFriction1.flange_b, piston1.flange_a) 
    annotation (Line(origin = {-20.999999999999957, -38.0}, 
      points = {{1.0, -1.4210854715202004e-14}, {5.910260869565207, -1.4210854715202004e-14}}, 
      color = {0, 127, 0}));
  connect(piston1.flange_b, plainSeatPoppet1.flange_b) 
    annotation (Line(origin = {11.000000000000043, -38.0}, 
      points = {{-5.782956521739093, -1.4210854715202004e-14}, {5.7829565217391306, -2.842170943040401e-14}}, 
      color = {0, 127, 0}));
  connect(pressureSource2.PressureSignal, timeTable.y) 
    annotation (Line(origin = {84.00000000000003, 8.0}, 
      points = {{-4.400000000000006, 0.35933723140702867}, {4.999999999999972, 0.3593372314069825}}, 
      color = {0, 0, 127}));
  connect(fixed1.flange, spring.flange_a) 
    annotation (Line(origin = {-81.99999999999999, -38.0}, 
      points = {{-1.4210854715202004e-14, -1.4210854715202004e-14}, {16.0, -1.4210854715202004e-14}}, 
      color = {0, 127, 0}));
  connect(spring.flange_b, massWithStopAndFriction1.flange_a) 
    annotation (Line(origin = {-47.999999999999986, -38.0}, 
      points = {{2.0, -1.4210854715202004e-14}, {8.000000000000028, -1.4210854715202004e-14}}, 
      color = {0, 127, 0}));
  connect(piston.port_A, pressureSource.port_B) 
    annotation (Line(origin = {-10.999999999999972, 10.0}, 
      points = {{-14.199999999999985, 15.999999999999943}, {-14.199999999999985, 8.0}, {15.000000000000004, 8.0}, {15.000000000000004, -3.6406627685930175}}, 
      color = {28, 193, 208}));
  connect(plainSeatPoppet.port_B, pressureSource.port_B) 
    annotation (Line(origin = {7.000000000000028, 10.0}, 
      points = {{3.0000000000000178, 15.999999999999943}, {3.0000000000000178, 8.0}, {-2.9999999999999964, 8.0}, {-2.9999999999999964, -3.6406627685930175}}, 
      color = {28, 193, 208}));
  connect(plainSeatPoppet.port_A, pressureSource2.port_B) 
    annotation (Line(origin = {43.00000000000003, 21.0}, 
      points = {{-23.999999999999982, 4.999999999999943}, {-23.999999999999982, -14.999999999999972}, {23.0, -14.999999999999972}}, 
      color = {28, 193, 208}));
  connect(piston1.port_A, pressureSource1.port_B) 
    annotation (Line(origin = {4.000000000000027, -64.0}, 
      points = {{-14.199999999999976, 15.999999999999986}, {-14.199999999999976, 6.0}, {14.000000000000002, 6.0}, {14.000000000000002, -4.000000000000043}}, 
      color = {28, 193, 208}));
  connect(plainSeatPoppet1.port_B, pressureSource1.port_B) 
    annotation (Line(origin = {22.00000000000003, -64.0}, 
      points = {{3.000000000000046, 15.999999999999972}, {3.000000000000046, 6.0}, {-4.0, 6.0}, {-4.0, -4.000000000000043}}, 
      color = {28, 193, 208}));
  connect(plainSeatPoppet1.port_A, pressureSource2.port_B) 
    annotation (Line(origin = {50.00000000000003, -18.0}, 
      points = {{-15.999999999999957, -30.00000000000003}, {-15.999999999999957, -34.0}, {16.0, -34.0}, {16.0, 24.00000000000003}}, 
      color = {28, 193, 208}));
end CheckValve;