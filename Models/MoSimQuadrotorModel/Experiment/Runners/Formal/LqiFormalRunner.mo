within MoSimQuadrotorModel.Experiment.Runners.Formal;
model LqiFormalRunner
  "Formal 100 Hz whole-aircraft runner for LqiAttitudeThrustAdapter"

  extends MoSimQuadrotorModel.Experiment.Runners.Base.FormalAttitudeThrustRunnerBase(
    redeclare model Controller = MoSimQuadrotorModel.Control.Adapters.LqiAttitudeThrustAdapter);
end LqiFormalRunner;