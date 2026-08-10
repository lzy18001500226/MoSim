within MoSimQuadrotorModel.Experiment.Runners.Formal;
model Px4CtrlFormalRunner
  "Formal whole-aircraft EquationBridge baseline used by the report regression"

  extends Px4CtrlEquationBridgeFormalRunner;
  annotation(
    experiment(Algorithm = Dassl, StartTime = 0, StopTime = 50, Tolerance = 0.0001, Interval = 0.01),
    __MWORKS(version = "26.3.0"));
end Px4CtrlFormalRunner;