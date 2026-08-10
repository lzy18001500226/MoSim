within MoSimQuadrotorModel.Experiment.Runners.Formal;
model AdaptiveBacksteppingFormalRunner
  "Formal 100 Hz whole-aircraft runner for AdaptiveBacksteppingAttitudeThrustAdapter"

  extends MoSimQuadrotorModel.Experiment.Runners.Base.FormalAttitudeThrustRunnerBase(
    redeclare model Controller = MoSimQuadrotorModel.Control.Adapters.AdaptiveBacksteppingAttitudeThrustAdapter);
end AdaptiveBacksteppingFormalRunner;