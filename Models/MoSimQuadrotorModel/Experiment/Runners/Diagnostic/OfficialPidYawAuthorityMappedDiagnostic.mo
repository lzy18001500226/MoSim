within MoSimQuadrotorModel.Experiment.Runners.Diagnostic;
model OfficialPidYawAuthorityMappedDiagnostic
  "Diagnostic only: Official PID yaw allocation mapped to the shared physical reaction torque"

  extends MoSimQuadrotorModel.Experiment.Runners.RotorCommandRunner(
    redeclare model Controller =
      MoSimQuadrotorModel.Control.Adapters.OfficialPIDYawAuthorityMappedRotorAdapter);

  annotation(__MWORKS(version="26.3.0"));
end OfficialPidYawAuthorityMappedDiagnostic;
