within MoSimQuadrotorModel.Experiment.Probes;
model OfficialPidFullFeedbackZeroReferenceSmoke
  "Zero-reference full-feedback control using the official PID on the shared plant"

  MoSimQuadrotorModel.Control.Adapters.OfficialPIDRotorAdapter controller 
    annotation(Placement(transformation(origin = {-48, 0}, extent = {{-32, -26}, {32, 26}})));
  MoSimQuadrotorModel.Vehicle.Sunray150Assembly plant 
    annotation(Placement(transformation(origin = {70, 0}, extent = {{-42, -58}, {42, 58}})));
  Modelica.Blocks.Continuous.Derivative velocity_estimator[3](
    each k = 1,
    each T = 0.05,
    each initType = Modelica.Blocks.Types.Init.InitialOutput,
    each y_start = 0)
    "Probe-owned filtered velocity from plant position";
  Real position[3];
  Real attitude[3];
  Real rotor_command[4];
  Real rotor_speed[4];

equation
  controller.position_ref = {0.0, 0.0, 0.0};
  connect(plant.position, controller.position_mea) 
    annotation(Line(points = {{28, -18}, {8, -18}, {8, -34}, {-48, -34}, {-48, -26}}, color = {0, 0, 127}));
  connect(plant.position, velocity_estimator.u);
  connect(velocity_estimator.y, controller.velocity_mea);
  connect(plant.attitude, controller.attitude_mea) 
    annotation(Line(points = {{28, -18}, {8, -18}, {8, -34}, {-48, -34}, {-48, -26}}, color = {0, 0, 127}));
  connect(controller.rotor_command, plant.rotor_command) 
    annotation(Line(points = {{-16, 0}, {28, 0}}, color = {0, 0, 127}));

  position = plant.position;
  attitude = plant.attitude;
  rotor_command = plant.rotor_command;
  rotor_speed = plant.rotor_speed;

  annotation(
    experiment(Algorithm = Dassl, StartTime = 0, StopTime = 0.2, Tolerance = 0.0001,
      Interval = 0.01),
    Diagram(coordinateSystem(extent = {{-110, -85}, {125, 85}}, grid = {2, 2})),
    __MWORKS(version = "26.3.0"));
end OfficialPidFullFeedbackZeroReferenceSmoke;