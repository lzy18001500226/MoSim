within MoSimQuadrotorModel.Experiment.Runners;
model AdaptiveMpcFormalRunner
  "Formal 100 Hz whole-aircraft runner for AdaptiveMpcAttitudeThrustAdapter"

  extends MoSimQuadrotorModel.Experiment.Runners.FormalAttitudeThrustRunnerBase(
    redeclare model Controller = MoSimQuadrotorModel.Control.Adapters.AdaptiveMpcAttitudeThrustAdapter);
end AdaptiveMpcFormalRunner;
