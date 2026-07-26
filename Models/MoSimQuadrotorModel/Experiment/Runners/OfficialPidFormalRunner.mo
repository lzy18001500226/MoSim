within MoSimQuadrotorModel.Experiment.Runners;
model OfficialPidFormalRunner
  "Formal whole-aircraft A/B baseline for the embedded Plant Official PID"

  extends MoSimQuadrotorModel.Experiment.Runners.RotorCommandRunner(
    redeclare model Controller = MoSimQuadrotorModel.Control.Adapters.OfficialPIDRotorAdapter);

  annotation(__MWORKS(version="26.3.0"));
end OfficialPidFormalRunner;
