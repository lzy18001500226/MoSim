model AirPistol "气枪"
  annotation (Documentation(link = "modelica://TYPneumaticComponents/Resources/HTML/AirPistol.html"), Icon(coordinateSystem(extent = {{-100.0, -100.0}, {100.0, 100.0}}, 
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
    experiment(Algorithm = Dassl, Interval = 1e-05, StartTime = 0, StopTime = 0.013, Tolerance = 1e-05), 
    Diagram(coordinateSystem(extent = {{-140.0, -100.0}, {140.0, 100.0}}, 
      grid = {2.0, 2.0})),Protection(access=Access.nonPackageDuplicate),__MWORKS(ResultViewerManager(resultViewers={
ResultViewer(name="1", executeTrigger=executeTrigger.SimulationFinished, commands={
CreatePlot(id=2, x_display_unit="s", legend_layout=7, left_title_type=2, left_title="位移/m", bottom_title_type=2, bottom_title="时间/s ", right_title_type=2, right_title="速度/（m/s）", fix_time_range_value=0, zoom_x=(0, 0.013), zoom_y_l=(-0.05, 0.25), zoom_y_r=(-10, 70)), 
Plot(y=["mass.s", "massWithStopAndFriction1.s", "massWithStopAndFriction1.v"], colors=["4278190335", "4294901760", "4278222848"]), 
CreatePlot(id=-1, x_display_unit="s", legend_layout=7, left_title_type=2, left_title="压力/Bar", bottom_title_type=2, bottom_title="时间/s ", right_title_type=2, fix_time_range_value=0, sub_plot=(2, 1), zoom_x=(0, 0.013), zoom_y_l=(-5, 25)), 
Plot(y=["fixedBodyPiston.V", "fixedBodyPiston1.V", "gasVolumeV.V"], colors=["4278190335", "4294901760", "4278222848"])})
})));
  Modelica.Mechanics.Translational.Components.Spring spring(c = 3000, s_rel(start = 0), s_rel0 = 0) 
    annotation (Placement(transformation(origin = {-84.0, 8.0}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYPneumaticComponents.Pistons.FixedBodyPiston fixedBodyPiston(ds = 0.02, dr = 0, redeclare model GasMedium = TYGasMedia.MediaProperties.Semi_Perfect.Semi_Perfect, redeclare model GasType = TYGasMedia.MediaTypes.Air, reverse = false) 
    annotation (Placement(transformation(origin = {-50.0, 8.0}, 
      extent = {{10.0, -10.0}, {-10.0, 10.0}})));
  Modelica.Mechanics.Translational.Components.Fixed fixed 
    annotation (Placement(transformation(origin = {-118.0, 8.0}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYPneumaticComponents.Pistons.FixedBodyPiston fixedBodyPiston1(ds = 0.0045, dr = 0, redeclare model GasMedium = TYGasMedia.MediaProperties.Semi_Perfect.Semi_Perfect, redeclare model GasType = TYGasMedia.MediaTypes.Air) 
    annotation (Placement(transformation(origin = {24.0, 7.999999999999986}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  Modelica.Mechanics.Translational.Components.MassWithStopAndFriction massWithStopAndFriction1(m = 0.0005, F_prop = 0.3, F_Coulomb = 0, F_Stribeck = 0, fexp = 0, v_small = 0) 
    annotation (Placement(transformation(origin = {51.999999999999986, 7.999999999999986}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  Modelica.Mechanics.Translational.Sensors.PositionSensor positionSensor 
    annotation (Placement(transformation(origin = {79.99999999999999, 7.999999999999986}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYPneumaticComponents.Auxiliaries.GasVolumeV gasVolumeV(n_ports = 2, V0 = 1e-8, redeclare model GasMedium = TYGasMedia.MediaProperties.Semi_Perfect.Semi_Perfect, redeclare model GasType = TYGasMedia.MediaTypes.Air) 
    annotation (Placement(transformation(origin = {-4.000000000000014, -22.00000000000003}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYPneumaticComponents.Sources.ZeroFlowSource zeroFlowSource(redeclare model GasMedium = TYGasMedia.MediaProperties.Semi_Perfect.Semi_Perfect, redeclare model GasType = TYGasMedia.MediaTypes.Air) 
    annotation (Placement(transformation(origin = {-4.000000000000014, -46.0}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  Modelica.Blocks.Logical.GreaterEqualThreshold greaterEqualThreshold(threshold = 0.16) 
    annotation (Placement(transformation(origin = {116.0, 7.999999999999986}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  Modelica.Mechanics.Translational.Components.Mass mass(m = 0.113, s(start = 0.065)) 
    annotation (Placement(transformation(origin = {-15.999999999999996, 7.999999999999986}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
equation
  connect(fixed.flange, spring.flange_a) 
    annotation (Line(origin = {-106.0, 8.0}, 
      points = {{-12.0, 0.0}, {12.0, 0.0}}, 
      color = {0, 127, 0}));
  connect(spring.flange_b, fixedBodyPiston.flange_b) 
    annotation (Line(origin = {-67.0, 8.0}, 
      points = {{-7.0, 0.0}, {6.782956521739102, 0.0}}, 
      color = {0, 127, 0}));

  connect(fixedBodyPiston.portV_A, gasVolumeV.portV_B[1]) 
    annotation (Line(origin = {-18.000000000000014, -9.0}, 
      points = {{-26.799999999999983, 7.0}, {-26.799999999999983, -6.053183520599275}, {14.03076154806492, -6.053183520599275}}, 
      color = {90, 229, 225}));
  connect(gasVolumeV.portV_B[2], fixedBodyPiston1.portV_A) 
    annotation (Line(origin = {-2.000000000000007, -9.000000000000014}, 
      points = {{-1.9692384519350883, -6.05318352059926}, {20.800000000000008, -6.05318352059926}, {20.800000000000008, 7.0}}, 
      color = {90, 229, 225}));
  connect(zeroFlowSource.port_B, gasVolumeV.port_A) 
    annotation (Line(origin = {-3.999999999999993, -34.0}, 
      points = {{0.07845303867401165, -4.0}, {0.02796504369535846, 4.977677902621693}}, 
      color = {90, 229, 225}));
  connect(positionSensor.s, greaterEqualThreshold.u) 
    annotation (Line(origin = {97.99999999999999, 7.999999999999986}, 
      points = {{-7.0, 0.0}, {6.000000000000014, 0.0}}, 
      color = {0, 0, 127}));
  connect(fixedBodyPiston1.flange_b, massWithStopAndFriction1.flange_a) 
    annotation (Line(origin = {37.999999999999986, 7.999999999999986}, 
      points = {{-3.782956521739088, 0.0}, {4.0, 0.0}}, 
      color = {0, 127, 0}));
  connect(positionSensor.flange, massWithStopAndFriction1.flange_b) 
    annotation (Line(origin = {65.99999999999999, 7.999999999999986}, 
      points = {{4.0, 0.0}, {-4.0, 0.0}}, 
      color = {0, 127, 0}));
  connect(fixedBodyPiston.flange_a, mass.flange_a) 
    annotation (Line(origin = {-33.0, 8.0}, 
      points = {{-6.9102608695651995, 0.0}, {7.0000000000000036, -1.4210854715202004e-14}}, 
      color = {0, 127, 0}));
end AirPistol;