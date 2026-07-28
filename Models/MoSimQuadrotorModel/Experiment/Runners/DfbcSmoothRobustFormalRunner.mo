within MoSimQuadrotorModel.Experiment.Runners;
model DfbcSmoothRobustFormalRunner
  "Formal 100 Hz whole-aircraft runner for DfbcSmoothRobustAttitudeThrustAdapter"

  extends MoSimQuadrotorModel.Experiment.Runners.FormalAttitudeThrustRunnerBase(
    redeclare model Controller = MoSimQuadrotorModel.Control.Adapters.DfbcSmoothRobustAttitudeThrustAdapter);
end DfbcSmoothRobustFormalRunner;
