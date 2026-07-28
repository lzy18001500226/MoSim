within MoSimQuadrotorModel.Experiment.Runners.Formal;
model AwffFormalRunner
  "Formal 100 Hz whole-aircraft runner for AWFFRotorAdapter"

  extends MoSimQuadrotorModel.Experiment.Runners.Base.FormalRotorCommandRunnerBase(
    redeclare model Controller = MoSimQuadrotorModel.Control.Adapters.AWFFRotorAdapter);
end AwffFormalRunner;
