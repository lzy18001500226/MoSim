within MoSimQuadrotorModel.Experiment.Runners;
model FaultCompensationFormalRunner
  "Formal 100 Hz whole-aircraft runner for FaultCompensationRotorAdapter"

  extends MoSimQuadrotorModel.Experiment.Runners.FormalRotorCommandRunnerBase(
    redeclare model Controller = MoSimQuadrotorModel.Control.Adapters.FaultCompensationRotorAdapter);
end FaultCompensationFormalRunner;
