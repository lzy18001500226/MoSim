model BoilerHeatingSys "锅炉制热系统"
  annotation(Documentation(link = "modelica://TYIntegratedEnergySys/Resources/HTML/BoilerHeatingSys.html"),Icon(coordinateSystem(extent = {{-100, -100}, {100, 100}}, 
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
</html>"    ), experiment(Algorithm = Dassl, InlineIntegrator = false, InlineStepSize = false, Interval = 1, StartTime = 0, StopTime = 86400, Tolerance = 0.0001), __MWORKS(ContinueSimConfig(SaveContinueFile = "false", SaveBeforeStop = "false", NumberBeforeStop = 1, FixedContinueInterval = "false", ContinueIntervalLength = 86400, ContinueTimeVector),ResultViewerManager(resultViewers={
ResultViewer(name="1", executeTrigger=executeTrigger.SimulationFinished, commands={
CreatePlot(id=2, x_display_unit="s", legend_layout=1, left_title_type=2, left_title="功率[kW]", bottom_title_type=2, bottom_title="时间/s", right_title_type=2, fix_time_range_value=0, zoom_x=(0, 86400), zoom_y_l=(40, 160)), 
Plot(legend=["热负荷 [kW]"], y=["heatLoad.Ph"], colors=["4278190335"]), 
CreatePlot(id=-1, x_display_unit="s", legend_layout=1, left_title_type=2, left_title="质量流量/[kg/s]", bottom_title_type=2, bottom_title="时间/s", right_title_type=2, fix_time_range_value=0, sub_plot=(1, 2), zoom_x=(0, 86400), zoom_y_l=(0.2, 0.9)), 
Plot(legend=["热水质量流量 [kg/s]"], y=["massFlowRateController1.m_flow"], colors=["4278190335"]), 
CreatePlot(id=-1, x_display_unit="s", legend_layout=1, left_title_type=2, left_title="体积流量[m3/s]", bottom_title_type=2, bottom_title="时间/s", right_title_type=2, fix_time_range_value=0, sub_plot=(2, 2), zoom_x=(0, 86400), zoom_y_l=(0.002, 0.0055)), 
Plot(legend=["天然气流量 [m3/s]"], y=["boundaryGas.qv_flow"], colors=["4278190335"]), 
CreatePlot(id=-1, x_display_unit="s", legend_layout=1, left_title_type=2, left_title="功率[kW]", bottom_title_type=2, bottom_title="时间/s", right_title_type=2, fix_time_range_value=0, sub_plot=(2, 1), zoom_x=(0, 86400), zoom_y_l=(20, 80)), 
Plot(legend=["余热锅炉制热功率 [kW]", "燃气锅炉制热功率 [kW]"], y=["heatRecoveryBoiler.Ph_out", "gasBoiler.Ph"], colors=["4278190335", "4294901760"])})
})),Protection(access=Access.nonPackageDuplicate));
  TYIntegratedEnergySys.Boundaries.BoundaryGas boundaryGas(use_qv_in = false, Type = "根据负荷计算所需流量") "气源" 
    annotation(Placement(transformation(origin = {-170, 66.2}, 
    extent = {{-10, -10}, {10, 10}})));
  TYIntegratedEnergySys.EnergyExchange.Gas2Heat.GasTurbine GT(Pel_nominal(displayUnit = "kW") = 100000, m_inv = 0.052, f_gt_min = 0.1, Type = "输入热负荷计算所需流量") "燃气轮机" 
    annotation(Placement(transformation(origin = {-75.4, 66.2}, 
    extent = {{-10, -10}, {10, 10}})));
  TYIntegratedEnergySys.Sensors.Sensor_P sensor_Ph1(PortType = "heat") "功率传感器" 
    annotation(Placement(transformation(origin = {-5.4, 62}, 
    extent = {{-10, -10}, {10, 10}})));
  TYIntegratedEnergySys.Load.HeatLoad heatLoad(DataType = "负荷数据导入", timeScale(displayUnit = "h") = 3600, LoadData = {{0.0, 125}, {1, 120}, {2, 122}, {3, 124}, {4, 125}, {5, 118}, {6, 110}, {7, 95}, {8, 90}, {9, 87}, {10, 85}, {11, 80}, {12, 75}, {13, 61}, {14, 55}, {15, 62}, {16, 76}, {17, 92}, {18, 110}, {19, 126}, {20, 130}, {21, 150}, {22, 143}, {23, 134}, {24, 126}}, Ph_constant = 0) "热负荷" 
    annotation(Placement(transformation(origin = {218, -1}, 
    extent = {{-10, -10}, {10, 10}})));
  TYIntegratedEnergySys.EnergyExchange.Heat2Heat.HeatRecoveryBoiler heatRecoveryBoiler(ModeType = "输入锅炉出口水温", Q_flow_nominal(displayUnit = "kW") = 100000, redeclare package Medium = Modelica.Media.Water.ConstantPropertyLiquidWater) "余热锅炉" 
    annotation(Placement(transformation(origin = {62, 38}, 
    extent = {{-10, -10}, {10, 10}})));
  TYIntegratedEnergySys.Boundaries.BoundaryTemperature bound_T(T = 303.15) "温度边界" 
    annotation(Placement(transformation(origin = {174, 42}, 
    extent = {{10, -10}, {-10, 10}})));
  TYIntegratedEnergySys.Boundaries.BoundaryMdot bound_mflow(use_mflow_in = true, redeclare package Medium = Modelica.Media.Water.ConstantPropertyLiquidWater) "质量流量边界" 
    annotation(Placement(transformation(origin = {32, 15.2}, 
    extent = {{-10, -10}, {10, 10}})));
  TYIntegratedEnergySys.Boundaries.BoundaryPressure bound_p(p = 3e5, redeclare package Medium = Modelica.Media.Water.ConstantPropertyLiquidWater) "压力边界" 
    annotation(Placement(transformation(origin = {64.6, -0.8}, 
    extent = {{-10, -10}, {10, 10}}, 
    rotation = 90)));
  TYIntegratedEnergySys.EnergyTransmission.HeatGrid heatGrid(N_a = 3, N_b = 2) "热网" 
    annotation(Placement(transformation(origin = {107, -0.8}, 
    extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Sources.RealExpression T_set1(y = 70 + 273.15) "温度设定" 
    annotation(Placement(transformation(origin = {22, 43}, 
    extent = {{-10, -10}, {10, 10}})));
  TYIntegratedEnergySys.Controllers.MassFlowRateController massFlowRateController1 "质量流量控制器" 
    annotation(Placement(transformation(origin = {-42.8, 21}, 
    extent = {{-10, 10}, {10, -10}})));
  Modelica.Blocks.Sources.RealExpression dT_Boiler(y = 70 - 25) "锅炉温差" 
    annotation(Placement(transformation(origin = {-92, 25.2}, 
    extent = {{-10, -10}, {10, 10}})));
  TYIntegratedEnergySys.EnergyExchange.Gas2Heat.GasBoiler gasBoiler(ModeType = "输入锅炉出口水温", Q_flow_nominal(displayUnit = "kW") = 2e5, redeclare package Medium = Modelica.Media.Water.ConstantPropertyLiquidWater) "燃气锅炉" 
    annotation(Placement(transformation(origin = {62, -58}, 
    extent = {{-10, -10}, {10, 10}})));
  TYIntegratedEnergySys.Boundaries.BoundaryTemperature bound_T1(T = 303.15) "温度边界" 
    annotation(Placement(transformation(origin = {118, -54}, 
    extent = {{10, -10}, {-10, 10}})));
  TYIntegratedEnergySys.Boundaries.BoundaryMdot bound_mflow1(use_mflow_in = true, redeclare package Medium = Modelica.Media.Water.ConstantPropertyLiquidWater) "质量流量边界" 
    annotation(Placement(transformation(origin = {39.2, -86}, 
    extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Sources.RealExpression T_set2(y = 70 + 273.15) "温度设定" 
    annotation(Placement(transformation(origin = {22, -50.8}, 
    extent = {{-10, -10}, {10, 10}})));
  TYIntegratedEnergySys.Boundaries.BoundaryPressure bound_p1(p = 3e5, redeclare package Medium = Modelica.Media.Water.ConstantPropertyLiquidWater) "压力边界" 
    annotation(Placement(transformation(origin = {64.6, -102}, 
    extent = {{-10, -10}, {10, 10}}, 
    rotation = 90)));
  TYIntegratedEnergySys.EnergyStorage.HeatTank heatTank(useFluidPorts = false, T_start = 343.15, T_s_max = 353.15) "储热罐" 
    annotation(Placement(transformation(origin = {149.4, -1}, 
    extent = {{-10, -10}, {10, 10}})));
  TYIntegratedEnergySys.Boundaries.BoundaryPower powerSource1(SetPower = false, PortType = "electric") "功率边界" 
    annotation(Placement(transformation(origin = {2, 90}, 
    extent = {{10, -10}, {-10, 10}})));
  TYIntegratedEnergySys.Sensors.Sensor_P sensor_Ph(PortType = "heat") "功率传感器" 
    annotation(Placement(transformation(origin = {184.85, -1}, 
    extent = {{-10, -10}, {10, 10}})));
  TYIntegratedEnergySys.EnergyTransmission.GasGrid gasGrid(N_b = 2) 
    annotation(Placement(transformation(origin = {-131.4, 66.2}, 
    extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Math.Gain gain(k = 0.5) "热负荷分配" 
    annotation(Placement(transformation(origin = {2, -80}, 
    extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Math.Gain gain1(k = 0.5) "热负荷分配" 
    annotation(Placement(transformation(origin = {-5.4, 21.45}, 
    extent = {{-10, -10}, {10, 10}})));
equation
  connect(gasGrid.gas_b[1], GT.gas) 
    annotation(Line(origin = {-80.4, 66.2}, 
    points = {{-40.6, 0}, {-5, 0}}, 
    color = {0, 209, 209}));
  connect(heatRecoveryBoiler.heatport, bound_T.port[1]) 
    annotation(Line(origin = {76.4, 98.2}, 
    points = {{-4.4, -56.2}, {87.6, -56.2}}, 
    color = {191, 0, 0}));
  connect(sensor_Ph1.heat_b, heatRecoveryBoiler.heat_in) 
    annotation(Line(origin={40,43}, 
points={{-36.4,19},{0,19},{0,-10},{12,-10}}, 
color={191,0,0}));
  connect(bound_mflow.fluidPort, heatRecoveryBoiler.port_a) 
    annotation(Line(origin = {49.4, 21.2}, 
    points = {{-9.4, -6}, {10, -6}, {10, 6.6}}, 
    color = {0, 127, 255}));
  connect(heatRecoveryBoiler.port_b, bound_p.port_b) 
    annotation(Line(origin = {62.4, 17.2}, 
    points = {{2.2, 10.6}, {2.2, -10}}, 
    color = {0, 127, 255}));
  connect(heatRecoveryBoiler.heat_out, heatGrid.heat_a[1]) 
    annotation(Line(origin = {87.4, 16.2}, 
    points = {{-15.4, 16.8}, {-8, 16.8}, {-8, -16.8}, {9.6, -16.8}}, 
    color = {191, 0, 0}));
  connect(heatRecoveryBoiler.T_set, T_set1.y) 
    annotation(Line(origin = {32.4, 119.2}, 
    points = {{19.6, -76.2}, {0.6, -76.2}}, 
    color = {0, 0, 127}));
  connect(gain1.u, massFlowRateController1.m_flow) 
    annotation(Line(origin = {5.4, 23.2}, 
    points = {{-22.8, -1.75}, {-37.8, -1.75}}, 
    color = {0, 0, 127}));
  connect(dT_Boiler.y, massFlowRateController1.dT) 
    annotation(Line(origin = {-108.6, 14.1}, 
    points = {{27.6, 11.1}, {55.4, 11.1}}, 
    color = {0, 0, 127}));
  connect(gasBoiler.gas, gasGrid.gas_b[2]) 
    annotation(Line(origin = {-104, 8}, 
    points = {{156, -66}, {-8, -66}, {-8, 58.2}, {-17, 58.2}}, 
    color = {0, 209, 209}));
  connect(gasBoiler.heatport, bound_T1.port[1]) 
    annotation(Line(origin = {57.2, -58}, 
    points = {{14.8, 4}, {50.8, 4}}, 
    color = {191, 0, 0}));
  connect(bound_mflow1.fluidPort, gasBoiler.port_a) 
    annotation(Line(origin = {52.2, -77}, 
    points = {{-5, -9}, {7.2, -9}, {7.2, 8.8}}, 
    color = {0, 127, 255}));
  connect(T_set2.y, gasBoiler.T_set) 
    annotation(Line(origin = {-17, -47}, 
    points = {{50, -3.8}, {69, -3.8}, {69, -6}}, 
    color = {0, 0, 127}));
  connect(bound_p1.port_b, gasBoiler.port_b) 
    annotation(Line(origin = {99, -84.8}, 
    points = {{-34.4, -9.2}, {-34.4, 16.6}}, 
    color = {0, 127, 255}));
  connect(bound_T.port[1], heatTank.heatport) 
    annotation(Line(origin = {134.4, 8.2}, 
    points = {{29.6, 33.8}, {15, 33.8}, {15, 1}}, 
    color = {191, 0, 0}));
  connect(heatGrid.heat_b[1], heatTank.heat_Gen) 
    annotation(Line(origin = {155.4, -0.8}, 
    points = {{-38.4, 0}, {-15.8, 0}}, 
    color = {191, 0, 0}));
  connect(gasBoiler.heat, heatGrid.heat_a[2]) 
    annotation(Line(origin = {68, -18}, 
    points = {{4, -40}, {29, -40}, {29, 17.4}}, 
    color = {191, 0, 0}));
  connect(GT.electric, powerSource1.electric) 
    annotation(Line(origin = {-19.4, 84.8}, 
    points = {{-46, -15.6}, {-16, -15.6}, {-16, 5.2}, {11.2, 5.2}}, 
    color = {16, 99, 16}));
  connect(heatLoad.heat, sensor_Ph.heat_b) 
    annotation(Line(origin = {180.3, -1}, 
    points = {{27.7, 0}, {13.55, 0}}, 
    color = {191, 0, 0}));
  connect(heatTank.heat_Consumer, sensor_Ph.heat_a) 
    annotation(Line(origin = {173, -17}, 
    points = {{-13.4, 16.2}, {3.05, 16.2}, {3.05, 16}}, 
    color = {191, 0, 0}));
  connect(sensor_Ph.P, massFlowRateController1.Q_demand) 
    annotation(Line(origin = {71, -11.8}, 
    points = {{113.85, 1.2}, {113.85, -22}, {-147, -22}, {-147, 27.8}, {-124.2, 27.8}}, 
    color = {0, 0, 127}));
  connect(boundaryGas.gas, gasGrid.gas_a[1]) 
    annotation(Line(origin = {-159.4, 66.2}, 
    points = {{-0.6, 0}, {17.6, 0}, {17.6, -0.2}}, 
    color = {0, 209, 209}));
  connect(gain1.y, bound_mflow.mflow_in) 
    annotation(Line(origin = {13, 21}, 
    points = {{-7.4, 0.45}, {8, 0.45}, {8, 0.2}}, 
    color = {0, 0, 127}));
  connect(bound_mflow1.mflow_in, gain.y) 
    annotation(Line(origin = {21, -80}, 
    points = {{7.2, 0}, {-8, 0}}, 
    color = {0, 0, 127}));
  connect(massFlowRateController1.m_flow, gain.u) 
    annotation(Line(origin = {-49, -24}, 
    points = {{16.8, 45.45}, {23, 45.45}, {23, -56}, {39, -56}}, 
    color = {0, 0, 127}));
  connect(GT.heat, sensor_Ph1.heat_a) 
    annotation(Line(origin={-23.4,61.8}, 
points={{-42,0.2},{9.2,0.2}}, 
color={191,0,0}));
  end BoilerHeatingSys;