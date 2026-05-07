model System2 "输电系统"
  annotation(Documentation(link = "modelica://TYElectricPower/Resources/HTML/System2.html"), Protection(access = Access.nonPackageDuplicate),__MWORKS(ResultViewerManager(resultViewers={
ResultViewer(name="典型曲线", executeTrigger=executeTrigger.SimulationFinished, commands={
CreatePlot(id=1, x_display_unit="s", legend_layout=1, left_title_type=2, left_title="有功功率[W]", bottom_title_type=2, bottom_title="时间/s", right_title_type=2, right_title="[var]", fix_time_range_value=0, zoom_x=(0, 1), zoom_y_l=(-2000, 8000)), 
Plot(y=["transformer.powerSensor.P"], colors=["4278190335"]), 
CreatePlot(id=-1, x_display_unit="s", legend_layout=1, left_title_type=2, left_title="电流[A]", bottom_title_type=2, bottom_title="时间/s", fix_time_range_value=0, sub_plot=(2, 1), zoom_x=(0, 1), zoom_y_l=(-30, 30)), 
Plot(y=["CB.i"], colors=["4278190335"])})
})));
  import Modelica.Constants.pi;
  extends TYElectricPower.Icons.Example;
  annotation(Icon(coordinateSystem(extent = {{-100.0, -100.0}, {100.0, 100.0}}, 
    grid = {2.0, 2.0})), 

    Documentation(info = "<html><p>
该案例体现了输电系统的应用实例，发电机发出电能，经变压器、断路器与输电线路相连接。
</p>
</html>"), Diagram(coordinateSystem(extent = {{-100, -100}, {100, 100}}, 
    grid = {2, 2})));
  TYElectricPower.Primary.Generator generator1 annotation(Placement(transformation(origin = {-86.00000000000001, 14.122345532566328}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYElectricPower.Primary.CB CB(mode = 1, t1 = 0.5, t2 = 0.8) annotation(Placement(transformation(origin = {0.0, 34.536763852714685}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYElectricPower.Basic.Common.Impedance impedance 
    annotation(Placement(transformation(origin = {48, 12.711736147285297}, 
    extent = {{-10, -10}, {10, 10}})));
  Modelica.Electrical.Polyphase.Basic.Star star 
    annotation(Placement(transformation(origin = {72, 12.731618073642665}, 
    extent = {{-10, -10}, {10, 10}})));
  Modelica.Electrical.Analog.Basic.Ground ground 
    annotation(Placement(transformation(origin = {86.0, -26.0}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYElectricPower.Primary.CB CB1(mode = 1, t1 = 0.5, t2 = 0.8) annotation(Placement(transformation(origin = {8.881784197001252e-16, 12.731618073642665}, 
    extent = {{-10, -10}, {10, 10}})));
  TYElectricPower.Primary.CB CB2(mode = 1, t1 = 0.5, t2 = 0.8) annotation(Placement(transformation(origin = {0.0, -8.0}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYElectricPower.Primary.Transformer transformer 
    annotation(Placement(transformation(origin = {-55.00000000000001, 12.711736147285297}, 
    extent = {{-10, -10}, {10, 10}})));
  TYElectricPower.Interfaces.Electrical.PlugToPins_p plugToPins 
    annotation(Placement(transformation(origin = {-34, 12.711736147285297}, 
    extent = {{-10, -10}, {10, 10}})));
  TYElectricPower.Interfaces.Electrical.PlugToPins_p plugToPins1 
    annotation(Placement(transformation(origin = {30, 12.611736147285297}, 
    extent = {{10, -10}, {-10, 10}})));
equation
  connect(impedance.n, star.plug_p) 
    annotation(Line(origin = {53, 13}, 
    points = {{5.100000000000001, -0.38826385271470265}, {9, -0.38826385271470265}, {9, -0.2683819263573355}}, 
    color = {0, 0, 255}));
  connect(ground.p, star.pin_n) 
    annotation(Line(origin = {83, -1}, 
    points = {{3, -15}, {3, 13.731618073642665}, {-1, 13.731618073642665}}, 
    color = {0, 0, 255}));
  connect(generator1.PowerSupply, transformer.positivePlug) 
    annotation(Line(origin = {-67, 13}, 
    points = {{-10.5183812625027, 0.4618835325663291}, {2, 0.4618835325663291}, {2, -0.288263852714703}}, 
    color = {0, 0, 255}));
  connect(transformer.positivePlug1, plugToPins.plug_p) 
    annotation(Line(origin = {-40, 13}, 
    points = {{-5.000000000000007, -0.288263852714703}, {4, -0.288263852714703}}, 
    color = {0, 0, 255}));
  connect(plugToPins.pin_p[1], CB.p) 
    annotation(Line(origin = {-21, 24}, 
    points = {{-11, -11.288263852714703}, {3, -11.288263852714703}, {3, 10.536763852714685}, {11, 10.536763852714685}}, 
    color = {0, 0, 255}));
  connect(plugToPins.pin_p[2], CB1.p) 
    annotation(Line(origin = {-21, 13}, 
    points = {{-11, -0.288263852714703}, {11, -0.288263852714703}, {11, -0.2683819263573355}}, 
    color = {0, 0, 255}));
  connect(plugToPins.pin_p[3], CB2.p) 
    annotation(Line(origin = {-21, 2}, 
    points = {{-11, 10.711736147285297}, {3, 10.711736147285297}, {3, -10}, {11, -10}}, 
    color = {0, 0, 255}));
  connect(plugToPins1.plug_p, impedance.p) 
    annotation(Line(origin = {35, 13}, 
    points = {{-3, -0.38826385271470265}, {2.8999999999999986, -0.38826385271470265}}, 
    color = {0, 0, 255}));
  connect(CB.n, plugToPins1.pin_p[1]) 
    annotation(Line(origin = {19, 24}, 
    points = {{-9, 10.536763852714685}, {-1, 10.536763852714685}, {-1, -11.388263852714703}, {9, -11.388263852714703}}, 
    color = {0, 0, 255}));
  connect(CB1.n, plugToPins1.pin_p[2]) 
    annotation(Line(origin = {19, 13}, 
    points = {{-9, -0.2683819263573355}, {9, -0.2683819263573355}, {9, -0.38826385271470265}}, 
    color = {0, 0, 255}));
  connect(CB2.n, plugToPins1.pin_p[3]) 
    annotation(Line(origin = {19, 2}, 
    points = {{-9, -10}, {-1, -10}, {-1, 10.611736147285297}, {9, 10.611736147285297}}, 
    color = {0, 0, 255}));
end System2;