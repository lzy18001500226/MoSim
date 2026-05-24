model FullBridgeLLC "全桥LLC电路"
  //参数

  annotation(Icon(coordinateSystem(extent = {{-100, -100}, {100, 100}}, 
    grid = {2, 2}), graphics = {Polygon(origin = {-3.55271e-15, 27}, 
    lineColor = {85, 0, 255}, 
    fillColor = {85, 0, 255}, 
    fillPattern = FillPattern.Solid, 
    points = {{-64, 1}, {0, 37}, {64, 1}, {0, -37}}), Line(origin = {3.55271e-15, -18}, 
    points = {{-62, 18}, {0, -18}, {62, 18}}, 
    color = {85, 0, 255}, 
    thickness = 5), Line(origin = {1.06581e-14, -46}, 
    points = {{-62, 18}, {0, -18}, {62, 18}}, 
    color = {85, 0, 255}, 
    thickness = 5)}), Diagram(coordinateSystem(extent={{-300,-190},{340,200}}, 
grid={2,2})), 
experiment(Algorithm=Dassl,InlineIntegrator=false,InlineStepSize=false,Interval=1e-06,StartTime=0,StopTime=0.005,Tolerance=0.0001), 
__MWORKS(ContinueSimConfig(SaveContinueFile="false",SaveBeforeStop="false",NumberBeforeStop=1,FixedContinueInterval="false",ContinueIntervalLength=0.005,ContinueTimeVector),ResultViewerManager(resultViewers={
ResultViewer(name="1", executeTrigger=executeTrigger.SimulationFinished, commands={
CreatePlot(id=1, position=[0, 28, 2029, 790], y=["Voltage.v"], x_display_unit="s", y_display_units=["V"], y_axis=[1], legend_layout=7, legend_frame=True, left_title="[V]", fix_time_range_value=6.95225e-310), 
CreatePlot(id=1, position=[0, 28, 2029, 790], y=["resistor2.v"], x_display_unit="s", y_display_units=["V"], y_axis=[1], legend_layout=7, legend_frame=True, left_title="[V]", fix_time_range_value=6.95225e-310, sub_plot=[2, 1])})
})), 
Documentation(link="modelica://TYElectrical/Resources/Example/FullBridgeLLC.html"));
  TYElectrical.Semiconductors.NchannelMOSFET mos1(Ciss = 3900e-12, Crss = 320e-12, Coss = 760e-12, ParamMode = 1, vth = 2, Rds_on = 0.054, Id_on = 25, Vgs_on = 16) 
    annotation(Placement(transformation(origin={-123.662,66.1321}, 
extent={{-10,-10},{10,10}})));
  TYElectrical.Semiconductors.NchannelMOSFET mos2(Ciss = 3900e-12, Crss = 320e-12, Coss = 760e-12, ParamMode = 1, vth = 2, Rds_on = 0.054, Id_on = 25, Vgs_on = 16) 
    annotation(Placement(transformation(origin={-48.6616,68.1321}, 
extent={{-10,-10},{10,10}})));
  TYElectrical.Semiconductors.NchannelMOSFET mos3(Ciss = 3900e-12, Crss = 320e-12, Coss = 760e-12, ParamMode = 1, vth = 2, Rds_on = 0.054, Id_on = 25, Vgs_on = 16) 
    annotation(Placement(transformation(origin={-123.662,-15.8677}, 
extent={{-10,-10},{10,10}})));
  TYElectrical.Semiconductors.NchannelMOSFET mos4(Ciss = 3900e-12, Crss = 320e-12, Coss = 760e-12, ParamMode = 1, vth = 2, Rds_on = 0.054, Id_on = 25, Vgs_on = 16) 
    annotation(Placement(transformation(origin={-48.6616,-13.8677}, 
extent={{-10,-10},{10,10}})));
  TYElectrical.BasicComponents.IdealBasicComponents.Capacitor capacitor(C(displayUnit = "uF") = 0.00047) 
    annotation(Placement(transformation(origin={-231.662,24.1325}, 
extent={{-10,-10},{10,10}}, 
rotation=270)));
  TYElectrical.Sources.VoltageSources.PiecewiseLinearVoltageSource Voltage(table = {{0, 0}, {0.001, 40}, {1, 40}}) 
    annotation(Placement(transformation(origin={-259.662,24.1325}, 
extent={{-10,-10},{10,10}}, 
rotation=270)));
  TYElectrical.BasicComponents.IdealBasicComponents.Capacitor capacitor1(C(displayUnit = "uF") = 2e-5) 
    annotation(Placement(transformation(origin={-197.86558,24.3425}, 
extent={{-10,-10},{10,10}}, 
rotation=270)));
  TYElectrical.BasicComponents.IdealBasicComponents.Inductor inductor(L = 44e-6) 
    annotation(Placement(transformation(origin={-213.662,100.132}, 
extent={{-10,-10},{10,10}})));
  Modelica.Electrical.Analog.Basic.Ground ground 
    annotation(Placement(transformation(origin={-259.662,-87.8682}, 
extent={{-10,-10},{10,10}})));
  TYElectrical.BasicComponents.IdealBasicComponents.Inductor inductor1(L = 50e-6) 
    annotation(Placement(transformation(origin={22.3106,18.1288}, 
extent={{-10,-10},{10,10}}, 
rotation=270)));
  TYElectrical.BasicComponents.IdealBasicComponents.Capacitor capacitor2(C(displayUnit = "uF") = 3e-7) 
    annotation(Placement(transformation(origin={-83.23942,7.6946}, 
extent={{10,-10},{-10,10}}, 
rotation=-360)));
  TYElectrical.BasicComponents.IdealBasicComponents.Inductor inductor2(L = 7.5e-6) 
    annotation(Placement(transformation(origin={-20,27.7061}, 
extent={{-10,-10},{10,10}}, 
rotation=360)));
  Modelica.Blocks.Sources.Pulse pulse(period = 1 / 85000, amplitude = 12, width = 50) 
    annotation(Placement(transformation(origin={-177.66158,54.1325}, 
extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Sources.Pulse pulse1(period = 1 / 85000, amplitude = 12, width = 50) 
    annotation(Placement(transformation(origin={-89.6616,-27.8677}, 
extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Sources.Pulse pulse2(period = 1 / 85000, amplitude = 12, startTime = 1 / 85000 * 0.5, width = 50) 
    annotation(Placement(transformation(origin={-177.66158,-29.8677}, 
extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Sources.Pulse pulse3(period = 1 / 85000, amplitude = 12, startTime = 1 / 85000 * 0.5, width = 50) 
    annotation(Placement(transformation(origin={-89.6616,54.1325}, 
extent={{-10,-10},{10,10}})));
  Modelica.Electrical.Analog.Sources.SignalVoltage signalVoltage 
    annotation(Placement(transformation(origin={-148.66158,54.1325}, 
extent={{-10,10},{10,-10}}, 
rotation=-90)));
  Modelica.Electrical.Analog.Sources.SignalVoltage signalVoltage1 
    annotation(Placement(transformation(origin={-148.66158,-29.8677}, 
extent={{-10,10},{10,-10}}, 
rotation=-90)));
  Modelica.Electrical.Analog.Sources.SignalVoltage signalVoltage2 
    annotation(Placement(transformation(origin={-60.661,-27.8677}, 
extent={{-10,10},{10,-10}}, 
rotation=-90)));
  Modelica.Electrical.Analog.Sources.SignalVoltage signalVoltage3 
    annotation(Placement(transformation(origin={-60.661,54.1325}, 
extent={{-10,10},{10,-10}}, 
rotation=-90)));
  TYElectrical.BasicComponents.IdealBasicComponents.IdealTransformer idealTransformer(n = 5/12) 
    annotation(Placement(transformation(origin={86.1185,89.7061}, 
extent={{-10,-10},{10,10}})));
  TYElectrical.BasicComponents.IdealBasicComponents.Diode diode(v_f = 2, R_on = 1.5) 
    annotation(Placement(transformation(origin={123.9964,125.475}, 
extent={{-10,-10},{10,10}}, 
rotation=90)));
  TYElectrical.BasicComponents.IdealBasicComponents.Capacitor capacitor3(C(displayUnit = "uF") = 0.47e-6) 
    annotation(Placement(transformation(origin={149.623,126.39}, 
extent={{-10,-10},{10,10}}, 
rotation=270)));
  TYElectrical.BasicComponents.IdealBasicComponents.Diode diode1(v_f = 2, R_on = 1.5) 
    annotation(Placement(transformation(origin={123.9964,52.4091}, 
extent={{-10,-10},{10,10}}, 
rotation=90)));
  TYElectrical.BasicComponents.IdealBasicComponents.Capacitor capacitor4(C(displayUnit = "uF") = 0.47e-6) 
    annotation(Placement(transformation(origin={149.623,53.3241}, 
extent={{-10,-10},{10,10}}, 
rotation=270)));
  TYElectrical.BasicComponents.IdealBasicComponents.Inductor inductor3(L = 44e-6) 
    annotation(Placement(transformation(origin={183.871,156.093}, 
extent={{-10,-10},{10,10}}, 
rotation=360)));
  TYElectrical.BasicComponents.IdealBasicComponents.Capacitor capacitor5(C(displayUnit = "uF") = 2.5e-7) 
    annotation(Placement(transformation(origin={214,21.1691}, 
extent={{-10,-10},{10,10}}, 
rotation=270)));
  TYElectrical.BasicComponents.IdealBasicComponents.IdealTransformer idealTransformer1(n = 5/12) 
    annotation(Placement(transformation(origin={86.1185,-61.8493}, 
extent={{-10,-10},{10,10}})));
  TYElectrical.BasicComponents.IdealBasicComponents.Diode diode2(v_f = 2, R_on = 1.5) 
    annotation(Placement(transformation(origin={124.24,-26.9165}, 
extent={{-10,-10},{10,10}}, 
rotation=90)));
  TYElectrical.BasicComponents.IdealBasicComponents.Capacitor capacitor6(C(displayUnit = "uF") = 0.47e-6) 
    annotation(Placement(transformation(origin={149.867,-26.0013}, 
extent={{-10,-10},{10,10}}, 
rotation=270)));
  TYElectrical.BasicComponents.IdealBasicComponents.Diode diode3(v_f = 2, R_on = 1.5) 
    annotation(Placement(transformation(origin={124.24,-99.9826}, 
extent={{-10,-10},{10,10}}, 
rotation=90)));
  TYElectrical.BasicComponents.IdealBasicComponents.Capacitor capacitor7(C(displayUnit = "uF") = 0.47e-6) 
    annotation(Placement(transformation(origin={149.867,-99.0676}, 
extent={{-10,-10},{10,10}}, 
rotation=270)));
  TYElectrical.BasicComponents.IdealBasicComponents.Resistor resistor(R = 328e3) 
    annotation(Placement(transformation(origin={242.53461,21.1691}, 
extent={{-10,-10},{10,10}}, 
rotation=270)));
  TYElectrical.BasicComponents.IdealBasicComponents.Resistor resistor2(R=750) 
    annotation(Placement(transformation(origin={271.06922,22.7331}, 
extent={{-10,-10},{10,10}}, 
rotation=270)));
  Modelica.Electrical.Analog.Basic.Ground ground1 
    annotation(Placement(transformation(origin={271.14822,-156.681}, 
extent={{-10,-10},{10,10}})));
  equation
  connect(mos1.S, mos3.D) 
    annotation(Line(origin={-113.662,34.1325}, 
points={{0.08,25.9414},{0.08,-44.1457},{0.130909,-44.1457}}, 
color={0,0,255}));
  connect(mos2.S, mos4.D) 
    annotation(Line(origin={-50.6614,36.1325}, 
points={{12.0798,25.9414},{12.0798,-44.1457},{12.1307,-44.1457}}, 
color={0,0,255}));
  connect(capacitor.p, Voltage.p) 
    annotation(Line(origin={-224.662,72.1321}, 
points={{-7.05421,-37.8972},{-7.05421,28},{-35.0542,28},{-35.0542,-37.8972}}, 
color={0,0,255}));
  connect(capacitor.n, Voltage.n) 
    annotation(Line(origin={-224.662,-17.8677}, 
points={{-6.98643,31.8714},{-6.98643,-40},{-34.9864,-40},{-34.9864,31.8714}}, 
color={0,0,255}));
  connect(mos3.S, Voltage.n) 
    annotation(Line(origin={-211.66158,-20.8677}, 
points={{98.08,-1.05818},{98.08,-37},{-47.9869,-37},{-47.9869,34.8714}}, 
color={0,0,255}));
  connect(capacitor1.n, Voltage.n) 
    annotation(Line(origin={-217.662,-21.8677}, 
points={{19.81,36.0814},{19.81,-36},{-41.9864,-36},{-41.9864,35.8714}}, 
color={0,0,255}));
  connect(inductor.p, Voltage.p) 
    annotation(Line(origin={-238.662,67.1321}, 
points={{14.8976,32.9458},{-21.0542,32.9458},{-21.0542,-32.8972}}, 
color={0,0,255}));
  connect(inductor.n, mos1.D) 
    annotation(Line(origin={-167.66158,87.1321}, 
points={{-35.8716,13.0136},{54.1309,13.0136},{54.1309,-15.1455}}, 
color={0,0,255}));
  connect(mos2.D, inductor.n) 
    annotation(Line(origin={-138.66158,87.1321}, 
points={{100.131,-13.1455},{100.131,13.0136},{-64.8716,13.0136}}, 
color={0,0,255}));
  connect(mos4.S, Voltage.n) 
    annotation(Line(origin={-171.66158,-26.8677}, 
points={{133.08,6.94182},{133.08,-31},{-87.9869,-31},{-87.9869,40.8714}}, 
color={0,0,255}));
  connect(ground.p, Voltage.n) 
    annotation(Line(origin={-259.662,-31.8677}, 
points={{0,-46.0005},{0,45.8714},{0.0135696,45.8714}}, 
color={0,0,255}));
  connect(capacitor1.p, inductor.n) 
    annotation(Line(origin={-189.66158,67.1321}, 
points={{-8.25821,-32.6872},{-8.25821,33.0136},{-13.8716,33.0136}}, 
color={0,0,255}));
  connect(inductor2.p, mos2.S) 
    annotation(Line(origin={-24.6616,42.1325}, 
points={{-5.44076,-14.4806},{-13.92,-14.4806},{-13.92,19.9414}}, 
color={0,0,255}));
  connect(inductor2.n, inductor1.p) 
    annotation(Line(origin={75.0941,169.347}, 
points={{-84.9653,-141.627},{-52.8377,-141.627},{-52.8377,-141.116}}, 
color={0,0,255}));
  connect(capacitor2.n, mos3.D) 
    annotation(Line(origin={-57.661,-5.8674}, 
points={{-35.7072,13.5756},{-55.8697,13.5756},{-55.8697,-4.14575}}, 
color={0,0,255}));
  connect(inductor1.n, capacitor2.p) 
    annotation(Line(origin={75.0941,146.347}, 
points={{-52.7699,-138.347},{-148.231,-138.347},{-148.231,-138.707}}, 
color={0,0,255}));
  connect(pulse.y, signalVoltage.v) 
    annotation(Line(origin={-158.66158,66.1321}, 
points={{-8,-11.9996},{-2,-11.9996}}, 
color={0,0,127}));
  connect(signalVoltage.p, mos1.G) 
    annotation(Line(origin={-141.66158,65.1321}, 
points={{-7,-0.9996},{-7,1},{7.97091,1}}, 
color={0,0,255}));
  connect(signalVoltage.n, mos1.S) 
    annotation(Line(origin={-130.66158,50.1325}, 
points={{-18,-6},{-18,-10},{17.08,-10},{17.08,9.94142}}, 
color={0,0,255}));
  connect(signalVoltage1.p, mos3.G) 
    annotation(Line(origin={-141.66158,-17.8677}, 
points={{-7,-2},{-7,2},{7.97091,2}}, 
color={0,0,255}));
  connect(signalVoltage1.n, mos3.S) 
    annotation(Line(origin={-130.66158,-32.8677}, 
points={{-18,-7},{-18,-11},{17.08,-11},{17.08,10.9418}}, 
color={0,0,255}));
  connect(pulse2.y, signalVoltage1.v) 
    annotation(Line(origin={-163.66158,-29.8677}, 
points={{-3,0},{3,0}}, 
color={0,0,127}));
  connect(signalVoltage3.p, mos2.G) 
    annotation(Line(origin={-59.661,63.1321}, 
points={{-1,1.0004},{-1,5},{0.970309,5}}, 
color={0,0,255}));
  connect(signalVoltage3.n, mos2.S) 
    annotation(Line(origin={-49.6616,48.1325}, 
points={{-10.9994,-4},{-10.9994,-13},{11.08,-13},{11.08,13.9414}}, 
color={0,0,255}));
  connect(signalVoltage3.v, pulse3.y) 
    annotation(Line(origin={-75.661,48.1325}, 
points={{3,6},{-3.00058,6}}, 
color={0,0,127}));
  connect(pulse1.y, signalVoltage2.v) 
    annotation(Line(origin={-75.661,-27.8677}, 
points={{-3.00058,0},{3,0}}, 
color={0,0,127}));
  connect(signalVoltage2.p, mos4.G) 
    annotation(Line(origin={-59.661,-15.8677}, 
points={{-1,-2},{-1,2},{0.970309,2}}, 
color={0,0,255}));
  connect(signalVoltage2.n, mos4.S) 
    annotation(Line(origin={-49.6616,-30.8677}, 
points={{-10.9994,-7},{-10.9994,-10},{11.08,-10},{11.08,10.9418}}, 
color={0,0,255}));
  connect(diode.p, diode1.n) 
    annotation(Line(origin={123.7438,100.628}, 
points={{0.306807,14.7446},{0.306807,-38.0902},{0.23903,-38.0902}}, 
color={0,0,255}));
  connect(capacitor3.n, capacitor4.p) 
    annotation(Line(origin={149.744,101.628}, 
points={{-0.10743,14.6332},{-0.10743,-38.2016},{-0.175207,-38.2016}}, 
color={0,0,255}));
  connect(idealTransformer.p2, diode.p) 
    annotation(Line(origin={112.7438,106.628}, 
points={{-16.6253,-6.922},{11.3068,-6.922},{11.3068,8.74464}}, 
color={0,0,255}));
  connect(inductor3.p, diode.n) 
    annotation(Line(origin={150.744,145.628}, 
points={{23.0246,10.4108},{-26.7612,10.4108},{-26.7612,-10.0242}}, 
color={0,0,255}));
  connect(capacitor5.p, inductor3.n) 
    annotation(Line(origin={196.744,131.628}, 
points={{17.2018,-100.357},{17.2018,24.4786},{-2.7442,24.4786}}, 
color={0,0,255}));
  connect(diode2.p, diode3.n) 
    annotation(Line(origin={123.987,-51.7636}, 
points={{0.306807,14.7447},{0.306807,-38.0902},{0.23903,-38.0902}}, 
color={0,0,255}));
  connect(capacitor6.n, capacitor7.p) 
    annotation(Line(origin={149.988,-50.7636}, 
points={{-0.10743,14.6335},{-0.10743,-38.2016},{-0.175207,-38.2016}}, 
color={0,0,255}));
  connect(capacitor7.n, diode3.p) 
    annotation(Line(origin={136.6824,-115.255}, 
points={{13.1982,6.0582},{13.1982,-10.5613},{-12.3881,-10.5613},{-12.3881,5.16964}}, 
color={0,0,255}));
  connect(idealTransformer1.p2, diode2.p) 
    annotation(Line(origin={112.1753,-42.5146}, 
points={{-16.0568,-9.3347},{12.119,-9.3347},{12.119,5.49574}}, 
color={0,0,255}));
  connect(idealTransformer1.p1, inductor1.p) 
    annotation(Line(origin={76.4147,67.1481}, 
points={{-0.2962,-118.9974},{-16.4147,-118.9974},{-16.4147,-38.9169},{-54.1583,-38.9169}}, 
color={0,0,255}));
  connect(capacitor4.n, capacitor6.p) 
    annotation(Line(origin={149.171,15.2154}, 
points={{0.46557,27.9799},{0.46557,-31.1143},{0.641793,-31.1143}}, 
color={0,0,255}));
  connect(diode1.p, capacitor4.n) 
    annotation(Line(origin={137.1705,43.2151}, 
points={{-13.1199,-0.908362},{-13.1199,-11.8721},{12.4661,-11.8721},{12.4661,-0.0198033}}, 
color={0,0,255}));
  connect(diode2.n, capacitor6.p) 
    annotation(Line(origin={137.1705,-1.7849}, 
points={{-12.944,-15.0028},{-12.944,-0.12692},{12.6423,-0.12692},{12.6423,-14.114}}, 
color={0,0,255}));
  connect(idealTransformer1.n2, capacitor6.n) 
    annotation(Line(origin={125.1705,-53.7846}, 
points={{-29.052,-18.0647},{24.7101,-18.0647},{24.7101,17.6545}}, 
color={0,0,255}));
  connect(idealTransformer.n2, capacitor3.n) 
    annotation(Line(origin={127.1705,97.2151}, 
points={{-31.052,-17.509},{22.4661,-17.509},{22.4661,19.0462}}, 
color={0,0,255}));
  connect(capacitor3.p, inductor3.p) 
    annotation(Line(origin={161.171,146.215}, 
points={{-11.6022,-9.72264},{-11.6022,9.82379},{12.5976,9.82379}}, 
color={0,0,255}));
  connect(resistor.p, inductor3.n) 
    annotation(Line(origin={215.17022,98.2151}, 
points={{27.3102,-66.9436},{27.3102,57.8916},{-21.1704,57.8916}}, 
color={0,0,255}));
  connect(capacitor5.n, capacitor7.n) 
    annotation(Line(origin={176.171,-54.7846}, 
points={{37.8426,65.8249},{37.8426,-70.5941},{-26.2904,-70.5941},{-26.2904,-54.4118}}, 
color={0,0,255}));
  connect(resistor.n, capacitor5.n) 
    annotation(Line(origin={219.17022,18.2154}, 
points={{23.378,-7.1751},{23.378,-143.901},{-5.15665,-143.901},{-5.15665,-7.1751}}, 
color={0,0,255}));
  connect(resistor2.p, inductor3.n) 
    annotation(Line(origin={232.17022,96.2151}, 
points={{38.8448,-63.3796},{38.8448,59.8916},{-38.1704,59.8916}}, 
color={0,0,255}));
  connect(ground1.p, resistor2.n) 
    annotation(Line(origin={271.17022,-64.7846}, 
points={{-0.022,-81.8963},{-0.022,77.3889},{-0.0874304,77.3889}}, 
color={0,0,255}));
  connect(resistor2.n, capacitor7.n) 
    annotation(Line(origin={210.17022,-46.7846}, 
points={{60.9126,59.3889},{60.9126,-79.0918},{-60.2897,-79.0918},{-60.2897,-62.4118}}, 
color={0,0,255}));
  connect(idealTransformer.p1, inductor1.p) 
    annotation(Line(origin={51.4844,105.789}, 
points={{24.6341,-6.083},{-29.228,-6.083},{-29.228,-77.5579}}, 
color={0,0,255}));
  connect(idealTransformer1.n1, inductor1.n) 
    annotation(Line(origin={50.4844,8.7891}, 
points={{25.6341,-80.6384},{-28.1603,-80.6384},{-28.1603,-0.789103}}, 
color={0,0,255}));
  connect(idealTransformer.n1, inductor1.n) 
    annotation(Line(origin={73.2402,3.8561}, 
points={{2.8783,75.85},{-25.2402,75.85},{-25.2402,4.1439},{-50.916,4.1439}}, 
color={0,0,255}));

end FullBridgeLLC;