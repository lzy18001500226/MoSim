within MoSimQuadrotorModel.Robustness.Scenarios.PIDBaselines;
model Example1Mass20ImprovedPID
  "Example1 improved PID with +20% central body mass perturbation"
  extends QuadrotorModel.Examples.Example1(
    quadChassisTest17_1.body(m = 1.2),
    controller3_2.PID3(KP = 1.65, KI = 0, KD = 1.0),
    controller3_2.PID4(KP = 1.65, KI = 0, KD = 1.0),
    controller3_2.PID5(KP = 14.142, KI = 0, KD = 1.70),
    controller3_2.PID6(KP = 14.142, KI = 0, KD = 1.70),
    controller3_2.PID7(KP = 8.0, KI = 6.0, KD = 4.0));
  annotation(experiment(Algorithm = Dassl, StartTime = 0, StopTime = 50, Tolerance = 0.0001, Interval = 0.01));
  annotation(__MWORKS(hide=true));
end Example1Mass20ImprovedPID;
