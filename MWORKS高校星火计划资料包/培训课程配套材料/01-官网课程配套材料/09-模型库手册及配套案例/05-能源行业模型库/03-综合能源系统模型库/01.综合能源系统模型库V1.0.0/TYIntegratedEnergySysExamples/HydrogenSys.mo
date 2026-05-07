model HydrogenSys "制氢储氢系统"
  annotation(Documentation(link = "modelica://TYIntegratedEnergySys/Resources/HTML/HydrogenSys.html"), Icon(coordinateSystem(extent = {{-100.0, -100.0}, {100.0, 100.0}}, 
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
    thickness = 5.0)}), Diagram(coordinateSystem(extent = {{-100, -100}, {100, 100}}, 
    grid = {2, 2})), experiment(Algorithm = Dassl, InlineIntegrator = false, InlineStepSize = false, Interval = 1, StartTime = 0, StopTime = 21600, Tolerance = 0.0001), __MWORKS(ContinueSimConfig(SaveContinueFile = "false", SaveBeforeStop = "false", NumberBeforeStop = 1, FixedContinueInterval = "false", ContinueIntervalLength = 219, ContinueTimeVector),ResultViewerManager(resultViewers={
ResultViewer(name="1", executeTrigger=executeTrigger.SimulationFinished, commands={
CreatePlot(id=1, x_display_unit="s", legend_layout=1, left_title_type=2, left_title="体积流量/[m3/s]", bottom_title_type=2, bottom_title="时间/s", right_title_type=2, fix_time_range_value=0, zoom_x=(0, 21600), zoom_y_l=(-2e-06, 1.2e-05)), 
Plot(legend=["储氢罐进口流量 [m3/s]"], y=["H2Tank.qv_in"], colors=["4278190335"]), 
CreatePlot(id=-1, x_display_unit="s", legend_layout=1, left_title_type=2, left_title="体积流量[m3/s]", bottom_title_type=2, bottom_title="时间/s", fix_time_range_value=0, sub_plot=(1, 2), zoom_x=(0, 21600), zoom_y_l=(-2e-05, 0.00012)), 
Plot(legend=["储氢罐出口流量 [m3/s]"], y=["H2Tank.qv_out"], colors=["4278190335"]), 
CreatePlot(id=-1, x_display_unit="s", legend_layout=1, left_title_type=2, left_title="体积流量/[m3/s]", bottom_title_type=2, bottom_title="时间/s", fix_time_range_value=0, sub_plot=(2, 2), zoom_x=(0, 21600), zoom_y_l=(-2e-05, 0.00012)), 
Plot(legend=["氢气总负荷 [m3/s]", "氢气源补充流量 [m3/s]"], y=["add.y", "boundaryGas.qv_flow"], colors=["4278190335", "4294901760"]), 
CreatePlot(id=-1, x_display_unit="s", legend_layout=1, left_title_type=2, left_title="SOC", bottom_title_type=2, bottom_title="时间/s", fix_time_range_value=0, sub_plot=(2, 1), zoom_x=(0, 21600), zoom_y_l=(0, 1.2)), 
Plot(legend=["储氢罐SOC"], y=["H2Tank.SOC"], colors=["4278190335"])})
})), Protection(access = Access.nonPackageDuplicate));
  TYIntegratedEnergySys.EnergySource.HydrogenProduction H2Production(useHeatPort = false, eta_nominal = 0.665, Pel_nominal = 7000, usePel_set = true) "电解制氢系统" 
    annotation(Placement(transformation(origin = {-60, -34}, 
    extent = {{-10, -10}, {10, 10}})));
  TYIntegratedEnergySys.EnergyStorage.HydrogenTank H2Tank(M_nominal = 1, SOC_min = 0.1, use_gasLoad = true, SOC_start = 0.9) "储氢罐" 
    annotation(Placement(transformation(origin = {-14, -34.2}, 
    extent = {{-10, -10}, {10, 10}})));
  TYIntegratedEnergySys.EnergyExchange.Gas2Heat.PEMFuelCell PEMFuelCell(T_cell = 343.15, useFluidPorts = false) "燃料电池" 
    annotation(Placement(transformation(origin = {46, 54}, 
    extent = {{-10, -10}, {10, 10}})));
  TYIntegratedEnergySys.Controllers.Control_SOC SOCControl(SOC_max = H2Tank.SOC_max, SOC_min = H2Tank.SOC_min, ControlH2Tank = true) "SOC控制器" 
    annotation(Placement(transformation(origin = {-102, 8.8}, 
    extent = {{-10, 10}, {10, -10}})));
  Modelica.Blocks.Sources.CombiTimeTable Pel(timeScale(displayUnit = "h") = 3600, table = {{0.0, 3e3}, {3, 3e3}, {3, 0}}) "电功率输入" 
    annotation(Placement(transformation(origin = {-150, 13.5}, 
    extent = {{-10, -10}, {10, 10}})));
  TYIntegratedEnergySys.Load.GasLoad gasLoad(DataType = "负荷数据导入", timeScale(displayUnit = "h") = 3600, LoadData = {{0.0, 0}, {4, 0}, {4, 1e-4}, {6, 1e-4}}) "气负荷" 
    annotation(Placement(transformation(origin = {122, -34.2}, 
    extent = {{-10, -10}, {10, 10}})));
  TYIntegratedEnergySys.Boundaries.BoundaryPower boundaryPower1(SetPower = false) "功率边界" 
    annotation(Placement(transformation(origin = {92, 58}, 
    extent = {{10, -10}, {-10, 10}})));
  TYIntegratedEnergySys.Boundaries.BoundaryPower boundaryPower2(SetPower = false, PortType = "heat") "功率边界" 
    annotation(Placement(transformation(origin = {92, 30}, 
    extent = {{10, -10}, {-10, 10}})));
  TYIntegratedEnergySys.Boundaries.BoundaryGas boundaryGas(use_qv_in = false, Type = "根据负荷计算所需流量") "氢气源" 
    annotation(Placement(transformation(origin = {-14, -66}, 
    extent = {{-10, -10}, {10, 10}})));
  TYIntegratedEnergySys.EnergyTransmission.GasGrid gasGrid(N_a = 2, N_b = 2) "气网" 
    annotation(Placement(transformation(origin = {46, -34.2}, 
    extent = {{-10, -10}, {10, 10}})));
  TYIntegratedEnergySys.Sensors.Sensor_qv sensor_qv "体积流量传感器" 
    annotation(Placement(transformation(origin = {92, -34.1}, 
    extent = {{-10, 10}, {10, -10}})));
  TYIntegratedEnergySys.Sensors.Sensor_qv sensor_qv1 "体积流量传感器" 
    annotation(Placement(transformation(origin = {20, 32}, 
    extent = {{-10, 10}, {10, -10}}, 
    rotation = 90)));
  Modelica.Blocks.Math.Add add 
    annotation(Placement(transformation(origin = {-43, 14.6}, 
    extent = {{-10, -10}, {10, 10}})));
  TYIntegratedEnergySys.Controllers.PowerController_FC powerController_FC(i_min = 0) "燃料电池功率控制器" 
    annotation(Placement(transformation(origin = {0, 62}, 
    extent = {{-10, 10}, {10, -10}})));
  Modelica.Blocks.Sources.CombiTimeTable Pel_FC(timeScale(displayUnit = "h") = 3600, table = {{0.0, 0}, {3, 0}, {3, 2e3}, {4, 2e3}, {4, 0}, {5, 0}}) "燃料电池电功率负荷" 
    annotation(Placement(transformation(origin = {-46, 59}, 
    extent = {{-10, -10}, {10, 10}})));
  TYIntegratedEnergySys.Sensors.Sensor_P sensor_P 
    annotation(Placement(transformation(origin = {-101, -34.2}, 
    extent = {{-10, -10}, {10, 10}})));
  TYIntegratedEnergySys.Boundaries.BoundaryPower boundaryPower3(SetPower = false) "功率边界" 
    annotation(Placement(transformation(origin = {-150, -34}, 
    extent = {{-10, -10}, {10, 10}})));
