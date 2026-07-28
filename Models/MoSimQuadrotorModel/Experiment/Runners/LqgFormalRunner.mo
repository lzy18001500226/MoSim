within MoSimQuadrotorModel.Experiment.Runners;
model LqgFormalRunner
  "Formal 100 Hz whole-aircraft runner for LqgAttitudeThrustAdapter"

  extends MoSimQuadrotorModel.Experiment.Runners.FormalAttitudeThrustRunnerBase(
    redeclare model Controller = MoSimQuadrotorModel.Control.Adapters.LqgAttitudeThrustAdapter);
end LqgFormalRunner;
