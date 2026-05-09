model HighPressureFuelInjector "高压油喷射器"
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
    experiment(Algorithm = Dassl, Interval = 0.0001, StartTime = 0, StopTime = 0.015, Tolerance = 1e-07, IntegratorStep = 1e-06), 
    Diagram(coordinateSystem(extent = {{-120.0, -120.0}, {120.0, 120.0}}, 
      grid = {2.0, 2.0})), 
    Documentation(link = "modelica://TYThermalHydraulicComponents/Resources/HTML/HighPressureFuelInjector.html"),Protection(access=Access.nonPackageDuplicate),__MWORKS(ResultViewerManager(resultViewers={
ResultViewer(name="1", executeTrigger=executeTrigger.SimulationFinished, commands={
CreatePlot(id=1, x_display_unit="s", legend_layout=7, left_title_type=2, left_title="速度[m/s]", bottom_title_type=2, bottom_title="时间/s", fix_time_range_value=0, zoom_x=(0, 0.015), zoom_y_l=(-0.5, 3)), 
Plot(y=["V_signal.y"], colors=["4278190335"]), 
CreatePlot(id=-1, x_display_unit="s", legend_layout=7, left_title_type=2, left_title="容腔压力/Bar", bottom_title_type=2, bottom_title="时间/s", fix_time_range_value=0, sub_plot=(1, 2), zoom_x=(0, 0.015), zoom_y_l=(-100, 600)), 
Plot(y=["volumeV.p"], colors=["4278190335"]), 
CreatePlot(id=-1, x_display_unit="s", legend_layout=7, left_title_type=2, left_title="喷嘴位移[m]", bottom_title_type=2, bottom_title="时间/s", fix_time_range_value=0, sub_plot=(2, 2), zoom_x=(0, 0.015), zoom_y_l=(-1e-05, 6e-05)), 
Plot(y=["sharpEdgeSeatPoppet.flange_a.s"], colors=["4278190335"]), 
CreatePlot(id=-1, x_display_unit="s", legend_layout=7, left_title_type=2, left_title="控制阀开度", bottom_title_type=2, bottom_title="时间/s", fix_time_range_value=0, sub_plot=(2, 1), zoom_x=(0, 0.015), zoom_y_l=(-0.2, 1.2)), 
Plot(y=["Signal.y"], colors=["4278190335"])})
})));
  TYThermalHydraulicComponents.Pistons.FixedBodyPiston fixedBodyPiston(dr = 0, len0 = 0.017, 
    reverse = true, redeclare model Medium = TYOilMedia.ThermalHydraulicOil.Types._5W30) annotation (Placement(transformation(origin = {46.0, 35.99999999999999}, 
      extent = {{10.0, -10.0}, {-10.0, 10.0}}, 
      rotation = -90.0)));
  TYThermalHydraulicComponents.Auxiliaries.VolumeV volumeV(useHeatPort = true, n_ports = 2, p(start = -1300), T(start = 313.15), V0 = 1e-5, 
    redeclare model Medium = TYOilMedia.ThermalHydraulicOil.Types._5W30) 
    annotation (Placement(transformation(origin = {-10.0, 32.5}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
      rotation = -90.0)));
  TYThermalHydraulicComponents.Pistons.SpringPiston springPiston(ds = 0.005, dr = 0, len0 = 1, s_0 = 0, f_0 = Modelica.Constants.pi / 4 * (3e-3) ^ 2 * 300e5, k0 = 1e6, 
    reverse = true, redeclare model Medium = TYOilMedia.ThermalHydraulicOil.Types._5W30) annotation (Placement(transformation(origin = {46.0, 4.0}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
      rotation = -90.0)));
  TYThermalHydraulicComponents.Sources.Tank tank(p_load = -1300, T_load = 313.15,redeclare model Medium = TYOilMedia.ThermalHydraulicOil.Types._5W30) annotation (Placement(transformation(origin = {11.999999999999996, 9.000000000000002}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
    rotation = -90.0)));
  TYThermalHydraulicComponents.Auxiliaries.VolumeV volumeV1(redeclare model Medium = TYOilMedia.ThermalHydraulicOil.Types._5W30) annotation (Placement(transformation(origin = {23.999999999999996, 9.000000000000002}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
    rotation = -90.0)));
  TYThermalHydraulics.Valves.FlowValves.VSymThrottleValve vSymThrottleValve(diam = 4 * Modelica.Constants.pi, redeclare model Medium = TYOilMedia.ThermalHydraulicOil.Types._5W30) 
    annotation (Placement(transformation(origin = {-54.0, 9.0}, 
      extent = {{10.0, -10.0}, {-10.0, 10.0}}, 
      rotation = -90.0)));
  TYThermalHydraulicComponents.Sources.Tank tank1(p_load = -1300, T_load = 313.15, redeclare model Medium = TYOilMedia.ThermalHydraulicOil.Types._5W30) annotation (Placement(transformation(origin = {-54.0, -14.000000000000004}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  Modelica.Mechanics.Translational.Components.MassWithStopAndFriction massWithStopAndFriction(smax = 5e-5, smin = 0, F_prop = 40, F_Coulomb = 0, F_Stribeck = 0, fexp = 0, m = 0.01) 
    annotation (Placement(transformation(origin = {46.0, -24.0}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
      rotation = -90.0)));
  TYThermalHydraulicComponents.ConicalValveSpool.SharpEdgeSeatPoppet sharpEdgeSeatPoppet(dpop = 0.005, ds = 0.003, dr = 0, 
    reverse = false, redeclare model Medium = TYOilMedia.ThermalHydraulicOil.Types._5W30) annotation (Placement(transformation(origin = {46.0, -52.0}, 
      extent = {{10.0, -10.0}, {-10.0, 10.0}}, 
      rotation = -90.0)));
  TYThermalHydraulicComponents.Sensors.MassFlowSensor massFlowSensor(redeclare model Medium = TYOilMedia.ThermalHydraulicOil.Types._5W30, InterfaceSwitch = true) annotation (Placement(transformation(origin = {-2.0000000000000036, -82.0}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
    rotation = -90.0)));
  TYThermalHydraulicComponents.Auxiliaries.VolumeV volumeV2(redeclare model Medium = TYOilMedia.ThermalHydraulicOil.Types._5W30) annotation (Placement(transformation(origin = {20.0, -59.0}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
    rotation = -90.0)));
  TYThermalHydraulicComponents.Sources.Tank tank2(p_load = -1300, T_load = 313.15, 
    redeclare model Medium = TYOilMedia.ThermalHydraulicOil.Types._5W30) 
    annotation (Placement(transformation(origin = {-2.0, -96.0}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  Modelica.Blocks.Sources.TimeTable Signal(table = {{0.0, 1}, {0.009, 1}, {0.009, 0}, {0.011, 0}, {0.011, 1}, {0.015, 1}}) 
    annotation (Placement(transformation(origin = {-90.0, 5.999999999999993}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  Modelica.Mechanics.Translational.Sources.Speed speed(f_crit = 0, useSupport = false, exact = true) 
    annotation (Placement(transformation(origin = {46.0, 67.99999999999997}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
      rotation = -90.0)));
  Modelica.Blocks.Sources.TimeTable V_signal(table = {{0.0, 0.0}, {0.005, 0}, {0.008, 2.5}, {0.012, 2.5}, {0.015, 0}}) 
    annotation (Placement(transformation(origin = {18.0, 94.0}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYThermalHydraulics.Sources.TemperatureSource temperatureSource 
    annotation (Placement(transformation(origin = {-10.0, 82.0}, 
      extent = {{-10.0, 10.0}, {10.0, -10.0}}, 
      rotation = -90.0)));
  Modelica.Thermal.HeatTransfer.Components.ThermalConductor thermalConductor(G = 1e-4) 
    annotation (Placement(transformation(origin = {-10.0, 54.25}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
      rotation = -90.0)));
equation
  connect(volumeV1.portV_B[1], springPiston.portV_A) 
    annotation (Line(origin = {32.0, 9.0}, 
      points = {{-1.0, 0.0}, {4.0, 0.0}}, 
      color = {255, 170, 0}));
  connect(tank.port_A, volumeV1.port_A) 
    annotation (Line(origin = {8.0, 9.0}, 
      points = {{4.0, 0.0}, {9.0, 0.0}}, 
      color = {255, 170, 0}));
  connect(vSymThrottleValve.port_B, volumeV.port_A) 
    annotation (Line(origin = {-34.0, 7.999999999999979}, 
      points = {{-20.0, 11.0}, {-20.0, 25.0}, {17.0, 25.0}}, 
      color = {255, 170, 0}));
  connect(tank1.port_A, vSymThrottleValve.port_A) 
    annotation (Line(origin = {-54.0, -7.0}, 
      points = {{0.0, -7.0}, {0.0, 6.0}}, 
      color = {255, 170, 0}));
  connect(massWithStopAndFriction.flange_a, springPiston.flange_b) 
    annotation (Line(origin = {46.0, -12.0}, 
      points = {{0.0, -2.0}, {0.0, 6.0}}, 
      color = {0, 127, 0}));
  connect(massWithStopAndFriction.flange_b, sharpEdgeSeatPoppet.flange_b) 
    annotation (Line(origin = {46.0, -36.00000000000002}, 
      points = {{0.0, 2.0}, {0.0, -6.0}}, 
      color = {0, 127, 0}));
  connect(sharpEdgeSeatPoppet.portV_A, volumeV2.portV_B[1]) 
    annotation (Line(origin = {32.0, -59.00000000000002}, 
      points = {{4.0, 0.0}, {-5.0, 0.0}}, 
      color = {255, 170, 0}));
  connect(volumeV2.port_A, massFlowSensor.port_A) 
    annotation (Line(origin = {-3.0, -66.0}, 
      points = {{16.0, 7.0}, {1.0, 7.0}, {1.0, -9.0}}, 
      color = {255, 170, 0}));
  connect(tank2.port_A, massFlowSensor.port_B) 
    annotation (Line(origin = {-2.0, -92.0}, 
      points = {{0.0, -4.0}, {0.0, 3.0}}, 
      color = {255, 170, 0}));
  connect(Signal.y, vSymThrottleValve.u) 
    annotation (Line(origin = {-69.0, 6.0}, 
      points = {{-10.0, 0.0}, {10.0, 0.0}}, 
      color = {0, 0, 127}));
  connect(volumeV.portV_B[1], fixedBodyPiston.portV_A) 
    annotation (Line(origin = {17.0, 31.0}, 
      points = {{-20.0, 2.0}, {19.0, 2.0}, {19.0, 0.0}}, 
      color = {255, 170, 0}));
  connect(volumeV.portV_B[2], sharpEdgeSeatPoppet.portV_B) 
    annotation (Line(origin = {17.0, -5.000000000000021}, 
      points = {{-20.0, 38.0}, {-20.0, -45.0}, {19.0, -45.0}}, 
      color = {255, 170, 0}));
  connect(speed.flange, fixedBodyPiston.flange_b) 
    annotation (Line(origin = {46.0, 52.0}, 
      points = {{0.0, 6.0}, {0.0, -6.0}}, 
      color = {0, 127, 0}));
  connect(V_signal.y, speed.v_ref) 
    annotation (Line(origin = {38.0, 87.0}, 
      points = {{-9.0, 7.0}, {8.0, 7.0}, {8.0, -7.0}}, 
      color = {0, 0, 127}));
  connect(thermalConductor.port_a, temperatureSource.heat_a) 
    annotation (Line(origin = {-10.0, 68.0}, 
      points = {{0.0, -4.0}, {0.0, 6.0}}, 
      color = {191, 0, 0}));
  connect(volumeV.heatPort, thermalConductor.port_b) 
    annotation (Line(origin = {-10.0, 41.0}, 
      points = {{0.0, -3.0}, {0.0, 3.0}}, 
      color = {191, 0, 0}));
end HighPressureFuelInjector;