within MoSimQuadrotorModel.Experiment.Runners.Formation;
model Px4CtrlThreeUavFigure8Runner
  "Nominal three-UAV PX4CTRL virtual-structure triangle figure-eight closure"

  parameter Real controller_sample_period_s(unit = "s") = 0.01
    "Sampled controller-input boundary required by each px4ctrl loop";
  parameter Real formation_slot_m[3, 3](each unit = "m") = {
    {0, 1.2, 0},
    {-1.0392304845, -0.6, 0},
    {1.0392304845, -0.6, 0}}
    "Fixed world-frame triangle slots; each plant starts in its own slot";

  MoSimQuadrotorModel.Guidance.Formation.TriangleFigure8Reference reference(
    slot_offset_m = formation_slot_m) 
    annotation(Placement(transformation(origin = {-220, 0}, extent = {{-28, -24}, {28, 24}})));

  MoSimQuadrotorModel.Control.Adapters.Px4CtrlAttitudeThrustAdapter controller_1 
    annotation(Placement(transformation(origin = {-100, 85}, extent = {{-38, -24}, {38, 24}})));
  MoSimQuadrotorModel.Control.Allocation.OfflineAttitudeRateAllocator allocator_1 
    annotation(Placement(transformation(origin = {45, 85}, extent = {{-45, -24}, {45, 24}})));
  MoSimQuadrotorModel.Vehicle.Sunray150Assembly plant_1(
    initial_position_m = {formation_slot_m[1, 1], formation_slot_m[1, 2], formation_slot_m[1, 3]}) 
    annotation(Placement(transformation(origin = {170, 85}, extent = {{-45, -52}, {45, 52}})));

  MoSimQuadrotorModel.Control.Adapters.Px4CtrlAttitudeThrustAdapter controller_2 
    annotation(Placement(transformation(origin = {-100, 0}, extent = {{-38, -24}, {38, 24}})));
  MoSimQuadrotorModel.Control.Allocation.OfflineAttitudeRateAllocator allocator_2 
    annotation(Placement(transformation(origin = {45, 0}, extent = {{-45, -24}, {45, 24}})));
  MoSimQuadrotorModel.Vehicle.Sunray150Assembly plant_2(
    initial_position_m = {formation_slot_m[2, 1], formation_slot_m[2, 2], formation_slot_m[2, 3]}) 
    annotation(Placement(transformation(origin = {170, 0}, extent = {{-45, -52}, {45, 52}})));

  MoSimQuadrotorModel.Control.Adapters.Px4CtrlAttitudeThrustAdapter controller_3 
    annotation(Placement(transformation(origin = {-100, -85}, extent = {{-38, -24}, {38, 24}})));
  MoSimQuadrotorModel.Control.Allocation.OfflineAttitudeRateAllocator allocator_3 
    annotation(Placement(transformation(origin = {45, -85}, extent = {{-45, -24}, {45, 24}})));
  MoSimQuadrotorModel.Vehicle.Sunray150Assembly plant_3(
    initial_position_m = {formation_slot_m[3, 1], formation_slot_m[3, 2], formation_slot_m[3, 3]}) 
    annotation(Placement(transformation(origin = {170, -85}, extent = {{-45, -52}, {45, 52}})));

  Modelica.Blocks.Discrete.UnitDelay sampled_position_ref_1[3](
    each samplePeriod = controller_sample_period_s,
    y_start = {formation_slot_m[1, 1], formation_slot_m[1, 2], formation_slot_m[1, 3]});
  Modelica.Blocks.Discrete.UnitDelay sampled_velocity_ref_1[3](
    each samplePeriod = controller_sample_period_s, each y_start = 0);
  Modelica.Blocks.Discrete.UnitDelay sampled_acceleration_ref_1[3](
    each samplePeriod = controller_sample_period_s, each y_start = 0);
  Modelica.Blocks.Discrete.UnitDelay sampled_position_1[3](
    each samplePeriod = controller_sample_period_s,
    y_start = {formation_slot_m[1, 1], formation_slot_m[1, 2], formation_slot_m[1, 3]});
  Modelica.Blocks.Continuous.Derivative velocity_estimator_1[3](
    each k = 1, each T = 0.05,
    each initType = Modelica.Blocks.Types.Init.InitialOutput, each y_start = 0);
  Modelica.Blocks.Discrete.UnitDelay sampled_attitude_1[3](
    each samplePeriod = controller_sample_period_s, each y_start = 0);

  Modelica.Blocks.Discrete.UnitDelay sampled_position_ref_2[3](
    each samplePeriod = controller_sample_period_s,
    y_start = {formation_slot_m[2, 1], formation_slot_m[2, 2], formation_slot_m[2, 3]});
  Modelica.Blocks.Discrete.UnitDelay sampled_velocity_ref_2[3](
    each samplePeriod = controller_sample_period_s, each y_start = 0);
  Modelica.Blocks.Discrete.UnitDelay sampled_acceleration_ref_2[3](
    each samplePeriod = controller_sample_period_s, each y_start = 0);
  Modelica.Blocks.Discrete.UnitDelay sampled_position_2[3](
    each samplePeriod = controller_sample_period_s,
    y_start = {formation_slot_m[2, 1], formation_slot_m[2, 2], formation_slot_m[2, 3]});
  Modelica.Blocks.Continuous.Derivative velocity_estimator_2[3](
    each k = 1, each T = 0.05,
    each initType = Modelica.Blocks.Types.Init.InitialOutput, each y_start = 0);
  Modelica.Blocks.Discrete.UnitDelay sampled_attitude_2[3](
    each samplePeriod = controller_sample_period_s, each y_start = 0);

  Modelica.Blocks.Discrete.UnitDelay sampled_position_ref_3[3](
    each samplePeriod = controller_sample_period_s,
    y_start = {formation_slot_m[3, 1], formation_slot_m[3, 2], formation_slot_m[3, 3]});
  Modelica.Blocks.Discrete.UnitDelay sampled_velocity_ref_3[3](
    each samplePeriod = controller_sample_period_s, each y_start = 0);
  Modelica.Blocks.Discrete.UnitDelay sampled_acceleration_ref_3[3](
    each samplePeriod = controller_sample_period_s, each y_start = 0);
  Modelica.Blocks.Discrete.UnitDelay sampled_position_3[3](
    each samplePeriod = controller_sample_period_s,
    y_start = {formation_slot_m[3, 1], formation_slot_m[3, 2], formation_slot_m[3, 3]});
  Modelica.Blocks.Continuous.Derivative velocity_estimator_3[3](
    each k = 1, each T = 0.05,
    each initType = Modelica.Blocks.Types.Init.InitialOutput, each y_start = 0);
  Modelica.Blocks.Discrete.UnitDelay sampled_attitude_3[3](
    each samplePeriod = controller_sample_period_s, each y_start = 0);

  Real position_ref_1[3](each unit = "m");
  Real position_1[3](each unit = "m");
  Real position_ref_2[3](each unit = "m");
  Real position_2[3](each unit = "m");
  Real position_ref_3[3](each unit = "m");
  Real position_3[3](each unit = "m");
  Real position_error_norm_1(unit = "m");
  Real position_error_norm_2(unit = "m");
  Real position_error_norm_3(unit = "m");
  Real formation_error_2_m(unit = "m");
  Real formation_error_3_m(unit = "m");
  Real formation_error_m(unit = "m");
  Real inter_uav_distance_12_m(unit = "m");
  Real inter_uav_distance_13_m(unit = "m");
  Real inter_uav_distance_23_m(unit = "m");
  Real min_inter_uav_distance_m(unit = "m");

