model PWMTimer "计时器PWM电路"
  annotation(Diagram(coordinateSystem(extent={{-100,-100},{100,100}}, 
grid={2,2})),Icon(coordinateSystem(extent={{-100,-100},{100,100}}, 
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
experiment(Algorithm=Dassl,InlineIntegrator=false,InlineStepSize=false,Interval=1e-06,StartTime=0,StopTime=0.1,Tolerance=0.0001), 
__MWORKS(ContinueSimConfig(SaveContinueFile="false",SaveBeforeStop="false",NumberBeforeStop=1,FixedContinueInterval="false",ContinueIntervalLength=0.01,ContinueTimeVector),ResultViewerManager(resultViewers={
ResultViewer(name="1", executeTrigger=executeTrigger.SimulationFinished, commands={
CreatePlot(id=1, position=[0, 28, 2029, 790], y=["voltageSensor.v"], x_display_unit="s", y_display_units=["V"], y_axis=[1], legend_layout=7, legend_frame=True, left_title="[V]", fix_time_range_value=6.95225e-310)})
})), 
Documentation(link = "modelica://TYElectrical/Resources/Example/PWMTimer.html"));
  TYElectrical.DigitalComponents.GeneralCircuits.Timer timer(Vcc=15,Delay=1e-7) 
    annotation (Placement(transformation(origin={-5.9476,-7.66406}, 
extent={{-20.8358,13.7489},{20.8358,-13.0057}})));
  TYElectrical.BasicComponents.IdealElectricSource.DCVoltageSource dCVoltageSource(v0=15) 
    annotation (Placement(transformation(origin={42.4913,-27.9446}, 
extent={{10,-10},{-10,10}}, 
rotation=-270)));
  Modelica.Electrical.Analog.Basic.Ground ground 
    annotation (Placement(transformation(origin={42.2271,-57.16181}, 
extent={{-10,-10},{10,10}})));
  TYElectrical.BasicComponents.IdealBasicComponents.Capacitor C1(R=1e-6,C=20e-9) 
    annotation (Placement(transformation(origin={-59.9434,-29.25351}, 
extent={{-8.30735,-7.74314},{8.30735,7.74314}}, 
rotation=270)));
  TYElectrical.BasicComponents.IdealBasicComponents.Capacitor C2(R=1e-6,C=10e-9) 
    annotation (Placement(transformation(origin={-42.3588,-32.50301}, 
extent={{-8.30735,-7.74314},{8.30735,7.74314}}, 
rotation=270)),__MWORKS(BlockSystem(StateMachine)));
  TYElectrical.BasicComponents.IdealBasicComponents.Resistor R1(R=1000) 
    annotation (Placement(transformation(origin={42.6146,27.84109}, 
extent={{-10,-10},{10,10}}, 
rotation=270)));
  TYElectrical.BasicComponents.IdealBasicComponents.Resistor R2(R=10000) 
    annotation (Placement(transformation(origin={1.0166,58.89779}, 
extent={{10,-10},{-10,10}})),__MWORKS(BlockSystem(StateMachine)));
  TYElectrical.BasicComponents.IdealSensors.VoltageSensor voltageSensor 
    annotation (Placement(transformation(origin={68,-8}, 
extent={{-10,10},{10,-10}})));
  TYElectrical.BasicComponents.IdealBasicComponents.Diode diode 
    annotation (Placement(transformation(origin={-68.6048,42.11969}, 
extent={{-10,-10},{10,10}}, 
rotation=270)));
  TYElectrical.BasicComponents.IdealBasicComponents.Diode diode1 
    annotation (Placement(transformation(origin={-9.0507,41.92949}, 
extent={{-10,-10},{10,10}}, 
rotation=90)));
  TYElectrical.BasicComponents.Passive.BasicPassive.Potentiometer P1(R0=470e3,Taper="线性", r = 1000) 
    annotation (Placement(transformation(origin={-48.5559,20.0185}, 
extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Sources.Constant const(k=0.5) 
    annotation (Placement(transformation(origin={-90,14}, 
extent={{-10,-10},{10,10}})));
  equation
  connect(ground.p, dCVoltageSource.n) 
  annotation(Line(origin={10.2252,-36.80351}, 
points={{32.0019,-10.3583},{32.0019,-1.2699},{32.2526,-1.2699}}, 
color={0,0,255}));
  connect(C2.p, timer.CONT) 
  annotation(Line(origin={-46.7748,-3.80352}, 
points={{4.37403,-20.3071},{4.37403,-13.5219},{19.9914,-13.5219}}, 
color={0,0,255}));
  connect(C2.n, ground.p) 
  annotation(Line(origin={-23.7748,-36.80351}, 
points={{-18.5735,-4.11385},{-18.5735,-10.3583},{66.0019,-10.3583}}, 
color={0,0,255}));
  connect(C1.n, ground.p) 
  annotation(Line(origin={-29.7748,-37.80351}, 
points={{-30.1581,0.135649},{-30.1581,-9.3583},{72.0019,-9.3583}}, 
color={0,0,255}));
  connect(R2.p, timer.DISCH) 
  annotation(Line(origin={-3.7748,30.19649}, 
points={{14.8938,28.6471},{18.663,28.6471},{18.663,-28.1992}}, 
color={0,0,255}));
  connect(R1.n, dCVoltageSource.p) 
  annotation(Line(origin={42.2252,-11.80351}, 
points={{0.40297,29.5158},{0.40297,-6.03874},{0.320307,-6.03874}}, 
color={0,0,255}));
  connect(R1.p, R2.p) 
  annotation(Line(origin={25.2252,73.1965}, 
points={{17.3352,-35.253},{17.3352,-14.3529},{-14.1062,-14.3529}}, 
color={0,0,255}));
  connect(timer.RESET, dCVoltageSource.p) 
  annotation(Line(origin={21.2252,-16.80351}, 
points={{-6.33696,-0.521925},{21.3203,-0.521925},{21.3203,-1.03874}}, 
color={0,0,255}));
  connect(timer.OUT, voltageSensor.p) 
  annotation(Line(origin={36.2252,-6.80352}, 
points={{-21.337,-0.860532},{21.7748,-0.860532},{21.7748,-1.19648}}, 
color={0,0,255}));
  connect(voltageSensor.n, ground.p) 
  annotation(Line(origin={65.2252,-27.80351}, 
points={{12.7748,19.80351},{22.9087,19.80351},{22.9087,-19.3583},{-22.9981,-19.3583}}, 
color={0,0,255}));
  connect(C1.p, timer.TRIG) 
  annotation(Line(origin={-43.546,-9.88101}, 
points={{-16.4394,-10.9801},{-16.4394,11.8783},{16.7626,11.8783}}, 
color={0,0,255}));
  connect(diode.p, R2.n) 
  annotation(Line(origin={-38.546,56.11899}, 
points={{-30.113,-3.89694},{-30.113,2.79237},{29.4338,2.79237}}, 
color={0,0,255}));
  connect(diode1.n, R2.n) 
  annotation(Line(origin={-9.546,53.11899}, 
points={{0.48173,-1.0607},{0.48173,5.79237},{0.433797,5.79237}}, 
color={0,0,255}));
  connect(const.y, P1.u) 
  annotation(Line(origin={14.5799,12.868}, 
points={{-93.5799,1.132},{-74.9983,1.132},{-74.9983,1.13202}}, 
color={0,0,127}));
  connect(diode.n, P1.p) 
  annotation(Line(origin={-64,26}, 
  points={{-4.59123,5.99089},{-4.59123,-6.02831},{5.37899,-6.02831}}, 
  color={0,0,255}));
  connect(P1.n, diode1.p) 
  annotation(Line(origin={-24,26}, 
  points={{-14.5376,-6.02831},{15.0035,-6.02831},{15.0035,5.82713}}, 
  color={0,0,255}));
  connect(P1.w, timer.TRIG) 
  annotation(Line(origin={-38,6}, 
  points={{-10.531,4.03559},{-10.531,-4.00267},{11.2166,-4.00267}}, 
  color={0,0,255}));
  connect(timer.THRES, P1.w) 
  annotation(Line(origin={-38,1}, 
  points={{11.2166,-8.66405},{-10.531,-8.66405},{-10.531,9.03559}}, 
  color={0,0,255}));
  end PWMTimer;