within MoSimQuadrotorModel.Experiment.Runners.Formal;
model OfficialPidFormalRunner
  "Formal whole-aircraft A/B baseline retaining the Official PID native continuous loop"

  extends MoSimQuadrotorModel.Experiment.Runners.RotorCommandRunner(
    redeclare model Controller =
      MoSimQuadrotorModel.Control.Adapters.OfficialPIDRotorAdapter);
end OfficialPidFormalRunner;
