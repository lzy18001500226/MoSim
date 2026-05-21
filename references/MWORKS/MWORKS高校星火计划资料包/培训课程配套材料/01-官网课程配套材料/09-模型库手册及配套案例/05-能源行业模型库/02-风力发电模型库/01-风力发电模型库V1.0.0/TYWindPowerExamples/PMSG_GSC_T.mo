model PMSG_GSC_T "直驱发电机并网系统-转矩控制"
  annotation(Documentation(link = "modelica://TYWindPower/Resources/HTML/PMSG_GSC_T.html"), Icon(coordinateSystem(extent = {{-100, -100}, {100, 100}}, 
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
    grid = {2, 2}), graphics = {Rectangle(origin = {43, 40}, 
    lineColor = {0, 0, 0}, 
    fillColor = {255, 255, 255}, 
    pattern = LinePattern.Dash, 
    extent = {{-83, 42}, {83, -42}}), Text(origin = {49.2932, 91.0446}, 
    lineColor = {0, 0, 128}, 
    extent = {{-27.2932, 7.04456}, {27.2931, -7.04456}}, 
    textString = "背靠背换流器", 
    textStyle = {TextStyle.Italic}, 
    textColor = {0, 0, 128}), Rectangle(origin = {125, -66}, 
    lineColor = {0, 0, 0}, 
    fillColor = {255, 255, 255}, 
    pattern = LinePattern.Dash, 
    extent = {{-55, 22}, {55, -22}}), Text(origin = {131.414, -93.3845}, 
    lineColor = {0, 0, 128}, 
    extent = {{-36.5863, 7.04456}, {36.5863, -7.04456}}, 
    textString = "网侧换流器控制器", 
    textStyle = {TextStyle.Italic}, 
    textColor = {0, 0, 128}), Text(origin = {-35.9137, -93.3845}, 
    lineColor = {0, 0, 128}, 
    extent = {{-36.5863, 7.04456}, {36.5863, -7.04456}}, 
    textString = "机侧换流器控制器", 
    textStyle = {TextStyle.Italic}, 
    textColor = {0, 0, 128}), Rectangle(origin = {-137, -64}, 
    fillColor = {255, 255, 255}, 
    pattern = LinePattern.Dash, 
    extent = {{-55, 22}, {55, -22}}), Text(origin = {-164.70685, -93.3845}, 
    lineColor = {0, 0, 128}, 
    extent = {{-27.2931, 7.04456}, {27.2931, -7.04456}}, 
    textString = "风力机控制器", 
    textStyle = {TextStyle.Italic}, 
    textColor = {0, 0, 128}), Rectangle(origin = {8.75, 47}, 
    fillColor = {255, 255, 255}, 
    pattern = LinePattern.Dash, 
    lineThickness = 0.4, 
    extent = {{-227.25, 53}, {227.25, -53}}), Text(origin = {228.000085, 43}, 
    rotation = -90, 
    lineColor = {0, 0, 128}, 
    extent = {{-39, -6.00009}, {39, 6.00009}}, 
    textString = "风电系统", 
    textStyle = {TextStyle.None}, 
    textColor = {0, 0, 128}), Rectangle(origin = {8.75, -64.0041}, 
    fillColor = {255, 255, 255}, 
    pattern = LinePattern.Dash, 
    lineThickness = 0.4, 
    extent = {{-227.25, 50.0041}, {227.25, -50.0041}}), Text(origin = {228.00015, -61}, 
    rotation = -90, 
    lineColor = {0, 0, 128}, 
    extent = {{47, -6.00015}, {-47, 6.00015}}, 
    textString = "控制系统", 
    textStyle = {TextStyle.None}, 
    textColor = {0, 0, 128}), Rectangle(origin = {-47.20685, -64.0041}, 
    fillColor = {255, 255, 255}, 
    pattern = LinePattern.Dash, 
    extent = {{-27.2931, 22}, {27.2931, -22}})}), experiment(Algorithm = Dassl, InlineIntegrator = false, InlineStepSize = false, StartTime = 0, StopTime = 1200, Tolerance = 0.0001, NumberOfIntervals = 50000), __MWORKS(ContinueSimConfig(SaveContinueFile = "false", SaveBeforeStop = "false", NumberBeforeStop = 1, FixedContinueInterval = "false", ContinueIntervalLength = 120, ContinueTimeVector),ResultViewerManager(resultViewers={
ResultViewer(name="1", executeTrigger=executeTrigger.SimulationFinished, commands={
CreatePlot(id=1, x_display_unit="s", legend_layout=1, left_title="[MW]", right_title_type=2, right_title="[W]", fix_time_range_value=0, zoom_x=(0, 1200), zoom_y_l=(-0.5, 3)), 
Plot(y=["blade.P_m", "blade.Pm_nom"], colors=["4278190335", "4294901760"]), 
CreatePlot(id=-1, x_display_unit="s", legend_layout=1, left_title="[var]", fix_time_range_value=0, sub_plot=(1, 2), zoom_x=(0, 1200), zoom_y_l=(-200000, 200000)), 
Plot(y=["gridSideController.Qg_ref", "gridSideController.power_Cal_abc.Q"], colors=["4278190335", "4294901760"]), 
CreatePlot(id=-1, x_display_unit="s", legend_layout=1, left_title="[W]", fix_time_range_value=0, sub_plot=(2, 2), zoom_x=(0, 1200), zoom_y_l=(-2.5e+06, 500000)), 
Plot(y=["gridSideController.power_Cal_abc.P"], colors=["4278190335"]), 
CreatePlot(id=-1, x_display_unit="s", legend_layout=1, left_title="[V]", fix_time_range_value=0, sub_plot=(2, 1), zoom_x=(0, 1200), zoom_y_l=(5399.5, 5402.5)), 
Plot(y=["gridSideController.Udc_ref", "gridSideController.Udc"], colors=["4278190335", "4294901760"]), 
CreatePlot(id=-1, x_display_unit="s", legend_layout=1, left_title="[rad]", fix_time_range_value=0, sub_plot=(3, 2), zoom_x=(0, 1200), zoom_y_l=(-0.05, 0.3)), 
Plot(y=["blade.pitchAngle"], colors=["4278190335"]), 
CreatePlot(id=-1, x_display_unit="s", legend_layout=1, left_title="[1]", fix_time_range_value=0, sub_plot=(3, 1), zoom_x=(0, 1200), zoom_y_l=(0, 0.5)), 
Plot(y=["blade.blade.Cp", "blade.Cp_max"], colors=["4278190335", "4294901760"])})
})),Protection(access=Access.nonPackageDuplicate));
  TYWindPower.Environment.WindSource windSource(DataType = "组合风速模型计算", v_basic = 3, v_gmax = 0, v_rmax = 12, tr1 = 0, tr2 = 300) 
    annotation(Placement(transformation(origin = {-196, 18.5}, 
    extent = {{-10, -10}, {10, 10}})));
  TYWindPower.Generators.PMSG PSMG 
    annotation(Placement(transformation(origin = {-95, 14}, 
    extent = {{-10, -10}, {10, 10}})));
  TYWindPower.Mechanics.Blade blade(w_start = windSource.initWindSpeed * blade.lambda_optimal / blade.R_t, H0 = 100, w_t_output = true, UserDefined = true, Cp_max = 0.441) 
    annotation(Placement(transformation(origin = {-137, 14}, 
    extent = {{-10, -10}, {10, 10}})));
  TYWindPower.PowerConverters.Averaged.AverageUniversalBridge averageUniversalBridge_m(eta = 1) 
    annotation(Placement(transformation(origin = {-19.5, 40}, 
    extent = {{10, -10}, {-10, 10}})));
  TYWindPower.Controllers.PMSG.VoltageModulation voltageModulation_m(Use_v_line_max = false) 
    annotation(Placement(transformation(origin = {-30, -64.0041}, 
    extent = {{-10, -10}, {10, 10}})));
  Modelica.Electrical.Analog.Basic.Capacitor capacitor(v(start = 5.4e3, fixed = true), C = 2.4e-3) 
    annotation(Placement(transformation(origin = {60, 38}, 
    extent = {{-10, -10}, {10, 10}}, 
    rotation = -90)));
  Modelica.Electrical.Analog.Sensors.VoltageSensor voltageSensor 
    annotation(Placement(transformation(origin = {32, 40}, 
    extent = {{-10, -10}, {10, 10}}, 
    rotation = -90)));
  TYWindPower.Controllers.PMSG.MachineSideController machineSideController(k_d = 3.75, T_d = 0.24, k_q = 3.75, T_q = 0.24, UserDefined = true) 
    annotation(Placement(transformation(origin = {-62.5, -64.0041}, 
    extent = {{-10, -10}, {10, 10}})));
  TYWindPower.Controllers.WindTurbines.MPPT MPPT(redeclare model MPPT = TYWindPower.Controllers.WindTurbines.Basics.MPPT_OT, UserDefined = true, Cp_max = 0.441) 
    annotation(Placement(transformation(origin = {-95, -64.0041}, 
    extent = {{-10, -10}, {10, 10}})));
  TYWindPower.PowerConverters.Averaged.AverageUniversalBridge averageUniversalBridge_g(eta = 1) 
    annotation(Placement(transformation(origin = {108, 38}, 
    extent = {{-10, -10}, {10, 10}})));
  TYWindPower.PowerTransmissions.PowerGrid powerGrid 
    annotation(Placement(transformation(origin = {156, 38}, 
    extent = {{10, -10}, {-10, 10}})));
  TYWindPower.Controllers.PMSG.VoltageModulation voltageModulation_g(Use_v_line_max = false) 
    annotation(Placement(transformation(origin = {94, -64.0041}, 
    extent = {{10, -10}, {-10, 10}})));
  TYWindPower.Controllers.PMSG.GridSideController gridSideController(Lc = 0, f_grid = 50, k_Q = 10, T_Q = 0.15, k_d = 30, T_d = 0.24, k_q = 30, T_q = 0.24, k_v = 1.44, T_v = 18.9e-3, k_PLL = 20, T_PLL = 0.2e-3) 
    annotation(Placement(transformation(origin = {158, -64.0041}, 
    extent = {{10, -10}, {-10, 10}})));
  Modelica.Blocks.Sources.Constant Udc_ref(k = 5.4e3) 
    annotation(Placement(transformation(origin = {202, -48.3041}, 
    extent = {{10, -10}, {-10, 10}})));
  Modelica.Blocks.Sources.TimeTable Qg_ref(table = [0, 0; 500, 0; 501, 150000; 600, 150000; 601, 0; 700, 0; 701, -150000; 800, -150000; 801, 0; 900, 0.0]) 
    annotation(Placement(transformation(origin = {202, -78.0041}, 
    extent = {{10, -10}, {-10, 10}})));
  TYWindPower.Controllers.WindTurbines.PitchController pitchController(UserDefined = true, Cp_max = 0.441) 
    annotation(Placement(transformation(origin = {-160, -64.0041}, 
    extent = {{10, -10}, {-10, 10}})));
