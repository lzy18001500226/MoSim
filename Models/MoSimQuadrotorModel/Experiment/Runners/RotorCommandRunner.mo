within MoSimQuadrotorModel.Experiment.Runners;
model RotorCommandRunner
  "Offline ROTOR_COMMAND runner; controller output connects directly to the shared plant"

  replaceable model Controller = MoSimQuadrotorModel.Control.Adapters.OfficialPIDRotorAdapter
    constrainedby MoSimQuadrotorModel.Control.Interfaces.PartialRotorCommandController;
  parameter Real rotor_effectiveness[4] = {1, 1, 1, 1};
  parameter Real gust_force[3] = {0, 0, 0};
  Controller controller
    annotation(Placement(transformation(origin = {-70, 55}, extent = {{-40, -28}, {40, 28}})));
  MoSimQuadrotorModel.Vehicle.Sunray150Assembly plant(
    rotor_effectiveness = rotor_effectiveness,
    gust_force = gust_force)
    annotation(Placement(transformation(origin = {150, 0}, extent = {{-52, -75}, {52, 75}})));
  MoSimQuadrotorModel.Guidance.Trajectories.ClimbPath reference(gain(k = 1))
    annotation(Placement(transformation(origin = {-175, 55}, extent = {{-20, -15}, {20, 15}})));
  Real position_ref[3];
  Real position[3];
  Real attitude[3];
  Real rotor_command[4];
  Real rotor_speed[4];
  Real position_error_norm;
equation
  connect(reference.position_command, controller.position_ref)
    annotation(Line(points = {{-155, 55}, {-110, 55}}, color = {0, 0, 127}));
  connect(plant.position, controller.position_mea)
    annotation(Line(points = {{98, -20}, {72, -20}, {72, -100}, {-125, -100}, {-125, 45}, {-110, 45}}, color = {0, 0, 127}));
  connect(plant.attitude, controller.attitude_mea)
    annotation(Line(points = {{98, -35}, {58, -35}, {58, -120}, {-140, -120}, {-140, 30}, {-110, 30}}, color = {0, 0, 127}));
  connect(controller.rotor_command, plant.rotor_command)
    annotation(Line(points = {{-30, 55}, {98, 55}}, color = {0, 0, 127}));
  position_ref = reference.position_command;
  position = plant.position;
  attitude = plant.attitude;
  rotor_command = plant.rotor_command;
  rotor_speed = plant.rotor_speed;
  position_error_norm = sqrt((position_ref[1] - position[1]) ^ 2
    + (position_ref[2] - position[2]) ^ 2
    + (position_ref[3] - position[3]) ^ 2);
  annotation(
    experiment(Algorithm = Dassl, StartTime = 0, StopTime = 50, Tolerance = 0.0001, Interval = 0.01),
    Diagram(coordinateSystem(extent = {{-240, -140}, {240, 140}}, grid = {2, 2})),
    __MWORKS(version="26.3.0"));
end RotorCommandRunner;
