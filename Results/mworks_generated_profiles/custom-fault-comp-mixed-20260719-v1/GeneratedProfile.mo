model MoSimGenerated_custom_fault_comp_mixed_20260719_v1
  "Generated thin offline profile wrapper; source remains in project packages"
  extends MoSimQuadrotorModel.ExperimentRunner.Runners.RotorCommandRunner(
    redeclare model Controller = MoSimQuadrotorModel.ExperimentRunner.Adapters.FaultCompensationRotorAdapter,
    rotor_effectiveness = {0.9, 1, 1, 1},
    gust_force = {0.4, 0, 0});
  annotation(experiment(Algorithm = Dassl, StartTime = 0, StopTime = 50, Tolerance = 0.0001, Interval = 0.01));
end MoSimGenerated_custom_fault_comp_mixed_20260719_v1;
