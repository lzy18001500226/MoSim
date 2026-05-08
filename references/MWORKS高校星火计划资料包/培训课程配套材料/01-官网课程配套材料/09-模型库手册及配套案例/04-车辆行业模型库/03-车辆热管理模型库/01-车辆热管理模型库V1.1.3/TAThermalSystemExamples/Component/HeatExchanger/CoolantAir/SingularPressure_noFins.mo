model SingularPressure_noFins "冷却液—空气换热器"
  extends TAThermalSystem.Utilities.Icons.BasicIcons.Example;
  parameter Modelica.Units.SI.MassFlowRate m_flow_coolin = 0.618 "冷端输入流量";
  parameter Modelica.Units.SI.MassFlowRate m_flow_heatin = 0.2 "热端输入流量";
  parameter Modelica.Units.SI.Temperature T_heatin = 343.15 "热端温度";
  TAThermalSystem.HeatExchangers.CoolingRadiatorNTU.Water_Air_HXNTU water_air_HXTU(
    title = "散热器", ConsiderMass = false, redeclare model Friction_ab = TYBase.Thermal.FluidHeatFlow.PressureLoss.HXPressureDrop.SingularPressureDrop, Across1(displayUnit = "m2"), Dhyd1(displayUnit = "mm"), cearea1(displayUnit = "m2"), heattransferType_1 = TYBase.Thermal.FluidHeatFlow.HeatExchangers.Basic.HeatTransferType.Nusseltnumber, ConsiderationFins_cd = false,
    etas2 = 0.8, ConsiderationFins_ab = false, heattransferType_2 = TYBase.Thermal.FluidHeatFlow.HeatExchangers.Basic.HeatTransferType.Nusseltnumber, fromDp = false) annotation (Placement(transformation(origin = {1.0634089535310065, 0.039262692492224804},
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TAThermalSystem.Sources.Coolant.Coolant_mT Coolant_mT(title = "水出口", mflow = m_flow_heatin, T_source = T_heatin) 
    annotation (Placement(transformation(origin = {-35.46266418315976, 20.842944204079796},
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TAThermalSystem.Sources.Coolant.Coolant_tank Coolant_pT(title = "水出口", p = 4.999999999999999e5,
    T_in(start
       = 293.15)) 
    annotation (Placement(transformation(origin = {41.431874207743476, 20.842944204079796},
      extent = {{10.0, -10.0}, {-10.0, 10.0}})));
  TAThermalSystem.Sources.Air.AirSource_mT airSource_mT1(m = m_flow_coolin, phi_source = 0.4,
    T = 313.15,
    redeclare package Medium = TYBase.Media_Extend.Air.MoistAir) 
    annotation (Placement(transformation(origin = {40.934313612497355, -24.85248750658971},
      extent = {{10.0, -9.999999999999996}, {-10.0, 10.0}})));
  TAThermalSystem.Sources.Air.AirSink_pT airSink_pT1(T_sink = 313.15, phi_sink = 0.4, redeclare package Medium = TYBase.Media_Extend.Air.MoistAir) 
    annotation (Placement(transformation(origin = {-35.46266418315975, -25.37237850233207},
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));

  annotation (Icon(coordinateSystem(extent = {{-100.0, -100.0}, {100.0, 100.0}},
    grid = {2.0, 2.0})),
    Protection(access=Access.nonPackageDuplicate),
    Documentation(link="modelica://TAThermalSystem/Resource/Doc/CoolantAirRadiatorSingularPressure_noFins.html"),experiment(Algorithm=Dassl,NumberOfIntervals=1200,StartTime=0,StopTime=120,Tolerance=0.0001,InlineIntegrator=false,InlineStepSize=false,StoreEventValue=0),__MWORKS(ContinueSimConfig(SaveContinueFile="false",SaveBeforeStop="false",NumberBeforeStop=1,FixedContinueInterval="false",ContinueIntervalLength=120,ContinueTimeVector),ResultViewerManager(resultViewers={
ResultViewer(name="1", executeTrigger=executeTrigger.SimulationStarted, commands={
CreatePlot(id=1, x_display_unit="s", legend_layout=7, left_title="[bar]", fix_time_range_value=0, zoom_x=(0, 100), zoom_y_l=(-0.039378, -0.039369)),
Plot(y=["water_air_HXTU.hXSummary.dp_ab"], thicknesses=[2], colors=["4278190335"]),
CreatePlot(id=-1, x_display_unit="s", legend_layout=7, left_title="[W]", fix_time_range_value=0, sub_plot=(2, 1), zoom_x=(0, 100), zoom_y_l=(-93.841, -93.8385)),
Plot(y=["water_air_HXTU.hXSummary.Qdot_abTotal"], thicknesses=[2], colors=["4278190335"])})
})));
equation
  connect(airSink_pT1.port_a, water_air_HXTU.d) 
    annotation (Line(origin = {-16.0, -15.0},
      points = {{-9.462664183159752, -10.372378502332069}, {7.0, -10.372378502332069}, {7.0, 8.882896652054358}, {7.100207873595327, 8.882896652054358}},
      color = {0, 232, 232},
      thickness = 1.0));
  connect(water_air_HXTU.c, airSource_mT1.port_b) 
    annotation (Line(origin = {21.0, -14.0},
      points = {{-9.82468547280293, 8.001860247038662}, {-9.82468547280293, -11.0}, {9.934313612497355, -11.0}, {9.934313612497355, -10.85248750658971}},
      color = {0, 232, 232},
      thickness = 1.0));
  connect(Coolant_mT.port_b, water_air_HXTU.a) 
    annotation (Line(origin = {-17.0, 14.0},
      points = {{-8.46266418315976, 6.842944204079796}, {8.04919985460008, 6.842944204079796}, {8.04919985460008, -7.958955423300015}},
      color = {0, 0, 128},
      thickness = 1.0));
  connect(water_air_HXTU.b, Coolant_pT.port_a) 
    annotation (Line(origin = {21.0, 14.0},
      points = {{-9.888664071784092, -8.09382692631592}, {-9.888664071784092, 7.0}, {20.431874207743476, 7.0}, {20.431874207743476, 6.842944204079796}},
      color = {0, 0, 128},
      thickness = 1.0));
end SingularPressure_noFins;