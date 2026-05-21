model FlowLimiter "流量限制器系统"
  annotation (Icon(coordinateSystem(extent = {{-100.0, -100.0}, {100.0, 100.0}}, 
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
    experiment(Algorithm = Dassl, Interval = 0.001, StartTime = 0, StopTime = 1.5, Tolerance = 1e-07), 
    Diagram(coordinateSystem(extent={{-100,-100},{100,100}}, 
grid={2,2})), 
    Documentation(link = "modelica://TYHydraulicComponents/Resources/HTML/FlowLimiter.html"),Protection(access=Access.nonPackageDuplicate),__MWORKS(ResultViewerManager(resultViewers={
ResultViewer(name="仿真结果", executeTrigger=executeTrigger.SimulationFinished, commands={
CreatePlot(id=4, x_display_unit="s", legend_layout=7, left_title_type=2, left_title="开度", bottom_title_type=2, bottom_title="时间/s", right_title_type=2, fix_time_range_value=0, zoom_x=(0, 1.5), zoom_y_l=(-0.2, 1.2)), 
Plot(y=["varSymThrottleValve.u"], colors=["4278190335"]), 
CreatePlot(id=5, x="signal.y", legend_layout=7, left_title_type=2, left_title="流量(l/min)", bottom_title_type=2, bottom_title="控制信号", right_title_type=2, fix_time_range_value=0, zoom_x=(0, 1), zoom_y_l=(-0.5, 2.5)), 
Plot(y=["varSymThrottleValve.port_A.q"], colors=["4278190335"]), 
CreatePlot(id=-1, x="signal.y", legend_layout=7, left_title_type=2, left_title="位移/mm", bottom_title_type=2, bottom_title="控制信号", right_title_type=2, fix_time_range_value=0, sub_plot=(1, 2), zoom_x=(0, 1), zoom_y_l=(-0.5, 3.5)), 
Plot(y=["massWithStopAndFriction.s"], colors=["4278190335"]), 
CreatePlot(id=-1, x="signal.y", legend_layout=7, left_title_type=2, left_title="面积/cm2", bottom_title_type=2, bottom_title="控制信号", right_title_type=2, fix_time_range_value=0, sub_plot=(2, 2), zoom_x=(0, 1), zoom_y_l=(-0.02, 0.08)), 
Plot(y=["sharpEdgeSeatPoppet.area"], colors=["4278190335"]), 
CreatePlot(id=-1, x="signal.y", legend_layout=7, left_title_type=2, left_title="压降/Pa", bottom_title_type=2, bottom_title="控制信号", right_title_type=2, fix_time_range_value=0, sub_plot=(2, 1), zoom_x=(0, 1), zoom_y_l=(-2e+06, 1.2e+07)), 
Plot(y=["add.y"], colors=["4278190335"]), 
CreatePlot(id=6, x="add.y", legend_layout=7, left_title_type=2, left_title="阀芯位移/mm", bottom_title_type=2, bottom_title="锥阀压降/Pa", right_title_type=2, fix_time_range_value=0, zoom_x=(0, 1e+07), zoom_y_l=(-0.5, 3.5)), 
Plot(y=["sharpEdgeSeatPoppet.xlap"], colors=["4294901760"])})
})));
  TYHydraulicComponents.Pistons.FixedBodyPiston fixedBodyPiston(ds = 0.006, dr = 0, len0 = 0.005, 
    reverse = true, redeclare model Medium = TYOilMedia.HydraulicOil.Partial.Advanced) annotation (Placement(transformation(origin = {41.0, 50.0}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
      rotation = -90.0)));
  TYHydraulicComponents.Pistons.SpringPiston springPiston(ds = 0.006, dr = 0.004, f_0 = 23, s_0 = 0, 
    reverse = false, redeclare model Medium = TYOilMedia.HydraulicOil.Partial.Advanced) annotation (Placement(transformation(origin = {41.99999999999999, -14.0}, 
      extent = {{10.0, -10.0}, {-10.0, 10.0}}, 
      rotation = -90.0)));
  TYHydraulicComponents.ConicalValveSpool.SharpEdgeSeatPoppet sharpEdgeSeatPoppet(dpop = 0.004, ds = 0.003, dr = 0, alpha = 0.523598775598299, 
    reverse = false, redeclare model Medium = TYOilMedia.HydraulicOil.Partial.Advanced) annotation (Placement(transformation(origin = {41.99999999999999, -50.0}, 
      extent = {{10.0, -10.0}, {-10.0, 10.0}}, 
      rotation = -90.0)));
  Modelica.Mechanics.Translational.Components.MassWithStopAndFriction massWithStopAndFriction(s(start = 0.003), m = 0.01, F_prop = 500, F_Coulomb = 0, F_Stribeck = 0, fexp = 0, smax = 0.003, smin = 0,L=0) 
    annotation (Placement(transformation(origin = {41.0, 18.0}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
      rotation = -90.0)));
  TYHydraulicComponents.Auxiliaries.VolumeV volumeV(p(start = 1e7), V0 = 5e-5, 
    redeclare model Medium = TYOilMedia.HydraulicOil.Partial.Advanced) 
    annotation (Placement(transformation(origin = {9.000000000000004, 55.0}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
      rotation = -90.0)));
  TYHydraulicComponents.Auxiliaries.VolumeV volumeV1(n_ports = 2, V0 = 5e-7, p(start = 1e7), 
    redeclare model Medium = TYOilMedia.HydraulicOil.Partial.Advanced) 
    annotation (Placement(transformation(origin = {16.999999999999996, -19.000000000000007}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
      rotation = -90.0)));
  TYHydraulicComponents.Sources.PressureSource pressureSource(constantPressure = 1e7, 
    redeclare model Medium = TYOilMedia.HydraulicOil.Partial.Advanced) 
    annotation (Placement(transformation(origin={-81,55}, 
extent={{-10,-10},{10,10}})));
  TYHydraulicComponents.Auxiliaries.VolumeV volumeV2(p(start = 1e7), 
    redeclare model Medium = TYOilMedia.HydraulicOil.Partial.Advanced) 
    annotation (Placement(transformation(origin = {16.999999999999996, -57.00000000000002}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
      rotation = -90.0)));
  TYHydraulicComponents.Sources.Tank tank(redeclare model Medium = TYOilMedia.HydraulicOil.Partial.Advanced) annotation (Placement(transformation(origin={-23.939,-86.8747}, 
extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Sources.TimeTable signal(table = {{0.0, 0.0}, {0.5, 0}, {1, 1}, {1.5, 1}}) 
    annotation (Placement(transformation(origin={-52.939,-62.8747}, 
extent={{-10,-10},{10,10}})));
  TYHydraulics.Valves.FlowValves.VarSymThrottleValve varSymThrottleValve(Method = "Q/dp", 
    qchar = 1.66666666666667e-6, redeclare model Medium = TYOilMedia.HydraulicOil.Partial.Advanced) annotation (Placement(transformation(origin={-23.9691,-66}, 
extent={{-10,-10},{10,10}}, 
rotation=-90)));
  TYHydraulicComponents.Auxiliaries.SymOrifice symOrifice(diam = 0.001, 
    redeclare model Medium = TYOilMedia.HydraulicOil.Partial.Advanced) annotation (Placement(transformation(origin = {2.0, 18.0}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
      rotation = -90.0)));
  TYHydraulics.Valves.FlowValves.SymThrottleValve symThrottleValve(Method = "Q/dp", 
    redeclare model Medium = TYOilMedia.HydraulicOil.Partial.Advanced) annotation (Placement(transformation(origin={-48,55}, 
extent={{-10,-10},{10,10}})));
  TYHydraulicComponents.Sensors.PressureSensor pressureSensor(InterfaceSwitch=true) 
    annotation (Placement(transformation(origin={-24,20}, 
extent={{-10,-10},{10,10}}, 
rotation=-90)));
  TYHydraulicComponents.Sensors.PressureSensor pressureSensor1(InterfaceSwitch=true) 
    annotation (Placement(transformation(origin={-24,-23}, 
extent={{-10,10},{10,-10}}, 
rotation=90)));
  Modelica.Blocks.Math.Add add(k2=-1) 
    annotation (Placement(transformation(origin={-52.939,-3.93735}, 
extent={{10,-10},{-10,10}})));
  equation
  connect(massWithStopAndFriction.flange_a, fixedBodyPiston.flange_b) 
    annotation (Line(origin = {41.999999999999986, 34.0}, 
      points = {{-1.0, -6.0}, {-1.0, 6.0}}, 
      color = {0, 127, 0}));
  connect(springPiston.flange_b, massWithStopAndFriction.flange_b) 
    annotation (Line(origin = {41.999999999999986, -10.0}, 
      points = {{0.0, 6.0}, {0.0, 18.0}, {-1.0, 18.0}}, 
      color = {0, 127, 0}));
  connect(sharpEdgeSeatPoppet.flange_b, springPiston.flange_a) 
    annotation (Line(origin = {41.999999999999986, -32.0}, 
      points = {{0.0, -8.0}, {0.0, 8.0}}, 
      color = {0, 127, 0}));
  connect(volumeV.portV_B[1], fixedBodyPiston.portV_A) 
    annotation (Line(origin = {23.999999999999993, 55.0}, 
      points = {{-8.0, 0.0}, {7.0, 0.0}}, 
      color = {0, 127, 255}));
  connect(volumeV1.portV_B[1], springPiston.portV_A) 
    annotation (Line(origin = {27.999999999999993, -19.0}, 
      points = {{-4.0, 0.0}, {4.0, 0.0}}, 
      color = {0, 127, 255}));
  connect(sharpEdgeSeatPoppet.portV_B, volumeV1.portV_B[2]) 
    annotation (Line(origin = {27.999999999999993, -33.0}, 
      points = {{4.0, -15.0}, {-4.0, -15.0}, {-4.0, 14.0}}, 
      color = {0, 127, 255}));
  connect(volumeV2.portV_B[1], sharpEdgeSeatPoppet.portV_A) 
    annotation (Line(origin = {27.999999999999993, -57.0}, 
      points = {{-4.0, 0.0}, {4.0, 0.0}}, 
      color = {0, 127, 255}));
  connect(tank.port_A, varSymThrottleValve.port_B) 
    annotation (Line(origin={-23.939,-81.8747}, 
points={{-0.0301075,-4.94409},{-0.0301075,5.8747},{-0.0301,5.8747}}, 
color={0,127,255}));
  connect(varSymThrottleValve.port_A, volumeV2.port_A) 
    annotation (Line(origin={1,-57}, 
points={{-24.9691,1},{9,1},{9,-2.13163e-14}}, 
color={0,127,255}));
  connect(signal.y, varSymThrottleValve.u) 
    annotation (Line(origin={-20,-64}, 
points={{-21.939,1.1253},{-9.60643,1.1253},{-9.60643,1.12533}}, 
color={0,0,127}));
  connect(symOrifice.port_A, volumeV.port_A) 
    annotation (Line(origin = {2.0, 42.0}, 
      points = {{0.0, -14.0}, {0.0, 13.0}}, 
      color = {0, 127, 255}));
  connect(symOrifice.port_B, volumeV1.port_A) 
    annotation (Line(origin = {6.0, -5.0}, 
      points = {{-4.0, 13.0}, {-4.0, -14.0}, {4.0, -14.0}}, 
      color = {0, 127, 255}));
  connect(pressureSource.port_B, symThrottleValve.port_A) 
    annotation (Line(origin={-65,55}, 
points={{-9,0},{7,0}}, 
color={0,127,255}));
  connect(volumeV.port_A, symThrottleValve.port_B) 
    annotation (Line(origin={-6,55}, 
points={{8,0},{-32,0}}, 
color={0,127,255}));
  connect(pressureSensor.port_A, symThrottleValve.port_B) 
  annotation(Line(origin={-31,41}, 
  points={{7,-14},{7,14},{-7,14}}, 
  color={0,127,255}));
  connect(pressureSensor1.port_A, varSymThrottleValve.port_A) 
  annotation(Line(origin={-24,-43}, 
  points={{0,13},{0,-13},{0.0309,-13}}, 
  color={0,127,255}));
  connect(add.u1, pressureSensor.pMeasured) 
  annotation(Line(origin={-38,8}, 
points={{-2.939,-5.93735},{14.0309,-5.93735},{14.0309,5.01105}}, 
color={0,0,127}));
  connect(add.u2, pressureSensor1.pMeasured) 
  annotation(Line(origin={-38,-13}, 
points={{-2.939,3.06265},{14.0309,3.06265},{14.0309,-3.01105}}, 
color={0,0,127}));
end FlowLimiter;