within MoSimQuadrotorModel.Control.Baselines;
model Example1EnhancedPID
  "Example1 with explicit derivative filtering and conservative command limits"
  extends MoSimQuadrotorModel.Vehicle.Examples.Example1(
    controller3_2.PID3(KP = 1.65, KI = 0, KD = 1.0, der1(T = 0.05)),
    controller3_2.PID4(KP = 1.65, KI = 0, KD = 1.0, der1(T = 0.05)),
    controller3_2.PID5(KP = 14.142, KI = 0, KD = 1.70, der1(T = 0.03)),
    controller3_2.PID6(KP = 14.142, KI = 0, KD = 1.70, der1(T = 0.03)),
    controller3_2.PID7(KP = 8.0, KI = 6.0, KD = 4.0, der1(T = 0.08)),
    controller3_2.limiter1(uMax = 12 / 57.3, uMin = -12 / 57.3),
    controller3_2.limiter2(uMax = 12 / 57.3, uMin = -12 / 57.3),
    controller3_2.limiter3(uMax = 6.5, uMin = -6.5),
    controller3_2.limiter4(uMax = 6.5, uMin = -6.5),
    controller3_2.limiter5(uMax = 6.5, uMin = -6.5));
  annotation(experiment(Algorithm = Dassl, StartTime = 0, StopTime = 50, Tolerance = 0.0001, Interval = 0.01));
  annotation(__MWORKS(hide=true,version="26.3.0"));
end Example1EnhancedPID;