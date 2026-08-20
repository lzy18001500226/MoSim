within MoSimQuadrotorModel.Guidance.Planning;
model Sunray150PlanningOpenBlocksPx4CtrlSysblockDynamicClosedLoop
  "PX4CTRL whole-aircraft tracking of dynamic OpenBlocks A* path from MAT file"

  parameter Real initial_position_m[3](each unit = "m") = {-41, -26, 1.5}
    "Match the first OpenBlocks reference point at the sampled controller boundary";

  MoSimQuadrotorModel.Guidance.Trajectories.OpenBlocksDynamicReference reference
    annotation(Placement(transformation(origin = {-82, 50}, extent = {{-18, -18}, {18, 18}})));
  OpenBlocksPx4CtrlVehicle vehicle(initial_position = initial_position_m)
    annotation(Placement(transformation(origin = {50, 50}, extent = {{-38, -38}, {38, 38}})));

  OpenBlocksMapTruthDisplay navigationDisplay
    annotation(Placement(transformation(extent={{-15,-46},{15,-6}})));

equation
  connect(reference.position_command, vehicle.position_reference) annotation(Line(points = {{-64, 57.2}, {-20, 57.2}, {-20, 63.5}, {7.6, 63.5}}, color = {0, 0, 127}));
  connect(reference.velocity_command, vehicle.velocity_reference) annotation(Line(points = {{-64, 50}, {-14, 50}, {-14, 53.8}, {7.6, 53.8}}, color = {0, 0, 127}));
  connect(reference.acceleration_command, vehicle.acceleration_reference) annotation(Line(points = {{-64, 42.8}, {-20, 42.8}, {-20, 44.1}, {7.6, 44.1}}, color = {0, 0, 127}));
  connect(vehicle.position, navigationDisplay.actual_position);
  connect(reference.position_command, navigationDisplay.reference_position);

  annotation(
    experiment(Algorithm = Dassl, StartTime = 0, StopTime = 300,
      Tolerance = 0.0001, Interval = 0.01),
    __MWORKS(hide=true,version="26.3.0"));
end Sunray150PlanningOpenBlocksPx4CtrlSysblockDynamicClosedLoop;
