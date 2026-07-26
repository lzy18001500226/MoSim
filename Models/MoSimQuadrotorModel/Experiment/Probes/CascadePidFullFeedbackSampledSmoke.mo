within MoSimQuadrotorModel.Experiment.Probes;
model CascadePidFullFeedbackSampledSmoke
  "Cascade-PID full feedback with one 100 Hz sample boundary at plant sensing"

  MoSimQuadrotorModel.Control.Adapters.CascadePidAttitudeThrustAdapter controller annotation(Placement(transformation(extent={{-63,6},{-33,46}})));
  MoSimQuadrotorModel.Control.Allocation.OfflineAttitudeRateAllocator allocator annotation(Placement(transformation(extent={{-15,-20},{15,20}})));
  MoSimQuadrotorModel.Vehicle.Sunray150Assembly plant annotation(Placement(transformation(extent={{33,-20},{63,20}})));
  Modelica.Blocks.Discrete.UnitDelay sampled_position[3](each samplePeriod = 0.01,
    each y_start = 0);
  Modelica.Blocks.Discrete.UnitDelay sampled_attitude[3](each samplePeriod = 0.01,
    each y_start = 0);
  Real position[3];
  Real attitude[3];
  Real rotor_command[4];
  Real status_code annotation(Placement(transformation(extent={{-63,-46},{-33,-6}})));

equation
  controller.position_ref = {0.0, 0.0, 0.0};
  connect(plant.position, sampled_position.u);
  connect(sampled_position.y, controller.position_mea);
  connect(plant.attitude, sampled_attitude.u);
  connect(sampled_attitude.y, controller.attitude_mea);
  connect(controller.attitude_ref, allocator.attitude_ref) annotation(Line(points={{-33,26},{-24,26},{-24,0},{-15,0}}, color={0,0,127}));
  connect(sampled_attitude.y, allocator.attitude_mea);
  connect(controller.collective_thrust_delta, allocator.collective_thrust_delta) annotation(Line(points={{-33,26},{-24,26},{-24,0},{-15,0}}, color={0,0,127}));
  connect(allocator.rotor_command, plant.rotor_command) annotation(Line(points={{15,0},{33,0}}, color={0,0,127}));
  position = plant.position;
  attitude = plant.attitude;
  rotor_command = allocator.rotor_command;
  status_code = controller.status_code;

  annotation(
    experiment(Algorithm = Dassl, StartTime = 0, StopTime = 0.2, Tolerance = 0.0001,
      Interval = 0.01),
    __MWORKS(version = "26.3.0"));
end CascadePidFullFeedbackSampledSmoke;
