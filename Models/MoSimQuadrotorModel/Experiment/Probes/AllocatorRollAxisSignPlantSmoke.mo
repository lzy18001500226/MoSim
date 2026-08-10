within MoSimQuadrotorModel.Experiment.Probes;
model AllocatorRollAxisSignPlantSmoke
  "Positive roll reference response of the shared allocator and plant"

  parameter Real roll_reference_rad = 0.08
    "Positive command used only to identify the plant roll-axis sign";

  MoSimQuadrotorModel.Control.Allocation.OfflineAttitudeRateAllocator allocator 
    annotation(Placement(transformation(extent={{-66,-20},{-26,20}})));
  MoSimQuadrotorModel.Vehicle.Sunray150Assembly plant 
    annotation(Placement(transformation(extent={{26,-20},{66,20}})));
  Real position[3];
  Real attitude[3];
  Real rotor_command[4];

equation
  allocator.attitude_ref = {roll_reference_rad, 0.0, 0.0};
  allocator.attitude_mea = {0.0, 0.0, 0.0};
  allocator.collective_thrust_delta = 0.0;
  connect(allocator.rotor_command, plant.rotor_command) 
    annotation(Line(points={{-26,0},{26,0}}, color={0,0,127}));
  position = plant.position;
  attitude = plant.attitude;
  rotor_command = allocator.rotor_command;

  annotation(
    experiment(Algorithm=Dassl, StartTime=0, StopTime=0.2, Tolerance=0.0001,
      Interval=0.01),
    __MWORKS(version="26.3.0"));
end AllocatorRollAxisSignPlantSmoke;