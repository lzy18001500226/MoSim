within MoSimQuadrotorModel.Experiment.Runners.Formal;
model LinearMpcRotorFormalRunner
  "Formal 100 Hz whole-aircraft runner for LinearMPCRotorAdapter"

  extends MoSimQuadrotorModel.Experiment.Runners.Base.FormalRotorCommandRunnerBase(
    redeclare model Controller = MoSimQuadrotorModel.Control.Adapters.LinearMPCRotorAdapter);
end LinearMpcRotorFormalRunner;
