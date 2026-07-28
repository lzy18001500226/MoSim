within MoSimQuadrotorModel.Experiment.Runners.Formal;
model AdaptiveSmcFormalRunner
  "Formal 100 Hz whole-aircraft runner for AdaptiveSmcAttitudeThrustAdapter"

  extends MoSimQuadrotorModel.Experiment.Runners.Base.FormalAttitudeThrustRunnerBase(
    redeclare model Controller = MoSimQuadrotorModel.Control.Adapters.AdaptiveSmcAttitudeThrustAdapter);
end AdaptiveSmcFormalRunner;
