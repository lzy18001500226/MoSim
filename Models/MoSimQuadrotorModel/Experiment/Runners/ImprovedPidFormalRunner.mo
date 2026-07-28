within MoSimQuadrotorModel.Experiment.Runners;
model ImprovedPidFormalRunner
  "Formal 100 Hz whole-aircraft runner for ImprovedPIDRotorAdapter"

  extends MoSimQuadrotorModel.Experiment.Runners.FormalRotorCommandRunnerBase(
    redeclare model Controller = MoSimQuadrotorModel.Control.Adapters.ImprovedPIDRotorAdapter);
end ImprovedPidFormalRunner;
