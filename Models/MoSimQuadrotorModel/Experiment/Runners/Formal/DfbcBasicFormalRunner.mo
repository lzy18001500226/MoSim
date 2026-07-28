within MoSimQuadrotorModel.Experiment.Runners.Formal;
model DfbcBasicFormalRunner
  "Formal 100 Hz whole-aircraft runner for DfbcBasicAttitudeThrustAdapter"

  extends MoSimQuadrotorModel.Experiment.Runners.Base.FormalAttitudeThrustRunnerBase(
    redeclare model Controller = MoSimQuadrotorModel.Control.Adapters.DfbcBasicAttitudeThrustAdapter);
end DfbcBasicFormalRunner;
