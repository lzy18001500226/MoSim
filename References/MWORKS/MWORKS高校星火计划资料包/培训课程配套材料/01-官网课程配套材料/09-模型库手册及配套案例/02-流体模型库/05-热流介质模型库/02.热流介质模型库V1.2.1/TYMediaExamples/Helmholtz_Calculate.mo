model Helmholtz_Calculate "基于Helmholtz方程介质调用与物性计算示例"
  import SI = Modelica.SIunits;
  /* 介质 */
  replaceable package Medium = TYMedia.Helmholtz.R134a 
    constrainedby TYMedia.Helmholtz.PartialHelmholtz "介质" 
    annotation(choicesAllMatching = true, Protection(access = Access.nonPackageDuplicate));

  /* 参数 */
  //根据温度、压力计算介质物性
  parameter SI.Pressure p = 3e5 "压力";
  parameter SI.SpecificEnthalpy h = 300e3 "比焓";

  /* 变量 */
  Medium.ThermodynamicState state_pT "热力状态(pT)";
  Medium.ThermodynamicState state_ph "热力状态(ph)";
  Medium.ThermodynamicState state_ps "热力状态(ps)";
  Medium.ThermodynamicState state_dT "热力状态(dT)";
  Medium.ThermodynamicState state_l "饱和液相热力状态";
  Medium.ThermodynamicState state_v "饱和气相热力状态";
  Medium.SaturationProperties sat_p "饱和状态(p)";
  Medium.SaturationProperties sat_T "饱和状态(T)";
  SI.Pressure p1 "压力";
  SI.Temperature T "温度";
  SI.Temperature T_ph "温度";
  SI.Temperature T_state "温度";
  SI.SpecificEnthalpy h1 "比焓";
  SI.SpecificEnthalpy hv "饱和气相比焓";
  SI.SpecificEnthalpy hl "饱和液相比焓";
  SI.SpecificInternalEnergy u "比内能";
  SI.SpecificEntropy s "比熵";
  SI.Density d "密度";
  SI.Density dv "饱和气相密度";
  SI.Density dl "饱和液相密度";
  SI.ThermalConductivity lambda "导热系数";
  SI.SpecificHeatCapacity cp "定压比热容";
  SI.SpecificHeatCapacity cv "定容比热容";
  SI.DynamicViscosity mu "动力粘度";
  SI.VelocityOfSound a "声速";
  SI.Pressure p_sat "饱和压力";
  SI.Temperature T_sat "饱和温度";
  SI.SurfaceTension sigma "表面张力";
  Real x "质量含气率";
  SI.MolarMass MM "摩尔质量";
  Real beta "等压膨胀系数";
  Real kappa "等温压缩系数";
  Modelica.Media.Interfaces.Types.DerDensityByEnthalpy ddhp "定压下密度关于比焓的偏导数";
  Modelica.Media.Interfaces.Types.DerDensityByPressure ddph "定比焓下密度关于压力的偏导数";
  Modelica.Media.Interfaces.Types.DerDensityByPressure ddldp "饱和液相密度关于压力的偏导数";
  Modelica.Media.Interfaces.Types.DerDensityByPressure ddvdp "饱和气相密度关于压力的偏导数";
  Modelica.Media.Interfaces.Types.DerEnthalpyByPressure dhldp "饱和液相比焓关于压力的偏导数";
  Modelica.Media.Interfaces.Types.DerEnthalpyByPressure dhvdp "饱和气相比焓关于压力的偏导数";
  SI.PrandtlNumber Pr "普朗特数";
equation
  //热力状态
  state_pT = Medium.setState_pTX(p, T);
  state_ph = Medium.setState_phX(p, h);
  state_ps = Medium.setState_psX(p, s);
  state_dT = Medium.setState_dTX(d, T);
  //饱和状态
  state_l = Medium.setBubbleState(sat_p);
  state_v = Medium.setDewState(sat_p);
  sat_p = Medium.setSat_p(p);
  sat_T = Medium.setSat_T(T);
  //压力
  p1 = Medium.pressure(state_dT);
  //比焓
  h1 = Medium.specificEnthalpy(state_pT);
  //饱和比焓
  hv = Medium.dewEnthalpy(sat_p);
  hl = Medium.bubbleEnthalpy(sat_p);
  //温度(分别给出以热力状态和物性参数为输入的物性计算示例，其余物性计算同理)
  T = Medium.temperature(state_ph);
  T_ph = Medium.temperature_phX(p, h);
  T_state = state_ph.T;
  //比内能
  u = Medium.specificInternalEnergy(state_ph);
  //比熵
  s = Medium.specificEntropy(state_ph);
  //密度
  d = Medium.density(state_ph);
  //饱和密度
  dv = Medium.dewDensity(sat_p);
  dl = Medium.bubbleDensity(sat_p);
  //导热系数
  lambda = Medium.thermalConductivity(state_ph);
  //比热容
  cp = Medium.specificHeatCapacityCp(state_ph);
  cv = Medium.specificHeatCapacityCv(state_ph);
  //动力粘度
  mu = Medium.dynamicViscosity(state_ph);
  //声速
  a = Medium.velocityOfSound(state_ph);
  //饱和温度/压力
  p_sat = Medium.saturationPressure(T);   //或 =sat_T.psat;
  T_sat = Medium.saturationTemperature(p);   //或 =sat_p.Tsat;
  //表面张力
  sigma = Medium.surfaceTension(sat_p);
  //质量含气率
  x = Medium.vapourQuality(state_ph);
  //其余物性
  MM = Medium.molarMass(state_ph);
  beta = Medium.beta(state_pT);
  kappa = Medium.kappa(state_pT);
  //偏导数
  ddhp = Medium.density_derh_p(state_pT);
  ddph = Medium.density_derp_h(state_pT);
  ddldp = Medium.dBubbleDensity_dPressure(sat_p);
  ddvdp = Medium.dDewDensity_dPressure(sat_p);
  dhldp = Medium.dBubbleEnthalpy_dPressure(sat_p);
  dhvdp = Medium.dDewEnthalpy_dPressure(sat_p);
  //无量纲数
  Pr = Medium.prandtlNumber(state_ph);

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
    experiment(Algorithm = Dassl, NumberOfIntervals = 500, StartTime = 0, StopTime = 1, Tolerance = 0.0001), __MWORKS(ContinueSimConfig(SaveContinueFile = "false", SaveBeforeStop = "false", NumberBeforeStop = 1, FixedContinueInterval = "false", ContinueIntervalLength = 0.002, ContinueTimeVector)), Protection(access = Access.nonPackageDuplicate));
end Helmholtz_Calculate;