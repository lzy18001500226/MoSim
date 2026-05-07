model Solid_Calculate "固体介质调用与物性计算示例"
  import SI = Modelica.SIunits;
  /* 介质 */
  replaceable package Medium = TYMedia.Solid.Steel 
    constrainedby TYMedia.Solid.PartialSolidMedium 
    annotation(choicesAllMatching = true,Protection(access=Access.nonPackageDuplicate));

  /* 参数 */
  //根据温度计算介质物性
  parameter SI.Temperature T = 298.15 "温度";

  /* 变量 */
  SI.Density rho "密度";
  SI.SpecificHeatCapacity cp "定压比热";
  SI.ThermalConductivity lamda "导热系数";
equation
  rho = Medium.rho_T(T);
  cp = Medium.Cp_T(T);
  lamda = Medium.thermalConductivity_T(T);

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
    thickness = 5)}), experiment(Algorithm = Dassl, StartTime = 0, StopTime = 1, Tolerance = 0.0001, NumberOfIntervals = 500), __MWORKS(ContinueSimConfig(SaveContinueFile = "false", SaveBeforeStop = "false", NumberBeforeStop = 1, FixedContinueInterval = "false", ContinueIntervalLength = 0.002, ContinueTimeVector)),Protection(access=Access.nonPackageDuplicate));
end Solid_Calculate;