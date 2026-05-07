model ABSElectromagneticValve "ABS电磁阀"
  TYPneumaticComponents.Pistons.SpringPiston springPiston(k0 = 3000) 
    annotation (Placement(transformation(origin = {-22.827965043695386, 110.00000000000003}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYPneumaticComponents.SlideValveSpool.AnnularOrificeSpool annularOrificeSpool(InterfaceSwitchA = true, InterfaceSwitchB = true, reverse = true) 
    annotation (Placement(transformation(origin = {7.172034956304628, 110.00000000000003}, 
      extent = {{10.0, -10.0}, {-10.0, 10.0}})));
  Modelica.Mechanics.Translational.Components.MassWithStopAndFriction massWithStopAndFriction 
    annotation (Placement(transformation(origin = {37.17203495630463, 110.00000000000003}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYPneumaticComponents.Auxiliaries.GasVolumeV gasVolumeV 
    annotation (Placement(transformation(origin = {-28.058726591760305, 80.00000000000003}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYPneumaticComponents.FlowControlValves.CqOrifice cqOrifice 
    annotation (Placement(transformation(origin = {-0.8279650436953858, 53.99999999999997}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
      rotation = -90.0)));
  TYPneumaticComponents.FlowControlValves.CqOrifice cqOrifice1 
    annotation (Placement(transformation(origin = {14.172034956304628, 53.99999999999997}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
      rotation = -90.0)));
  TYPneumatics.Pipes.Pipe_C pipe_C 
    annotation (Placement(transformation(origin = {-0.8279650436953858, 79.99999999999994}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
      rotation = -90.0)));
  TYPneumatics.Pipes.Pipe_C pipe_C1 
    annotation (Placement(transformation(origin = {14.172034956304628, 79.99999999999994}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
      rotation = -90.0)));
  TYPneumaticComponents.FlowControlValves.CqOrifice cqOrifice2 
    annotation (Placement(transformation(origin = {-0.8279650436953858, 19.999999999999986}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
      rotation = -90.0)));
  TYPneumatics.Auxiliaries.GasCylinder gasCylinder 
    annotation (Placement(transformation(origin = {-0.8279650436954, -14.000000000000071}, 
      extent = {{-10.0, 10.0}, {10.0, -10.0}})));
  TYPneumaticComponents.FlowControlValves.CqOrifice cqOrifice3 
    annotation (Placement(transformation(origin = {-11.999999999999998, -48.00000000000013}, 
      extent = {{10.0, -10.0}, {-10.0, 10.0}})));
  TYPneumatics.Pipes.Pipe_C pipe_C2 
    annotation (Placement(transformation(origin = {14.172034956304628, 19.999999999999986}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
      rotation = -90.0)));
  TYPneumatics.Valves.DirectionalValves.DirectionalValve23_N directionalValve23_N(dynamics = "Static", wn = 100) 
    annotation (Placement(transformation(origin = {-78.82796504369536, 32.00000000000001}, 
      extent = {{-12.0, -10.0}, {12.0, 10.0}})));
  TYPneumatics.Sources.PressureSource pressureSource(constantPressure = 7.999999999999999e5) 
    annotation (Placement(transformation(origin = {-48.0, -119.99999999999999}, 
      extent = {{-10.0, 10.0}, {10.0, -10.0}}, 
      rotation = 90.0)));
  TYPneumatics.Sources.Surroundings surroundings 
    annotation (Placement(transformation(origin = {-84.92796504369534, 10.000000000000018}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYPneumatics.Pipes.Pipe_C pipe_C3 
    annotation (Placement(transformation(origin = {-36.87796504369537, -2.0}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
      rotation = -90.0)));
  TYPneumaticComponents.Pistons.SpringPiston springPiston1(reverse = true) 
    annotation (Placement(transformation(origin = {94.0, -108.0}, 
      extent = {{10.0, 10.0}, {-10.0, -10.0}})));
  TYPneumaticComponents.SlideValveSpool.AnnularOrificeSpool annularOrificeSpool1(InterfaceSwitchA = true, InterfaceSwitchB = true) 
    annotation (Placement(transformation(origin = {62.0, -108.0}, 
      extent = {{-10.0, 10.0}, {10.0, -10.0}})));
  Modelica.Mechanics.Translational.Components.MassWithStopAndFriction massWithStopAndFriction1 
    annotation (Placement(transformation(origin = {30.0, -108.0}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYPneumaticComponents.Auxiliaries.GasVolumeV gasVolumeV1 
    annotation (Placement(transformation(origin = {99.17203495630463, -82.0}, 
      extent = {{-10.0, 10.0}, {10.0, -10.0}})));
  TYPneumatics.Valves.DirectionalValves.DirectionalValve23_N directionalValve23_N1(dynamics = "Static", wn = 100) 
    annotation (Placement(transformation(origin = {-78.82796504369536, -81.99999999999999}, 
      extent = {{12.0, -10.0}, {-12.0, 10.0}})));
  TYPneumatics.Sources.Surroundings surroundings1 
    annotation (Placement(transformation(origin = {-76.82796504369536, -108.00000000000001}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYPneumatics.Sources.Surroundings surroundings2 
    annotation (Placement(transformation(origin = {63.89999999999999, -81.99999999999999}, 
      extent = {{-10.0, 10.0}, {10.0, -10.0}})));
  Modelica.Blocks.Sources.Constant const(k = 40) 
    annotation (Placement(transformation(origin = {-48.00000000000001, 32.00000000000001}, 
      extent = {{10.0, -10.0}, {-10.0, 10.0}})));
  Modelica.Blocks.Sources.Constant const1(k = 40) 
    annotation (Placement(transformation(origin = {-113.99999999999999, -81.99999999999999}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  annotation (Documentation(link = "modelica://TYPneumaticComponents/Resources/HTML/ABSElectromagneticValve.html"), Icon(coordinateSystem(extent = {{-100.0, -100.0}, {100.0, 100.0}}, 
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
    Diagram(coordinateSystem(extent = {{-130.0, -130.0}, {130.0, 130.0}}, 
      grid = {2.0, 2.0})),experiment(Algorithm=Dassl,Interval=0.01,StartTime=0,StopTime=10,Tolerance=1e-07),Protection(access=Access.nonPackageDuplicate),__MWORKS(ResultViewerManager(resultViewers={
ResultViewer(name="1", executeTrigger=executeTrigger.SimulationFinished, commands={
CreatePlot(id=1, x_display_unit="s", legend_layout=7, left_title_type=2, left_title="压力/Bar", bottom_title_type=2, bottom_title="时间/s", fix_time_range_value=0, zoom_x=(0, 10), zoom_y_l=(-2, 10)), 
Plot(y=["gasCylinder.p"], colors=["4278190335"])})
})));
equation
  connect(pressureSource.port_B, cqOrifice3.port_B) 
    annotation (Line(origin = {-39.827965043695386, -37.00000000000003}, 
      points = {{-8.172034956304614, -74.99999999999996}, {17.827965043695386, -74.99999999999996}, {17.827965043695386, -11.0000000000001}}, 
      color = {28, 193, 208}));
  connect(cqOrifice3.port_B, directionalValve23_N.port_T) 
    annotation (Line(origin = {-54.827965043695386, -12.000000000000014}, 
      points = {{32.827965043695386, -36.000000000000114}, {-25.99999999999997, -36.000000000000114}, {-25.99999999999997, 34.00000000000002}}, 
      color = {28, 193, 208}));
  connect(directionalValve23_N.port_P, surroundings.port_A) 
    annotation (Line(origin = {-86.8279650436954, 14.99999999999999}, 
      points = {{2.0000000000000426, 7.000000000000018}, {2.000000000000057, 2.842170943040401e-14}}, 
      color = {28, 193, 208}));
  connect(directionalValve23_N.port_A, gasVolumeV.port_A) 
    annotation (Line(origin = {-54.827965043695386, 62.99999999999996}, 
      points = {{-29.99999999999997, -20.99999999999995}, {-29.99999999999997, 9.000000000000057}, {26.797203495630463, 9.000000000000057}, {26.797203495630463, 9.977677902621792}}, 
      color = {28, 193, 208}));
  connect(gasVolumeV.portV_B[1], springPiston.portV_A) 
    annotation (Line(origin = {-27.827965043695386, 92.99999999999994}, 
      points = {{-0.1999999999999993, -6.053183520599163}, {-0.1999999999999993, 7.000000000000085}}, 
      color = {28, 193, 208}));
  connect(springPiston.flange_b, annularOrificeSpool.flange_b) 
    annotation (Line(origin = {-7.827965043695386, 109.99999999999994}, 
      points = {{-4.7829565217391, 8.526512829121202e-14}, {4.782956521739115, 8.526512829121202e-14}}, 
      color = {0, 127, 0}));
  connect(annularOrificeSpool.flange_a, massWithStopAndFriction.flange_a) 
    annotation (Line(origin = {22.172034956304614, 109.99999999999994}, 
      points = {{-4.910260869565185, 8.526512829121202e-14}, {5.000000000000014, 8.526512829121202e-14}}, 
      color = {0, 127, 0}));
  connect(pipe_C.port_A, annularOrificeSpool.port_B) 
    annotation (Line(origin = {2.172034956304614, 94.99999999999994}, 
      points = {{-2.9999999999999973, -5.0}, {-2.9999999999999973, -1.0}, {3.000000000000014, -1.0}, {3.000000000000014, 5.000000000000085}}, 
      color = {28, 193, 208}));
  connect(annularOrificeSpool.port_A, pipe_C1.port_A) 
    annotation (Line(origin = {14.172034956304614, 94.99999999999994}, 
      points = {{1.4210854715202004e-14, 5.000000000000085}, {1.7763568394002505e-14, -5.0}}, 
      color = {28, 193, 208}));
  connect(pipe_C.port_B, cqOrifice.port_A) 
    annotation (Line(origin = {-0.8279650436953858, 66.99999999999997}, 
      points = {{2.886579864025407e-15, 2.9999999999999716}, {0.0, -3.0}}, 
      color = {28, 193, 208}));
  connect(pipe_C1.port_B, cqOrifice1.port_A) 
    annotation (Line(origin = {14.172034956304614, 66.99999999999997}, 
      points = {{1.7763568394002505e-14, 2.9999999999999716}, {1.4210854715202004e-14, -3.0}}, 
      color = {28, 193, 208}));
  connect(cqOrifice.port_B, cqOrifice2.port_A) 
    annotation (Line(origin = {-0.8279650436953858, 36.99999999999997}, 
      points = {{0.0, 7.0}, {0.0, -6.999999999999986}}, 
      color = {28, 193, 208}));
  connect(cqOrifice1.port_B, pipe_C2.port_A) 
    annotation (Line(origin = {14.172034956304614, 36.99999999999997}, 
      points = {{1.4210854715202004e-14, 7.0}, {1.7763568394002505e-14, -6.999999999999986}}, 
      color = {28, 193, 208}));
  connect(cqOrifice2.port_B, gasCylinder.port_A) 
    annotation (Line(origin = {-0.8279650436953858, 2.9999999999999716}, 
      points = {{0.0, 7.000000000000014}, {-1.4210854715202004e-14, -7.000000000000041}}, 
      color = {28, 193, 208}));
  connect(pipe_C2.port_B, cqOrifice3.port_A) 
    annotation (Line(origin = {1.1720349563046142, -24.00000000000003}, 
      points = {{13.000000000000018, 34.000000000000014}, {13.000000000000018, -24.0000000000001}, {-3.1720349563046124, -24.0000000000001}}, 
      color = {28, 193, 208}));
  connect(springPiston1.portV_A, gasVolumeV1.portV_B[1]) 
    annotation (Line(origin = {98.99999999999997, -93.0}, 
      points = {{0.20000000000003126, -5.0}, {0.20279650436957297, 4.053183520599248}}, 
      color = {28, 193, 208}));
  connect(gasVolumeV1.port_A, directionalValve23_N1.port_A) 
    annotation (Line(origin = {10.172034956304614, -58.00000000000003}, 
      points = {{89.02796504369539, -16.977677902621693}, {89.02796504369539, 0.0}, {-82.99999999999997, 0.0}, {-82.99999999999997, -13.999999999999957}}, 
      color = {28, 193, 208}));
  connect(massWithStopAndFriction1.flange_b, annularOrificeSpool1.flange_a) 
    annotation (Line(origin = {46.172034956304614, -108.00000000000003}, 
      points = {{-6.172034956304614, 2.842170943040401e-14}, {5.738225913260585, 2.842170943040401e-14}}, 
      color = {0, 127, 0}));
  connect(annularOrificeSpool1.flange_b, springPiston1.flange_b) 
    annotation (Line(origin = {78.17203495630461, -108.00000000000003}, 
      points = {{-5.954991478043709, 2.842170943040401e-14}, {5.610921565434481, 2.842170943040401e-14}}, 
      color = {0, 127, 0}));
  connect(directionalValve23_N1.port_P, pressureSource.port_B) 
    annotation (Line(origin = {-63.827965043695386, -72.00000000000003}, 
      points = {{-8.999999999999972, -19.999999999999957}, {-8.999999999999972, -39.99999999999996}, {15.827965043695386, -39.99999999999996}}, 
      color = {28, 193, 208}));
  connect(directionalValve23_N1.port_T, surroundings1.port_A) 
    annotation (Line(origin = {-76.8279650436954, -97.00000000000003}, 
      points = {{4.263256414560601e-14, 5.000000000000043}, {0.10000000000003695, -5.999999999999986}}, 
      color = {28, 193, 208}));
  connect(annularOrificeSpool1.port_A, pipe_C3.port_B) 
    annotation (Line(origin = {9.172034956304614, -49.00000000000003}, 
      points = {{45.827965043695386, -48.99999999999997}, {45.827965043695386, -29.0}, {-46.04999999999998, -29.0}, {-46.04999999999998, 37.00000000000003}}, 
      color = {28, 193, 208}));
  connect(pipe_C3.port_A, cqOrifice2.port_A) 
    annotation (Line(origin = {-11.827965043695386, 21.99999999999997}, 
      points = {{-25.049999999999983, -13.999999999999972}, {-9.0, -13.999999999999972}, {-9.0, 14.0}, {10.126040622758168, 14.0}, {10.126040622758168, 13.75175982529209}, {11.0, 13.75175982529209}, {11.0, 8.000000000000014}}, 
      color = {28, 193, 208}));
  connect(annularOrificeSpool1.port_B, surroundings2.port_A) 
    annotation (Line(origin = {64.17203495630461, -93.00000000000003}, 
      points = {{-0.17203495630461418, -4.999999999999972}, {-0.1720349563046213, 6.000000000000043}}, 
      color = {28, 193, 208}));
  connect(const.y, directionalValve23_N.realin) 
    annotation (Line(origin = {-55.827965043695386, 31.999999999999986}, 
      points = {{-3.1720349563046213, 2.1316282072803006e-14}, {-11.999999999999972, 2.1316282072803006e-14}}, 
      color = {0, 0, 127}));
  connect(directionalValve23_N1.realin, const1.y) 
    annotation (Line(origin = {-56.827965043695386, -82.00000000000003}, 
      points = {{-32.99999999999997, 4.263256414560601e-14}, {-46.1720349563046, 4.263256414560601e-14}}, 
      color = {0, 0, 127}));
end ABSElectromagneticValve;