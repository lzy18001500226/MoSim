within MoSimQuadrotorModel.Experiment.Runners.Formal;
model FuzzySmcFormalRunner
  "Formal 100 Hz whole-aircraft runner for FuzzySmcAttitudeThrustAdapter"

  extends MoSimQuadrotorModel.Experiment.Runners.Base.FormalAttitudeThrustRunnerBase(
    redeclare model Controller = MoSimQuadrotorModel.Control.Adapters.FuzzySmcAttitudeThrustAdapter);
end FuzzySmcFormalRunner;
