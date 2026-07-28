within MoSimQuadrotorModel.Experiment.Runners;
model ExplicitGainScheduledMpcFormalRunner
  "Formal 100 Hz whole-aircraft runner for ExplicitGainScheduledMpcAttitudeThrustAdapter"

  extends MoSimQuadrotorModel.Experiment.Runners.FormalAttitudeThrustRunnerBase(
    redeclare model Controller = MoSimQuadrotorModel.Control.Adapters.ExplicitGainScheduledMpcAttitudeThrustAdapter);
end ExplicitGainScheduledMpcFormalRunner;
