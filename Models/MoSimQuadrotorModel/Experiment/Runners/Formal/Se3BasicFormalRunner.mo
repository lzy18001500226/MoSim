within MoSimQuadrotorModel.Experiment.Runners.Formal;
model Se3BasicFormalRunner
  "Formal 100 Hz whole-aircraft runner for Se3BasicAttitudeThrustAdapter"

  extends MoSimQuadrotorModel.Experiment.Runners.Base.FormalAttitudeThrustRunnerBase(
    redeclare model Controller = MoSimQuadrotorModel.Control.Adapters.Se3BasicAttitudeThrustAdapter);
end Se3BasicFormalRunner;