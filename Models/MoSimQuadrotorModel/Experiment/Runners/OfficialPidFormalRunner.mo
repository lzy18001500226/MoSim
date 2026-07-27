within MoSimQuadrotorModel.Experiment.Runners;
model OfficialPidFormalRunner
  "Formal whole-aircraft A/B baseline with an external 100 Hz hold harness"

  parameter Real controller_sample_period_s(unit = "s") = 0.01
    "Common external reference, measurement, and command hold period";
  parameter Real gust_force[3](each unit = "N") = {0, 0, 0};
  parameter Real gust_start_s(unit = "s") = 0;
  parameter Real gust_duration_s(unit = "s") = 0;
  parameter Real mass_scale(min = 0.01) = 1;
  parameter Real inertia_scale[3](each min = 0.01) = {1, 1, 1};
  parameter Real rotor_effectiveness[4](each min = 0, each max = 1) = {1, 1, 1, 1};
  parameter Real fault_start_s(unit = "s") = 1e9;
  parameter Integer fault_rotor_index(min = 1, max = 4) = 1;
  parameter Real fault_rotor_effectiveness(min = 0, max = 1) = 1;

  MoSimQuadrotorModel.Control.Adapters.OfficialPIDRotorAdapter controller
    annotation(Placement(transformation(origin = {-100, 50}, extent = {{-38, -28}, {38, 28}})));
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
  Modelica.Blocks.Discrete.UnitDelay sampled_position_ref[3](each samplePeriod = controller_sample_period_s,
    each y_start = 0)
    annotation(Placement(transformation(origin = {-150, 0}, extent = {{-18, -12}, {18, 12}})));
  Modelica.Blocks.Discrete.UnitDelay sampled_velocity_ref[3](each samplePeriod = controller_sample_period_s,
    each y_start = 0)
    annotation(Placement(transformation(origin = {-150, -35}, extent = {{-18, -12}, {18, 12}})));
  Modelica.Blocks.Discrete.UnitDelay sampled_acceleration_ref[3](each samplePeriod = controller_sample_period_s,
    each y_start = 0)
    annotation(Placement(transformation(origin = {-150, -70}, extent = {{-18, -12}, {18, 12}})));
  Modelica.Blocks.Discrete.UnitDelay sampled_position[3](each samplePeriod = controller_sample_period_s,
    each y_start = 0)
    annotation(Placement(transformation(origin = {-15, -35}, extent = {{-18, -12}, {18, 12}})));
  Modelica.Blocks.Continuous.Derivative velocity_estimator[3](
    each k = 1,
    each T = 0.05,
    each initType = Modelica.Blocks.Types.Init.InitialOutput,
    each y_start = 0)
    "Runner-owned filtered velocity from the held position boundary";
  Modelica.Blocks.Discrete.UnitDelay sampled_attitude[3](each samplePeriod = controller_sample_period_s,
    each y_start = 0)
    annotation(Placement(transformation(origin = {65, -55}, extent = {{-18, -12}, {18, 12}})));
  Modelica.Blocks.Discrete.UnitDelay sampled_rotor_command[4](each samplePeriod = controller_sample_period_s,
    each y_start = 0)
    annotation(Placement(transformation(origin = {55, 50}, extent = {{-20, -14}, {20, 14}})));
  Real position_ref[3];
  Real position[3];
  Real attitude[3];
  Real rotor_command[4];
  Real position_error_norm;

equation
  connect(reference.position_command, sampled_position_ref.u)
    annotation(Line(points = {{-185, 50}, {-170, 50}, {-170, 0}, {-168, 0}}, color = {0, 0, 127}));
  connect(sampled_position_ref.y, controller.position_ref)
    annotation(Line(points = {{-132, 0}, {-120, 0}, {-120, 50}, {-138, 50}}, color = {0, 0, 127}));
  connect(reference.velocity_command, sampled_velocity_ref.u)
    annotation(Line(points = {{-185, 45}, {-175, 45}, {-175, -35}, {-168, -35}}, color = {0, 0, 127}));
  connect(sampled_velocity_ref.y, controller.velocity_ref)
    annotation(Line(points = {{-132, -35}, {-125, -35}, {-125, 45}, {-138, 45}}, color = {0, 0, 127}));
  connect(reference.acceleration_command, sampled_acceleration_ref.u)
    annotation(Line(points = {{-185, 40}, {-180, 40}, {-180, -70}, {-168, -70}}, color = {0, 0, 127}));
  connect(sampled_acceleration_ref.y, controller.acceleration_ref)
    annotation(Line(points = {{-132, -70}, {-120, -70}, {-120, 35}, {-138, 35}}, color = {0, 0, 127}));
  connect(plant.position, sampled_position.u)
    annotation(Line(points = {{113, -20}, {95, -20}, {95, -35}, {3, -35}}, color = {0, 0, 127}));
  connect(sampled_position.y, controller.position_mea)
    annotation(Line(points = {{-33, -35}, {-55, -35}, {-55, 40}, {-138, 40}}, color = {0, 0, 127}));
  connect(sampled_position.y, velocity_estimator.u);
  connect(velocity_estimator.y, controller.velocity_mea);
  connect(plant.attitude, sampled_attitude.u)
    annotation(Line(points = {{113, -35}, {97, -35}, {97, -55}, {83, -55}}, color = {0, 0, 127}));
  connect(sampled_attitude.y, controller.attitude_mea)
    annotation(Line(points = {{47, -55}, {25, -55}, {25, 25}, {-138, 25}}, color = {0, 0, 127}));
  connect(controller.rotor_command, sampled_rotor_command.u)
    annotation(Line(points = {{-62, 50}, {35, 50}}, color = {0, 0, 127}));
  connect(sampled_rotor_command.y, plant.rotor_command)
    annotation(Line(points = {{75, 50}, {113, 50}}, color = {0, 0, 127}));
  position_ref = reference.position_command;
  position = plant.position;
  attitude = plant.attitude;
  rotor_command = sampled_rotor_command.y;
  position_error_norm = sqrt((position_ref[1] - position[1]) ^ 2
    + (position_ref[2] - position[2]) ^ 2
    + (position_ref[3] - position[3]) ^ 2);

  annotation(
    experiment(Algorithm = Dassl, StartTime = 0, StopTime = 50, Tolerance = 0.0001, Interval = 0.01),
    Diagram(coordinateSystem(extent = {{-250, -140}, {240, 140}}, grid = {2, 2})),
    __MWORKS(version = "26.3.0"));
end OfficialPidFormalRunner;
