within MoSimQuadrotorModel.Experiment.Runners.Formal;
model AdaptiveMpcFormalRunner
  "Formal 100 Hz whole-aircraft runner for AdaptiveMpcAttitudeThrustAdapter"

  extends MoSimQuadrotorModel.Experiment.Runners.Base.FormalAttitudeThrustRunnerBase(
    redeclare model Controller = MoSimQuadrotorModel.Control.Adapters.AdaptiveMpcAttitudeThrustAdapter);
end AdaptiveMpcFormalRunner;
