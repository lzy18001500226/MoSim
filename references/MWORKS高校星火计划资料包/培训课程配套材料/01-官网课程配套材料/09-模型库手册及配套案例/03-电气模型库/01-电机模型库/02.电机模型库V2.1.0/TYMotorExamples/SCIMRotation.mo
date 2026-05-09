model SCIMRotation "异步电机正反转示例"
annotation (Documentation(link="modelica://TYMotor/Resources/HTML/SCIMRotation.html"),Protection(access=Access.nonPackageDuplicate));
  extends TYMotor.Utilities.Icons.Common.Example;
  TYMotor.Machines.Asynchronous.IM_SquirrelCage SCIM 
    annotation (Placement(transformation(origin={2,-90}, 
extent={{-7,-7},{7,7}})));
  Modelica.Electrical.Polyphase.Sources.SineVoltage sineVoltage(V=fill(220, 3),f=fill(50, 3)) 
    annotation (Placement(transformation(origin={-48,62}, 
extent={{10,-10},{-10,10}})));
  Modelica.Electrical.Polyphase.Basic.Star star 
    annotation (Placement(transformation(origin={-76,62}, 
extent={{10,-10},{-10,10}})));
  Modelica.Electrical.Spice3.Basic.Ground ground 
    annotation (Placement(transformation(origin={-92,38}, 
extent={{-10,-10},{10,10}})));
  Modelica.Electrical.Analog.Ideal.IdealClosingSwitch switch1 
    annotation (Placement(transformation(origin={18,40}, 
extent={{10,10},{-10,-10}}, 
rotation=90)));
  Modelica.Electrical.Analog.Ideal.IdealClosingSwitch switch2 
    annotation (Placement(transformation(origin={36,21}, 
extent={{10,10},{-10,-10}}, 
rotation=90)));
  Modelica.Electrical.Analog.Ideal.IdealClosingSwitch switch3 
    annotation (Placement(transformation(origin={52,1}, 
extent={{10,10},{-10,-10}}, 
rotation=90)));
  Modelica.Blocks.Sources.BooleanPulse Pulse_C 
    annotation (Placement(transformation(origin={91,40}, 
extent={{7,-7},{-7,7}})));
  Modelica.Electrical.Analog.Ideal.IdealOpeningSwitch switch 
    annotation (Placement(transformation(origin={-48,-14}, 
extent={{-10,-10},{10,10}}, 
rotation=-90)));
  Modelica.Electrical.Analog.Ideal.IdealOpeningSwitch switch4 
    annotation (Placement(transformation(origin={-31,-32}, 
extent={{-10,-10},{10,10}}, 
rotation=-90)));
  Modelica.Electrical.Analog.Ideal.IdealOpeningSwitch switch5 
    annotation (Placement(transformation(origin={-16,-52}, 
extent={{-10,-10},{10,10}}, 
rotation=-90)));
  Modelica.Electrical.Polyphase.Ideal.IdealClosingSwitch switch7 
    annotation (Placement(transformation(origin={-31,38}, 
extent={{-10,-10},{10,10}}, 
rotation=-90)));
  Modelica.Electrical.Polyphase.Ideal.IdealOpeningSwitch switch8 
    annotation (Placement(transformation(origin={2,62}, 
extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Sources.BooleanPulse Pulse_C1[3](period=2) 
    annotation (Placement(transformation(origin={-31,86}, 
extent={{-7,-7},{7,7}})));
  Modelica.Mechanics.Rotational.Sources.TorqueStep torqueStep(stepTorque = 0, startTime = 0.5, offsetTorque = 0) 
    annotation (Placement(transformation(origin={33,-90}, 
extent={{7,-7},{-7,7}})));
  annotation(Diagram(coordinateSystem(extent={{-100,-100},{100,100}}, 
grid={2,2})),experiment(Algorithm=Dassl,InlineIntegrator=false,InlineStepSize=false,Interval=0.002,StartTime=0,StopTime=10,Tolerance=0.0001),__MWORKS(ContinueSimConfig(SaveContinueFile="false",SaveBeforeStop="false",NumberBeforeStop=1,FixedContinueInterval="false",ContinueIntervalLength=10,ContinueTimeVector),ResultViewerManager(resultViewers={
ResultViewer(name="1", executeTrigger=executeTrigger.SimulationFinished, commands={
CreatePlot(id=1, x_display_unit="s", legend_layout=1, left_title_type=2, left_title="转速[rad/s]", bottom_title_type=2, bottom_title="时间/s", fix_time_range_value=0, zoom_x=(0, 10), zoom_y_l=(-150, 100)), 
Plot(y=["SCIM.w"], colors=["4278190335"])})
})));
  equation
  connect(star.plug_p, sineVoltage.plug_n) 
  annotation(Line(origin={-65,62}, 
points={{-1,0},{7,0}}, 
color={0,0,255}));
  connect(ground.p, star.pin_n) 
  annotation(Line(origin={-100,51}, 
points={{8,-3},{8,11},{14,11}}, 
color={0,0,255}));
  connect(switch7.plug_n.pin[1], switch.p) 
  annotation(Line(origin={-36,8}, 
points={{5,20},{5,8},{-12,8},{-12,-12}}, 
color={0,0,255}));
  connect(switch7.plug_n.pin[2], switch4.p) 
  annotation(Line(origin={-23,-4}, 
points={{-8,32},{-8,-18}}, 
color={0,0,255}));
  connect(switch7.plug_n.pin[3], switch5.p) 
  annotation(Line(origin={-12,-15}, 
points={{-19,43},{-19,31},{-4,31},{-4,-27}}, 
color={0,0,255}));
  connect(switch.n, SCIM.positivePlug.pin[3]) 
  annotation(Line(origin={-25,-75}, 
points={{-23,51},{-23,3},{27.14,3},{27.14,-6.46}}, 
color={0,0,255}));
  connect(switch4.n, SCIM.positivePlug.pin[2]) 
  annotation(Line(origin={-12,-87}, 
points={{-19,45},{-19,15},{14.14,15},{14.14,5.54}}, 
color={0,0,255}));
  connect(switch5.n, SCIM.positivePlug.pin[1]) 
  annotation(Line(origin={-2,-100}, 
points={{-14,38},{-14,28},{4.14,28},{4.14,18.54}}, 
color={0,0,255}));
  connect(sineVoltage.plug_p, switch8.plug_p) 
  annotation(Line(origin={-14,62}, 
points={{-24,0},{6,0}}, 
color={0,0,255}));
  connect(switch8.plug_n.pin[1], switch1.p) 
  annotation(Line(origin={40,43}, 
points={{-28,19},{-22,19},{-22,7}}, 
color={0,0,255}));
  connect(switch8.plug_n.pin[2], switch2.p) 
  annotation(Line(origin={53,30}, 
points={{-41,32},{-17,32},{-17,1}}, 
color={0,0,255}));
  connect(switch8.plug_n.pin[3], switch3.p) 
  annotation(Line(origin={65,20}, 
points={{-53,42},{-13,42},{-13,-9}}, 
color={0,0,255}));
  connect(switch2.n, SCIM.positivePlug.pin[2]) 
  annotation(Line(origin={34,-66}, 
points={{2,77},{2,-6},{-31.86,-6},{-31.86,-15.46}}, 
color={0,0,255}));
  connect(switch3.n, SCIM.positivePlug.pin[3]) 
  annotation(Line(origin={46,-75}, 
points={{6,66},{6,3},{-43.86,3},{-43.86,-6.46}}, 
color={0,0,255}));
  connect(switch1.n, SCIM.positivePlug.pin[1]) 
  annotation(Line(origin={21,-52}, 
points={{-3,82},{-3,-20},{-18.86,-20},{-18.86,-29.46}}, 
color={0,0,255}));
  connect(switch7.plug_p, switch8.plug_p) 
  annotation(Line(origin={-6,55}, 
points={{-25,-7},{-25,7},{-2,7}}, 
color={0,0,255}));
  connect(Pulse_C.y, switch1.control) 
  annotation(Line(origin={94,26}, 
points={{-10.7,14},{-64,14}}, 
color={255,0,255}));
  connect(switch2.control, Pulse_C.y) 
  annotation(Line(origin={114,10}, 
points={{-66,11},{-38,11},{-38,30},{-30.7,30}}, 
color={255,0,255}));
  connect(switch3.control, Pulse_C.y) 
  annotation(Line(origin={127,0}, 
points={{-63,1},{-51,1},{-51,40},{-43.7,40}}, 
color={255,0,255}));
  connect(switch5.control, Pulse_C.y) 
  annotation(Line(origin={78,-11}, 
points={{-82,-41},{-2,-41},{-2,51},{5.3,51}}, 
color={255,0,255}));
  connect(switch4.control, Pulse_C.y) 
  annotation(Line(origin={67,2}, 
points={{-86,-34},{9,-34},{9,38},{16.3,38}}, 
color={255,0,255}));
  connect(switch.control, Pulse_C.y) 
  annotation(Line(origin={54,14}, 
points={{-90,-28},{22,-28},{22,26},{29.3,26}}, 
color={255,0,255}));
  connect(Pulse_C1.y, switch8.control) 
  annotation(Line(origin={3,89}, 
points={{-26.3,-3},{-1,-3},{-1,-15}}, 
color={255,0,255}));
  connect(Pulse_C1.y, switch7.control) 
  annotation(Line(origin={-8,71}, 
points={{-15.3,15},{-6,15},{-6,-33},{-11,-33}}, 
color={255,0,255}));
  connect(SCIM.flange_a, torqueStep.flange) 
  annotation(Line(origin={18,-90}, 
points={{-7.6,0},{8,0}}, 
color={0,0,0}));
  end SCIMRotation;