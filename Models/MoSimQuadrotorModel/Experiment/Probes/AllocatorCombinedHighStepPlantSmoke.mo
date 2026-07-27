within MoSimQuadrotorModel.Experiment.Probes;
model AllocatorCombinedHighStepPlantSmoke
  "Cascade-PID command at the first observed negative-rotor boundary crossing"

  MoSimQuadrotorModel.Control.Allocation.OfflineAttitudeRateAllocator allocator;
  MoSimQuadrotorModel.Vehicle.Sunray150Assembly plant;
  Real position[3];
  Real attitude[3];
  Real rotor_command[4];

equation
  allocator.attitude_ref = {0.10045275426336601, 0.18870626209290053, 0.01890514640028707};
  allocator.attitude_mea = {0.0, 0.0, 0.0};
  // Preserve the historical 5.5579 rad/s collective step at the new N boundary.
  allocator.collective_thrust_delta = 5.557858380300746 * allocator.collective_thrust_slope;
  connect(allocator.rotor_command, plant.rotor_command);
  position = plant.position;
  attitude = plant.attitude;
  rotor_command = allocator.rotor_command;

  annotation(
    experiment(Algorithm = Dassl, StartTime = 0, StopTime = 0.2, Tolerance = 0.0001,
      Interval = 0.01),
    __MWORKS(version = "26.3.0"));
end AllocatorCombinedHighStepPlantSmoke;
