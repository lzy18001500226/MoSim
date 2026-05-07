model InjectionCircuit "喷射回路"
  annotation (Icon(coordinateSystem(extent = {{-100.0, -100.0}, {100.0, 100.0}}, 
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
    experiment(Algorithm = Dassl, Interval = 0.1, StartTime = 0, StopTime = 50, Tolerance = 1e-07), 
    Diagram(coordinateSystem(extent = {{-100.0, -100.0}, {100.0, 100.0}}, 
      grid = {2.0, 2.0})), 
    Documentation(link = "modelica://TYThermalHydraulicComponents/Resources/HTML/InjectionCircuit.html"),Protection(access=Access.nonPackageDuplicate),__MWORKS(ResultViewerManager(resultViewers={
ResultViewer(name="1", executeTrigger=executeTrigger.SimulationFinished, commands={
CreatePlot(id=1, x_display_unit="s", legend_layout=7, left_title_type=2, left_title="温度/degC", bottom_title_type=2, bottom_title="时间/s", fix_time_range_value=0, zoom_x=(0, 50), zoom_y_l=(10, 80)), 
Plot(y=["pipe_C2.port_B.T", "volumeV1.T_A"], colors=["4278190335", "4294901760"])})
})));
  TYThermalHydraulicComponents.Sources.MHFlowSource flowSource(constantMassflow = 0.3, constantPressure = -1300, constantTemperature = 323.15, 
    redeclare model Medium = TYOilMedia.ThermalHydraulicOil.Types._5W30) 
    annotation (Placement(transformation(origin = {-58.0, 13.999999999999984}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYThermalHydraulicComponents.Sources.MHFlowSource flowSource1(constantTemperature = 323.15, constantPressure = 9.989869999999999e7, constantMassflow = 0.3, 
    redeclare model Medium = TYOilMedia.ThermalHydraulicOil.Types._5W30) 
    annotation (Placement(transformation(origin = {14.000000000000007, 80.0}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYThermalHydraulics.Pipes.Pipe_C pipe_C(d = 0.012, length = 0.4, pin(start = -1300), Tin(start = 323.15), 
    redeclare model Medium = TYOilMedia.ThermalHydraulicOil.Types._5W30) annotation (Placement(transformation(origin = {39.999999999999986, 80.0}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYThermalHydraulicComponents.Auxiliaries.SymOrifice symOrifice(Cqmax = 1, diam = 1e-6, 
    redeclare model Medium = TYOilMedia.ThermalHydraulicOil.Types._5W30) 
    annotation (Placement(transformation(origin = {82.0, 80.0}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYThermalHydraulicComponents.Sources.Tank tank(p_load = -1300, T_load = 293.15, 
    redeclare model Medium = TYOilMedia.ThermalHydraulicOil.Types._5W30) 
    annotation (Placement(transformation(origin = {95.99999999999999, 60.0}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYThermalHydraulicComponents.Pistons.SpringPiston springPiston(ds = 0.015, dr = 0, len0 = 1, s_0 = 0, k0 = 1e6, f_0 = 1000, 
    reverse = true) annotation (Placement(transformation(origin = {-7.105427357601002e-15, 31.99999999999999}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  Modelica.Mechanics.Translational.Components.MassWithStopAndFriction massWithStopAndFriction(smax = 2, smin = 0, F_prop = 40, F_Coulomb = 0, F_Stribeck = 0, fexp = 0, m = 0.01) 
    annotation (Placement(transformation(origin = {25.999999999999996, 31.999999999999996}, 
      extent = {{10.0, -10.0}, {-10.0, 10.0}})));
  TYThermalHydraulicComponents.ConicalValveSpool.SharpEdgeSeatPoppet sharpEdgeSeatPoppet(dpop = 0.015, ds = 0.004, dr = 0, xmax = 0.01, Cqmax = 1, reverse = false, 
    redeclare model Medium = TYOilMedia.ThermalHydraulicOil.Types._5W30) 
    annotation (Placement(transformation(origin = {52.0, 31.999999999999996}, 
      extent = {{10.0, -10.0}, {-10.0, 10.0}})));
  TYThermalHydraulicComponents.Auxiliaries.VolumeV volumeV(redeclare model Medium = TYOilMedia.ThermalHydraulicOil.Types._5W30) annotation (Placement(transformation(origin = {59.0, 3.9999999999999822}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYThermalHydraulicComponents.Auxiliaries.VolumeV volumeV1(redeclare model Medium = TYOilMedia.ThermalHydraulicOil.Types._5W30) annotation (Placement(transformation(origin = {38.0, 3.999999999999983}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYThermalHydraulicComponents.Auxiliaries.VolumeV volumeV2 annotation (Placement(transformation(origin = {-5.000000000000021, 3.999999999999984}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYThermalHydraulicComponents.Sources.Tank tank1(p_load = -1300, T_load = 293.15) annotation (Placement(transformation(origin = {-5.000000000000014, -14.000000000000014}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYThermalHydraulicComponents.Sources.Tank tank2(p_load = -1300, T_load = 293.15, 
    redeclare model Medium = TYOilMedia.ThermalHydraulicOil.Types._5W30) 
    annotation (Placement(transformation(origin = {-96.0, -56.00000000000004}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYThermalHydraulics.Pipes.Pipe_C pipe_C1(redeclare model Medium = TYOilMedia.ThermalHydraulicOil.Types._5W30) 
    annotation (Placement(transformation(origin = {-40.0, 3.999999999999984}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
      rotation = -90.0)));
  TYThermalHydraulicComponents.Auxiliaries.SymOrifice symOrifice1(diam = 0.002, 
    redeclare model Medium = TYOilMedia.ThermalHydraulicOil.Types._5W30) 
    annotation (Placement(transformation(origin = {-40.0, -26.00000000000003}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
      rotation = -90.0)));
  TYThermalHydraulicComponents.Auxiliaries.SymOrifice symOrifice2(diam = 0.002, 
    redeclare model Medium = TYOilMedia.ThermalHydraulicOil.Types._5W30) 
    annotation (Placement(transformation(origin = {-82.0, -46.00000000000001}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYThermalHydraulics.Pipes.Pipe_C pipe_C2(redeclare model Medium = TYOilMedia.ThermalHydraulicOil.Types._5W30) 
    annotation (Placement(transformation(origin = {-58.0, -46.00000000000001}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYThermalHydraulicComponents.Auxiliaries.SymOrifice symOrifice3(diam = 0.002, 
    redeclare model Medium = TYOilMedia.ThermalHydraulicOil.Types._5W30) 
    annotation (Placement(transformation(origin = {-19.99999999999998, -46.00000000000001}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYThermalHydraulics.Pipes.Pipe_C pipe_C3(redeclare model Medium = TYOilMedia.ThermalHydraulicOil.Types._5W30) 
    annotation (Placement(transformation(origin = {10.000000000000007, -46.00000000000001}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
equation
  connect(flowSource1.port_B, pipe_C.port_A) 
    annotation (Line(origin = {25.99999999999997, 80.0}, 
      points = {{-4.0, 0.0}, {4.0, 0.0}}, 
      color = {255, 170, 0}));
  connect(pipe_C.port_B, symOrifice.port_A) 
    annotation (Line(origin = {59.99999999999997, 80.0}, 
      points = {{-10.0, 0.0}, {12.0, 0.0}}, 
      color = {255, 170, 0}));
  connect(symOrifice.port_B, tank.port_A) 
    annotation (Line(origin = {85.99999999999997, 70.0}, 
      points = {{6.0, 10.0}, {10.0, 10.0}, {10.0, -10.0}}, 
      color = {255, 170, 0}));
  connect(volumeV.portV_B[1], sharpEdgeSeatPoppet.portV_A) 
    annotation (Line(origin = {59.0, 16.999999999999986}, 
      points = {{0.0, -6.0}, {0.0, 5.0}}, 
      color = {255, 170, 0}));
  connect(volumeV.port_A, symOrifice.port_A) 
    annotation (Line(origin = {69.99999999999997, 38.999999999999986}, 
      points = {{-11.0, -42.0}, {2.0, -42.0}, {2.0, 41.0}}, 
      color = {255, 170, 0}));
  connect(volumeV1.portV_B[1], sharpEdgeSeatPoppet.portV_B) 
    annotation (Line(origin = {44.0, 16.999999999999986}, 
      points = {{-6.0, -6.0}, {-6.0, -1.0}, {6.0, -1.0}, {6.0, 5.0}}, 
      color = {255, 170, 0}));
  connect(tank1.port_A, volumeV2.port_A) 
    annotation (Line(origin = {-5.0, -8.000000000000014}, 
      points = {{0.0, -6.0}, {0.0, 5.0}}, 
      color = {255, 170, 0}));
  connect(volumeV2.portV_B[1], springPiston.portV_A) 
    annotation (Line(origin = {-5.0, 16.999999999999986}, 
      points = {{0.0, -6.0}, {0.0, 5.0}}, 
      color = {255, 170, 0}));
  connect(flowSource.port_B, pipe_C1.port_A) 
    annotation (Line(origin = {-45.0, 13.999999999999986}, 
      points = {{-5.0, 0.0}, {5.0, 0.0}}, 
      color = {255, 170, 0}));
  connect(pipe_C1.port_B, symOrifice1.port_A) 
    annotation (Line(origin = {-40.0, -11.000000000000014}, 
      points = {{0.0, 5.0}, {0.0, -5.0}}, 
      color = {255, 170, 0}));
  connect(pipe_C3.port_B, volumeV1.port_A) 
    annotation (Line(origin = {29.0, -24.000000000000014}, 
      points = {{-9.0, -22.0}, {8.0, -22.0}, {8.0, 21.0}, {9.0, 21.0}}, 
      color = {255, 170, 0}));
  connect(symOrifice3.port_B, pipe_C3.port_A) 
    annotation (Line(origin = {-5.0, -46.000000000000014}, 
      points = {{-5.0, 0.0}, {5.0, 0.0}}, 
      color = {255, 170, 0}));
  connect(symOrifice1.port_B, pipe_C2.port_B) 
    annotation (Line(origin = {-44.0, -41.000000000000014}, 
      points = {{4.0, 5.0}, {4.0, -5.0}, {-4.0, -5.0}}, 
      color = {255, 170, 0}));
  connect(symOrifice1.port_B, symOrifice3.port_A) 
    annotation (Line(origin = {-35.0, -41.000000000000014}, 
      points = {{-5.0, 5.0}, {-5.0, -5.0}, {5.0, -5.0}}, 
      color = {255, 170, 0}));
  connect(pipe_C2.port_A, symOrifice2.port_B) 
    annotation (Line(origin = {-70.0, -46.000000000000014}, 
      points = {{2.0, 0.0}, {-2.0, 0.0}}, 
      color = {255, 170, 0}));
  connect(symOrifice2.port_A, tank2.port_A) 
    annotation (Line(origin = {-94.0, -51.000000000000014}, 
      points = {{2.0, 5.0}, {-2.0, 5.0}, {-2.0, -5.0}}, 
      color = {255, 170, 0}));
  connect(springPiston.flange_b, massWithStopAndFriction.flange_b) 
    annotation (Line(origin = {13.0, 32.0}, 
      points = {{-3.0, 0.0}, {3.0, 0.0}}, 
      color = {0, 127, 0}));
  connect(massWithStopAndFriction.flange_a, sharpEdgeSeatPoppet.flange_b) 
    annotation (Line(origin = {39.0, 32.0}, 
      points = {{-3.0, 0.0}, {3.0, 0.0}}, 
      color = {0, 127, 0}));
end InjectionCircuit;