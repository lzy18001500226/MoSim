within MoSimQuadrotorModel.Experiment.Runners.Formal;
model NdiFormalRunner
  "Formal 100 Hz whole-aircraft runner for NdiAttitudeThrustAdapter"

  extends MoSimQuadrotorModel.Experiment.Runners.Base.FormalAttitudeThrustRunnerBase(
    redeclare model Controller = MoSimQuadrotorModel.Control.Adapters.NdiAttitudeThrustAdapter);
end NdiFormalRunner;
