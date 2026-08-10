within MoSimQuadrotorModel.Experiment.Runners.Formal;
model IndiFormalRunner
  "Formal 100 Hz whole-aircraft runner for INDIRotorAdapter"

  extends MoSimQuadrotorModel.Experiment.Runners.Base.FormalRotorCommandRunnerBase(
    redeclare model Controller = MoSimQuadrotorModel.Control.Adapters.INDIRotorAdapter);
end IndiFormalRunner;