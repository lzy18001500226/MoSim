model RefPropertyCal "制冷剂物性计算"
  extends TAThermalSystem.Utilities.Icons.SpecialIcons.Experiment;

  replaceable package Medium = TYMedia.Helmholtz.R134a 
    constrainedby TYMedia.Helmholtz.PartialHelmholtz "介质" 
    annotation(choicesAllMatching = true, Protection(access=Access.nonPackageDuplicate));

  // replaceable package Medium = TYBase.Media_Extend.Refrigerant.R134a 
  //   annotation (Protection(access = Access.nonPackageDuplicate));
  import TYBase.Thermal.FluidHeatFlow.Components.Functions.spliceFunction;

  parameter Boolean initialtypeTX = false "是否以温度和干度进行饱和态初始化" annotation (Dialog(group = "查询类型"));
  input Modelica.SIunits.Temperature Tsatin = 293.15 "饱和态温度" annotation (Dialog(group = "输入数据", enable = initialtypeTX));
  input Real X(min = 0, max = 1, unit = "1") = 1 "干度,输入0~1" annotation (Dialog(group = "输入数据", enable = initialtypeTX));
  input Modelica.SIunits.SpecificEnthalpy hin = 200000 "比焓" annotation (Dialog(group = "输入数据", enable = initialtypeTX == false));
  input Modelica.SIunits.Pressure pin = 200000 "压力" annotation (Dialog(group = "输入数据", enable = initialtypeTX == false));


 Modelica.SIunits.AbsolutePressure p = if initialtypeTX then Medium.saturationPressure(Tsatin) else pin "R134a压力";
 Modelica.SIunits.SpecificEnthalpy h = if initialtypeTX then 
    X * (Medium.dewEnthalpy_pX(p = p, X = Medium.fixedComposition) - Medium.bubbleEnthalpy_pX(p = p, X = Medium.fixedComposition)) +
    Medium.bubbleEnthalpy_pX(p = p, X = Medium.fixedComposition) else hin "R134a比焓" ;
  Medium.SaturationProperties bubble "液相压力和温度线";
  Modelica.SIunits.DerDensityByEnthalpy ddhp "密度对比焓偏导";
  Modelica.SIunits.DerDensityByPressure ddph "密度对压力偏导";
  Medium.ThermodynamicState state(phase(each start = 2)) "R134a热力学状态";
  Modelica.SIunits.SpecificHeatCapacity cp "定压比热容";
  Modelica.SIunits.SpecificHeatCapacity cv "定容比热容";
  Modelica.SIunits.DynamicViscosity eta "动力粘度";
  Modelica.SIunits.DynamicViscosity eta_dukler "动力粘度";
  Modelica.SIunits.DynamicViscosity eta_github "基于Github的NIST公式动力粘度";
  Modelica.SIunits.DynamicViscosity eta_github_liq "基于Github的NIST公式计算液相动力粘度";
  Modelica.SIunits.DynamicViscosity eta_github_vap "基于Github的NIST公式计算气相动力粘度";

  Modelica.SIunits.SpecificVolume v_ave "比体积";
  Modelica.SIunits.SurfaceTension sigma "表面张力";
  Modelica.SIunits.ThermalConductivity lam "热导率";
  Modelica.SIunits.Density d "密度";
  Modelica.SIunits.Temperature T "温度";
  Modelica.SIunits.Temperature Tsat = Medium.saturationTemperature(p) "温度";
  Medium.MassFraction quality "干度";
  Modelica.SIunits.PrandtlNumber Pr "普朗特数";
  Modelica.SIunits.SpecificEntropy s "比熵";
  Medium.ThermodynamicState vap(phase(each start = 1)) "气态热力学状态";
  Medium.ThermodynamicState liq(phase(each start = 1)) "液态热力学状态";
  Modelica.SIunits.PrandtlNumber Pr_liq "液相普朗特数";
  Modelica.SIunits.PrandtlNumber Pr_vap "气相普朗特数";
  Modelica.SIunits.SpecificEntropy s_liq "液相比熵";
  Modelica.SIunits.SpecificEntropy s_vap "气相比熵";
  Modelica.SIunits.SpecificEnthalpy h_liq "液相比焓";
  Modelica.SIunits.SpecificEnthalpy h_vap "气相比焓";
  Modelica.SIunits.Density d_liq(start = 1000.0) "液相平均密度";
  Modelica.SIunits.Density d_vap(start = 100.0) "气相平均密度";
  Medium.PhaseBoundaryProps sat "饱和热力学状态(包括气相和液相)";
  Real pred "相对临界压力,pred>1表示临界状态";
  annotation (Protection(access=Access.nonPackageDuplicate),
    experiment(Algorithm = Dassl, NumberOfIntervals = 500, StartTime = 0, StopTime = 100, Tolerance = 0.0001),Documentation(link="modelica://TAThermalSystem/Resource/Doc/RefPropertyCal.html"
),__MWORKS(ResultViewerManager(resultViewers={
ResultViewer(name="1", executeTrigger=executeTrigger.SimulationFinished, commands={
CreatePlot(id=1, x_display_unit="s", legend_layout=7, fix_time_range_value=0, zoom_x=(0, 100), zoom_y_l=(-0.4, 0.4)),
Plot(y=["initialtypeTX"], colors=["4278190335"]),
CreatePlot(id=-1, x_display_unit="s", legend_layout=7, left_title="[bar]", fix_time_range_value=0, sub_plot=(2, 1), zoom_x=(0, 100), zoom_y_l=(-2, 6)),
Plot(y=["p"], colors=["4278190335"])})
})));
equation

  bubble.psat = min(p, Medium.fluidConstants[1].criticalPressure);
  bubble.Tsat = Medium.bubbleTemperature(bubble.psat, Medium.fixedComposition);
  bubble.Xsat = Medium.fixedComposition;
  sigma = Medium.surfaceTension(bubble);
  ddph = Medium.density_derp_h(state);
  ddhp = Medium.density_derh_p(state);
  eta_dukler = 1 / v_ave * (sat.x * sat.eta_vap / sat.d_vap + (1 - sat.x) * sat.eta_liq / sat.d_liq);
  v_ave = sat.x * (1 / sat.d_vap) + (1 - sat.x) * (1 / sat.d_liq);

  state = Medium.setState_phX(p, h, X = Medium.fixedComposition, phase = 0);
  cp = min(max(Medium.specificHeatCapacityCp_phX(p, h, X = Medium.fixedComposition, phase = 0), 500), 5e5);
  cv = Medium.specificHeatCapacityCv_phX(p, h, X = Medium.fixedComposition, phase = 0);
  eta = Medium.dynamicViscosity_dTX(state.d, state.T, state.X);
  lam = Medium.thermalConductivity_dTX(d, T, Medium.fixedComposition);
  d = Medium.density(state);
  T = Medium.temperature(state);
  quality = smooth(0, max(0.0, min(1.0, sat.x)));
  Pr = cp * eta_github / lam;
  s = Medium.specificEntropy_phX(p, h);


  sat.d_vap = d_vap;
  sat.d_liq = d_liq;
  pred = p / Medium.fluidConstants[1].criticalPressure;
  liq = Medium.setState_phX(p = p, h = h_liq);
  vap = Medium.setState_phX(p = p, h = h_vap);
  sat.lam_vap = min(max(Medium.thermalConductivity_dTX(vap.d, vap.T, vap.X), 1.0e-4), 2.0);
  sat.lam_liq = min(max(Medium.thermalConductivity_dTX(liq.d, liq.T, liq.X), 1.0e-4), 2.0);
  sat.cp_vap = min(max(Medium.specificHeatCapacityCp(vap), 500), 5e5);
  sat.cp_liq = min(max(Medium.specificHeatCapacityCp(liq), 500), 5e5);
  sat.eta_vap = Medium.dynamicViscosity_dTX(vap.d, vap.T, vap.X);
  sat.eta_liq = Medium.dynamicViscosity_dTX(liq.d, liq.T, liq.X);
  sat.x = (h - h_liq) / max(h_vap - h_liq, 1e-6);
  d_liq = Medium.bubbleDensity(bubble);
  d_vap = Medium.dewDensity(bubble);
  h_vap = Medium.dewEnthalpy(bubble);
  h_liq = Medium.bubbleEnthalpy(bubble);
  Pr_liq = sat.cp_liq * sat.eta_liq / sat.lam_liq;
  Pr_vap = sat.cp_vap * sat.eta_vap / sat.lam_vap;
  s_liq = Medium.specificEntropy_phX(p, h_liq);
  s_vap = Medium.specificEntropy_phX(p, h_vap);
  // //
  eta_github_liq = TYBase.Media_Extend.Utilities.DynamicViscosity.dynamicViscosity_Td(liq.T, liq.d);
  eta_github_vap = TYBase.Media_Extend.Utilities.DynamicViscosity.dynamicViscosity_Td(vap.T, vap.d);
  eta_github = d * (quality * eta_github_vap / vap.d + (1 - quality) * eta_github_liq / liq.d);


end RefPropertyCal;