equation
  connect(PEMFuelCell.heat, boundaryPower2.heat) 
    annotation(Line(origin = {69, 44}, 
    points = {{-13, 6}, {-13, -14}, {12.8, -14}}, 
    color = {191, 0, 0}));
  connect(gasGrid.gas_b[1], sensor_qv.gas_a) 
    annotation(Line(origin = {60, -21.2}, 
    points = {{-3.6, -13}, {23.5, -13}, {23.5, -12.8}}, 
    color = {0, 209, 209}));
  connect(boundaryGas.gas, gasGrid.gas_a[2]) 
    annotation(Line(origin = {16, -53}, 
    points = {{-20, -13}, {-6, -13}, {-6, 18.6}, {19.6, 18.6}}, 
    color = {0, 209, 209}));
  connect(sensor_qv1.gas_a, gasGrid.gas_b[2]) 
    annotation(Line(origin = {45, 14}, 
    points = {{-25.1, 9.5}, {-25.1, -8}, {23, -8}, {23, -48.2}, {11.4, -48.2}}, 
    color = {0, 209, 209}));
  connect(sensor_qv.gas_b, gasLoad.gas) 
    annotation(Line(origin = {107, -34.2}, 
    points = {{-6, 0.1}, {5, 0.1}, {5, 0}}, 
    color = {0, 209, 209}));
  connect(sensor_qv1.gas_b, PEMFuelCell.gas) 
    annotation(Line(origin = {28, 47}, 
    points = {{-8, -6}, {-8, 6.8}, {8, 6.8}}, 
    color = {0, 209, 209}));
  connect(sensor_qv1.qv_flow, add.u1) 
    annotation(Line(origin = {-23, 26}, 
    points = {{33.4, 6}, {-37, 6}, {-37, -5.4}, {-32, -5.4}}, 
    color = {0, 0, 127}));
  connect(sensor_qv.qv_flow, add.u2) 
    annotation(Line(origin = {18, 3}, 
    points = {{74, -27.5}, {74, -9}, {-78, -9}, {-78, 5.6}, {-73, 5.6}}, 
    color = {0, 0, 127}));
  connect(PEMFuelCell.U_stack, powerController_FC.V) 
    annotation(Line(origin = {18, 51}, 
    points = {{38.8, 10.8}, {48, 10.8}, {48, 31}, {-38, 31}, {-38, 14.6}, {-28.2, 14.6}}, 
    color = {0, 0, 127}));
  connect(powerController_FC.P, Pel_FC.y[1]) 
    annotation(Line(origin = {-23, 65}, 
    points = {{12.8, -6}, {-12, -6}}, 
    color = {0, 0, 127}));
  connect(sensor_P.electric_b, H2Production.electric) 
    annotation(Line(origin = {-75, -34}, 
    points = {{-17, -0.2}, {5, -0.2}, {5, 0}}, 
    color = {16, 99, 16}));
  connect(SOCControl.SOC, H2Tank.SOC) 
    annotation(Line(origin={-82,-11}, 
points={{-32,13.4},{-34,13.4},{-34,-3},{86,-3},{86,-15.3},{79,-15.3}}, 
color={0,0,127}));
  connect(SOCControl.y, H2Production.P_el_set) 
    annotation(Line(origin = {-81, -9}, 
    points = {{-10.6, 18}, {7, 18}, {7, -17.4}, {10.8, -17.4}}, 
    color = {0, 0, 127}));
  connect(add.y, H2Tank.qv_out_set) 
    annotation(Line(origin = {-28, -7}, 
    points = {{-4, 21.6}, {0, 21.6}, {0, -21}, {3.4, -21}}, 
    color = {0, 0, 127}));
  connect(powerController_FC.I, PEMFuelCell.I) 
    annotation(Line(origin = {23, 62}, 
    points = {{-12.6, 0.2}, {13.2, 0.2}, {13.2, -0.2}}, 
    color = {0, 0, 127}));
  connect(H2Tank.gas_b, gasGrid.gas_a[1]) 
    annotation(Line(origin = {16, -49}, 
    points = {{-19.8, 14.8}, {19.6, 14.8}, {19.6, 14.6}}, 
    color = {0, 209, 209}));
  connect(H2Production.gas, H2Tank.gas_a) 
    annotation(Line(origin = {-37, -34}, 
    points = {{-12.6, 0.1}, {13, 0.1}, {13, -0.2}}, 
    color = {0, 209, 209}));
  connect(H2Tank.qv_out, SOCControl.qv_out) 
    annotation(Line(origin = {-56, -11}, 
    points = {{53, -18.8}, {56, -18.8}, {56, -7}, {-68, -7}, {-68, 19.8}, {-57, 19.8}}, 
    color = {0, 0, 127}));
  connect(PEMFuelCell.electric, boundaryPower1.electric) 
    annotation(Line(origin = {69, 58}, 
    points = {{-13, 0}, {12.8, 0}}, 
    color = {16, 99, 16}));
  connect(SOCControl.u, Pel.y[1]) 
    annotation(Line(origin = {-126, 14}, 
    points = {{13.2, -0.5}, {-13, -0.5}}, 
    color = {0, 0, 127}));
  connect(boundaryPower3.electric, sensor_P.electric_a) 
    annotation(Line(origin = {-125, -34}, 
    points = {{-14.8, 0}, {15.2, 0}, {15.2, -0.2}}, 
    color = {16, 99, 16}));
end HydrogenSys;