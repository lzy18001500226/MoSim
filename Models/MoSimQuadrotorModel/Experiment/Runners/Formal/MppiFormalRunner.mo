within MoSimQuadrotorModel.Experiment.Runners.Formal;
model MppiFormalRunner
  "Formal 100 Hz whole-aircraft runner for MppiAttitudeThrustAdapter"

  extends MoSimQuadrotorModel.Experiment.Runners.Base.FormalAttitudeThrustRunnerBase(
    redeclare model Controller = MoSimQuadrotorModel.Control.Adapters.MppiAttitudeThrustAdapter);
end MppiFormalRunner;
