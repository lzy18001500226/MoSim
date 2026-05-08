package Repeat "模型重用"
  annotation(__MWORKS(version="2025b"));
  partial model PartialPort
  import SI=Modelica.SIunits;
  SI.Voltage v;
  SI.Current i;
    Connet.Connector_Energy.PositivePin p 
      annotation (Placement(transformation(origin={-180,0},
  extent={{-10,-10},{10,10}})));
    Connet.Connector_Energy.NegativePin n 
      annotation (Placement(transformation(origin={-70,0},
  extent={{-10,-10},{10,10}})));

  equation
  v = p.v - n.v;
  0 = p.i + n.i;
  i = p.i;
  end PartialPort;
  model Resistor
  import SI=Modelica.SIunits;
  parameter SI.Resistance R = 1;
  extends PartialPort;//继承一个模型需要用到的关键词是（extends）
  equation
  R*i=v;//方程等价I=V/R；等价v=R*i
  end Resistor;
  model Inductor
  import SI=Modelica.SIunits;
  parameter SI.Inductance L = 1;
  extends PartialPort;
  equation
  L* der(i) = v;
  end Inductor;
  end Repeat;