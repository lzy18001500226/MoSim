within MoSimQuadrotorModel.Experiment.Probes;
model CascadePidFullFeedbackZeroReferenceEulerSmoke
  "Euler counterpart of the full-feedback zero-reference cascade-PID isolation"

  MoSimQuadrotorModel.Control.Adapters.CascadePidAttitudeThrustAdapter controller annotation(Placement(transformation(extent={{-63,6},{-33,46}})));
  MoSimQuadrotorModel.Control.Allocation.OfflineAttitudeRateAllocator allocator annotation(Placement(transformation(extent={{-15,-20},{15,20}})));
  MoSimQuadrotorModel.Vehicle.Sunray150Assembly plant annotation(Placement(transformation(extent={{33,-20},{63,20}})));
  Modelica.Blocks.Continuous.Derivative velocity_estimator[3](
    each k = 1,
    each T = 0.05,
    each initType = Modelica.Blocks.Types.Init.InitialOutput,
    each y_start = 0);
  Real position[3];
  Real attitude[3];
  Real rotor_command[4];
  Real status_code annotation(Placement(transformation(extent={{-63,-46},{-33,-6}})));

equation
  controller.position_ref = {0.0, 0.0, 0.0};
  connect(plant.position, controller.position_mea) annotation(Line(points={{63,0},{63,-76},{-63,-76},{-63,26}}, color={0,0,127}));
  connect(plant.position, velocity_estimator.u);
  connect(velocity_estimator.y, controller.velocity_mea);
  connect(plant.attitude, controller.attitude_mea) annotation(Line(points={{63,0},{63,-76},{-63,-76},{-63,26}}, color={0,0,127}));
  connect(controller.attitude_ref, allocator.attitude_ref) annotation(Line(points={{-33,26},{-24,26},{-24,0},{-15,0}}, color={0,0,127}));
  connect(plant.attitude, allocator.attitude_mea) annotation(Line(points={{63,0},{63,-76},{-15,-76},{-15,0}}, color={0,0,127}));
  connect(controller.collective_thrust_delta, allocator.collective_thrust_delta) annotation(Line(points={{-33,26},{-24,26},{-24,0},{-15,0}}, color={0,0,127}));
  connect(allocator.rotor_command, plant.rotor_command) annotation(Line(points={{15,0},{33,0}}, color={0,0,127}));
  position = plant.position;
  attitude = plant.attitude;
  rotor_command = allocator.rotor_command;
  status_code = controller.status_code;

  annotation(
    experiment(Algorithm = Euler, StartTime = 0, StopTime = 0.2, Tolerance = 0.0001,
      Interval = 0.01, IntegratorStep = 0.01),
    __MWORKS(version = "26.3.0"));
end CascadePidFullFeedbackZeroReferenceEulerSmoke;
