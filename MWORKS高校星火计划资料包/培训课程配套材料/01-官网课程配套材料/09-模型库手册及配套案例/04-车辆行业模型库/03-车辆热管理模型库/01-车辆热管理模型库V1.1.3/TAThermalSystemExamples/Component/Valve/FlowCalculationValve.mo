model FlowCalculationValve "流量计算阀门"
  parameter Real m_flow = 0.2 "质量流量";
  annotation(Documentation(link = "modelica://TAThermalSystem/Resource/Doc/FlowCalculationValve.html"), info = "<html><p>
<br>
</p>
</html>", Icon(coordinateSystem(extent = {{-100.0, -100.0}, {100.0, 100.0}},
    grid = {2.0, 2.0}), graphics = {Bitmap(origin = {0.0, 0.0},
    extent = {{-100.0, -100.0}, {100.0, 100.0}},
    fileName = "modelica://TAThermalSystem/Resource/Icons/Example.svg")}),
    Protection(access=Access.nonPackageDuplicate),
    experiment(Algorithm = Dassl, NumberOfIntervals = 500, StartTime = 0, StopTime = 10, Tolerance = 0.0001), __MWORKS(ContinueSimConfig(SaveContinueFile = "false", SaveBeforeStop = "false", NumberBeforeStop = 1, FixedContinueInterval = "false", ContinueIntervalLength = 10, ContinueTimeVector),ResultViewerManager(resultViewers={
ResultViewer(name="1", executeTrigger=executeTrigger.SimulationStarted, commands={
CreatePlot(id=1, x_display_unit="s", legend_layout=7, left_title="[bar]", fix_time_range_value=0, zoom_x=(0, 10), zoom_y_l=(4.8, 6.2)),
Plot(y=["pin", "pout"], thicknesses=[2, 2], colors=["4278190335", "4294901760"])})
})));
  TAThermalSystem.Sources.Coolant.Coolant_pT Coolant_pT(p = 4.999999999999999e5) 
    annotation(Placement(transformation(origin = {50.9869969040248, 1.9999999999999964},
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TAThermalSystem.Sources.Coolant.Coolant_mT Coolant_mT(mflow = m_flow) 
    annotation(Placement(transformation(origin = {-44.000000000000014, 2.0},
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TAThermalSystem.Valves.HydraulicValve.FixedValve orifice1(fromDp = false) annotation(Placement(transformation(origin = {3.493498452012396, 2.0377740303541283},
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  Modelica.Units.SI.Pressure pin;
  Modelica.Units.SI.Pressure pout;
equation
  pin = orifice1.P_in;
  pout = orifice1.P_out;
  connect(orifice1.b, Coolant_pT.port_a) 
    annotation(Line(origin = {28.38699690402477, 3.624770934378898},
    points = {{-15.0, -2.0}, {13.0, -2.0}},
    color = {0, 0, 128},
    thickness = 1.0));
  connect(orifice1.a, Coolant_mT.port_b) 
    annotation(Line(origin = {-19.613003095975234, 4.624770934378898},
    points = {{13.0, -3.0}, {-14.0, -3.0}},
    color = {0, 0, 128},
    thickness = 1.0));
end FlowCalculationValve;