within MoSimQuadrotorModel.Robustness.Scenarios.PIDBaselines;
model Example1WindGustImprovedPID
  "Example1 improved PID with lateral gust disturbance"
  extends Example1WindGustBase(
    controller3_2.PID3(KP = 1.65, KI = 0, KD = 1.0),
    controller3_2.PID4(KP = 1.65, KI = 0, KD = 1.0),
    controller3_2.PID5(KP = 14.142, KI = 0, KD = 1.70),
    controller3_2.PID6(KP = 14.142, KI = 0, KD = 1.70),
    controller3_2.PID7(KP = 8.0, KI = 6.0, KD = 4.0));
  annotation(__MWORKS(hide=true));
end Example1WindGustImprovedPID;
