within MoSimQuadrotorModel.Experiment.Runners;
model OfficialPidYawAuthorityMappedFormalRunner
  "Formal 100 Hz whole-aircraft runner for OfficialPIDYawAuthorityMappedRotorAdapter"

  extends MoSimQuadrotorModel.Experiment.Runners.FormalRotorCommandRunnerBase(
    redeclare model Controller = MoSimQuadrotorModel.Control.Adapters.OfficialPIDYawAuthorityMappedRotorAdapter);
end OfficialPidYawAuthorityMappedFormalRunner;
