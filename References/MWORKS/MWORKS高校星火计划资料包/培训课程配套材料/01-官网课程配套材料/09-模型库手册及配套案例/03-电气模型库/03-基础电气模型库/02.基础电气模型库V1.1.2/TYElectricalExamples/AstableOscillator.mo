model AstableOscillator "双稳态振荡器"
  annotation(Diagram(coordinateSystem(extent={{-100,-100},{100,100}}, 
grid={2,2})),experiment(Algorithm=Dassl,Interval=1e-06,StartTime=0,StopTime=0.015,Tolerance=1e-09),Icon(coordinateSystem(extent={{-100,-100},{100,100}}, 
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
__MWORKS(ContinueSimConfig(SaveContinueFile="false",SaveBeforeStop="false",NumberBeforeStop=1,FixedContinueInterval="false",ContinueIntervalLength=0.015,ContinueTimeVector),ResultViewerManager(resultViewers={
ResultViewer(name="1", executeTrigger=executeTrigger.SimulationFinished, commands={
CreatePlot(id=1, position=[0, 28, 2029, 790], y=["V1.v", "V2.v"], x_display_unit="s", y_display_units=["V", "V"], y_axis=[1, 1], legend_layout=7, legend_frame=True, left_title="[V]", fix_time_range_value=6.95225e-310)})
})), 
Documentation(link = "modelica://TYElectrical/Resources/Example/AstableOscillator.html"));
  TYElectrical.BasicComponents.IdealBasicComponents.Resistor R2(R = 4.7e3) 
    annotation (Placement(transformation(origin={-82.03671970624235,33.93390452876377}, 
extent={{-10,-10},{10,10}}, 
rotation=270)));
  TYElectrical.BasicComponents.IdealBasicComponents.Resistor R1(R = 200e3) 
    annotation (Placement(transformation(origin={-45.66733268257066,-10.343849981257362}, 
extent={{-10,-10},{10,10}}, 
rotation=270)));
  TYElectrical.BasicComponents.IdealBasicComponents.Resistor R3(R = 210e3) 
    annotation (Placement(transformation(origin={44,-10.3438}, 
extent={{-10,-10},{10,10}}, 
rotation=270)));
  TYElectrical.BasicComponents.IdealBasicComponents.Resistor R4(R = 4.7e3) 
    annotation (Placement(transformation(origin={84.64626682986537,30.903304773561814}, 
extent={{-10,-10},{10,10}}, 
rotation=270)));
  TYElectrical.BasicComponents.IdealBasicComponents.Capacitor C1(C(displayUnit="F") = 0.01e-6,R=1e-6) 
    annotation (Placement(transformation(origin={-28.10565210765442,-40.51191108772558}, 
extent={{10,-10},{-10,10}}, 
rotation=-360)));
  TYElectrical.Sources.VoltageSources.PositiveSupplyRail positiveSupplyRail(v_constant=10) 
    annotation (Placement(transformation(origin={1.6450423867809054,75.1236228629131}, 
extent={{-10,-10},{10,10}})));
  TYElectrical.BasicComponents.IdealBasicComponents.Capacitor C2(C = 0.01e-6,R=1e-6) 
    annotation (Placement(transformation(origin={28,-40.5119}, 
extent={{-10,-10},{10,10}}, 
rotation=360)));
  TYElectrical.Semiconductors.NPNBipolarTransistor Transistor2(Rc=0.1,Re=0.1,Rb=0.1,Initial_eqution=2) 
    annotation (Placement(transformation(origin={66,-40.6646}, 
extent={{-10,-10},{10,10}})));
  TYElectrical.BasicComponents.IdealBasicComponents.ElectricalReference electricalReference 
    annotation (Placement(transformation(origin={-3.640632962278165,-80.6816455323664}, 
extent={{-10,-10},{10,10}})));
  TYElectrical.Semiconductors.NPNBipolarTransistor Transistor1(Rc=0.1,Re=0.1,Rb=0.1,Initial_eqution=2) 
    annotation (Placement(transformation(origin={-64.27690477419117,-40.664554271269125}, 
extent={{10,-10},{-10,10}})));
  TYElectrical.BasicComponents.IdealSensors.VoltageSensor V1 
    annotation (Placement(transformation(origin={-114,20}, 
extent={{10,-10},{-10,10}})));
  TYElectrical.BasicComponents.IdealBasicComponents.ElectricalReference electricalReference1 
    annotation (Placement(transformation(origin={-130,-10.3438}, 
extent={{-10,-10},{10,10}})));
  TYElectrical.BasicComponents.IdealSensors.VoltageSensor V2 
    annotation (Placement(transformation(origin={110,20}, 
extent={{-10,-10},{10,10}})));
  TYElectrical.BasicComponents.IdealBasicComponents.ElectricalReference electricalReference2 
    annotation (Placement(transformation(origin={133.667,-10.3438}, 
extent={{10,-10},{-10,10}})));
  equation
  connect(R2.n, R1.p) 
  annotation(Line(origin={-70,12}, 
points={{-12.023150127535203,11.805101226114985},{-12.023150127535203,4.450428396572828},{24.278460799313493,4.450428396572828},{24.278460799313493,-12.241488382241998}}, 
color={0,0,255}));
  connect(positiveSupplyRail.pin_p, R2.p) 
  annotation(Line(origin={-40,62}, 
points={{41.64504238678091,4.923622862913092},{41.64504238678091,-2.7784577723378163},{-42.0909262243582,-2.7784577723378163},{-42.0909262243582,-17.96373387222087}}, 
color={0,0,255}));




  connect(positiveSupplyRail.pin_p, R4.p) 
  annotation(Line(origin={43,54}, 
points={{-41.35495761321909,12.923622862913092},{-41.35495761321909,5.769889840881277},{41.59206031174952,5.769889840881277},{41.59206031174952,-12.994333627422819}}, 
color={0,0,255}));
  connect(C2.n, Transistor2.B) 
  annotation(Line(origin={37,-41}, 
points={{1.1288,0.501658},{19,0.501658},{19,0.321463}}, 
color={0,0,255}));
  connect(R4.n, Transistor2.C) 
  annotation(Line(origin={76,-7}, 
points={{8.65984,27.7745},{8.65984,-27.708},{0.0114856,-27.708}}, 
color={0,0,255}));
  connect(Transistor2.E, electricalReference.p) 
  annotation(Line(origin={57,-59}, 
points={{19.0115,12.295},{27.8188,12.295},{27.8188,-5.04664},{-60.6406,-5.04664},{-60.6406,-11.6816}}, 
color={0,0,255}));
  connect(Transistor1.E, electricalReference.p) 
  annotation(Line(origin={-30,-58}, 
points={{-44.28839041713749,11.29499629052863},{-55.333466993442684,11.29499629052863},{-55.333466993442684,-6.0466394124153595},{26.359367037721835,-6.0466394124153595},{26.359367037721835,-12.681645532366403}}, 
color={0,0,255}));
  connect(Transistor1.C, R2.n) 
  annotation(Line(origin={-78,-5}, 
  points={{3.7116095828625078,-29.707999964153018},{-4.023150127535203,-29.707999964153018},{-4.023150127535203,28.805101226114985}}, 
  color={0,0,255}));
  connect(R4.n, R3.p) 
  annotation(Line(origin={60,10}, 
points={{24.6598,10.7745},{24.6598,5.95198},{-16.0542,5.95198},{-16.0542,-10.2415}}, 
color={0,0,255}));
  connect(Transistor1.B, C1.n) 
  annotation(Line(origin={-46,-41}, 
points={{-8.276904774191166,0.3214632068831875},{7.765544589696788,0.3214632068831875},{7.765544589696788,0.5016584909815691}}, 
color={0,0,255}));
  connect(C2.p, R1.p) 
  annotation(Line(origin={-36,-9}, 
points={{53.8976,-31.5661},{53.8976,25.5669},{-9.72154,25.5669},{-9.72154,8.75851}}, 
color={0,0,255}));
  connect(C1.p, R3.p) 
  annotation(Line(origin={33,-10}, 
points={{-51.0033,-30.5661},{-48.9843,-30.5661},{-48.9843,20},{10.9458,20},{10.9458,9.75851}}, 
color={0,0,255}));
  connect(R3.n, C2.n) 
  annotation(Line(origin={33,-31}, 
points={{11.0136,10.5273},{11.0136,-9.49834},{5.1288,-9.49834}}, 
color={0,0,255}));
  connect(R1.n, Transistor1.B) 
  annotation(Line(origin={-50,-31}, 
  points={{4.346236896136489,10.527346716093852},{4.346236896136489,-9.678536793116812},{-4.276904774191166,-9.678536793116812}}, 
  color={0,0,255}));
  connect(V1.p, R2.n) 
  annotation(Line(origin={-94,22}, 
points={{-10,-2},{11.9768,-2},{11.9768,1.8051}}, 
color={0,0,255}));
  connect(V1.n, electricalReference1.p) 
  annotation(Line(origin={-129,6}, 
points={{5,14},{-1,14},{-1,-6.34385}}, 
color={0,0,255}));
  connect(V2.n, electricalReference2.p) 
  annotation(Line(origin={145,-4}, 
points={{-25,24},{-11.3327,24},{-11.3327,3.6562}}, 
color={0,0,255}));
  connect(V2.p, R4.n) 
  annotation(Line(origin={92,18}, 
points={{8,2},{-7.34016,2},{-7.34016,2.7745}}, 
color={0,0,255}));
  end AstableOscillator;