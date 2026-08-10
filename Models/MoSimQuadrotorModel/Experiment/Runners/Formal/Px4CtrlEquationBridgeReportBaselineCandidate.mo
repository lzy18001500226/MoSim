within MoSimQuadrotorModel.Experiment.Runners.Formal;
model Px4CtrlEquationBridgeReportBaselineCandidate
  "Isolated report-compatible EquationBridge candidate for R1 verification"

  parameter Real controller_sample_period_s = 0.01;
  MoSimQuadrotorModel.Control.Adapters.Px4CtrlEquationBridgeReportBaselineAdapter controller annotation(Placement(transformation(extent={{-63,58},{-33,98}})));
  MoSimQuadrotorModel.Control.Allocation.OfflineAttitudeRateReportBaselineAllocator offline_inner_allocator annotation(Placement(transformation(extent={{-15,-20},{15,20}})));
  parameter Real gust_force[3](each unit = "N") = {0, 0, 0};
  parameter Real gust_start_s(unit = "s") = 0;
  parameter Real gust_duration_s(unit = "s") = 0;
  parameter Real mass_scale(min = 0.01) = 1;
  parameter Real inertia_scale[3](each min = 0.01) = {1, 1, 1};
  parameter Real rotor_effectiveness[4](each min = 0, each max = 1) = {1, 1, 1, 1};
  parameter Real fault_start_s(unit = "s") = 1e9;
  parameter Integer fault_rotor_index(min = 1, max = 4) = 1;
  parameter Real fault_rotor_effectiveness(min = 0, max = 1) = 1;
  MoSimQuadrotorModel.Vehicle.Sunray150EquationBridgeBaselineAssembly plant(
    rotor_effectiveness = rotor_effectiveness,
    gust_force = gust_force,
    gust_start_s = gust_start_s,
    gust_duration_s = gust_duration_s,
    mass_scale = mass_scale,
    inertia_scale = inertia_scale,
    fault_start_s = fault_start_s,
    fault_rotor_index = fault_rotor_index,
    fault_rotor_effectiveness = fault_rotor_effectiveness) annotation(Placement(transformation(extent={{33,-20},{63,20}})));
  replaceable model Trajectory = MoSimQuadrotorModel.Guidance.Trajectories.ClimbPath;
  Trajectory reference annotation(Placement(transformation(extent={{-63,-98},{-33,-58}})));
  Modelica.Blocks.Discrete.UnitDelay sampled_position_ref[3](each samplePeriod = controller_sample_period_s,
    each y_start = 0);
  Modelica.Blocks.Discrete.UnitDelay sampled_velocity_ref[3](each samplePeriod = controller_sample_period_s,
    each y_start = 0);
  Modelica.Blocks.Discrete.UnitDelay sampled_acceleration_ref[3](each samplePeriod = controller_sample_period_s,
    each y_start = 0);
  Modelica.Blocks.Discrete.UnitDelay sampled_position[3](each samplePeriod = controller_sample_period_s,
    each y_start = 0);
  Modelica.Blocks.Continuous.Derivative velocity_estimator[3](
    each k = 1,
    each T = 0.05,
    each initType = Modelica.Blocks.Types.Init.InitialOutput,
    each y_start = 0);
  Modelica.Blocks.Discrete.UnitDelay sampled_attitude[3](each samplePeriod = controller_sample_period_s,
    each y_start = 0);
  Real position_ref[3];
  Real position[3];
  Real attitude[3];
  Real rotor_command[4];
  Real position_error_norm annotation(Placement(transformation(extent={{-63,-46},{-33,-6}})));

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
  connect(controller.attitude_ref, offline_inner_allocator.attitude_ref) annotation(Line(points={{-33,78},{-24,78},{-24,0},{-15,0}}, color={0,0,127}));
  connect(plant.attitude, offline_inner_allocator.attitude_mea) annotation(Line(points={{63,0},{63,-128},{-15,-128},{-15,0}}, color={0,0,127}));
  connect(controller.collective_thrust_delta, offline_inner_allocator.collective_thrust_delta) annotation(Line(points={{-33,78},{-24,78},{-24,0},{-15,0}}, color={0,0,127}));
  connect(offline_inner_allocator.rotor_command, plant.rotor_command) annotation(Line(points={{15,0},{33,0}}, color={0,0,127}));
  position_ref = reference.position_command;
  position = plant.position;
  attitude = plant.attitude;
  rotor_command = plant.rotor_command;
  position_error_norm = sqrt((position_ref[1] - position[1]) ^ 2
    + (position_ref[2] - position[2]) ^ 2
    + (position_ref[3] - position[3]) ^ 2);

  annotation(
    experiment(Algorithm = Dassl, StartTime = 0, StopTime = 50, Tolerance = 0.0001, Interval = 0.01),
    __MWORKS(version = "26.3.0"));
end Px4CtrlEquationBridgeReportBaselineCandidate;