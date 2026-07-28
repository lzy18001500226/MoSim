within MoSimQuadrotorModel.Experiment.Runners.Formal;
model ImprovedPidFormalRunner
  "Formal 100 Hz whole-aircraft runner for ImprovedPIDRotorAdapter"

  extends MoSimQuadrotorModel.Experiment.Runners.Base.FormalRotorCommandRunnerBase(
    redeclare model Controller = MoSimQuadrotorModel.Control.Adapters.ImprovedPIDRotorAdapter);
end ImprovedPidFormalRunner;
