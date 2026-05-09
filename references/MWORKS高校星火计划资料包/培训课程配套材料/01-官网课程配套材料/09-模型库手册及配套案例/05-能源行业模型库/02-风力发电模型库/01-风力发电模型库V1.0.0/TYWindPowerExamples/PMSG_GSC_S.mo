model PMSG_GSC_S "直驱发电机并网系统-转速控制"
  annotation(Documentation(link = "modelica://TYWindPower/Resources/HTML/PMSG_GSC_S.html"), Icon(coordinateSystem(extent = {{-100, -100}, {100, 100}}, 
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
    grid = {2, 2}), graphics = {Rectangle(origin = {39, 58}, 
    lineColor = {0, 0, 0}, 
    fillColor = {255, 255, 255}, 
    pattern = LinePattern.Dash, 
    extent = {{-83, 42}, {83, -42}}), Text(origin = {45.2932, 109.045}, 
    lineColor = {0, 0, 128}, 
    extent = {{-27.2932, 7.04456}, {27.2931, -7.04456}}, 
    textString = "背靠背换流器", 
    textStyle = {TextStyle.Italic}, 
    textColor = {0, 0, 128}), Rectangle(origin = {127.414, -43}, 
    lineColor = {0, 0, 0}, 
    fillColor = {255, 255, 255}, 
    pattern = LinePattern.Dash, 
    extent = {{-55, 22}, {55, -22}}), Text(origin = {127.414, -75.3845}, 
    lineColor = {0, 0, 128}, 
    extent = {{-36.5863, 7.04456}, {36.5863, -7.04456}}, 
    textString = "网侧换流器控制器", 
    textStyle = {TextStyle.Italic}, 
    textColor = {0, 0, 128}), Text(origin = {-39.9137, -75.3845}, 
    lineColor = {0, 0, 128}, 
    extent = {{-36.5863, 7.04456}, {36.5863, -7.04456}}, 
    textString = "机侧换流器控制器", 
    textStyle = {TextStyle.Italic}, 
    textColor = {0, 0, 128}), Rectangle(origin = {-153.1637, -46.0041}, 
    fillColor = {255, 255, 255}, 
    pattern = LinePattern.Dash, 
    extent = {{-55, 22}, {55, -22}}), Text(origin = {-168.70685, -75.3845}, 
    lineColor = {0, 0, 128}, 
    extent = {{-27.2931, 7.04456}, {27.2931, -7.04456}}, 
    textString = "风力机控制器", 
    textStyle = {TextStyle.Italic}, 
    textColor = {0, 0, 128}), Rectangle(origin = {4.75, 65}, 
    fillColor = {255, 255, 255}, 
    pattern = LinePattern.Dash, 
    lineThickness = 0.4, 
    extent = {{-227.25, 53}, {227.25, -53}}), Text(origin = {224.000085, 61}, 
    rotation = -90, 
    lineColor = {0, 0, 128}, 
    extent = {{-39, -6.00009}, {39, 6.00009}}, 
    textString = "风电系统", 
    textStyle = {TextStyle.None}, 
    textColor = {0, 0, 128}), Rectangle(origin = {4.75, -46.0041}, 
    fillColor = {255, 255, 255}, 
    pattern = LinePattern.Dash, 
    lineThickness = 0.4, 
    extent = {{-227.25, 50.0041}, {227.25, -50.0041}}), Text(origin = {224.00015, -43}, 
    rotation = -90, 
    lineColor = {0, 0, 128}, 
    extent = {{47, -6.00015}, {-47, 6.00015}}, 
    textString = "控制系统", 
    textStyle = {TextStyle.None}, 
    textColor = {0, 0, 128}), Rectangle(origin = {-60, -46.0041}, 
    fillColor = {255, 255, 255}, 
    pattern = LinePattern.Dash, 
    extent = {{-32, 22}, {32, -22}})}), experiment(Algorithm = ImplicitEuler, InlineIntegrator = false, InlineStepSize = false, StartTime = 0, StopTime = 1200, Tolerance = 0.0001, IntegratorStep = 0.024, Interval = 0.024), __MWORKS(ContinueSimConfig(SaveContinueFile = "false", SaveBeforeStop = "false", NumberBeforeStop = 1, FixedContinueInterval = "false", ContinueIntervalLength = 1200, ContinueTimeVector),ResultViewerManager(resultViewers={
ResultViewer(name="1", executeTrigger=executeTrigger.SimulationFinished, commands={
CreatePlot(id=1, x_display_unit="s", legend_layout=1, left_title="[MW]", fix_time_range_value=0, zoom_x=(0, 1200), zoom_y_l=(0, 3)), 
Plot(y=["blade.P_m", "blade.Pm_nom"], colors=["4278190335", "4294901760"]), 
CreatePlot(id=-1, x_display_unit="s", legend_layout=1, left_title="[1]", fix_time_range_value=0, sub_plot=(1, 2), zoom_x=(0, 1200), zoom_y_l=(0.1, 0.5)), 
Plot(y=["blade.blade.Cp", "blade.Cp_max"], colors=["4278190335", "4294901760"]), 
CreatePlot(id=-1, x_display_unit="s", legend_layout=1, left_title="[W]", fix_time_range_value=0, sub_plot=(2, 2), zoom_x=(0, 1200), zoom_y_l=(-5e+06, 2e+06)), 
Plot(y=["vOC_Q.power_Cal_abc.P"], colors=["4278190335"]), 
CreatePlot(id=-1, x_display_unit="s", legend_layout=1, left_title="[var]", fix_time_range_value=0, sub_plot=(2, 1), zoom_x=(0, 1200), zoom_y_l=(-200000, 200000)), 
Plot(y=["vOC_Q.power_Cal_abc.Q", "vOC_Q.Qg_ref"], colors=["4278190335", "4294901760"]), 
CreatePlot(id=-1, x_display_unit="s", legend_layout=1, left_title="[rad]", fix_time_range_value=0, sub_plot=(3, 2), zoom_x=(0, 1200), zoom_y_l=(-0.05, 0.3)), 
Plot(y=["blade.pitchAngle"], colors=["4278190335"]), 
CreatePlot(id=-1, x_display_unit="s", legend_layout=1, left_title="[V]", fix_time_range_value=0, sub_plot=(3, 1), zoom_x=(0, 1200), zoom_y_l=(5370, 5430)), 
Plot(y=["vOC_Q.Udc", "vOC_Q.Udc_ref"], colors=["4278190335", "4294901760"])})
})),Protection(access=Access.nonPackageDuplicate));
  TYWindPower.Generators.PMSG linearPSM 
    annotation(Placement(transformation(origin = {-104, 39.95}, 
    extent = {{-10, -10}, {10, 10}})));
  TYWindPower.Mechanics.Blade blade(w_start = windSource.initWindSpeed * blade.lambda_optimal / blade.R_t, H0 = 100, w_t_output = true, UserDefined = true, Cp_max = 0.441) 
    annotation(Placement(transformation(origin = {-148, 39.95}, 
    extent = {{-10, -10}, {10, 10}})));
  TYWindPower.PowerConverters.Averaged.AverageUniversalBridge averageUniversalBridge_m(eta = 1) 
    annotation(Placement(transformation(origin = {-16, 62}, 
    extent = {{10, -10}, {-10, 10}})));
  TYWindPower.Controllers.PMSG.VoltageModulation voltageModulation_m(Use_v_line_max = true) 
    annotation(Placement(transformation(origin = {-40, -40}, 
    extent = {{-10, -10}, {10, 10}})));
  Modelica.Electrical.Analog.Basic.Capacitor capacitor(v(start = 5.4e3), C = 2.4e-3) 
    annotation(Placement(transformation(origin = {48, 58}, 
    extent = {{-10, -10}, {10, 10}}, 
    rotation = -90)));
  Modelica.Electrical.Analog.Sensors.VoltageSensor voltageSensor 
    annotation(Placement(transformation(origin = {28, 58}, 
    extent = {{-10, -10}, {10, 10}}, 
    rotation = -90)));
  TYWindPower.PowerConverters.Averaged.AverageUniversalBridge averageUniversalBridge_g(eta = 1) 
    annotation(Placement(transformation(origin = {88, 62}, 
    extent = {{-10, -10}, {10, 10}})));
  TYWindPower.PowerTransmissions.PowerGrid powerGrid 
    annotation(Placement(transformation(origin = {160, 62}, 
    extent = {{10, -10}, {-10, 10}})));
  TYWindPower.Controllers.PMSG.VoltageModulation voltageModulation_g(Use_v_line_max = true) 
    annotation(Placement(transformation(origin = {88, -40}, 
    extent = {{10, -10}, {-10, 10}})));
  TYWindPower.Controllers.PMSG.GridSideController vOC_Q(f_grid = 50, k_Q = 10, T_Q = 0.15, k_d = 30, T_d = 0.24, k_q = 30, T_q = 0.24, k_v = 1.44, T_v = 18.9e-3, k_PLL = 20, T_PLL = 0.2e-3, Lc = 0) 
    annotation(Placement(transformation(origin = {162, -40}, 
    extent = {{10, -10}, {-10, 10}})));
  Modelica.Blocks.Sources.Constant const1(k = 5.4e3) 
    annotation(Placement(transformation(origin = {203, -22.05}, 
    extent = {{10, -10}, {-10, 10}})));
  Modelica.Blocks.Sources.TimeTable timeTable(table = [0, 0; 500, 0; 501, 150000; 600, 150000; 601, 0; 700, 0; 701, -150000; 800, -150000; 801, 0; 900, 0.0]) 
    annotation(Placement(transformation(origin = {205, -54}, 
    extent = {{10, -10}, {-10, 10}})));
  TYWindPower.Controllers.WindTurbines.MPPT mPPT(redeclare model MPPT = TYWindPower.Controllers.WindTurbines.Basics.MPPT_TSR, UserDefined = true, Cp_max = 0.441) 
    annotation(Placement(transformation(origin = {-110.33185, -40}, 
    extent = {{-10, -10}, {10, 10}})));
  TYWindPower.Controllers.PMSG.MachineSideController speedController(T_w = 5, ControllerType = "转速控制器") 
    annotation(Placement(transformation(origin = {-79, -40}, 
    extent = {{-10, -10}, {10, 10}})));
  TYWindPower.Controllers.WindTurbines.PitchController pitchController(UserDefined = true, Cp_max = 0.441, Ti = 1) 
    annotation(Placement(transformation(origin = {-182, -40}, 
    extent = {{10, -10}, {-10, 10}})));
  TYWindPower.Environment.WindSource windSource(DataType = "组合风速模型计算", v_basic = 3, v_gmax = 0, v_rmax = 12, tr1 = 0, tr2 = 300) 
    annotation(Placement(transformation(origin = {-198.1637, 44.45}, 
    extent = {{-10, -10}, {10, 10}})));
