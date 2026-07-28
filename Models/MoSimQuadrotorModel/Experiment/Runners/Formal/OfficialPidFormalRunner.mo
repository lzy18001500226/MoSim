within MoSimQuadrotorModel.Experiment.Runners.Formal;
model OfficialPidFormalRunner
  "Formal whole-aircraft A/B baseline for the Official PID"

  extends MoSimQuadrotorModel.Experiment.Runners.Base.FormalRotorCommandRunnerBase(
    redeclare model Controller =
      MoSimQuadrotorModel.Control.Adapters.OfficialPIDRotorAdapter);
end OfficialPidFormalRunner;
