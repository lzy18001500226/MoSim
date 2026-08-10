within MoSimQuadrotorModel.Experiment.Probes;
model AllocatorFullFeedbackZeroReferenceSmoke
  "Zero-reference, full-feedback isolation of the shared attitude allocator and plant"

  MoSimQuadrotorModel.Control.Allocation.OfflineAttitudeRateAllocator allocator 
    annotation(Placement(transformation(origin = {-48, 0}, extent = {{-32, -26}, {32, 26}})));
  MoSimQuadrotorModel.Vehicle.Sunray150Assembly plant 
    annotation(Placement(transformation(origin = {70, 0}, extent = {{-42, -58}, {42, 58}})));
  Real position[3];
  Real attitude[3];
  Real rotor_command[4];

equation
  allocator.attitude_ref = {0.0, 0.0, 0.0};
  allocator.collective_thrust_delta = 0.0;
  connect(plant.attitude, allocator.attitude_mea) 
    annotation(Line(points = {{28, -18}, {8, -18}, {8, -34}, {-48, -34}, {-48, -26}}, color = {0, 0, 127}));
  connect(allocator.rotor_command, plant.rotor_command) 
    annotation(Line(points = {{-16, 0}, {28, 0}}, color = {0, 0, 127}));

  position = plant.position;
  attitude = plant.attitude;
  rotor_command = plant.rotor_command;

  annotation(
    experiment(Algorithm = Dassl, StartTime = 0, StopTime = 0.2, Tolerance = 0.0001,
      Interval = 0.01),
    Diagram(coordinateSystem(extent = {{-110, -85}, {125, 85}}, grid = {2, 2})),
    __MWORKS(version = "26.3.0"));
end AllocatorFullFeedbackZeroReferenceSmoke;