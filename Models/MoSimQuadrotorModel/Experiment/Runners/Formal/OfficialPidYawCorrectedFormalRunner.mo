within MoSimQuadrotorModel.Experiment.Runners.Formal;
model OfficialPidYawCorrectedFormalRunner
  "Formal 100 Hz whole-aircraft runner for OfficialPIDYawCorrectedRotorAdapter"

  extends MoSimQuadrotorModel.Experiment.Runners.Base.FormalRotorCommandRunnerBase(
    redeclare model Controller = MoSimQuadrotorModel.Control.Adapters.OfficialPIDYawCorrectedRotorAdapter);
end OfficialPidYawCorrectedFormalRunner;