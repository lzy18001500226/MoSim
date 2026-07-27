within MoSimQuadrotorModel.Experiment.Probes;
model CascadePidAdapterSmoke
  "Fixed-input startup smoke for the current-root cascade PID adapter"

  MoSimQuadrotorModel.Control.Adapters.CascadePidAttitudeThrustAdapter controller;
  Real attitude_ref[3];
  Real collective_thrust_delta;
  Real status_code;

equation
  controller.position_ref = {1.0, -0.5, 0.8};
  controller.position_mea = {0.0, 0.0, 0.0};
  controller.velocity_mea = {0.0, 0.0, 0.0};
  controller.attitude_mea = {0.0, 0.0, 0.0};
  attitude_ref = controller.attitude_ref;
  collective_thrust_delta = controller.collective_thrust_delta;
  status_code = controller.status_code;

  annotation(
    experiment(Algorithm = Euler, StartTime = 0, StopTime = 0.2, Tolerance = 0.0001,
      Interval = 0.01, IntegratorStep = 0.01),
    __MWORKS(version = "26.3.0"));
end CascadePidAdapterSmoke;
