within MoSimQuadrotorModel.Experiment.Runners.Formal;
model IlqrFormalRunner
  "Formal 100 Hz whole-aircraft runner for IlqrAttitudeThrustAdapter"

  extends MoSimQuadrotorModel.Experiment.Runners.Base.FormalAttitudeThrustRunnerBase(
    redeclare model Controller = MoSimQuadrotorModel.Control.Adapters.IlqrAttitudeThrustAdapter);
end IlqrFormalRunner;