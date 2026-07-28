within MoSimQuadrotorModel.Experiment.Runners;
model OfficialPidYawCorrectedFormalRunner
  "Formal 100 Hz whole-aircraft runner for OfficialPIDYawCorrectedRotorAdapter"

  extends MoSimQuadrotorModel.Experiment.Runners.FormalRotorCommandRunnerBase(
    redeclare model Controller = MoSimQuadrotorModel.Control.Adapters.OfficialPIDYawCorrectedRotorAdapter);
end OfficialPidYawCorrectedFormalRunner;
