within MoSimQuadrotorModel.Experiment.Runners;
model Se3BasicFormalRunner
  "Formal 100 Hz whole-aircraft runner for Se3BasicAttitudeThrustAdapter"

  extends MoSimQuadrotorModel.Experiment.Runners.FormalAttitudeThrustRunnerBase(
    redeclare model Controller = MoSimQuadrotorModel.Control.Adapters.Se3BasicAttitudeThrustAdapter);
end Se3BasicFormalRunner;
