within MoSimQuadrotorModel.Experiment.Runners;
model AdaptiveSmcFormalRunner
  "Formal 100 Hz whole-aircraft runner for AdaptiveSmcAttitudeThrustAdapter"

  extends MoSimQuadrotorModel.Experiment.Runners.FormalAttitudeThrustRunnerBase(
    redeclare model Controller = MoSimQuadrotorModel.Control.Adapters.AdaptiveSmcAttitudeThrustAdapter);
end AdaptiveSmcFormalRunner;
