model PMSG_MPPT_T "直驱发电机MPPT控制系统-转矩控制"
  annotation(Documentation(link = "modelica://TYWindPower/Resources/HTML/PMSG_MPPT_T.html"), Icon(coordinateSystem(extent = {{-100, -100}, {100, 100}}, 
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
    thickness = 5)}), Diagram(coordinateSystem(extent = {{-180, -80}, {180, 80}}, 
    grid = {2, 2})), experiment(Algorithm = Dassl, InlineIntegrator = false, InlineStepSize = false, StartTime = 0, StopTime = 500, Tolerance = 0.0001, NumberOfIntervals = 50000), __MWORKS(ContinueSimConfig(SaveContinueFile = "false", SaveBeforeStop = "false", NumberBeforeStop = 1, FixedContinueInterval = "false", ContinueIntervalLength = 500, ContinueTimeVector),ResultViewerManager(resultViewers={
ResultViewer(name="Result", executeTrigger=executeTrigger.SimulationFinished, commands={
CreatePlot(id=1, x_display_unit="s", legend_layout=1, left_title_type=2, left_title="风速/[m/s]", bottom_title_type=2, bottom_title="时间/s", right_title_type=2, fix_time_range_value=0, zoom_x=(0, 500), zoom_y_l=(0, 12)), 
Plot(legend=["风速 [m/s]"], y=["windSource.windSpeed"], colors=["4278190335"]), 
CreatePlot(id=-1, x_display_unit="s", legend_layout=1, left_title_type=2, left_title="功率/MW", bottom_title_type=2, bottom_title="时间/s", fix_time_range_value=0, sub_plot=(2, 1), zoom_x=(0, 500), zoom_y_l=(0, 4)), 
Plot(legend=["(风机额定机械功率)blade.Pm_nom [MW]", "(风机实际机械功率)blade.P_m [MW]", "(风能)blade.P_w [MW]"], y=["blade.Pm_nom", "blade.P_m", "blade.P_w"], colors=["4278190335", "4294901760", "4278222848"]), 
CreatePlot(id=-1, x_display_unit="s", legend_layout=1, left_title_type=2, left_title="叶尖速比/1", bottom_title_type=2, bottom_title="时间/s", fix_time_range_value=0, sub_plot=(2, 2), zoom_x=(0, 500), zoom_y_l=(4, 11)), 
Plot(legend=["(最大风能利用系数的最优叶尖比)blade.lambda_optimal [1]", "(叶尖速比)blade.blade.lambda [rad]"], y=["blade.lambda_optimal", "blade.blade.lambda"], colors=["4278190335", "4294901760"]), 
CreatePlot(id=-1, x_display_unit="s", legend_layout=1, left_title_type=2, left_title="最大风能利用系数/1", bottom_title_type=2, bottom_title="时间/s", fix_time_range_value=0, sub_plot=(1, 2), zoom_x=(0, 500), zoom_y_l=(0.05, 0.45)), 
Plot(legend=["(风能利用系数)blade.blade.Cp [1]", "(最大风能利用系数)blade.Cp_max [1]"], y=["blade.blade.Cp", "blade.Cp_max"], colors=["4278190335", "4294901760"])})
})),Protection(access=Access.nonPackageDuplicate));
  TYWindPower.Environment.WindSource windSource(DataType = "组合风速模型计算", v_basic = 3, v_gmax = 0, v_rmax = 6, tr1 = 0, tr2 = 300, initWindSpeed = 3) 
    annotation(Placement(transformation(origin = {-162, 12.5}, 
    extent = {{-10, -10}, {10, 10}})));
  TYWindPower.Generators.PMSG PSMG(redeclare TYWindPower.Generators.DeviceParameter.PMSG.PMSG_2MW device, use_Tr = false, use_power_m = false, use_temperatures = false, use_power_el = false, UserDefined = true) 
    annotation(Placement(transformation(origin = {-80, 8}, 
    extent = {{-10, -10}, {10, 10}})));
  TYWindPower.Mechanics.Blade blade(w_start = windSource.initWindSpeed * blade.lambda_optimal / blade.R_t, H0 = 100, Cp_output = false, lambda_output = false, w_t_output = true) 
    annotation(Placement(transformation(origin = {-114, 8}, 
    extent = {{-10, -10}, {10, 10}})));
  TYWindPower.PowerConverters.Averaged.AverageUniversalBridge averageUniversalBridge(eta = 1) 
    annotation(Placement(transformation(origin = {-2, 30}, 
    extent = {{10, -10}, {-10, 10}})));
  TYWindPower.Controllers.PMSG.VoltageModulation voltageModulation(Use_v_line_max = false) 
    annotation(Placement(transformation(origin = {-2, -34}, 
    extent = {{-10, -10}, {10, 10}})));
  Modelica.Electrical.Analog.Basic.Capacitor capacitor(v(start = 5.4e3), C = 2.4e-3) 
    annotation(Placement(transformation(origin = {82, 28}, 
    extent = {{-10, -10}, {10, 10}}, 
    rotation = -90)));
  Modelica.Electrical.Analog.Basic.Ground ground 
    annotation(Placement(transformation(origin = {110, -26.9}, 
    extent = {{-10, -10}, {10, 10}})));
  Modelica.Electrical.Analog.Sources.ConstantVoltage constantVoltage(V = 5.4e3) 
    annotation(Placement(transformation(origin = {110, 28}, 
    extent = {{-10, -10}, {10, 10}}, 
    rotation = -90)));
  Modelica.Blocks.Sources.Constant const(k = 0) 
    annotation(Placement(transformation(origin = {-162, -42}, 
    extent = {{-10, -10}, {10, 10}})));
  Modelica.Electrical.Analog.Sensors.VoltageSensor voltageSensor 
    annotation(Placement(transformation(origin = {148, 28}, 
    extent = {{-10, -10}, {10, 10}}, 
    rotation = -90)));
  TYWindPower.Controllers.PMSG.MachineSideController machineSideController(k_d = 3.75, T_d = 0.24, k_q = 3.75, T_q = 0.24, UserDefined = true, redeclare TYWindPower.Controllers.PMSG.DeviceParameter.PMSG_2MW device) 
    annotation(Placement(transformation(origin = {-48, -34}, 
    extent = {{-10, -10}, {10, 10}})));
  TYWindPower.Controllers.WindTurbines.MPPT MPPT(redeclare model MPPT = TYWindPower.Controllers.WindTurbines.Basics.MPPT_OT) 
    annotation(Placement(transformation(origin = {-80, -34}, 
    extent = {{-10, -10}, {10, 10}})));
