model SCIMSystem "异步电机示例"
annotation (Documentation(link="modelica://TYMotor/Resources/HTML/SCIMSystem.html"),Protection(access=Access.nonPackageDuplicate));
  extends TYMotor.Utilities.Icons.Common.Example;
  Modelica.Electrical.MultiPhase.Basic.Star star 
    annotation (Placement(transformation(origin = {-37.999999999999986, 36.0}, 
      extent = {{10.0, -10.0}, {-10.0, 10.0}})));
  Modelica.Electrical.Analog.Basic.Ground ground 
    annotation (Placement(transformation(origin = {-65.99999999999999, 36.0}, 
      extent = {{10.0, -10.0}, {-10.0, 10.0}}, 
      rotation = -90.0)));
  Modelica.Electrical.MultiPhase.Sources.SineVoltage sineVoltage(V = fill(100, 3), freqHz = fill(1, 3)) 
    annotation (Placement(transformation(origin = {-15.999999999999993, 18.000000000000004}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
      rotation = 90.0)));
  Modelica.Mechanics.Rotational.Sources.TorqueStep torqueStep(stepTorque = -100, startTime = 1.2, offsetTorque = 0) 
    annotation (Placement(transformation(origin = {32.000000000000014, -34.000000000000014}, 
      extent = {{10.0, -10.0}, {-10.0, 10.0}})));
  TYMotor.Machines.Asynchronous.IM_SquirrelCage SCIM1(Rs = 1.275, p = 6) 
    annotation (Placement(transformation(origin = {-16.0, -34.000000000000014}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
equation
  connect(ground.p, star.pin_n) 
    annotation (Line(origin = {-57.99999999999999, 36.0}, 
      points = {{2.0, 0.0}, {10.0, 0.0}}, 
      color = {0, 0, 255}));
  connect(star.plug_p, sineVoltage.plug_n) 
    annotation (Line(origin = {-20.999999999999993, 53.0}, 
      points = {{-7.0, -17.0}, {5.0, -17.0}, {5.0, -25.0}}, 
      color = {0, 0, 255}));
  connect(SCIM1.flange_a, torqueStep.flange) 
    annotation (Line(origin = {23.999999999999993, -34.000000000000014}, 
      points = {{-27.0, 0.0}, {-2.0, 0.0}}, 
      color = {0, 0, 0}));
  annotation (Documentation(info="<html><p>
该案例为异步电机的应用实例，可以在特定的输入电压与输出转矩下模拟<span style=\"color: rgb(51, 51, 51); background-color: rgb(243, 243, 243);\">异步电机</span>工作时的机械特性和损耗。
</p>
</html>"), Icon(graphics, coordinateSystem(preserveAspectRatio = true, extent = {{-100, -100}, {100, 100}})), Diagram(graphics, coordinateSystem(preserveAspectRatio = true, extent = {{-100, -100}, {100, 100}})), experiment(StartTime = 0, StopTime = 3, Interval = 0.001, Algorithm = Dassl, Tolerance = 0.0001, DoublePrecision = true), __MWorks(ResultViewerManager(resultViewers={
ResultViewer(name="1", executeTrigger=executeTrigger.SimulationFinished, commands={
CreatePlot(id=1, x_display_unit="s", legend_layout=1, left_title_type=2, left_title="电流/A", bottom_title_type=2, bottom_title="时间/s", right_title_type=2, fix_time_range_value=0, zoom_x=(0, 3), zoom_y_l=(-60, 60)), 
Plot(y=["SCIM1.is[1]", "SCIM1.is[2]", "SCIM1.is[3]"], colors=["4278190335", "4294901760", "4278222848"])})
})));
  connect(SCIM1.positivePlug, sineVoltage.plug_p) 
    annotation (Line(origin = {-22.0, -6.0}, 
      points = {{6.0, -6.0}, {6.0, 14.0}}, 
      color = {0, 0, 255}));
end SCIMSystem;