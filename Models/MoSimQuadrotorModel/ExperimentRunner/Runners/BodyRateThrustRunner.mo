within MoSimQuadrotorModel.ExperimentRunner.Runners;
model BodyRateThrustRunner
  "Offline BODY_RATE_THRUST runner using the MWORKS rate loop and allocator"

  replaceable model Controller = MoSimQuadrotorModel.ExperimentRunner.Adapters.OfflineBodyRateThrustController
    constrainedby MoSimQuadrotorModel.ExperimentRunner.Interfaces.PartialBodyRateThrustController;
  Controller controller;
  MoSimQuadrotorModel.ExperimentRunner.Adapters.OfflineBodyRateAllocator offline_rate_allocator;
  MoSimQuadrotorModel.ExperimentRunner.Plant.SingleUavPlantAnimation plant;
  QuadrotorModel.PathPlanning.ClimbPath reference(gain(k = 1));
  Real position_ref[3];
  Real position[3];
  Real attitude[3];
  Real rotor_command[4];
  Real position_error_norm;
equation
  connect(reference.position_command, controller.position_ref);
  connect(plant.position, controller.position_mea);
  connect(plant.attitude, controller.attitude_mea);
  connect(controller.body_rate_ref, offline_rate_allocator.body_rate_ref);
  connect(controller.collective_thrust_delta, offline_rate_allocator.collective_thrust_delta);
  connect(offline_rate_allocator.rotor_command, plant.rotor_command);
  position_ref = reference.position_command;
  position = plant.position;
  attitude = plant.attitude;
  rotor_command = plant.rotor_command;
  position_error_norm = sqrt((position_ref[1] - position[1]) ^ 2
    + (position_ref[2] - position[2]) ^ 2
    + (position_ref[3] - position[3]) ^ 2);
  annotation(experiment(Algorithm = Dassl, StartTime = 0, StopTime = 50, Tolerance = 0.0001, Interval = 0.01));
end BodyRateThrustRunner;
