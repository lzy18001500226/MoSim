within MoSimQuadrotorModel.Experiment.Runners.Formal;
model FuzzyPidFormalRunner
  "Formal 100 Hz whole-aircraft runner for FuzzyPidAttitudeThrustAdapter"

  extends MoSimQuadrotorModel.Experiment.Runners.Base.FormalAttitudeThrustRunnerBase(
    redeclare model Controller = MoSimQuadrotorModel.Control.Adapters.FuzzyPidAttitudeThrustAdapter);
end FuzzyPidFormalRunner;