equation
  connect(reference.uav1_position_command, sampled_position_ref_1.u);
  connect(sampled_position_ref_1.y, controller_1.position_ref);
  connect(reference.uav1_velocity_command, sampled_velocity_ref_1.u);
  connect(sampled_velocity_ref_1.y, controller_1.velocity_ref);
  connect(reference.uav1_acceleration_command, sampled_acceleration_ref_1.u);
  connect(sampled_acceleration_ref_1.y, controller_1.acceleration_ref);
  connect(plant_1.position, sampled_position_1.u);
  connect(sampled_position_1.y, controller_1.position_mea);
  connect(sampled_position_1.y, velocity_estimator_1.u);
  connect(velocity_estimator_1.y, controller_1.velocity_mea);
  connect(plant_1.attitude, sampled_attitude_1.u);
  connect(sampled_attitude_1.y, controller_1.attitude_mea);
  connect(controller_1.attitude_ref, allocator_1.attitude_ref);
  connect(plant_1.attitude, allocator_1.attitude_mea);
  connect(controller_1.collective_thrust_delta, allocator_1.collective_thrust_delta);
  connect(allocator_1.rotor_command, plant_1.rotor_command);

  connect(reference.uav2_position_command, sampled_position_ref_2.u);
  connect(sampled_position_ref_2.y, controller_2.position_ref);
  connect(reference.uav2_velocity_command, sampled_velocity_ref_2.u);
  connect(sampled_velocity_ref_2.y, controller_2.velocity_ref);
  connect(reference.uav2_acceleration_command, sampled_acceleration_ref_2.u);
  connect(sampled_acceleration_ref_2.y, controller_2.acceleration_ref);
  connect(plant_2.position, sampled_position_2.u);
  connect(sampled_position_2.y, controller_2.position_mea);
  connect(sampled_position_2.y, velocity_estimator_2.u);
  connect(velocity_estimator_2.y, controller_2.velocity_mea);
  connect(plant_2.attitude, sampled_attitude_2.u);
  connect(sampled_attitude_2.y, controller_2.attitude_mea);
  connect(controller_2.attitude_ref, allocator_2.attitude_ref);
  connect(plant_2.attitude, allocator_2.attitude_mea);
  connect(controller_2.collective_thrust_delta, allocator_2.collective_thrust_delta);
  connect(allocator_2.rotor_command, plant_2.rotor_command);

  connect(reference.uav3_position_command, sampled_position_ref_3.u);
  connect(sampled_position_ref_3.y, controller_3.position_ref);
  connect(reference.uav3_velocity_command, sampled_velocity_ref_3.u);
  connect(sampled_velocity_ref_3.y, controller_3.velocity_ref);
  connect(reference.uav3_acceleration_command, sampled_acceleration_ref_3.u);
  connect(sampled_acceleration_ref_3.y, controller_3.acceleration_ref);
  connect(plant_3.position, sampled_position_3.u);
  connect(sampled_position_3.y, controller_3.position_mea);
  connect(sampled_position_3.y, velocity_estimator_3.u);
  connect(velocity_estimator_3.y, controller_3.velocity_mea);
  connect(plant_3.attitude, sampled_attitude_3.u);
  connect(sampled_attitude_3.y, controller_3.attitude_mea);
  connect(controller_3.attitude_ref, allocator_3.attitude_ref);
  connect(plant_3.attitude, allocator_3.attitude_mea);
  connect(controller_3.collective_thrust_delta, allocator_3.collective_thrust_delta);
  connect(allocator_3.rotor_command, plant_3.rotor_command);

  position_ref_1 = reference.uav1_position_command;
  position_1 = plant_1.position;
  position_ref_2 = reference.uav2_position_command;
  position_2 = plant_2.position;
  position_ref_3 = reference.uav3_position_command;
  position_3 = plant_3.position;
  position_error_norm_1 = sqrt((position_ref_1[1] - position_1[1]) ^ 2
    + (position_ref_1[2] - position_1[2]) ^ 2
    + (position_ref_1[3] - position_1[3]) ^ 2);
  position_error_norm_2 = sqrt((position_ref_2[1] - position_2[1]) ^ 2
    + (position_ref_2[2] - position_2[2]) ^ 2
    + (position_ref_2[3] - position_2[3]) ^ 2);
  position_error_norm_3 = sqrt((position_ref_3[1] - position_3[1]) ^ 2
    + (position_ref_3[2] - position_3[2]) ^ 2
    + (position_ref_3[3] - position_3[3]) ^ 2);
  formation_error_2_m = sqrt((position_2[1] - position_1[1]
    - (formation_slot_m[2, 1] - formation_slot_m[1, 1])) ^ 2
    + (position_2[2] - position_1[2]
    - (formation_slot_m[2, 2] - formation_slot_m[1, 2])) ^ 2
    + (position_2[3] - position_1[3]
    - (formation_slot_m[2, 3] - formation_slot_m[1, 3])) ^ 2);
  formation_error_3_m = sqrt((position_3[1] - position_1[1]
    - (formation_slot_m[3, 1] - formation_slot_m[1, 1])) ^ 2
    + (position_3[2] - position_1[2]
    - (formation_slot_m[3, 2] - formation_slot_m[1, 2])) ^ 2
    + (position_3[3] - position_1[3]
    - (formation_slot_m[3, 3] - formation_slot_m[1, 3])) ^ 2);
  formation_error_m = 0.5 * (formation_error_2_m + formation_error_3_m);
  inter_uav_distance_12_m = sqrt((position_2[1] - position_1[1]) ^ 2
    + (position_2[2] - position_1[2]) ^ 2 + (position_2[3] - position_1[3]) ^ 2);
  inter_uav_distance_13_m = sqrt((position_3[1] - position_1[1]) ^ 2
    + (position_3[2] - position_1[2]) ^ 2 + (position_3[3] - position_1[3]) ^ 2);
  inter_uav_distance_23_m = sqrt((position_3[1] - position_2[1]) ^ 2
    + (position_3[2] - position_2[2]) ^ 2 + (position_3[3] - position_2[3]) ^ 2);
  min_inter_uav_distance_m = min(inter_uav_distance_12_m,
    min(inter_uav_distance_13_m, inter_uav_distance_23_m));

  annotation(
    experiment(Algorithm = Dassl, StartTime = 0, StopTime = 50,
      Tolerance = 0.0001, Interval = 0.01),
    Diagram(coordinateSystem(extent = {{-260, -135}, {230, 135}}, grid = {2, 2})),
    __MWORKS(version = "26.3.0"));
end Px4CtrlThreeUavFigure8Runner;