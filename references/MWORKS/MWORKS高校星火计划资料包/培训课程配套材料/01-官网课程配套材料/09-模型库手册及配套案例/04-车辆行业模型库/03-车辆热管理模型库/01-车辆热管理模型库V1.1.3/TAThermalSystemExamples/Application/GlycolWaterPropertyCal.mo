model GlycolWaterPropertyCal "乙二醇水物性计算模块"
  extends TAThermalSystem.Utilities.Icons.SpecialIcons.Experiment;
  import E = Modelica.Constants.e;
  replaceable package Medium = TYBase.Media_Extend.GW50 
    annotation (Protection(access=Access.nonPackageDuplicate));



  parameter Modelica.Units.SI.Pressure p = 5e5;
  parameter Modelica.Units.SI.Temperature T = 343.15;
  Modelica.Units.SI.SpecificHeatCapacityAtConstantPressure Cp = Medium.Cp_pT(p, T) "比热容";
  Modelica.Units.SI.DynamicViscosity mu = Medium.mu_pT(p, T) "粘度";
  Modelica.Units.SI.ThermalConductivity lambda = Medium.lambda_T(T) "热导率";
  Modelica.Units.SI.Density d = Medium.d_pT(p, T) "密度";
  Modelica.Units.SI.SpecificEnthalpy h = Medium.h_T(T) "比焓";
  annotation (Protection(access=Access.nonPackageDuplicate),Documentation(link="modelica://TAThermalSystem/Resource/Doc/GlycolWaterPropertyCal.html"
),__MWORKS(ResultViewerManager(resultViewers={
ResultViewer(name="h", executeTrigger=executeTrigger.SimulationStarted, commands={
CreatePlot(id=1, x_display_unit="s", legend_layout=7, left_title="[J/kg]", fix_time_range_value=0, zoom_x=(0, 1), zoom_y_l=(171640, 171720)),
Plot(y=["h"], thicknesses=[2], colors=["4278190335"])})
})));
end GlycolWaterPropertyCal;