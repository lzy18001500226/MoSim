within MoSimQuadrotorModel.Experiment.Runners;
model HinfHoverWrenchFormalRunner
  "Formal 100 Hz whole-aircraft runner for HinfHoverWrenchAdapter"

  extends MoSimQuadrotorModel.Experiment.Runners.FormalWrenchRunnerBase(
    redeclare model Controller = MoSimQuadrotorModel.Control.Adapters.HinfHoverWrenchAdapter);
end HinfHoverWrenchFormalRunner;
