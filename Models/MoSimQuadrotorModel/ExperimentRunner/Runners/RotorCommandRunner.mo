within MoSimQuadrotorModel.ExperimentRunner.Runners;
model RotorCommandRunner
  "Offline ROTOR_COMMAND runner; controller output connects directly to the shared plant"

  replaceable model Controller = MoSimQuadrotorModel.ExperimentRunner.Adapters.OfficialPIDRotorAdapter
    constrainedby MoSimQuadrotorModel.ExperimentRunner.Interfaces.PartialRotorCommandController;
  parameter Real rotor_effectiveness[4] = {1, 1, 1, 1};
  parameter Real gust_force[3] = {0, 0, 0};
  Controller controller;
  MoSimQuadrotorModel.ExperimentRunner.Plant.SingleUavPlantAnimation plant(
    rotor_effectiveness = rotor_effectiveness,
    gust_force = gust_force);
  MoSimQuadrotorModel.Plant.PathPlanning.ClimbPath reference(gain(k = 1));
  Real position_ref[3];
  Real position[3];
  Real attitude[3];
  Real rotor_command[4];
  Real rotor_speed[4];
  Real position_error_norm;
equation
  connect(reference.position_command, controller.position_ref);
  connect(plant.position, controller.position_mea);
  connect(plant.attitude, controller.attitude_mea);
  connect(controller.rotor_command, plant.rotor_command);
  position_ref = reference.position_command;
  position = plant.position;
  attitude = plant.attitude;
  rotor_command = plant.rotor_command;
  rotor_speed = plant.rotor_speed;
  position_error_norm = sqrt((position_ref[1] - position[1]) ^ 2
    + (position_ref[2] - position[2]) ^ 2
    + (position_ref[3] - position[3]) ^ 2);
  annotation(experiment(Algorithm = Dassl, StartTime = 0, StopTime = 50, Tolerance = 0.0001, Interval = 0.01),__MWORKS(version="26.3.0"));
end RotorCommandRunner;