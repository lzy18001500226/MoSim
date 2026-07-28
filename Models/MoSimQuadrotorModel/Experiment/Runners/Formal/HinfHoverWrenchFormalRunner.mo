within MoSimQuadrotorModel.Experiment.Runners.Formal;
model HinfHoverWrenchFormalRunner
  "Formal 100 Hz whole-aircraft runner for HinfHoverWrenchAdapter"

  extends MoSimQuadrotorModel.Experiment.Runners.Base.FormalWrenchRunnerBase(
    redeclare model Controller = MoSimQuadrotorModel.Control.Adapters.HinfHoverWrenchAdapter);
end HinfHoverWrenchFormalRunner;
