within MoSimQuadrotorModel.Experiment.Probes;
model AllocatorAttitudeStepPlantSmoke
  "Representative cascade-PID attitude command into the plant"

  MoSimQuadrotorModel.Control.Allocation.OfflineAttitudeRateAllocator allocator;
  MoSimQuadrotorModel.Vehicle.Sunray150Assembly plant;
  Real position[3];
  Real attitude[3];
  Real rotor_command[4];

equation
  allocator.attitude_ref = {0.08891789913112476, 0.17254044638037574, 0.015305090431318504};
  allocator.attitude_mea = {0.0, 0.0, 0.0};
  allocator.collective_thrust_delta = 0.0;
  connect(allocator.rotor_command, plant.rotor_command);
  position = plant.position;
  attitude = plant.attitude;
  rotor_command = allocator.rotor_command;

  annotation(
    experiment(Algorithm = Dassl, StartTime = 0, StopTime = 0.2, Tolerance = 0.0001,
      Interval = 0.01),
    __MWORKS(version = "26.3.0"));
end AllocatorAttitudeStepPlantSmoke;