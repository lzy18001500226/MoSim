within MoSimQuadrotorModel.Experiment.Runners;
model IndiFormalRunner
  "Formal 100 Hz whole-aircraft runner for INDIRotorAdapter"

  extends MoSimQuadrotorModel.Experiment.Runners.FormalRotorCommandRunnerBase(
    redeclare model Controller = MoSimQuadrotorModel.Control.Adapters.INDIRotorAdapter);
end IndiFormalRunner;
