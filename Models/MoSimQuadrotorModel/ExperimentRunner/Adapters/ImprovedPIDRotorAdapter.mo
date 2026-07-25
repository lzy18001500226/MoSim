within MoSimQuadrotorModel.ExperimentRunner.Adapters;
model ImprovedPIDRotorAdapter
  "Improved PID adapted explicitly to the offline ROTOR_COMMAND boundary"

  extends MoSimQuadrotorModel.ExperimentRunner.Adapters.OfficialPIDRotorAdapter(
    core.PID3(KP = 1.65, KI = 0, KD = 1.0),
    core.PID4(KP = 1.65, KI = 0, KD = 1.0),
    core.PID5(KP = 14.142, KI = 0, KD = 1.70),
    core.PID6(KP = 14.142, KI = 0, KD = 1.70),
    core.PID7(KP = 8.0, KI = 6.0, KD = 4.0));
  annotation(__MWORKS(version="26.3.0"));
end ImprovedPIDRotorAdapter;