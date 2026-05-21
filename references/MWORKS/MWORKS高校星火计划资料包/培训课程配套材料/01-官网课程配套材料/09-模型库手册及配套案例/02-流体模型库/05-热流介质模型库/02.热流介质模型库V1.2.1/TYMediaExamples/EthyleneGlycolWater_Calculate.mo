model EthyleneGlycolWater_Calculate "乙二醇水溶液介质调用与物性计算示例"
  /* 介质 */
  //给定溶液浓度与特性温度
  package Medium = TYMedia.Incompressible.EthyleneGlycolWater(X_a = 0.60, property_T = 293.15) annotation(Protection(access=Access.nonPackageDuplicate));

  /* 参数 */
  //根据温度、压力计算介质物性
  parameter Modelica.Units.SI.Temperature T(displayUnit = "degC") = 293.15 "温度";
  parameter Modelica.Units.SI.Pressure p = 100000 "压力";

  /* 变量 */
  Medium.ThermodynamicState state_pT "热力状态(pT)";
  Medium.ThermodynamicState state_ph "热力状态(ph)";
  Medium.ThermodynamicState state_ps "热力状态(ps)";
  Modelica.Units.SI.Temperature T1 "温度";
  Modelica.Units.SI.Pressure p1 "压力";
  Modelica.Units.SI.SpecificEnthalpy h "比焓";
  Modelica.Units.SI.SpecificEntropy s "比熵";
  Modelica.Units.SI.SpecificInternalEnergy u "比内能";
  Modelica.Units.SI.Density rho "密度";
  Modelica.Units.SI.DynamicViscosity mu "动力粘度";
  Modelica.Units.SI.ThermalConductivity lambda "导热系数";
  Modelica.Units.SI.SpecificHeatCapacity cp "定压比热";
  Modelica.Units.SI.SpecificHeatCapacity cv "定容比热";
  Modelica.Units.SI.VelocityOfSound a "声速";
  Modelica.Units.SI.MolarMass MM "摩尔质量";
equation
  //热力状态
  state_pT = Medium.setState_pTX(p, T);
  state_ph = Medium.setState_phX(p, h);
  state_ps = Medium.setState_psX(p, s);
  //温度
  T1 = Medium.temperature(state_ph);
  //压力
  p1=Medium.pressure(state_pT);
  //比焓
  h = Medium.specificEnthalpy(state_pT);
  //比熵
  s = Medium.specificEntropy(state_pT);
  //比内能
  u = Medium.specificInternalEnergy(state_pT);
  //密度
  rho = Medium.density(state_pT);
  //动力粘度
  mu = Medium.dynamicViscosity(state_pT);
  //导热系数
  lambda = Medium.thermalConductivity(state_pT);
  //比热
  cp = Medium.specificHeatCapacityCp(state_pT);
  cv = Medium.specificHeatCapacityCv(state_pT);
  //声速
  a = Medium.velocityOfSound(state_pT);
  //摩尔质量
  MM = Medium.molarMass(state_pT);
  annotation(Icon(coordinateSystem(extent = {{-100, -100}, {100, 100}}, 
    grid = {2, 2}), graphics = {Polygon(origin = {2, 21}, 
    lineColor = {0, 94, 138}, 
    fillColor = {0, 94, 138}, 
    fillPattern = FillPattern.Solid, 
    points = {{-64, 1}, {0, 37}, {64, 1}, {0, -37}}), Line(origin = {2, -24}, 
    points = {{-62, 18}, {0, -18}, {62, 18}}, 
    color = {0, 94, 138}, 
    thickness = 5), Line(origin = {2, -52}, 
    points = {{-62, 18}, {0, -18}, {62, 18}}, 
    color = {0, 94, 138}, 
    thickness = 5)}), experiment(Algorithm = Dassl, NumberOfIntervals = 50, StartTime = 0, StopTime = 1, Tolerance = 0.0001, InlineIntegrator = false, InlineStepSize = false),Protection(access=Access.nonPackageDuplicate));
end EthyleneGlycolWater_Calculate;