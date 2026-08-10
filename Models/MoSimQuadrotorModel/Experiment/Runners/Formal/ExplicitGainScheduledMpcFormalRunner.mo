within MoSimQuadrotorModel.Experiment.Runners.Formal;
model ExplicitGainScheduledMpcFormalRunner
  "Formal 100 Hz whole-aircraft runner for ExplicitGainScheduledMpcAttitudeThrustAdapter"

  extends MoSimQuadrotorModel.Experiment.Runners.Base.FormalAttitudeThrustRunnerBase(
    redeclare model Controller = MoSimQuadrotorModel.Control.Adapters.ExplicitGainScheduledMpcAttitudeThrustAdapter);
end ExplicitGainScheduledMpcFormalRunner;