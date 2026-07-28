within MoSimQuadrotorModel.Experiment.Runners.Formal;
model BacksteppingBaselineFormalRunner
  "Formal 100 Hz whole-aircraft runner for BacksteppingBaselineAttitudeThrustAdapter"

  extends MoSimQuadrotorModel.Experiment.Runners.Base.FormalAttitudeThrustRunnerBase(
    redeclare model Controller = MoSimQuadrotorModel.Control.Adapters.BacksteppingBaselineAttitudeThrustAdapter);
end BacksteppingBaselineFormalRunner;
