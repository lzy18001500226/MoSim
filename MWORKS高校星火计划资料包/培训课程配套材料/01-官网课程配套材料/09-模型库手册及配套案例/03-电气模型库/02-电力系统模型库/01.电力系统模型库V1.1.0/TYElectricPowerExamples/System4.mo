model System4 "厂用电系统"
  annotation(Documentation(link = "modelica://TYElectricPower/Resources/HTML/System4.html"), Protection(access = Access.nonPackageDuplicate),__MWORKS(ResultViewerManager(resultViewers={
ResultViewer(name="典型曲线", executeTrigger=executeTrigger.SimulationFinished, commands={
CreatePlot(id=1, x_display_unit="s", legend_layout=1, left_title_type=2, left_title="三相电压[V]", bottom_title_type=2, bottom_title="时间/s", right_title_type=2, fix_time_range_value=0, zoom_x=(0, 100), zoom_y_l=(-300, 300)), 
Plot(y=["transformer.positivePlug1.pin[1].v", "transformer.positivePlug1.pin[2].v", "transformer.positivePlug1.pin[3].v"], colors=["4278190335", "4294901760", "4278222848"]), 
CreatePlot(id=-1, x_display_unit="s", legend_layout=1, left_title_type=2, left_title="有功功率[W]", bottom_title_type=2, bottom_title="时间/s", fix_time_range_value=0, sub_plot=(2, 1), zoom_x=(0, 100), zoom_y_l=(-50, 200)), 
Plot(y=["transformer.powerSensor.P"], colors=["4278190335"])})
})));
  extends TYElectricPower.Icons.Example;
  import Modelica.Constants.pi;
  annotation(Icon(coordinateSystem(extent = {{-100.0, -100.0}, {100.0, 100.0}}, 
    grid = {2.0, 2.0})), 
    Diagram(coordinateSystem(extent = {{-150.0, -100.0}, {150.0, 100.0}}, 
    grid = {2.0, 2.0})), 
    experiment(Algorithm = Dassl, Interval = 0.001, StartTime = 0, StopTime = 100, Tolerance = 0.0001), 

    Documentation(info = "<html><p>
该案例为厂用电系统的应用实例，体现了2台发电机经变压后，向下游负荷供电的场景
</p>
</html>"));
  TYElectricPower.Primary.Generator generator1 annotation(Placement(transformation(origin = {-114.0, 47.271761999999995}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYElectricPower.Basic.Common.Impedance impedance 
    annotation(Placement(transformation(origin = {-42.05206000000001, 46.61129999999999}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYElectricPower.Basic.Common.Impedance impedance1 
    annotation(Placement(transformation(origin = {29.9, 67.9598}, 
    extent = {{-10, -10}, {10, 10}})));
  TYElectricPower.Primary.Bus bus1 
    annotation(Placement(transformation(origin = {68.10412, 67.25980000000001}, 
    extent = {{-10, -10}, {9.89588, 10.0402}})));
  TYElectricPower.Load.StLoad stLoad 
    annotation(Placement(transformation(origin = {98, 67.25980000000001}, 
    extent = {{-10, -10}, {10, 10}})));
  TYElectricPower.Load.StLoad stLoad1 
    annotation(Placement(transformation(origin = {98, 24.742918073642635}, 
    extent = {{-10, -10}, {10, 10}})));
  TYElectricPower.Primary.Generator generator2 annotation(Placement(transformation(origin = {-111.94793999999995, -51.901765705429376}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYElectricPower.Basic.Common.Impedance impedance2 
    annotation(Placement(transformation(origin = {-42.05206000000001, -53.2220277054294}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYElectricPower.Basic.Common.Impedance impedance3 
    annotation(Placement(transformation(origin = {27.94794000000001, -30.676963852714707}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYElectricPower.Basic.Common.Impedance impedance4 
    annotation(Placement(transformation(origin = {27.94794000000001, -73.19384577907203}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYElectricPower.Primary.Bus bus2 
    annotation(Placement(transformation(origin = {68.10412, 24.742918073642635}, 
    extent = {{-10, -10}, {9.89588, 10.0402}})));
  TYElectricPower.Load.StLoad stLoad2 
    annotation(Placement(transformation(origin = {-52, 14.165093073642652}, 
    extent = {{-10, -10}, {10, 10}})));
  TYElectricPower.Load.StLoad stLoad3 
    annotation(Placement(transformation(origin = {-52, -19.528467315893373}, 
    extent = {{-10, 10}, {10, -10}})));
  TYElectricPower.Basic.Common.Impedance impedance5 
    annotation(Placement(transformation(origin = {29.9, 25.442918073642637}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYElectricPower.Primary.Transformer transformer 
    annotation(Placement(transformation(origin = {-76.99999999999997, 46.611299999999986}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYElectricPower.Primary.Transformer transformer1 
    annotation(Placement(transformation(origin = {-80, -53.3220277054294}, 
    extent = {{-10, -10}, {10, 10}})));
  TYElectricPower.Primary.Transformer transformer2 
    annotation(Placement(transformation(origin = {1.7999999999999972, 67.8598}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYElectricPower.Primary.Transformer transformer3 
    annotation(Placement(transformation(origin = {1.7999999999999972, 25.442918073642637}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYElectricPower.Primary.Bus bus 
    annotation(Placement(transformation(origin = {-25.94793999999999, 45.91129999999998}, 
    extent = {{-10.0, -10.0}, {9.89588, 10.0402}})));
  TYElectricPower.Primary.Bus bus3 
    annotation(Placement(transformation(origin = {-25.94793999999999, -53.262227705429396}, 
    extent = {{-10.0, -10.0}, {9.89588, 10.0402}})));
  TYElectricPower.Primary.Transformer transformer4 
    annotation(Placement(transformation(origin = {1.7999999999999972, -30.676963852714714}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYElectricPower.Primary.Transformer transformer5 
    annotation(Placement(transformation(origin = {1.7999999999999972, -73.29384577907203}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
equation
  connect(bus1.negativePlug, stLoad.positivePlug) 
    annotation(Line(origin = {98.94794000000002, 49}, 
    points = {{-29.743820000000028, 18.859800000000007}, {-11.347940000000023, 18.859800000000007}, {-11.347940000000023, 18.15980000000002}}, 
    color = {0, 0, 255}));
  connect(bus2.negativePlug, stLoad1.positivePlug) 
    annotation(Line(origin = {80.94794000000002, 19}, 
    points = {{-11.743820000000028, 6.342918073642636}, {6.652059999999977, 6.342918073642636}, {6.652059999999977, 5.642918073642633}}, 
    color = {0, 0, 255}));
  connect(impedance3.n, bus1.positivePlug) 
    annotation(Line(origin = {54.94794000000001, 19}, 
    points = {{-16.9, -49.77696385271471}, {-2.9479400000000098, -49.77696385271471}, {-2.9479400000000098, 48.85980000000001}, {11.956179999999982, 48.85980000000001}}, 
    color = {0, 0, 255}));
  connect(impedance4.n, bus2.positivePlug) 
    annotation(Line(origin = {61.94794000000001, -24}, 
    points = {{-23.9, -49.29384577907203}, {-1.9479400000000098, -49.29384577907203}, {-1.9479400000000098, 49.342918073642636}, {4.956179999999982, 49.342918073642636}}, 
    color = {0, 0, 255}));
  connect(impedance5.n, bus2.positivePlug) 
    annotation(Line(origin = {57.94794000000001, 25}, 
    points = {{-17.94794000000001, 0.34291807364263605}, {8.956179999999982, 0.34291807364263605}}, 
    color = {0, 0, 255}));
  connect(generator1.PowerSupply, transformer.positivePlug) 
    annotation(Line(origin = {-95.05205999999998, 47.0}, 
    points = {{-10.0, 0.0}, {8.0, 0.0}}, 
    color = {0, 0, 255}));
  connect(transformer.positivePlug1, impedance.p) 
    annotation(Line(origin = {-58.05205999999998, 47.0}, 
    points = {{-9.0, 0.0}, {6.0, 0.0}}, 
    color = {0, 0, 255}));
  connect(stLoad2.positivePlug, transformer.positivePlug1) 
    annotation(Line(origin = {-63.05205999999998, 37}, 
    points = {{0.6520599999999774, -22.93490692635735}, {-3.9479399999999885, -22.93490692635735}, {-3.9479399999999885, 9.611299999999986}}, 
    color = {0, 0, 255}));
  connect(generator2.PowerSupply, transformer1.positivePlug) 
    annotation(Line(origin = {-95.05205999999998, -53}, 
    points = {{-8.414261262502649, 0.43777229457062106}, {5.052059999999983, 0.43777229457062106}, {5.052059999999983, -0.32202770542939874}}, 
    color = {0, 0, 255}));
  connect(transformer1.positivePlug1, impedance2.p) 
    annotation(Line(origin = {-58.05205999999998, -53}, 
    points = {{-11.947940000000017, -0.32202770542939874}, {5.89999999999997, -0.32202770542939874}}, 
    color = {0, 0, 255}));
  connect(stLoad3.positivePlug, impedance2.p) 
    annotation(Line(origin = {-55.05205999999998, -41}, 
    points = {{-7.347940000000023, 21.57153268410663}, {-10.947940000000017, 21.57153268410663}, {-10.947940000000017, -12.322027705429399}, {2.89999999999997, -12.322027705429399}}, 
    color = {0, 0, 255}));
  connect(impedance1.p, transformer2.positivePlug1) 
    annotation(Line(origin = {13.94794000000001, 68}, 
    points = {{5.852059999999987, -0.140199999999993}, {-2.1479400000000126, -0.140199999999993}}, 
    color = {0, 0, 255}));
  connect(transformer3.positivePlug1, impedance5.p) 
    annotation(Line(origin = {13.94794000000001, 25.0}, 
    points = {{-2.0, 0.0}, {6.0, 0.0}}, 
    color = {0, 0, 255}));
  connect(impedance.n, bus.positivePlug) 
    annotation(Line(origin = {-29.052059999999983, 47.0}, 
    points = {{-3.0, 0.0}, {2.0, 0.0}}, 
    color = {0, 0, 255}));
  connect(bus.negativePlug, transformer2.positivePlug) 
    annotation(Line(origin = {-18.052059999999983, 58.0}, 
    points = {{-7.0, -11.0}, {0.0, -11.0}, {0.0, 10.0}, {10.0, 10.0}}, 
    color = {0, 0, 255}));
  connect(bus.negativePlug, transformer3.positivePlug) 
    annotation(Line(origin = {-18.052059999999983, 36.0}, 
    points = {{-7.0, 11.0}, {0.0, 11.0}, {0.0, -11.0}, {10.0, -11.0}}, 
    color = {0, 0, 255}));
  connect(impedance2.n, bus3.positivePlug) 
    annotation(Line(origin = {-29.052059999999983, -53.0}, 
    points = {{-3.0, 0.0}, {2.0, 0.0}}, 
    color = {0, 0, 255}));
  connect(transformer4.positivePlug1, impedance3.p) 
    annotation(Line(origin = {14.94794000000001, -31.0}, 
    points = {{-3.0, 0.0}, {3.0, 0.0}}, 
    color = {0, 0, 255}));
  connect(transformer5.positivePlug1, impedance4.p) 
    annotation(Line(origin = {14.94794000000001, -73.0}, 
    points = {{-3.0, 0.0}, {3.0, 0.0}}, 
    color = {0, 0, 255}));
  connect(bus3.negativePlug, transformer4.positivePlug) 
    annotation(Line(origin = {-16.052059999999983, -42.0}, 
    points = {{-9.0, -11.0}, {0.0, -11.0}, {0.0, 11.0}, {8.0, 11.0}}, 
    color = {0, 0, 255}));
  connect(bus3.negativePlug, transformer5.positivePlug) 
    annotation(Line(origin = {-16.052059999999983, -63.0}, 
    points = {{-9.0, 10.0}, {0.0, 10.0}, {0.0, -10.0}, {8.0, -10.0}}, 
    color = {0, 0, 255}));
  connect(impedance1.n, bus1.positivePlug) 
    annotation(Line(origin = {50, 69}, 
    points = {{-10, -1.140199999999993}, {16.904119999999992, -1.140199999999993}}, 
    color = {0, 0, 255}));
end System4;