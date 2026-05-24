model System6 "单台变压器系统"
  annotation(Documentation(link = "modelica://TYElectricPower/Resources/HTML/System6.html"), Protection(access = Access.nonPackageDuplicate));
  extends TYElectricPower.Icons.Example;
  import Modelica.Constants.pi;
  annotation(Icon(coordinateSystem(extent = {{-100.0, -100.0}, {100.0, 100.0}}, 
    grid = {2.0, 2.0})), 
    Diagram(coordinateSystem(extent = {{-150.0, -100.0}, {150.0, 100.0}}, 
    grid = {2.0, 2.0})), 
    experiment(Algorithm = Rkfix4, Interval = 0.001, StartTime = 0, StopTime = 1, Tolerance = 0.0001, IntegratorStep = 0.001), 

    Documentation(info = "<html><p>
该案例体现了1台变压器变压供下游负荷用电的应用场景
</p>
</html>"), __MWORKS(ContinueSimConfig(SaveContinueFile = "false", SaveBeforeStop = "false", NumberBeforeStop = 1, FixedContinueInterval = "false", ContinueIntervalLength = 0.5, ContinueTimeVector),ResultViewerManager(resultViewers={
ResultViewer(name="典型曲线", executeTrigger=executeTrigger.SimulationFinished, commands={
CreatePlot(id=1, x_display_unit="s", legend_layout=1, left_title_type=2, left_title="三相电压[V]", bottom_title_type=2, bottom_title="时间/s", right_title_type=2, fix_time_range_value=0, zoom_x=(0, 1), zoom_y_l=(-1500, 1500)), 
Plot(y=["Transformer.positivePlug1.pin[1].v", "Transformer.positivePlug1.pin[2].v", "Transformer.positivePlug1.pin[3].v"], colors=["4278190335", "4294901760", "4278222848"])})
})));
  TYElectricPower.Primary.Generator generator1 annotation(Placement(transformation(origin = {-66, 21.35188007364267}, 
    extent = {{-10, -10}, {10, 10}})));
  TYElectricPower.Primary.Transformer Transformer(n = 10e3 / 1e3) annotation(Placement(transformation(origin = {-8.947940000000006, 20.69141807364267}, 
    extent = {{-9.411764705882348, -10.0}, {9.411764705882334, 10.0}})));
  Modelica.Electrical.Analog.Basic.Ground ground annotation(Placement(transformation(origin = {65.99999999999999, -28.0}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  Modelica.Electrical.Polyphase.Basic.Star star 
    annotation(Placement(transformation(origin = {66.0, 2.0}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
    rotation = -90.0)));
  TYElectricPower.Primary.Bus bus annotation(Placement(transformation(origin = {14.171767058823518, 20.091418073642668}, 
    extent = {{-10.0, -10.0}, {9.89588, 10.0402}})));
  TYElectricPower.Basic.Common.MulConductor MulConductor 
    annotation(Placement(transformation(origin = {40.03382352941177, 20.8117361472853}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYElectricPower.Primary.Bus bus1 annotation(Placement(transformation(origin = {-40.079852352941174, 20.091418073642668}, 
    extent = {{-10.0, -10.0}, {9.89588, 10.0402}})));
  TYElectricPower.Load.AcLoadThree PLoad 
    annotation(Placement(transformation(origin = {26.000000000000007, -7.999999999999999}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
equation
  connect(star.pin_n, ground.p) 
    annotation(Line(origin = {66.0, -13.0}, 
    points = {{0.0, 5.0}, {0.0, -5.0}}, 
    color = {0, 0, 255}));
  connect(Transformer.positivePlug1, bus.positivePlug) 
    annotation(Line(origin = {16.0, 21.0}, 
    points = {{-16.0, 0.0}, {-3.0, 0.0}}, 
    color = {0, 0, 255}));
  connect(MulConductor.plug_p, bus.negativePlug) 
    annotation(Line(origin = {23.0, 21.0}, 
    points = {{7.0, 0.0}, {-8.0, 0.0}}, 
    color = {0, 0, 255}));
  connect(MulConductor.plug_n, star.plug_p) 
    annotation(Line(origin = {58.0, 17.0}, 
    points = {{-8.0, 4.0}, {8.0, 4.0}, {8.0, -5.0}}, 
    color = {0, 0, 255}));
  connect(generator1.PowerSupply, bus1.positivePlug) 
    annotation(Line(origin = {-51, 21}, 
    points = {{-6.518381262502686, -0.3085819263573306}, {9.720147647058823, -0.3085819263573306}}, 
    color = {0, 0, 255}));
  connect(bus1.negativePlug, Transformer.positivePlug) 
    annotation(Line(origin = {-28.0, 21.0}, 
    points = {{-11.0, 0.0}, {10.0, 0.0}}, 
    color = {0, 0, 255}));
  connect(PLoad.positivePlug, Transformer.positivePlug1) 
    annotation(Line(origin = {8, 7}, 
    points = {{8.000000000000007, -15}, {-2, -15}, {-2, 13.69141807364267}, {-7.5361752941176725, 13.69141807364267}}, 
    color = {0, 0, 255}));
end System6;