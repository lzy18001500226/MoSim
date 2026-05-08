model PMSG_MPPT_S "直驱发电机MPPT控制系统-转速控制"
  annotation(Documentation(link = "modelica://TYWindPower/Resources/HTML/PMSG_MPPT_S.html"), Diagram(coordinateSystem(extent = {{-140, -100}, {160, 100}}, 
    grid = {2, 2})), Icon(coordinateSystem(extent = {{-100, -100}, {100, 100}}, 
    grid = {2, 2}), graphics = {Polygon(origin = {2, 27}, 
    lineColor = {16, 99, 16}, 
    fillColor = {16, 99, 16}, 
    fillPattern = FillPattern.Solid, 
    points = {{-64, 1}, {0, 37}, {64, 1}, {0, -37}}), Line(origin = {2, -18}, 
    points = {{-62, 18}, {0, -18}, {62, 18}}, 
    color = {16, 99, 16}, 
    thickness = 5), Line(origin = {2, -46}, 
    points = {{-62, 18}, {0, -18}, {62, 18}}, 
    color = {16, 99, 16}, 
    thickness = 5)}), experiment(Algorithm = Dassl, InlineIntegrator = false, InlineStepSize = false, NumberOfIntervals = 50000, StartTime = 0, StopTime = 500, Tolerance = 0.0001), __MWORKS(ContinueSimConfig(SaveContinueFile = "false", SaveBeforeStop = "false", NumberBeforeStop = 1, FixedContinueInterval = "false", ContinueIntervalLength = 500, ContinueTimeVector),ResultViewerManager(resultViewers={
ResultViewer(name="1", executeTrigger=executeTrigger.SimulationFinished, commands={
CreatePlot(id=2, x_display_unit="s", legend_layout=1, left_title="[m/s]", fix_time_range_value=0, zoom_x=(0, 500), zoom_y_l=(0, 12)), 
Plot(y=["windSource.windSpeed"], colors=["4278190335"]), 
CreatePlot(id=-1, x_display_unit="s", legend_layout=1, left_title="[rad/s]", fix_time_range_value=0, sub_plot=(1, 2), zoom_x=(0, 500), zoom_y_l=(0.4, 2)), 
Plot(y=["blade.w_t_nom", "blade.blade.w_t"], colors=["4278190335", "4294901760"]), 
CreatePlot(id=-1, x_display_unit="s", legend_layout=1, left_title="[1]", fix_time_range_value=0, sub_plot=(2, 2), zoom_x=(0, 500), zoom_y_l=(0.25, 0.5)), 
Plot(y=["blade.Cp_max", "blade.blade.Cp"], colors=["4278190335", "4294901760"]), 
CreatePlot(id=-1, x_display_unit="s", legend_layout=1, fix_time_range_value=0, sub_plot=(2, 1), zoom_x=(0, 500), zoom_y_l=(5, 10)), 
Plot(y=["blade.lambda_optimal", "blade.blade.lambda"], colors=["4278190335", "4294901760"])})
})),Protection(access=Access.nonPackageDuplicate));
  TYWindPower.Environment.WindSource windSource(DataType = "组合风速模型计算", v_basic = 3, v_gmax = 0, v_rmax = 6, tr1 = 0, tr2 = 300) 
    annotation(Placement(transformation(origin = {-122, 18.7}, 
    extent = {{-10, -10}, {10, 10}})));
  TYWindPower.Generators.PMSG linearPSM 
    annotation(Placement(transformation(origin = {-40, 14.2}, 
    extent = {{-10, -10}, {10, 10}})));
  TYWindPower.Mechanics.Blade blade(w_start = windSource.initWindSpeed * blade.lambda_optimal / blade.R_t, H0 = 100) 
    annotation(Placement(transformation(origin = {-70, 14.2}, 
    extent = {{-10, -10}, {10, 10}})));
  TYWindPower.PowerConverters.Averaged.AverageUniversalBridge averageUniversalBridge(eta = 1) 
    annotation(Placement(transformation(origin = {20, 34.2}, 
    extent = {{10, -10}, {-10, 10}})));
  TYWindPower.Controllers.PMSG.VoltageModulation voltageModulation(Use_v_line_max = true) 
    annotation(Placement(transformation(origin = {20, -36}, 
    extent = {{-10, -10}, {10, 10}})));
  Modelica.Electrical.Analog.Basic.Capacitor capacitor(v(start = 5.4e3), C = 2.4e-3) 
    annotation(Placement(transformation(origin = {111.5, 34.2}, 
    extent = {{-10, -10}, {10, 10}}, 
    rotation = -90)));
  Modelica.Electrical.Analog.Basic.Ground ground 
    annotation(Placement(transformation(origin = {136, -15.8}, 
    extent = {{-10, -10}, {10, 10}})));
  Modelica.Electrical.Analog.Sources.ConstantVoltage constantVoltage(V = 5.4e3) 
    annotation(Placement(transformation(origin = {136, 34.2}, 
    extent = {{-10, -10}, {10, 10}}, 
    rotation = -90)));
  Modelica.Blocks.Sources.Constant const(k = 0) 
    annotation(Placement(transformation(origin = {-122, -44}, 
    extent = {{-10, -10}, {10, 10}})));
  Modelica.Electrical.Analog.Sensors.VoltageSensor voltageSensor 
    annotation(Placement(transformation(origin = {87, 34.2}, 
    extent = {{-10, -10}, {10, 10}}, 
    rotation = -90)));
  TYWindPower.Controllers.WindTurbines.MPPT MPPT(redeclare model MPPT = TYWindPower.Controllers.WindTurbines.Basics.MPPT_TSR) 
    annotation(Placement(transformation(origin = {-56, -36}, 
    extent = {{-10, -10}, {10, 10}})));
  TYWindPower.Controllers.PMSG.MachineSideController machineSideController(T_w = 5, ControllerType = "转速控制器") 
    annotation(Placement(transformation(origin = {-15, -36}, 
    extent = {{-10, -10}, {10, 10}})));
