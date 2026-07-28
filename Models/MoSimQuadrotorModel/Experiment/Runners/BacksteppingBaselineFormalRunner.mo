within MoSimQuadrotorModel.Experiment.Runners;
model BacksteppingBaselineFormalRunner
  "Formal 100 Hz whole-aircraft runner for BacksteppingBaselineAttitudeThrustAdapter"

  extends MoSimQuadrotorModel.Experiment.Runners.FormalAttitudeThrustRunnerBase(
    redeclare model Controller = MoSimQuadrotorModel.Control.Adapters.BacksteppingBaselineAttitudeThrustAdapter);
end BacksteppingBaselineFormalRunner;
