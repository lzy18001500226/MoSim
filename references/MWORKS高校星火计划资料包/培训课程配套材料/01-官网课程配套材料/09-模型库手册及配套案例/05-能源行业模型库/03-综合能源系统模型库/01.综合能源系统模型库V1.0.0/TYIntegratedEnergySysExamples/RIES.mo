model RIES "区域综合能源系统"
  annotation(Documentation(link = "modelica://TYIntegratedEnergySys/Resources/HTML/RIES.html"), Icon(coordinateSystem(extent = {{-100, -100}, {100, 100}}, 
    grid = {2, 2}), graphics = {Polygon(origin = {0, 29}, 
    lineColor = {16, 99, 16}, 
    fillColor = {16, 99, 16}, 
    fillPattern = FillPattern.Solid, 
    points = {{-64, 1}, {0, 37}, {64, 1}, {0, -37}}), Line(origin = {0, -16}, 
    points = {{-62, 18}, {0, -18}, {62, 18}}, 
    color = {16, 99, 16}, 
    thickness = 5), Line(origin = {0, -44}, 
    points = {{-62, 18}, {0, -18}, {62, 18}}, 
    color = {16, 99, 16}, 
    thickness = 5)}), Diagram(coordinateSystem(extent = {{-100, -100}, {100, 100}}, 
    grid = {2, 2})), Documentation(info = "<html><p>
<br>
</p>
</html>"      ), experiment(Algorithm = Dassl, InlineIntegrator = false, InlineStepSize = false, Interval = 1, StartTime = 0, StopTime = 86400, Tolerance = 0.0001), __MWORKS(ContinueSimConfig(SaveContinueFile = "false", SaveBeforeStop = "false", NumberBeforeStop = 1, FixedContinueInterval = "false", ContinueIntervalLength = 86400, ContinueTimeVector),ResultViewerManager(resultViewers={
ResultViewer(name="1", executeTrigger=executeTrigger.SimulationFinished, commands={
CreatePlot(id=6, x_display_unit="s", legend_layout=1, left_title_type=2, left_title="功率[kW]", bottom_title_type=2, bottom_title="时间/s", right_title_type=2, fix_time_range_value=0, zoom_x=(0, 86400), zoom_y_l=(-10, 70)), 
Plot(legend=["风力电功率 [kW]", "光伏电功率 [kW]"], y=["windPower.Pel", "PVPower.Pel"], colors=["4278190335", "4294901760"]), 
CreatePlot(id=-1, x_display_unit="s", legend_layout=1, left_title_type=2, left_title="功率[kW]", bottom_title_type=2, bottom_title="时间/s", fix_time_range_value=0, sub_plot=(1, 2), zoom_x=(0, 86400), zoom_y_l=(-100, 150)), 
Plot(legend=["蓄冰槽功率 [kW]"], y=["iceTank.Pc"], colors=["4278190335"]), 
CreatePlot(id=-1, x_display_unit="s", legend_layout=1, left_title_type=2, left_title="成本[CNY]", bottom_title_type=2, bottom_title="时间/s", fix_time_range_value=0, sub_plot=(2, 2), zoom_x=(0, 86400), zoom_y_l=(-100, 700)), 
Plot(legend=["外部能源购置成本 [CNY]"], y=["GT.collectCosts.PurchaseCosts"], colors=["4278190335"]), 
CreatePlot(id=-1, x_display_unit="s", legend_layout=1, left_title_type=2, left_title="功率[kW]", bottom_title_type=2, bottom_title="时间/s", fix_time_range_value=0, sub_plot=(2, 1), zoom_x=(0, 86400), zoom_y_l=(-50, 300)), 
Plot(legend=["吸收式制冷机制冷功率 [kW]", "电制冷机制冷功率[kW]"], y=["absChi.Pc", "EleChi.Pc"], colors=["4278190335", "4294901760"]), 
CreatePlot(id=-1, x_display_unit="s", legend_layout=1, left_title_type=2, left_title="流量[m3/s]", bottom_title_type=2, bottom_title="时间/s", fix_time_range_value=0, sub_plot=(3, 2), zoom_x=(0, 86400), zoom_y_l=(-0.002, 0.008)), 
Plot(legend=["体积流量 [m3/s]"], y=["boundaryGas.qv_flow"], colors=["4278190335"]), 
CreatePlot(id=-1, x_display_unit="s", legend_layout=1, left_title_type=2, left_title="功率[kW]", bottom_title_type=2, bottom_title="时间/s", fix_time_range_value=0, sub_plot=(3, 1), zoom_x=(0, 86400), zoom_y_l=(100, 180)), 
Plot(legend=["冷负荷 [kW]"], y=["coldLoad.Pc"], colors=["4278190335"])})
})),Protection(access=Access.nonPackageDuplicate));
  TYIntegratedEnergySys.Boundaries.BoundaryGas boundaryGas(use_qv_in = false, Type = "根据负荷计算所需流量") "气源" 
    annotation(Placement(transformation(origin = {-168, -37.600011}, 
    extent = {{-10, -10}, {10, 10}})));
  TYIntegratedEnergySys.EnergyExchange.Gas2Heat.GasTurbine GT(Pel_nominal(displayUnit = "kW") = 100000, m_inv = 0.052, f_gt_min = 0.3, Type = "输入电负荷计算所需流量",usePowerSet=true) "燃气轮机" 
    annotation(Placement(transformation(origin = {-54, -37.6}, 
    extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Sources.BooleanExpression booleanExpression(y = true) 
    annotation(Placement(transformation(origin = {96, -94}, 
    extent = {{-10, -10}, {10, 10}})));
  TYIntegratedEnergySys.EnergyExchange.Cold.AbsorptionChiller absChi(redeclare package Medium_Con = Modelica.Media.Water.ConstantPropertyLiquidWater, redeclare package Medium_Eva = Modelica.Media.Water.ConstantPropertyLiquidWater, dpCon_nominal(displayUnit = "Pa") = 0, dpEva_nominal(displayUnit = "Pa") = 0, mEva_flow_nominal = 10, tau_Con = 30, tau_Eva = 30, mCon_flow_nominal = 20, from_dp_Eva = false, linearized_Eva = false, from_dp_Con = false, linearized_Con = false, deltaM_Eva = 0.1, deltaM_Con = 0.1, energyDynamics = Modelica.Fluid.Types.Dynamics.FixedInitial, TCon_start = 298.15, TEva_start = 279.15, pCon_start = 3e5, pEva_start = 3e5, Qflow_Eva_nominal(displayUnit = "kW") = -3e5, P_nominal = 550, useFluidPorts = false, ModeType = "设定输入功率") 
    "吸收式制冷机" 
    annotation(Placement(transformation(origin = {139.5, -77.522}, 
    extent = {{-10, -10}, {10, 10}})));
  TYIntegratedEnergySys.EnergyTransmission.HeatGrid heatGrid(N_a = 2, N_b = 2) "热网" 
    annotation(Placement(transformation(origin = {51.0625, -42}, 
    extent = {{-10, -10}, {10, 10}})));
  TYIntegratedEnergySys.Sensors.Sensor_P sensor_Ph1(PortType = "heat") "功率传感器" 
    annotation(Placement(transformation(origin = {-1.46875, -41.8}, 
    extent = {{-10, -10}, {10, 10}})));
  TYIntegratedEnergySys.Load.ColdLoad coldLoad(DataType = "负荷数据导入", timeScale(displayUnit = "h") = 3600, LoadData = {{0.0, 110}, {1, 109}, {2, 110.2}, {3, 109.5}, {4, 112.3}, {5, 113.4}, {6, 115.1}, {7, 118.8}, {8, 120}, {9, 121.2}, {10, 138.2}, {11, 145.3}, {12, 150}, {13, 162.3}, {14, 175}, {15, 160}, {16, 125}, {17, 130.2}, {18, 142}, {19, 135}, {20, 127}, {21, 116}, {22, 110}, {23, 105}, {24, 102}}) "冷负荷" 
    annotation(Placement(transformation(origin = {289.7, -4.0361}, 
    extent = {{-10, -10}, {10, 10}})));
  TYIntegratedEnergySys.Sensors.Sensor_P sensor_Pc(PortType = "cold") "功率传感器" 
    annotation(Placement(transformation(origin = {249.5, -3.98611}, 
    extent = {{-10, -10}, {10, 10}})));
  TYIntegratedEnergySys.EnergyTransmission.ColdGrid coldGrid(N_a = 2, N_b = 2) "冷网" 
    annotation(Placement(transformation(origin = {192, -3.98611}, 
    extent = {{-10, -10}, {10, 10}})));
  TYIntegratedEnergySys.EnergyStorage.Battery battery(use_P_set = true, EMax(displayUnit = "kWh") = 3.6e8, EMin(displayUnit = "kWh") = 1.44e8, etaCha = 0.95, etaDis = 0.95, Capality_nominal = 1000, V_nominal = 100) "蓄电池" 
    annotation(Placement(transformation(origin = {34, 116}, 
    extent = {{-10, -10}, {10, 10}})));
  TYIntegratedEnergySys.Load.ElectricLoad electricLoad(DataType = "负荷数据导入", timeScale(displayUnit = "h") = 3600, LoadData = {{0.0, 60}, {1, 55}, {2, 50}, {3, 48}, {4, 47.5}, {5, 46}, {6, 70}, {7, 76}, {8, 80}, {9, 102}, {10, 120}, {11, 123}, {12, 125}, {13, 103}, {14, 90}, {15, 80}, {16, 82}, {17, 110}, {18, 125}, {19, 130}, {20, 125}, {21, 118}, {22, 108}, {23, 96}, {24, 75}}) 
    "电负荷" 
    annotation(Placement(transformation(origin = {208, 91.7281}, 
    extent = {{-10, -10}, {10, 10}})));
  TYIntegratedEnergySys.EnergyTransmission.Busbar busbar_DC(N_a = 3, N_b = 2) "直流母线" 
    annotation(Placement(transformation(origin = {65.85, 91.7281}, 
    extent = {{-10, -10}, {10, 10}})));
  TYIntegratedEnergySys.EnergySource.WindPower windPower(h0 = 50, v_min = 2, N = 1, P_nom(displayUnit = "kW") = 60000, eta_constant = false) "风力发电" 
    annotation(Placement(transformation(origin = {-180, 91.9281}, 
    extent = {{-10, -10}, {10, 10}})));
  TYIntegratedEnergySys.EnergyTransmission.Busbar busbar_AC(N_a = 3, N_b = 2) "交流母线" 
    annotation(Placement(transformation(origin = {-92, 91.9281}, 
    extent = {{-10, -10}, {10, 10}})));
  TYIntegratedEnergySys.Components.Electrical.Inverter inverter(eta = 1) "逆变器" 
    annotation(Placement(transformation(origin = {-132, 51.9281}, 
    extent = {{-10, -10}, {10, 10}})));
  TYIntegratedEnergySys.Environment.Illumination illumination(TAmbInputType = "数据导入", IrradianceInputType = "数据导入", Irradiance_Table = {{0, 0.00}, {3600, 0.00}, {7200, 0.00}, {10800, 2.85}, {14400, 26.37}, {18000, 84.56}, {21600, 166.64}, {25200, 253.11}, {28800, 321.56}, {32400, 370.22}, {36000, 394.68}, {39600, 420.16}, {43200, 446.37}, {46800, 450.10}, {50400, 413.33}, {54000, 368.68}, {57600, 253.24}, {61200, 150.85}, {64800, 98.33}, {68400, 45.80}, {72000, 0.00}, {75600, 0.00}, {79200, 0.00}, {82800, 0.00}, {86400, 0.00}}, TAmb_Table = {{0.0, 23}, {2, 22}, {4, 22}, {6, 22}, {8, 25}, {10, 28}, {12, 30}, {14, 31}, {16, 30}, {18, 28}, {20, 26}, {22, 25}, {24, 23}}, timeScale_TAmb(displayUnit = "h") = 3600) 
    "光照模型" 
    annotation(Placement(transformation(origin = {-228, 51.8281}, 
    extent = {{-10, -10}, {10, 10}})));
  TYIntegratedEnergySys.EnergySource.PhotovoltaicPower PVPower(N = 1000, P_nom(displayUnit = "W") = 55, A = 0.6) "光伏发电" 
    annotation(Placement(transformation(origin = {-180, 51.9281}, 
    extent = {{-10, -10}, {10, 10}})));
  TYIntegratedEnergySys.Environment.WindSource windSource(DataType = "风速数据导入", windSpeedTable = {{0, 11}, {1, 12}, {2, 9.8}, {3, 10}, {4, 10.5}, {5, 11}, {6, 7}, {7, 5.2}, {8, 5.6}, {9, 2.6}, {10, 5.8}, {11, 5}, {12, 2.2}, {13, 3.8}, {14, 5.3}, {15, 2}, {16, 4.3}, {17, 6.5}, {18, 10}, {19, 10.3}, {20, 12.2}, {21, 14.3}, {22, 12}, {23, 10.1}, {24, 12.5}}, timeScale(displayUnit = "h") = 3600, v_nmax = 0, v_nmin = 0, Tg(displayUnit = "h") = 7200, tg(displayUnit = "h") = 14400, tr1(displayUnit = "h") = 14400, tr2(displayUnit = "h") = 18000) 
    "风速模型" 
    annotation(Placement(transformation(origin = {-228, 91.6281}, 
    extent = {{-10, -10}, {10, 10}})));
  TYIntegratedEnergySys.EnergyTransmission.ElectricGrid electricGrid "电网" 
    annotation(Placement(transformation(origin = {-180, 131.928}, 
    extent = {{-10, -10}, {10, 10}})));
  TYIntegratedEnergySys.Components.Electrical.Inverter inverter1(eta = 1) "逆变器" 
    annotation(Placement(transformation(origin = {86.65, 91.9281}, 
    extent = {{-10, -10}, {10, 10}})));
  TYIntegratedEnergySys.Sensors.Sensor_P sensor_Pe(PortType = "electric") "功率传感器" 
    annotation(Placement(transformation(origin = {174, 91.7281}, 
    extent = {{-10, 10}, {10, -10}})));
  TYIntegratedEnergySys.Components.Electrical.Rectifier rectifier1(eta = 1) "整流器" 
    annotation(Placement(transformation(origin = {-1.46875, 92.1281}, 
    extent = {{-10, -10}, {10, 10}})));
  TYIntegratedEnergySys.Controllers.PowerController_Battery powerController_Battery(SOC_max = battery.SOC_max, SOC_min = battery.SOC_min) "燃料电池功率控制器" 
    annotation(Placement(transformation(origin = {-10, 132.15}, 
    extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Sources.RealExpression Pel_produce(y = windPower.Pel + PVPower.Pel) "生产电功率" 
    annotation(Placement(transformation(origin = {-54, 150}, 
    extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Sources.RealExpression Pel_demand(y = sensor_Pe.P) "消耗电功率" 
    annotation(Placement(transformation(origin = {-54, 116}, 
    extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Sources.BooleanExpression ONTime(y = (time >= 8 * 3600 and time <= 11 * 3600) or (time >= 17 * 3600 and time <= 22 * 3600)) "开启时间" 
    annotation(Placement(transformation(origin = {-130, 6.04999}, 
    extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Sources.RealExpression Pel_produce1(y = windPower.Pel + PVPower.Pel) "生产电功率" 
    annotation(Placement(transformation(origin = {-130, 22.28609}, 
    extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Sources.RealExpression Pel_demand1(y = sensor_Pe.P) "消耗电功率" 
    annotation(Placement(transformation(origin = {-130, -10.7139}, 
    extent = {{-10, -10}, {10, 10}})));
  TYIntegratedEnergySys.Controllers.PowerController_GT powerController_GT(P_nominal = GT.Pel_nominal, f_min = GT.f_gt_min) "燃气轮机功率控制器" 
    annotation(Placement(transformation(origin = {-94, 6}, 
    extent = {{-10, -10}, {10, 10}})));
  TYIntegratedEnergySys.EnergyExchange.Cold.CompressionChiller EleChi(useFluidPorts = false, ModeType = "设定输出功率", useCOPinput = false) "电制冷机" 
    annotation(Placement(transformation(origin = {139.5, 32.4}, 
    extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Sources.RealExpression T_set(y = 6 + 273.15) "温度设定值" 
    annotation(Placement(transformation(origin = {96, 60}, 
    extent = {{-10, -10}, {10, 10}})));
  TYIntegratedEnergySys.Load.HeatLoad heatLoad(DataType = "常数输入", timeScale(displayUnit = "h") = 3600, LoadData = {{0.0, 125}, {1, 120}, {2, 122}, {3, 124}, {4, 125}, {5, 118}, {6, 110}, {7, 95}, {8, 90}, {9, 87}, {10, 85}, {11, 80}, {12, 75}, {13, 61}, {14, 55}, {15, 62}, {16, 76}, {17, 92}, {18, 110}, {19, 126}, {20, 130}, {21, 150}, {22, 143}, {23, 134}, {24, 126}}, Ph_constant = 0) 
    "热负荷" 
    annotation(Placement(transformation(origin = {208, -144.2}, 
    extent = {{-10, -10}, {10, 10}})));
  TYIntegratedEnergySys.Sensors.Sensor_P sensor_Ph(PortType = "heat") "功率传感器" 
    annotation(Placement(transformation(origin = {161.475, -144.2}, 
    extent = {{-10, -10}, {10, 10}})));
  TYIntegratedEnergySys.EnergyExchange.Gas2Heat.GasBoiler gasBoiler(ModeType = "输入锅炉出口水温", Q_flow_nominal(displayUnit = "kW") = 2e5, useFluidPorts = false, eta_constant = 0.95) "燃气锅炉" 
    annotation(Placement(transformation(origin = {-22, -94}, 
    extent = {{-10, -10}, {10, 10}})));
  TYIntegratedEnergySys.EnergyStorage.HeatTank heatTank(useFluidPorts = false, T_start = 313.15, redeclare package Medium = Modelica.Media.Water.ConstantPropertyLiquidWater) "储热罐" 
    annotation(Placement(transformation(origin = {96, -144.2}, 
    extent = {{-10, -10}, {10, 10}})));
  TYIntegratedEnergySys.Boundaries.BoundaryTemperature bound_T(T = 303.15) "温度边界" 
    annotation(Placement(transformation(origin = {128, -120}, 
    extent = {{10, -10}, {-10, 10}})));
  Modelica.Blocks.Sources.RealExpression Pc(y = max(0, sensor_Pc.P - sensor_Pc1.P)) "冷功率" 
    annotation(Placement(transformation(origin = {96, 38.6}, 
    extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Sources.BooleanExpression booleanExpression1(y = true) 
    annotation(Placement(transformation(origin = {65.85, 32.4}, 
    extent = {{-10, -10}, {10, 10}})));
  TYIntegratedEnergySys.Sensors.Sensor_P sensor_Pc1(PortType = "cold") "功率传感器" 
    annotation(Placement(transformation(origin = {174, -37.6}, 
    extent = {{10, -10}, {-10, 10}}, 
    rotation = -90)));
  TYIntegratedEnergySys.EnergyStorage.IceTank iceTank(useFluidPorts = false) "蓄冰槽" 
    annotation(Placement(transformation(origin = {224, -30}, 
    extent = {{-10, -10}, {10, 10}})));
  TYIntegratedEnergySys.Components.Electrical.Inverter inverter2(eta = 1) "逆变器" 
    annotation(Placement(transformation(origin = {-33.075, 32.4}, 
    extent = {{-10, -10}, {10, 10}}, 
    rotation = 90)));
  Modelica.Blocks.Sources.RealExpression HeatLoad(y = sensor_Ph.P) "热负荷" 
    annotation(Placement(transformation(origin = {-70, -71.3664}, 
    extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Sources.RealExpression realExpression(y = sensor_Ph1.P) 
    annotation(Placement(transformation(origin = {96, -71.3664}, 
    extent = {{-10, -10}, {10, 10}})));
  TYIntegratedEnergySys.EnergyTransmission.GasGrid gasGrid(N_b = 2) "气网" 
    annotation(Placement(transformation(origin = {-106.53125, -37.6}, 
    extent = {{-10, -10}, {10, 10}})));
  inner TYIntegratedEnergySys.Components.Collectors.CostsCenter costsCenter(calculateCost = true) 
    annotation(Placement(transformation(origin = {-256, 160}, 
    extent = {{-10, -10}, {10, 10}})));
equation
  connect(gasGrid.gas_b[1], GT.gas) 
    annotation(Line(origin = {-73, -37.6}, 
    points = {{-23.1312, 0}, {9, 0}}, 
    color = {0, 209, 209}));
  connect(booleanExpression.y, absChi.on) 
    annotation(Line(origin = {110.125, -87.4861}, 
    points = {{-3.125, -6.5139}, {19.375, -6.5139}, {19.375, 9.9641}}, 
    color = {255, 0, 255}));
  connect(sensor_Ph1.heat_b, heatGrid.heat_a[1]) 
    annotation(Line(origin = {-18, -41.6}, 
    points = {{25.53125, -0.2}, {59.0625, -0.2}}, 
    color = {191, 0, 0}));
  connect(heatGrid.heat_b[1], absChi.heat) 
    annotation(Line(origin = {91.075, -62}, 
    points = {{-30.0125, 20}, {48.525, 20}, {48.525, -5.522}}, 
    color = {191, 0, 0}));
  connect(sensor_Pe.electric_b, electricLoad.electric) 
    annotation(Line(origin = {145, 135.273}, 
    points = {{38, -43.5449}, {53, -43.5449}}, 
    color = {16, 99, 16}));
  connect(windPower.electric, busbar_AC.electric_a[1]) 
    annotation(Line(origin = {-137, 94.9281}, 
    points = {{-33, -3}, {42.4, -3}, {42.4, -2.8}}, 
    color = {16, 99, 16}));
  connect(inverter.electric_AC, busbar_AC.electric_a[2]) 
    annotation(Line(origin = {-121, 74.9281}, 
    points = {{-0.8, -23}, {11, -23}, {11, 17.2}, {26.4, 17.2}}, 
    color = {16, 99, 16}));
  connect(PVPower.electric, inverter.electric_DC) 
    annotation(Line(origin = {-149, 30.2}, 
    points = {{-20.8, 21.7281}, {7, 21.7281}}, 
    color = {16, 99, 16}));
  connect(illumination.TAmbient, PVPower.TAmbient) 
    annotation(Line(origin = {-188, 33.2}, 
    points = {{-29.4, 21.7281}, {-2.2, 21.7281}}, 
    color = {0, 0, 127}));
  connect(illumination.Irradiance, PVPower.Irradiance) 
    annotation(Line(origin = {-188, 27.2}, 
    points = {{-29.4, 21.6281}, {-2.2, 21.6281}, {-2.2, 21.9281}}, 
    color = {0, 0, 127}));
  connect(windPower.windSpeed, windSource.windSpeed) 
    annotation(Line(origin = {-189, 91.9281}, 
    points = {{-1.28512, 0}, {-28.4, 0}, {-28.4, -0.3}}, 
    color = {0, 0, 127}));
  connect(electricGrid.electric, busbar_AC.electric_a[3]) 
    annotation(Line(origin = {-132, 111.928}, 
    points = {{-38, 20.1}, {22, 20.1}, {22, -19.7999}, {37.4, -19.7999}}, 
    color = {16, 99, 16}));
  connect(busbar_DC.electric_b[1], inverter1.electric_DC) 
    annotation(Line(origin = {95, 91.7281}, 
    points = {{-25.75, 0.2}, {-18.35, 0.2}}, 
    color = {16, 99, 16}));
  connect(rectifier1.electric_DC, busbar_DC.electric_a[2]) 
    annotation(Line(origin={28,91.7281}, 
points={{-19.2687,0.4},{35.25,0.4},{35.25,0.2}}, 
color={16,99,16}));
  connect(battery.electric, busbar_DC.electric_a[1]) 
    annotation(Line(origin = {33, 109}, 
    points = {{-9, 7}, {-15, 7}, {-15, -17.0719}, {30.25, -17.0719}}, 
    color = {16, 99, 16}));
  connect(powerController_Battery.Pel, battery.P_set) 
    annotation(Line(origin = {9, 139}, 
    points = {{-8.6, -6.85006}, {14.6, -6.85006}, {14.6, -19.1719}}, 
    color = {0, 0, 127}));
  connect(battery.SOC, powerController_Battery.SOC) 
    annotation(Line(origin = {11, 142}, 
    points = {{33.6, -22.1719}, {39, -22.1719}, {39, 14}, {-20.95, 14}, {-20.95, 0.35}}, 
    color = {0, 0, 127}));
  connect(Pel_produce.y, powerController_Battery.P_produce) 
    annotation(Line(origin = {-31, 143}, 
    points = {{-12, 7}, {11.2, 7}, {11.2, -6.58}}, 
    color = {0, 0, 127}));
  connect(Pel_demand.y, powerController_Battery.P_demand) 
    annotation(Line(origin = {-31, 122}, 
    points = {{-12, -6}, {11.2, -6}, {11.2, 5.8}}, 
    color = {0, 0, 127}));
  connect(rectifier1.electric_AC, busbar_AC.electric_b[1]) 
    annotation(Line(origin={-53,92}, 
points={{41.53125,0.1281},{-35.6,0.1281}}, 
color={16,99,16}));
  connect(powerController_GT.Pel, GT.Pel_set) 
    annotation(Line(origin = {-55, -16}, 
    points = {{-28.6, 21.8}, {-9, 21.8}, {-9, -13.8}}, 
    color = {0, 0, 127}));
  connect(powerController_GT.conditon_ON, ONTime.y) 
    annotation(Line(origin = {-111, 6.03609}, 
    points = {{7.2, 0.01391}, {-8, 0.01391}, {-8, 0.0139}}, 
    color = {255, 0, 255}));
  connect(Pel_demand1.y, powerController_GT.P_demand) 
    annotation(Line(origin = {-111, -4.96389}, 
    points = {{-8, -5.75003}, {7.2, -5.75003}, {7.2, 6.61389}}, 
    color = {0, 0, 127}));
  connect(Pel_produce1.y, powerController_GT.P_produce) 
    annotation(Line(origin = {-111, 16.03609}, 
    points = {{-8, 6.25}, {7.2, 6.25}, {7.2, -5.76609}}, 
    color = {0, 0, 127}));
  connect(inverter1.electric_AC, sensor_Pe.electric_a) 
    annotation(Line(origin = {107, 92}, 
    points = {{-10.15, -0.0719}, {58.2, -0.0719}, {58.2, -0.2719}}, 
    color = {16, 99, 16}));
  connect(inverter1.electric_AC, EleChi.electric) 
    annotation(Line(origin = {137, 67}, 
    points = {{-40.15, 24.9281}, {2.6, 24.9281}, {2.6, -24.4}}, 
    color = {16, 99, 16}));
  connect(sensor_Ph.heat_b, heatLoad.heat) 
    annotation(Line(origin = {146.00025, -143.764}, 
    points = {{24.47475, -0.436}, {51.9998, -0.436}}, 
    color = {191, 0, 0}));
  connect(bound_T.port[1], heatTank.heatport) 
    annotation(Line(origin = {-239.744, -85.164}, 
    points = {{357.744, -34.836}, {335.744, -34.836}, {335.744, -48.836}}, 
    color = {191, 0, 0}));
  connect(gasGrid.gas_b[2], gasBoiler.gas) 
    annotation(Line(origin = {-99, -129}, 
    points = {{2.86875, 91.4}, {2.86875, 35}, {67, 35}}, 
    color = {0, 209, 209}));
  connect(GT.heat, sensor_Ph1.heat_a) 
    annotation(Line(origin = {-19, -42}, 
    points = {{-25, 0.2}, {8.73125, 0.2}}, 
    color = {191, 0, 0}));
  connect(T_set.y, EleChi.T_Eva_set) 
    annotation(Line(origin = {108, 48}, 
    points = {{-1, 12}, {20.8778, 12}, {20.8778, -7.2}}, 
    color = {0, 0, 127}));
  connect(booleanExpression1.y, EleChi.on) 
    annotation(Line(origin = {105, 31}, 
    points = {{-28.15, 1.4}, {23.8778, 1.4}, {23.8778, 1.48889}}, 
    color = {255, 0, 255}));
  connect(Pc.y, EleChi.P_set) 
    annotation(Line(origin = {118, 42}, 
    points = {{-11, -3.4}, {10.9528, -3.4}}, 
    color = {0, 0, 127}));
  connect(gasBoiler.heat, heatGrid.heat_a[2]) 
    annotation(Line(origin = {23, -88}, 
    points = {{-35, -6}, {-1, -6}, {-1, 46.2}, {18.0625, 46.2}}, 
    color = {191, 0, 0}));
  connect(heatGrid.heat_b[2], heatTank.heat_Gen) 
    annotation(Line(origin = {117, -101}, 
    points = {{-55.9375, 59}, {-43, 59}, {-43, -43}, {-30.8, -43}}, 
    color = {191, 0, 0}));
  connect(heatTank.heat_Consumer, sensor_Ph.heat_a) 
    annotation(Line(origin = {149, -143.964}, 
    points = {{-42.8, -0.036}, {3.675, -0.036}, {3.675, -0.236}}, 
    color = {191, 0, 0}));
  connect(HeatLoad.y, gasBoiler.P_set) 
    annotation(Line(origin = {-56, -156}, 
    points = {{-3, 84.6336}, {10, 84.6336}, {10, 65}, {23.2, 65}}, 
    color = {0, 0, 127}));
  connect(realExpression.y, absChi.P_set) 
    annotation(Line(origin = {118, -71}, 
    points = {{-11, -0.3664}, {11.225, -0.3664}, {11.225, -0.36644}}, 
    color = {0, 0, 127}));
  connect(GT.electric, inverter2.electric_DC) 
    annotation(Line(origin = {-39, -6}, 
    points = {{-5, -28.6}, {5.925, -28.6}, {5.925, 28.4}}, 
    color = {16, 99, 16}));
  connect(inverter2.electric_AC, busbar_AC.electric_b[2]) 
    annotation(Line(origin = {-61, 67}, 
    points = {{27.925, -24.4}, {27.925, 25.1281}, {-27.6, 25.1281}}, 
    color = {16, 99, 16}));
  connect(boundaryGas.gas, gasGrid.gas_a[1]) 
    annotation(Line(origin = {-137, -38}, 
    points = {{-21, 0.399989}, {20.0687, 0.399989}, {20.0687, 0.2}}, 
    color = {0, 209, 209}));
  connect(absChi.cold, sensor_Pc1.cold_a) 
    annotation(Line(origin = {157, -68}, 
    points = {{-17.4, -19.522}, {-17.4, -28}, {17, -28}, {17, 21.6}}, 
    color = {117, 141, 176}));
  connect(sensor_Pc1.cold_b, coldGrid.cold_a[2]) 
    annotation(Line(origin = {178, -16}, 
    points = {{-4, -12.6}, {-4, 12.21389}, {4, 12.21389}}, 
    color = {117, 141, 176}));
  connect(EleChi.cold, coldGrid.cold_a[1]) 
    annotation(Line(origin = {161, 9}, 
    points = {{-21.4, 13.2}, {-21.4, -12.78611}, {21, -12.78611}}, 
    color = {117, 141, 176}));
  connect(coldGrid.cold_b[2], iceTank.cold) 
    annotation(Line(origin = {213, -12}, 
    points = {{-11, 8.01389}, {10.9661, 8.01389}, {10.9661, -7.96}}, 
    color = {117, 141, 176}));
  connect(coldGrid.cold_b[1], sensor_Pc.cold_a) 
    annotation(Line(origin = {221, -4}, 
    points = {{-19, 0.01389}, {19.7, 0.01389}}, 
    color = {117, 141, 176}));
  connect(sensor_Pc.cold_b, coldLoad.cold) 
    annotation(Line(origin = {269, -4}, 
    points = {{-10.5, 0.01389}, {10.7, 0.01389}, {10.7, -0.0361}}, 
    color = {117, 141, 176}));
end RIES;