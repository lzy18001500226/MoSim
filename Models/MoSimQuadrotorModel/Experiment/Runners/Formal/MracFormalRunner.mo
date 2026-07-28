within MoSimQuadrotorModel.Experiment.Runners.Formal;
model MracFormalRunner
  "Formal 100 Hz whole-aircraft runner for MracAttitudeThrustAdapter"

  extends MoSimQuadrotorModel.Experiment.Runners.Base.FormalAttitudeThrustRunnerBase(
    redeclare model Controller = MoSimQuadrotorModel.Control.Adapters.MracAttitudeThrustAdapter);
end MracFormalRunner;
