model UserDefined "dm=f(dp,T)"
  extends TAThermalSystem.Utilities.Icons.BasicIcons.Example;
  parameter Modelica.Units.SI.MassFlowRate m_flow_coolin = 0.618 "冷端输入流量";
  parameter Modelica.Units.SI.MassFlowRate m_flow_heatin = 0.3 "热端输入流量";
  parameter Modelica.Units.SI.Temperature T_heatin = 343.15 "热端温度";
  TAThermalSystem.HeatExchangers.CoolingRadiatorNTU.Water_Air_HXNTU water_air_HXTU(
    title = "散热器", ConsiderMass = false, redeclare model Friction_ab = TYBase.Thermal.FluidHeatFlow.PressureLoss.HXPressureDrop.UserDefined, Across1(displayUnit = "m2"), Dhyd1(displayUnit = "mm"), cearea1(displayUnit = "m2"), heattransferType_1 = TYBase.Thermal.FluidHeatFlow.HeatExchangers.Basic.HeatTransferType.Nusseltnumber, ConsiderationFins_cd = false,
    etas2 = 0.8, ConsiderationFins_ab = true, heattransferType_2 = TYBase.Thermal.FluidHeatFlow.HeatExchangers.Basic.HeatTransferType.Nusseltnumber, fromDp = false) annotation(Placement(transformation(origin = {1.0634089535310065, 0.039262692492224804},
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TAThermalSystem.Sources.Coolant.Coolant_mT Coolant_mT(title = "水出口", mflow = m_flow_heatin, T_source = T_heatin) 
    annotation(Placement(transformation(origin = {-35.26111246797721, 22.172413183310553},
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TAThermalSystem.Sources.Coolant.Coolant_tank Coolant_pT(title = "水出口", p = 4.999999999999999e5,
    T_in(start
    = 293.15)) 
    annotation(Placement(transformation(origin = {41.431874207743476, 20.842944204079796},
    extent = {{10.0, -10.0}, {-10.0, 10.0}})));
  TAThermalSystem.Sources.Air.AirSource_mT airSource_mT1(m = m_flow_coolin, phi_source = 0.4,
    T = 313.15,
  redeclare package Medium = TYBase.Media_Extend.Air.MoistAir) 
    annotation(Placement(transformation(origin = {40.934313612497355, -24.85248750658971},
    extent = {{10.0, -9.999999999999996}, {-10.0, 10.0}})));
  TAThermalSystem.Sources.Air.AirSink_pT airSink_pT1(T_sink = 313.15, phi_sink = 0.4, redeclare package Medium = TYBase.Media_Extend.Air.MoistAir) 
    annotation(Placement(transformation(origin = {-35.46266418315975, -25.37237850233207},
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));

  Modelica.Units.SI.Pressure pa;
  Modelica.Units.SI.Pressure pb;
  Modelica.Units.SI.Pressure pc;
  Modelica.Units.SI.Pressure pd;
  annotation(Icon(coordinateSystem(extent = {{-100.0, -100.0}, {100.0, 100.0}},
    grid = {2.0, 2.0})),
    Protection(access=Access.nonPackageDuplicate),
    Documentation(link="modelica://TAThermalSystem/Resource/Doc/CoolantAirRadiatorUserDefined.html"
),__MWORKS(ResultViewerManager(resultViewers={
ResultViewer(name="1", executeTrigger=executeTrigger.SimulationStarted, commands={
CreatePlot(id=1, x_display_unit="s", legend_layout=7, left_title="[bar]", fix_time_range_value=0, zoom_x=(0, 10), zoom_y_l=(0.0061978, 0.0061986)),
Plot(y=["water_air_HXTU.hXSummary.dp_ab"], thicknesses=[2], colors=["4278190335"]),
CreatePlot(id=-1, x_display_unit="s", legend_layout=7, left_title="[W]", fix_time_range_value=0, sub_plot=(2, 1), zoom_x=(0, 10), zoom_y_l=(-106.305, -106.301)),
Plot(y=["water_air_HXTU.hXSummary.Qdot_abTotal"], thicknesses=[2], colors=["4278190335"])})
})));
equation
  pa = water_air_HXTU.hXSummary.pa;
  pb = water_air_HXTU.hXSummary.pb;
  pc = water_air_HXTU.hXSummary.pc;
  pd = water_air_HXTU.hXSummary.pd;


  connect(airSink_pT1.port_a, water_air_HXTU.d) 
    annotation(Line(origin = {-16.0, -15.0},
    points = {{-9.0, -10.0}, {7.0, -10.0}, {7.0, 9.0}},
    color = {0, 232, 232},
    thickness = 1.0));
  connect(water_air_HXTU.c, airSource_mT1.port_b) 
    annotation(Line(origin = {21.0, -14.0},
    points = {{-10.0, 8.0}, {-10.0, -11.0}, {10.0, -11.0}},
    color = {0, 232, 232},
    thickness = 1.0));
  connect(Coolant_mT.port_b, water_air_HXTU.a) 
    annotation(Line(origin = {-17.0, 14.0},
    points = {{-8.0, 8.0}, {8.0, 8.0}, {8.0, -8.0}},
    color = {0, 0, 128},
    thickness = 1.0));
  connect(water_air_HXTU.b, Coolant_pT.port_a) 
    annotation(Line(origin = {21.0, 14.0},
    points = {{-10.0, -8.0}, {-10.0, 7.0}, {10.0, 7.0}},
    color = {0, 0, 128},
    thickness = 1.0));
end UserDefined;