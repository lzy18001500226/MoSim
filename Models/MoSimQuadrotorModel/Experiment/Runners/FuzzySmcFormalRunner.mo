within MoSimQuadrotorModel.Experiment.Runners;
model FuzzySmcFormalRunner
  "Formal 100 Hz whole-aircraft runner for FuzzySmcAttitudeThrustAdapter"

  extends MoSimQuadrotorModel.Experiment.Runners.FormalAttitudeThrustRunnerBase(
    redeclare model Controller = MoSimQuadrotorModel.Control.Adapters.FuzzySmcAttitudeThrustAdapter);
end FuzzySmcFormalRunner;
