within MoSimQuadrotorModel.Experiment.Runners;
model OfficialPidFormalRunner
  "Formal whole-aircraft A/B baseline with native continuous Official PID closure"

  extends MoSimQuadrotorModel.Experiment.Runners.RotorCommandRunner(
    redeclare model Controller =
      MoSimQuadrotorModel.Control.Adapters.OfficialPIDRotorAdapter);

  annotation(
    experiment(Algorithm = Dassl, StartTime = 0, StopTime = 50, Tolerance = 0.0001, Interval = 0.01),
    __MWORKS(version = "26.3.0"));
end OfficialPidFormalRunner;
