within MoSimQuadrotorModel.Experiment.Runners;
model LqiFormalRunner
  "Formal 100 Hz whole-aircraft runner for LqiAttitudeThrustAdapter"

  extends MoSimQuadrotorModel.Experiment.Runners.FormalAttitudeThrustRunnerBase(
    redeclare model Controller = MoSimQuadrotorModel.Control.Adapters.LqiAttitudeThrustAdapter);
end LqiFormalRunner;
