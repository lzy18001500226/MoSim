model System5 "新能源发电系统"
  annotation(Documentation(link = "modelica://TYElectricPower/Resources/HTML/System5.html"), Protection(access = Access.nonPackageDuplicate));
  extends TYElectricPower.Icons.Example;
  import pi = Modelica.Constants.pi;
  annotation(Icon(coordinateSystem(extent = {{-100.0, -100.0}, {100.0, 100.0}}, 
    grid = {2.0, 2.0})), 
    Diagram(coordinateSystem(extent = {{-150, -100}, {150, 100}}, 
    grid = {2, 2})), 
    experiment(Algorithm = Dassl, Interval = 0.001, StartTime = 0, StopTime = 10, Tolerance = 0.0001), 

    Documentation(info = "<html><p>
该案例体现了光伏、储能与负荷供应的应用场景
</p>
</html>"), __MWORKS(ContinueSimConfig(SaveContinueFile = "false", SaveBeforeStop = "false", NumberBeforeStop = 1, FixedContinueInterval = "false", ContinueIntervalLength = 0.05, ContinueTimeVector),ResultViewerManager(resultViewers={
ResultViewer(name="典型曲线", executeTrigger=executeTrigger.SimulationFinished, commands={
CreatePlot(id=3, x_display_unit="s", legend_layout=1, left_title_type=2, left_title="光伏电压[V]", bottom_title_type=2, bottom_title="时间/s", right_title_type=2, fix_time_range_value=0, zoom_x=(0, 10), zoom_y_l=(-100, 400)), 
Plot(y=["pVarray.pin_p.v"], colors=["4278190335"]), 
CreatePlot(id=-1, x_display_unit="s", legend_layout=1, left_title_type=2, left_title="电压[V]", bottom_title_type=2, bottom_title="时间/s", fix_time_range_value=0, sub_plot=(2, 1), zoom_x=(0, 10), zoom_y_l=(-200, 200)), 
Plot(y=["inverter.A.v", "inverter.B.v", "inverter.C.v"], colors=["4278190335", "4294901760", "4278222848"])})
})));
  TYElectricPower.DGLibrary.PVarray pVarray 
    annotation(Placement(transformation(origin = {-94.00000000000003, 0.9762291955681093}, 
    extent = {{-10, -10}, {10, 10}})));
  TYElectricPower.Basic.Common.Impedance impedance 
    annotation(Placement(transformation(origin = {40, -1.2484999999999715}, 
    extent = {{-10, -10}, {10, 10}})));
  Modelica.Electrical.Polyphase.Basic.Star star 
    annotation(Placement(transformation(origin = {140, -32.08011807364266}, 
    extent = {{-10, -10}, {10, 10}})));
  Modelica.Electrical.Analog.Basic.Ground ground 
    annotation(Placement(transformation(origin = {154, -60.00000000000001}, 
    extent = {{-10, -10}, {10, 10}})));
  TYElectricPower.Basic.Common.Impedance impedance1 
    annotation(Placement(transformation(origin = {103.00000000000004, 25.70784726921076}, 
    extent = {{-10, -10}, {10, 10}})));
  TYElectricPower.Primary.Bus bus1 
    annotation(Placement(transformation(origin = {120.10412000000001, 24.307847269210754}, 
    extent = {{-10, -10}, {9.89588, 10.0402}})));
  TYElectricPower.Basic.Common.Impedance impedance2 
    annotation(Placement(transformation(origin = {117, -31.980118073642664}, 
    extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Sources.RealExpression solar(y = 1000) 
    annotation(Placement(transformation(origin = {-126.00000000000003, 5.2512852954737}, 
    extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Sources.RealExpression T(y = 25) 
    annotation(Placement(transformation(origin = {-150.00000000000006, -3.0436527307892334}, 
    extent = {{-10, -10}, {10, 10}})));
  TYElectricPower.Primary.Inverter inverter 
    annotation(Placement(transformation(origin = {-14, -1.2484999999999715}, 
    extent = {{-10, -10}, {10, 10}})));
  TYElectricPower.Load.AcLoad acLoad 
    annotation(Placement(transformation(origin = {-60.000000000000036, 25.607847269210765}, 
    extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Sources.RealExpression Uref[3](y = {sin(100 * Modelica.Constants.pi * time), sin(100 * Modelica.Constants.pi * time - 2 * pi / 3), sin(100 * Modelica.Constants.pi * time - 4 * pi / 3)}) annotation(Placement(transformation(origin = {-37.999999999999964, -19.083416583503915}, 
    extent = {{-10, -10}, {10, 10}})));
  Modelica.Electrical.Analog.Basic.Ground ground1 
    annotation(Placement(transformation(origin = {-74.00000000000003, -19.083416583503908}, 
    extent = {{-10, -10}, {10, 10}})));
  TYElectricPower.Primary.Bus bus2 
    annotation(Placement(transformation(origin = {54.104119999999995, -1.9484999999999744}, 
    extent = {{-10, -10}, {9.89588, 10.0402}})));
  TYElectricPower.Primary.Transformer transformer 
    annotation(Placement(transformation(origin = {80, 25.607847269210765}, 
    extent = {{-10, -10}, {10, 10}})));
  TYElectricPower.Primary.Transformer transformer1 
    annotation(Placement(transformation(origin = {82, -31.980118073642664}, 
    extent = {{-10, -10}, {10, 10}})));
  TYElectricPower.Interfaces.Electrical.PlugToPins_p plugToPins 
    annotation(Placement(transformation(origin = {20, -1.2484999999999715}, 
    extent = {{10, -10}, {-10, 10}})));
  TYElectricPower.DGLibrary.Battery battery(Enom = 7.2, Q = 5.4, Qnom = 4.8835, Eexp = 7.7788, Qexp = 0.2653, Efull = 8.3807, Rin = 0.013333, Idischarge = 2.3478) annotation(Placement(transformation(origin = {-24.000000000000036, 25.607847269210765}, 
    extent = {{10, -10}, {-10, 10}})));
  TYElectricPower.Load.AcLoadThree Load 
    annotation(Placement(transformation(origin = {148, 24.307847269210754}, 
    extent = {{-10, -10}, {10, 10}})));
  TYElectricPower.Load.AcLoadThree Load1 
    annotation(Placement(transformation(origin = {117, -54.731618073642686}, 
    extent = {{-10, -10}, {10, 10}})));
equation
  connect(ground.p, star.pin_n) 
    annotation(Line(origin = {218.99999999999994, -47.00000000000001}, 
    points = {{-64.99999999999994, -3}, {-64.99999999999994, 14.919881926357348}, {-68.99999999999994, 14.919881926357348}}, 
    color = {0, 0, 255}));
  connect(impedance1.n, bus1.positivePlug) 
    annotation(Line(origin = {123.00000000000003, 23.390965342853427}, 
    points = {{-9.899999999999977, 2.216881926357331}, {-4.095880000000022, 2.216881926357331}, {-4.095880000000022, 1.5168819263573283}}, 
    color = {0, 0, 255}));
  connect(impedance2.n, star.plug_p) 
    annotation(Line(origin = {144.99999999999997, -32.100000000000016}, 
    points = {{-17.899999999999977, 0.019881926357349755}, {-14.999999999999972, 0.019881926357349755}, {-14.999999999999972, 0.01988192635735686}}, 
    color = {0, 0, 255}));
  connect(T.y, pVarray.T) 
    annotation(Line(origin = {-114.00000000000003, -3.0436527307892405}, 
    points = {{-25.00000000000003, 7.105427357601002e-15}, {8, 7.105427357601002e-15}, {8, -0.22882157086112898}}, 
    color = {0, 0, 127}));
  connect(pVarray.Irradiance, solar.y) 
    annotation(Line(origin = {-114.00000000000003, 4.9563472692107595}, 
    points = {{8, 0.2949380262629333}, {-1, 0.2949380262629333}, {-1, 0.2949380262629404}}, 
    color = {0, 0, 127}));
  connect(pVarray.pin_p, inverter.p) 
    annotation(Line(origin = {-81, 2.9563472692107595}, 
    points = {{-3.0000000000000284, 0.20064375507649146}, {57, 0.20064375507649146}}, 
    color = {0, 0, 255}));
  connect(pVarray.pin_n, inverter.n) 
    annotation(Line(origin = {-81, -4.0436527307892405}, 
    points = {{-3.0000000000000284, 1.1711784291388696}, {57, 1.1711784291388696}, {57, -1.6048472692107296}}, 
    color = {0, 0, 255}));
  connect(acLoad.in_n, pVarray.pin_n) 
    annotation(Line(origin = {-72.00000000000003, 10.95634726921076}, 
    points = {{2, 9.651500000000006}, {-2, 9.651500000000006}, {-2, -13.82882157086113}, {-12, -13.82882157086113}}, 
    color = {0, 0, 255}));
  connect(acLoad.in_p, pVarray.pin_p) 
    annotation(Line(origin = {-72.00000000000003, 18.95634726921076}, 
    points = {{2, 11.651500000000006}, {-6, 11.651500000000006}, {-6, -15.799356244923509}, {-12, -15.799356244923509}}, 
    color = {0, 0, 255}));
  connect(Uref.y, inverter.uref) 
    annotation(Line(origin = {-78.00000000000003, -15.04365273078924}, 
    points = {{51.000000000000064, -4.039763852714675}, {64.04271166473542, -4.039763852714675}, {64.04271166473542, 2.795152730789269}}, 
    color = {0, 0, 127}));
  connect(pVarray.pin_n, ground1.p) 
    annotation(Line(origin = {-79.00000000000003, -6.0436527307892405}, 
    points = {{-5, 3.1711784291388696}, {5, 3.1711784291388696}, {5, -3.0397638527146675}}, 
    color = {0, 0, 255}));
  connect(impedance.n, bus2.positivePlug) 
    annotation(Line(origin = {50, -11.248499999999986}, 
    points = {{0.10000000000000142, 9.900000000000013}, {2.904119999999992, 9.900000000000013}}, 
    color = {0, 0, 255}));
  connect(bus2.negativePlug, transformer.positivePlug) 
    annotation(Line(origin = {71, -9.248499999999986}, 
    points = {{-15.795880000000004, 7.900000000000011}, {-7, 7.900000000000011}, {-7, 34.85634726921075}, {-1, 34.85634726921075}}, 
    color = {0, 0, 255}));
  connect(bus2.negativePlug, transformer1.positivePlug) 
    annotation(Line(origin = {71, -30.248499999999986}, 
    points = {{-15.795880000000004, 28.900000000000013}, {-7, 28.900000000000013}, {-7, -1.7316180736426787}, {1, -1.7316180736426787}}, 
    color = {0, 0, 255}));
  connect(transformer.positivePlug1, impedance1.p) 
    annotation(Line(origin = {86.00000000000003, 23.007847269210743}, 
    points = {{3.9999999999999716, 2.6000000000000227}, {6.900000000000006, 2.6000000000000227}, {6.900000000000006, 2.6000000000000156}}, 
    color = {0, 0, 255}));
  connect(transformer1.positivePlug1, impedance2.p) 
    annotation(Line(origin = {131, -32.38311807364269}, 
    points = {{-39, 0.4030000000000271}, {-24.099999999999994, 0.4030000000000271}, {-24.099999999999994, 0.3030000000000257}}, 
    color = {0, 0, 255}));
  connect(plugToPins.plug_p, impedance.p) 
    annotation(Line(origin = {28, 33}, 
    points = {{-6, -34.24849999999997}, {1.8999999999999986, -34.24849999999997}, {1.8999999999999986, -34.34849999999997}}, 
    color = {0, 0, 255}));
  connect(inverter.A, plugToPins.pin_p[1]) 
    annotation(Line(origin = {14, 37}, 
    points = {{-17.6, -32.24849999999997}, {-10, -32.24849999999997}, {-10, -38.24849999999997}, {4, -38.24849999999997}}, 
    color = {0, 0, 255}));
  connect(inverter.B, plugToPins.pin_p[2]) 
    annotation(Line(origin = {14, 34}, 
    points = {{-17.6, -35.26624023231253}, {4, -35.26624023231253}, {4, -35.24849999999997}}, 
    color = {0, 0, 255}));
  connect(inverter.C, plugToPins.pin_p[3]) 
    annotation(Line(origin = {14, 30}, 
    points = {{-17.6, -39.24849999999997}, {-10, -39.24849999999997}, {-10, -31.24849999999997}, {4, -31.24849999999997}}, 
    color = {0, 0, 255}));
  connect(battery.pin_p, pVarray.pin_p) 
    annotation(Line(origin = {68, 45.52225805464133}, 
    points = {{-102.40795321637431, -18.59944648549692}, {-112.00000000000003, -18.59944648549692}, {-112.00000000000003, -42.365267030354076}, {-152.00000000000003, -42.365267030354076}}, 
    color = {0, 0, 255}));
  connect(battery.pin_n, pVarray.pin_n) 
    annotation(Line(origin = {68, 36.52225805464133}, 
    points = {{-102.40795321637431, -16.992539440401323}, {-108.00000000000003, -16.992539440401323}, {-108.00000000000003, -39.3947323562917}, {-152.00000000000003, -39.3947323562917}}, 
    color = {0, 0, 255}));
  connect(bus1.negativePlug, Load.positivePlug) 
    annotation(Line(origin = {128, 24.65934726921075}, 
    points = {{-6.795879999999997, 0.24850000000000705}, {10, 0.24850000000000705}, {10, -0.3514999999999944}}, 
    color = {0, 0, 255}));
  connect(Load1.positivePlug, transformer1.positivePlug1) 
    annotation(Line(origin = {100, -43.731618073642686}, 
    points = {{7, -11}, {-8, -11}, {-8, 11.751500000000021}}, 
    color = {0, 0, 255}));
end System5;