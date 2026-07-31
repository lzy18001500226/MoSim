within MoSimQuadrotorModel.Experiment.Runners.Formal;
model PidAwffLinearEsoFormalRunner
  "Formal 100 Hz whole-aircraft runner for PidAwffLinearEsoRotorAdapter"

  extends MoSimQuadrotorModel.Experiment.Runners.Base.FormalRotorCommandRunnerBase(
    redeclare model Controller =
      MoSimQuadrotorModel.Control.Adapters.PidAwffLinearEsoRotorAdapter);
end PidAwffLinearEsoFormalRunner;
