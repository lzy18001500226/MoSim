within MoSimQuadrotorModel.ExperimentRunner.Runners;
model AttitudeThrustRunner
  "Offline ATTITUDE_THRUST runner using the MWORKS inner loop and allocator"

  replaceable model Controller = MoSimQuadrotorModel.ExperimentRunner.Adapters.OfflineAttitudeThrustController
    constrainedby MoSimQuadrotorModel.ExperimentRunner.Interfaces.PartialAttitudeThrustController;
  Controller controller;
  MoSimQuadrotorModel.ExperimentRunner.Adapters.OfflineAttitudeRateAllocator offline_inner_allocator;
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
  connect(controller.attitude_ref, offline_inner_allocator.attitude_ref);
  connect(plant.attitude, offline_inner_allocator.attitude_mea);
  connect(controller.collective_thrust_delta, offline_inner_allocator.collective_thrust_delta);
  connect(offline_inner_allocator.rotor_command, plant.rotor_command);
  position_ref = reference.position_command;
  position = plant.position;
  attitude = plant.attitude;
  rotor_command = plant.rotor_command;
  position_error_norm = sqrt((position_ref[1] - position[1]) ^ 2
    + (position_ref[2] - position[2]) ^ 2
    + (position_ref[3] - position[3]) ^ 2);
  annotation(experiment(Algorithm = Dassl, StartTime = 0, StopTime = 50, Tolerance = 0.0001, Interval = 0.01));
end AttitudeThrustRunner;
