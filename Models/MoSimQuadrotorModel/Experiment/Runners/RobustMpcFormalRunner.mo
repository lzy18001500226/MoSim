within MoSimQuadrotorModel.Experiment.Runners;
model RobustMpcFormalRunner
  "Formal 100 Hz whole-aircraft runner for RobustMpcAttitudeThrustAdapter"

  extends MoSimQuadrotorModel.Experiment.Runners.FormalAttitudeThrustRunnerBase(
    redeclare model Controller = MoSimQuadrotorModel.Control.Adapters.RobustMpcAttitudeThrustAdapter);
end RobustMpcFormalRunner;
