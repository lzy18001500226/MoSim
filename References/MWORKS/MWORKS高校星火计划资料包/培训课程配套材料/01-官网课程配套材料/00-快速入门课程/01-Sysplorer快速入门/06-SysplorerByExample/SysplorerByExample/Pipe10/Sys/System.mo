model System "全局变量"
  annotation(__MWORKS(version = "2025b"),Icon(coordinateSystem(extent={{-100,-100},{100,100}},
grid={2,2}),graphics = {Rectangle(origin={-1,1},
fillColor={255,255,255},
fillPattern=FillPattern.Solid,
extent={{-97,85},{97,-85}}), Text(origin={10,2},
lineColor={0,0,0},
extent={{-20,12},{20,-12}},
textString="g",
fontSize=14,
textStyle={TextStyle.None},
textColor={0,0,0},
horizontalAlignment=TextAlignment.Left), Ellipse(origin={-49,10},
fillColor={255,255,0},
fillPattern=FillPattern.Solid,
extent={{-15,15},{15,-15}}), Line(origin={23,7},
points={{-1,27},{1,-27}}), Line(origin={19,-16},
points={{-5,4},{5,-4}}), Line(origin={31,-14},
points={{-7,-6},{7,6}})}));
  parameter Modelica.SIunits.Pressure p0 = 1.01e5 "环境压力";
  parameter Modelica.SIunits.Temperature T0 = 293.15 "环境温度";
  parameter Modelica.SIunits.Acceleration g = Modelica.Constants.g_n "重力加速度";
  parameter Modelica.SIunits.Density rho = 1000 "液体密度";
  parameter Modelica.SIunits.DynamicViscosity mu = 0.001 "动力粘度";
  parameter Modelica.SIunits.SpecificHeatCapacityAtConstantPressure cp = 4181 "定压比热容";
  parameter Modelica.SIunits.ThermalConductivity lambda = 0.598 "导热系数";

annotation(defaultComponentName="system",defaultComponentPrefixes="inner");

end System;