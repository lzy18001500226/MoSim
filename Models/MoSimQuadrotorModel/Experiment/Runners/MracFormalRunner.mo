within MoSimQuadrotorModel.Experiment.Runners;
model MracFormalRunner
  "Formal 100 Hz whole-aircraft runner for MracAttitudeThrustAdapter"

  extends MoSimQuadrotorModel.Experiment.Runners.FormalAttitudeThrustRunnerBase(
    redeclare model Controller = MoSimQuadrotorModel.Control.Adapters.MracAttitudeThrustAdapter);
end MracFormalRunner;
