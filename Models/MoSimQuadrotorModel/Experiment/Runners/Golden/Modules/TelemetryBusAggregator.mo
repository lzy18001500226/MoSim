within MoSimQuadrotorModel.Experiment.Runners.Golden.Modules;
block TelemetryBusAggregator
  "Collect top-level telemetry into two visible recorder buses"

  input Real vehicle_values[28]
    "Bound vehicle and actuator telemetry; not a graphical terminal";
  input Real autonomy_values[40]
    "Bound perception, mission, and supervisor telemetry; not a graphical terminal";
  Modelica.Blocks.Interfaces.RealOutput vehicle_bus[28]
    "Actuation and plant telemetry bus" 
    annotation(Placement(
      transformation(origin = {100, 60}, extent = {{-8, -8}, {8, 8}}),
      iconTransformation(origin = {100, 60}, extent = {{-8, -8}, {8, 8}})));
  Modelica.Blocks.Interfaces.RealOutput autonomy_bus[40]
    "Avionics, mission, and supervisor telemetry bus" 
    annotation(Placement(
      transformation(origin = {100, -60}, extent = {{-8, -8}, {8, 8}}),
      iconTransformation(origin = {100, -60}, extent = {{-8, -8}, {8, 8}})));

equation
  vehicle_bus = vehicle_values;
  autonomy_bus = autonomy_values;

  annotation(
    Icon(coordinateSystem(extent = {{-100, -100}, {100, 100}}), graphics = {
      Rectangle(extent = {{-100, 100}, {100, -100}}, lineColor = {55, 80, 115},
        fillColor = {239, 246, 255}, fillPattern = FillPattern.Solid),
      Text(origin = {0, 26}, extent = {{-82, 18}, {82, -18}},
        textString = "Telemetry", textColor = {55, 80, 115}),
      Text(origin = {0, -18}, extent = {{-82, 18}, {82, -18}},
        textString = "bus merge", textColor = {55, 80, 115})}),
    Diagram(coordinateSystem(extent = {{-120, -100}, {120, 100}}, grid = {2, 2})),
    __MWORKS(version = "26.3.0"));
end TelemetryBusAggregator;