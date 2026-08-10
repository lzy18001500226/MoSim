within MoSimQuadrotorModel.Control.LegacyExamples.PidVariants;
model Example2HelixTunedEnhancedPID
  "Example2 enhanced PID with helix-specific lateral command authority"
  extends MoSimQuadrotorModel.Vehicle.Examples.Example2(
    controller3_2.PID3(KP = 1.65, KI = 0, KD = 1.0, der1(T = 0.05)),
    controller3_2.PID4(KP = 1.65, KI = 0, KD = 1.0, der1(T = 0.05)),
    controller3_2.PID5(KP = 14.142, KI = 0, KD = 1.70, der1(T = 0.03)),
    controller3_2.PID6(KP = 14.142, KI = 0, KD = 1.70, der1(T = 0.03)),
    controller3_2.PID7(KP = 8.0, KI = 6.0, KD = 4.0, der1(T = 0.08)),
    controller3_2.limiter1(uMax = 15 / 57.3, uMin = -15 / 57.3),
    controller3_2.limiter2(uMax = 15 / 57.3, uMin = -15 / 57.3),
    controller3_2.limiter3(uMax = 7.0, uMin = -7.0),
    controller3_2.limiter4(uMax = 7.0, uMin = -7.0),
    controller3_2.limiter5(uMax = 7.0, uMin = -7.0));
  annotation(experiment(Algorithm = Dassl, StartTime = 0, StopTime = 50, Tolerance = 0.0001, Interval = 0.01));
  annotation(__MWORKS(hide=true,version="26.3.0"));
end Example2HelixTunedEnhancedPID;