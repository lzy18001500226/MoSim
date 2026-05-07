model System1 "5节点系统"
  annotation(Documentation(link = "modelica://TYElectricPower/Resources/HTML/System1.html"), Protection(access = Access.nonPackageDuplicate));
  import Modelica.Constants.pi;
  extends TYElectricPower.Icons.Example;
  annotation(Icon(coordinateSystem(extent = {{-100.0, -100.0}, {100.0, 100.0}}, 
    grid = {2.0, 2.0})), 
    Diagram(coordinateSystem(extent = {{-150.0, -100.0}, {150.0, 100.0}}, 
    grid = {2.0, 2.0})), 
    experiment(Algorithm = Dassl, Interval = 0.001, StartTime = 0, StopTime = 0.2, Tolerance = 0.0001), 

    Documentation(info = "<html><p>
该案例为电力系统两机五节点系统模型，两台发电机作为整个系统的电能来源，分别经过变压器、母线、线路等模型，对电能进行变换与分配，为下游负荷供电。
</p>
</html>"), __MWORKS(ContinueSimConfig(SaveContinueFile = "false", SaveBeforeStop = "false", NumberBeforeStop = 1, FixedContinueInterval = "false", ContinueIntervalLength = 0.001, ContinueTimeVector),ResultViewerManager(resultViewers={
ResultViewer(name="典型曲线", executeTrigger=executeTrigger.SimulationFinished, commands={
CreatePlot(id=1, x_display_unit="s", legend_layout=1, left_title_type=2, left_title="电压/V", bottom_title_type=2, bottom_title="时间/s", right_title_type=2, fix_time_range_value=0, zoom_x=(0, 0.2), zoom_y_l=(-15000, 15000)), 
Plot(y=["generator.PowerSupply.pin[1].v", "generator.PowerSupply.pin[2].v", "generator.PowerSupply.pin[3].v"], colors=["4278190335", "4294901760", "4278222848"]), 
CreatePlot(id=-1, x_display_unit="s", legend_layout=1, left_title_type=2, left_title="有功[W]", bottom_title_type=2, bottom_title="时间/s", right_title_type=2, right_title="无功[var]", fix_time_range_value=0, sub_plot=(2, 1), zoom_x=(0, 0.2), zoom_y_l=(-1000, 5000), zoom_y_r=(-1000, 2000)), 
Plot(y=["transformer.powerSensor.P", "transformer.powerSensor.Q"], colors=["4278190335", "4294901760"])})
})));
  TYElectricPower.Primary.Bus bus1(swing_voltage = 220) 
    annotation(Placement(transformation(origin = {-37.89588, 32.031618073642655}, 
    extent = {{-10, -10}, {9.89588, 10.0402}})));
  TYElectricPower.Basic.Common.Impedance impedance(R = 10.58, X = 0.1263) 
    annotation(Placement(transformation(origin = {3.999999999999999, 32.73161807364266}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYElectricPower.Load.StLoad stLoad(P = 2e3, 
    Vnominal = 220, Qc = 0, Ql = 1e3) annotation(Placement(transformation(origin = {-56, 9.255572}, 
    extent = {{6, -6}, {-6, 6}})));
  TYElectricPower.Primary.Bus bus2(swing_voltage = 220) 
    annotation(Placement(transformation(origin = {48.10412, 32.0632361472853}, 
    extent = {{-10, -10}, {9.89588, 10.0402}})));
  Modelica.Electrical.Polyphase.Basic.Capacitor C1(C = fill(1.2e-5, 3)) 
    annotation(Placement(transformation(origin = {-13.999999999999996, 24.0}, 
    extent = {{-6.0, -6.0}, {6.0, 6.0}}, 
    rotation = -90.0)));
  Modelica.Electrical.Polyphase.Basic.Capacitor C2(C = fill(1.2e-5, 3)) 
    annotation(Placement(transformation(origin = {21.999999999999986, 23.999999999999993}, 
    extent = {{-6.0, -6.0}, {6.0, 6.0}}, 
    rotation = -90.0)));
  Modelica.Electrical.Polyphase.Basic.Star star 
    annotation(Placement(transformation(origin = {-13.999999999999996, 11.627786000000004}, 
    extent = {{-3.627785999999997, -3.5}, {3.627786000000004, 3.5}}, 
    rotation = -90.0)));
  Modelica.Electrical.Analog.Basic.Ground ground 
    annotation(Placement(transformation(origin = {-14.000000000000004, -0.5000000000000018}, 
    extent = {{-3.500000000000001, -3.5}, {3.5, 3.5}})));
  Modelica.Electrical.Polyphase.Basic.Star star1 
    annotation(Placement(transformation(origin = {21.999999999999986, 11.627786000000004}, 
    extent = {{-3.627785999999997, -3.5}, {3.627786000000004, 3.5}}, 
    rotation = -90.0)));
  Modelica.Electrical.Analog.Basic.Ground ground1 
    annotation(Placement(transformation(origin = {21.99999999999998, -0.49999999999999645}, 
    extent = {{-3.500000000000001, -3.5}, {3.5, 3.5}})));
  TYElectricPower.Basic.Common.Impedance impedance1(R = 10.58, X = 0.1263) 
    annotation(Placement(transformation(origin = {-28.500000000000014, -28.50000000000001}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
    rotation = -90.0)));
  TYElectricPower.Primary.Bus bus3 
    annotation(Placement(transformation(origin = {94.0, 31.4632361472853}, 
    extent = {{-10.0, -10.0}, {9.89588, 10.0402}})));
  TYElectricPower.Primary.Bus bus4 
    annotation(Placement(transformation(origin = {7.45979999999998, -70.0}, 
    extent = {{-10.0, -10.0}, {9.89588, 10.0402}}, 
    rotation = -90.0)));
  TYElectricPower.Basic.Common.Impedance impedance2(R = 10.58, X = 0.1263) 
    annotation(Placement(transformation(origin = {42.000000000000014, -28.500000000000007}, 
    extent = {{10.0, -10.0}, {-10.0, 10.0}}, 
    rotation = 90.0)));
  TYElectricPower.Load.StLoad stLoad1(P = 2e3, 
    Vnominal = 220, Qc = 0, Ql = 1e3) annotation(Placement(transformation(origin = {8.10679, -92}, 
    extent = {{-6, -6}, {6, 6}}, 
    rotation = -90)));
  Modelica.Electrical.Polyphase.Basic.Capacitor C3(C = fill(1.2e-5, 3)) 
    annotation(Placement(transformation(origin = {-89.8, -28.500000000000018}, 
    extent = {{-6.0, -6.0}, {6.0, 6.0}}, 
    rotation = -90.0)));
  Modelica.Electrical.Polyphase.Basic.Star star2 
    annotation(Placement(transformation(origin = {-89.8, -40.87221400000002}, 
    extent = {{-3.627785999999997, -3.5}, {3.627786000000004, 3.5}}, 
    rotation = -90.0)));
  Modelica.Electrical.Analog.Basic.Ground ground2 
    annotation(Placement(transformation(origin = {-89.8, -53.000000000000036}, 
    extent = {{-3.500000000000001, -3.5}, {3.5, 3.5}})));
  Modelica.Electrical.Polyphase.Basic.Capacitor C4(C = fill(1.2e-5, 3)) 
    annotation(Placement(transformation(origin = {-66.0, -55.500000000000036}, 
    extent = {{-6.0, -6.0}, {6.0, 6.0}}, 
    rotation = -90.0)));
  Modelica.Electrical.Polyphase.Basic.Star star3 
    annotation(Placement(transformation(origin = {-66.00000000000003, -67.87221400000004}, 
    extent = {{-3.627785999999997, -3.5}, {3.627786000000004, 3.5}}, 
    rotation = -90.0)));
  Modelica.Electrical.Analog.Basic.Ground ground3 
    annotation(Placement(transformation(origin = {-66.00000000000003, -80.00000000000007}, 
    extent = {{-3.500000000000001, -3.5}, {3.5, 3.5}})));
  TYElectricPower.Load.StLoad stLoad2(P = 2e3, 
    Vnominal = 220, Qc = 0, Ql = 1e3) annotation(Placement(transformation(origin = {64, 9.255572}, 
    extent = {{-6, -6}, {6, 6}})));
  TYElectricPower.Primary.Generator generator(Lmd=1.5 / (2 * pi * 50),Lmq=1.5 / (2 *pi * 50),Lssigma=0.1 / (2 * pi* 50)) annotation(Placement(transformation(origin = {-122.00000000000001, 34.12234553256633}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYElectricPower.Primary.Generator generator1 annotation(Placement(transformation(origin = {126.00000000000001, 32.723698147285305}, 
    extent = {{10.0, -10.0}, {-10.0, 10.0}})));
  TYElectricPower.Primary.Transformer transformer 
    annotation(Placement(transformation(origin = {-79.94793999999999, 32.69141807364266}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYElectricPower.Primary.Transformer transformer1 
    annotation(Placement(transformation(origin = {74, 32.73161807364266}, 
    extent = {{10, -10}, {-10, 10}})));
equation
  connect(C1.plug_p, impedance.p) 
    annotation(Line(origin = {-18.0, 30.0}, 
    points = {{4.0, 0.0}, {4.0, 3.0}, {12.0, 3.0}}, 
    color = {0, 0, 255}));
  connect(C2.plug_p, impedance.n) 
    annotation(Line(origin = {9.0, 30.0}, 
    points = {{13.0, 0.0}, {13.0, 3.0}, {5.0, 3.0}}, 
    color = {0, 0, 255}));
  connect(C1.plug_n, star.plug_p) 
    annotation(Line(origin = {-11.0, 14.0}, 
    points = {{-3.0, 4.0}, {-3.0, 1.0}}, 
    color = {0, 0, 255}));
  connect(ground.p, star.pin_n) 
    annotation(Line(origin = {-1.0, 10.0}, 
    points = {{-13.0, -7.0}, {-13.0, -2.0}}, 
    color = {0, 0, 255}));
  connect(ground1.p, star1.pin_n) 
    annotation(Line(origin = {34.99999999999998, 10.000000000000004}, 
    points = {{-13.0, -7.0}, {-13.0, -2.0}}, 
    color = {0, 0, 255}));
  connect(star1.plug_p, C2.plug_n) 
    annotation(Line(origin = {22.0, 15.0}, 
    points = {{0.0, 0.0}, {0.0, 3.0}}, 
    color = {0, 0, 255}));
  connect(C3.plug_n, star2.plug_p) 
    annotation(Line(origin = {-86.8, -38.50000000000002}, 
    points = {{-3.0, 4.0}, {-3.0, 1.0}}, 
    color = {0, 0, 255}));
  connect(ground2.p, star2.pin_n) 
    annotation(Line(origin = {-76.8, -42.50000000000002}, 
    points = {{-13.0, -7.0}, {-13.0, -2.0}}, 
    color = {0, 0, 255}));
  connect(C4.plug_n, star3.plug_p) 
    annotation(Line(origin = {-63.00000000000001, -65.50000000000006}, 
    points = {{-3.0, 4.0}, {-3.0, 1.0}}, 
    color = {0, 0, 255}));
  connect(ground3.p, star3.pin_n) 
    annotation(Line(origin = {-53.00000000000001, -69.50000000000006}, 
    points = {{-13.0, -7.0}, {-13.0, -2.0}}, 
    color = {0, 0, 255}));
  connect(bus1.negativePlug, impedance.p) 
    annotation(Line(origin = {-21.44794, 32.96151807364266}, 
    points = {{-15.347939999999998, -0.3299000000000021}, {15.347939999999998, -0.3299000000000021}}, 
    color = {0, 0, 255}));
  connect(stLoad.positivePlug, bus1.positivePlug) 
    annotation(Line(origin = {-46, 24}, 
    points = {{-3.759999999999998, -14.804428}, {0, -14.804428}, {0, 8.631618073642656}, {6.904119999999999, 8.631618073642656}}, 
    color = {0, 0, 255}));
  connect(bus1.negativePlug, impedance1.p) 
    annotation(Line(origin = {-31, 8}, 
    points = {{-5.795879999999997, 24.631618073642656}, {2.3999999999999844, 24.631618073642656}, {2.3999999999999844, -26.40000000000001}}, 
    color = {0, 0, 255}));
  connect(C3.plug_p, impedance1.p) 
    annotation(Line(origin = {-69.07221399999997, -22.000000000000007}, 
    points = {{-21.0, -1.0}, {-21.0, 10.0}, {40.0, 10.0}, {40.0, 4.0}}, 
    color = {0, 0, 255}));
  connect(C4.plug_p, impedance1.n) 
    annotation(Line(origin = {-53.172214, -42.0}, 
    points = {{-13.0, -8.0}, {-13.0, 3.0}, {25.0, 3.0}}, 
    color = {0, 0, 255}));
  connect(impedance1.n, bus4.positivePlug) 
    annotation(Line(origin = {-10.0, -54.0}, 
    points = {{-19.0, 15.0}, {-19.0, -6.0}, {18.0, -6.0}, {18.0, -15.0}}, 
    color = {0, 0, 255}));
  connect(bus4.negativePlug, stLoad1.positivePlug) 
    annotation(Line(origin = {9, -78}, 
    points = {{-0.9402000000000204, 6.900000000000006}, {-0.9402000000000204, -7.760000000000005}, {-0.9532100000000003, -7.760000000000005}}, 
    color = {0, 0, 255}));
  connect(impedance2.n, bus4.positivePlug) 
    annotation(Line(origin = {25.0, -54.0}, 
    points = {{17.0, 15.0}, {17.0, -6.0}, {-17.0, -6.0}, {-17.0, -15.0}}, 
    color = {0, 0, 255}));
  connect(impedance.n, bus2.positivePlug) 
    annotation(Line(origin = {31, 33}, 
    points = {{-16.9, -0.368381926357344}, {15.904119999999999, -0.368381926357344}, {15.904119999999999, -0.33676385271469655}}, 
    color = {0, 0, 255}));
  connect(stLoad2.positivePlug, bus2.negativePlug) 
    annotation(Line(origin = {54, 20}, 
    points = {{3.759999999999998, -10.804428}, {0, -10.804428}, {0, 12.663236147285303}, {-4.795879999999997, 12.663236147285303}}, 
    color = {0, 0, 255}));
  connect(impedance2.p, bus2.positivePlug) 
    annotation(Line(origin = {45, 7}, 
    points = {{-2.8999999999999844, -25.400000000000006}, {-2.8999999999999844, 25.663236147285303}, {1.904119999999999, 25.663236147285303}}, 
    color = {0, 0, 255}));
  connect(bus3.negativePlug, generator1.PowerSupply) 
    annotation(Line(origin = {105.0, 32.0}, 
    points = {{-10.0, 0.0}, {13.0, 0.0}}, 
    color = {0, 0, 255}));
  connect(generator.PowerSupply, transformer.positivePlug) 
    annotation(Line(origin = {-100.0, 33.0}, 
    points = {{-14.0, 0.0}, {10.0, 0.0}}, 
    color = {0, 0, 255}));
  connect(transformer.positivePlug1, bus1.positivePlug) 
    annotation(Line(origin = {-54, 33}, 
    points = {{-15.947939999999988, -0.3085819263573413}, {14.904119999999999, -0.3085819263573413}, {14.904119999999999, -0.368381926357344}}, 
    color = {0, 0, 255}));
  connect(transformer1.positivePlug, bus3.positivePlug) 
    annotation(Line(origin = {89, 32}, 
    points = {{-5, 0.7316180736426574}, {3.799999999999997, 0.7316180736426574}, {3.799999999999997, 0.06323614728530202}}, 
    color = {0, 0, 255}));
  connect(transformer1.positivePlug1, bus2.negativePlug) 
    annotation(Line(origin = {57, 32}, 
    points = {{7, 0.7316180736426574}, {-7.795879999999997, 0.7316180736426574}, {-7.795879999999997, 0.6632361472853034}}, 
    color = {0, 0, 255}));
end System1;