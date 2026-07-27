within MoSimQuadrotorModel.Experiment.Runners;
model WrenchRunner
  "Offline WRENCH runner using the MWORKS control allocator"

  replaceable model Controller = MoSimQuadrotorModel.Control.Baselines.OfflineWrenchController
    constrainedby MoSimQuadrotorModel.Control.Interfaces.PartialWrenchController;
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
    annotation(Placement(transformation(origin = {-75, 55}, extent = {{-38, -28}, {38, 28}})));
  MoSimQuadrotorModel.Control.Allocation.OfflineWrenchAllocator offline_allocator
    annotation(Placement(transformation(origin = {55, 55}, extent = {{-45, -28}, {45, 28}})));
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
    annotation(Placement(transformation(origin = {160, 0}, extent = {{-52, -75}, {52, 75}})));
  replaceable model Trajectory = MoSimQuadrotorModel.Guidance.Trajectories.ClimbPath;
  Trajectory reference
    annotation(Placement(transformation(origin = {-175, 55}, extent = {{-20, -15}, {20, 15}})));
  Modelica.Blocks.Continuous.Derivative velocity_estimator[3](
    each k = 1,
    each T = 0.05,
    each initType = Modelica.Blocks.Types.Init.InitialOutput,
    each y_start = 0)
    "Shared Runner-owned filtered position derivative";
  Real position_ref[3];
  Real position[3];
  Real attitude[3];
  Real rotor_command[4];
  Real position_error_norm;
equation
  connect(reference.position_command, controller.position_ref)
    annotation(Line(points = {{-155, 55}, {-113, 55}}, color = {0, 0, 127}));
  connect(reference.velocity_command, controller.velocity_ref);
  connect(reference.acceleration_command, controller.acceleration_ref);
  connect(plant.position, controller.position_mea)
    annotation(Line(points = {{108, -20}, {75, -20}, {75, -100}, {-135, -100}, {-135, 45}, {-113, 45}}, color = {0, 0, 127}));
  connect(plant.position, velocity_estimator.u);
  connect(velocity_estimator.y, controller.velocity_mea);
  connect(plant.attitude, controller.attitude_mea)
    annotation(Line(points = {{108, -35}, {60, -35}, {60, -120}, {-150, -120}, {-150, 30}, {-113, 30}}, color = {0, 0, 127}));
  connect(controller.body_force, offline_allocator.body_force)
    annotation(Line(points = {{-37, 70}, {10, 70}}, color = {0, 0, 127}));
  connect(controller.body_torque, offline_allocator.body_torque)
    annotation(Line(points = {{-37, 40}, {10, 40}}, color = {0, 0, 127}));
  connect(offline_allocator.rotor_command, plant.rotor_command)
    annotation(Line(points = {{100, 55}, {108, 55}}, color = {0, 0, 127}));
  position_ref = reference.position_command;
  position = plant.position;
  attitude = plant.attitude;
  rotor_command = plant.rotor_command;
  position_error_norm = sqrt((position_ref[1] - position[1]) ^ 2
    + (position_ref[2] - position[2]) ^ 2
    + (position_ref[3] - position[3]) ^ 2);
  annotation(
    experiment(Algorithm = Dassl, StartTime = 0, StopTime = 50, Tolerance = 0.0001, Interval = 0.01),
    Diagram(coordinateSystem(extent = {{-240, -140}, {240, 140}}, grid = {2, 2})),
    __MWORKS(version="26.3.0"));
end WrenchRunner;
