within MoSimQuadrotorModel.Experiment.Runners.Diagnostic;
model OfficialPidReactionTorqueIsolatedDiagnostic
  "Official PID shared-assembly diagnostic with only aerodynamic yaw reaction torque isolated"

  extends MoSimQuadrotorModel.Experiment.Runners.Formal.OfficialPidFormalRunner(
    plant(reaction_moment_ratio = 0));

  annotation(__MWORKS(version="26.3.0"));
end OfficialPidReactionTorqueIsolatedDiagnostic;