model PneumaticJack "气动千斤顶"
  TYPneumatics.Sources.PressureSource pressureSource(constantPressure = 1.98987e7, constantTemperature(displayUnit = "degC"), redeclare model GasType = TYGasMedia.MediaTypes.Air) 
    annotation (Placement(transformation(origin = {-24.5, 19.99999999999997}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYPneumatics.Sources.PressureSource pressureSource1(constantPressure = 1.98987e7, constantTemperature(displayUnit = "degC"), redeclare model GasType = TYGasMedia.MediaTypes.Air, redeclare model GasMedium = TYGasMedia.MediaProperties.Perfect.Perfect) 
    annotation (Placement(transformation(origin = {-24.600000000000023, -74.5}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYPneumatics.Sources.Surroundings surroundings(redeclare model GasMedium = TYGasMedia.MediaProperties.Perfect.Perfect) 
    annotation (Placement(transformation(origin = {-2.1999999999999957, -74.5}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
      rotation = 360.0)));
  TYPneumatics.Sources.Surroundings surroundings1(redeclare model GasType = TYGasMedia.MediaTypes.Air) 
    annotation (Placement(transformation(origin = {-3.6000000000000085, 19.99999999999997}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
      rotation = 360.0)));
  TYPneumatics.Actuators.FixDActingAsymCylinderWithMass fixDActingAsymCylinderWithMass(m = 3000, pA(start = 9.898699999999998e6), pB(start = 1.48987e7), redeclare model GasType = TYGasMedia.MediaTypes.Air) 
    annotation (Placement(transformation(origin = {-7.500000000000007, 73.0}, 
      extent = {{-10.0, -7.0}, {14.0, 8.0}})));
  TYPneumatics.Actuators.FixDActingAsymCylinderWithMass fixDActingAsymCylinderWithMass1(m = 3000, redeclare model GasMedium = TYGasMedia.MediaProperties.Perfect.Perfect) 
    annotation (Placement(transformation(origin = {-2.0999999999999943, -20.5}, 
      extent = {{-10.0, -7.0}, {14.0, 8.0}})));
  Modelica.Blocks.Sources.Sine sine(amplitude = 10, phase = 0, f = 1) 
    annotation (Placement(transformation(origin = {48.0, -6.661338147750939e-16}, 
      extent = {{10.0, -10.0}, {-10.0, 10.0}})));
  annotation (experiment(Algorithm = Dassl, Interval = 0.01, StartTime = 0, StopTime = 5, Tolerance = 1e-07), 
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
    Documentation(link="modelica://TYPneumatics/Resources/HTML/PneumaticJack.html"),__MWORKS(ResultViewerManager(resultViewers={
ResultViewer(name="1", executeTrigger=executeTrigger.SimulationFinished, commands={
CreatePlot(id=1, x_display_unit="s", legend_layout=7, left_title_type=2, left_title="位移/m", bottom_title_type=2, bottom_title="时间/s", fix_time_range_value=0, zoom_x=(0, 5), zoom_y_l=(-0.05, 0.35)), 
Plot(y=["fixDActingAsymCylinderWithMass.s", "fixDActingAsymCylinderWithMass1.s"], colors=["4278190335", "4294901760"])})
})));
  TYPneumatics.Valves.DirectionalValves.DirectionalValve34_H directionalValve34_H(dynamics = "2nd order") 
    annotation (Placement(transformation(origin = {-1.5, 47.99999999999998}, 
      extent = {{-28.0, -10.0}, {19.0, 10.0}})));
  TYPneumatics.Valves.DirectionalValves.DirectionalValve34_H directionalValve34_H1(dynamics = "2nd order", redeclare model GasMedium = TYGasMedia.MediaProperties.Perfect.Perfect) 
    annotation (Placement(transformation(origin = {-0.09999999999999432, -46.0}, 
      extent = {{-28.0, -10.0}, {19.0, 10.0}})));
equation
  connect(pressureSource.port_B, directionalValve34_H.port_P) 
    annotation (Line(origin = {-14.0, 29.0}, 
      points = {{-2.5, -9.000000000000028}, {6.499999999999998, -9.000000000000028}, {6.499999999999998, 8.999999999999979}}, 
      color = {90, 229, 225}));
  connect(directionalValve34_H.port_T, surroundings1.port_A) 
    annotation (Line(origin = {-1.0, 32.0}, 
      points = {{-2.5, 5.999999999999979}, {-2.5000000000000084, -7.000000000000028}}, 
      color = {90, 229, 225}));
  connect(directionalValve34_H.port_A, fixDActingAsymCylinderWithMass.port_A) 
    annotation (Line(origin = {-11.0, 62.0}, 
      points = {{3.5, -4.000000000000021}, {3.5, 4.0}, {-4.500000000000007, 4.0}}, 
      color = {90, 229, 225}));
  connect(fixDActingAsymCylinderWithMass.port_B, directionalValve34_H.port_B) 
    annotation (Line(origin = {-3.0, 62.0}, 
      points = {{-0.5000000000000071, 4.0}, {-0.5, -4.000000000000021}}, 
      color = {90, 229, 225}));
  connect(directionalValve34_H.realin, sine.y) 
    annotation (Line(origin = {43.0, 22.000000000000004}, 
      points = {{-26.7, 24.149999999999974}, {-11.0, 24.149999999999974}, {-11.0, -22.000000000000004}, {-6.0, -22.000000000000004}}, 
      color = {0, 0, 127}));
  connect(directionalValve34_H1.realin, sine.y) 
    annotation (Line(origin = {27.0, -23.999999999999996}, 
      points = {{-9.299999999999994, -23.850000000000005}, {5.0, -23.850000000000005}, {5.0, 23.999999999999996}, {10.0, 23.999999999999996}}, 
      color = {0, 0, 127}));
  connect(directionalValve34_H1.port_A, fixDActingAsymCylinderWithMass1.port_A) 
    annotation (Line(origin = {-8.0, -31.999999999999996}, 
      points = {{1.9000000000000057, -4.0000000000000036}, {-2.0999999999999943, -4.0000000000000036}, {-2.0999999999999943, 4.4999999999999964}}, 
      color = {90, 229, 225}));
  connect(directionalValve34_H1.port_B, fixDActingAsymCylinderWithMass1.port_B) 
    annotation (Line(origin = {0.0, -31.999999999999996}, 
      points = {{-2.0999999999999943, -4.0000000000000036}, {1.9000000000000057, -4.0000000000000036}, {1.9000000000000057, 4.4999999999999964}}, 
      color = {90, 229, 225}));
  connect(directionalValve34_H1.port_P, pressureSource1.port_B) 
    annotation (Line(origin = {-11.0, -65.0}, 
      points = {{4.900000000000004, 9.0}, {4.900000000000004, -9.5}, {-5.600000000000023, -9.5}}, 
      color = {90, 229, 225}));
  connect(surroundings.port_A, directionalValve34_H1.port_T) 
    annotation (Line(origin = {-2.0, -62.0}, 
      points = {{-0.09999999999999565, -7.5}, {-0.09999999999999432, 6.0}}, 
      color = {90, 229, 225}));
end PneumaticJack;