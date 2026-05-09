model FlyBackConverter "反激电路"
  annotation(Diagram(coordinateSystem(extent={{-200,-100},{200,100}}, 
grid={2,2})),experiment(Algorithm=Dassl,InlineIntegrator=false,InlineStepSize=false,Interval=1e-07,StartTime=0,StopTime=0.005,Tolerance=0.0001),__MWORKS(ContinueSimConfig(SaveContinueFile="false",SaveBeforeStop="false",NumberBeforeStop=1,FixedContinueInterval="false",ContinueIntervalLength=0.0005,ContinueTimeVector),ResultViewerManager(resultViewers={
ResultViewer(name="1", executeTrigger=executeTrigger.SimulationFinished, commands={
CreatePlot(id=1, position=[0, 28, 2029, 790], y=["voltageSensor.v"], x_display_unit="s", y_display_units=["V"], y_axis=[1], legend_layout=7, legend_frame=True, left_title="[V]", fix_time_range_value=6.95225e-310)})
})),Icon(coordinateSystem(extent={{-100,-100},{100,100}}, 
grid={2,2}),graphics = {Polygon(origin={-3.55271e-15,27}, 
lineColor={85,0,255}, 
fillColor={85,0,255}, 
fillPattern=FillPattern.Solid, 
points={{-64,1},{0,37},{64,1},{0,-37}}), Line(origin={3.55271e-15,-18}, 
points={{-62,18},{0,-18},{62,18}}, 
color={85,0,255}, 
thickness=5), Line(origin={1.06581e-14,-46}, 
points={{-62,18},{0,-18},{62,18}}, 
color={85,0,255}, 
thickness=5)}), 
Documentation(link = "modelica://TYElectrical/Resources/Example/FlyBackConverter.html"));
  TYElectrical.Semiconductors.GateDriver gateDriver(ModelingOption="电接口输入", Vgs_on = 5, ONdelay = 10e-9, OFFdelay = 10e-9, Ron = 100, Roff = 10) 
    annotation (Placement(transformation(origin={-105,6.0136}, 
extent={{-10,-10},{10,10}})));
  TYElectrical.Semiconductors.NchannelMOSFET nchannelMOSFET(Rds_on=0.01,Id_on=20,Vgs_on=5,vth=2,Rs=0.001,Rd=0.001,Coss=161e-12,Crss=160e-12,Ciss=700e-12) 
    annotation (Placement(transformation(origin={-64,12.0136}, 
extent={{-10,-10},{10,10}})));
  TYElectrical.BasicComponents.IdealElectricSource.DCVoltageSource dCVoltageSource(v0=5) 
    annotation (Placement(transformation(origin={-60,70.0136}, 
extent={{-10,-10},{10,10}}, 
rotation=180)));
  TYElectrical.BasicComponents.IdealBasicComponents.ElectricalReference electricalReference 
    annotation (Placement(transformation(origin={-106,70}, 
extent={{-10,-10},{10,10}}, 
rotation=270)));
  TYElectrical.BasicComponents.IdealBasicComponents.MutualInductor mutualInductor(L1=1e-6,L2=9e-6,k=0.99) 
    annotation (Placement(transformation(origin={-8,60.0136}, 
extent={{-10,-10},{10,10}})));
  TYElectrical.Sensors.PowerSensor powerSensor(PowerType="平均功率", Average_time = 1 / 50e3) 
    annotation (Placement(transformation(origin={-28,6.0136}, 
extent={{-10,-10},{10,10}}, 
rotation=270)));
  TYElectrical.BasicComponents.IdealBasicComponents.ElectricalReference electricalReference1 
    annotation (Placement(transformation(origin={174,70.0136}, 
extent={{-10,-10},{10,10}}, 
rotation=90)));
  TYElectrical.DigitalComponents.GeneralCircuits.ControlledPWMVoltage controlledPWMVoltage(ModelingOption=2,f=50e3,SimulationMode=1) 
    annotation (Placement(transformation(origin={-146,6.0136}, 
extent={{-10,-10},{10,10}})));
  TYElectrical.BasicComponents.IdealBasicComponents.ElectricalReference electricalReference2 
    annotation (Placement(transformation(origin={-110,-18}, 
extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Nonlinear.Limiter limiter(uMax=0.65,uMin=0.01) 
    annotation (Placement(transformation(origin={-172,-46}, 
extent={{10,-10},{-10,10}})));
  Modelica.Blocks.Math.Feedback feedback 
    annotation (Placement(transformation(origin={-104,-46}, 
extent={{10,-10},{-10,10}})));
  Modelica.Blocks.Sources.Constant Vref(k=15) 
    annotation (Placement(transformation(origin={-70,-46}, 
extent={{10,-10},{-10,10}})));
  TYElectrical.BasicComponents.IdealBasicComponents.Capacitor capacitor(C(displayUnit="uF")=0.0001) 
    annotation (Placement(transformation(origin={36,-23.9864}, 
extent={{-10,-10},{10,10}}, 
rotation=270)));
  TYElectrical.BasicComponents.IdealBasicComponents.Diode diode(v_f=0.25,R_on=1) 
    annotation (Placement(transformation(origin={22,50}, 
extent={{-10,-10},{10,10}})));
  TYElectrical.BasicComponents.IdealSensors.VoltageSensor voltageSensor 
    annotation (Placement(transformation(origin={140,50}, 
extent={{-10,-10},{10,10}})));
  TYElectrical.BasicComponents.IdealBasicComponents.Resistor resistor(R=15) 
    annotation (Placement(transformation(origin={124,-23.9864}, 
extent={{-10,-10},{10,10}}, 
rotation=270)));
  TYElectrical.BasicComponents.IdealElectricSource.ControlledCurrentSource controlledCurrentSource 
    annotation (Placement(transformation(origin={93,-23.9864}, 
extent={{10,-10},{-10,10}}, 
rotation=-270)));
  Modelica.Blocks.Sources.Pulse pulse(amplitude=1,period=1/500,startTime=1e-6) 
    annotation (Placement(transformation(origin={62,-24.5056}, 
extent={{-10,-10},{10,10}})));
  TYElectrical.BasicComponents.IdealBasicComponents.ElectricalReference electricalReference3 
    annotation (Placement(transformation(origin={36.0136,-76}, 
extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Continuous.PI PI(k=0.25,T=0.001) 
    annotation (Placement(transformation(origin={-138,-46}, 
extent={{10,-10},{-10,10}})));
  equation
  connect(dCVoltageSource.n, electricalReference.p) 
  annotation(Line(origin={-148,1.0136}, 
points={{77.8712,68.9864},{52,68.9864},{52,68.9864}}, 
color={0,0,255}));
  connect(mutualInductor.p2, electricalReference1.p) 
  annotation(Line(origin={14,70.0136}, 
points={{-12,0},{150,0}}, 
color={0,0,255}));
  connect(dCVoltageSource.p, mutualInductor.p1) 
  annotation(Line(origin={-83,56.0136}, 
points={{33.1024,14.0542},{65,14.0542},{65,14}}, 
color={0,0,255}));
  connect(powerSensor.p, nchannelMOSFET.D) 
  annotation(Line(origin={-44,16.0136}, 
points={{15.9,0},{15.9,7.9864},{-9.86909,7.9864},{-9.86909,1.85455}}, 
color={0,0,255}));
  connect(powerSensor.n, nchannelMOSFET.S) 
  annotation(Line(origin={-39,0.0136}, 
points={{11,-4},{11,-8},{-14.92,-8},{-14.92,5.94182}}, 
color={0,0,255}));
  connect(powerSensor.S, mutualInductor.n1) 
  annotation(Line(origin={-30,36.0136}, 
points={{7.6,-20},{7.6,14},{12,14}}, 
color={0,0,255}));
  connect(controlledPWMVoltage.PWM, gateDriver.PWM) 
  annotation(Line(origin={-95,-6.9864}, 
points={{-41,17},{-19.8,17},{-19.8,19}}, 
color={0,0,255}));
  connect(controlledPWMVoltage.REF, gateDriver.REF) 
  annotation(Line(origin={-109,1.3554}, 
points={{-27,0.6582},{-5.8,0.6582},{-5.8,-1.3418}}, 
color={0,0,255}));
  connect(nchannelMOSFET.G, gateDriver.G) 
  annotation(Line(origin={-78,12.0136}, 
points={{3.97091,0},{-17,0}}, 
color={0,0,255}));
  connect(PI.y, limiter.u) 
  annotation(Line(origin={-239,-50.0136}, 
points={{90,4.0136},{79,4.0136}}, 
color={0,0,127}));
  connect(controlledPWMVoltage.u, limiter.y) 
  annotation(Line(origin={-137,13}, 
points={{-20,0.0136},{-51,0.0136},{-51,-59},{-46,-59}}, 
color={0,0,127}));
  connect(PI.u, feedback.y) 
  annotation(Line(origin={-261,-50.0136}, 
points={{135,4.0136},{148,4.0136}}, 
color={0,0,127}));
  connect(feedback.u1, Vref.y) 
  annotation(Line(origin={-282,-50.0136}, 
points={{186,4.0136},{201,4.0136}}, 
color={0,0,127}));
  connect(diode.p, mutualInductor.n2) 
  annotation(Line(origin={10,46}, 
points={{1.89764,3.94579},{-8,3.94579},{-8,4.0136}}, 
color={0,0,255}));
  connect(diode.n, capacitor.p) 
  annotation(Line(origin={34,18}, 
points={{-1.8712,32.0136},{1.94579,32.0136},{1.94579,-31.884}}, 
color={0,0,255}));
  connect(pulse.y, controlledCurrentSource.i_T) 
  annotation(Line(origin={50,-59}, 
points={{23,34.4944},{33.1629,34.4944},{33.1629,34.4944}}, 
color={0,0,127}));
  connect(diode.n, voltageSensor.p) 
  annotation(Line(origin={68,50}, 
points={{-35.8712,0.0135696},{62,0.0135696},{62,0}}, 
color={0,0,255}));
  connect(resistor.p, diode.n) 
  annotation(Line(origin={64,18}, 
points={{59.9458,-31.884},{59.9458,32.0136},{-31.8712,32.0136}}, 
color={0,0,255}));
  connect(capacitor.n, electricalReference3.p) 
  annotation(Line(origin={36,-46}, 
points={{0.0135696,11.8848},{0.0135696,-20},{0.0136,-20}}, 
color={0,0,255}));
  connect(voltageSensor.n, electricalReference1.p) 
  annotation(Line(origin={157,60}, 
points={{-7,-10},{7,-10},{7,10.0136}}, 
color={0,0,255}));
  connect(voltageSensor.v, feedback.u2) 
  annotation(Line(origin={18,-38}, 
points={{122,77},{122,-50},{-122,-50},{-122,-16}}, 
color={0,0,127}));
  connect(resistor.n, electricalReference3.p) 
  annotation(Line(origin={80,-50}, 
points={{44.0136,15.8848},{44.0136,-16},{-43.9864,-16}}, 
color={0,0,255}));
  connect(nchannelMOSFET.S, electricalReference3.p) 
  annotation(Line(origin={-9,-30}, 
points={{-44.92,35.9554},{-44.92,-36},{45.0136,-36}}, 
color={0,0,255}));
  connect(controlledCurrentSource.p, diode.n) 
  annotation(Line(origin={63,18}, 
points={{30.0542,-31.884},{30.0542,32.0136},{-30.8712,32.0136}}, 
color={0,0,255}));
  connect(controlledCurrentSource.n, electricalReference3.p) 
  annotation(Line(origin={65,-50}, 
points={{27.9864,15.8848},{27.9864,-16},{-28.9864,-16}}, 
color={0,0,255}));
  connect(gateDriver.S, nchannelMOSFET.S) 
  annotation(Line(origin={-74,3}, 
points={{-21,-2.9864},{20.08,-2.9864},{20.08,2.95542}}, 
color={0,0,255}));
  connect(electricalReference2.p, gateDriver.REF) 
  annotation(Line(origin={-112,-4}, 
points={{2,-4},{-2.8,-4},{-2.8,4.0136}}, 
color={0,0,255}));
  end FlyBackConverter;