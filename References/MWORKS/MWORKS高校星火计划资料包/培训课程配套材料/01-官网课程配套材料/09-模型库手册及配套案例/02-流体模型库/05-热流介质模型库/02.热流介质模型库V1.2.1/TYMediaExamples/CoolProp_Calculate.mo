model CoolProp_Calculate "CoolProp介质调用与物性计算示例"
  import SI = Modelica.SIunits;
  /* 介质 */
  replaceable package Medium = TYMedia.CoolProp.Methane_CoolProp 
    constrainedby TYMedia.CoolProp.CoolPropInterface 
    annotation(choicesAllMatching = true,Protection(access=Access.nonPackageDuplicate));

  /* 参数 */
  //根据压力、比焓计算介质物性
  parameter SI.Pressure p = 0.3e6 "压力";
  parameter SI.SpecificEnthalpy h = 3e5 "比焓";

  /* 变量 */
  Medium.ThermodynamicState state_ph "热力状态(ph)";
  Medium.ThermodynamicState state_dT "热力状态(dT)";
  Medium.ThermodynamicState state_ps "热力状态(ps)";
  Medium.ThermodynamicState state_hs "热力状态(hs)";
  Medium.ThermodynamicState state_bubble "饱和液相状态";
  Medium.ThermodynamicState state_Dew "饱和气相状态";
  Medium.SaturationProperties sat_p "饱和状态(p)";
  Medium.SaturationProperties sat_T "饱和状态(T)";
  SI.Temperature T "温度";
  SI.SpecificEnthalpy h1 "比焓";
  SI.SpecificEnthalpy hl "饱和液相比焓";
  SI.SpecificEnthalpy hv "饱和气相比焓";
  SI.SpecificEntropy s "比熵";
  SI.SpecificInternalEnergy u "比内能";
  SI.Density rho "密度";
  SI.Density rhov "饱和气相密度";
  SI.Density rhol "饱和液相密度";
  SI.SpecificHeatCapacity cp "定压比热";
  SI.SpecificHeatCapacity cv "定容比热";
  SI.DynamicViscosity mu "动力粘度";
  SI.ThermalConductivity lambda "导热系数";
  SI.VelocityOfSound a "声速";
  SI.SurfaceTension sigma "表面张力";
  SI.Pressure p_sat "饱和压力";
  SI.Temperature T_sat "饱和温度";
  Real x "干度";
  Real dddp_h "密度关于压力的偏导数";
  Real dddh_p "密度关于比焓的偏导数";
  Real dddp_T "密度关于压力的偏导数";
  Real dddT_p "密度关于温度的偏导数";
  SI.DerDensityByPressure ddldp "饱和液相密度关于压力的偏导数";
  SI.DerDensityByPressure ddvdp "饱和气相密度关于压力的偏导数";
  Real dudh_p "比内能关于比焓的偏导数";
  Real dudp_h "比内能关于压力的偏导数";
  SI.DerEnthalpyByPressure dhldp "饱和液相比焓关于压力的偏导数";
  SI.DerEnthalpyByPressure dhvdp "饱和气相比焓关于压力的偏导数";
equation
  //热力状态
  state_ph = Medium.setState_phX(p, h);
  state_dT = Medium.setState_dTX(rho, T);
  state_ps = Medium.setState_psX(p, s);
  state_hs = Medium.setState_hsX(h, s);
  //饱和状态
  state_bubble = Medium.setBubbleState(sat_p);
  state_Dew = Medium.setDewState(sat_p);
  sat_p = Medium.setSat_p(p);
  sat_T = Medium.setSat_T(T);
  //温度
  T = Medium.temperature(state_ph);
  //比焓
  h1 = Medium.specificEnthalpy(state_ps);
  //饱和比焓
  hl = Medium.bubbleEnthalpy(sat_p);
  hv = Medium.dewEnthalpy(sat_p);
  //比熵
  s = Medium.specificEntropy(state_ph);
  //比内能
  u = Medium.specificInternalEnergy(state_ph);
  //密度
  rho = Medium.density(state_ph);
  //饱和密度
  rhov = Medium.dewDensity(sat_p);
  rhol = Medium.bubbleDensity(sat_p);
  //比热
  cp = Medium.specificHeatCapacityCp(state_ph);
  cv = Medium.specificHeatCapacityCv(state_ph);
  //动力粘度
  mu = Medium.dynamicViscosity(state_ph);
  //导热系数
  lambda = Medium.thermalConductivity(state_ph);
  //声速
  a = Medium.velocityOfSound(state_ph);
  //表面张力
  sigma = Medium.surfaceTension(sat_p);
  //饱和参数
  p_sat = Medium.saturationPressure(T);
  T_sat = Medium.saturationTemperature(p);
  //干度
  x = Medium.vapourQuality(state_ph);
  //偏导数
  dddp_h = Medium.density_derp_h(state_ph);
  dddh_p = Medium.density_derh_p(state_ph);
  dudh_p = Medium.specificInternalEnergy_derh_p(state_ph);
  dudp_h = Medium.specificInternalEnergy_derp_h(state_ph);
  dddp_T = Medium.density_derp_T(state_ph);
  dddT_p = Medium.density_derT_p(state_ph);
  ddldp = Medium.dBubbleDensity_dPressure(sat_p);
  ddvdp = Medium.dDewDensity_dPressure(sat_p);
  dhldp = Medium.dBubbleEnthalpy_dPressure(sat_p);
  dhvdp = Medium.dDewEnthalpy_dPressure(sat_p);

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
    thickness = 5)}), Documentation(info = "<html><p>
<strong>注：</strong>由于CoolProp为调用外部函数，使用时需要使用VS2015/2017编译器。
</p>
</html>"), experiment(Algorithm = Dassl, Interval = 0.02, StartTime = 0, StopTime = 1, Tolerance = 0.0001),Protection(access=Access.nonPackageDuplicate));
end CoolProp_Calculate;