equation
  connect(ground.p, constantVoltage.n) 
    annotation(Line(origin = {142, 7}, 
    points = {{-32, -23.9}, {-32, 11}}, 
    color = {0, 0, 255}));
  connect(constantVoltage.p, averageUniversalBridge.pin_p) 
    annotation(Line(origin = {63, 24.1}, 
    points = {{47, 13.9}, {47, 31.9}, {-19, 31.9}, {-19, 13.9}, {-55, 13.9}}, 
    color = {0, 0, 255}));
  connect(averageUniversalBridge.pin_n, ground.p) 
    annotation(Line(origin = {35, -8.3}, 
    points = {{-27, 30.3}, {9, 30.3}, {9, 8.3}, {75, 8.3}, {75, -8.6}}, 
    color = {0, 0, 255}));
  connect(capacitor.n, ground.p) 
    annotation(Line(origin = {122, 4.7}, 
    points = {{-40, 13.3}, {-40, -4.7}, {-12, -4.7}, {-12, -21.6}}, 
    color = {0, 0, 255}));
  connect(capacitor.p, averageUniversalBridge.pin_p) 
    annotation(Line(origin = {45, 24.1}, 
    points = {{37, 13.9}, {37, 31.9}, {-1, 31.9}, {-1, 13.9}, {-37, 13.9}}, 
    color = {0, 0, 255}));
  connect(averageUniversalBridge.plug, PSMG.plug_p) 
    annotation(Line(origin = {-42, 20}, 
    points = {{30, 10}, {-38, 10}, {-38, -2}}, 
    color = {0, 0, 255}));
  connect(PSMG.flange, blade.flange) 
    annotation(Line(origin = {-89, 8}, 
    points = {{-1, 0}, {-15.1, 0}}, 
    color = {0, 0, 0}));
  connect(windSource.windSpeed, blade.windSpeed) 
    annotation(Line(origin = {-140, 10}, 
    points = {{-11, 2.5}, {14.5, 2.5}}, 
    color = {0, 0, 127}));
  connect(const.y, blade.pitchAngle) 
    annotation(Line(origin = {-140, -1}, 
    points = {{-11, -41}, {8, -41}, {8, 4.3}, {14.5, 4.3}}, 
    color = {0, 0, 127}));
  connect(averageUniversalBridge.pin_p, voltageSensor.p) 
    annotation(Line(origin = {11, 23}, 
    points = {{-3, 15}, {33, 15}, {33, 33}, {137, 33}, {137, 15}}, 
    color = {0, 0, 255}));
  connect(voltageSensor.n, averageUniversalBridge.pin_n) 
    annotation(Line(origin = {9, 2.7}, 
    points = {{139, 15.3}, {139, -2.7}, {35, -2.7}, {35, 19.3}, {-1, 19.3}}, 
    color = {0, 0, 255}));
  connect(voltageSensor.v, voltageModulation.Udc) 
    annotation(Line(origin = {-11, -6}, 
    points = {{148, 34}, {148, -48}, {-13, -48}, {-13, -36}, {-3, -36}}, 
    color = {0, 0, 127}));
  connect(const.y, MPPT.pitchAngle) 
    annotation(Line(origin = {-133, -42.6}, 
    points = {{-18, 0.6}, {41, 0.6}}, 
    color = {0, 0, 127}), __MWORKS(BlockSystem(NamedSignal)));
  connect(MPPT.T_desire, machineSideController.T_desired) 
    annotation(Line(origin = {-77, -34}, 
    points = {{8, 0}, {17, 0}}, 
    color = {0, 0, 127}));
  connect(blade.w_t, MPPT.w_t) 
    annotation(Line(origin = {-113, -15}, 
    points = {{10, 19.45}, {15, 19.45}, {15, -19}, {21, -19}}, 
    color = {0, 0, 127}));
  connect(PSMG.w_r, machineSideController.w_r) 
    annotation(Line(origin = {-62, -11}, 
    points = {{-7, 11.6375}, {6, 11.6375}, {6, -11}}, 
    color = {0, 0, 127}));
  connect(PSMG.theta_r, machineSideController.theta_r) 
    annotation(Line(origin = {-58, -10}, 
    points = {{-11, 12.76875}, {10, 12.76875}, {10, -12}}, 
    color = {0, 0, 127}));
  connect(PSMG.is_abc, machineSideController.is_abc) 
    annotation(Line(origin = {-54, -9}, 
    points = {{-15, 13.9}, {14, 13.9}, {14, -13}}, 
    color = {0, 0, 127}));
  connect(voltageModulation.Uabc_normalized, averageUniversalBridge.Uabc_normalized) 
    annotation(Line(origin = {-9, 1}, 
    points = {{18, -35}, {27, -35}, {27, 17}, {7, 17}}, 
    color = {0, 0, 127}));
  connect(machineSideController.Us_abc_ref, voltageModulation.Uabc) 
    annotation(Line(origin = {-25, -34}, 
    points = {{-12, 0}, {11, 0}}, 
    color = {0, 0, 127}));
end PMSG_MPPT_T;