within MoSimQuadrotorModel.Deployment;
model RT0RealtimeProbe50Hz
  "50 Hz RT0 capability probe; preserves the failed 100 Hz candidate"
  extends RT0RealtimeProbe(final samplePeriod=0.02);

  annotation(
    experiment(StartTime=0, StopTime=22, Interval=0.02, Tolerance=1e-6),__MWORKS(version="26.3.0"));
end RT0RealtimeProbe50Hz;