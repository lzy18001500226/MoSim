model DFIG_GSC "双馈风电机组并网系统"
  annotation(Documentation(link = "modelica://TYWindPower/Resources/HTML/DFIG_GSC.html"), Diagram(coordinateSystem(extent={{-200,-100},{180,120}}, 
grid={2,2}),graphics = {Rectangle(origin={-148.5,40}, 
fillColor={255,255,255}, 
pattern=LinePattern.Dash, 
extent={{-74.5,24},{74.5,-24}}), Text(origin={-148.5,70}, 
lineColor={0,0,128}, 
extent={{-31.25,5},{31.25,-5}}, 
textString="风力机系统", 
textStyle={TextStyle.Italic}, 
textColor={0,0,128}), Rectangle(origin={-165.333,-77.0199}, 
fillColor={255,255,255}, 
pattern=LinePattern.Dash, 
extent={{-31.25,17.3391},{31.25,-17.3391}}), Text(origin={-165.333,-100.806}, 
lineColor={0,0,128}, 
extent={{-27.2931,5},{27.2932,-5}}, 
textString="桨距控制器", 
textStyle={TextStyle.Italic}, 
textColor={0,0,128}), Rectangle(origin={40,-74.0195}, 
fillColor={255,255,255}, 
pattern=LinePattern.Dash, 
extent={{-108,22.5},{108,-22.5}}), Text(origin={45,-101.86014}, 
lineColor={0,0,128}, 
extent={{-39,6.05463},{39,-6.05463}}, 
textString="机侧、网侧控制器", 
textStyle={TextStyle.Italic}, 
textColor={0,0,128}), Rectangle(origin={-28,18}, 
fillColor={255,255,255}, 
pattern=LinePattern.Dash, 
lineThickness=0.4, 
extent={{-202,58},{202,-58}}), Rectangle(origin={-28,-79.5}, 
fillColor={255,255,255}, 
pattern=LinePattern.Dash, 
lineThickness=0.4, 
extent={{-202,32.5},{202,-32.5}}), Rectangle(origin={40,-6.5}, 
fillColor={255,255,255}, 
pattern=LinePattern.Dash, 
extent={{-70,26.5},{70,-26.5}}), Text(origin={50,30}, 
lineColor={0,0,128}, 
extent={{-27.2932,7.04456},{27.2931,-7.04456}}, 
textString="背靠背换流器", 
textStyle={TextStyle.Italic}, 
textColor={0,0,128}), Text(origin={164.563085,27.921}, 
rotation=-90, 
lineColor={0,0,128}, 
extent={{-39,-6.00009},{39,6.00009}}, 
textString="风电系统", 
textStyle={TextStyle.None}, 
textColor={0,0,128}), Text(origin={164.563,-76.079}, 
rotation=-90, 
lineColor={0,0,128}, 
extent={{47,-6.00015},{-47,6.00015}}, 
textString="控制系统", 
textStyle={TextStyle.None}, 
textColor={0,0,128})}), 
    experiment(Algorithm=Dassl,Interval=0.0001,StartTime=0,StopTime=5,Tolerance=1e-05,InlineIntegrator=false,InlineStepSize=false), Icon(coordinateSystem(extent = {{-100, -100}, {100, 100}}, 
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
    thickness = 5)}), __MWORKS(ResultViewerManager(resultViewers={
ResultViewer(name="1", executeTrigger=executeTrigger.SimulationFinished, commands={
CreatePlot(id=1, x_display_unit="s", legend_layout=1, left_title="[V]", right_title_type=2, fix_time_range_value=0, zoom_x=(0, 5), zoom_y_l=(-500, 2000)), 
Plot(y=["Vdref.y", "voltageSensor.v"], colors=["4278190335", "4294901760"]), 
CreatePlot(id=-1, x_display_unit="s", legend_layout=1, left_title="[var]", fix_time_range_value=0, sub_plot=(1, 2), zoom_x=(0, 5), zoom_y_l=(-4e+06, 2e+06)), 
Plot(y=["GSCtrl.power_Cal.Q"], colors=["4278190335"]), 
CreatePlot(id=-1, x_display_unit="s", legend_layout=1, left_title="[m/s]", fix_time_range_value=0, sub_plot=(2, 2), zoom_x=(0, 5), zoom_y_l=(7.5, 10)), 
Plot(y=["windSource.windSpeed"], colors=["4278190335"]), 
CreatePlot(id=-1, x_display_unit="s", legend_layout=1, fix_time_range_value=0, sub_plot=(2, 1), zoom_x=(0, 5), zoom_y_l=(-2e+06, 8e+06)), 
Plot(y=["GSCtrl.power_Cal.P", "Pref.y"], colors=["4278190335", "4294901760"])})
})),Protection(access=Access.nonPackageDuplicate));
  /* 参数 */
  parameter Modelica.SIunits.Voltage Enom = 690"额定电压";
  parameter Modelica.SIunits.Power Pn = 2e6 "额定功率:2MW";
  parameter Modelica.SIunits.Frequency fn = 50 "额定频率";
  parameter Integer np = 3 "极对数";
  parameter Modelica.SIunits.Inertia J = 77.96 "转动惯量";
  parameter Modelica.SIunits.Inductance Lg = 300e-6"滤波电感";
  parameter Modelica.SIunits.Resistance Rg = 0.3"滤波电阻";

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
    annotation(Placement(transformation(origin = {-38, 40}, 
    extent = {{-10, -10}, {10, 10}})));
  TYWindPower.PowerConverters.IdealSwitching.Rectifier ACDC(VkneeThyristor = 0, constantEnable = true) 
    annotation(Placement(transformation(origin = {16, -18.1093}, 
    extent = {{-10, -10}, {10, 10}})));
  Modelica.Electrical.Analog.Basic.Capacitor C(C = 0.5) 
    annotation(Placement(transformation(origin = {45.945375, -18.1093}, 
    extent = {{-6.05463, -6.05463}, {6.05463, 6.05463}}, 
    rotation = 270)));
  Modelica.Electrical.Polyphase.Basic.Resistor resistor(R = fill(Rg, 3)) 
    annotation(Placement(transformation(origin={98,28}, 
extent={{-10,-10},{10,10}}, 
rotation=90)));
  Modelica.Electrical.Polyphase.Basic.Inductor inductor(L = fill(Lg, 3)) 
    annotation(Placement(transformation(origin={98,4}, 
extent={{-10,-10},{10,10}}, 
rotation=90)));
  TYWindPower.Controllers.DFIG.MachineSideControllerP MSCtrl(j = 77.96, Rr = 6.21e-3, Rs = 5.5e-3, p = 3, Lm = 11.01e-3, Ls = 1.71e-4 + 11.01e-3, Lr = 11.01e-3 + 2.26e-4,kp1=100) 
    annotation(Placement(transformation(origin = {16, -73.5195}, 
    extent = {{-10, -10}, {10, 10}})));
  TYWindPower.Controllers.DFIG.GridSideController GSCtrl(Id_pi(k = 5e-5, T = 0.08), Iq_PI(k = 5e-3, T = 0.01), Vdc_PI(T = 10 / 60)) 
    annotation(Placement(transformation(origin = {75.89075, -73.5195}, 
    extent = {{10, -10}, {-10, 10}})));
  Modelica.Blocks.Sources.RealExpression Pref(y = 1.3e6) 
    "参考有功功率" annotation(Placement(transformation(origin = {-4, -81.7195}, 
    extent = {{-3, -3}, {3, 3}})));
  TYWindPower.PowerConverters.IdealSwitching.UniversalBridge DCAC 
    annotation(Placement(transformation(origin = {75.89075, -18.1093}, 
    extent = {{-10, -10}, {10, 10}})));
  TYWindPower.Controllers.Basics.PLL3ph pLL(pI(Kp = 0.5)) 
    annotation(Placement(transformation(origin = {126, -18.1093}, 
    extent = {{-4.25, -4}, {4.25, 4}})));
  Modelica.Electrical.Polyphase.Basic.Inductor Lf(L = fill(1e-5, 3)) 
    annotation(Placement(transformation(origin = {-16, 4}, 
    extent = {{-10, -10}, {10, 10}}, 
    rotation = -90)));
  TYWindPower.Environment.WindSource windSource 
    annotation(Placement(transformation(origin = {-208, 44.5}, 
    extent = {{-10, -10}, {10, 10}})));
  TYWindPower.Mechanics.GearBox gearBox(i_ba = 200) 
    annotation(Placement(transformation(origin = {-88, 40}, 
    extent = {{-10, -10}, {10, 10}})));
  TYWindPower.Mechanics.Coupling coupling 
    annotation(Placement(transformation(origin = {-117.5, 40}, 
    extent = {{-10, -10}, {10, 10}})));
  TYWindPower.Mechanics.Blade blade(w_t_output=true) 
    annotation(Placement(transformation(origin = {-159.917, 40}, 
    extent = {{-10, -10}, {10, 10}})));
  TYWindPower.Controllers.WindTurbines.PitchController pitchController(UserDefined=true,w_t_nom=0.3) 
    annotation(Placement(transformation(origin={-160,-78.359}, 
extent={{10,-10},{-10,10}})));
  TYWindPower.Sensors.MechanicalSensors.AbsoluteSensor absoluteSensor 
    annotation(Placement(transformation(origin={-138,52}, 
extent={{-8,8},{8,-8}}, 
rotation=90)));
  TYWindPower.PowerTransmissions.PowerGrid powerGrid(V = 690 * ones(3)) 
    annotation(Placement(transformation(origin = {144, 56}, 
    extent = {{10, -10}, {-10, 10}})));
  Modelica.Electrical.Polyphase.Sensors.CurrentSensor currentSensor1 
    annotation(Placement(transformation(origin={98,47}, 
extent={{5,5},{-5,-5}}, 
rotation=-270)));
  Modelica.Electrical.Polyphase.Sensors.PotentialSensor potentialSensor1 
    annotation(Placement(transformation(origin = {118, 11}, 
    extent = {{-5, -5}, {5, 5}}, 
    rotation = -90)));
  TYUtility.SignalRouting.Goto Ig_abc[3] 
    annotation(Placement(transformation(origin={83,46.9211}, 
extent={{3,-3},{-3,3}})), HideResult = true);
  TYUtility.SignalRouting.From from[3](redeclare connector OutputConnectorType =Modelica.Blocks.Interfaces.RealOutput, y = Ig_abc.u) 
    annotation(Placement(transformation(origin = {98, -69.279}, 
    extent = {{3, -3}, {-3, 3}})), HideResult = true);
  TYUtility.SignalRouting.Goto Udc 
    annotation(Placement(transformation(origin = {68.89075, 6}, 
    extent = {{-3, -3}, {3, 3}})), HideResult = true);
  TYUtility.SignalRouting.From from1(redeclare connector OutputConnectorType = Modelica.Blocks.Interfaces.RealOutput, y = Udc.u) 
    annotation(Placement(transformation(origin = {96, -76.079}, 
    extent = {{3, -3}, {-3, 3}})), HideResult = true);
  TYUtility.SignalRouting.Goto Im_abc[3] 
    annotation(Placement(transformation(origin = {-2, 28.9211}, 
    extent = {{-3, -3}, {3, 3}})), HideResult = true);
  TYUtility.SignalRouting.From from2[3](redeclare connector OutputConnectorType = Modelica.Blocks.Interfaces.RealOutput, y = Im_abc.u) 
    annotation(Placement(transformation(origin = {-4, -60.9595}, 
    extent = {{-3, -3}, {3, 3}})), HideResult = true);
  TYUtility.SignalRouting.From from3[3](redeclare connector OutputConnectorType =Modelica.Blocks.Interfaces.RealOutput, y = Ig_abc.u) 
    annotation(Placement(transformation(origin = {-12, -67.919}, 
    extent = {{-3, -3}, {3, 3}})), HideResult = true);
  TYUtility.SignalRouting.From from4(redeclare connector OutputConnectorType =Modelica.Blocks.Interfaces.RealOutput, y = theta_s.u) 
    annotation(Placement(transformation(origin = {-21, -71.359}, 
    extent = {{-3, -3}, {3, 3}})), HideResult = true);
  TYUtility.SignalRouting.Goto theta_s(redeclare Modelica.Blocks.Interfaces.RealInput u) 
    annotation(Placement(transformation(origin={124.75,-30}, 
extent={{3,-3},{-3,3}})), HideResult = true);
  TYWindPower.Sensors.MechanicalSensors.AbsoluteSensor absoluteSensor1 
    annotation(Placement(transformation(origin = {-56, 4}, 
    extent = {{-10, -10}, {10, 10}}, 
    rotation = -90)));
  Modelica.Electrical.Analog.Sensors.VoltageSensor voltageSensor 
    annotation(Placement(transformation(origin = {54, 1}, 
    extent = {{-5, 5}, {5, -5}})));
  Modelica.Electrical.Polyphase.Sensors.CurrentSensor currentSensor2 
    annotation(Placement(transformation(origin = {-16, 29}, 
    extent = {{-5, 5}, {5, -5}}, 
    rotation = 270)));
  Modelica.Blocks.Sources.RealExpression Vdref(y = 1200) 
    annotation(Placement(transformation(origin = {100, -61}, 
    extent = {{5, -6.05463}, {-5, 6.05463}})));
  Modelica.Blocks.Math.Gain gain(k=Modelica.Constants.pi*2) 
    annotation (Placement(transformation(origin={132.05465,-25.9453}, 
extent={{-2.05465,-2.05465},{2.05465,2.05465}}, 
rotation=-90)));
equation
  connect(resistor.plug_p, inductor.plug_n) 
    annotation(Line(origin={120.7415,-17.2903}, 
points={{-22.7415,35.2903},{-22.7415,31.2903}}, 
color={0,0,255}));
  connect(C.p, DCAC.pSupply) 
    annotation(Line(origin = {88.1664, 1.8856}, 
    points = {{-42.221025, -13.9403}, {-22.27565, -13.9403}, {-22.27565, -13.9949}}, 
    color = {0, 0, 255}));
  connect(DCAC.nSupply, C.n) 
    annotation(Line(origin = {88.1664, -16.1144}, 
    points = {{-22.27565, -7.9949}, {-42.221025, -7.9949}, {-42.221025, -8.17062}}, 
    color = {0, 0, 255}));
  connect(ACDC.pLoad, C.p) 
    annotation(Line(origin = {50.1664, -0.1144}, 
    points = {{-24.1664, -11.9949}, {-4.22103, -11.9949}, {-4.22103, -11.9403}}, 
    color = {0, 0, 255}));
  connect(ACDC.nLoad, C.n) 
    annotation(Line(origin = {50.1664, -17.1144}, 
    points = {{-24.1664, -6.9949}, {-4.22103, -6.9949}, {-4.22103, -7.17062}}, 
    color = {0, 0, 255}));
  connect(Lf.plug_n, ACDC.pSupply) 
    annotation(Line(origin = {4.1664, -9.1144}, 
    points = {{-20.1664, 3.1144}, {-20.1664, -8.9949}, {1.8336, -8.9949}}, 
    color = {0, 0, 255}));
  connect(gearBox.flange_a, coupling.flange_b) 
    annotation(Line(origin = {-6.8336, 58.5}, 
    points = {{-91.1664, -18.5}, {-100.6664, -18.5}}, 
    color = {0, 0, 0}));
  connect(windSource.windSpeed, blade.windSpeed) 
    annotation(Line(origin = {-169.8336, 58.5}, 
    points = {{-27.1664, -14}, {-1.5832, -14}}, 
    color = {0, 0, 127}));
  connect(pitchController.pitchAngle, blade.pitchAngle) 
    annotation(Line(origin={-151.8336,27.5}, 
points={{-19.1664,-105.859},{-30.1664,-105.859},{-30.1664,7.8},{-19.5834,7.8}}, 
color={0,0,127}));
  connect(absoluteSensor.flange, blade.flange) 
    annotation(Line(origin={-132.834,46.5}, 
points={{-5.166,-2.5},{-5.166,-6.5},{-17.183,-6.5}}, 
color={96,96,96}));
  connect(blade.flange, coupling.flange_a) 
    annotation(Line(origin = {-109.834, 58.5}, 
    points = {{-40.1828, -18.5}, {-17.666, -18.5}}, 
    color = {96, 96, 96}));
  connect(gearBox.flange_b, DFIG.flange) 
    annotation(Line(origin = {-51, 40.5}, 
    points = {{-27, -0.5}, {3, -0.5}, {3, -0.5}}, 
    color = {0, 0, 0}));
  connect(currentSensor2.plug_n, Lf.plug_p) 
    annotation(Line(origin = {-21, 21}, 
    points = {{5, 3}, {5, -7}}, 
    color = {0, 0, 255}));
  connect(inductor.plug_p, DCAC.pload) 
    annotation(Line(origin={98,-25}, 
points={{0,19},{0,6.8907},{-12.1093,6.8907}}, 
color={0,0,255}));
  connect(resistor.plug_n, currentSensor1.plug_n) 
    annotation(Line(origin={135,48}, 
points={{-37,-10},{-37,-6}}, 
color={0,0,255}));
  connect(DFIG.plug_sp, powerGrid.plug_p) 
    annotation(Line(origin={78,56}, 
points={{-116,-5.6},{-116,0},{55.6,0}}, 
color={0,0,255}));
  connect(potentialSensor1.plug_p, powerGrid.plug_p) 
    annotation(Line(origin = {145, 35}, 
    points = {{-27, -19}, {-27, 21}, {-11.4, 21}}, 
    color = {0, 0, 255}));
  connect(potentialSensor1.phi, pLL.Uabc) 
    annotation(Line(origin = {120, -1}, 
    points = {{-2, 6.5}, {-2, -17.1093}, {0.9, -17.1093}}, 
    color = {0, 0, 127}));
  connect(GSCtrl.is_abc, from.y) 
    annotation(Line(origin = {90, -63}, 
    points = {{-3.10925, -6.3195}, {4.52, -6.3195}}, 
    color = {0, 0, 127}));
  connect(GSCtrl.Us_abc, potentialSensor1.phi) 
    annotation(Line(origin = {102, -25}, 
    points = {{-15.1093, -46.1195}, {16, -46.1195}, {16, 30.5}}, 
    color = {0, 0, 127}));
  connect(from1.y, GSCtrl.Udc) 
    annotation(Line(origin = {90, -76.5195}, 
    points = {{2.52, 0.399959}, {-3.10925, 0.399959}, {-3.10925, 0.4}}, 
    color = {0, 0, 127}));
  connect(pLL.Theta, GSCtrl.theta_s) 
    annotation(Line(origin = {109, -41}, 
    points = {{21.675, 24.4907}, {27, 24.4907}, {27, -40.1195}, {-22.1093, -40.1195}}, 
    color = {0, 0, 127}));
  connect(GSCtrl.fire_p, DCAC.fire_p) 
    annotation(Line(origin = {65, -48}, 
    points = {{-0.10925, -27.5862}, {-5, -27.5862}, {-5, 4}, {4.89075, 4}, {4.89075, 17.8907}}, 
    color = {255, 0, 255}));
  connect(GSCtrl.fire_n, DCAC.fire_n) 
    annotation(Line(origin = {71, -52}, 
    points = {{-6.10925, -27.7195}, {-11, -27.7195}, {-11, 8}, {10.8907, 8}, {10.8907, 21.8907}}, 
    color = {255, 0, 255}));
  connect(MSCtrl.fire_p, ACDC.fire_p) 
    annotation(Line(origin = {23, -43}, 
    points = {{4, -25.3195}, {13, -25.3195}, {13, -1}, {-13, -1}, {-13, 12.8907}}, 
    color = {255, 0, 255}));
  connect(MSCtrl.fire_n, ACDC.fire_n) 
    annotation(Line(origin = {29, -49}, 
    points = {{-2, -30.3195}, {7, -30.3195}, {7, 5}, {-7, 5}, {-7, 18.8907}}, 
    color = {255, 0, 255}));
  connect(currentSensor2.plug_p, DFIG.plug_rp) 
    annotation(Line(origin = {-21, 36}, 
    points = {{5, -2}, {5, 4}, {-6, 4}}, 
    color = {0, 0, 255}));
  connect(from2.y, MSCtrl.ir_abc) 
    annotation(Line(origin={2,-61}, 
points={{-2.52,-4.05405e-5},{0,-4.05405e-5},{0,-3.5195},{3,-3.5195}}, 
color={0,0,127}));
  connect(MSCtrl.is_abc, from3.y) 
    annotation(Line(origin = {-2, -64}, 
    points = {{7, -3.9595}, {-6.52, -3.9595}, {-6.52, -3.95954}}, 
    color = {0, 0, 127}));
  connect(absoluteSensor1.flange, DFIG.flange) 
    annotation(Line(origin = {-52, 27}, 
    points = {{-4, -13}, {-4, 13}, {4, 13}}, 
    color = {96, 96, 96}));
  connect(absoluteSensor1.phi, MSCtrl.theta_r) 
    annotation(Line(origin = {-23, -34}, 
    points = {{-27, 27}, {-27, -40.8395}, {28, -40.8395}}, 
    color = {0, 0, 127}));
  connect(voltageSensor.p, C.p) 
    annotation(Line(origin = {46, 1}, 
    points = {{3, 0}, {-0.054625, 0}, {-0.054625, -13.0547}}, 
    color = {0, 0, 255}));
  connect(voltageSensor.n, C.n) 
    annotation(Line(origin = {53, -5}, 
    points = {{6, 6}, {6, -19.285}, {-7.05463, -19.285}}, 
    color = {0, 0, 255}));
  connect(voltageSensor.v, Udc.u) 
    annotation(Line(origin = {58, 10}, 
    points = {{-4, -3.5}, {7.29075, -3.5}, {7.29075, -3.92105}}, 
    color = {0, 0, 127}));
  connect(currentSensor2.i, Im_abc.u) 
    annotation(Line(origin = {-8, 29}, 
    points = {{-2.5, 0}, {2.4, 0}, {2.4, 4.73684e-5}}, 
    color = {0, 0, 127}));
  connect(blade.w_t, pitchController.w_t) 
    annotation(Line(origin={-173,22}, 
points={{24.083,14.45},{33,14.45},{33,-100.359},{25,-100.359}}, 
color={0,0,127}));
  connect(GSCtrl.Vdcref, Vdref.y) 
    annotation(Line(origin = {91, -63}, 
    points = {{-4.10925, -2.1195}, {1, -2.1195}, {1, 2}, {3.5, 2}}, 
    color = {0, 0, 127}));
  connect(currentSensor1.plug_p, powerGrid.plug_p) 
  annotation(Line(origin={116,55}, 
points={{-18,-3},{-18,1},{17.6,1}}, 
color={0,0,255}));
  connect(currentSensor1.i, Ig_abc.u) 
  annotation(Line(origin={90,47}, 
  points={{2.5,0},{-3.4,0}}, 
  color={0,0,127}));
  connect(GSCtrl.Q, MSCtrl.Qs) 
  annotation(Line(origin={37,-81}, 
  points={{27.8907,9.54717},{15,9.54717},{15,-9},{-28.6,-9},{-28.6,-3.5195}}, 
  color={0,0,127}));
  connect(Pref.y, MSCtrl.Ps_ref) 
  annotation(Line(origin={2,-82}, 
  points={{-2.7,0.2805},{3,0.2805}}, 
  color={0,0,127}));
  connect(GSCtrl.P, MSCtrl.Ps) 
  annotation(Line(origin={33,-79}, 
  points={{31.8907,11.6805},{17,11.6805},{17,-11},{-31,-11},{-31,0.7205},{-28,0.7205}}, 
  color={0,0,127}));
  connect(pLL.f, gain.u) 
  annotation(Line(origin={131,-22}, 
  points={{-0.325,2.2107},{1.05465,2.2107},{1.05465,-1.47977}}, 
  color={0,0,127}));
  connect(gain.y, theta_s.u) 
  annotation(Line(origin={130,-29}, 
  points={{2.05465,0.794535},{2.05465,-0.921053},{-1.65,-0.921053}}, 
  color={0,0,127}));
  connect(from4.y, MSCtrl.Ws) 
  annotation(Line(origin={-6,-71}, 
  points={{-11.52,-0.399541},{11,-0.399541},{11,-0.3995}}, 
  color={0,0,127}));
  end DFIG_GSC;