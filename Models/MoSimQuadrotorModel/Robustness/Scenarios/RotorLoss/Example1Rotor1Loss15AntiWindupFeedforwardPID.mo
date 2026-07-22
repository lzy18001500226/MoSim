within MoSimQuadrotorModel.Robustness.Scenarios.RotorLoss;
model Example1Rotor1Loss15AntiWindupFeedforwardPID
  "Example1 AWFF PID with rotor 1 lift efficiency reduced to 85%"
  extends Example1ProjectControllerBase(
    quadChassisTest17_1.gain2(k = 0.0007266293));
  annotation(experiment(Algorithm = Dassl, StartTime = 0, StopTime = 50, Tolerance = 0.0001, Interval = 0.01));
  annotation(__MWORKS(hide=true));
end Example1Rotor1Loss15AntiWindupFeedforwardPID;
