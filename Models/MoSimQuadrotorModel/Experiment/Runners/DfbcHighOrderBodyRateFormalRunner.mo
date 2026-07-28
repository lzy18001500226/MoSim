within MoSimQuadrotorModel.Experiment.Runners;
model DfbcHighOrderBodyRateFormalRunner
  "Formal 100 Hz whole-aircraft runner for DfbcHighOrderBodyRateAdapter"

  extends MoSimQuadrotorModel.Experiment.Runners.FormalBodyRateThrustRunnerBase(
    redeclare model Controller = MoSimQuadrotorModel.Control.Adapters.DfbcHighOrderBodyRateAdapter);
end DfbcHighOrderBodyRateFormalRunner;
