within MoSimQuadrotorModel.LiveIntegration;
model RT0RealtimeProbe200Hz
  "200 Hz candidate RT0 capability probe; does not alter the accepted 50 Hz profile"
  extends RT0RealtimeProbe(final samplePeriod=0.005);

  impure function requestHighResolutionTimer
    output Integer status;
    external "C" status = mosim_mworks_live_request_1ms_timer_resolution()
      annotation(
        Include="#include \"mosim_mworks_live_rt0_timer_resolution.h\"",
        IncludeDirectory="modelica://MoSimQuadrotorModel/LiveIntegration/Resources/Include",
        Library="Winmm");
  end requestHighResolutionTimer;

  discrete Integer timerResolutionStatus(start=0, fixed=true);

algorithm
  when initial() then
    timerResolutionStatus := requestHighResolutionTimer();
  end when;

  annotation(
    experiment(StartTime=0, StopTime=12, Interval=0.005, Tolerance=1e-6),
    Documentation(info="<html><p>Candidate-only 200 Hz real-time transport and timing probe. Promotion requires an accepted RT0 analysis and a new versioned profile/hash.</p></html>"),__MWORKS(version="26.3.0"));
end RT0RealtimeProbe200Hz;