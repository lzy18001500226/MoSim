model ACGenerator "交流发电机示例"
annotation (Documentation(link="modelica://TYMotor/Resources/HTML/ACGenerator.html"),Protection(access=Access.nonPackageDuplicate),__MWORKS(ResultViewerManager(resultViewers={
ResultViewer(name="1", executeTrigger=executeTrigger.SimulationFinished, commands={
CreatePlot(id=1, x_display_unit="s", legend_layout=1, left_title_type=2, left_title="电机电压/V", bottom_title_type=2, bottom_title="时间/s", fix_time_range_value=0, zoom_x=(0, 50), zoom_y_l=(-40, 40)), 
Plot(y=["PMSM1.plugSupply.pin[1].v", "PMSM1.plugSupply.pin[2].v", "PMSM1.plugSupply.pin[3].v"], colors=["4278190335", "4294901760", "4278222848"])})
})));
  extends TYMotor.Utilities.Icons.Common.Example;
  TYMotor.Sensors.CurrentSensor currentmeasure 
    annotation (Placement(transformation(origin={-32,-1.9999999999999973}, 
extent={{-10,-10},{10,10}}, 
rotation=90)));
  TYMotor.Machines.Synchronous.PMSM PMSM1(V0 = 112.3, 
    p = 6, Rs = 1.275, Lssigma = 0.00047, Lmd = 0.00975, Lmq = 0.00975, J_Rotor = 0.05) annotation (Placement(transformation(origin = {-42.0, -46.0}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  Modelica.Mechanics.Rotational.Sources.Speed speed 
    annotation (Placement(transformation(origin = {0.0, -46.0}, 
      extent = {{10.0, -10.0}, {-10.0, 10.0}})));
  Modelica.Blocks.Sources.Sine sine(offset=50, f=0.1, amplitude=0) annotation (Placement(transformation(origin = {42.0, -46.0}, 
      extent = {{10.0, -10.0}, {-10.0, 10.0}})));
  Modelica.Electrical.MultiPhase.Basic.Star star 
    annotation (Placement(transformation(origin = {18.0, 15.999999999999996}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  Modelica.Electrical.MultiPhase.Basic.Resistor resistor 
    annotation (Placement(transformation(origin = {-11.999999999999998, 15.999999999999996}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  Modelica.Electrical.Analog.Basic.Ground ground 
    annotation (Placement(transformation(origin = {42.0, -1.9999999999999987}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
equation
  connect(PMSM1.flange_a, speed.flange) 
    annotation (Line(origin = {-19.0, -46.0}, 
      points = {{-10.0, 0.0}, {9.0, 0.0}}, 
      color = {0, 0, 0}));
  connect(speed.w_ref, sine.y) 
    annotation (Line(origin = {28.0, -46.0}, 
      points = {{-16.0, 0.0}, {3.0, 0.0}}, 
      color = {0, 0, 127}));
  connect(currentmeasure.plug_n, resistor.plug_p) 
    annotation (Line(origin={-36,21}, 
points={{-5.850000000000001,-18.9},{-5.850000000000001,-5.0000000000000036},{14,-5.0000000000000036}}, 
color={0,0,255}));
  connect(resistor.plug_n, star.plug_p) 
    annotation (Line(origin = {7.9999999999999964, 16.0}, 
      points = {{-10.0, 0.0}, {0.0, 0.0}}, 
      color = {0, 0, 255}));
  connect(star.pin_n, ground.p) 
    annotation (Line(origin = {38.0, 12.0}, 
      points = {{-10.0, 4.0}, {4.0, 4.0}, {4.0, -4.0}}, 
      color = {0, 0, 255}));
  annotation (experiment(Algorithm = Dassl, IntegratorStep = -1, Interval = 0.01, StartTime = 0, StopTime = 50, Tolerance = 0.0001), 
    Documentation(info="<html><p>
该实例为交流发电机的应用实例，发电机的转轴转速由speed和sine模块决定。该实例可以模拟三相交流发电机在特定转速曲线下的发电能力。
</p>
</html>"));
  connect(currentmeasure.plug_p, PMSM1.plugSupply) 
    annotation (Line(origin={-42,-23}, 
points={{0.1389999999999958,17.01},{0.1389999999999958,-10.200000000000003},{0,-10.200000000000003}}, 
color={0,0,255}));
end ACGenerator;