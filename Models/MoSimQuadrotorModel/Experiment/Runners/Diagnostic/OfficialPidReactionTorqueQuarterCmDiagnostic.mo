within MoSimQuadrotorModel.Experiment.Runners.Diagnostic;
model OfficialPidReactionTorqueQuarterCmDiagnostic
  "Diagnostic only: Official PID with Cm=0.015 yaw reaction coefficient"

  extends MoSimQuadrotorModel.Experiment.Runners.Formal.OfficialPidFormalRunner(
    plant(reaction_moment_ratio = 0.015));

  annotation(__MWORKS(version="26.3.0"));
end OfficialPidReactionTorqueQuarterCmDiagnostic;