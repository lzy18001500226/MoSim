within MoSimQuadrotorModel.Robustness.Scenarios.PIDBaselines;
model Example1Rotor3Loss15PID
  "Example1 baseline PID with rotor 3 lift efficiency reduced to 85%"
  extends QuadrotorModel.Examples.Example1(
    quadChassisTest17_1.gain4(k = 0.0007266293));
  annotation(experiment(Algorithm = Dassl, StartTime = 0, StopTime = 50, Tolerance = 0.0001, Interval = 0.01));
  annotation(__MWORKS(hide=true));
end Example1Rotor3Loss15PID;
