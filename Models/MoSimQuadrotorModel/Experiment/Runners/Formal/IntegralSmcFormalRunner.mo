within MoSimQuadrotorModel.Experiment.Runners.Formal;
model IntegralSmcFormalRunner
  "Formal 100 Hz whole-aircraft runner for IntegralSmcAttitudeThrustAdapter"

  extends MoSimQuadrotorModel.Experiment.Runners.Base.FormalAttitudeThrustRunnerBase(
    redeclare model Controller = MoSimQuadrotorModel.Control.Adapters.IntegralSmcAttitudeThrustAdapter);
end IntegralSmcFormalRunner;