equation
  connect(capacitor.p, averageUniversalBridge_m.pin_p) 
    annotation(Line(origin = {21, 55}, 
    points = {{27, 13}, {27, 39}, {-17, 39}, {-17, 15}, {-27, 15}}, 
    color = {0, 0, 255}));
  connect(averageUniversalBridge_m.plug, linearPSM.plug_p) 
    annotation(Line(origin = {-40, 50}, 
    points = {{14, 12}, {-64, 12}, {-64, -0.05}}, 
    color = {0, 0, 255}));
  connect(linearPSM.flange, blade.flange) 
    annotation(Line(origin = {-95, 39.95}, 
    points = {{-19, 0}, {-43.1, 0}}, 
    color = {0, 0, 0}));
  connect(averageUniversalBridge_m.pin_p, voltageSensor.p) 
    annotation(Line(origin = {13, 53}, 
    points = {{-19, 17}, {-9, 17}, {-9, 41}, {15, 41}, {15, 15}}, 
    color = {0, 0, 255}));
  connect(voltageSensor.n, averageUniversalBridge_m.pin_n) 
    annotation(Line(origin = {13, 35}, 
    points = {{15, 13}, {15, -13}, {-9, -13}, {-9, 19}, {-19, 19}}, 
    color = {0, 0, 255}));
  connect(capacitor.n, averageUniversalBridge_m.pin_n) 
    annotation(Line(origin = {21, 25.9}, 
    points = {{27, 22.1}, {27, -3.9}, {-17, -3.9}, {-17, 28.1}, {-27, 28.1}}, 
    color = {0, 0, 255}));
  connect(averageUniversalBridge_g.pin_p, capacitor.p) 
    annotation(Line(origin = {60, 55.9}, 
    points = {{18, 14.1}, {6, 14.1}, {6, 38.1}, {-12, 38.1}, {-12, 12.1}}, 
    color = {0, 0, 255}));
  connect(capacitor.n, averageUniversalBridge_g.pin_n) 
    annotation(Line(origin = {60, 26.9}, 
    points = {{-12, 21.1}, {-12, -4.9}, {6, -4.9}, {6, 27.1}, {18, 27.1}}, 
    color = {0, 0, 255}));
  connect(averageUniversalBridge_g.plug, powerGrid.plug_p) 
    annotation(Line(origin = {111, 37.9}, 
    points = {{-13, 24.1}, {38.6, 24.1}}, 
    color = {0, 0, 255}));
  connect(mPPT.w_desire, speedController.w_desired) 
    annotation(Line(origin = {-119, -48.05}, 
    points = {{19.6681, 8.05}, {28, 8.05}}, 
    color = {0, 0, 127}));
  connect(voltageModulation_m.U_line, speedController.U_line) 
    annotation(Line(origin = {-29, -44}, 
    points = {{0, -4}, {35, -4}, {35, -20}, {-62, -20}, {-62, -4}}, 
    color = {0, 0, 127}));
  connect(speedController.Us_abc_ref, voltageModulation_m.Uabc) 
    annotation(Line(origin = {-35, -29}, 
    points = {{-33, -11}, {-17, -11}}, 
    color = {0, 0, 127}));
  connect(voltageSensor.v, voltageModulation_m.Udc) 
    annotation(Line(origin = {-7, 12}, 
    points = {{24, 46}, {24, -72}, {-45, -72}, {-45, -60}}, 
    color = {0, 0, 127}));
  connect(linearPSM.is_abc, speedController.is_abc) 
    annotation(Line(origin = {-91, -0.05}, 
    points = {{-2, 36.9}, {20, 36.9}, {20, -27.95}}, 
    color = {0, 0, 127}));
  connect(linearPSM.theta_r, speedController.theta_r) 
    annotation(Line(origin = {-91, -1.05}, 
    points = {{-2, 35.76875}, {12, 35.76875}, {12, -26.95}}, 
    color = {0, 0, 127}));
  connect(linearPSM.w_r, speedController.w_r) 
    annotation(Line(origin = {-95, -2.05}, 
    points = {{2, 34.6375}, {8, 34.6375}, {8, -25.95}}, 
    color = {0, 0, 127}));
  connect(voltageModulation_m.Uabc_normalized, averageUniversalBridge_m.Uabc_normalized) 
    annotation(Line(origin = {1, 27}, 
    points = {{-30, -67}, {-17, -67}, {-17, 23}}, 
    color = {0, 0, 127}));
  connect(voltageModulation_g.Uabc, vOC_Q.Uc_abc_ref) 
    annotation(Line(origin = {112, -34}, 
    points = {{-12, -6}, {39, -6}}, 
    color = {0, 0, 127}));
  connect(voltageSensor.v, voltageModulation_g.Udc) 
    annotation(Line(origin = {59, 12}, 
    points = {{-42, 46}, {-42, -72}, {41, -72}, {41, -60}}, 
    color = {0, 0, 127}), __MWORKS(BlockSystem(NamedSignal)));
  connect(powerGrid.i_abc, vOC_Q.ig_abc) 
    annotation(Line(origin = {119, 28}, 
    points = {{35, 23}, {35, -56}}, 
    color = {0, 0, 127}));
  connect(powerGrid.Uabc, vOC_Q.Ug_abc) 
    annotation(Line(origin = {125, 28}, 
    points = {{33, 23}, {33, -56}, {37, -56}}, 
    color = {0, 0, 127}));
  connect(voltageModulation_g.Uabc_normalized, averageUniversalBridge_g.Uabc_normalized) 
    annotation(Line(origin = {69, 27}, 
    points = {{8, -67}, {-9, -67}, {-9, -33}, {19, -33}, {19, 23}}, 
    color = {0, 0, 127}));
  connect(voltageSensor.v, vOC_Q.Udc) 
    annotation(Line(origin = {74, 10}, 
    points = {{-57, 48}, {-57, -26}, {96, -26}, {96, -38}}, 
    color = {0, 0, 127}), __MWORKS(BlockSystem(NamedSignal)));
  connect(vOC_Q.Qg_ref, timeTable.y) 
    annotation(Line(origin = {185, -82}, 
    points = {{-11, 36}, {-11, 28}, {9, 28}}, 
    color = {0, 0, 127}));
  connect(const1.y, vOC_Q.Udc_ref) 
    annotation(Line(origin = {185, -59}, 
    points = {{7, 36.95}, {-11, 36.95}, {-11, 25}}, 
    color = {0, 0, 127}));
  connect(blade.w_t, pitchController.w_t) 
    annotation(Line(origin = {-156, 7.95}, 
    points = {{19, 28.45}, {19, -47.95}, {-14, -47.95}}, 
    color = {0, 0, 127}));
  connect(pitchController.pitchAngle, mPPT.pitchAngle) 
    annotation(Line(origin = {-187, -38.05}, 
    points = {{-6, -1.95}, {-13, -1.95}, {-13, -15.95}, {64.66815, -15.95}, {64.66815, -9.95}}, 
    color = {0, 0, 127}));
  connect(pitchController.pitchAngle, blade.pitchAngle) 
    annotation(Line(origin = {-184, 7.95}, 
    points = {{-9, -47.95}, {-16, -47.95}, {-16, 12.05}, {24.5, 12.05}, {24.5, 27.3}}, 
    color = {0, 0, 127}), __MWORKS(BlockSystem(NamedSignal)));
  connect(windSource.windSpeed, blade.windSpeed) 
    annotation(Line(origin = {-166, 53.95}, 
    points = {{-21.1637, -9.5}, {6.5, -9.5}}, 
    color = {0, 0, 127}));
  connect(windSource.windSpeed, mPPT.windSpeed) 
    annotation(Line(origin = {-166, 7.95}, 
    points = {{-21.1637, 36.5}, {-8, 36.5}, {-8, -11.95}, {43.66815, -11.95}, {43.66815, -47.95}}, 
    color = {0, 0, 127}), __MWORKS(BlockSystem(NamedSignal)));
end PMSG_GSC_S;