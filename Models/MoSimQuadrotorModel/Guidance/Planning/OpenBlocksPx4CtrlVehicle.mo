within MoSimQuadrotorModel.Guidance.Planning;
model OpenBlocksPx4CtrlVehicle
  "Reusable whole-aircraft PX4CTRL tracking vehicle for multi-UAV OpenBlocks experiments"

  parameter Real initial_position[3](each unit = "m") = {0, 0, 1.5};
  parameter Real controller_sample_period_s(unit = "s") = 0.01
    "Sampled controller-input boundary required by the px4ctrl loop";

  Modelica.Blocks.Interfaces.RealInput position_reference[3]
    annotation(Placement(transformation(origin = {-140, 65}, extent = {{-20, -20}, {20, 20}})));
  Modelica.Blocks.Interfaces.RealInput velocity_reference[3]
    annotation(Placement(transformation(origin = {-140, 10}, extent = {{-20, -20}, {20, 20}})));
  Modelica.Blocks.Interfaces.RealInput acceleration_reference[3]
    annotation(Placement(transformation(origin = {-140, -45}, extent = {{-20, -20}, {20, 20}})));
  Modelica.Blocks.Interfaces.RealOutput position[3]
    annotation(Placement(transformation(origin = {140, 65}, extent = {{-20, -20}, {20, 20}})));
  Modelica.Blocks.Interfaces.RealOutput tracking_error_m(unit = "m")
    annotation(Placement(transformation(origin = {140, 5}, extent = {{-20, -20}, {20, 20}})));

  MoSimQuadrotorModel.Control.Adapters.Px4CtrlAttitudeThrustAdapter controller
    annotation(Placement(transformation(origin = {-42, 56}, extent = {{-38, -24}, {38, 24}})));
  MoSimQuadrotorModel.Control.Allocation.OfflineAttitudeRateAllocator allocator
    annotation(Placement(transformation(origin = {55, 56}, extent = {{-38, -24}, {38, 24}})));
  MoSimQuadrotorModel.Vehicle.Sunray150Assembly plant(
    initial_position_m = initial_position)
    annotation(Placement(transformation(origin = {104, -45}, extent = {{-28, -42}, {28, 42}})));

  Modelica.Blocks.Discrete.UnitDelay sampled_position_ref[3](
    each samplePeriod = controller_sample_period_s, y_start = initial_position);
  Modelica.Blocks.Discrete.UnitDelay sampled_velocity_ref[3](
    each samplePeriod = controller_sample_period_s, each y_start = 0);
  Modelica.Blocks.Discrete.UnitDelay sampled_acceleration_ref[3](
    each samplePeriod = controller_sample_period_s, each y_start = 0);
  Modelica.Blocks.Discrete.UnitDelay sampled_position[3](
    each samplePeriod = controller_sample_period_s, y_start = initial_position);
  Modelica.Blocks.Continuous.Derivative velocity_estimator[3](
    each k = 1, each T = 0.05,
    each initType = Modelica.Blocks.Types.Init.InitialOutput, each y_start = 0);
  Modelica.Blocks.Discrete.UnitDelay sampled_attitude[3](
    each samplePeriod = controller_sample_period_s, each y_start = 0);

equation
  connect(position_reference, sampled_position_ref.u);
  connect(sampled_position_ref.y, controller.position_ref);
  connect(velocity_reference, sampled_velocity_ref.u);
  connect(sampled_velocity_ref.y, controller.velocity_ref);
  connect(acceleration_reference, sampled_acceleration_ref.u);
  connect(sampled_acceleration_ref.y, controller.acceleration_ref);
  connect(plant.position, sampled_position.u);
  connect(sampled_position.y, controller.position_mea);
  connect(sampled_position.y, velocity_estimator.u);
  connect(velocity_estimator.y, controller.velocity_mea);
  connect(plant.attitude, sampled_attitude.u);
  connect(sampled_attitude.y, controller.attitude_mea);
  connect(controller.attitude_ref, allocator.attitude_ref);
  connect(plant.attitude, allocator.attitude_mea);
  connect(controller.collective_thrust_delta, allocator.collective_thrust_delta);
  connect(allocator.rotor_command, plant.rotor_command);

  position = plant.position;
  tracking_error_m = sqrt(sum((position_reference[i] - plant.position[i]) ^ 2 for i in 1:3));

  annotation(
    Diagram(coordinateSystem(extent = {{-160, -110}, {160, 110}}, grid = {2, 2})),
    __MWORKS(hide=true,version="26.3.0"));
end OpenBlocksPx4CtrlVehicle;