equation
  connect(ground.p, constantVoltage.n) 
    annotation(Line(origin = {135, -0.8}, 
    points = {{1, -5}, {1, 25}}, 
    color = {0, 0, 255}));
  connect(constantVoltage.p, averageUniversalBridge.pin_p) 
    annotation(Line(origin = {69, 31.2}, 
    points = {{67, 13}, {67, 39}, {1, 39}, {1, 11}, {-39, 11}}, 
    color = {0, 0, 255}));
  connect(averageUniversalBridge.pin_n, ground.p) 
    annotation(Line(origin = {73, -0.4}, 
    points = {{-43, 26.6}, {-3, 26.6}, {-3, -5.4}, {63, -5.4}}, 
    color = {0, 0, 255}));
  connect(capacitor.n, ground.p) 
    annotation(Line(origin = {117, -0.8}, 
    points = {{-5.5, 25}, {-5.5, -5}, {19, -5}}, 
    color = {0, 0, 255}));
  connect(capacitor.p, averageUniversalBridge.pin_p) 
    annotation(Line(origin = {51, 31.2}, 
    points = {{60.5, 13}, {60.5, 39}, {19, 39}, {19, 11}, {-21, 11}}, 
    color = {0, 0, 255}));
  connect(averageUniversalBridge.plug, linearPSM.plug_p) 
    annotation(Line(origin = {22, 26.2}, 
    points = {{-12, 8}, {-62, 8}, {-62, -2}}, 
    color = {0, 0, 255}));
  connect(linearPSM.flange, blade.flange) 
    annotation(Line(origin = {-47, 14.2}, 
    points = {{-3, 0}, {-13.1, 0}}, 
    color = {0, 0, 0}));
  connect(windSource.windSpeed, blade.windSpeed) 
    annotation(Line(origin = {-98, 16.2}, 
    points = {{-13, 2.5}, {16.5, 2.5}}, 
    color = {0, 0, 127}));
  connect(const.y, blade.pitchAngle) 
    annotation(Line(origin = {-98, 5.2}, 
    points = {{-13, -49.2}, {12, -49.2}, {12, 4.3}, {16.5, 4.3}}, 
    color = {0, 0, 127}));
  connect(averageUniversalBridge.pin_p, voltageSensor.p) 
    annotation(Line(origin = {43, 29.2}, 
    points = {{-13, 13}, {27, 13}, {27, 41}, {44, 41}, {44, 15}}, 
    color = {0, 0, 255}));
  connect(voltageSensor.n, averageUniversalBridge.pin_n) 
    annotation(Line(origin = {47, 10.6}, 
    points = {{40, 13.6}, {40, -16.6}, {23, -16.6}, {23, 15.6}, {-17, 15.6}}, 
    color = {0, 0, 255}));
  connect(const.y, MPPT.pitchAngle) 
    annotation(Line(origin = {-101, -35.8}, 
    points = {{-10, -8.2}, {33, -8.2}}, 
    color = {0, 0, 127}), __MWORKS(BlockSystem(NamedSignal)));
  connect(windSource.windSpeed, MPPT.windSpeed) 
    annotation(Line(origin = {-101, -0.9}, 
    points = {{-10, 19.6}, {1, 19.6}, {1, -35.1}, {33, -35.1}}, 
    color = {0, 0, 127}), __MWORKS(BlockSystem(NamedSignal)));
  connect(MPPT.w_desire, machineSideController.w_desired) 
    annotation(Line(origin = {-47, -31.9}, 
    points = {{2, -4.1}, {20, -4.1}}, 
    color = {0, 0, 127}));
  connect(machineSideController.Us_abc_ref, voltageModulation.Uabc) 
    annotation(Line(origin = {5, -36}, 
    points = {{-9, 0}, {3, 0}}, 
    color = {0, 0, 127}));
  connect(voltageModulation.Uabc_normalized, averageUniversalBridge.Uabc_normalized) 
    annotation(Line(origin = {38, -1}, 
    points = {{-7, -35}, {0, -35}, {0, 23.2}, {-18, 23.2}}, 
    color = {0, 0, 127}));
  connect(voltageSensor.v, voltageModulation.Udc) 
    annotation(Line(origin = {25, -10}, 
    points = {{51, 44.2}, {23, 44.2}, {23, -44}, {-25, -44}, {-25, -34}, {-17, -34}}, 
    color = {0, 0, 127}));
  connect(linearPSM.is_abc, machineSideController.is_abc) 
    annotation(Line(origin = {-20, -6}, 
    points = {{-9, 17.1}, {13, 17.1}, {13, -18}}, 
    color = {0, 0, 127}));
  connect(linearPSM.theta_r, machineSideController.theta_r) 
    annotation(Line(origin = {-24, -8}, 
    points = {{-5, 16.96875}, {9, 16.96875}, {9, -16}}, 
    color = {0, 0, 127}));
  connect(linearPSM.w_r, machineSideController.w_r) 
    annotation(Line(origin = {-28, -9}, 
    points = {{-1, 15.8375}, {5, 15.8375}, {5, -15}}, 
    color = {0, 0, 127}));
  connect(voltageModulation.U_line, machineSideController.U_line) 
    annotation(Line(origin = {-1, -53}, 
    points = {{32, 9}, {37, 9}, {37, -5}, {-31, -5}, {-31, 9}, {-26, 9}}, 
    color = {0, 0, 127}));
end PMSG_MPPT_S;