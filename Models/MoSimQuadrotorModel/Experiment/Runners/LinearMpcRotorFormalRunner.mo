within MoSimQuadrotorModel.Experiment.Runners;
model LinearMpcRotorFormalRunner
  "Formal 100 Hz whole-aircraft runner for LinearMPCRotorAdapter"

  extends MoSimQuadrotorModel.Experiment.Runners.FormalRotorCommandRunnerBase(
    redeclare model Controller = MoSimQuadrotorModel.Control.Adapters.LinearMPCRotorAdapter);
end LinearMpcRotorFormalRunner;
