within MoSimQuadrotorModel.Experiment.Probes;
model CascadePidPlantActuationSmoke
  "Cascade-PID output-to-plant startup isolation with fixed controller inputs"

  MoSimQuadrotorModel.Control.Adapters.CascadePidAttitudeThrustAdapter controller;
  MoSimQuadrotorModel.Control.Allocation.OfflineAttitudeRateAllocator allocator;
  MoSimQuadrotorModel.Vehicle.Sunray150Assembly plant;
  Real position[3];
  Real attitude[3];
  Real rotor_command[4];
  Real status_code;

equation
  controller.position_ref = {1.0, -0.5, 0.8};
  controller.position_mea = {0.0, 0.0, 0.0};
  controller.velocity_mea = {0.0, 0.0, 0.0};
  controller.attitude_mea = {0.0, 0.0, 0.0};
  allocator.attitude_mea = {0.0, 0.0, 0.0};
  connect(controller.attitude_ref, allocator.attitude_ref);
  connect(controller.collective_thrust_delta, allocator.collective_thrust_delta);
  connect(allocator.rotor_command, plant.rotor_command);
  position = plant.position;
  attitude = plant.attitude;
  rotor_command = allocator.rotor_command;
  status_code = controller.status_code;

  annotation(
    experiment(Algorithm = Dassl, StartTime = 0, StopTime = 0.2, Tolerance = 0.0001,
      Interval = 0.01),
    __MWORKS(version = "26.3.0"));
end CascadePidPlantActuationSmoke;