equation
  connect(capacitor.p, averageUniversalBridge_m.pin_p) 
    annotation(Line(origin = {55, 18.1}, 
    points = {{5, 29.9}, {5, 57.9}, {-53, 57.9}, {-53, 29.9}, {-64.5, 29.9}}, 
    color = {0, 0, 255}));
  connect(averageUniversalBridge_m.plug, PSMG.plug_p) 
    annotation(Line(origin = {-22, 13.1}, 
    points = {{-7.5, 26.9}, {-73, 26.9}, {-73, 10.9}}, 
    color = {0, 0, 255}));
  connect(PSMG.flange, blade.flange) 
    annotation(Line(origin = {-66, 14}, 
    points = {{-39, 0}, {-61.1, 0}}, 
    color = {0, 0, 0}));
  connect(windSource.windSpeed, blade.windSpeed) 
    annotation(Line(origin = {-140, 17.6}, 
    points = {{-45, 0.9}, {-8.5, 0.9}}, 
    color = {0, 0, 127}));
  connect(averageUniversalBridge_m.pin_p, voltageSensor.p) 
    annotation(Line(origin = {47, 16.1}, 
    points = {{-56.5, 31.9}, {-45, 31.9}, {-45, 59.9}, {-15, 59.9}, {-15, 33.9}}, 
    color = {0, 0, 255}));
  connect(voltageSensor.n, averageUniversalBridge_m.pin_n) 
    annotation(Line(origin = {47, 2.1}, 
    points = {{-15, 27.9}, {-15, -2.1}, {-51, -2.1}, {-51, 29.9}, {-56.5, 29.9}}, 
    color = {0, 0, 255}));
  connect(capacitor.n, averageUniversalBridge_m.pin_n) 
    annotation(Line(origin = {55, -7}, 
    points = {{5, 35}, {5, 7}, {-59, 7}, {-59, 39}, {-64.5, 39}}, 
    color = {0, 0, 255}));
  connect(averageUniversalBridge_g.pin_p, capacitor.p) 
    annotation(Line(origin = {80, 19}, 
    points = {{18, 27}, {4, 27}, {4, 57}, {-20, 57}, {-20, 29}}, 
    color = {0, 0, 255}));
  connect(capacitor.n, averageUniversalBridge_g.pin_n) 
    annotation(Line(origin = {80, -6}, 
    points = {{-20, 34}, {-20, 6}, {4, 6}, {4, 36}, {18, 36}}, 
    color = {0, 0, 255}));
  connect(averageUniversalBridge_g.plug, powerGrid.plug_p) 
    annotation(Line(origin = {113, 1}, 
    points = {{5, 37}, {32.6, 37}}, 
    color = {0, 0, 255}));
  connect(Qg_ref.y, gridSideController.Qg_ref) 
    annotation(Line(origin = {155, -88.7041}, 
    points = {{36, 10.7}, {19, 10.7}, {19, 18.7}, {15, 18.7}}, 
    color = {0, 0, 127}));
  connect(Udc_ref.y, gridSideController.Udc_ref) 
    annotation(Line(origin = {172, -98.7041}, 
    points = {{19, 50.4}, {2, 50.4}, {2, 40.7}, {-2, 40.7}}, 
    color = {0, 0, 127}));
  connect(voltageSensor.v, gridSideController.Udc) 
    annotation(Line(origin = {77, -13}, 
    points = {{-56, 53}, {-56, -15}, {89, -15}, {89, -39.0041}}, 
    color = {0, 0, 127}), __MWORKS(BlockSystem(NamedSignal)));
  connect(MPPT.T_desire, machineSideController.T_desired) 
    annotation(Line(origin = {-77.5, -63.7041}, 
    points = {{-6.5, -0.3}, {3, -0.3}}, 
    color = {0, 0, 127}));
  connect(PSMG.is_abc, machineSideController.is_abc) 
    annotation(Line(origin = {-48, -15}, 
    points = {{-36, 25.9}, {-6.5, 25.9}, {-6.5, -37.0041}}, 
    color = {0, 0, 127}));
  connect(PSMG.theta_r, machineSideController.theta_r) 
    annotation(Line(origin = {-52, -16}, 
    points = {{-32, 24.76875}, {-10.5, 24.76875}, {-10.5, -36.0041}}, 
    color = {0, 0, 127}));
  connect(PSMG.w_r, machineSideController.w_r) 
    annotation(Line(origin = {-56, -17}, 
    points = {{-28, 23.6375}, {-14.5, 23.6375}, {-14.5, -35.0041}}, 
    color = {0, 0, 127}));
  connect(machineSideController.Us_abc_ref, voltageModulation_m.Uabc) 
    annotation(Line(origin = {-15.5, -51.1541}, 
    points = {{-36, -12.85}, {-26.5, -12.85}}, 
    color = {0, 0, 127}));
  connect(voltageSensor.v, voltageModulation_m.Udc) 
    annotation(Line(origin = {-4, -12}, 
    points = {{25, 52}, {25, -72}, {-38, -72}, {-38, -60.0041}}, 
    color = {0, 0, 127}), __MWORKS(BlockSystem(NamedSignal)));
  connect(voltageModulation_m.Uabc_normalized, averageUniversalBridge_m.Uabc_normalized) 
    annotation(Line(origin = {-6, 0}, 
    points = {{-13, -64.0041}, {-4, -64.0041}, {-4, 28}, {-13.5, 28}}, 
    color = {0, 0, 127}));
  connect(gridSideController.Uc_abc_ref, voltageModulation_g.Uabc) 
    annotation(Line(origin = {101, -43.0041}, 
    points = {{46, -21}, {5, -21}}, 
    color = {0, 0, 127}));
  connect(voltageSensor.v, voltageModulation_g.Udc) 
    annotation(Line(origin = {57, -12}, 
    points = {{-36, 52}, {-36, -72}, {55, -72}, {55, -60.0041}, {49, -60.0041}}, 
    color = {0, 0, 127}), __MWORKS(BlockSystem(NamedSignal)));
  connect(voltageModulation_g.Uabc_normalized, averageUniversalBridge_g.Uabc_normalized) 
    annotation(Line(origin = {73, -3}, 
    points = {{10, -61.0041}, {1, -61.0041}, {1, -19}, {35, -19}, {35, 29}}, 
    color = {0, 0, 127}));
  connect(powerGrid.Uabc, gridSideController.Ug_abc) 
    annotation(Line(origin = {156, -2}, 
    points = {{-2, 29}, {-2, -50.0041}, {2, -50.0041}}, 
    color = {0, 0, 127}));
  connect(powerGrid.i_abc, gridSideController.ig_abc) 
    annotation(Line(origin = {120, -2}, 
    points = {{30, 29}, {30, -50.0041}}, 
    color = {0, 0, 127}));
  connect(blade.w_t, MPPT.w_t) 
    annotation(Line(origin = {-107, -21}, 
    points = {{-19, 31.45}, {-11, 31.45}, {-11, -43.0041}, {0, -43.0041}}, 
    color = {0, 0, 127}));
  connect(blade.w_t, pitchController.w_t) 
    annotation(Line(origin = {-111, -21}, 
    points = {{-15, 31.45}, {-7, 31.45}, {-7, -43.0041}, {-37, -43.0041}}, 
    color = {0, 0, 127}), __MWORKS(BlockSystem(NamedSignal)));
  connect(pitchController.pitchAngle, blade.pitchAngle) 
    annotation(Line(origin = {-146, -30}, 
    points = {{-25, -34.0041}, {-32, -34.0041}, {-32, 39.3}, {-2.5, 39.3}}, 
    color = {0, 0, 127}));
  connect(pitchController.pitchAngle, MPPT.pitchAngle) 
    annotation(Line(origin = {-141.5, -74.7041}, 
    points = {{-29.5, 10.7}, {-36.5, 10.7}, {-36.5, -6.45}, {34.5, -6.45}, {34.5, 2.7}}, 
    color = {0, 0, 127}), __MWORKS(BlockSystem(NamedSignal)));
end PMSG_GSC_T;