within MoSimQuadrotorModel.Robustness.Scenarios.PIDBaselines;
model Example1Mass20PID
  "Example1 baseline PID with +20% central body mass perturbation"
  extends QuadrotorModel.Examples.Example1(
    quadChassisTest17_1.body(m = 1.2));
  annotation(experiment(Algorithm = Dassl, StartTime = 0, StopTime = 50, Tolerance = 0.0001, Interval = 0.01));
  annotation(__MWORKS(hide=true));
end Example1Mass20PID;
