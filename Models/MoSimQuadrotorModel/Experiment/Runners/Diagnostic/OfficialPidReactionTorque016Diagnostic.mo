within MoSimQuadrotorModel.Experiment.Runners.Diagnostic;
model OfficialPidReactionTorque016Diagnostic
  "Diagnostic only: Official PID with Cm=0.016 yaw reaction coefficient"

  extends MoSimQuadrotorModel.Experiment.Runners.Formal.OfficialPidFormalRunner(
    plant(reaction_moment_ratio = 0.016));

  annotation(__MWORKS(version="26.3.0"));
end OfficialPidReactionTorque016Diagnostic;