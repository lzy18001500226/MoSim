model TableDCSystem "直流查表电机示例"
annotation (Documentation(link="modelica://TYMotor/Resources/HTML/TableDCSystem.html"),Protection(access=Access.nonPackageDuplicate));
  extends TYMotor.Utilities.Icons.Common.Example;
  Modelica.Electrical.Analog.Sources.SignalVoltage signalvoltage 
    annotation (Placement(transformation(origin = {-8.0, 22.0}, 
      extent = {{-10.0, 10.0}, {10.0, -10.0}}, 
      rotation = 180.0)));
  Modelica.Electrical.Analog.Basic.Ground ground 
    annotation (Placement(transformation(origin={-36.00000000000001,8.003000000000002}, 
extent={{-10,-9.997},{10.000000000000007,9.997}})));
  Modelica.Blocks.Sources.Constant const(k = 400) 
    annotation (Placement(transformation(origin = {-46.0, 48.0}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYMotor.Machines.FunctionalDevice.TableMachine TableDC(
    tableOnFile_MaxTorque = false, tableOnFile_MinTorque = false, tableOnFile_Loss = false, 
    T = 0.01) annotation (Placement(transformation(origin = {-8.0, -14.0}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  Modelica.Mechanics.Rotational.Sources.TorqueStep torqueStep(startTime = 2, stepTorque = -50, 
    offsetTorque = -50) annotation (Placement(transformation(origin = {66.0, -14.0}, 
      extent = {{10.0, -10.0}, {-10.0, 10.0}})));
  Modelica.Blocks.Sources.Step step(offset = 60, height = 80, startTime = 2) 
    annotation (Placement(transformation(origin = {-52.0, -14.0}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
equation
  connect(const.y, signalvoltage.v) 
    annotation (Line(origin = {-24.0, 70.0}, 
      points = {{-11.0, -22.0}, {16.0, -22.0}, {16.0, -36.0}}, 
      color = {0, 0, 127}));
  connect(signalvoltage.n, TableDC.pin_an) 
    annotation (Line(origin = {-16.0, 26.0}, 
      points = {{-2.0, -4.0}, {-8.0, -4.0}, {-8.0, -28.0}, {2.0, -28.0}}, 
      color = {0, 0, 255}));
  connect(signalvoltage.p, TableDC.pin_ap) 
    annotation (Line(origin = {-1.0, 26.0}, 
      points = {{3.0, -4.0}, {11.0, -4.0}, {11.0, -28.0}, {-1.0, -28.0}}, 
      color = {0, 0, 255}));
  connect(step.y, TableDC.TorqueCommand) 
    annotation (Line(origin = {-45.0, -14.0}, 
      points = {{4.0, 0.0}, {26.0, 0.0}}, 
      color = {0, 0, 127}));
  connect(TableDC.flange_a, torqueStep.flange) 
    annotation (Line(origin = {29.0, -14.0}, 
      points = {{-24.0, 0.0}, {27.0, 0.0}}, 
      color = {0, 0, 0}));
  connect(ground.p, signalvoltage.n) 
    annotation (Line(origin={-35,22}, 
points={{-1,-4},{-1,0},{17,0}}, 
color={0,0,255}));
  annotation (Diagram(coordinateSystem(extent = {{-100.0, -100.0}, {100.0, 100.0}}, 
    grid = {2.0, 2.0}), graphics = {graphics, coordinateSystem(extent = {{-140.0, -100.0}, {140.0, 100.0}}, 
    preserveAspectRatio = false, 
    grid = {2.0, 2.0})}), 
    Icon(coordinateSystem(extent = {{-100.0, -100.0}, {100.0, 100.0}}, 
      grid = {2.0, 2.0}), graphics = {graphics, coordinateSystem(extent = {{-100.0, -100.0}, {100.0, 100.0}}, 
      preserveAspectRatio = false, 
      grid = {2.0, 2.0})}), 
    experiment(Algorithm = Rkfix4, Interval = 0.001, StartTime = 0, StopTime = 4, Tolerance = 1e-07, IntegratorStep = 1e-05), 
    __MWorks(ResultViewerManager(resultViewers={
ResultViewer(name="1", executeTrigger=executeTrigger.SimulationFinished, commands={
CreatePlot(id=1, x_display_unit="s", legend_layout=1, left_title_type=2, left_title="转矩[N.m]", bottom_title_type=2, bottom_title="时间/s", fix_time_range_value=0, zoom_x=(0, 4), zoom_y_l=(-50, 200)), 
Plot(y=["TableDC.Te"], colors=["4278190335"])})
})), 
    Documentation(info="<html><p>
该案例为查表直流电机的应用案例， 常数输出组件和信号电压源组成输入电压部分，左侧step组件作为转矩输入，可模拟在特定输入电压和转矩情况下电机的机械特性和损耗。
</p>
</html>"));
end TableDCSystem;