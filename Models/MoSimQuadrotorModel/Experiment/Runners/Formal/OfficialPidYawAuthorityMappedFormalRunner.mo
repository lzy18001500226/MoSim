within MoSimQuadrotorModel.Experiment.Runners.Formal;
model OfficialPidYawAuthorityMappedFormalRunner
  "Formal 100 Hz whole-aircraft runner for OfficialPIDYawAuthorityMappedRotorAdapter"

  extends MoSimQuadrotorModel.Experiment.Runners.Base.FormalRotorCommandRunnerBase(
    redeclare model Controller = MoSimQuadrotorModel.Control.Adapters.OfficialPIDYawAuthorityMappedRotorAdapter);
end OfficialPidYawAuthorityMappedFormalRunner;
