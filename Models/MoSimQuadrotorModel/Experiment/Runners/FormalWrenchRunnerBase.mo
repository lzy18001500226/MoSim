within MoSimQuadrotorModel.Experiment.Runners;
model FormalWrenchRunnerBase
  "Reusable 100 Hz formal whole-aircraft runner for WRENCH adapters"

  replaceable model Controller =
      MoSimQuadrotorModel.Control.Adapters.HinfHoverWrenchAdapter
    constrainedby MoSimQuadrotorModel.Control.Interfaces.PartialWrenchController;
  parameter Real controller_sample_period_s(unit = "s") = 0.01
    "External reference and measurement hold period";
  parameter Real gust_force[3](each unit = "N") = {0, 0, 0};
  parameter Real gust_start_s(unit = "s") = 0;
  parameter Real gust_duration_s(unit = "s") = 0;
  parameter Real mass_scale(min = 0.01) = 1;
  parameter Real inertia_scale[3](each min = 0.01) = {1, 1, 1};
  parameter Real rotor_effectiveness[4](each min = 0, each max = 1) = {1, 1, 1, 1};
  parameter Real fault_start_s(unit = "s") = 1e9;
  parameter Integer fault_rotor_index(min = 1, max = 4) = 1;
  parameter Real fault_rotor_effectiveness(min = 0, max = 1) = 1;

  Controller controller
    annotation(Placement(transformation(origin = {-100, 50}, extent = {{-38, -28}, {38, 28}})));
  MoSimQuadrotorModel.Control.Allocation.OfflineWrenchAllocator offline_allocator
    annotation(Placement(transformation(origin = {55, 50}, extent = {{-45, -28}, {45, 28}})));
  MoSimQuadrotorModel.Vehicle.Sunray150Assembly plant(
    rotor_effectiveness = rotor_effectiveness,
    gust_force = gust_force,
    gust_start_s = gust_start_s,
    gust_duration_s = gust_duration_s,
    mass_scale = mass_scale,
    inertia_scale = inertia_scale,
    fault_start_s = fault_start_s,
    fault_rotor_index = fault_rotor_index,
    fault_rotor_effectiveness = fault_rotor_effectiveness)
    annotation(Placement(transformation(origin = {165, 0}, extent = {{-52, -75}, {52, 75}})));
  replaceable model Trajectory = MoSimQuadrotorModel.Guidance.Trajectories.ClimbPath;
  Trajectory reference
    annotation(Placement(transformation(origin = {-205, 50}, extent = {{-20, -15}, {20, 15}})));
  Modelica.Blocks.Discrete.UnitDelay sampled_position_ref[3](
    each samplePeriod = controller_sample_period_s,
    each y_start = 0)
    annotation(Placement(transformation(origin = {-150, 0}, extent = {{-18, -12}, {18, 12}})));
  Modelica.Blocks.Discrete.UnitDelay sampled_velocity_ref[3](
    each samplePeriod = controller_sample_period_s,
    each y_start = 0)
    annotation(Placement(transformation(origin = {-150, -35}, extent = {{-18, -12}, {18, 12}})));
  Modelica.Blocks.Discrete.UnitDelay sampled_acceleration_ref[3](
    each samplePeriod = controller_sample_period_s,
    each y_start = 0)
    annotation(Placement(transformation(origin = {-150, -70}, extent = {{-18, -12}, {18, 12}})));
  Modelica.Blocks.Discrete.UnitDelay sampled_position[3](
    each samplePeriod = controller_sample_period_s,
    each y_start = 0)
    annotation(Placement(transformation(origin = {-15, -35}, extent = {{-18, -12}, {18, 12}})));
  Modelica.Blocks.Continuous.Derivative velocity_estimator[3](
    each k = 1,
    each T = 0.05,
    each initType = Modelica.Blocks.Types.Init.InitialOutput,
    each y_start = 0)
    "Runner-owned filtered velocity from the sampled position boundary";
  Modelica.Blocks.Discrete.UnitDelay sampled_attitude[3](
    each samplePeriod = controller_sample_period_s,
    each y_start = 0)
    annotation(Placement(transformation(origin = {65, -55}, extent = {{-18, -12}, {18, 12}})));
  Real position_ref[3];
  Real position[3];
  Real attitude[3];
  Real rotor_command[4];
  Real position_error_norm;

equation
  connect(reference.position_command, sampled_position_ref.u);
  connect(sampled_position_ref.y, controller.position_ref);
  connect(reference.velocity_command, sampled_velocity_ref.u);
  connect(sampled_velocity_ref.y, controller.velocity_ref);
  connect(reference.acceleration_command, sampled_acceleration_ref.u);
  connect(sampled_acceleration_ref.y, controller.acceleration_ref);
  connect(plant.position, sampled_position.u);
  connect(sampled_position.y, controller.position_mea);
  connect(sampled_position.y, velocity_estimator.u);
  connect(velocity_estimator.y, controller.velocity_mea);
  connect(plant.attitude, sampled_attitude.u);
  connect(sampled_attitude.y, controller.attitude_mea);
  connect(controller.body_force, offline_allocator.body_force);
  connect(controller.body_torque, offline_allocator.body_torque);
  connect(offline_allocator.rotor_command, plant.rotor_command);
  position_ref = reference.position_command;
  position = plant.position;
  attitude = plant.attitude;
  rotor_command = plant.rotor_command;
  position_error_norm = sqrt((position_ref[1] - position[1]) ^ 2
    + (position_ref[2] - position[2]) ^ 2
    + (position_ref[3] - position[3]) ^ 2);

  annotation(
    experiment(Algorithm = Dassl, StartTime = 0, StopTime = 50, Tolerance = 0.0001, Interval = 0.01),
    Diagram(coordinateSystem(extent = {{-250, -140}, {240, 140}}, grid = {2, 2})),
    __MWORKS(version = "26.3.0"));
end FormalWrenchRunnerBase;
