within MoSimQuadrotorModel.Support.Models;
block TraceTableReference
  "Reference source that reads x/y/z/yaw commands from a Modelica table file"
  parameter String tableName = "trace_ref";
  parameter String fileName = "NoName";

  Modelica.Blocks.Sources.CombiTimeTable traceTable(
    tableOnFile = true,
    tableName = tableName,
    fileName = fileName,
    columns = {2, 3, 4, 5, 6},
    smoothness = Modelica.Blocks.Types.Smoothness.LinearSegments,
    extrapolation = Modelica.Blocks.Types.Extrapolation.HoldLastPoint,
    verboseRead = false);

  Modelica.Blocks.Interfaces.RealOutput position_command[3]
    annotation(Placement(transformation(origin = {100, 40}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Interfaces.RealOutput z_ref_rate
    annotation(Placement(transformation(origin = {100, 0}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Interfaces.RealOutput yaw_ref
    annotation(Placement(transformation(origin = {100, -40}, extent = {{-10, -10}, {10, 10}})));

equation
  position_command[1] = traceTable.y[1];
  position_command[2] = traceTable.y[2];
  position_command[3] = traceTable.y[3];
  yaw_ref = traceTable.y[4];
  z_ref_rate = traceTable.y[5];

  annotation(
    Icon(coordinateSystem(extent = {{-100, -100}, {100, 100}}), graphics = {
      Rectangle(extent = {{-100, -100}, {100, 100}}, lineColor = {32, 88, 130}, fillColor = {238, 248, 255}, fillPattern = FillPattern.Solid),
      Line(points = {{-80, -20}, {-20, 30}, {30, -5}, {80, 28}}, color = {32, 88, 130}, thickness = 1.2),
      Text(extent = {{-92, -60}, {92, -86}}, textString = "Trace Table", textColor = {32, 88, 130})}),
    Diagram(coordinateSystem(extent = {{-120, -80}, {120, 80}})));
  annotation(__MWORKS(hide=true));
end TraceTableReference;
