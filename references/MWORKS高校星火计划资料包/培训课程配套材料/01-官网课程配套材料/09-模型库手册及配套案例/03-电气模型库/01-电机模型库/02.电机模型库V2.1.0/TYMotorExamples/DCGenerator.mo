model DCGenerator "直流发电机示例"
annotation (Documentation(link="modelica://TYMotor/Resources/HTML/DCGenerator.html"),Protection(access=Access.nonPackageDuplicate),__MWORKS(ResultViewerManager(resultViewers={
ResultViewer(name="1", executeTrigger=executeTrigger.SimulationFinished, commands={
CreatePlot(id=1, x_display_unit="s", legend_layout=1, left_title_type=2, left_title="电机电压/V", bottom_title_type=2, bottom_title="时间/s", fix_time_range_value=0, zoom_x=(0, 50), zoom_y_l=(-50, 200)), 
Plot(y=["PMDC1.pin_ap.v"], colors=["4278190335"])})
})));
  extends TYMotor.Utilities.Icons.Common.Example;
  Modelica.Electrical.Analog.Basic.Ground ground 
    annotation (Placement(transformation(origin = {-36.00000000000001, -17.997}, 
      extent = {{-10.0, -9.997}, {10.000000000000007, 9.997}})));
  TYMotor.Machines.DCMachines.PMDC PMDC1 
    annotation (Placement(transformation(origin = {-10.0, -10.0}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  Modelica.Mechanics.Rotational.Sources.Speed speed 
    annotation (Placement(transformation(origin = {28.0, -10.0}, 
      extent = {{10.0, -10.0}, {-10.0, 10.0}})));
  Modelica.Blocks.Sources.Sine sine(amplitude=20, offset=200, f=0.1) 
    annotation (Placement(transformation(origin = {64.0, -10.0}, 
      extent = {{10.0, -10.0}, {-10.0, 10.0}})));
  Modelica.Electrical.Analog.Basic.Resistor resistor1(R = 3) 
    annotation (Placement(transformation(origin = {-10.0, 34.000000000000014}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
      rotation = -180.0)));
equation
  connect(PMDC1.pin_an, ground.p) 
    annotation (Line(origin = {-29.0, 50.0}, 
      points = {{15.0, -48.0}, {-7.0, -48.0}, {-7.0, -58.0}}, 
      color = {0, 0, 255}));
  connect(speed.flange, PMDC1.flange_a) 
    annotation (Line(origin = {24.0, -8.0}, 
      points = {{-6.0, -2.0}, {-21.0, -2.0}}, 
      color = {0, 0, 0}));
  connect(sine.y, speed.w_ref) 
    annotation (Line(origin = {56.0, -10.0}, 
      points = {{-3.0, 0.0}, {-16.0, 0.0}}, 
      color = {0, 0, 127}));
  connect(ground.p, resistor1.n) 
    annotation (Line(origin = {-34.0, 26.0}, 
      points = {{-2.0, -34.0}, {-2.0, 8.0}, {14.0, 8.0}}, 
      color = {0, 0, 255}));
  connect(resistor1.p, PMDC1.pin_ap) 
    annotation (Line(origin = {-10.0, 16.0}, 
      points = {{10.0, 18.0}, {20.0, 18.0}, {20.0, -14.0}, {4.0, -14.0}}, 
      color = {0, 0, 255}));
  annotation (experiment(Algorithm = Dassl, IntegratorStep = -1, Interval = 0.1, StartTime = 0, StopTime = 50, Tolerance = 0.0001), 
    Documentation(info="<html><p>
该案例为直流发电机的应用实例，发电机的转轴转速由右侧的speed和sine模块确定，该实例可以模拟在特定转速曲线下直流发电机的发电情况。
</p>
</html>"));
end DCGenerator;