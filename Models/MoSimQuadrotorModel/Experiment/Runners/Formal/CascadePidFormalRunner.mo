within MoSimQuadrotorModel.Experiment.Runners.Formal;
model CascadePidFormalRunner
  "Formal whole-aircraft minimum-closure runner for the selected cascade PID"

  extends MoSimQuadrotorModel.Experiment.Runners.Base.FormalAttitudeThrustRunnerBase(
    redeclare model Controller =
      MoSimQuadrotorModel.Control.Adapters.CascadePidAttitudeThrustAdapter);
end CascadePidFormalRunner;
