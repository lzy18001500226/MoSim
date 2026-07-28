within MoSimQuadrotorModel.Experiment.Runners;
model MppiFormalRunner
  "Formal 100 Hz whole-aircraft runner for MppiAttitudeThrustAdapter"

  extends MoSimQuadrotorModel.Experiment.Runners.FormalAttitudeThrustRunnerBase(
    redeclare model Controller = MoSimQuadrotorModel.Control.Adapters.MppiAttitudeThrustAdapter);
end MppiFormalRunner;
