within MoSimQuadrotorModel.Experiment.Runners.Diagnostic;
model OfficialPidReactionTorqueHalfCmDiagnostic
  "Diagnostic only: Official PID with Cm=0.03 yaw reaction coefficient"

  extends MoSimQuadrotorModel.Experiment.Runners.Formal.OfficialPidFormalRunner(
    plant(reaction_moment_ratio = 0.03));

  annotation(__MWORKS(version="26.3.0"));
end OfficialPidReactionTorqueHalfCmDiagnostic;
