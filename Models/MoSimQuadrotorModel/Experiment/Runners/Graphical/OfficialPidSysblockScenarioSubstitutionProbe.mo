within MoSimQuadrotorModel.Experiment.Runners.Graphical;
model OfficialPidSysblockScenarioSubstitutionProbe
  "Scenario substitution probe: replaceable trajectory, unchanged controller topology"

  extends OfficialPidSysblockSingleUavRunner(
    redeclare model Trajectory = MoSimQuadrotorModel.Guidance.Trajectories.StepResponse);

  annotation(
    experiment(Algorithm = Dassl, StartTime = 0, StopTime = 10,
      Tolerance = 0.0001, Interval = 0.01),
    __MWORKS(version = "26.3.0"));
end OfficialPidSysblockScenarioSubstitutionProbe;