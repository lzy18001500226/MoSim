within MoSimQuadrotorModel.Experiment.Runners.Formal;
model L1FormalRunner
  "Formal 100 Hz whole-aircraft runner for L1RotorAdapter"

  extends MoSimQuadrotorModel.Experiment.Runners.Base.FormalRotorCommandRunnerBase(
    redeclare model Controller = MoSimQuadrotorModel.Control.Adapters.L1RotorAdapter);
end L1FormalRunner;
