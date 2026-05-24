model PressureRegulation "压力调节器"
  annotation (Documentation(link = "modelica://TYPneumaticComponents/Resources/HTML/PressureRegulation.html"), Icon(coordinateSystem(extent = {{-100.0, -100.0}, {100.0, 100.0}}, 
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
    Diagram(coordinateSystem(extent = {{-100.0, -120.0}, {100.0, 120.0}}, 
      grid = {2.0, 2.0})), 
    experiment(Algorithm = Dassl, Interval = 0.001, StartTime = 0, StopTime = 3, Tolerance = 1e-07),Protection(access=Access.nonPackageDuplicate),__MWORKS(ResultViewerManager(resultViewers={
ResultViewer(name="1", executeTrigger=executeTrigger.SimulationFinished, commands={
CreatePlot(id=2, x_display_unit="s", legend_layout=7, left_title_type=2, left_title="控制信号", bottom_title_type=2, bottom_title="时间/s", right_title_type=2, fix_time_range_value=0, zoom_x=(0, 3), zoom_y_l=(-0.2, 1.2)), 
Plot(y=["varThrottleValve.u", "varThrottleValve1.u"], colors=["4278190335", "4294901760"]), 
CreatePlot(id=-1, x_display_unit="s", legend_layout=7, left_title_type=2, left_title="压力/Bar", bottom_title_type=2, bottom_title="时间/s", right_title_type=2, fix_time_range_value=0, sub_plot=(1, 2), zoom_x=(0, 3), zoom_y_l=(-1, 6)), 
Plot(y=["varThrottleValve1.port_A.p"], colors=["4278190335"]), 
CreatePlot(id=-1, x_display_unit="s", legend_layout=7, left_title_type=2, left_title="压力/Bar", bottom_title_type=2, bottom_title="时间/s", right_title_type=2, fix_time_range_value=0, sub_plot=(2, 2), zoom_x=(0, 3), zoom_y_l=(-0.005, 0.02)), 
Plot(y=["varThrottleValve1.port_A.m_flow"], colors=["4278190335"]), 
CreatePlot(id=-1, x_display_unit="s", legend_layout=7, left_title_type=2, left_title="位移/mm", bottom_title_type=2, bottom_title="时间/s", right_title_type=2, fix_time_range_value=0, sub_plot=(2, 1), zoom_x=(0, 3), zoom_y_l=(-0.5, 2.5)), 
Plot(y=["massWithStopAndFriction.s"], colors=["4278190335"])})
})));
  TYPneumaticComponents.Sources.PressureSource pressureSource1(constantPressure = 1e7, redeclare model GasType = TYGasMedia.MediaTypes.CH4_methane) 
    annotation (Placement(transformation(origin = {-20.0, 100.00000000000001}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
      rotation = -90.0)));
  TYPneumatics.Valves.FlowControlValves.VarThrottleValve varThrottleValve(Amax(displayUnit = "cm2") = 3.14159e-6, redeclare model GasType = TYGasMedia.MediaTypes.CH4_methane) 
    annotation (Placement(transformation(origin = {-20.0, 72.0}, 
      extent = {{10.0, -10.0}, {-10.0, 10.0}}, 
      rotation = 90.0)));
  TYPneumaticComponents.ConicalValveSpool.PlainSeatPoppet plainSeatPoppet1(df = 0.005, ds = 0.003, redeclare model GasType = TYGasMedia.MediaTypes.CH4_methane) 
    annotation (Placement(transformation(origin = {-39.99999999999994, 22.0}, 
      extent = {{-10.0, 10.0}, {10.0, -10.0}}, 
      rotation = -90.0)));
  TYPneumaticComponents.Auxiliaries.GasVolumeV gasVolumeV3(T(start = 293), V0(displayUnit = "l") = 1e-6, Text = 293, redeclare model GasType = TYGasMedia.MediaTypes.CH4_methane) 
    annotation (Placement(transformation(origin = {-19.97203495630461, 46.98461922596753}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
      rotation = 180.0)));
  TYPneumaticComponents.Pistons.SpringPiston springPiston1(len0 = 0.01, k0 = 10000, f_0 = (30e-3 ^ 2 - (5e-3 ^ 2 - 3e-3 ^ 2)) * Modelica.Constants.pi / 4 * 5e5 - 100e5 * Modelica.Constants.pi * 3e-3 ^ 2 / 4 - 1e5 * (30e-3 ^ 2 - 5e-3 ^ 2) * Modelica.Constants.pi / 4, s_0 = 0, redeclare model GasType = TYGasMedia.MediaTypes.CH4_methane, dr = 0.01, InterfaceSwitch = true) 
    annotation (Placement(transformation(origin = {-39.99999999999994, -10.0}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
      rotation = -90.0)));
  TYPneumatics.Sources.Surroundings surroundingsV2(redeclare model GasType = TYGasMedia.MediaTypes.CH4_methane) 
    annotation (Placement(transformation(origin = {-72.0, -4.77231478230778}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
      rotation = -90.0)));
  Modelica.Mechanics.Translational.Components.MassWithStopAndFriction massWithStopAndFriction(m = 0.01, F_prop = 10, F_Coulomb = 0, F_Stribeck = 0, smin = 0, smax = 0.002, s(start = 0.002)) 
    annotation (Placement(transformation(origin = {-39.99999999999994, -38.0}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
      rotation = -90.0)));
  TYPneumaticComponents.Pistons.Piston piston1(ds = 0.03, redeclare model GasMedium = TYGasMedia.MediaProperties.Semi_Perfect.Semi_Perfect, redeclare model GasType = TYGasMedia.MediaTypes.CH4_methane, reverse = false, InterfaceSwitch = true) 
    annotation (Placement(transformation(origin = {-39.99999999999994, -66.0}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
      rotation = -90.0)));
  TYPneumatics.Sources.Surroundings surroundingsV3(redeclare model GasMedium = TYGasMedia.MediaProperties.Semi_Perfect.Semi_Perfect, redeclare model GasType = TYGasMedia.MediaTypes.CH4_methane) 
    annotation (Placement(transformation(origin = {-72.0, -60.699999999999996}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
      rotation = -90.0)));
  TYPneumaticComponents.Pistons.FixedBodyPiston fixedBodyPiston1(reverse = true, ds = 0.03, dr = 0, redeclare model GasType = TYGasMedia.MediaTypes.CH4_methane) 
    annotation (Placement(transformation(origin = {-39.99999999999994, -94.0}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
      rotation = 90.0)));
  TYPneumaticComponents.Auxiliaries.GasVolumeV gasVolumeV4(T(start = 293), V0(displayUnit = "l") = 1e-5, kth = 500, redeclare model GasType = TYGasMedia.MediaTypes.CH4_methane) 
    annotation (Placement(transformation(origin = {-6.0, -99.23076154806492}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
      rotation = 90.0)));
  TYPneumaticComponents.FlowControlValves.CqOrifice cqOrifice(A(displayUnit = "cm2") = 1e-06 * (Modelica.Constants.pi / 4 * 1.0 ^ 2), redeclare model GasType = TYGasMedia.MediaTypes.CH4_methane) 
    annotation (Placement(transformation(origin = {9.999999999999972, -35.06152309612984}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
      rotation = 90.0)));
  TYPneumaticComponents.Auxiliaries.GasVolumeV gasVolumeV5(T(start = 293), V0(displayUnit = "l") = 5e-5, redeclare model GasType = TYGasMedia.MediaTypes.CH4_methane, n_ports = 1) 
    annotation (Placement(transformation(origin = {-1.9999999999999432, 19.969238451935066}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
      rotation = 90.0)));
  Modelica.Blocks.Sources.TimeTable timeTable2(table = {{0.0, 0.0}, {1, 1}, {3, 1}}) 
    annotation (Placement(transformation(origin = {10.0, 75.0}, 
      extent = {{10.0, -10.0}, {-10.0, 10.0}})));
  TYPneumatics.Valves.FlowControlValves.VarThrottleValve varThrottleValve1(Amax = 2.5e-5, redeclare model GasType = TYGasMedia.MediaTypes.CH4_methane) 
    annotation (Placement(transformation(origin = {50.0, 19.96923845193506}, 
      extent = {{10.0, 10.0}, {-10.0, -10.0}}, 
      rotation = -180.0)));
  TYPneumatics.Sources.Surroundings surroundings1(redeclare model GasType = TYGasMedia.MediaTypes.CH4_methane) 
    annotation (Placement(transformation(origin = {79.99999999999999, 19.96923845193508}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
      rotation = 90.0)));
  Modelica.Blocks.Sources.TimeTable timeTable3(table = {{0.0, 0.0}, {1, 0}, {2, 1}, {3, 1}}) 
    annotation (Placement(transformation(origin = {28.0, -4.77231478230778}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
equation
  connect(pressureSource1.port_B, varThrottleValve.port_A) 
    annotation (Line(origin = {-20.00000000000003, 87.0}, 
      points = {{2.842170943040401e-14, 5.000000000000014}, {2.842170943040401e-14, -5.0}}, 
      color = {90, 229, 225}));
  connect(varThrottleValve.port_B, gasVolumeV3.port_A) 
    annotation (Line(origin = {-20.00000000000003, 58.0}, 
      points = {{2.842170943040401e-14, 4.0}, {3.552713678800501e-14, -3.9930586766541936}}, 
      color = {90, 229, 225}, 
      thickness = 0.5));
  connect(timeTable3.y, varThrottleValve1.u) 
    annotation (Line(origin = {42.99999999999997, 4.999999999999998}, 
      points = {{-3.9999999999999716, -9.772314782307777}, {4.000000000000028, -9.772314782307777}, {4.000000000000028, 9.56923845193506}}, 
      color = {0, 0, 127}));
  connect(springPiston1.flange_a, plainSeatPoppet1.flange_b) 
    annotation (Line(origin = {-40.00000000000003, 5.999999999999998}, 
      points = {{8.526512829121202e-14, -5.910260869565198}, {8.526512829121202e-14, 5.782956521739102}}, 
      color = {0, 127, 0}));
  connect(springPiston1.flange_b, massWithStopAndFriction.flange_a) 
    annotation (Line(origin = {-39.00000000000003, -24.0}, 
      points = {{-0.9999999999999147, 3.782956521739102}, {-0.9999999999999147, -4.0}}, 
      color = {0, 127, 0}));
  connect(fixedBodyPiston1.flange_b, piston1.flange_b) 
    annotation (Line(origin = {-39.00000000000003, -80.0}, 
      points = {{-0.9999999999999147, -3.782956521739095}, {-0.9999999999999147, 3.782956521739095}}, 
      color = {0, 127, 0}));
  connect(piston1.flange_a, massWithStopAndFriction.flange_b) 
    annotation (Line(origin = {-39.00000000000003, -51.999999999999986}, 
      points = {{-0.9999999999999147, -3.9102608695652137}, {-0.9999999999999147, 3.999999999999986}}, 
      color = {0, 127, 0}));
  connect(varThrottleValve.u, timeTable2.y) 
    annotation (Line(origin = {-8.0, 75.0}, 
      points = {{-6.6, 0.0}, {7.0, 0.0}}, 
      color = {0, 0, 127}));
  connect(plainSeatPoppet1.portV_A, gasVolumeV3.portV_B[1]) 
  annotation(Line(origin={-25,35}, 
  points={{-4.999999999999943,-6},{4.997203495630469,-6},{4.997203495630469,5.037802746566776}}, 
  color={28,193,208}));
  connect(plainSeatPoppet1.portV_B, gasVolumeV5.portV_B[1]) 
  annotation(Line(origin={-19,20}, 
  points={{-10.999999999999943,0},{10.053183520599303,0},{10.053183520599303,-1.4210854715202004e-14}}, 
  color={28,193,208}));
  connect(gasVolumeV5.port_A, varThrottleValve1.port_A) 
  annotation(Line(origin={23,20}, 
  points={{-17.977677902621664,-0.002796504369555919},{17,-0.002796504369555919},{17,-0.030761548064941024}}, 
  color={28,193,208}));
  connect(cqOrifice.port_B, varThrottleValve1.port_A) 
  annotation(Line(origin={25,-3}, 
  points={{-15.000000000000028,-22.06152309612984},{-15.000000000000028,22.96923845193506},{15,22.96923845193506}}, 
  color={28,193,208}));
  connect(varThrottleValve1.port_B, surroundings1.port_A) 
  annotation(Line(origin={68,20}, 
  points={{-8,-0.030761548064941024},{6.999999999999986,-0.030761548064941024},{6.999999999999986,0.06923845193508171}}, 
  color={28,193,208}));
  connect(cqOrifice.port_A, gasVolumeV4.port_A) 
  annotation(Line(origin={6,-72}, 
  points={{3.9999999999999716,26.93847690387016},{3.9999999999999716,-27.202796504369545},{-4.977677902621722,-27.202796504369545}}, 
  color={28,193,208}));
  connect(fixedBodyPiston1.portV_A, gasVolumeV4.portV_B[1]) 
  annotation(Line(origin={-21,-99}, 
  points={{-8.999999999999943,-0.20000000000000284},{8.053183520599246,-0.20000000000000284}}, 
  color={28,193,208}));
  connect(surroundingsV3.port_A, piston1.port_A) 
  annotation(Line(origin={-58,-61}, 
  points={{-9,0.20000000000000284},{8.000000000000057,0.20000000000000284}}, 
  color={28,193,208}));
  connect(surroundingsV2.port_A, springPiston1.port_A) 
  annotation(Line(origin={-58,-5}, 
  points={{-9,0.1276852176922203},{8.000000000000057,0.1276852176922203},{8.000000000000057,0.20000000000000018}}, 
  color={28,193,208}));
end PressureRegulation;