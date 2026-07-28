within MoSimQuadrotorModel.Experiment.Runners.Diagnostic;
model OfficialPidYawCorrectedDiagnostic
  "Diagnostic only: Official PID with corrected yaw translation and signed visual-speed limit"

  extends MoSimQuadrotorModel.Experiment.Runners.RotorCommandRunner(
    redeclare model Controller = MoSimQuadrotorModel.Control.Adapters.OfficialPIDYawCorrectedRotorAdapter);

  annotation(__MWORKS(version="26.3.0"));
end OfficialPidYawCorrectedDiagnostic;
