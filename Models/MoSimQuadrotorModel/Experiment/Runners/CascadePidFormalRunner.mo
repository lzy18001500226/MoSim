within MoSimQuadrotorModel.Experiment.Runners;
model CascadePidFormalRunner
  "Formal whole-aircraft minimum-closure runner for the selected cascade PID"

  extends FormalAttitudeThrustRunnerBase(
    redeclare model Controller =
      MoSimQuadrotorModel.Control.Adapters.CascadePidAttitudeThrustAdapter);
end CascadePidFormalRunner;
