model singular "冷却液—冷却液换热器"
  extends TAThermalSystem.Utilities.Icons.BasicIcons.Example;
  parameter Modelica.Units.SI.MassFlowRate m_flow_coolin = 0.3 "冷端输入流量";
  parameter Modelica.Units.SI.MassFlowRate m_flow_heatin = 0.2 "热端输入流量";
  parameter Modelica.Units.SI.Temperature T_heatin(displayUnit = "degC") = 343.15 "热端温度";
  TAThermalSystem.HeatExchangers.CoolingRadiatorNTU.Water_WaterHXNTU water_WaterHXNTU_(ConsiderationFins_cd = false, ConsiderationFins_ab = false, heattransferType_1 = TAThermalSystem.HeatExchangers.CoolingRadiatorNTU.Water_WaterHXNTU.HeatTransferType.Nusseltnumber, heattransferType_2 = TAThermalSystem.HeatExchangers.CoolingRadiatorNTU.Water_WaterHXNTU.HeatTransferType.Nusseltnumber,
  redeclare model Friction_ab = TYBase.Thermal.FluidHeatFlow.PressureLoss.HXPressureDrop.UserDefined, redeclare model Friction_cd = TYBase.Thermal.FluidHeatFlow.PressureLoss.HXPressureDrop.UserDefined) annotation(Placement(transformation(origin = {-2.7944489097334695, 0.0677945917309537},
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));


  TAThermalSystem.Sources.Coolant.Coolant_mT Coolant_mT(title = "水出口", mflow = m_flow_heatin, T_source = T_heatin) 
    annotation(Placement(transformation(origin = {-47.00054527669576, 27.57492830107095},
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TAThermalSystem.Sources.Coolant.Coolant_tank Coolant_pT(title = "水出口", p = 100000) 
    annotation(Placement(transformation(origin = {37.14713256779397, 26.99759949413892},
    extent = {{10.0, -10.0}, {-10.0, 10.0}})));
  TAThermalSystem.Sources.Coolant.Coolant_mT Coolant_mT1(title = "水出口", mflow = m_flow_coolin, T_source = 298.15) 
    annotation(Placement(transformation(origin = {34.227030659998135, -31.536977625914105},
    extent = {{10.0, -10.0}, {-10.0, 10.0}})));
  TAThermalSystem.Sources.Coolant.Coolant_tank Coolant_pT1(title = "水出口", p = 100000) 
    annotation(Placement(transformation(origin = {-45.537661231970866, -30.581497549188448},
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  annotation(Icon(coordinateSystem(extent = {{-100.0, -100.0}, {100.0, 100.0}},
    grid = {2.0, 2.0})),
    Protection(access=Access.nonPackageDuplicate),
    Documentation(link="modelica://TAThermalSystem/Resource/Doc/coolantCoolantRadiatorSingular.html"),experiment(Algorithm=Dassl,NumberOfIntervals=1200,StartTime=0,StopTime=120,Tolerance=0.0001,InlineIntegrator=false,InlineStepSize=false,StoreEventValue=0),__MWORKS(ContinueSimConfig(SaveContinueFile="false",SaveBeforeStop="false",NumberBeforeStop=1,FixedContinueInterval="false",ContinueIntervalLength=120,ContinueTimeVector),ResultViewerManager(resultViewers={
ResultViewer(name="1", executeTrigger=executeTrigger.SimulationStarted, commands={
CreatePlot(id=1, x_display_unit="s", legend_layout=7, left_title_type=2, left_title="[bar]", bottom_title_type=2, right_title_type=2, fix_time_range_value=0, zoom_x=(0, 120), zoom_y_l=(0.0041318, 0.0041325)),
Plot(y=["water_WaterHXNTU_.hXSummary.dp_ab"], thicknesses=[2], colors=["4278190335"]),
CreatePlot(id=-1, x_display_unit="s", legend_layout=7, left_title_type=2, left_title="[W]", bottom_title_type=2, right_title_type=2, fix_time_range_value=0, sub_plot=(2, 1), zoom_x=(0, 120), zoom_y_l=(-97.406, -97.399)),
Plot(y=["water_WaterHXNTU_.hXSummary.Qdot_abTotal"], thicknesses=[2], colors=["4278190335"])})
})));
  Modelica.Units.SI.Pressure pa;
  Modelica.Units.SI.Pressure pb;
  Modelica.Units.SI.Pressure pc;
  Modelica.Units.SI.Pressure pd;
equation
  pa = water_WaterHXNTU_.hXSummary.pa;
  pb = water_WaterHXNTU_.hXSummary.pb;
  pc = water_WaterHXNTU_.hXSummary.pc;
  pd = water_WaterHXNTU_.hXSummary.pd;
  connect(Coolant_pT1.port_a, water_WaterHXNTU_.d) 
    annotation(Line(origin = {-44.970839683139175, -17.8833587325567},
    points = {{-0.5668215488316903, -12.698138816631747}, {32.09590973201692, -12.698138816631747}, {32.09590973201692, 12.062455372564477}, {32.242930592216105, 12.062455372564477}},
    color = {0, 0, 128},
    thickness = 1.0));
  connect(water_WaterHXNTU_.c, Coolant_mT1.port_b) 
    annotation(Line(origin = {30.029160316860825, -17.8833587325567},
    points = {{-22.741444551674306, 12.0327144738184}, {-22.425506610912663, 12.0327144738184}, {-22.425506610912663, -14.0}, {-5.8021296568626894, -14.0}, {-5.8021296568626894, -13.653618893357404}},
    color = {0, 0, 128},
    thickness = 1.0));
  connect(Coolant_mT.port_b, water_WaterHXNTU_.a) 
    annotation(Line(origin = {-26.970839683139175, 11.116641267443304},
    points = {{-10.029705593556585, 16.45828703362765}, {14.034744300993564, 16.45828703362765}, {14.034744300993564, -5.130407825243097}},
    color = {0, 0, 128},
    thickness = 1.0));
  connect(water_WaterHXNTU_.b, Coolant_pT.port_a) 
    annotation(Line(origin = {35.029160316860825, 10.116641267443304},
    points = {{-27.62248095669, -4.189889622735249}, {-27.263751763046542, -4.189889622735249}, {-27.263751763046542, 16.88095822669562}, {2.1179722509331427, 16.88095822669562}},
    color = {0, 0, 128},
    thickness = 1.0));
end singular;