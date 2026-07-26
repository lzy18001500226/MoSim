within MoSimQuadrotorModel.Experiment.Runners;
model OfficialPidReactionTorqueProfileSignDiagnostic
  "Official PID diagnostic using the profile yaw-reaction sign without changing any controller parameter"

  parameter MoSimQuadrotorModel.Parameters.Sunray150VirtualPx4Classic profile;
  extends MoSimQuadrotorModel.Experiment.Runners.OfficialPidFormalRunner(
    plant(
      profile = profile,
      yaw_reaction_direction = profile.mworks_yaw_direction));

  annotation(__MWORKS(version="26.3.0"));
end OfficialPidReactionTorqueProfileSignDiagnostic;
