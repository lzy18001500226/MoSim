within MoSimQuadrotorModel.Experiment.Runners;
model OfficialPidFormalRunner
  "Formal whole-aircraft A/B baseline for the Official PID"

  extends FormalRotorCommandRunnerBase(
    redeclare model Controller =
      MoSimQuadrotorModel.Control.Adapters.OfficialPIDRotorAdapter);
end OfficialPidFormalRunner;
