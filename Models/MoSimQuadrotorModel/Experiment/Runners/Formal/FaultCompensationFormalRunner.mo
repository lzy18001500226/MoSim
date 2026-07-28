within MoSimQuadrotorModel.Experiment.Runners.Formal;
model FaultCompensationFormalRunner
  "Formal 100 Hz whole-aircraft runner for FaultCompensationRotorAdapter"

  extends MoSimQuadrotorModel.Experiment.Runners.Base.FormalRotorCommandRunnerBase(
    redeclare model Controller = MoSimQuadrotorModel.Control.Adapters.FaultCompensationRotorAdapter);
end FaultCompensationFormalRunner;
