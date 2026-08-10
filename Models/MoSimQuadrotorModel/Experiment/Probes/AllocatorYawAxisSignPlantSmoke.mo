within MoSimQuadrotorModel.Experiment.Probes;
model AllocatorYawAxisSignPlantSmoke
  "Positive yaw reference response of the current shared allocator and plant"

  parameter Real yaw_reference_rad = 0.08
    "Positive command used only to identify the current yaw-axis sign";

  MoSimQuadrotorModel.Control.Allocation.OfflineAttitudeRateAllocator allocator;
  MoSimQuadrotorModel.Vehicle.Sunray150Assembly plant;
  Real position[3];
  Real attitude[3];
  Real rotor_command[4];
  Real rotor_speed[4];
  Real applied_reaction_yaw_moment(unit = "N.m");

equation
  allocator.attitude_ref = {0.0, 0.0, yaw_reference_rad};
  allocator.attitude_mea = {0.0, 0.0, 0.0};
  allocator.collective_thrust_delta = 0.0;
  connect(allocator.rotor_command, plant.rotor_command);

  position = plant.position;
  attitude = plant.attitude;
  rotor_command = plant.rotor_command;
  rotor_speed = plant.rotor_speed;
  applied_reaction_yaw_moment = plant.applied_reaction_yaw_moment;

  annotation(
    experiment(Algorithm = Dassl, StartTime = 0, StopTime = 0.02, Tolerance = 0.0001,
      Interval = 0.00001),
    __MWORKS(version = "26.3.0"));
end AllocatorYawAxisSignPlantSmoke;