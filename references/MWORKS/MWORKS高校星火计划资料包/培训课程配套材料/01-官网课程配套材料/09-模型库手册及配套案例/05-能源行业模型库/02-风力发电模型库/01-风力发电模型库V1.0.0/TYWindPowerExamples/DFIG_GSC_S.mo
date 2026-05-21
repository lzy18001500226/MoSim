model DFIG_GSC_S "双馈发电机并网系统-转速控制"
  annotation(Documentation(link = "modelica://TYWindPower/Resources/HTML/DFIG_GSC_S.html"), Diagram(coordinateSystem(extent = {{-160, -100}, {160, 100}}, 
    grid = {2, 2})), 
    experiment(Algorithm = Dassl, Interval = 0.0001, StartTime = 0, StopTime = 2, Tolerance = 1e-05, InlineIntegrator = false, InlineStepSize = false), __MWORKS(ContinueSimConfig(SaveContinueFile = "false", SaveBeforeStop = "false", NumberBeforeStop = 1, FixedContinueInterval = "false", ContinueIntervalLength = 0.4, ContinueTimeVector),ResultViewerManager(resultViewers={
ResultViewer(name="Result", executeTrigger=executeTrigger.SimulationFinished, commands={
CreatePlot(id = 6, position = [0, 28, 837, 544], y = ["Wref.y", "DFIG.wMechanical"], x_display_unit = "s", y_display_units = ["", "rad/s"], y_axis = [1, 1], legends = ["参考转速[rad/s]", "实际转速[rad/s]"], legend_layout = 1, legend_frame = True, left_title_type = 2, left_title = "转速/[rad/s]", bottom_title_type = 2, bottom_title = "时间/s", right_title_type = 2, fix_time_range_value = 6.95328e-310), 
CreatePlot(id = 7, position = [0, 28, 843, 544], y = ["Vdref.y", "voltageSensor.v"], x_display_unit = "s", y_display_units = ["V", "V"], y_axis = [1, 1], legends = ["直流侧参考电压 [V]", "直流侧实际电压 [V]"], legend_layout = 1, legend_frame = True, left_title_type = 2, left_title = "电压/V", bottom_title_type = 2, bottom_title = "时间/s", right_title_type = 2, fix_time_range_value = 6.95328e-310), 
CreatePlot(id = 8, position = [0, 28, 839, 559], y = ["GSCtrl.power_Cal.Q"], x_display_unit = "s", y_display_units = ["var"], y_axis = [1], legends = ["无功功率 [var]"], legend_layout = 1, legend_frame = True, left_title_type = 2, left_title = "功率/var", bottom_title_type = 2, bottom_title = "时间/s", right_title_type = 2, fix_time_range_value = 6.95328e-310), 
CreatePlot(id = 9, position = [0, 28, 837, 559], y = ["GSCtrl.power_Cal.P"], x_display_unit = "s", y_display_units = ["W"], y_axis = [1], legends = ["有功功率 [W]"], legend_layout = 1, legend_frame = True, left_title_type = 2, left_title = "功率/W", bottom_title_type = 2, bottom_title = "时间/s", right_title_type = 2, fix_time_range_value = 6.95328e-310), 
CreatePlot(id = 10, position = [0, 28, 843, 559], y = ["resistor.v[1]", "resistor.v[2]", "resistor.v[3]"], x_display_unit = "s", y_display_units = ["V", "V", "V"], y_axis = [1, 1, 1], legends = ["A相电压 [V]", "B相电压 [V]", "C相电压 [V]"], legend_layout = 1, legend_frame = True, left_title_type = 2, left_title = "电压/V", bottom_title_type = 2, bottom_title = "时间/s", right_title_type = 2, fix_time_range_value = 6.95328e-310)})
})), Icon(coordinateSystem(extent = {{-100, -100}, {100, 100}}, 
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
    thickness = 5)}),Protection(access=Access.nonPackageDuplicate));
  /* 参数 */
  parameter Modelica.SIunits.Voltage Enom = 690"额定电压";
  parameter Modelica.SIunits.Power Pn = 2e6 "额定功率:2MW";
  parameter Modelica.SIunits.Frequency fn = 50 "额定频率";
  parameter Integer np = 3 "极对数";
  parameter Modelica.SIunits.Inertia J = 77.96 "转动惯量";
  parameter Modelica.SIunits.Inductance Lg = 300e-6"滤波电感";
  parameter Modelica.SIunits.Resistance Rg = 0.1"滤波电阻";
  /* 变量 */
  Real j = 127;
  Real Rr = 2.9e-3;
  Real p = 2;
  Real Lm = 2.5e-3;
  Real Ls = 0.087e-3 + 2.5e-3;
  Real Lr = 0.087e-3 + 2.5e-3;
  Real sigma = 1 - (Lm ^ 2) / (Ls * Lr);
  Real tau_i = sigma * Lr / Rr;
  Real tau_n = 0.05;
  Real wni = 100 * (1 / tau_i);
  Real wnn = 1 / tau_n;
  Real Kp_i = 2 * wni * sigma * Lr - Rr;
  Real Ki_i = (wni ^ 2) * Lr * sigma;
  Real Ti = Kp_i / Ki_i;
  Real Kp_n = (2 * wnn * j) / 2;
  Real Ki_n = (wnn ^ 2) * j / 2;
  Real Tn = Kp_n / Ki_n;

  /* 实例化 */
  TYWindPower.Generators.DFIG DFIG(VsNominal = Enom, Jr = 77.96, Rs = 5.5e-3, Rr = 6.21e-3, Lssigma = 1.71e-4, Lrsigma = 2.26e-4, Lm = 11.01e-3, 
    p = 3, fsNominal = 50, turnsRatio = 1 / 3) 
    annotation(Placement(transformation(origin = {-50, 44}, extent = {{-10, -10}, {10, 10}})));
  TYWindPower.PowerConverters.IdealSwitching.Rectifier ACDC(VkneeThyristor = 0, constantEnable = true) 
    annotation(Placement(transformation(origin = {4, -14.1093}, 
    extent = {{-10, -10}, {10, 10}})));
  Modelica.Electrical.Analog.Basic.Capacitor C(C = 0.5) 
    annotation(Placement(transformation(origin = {33.945375, -14.1093}, 
    extent = {{-6.05463, -6.05463}, {6.05463, 6.05463}}, 
    rotation = 270)));
  Modelica.Electrical.Polyphase.Basic.Resistor resistor(R = fill(Rg, 3)) 
    annotation(Placement(transformation(origin = {86, 36}, 
    extent = {{-10, -10}, {10, 10}}, 
    rotation = 90)));
  Modelica.Electrical.Polyphase.Basic.Inductor inductor(L = fill(Lg, 3)) 
    annotation(Placement(transformation(origin = {86, 10}, 
    extent = {{-10, -10}, {10, 10}}, 
    rotation = 90)));
  TYWindPower.Controllers.DFIG.MachineSideControllerW MSCtrl(j = 77.96, Rr = 6.21e-3, Rs = 5.5e-3, p = 3, Lm = 11.01e-3, Ls = 1.71e-4 + 11.01e-3, Lr = 11.01e-3 + 2.26e-4) 
    annotation(Placement(transformation(origin = {4, -54}, 
    extent = {{-10, -10}, {10, 10}})));
  TYWindPower.Controllers.DFIG.GridSideController GSCtrl(Id_pi(k = 5e-5, T = 0.08), Iq_PI(k = 5e-3, T = 0.01), Vdc_PI(T = 10 / 60)) 
    annotation(Placement(transformation(origin = {63.89075, -54}, 
    extent = {{10, -10}, {-10, 10}})));
  Modelica.Blocks.Sources.RealExpression Wref(y = 1325 * Modelica.Constants.pi / 30) 
    annotation(Placement(transformation(origin = {-16, -62.2}, 
    extent = {{-3, -3}, {3, 3}})));
  TYWindPower.PowerConverters.IdealSwitching.UniversalBridge DCAC 
    annotation(Placement(transformation(origin = {63.89075, -14.1093}, 
    extent = {{-10, -10}, {10, 10}})));
  TYWindPower.Controllers.Basics.PLL3ph pLL(pI(Kp = 0.5)) 
    annotation(Placement(transformation(origin = {114, -14.1093}, 
    extent = {{-4.25, -4}, {4.25, 4}})));
  Modelica.Electrical.Polyphase.Basic.Inductor Lf(L = fill(1e-5, 3)) 
    annotation(Placement(transformation(origin = {-28, 8}, 
    extent = {{-10, -10}, {10, 10}}, 
    rotation = -90)));
  TYWindPower.PowerTransmissions.PowerGrid powerGrid(V = 690 * ones(3)) 
    annotation(Placement(transformation(origin = {132, 60}, 
    extent = {{10, -10}, {-10, 10}})));
  Modelica.Electrical.Polyphase.Sensors.CurrentSensor currentSensor1 
    annotation(Placement(transformation(origin = {-12, 60}, 
    extent = {{5, 5}, {-5, -5}}, 
    rotation = -180)));
  Modelica.Electrical.Polyphase.Sensors.PotentialSensor potentialSensor1 
    annotation(Placement(transformation(origin = {106, 15}, 
    extent = {{-5, -5}, {5, 5}}, 
    rotation = -90)));
  TYUtility.SignalRouting.Goto Ig_abc[3] 
    annotation(Placement(transformation(origin = {-1.75, 53.315}, 
    extent = {{-3, -3}, {3, 3}})), HideResult = true);
  TYUtility.SignalRouting.From from[3](redeclare connector OutputConnectorType = Modelica.Blocks.Interfaces.RealOutput, y = Ig_abc.u) 
    annotation(Placement(transformation(origin = {84, -46.5595}, 
    extent = {{3, -3}, {-3, 3}})), HideResult = true);
  TYUtility.SignalRouting.Goto Udc 
    annotation(Placement(transformation(origin = {53, 17}, 
    extent = {{-3, -3}, {3, 3}})), HideResult = true);
  TYUtility.SignalRouting.From from1(redeclare connector OutputConnectorType = Modelica.Blocks.Interfaces.RealOutput, y = Udc.u) 
    annotation(Placement(transformation(origin = {84, -56.5595}, 
    extent = {{3, -3}, {-3, 3}})), HideResult = true);
  TYUtility.SignalRouting.Goto Im_abc[3] 
    annotation(Placement(transformation(origin = {-14, 32.9211}, 
    extent = {{-3, -3}, {3, 3}})), HideResult = true);
  TYUtility.SignalRouting.From from2[3](redeclare connector OutputConnectorType = Modelica.Blocks.Interfaces.RealOutput, y = Im_abc.u) 
    annotation(Placement(transformation(origin = {-16, -44.9595}, 
    extent = {{-3, -3}, {3, 3}})), HideResult = true);
  TYUtility.SignalRouting.From from3[3](redeclare connector OutputConnectorType = Modelica.Blocks.Interfaces.RealOutput, y = Ig_abc.u) 
    annotation(Placement(transformation(origin = {-24, -48.3995}, 
    extent = {{-3, -3}, {3, 3}})), HideResult = true);
  TYUtility.SignalRouting.From from4(redeclare connector OutputConnectorType = Modelica.Blocks.Interfaces.RealOutput, y = theta_s.u) 
    annotation(Placement(transformation(origin = {-33, -51.8395}, 
    extent = {{-3, -3}, {3, 3}})), HideResult = true);
  TYUtility.SignalRouting.Goto theta_s(redeclare Modelica.Blocks.Interfaces.RealInput u) 
    annotation(Placement(transformation(origin = {116.7815, -26}, 
    extent = {{3, -3}, {-3, 3}})), HideResult = true);
  TYWindPower.Sensors.MechanicalSensors.AbsoluteSensor absoluteSensor1 
    annotation(Placement(transformation(origin = {-68, 8}, 
    extent = {{-10, -10}, {10, 10}}, 
    rotation = -90)));
  Modelica.Electrical.Analog.Sensors.VoltageSensor voltageSensor 
    annotation(Placement(transformation(origin = {42, 5}, 
    extent = {{-5, 5}, {5, -5}})));
  Modelica.Electrical.Polyphase.Sensors.CurrentSensor currentSensor2 
    annotation(Placement(transformation(origin = {-28, 33}, 
    extent = {{-5, 5}, {5, -5}}, 
    rotation = 270)));
  Modelica.Blocks.Sources.Step step(offset = 7500, startTime = 0, height = 0) 
    annotation(Placement(transformation(origin = {-130, 44}, 
    extent = {{-10, -10}, {10, 10}})));
  Modelica.Mechanics.Rotational.Sources.Torque torque 
    annotation(Placement(transformation(origin = {-90, 44}, 
    extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Sources.RealExpression Vdref(y = 1200) 
    annotation(Placement(transformation(origin = {86, -38.05463}, 
    extent = {{5, -6.05463}, {-5, 6.05463}})));
equation
  connect(resistor.plug_p, inductor.plug_n) 
    annotation(Line(origin = {108.7415, -13.2903}, 
    points = {{-22.7415, 39.2903}, {-22.7415, 33.2903}}, 
    color = {0, 0, 255}));
  connect(Wref.y, MSCtrl.Wr_ref) 
    annotation(Line(origin = {-16.625, -51.9}, 
    points = {{3.925, -10.3}, {9.625, -10.3}}, 
    color = {0, 0, 127}));
  connect(C.p, DCAC.pSupply) 
    annotation(Line(origin = {76.1664, 5.8856}, 
    points = {{-42.221025, -13.9403}, {-22.27565, -13.9403}, {-22.27565, -13.9949}}, 
    color = {0, 0, 255}));
  connect(DCAC.nSupply, C.n) 
    annotation(Line(origin = {76.1664, -12.1144}, 
    points = {{-22.27565, -7.9949}, {-42.221025, -7.9949}, {-42.221025, -8.17062}}, 
    color = {0, 0, 255}));
  connect(ACDC.pLoad, C.p) 
    annotation(Line(origin = {38.1664, 3.8856}, 
    points = {{-24.1664, -11.9949}, {-4.22103, -11.9949}, {-4.22103, -11.9403}}, 
    color = {0, 0, 255}));
  connect(ACDC.nLoad, C.n) 
    annotation(Line(origin = {38.1664, -13.1144}, 
    points = {{-24.1664, -6.9949}, {-4.22103, -6.9949}, {-4.22103, -7.17062}}, 
    color = {0, 0, 255}));
  connect(Lf.plug_n, ACDC.pSupply) 
    annotation(Line(origin = {-7.8336, -5.1144}, 
    points = {{-20.1664, 3.1144}, {-20.1664, -8.9949}, {1.8336, -8.9949}}, 
    color = {0, 0, 255}));
  connect(currentSensor2.plug_n, Lf.plug_p) 
    annotation(Line(origin = {-33, 25}, 
    points = {{5, 3}, {5, -7}}, 
    color = {0, 0, 255}));
  connect(inductor.plug_p, DCAC.pload) 
    annotation(Line(origin = {86, -21}, 
    points = {{0, 21}, {0, 6.8907}, {-12.1093, 6.8907}}, 
    color = {0, 0, 255}));
  connect(currentSensor1.plug_p, DFIG.plug_sp) 
    annotation(Line(origin = {-33, 57}, 
    points = {{16, 3}, {-17, 3}, {-17, -2.6}}, 
    color = {0, 0, 255}));
  connect(resistor.plug_n, powerGrid.plug_p) 
    annotation(Line(origin = {123, 52}, 
    points = {{-37, -6}, {-37, 8}, {-1.4, 8}}, 
    color = {0, 0, 255}));
  connect(currentSensor1.plug_n, powerGrid.plug_p) 
    annotation(Line(origin = {66, 60}, 
    points = {{-73, 0}, {55.6, 0}}, 
    color = {0, 0, 255}));
  connect(potentialSensor1.plug_p, powerGrid.plug_p) 
    annotation(Line(origin = {133, 39}, 
    points = {{-27, -19}, {-27, 21}, {-11.4, 21}}, 
    color = {0, 0, 255}));
  connect(potentialSensor1.phi, pLL.Uabc) 
    annotation(Line(origin = {108, 3}, 
    points = {{-2, 6.5}, {-2, -17.1093}, {0.9, -17.1093}}, 
    color = {0, 0, 127}));
  connect(currentSensor1.i, Ig_abc.u) 
    annotation(Line(origin = {-9, 54}, 
    points = {{-3, 0.5}, {-3, -0.685}, {2.15, -0.685}}, 
    color = {0, 0, 127}));
  connect(GSCtrl.is_abc, from.y) 
    annotation(Line(origin = {78, -47}, 
    points = {{-3.10925, 0.4}, {2.52, 0.4}}, 
    color = {0, 0, 127}));
  connect(GSCtrl.Us_abc, potentialSensor1.phi) 
    annotation(Line(origin = {90, -21}, 
    points = {{-15.1093, -30.6}, {-10, -30.6}, {-10, -29}, {16, -29}, {16, 30.5}}, 
    color = {0, 0, 127}));
  connect(from1.y, GSCtrl.Udc) 
    annotation(Line(origin = {78, -57}, 
    points = {{2.52, 0.399959}, {-3.10925, 0.399959}, {-3.10925, 0.4}}, 
    color = {0, 0, 127}));
  connect(pLL.Theta, GSCtrl.theta_s) 
    annotation(Line(origin = {97, -37}, 
    points = {{21.675, 24.4907}, {27, 24.4907}, {27, -13}, {9, -13}, {9, -24.6}, {-22.1093, -24.6}}, 
    color = {0, 0, 127}));
  connect(GSCtrl.fire_p, DCAC.fire_p) 
    annotation(Line(origin = {53, -38}, 
    points = {{-0.10925, -18.0667}, {-5, -18.0667}, {-5, 4}, {4.89075, 4}, {4.89075, 11.8907}}, 
    color = {255, 0, 255}));
  connect(GSCtrl.fire_n, DCAC.fire_n) 
    annotation(Line(origin = {59, -42}, 
    points = {{-6.10925, -16}, {-11, -16}, {-11, 8}, {10.8907, 8}, {10.8907, 15.8907}}, 
    color = {255, 0, 255}));
  connect(MSCtrl.fire_p, ACDC.fire_p) 
    annotation(Line(origin = {11, -37}, 
    points = {{4, -11.8}, {13, -11.8}, {13, -1}, {-13, -1}, {-13, 10.8907}}, 
    color = {255, 0, 255}));
  connect(MSCtrl.fire_n, ACDC.fire_n) 
    annotation(Line(origin = {17, -43}, 
    points = {{-2, -16.8}, {7, -16.8}, {7, 5}, {-7, 5}, {-7, 16.8907}}, 
    color = {255, 0, 255}));
  connect(currentSensor2.plug_p, DFIG.plug_rp) 
    annotation(Line(origin = {-33, 40}, 
    points = {{5, -2}, {5, 4}, {-6, 4}}, 
    color = {0, 0, 255}));
  connect(from2.y, MSCtrl.ir_abc) 
    annotation(Line(origin = {-10, -45}, 
    points = {{-2.52, 0}, {3, 0}}, 
    color = {0, 0, 127}));
  connect(MSCtrl.is_abc, from3.y) 
    annotation(Line(origin = {-14, -48}, 
    points = {{7, -0.44}, {-6.52, -0.44}}, 
    color = {0, 0, 127}));
  connect(from4.y, MSCtrl.the) 
    annotation(Line(origin = {-22, -53}, 
    points = {{-7.52, 1.12}, {15, 1.12}}, 
    color = {0, 0, 127}));
  connect(absoluteSensor1.phi, MSCtrl.theta_r) 
    annotation(Line(origin = {-35, -30}, 
    points = {{-29, 26}, {-29, -25.32}, {28, -25.32}}, 
    color = {0, 0, 127}));
  connect(absoluteSensor1.om, MSCtrl.Wr) 
    annotation(Line(origin = {-37, -31}, 
    points = {{-31, 27}, {-31, -27.76}, {30, -27.76}}, 
    color = {0, 0, 127}));
  connect(voltageSensor.p, C.p) 
    annotation(Line(origin = {34, 5}, 
    points = {{3, 0}, {-0.054625, 0}, {-0.054625, -13.0547}}, 
    color = {0, 0, 255}));
  connect(voltageSensor.n, C.n) 
    annotation(Line(origin = {41, -1}, 
    points = {{6, 6}, {6, -19.285}, {-7.05463, -19.285}}, 
    color = {0, 0, 255}));
  connect(voltageSensor.v, Udc.u) 
    annotation(Line(origin = {46, 14}, 
    points = {{-4, -3.5}, {-4, 3.07895}, {3.4, 3.07895}}, 
    color = {0, 0, 127}));
  connect(currentSensor2.i, Im_abc.u) 
    annotation(Line(origin = {-20, 33}, 
    points = {{-2.5, 0}, {2.4, 0}}, 
    color = {0, 0, 127}));
  connect(step.y, torque.tau) 
    annotation(Line(origin = {-117.571, 49.3204}, 
    points = {{-1.429, -5.3204}, {15.571, -5.3204}}, 
    color = {0, 0, 127}));
  connect(DFIG.flange, torque.flange) 
    annotation(Line(origin = {-70, 44}, 
    points = {{10, 0}, {-10, 0}}, 
    color = {0, 0, 0}));
  connect(torque.flange, absoluteSensor1.flange) 
    annotation(Line(origin = {-74, 31}, 
    points = {{-6, 13}, {6, 13}, {6, -13}}, 
    color = {0, 0, 0}));
  connect(GSCtrl.Vdcref, Vdref.y) 
    annotation(Line(origin = {78, -42}, 
    points = {{-3.10925, -3.6}, {0, -3.6}, {0, 3.94537}, {2.5, 3.94537}}, 
    color = {0, 0, 127}));
  connect(pLL.Theta, theta_s.u) 
    annotation(Line(origin = {121, -19}, 
    points = {{-2.325, 6.4907}, {3, 6.4907}, {3, -6.92105}, {-0.6185, -6.92105}}, 
    color = {0, 0, 127}));
end DFIG_GSC_S;