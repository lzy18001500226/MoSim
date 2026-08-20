within MoSimQuadrotorModel.Guidance.Planning;
model ThreeUavOpenBlocksReconfigurableFormationPx4CtrlDynamic
  "Three whole-aircraft PX4CTRL loops following dynamic OpenBlocks references from MAT files"

  MoSimQuadrotorModel.Guidance.Trajectories.OpenBlocksDynamicReference reference1
    annotation(Placement(transformation(origin = {-82, 74}, extent = {{-18, -18}, {18, 18}})));
  MoSimQuadrotorModel.Guidance.Trajectories.OpenBlocksUav2DynamicReference reference2
    annotation(Placement(transformation(origin = {-82, 4}, extent = {{-18, -18}, {18, 18}})));
  MoSimQuadrotorModel.Guidance.Trajectories.OpenBlocksUav3DynamicReference reference3
    annotation(Placement(transformation(origin = {-82, -66}, extent = {{-18, -18}, {18, 18}})));

  OpenBlocksMapTruthDisplay navigationDisplay(
    n_segments = 54,
    p_x = {-41, -41, -41, -41, -41, -41, -41, -41, -41, -41, -41, -41, -41, -41, -41, -41, -41, -41, -41, -41, -41, -41, -41, -41, -41, -41, -41, -41, -41, -41, -41, -41, -41, -41, -41, -41, -41, -41, -41, -41, -41, -41, -41, -41, -41, -41, -41, -41, -41, -41, -41, -41, -41, 41},
    p_y = {-26, -26, -26, -26, -26, -26, -26, -26, -26, -26, -26, -26, -26, -26, -26, -26, -26, -26, -26, -26, -26, -26, -26, -26, -26, -26, -26, -26, -26, -26, -26, -26, -26, -26, -26, -26, -26, -26, -26, -26, -26, -26, -26, -26, -26, -26, -26, -26, -26, -26, -26, -26, -26, 26},
    p_z = {1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5},
    segment_duration = {1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1})
    annotation(Placement(transformation(origin = {0, 72}, extent = {{-22, -22}, {22, 22}})));

  OpenBlocksPx4CtrlVehicle vehicle1(initial_position = {-41, -26, 1.5})
    annotation(Placement(transformation(origin = {70, 74}, extent = {{-22, -22}, {22, 22}})));
  OpenBlocksPx4CtrlVehicle vehicle2(initial_position = {-43, -26, 1.5})
    annotation(Placement(transformation(origin = {70, 4}, extent = {{-22, -22}, {22, 22}})));
  OpenBlocksPx4CtrlVehicle vehicle3(initial_position = {-41, -28, 1.32})
    annotation(Placement(transformation(origin = {70, -66}, extent = {{-22, -22}, {22, 22}})));

  Real pair_distance_12_m;
  Real pair_distance_13_m;
  Real pair_distance_23_m;
  Real min_inter_uav_distance_m;
  Real reference_pair_distance_12_m;
  Real reference_pair_distance_13_m;
  Real reference_pair_distance_23_m;
  Real formation_distance_error_m;

equation
  connect(reference1.position_command, vehicle1.position_reference) annotation(Line(points = {{-64, 81.2}, {18, 81.2}, {18, 87.2}, {43.6, 87.2}}, color = {0, 0, 127}));
  connect(reference1.velocity_command, vehicle1.velocity_reference) annotation(Line(points = {{-64, 74}, {24, 74}, {24, 76.2}, {43.6, 76.2}}, color = {0, 0, 127}));
  connect(reference1.acceleration_command, vehicle1.acceleration_reference) annotation(Line(points = {{-64, 66.8}, {18, 66.8}, {18, 65.2}, {43.6, 65.2}}, color = {0, 0, 127}));
  connect(reference2.position_command, vehicle2.position_reference) annotation(Line(points = {{-64, 11.2}, {18, 11.2}, {18, 17.2}, {43.6, 17.2}}, color = {0, 0, 127}));
  connect(reference2.velocity_command, vehicle2.velocity_reference) annotation(Line(points = {{-64, 4}, {24, 4}, {24, 6.2}, {43.6, 6.2}}, color = {0, 0, 127}));
  connect(reference2.acceleration_command, vehicle2.acceleration_reference) annotation(Line(points = {{-64, -3.2}, {18, -3.2}, {18, -4.8}, {43.6, -4.8}}, color = {0, 0, 127}));
  connect(reference3.position_command, vehicle3.position_reference) annotation(Line(points = {{-64, -58.8}, {18, -58.8}, {18, -52.8}, {43.6, -52.8}}, color = {0, 0, 127}));
  connect(reference3.velocity_command, vehicle3.velocity_reference) annotation(Line(points = {{-64, -66}, {24, -66}, {24, -63.8}, {43.6, -63.8}}, color = {0, 0, 127}));
  connect(reference3.acceleration_command, vehicle3.acceleration_reference) annotation(Line(points = {{-64, -73.2}, {18, -73.2}, {18, -74.8}, {43.6, -74.8}}, color = {0, 0, 127}));
  connect(vehicle1.position, navigationDisplay.actual_position) annotation(Line(points = {{96.4, 87.2}, {108, 87.2}, {108, 104}, {-34, 104}, {-34, 78.6}, {-26.4, 78.6}}, color = {0, 0, 127}));
  connect(reference1.position_command, navigationDisplay.reference_position) annotation(Line(points = {{-64, 81.2}, {-48, 81.2}, {-48, 65.4}, {-26.4, 65.4}}, color = {0, 0, 127}));

  pair_distance_12_m = sqrt(sum((vehicle1.position[i] - vehicle2.position[i]) ^ 2 for i in 1:3));
  pair_distance_13_m = sqrt(sum((vehicle1.position[i] - vehicle3.position[i]) ^ 2 for i in 1:3));
  pair_distance_23_m = sqrt(sum((vehicle2.position[i] - vehicle3.position[i]) ^ 2 for i in 1:3));
  min_inter_uav_distance_m = min(pair_distance_12_m, min(pair_distance_13_m, pair_distance_23_m));
  reference_pair_distance_12_m = sqrt(sum((reference1.position_command[i] - reference2.position_command[i]) ^ 2 for i in 1:3));
  reference_pair_distance_13_m = sqrt(sum((reference1.position_command[i] - reference3.position_command[i]) ^ 2 for i in 1:3));
  reference_pair_distance_23_m = sqrt(sum((reference2.position_command[i] - reference3.position_command[i]) ^ 2 for i in 1:3));
  formation_distance_error_m = (abs(pair_distance_12_m - reference_pair_distance_12_m) + abs(pair_distance_13_m - reference_pair_distance_13_m) + abs(pair_distance_23_m - reference_pair_distance_23_m)) / 3;

  annotation(experiment(Algorithm = Dassl, StartTime = 0, StopTime = 300, Tolerance = 0.0001, Interval = 0.05));
  annotation(__MWORKS(hide=false));
end ThreeUavOpenBlocksReconfigurableFormationPx4CtrlDynamic;
