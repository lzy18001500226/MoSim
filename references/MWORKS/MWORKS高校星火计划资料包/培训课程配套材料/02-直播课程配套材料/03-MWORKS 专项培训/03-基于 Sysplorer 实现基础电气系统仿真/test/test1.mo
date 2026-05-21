model test1
  annotation(__MWORKS(version="2025a"),Diagram(coordinateSystem(extent={{-100,-100},{100,100}}, 
grid={2,2})));
  Modelica.Electrical.Analog.Basic.Ground ground 
    annotation (Placement(transformation(origin={-120.984,-30.0548}, 
extent={{10,-10},{-10,10}}, 
rotation=-90)));
  Modelica.Electrical.Analog.Basic.Resistor R1(R=100) 
    annotation (Placement(transformation(origin={-79.7808,34.9041}, 
extent={{-10,-10},{10,10}})));
  Modelica.Electrical.Analog.Basic.Resistor resistor1(R=200) 
    annotation (Placement(transformation(origin={-5.4024,34.9041}, 
extent={{10,-10},{-10,10}})));
  Modelica.Electrical.Analog.Sources.ConstantVoltage constantVoltage(V=15) 
    annotation (Placement(transformation(origin={-84.052,-1.34568}, 
extent={{-10,10},{10,-10}}, 
rotation=-90)));
  Modelica.Electrical.Analog.Sources.ConstantVoltage constantVoltage1(V=-15) 
    annotation (Placement(transformation(origin={-84.052,-56.7703}, 
extent={{-10,-10},{10,10}}, 
rotation=90)));
  Modelica.Electrical.Analog.Sources.SineVoltage trapezoidVoltage(f=10) 
    annotation (Placement(transformation(origin={-147.288,-28.7671}, 
extent={{-10,10},{10,-10}}, 
rotation=-90)));
  Modelica.Electrical.Analog.Ideal.IdealOpAmpLimited opAmp 
    annotation (Placement(transformation(origin={-27.2553,-36.0548}, 
extent={{-10,-10},{10,10}})));
  Modelica.Electrical.Analog.Sensors.VoltageSensor voltageSensor 
    annotation (Placement(transformation(origin={25.4841,-56.7703}, 
extent={{-10,10},{10,-10}}, 
rotation=-90)));
  Modelica.Electrical.Analog.Basic.Ground ground1 
    annotation (Placement(transformation(origin={-48.6018,-116.268}, 
extent={{10,-10},{-10,10}})));
equation
  connect(R1.p, trapezoidVoltage.p) 
  annotation(Line(origin={-99,8}, 
points={{9.2192,26.9041},{-48.288,26.9041},{-48.288,-26.7671}}, 
color={0,0,255}));
  connect(R1.n, opAmp.in_n) 
  annotation(Line(origin={-54,2}, 
  points={{-15.7808,32.9041},{6.0678,32.9041},{6.0678,-32.0548},{16.7447,-32.0548}}, 
  color={0,0,255}));
  connect(ground.p, constantVoltage.n) 
  annotation(Line(origin={-98,-21}, 
  points={{-12.9845,-9.05479},{13.948,-9.05479},{13.948,9.65432}}, 
  color={0,0,255}));
  connect(constantVoltage.p, opAmp.VMax) 
  annotation(Line(origin={-56,-5}, 
  points={{-28.052,13.6543},{-28.052,20.8983},{28.7447,20.8983},{28.7447,-21.0548}}, 
  color={0,0,255}));
  connect(constantVoltage1.n, ground.p) 
  annotation(Line(origin={-98,-38}, 
  points={{13.948,-8.77035},{13.948,7.94521},{-12.9845,7.94521}}, 
  color={0,0,255}));
  connect(constantVoltage1.p, opAmp.VMin) 
  annotation(Line(origin={-56,-62}, 
  points={{-28.052,-4.77035},{-28.052,-16.7797},{28.7447,-16.7797},{28.7447,15.9452}}, 
  color={0,0,255}));
  connect(opAmp.in_p, ground1.p) 
  annotation(Line(origin={-43,-74}, 
points={{5.74466,31.9452},{-5.60182,31.9452},{-5.60182,-32.2679}}, 
color={0,0,255}));
  connect(opAmp.out, voltageSensor.p) 
  annotation(Line(origin={5,-41}, 
points={{-22.2553,4.94521},{20.4841,4.94521},{20.4841,-5.77035}}, 
color={0,0,255}));
  connect(voltageSensor.n, ground1.p) 
  annotation(Line(origin={-12,-87}, 
points={{37.4841,20.2297},{37.4841,8.22034},{-36.6018,8.22034},{-36.6018,-19.2679}}, 
color={0,0,255}));
  connect(resistor1.p, voltageSensor.p) 
  annotation(Line(origin={18,-6}, 
points={{-13.4024,40.9041},{2.16949,40.9041},{2.16949,-30.0924},{7.48408,-30.0924},{7.48408,-40.7703}}, 
color={0,0,255}));
  connect(resistor1.n, opAmp.in_n) 
  annotation(Line(origin={-32,2}, 
  points={{16.5976,32.9041},{-15.9322,32.9041},{-15.9322,-32.0548},{-5.25534,-32.0548}}, 
  color={0,0,255}));
  connect(trapezoidVoltage.n, ground1.p) 
  annotation(Line(origin={-98,-73}, 
points={{-49.288,34.2329},{-49.288,-5.77966},{49.3982,-5.77966},{49.3982,-33.2679}}, 
color={0,0,255}));

end test1;