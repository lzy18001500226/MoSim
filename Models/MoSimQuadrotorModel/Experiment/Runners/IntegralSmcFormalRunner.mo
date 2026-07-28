within MoSimQuadrotorModel.Experiment.Runners;
model IntegralSmcFormalRunner
  "Formal 100 Hz whole-aircraft runner for IntegralSmcAttitudeThrustAdapter"

  extends MoSimQuadrotorModel.Experiment.Runners.FormalAttitudeThrustRunnerBase(
    redeclare model Controller = MoSimQuadrotorModel.Control.Adapters.IntegralSmcAttitudeThrustAdapter);
end IntegralSmcFormalRunner;
