within MoSimQuadrotorModel.Experiment.Runners;
model AwffFormalRunner
  "Formal 100 Hz whole-aircraft runner for AWFFRotorAdapter"

  extends MoSimQuadrotorModel.Experiment.Runners.FormalRotorCommandRunnerBase(
    redeclare model Controller = MoSimQuadrotorModel.Control.Adapters.AWFFRotorAdapter);
end AwffFormalRunner;
