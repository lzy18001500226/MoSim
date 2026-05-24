model SCIMOpenLoop "异步电机开环系统示例"
annotation (Documentation(link="modelica://TYMotor/Resources/HTML/SCIMOpenLoop.html"));
   extends TYMotor.Utilities.Icons.Common.Example;
  TYMotor.Converters.IdealSwitching.DCAC.ThreePhase DCAC(RonTransistor = 1e-3, 
    IConverterMax = 10000000)  annotation(Placement(transformation(origin={-18,54}, 
extent={{-10,-10},{10,10}})));
  Modelica.Electrical.Analog.Basic.Ground ground 
    annotation (Placement(transformation(origin={-72,32}, 
extent={{-10,-10},{10,10}})));
  Modelica.Electrical.Analog.Sources.ConstantVoltage constantVoltage(V = 400) 
    annotation (Placement(transformation(origin={-58,56}, 
extent={{-10,-10},{10,10}}, 
rotation=-90)));
  Modelica.Blocks.Sources.BooleanPulse booleanPulse1(period = 0.02,width=50,startTime=0) 
    annotation (Placement(transformation(origin={-48,8}, 
extent={{-10,-10},{10,10}})));

  Modelica.Blocks.Sources.BooleanPulse booleanPulse2(period = 0.02, 
    startTime = 0.02/6,width=50)  annotation(Placement(transformation(origin={12,-52}, 
extent={{10,-10},{-10,10}})));
  Modelica.Blocks.Sources.BooleanPulse booleanPulse3(period = 0.02, 
    startTime = 0.02/3,width=50)  annotation(Placement(transformation(origin={-48,-22}, 
extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Sources.BooleanPulse booleanPulse4(period = 0.02, 
    startTime = 0.02/2,width=50)  annotation(Placement(transformation(origin={12,8}, 
extent={{10,-10},{-10,10}})));
  Modelica.Blocks.Sources.BooleanPulse booleanPulse5(period = 0.02, 
    startTime = -0.02/3,width=50)  annotation(Placement(transformation(origin={-48,-52}, 
extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Sources.BooleanPulse booleanPulse6(period = 0.02, 
    startTime = -0.02/6,width=50)  annotation(Placement(transformation(origin={12,-22}, 
extent={{10,-10},{-10,10}})));
  Modelica.Mechanics.Rotational.Sources.TorqueStep torqueStep1(stepTorque = -100, startTime = 0.5, offsetTorque = 0) 
    annotation (Placement(transformation(origin={84,-3}, 
extent={{10,-10},{-10,10}})));
  TYMotor.Machines.Asynchronous.IM_SquirrelCage SCIM(Rs = 1.275, p = 6) 
    annotation (Placement(transformation(origin={48,-3}, 
extent={{-10,-10},{10,10}})));
  equation
  connect(constantVoltage.n, ground.p) 
    annotation (Line(origin={-56,37}, 
points={{-2,9},{-16,9},{-16,5}}, 
color={0,0,255}));
  connect(booleanPulse1.y, DCAC.fire_p[1]) 
    annotation (Line(origin={-21,32}, 
points={{-16,-24},{-3,-24},{-3,10}}, 
color={255,0,255}),__MWORKS(BlockSystem(NamedSignal)));
  connect(booleanPulse3.y, DCAC.fire_p[2]) 
    annotation (Line(origin={-21,12}, 
points={{-16,-34},{-3,-34},{-3,30}}, 
color={255,0,255}));
  connect(booleanPulse5.y, DCAC.fire_p[3]) 
    annotation (Line(origin={-21,-9}, 
points={{-16,-43},{-3,-43},{-3,51}}, 
color={255,0,255}));
  connect(booleanPulse4.y, DCAC.fire_n[1]) 
    annotation (Line(origin={10,32}, 
points={{-9,-24},{-22,-24},{-22,10}}, 
color={255,0,255}));
  connect(booleanPulse6.y, DCAC.fire_n[2]) 
    annotation (Line(origin={10,11}, 
points={{-9,-33},{-22,-33},{-22,31}}, 
color={255,0,255}));
  connect(booleanPulse2.y, DCAC.fire_n[3]) 
    annotation (Line(origin={10,-8}, 
points={{-9,-44},{-22,-44},{-22,50}}, 
color={255,0,255}));
  connect(constantVoltage.p, DCAC.pSupply) 
    annotation (Line(origin={-42,69}, 
points={{-16,-3},{-16,-1},{14,-1},{14,-9}}, 
color={0,0,255}));
  annotation (experiment(StartTime=0,StopTime=1,Interval=0.0001,Algorithm=Dassl,Tolerance=1e-05,DoublePrecision = true,InlineIntegrator=false,InlineStepSize=false), 
    __MWorks(ResultViewerManager(resultViewers={
ResultViewer(name="1", executeTrigger=executeTrigger.SimulationFinished, commands={
CreatePlot(id=4, x_display_unit="s", legend_layout=1, left_title_type=2, left_title="转速[rad/s]", bottom_title_type=2, bottom_title="时间/s", fix_time_range_value=0, zoom_x=(0, 1), zoom_y_l=(-10, 60)), 
Plot(y=["SCIM.w"], colors=["4278190335"])})
}),ContinueSimConfig(SaveContinueFile="false",SaveBeforeStop="false",NumberBeforeStop=1,FixedContinueInterval="false",ContinueIntervalLength=0.04,ContinueTimeVector)),Diagram(coordinateSystem(extent={{-100,-100},{100,100}}, 
grid={2,2})),Protection(access=Access.nonPackageDuplicate));
  connect(constantVoltage.n, DCAC.nSupply) 
  annotation(Line(origin={-42,52}, 
points={{-16,-6},{-16,-14},{14,-14},{14,-4}}, 
color={0,0,255}));
  connect(torqueStep1.flange, SCIM.flange_a) 
  annotation(Line(origin={67,-3}, 
  points={{7,0},{-7,0}}, 
  color={0,0,0}));
  connect(DCAC.pload, SCIM.positivePlug) 
  annotation(Line(origin={20,32}, 
  points={{-28,22},{28.2,22},{28.2,-22.8}}, 
  color={0,0,255}));
  end SCIMOpenLoop;