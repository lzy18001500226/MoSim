within MoSimQuadrotorModel.Experiment.Runners.Formal;
model RobustMpcFormalRunner
  "Formal 100 Hz whole-aircraft runner for RobustMpcAttitudeThrustAdapter"

  extends MoSimQuadrotorModel.Experiment.Runners.Base.FormalAttitudeThrustRunnerBase(
    redeclare model Controller = MoSimQuadrotorModel.Control.Adapters.RobustMpcAttitudeThrustAdapter);
end RobustMpcFormalRunner;
