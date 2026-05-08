model Start_system_of_CNC_machining_center "数控加工中心启动系统"
  annotation (experiment(StartTime = 0, StopTime = 20, Interval = 0.01, Algorithm = Dassl, Tolerance = 1e-07, DoublePrecision = true, StoreEventValue = false), Diagram(coordinateSystem(extent={{-140,-160},{240,180}}, 
grid={2,2}),graphics = {Text(origin={115.86335403726707,107.18181818181819}, 
extent={{-227.86335403726707,24.818181818181813},{104.13664596273291,-1.181818181818187}}, 
textString="1YA得电时，刀具和工件加紧，1YA失电时，刀具和工件松开，
2YA得电时，压缩空气吹向主轴锥孔，吹去铁屑", 
textStyle={TextStyle.None}), Text(origin={-29.285714285714278,-58}, 
extent={{-16.714285714285722,10},{1.2857142857142776,0}}, 
textString="1YA", 
textStyle={TextStyle.None}), Text(origin={158,-11.999999999999996}, 
extent={{-8,6},{8,-6}}, 
textString="2YA", 
textStyle={TextStyle.None})}), 
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
      thickness = 5.0)}), Protection(access=Access.nonPackageDuplicate), 
    Documentation(link="modelica://TYPneumatics/Resources/HTML/Start_system_of_CNC_machining_center.html"),__MWORKS(ResultViewerManager(resultViewers={
ResultViewer(name="1", executeTrigger=executeTrigger.SimulationFinished, commands={
CreatePlot(id=1, x_display_unit="s", legend_layout=7, left_title_type=2, left_title="气动缸位移[m]", bottom_title_type=2, bottom_title="时间/s", fix_time_range_value=0, zoom_x=(0, 20), zoom_y_l=(-0.1, 0.5)), 
Plot(y=["fixedDoubleCylinder.s"], colors=["4278190335"]), 
CreatePlot(id=-1, x_display_unit="s", legend_layout=7, left_title_type=2, left_title="流量[kg/s]", bottom_title_type=2, bottom_title="时间/s", fix_time_range_value=0, sub_plot=(1, 2), zoom_x=(0, 20), zoom_y_l=(-0.002, 0.01)), 
Plot(y=["orifice_Cq4.port_A.m_flow"], colors=["4278190335"]), 
CreatePlot(id=-1, x_display_unit="s", legend_layout=7, left_title_type=2, left_title="控制信号", bottom_title_type=2, bottom_title="时间/s", fix_time_range_value=0, sub_plot=(2, 2), zoom_x=(0, 20), zoom_y_l=(-0.2, 1.2)), 
Plot(y=["timeTable1.y"], colors=["4278190335"]), 
CreatePlot(id=-1, x_display_unit="s", legend_layout=7, left_title_type=2, left_title="控制信号", bottom_title_type=2, bottom_title="时间/s", fix_time_range_value=0, sub_plot=(2, 1), zoom_x=(0, 20), zoom_y_l=(-0.2, 1.2)), 
Plot(y=["timeTable.y"], colors=["4278190335"])})
})));
  TYPneumatics.Sources.PressureSource pressureSource 
    annotation (Placement(transformation(origin = {-40.0, -122.0}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYPneumatics.Valves.DirectionalValves.DirectionalValve24 directionalValve25_1(ratedCurrent = 0.001, redeclare model GasMedium = TYGasMedia.MediaProperties.Semi_Perfect.Semi_Perfect, UseVolumeA = true, UseVolumeB = true, UseVolumeT = true, A = 0.0001) annotation (Placement(transformation(origin = {-3.999999999999993, -65.99999999999999}, 
    extent = {{23.999999999999993, -20.0}, {-24.000000000000007, 20.0}})));
  TYPneumatics.Actuators.FixDActingSymCylinderWithMass fixedDoubleCylinder(redeclare model GasMedium = TYGasMedia.MediaProperties.Semi_Perfect.Semi_Perfect, diamp(displayUnit = "m") = 63e-3, stroke = 0.4, m = 1.96, kth = 100) annotation (Placement(transformation(origin = {4.0, 74.0}, 
    extent = {{-32.0, -20.0}, {32.0, 20.0}})));
  TYPneumatics.Valves.DirectionalValves.CheckValvewithSaturation checkValve_saturation1(redeclare model GasMedium = TYGasMedia.MediaProperties.Semi_Perfect.Semi_Perfect, pcrack = 100000, pmax = 3e5) annotation (Placement(transformation(origin = {44.00000000000002, 9.933333333333328}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYPneumatics.Valves.FlowControlValves.ThrottleValve orifice_Cq1(redeclare model GasMedium = TYGasMedia.MediaProperties.Semi_Perfect.Semi_Perfect, UseVolumeA = false, A = 0.001) annotation (Placement(transformation(origin = {27.000000000000025, 9.933333333333328}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
    rotation = 90.0)));
  TYPneumatics.Valves.DirectionalValves.CheckValvewithSaturation checkValve_saturation2(redeclare model GasMedium = TYGasMedia.MediaProperties.Semi_Perfect.Semi_Perfect, pcrack = 100000, pmax = 3e5, flowset = "Cv", Cv = 0.8) annotation (Placement(transformation(origin = {-56.000000000000014, 9.933333333333328}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYPneumatics.Valves.FlowControlValves.ThrottleValve orifice_Cq2(redeclare model GasMedium = TYGasMedia.MediaProperties.Semi_Perfect.Semi_Perfect, UseVolumeA = false, A = 0.001) annotation (Placement(transformation(origin = {-37.999999999999986, 9.933333333333328}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
    rotation = 90.0)));
  TYPneumatics.Valves.FlowControlValves.ThrottleValve orifice_Cq4 annotation (Placement(transformation(origin = {160.0, 72.0}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYPneumatics.Sources.Surroundings surroundings annotation (Placement(transformation(origin = {200.0, 72.0}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
    rotation = 90.0)));
  Modelica.Blocks.Sources.TimeTable timeTable(table = {{0, 1}, {10, 1}, {10.01, 0}, {15, 0}, {15.01, 1}, {20, 1}}) 
    annotation (Placement(transformation(origin = {-62.00000000000001, -65.99999999999999}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  Modelica.Blocks.Sources.TimeTable timeTable1(table = {{0, 0}, {15, 0}, {15.01, 1}, {20, 1}}) 
    annotation (Placement(transformation(origin = {184.0, 10.0}, 
      extent = {{11.0, -11.0}, {-11.0, 11.0}})));
  Modelica.Mechanics.Translational.Components.SpringDamper springDamper(c = 1000, d = 10) 
    annotation (Placement(transformation(origin = {78.0, 74.03333333333333}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  Modelica.Mechanics.Translational.Components.Fixed fixed(s0 = 0.3) 
    annotation (Placement(transformation(origin = {98.00000000000001, 64.0}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYPneumatics.Valves.FlowControlValves.ThrottleValve throttleValve(redeclare model GasMedium = TYGasMedia.MediaProperties.Semi_Perfect.Semi_Perfect, A = 0.001) annotation (Placement(transformation(origin = {-19.999999999999996, -94.0}, 
    extent = {{10.0, -10.0}, {-10.0, 10.0}})));
  TYPneumatics.Sources.Surroundings surroundings1(redeclare model GasMedium = TYGasMedia.MediaProperties.Semi_Perfect.Semi_Perfect) 
    annotation (Placement(transformation(origin = {-52.000000000000014, -94.1}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
      rotation = -90.0)));
  TYPneumatics.Valves.DirectionalValves.DirectionalValve22 directionalValve22_1(UseVolumeA = true, ratedCurrent = 0.001) 
    annotation (Placement(transformation(origin = {124.0, 10.0}, 
      extent = {{-24.0, -20.0}, {24.0, 20.0}})));
equation
  connect(springDamper.flange_b, fixed.flange) 
    annotation (Line(origin = {96.33333333333333, 80.0}, 
      points = {{-8.333333333333329, -5.966666666666669}, {1.6666666666666856, -5.966666666666669}, {1.6666666666666856, -16.0}}, 
      color = {0, 127, 0}), 
      Text);
  connect(timeTable.y, directionalValve25_1.realin) 
    annotation (Line(origin = {-44.0, -64.0}, 
      points = {{-7.000000000000007, -1.9999999999999858}, {18.000000000000007, -1.9999999999999858}}, 
      color = {0, 0, 127}));
  connect(throttleValve.port_A, directionalValve25_1.port_T) 
    annotation (Line(origin = {-19.0, -90.0}, 
      points = {{9.000000000000004, -4.0}, {19.000000000000007, -4.0}, {19.000000000000007, 4.000000000000014}}, 
      color = {28, 193, 208}));
  connect(surroundings1.port_A, throttleValve.port_B) 
    annotation (Line(origin = {-38.0, -94.0}, 
      points = {{-9.000000000000014, -0.19999999999998863}, {8.000000000000004, -0.19999999999998863}, {8.000000000000004, 0.0}}, 
      color = {28, 193, 208}));
  connect(checkValve_saturation2.port_A, directionalValve25_1.port_B) 
    annotation (Line(origin = {-38.0, -2.999999999999991}, 
      points = {{-18.000000000000014, 2.9333333333333194}, {-18.000000000000014, -25.0}, {38.00000000000001, -25.0}, {38.00000000000001, -42.99999999999999}}, 
      color = {28, 193, 208}), 
      Text);
  connect(checkValve_saturation1.port_A, directionalValve25_1.port_A) 
    annotation (Line(origin = {43.0, -2.999999999999991}, 
      points = {{1.0000000000000213, 2.9333333333333194}, {1.0000000000000213, -25.0}, {-34.99999999999999, -25.0}, {-34.99999999999999, -42.99999999999999}}, 
      color = {28, 193, 208}), 
      Text);
  connect(orifice_Cq2.port_A, directionalValve25_1.port_B) 
    annotation (Line(origin = {-26.000000000000004, -2.999999999999991}, 
      points = {{-11.999999999999982, 2.9333333333333194}, {-11.999999999999982, -25.0}, {26.00000000000001, -25.0}, {26.00000000000001, -42.99999999999999}}, 
      color = {28, 193, 208}), 
      Text);
  connect(orifice_Cq1.port_A, directionalValve25_1.port_A) 
    annotation (Line(origin = {32.0, -2.999999999999991}, 
      points = {{-4.999999999999975, 2.9333333333333194}, {-4.999999999999975, -25.0}, {-23.999999999999993, -25.0}, {-23.999999999999993, -42.99999999999999}}, 
      color = {28, 193, 208}), 
      Text);
  connect(fixedDoubleCylinder.flange_a, springDamper.flange_a) 
    annotation (Line(origin = {49.00000000000001, 74.0}, 
      points = {{-7.666666666666671, 0.0}, {18.999999999999993, 0.03333333333333144}}, 
      color = {0, 127, 0}), 
      Text);
  connect(checkValve_saturation2.port_B, fixedDoubleCylinder.port_A) 
    annotation (Line(origin = {-37.0, 38.00000000000001}, 
      points = {{-19.000000000000014, -18.06666666666668}, {-19.000000000000014, -4.0}, {19.666666666666668, -4.0}, {19.666666666666668, 17.33333333333332}}, 
      color = {28, 193, 208}));
  connect(orifice_Cq2.port_B, fixedDoubleCylinder.port_A) 
    annotation (Line(origin = {-28.0, 38.00000000000001}, 
      points = {{-9.999999999999986, -18.066666666666677}, {-9.999999999999986, -4.0}, {10.666666666666668, -4.0}, {10.666666666666668, 17.33333333333332}}, 
      color = {28, 193, 208}));
  connect(fixedDoubleCylinder.port_B, checkValve_saturation1.port_B) 
    annotation (Line(origin = {29.000000000000004, 38.00000000000001}, 
      points = {{-14.333333333333337, 17.33333333333332}, {-14.333333333333337, -4.0}, {15.000000000000018, -4.0}, {15.000000000000018, -18.06666666666668}}, 
      color = {28, 193, 208}));
  connect(orifice_Cq1.port_B, checkValve_saturation1.port_B) 
    annotation (Line(origin = {35.0, 27.000000000000007}, 
      points = {{-7.999999999999975, -7.066666666666677}, {-7.999999999999975, 7.0}, {9.000000000000021, 7.0}, {9.000000000000021, -7.066666666666681}}, 
      color = {28, 193, 208}));
  connect(orifice_Cq4.port_B, surroundings.port_A) 
    annotation (Line(origin = {182.0, 72.0}, 
      points = {{-12.0, 0.0}, {13.0, 0.09999999999999432}}, 
      color = {28, 193, 208}));
  connect(pressureSource.port_B, directionalValve25_1.port_P) 
    annotation (Line(origin = {-12.0, -104.0}, 
      points = {{-20.0, -18.0}, {20.00000000000001, -18.0}, {20.00000000000001, 18.000000000000014}}, 
      color = {28, 193, 208}));
  connect(directionalValve22_1.port_P, directionalValve25_1.port_P) 
    annotation (Line(origin = {63.0, -61.0}, 
      points = {{53.0, 51.4}, {53.0, -61.0}, {-54.999999999999986, -61.0}, {-54.999999999999986, -24.999999999999986}}, 
      color = {28, 193, 208}));
  connect(directionalValve22_1.realin, timeTable1.y) 
    annotation (Line(origin = {153.0, 9.0}, 
      points = {{-7.072599449142842, 0.9524479075918499}, {18.900000000000006, 1.0}}, 
      color = {0, 0, 127}));
  connect(directionalValve22_1.port_A, orifice_Cq4.port_A) 
  annotation(Line(origin={133,51}, 
  points={{-17,-21},{-17,21},{17,21}}, 
  color={28,193,208}));
end Start_system_of_CNC_machining_center;