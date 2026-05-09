model PVFuelCellCogenerationSys "光伏-氢燃料电池热电联产系统"
  annotation(Documentation(link = "modelica://TYIntegratedEnergySys/Resources/HTML/PVFuelCellCogenerationSys.html"), Icon(coordinateSystem(extent = {{-100.0, -100.0}, {100.0, 100.0}}, 
    grid = {2.0, 2.0}), graphics = {Polygon(origin = {-7.105427357601002e-15, 33.0}, 
    lineColor = {16, 99, 16}, 
    fillColor = {16, 99, 16}, 
    fillPattern = FillPattern.Solid, 
    points = {{-64.0, 1.0}, {0.0, 37.0}, {64.0, 1.0}, {0.0, -37.0}}), Line(origin = {0.0, -12.0}, 
    points = {{-62.0, 18.0}, {0.0, -18.0}, {62.0, 18.0}}, 
    color = {16, 99, 16}, 
    thickness = 5.0), Line(origin = {7.105427357601002e-15, -39.99999999999999}, 
    points = {{-62.0, 18.0}, {0.0, -18.0}, {62.0, 18.0}}, 
    color = {16, 99, 16}, 
    thickness = 5.0)}), Diagram(coordinateSystem(extent = {{-180, -120}, {180, 120}}, 
    grid = {2, 2})), experiment(Algorithm = Dassl, InlineIntegrator = false, InlineStepSize = false, Interval = 10, StartTime = 0, StopTime = 86400, Tolerance = 0.0001), __MWORKS(ContinueSimConfig(SaveContinueFile = "false", SaveBeforeStop = "false", NumberBeforeStop = 1, FixedContinueInterval = "false", ContinueIntervalLength = 17280, ContinueTimeVector),ResultViewerManager(resultViewers={
ResultViewer(name="1", executeTrigger=executeTrigger.SimulationFinished, commands={
CreatePlot(id=1, x_display_unit="s", legend_layout=1, left_title="[kW]", fix_time_range_value=0, zoom_x=(0, 86400), zoom_y_l=(-2, 10)), 
Plot(y=["PVPower.Pel"], colors=["4278190335"]), 
CreatePlot(id=-1, x_display_unit="s", legend_layout=1, left_title="[kW]", fix_time_range_value=0, sub_plot=(1, 2), zoom_x=(0, 86400), zoom_y_l=(0, 1)), 
Plot(y=["sensor_Pload.P"], colors=["4278190335"]), 
CreatePlot(id=-1, x_display_unit="s", legend_layout=1, left_title="[1]", right_title="[kW]", fix_time_range_value=0, sub_plot=(1, 3), zoom_x=(0, 86400), zoom_y_l=(0, 1.2), zoom_y_r=(-1, 3)), 
Plot(y=["battery.SOC", "battery.P"], colors=["4278190335", "4294901760"]), 
CreatePlot(id=-1, x_display_unit="s", legend_layout=1, left_title="[m3/s]", fix_time_range_value=0, sub_plot=(2, 2), zoom_x=(0, 86400), zoom_y_l=(-2e-05, 0.0001)), 
Plot(y=["H2Tank.qv_out", "H2Tank.qv_in"], colors=["4278190335", "4294901760"]), 
CreatePlot(id=-1, x_display_unit="s", legend_layout=1, fix_time_range_value=0, sub_plot=(2, 3), zoom_x=(0, 86400), zoom_y_l=(0, 1.2)), 
Plot(y=["H2Tank.SOC"], colors=["4278190335"]), 
CreatePlot(id=-1, x_display_unit="s", legend_layout=1, left_title="[kW]", fix_time_range_value=0, sub_plot=(2, 1), zoom_x=(0, 86400), zoom_y_l=(-0.5, 2)), 
Plot(y=["electricGrid.Pel"], colors=["4278190335"]), 
CreatePlot(id=-1, x_display_unit="s", legend_layout=1, left_title="[kW]", fix_time_range_value=0, sub_plot=(3, 2), zoom_x=(0, 86400), zoom_y_l=(-0.05, 0.35)), 
Plot(y=["PEMFuelCell.Q_gen", "electricBoiler.Ph"], colors=["4278190335", "4294901760"]), 
CreatePlot(id=-1, x_display_unit="s", legend_layout=1, left_title="[kW]", fix_time_range_value=0, sub_plot=(3, 3), zoom_x=(0, 86400), zoom_y_l=(-0.05, 0.35)), 
Plot(y=["boundaryPower2.heat.Ph"], colors=["4278190335"]), 
CreatePlot(id=-1, x_display_unit="s", legend_layout=1, left_title="[m3/s]", fix_time_range_value=0, sub_plot=(3, 1), zoom_x=(0, 86400), zoom_y_l=(-2e-05, 0.0001)), 
Plot(y=["H2Station.qv_flow"], colors=["4278190335"])})
})), Protection(access = Access.nonPackageDuplicate));
  inner TYIntegratedEnergySys.Components.Collectors.CostsCenter costsCenter(calculateCost = false) "经济性计算" 
    annotation(Placement(transformation(origin = {-230.4, 152}, 
    extent = {{-10, -10}, {10, 10}})));
  TYIntegratedEnergySys.Components.Electrical.Inverter inverter(eta = 0.95) "逆变器" 
    annotation(Placement(transformation(origin = {-24.95, 46.1}, 
    extent = {{-10, -10}, {10, 10}})));
  TYIntegratedEnergySys.EnergyStorage.Battery battery(use_P_set = true, SOC_start = 0.5, SOC_min = 0.1, EMax = 4.8e3 * 3600) "蓄电池" 
    annotation(Placement(transformation(origin = {-130.95, 26.1}, 
    extent = {{10, -10}, {-10, 10}})));
  TYIntegratedEnergySys.EnergySource.HydrogenProduction H2Production(useHeatPort = false, eta_nominal = 0.665, Pel_nominal = 7000, usePel_set = true) "电解制氢" 
    annotation(Placement(transformation(origin = {-64.6, -96.5}, 
    extent = {{-10, -10}, {10, 10}})));
  TYIntegratedEnergySys.EnergyStorage.HydrogenTank H2Tank(M_nominal = 1, SOC_min = 0.1, use_gasLoad = true) "储氢罐" 
    annotation(Placement(transformation(origin = {-28.6, -96.5}, 
    extent = {{-10, -10}, {10, 10}})));
  TYIntegratedEnergySys.EnergyTransmission.Busbar DCBar(N_a = 5, N_b = 1) "直流母线" 
    annotation(Placement(transformation(origin = {-76.95, 46.1}, 
    extent = {{-10, -10}, {10, 10}})));
  TYIntegratedEnergySys.EnergyTransmission.Busbar ACBar(N_a = 1, N_b = 2) "交流母线" 
    annotation(Placement(transformation(origin = {-0.95, 46.1}, 
    extent = {{-10, -10}, {10, 10}})));
  TYIntegratedEnergySys.EnergyExchange.Gas2Heat.PEMFuelCell PEMFuelCell(T_cell = 343.15, useFluidPorts = false, I_start = 0) "燃料电池" 
    annotation(Placement(transformation(origin = {35.6, -14.2}, 
    extent = {{-10, -10}, {10, 10}})));
  TYIntegratedEnergySys.EnergyStorage.HeatTank heatTank(useFluidPorts = false, dp_nominal = {100, 100}, m_flow_nominal = {0.1, 0.003}, T_s_max = 343.15, T_s_min = 303.15, T_start_Gen = 343.15, T_start = 323.15) "储热罐" 
    annotation(Placement(transformation(origin = {129.9, -18.2}, 
    extent = {{-10, -10}, {10, 10}})));
  TYIntegratedEnergySys.Boundaries.BoundaryTemperature bound_T "温度边界" 
    annotation(Placement(transformation(origin = {152.75, 16}, 
    extent = {{10, 10}, {-10, -10}})));
  Modelica.Blocks.Sources.CombiTimeTable hotWater(timeScale(displayUnit = "h") = 3600, table = {{0, 0}, {8, 0}, {8, 0.003}, {9, 0.003}, {9, 0}, {12, 0}, {12, 0.003}, {13, 0.003}, {13, 0}, {20, 0}, {20, 0.003}, {22, 0.003}, {22, 0}, {24, 0}}) "热水流量负荷" 
    annotation(Placement(transformation(origin = {256.2, -39.4}, 
    extent = {{10, -10}, {-10, 10}})));
  TYIntegratedEnergySys.Load.ElectricLoad electricLoad(DataType = "负荷数据导入", timeScale(displayUnit = "h") = 3600, LoadData = {{0, 0.25}, {2, 0.24}, {4, 0.24}, {6, 0.25}, {8, 0.3}, {10, 0.23}, {12, 0.34}, {14, 0.35}, {16, 0.18}, {18, 0.45}, {20, 0.58}, {22, 0.55}, {24, 0.3}}) "电功率负荷" 
    annotation(Placement(transformation(origin = {72.05, 91.7}, 
    extent = {{-10, -10}, {10, 10}})));
  TYIntegratedEnergySys.Load.GasLoad gasLoad(DataType = "负荷数据导入", LoadData = {{0, 0}, {17 - 0.0001, 0}, {17, 0.5 / 3600}, {19, 0.5 / 3600}, {19 + 0.0001, 0}, {24, 0}}, LoadDataType = "质量流量输入", timeScale(displayUnit = "h") = 3600) "气负荷" 
    annotation(Placement(transformation(origin = {121.05, -96.5}, 
    extent = {{-10, -10}, {10, 10}})));
  TYIntegratedEnergySys.EnergyTransmission.ElectricGrid electricGrid "电网" 
    annotation(Placement(transformation(origin = {-152.95, 131.5}, 
    extent = {{-10, -10}, {10, 10}})));
  TYIntegratedEnergySys.Environment.Illumination illumination(TAmbInputType = "数据导入", IrradianceInputType = "数据导入", Irradiance_Table = {{0, 0.00}, {3600, 0.00}, {7200, 0.00}, {10800, 2.85}, {14400, 26.37}, {18000, 84.56}, {21600, 166.64}, {25200, 253.11}, {28800, 321.56}, {32400, 370.22}, {36000, 394.68}, {39600, 548.16}, {43200, 527.37}, {46800, 370.10}, {50400, 314.33}, {54000, 239.68}, {57600, 153.24}, {61200, 100.85}, {64800, 42.33}, {68400, 3.80}, {72000, 0.00}, {75600, 0.00}, {79200, 0.00}, {82800, 0.00}, {86400, 0.00}}, TAmb_Table = {{0.0, 23}, {2, 22}, {4, 22}, {6, 22}, {8, 25}, {10, 28}, {12, 30}, {14, 31}, {16, 30}, {18, 28}, {20, 26}, {22, 25}, {24, 23}}, timeScale_TAmb(displayUnit = "h") = 3600) 
    "光照模型" 
    annotation(Placement(transformation(origin = {-192.95, 91.7}, 
    extent = {{-10, -10}, {10, 10}})));
  TYIntegratedEnergySys.EnergySource.PhotovoltaicPower PVPower(N = 100) "光伏发电" 
    annotation(Placement(transformation(origin = {-152.95, 91.8}, 
    extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Sources.CombiTimeTable current(timeScale(displayUnit = "h") = 3600, table = {{0, 0}, {20, 0}, {20, 5}, {22, 5}, {22, 0}, {24, 0}}) "电流" 
    annotation(Placement(transformation(origin = {-18.4, -6.4}, 
    extent = {{-10, -10}, {10, 10}})));
  TYIntegratedEnergySys.Load.HeatLoad boundaryPower2(DataType = "外部信号接入") "功率边界" 
    annotation(Placement(transformation(origin = {159.6, -18.2}, 
    extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Sources.RealExpression delta_T(y = heatTank.T_stor_out - (25 + 273.15)) "温差" 
    annotation(Placement(transformation(origin = {256.2, -13.6}, 
    extent = {{10, -10}, {-10, 10}})));
  Modelica.Blocks.Math.Product product1 annotation(Placement(transformation(origin = {212, -19}, 
    extent = {{9, -9}, {-9, 9}})));
  Modelica.Blocks.Math.Gain gain(k = heatTank.cp) 
    annotation(Placement(transformation(origin = {186.3, -18}, 
    extent = {{7, -7}, {-7, 7}})));
  Modelica.Blocks.Math.Add add(k1 = -1) 
    annotation(Placement(transformation(origin = {129.9, 67.5}, 
    extent = {{10, -10}, {-10, 10}})));
  Modelica.Blocks.Sources.RealExpression FuelCell_Q(y = PEMFuelCell.Q_gen) "燃料电池产热量" 
    annotation(Placement(transformation(origin = {159.6, 73.5}, 
    extent = {{10, -10}, {-10, 10}})));
  TYIntegratedEnergySys.EnergyTransmission.GasGrid gasGrid(N_a = 2, N_b = 2) "气网" 
    annotation(Placement(transformation(origin = {7.4, -96.3}, 
    extent = {{-10, -10}, {10, 10}})));
  TYIntegratedEnergySys.Sensors.Sensor_qv sensor_qv "体积流量传感器" 
    annotation(Placement(transformation(origin = {72.05, -96.5}, 
    extent = {{-10, 10}, {10, -10}})));
  Modelica.Blocks.Math.Add add1 
    annotation(Placement(transformation(origin = {-64.6, -61.9}, 
    extent = {{-10, -10}, {10, 10}})));
  TYIntegratedEnergySys.Sensors.Sensor_qv sensor_qv1 "体积流量传感器" 
    annotation(Placement(transformation(origin = {17.6, -46.5}, 
    extent = {{-10, 10}, {10, -10}}, 
    rotation = 90)));
  TYIntegratedEnergySys.Boundaries.BoundaryGas H2Station(use_qv_in = false, Type = "根据负荷计算所需流量") "氢气源" 
    annotation(Placement(transformation(origin = {-28.6, -132}, 
    extent = {{-10, -10}, {10, 10}})));
  TYIntegratedEnergySys.Sensors.Sensor_P sensor_Pload "功率传感器" 
    annotation(Placement(transformation(origin = {-50.95, 46.1}, 
    extent = {{-10, -10}, {10, 10}})));
  TYIntegratedEnergySys.Components.Electrical.Rectifier rectifier(eta = 1) "整流器" 
    annotation(Placement(transformation(origin = {-122.95, 131.5}, 
    extent = {{-10, -10}, {10, 10}})));
  TYIntegratedEnergySys.Controllers.PowerController_Battery powerController_Battery(SOC_max = battery.SOC_max, SOC_min = battery.SOC_min) "蓄电池充放电控制器" 
    annotation(Placement(transformation(origin = {-190.675, 46.1}, 
    extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Sources.RealExpression P_load(y = sensor_Pload.P) "需求功率" 
    annotation(Placement(transformation(origin = {-230.4, 33.75}, 
    extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Sources.RealExpression P_produce(y = PVPower.Pel + sensor_FC.P) "生产功率" 
    annotation(Placement(transformation(origin = {-230.4, 50.37}, 
    extent = {{-10, -10}, {10, 10}})));
  TYIntegratedEnergySys.EnergyExchange.Electric2Heat.ElectricBoiler electricBoiler(useFluidPorts = false, ModeType1 = "设定输出功率") "电锅炉" 
    annotation(Placement(transformation(origin = {57.6, 47.7}, 
    extent = {{-10, -10}, {10, 10}})));
  TYIntegratedEnergySys.EnergyTransmission.HeatGrid heatGrid(N_a = 2) "热网" 
    annotation(Placement(transformation(origin = {89.6, -18.4}, 
    extent = {{-10, -10}, {10, 10}})));
  TYIntegratedEnergySys.Sensors.Sensor_P sensor_FC 
    annotation(Placement(transformation(origin = {-60, 10}, 
    extent = {{10, -10}, {-10, 10}})));
  TYIntegratedEnergySys.Controllers.Control_SOC SOCControl(ControlH2Tank = true, SOC_max = H2Tank.SOC_max, SOC_min = H2Tank.SOC_min) 
    annotation(Placement(transformation(origin = {-112, -88.7}, 
    extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Sources.RealExpression H2Tank_SOC(y = H2Tank.SOC) "储氢罐SOC" 
    annotation(Placement(transformation(origin = {-170, -83.6}, 
    extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Sources.RealExpression H2Tank_qv(y = H2Tank.qv_out) "储氢罐出口质量流量" 
    annotation(Placement(transformation(origin = {-170, -108}, 
    extent = {{-10, -10}, {10, 10}})));
  TYIntegratedEnergySys.Controllers.Control_BatteryH2Tank control_BatteryH2Tank 
    annotation(Placement(transformation(origin = {-140, -18.4}, 
    extent = {{-10, -10}, {10, 10}})));
equation
  connect(H2Production.gas, H2Tank.gas_a) 
    annotation(Line(origin = {63.4, -110.9}, 
    points = {{-117.6, 14.5}, {-102, 14.5}, {-102, 14.4}}, 
    color = {0, 209, 209}));
  connect(heatTank.heatport, bound_T.port[1]) 
    annotation(Line(origin = {169.2, -16.6}, 
    points = {{-39.3, 8.6}, {-39.3, 32.6}, {-26.45, 32.6}}, 
    color = {191, 0, 0}));
  connect(gasGrid.gas_b[2], sensor_qv1.gas_a) 
    annotation(Line(origin = {-17.15, -44.9}, 
    points = {{34.95, -51.4}, {34.95, -10.1}, {34.65, -10.1}}, 
    color = {0, 209, 209}));
  connect(illumination.Irradiance, PVPower.Irradiance) 
    annotation(Line(origin = {-172.95, 88.9}, 
    points = {{-9.4, -0.2}, {9.8, -0.2}, {9.8, 0.1}}, 
    color = {0, 0, 127}));
  connect(illumination.TAmbient, PVPower.TAmbient) 
    annotation(Line(origin = {-172.95, 94.9}, 
    points = {{-9.4, -0.1}, {9.8, -0.1}}, 
    color = {0, 0, 127}));
  connect(PEMFuelCell.heat, heatGrid.heat_a[1]) 
    annotation(Line(origin = {61.05, -30.9}, 
    points = {{-15.45, 12.7}, {18.55, 12.7}}, 
    color = {191, 0, 0}));
  connect(gain.u, product1.y) 
    annotation(Line(origin = {271.45, -31.4}, 
    points = {{-76.75, 13.4}, {-69.35, 13.4}, {-69.35, 12.4}}, 
    color = {0, 0, 127}));
  connect(product1.u1, delta_T.y) 
    annotation(Line(origin = {274.8, -12.8066}, 
    points = {{-52, -0.7934}, {-29.6, -0.7934}}, 
    color = {0, 0, 127}));
  connect(hotWater.y[1], product1.u2) 
    annotation(Line(origin = {278.8, -37}, 
    points = {{-33.6, -2.4}, {-56, -2.4}, {-56, 12.6}}, 
    color = {0, 0, 127}));
  connect(heatTank.heat_Consumer, boundaryPower2.heat) 
    annotation(Line(origin = {160.2, -18.4}, 
    points = {{-20.1, 0.4}, {-10.6, 0.4}, {-10.6, 0.2}}, 
    color = {191, 0, 0}));
  connect(gain.y, add.u2) 
    annotation(Line(origin = {112.05, -40.7}, 
    points = {{66.55, 22.7}, {66.55, 102.2}, {29.85, 102.2}}, 
    color = {0, 0, 127}));
  connect(gasGrid.gas_b[1], sensor_qv.gas_a) 
    annotation(Line(origin = {37.6, -113.3}, 
    points = {{-19.8, 17}, {25.95, 17}, {25.95, 16.9}}, 
    color = {0, 209, 209}));
  connect(H2Tank.gas_b, gasGrid.gas_a[1]) 
    annotation(Line(origin = {-2.4, -109.3}, 
    points = {{-16, 12.8}, {-0.6, 12.8}}, 
    color = {0, 209, 209}));
  connect(sensor_qv.gas_b, gasLoad.gas) 
    annotation(Line(origin = {95.6, -96.5}, 
    points = {{-14.55, 0}, {15.45, 0}}, 
    color = {0, 209, 209}));
  connect(sensor_qv.qv_flow, add1.u2) 
    annotation(Line(origin = {-2.4, -78.5}, 
    points = {{74.45, -8.4}, {74.45, 2}, {-86, 2}, {-86, 10.6}, {-74.2, 10.6}}, 
    color = {0, 0, 127}));
  connect(sensor_qv1.gas_b, PEMFuelCell.gas) 
    annotation(Line(origin = {-7.4, -28.5}, 
    points = {{25, -9}, {25, 14.1}, {33, 14.1}}, 
    color = {0, 209, 209}));
  connect(H2Station.gas, gasGrid.gas_a[2]) 
    annotation(Line(origin = {-3.4, -114.5}, 
    points = {{-15.2, -17.5}, {-5, -17.5}, {-5, 18}, {0.4, 18}}, 
    color = {0, 209, 209}));
  connect(sensor_qv1.qv_flow, add1.u1) 
    annotation(Line(origin = {-49.4, -54.5}, 
    points = {{57.4, 8}, {-39, 8}, {-39, -1.4}, {-27.2, -1.4}}, 
    color = {0, 0, 127}));
  connect(add.u1, FuelCell_Q.y) 
    annotation(Line(origin = {147.9, 52.0998}, 
    points = {{-6, 21.4002}, {0.7, 21.4002}}, 
    color = {0, 0, 127}));
  connect(PVPower.electric, DCBar.electric_a[1]) 
    annotation(Line(origin = {-108.4, 71.5}, 
    points = {{-34.35, 20.3}, {10, 20.3}, {10, -25.2}, {28.85, -25.2}}, 
    color = {16, 99, 16}));
  connect(battery.electric, DCBar.electric_a[2]) 
    annotation(Line(origin = {-97.4, 35.5}, 
    points = {{-23.55, -9.4}, {-1, -9.4}, {-1, 10.8}, {17.85, 10.8}}, 
    color = {16, 99, 16}));
  connect(H2Production.electric, DCBar.electric_a[3]) 
    annotation(Line(origin = {-74.4, -25.5}, 
    points = {{-0.2, -71}, {-24, -71}, {-24, 71.8}, {-5.15, 71.8}}, 
    color = {16, 99, 16}));
  connect(sensor_FC.electric_a, PEMFuelCell.electric) 
    annotation(Line(origin = {-34.4, 18.5}, 
    points = {{-16.8, -8.5}, {88, -8.5}, {88, -28.7}, {80, -28.7}}, 
    color = {16, 99, 16}));
  connect(rectifier.electric_DC, DCBar.electric_a[5]) 
    annotation(Line(origin={-54.4,71.5}, 
points={{-58.35,60},{-44,60},{-44,-25.2},{-25.15,-25.2}}, 
color={16,99,16}));
  connect(electricGrid.electric, rectifier.electric_AC) 
    annotation(Line(origin={-134.4,131.5}, 
points={{-8.55,0.1},{1.45,0}}, 
color={16,99,16}));
  connect(DCBar.electric_b[1], sensor_Pload.electric_a) 
    annotation(Line(origin = {-63.4, 46.5}, 
    points = {{-10.15, -0.2}, {3.65, -0.2}, {3.65, -0.4}}, 
    color = {16, 99, 16}));
  connect(sensor_Pload.electric_b, inverter.electric_DC) 
    annotation(Line(origin = {-38.4, 46.5}, 
    points = {{-3.55, -0.4}, {3.45, -0.4}}, 
    color = {16, 99, 16}));
  connect(inverter.electric_AC, ACBar.electric_a[1]) 
    annotation(Line(origin = {-9.4, 46.5}, 
    points = {{-5.35, -0.4}, {5.85, -0.4}, {5.85, -0.2}}, 
    color = {16, 99, 16}));
  connect(ACBar.electric_b[1], electricLoad.electric) 
    annotation(Line(origin = {32.6, 68.5}, 
    points = {{-30.15, -22.2}, {-13, -22.2}, {-13, 23.2}, {29.45, 23.2}}, 
    color = {16, 99, 16}));
  connect(P_load.y, powerController_Battery.P_demand) 
    annotation(Line(origin = {-230.4, 29.5}, 
    points = {{11, 4.25}, {29.925, 4.25}, {29.925, 12.25}}, 
    color = {0, 0, 127}));
  connect(battery.SOC, powerController_Battery.SOC) 
    annotation(Line(origin = {-167.4, 43.5}, 
    points = {{25.65, -13.17194}, {7.4, -13.17194}, {7.4, 24}, {-23.225, 24}, {-23.225, 13.4}}, 
    color = {0, 0, 127}));
  connect(electricBoiler.heat, heatGrid.heat_a[2]) 
    annotation(Line(origin = {75.6, -13.5}, 
    points = {{-8, 61.2}, {0, 61.2}, {0, -4.7}, {4, -4.7}}, 
    color = {191, 0, 0}));
  connect(electricBoiler.P_set, add.y) 
    annotation(Line(origin = {71.6, 26.5}, 
    points = {{-24.2, 24.8}, {-36, 24.8}, {-36, 41}, {47.3, 41}}, 
    color = {0, 0, 127}));
  connect(ACBar.electric_b[2], electricBoiler.electric) 
    annotation(Line(origin = {30.6, 32.5}, 
    points = {{-28.15, 13.8}, {17, 13.8}, {17, 15.2}}, 
    color = {16, 99, 16}));
  connect(heatGrid.heat_b[1], heatTank.heat_Gen) 
    annotation(Line(origin = {109.6, -18.5}, 
    points = {{-10, 0.1}, {10.5, 0.1}, {10.5, 0.5}}, 
    color = {191, 0, 0}));
  connect(current.y[1], PEMFuelCell.I) 
    annotation(Line(origin = {9, -6}, 
    points = {{-16.4, -0.4}, {16, -0.4}, {16, -0.4}}, 
    color = {0, 0, 127}));
  connect(boundaryPower2.Ph_input, gain.y) 
    annotation(Line(origin = {174, -18}, 
    points = {{-3.8, -0.2}, {4.6, -0.2}, {4.6, 0}}, 
    color = {0, 0, 127}));
  connect(P_produce.y, powerController_Battery.P_produce) 
    annotation(Line(origin = {-210, 50}, 
    points = {{-9.4, 0.37}, {9.525, 0.37}, {9.525, 0.37}}, 
    color = {0, 0, 127}));
  connect(sensor_FC.electric_b, DCBar.electric_a[4]) 
    annotation(Line(origin = {-74, 28}, 
    points = {{5, -18}, {-16, -18}, {-16, 18.3}, {-5.55, 18.3}}, 
    color = {16, 99, 16}));
  connect(add1.y, H2Tank.qv_out_set) 
    annotation(Line(origin = {-46, -76}, 
    points = {{-7.6, 14.1}, {4, 14.1}, {4, -14.3}, {6.8, -14.3}}, 
    color = {0, 0, 127}));
  connect(H2Tank_SOC.y, SOCControl.SOC) 
    annotation(Line(origin = {-142, -65}, 
    points = {{-17, -18.6}, {19.2, -18.6}, {19.2, -18.6}}, 
    color = {0, 0, 127}));
  connect(H2Tank_qv.y, SOCControl.qv_out) 
    annotation(Line(origin = {-141, -98}, 
    points = {{-18, -10}, {-9, -10}, {-9, 9.3}, {18, 9.3}}, 
    color = {0, 0, 127}));
  connect(powerController_Battery.Pel, battery.P_set) 
    annotation(Line(origin = {-150, 38}, 
    points = {{-29.875, 8.6}, {40, 8.6}, {40, -7.61491}, {29.907, -7.61491}}, 
    color = {0, 0, 127}));
  connect(powerController_Battery.Pel_surplus, control_BatteryH2Tank.Pel) 
    annotation(Line(origin = {-159, -29}, 
    points = {{-35.275, 64.5}, {-35.275, 10.7}, {8.3, 10.7}}, 
    color = {0, 0, 127}));
  connect(battery.SOC, control_BatteryH2Tank.SOC_Battery) 
    annotation(Line(origin = {-140, 9}, 
    points = {{-1.75, 21.32806}, {-20, 21.32806}, {-20, -20.9}, {-10.7, -20.9}}, 
    color = {0, 0, 127}));
  connect(H2Tank_SOC.y, control_BatteryH2Tank.SOC_H2Tank) 
    annotation(Line(origin={-160,-54}, 
points={{1,-29.6},{4,-29.6},{4,30.1},{8,30.1}}, 
color={0,0,127}));
  connect(control_BatteryH2Tank.Pel_H2Production, SOCControl.u) 
    annotation(Line(origin = {-126, -58}, 
    points = {{-3.4, 35.7}, {-3.4, -35.4}, {3.2, -35.4}}, 
    color = {0, 0, 127}));
  connect(SOCControl.y, H2Production.P_el_set) 
    annotation(Line(origin = {-88, -89}, 
    points = {{-13.4, 0.1}, {12.6, 0.1}}, 
    color = {0, 0, 127}));
end PVFuelCellCogenerationSys;