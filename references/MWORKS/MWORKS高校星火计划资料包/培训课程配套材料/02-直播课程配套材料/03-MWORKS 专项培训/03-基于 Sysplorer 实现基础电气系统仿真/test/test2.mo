model test2
  import Modelica.Electrical.Digital;
  import L = Modelica.Electrical.Digital.Interfaces.Logic;
  annotation(__MWORKS(version="2025a"),Diagram(coordinateSystem(extent={{-100,-100},{100,100}}, 
grid={2,2})));
  Modelica.Electrical.Digital.Examples.Utilities.FullAdder fullAdder 
    annotation (Placement(transformation(origin={-64.1667,-35.7778}, 
extent={{-10,-10},{10,10}})));
  Modelica.Electrical.Digital.Examples.Utilities.FullAdder fullAdder1 
    annotation (Placement(transformation(origin={-5.9033,-35.7778}, 
extent={{-10,-10},{10,10}})));
  Modelica.Electrical.Digital.Examples.Utilities.FullAdder fullAdder2 
    annotation (Placement(transformation(origin={50.0968,-35.7778}, 
extent={{-10,-10},{10,10}})));
  Modelica.Electrical.Digital.Examples.Utilities.FullAdder fullAdder3 
    annotation (Placement(transformation(origin={106.096,-35.7778}, 
extent={{-10,-10},{10,10}})));
  Modelica.Electrical.Digital.Sources.Table table1(t={4},y0=Modelica.Electrical.Digital.Interfaces.Logic.'0') 
    annotation (Placement(transformation(origin={-48.8459,39.4714}, 
extent={{-10,-10},{10,10}})));
  Modelica.Electrical.Digital.Sources.Table table2(y0=Modelica.Electrical.Digital.Interfaces.Logic.'0') 
    annotation (Placement(transformation(origin={10.4238,39.4714}, 
extent={{-10,-10},{10,10}})));
  Modelica.Electrical.Digital.Sources.Table table3(x={L.'1', L.'0'},t={1, 3},y0=Modelica.Electrical.Digital.Interfaces.Logic.'0') 
    annotation (Placement(transformation(origin={62.6268,39.4714}, 
extent={{-10,-10},{10,10}})));
  Modelica.Electrical.Digital.Sources.Set set(x=Modelica.Electrical.Digital.Interfaces.Logic.'0') 
    annotation (Placement(transformation(origin={-133.51,-42.7778}, 
extent={{-10,-10},{10,10}})));
  Modelica.Electrical.Digital.Sources.Table table4(x={L.'1', L.'0', L.'1'},t={1, 2, 3},y0=Modelica.Electrical.Digital.Interfaces.Logic.'0') 
    annotation (Placement(transformation(origin={-117.427,71.8167}, 
extent={{-10,-10},{10,10}})));
  Modelica.Electrical.Digital.Sources.Table table5(y0=Modelica.Electrical.Digital.Interfaces.Logic.'0') 
    annotation (Placement(transformation(origin={-48.8463,88.8106}, 
extent={{-10,-10},{10,10}})));
  Modelica.Electrical.Digital.Sources.Table table6(x={L.'1', L.'0'},t={1, 4},y0=Modelica.Electrical.Digital.Interfaces.Logic.'0') 
    annotation (Placement(transformation(origin={10.4234,88.8106}, 
extent={{-10,-10},{10,10}})));
  Modelica.Electrical.Digital.Sources.Table table7(x={L.'0'},y0=Modelica.Electrical.Digital.Interfaces.Logic.'0') 
    annotation (Placement(transformation(origin={62.6264,88.8106}, 
extent={{-10,-10},{10,10}})));
  Modelica.Electrical.Digital.Sources.Table table8(x={L.'1', L.'0', L.'1'},t={1, 2, 3},y0=Modelica.Electrical.Digital.Interfaces.Logic.'0') 
    annotation (Placement(transformation(origin={-117.427,32.5003}, 
extent={{-10,-10},{10,10}})));
  equation
  connect(fullAdder.c_out, fullAdder1.c_in) 
  annotation(Line(origin={-44.8859,-65.7139}, 
points={{-9.28076,22.9361},{28.9826,22.9361}}, 
color={127,0,127}));
  connect(fullAdder1.c_out, fullAdder2.c_in) 
  annotation(Line(origin={22.2634,-43}, 
points={{-18.16668,0.2222},{17.8334,0.2222}}, 
color={127,0,127}));
  connect(fullAdder2.c_out, fullAdder3.c_in) 
  annotation(Line(origin={78.2634,-43}, 
points={{-18.1666,0.2222},{17.833,0.2222}}, 
color={127,0,127}));
  connect(fullAdder.c_in, set.y) 
  annotation(Line(origin={-99,-43}, 
  points={{24.8333,0.2222},{-24.5097,0.2222}}, 
  color={127,0,127}));
  connect(table4.y, fullAdder.a) 
  annotation(Line(origin={-91,22}, 
  points={{-16.4274,49.8167},{-0.56582,49.8167},{-0.56582,-50.7778},{16.8333,-50.7778}}, 
  color={127,0,127}));
  connect(table8.y, fullAdder.b) 
  annotation(Line(origin={-91,0}, 
  points={{-16.427,32.5003},{-6.77367,32.5003},{-6.77367,-32.7778},{16.8333,-32.7778}}, 
  color={127,0,127}));
  connect(table5.y, fullAdder1.a) 
  annotation(Line(origin={-27,30}, 
  points={{-11.8463,58.8106},{4.7552,58.8106},{4.7552,-58.7778},{11.0967,-58.7778}}, 
  color={127,0,127}));
  connect(table1.y, fullAdder1.b) 
  annotation(Line(origin={-27,3}, 
  points={{-11.8459,36.4714},{-7.66051,36.4714},{-7.66051,-35.7778},{11.0967,-35.7778}}, 
  color={127,0,127}));
  connect(table6.y, fullAdder2.a) 
  annotation(Line(origin={30,30}, 
  points={{-9.57658,58.8106},{5.33372,58.8106},{5.33372,-58.7778},{10.0968,-58.7778}}, 
  color={127,0,127}));
  connect(table2.y, fullAdder2.b) 
  annotation(Line(origin={30,3}, 
  points={{-9.5762,36.4714},{-4.55972,36.4714},{-4.55972,-35.7778},{10.0968,-35.7778}}, 
  color={127,0,127}));
  connect(table7.y, fullAdder3.a) 
  annotation(Line(origin={84,30}, 
  points={{-11.3736,58.8106},{2.56762,58.8106},{2.56762,-58.7778},{12.096,-58.7778}}, 
  color={127,0,127}));
  connect(table3.y, fullAdder3.b) 
  annotation(Line(origin={84,3}, 
  points={{-11.3732,36.4714},{-7.67916,36.4714},{-7.67916,-35.7778},{12.096,-35.7778}}, 
  color={127,0,127}));
  end test2;