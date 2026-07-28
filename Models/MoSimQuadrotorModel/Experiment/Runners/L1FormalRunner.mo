within MoSimQuadrotorModel.Experiment.Runners;
model L1FormalRunner
  "Formal 100 Hz whole-aircraft runner for L1RotorAdapter"

  extends MoSimQuadrotorModel.Experiment.Runners.FormalRotorCommandRunnerBase(
    redeclare model Controller = MoSimQuadrotorModel.Control.Adapters.L1RotorAdapter);
end L1FormalRunner;
