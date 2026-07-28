within MoSimQuadrotorModel.Experiment.Runners;
model FopidFormalRunner
  "Formal 100 Hz whole-aircraft runner for FopidAttitudeThrustAdapter"

  extends MoSimQuadrotorModel.Experiment.Runners.FormalAttitudeThrustRunnerBase(
    redeclare model Controller = MoSimQuadrotorModel.Control.Adapters.FopidAttitudeThrustAdapter);
end FopidFormalRunner;
