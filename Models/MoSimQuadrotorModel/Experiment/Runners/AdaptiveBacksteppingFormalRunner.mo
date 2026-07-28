within MoSimQuadrotorModel.Experiment.Runners;
model AdaptiveBacksteppingFormalRunner
  "Formal 100 Hz whole-aircraft runner for AdaptiveBacksteppingAttitudeThrustAdapter"

  extends MoSimQuadrotorModel.Experiment.Runners.FormalAttitudeThrustRunnerBase(
    redeclare model Controller = MoSimQuadrotorModel.Control.Adapters.AdaptiveBacksteppingAttitudeThrustAdapter);
end AdaptiveBacksteppingFormalRunner;
