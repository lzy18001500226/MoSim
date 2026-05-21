model System3 "配电系统"
  annotation(Documentation(link = "modelica://TYElectricPower/Resources/HTML/System3.html"), Protection(access = Access.nonPackageDuplicate),__MWORKS(ResultViewerManager(resultViewers={
ResultViewer(name="典型曲线", executeTrigger=executeTrigger.SimulationFinished, commands={
CreatePlot(id=1, x_display_unit="s", legend_layout=1, left_title_type=2, left_title="三相电压[V]", bottom_title_type=2, bottom_title="时间/s", right_title_type=2, fix_time_range_value=0, zoom_x=(0, 20), zoom_y_l=(-300, 300)), 
Plot(y=["transformer.positivePlug1.pin[1].v", "transformer.positivePlug1.pin[2].v", "transformer.positivePlug1.pin[3].v"], colors=["4278190335", "4294901760", "4278222848"])})
})));
  import Modelica.Constants.pi;
  extends TYElectricPower.Icons.Example;
  annotation(Icon(coordinateSystem(extent = {{-100.0, -100.0}, {100.0, 100.0}}, 
    grid = {2.0, 2.0})), 
    Diagram(coordinateSystem(extent = {{-150.0, -100.0}, {150.0, 100.0}}, 
    grid = {2.0, 2.0})), 
    experiment(Algorithm = Dassl, Interval = 0.001, StartTime = 0, StopTime = 20, Tolerance = 0.0001), 

    Documentation(info = "<html><p>
该案例体现了小型配电网的应用实例，发电机发出的电能经过变压器变换，再由母线进行两路电能分配，为下游负荷进行供电。
</p>
</html>"));
  TYElectricPower.Primary.Generator generator1 annotation(Placement(transformation(origin = {-118.00000000000001, 7.292080073642641}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYElectricPower.Basic.Common.Impedance impedance 
    annotation(Placement(transformation(origin = {-62.0, 6.73161807364264}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  Modelica.Electrical.Polyphase.Basic.Star star 
    annotation(Placement(transformation(origin = {70.00000000000003, -13.980118073642672}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  Modelica.Electrical.Analog.Basic.Ground ground 
    annotation(Placement(transformation(origin = {87.99999999999997, -42.00000000000001}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYElectricPower.Basic.Common.Impedance impedance1 
    annotation(Placement(transformation(origin = {28.000000000000004, 28.616881926357294}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYElectricPower.Primary.Bus bus1 
    annotation(Placement(transformation(origin = {52.0, 28.616881926357323}, 
    extent = {{-10.0, -10.0}, {9.89588, 10.0402}})));
  TYElectricPower.Load.StLoad stLoad(Qc = 0, Ql = 500, P = 1000) 
    annotation(Placement(transformation(origin = {87.99999999999997, 7.268381926357311}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYElectricPower.Load.StLoad stLoad1 
    annotation(Placement(transformation(origin = {16, -42}, 
    extent = {{-10, -10}, {10, 10}})));
  TYElectricPower.Basic.Common.Impedance impedance2 
    annotation(Placement(transformation(origin = {37.899999999999984, -14.000000000000018}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYElectricPower.Primary.Transformer transformer 
    annotation(Placement(transformation(origin = {-87.00000000000001, 6.631618073642642}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYElectricPower.Primary.Transformer transformer1 
    annotation(Placement(transformation(origin = {-10.0, 28.5168819263573}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYElectricPower.Primary.Transformer transformer2 
    annotation(Placement(transformation(origin = {-10.0, -13.980118073642668}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYElectricPower.Primary.Bus bus 
    annotation(Placement(transformation(origin = {-41.89587999999999, 6.03161807364264}, 
    extent = {{-10.0, -10.0}, {9.89588, 10.0402}})));
equation
  connect(ground.p, star.pin_n) 
    annotation(Line(origin = {100.99999999999994, -29.000000000000014}, 
    points = {{-13.0, -3.0}, {-13.0, 15.0}, {-21.0, 15.0}}, 
    color = {0, 0, 255}));
  connect(impedance1.n, bus1.positivePlug) 
    annotation(Line(origin = {45.0, 28.999999999999986}, 
    points = {{-7.0, 0.0}, {6.0, 0.0}}, 
    color = {0, 0, 255}));
  connect(bus1.negativePlug, stLoad.positivePlug) 
    annotation(Line(origin = {71, 26.999999999999986}, 
    points = {{-17.9, 2.2168819263573383}, {-5, 2.2168819263573383}, {-5, -19.831618073642673}, {6.599999999999966, -19.831618073642673}}, 
    color = {0, 0, 255}));
  connect(impedance2.n, star.plug_p) 
    annotation(Line(origin = {63.0, -14.000000000000018}, 
    points = {{-15.0, 0.0}, {-3.0, 0.0}}, 
    color = {0, 0, 255}));
  connect(generator1.PowerSupply, transformer.positivePlug) 
    annotation(Line(origin = {-105.0, 6.999999999999989}, 
    points = {{-5.0, 0.0}, {8.0, 0.0}}, 
    color = {0, 0, 255}));
  connect(transformer.positivePlug1, impedance.p) 
    annotation(Line(origin = {-68.0, 6.999999999999989}, 
    points = {{-9.0, 0.0}, {-4.0, 0.0}}, 
    color = {0, 0, 255}));
  connect(impedance.n, bus.positivePlug) 
    annotation(Line(origin = {-45.0, 5.999999999999989}, 
    points = {{-7.0, 1.0}, {2.0, 1.0}}, 
    color = {0, 0, 255}));
  connect(bus.negativePlug, transformer1.positivePlug) 
    annotation(Line(origin = {-28.0, 17.999999999999986}, 
    points = {{-13.0, -11.0}, {8.0, -11.0}, {8.0, 11.0}}, 
    color = {0, 0, 255}));
  connect(bus.negativePlug, transformer2.positivePlug) 
    annotation(Line(origin = {-28.0, -4.000000000000011}, 
    points = {{-13.0, 11.0}, {8.0, 11.0}, {8.0, -10.0}}, 
    color = {0, 0, 255}));
  connect(transformer1.positivePlug1, impedance1.p) 
    annotation(Line(origin = {9.0, 28.999999999999986}, 
    points = {{-9.0, 0.0}, {9.0, 0.0}}, 
    color = {0, 0, 255}));
  connect(transformer2.positivePlug1, impedance2.p) 
    annotation(Line(origin = {14.0, -14.00000000000001}, 
    points = {{-14.0, 0.0}, {14.0, 0.0}}, 
    color = {0, 0, 255}));
  connect(transformer2.positivePlug1, stLoad1.positivePlug) 
    annotation(Line(origin = {3, -23.00000000000001}, 
    points = {{-3, 9.019881926357343}, {-3, -19.09999999999999}, {2.5999999999999996, -19.09999999999999}}, 
    color = {0, 0, 255}));
end System3;