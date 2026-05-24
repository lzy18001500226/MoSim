model Incompressible_Calculate "不可压流体介质调用与物性计算示例"
  import SI = Modelica.SIunits;
  /* 介质 */
  replaceable package Medium = TYMedia.Incompressible.LBE 
    constrainedby TYMedia.Incompressible.PartialIncompressible 
    annotation(choicesAllMatching = true,Protection(access=Access.nonPackageDuplicate));

  /* 参数 */
  //根据温度、压力计算介质物性
  parameter SI.Temperature T = 298.15 "温度";
  parameter SI.Pressure p = 100000 "压力";

  /* 变量 */
  Medium.ThermodynamicState state_pT "热力状态(pT)";
  Medium.ThermodynamicState state_ph "热力状态(ph)";
  SI.Temperature T_ph "温度";
  SI.Temperature T1 "温度";
  SI.SpecificEnthalpy h_pT "比焓";
  SI.SpecificEnthalpy h "比焓";
  SI.SpecificInternalEnergy u "比内能";
  SI.Density rho "密度";
  SI.DynamicViscosity mu "动力粘度";
  SI.ThermalConductivity lambda "导热系数";
  SI.SpecificHeatCapacity cp "定压比热";
  SI.VelocityOfSound a "声速";
  SI.Pressure ps "饱和压力";
  SI.SurfaceTension sigma "表面张力";
  SI.Temperature T_melt "融化温度";
  SI.SpecificEnthalpy h_melt "融化比焓";
  SI.Temperature T_boil "沸腾温度";
  SI.SpecificEnthalpy h_boil "沸腾比焓";
  Real beta "热膨胀系数";
  Real kappa "压缩系数";
  Real dhdT_p "比焓对温度的偏导数";
  Real dudp_h "比内能对压力的偏导数";
  Real dudh_p "比内能对比焓的偏导数";
  Real dudT_p "比内能对温度的偏导数";
  Real dudp_T "比内能对压力的偏导数";
  Real dddp_T "密度对压力的偏导数";
  Real dddp_h "密度对压力的偏导数";
  Real dddh_p "密度对比焓的偏导数";
  Real dddT_p "密度对温度的偏导数";

equation
  state_pT = Medium.setState_pTX(p, T);
  state_ph = Medium.setState_phX(p, h_pT);
  //温度
  T_ph = Medium.temperature_phX(p, h_pT);
  T1 = Medium.temperature(state_ph);
  //比焓
  h_pT = Medium.specificEnthalpy_pTX(p, T);
  h = Medium.specificEnthalpy(state_pT);
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
  //声速
  a = Medium.velocityOfSound(state_pT);
  //饱和物性
  ps = Medium.saturationPressure(state_pT);
  //表面张力
  sigma = Medium.surfaceTension(state_pT);
  //其余物性
  T_melt = Medium.T_melt();
  h_melt = Medium.h_melt();
  T_boil = Medium.T_boil();
  h_boil = Medium.h_boil();
  kappa = Medium.kappa(state_pT);
  beta = Medium.beta(state_pT);
  //偏导数
  dhdT_p = Medium.specificEnthalpy_derT_p(state_pT);
  dudp_h = Medium.specificInternalEnergy_derp_h(state_pT);
  dudh_p = Medium.specificInternalEnergy_derh_p(state_pT);
  dudT_p = Medium.specificInternalEnergy_derT_p(state_pT);
  dudp_T = Medium.specificInternalEnergy_derp_T(state_pT);
  dddp_T = Medium.density_derp_T(state_pT);
  dddp_h = Medium.density_derp_h(state_pT);
  dddh_p = Medium.density_derh_p(state_pT);
  dddT_p = Medium.density_derT_p(state_pT);

  annotation(Icon(coordinateSystem(extent = {{-100, -100}, {100, 100}}, 
    grid = {2, 2}), graphics = {Polygon(origin = {1.7763568394002505e-15, 27}, 
    lineColor = {0, 94, 138}, 
    fillColor = {0, 94, 138}, 
    fillPattern = FillPattern.Solid, 
    points = {{-64, 1}, {0, 37}, {64, 1}, {0, -37}}), Line(origin = {8.881784197001252e-15, -18}, 
    points = {{-62, 18}, {0, -18}, {62, 18}}, 
    color = {0, 94, 138}, 
    thickness = 5), Line(origin = {1.5987211554602254e-14, -46}, 
    points = {{-62, 18}, {0, -18}, {62, 18}}, 
    color = {0, 94, 138}, 
    thickness = 5)}), 
    experiment(Algorithm = Dassl, Interval = 0.02, StartTime = 0, StopTime = 1, Tolerance = 0.0001), __MWORKS(ContinueSimConfig(SaveContinueFile = "false", SaveBeforeStop = "false", NumberBeforeStop = 1, FixedContinueInterval = "false", ContinueIntervalLength = 0.02, ContinueTimeVector)),Protection(access=Access.nonPackageDuplicate));
end Incompressible_Calculate;