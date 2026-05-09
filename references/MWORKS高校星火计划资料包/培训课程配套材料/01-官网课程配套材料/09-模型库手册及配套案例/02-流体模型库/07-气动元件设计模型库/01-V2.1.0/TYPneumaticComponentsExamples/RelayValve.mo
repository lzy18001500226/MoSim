model RelayValve "继动阀"
  TYPneumaticComponents.Pistons.SpringPiston springPiston(InterfaceSwitch = true, f_0 = 40, s_0 = 0, k0 = 1500) 
    annotation (Placement(transformation(origin = {-120.0, 78.0}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYPneumaticComponents.ConicalValveSpool.PlainSeatPoppet plainSeatPoppet(reverse = true, InterfaceSwitchA = true, InterfaceSwitchB = true) 
    annotation (Placement(transformation(origin = {-90.0, 78.0}, 
      extent = {{10.0, -10.0}, {-10.0, 10.0}})));
  Modelica.Mechanics.Translational.Components.MassWithStopAndFriction massWithStopAndFriction(m = 0.1, F_prop = 0, F_Coulomb = 0, F_Stribeck = 0) 
    annotation (Placement(transformation(origin = {-60.0, 78.0}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYPneumaticComponents.Pistons.Piston piston(reverse = true, InterfaceSwitch = true, ds = 0.031, dr = 0.028) 
    annotation (Placement(transformation(origin = {-30.0, 78.0}, 
      extent = {{10.0, -10.0}, {-10.0, 10.0}})));
  TYPneumaticComponents.ConicalValveSpool.PlainSeatPoppet plainSeatPoppet1(InterfaceSwitchA = true, InterfaceSwitchB = true, ds = 0.031, dr = 0.028, df = 0.032) 
    annotation (Placement(transformation(origin = {0.0, 78.0}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  Modelica.Mechanics.Translational.Components.ElastoGap elastoGap(s_rel(displayUnit = "mm", start = 0.0005, fixed = true), c = 1e6, d = 1e5) 
    annotation (Placement(transformation(origin = {30.000000000000004, 78.0}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYPneumaticComponents.Pistons.FixedBodyPiston fixedBodyPiston(InterfaceSwitch = true, ds = 0.09, dr = 0.02) 
    annotation (Placement(transformation(origin = {60.0, 78.0}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYPneumaticComponents.Pistons.FixedBodyPiston fixedBodyPiston1(reverse = true, InterfaceSwitch = true, ds = 0.09, dr = 0.02) 
    annotation (Placement(transformation(origin = {90.0, 78.0}, 
      extent = {{10.0, -10.0}, {-10.0, 10.0}})));
  Modelica.Mechanics.Translational.Components.MassWithStopAndFriction massWithStopAndFriction1(m = 0.2, F_prop = 0, F_Coulomb = 0, F_Stribeck = 0) 
    annotation (Placement(transformation(origin = {119.99999999999994, 78.0}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYPneumaticComponents.FlowControlValves.CqOrifice cqOrifice 
    annotation (Placement(transformation(origin = {-97.0, 5.9999999999999964}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
      rotation = -90.0)));
  TYPneumaticComponents.FlowControlValves.CqOrifice cqOrifice1 
    annotation (Placement(transformation(origin = {-76.0, 5.999999999999993}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
      rotation = -90.0)));
  TYPneumaticComponents.FlowControlValves.CqOrifice cqOrifice2 
    annotation (Placement(transformation(origin = {95.19999999999996, 21.999999999999996}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
      rotation = -90.0)));
  TYPneumaticComponents.FlowControlValves.CqOrifice cqOrifice3 
    annotation (Placement(transformation(origin = {-24.8, -62.0}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
      rotation = -90.0)));
  TYPneumatics.Pipes.Pipe_C pipe_C(D(displayUnit = "mm") = 0.005) 
    annotation (Placement(transformation(origin = {-97.0, 42.0}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
      rotation = -90.0)));
  TYPneumatics.Sources.PressureSource pressureSource(constantPressure = 7.999999999999999e5) 
    annotation (Placement(transformation(origin = {-111.99999999999999, -24.0}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
      rotation = 90.0)));
  TYPneumatics.Pipes.Pipe_C pipe_C1(D = 0.005) 
    annotation (Placement(transformation(origin = {-76.0, 42.0}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
      rotation = -90.0)));
  TYPneumatics.Pipes.Pipe_C pipe_C2(D = 0.005) 
    annotation (Placement(transformation(origin = {-76.0, -24.0}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
      rotation = -90.0)));
  TYPneumatics.Auxiliaries.GasCylinder gasCylinder 
    annotation (Placement(transformation(origin = {-24.8, -92.0}, 
      extent = {{-10.0, 10.0}, {10.0, -10.0}})));
  TYPneumatics.Sources.Surroundings surroundings 
    annotation (Placement(transformation(origin = {1.8999999999999986, 50.0}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYPneumatics.Pipes.Pipe_C pipe_C3(D = 0.005) 
    annotation (Placement(transformation(origin = {95.19999999999996, 50.0}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
      rotation = -90.0)));
  TYPneumatics.Sources.PressureSource pressureSource1(inputType_p = 2, heightPressure = 7.999999999999999e5) 
    annotation (Placement(transformation(origin = {95.2, -12.000000000000004}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
      rotation = 90.0)));
  annotation (experiment(Algorithm=Dassl,StartTime=0,StopTime=10,Tolerance=1e-07,Interval=0.01), 
    Documentation(link = "modelica://TYPneumaticComponents/Resources/HTML/RelayValve.html"), Icon(coordinateSystem(extent = {{-100.0, -100.0}, {100.0, 100.0}}, 
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
    Diagram(coordinateSystem(extent = {{-140.0, -120.0}, {140.0, 120.0}}, 
      grid = {2.0, 2.0})),Protection(access=Access.nonPackageDuplicate),__MWORKS(ResultViewerManager(resultViewers={
ResultViewer(name="1", executeTrigger=executeTrigger.SimulationFinished, commands={
CreatePlot(id=1, x_display_unit="s", legend_layout=7, left_title_type=2, left_title="压力/Bar", bottom_title_type=2, bottom_title="时间/s", fix_time_range_value=0, zoom_x=(0, 10), zoom_y_l=(-1, 6)), 
Plot(y=["gasCylinder.p"], colors=["4278190335"])})
})));
equation
  connect(springPiston.flange_b, plainSeatPoppet.flange_b) 
    annotation (Line(origin = {-105.0, 78.0}, 
      points = {{-4.782956521739095, 0.0}, {4.782956521739095, 0.0}}, 
      color = {0, 127, 0}));
  connect(plainSeatPoppet.flange_a, massWithStopAndFriction.flange_a) 
    annotation (Line(origin = {-75.0, 78.0}, 
      points = {{-4.910260869565207, 0.0}, {5.0, 0.0}}, 
      color = {0, 127, 0}));
  connect(massWithStopAndFriction.flange_b, piston.flange_b) 
    annotation (Line(origin = {-45.0, 78.0}, 
      points = {{-5.0, 0.0}, {4.782956521739102, 0.0}}, 
      color = {0, 127, 0}));
  connect(piston.flange_a, plainSeatPoppet1.flange_a) 
    annotation (Line(origin = {-15.0, 78.0}, 
      points = {{-4.9102608695651995, 0.0}, {4.9102608695651995, 0.0}}, 
      color = {0, 127, 0}));
  connect(plainSeatPoppet1.flange_b, elastoGap.flange_a) 
    annotation (Line(origin = {15.0, 78.0}, 
      points = {{-4.7829565217391, 0.0}, {5.0000000000000036, 0.0}}, 
      color = {0, 127, 0}));
  connect(elastoGap.flange_b, fixedBodyPiston.flange_a) 
    annotation (Line(origin = {45.0, 78.0}, 
      points = {{-5.0, 0.0}, {4.9102608695651995, 0.0}}, 
      color = {0, 127, 0}));
  connect(fixedBodyPiston.flange_b, fixedBodyPiston1.flange_b) 
    annotation (Line(origin = {75.0, 78.0}, 
      points = {{-4.782956521739095, 0.0}, {4.782956521739095, 0.0}}, 
      color = {0, 127, 0}));
  connect(fixedBodyPiston1.flange_a, massWithStopAndFriction1.flange_a) 
    annotation (Line(origin = {105.0, 78.0}, 
      points = {{-4.910260869565207, 0.0}, {4.999999999999943, 0.0}}, 
      color = {0, 127, 0}));
  connect(pipe_C.port_A, plainSeatPoppet.port_B) 
    annotation (Line(origin = {-94.0, 60.0}, 
      points = {{-3.0, -8.0}, {-3.0, -2.0}, {2.0, -2.0}, {2.0, 8.0}}, 
      color = {28, 193, 208}));
  connect(cqOrifice.port_A, pipe_C.port_B) 
    annotation (Line(origin = {-97.0, 24.0}, 
      points = {{0.0, -8.000000000000004}, {0.0, 8.0}}, 
      color = {28, 193, 208}));
  connect(pressureSource.port_B, cqOrifice.port_B) 
    annotation (Line(origin = {-104.0, -10.0}, 
      points = {{-7.999999999999986, -6.0}, {-7.999999999999986, 2.9999999999999964}, {7.0, 2.9999999999999964}, {7.0, 5.9999999999999964}}, 
      color = {28, 193, 208}));
  connect(pressureSource.port_B, springPiston.port_A) 
    annotation (Line(origin = {-119.0, 26.0}, 
      points = {{7.000000000000014, -42.0}, {7.000000000000014, -32.0}, {-6.200000000000003, -32.0}, {-6.200000000000003, 42.0}}, 
      color = {28, 193, 208}));
  connect(plainSeatPoppet.port_A, pipe_C1.port_A) 
    annotation (Line(origin = {-79.0, 60.0}, 
      points = {{-4.0, 8.0}, {-4.0, -2.0}, {3.0, -2.0}, {3.0, -8.0}}, 
      color = {28, 193, 208}));
  connect(pipe_C1.port_B, cqOrifice1.port_A) 
    annotation (Line(origin = {-76.0, 24.0}, 
      points = {{0.0, 8.0}, {0.0, -8.000000000000007}}, 
      color = {28, 193, 208}));
  connect(cqOrifice1.port_B, pipe_C2.port_A) 
    annotation (Line(origin = {-76.0, -9.0}, 
      points = {{0.0, 4.999999999999993}, {0.0, -5.0}}, 
      color = {28, 193, 208}));
  connect(pipe_C2.port_B, piston.port_A) 
    annotation (Line(origin = {-50.0, 13.0}, 
      points = {{-26.0, -47.0}, {-26.0, -55.0}, {25.2, -55.0}, {25.2, 55.0}}, 
      color = {28, 193, 208}));
  connect(gasCylinder.port_A, cqOrifice3.port_B) 
    annotation (Line(origin = {-25.0, -82.0}, 
      points = {{0.1999999999999993, 0.0}, {0.1999999999999993, 10.0}}, 
      color = {28, 193, 208}));
  connect(cqOrifice3.port_A, piston.port_A) 
    annotation (Line(origin = {-25.0, 7.0}, 
      points = {{0.1999999999999993, -59.0}, {0.1999999999999993, 61.0}}, 
      color = {28, 193, 208}));
  connect(pipe_C2.port_B, plainSeatPoppet1.port_A) 
    annotation (Line(origin = {-41.0, 13.0}, 
      points = {{-35.0, -47.0}, {-35.0, -55.0}, {34.0, -55.0}, {34.0, 55.0}}, 
      color = {28, 193, 208}));
  connect(plainSeatPoppet1.port_B, surroundings.port_A) 
    annotation (Line(origin = {2.0, 62.0}, 
      points = {{0.0, 6.0}, {-1.3322676295501878e-15, -7.0}}, 
      color = {28, 193, 208}));
  connect(pipe_C2.port_B, fixedBodyPiston.port_A) 
    annotation (Line(origin = {-11.0, 13.0}, 
      points = {{-65.0, -47.0}, {-65.0, -55.0}, {65.8, -55.0}, {65.8, 55.0}}, 
      color = {28, 193, 208}));
  connect(fixedBodyPiston1.port_A, pipe_C3.port_A) 
    annotation (Line(origin = {95.0, 64.0}, 
      points = {{0.20000000000000284, 4.0}, {0.1999999999999602, -4.0}}, 
      color = {28, 193, 208}));
  connect(pipe_C3.port_B, cqOrifice2.port_A) 
    annotation (Line(origin = {95.0, 36.0}, 
      points = {{0.1999999999999602, 4.0}, {0.1999999999999602, -4.0000000000000036}}, 
      color = {28, 193, 208}));
  connect(cqOrifice2.port_B, pressureSource1.port_B) 
    annotation (Line(origin = {95.0, 4.0}, 
      points = {{0.1999999999999602, 7.9999999999999964}, {0.20000000000000284, -8.000000000000004}}, 
      color = {28, 193, 208}));
end RelayValve;