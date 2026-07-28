within MoSimQuadrotorModel.Experiment.Runners;
model DfbcSmoothRobustBodyRateFormalRunner
  "Formal 100 Hz whole-aircraft runner for DfbcSmoothRobustBodyRateAdapter"

  extends MoSimQuadrotorModel.Experiment.Runners.FormalBodyRateThrustRunnerBase(
    redeclare model Controller = MoSimQuadrotorModel.Control.Adapters.DfbcSmoothRobustBodyRateAdapter);
end DfbcSmoothRobustBodyRateFormalRunner;
