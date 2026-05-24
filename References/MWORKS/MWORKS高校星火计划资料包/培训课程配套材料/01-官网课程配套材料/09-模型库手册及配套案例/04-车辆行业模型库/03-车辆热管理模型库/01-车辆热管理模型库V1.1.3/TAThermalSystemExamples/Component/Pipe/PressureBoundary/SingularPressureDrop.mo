model SingularPressureDrop "SingularPressureDrop压降方式"

  parameter Modelica.Units.SI.Temperature T_heatin = 343.15 "壁面边界温度";
  parameter Modelica.Units.SI.Pressure p_in(displayUnit = "Pa") = 396143 "输入压力";
  TAThermalSystem.Sources.Coolant.Coolant_pT Coolant_pT1(p = 100000, title = "水进口") 
    annotation (Placement(transformation(origin = {56.05140230006194, -2.7585198456086726},
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TAThermalSystem.Sources.HeatTransfer.FixedTemperature fixedTemperature(T = T_heatin,
    n = 1) annotation (Placement(transformation(origin = {-28.087195457043418, 35.97581974720646},
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TAThermalSystem.Pipes.LiquidCoolingPipe.CoolingPipe coolingPipeBase2(
    useHeatTransfer = true, redeclare Integer calType = 2, h_conv_set = 75,
    CF_PressureLoss = 1,
    p0 = 100000,
    fromDp = true,
    redeclare model Friction = TYBase.Thermal.FluidHeatFlow.PressureLoss.LiquidPressureDrop.SingularPressureDrop) annotation (Placement(transformation(origin = {2.662432518259771, -1.9330812090418306},
      extent = {{-10.0997, -8.821720000000001}, {10.0638, 9.007800000000001}})));

  TAThermalSystem.Sources.Coolant.Coolant_pT Coolant_pT(
    p = p_in, title = "水进口") annotation (Placement(transformation(origin = {-63.36515129559615, -3.3365388415381148},
      extent = {{10.0, -10.0}, {-10.0, 10.0}})));
  annotation (Icon(coordinateSystem(extent = {{-100.0, -100.0}, {100.0, 100.0}},
    grid = {2.0, 2.0}), graphics = {Bitmap(origin = {0.0, 0.0},
    extent = {{-100.0, -100.0}, {100.0, 100.0}},
    fileName = "modelica://TAThermalSystem/Resource/Icons/Example.svg")}),
    Protection(access=Access.nonPackageDuplicate),
    experiment(Algorithm = Dassl, NumberOfIntervals = 500, StartTime = 0, StopTime = 10, Tolerance = 0.0001),
    Documentation(link = "modelica://TAThermalSystem/Resource/Doc/PressureBoundarySingularPressureDrop.html"
),__MWORKS(ResultViewerManager(resultViewers={
ResultViewer(name="1", executeTrigger=executeTrigger.SimulationStarted, commands={
CreatePlot(id=1, x_display_unit="s", legend_layout=7, left_title="[kg/s]", fix_time_range_value=0, zoom_x=(0, 10), zoom_y_l=(8.64611, 8.64615)),
Plot(y=["coolingPipeBase2.pipeSummary.mdot"], thicknesses=[2], colors=["4278190335"])})
})));
equation
  connect(fixedTemperature.port[1], coolingPipeBase2.qa) 
    annotation (Line(origin = {-8.0, 22.0},
      points = {{-10.0, 14.0}, {11.0, 14.0}, {11.0, -14.0}},
      color = {191, 0, 0},
      thickness = 1.0));
  connect(coolingPipeBase2.b, Coolant_pT1.port_a) 
    annotation (Line(origin = {35.0, -2.0},
      points = {{-22.0, 0.0}, {11.0, 0.0}, {11.0, -1.0}},
      color = {0, 0, 128},
      thickness = 1.0));
  connect(Coolant_pT.port_a, coolingPipeBase2.a) 
    annotation (Line(origin = {-30.0, -2.0},
      points = {{-23.0, -1.0}, {23.0, -1.0}, {23.0, 0.0}},
      color = {0, 0, 128},
      thickness = 1.0));
end SingularPressureDrop;