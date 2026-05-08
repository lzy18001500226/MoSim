package Connector_Energy "非因果连接器"
  annotation(__MWORKS(version="2025b"));
  connector PositivePin
  //能量流连接器中包含的两种变量分别是 (流变量) 和 (势变量),流入为正流出为负
    Modelica.SIunits.Voltage v;
    flow  Modelica.SIunits.Current i;
    annotation(Icon(coordinateSystem(extent={{-100,-100},{100,100}},
  grid={2,2}),graphics = {Rectangle(origin={0,0},
  fillColor={0,0,255},
  fillPattern=FillPattern.Solid,
  extent={{-100,100},{100,-100}})}));
  end PositivePin;
  connector NegativePin

    Modelica.SIunits.Voltage v;
    flow  Modelica.SIunits.Current i;
    annotation(Icon(coordinateSystem(extent={{-100,-100},{100,100}},
  grid={2,2}),graphics = {Rectangle(origin={0,0},
  lineColor={0,0,255},
  fillColor={255,255,255},
  extent={{-100,100},{100,-100}})}));
  end NegativePin;
  model TestCon "连接器示例-电阻"
    parameter Modelica.SIunits.Resistance R = 10;
    Modelica.SIunits.Voltage v;
    Modelica.SIunits.Current i;

    annotation(__MWORKS(version="2025b"));
    .SysplorerByExample.Easy.Connet.Connector_Energy.PositivePin positivePin 
      annotation (Placement(transformation(origin={-110,10},
  extent={{-10,-10},{10,10}})));
    .SysplorerByExample.Easy.Connet.Connector_Energy.NegativePin negativePin 
      annotation (Placement(transformation(origin={32,10},
  extent={{-10,-10},{10,10}})));
  equation
    v = positivePin.v - negativePin.v;
    i = positivePin.i;
    positivePin.i + negativePin.i = 0;
    v = R * i;

  end TestCon;

end Connector_Energy;