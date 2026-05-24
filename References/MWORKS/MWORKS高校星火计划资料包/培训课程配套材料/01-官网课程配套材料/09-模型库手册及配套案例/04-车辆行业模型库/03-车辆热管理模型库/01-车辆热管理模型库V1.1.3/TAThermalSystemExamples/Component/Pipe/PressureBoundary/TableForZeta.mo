model TableForZeta "TableForZeta压降方式"

  parameter Modelica.Units.SI.Temperature T_heatin = 343.15 "壁面边界温度";
  parameter Modelica.Units.SI.Pressure p_in (displayUnit="Pa")=550076 "输入压力";
  TAThermalSystem.Sources.Coolant.Coolant_pT Coolant_pT(
    p = p_in, title = "水进口") annotation (Placement(transformation(origin = {-63.36515129559615, -3.3365388415381148},
      extent = {{10.0, -10.0}, {-10.0, 10.0}})));
  TAThermalSystem.Pipes.LiquidCoolingPipe.CoolingPipe coolingPipeBase2(
    useHeatTransfer = true, redeclare model Friction =TAThermalSystem.Utilities.PressureDrop.TableForZeta, redeclare Integer calType = 2, h_conv_set = 75,
    CF_PressureLoss = 1,
    p0 = 100000,
    fromDp = true) annotation (Placement(transformation(origin = {2.662432518259771, -1.9330812090418306},
      extent = {{-10.0997, -8.821720000000001}, {10.0638, 9.007800000000001}})));
  TAThermalSystem.Sources.Coolant.Coolant_pT Coolant_pT1(p = 100000, title = "水进口") 
    annotation (Placement(transformation(origin = {56.05140230006194, -2.7585198456086726},
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TAThermalSystem.Sources.HeatTransfer.FixedTemperature fixedTemperature(T = T_heatin,
    n = 1) annotation (Placement(transformation(origin = {-28.087195457043418, 35.97581974720646},
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  annotation (Icon(coordinateSystem(extent = {{-100.0, -100.0}, {100.0, 100.0}},
    grid = {2.0, 2.0}), graphics = {Bitmap(origin = {0.0, 0.0},
    extent = {{-100.0, -100.0}, {100.0, 100.0}},
    fileName = "modelica://TAThermalSystem/Resource/Icons/Example.svg")}),
    Protection(access=Access.nonPackageDuplicate),
    experiment(Algorithm = Dassl, NumberOfIntervals = 500, StartTime = 0, StopTime = 10, Tolerance = 0.0001),
    Documentation(link = "modelica://TAThermalSystem/Resource/Doc/PressureBoundaryTableForZeta.html"
));
equation
  connect(coolingPipeBase2.b, Coolant_pT1.port_a) 
    annotation (Line(origin = {30.0, -2.0},
      points = {{-17.0, 0.0}, {16.0, 0.0}, {16.0, -1.0}},
      color = {0, 0, 128},
      thickness = 1.0));
  connect(Coolant_pT.port_a, coolingPipeBase2.a) 
    annotation (Line(origin = {-30.0, -2.0},
      points = {{-23.0, -1.0}, {23.0, -1.0}, {23.0, 0.0}},
      color = {0, 0, 128},
      thickness = 1.0));
  connect(fixedTemperature.port[1], coolingPipeBase2.qa) 
    annotation (Line(origin = {-7.0, 18.0},
      points = {{-11.0, 18.0}, {10.0, 18.0}, {10.0, -18.0}},
      color = {191, 0, 0},
      thickness = 1.0));

end TableForZeta;