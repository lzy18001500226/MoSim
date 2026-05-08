model PMSG_MSC_T "直驱发电机机侧控制系统"
  annotation(Documentation(link = "modelica://TYWindPower/Resources/HTML/PMSG_MSC_T.html"), Icon(coordinateSystem(extent = {{-100, -100}, {100, 100}}, 
    grid = {2, 2}), graphics = {Polygon(origin = {-7.10543e-15, 33}, 
    lineColor = {16, 99, 16}, 
    fillColor = {16, 99, 16}, 
    fillPattern = FillPattern.Solid, 
    points = {{-64, 1}, {0, 37}, {64, 1}, {0, -37}}), Line(origin = {0, -12}, 
    points = {{-62, 18}, {0, -18}, {62, 18}}, 
    color = {16, 99, 16}, 
    thickness = 5), Line(origin = {7.10543e-15, -40}, 
    points = {{-62, 18}, {0, -18}, {62, 18}}, 
    color = {16, 99, 16}, 
    thickness = 5)}), Diagram(coordinateSystem(extent = {{-180, -100}, {180, 100}}, 
    grid = {2, 2}), graphics = {Rectangle(origin = {-1, -42.9}, 
    fillColor = {255, 255, 255}, 
    pattern = LinePattern.Dash, 
    extent = {{-43, 28}, {43, -28}}), Text(origin = {-1, -81.85544}, 
    lineColor = {0, 0, 128}, 
    extent = {{-36.5863, 7.04456}, {36.5863, -7.04456}}, 
    textString = "机侧换流器控制器", 
    textStyle = {TextStyle.Italic}, 
    textColor = {0, 0, 128}), Rectangle(origin = {-91, -42.9}, 
    fillColor = {255, 255, 255}, 
    pattern = LinePattern.Dash, 
    extent = {{-43, 28}, {43, -28}}), Text(origin = {-91, -81.85544}, 
    lineColor = {0, 0, 128}, 
    extent = {{-27.2931, 7.04456}, {27.2931, -7.04456}}, 
    textString = "风力机控制器", 
    textStyle = {TextStyle.Italic}, 
    textColor = {0, 0, 128})}), experiment(Algorithm = Dassl, InlineIntegrator = false, InlineStepSize = false, NumberOfIntervals = 50000, StartTime = 0, StopTime = 500, Tolerance = 0.0001), __MWORKS(ContinueSimConfig(SaveContinueFile = "false", SaveBeforeStop = "false", NumberBeforeStop = 1, FixedContinueInterval = "false", ContinueIntervalLength = 500, ContinueTimeVector),ResultViewerManager(resultViewers={
ResultViewer(name="1", executeTrigger=executeTrigger.SimulationFinished, commands={
CreatePlot(id=1, x_display_unit="s", legend_layout=1, left_title="[m/s]", right_title_type=2, fix_time_range_value=0, zoom_x=(0, 500), zoom_y_l=(0, 20)), 
Plot(y=["windSource.windSpeed"], colors=["4278190335"]), 
CreatePlot(id=-1, x_display_unit="s", legend_layout=1, left_title="[rad/s]", fix_time_range_value=0, sub_plot=(1, 2), zoom_x=(0, 500), zoom_y_l=(0.4, 2)), 
Plot(y=["blade.w_t_nom", "blade.blade.w_t"], colors=["4278190335", "4294901760"]), 
CreatePlot(id=-1, x_display_unit="s", legend_layout=1, fix_time_range_value=0, sub_plot=(2, 2), zoom_x=(0, 500), zoom_y_l=(2, 14)), 
Plot(y=["blade.lambda_optimal", "blade.blade.lambda"], colors=["4278190335", "4294901760"]), 
CreatePlot(id=-1, x_display_unit="s", legend_layout=1, left_title="[MW]", fix_time_range_value=0, sub_plot=(2, 1), zoom_x=(0, 500), zoom_y_l=(-0.5, 3)), 
Plot(y=["blade.Pm_nom", "blade.P_m"], colors=["4278190335", "4294901760"]), 
CreatePlot(id=-1, x_display_unit="s", legend_layout=1, left_title="[rad]", fix_time_range_value=0, sub_plot=(3, 2), zoom_x=(0, 500), zoom_y_l=(-0.05, 0.3)), 
Plot(y=["blade.pitchAngle"], colors=["4278190335"]), 
CreatePlot(id=-1, x_display_unit="s", legend_layout=1, left_title="[1]", fix_time_range_value=0, sub_plot=(3, 1), zoom_x=(0, 500), zoom_y_l=(-0.1, 0.5)), 
Plot(y=["blade.Cp_max", "blade.blade.Cp"], colors=["4278190335", "4294901760"])})
})),Protection(access=Access.nonPackageDuplicate));
  TYWindPower.Environment.WindSource windSource(DataType = "组合风速模型计算", v_basic = 3, v_gmax = 0, v_rmax = 12, tr1 = 0, tr2 = 300) 
    annotation(Placement(transformation(origin = {-160, 7.6}, 
    extent = {{-10, -10}, {10, 10}})));
  TYWindPower.Generators.PMSG PSMG(use_Tr = false, use_power_m = false, use_temperatures = false, use_power_el = false) 
    annotation(Placement(transformation(origin = {-62, 3.1}, 
    extent = {{-10, -10}, {10, 10}})));
  TYWindPower.Mechanics.Blade blade(w_start = windSource.initWindSpeed * blade.lambda_optimal / blade.R_t, H0 = 100, Cp_output = false, lambda_output = false, w_t_output = true, UserDefined = true, Cp_max = 0.441) 
    annotation(Placement(transformation(origin = {-96, 3.1}, 
    extent = {{-10, -10}, {10, 10}})));
  TYWindPower.PowerConverters.Averaged.AverageUniversalBridge averageUniversalBridge(eta = 1) 
    annotation(Placement(transformation(origin = {16, 32}, 
    extent = {{10, -10}, {-10, 10}})));
  TYWindPower.Controllers.PMSG.VoltageModulation voltageModulation(Use_v_line_max = false) 
    annotation(Placement(transformation(origin = {16, -38.9}, 
    extent = {{-10, -10}, {10, 10}})));
  Modelica.Electrical.Analog.Basic.Capacitor capacitor(v(start = 5.4e3), C = 2.4e-3) 
    annotation(Placement(transformation(origin = {92, 32}, 
    extent = {{-10, -10}, {10, 10}}, 
    rotation = -90)));
  Modelica.Electrical.Analog.Basic.Ground ground 
    annotation(Placement(transformation(origin = {120, -22.9}, 
    extent = {{-10, -10}, {10, 10}})));
  Modelica.Electrical.Analog.Sources.ConstantVoltage constantVoltage(V = 5.4e3) 
    annotation(Placement(transformation(origin = {120, 32}, 
    extent = {{-10, -10}, {10, 10}}, 
    rotation = -90)));
  Modelica.Electrical.Analog.Sensors.VoltageSensor voltageSensor 
    annotation(Placement(transformation(origin = {158, 32}, 
    extent = {{-10, -10}, {10, 10}}, 
    rotation = -90)));
  TYWindPower.Controllers.PMSG.MachineSideController machineSideController(k_d = 3.75, T_d = 0.24, k_q = 3.75, T_q = 0.24) 
    annotation(Placement(transformation(origin = {-30, -38.9}, 
    extent = {{-10, -10}, {10, 10}})));
  TYWindPower.Controllers.WindTurbines.MPPT MPPT(redeclare model MPPT = TYWindPower.Controllers.WindTurbines.Basics.MPPT_OT, UserDefined = true, Cp_max = 0.441) 
    annotation(Placement(transformation(origin = {-62, -38.9}, 
    extent = {{-10, -10}, {10, 10}})));
  TYWindPower.Controllers.WindTurbines.PitchController pitchController(UserDefined = true, Cp_max = 0.441) 
    annotation(Placement(transformation(origin = {-116, -38.9}, 
    extent = {{10, -10}, {-10, 10}})));
