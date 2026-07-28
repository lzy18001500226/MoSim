within MoSimQuadrotorModel.Experiment.Runners;
model DfbcBasicFormalRunner
  "Formal 100 Hz whole-aircraft runner for DfbcBasicAttitudeThrustAdapter"

  extends MoSimQuadrotorModel.Experiment.Runners.FormalAttitudeThrustRunnerBase(
    redeclare model Controller = MoSimQuadrotorModel.Control.Adapters.DfbcBasicAttitudeThrustAdapter);
end DfbcBasicFormalRunner;
