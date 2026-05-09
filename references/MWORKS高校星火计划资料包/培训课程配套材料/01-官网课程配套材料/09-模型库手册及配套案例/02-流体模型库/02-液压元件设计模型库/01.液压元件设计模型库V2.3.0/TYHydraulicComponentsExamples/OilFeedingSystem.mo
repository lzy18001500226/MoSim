model OilFeedingSystem "供油系统"
  annotation (Documentation(link = "modelica://TYHydraulicComponents/Resources/HTML/OilFeedingSystem.html"), Icon(coordinateSystem(extent = {{-100.0, -100.0}, {100.0, 100.0}}, 
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
    Diagram(coordinateSystem(extent = {{-260.0, -200.0}, {260.0, 200.0}}, 
      grid = {2.0, 2.0}), graphics = {Rectangle(origin = {1.999999999999993, -3.0}, 
      lineColor = {255, 255, 255}, 
      fillColor = {255, 255, 255}, 
      pattern = LinePattern.None, 
      extent = {{-260.0, 205.0}, {260.0, -205.0}})}), 
    experiment(Algorithm = Dassl, Interval = 0.01, StartTime = 0, StopTime = 12, Tolerance = 1e-07),Protection(access=Access.nonPackageDuplicate),__MWORKS(ResultViewerManager(resultViewers={
ResultViewer(name="仿真结果", executeTrigger=executeTrigger.SimulationFinished, commands={
CreatePlot(id=1, x_display_unit="s", legend_layout=7, left_title_type=2, left_title="流量[l/min]", bottom_title_type=2, bottom_title="时间/s", fix_time_range_value=0, zoom_x=(0, 12), zoom_y_l=(-0.5, 3.5)), 
Plot(y=["symThrottleValve4.port_A.q", "symThrottleValve5.port_A.q", "symThrottleValve2.port_A.q", "symThrottleValve3.port_A.q"], colors=["4278190335", "4294901760", "4278222848", "4294902015"]), 
CreatePlot(id=-1, x_display_unit="s", legend_layout=7, left_title_type=2, left_title="压力[bar]", bottom_title_type=2, bottom_title="时间/s", fix_time_range_value=0, sub_plot=(2, 1), zoom_x=(0, 12), zoom_y_l=(-0.05, 0.2)), 
Plot(y=["pipe_C8.pA"], colors=["4278190335"])})
})));
  TYHydraulicComponents.ConicalValveSpool.ConicalSeatPoppet conicalSeatPoppet(reverse = true, ds = 0.001, dsc = 0.02, dcyl = 0.01, dpop = 0.008, da = 0.006) 
    annotation (Placement(transformation(origin = {-171.0, 92.0}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
      rotation = 90.0)));
  Modelica.Mechanics.Translational.Components.Spring spring(c = 1600) 
    annotation (Placement(transformation(origin = {-172.0, 152.00000000000003}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
      rotation = 90.0)));
  Modelica.Mechanics.Translational.Components.Fixed fixed 
    annotation (Placement(transformation(origin = {-172.0, 170.00000000000003}, 
      extent = {{-10.0, 10.0}, {10.0, -10.0}})));
  Modelica.Mechanics.Translational.Components.Spring spring1(c = 1600) 
    annotation (Placement(transformation(origin = {-85.99999999999997, 152.00000000000003}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
      rotation = 90.0)));
  Modelica.Mechanics.Translational.Components.Fixed fixed1 
    annotation (Placement(transformation(origin = {-86.0, 170.0}, 
      extent = {{-10.0, 10.0}, {10.0, -10.0}})));
  TYHydraulicComponents.ConicalValveSpool.ConicalSeatPoppet conicalSeatPoppet1(reverse = true, ds = 0.001, dsc = 0.02, dcyl = 0.01, dpop = 0.008, da = 0.006) 
    annotation (Placement(transformation(origin = {-85.99999999999997, 92.0}, 
      extent = {{10.0, -10.0}, {-10.0, 10.0}}, 
      rotation = -90.0)));
  TYHydraulics.Valves.FlowValves.BasicModels.SymThrottleValve symThrottleValve(Method = "Q/dp", dpchar = 20000) 
    annotation (Placement(transformation(origin = {-136.0, 62.0}, 
      extent = {{-10.0, 10.0}, {10.0, -10.0}}, 
      rotation = 90.0)));
  TYHydraulicComponents.Auxiliaries.VolumeV volumeV(V0 = 1e-5) 
    annotation (Placement(transformation(origin = {-120.00000000000001, 85.0}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
      rotation = -90.0)));
  TYHydraulicComponents.Auxiliaries.VolumeV volumeV1(V0 = 1e-5) 
    annotation (Placement(transformation(origin = {-154.0, 72.0}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYHydraulics.Resistances.Junctions.AbruptPipe abruptPipe 
    annotation (Placement(transformation(origin = {-136.0, 10.0}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
      rotation = 90.0)));
  TYHydraulics.Resistances.Junctions.GeneralBend generalBend 
    annotation (Placement(transformation(origin = {-132.9110901805825, -52.0}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
      rotation = 90.0)));
  TYHydraulics.Pumps.ConstantPumps.ConstantPump constantPump(displ = 1e-5) 
    annotation (Placement(transformation(origin = {-112.0, -108.0}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYHydraulics.Resistances.Junctions.GeneralBend generalBend1 
    annotation (Placement(transformation(origin = {-108.91109018058252, -158.0}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
      rotation = 90.0)));
  TYHydraulics.Pipes.Pipe_C pipe_C 
    annotation (Placement(transformation(origin = {-136.0, 36.0}, 
      extent = {{-10.0, 10.0}, {10.0, -10.0}}, 
      rotation = 90.0)));
  TYHydraulics.Pipes.Pipe_C pipe_C1 
    annotation (Placement(transformation(origin = {-136.0, -21.0}, 
      extent = {{-10.0, 10.0}, {10.0, -10.0}}, 
      rotation = 90.0)));
  TYHydraulicComponents.Pistons.SpringPiston springPiston(s_0 = 0, ds = 0.03) 
    annotation (Placement(transformation(origin = {-34.999999999999964, -6.0}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
      rotation = -90.0)));
  TYHydraulicComponents.Auxiliaries.VolumeV volumeV2(V0 = 1e-5) 
    annotation (Placement(transformation(origin = {-62.000000000000014, -1.0}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
      rotation = -90.0)));
  TYHydraulicComponents.Sources.Tank tank(p_load = 50000) 
    annotation (Placement(transformation(origin = {-76.0, -1.0301075268817215}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
      rotation = -90.0)));
  Modelica.Mechanics.Translational.Components.Mass mass(m = 0.5) 
    annotation (Placement(transformation(origin = {-34.999999999999964, -30.0}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
      rotation = -90.0)));
  TYHydraulicComponents.DiaphragmLeakageSealings.ViscousFrictionAndLeakage viscousFrictionAndLeakageSpool(ds = 0.03, InterfaceSwitchA = true, InterfaceSwitchB = true) 
    annotation (Placement(transformation(origin = {-34.99999999999996, -54.0}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
      rotation = -90.0)));
  TYHydraulicComponents.SlideValveSpool.OrificeHoleSpool orificeHoleSpool(reverse = true, ds = 0.03, InterfaceSwitchB = true) 
    annotation (Placement(transformation(origin = {-34.99999999999996, -86.0}, 
      extent = {{-10.0, 10.0}, {10.0, -10.0}}, 
      rotation = 90.0)));
  TYHydraulicComponents.Sources.PressureSource pressureSource(constantPressure = 9.999999999999999e5) 
    annotation (Placement(transformation(origin = {-65.49999999999999, -74.0}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYHydraulicComponents.Auxiliaries.VolumeV volumeV3(V0 = 1e-5) 
    annotation (Placement(transformation(origin = {-62.00000000000003, -93.01694240244156}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
      rotation = -90.0)));
  TYHydraulics.Valves.FlowValves.BasicModels.SymThrottleValve symThrottleValve1(diam = 0.005) 
    annotation (Placement(transformation(origin = {-89.00000000000007, -93.01694240244156}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYHydraulics.Pipes.Pipe_C pipe_C2 
    annotation (Placement(transformation(origin = {-112.0, -74.00000000000001}, 
      extent = {{-10.0, 10.0}, {10.0, -10.0}}, 
      rotation = 90.0)));
  TYHydraulics.Pipes.Pipe_C pipe_C3 
    annotation (Placement(transformation(origin = {-112.0, -133.0}, 
      extent = {{-10.0, 10.0}, {10.0, -10.0}}, 
      rotation = 90.0)));
  TYHydraulics.Pipes.Pipe_C pipe_C4 
    annotation (Placement(transformation(origin = {-76.0, -160.86498074267163}, 
      extent = {{-10.0, 10.0}, {10.0, -10.0}}, 
      rotation = 180.0)));
  TYHydraulics.Resistances.Junctions.GeneralBend generalBend2 
    annotation (Placement(transformation(origin = {-46.86498074267162, -176.0}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
      rotation = 180.0)));
  TYHydraulicComponents.Sources.Tank tank1(p_load = 50000) 
    annotation (Placement(transformation(origin = {-89.00000000000007, -186.0}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYHydraulicComponents.Auxiliaries.VolumeV volumeV4(n_ports = 2, V0(displayUnit = "ml") = 1e-5) 
    annotation (Placement(transformation(origin = {-136.0, 114.0}, 
      extent = {{-10.0, 10.0}, {10.0, -10.0}})));
  Modelica.Blocks.Sources.Ramp ramp(height = 4000, duration = 5) 
    annotation (Placement(transformation(origin = {-208.0, -108.00000000000001}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  Modelica.Mechanics.Rotational.Sources.Speed speed 
    annotation (Placement(transformation(origin = {-142.00000000000006, -108.0}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  Modelica.Blocks.Math.Gain gain(k = 2 * Modelica.Constants.pi / 60) 
    annotation (Placement(transformation(origin = {-172.0, -108.0}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYHydraulics.Pipes.Pipe_C pipe_C5 
    annotation (Placement(transformation(origin = {-136.0, 156.0}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
      rotation = -90.0)));
  TYHydraulics.Resistances.Junctions.GeneralBend generalBend3 
    annotation (Placement(transformation(origin = {0.0, 184.0}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
      rotation = -90.0)));
  TYHydraulics.Resistances.Junctions.AbruptPipe abruptPipe1 
    annotation (Placement(transformation(origin = {68.0, 170.00000000000003}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
      rotation = 180.0)));
  TYHydraulics.Resistances.Junctions.GeneralBend generalBend4(delta_degree = 0.523598775598299) 
    annotation (Placement(transformation(origin = {94.0, 101.99999999999999}, 
      extent = {{10.0, -10.0}, {-10.0, 10.0}}, 
      rotation = -90.0)));
  TYHydraulics.Pipes.Pipe_C pipe_C6 
    annotation (Placement(transformation(origin = {30.35563927766982, 170.00000000000003}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYHydraulics.Pipes.Pipe_C pipe_C7 
    annotation (Placement(transformation(origin = {97.08890981941748, 137.99999999999997}, 
      extent = {{-10.0, 10.0}, {10.0, -10.0}}, 
      rotation = 90.0)));
  TYHydraulics.Resistances.Junctions.GeneralTjunction generalTjunction 
    annotation (Placement(transformation(origin = {78.0, 54.0}, 
      extent = {{-10.0, 10.0}, {10.0, -10.0}})));
  TYHydraulics.Resistances.Junctions.GeneralTjunction generalTjunction1 
    annotation (Placement(transformation(origin = {132.91109018058256, 54.0}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYHydraulics.Pipes.Pipe_C pipe_C8 
    annotation (Placement(transformation(origin = {78.0, 78.0}, 
      extent = {{-10.0, 10.0}, {10.0, -10.0}}, 
      rotation = 90.0)));
  TYHydraulics.Pipes.Pipe_C pipe_C9 
    annotation (Placement(transformation(origin = {132.91109018058256, 25.999999999999993}, 
      extent = {{-10.0, 10.0}, {10.0, -10.0}}, 
      rotation = 90.0)));
  TYHydraulics.Pipes.Pipe_C pipe_C10 
    annotation (Placement(transformation(origin = {105.45554509029128, 54.0}, 
      extent = {{-10.0, 10.0}, {10.0, -10.0}})));
  TYHydraulics.Pipes.Pipe_C pipe_C11 
    annotation (Placement(transformation(origin = {52.17781963883491, 54.0}, 
      extent = {{-10.0, 10.0}, {10.0, -10.0}})));
  TYHydraulics.Resistances.Junctions.GeneralBend generalBend5 
    annotation (Placement(transformation(origin = {26.35563927766982, 50.91109018058252}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYHydraulics.Resistances.Junctions.GeneralBend generalBend6 
    annotation (Placement(transformation(origin = {135.77607092325422, -2.000000000000014}, 
      extent = {{10.0, 10.0}, {-10.0, -10.0}}, 
      rotation = -90.0)));
  TYHydraulics.Resistances.Junctions.ProgressivePipe progressivePipe 
    annotation (Placement(transformation(origin = {150.00000000000003, -50.0}, 
      extent = {{10.0, -10.0}, {-10.0, 10.0}}, 
      rotation = -90.0)));
  TYHydraulics.Pipes.Pipe_C pipe_C12 
    annotation (Placement(transformation(origin = {150.0, -79.99999999999999}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
      rotation = 90.0)));
  TYHydraulics.Valves.FlowValves.BasicModels.SymThrottleValve symThrottleValve2 
    annotation (Placement(transformation(origin = {150.0, -110.0}, 
      extent = {{-10.0, 10.0}, {10.0, -10.0}}, 
      rotation = -90.0)));
  TYHydraulicComponents.Sources.PressureSource pressureSource1(constantPressure = 0) 
    annotation (Placement(transformation(origin = {150.0, -140.0}, 
      extent = {{10.0, -10.0}, {-10.0, 10.0}}, 
      rotation = -90.0)));
  TYHydraulics.Resistances.Junctions.GeneralBend generalBend7 
    annotation (Placement(transformation(origin = {198.0, 50.91109018058252}, 
      extent = {{10.0, -10.0}, {-10.0, 10.0}})));
  TYHydraulics.Resistances.Junctions.GeneralBend generalBend8 
    annotation (Placement(transformation(origin = {203.95389056208913, -1.2667294582524349}, 
      extent = {{10.0, 10.0}, {-10.0, -10.0}}, 
      rotation = -90.0)));
  TYHydraulics.Pipes.Pipe_C pipe_C13 
    annotation (Placement(transformation(origin = {150.0, -20.0}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
      rotation = 90.0)));
  TYHydraulics.Pipes.Pipe_C pipe_C14 
    annotation (Placement(transformation(origin = {165.45554509029128, 54.0}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYHydraulics.Pipes.Pipe_C pipe_C15 
    annotation (Placement(transformation(origin = {200.86498074267166, 23.822180361165046}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
      rotation = 90.0)));
  TYHydraulics.Resistances.Junctions.ProgressivePipe progressivePipe1 
    annotation (Placement(transformation(origin = {222.0, -50.0}, 
      extent = {{10.0, -10.0}, {-10.0, 10.0}}, 
      rotation = -90.0)));
  TYHydraulics.Pipes.Pipe_C pipe_C16 
    annotation (Placement(transformation(origin = {222.0, -80.0}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
      rotation = 90.0)));
  TYHydraulics.Valves.FlowValves.BasicModels.SymThrottleValve symThrottleValve3 
    annotation (Placement(transformation(origin = {222.0, -110.0}, 
      extent = {{-10.0, 10.0}, {10.0, -10.0}}, 
      rotation = -90.0)));
  TYHydraulicComponents.Sources.PressureSource pressureSource2(constantPressure = 0) 
    annotation (Placement(transformation(origin = {222.00000000000003, -140.0}, 
      extent = {{10.0, -10.0}, {-10.0, 10.0}}, 
      rotation = -90.0)));
  TYHydraulics.Pipes.Pipe_C pipe_C17 
    annotation (Placement(transformation(origin = {222.0, -22.000000000000014}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
      rotation = 90.0)));
  TYHydraulics.Resistances.Junctions.GeneralBend generalBend9 
    annotation (Placement(transformation(origin = {25.953890562089086, -10.000000000000007}, 
      extent = {{-10.0, 10.0}, {10.0, -10.0}})));
  TYHydraulics.Resistances.Junctions.GeneralBend generalBend10 
    annotation (Placement(transformation(origin = {80.90778112417813, -15.953890562089157}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
      rotation = -90.0)));
  TYHydraulics.Pipes.Pipe_C pipe_C18 
    annotation (Placement(transformation(origin = {23.088909819417424, 19.45554509029126}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
      rotation = 90.0)));
  TYHydraulics.Resistances.Junctions.GeneralTjunction generalTjunction2 
    annotation (Placement(transformation(origin = {83.99669094359561, -74.07999424279396}, 
      extent = {{-10.0, 10.0}, {10.0, -10.0}})));
  TYHydraulics.Pipes.Pipe_C pipe_C19 
    annotation (Placement(transformation(origin = {53.430835843133615, -13.088909819417495}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYHydraulics.Pipes.Pipe_C pipe_C20 
    annotation (Placement(transformation(origin = {83.99669094359561, -45.01694240244156}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
      rotation = -90.0)));
  TYHydraulics.Resistances.Junctions.GeneralBend generalBend11 
    annotation (Placement(transformation(origin = {53.430835843133615, -77.16890406221145}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYHydraulics.Resistances.Junctions.GeneralBend generalBend12 
    annotation (Placement(transformation(origin = {114.56254604405758, -77.16890406221142}, 
      extent = {{10.0, -10.0}, {-10.0, 10.0}})));
  TYHydraulics.Pipes.Pipe_C pipe_C21 
    annotation (Placement(transformation(origin = {50.56585510046195, -106.0}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
      rotation = 90.0)));
  TYHydraulics.Pipes.Pipe_C pipe_C22 
    annotation (Placement(transformation(origin = {117.42752678672926, -106.0}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
      rotation = 90.0)));
  TYHydraulics.Valves.FlowValves.SymThrottleValve symThrottleValve4 
    annotation (Placement(transformation(origin = {50.56585510046195, -134.83109593778855}, 
      extent = {{-10.0, 10.0}, {10.0, -10.0}}, 
      rotation = -90.0)));
  TYHydraulics.Valves.FlowValves.SymThrottleValve symThrottleValve5 
    annotation (Placement(transformation(origin = {117.42752678672926, -136.0}, 
      extent = {{-10.0, 10.0}, {10.0, -10.0}}, 
      rotation = -90.0)));
  TYHydraulicComponents.Sources.PressureSource pressureSource3(constantPressure = 0) 
    annotation (Placement(transformation(origin = {50.56585510046195, -163.66219187557712}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
      rotation = 90.0)));
  TYHydraulicComponents.Sources.PressureSource pressureSource4(constantPressure = 0) 
    annotation (Placement(transformation(origin = {117.42752678672925, -166.0}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
      rotation = 90.0)));
  Modelica.Mechanics.Translational.Components.Mass mass1(m=1) 
    annotation (Placement(transformation(origin = {-171.99999999999997, 124.0}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
      rotation = -90.0)));
  Modelica.Mechanics.Translational.Components.Mass mass2(m=1) 
    annotation (Placement(transformation(origin = {-85.99999999999999, 124.0}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
      rotation = -90.0)));
equation
  connect(spring.flange_b, fixed.flange) 
    annotation (Line(origin = {-172.0, 166.0}, 
      points = {{0.0, -4.0}, {0.0, 4.0}}, 
      color = {0, 127, 0}));
  connect(spring1.flange_b, fixed1.flange) 
    annotation (Line(origin = {-162.0, 176.0}, 
      points = {{76.0, -14.0}, {76.0, -6.0}}, 
      color = {0, 127, 0}));
  connect(volumeV.portV_B[1], conicalSeatPoppet1.portV_A) 
    annotation (Line(origin = {-104.0, 85.0}, 
      points = {{-9.0, 0.0}, {8.0, 0.0}}, 
      color = {0, 127, 255}));
  connect(conicalSeatPoppet.portV_A, volumeV1.portV_B[1]) 
    annotation (Line(origin = {-157.0, 82.0}, 
      points = {{-4.0, 3.0}, {3.0, 3.0}, {3.0, -3.0}}, 
      color = {0, 127, 255}));
  connect(symThrottleValve.port_B, volumeV.port_A) 
    annotation (Line(origin = {-131.0, 79.0}, 
      points = {{-5.0, -7.0}, {-5.0, 6.0}, {4.0, 6.0}}, 
      color = {0, 127, 255}));
  connect(symThrottleValve.port_A, pipe_C.port_B) 
    annotation (Line(origin = {-136.0, 49.0}, 
      points = {{0.0, 3.0}, {0.0, -3.0}}, 
      color = {0, 127, 255}));
  connect(volumeV1.port_A, symThrottleValve.port_A) 
    annotation (Line(origin = {-145.0, 59.0}, 
      points = {{-9.0, 6.0}, {-9.0, -7.0}, {9.0, -7.0}}, 
      color = {0, 127, 255}));
  connect(pipe_C.port_A, abruptPipe.port_B) 
    annotation (Line(origin = {-136.0, 23.0}, 
      points = {{0.0, 3.0}, {0.0, -3.0}}, 
      color = {0, 127, 255}));
  connect(pipe_C1.port_B, abruptPipe.port_A) 
    annotation (Line(origin = {-136.0, -5.0}, 
      points = {{0.0, -6.0}, {0.0, 5.0}}, 
      color = {0, 127, 255}));
  connect(pipe_C1.port_A, generalBend.port_B) 
    annotation (Line(origin = {-136.0, -36.0}, 
      points = {{0.0, 5.0}, {0.0, -6.0}}, 
      color = {0, 127, 255}));
  connect(springPiston.portV_A, volumeV2.portV_B[1]) 
    annotation (Line(origin = {-59.0, -1.0}, 
      points = {{14.0, 0.0}, {4.0, 0.0}}, 
      color = {0, 127, 255}));
  connect(tank.port_A, volumeV2.port_A) 
    annotation (Line(origin = {-72.0, -1.0}, 
      points = {{-4.0, 0.0}, {3.0, 0.0}}, 
      color = {0, 127, 255}));
  connect(viscousFrictionAndLeakageSpool.flange_a, mass.flange_b) 
    annotation (Line(origin = {-35.0, -42.0}, 
      points = {{0.0, -2.0}, {0.0, 2.0}}, 
      color = {0, 127, 0}));
  connect(mass.flange_a, springPiston.flange_b) 
    annotation (Line(origin = {-35.0, -18.0}, 
      points = {{0.0, -2.0}, {0.0, 2.0}}, 
      color = {0, 127, 0}));
  connect(viscousFrictionAndLeakageSpool.port_A, volumeV2.port_A) 
    annotation (Line(origin = {-57.0, -25.0}, 
      points = {{12.0, -24.0}, {-12.0, -24.0}, {-12.0, 24.0}}, 
      color = {0, 127, 255}));
  connect(orificeHoleSpool.flange_b, viscousFrictionAndLeakageSpool.flange_b) 
    annotation (Line(origin = {-35.0, -70.0}, 
      points = {{0.0, -6.0}, {0.0, 6.0}}, 
      color = {0, 127, 0}));
  connect(pressureSource.port_B, viscousFrictionAndLeakageSpool.port_B) 
    annotation (Line(origin = {-51.0, -66.0}, 
      points = {{-7.0, -8.0}, {-3.0, -8.0}, {-3.0, 7.0}, {6.0, 7.0}}, 
      color = {0, 127, 255}));
  connect(orificeHoleSpool.port_B, viscousFrictionAndLeakageSpool.port_B) 
    annotation (Line(origin = {-49.0, -71.0}, 
      points = {{4.0, -13.0}, {-5.0, -13.0}, {-5.0, 12.0}, {4.0, 12.0}}, 
      color = {0, 127, 255}));
  connect(generalBend.port_A, pipe_C2.port_B) 
    annotation (Line(origin = {-117.0, -59.0}, 
      points = {{-6.0, 4.0}, {5.0, 4.0}, {5.0, -5.0}}, 
      color = {0, 127, 255}));
  connect(pipe_C2.port_A, constantPump.port_B) 
    annotation (Line(origin = {-112.0, -91.0}, 
      points = {{0.0, 7.0}, {0.0, -7.0}}, 
      color = {0, 127, 255}));
  connect(symThrottleValve1.port_A, constantPump.port_B) 
    annotation (Line(origin = {-105.0, -95.0}, 
      points = {{6.0, 2.0}, {-7.0, 2.0}, {-7.0, -3.0}}, 
      color = {0, 127, 255}));
  connect(symThrottleValve1.port_B, volumeV3.port_A) 
    annotation (Line(origin = {-74.0, -93.0}, 
      points = {{-5.0, 0.0}, {5.0, 0.0}}, 
      color = {0, 127, 255}));
  connect(volumeV3.portV_B[1], orificeHoleSpool.portV_A) 
    annotation (Line(origin = {-50.0, -93.0}, 
      points = {{-5.0, 0.0}, {5.0, 0.0}}, 
      color = {0, 127, 255}));
  connect(tank1.port_A, generalBend2.port_B) 
    annotation (Line(origin = {-77.00000000000007, -189.0}, 
      points = {{-12.0, 3.0}, {-12.0, 10.0}, {20.0, 10.0}}, 
      color = {0, 127, 255}));
  connect(pipe_C4.port_A, generalBend2.port_A) 
    annotation (Line(origin = {-62.0, -162.0}, 
      points = {{-4.0, 1.0}, {18.0, 1.0}, {18.0, -4.0}}, 
      color = {0, 127, 255}));
  connect(generalBend1.port_A, pipe_C4.port_B) 
    annotation (Line(origin = {-92.0, -161.0}, 
      points = {{-7.0, 0.0}, {6.0, 0.0}}, 
      color = {0, 127, 255}));
  connect(generalBend1.port_B, pipe_C3.port_A) 
    annotation (Line(origin = {-112.0, -145.0}, 
      points = {{0.0, -3.0}, {0.0, 2.0}}, 
      color = {0, 127, 255}));
  connect(pipe_C3.port_B, constantPump.port_A) 
    annotation (Line(origin = {-112.0, -120.0}, 
      points = {{0.0, -3.0}, {0.0, 2.0}}, 
      color = {0, 127, 255}));
  connect(conicalSeatPoppet.portV_B, volumeV4.portV_B[1]) 
    annotation (Line(origin = {-151.0, 100.0}, 
      points = {{-10.0, -6.0}, {4.0, -6.0}, {4.0, 6.0}, {15.0, 6.0}, {15.0, 7.0}}, 
      color = {0, 127, 255}));
  connect(conicalSeatPoppet1.portV_B, volumeV4.portV_B[2]) 
    annotation (Line(origin = {-119.0, 100.0}, 
      points = {{23.0, -6.0}, {8.0, -6.0}, {8.0, 6.0}, {-17.0, 6.0}, {-17.0, 7.0}}, 
      color = {0, 127, 255}));
  connect(gain.y, speed.w_ref) 
    annotation (Line(origin = {-146.00000000000009, -170.0}, 
      points = {{-15.0, 62.0}, {-8.0, 62.0}}, 
      color = {0, 0, 127}));
  connect(speed.flange, constantPump.flange_a) 
    annotation (Line(origin = {-127.0, -108.0}, 
      points = {{-5.0, 0.0}, {5.0, 0.0}}, 
      color = {0, 0, 0}));
  connect(generalBend4.port_A, pipe_C8.port_B) 
    annotation (Line(origin = {40.0, 90.0}, 
      points = {{44.0, 9.0}, {38.0, 9.0}, {38.0, -2.0}}, 
      color = {0, 127, 255}));
  connect(generalBend5.port_B, pipe_C11.port_A) 
    annotation (Line(origin = {39.0, 54.0}, 
      points = {{-3.0, 0.0}, {3.0, 0.0}}, 
      color = {0, 127, 255}));
  connect(pipe_C11.port_B, generalTjunction.port_A) 
    annotation (Line(origin = {65.0, 54.0}, 
      points = {{-3.0, 0.0}, {3.0, 0.0}}, 
      color = {0, 127, 255}));
  connect(generalTjunction.port_B, pipe_C10.port_A) 
    annotation (Line(origin = {92.0, 54.0}, 
      points = {{-4.0, 0.0}, {3.0, 0.0}}, 
      color = {0, 127, 255}));
  connect(pipe_C10.port_B, generalTjunction1.port_A) 
    annotation (Line(origin = {119.0, 54.0}, 
      points = {{-4.0, 0.0}, {4.0, 0.0}}, 
      color = {0, 127, 255}));
  connect(pipe_C9.port_B, generalTjunction1.port_C) 
    annotation (Line(origin = {133.0, 40.0}, 
      points = {{0.0, -4.0}, {0.0, 4.0}}, 
      color = {0, 127, 255}));
  connect(generalBend6.port_B, pipe_C9.port_A) 
    annotation (Line(origin = {133.0, 12.0}, 
      points = {{0.0, -4.0}, {0.0, 4.0}}, 
      color = {0, 127, 255}));
  connect(generalBend6.port_A, pipe_C13.port_B) 
    annotation (Line(origin = {148.0, -7.0}, 
      points = {{-2.0, 2.0}, {2.0, 2.0}, {2.0, -3.0}}, 
      color = {0, 127, 255}));
  connect(pipe_C13.port_A, progressivePipe.port_B) 
    annotation (Line(origin = {150.0, -35.0}, 
      points = {{0.0, 5.0}, {0.0, -5.0}}, 
      color = {0, 127, 255}));
  connect(progressivePipe.port_A, pipe_C12.port_B) 
    annotation (Line(origin = {150.0, -65.0}, 
      points = {{0.0, 5.0}, {0.0, -5.0}}, 
      color = {0, 127, 255}));
  connect(pipe_C16.port_B, progressivePipe1.port_A) 
    annotation (Line(origin = {222.0, -65.0}, 
      points = {{0.0, -5.0}, {0.0, 5.0}}, 
      color = {0, 127, 255}));
  connect(generalBend8.port_A, pipe_C17.port_B) 
    annotation (Line(origin = {218.0, -16.0}, 
      points = {{-4.0, 12.0}, {4.0, 12.0}, {4.0, 4.0}}, 
      color = {0, 127, 255}));
  connect(generalBend7.port_A, pipe_C15.port_B) 
    annotation (Line(origin = {201.0, 38.0}, 
      points = {{0.0, 3.0}, {0.0, -4.0}}, 
      color = {0, 127, 255}));
  connect(pipe_C15.port_A, generalBend8.port_B) 
    annotation (Line(origin = {201.0, 12.0}, 
      points = {{0.0, 2.0}, {0.0, -3.0}}, 
      color = {0, 127, 255}));
  connect(pipe_C17.port_A, progressivePipe1.port_B) 
    annotation (Line(origin = {222.0, -36.0}, 
      points = {{0.0, 4.0}, {0.0, -4.0}}, 
      color = {0, 127, 255}));
  connect(generalBend5.port_A, pipe_C18.port_B) 
    annotation (Line(origin = {23.0, 35.0}, 
      points = {{0.0, 6.0}, {0.0, -6.0}}, 
      color = {0, 127, 255}));
  connect(pipe_C18.port_A, generalBend9.port_A) 
    annotation (Line(origin = {23.0, 5.0}, 
      points = {{0.0, 4.0}, {0.0, -5.0}}, 
      color = {0, 127, 255}));
  connect(generalBend9.port_B, pipe_C19.port_A) 
    annotation (Line(origin = {40.0, -13.0}, 
      points = {{-4.0, 0.0}, {3.0, 0.0}}, 
      color = {0, 127, 255}));
  connect(pipe_C19.port_B, generalBend10.port_A) 
    annotation (Line(origin = {67.0, -13.0}, 
      points = {{-4.0, 0.0}, {4.0, 0.0}}, 
      color = {0, 127, 255}));
  connect(generalBend10.port_B, pipe_C20.port_A) 
    annotation (Line(origin = {84.0, -31.0}, 
      points = {{0.0, 5.0}, {0.0, -4.0}}, 
      color = {0, 127, 255}));
  connect(pipe_C20.port_B, generalTjunction2.port_C) 
    annotation (Line(origin = {84.0, -60.0}, 
      points = {{0.0, 5.0}, {0.0, -4.0}}, 
      color = {0, 127, 255}));
  connect(generalBend11.port_A, pipe_C21.port_B) 
    annotation (Line(origin = {51.0, -91.0}, 
      points = {{0.0, 4.0}, {0.0, -5.0}}, 
      color = {0, 127, 255}));
  connect(pipe_C22.port_B, generalBend12.port_A) 
    annotation (Line(origin = {117.0, -91.0}, 
      points = {{0.0, -5.0}, {0.0, 4.0}}, 
      color = {0, 127, 255}));
  connect(generalTjunction2.port_B, generalBend12.port_B) 
    annotation (Line(origin = {100.0, -74.0}, 
      points = {{-6.0, 0.0}, {5.0, 0.0}}, 
      color = {0, 127, 255}));
  connect(generalBend11.port_B, generalTjunction2.port_A) 
    annotation (Line(origin = {69.0, -74.0}, 
      points = {{-6.0, 0.0}, {5.0, 0.0}}, 
      color = {0, 127, 255}));
  connect(generalBend3.port_B, pipe_C6.port_A) 
    annotation (Line(origin = {12.0, 172.0}, 
      points = {{-9.0, 2.0}, {-9.0, 0.0}, {8.0, 0.0}, {8.0, -2.0}}, 
      color = {0, 127, 255}));
  connect(pipe_C6.port_B, abruptPipe1.port_B) 
    annotation (Line(origin = {49.0, 170.0}, 
      points = {{-9.0, 0.0}, {9.0, 0.0}}, 
      color = {0, 127, 255}));
  connect(abruptPipe1.port_A, pipe_C7.port_B) 
    annotation (Line(origin = {88.0, 159.0}, 
      points = {{-10.0, 11.0}, {9.0, 11.0}, {9.0, -11.0}}, 
      color = {0, 127, 255}));
  connect(pipe_C7.port_A, generalBend4.port_B) 
    annotation (Line(origin = {97.0, 120.0}, 
      points = {{0.0, 8.0}, {0.0, -8.0}}, 
      color = {0, 127, 255}));
  connect(generalTjunction1.port_B, pipe_C14.port_A) 
    annotation (Line(origin = {149.0, 54.0}, 
      points = {{-6.0, 0.0}, {6.0, 0.0}}, 
      color = {0, 127, 255}));
  connect(pipe_C14.port_B, generalBend7.port_B) 
    annotation (Line(origin = {182.0, 54.0}, 
      points = {{-7.0, 0.0}, {6.0, 0.0}}, 
      color = {0, 127, 255}));
  connect(conicalSeatPoppet.flange_b, mass1.flange_b) 
    annotation (Line(origin = {-171.0, 108.0}, 
      points = {{0.0, -6.0}, {0.0, 6.0}, {-1.0, 6.0}}, 
      color = {0, 127, 0}));
  connect(mass1.flange_a, spring.flange_a) 
    annotation (Line(origin = {-172.0, 138.0}, 
      points = {{0.0, -4.0}, {0.0, 4.0}}, 
      color = {0, 127, 0}));
  connect(mass2.flange_a, spring1.flange_a) 
    annotation (Line(origin = {-86.0, 138.0}, 
      points = {{0.0, -4.0}, {0.0, 4.0}}, 
      color = {0, 127, 0}));
  connect(conicalSeatPoppet1.flange_b, mass2.flange_b) 
    annotation (Line(origin = {-86.0, 108.0}, 
      points = {{0.0, -6.0}, {0.0, 6.0}}, 
      color = {0, 127, 0}));
  connect(volumeV4.port_A, pipe_C5.port_B) 
    annotation (Line(origin = {-136.0, 134.0}, 
      points = {{0.0, -13.0}, {0.0, 12.0}}, 
      color = {0, 127, 255}));
  connect(pipe_C5.port_A, generalBend3.port_A) 
    annotation (Line(origin = {-73.0, 178.0}, 
      points = {{-63.0, -12.0}, {-63.0, 9.0}, {63.0, 9.0}}, 
      color = {0, 127, 255}));
  connect(generalTjunction.port_C, pipe_C8.port_A) 
    annotation (Line(origin = {78.0, 66.0}, 
      points = {{0.0, -2.0}, {0.0, 2.0}}, 
      color = {0, 127, 255}));
  connect(gain.u, ramp.y) 
    annotation (Line(origin = {-190.0, -108.0}, 
      points = {{6.0, 0.0}, {-7.0, -1.4210854715202004e-14}}, 
      color = {0, 0, 127}));
  connect(pipe_C21.port_A, symThrottleValve4.port_A) 
    annotation (Line(origin = {51.0, -120.0}, 
      points = {{-0.43414489953804747, 4.0}, {-0.43414489953804747, -4.831095937788547}}, 
      color = {0, 127, 255}));
  connect(symThrottleValve4.port_B, pressureSource3.port_B) 
    annotation (Line(origin = {51.0, -151.0}, 
      points = {{-0.43414489953804747, 6.168904062211453}, {-0.43414489953804747, -5.662191875577122}}, 
      color = {0, 127, 255}));
  connect(pipe_C22.port_A, symThrottleValve5.port_A) 
    annotation (Line(origin = {117.0, -121.0}, 
      points = {{0.4275267867292598, 5.0}, {0.4275267867292598, -5.0}}, 
      color = {0, 127, 255}));
  connect(symThrottleValve5.port_B, pressureSource4.port_B) 
    annotation (Line(origin = {117.0, -152.0}, 
      points = {{0.4275267867292598, 6.0}, {0.4275267867292456, -7.0}}, 
      color = {0, 127, 255}));
  connect(pipe_C12.port_A, symThrottleValve2.port_A) 
    annotation (Line(origin = {150.0, -95.0}, 
      points = {{0.0, 5.000000000000014}, {0.0, -5.0}}, 
      color = {0, 127, 255}));
  connect(symThrottleValve2.port_B, pressureSource1.port_B) 
    annotation (Line(origin = {150.0, -126.0}, 
      points = {{0.0, 6.0}, {0.0, -7.0}}, 
      color = {0, 127, 255}));
  connect(pipe_C16.port_A, symThrottleValve3.port_A) 
    annotation (Line(origin = {222.0, -95.0}, 
      points = {{0.0, 5.0}, {0.0, -5.0}}, 
      color = {0, 127, 255}));
  connect(symThrottleValve3.port_B, pressureSource2.port_B) 
    annotation (Line(origin = {222.0, -126.0}, 
      points = {{0.0, 6.0}, {2.842170943040401e-14, -7.0}}, 
      color = {0, 127, 255}));
end OilFeedingSystem;