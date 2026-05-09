model SCIMSystem_FOC "异步电机示例"
annotation (Documentation(link="modelica://TYMotor/Resources/HTML/SCIMSystem_FOC.html"),Protection(access=Access.nonPackageDuplicate));
  extends TYMotor.Utilities.Icons.Common.Example;
 annotation (Icon(coordinateSystem(extent={{-100,-100},{100,100}}, 
grid={2,2})), 
    Diagram(coordinateSystem(extent={{-200,-200},{200,200}}, 
grid={2,2})), 
    experiment(Algorithm=Rkfix4,StartTime=0,StopTime=1,Tolerance=1e-05,Interval=1e-05,IntegratorStep=1e-05),Documentation(info="<html><p>
<span style=\"color: rgb(51, 51, 51); background-color: rgb(243, 243, 243);\">该实例为异步电机的一种应用案例，利用矢量控制器使得电机可以获得理想的，并与输出转矩对应的电压矢量，在此种模式下，模拟异步电机工作时的输出特性。</span>
</p>
</html>"),__MWORKS(ContinueSimConfig(SaveContinueFile="false",SaveBeforeStop="false",NumberBeforeStop=1,FixedContinueInterval="false",ContinueIntervalLength=0.06667,ContinueTimeVector),ResultViewerManager(resultViewers={
ResultViewer(name="1", executeTrigger=executeTrigger.SimulationFinished, commands={
CreatePlot(id=1, x_display_unit="s", legend_layout=1, left_title_type=2, left_title="转速[rev/min]", bottom_title_type=2, bottom_title="时间/s", right_title="[rad/s]", fix_time_range_value=0, zoom_x=(0, 1), zoom_y_l=(-200, 1200)), 
Plot(y=["const.y", "SCIM.w"], colors=["4278190335", "4294901760"])})
})));
  Modelica.Electrical.Analog.Basic.Ground ground 
    annotation (Placement(transformation(origin={-158,45.999999999999986}, 
extent={{-10,-10},{10,10}})));
  Modelica.Electrical.Spice3.Sources.V_constant v_constant(V = 510) 
    annotation (Placement(transformation(origin={-158,85.99999999999999}, 
extent={{-10,-10},{10,10}}, 
rotation=-90)));
  TYMotor.Converters.IdealSwitching.DCAC.ThreePhase inverter(m = 3) 
    annotation (Placement(transformation(origin={-93.00000000000003,85.99999999999996}, 
extent={{-13,-14},{13,14}})));
  TYMotor.Machines.Asynchronous.IM_SquirrelCage SCIM(Rs = 0.435, Lm = 0.069, Rr = 0.816, p = 2, fsNominal = 50, Lssigma = 0.002, Lrsigma = 0.002) 
    annotation (Placement(transformation(origin={-16.2,-102.00000000000001}, 
extent={{-10,-10},{10,10}})));
  Modelica.Mechanics.Rotational.Sources.TorqueStep torqueStep(stepTorque = -20, offsetTorque = 0, startTime = 0.5) 
    annotation (Placement(transformation(origin={80,-102.00000000000001}, 
extent={{10,-10},{-10,10}})));
  TYMotor.Sensors.AngularVelecitySensor angularVelecitySensor 
    annotation (Placement(transformation(origin={64,-72.00000000000001}, 
extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Sources.Constant const(k = 1000) 
    annotation (Placement(transformation(origin={142.1818181818182,60.999999999999986}, 
extent={{14.181818181818215,-13},{-14.181818181818187,13.000000000000014}})));
  TYMotor.Sensors.CurrentSensor currentSensor 
    annotation (Placement(transformation(origin={-6.000000000000002,-14.000000000000014}, 
extent={{-10,10},{10,-10}}, 
rotation=-90)));
  TYMotor.Controllers.IM.IMFOC_Controller IMFOC_Controller 
    annotation (Placement(transformation(origin={68,44}, 
extent={{30,-30},{-30,30}})));
  equation
  connect(ground.p, v_constant.n) 
    annotation (Line(origin={-156,53.999999999999986}, 
points={{-2,2},{-2,22}}, 
color={0,0,255}));
  connect(IMFOC_Controller.fire_p, inverter.fire_p) 
    annotation (Line(origin={-19,25.999999999999986}, 
points={{54,5.038314338455308},{-81.80000000000003,5.038314338455308},{-81.80000000000003,43.199999999999974}}, 
color={255,0,255}));
  connect(IMFOC_Controller.fire_n, inverter.fire_n) 
    annotation (Line(origin={-11,37.999999999999986}, 
points={{46,16.80000000000001},{-74.20000000000003,16.80000000000001},{-74.20000000000003,31.199999999999974}}, 
color={255,0,255}));
  connect(IMFOC_Controller.w_ref, const.y) 
    annotation (Line(origin={133,61.999999999999986}, 
points={{-32,-1.1999999999999886},{-6.418181818181836,-1.1999999999999886},{-6.418181818181836,-0.9999999999999929}}, 
color={0,0,127}));
  connect(angularVelecitySensor.w, IMFOC_Controller.w) 
    annotation (Line(origin={108,52.999999999999986}, 
points={{-33.004999999999995,-125.0018},{16,-125.0018},{16,-9.52245646196149},{-7,-9.52245646196149}}, 
color={0,0,127}));
  connect(currentSensor.plug_n, SCIM.positivePlug) 
  annotation(Line(origin={-16,-54.000000000000014}, 
points={{0.14999999999999858,35.9},{0.14999999999999858,-35.8},{0,-35.8}}, 
color={0,0,255}));
  connect(SCIM.flange_a, angularVelecitySensor.flange_a) 
  annotation(Line(origin={25,-83.00000000000001}, 
points={{-28.599999999999998,-19},{-1,-19},{-1,11},{29,11}}, 
color={0,0,0}));
  connect(torqueStep.flange, SCIM.flange_a) 
  annotation(Line(origin={33,-102.00000000000001}, 
points={{37,0},{-36.599999999999994,0}}, 
color={0,0,0}));
  connect(inverter.pload, currentSensor.plug_p) 
  annotation(Line(origin={-48,39.999999999999986}, 
points={{-32.00000000000003,45.99999999999997},{32.138999999999996,45.99999999999997},{32.138999999999996,-50.01}}, 
color={0,0,255}));
  connect(v_constant.p, inverter.pSupply) 
  annotation(Line(origin={-132,101.99999999999999}, 
points={{-26,-6},{-26,8.000000000000014},{25.99999999999997,8.000000000000014},{25.99999999999997,-7.600000000000023}}, 
color={0,0,255}));
  connect(inverter.nSupply, v_constant.n) 
  annotation(Line(origin={-133,70.99999999999999}, 
points={{26.99999999999997,6.599999999999966},{26.99999999999997,-7},{-25,-7},{-25,5}}, 
color={0,0,255}));
  connect(currentSensor.y, IMFOC_Controller.is) 
  annotation(Line(origin={58,5.999999999999986}, 
points={{-53.04,-20.045299999999997},{54,-20.045299999999997},{54,20.15508707607701},{43,20.15508707607701}}, 
color={0,0,127}));
end SCIMSystem_FOC;