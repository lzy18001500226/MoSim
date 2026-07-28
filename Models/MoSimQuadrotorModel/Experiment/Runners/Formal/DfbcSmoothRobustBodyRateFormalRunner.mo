within MoSimQuadrotorModel.Experiment.Runners.Formal;
model DfbcSmoothRobustBodyRateFormalRunner
  "Formal 100 Hz whole-aircraft runner for DfbcSmoothRobustBodyRateAdapter"

  extends MoSimQuadrotorModel.Experiment.Runners.Base.FormalBodyRateThrustRunnerBase(
    redeclare model Controller = MoSimQuadrotorModel.Control.Adapters.DfbcSmoothRobustBodyRateAdapter);
end DfbcSmoothRobustBodyRateFormalRunner;
