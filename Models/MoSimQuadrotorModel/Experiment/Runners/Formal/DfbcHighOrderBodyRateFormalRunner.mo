within MoSimQuadrotorModel.Experiment.Runners.Formal;
model DfbcHighOrderBodyRateFormalRunner
  "Formal 100 Hz whole-aircraft runner for DfbcHighOrderBodyRateAdapter"

  extends MoSimQuadrotorModel.Experiment.Runners.Base.FormalBodyRateThrustRunnerBase(
    redeclare model Controller = MoSimQuadrotorModel.Control.Adapters.DfbcHighOrderBodyRateAdapter);
end DfbcHighOrderBodyRateFormalRunner;
