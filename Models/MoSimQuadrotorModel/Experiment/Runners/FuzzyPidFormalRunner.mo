within MoSimQuadrotorModel.Experiment.Runners;
model FuzzyPidFormalRunner
  "Formal 100 Hz whole-aircraft runner for FuzzyPidAttitudeThrustAdapter"

  extends MoSimQuadrotorModel.Experiment.Runners.FormalAttitudeThrustRunnerBase(
    redeclare model Controller = MoSimQuadrotorModel.Control.Adapters.FuzzyPidAttitudeThrustAdapter);
end FuzzyPidFormalRunner;
