model Pneumatic_suspension "气动悬架系统"
  TYPneumatics.Compressors.Compressor compressor(Volume_B(displayUnit = "l") = 0.001, UseVolumeB = true, table_user = {{0.0, 0.1, 0.2}, {1000, 1, 1}, {2000, 1, 1}}, Method = "Table") 
    annotation (Placement(transformation(origin = {-54.0, -42.0}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYPneumatics.Auxiliaries.GasCylinder gasCylinder(pin(start = 9.999999999999999e5), V = 0.012) 
    annotation (Placement(transformation(origin = {-54.0, -80.0}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
      rotation = -180.0)));
  Modelica.Mechanics.Rotational.Sources.Speed speed 
    annotation (Placement(transformation(origin = {-100.0, -42.0}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  Modelica.Blocks.Sources.Constant const(k = 6000 * 3.14 / 30) 
    annotation (Placement(transformation(origin = {-138.0, -42.0}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYPneumatics.Valves.FlowControlValves.ThrottleValve throttleValve 
    annotation (Placement(transformation(origin = {3.999999999999993, 30.000000000000007}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYPneumatics.Pipes.Pipe_C pipe_C(pin(start = 4.999999999999999e5)) 
    annotation (Placement(transformation(origin = {38.0, 30.0}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYPneumatics.Auxiliaries.AirSpring airSpring(pin(start = 4.999999999999999e5), dx_max = 0.12) 
    annotation (Placement(transformation(origin = {146.0, -4.0}, 
      extent = {{10.0, 10.0}, {-10.0, -10.0}})));
  Modelica.Mechanics.Translational.Components.Fixed fixed 
    annotation (Placement(transformation(origin = {146.0, -34.0}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  Modelica.Mechanics.Translational.Components.Mass mass 
    annotation (Placement(transformation(origin = {20.0, 60.0}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  Modelica.Mechanics.Translational.Sources.Force force 
    annotation (Placement(transformation(origin = {-30.0, 60.0}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  Modelica.Blocks.Sources.Constant const1(k = 18000) 
    annotation (Placement(transformation(origin = {-90.0, 59.999999999999986}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  annotation (experiment(Algorithm = Dassl, NumberOfIntervals = 500, StartTime = 0, StopTime = 10, Tolerance = 0.0001), 
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
    Diagram(coordinateSystem(extent = {{-154.0, -110.0}, {180.0, 86.0}}, 
      grid = {2.0, 2.0})), 
    Documentation(link = "modelica://TYPneumatics/Resources/HTML/Pneumatic_suspension.html"),__MWORKS(ResultViewerManager(resultViewers={
ResultViewer(name="1", executeTrigger=executeTrigger.SimulationFinished, commands={
CreatePlot(id=1, x_display_unit="s", legend_layout=7, left_title_type=2, left_title="压力/Bar", bottom_title_type=2, bottom_title="时间/s", fix_time_range_value=0, zoom_x=(0, 10), zoom_y_l=(4.5, 8)), 
Plot(y=["airSpring.pin"], colors=["4278190335"]), 
CreatePlot(id=-1, x_display_unit="s", legend_layout=7, left_title_type=2, left_title="位移/m", bottom_title_type=2, bottom_title="时间/s", fix_time_range_value=0, sub_plot=(2, 1), zoom_x=(0, 10), zoom_y_l=(-0.12, 0.02)), 
Plot(y=["mass.s"], colors=["4278190335"])})
})));
  TYPneumatics.Pipes.Pipe_C pipe_C1(pin(start = 4.999999999999999e5)) 
    annotation (Placement(transformation(origin = {-30.000000000000014, 29.999999999999993}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYPneumatics.Valves.DirectionalValves.DirectionalValve22 directionalValve22_1 
    annotation (Placement(transformation(origin = {-50.0, -4.0}, 
      extent = {{-12.0, -10.0}, {12.0, 10.0}})));
  Modelica.Blocks.Sources.RealExpression realExpression(y = airSpring.pin / 1e5) 
    annotation (Placement(transformation(origin = {146.0, -87.0}, 
      extent = {{23.0, -17.00000000000003}, {-23.0, 16.99999999999997}})));
  Modelica.Blocks.Logical.Switch switch1 
    annotation (Placement(transformation(origin = {-11.999999999999993, -4.0}, 
      extent = {{10.0, -10.0}, {-10.0, 10.0}})));
  Modelica.Blocks.Sources.TimeTable timeTable(table = {{0.0, 40}, {10, 40}}) 
    annotation (Placement(transformation(origin = {38.0, 4.0}, 
      extent = {{10.0, -10.0}, {-10.0, 10.0}})));
  Modelica.Blocks.Sources.Constant const2(k = 0) 
    annotation (Placement(transformation(origin = {-11.999999999999993, -42.0}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  Modelica.Blocks.Discrete.TriggeredSampler triggeredSampler 
    annotation (Placement(transformation(origin = {66.99999999999999, -42.0}, 
      extent = {{10.0, -10.0}, {-10.0, 10.0}})));
  Modelica.Blocks.Logical.GreaterEqualThreshold greaterEqualThreshold(threshold = 7.5) 
    annotation (Placement(transformation(origin = {89.00000000000003, -87.0}, 
      extent = {{10.0, -10.0}, {-10.0, 10.0}})));
  Modelica.Blocks.Sources.Constant const3(k = 1) 
    annotation (Placement(transformation(origin = {106.50000000000003, -42.0}, 
      extent = {{10.0, -10.0}, {-10.0, 10.0}})));
  Modelica.Blocks.Math.RealToBoolean realToBoolean 
    annotation (Placement(transformation(origin = {37.99999999999999, -42.0}, 
      extent = {{10.0, -10.0}, {-10.0, 10.0}})));
equation
  connect(gasCylinder.port_A, compressor.port_A) 
    annotation (Line(origin = {-54.0, -61.0}, 
      points = {{0.0, -9.0}, {0.0, 8.999999999999993}}, 
      color = {90, 229, 225}));
  connect(speed.flange, compressor.flange_a) 
    annotation (Line(origin = {-77.0, -42.0}, 
      points = {{-13.0, 0.0}, {13.0, 0.0}}, 
      color = {0, 0, 0}));
  connect(speed.w_ref, const.y) 
    annotation (Line(origin = {-128.0, -42.0}, 
      points = {{16.0, 0.0}, {1.0, 0.0}}, 
      color = {0, 0, 127}));
  connect(throttleValve.port_B, pipe_C.port_A) 
    annotation (Line(origin = {14.0, 30.0}, 
      points = {{-7.105427357601002e-15, 7.105427357601002e-15}, {14.0, 3.552713678800501e-15}}, 
      color = {90, 229, 225}));
  connect(const1.y, force.f) 
    annotation (Line(origin = {-60.0, 60.0}, 
      points = {{-19.0, -1.4210854715202004e-14}, {18.0, 0.0}}, 
      color = {0, 0, 127}));
  connect(force.flange, mass.flange_a) 
    annotation (Line(origin = {-5.0, 60.0}, 
      points = {{-15.0, 0.0}, {15.0, 0.0}}, 
      color = {0, 127, 0}));
  connect(pipe_C.port_B, airSpring.port_A) 
    annotation (Line(origin = {134.0, 4.0}, 
      points = {{-86.0, 26.000000000000004}, {-4.0, 26.000000000000004}, {-4.0, -22.0}, {8.0, -22.0}, {8.0, -18.0}}, 
      color = {90, 229, 225}));
  connect(fixed.flange, airSpring.flange_b) 
    annotation (Line(origin = {146.0, -24.0}, 
      points = {{0.0, -10.0}, {0.0, 9.999999999999996}}, 
      color = {0, 127, 0}));
  connect(mass.flange_b, airSpring.flange_a) 
    annotation (Line(origin = {49.0, 35.0}, 
      points = {{-19.0, 25.0}, {97.0, 25.0}, {97.0, -29.0}}, 
      color = {0, 127, 0}));
  connect(pipe_C1.port_B, throttleValve.port_A) 
    annotation (Line(origin = {-20.0, 30.0}, 
      points = {{-1.4210854715202004e-14, -3.552713678800501e-15}, {13.999999999999993, 7.105427357601002e-15}}, 
      color = {90, 229, 225}));
  connect(compressor.port_B, directionalValve22_1.port_P) 
    annotation (Line(origin = {-54.0, -23.0}, 
      points = {{0.0, -9.0}, {0.0, 9.2}}, 
      color = {90, 229, 225}));
  connect(directionalValve22_1.port_A, pipe_C1.port_A) 
    annotation (Line(origin = {-47.0, 18.0}, 
      points = {{-7.0, -12.0}, {-7.0, 11.999999999999996}, {6.999999999999986, 11.999999999999996}}, 
      color = {90, 229, 225}));
  connect(switch1.y, directionalValve22_1.realin) 
    annotation (Line(origin = {-31.0, -4.0}, 
      points = {{8.000000000000007, 0.0}, {-8.036299724571414, -0.02377604620407503}}, 
      color = {0, 0, 127}));
  connect(greaterEqualThreshold.u, realExpression.y) 
    annotation (Line(origin = {111.0, -87.00000000000001}, 
      points = {{-9.999999999999972, 1.4210854715202004e-14}, {9.700000000000003, 1.4210854715202004e-14}}, 
      color = {0, 0, 127}));
  connect(greaterEqualThreshold.y, triggeredSampler.trigger) 
    annotation (Line(origin = {73.0, -70.0}, 
      points = {{5.000000000000028, -17.0}, {-6.000000000000014, -17.0}, {-6.000000000000014, 16.200000000000003}}, 
      color = {255, 0, 255}));
  connect(const3.y, triggeredSampler.u) 
    annotation (Line(origin = {87.0, -42.0}, 
      points = {{8.500000000000028, 0.0}, {-8.000000000000014, 0.0}}, 
      color = {0, 0, 127}));
  connect(realToBoolean.u, triggeredSampler.y) 
    annotation (Line(origin = {53.0, -42.0}, 
      points = {{-3.000000000000007, 0.0}, {2.999999999999986, 0.0}}, 
      color = {0, 0, 127}));
  connect(switch1.u2, realToBoolean.y) 
    annotation (Line(origin = {14.0, -23.0}, 
      points = {{-13.999999999999993, 19.0}, {6.0, 19.0}, {6.0, -19.0}, {12.999999999999993, -19.0}}, 
      color = {255, 0, 255}));
  connect(const2.y, switch1.u1) 
    annotation (Line(origin = {7.0, -19.0}, 
      points = {{-7.999999999999993, -23.0}, {7.0, -23.0}, {7.0, 23.0}, {-6.999999999999993, 23.0}}, 
      color = {0, 0, 127}));
  connect(switch1.u3, timeTable.y) 
    annotation (Line(origin = {14.0, -4.0}, 
      points = {{-13.999999999999993, -8.0}, {-4.0, -8.0}, {-4.0, 8.0}, {13.0, 8.0}}, 
      color = {0, 0, 127}));
end Pneumatic_suspension;