within MoSimQuadrotorModel.Experiment.Runners;
model IlqrFormalRunner
  "Formal 100 Hz whole-aircraft runner for IlqrAttitudeThrustAdapter"

  extends MoSimQuadrotorModel.Experiment.Runners.FormalAttitudeThrustRunnerBase(
    redeclare model Controller = MoSimQuadrotorModel.Control.Adapters.IlqrAttitudeThrustAdapter);
end IlqrFormalRunner;
