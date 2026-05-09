model PneumaticJack "气动千斤顶"
  annotation (Documentation(link = "modelica://TYPneumaticComponents/Resources/HTML/PneumaticJack.html"), Icon(coordinateSystem(extent = {{-100.0, -100.0}, {100.0, 100.0}}, 
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
    experiment(Algorithm = Dassl, Interval = 0.01, StartTime = 0, StopTime = 5, Tolerance = 1e-05), 
    Diagram(coordinateSystem(extent = {{-100.0, -100.0}, {100.0, 100.0}}, 
      grid = {2.0, 2.0})),Protection(access=Access.nonPackageDuplicate),__MWORKS(ResultViewerManager(resultViewers={
ResultViewer(name="1", executeTrigger=executeTrigger.SimulationFinished, commands={
CreatePlot(id=1, x_display_unit="s", legend_layout=7, left_title="[m]", fix_time_range_value=0, zoom_x=(0, 5), zoom_y_l=(-0.05, 0.35)), 
Plot(y=["massWithStopAndFriction.s", "fixDActingAsymCylinderWithMass.s"], colors=["4278190335", "4294901760"])})
})));
  TYPneumatics.Actuators.FixDActingAsymCylinderWithMass fixDActingAsymCylinderWithMass(m = 100, redeclare model GasMedium = TYGasMedia.MediaProperties.Perfect.Perfect) 
    annotation (Placement(transformation(origin = {-70.0, 32.0}, 
      extent = {{-10.0, -7.0}, {14.0, 8.0}})));
  TYPneumatics.Valves.DirectionalValves.DirectionalValve34_H directionalValve34_H(redeclare model GasMedium = TYGasMedia.MediaProperties.Perfect.Perfect) 
    annotation (Placement(transformation(origin = {-64.0, -2.0}, 
      extent = {{-28.0, -10.0}, {19.0, 10.0}})));
  TYPneumatics.Sources.PressureSource pressureSource(constantPressure = 5.987e5, redeclare model GasMedium = TYGasMedia.MediaProperties.Perfect.Perfect) 
    annotation (Placement(transformation(origin = {-70.0, -39.0}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
      rotation = 90.0)));
  TYPneumatics.Sources.Surroundings surroundings(redeclare model GasMedium = TYGasMedia.MediaProperties.Perfect.Perfect) 
    annotation (Placement(transformation(origin = {-55.00000000000001, -26.0}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYPneumaticComponents.Pistons.FixedBodyPiston fixedBodyPiston(ds = 0.025, dr = 0, redeclare model GasMedium = TYGasMedia.MediaProperties.Perfect.Perfect) 
    annotation (Placement(transformation(origin = {12.0, 30.0}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYPneumaticComponents.Pistons.FixedBodyPiston fixedBodyPiston1(ds = 0.025, dr = 0.012, len0 = 0.3, reverse = true, redeclare model GasMedium = TYGasMedia.MediaProperties.Perfect.Perfect) 
    annotation (Placement(transformation(origin = {44.0, 30.0}, 
      extent = {{10.0, -10.0}, {-10.0, 10.0}})));
  Modelica.Mechanics.Translational.Components.MassWithStopAndFriction massWithStopAndFriction(smin = 0, smax = 0.3, m = 100, fexp = 0, F_Stribeck = 0, F_Coulomb = 0, F_prop = 0) 
    annotation (Placement(transformation(origin = {84.0, 30.0}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYPneumaticComponents.Auxiliaries.GasVolumeV gasVolumeV(V0(displayUnit = "l") = 5e-5, T(start = 293.15), redeclare model GasMedium = TYGasMedia.MediaProperties.Perfect.Perfect) 
    annotation (Placement(transformation(origin = {6.769238451935079, -2.0}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYPneumaticComponents.Auxiliaries.GasVolumeV gasVolumeV1(V0(displayUnit = "l") = 5e-5, T(start = 293.15), redeclare model GasMedium = TYGasMedia.MediaProperties.Perfect.Perfect) 
    annotation (Placement(transformation(origin = {49.16923845193507, -2.0}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYPneumatics.Valves.DirectionalValves.DirectionalValve34_H directionalValve34_H1(redeclare model GasMedium = TYGasMedia.MediaProperties.Perfect.Perfect) 
    annotation (Placement(transformation(origin = {40.16923845193507, -26.0}, 
      extent = {{-28.0, -10.0}, {19.0, 10.0}})));
  TYPneumatics.Sources.PressureSource pressureSource1(constantPressure = 5.987e5, redeclare model GasMedium = TYGasMedia.MediaProperties.Perfect.Perfect) 
    annotation (Placement(transformation(origin = {34.16923845193507, -55.99999999999994}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
      rotation = 90.0)));
  TYPneumatics.Sources.Surroundings surroundings1(redeclare model GasMedium = TYGasMedia.MediaProperties.Perfect.Perfect) 
    annotation (Placement(transformation(origin = {49.16923845193511, -50.0}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  Modelica.Blocks.Sources.Sine sine(amplitude = 10) 
    annotation (Placement(transformation(origin = {-24.115380774032463, -3.8499999999999943}, 
      extent = {{10.0, -10.0}, {-10.0, 10.0}})));
  Modelica.Blocks.Sources.Sine sine1(amplitude = 10) 
    annotation (Placement(transformation(origin = {80.0, -28.0}, 
      extent = {{10.0, -10.0}, {-10.0, 10.0}})));
equation
  connect(fixedBodyPiston1.flange_a, massWithStopAndFriction.flange_a) 
    annotation (Line(origin = {63.999999999999986, 30.00000000000003}, 
      points = {{-9.910260869565185, -2.842170943040401e-14}, {10.000000000000014, -2.842170943040401e-14}}, 
      color = {0, 127, 0}));
  connect(fixedBodyPiston.flange_b, fixedBodyPiston1.flange_b) 
    annotation (Line(origin = {27.999999999999986, 30.00000000000003}, 
      points = {{-5.782956521739088, -2.842170943040401e-14}, {5.782956521739116, -2.842170943040401e-14}}, 
      color = {0, 127, 0}));
  connect(directionalValve34_H1.realin, sine1.y) 
    annotation (Line(origin = {62.999999999999986, -27.99999999999997}, 
      points = {{-5.030761548064916, 0.14999999999997016}, {6.000000000000014, 0.14999999999997016}, {6.000000000000014, -2.842170943040401e-14}}, 
      color = {0, 0, 127}));
  connect(directionalValve34_H.realin, sine.y) 
    annotation (Line(origin = {-41.00000000000001, -3.9999999999999716}, 
      points = {{-5.199999999999996, 0.14999999999997105}, {5.884619225967548, 0.14999999999997726}}, 
      color = {0, 0, 127}));
  connect(fixedBodyPiston.portV_A, gasVolumeV.portV_B[1]) 
    annotation (Line(origin = {6.999999999999988, 12.000000000000028}, 
      points = {{-0.19999999999998774, 7.999999999999972}, {-0.19999999999998952, -7.053183520599275}}, 
      color = {28, 193, 208}));
  connect(fixDActingAsymCylinderWithMass.port_A, directionalValve34_H.port_A) 
    annotation (Line(origin = {-74.0, 17.00000000000003}, 
      points = {{-4.0, 7.999999999999972}, {-4.0, -9.000000000000028}, {4.0, -9.000000000000028}}, 
      color = {28, 193, 208}));
  connect(fixDActingAsymCylinderWithMass.port_B, directionalValve34_H.port_B) 
    annotation (Line(origin = {-66.0, 17.00000000000003}, 
      points = {{0.0, 7.999999999999972}, {0.0, -9.000000000000028}}, 
      color = {28, 193, 208}));
  connect(directionalValve34_H.port_P, pressureSource.port_B) 
    annotation (Line(origin = {-70.0, -21.99999999999997}, 
      points = {{0.0, 9.999999999999972}, {0.0, -9.000000000000028}}, 
      color = {28, 193, 208}));
  connect(directionalValve34_H.port_T, surroundings.port_A) 
    annotation (Line(origin = {-64.0, -18.99999999999997}, 
      points = {{-2.0, 6.999999999999972}, {-2.0, -6.900000000000027}, {2.5999999999999943, -6.900000000000027}}, 
      color = {28, 193, 208}));
  connect(fixedBodyPiston1.portV_A, gasVolumeV1.portV_B[1]) 
    annotation (Line(origin = {48.999999999999986, 12.000000000000028}, 
      points = {{0.20000000000001705, 7.999999999999972}, {0.20000000000000284, -7.053183520599275}}, 
      color = {28, 193, 208}));
  connect(gasVolumeV.port_A, directionalValve34_H1.port_A) 
    annotation (Line(origin = {19.999999999999986, -12.999999999999972}, 
      points = {{-13.202796504369527, 3.977677902621693}, {-13.202796504369527, -3.0000000000000284}, {14.169238451935087, -3.0000000000000284}}, 
      color = {28, 193, 208}));
  connect(directionalValve34_H1.port_B, gasVolumeV1.port_A) 
    annotation (Line(origin = {43.999999999999986, -12.999999999999972}, 
      points = {{-5.830761548064913, -3.0000000000000284}, {5.197203495630468, -3.0000000000000284}, {5.197203495630468, 3.977677902621693}}, 
      color = {28, 193, 208}));
  connect(directionalValve34_H1.port_P, pressureSource1.port_B) 
    annotation (Line(origin = {33.999999999999986, -41.99999999999997}, 
      points = {{0.1692384519350867, 5.999999999999972}, {0.1692384519350867, -5.999999999999972}}, 
      color = {28, 193, 208}));
  connect(directionalValve34_H1.port_T, surroundings1.port_A) 
    annotation (Line(origin = {39.999999999999986, -42.99999999999997}, 
      points = {{-1.8307615480649133, 6.999999999999972}, {-1.8307615480649133, -6.900000000000027}, {2.7692384519351236, -6.900000000000027}}, 
      color = {28, 193, 208}));
end PneumaticJack;