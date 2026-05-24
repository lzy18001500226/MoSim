model System "全局变量"
  parameter Modelica.SIunits.Pressure p0 = 1.0135e5 "环境压力";
  parameter Modelica.SIunits.Temperature T0 = 293.15 "环境温度";
  parameter Modelica.SIunits.Acceleration g = Modelica.Constants.g_n "重力加速度";
  parameter Modelica.SIunits.Density rho = 1000 "液体密度";
  parameter Modelica.SIunits.DynamicViscosity mu = 0.001 "动力粘度";
  parameter Modelica.SIunits.SpecificHeatCapacityAtConstantPressure cp = 4181 "定压比热容";
  parameter Modelica.SIunits.ThermalConductivity lambda = 0.598 "导热系数";
  annotation (defaultComponentName = "system",
    defaultComponentPrefixes = "inner",
    Icon(coordinateSystem(extent = {{-100.0, -100.0}, {100.0, 100.0}},
      grid = {2.0, 2.0}), graphics = {Rectangle(origin = {0.0, 0.0},
      lineColor = {0, 0, 255},
      fillColor = {255, 255, 255},
      fillPattern = FillPattern.Solid,
      extent = {{-100.0, 100.0}, {100.0, -100.0}}), Line(origin = {-2.0, -30.0},
      points = {{-84.0, 0.0}, {84.0, 0.0}}), Line(origin = {-67.0, -49.0},
      points = {{-15.0, -19.0}, {15.0, 19.0}}), Line(origin = {-33.0, -49.0},
      points = {{-15.0, -19.0}, {15.0, 19.0}}), Line(origin = {1.0, -49.0},
      points = {{-15.0, -19.0}, {15.0, 19.0}}), Line(origin = {37.0, -49.0},
      points = {{-15.0, -19.0}, {15.0, 19.0}}), Line(origin = {74.0, 49.0},
      points = {{0.0, 35.0}, {0.0, -35.0}}), Polygon(origin = {74.0, -2.0},
      fillPattern = FillPattern.Solid,
      points = {{-14.0, 16.0}, {14.0, 16.0}, {0.0, -16.0}, {-14.0, 16.0}}), Text(origin = {38.0, 1.0},
      extent = {{-22.0, 19.0}, {22.0, -19.0}},
      textString = "g"), Text(origin = {-8.0, 66.0},
      extent = {{-82.0, 16.0}, {82.0, -16.0}},
      textString = "defaults"), Line(origin = {-40.0, 5.0},
      points = {{-42.0, 9.0}, {-2.0, -25.0}, {42.0, 25.0}},
      thickness = 0.5), Ellipse(origin = {1.0, 29.0},
      fillColor = {255, 0, 0},
      pattern = LinePattern.None,
      fillPattern = FillPattern.Solid,
      extent = {{-11.0, 11.0}, {11.0, -11.0}})}));
end System;