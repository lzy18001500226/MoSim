model FuelCellCHPSys "燃料电池CHP热回收系统"
  annotation(Documentation(link = "modelica://TYIntegratedEnergySys/Resources/HTML/FuelCellCHPSys.html"), Icon(coordinateSystem(extent = {{-100.0, -100.0}, {100.0, 100.0}}, 
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
    grid = {2, 2})), experiment(Algorithm = Dassl, InlineIntegrator = false, InlineStepSize = false, Interval = 2, StartTime = 0, StopTime = 500, Tolerance = 0.0001), __MWORKS(ContinueSimConfig(SaveContinueFile = "false", SaveBeforeStop = "false", NumberBeforeStop = 1, FixedContinueInterval = "false", ContinueIntervalLength = 22, ContinueTimeVector),ResultViewerManager(resultViewers={
ResultViewer(name="1", executeTrigger=executeTrigger.SimulationFinished, commands={
CreatePlot(id=1, x_display_unit="s", legend_layout=1, left_title_type=2, left_title="功率/kW", bottom_title_type=2, bottom_title="时间/s", right_title_type=2, fix_time_range_value=0, zoom_x=(0, 500), zoom_y_l=(20, 80)), 
Plot(legend=["氢燃料电池电功率 [kW]"], y=["PEMFuelCell.Pel"], colors=["4278190335"]), 
CreatePlot(id=-1, x_display_unit="s", legend_layout=1, left_title_type=2, left_title="质量流量[kg/s]", bottom_title_type=2, bottom_title="时间/s", fix_time_range_value=0, sub_plot=(1, 2), zoom_x=(0, 500), zoom_y_l=(0, 3.5)), 
Plot(legend=["冷却液流量[kg/s]"], y=["PEMFuelCell.m_flow_cl"], colors=["4278190335"]), 
CreatePlot(id=-1, x_display_unit="s", legend_layout=1, left_title_type=2, left_title="功率[kW]", bottom_title_type=2, bottom_title="时间/s", fix_time_range_value=0, sub_plot=(2, 2), zoom_x=(0, 500), zoom_y_l=(0, 140)), 
Plot(legend=["燃料电池热功率 [kW]"], y=["PEMFuelCell.Q_gen"], colors=["4278190335"]), 
CreatePlot(id=-1, x_display_unit="s", legend_layout=1, left_title_type=2, left_title="温度/degC", bottom_title_type=2, bottom_title="时间/s", fix_time_range_value=0, sub_plot=(2, 1), zoom_x=(0, 500), zoom_y_l=(58, 72)), 
Plot(legend=["冷却液入口温度 [degC]", "冷却液出口温度 [degC]"], y=["PEMFuelCell.T_cl_in", "PEMFuelCell.T_cl_out"], colors=["4278190335", "4294901760"])})
})), Protection(access = Access.nonPackageDuplicate));
  TYIntegratedEnergySys.EnergyExchange.Gas2Heat.PEMFuelCell PEMFuelCell(useFluidPorts = true, redeclare package Medium = Modelica.Media.Water.StandardWater, QDW = 141.774e6, N = 600, A_cell(displayUnit = "cm2") = 0.025, T_cell = 343.15, R_tot = 4E-5, eta = 0.825, U_tm = 1.23, T_start = 343.15, p_start = 1.8e5, m_flow_nominal = 3, dp_nominal = 10, I_start = 250) 
    "燃料电池" 
    annotation(Placement(transformation(origin = {-44, -10}, 
    extent = {{-10, -10}, {10, 10}})));
  TYIntegratedEnergySys.Boundaries.BoundaryGas boundaryGas(Type = "根据负荷计算所需流量") "气体边界" 
    annotation(Placement(transformation(origin = {-90, -10}, 
    extent = {{-10, -10}, {10, 10}})));
  TYIntegratedEnergySys.Controllers.PowerController_FC powerController_FC(k = 1, i_max = 250, i_min = 0) "燃料电池功率控制器" 
    annotation(Placement(transformation(origin = {-90, 30.2}, 
    extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Sources.TimeTable load(table = {{0.0, 30E3}, {100, 30E3}, {100, 50E3}, {200, 50E3}, {200, 70E3}, {300, 70E3}, {300, 60E3}, {400, 60E3}, {400, 40E3}, {500, 40E3}}, offset = 0) 
    "功率负荷输入" 
    annotation(Placement(transformation(origin = {-134, 52}, 
    extent = {{-10, -10}, {10, 10}})));
  TYIntegratedEnergySys.Boundaries.BoundaryPower PelSink(SetPower = false, P_in(displayUnit = "W") = -375) "功率边界" 
    annotation(Placement(transformation(origin = {18, 5.8}, 
    extent = {{10, -10}, {-10, 10}})));
  TYThermoFluidSys.Machines.SuterPump P1(qv_start = 3e-3, qvr = 3e-3, eta_r = 0.8, Hr = 10, redeclare package Medium = Modelica.Media.Water.StandardWater) "泵" 
    annotation(Placement(transformation(origin = {34, -60}, 
    extent = {{10, -10}, {-10, 10}})));
  TYThermoFluidSys.Boundaries.BoundarySpeed boundarySpeed(use_w_in = false, w(displayUnit = "rpm") = 314.159265358979) "转速边界" 
    annotation(Placement(transformation(origin = {-10, -38}, 
    extent = {{-10, -10}, {10, 10}})));
  TYIntegratedEnergySys.EnergyStorage.HeatTank heatTank(redeclare package Medium = Modelica.Media.Water.StandardWater, useFluidPorts = true, T_start_Gen = 333.15, T_start = 333.15, dp_nominal = {1e5, 1e5}, m_flow_nominal = {3.5, 1}, d = 1, height = 5, T_max = 393.15, tau_Gen = 10, tau_Con = 10, T_start_Con = 333.15, T_s_max = 353.15) 
    "储热罐" 
    annotation(Placement(transformation(origin = {74, -13.6}, 
    extent = {{-10, -10}, {10, 10}})));
  TYIntegratedEnergySys.Boundaries.BoundaryTemperature bound_T(T = 298.15) "温度边界" 
    annotation(Placement(transformation(origin = {100, 30}, 
    extent = {{10, -10}, {-10, 10}})));
  TYIntegratedEnergySys.Boundaries.BoundaryPressure bound_p(redeclare package Medium = Modelica.Media.Water.StandardWater, p = 100000) "压力边界" 
    annotation(Placement(transformation(origin = {134, 6}, 
    extent = {{10, -10}, {-10, 10}})));
  TYIntegratedEnergySys.Boundaries.BoundaryMdot bound_mdot(redeclare package Medium = Modelica.Media.Water.StandardWater, m_flow = 1, T = 333.15, use_mflow_in = false) "质量流量边界" 
    annotation(Placement(transformation(origin = {134, -60}, 
    extent = {{10, -10}, {-10, 10}})));
  TYUtility.SignalRouting.Goto V_cell(redeclare Modelica.Blocks.Interfaces.RealInput u) 
    annotation(Placement(transformation(origin = {-10, 13.8}, 
    extent = {{-10, -7.8}, {10, 7.4}})), HideResult = true);
  TYUtility.SignalRouting.From from(redeclare connector OutputConnectorType = Modelica.Blocks.Interfaces.RealOutput, y = V_cell.u) 
    annotation(Placement(transformation(origin = {-134, 21.2}, 
    extent = {{-10, -7.4}, {10, 7.4}})), HideResult = true);
  TYIntegratedEnergySys.Boundaries.BoundaryPower PhSink(SetPower = false, PortType = "heat") "功率边界" 
    annotation(Placement(transformation(origin = {18, -22}, 
    extent = {{10, -10}, {-10, 10}})));
  TYIntegratedEnergySys.Boundaries.BoundaryPower PhSink1(SetPower = false, PortType = "heat") "功率边界" 
    annotation(Placement(transformation(origin = {100, -13.6}, 
    extent = {{10, -10}, {-10, 10}})));
  TYIntegratedEnergySys.Boundaries.BoundaryPower PhSink2(SetPower = false, PortType = "heat") "功率边界" 
    annotation(Placement(transformation(origin = {46, -13.4}, 
    extent = {{-10, -10}, {10, 10}})));
equation
  connect(boundaryGas.gas, PEMFuelCell.gas) 
    annotation(Line(origin = {-67, -10.4}, 
    points = {{-13, 0.4}, {13, 0.4}, {13, 0.2}}, 
    color = {0, 209, 209}));
  connect(boundarySpeed.flange, P1.flange_a) 
    annotation(Line(origin = {44, -40}, 
    points = {{-44, 2}, {-9.8, 2}, {-9.8, -11}}, 
    color = {0, 0, 0}));
  connect(bound_T.port[1], heatTank.heatport) 
    annotation(Line(origin = {59, -46}, 
    points = {{31, 76}, {15, 76}, {15, 42.6}}, 
    color = {191, 0, 0}));
  connect(load.y, powerController_FC.P) 
    annotation(Line(origin = {-121, 48.2}, 
    points = {{-2, 3.8}, {20.8, 3.8}, {20.8, -15}}, 
    color = {0, 0, 127}));
  connect(PEMFuelCell.U_stack, V_cell.u) 
    annotation(Line(origin = {-29, 2}, 
    points = {{-4.2, -4.2}, {7, -4.2}, {7, 11.8}}, 
    color = {0, 0, 127}));
  connect(from.y, powerController_FC.V) 
    annotation(Line(origin = {-111, 24.2}, 
    points = {{-11.4, -3.1}, {10.8, -3.1}, {10.8, 2.4}}, 
    color = {0, 0, 127}));
  connect(PEMFuelCell.electric, PelSink.electric) 
    annotation(Line(origin = {-15, -8}, 
    points = {{-19, 2}, {22.8, 2}, {22.8, 13.8}}, 
    color = {16, 99, 16}));
  connect(powerController_FC.I, PEMFuelCell.I) 
    annotation(Line(origin = {-67, 14}, 
    points = {{-12.6, 16}, {-1, 16}, {-1, -16.2}, {12.4, -16.2}}, 
    color = {0, 0, 127}));
  connect(PhSink.heat, PEMFuelCell.heat) 
    annotation(Line(origin = {-13, -20}, 
    points = {{20.8, -2}, {-21, -2}, {-21, 6}}, 
    color = {191, 0, 0}));
  connect(heatTank.heat_Consumer, PhSink1.heat) 
    annotation(Line(origin = {98, -13}, 
    points = {{-14, -0.4}, {-8.2, -0.4}, {-8.2, -0.6}}, 
    color = {191, 0, 0}));
  connect(PhSink2.heat, heatTank.heat_Gen) 
    annotation(Line(origin = {60, -13}, 
    points = {{-3.8, -0.4}, {4, -0.4}}, 
    color = {191, 0, 0}));
  connect(PEMFuelCell.port_b, heatTank.port_a_Gen) 
    annotation(Line(origin = {12, 0}, 
    points = {{-56, -0.2}, {-56, 36}, {55.8, 36}, {55.8, -3.8}}, 
    color = {0, 178, 226}));
  connect(PEMFuelCell.port_a, P1.port_b) 
    annotation(Line(origin = {-10, -40}, 
    points = {{-34, 19.8}, {-34, -20}, {33.6, -20}}, 
    color = {0, 178, 226}));
  connect(P1.port_a, heatTank.port_b_Gen) 
    annotation(Line(origin = {56, -42}, 
    points = {{-12.8, -18}, {11.8, -18}, {11.8, 18.2}}, 
    color = {0, 178, 226}));
  connect(heatTank.port_a_Con, bound_mdot.fluidPort) 
    annotation(Line(origin = {103, -42}, 
    points = {{-23, 18.4}, {-23, -18}, {23, -18}}, 
    color = {0, 178, 226}));
  connect(heatTank.port_b_Con, bound_p.port_b) 
    annotation(Line(origin = {103, 1}, 
    points = {{-23, -4.6}, {-23, 5}, {23, 5}}, 
    color = {0, 178, 226}));
end FuelCellCHPSys;