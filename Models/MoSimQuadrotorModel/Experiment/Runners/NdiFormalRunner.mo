within MoSimQuadrotorModel.Experiment.Runners;
model NdiFormalRunner
  "Formal 100 Hz whole-aircraft runner for NdiAttitudeThrustAdapter"

  extends MoSimQuadrotorModel.Experiment.Runners.FormalAttitudeThrustRunnerBase(
    redeclare model Controller = MoSimQuadrotorModel.Control.Adapters.NdiAttitudeThrustAdapter);
end NdiFormalRunner;
