within MoSimQuadrotorModel.Experiment.Runners.Formal;
model DfbcSmoothRobustFormalRunner
  "Formal 100 Hz whole-aircraft runner for DfbcSmoothRobustAttitudeThrustAdapter"

  extends MoSimQuadrotorModel.Experiment.Runners.Base.FormalAttitudeThrustRunnerBase(
    redeclare model Controller = MoSimQuadrotorModel.Control.Adapters.DfbcSmoothRobustAttitudeThrustAdapter);
end DfbcSmoothRobustFormalRunner;