equation
  connect(ground.p, constantVoltage.n) 
    annotation(Line(origin = {152, 11}, 
    points = {{-32, -23.9}, {-32, 11}}, 
    color = {0, 0, 255}));
  connect(constantVoltage.p, averageUniversalBridge.pin_p) 
    annotation(Line(origin = {55, 20.1}, 
    points = {{65, 21.9}, {65, 51}, {7, 51}, {7, 19.9}, {-29, 19.9}}, 
    color = {0, 0, 255}));
  connect(averageUniversalBridge.pin_n, ground.p) 
    annotation(Line(origin = {91, -15.2}, 
    points = {{-65, 39.2}, {-27, 39.2}, {-27, 8.3}, {29, 8.3}, {29, 2.3}}, 
    color = {0, 0, 255}));
  connect(capacitor.n, ground.p) 
    annotation(Line(origin = {132, 8.7}, 
    points = {{-40, 13.3}, {-40, -5.6}, {-12, -5.6}, {-12, -21.6}}, 
    color = {0, 0, 255}));
  connect(capacitor.p, averageUniversalBridge.pin_p) 
    annotation(Line(origin = {37, 20.1}, 
    points = {{55, 21.9}, {55, 51}, {25, 51}, {25, 19.9}, {-11, 19.9}}, 
    color = {0, 0, 255}));
  connect(averageUniversalBridge.plug, PSMG.plug_p) 
    annotation(Line(origin = {-24, 15.1}, 
    points = {{30, 16.9}, {-38, 16.9}, {-38, -2}}, 
    color = {0, 0, 255}));
  connect(PSMG.flange, blade.flange) 
    annotation(Line(origin = {-71, 3.1}, 
    points = {{-1, 0}, {-15.1, 0}}, 
    color = {0, 0, 0}));
  connect(windSource.windSpeed, blade.windSpeed) 
    annotation(Line(origin = {-122, 5.1}, 
    points = {{-27, 2.5}, {14.5, 2.5}}, 
    color = {0, 0, 127}));
  connect(averageUniversalBridge.pin_p, voltageSensor.p) 
    annotation(Line(origin = {29, 18.1}, 
    points = {{-3, 21.9}, {33, 21.9}, {33, 53}, {129, 53}, {129, 23.9}}, 
    color = {0, 0, 255}));
  connect(voltageSensor.n, averageUniversalBridge.pin_n) 
    annotation(Line(origin = {65, -4.2}, 
    points = {{93, 26.2}, {93, -2.7}, {-1, -2.7}, {-1, 28.2}, {-39, 28.2}}, 
    color = {0, 0, 255}));
  connect(voltageSensor.v, voltageModulation.Udc) 
    annotation(Line(origin = {7, -10.9}, 
    points = {{140, 42.9}, {140, -48}, {-13, -48}, {-13, -36}, {-3, -36}}, 
    color = {0, 0, 127}));
  connect(PSMG.w_r, machineSideController.w_r) 
    annotation(Line(origin = {-44, -15.9}, 
    points = {{-7, 11.6375}, {6, 11.6375}, {6, -11}}, 
    color = {0, 0, 127}));
  connect(PSMG.theta_r, machineSideController.theta_r) 
    annotation(Line(origin = {-40, -14.9}, 
    points = {{-11, 12.76875}, {10, 12.76875}, {10, -12}}, 
    color = {0, 0, 127}));
  connect(PSMG.is_abc, machineSideController.is_abc) 
    annotation(Line(origin = {-36, -13.9}, 
    points = {{-15, 13.9}, {14, 13.9}, {14, -13}}, 
    color = {0, 0, 127}));
  connect(voltageModulation.Uabc_normalized, averageUniversalBridge.Uabc_normalized) 
    annotation(Line(origin = {9, -3.9}, 
    points = {{18, -35}, {27, -35}, {27, 23.9}, {7, 23.9}}, 
    color = {0, 0, 127}));
  connect(machineSideController.Us_abc_ref, voltageModulation.Uabc) 
    annotation(Line(origin = {-7, -38.9}, 
    points = {{-12, 0}, {11, 0}}, 
    color = {0, 0, 127}));
  connect(pitchController.pitchAngle, blade.pitchAngle) 
    annotation(Line(origin = {-128, -23.9}, 
    points = {{1, -15}, {-12, -15}, {-12, 22.3}, {20.5, 22.3}}, 
    color = {0, 0, 127}));
  connect(pitchController.pitchAngle, MPPT.pitchAngle) 
    annotation(Line(origin = {-107, -55.9}, 
    points = {{-20, 17}, {-33, 17}, {-33, -9}, {33, -9}, {33, 9}}, 
    color = {0, 0, 127}), __MWORKS(BlockSystem(NamedSignal)));
  connect(blade.w_t, pitchController.w_t) 
    annotation(Line(origin = {-93, -23.9}, 
    points = {{8, 23.45}, {13, 23.45}, {13, -15}, {-11, -15}}, 
    color = {0, 0, 127}), __MWORKS(BlockSystem(NamedSignal)));
  connect(MPPT.T_desire, machineSideController.T_desired) 
    annotation(Line(origin = {-46, -38.9}, 
    points = {{-5, 0}, {4, 0}}, 
    color = {0, 0, 127}));
  connect(blade.w_t, MPPT.w_t) 
    annotation(Line(origin = {-79, -19.9}, 
    points = {{-6, 19.45}, {-1, 19.45}, {-1, -19}, {5, -19}}, 
    color = {0, 0, 127}), __MWORKS(BlockSystem(NamedSignal)));
end PMSG_MSC_T;