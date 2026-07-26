within MoSimQuadrotorModel.Deployment;
model RT0RealtimeProbe
  "Real-time external-I/O probe for the MWORKS Live capability gate"

  parameter Real samplePeriod=0.01 "External-I/O sampling period in seconds";

  impure function exchangeFrame
    input Real simulationTime;
    output Integer processedFrames;
    output Integer sentFrames;
    output Integer lastSequence;
    output Real sourceStampNs;
    output Real computeStartedNs;
    output Real computeFinishedNs;
    output Real desiredQz;
    output Real desiredQw;
    output Real collectiveThrustN;
    output Integer outputValid;
    external "C" processedFrames = mosim_mworks_live_rt0_exchange(
      simulationTime,
      sentFrames,
      lastSequence,
      sourceStampNs,
      computeStartedNs,
      computeFinishedNs,
      desiredQz,
      desiredQw,
      collectiveThrustN,
      outputValid)
      annotation(
        Include="#include \"mosim_mworks_live_rt0_bridge.h\"",
        IncludeDirectory="modelica://MoSimQuadrotorModel/Deployment/Resources/Include",
        Library="Ws2_32");
  end exchangeFrame;

  discrete Integer processedFrames(start=0, fixed=true);
  discrete Integer processedFramesThisTick(start=0, fixed=true);
  discrete Integer sentFrames(start=0, fixed=true);
  discrete Integer sentFramesThisTick(start=0, fixed=true);
  discrete Integer coalescedFrames(start=0, fixed=true);
  discrete Integer lastSequence(start=-1, fixed=true);
  discrete Real sourceStampNs(start=0, fixed=true);
  discrete Real computeStartedNs(start=0, fixed=true);
  discrete Real computeFinishedNs(start=0, fixed=true);
  discrete Real desiredQz(start=0, fixed=true);
  discrete Real desiredQw(start=1, fixed=true);
  discrete Real collectiveThrustN(start=0, fixed=true);
  discrete Integer outputValid(start=0, fixed=true);

algorithm
  when sample(0, samplePeriod) then
    (processedFramesThisTick,
     sentFramesThisTick,
     lastSequence,
     sourceStampNs,
     computeStartedNs,
     computeFinishedNs,
     desiredQz,
     desiredQw,
     collectiveThrustN,
     outputValid) := exchangeFrame(time);
    processedFrames := pre(processedFrames) + max(processedFramesThisTick, 0);
    sentFrames := pre(sentFrames) + max(sentFramesThisTick, 0);
    coalescedFrames := pre(coalescedFrames) +
      max(processedFramesThisTick - sentFramesThisTick, 0);
  end when;

  annotation(
    experiment(StartTime=0, StopTime=12, Interval=0.01, Tolerance=1e-6),
    Documentation(info="<html><p>This model is only an RT0 transport and timing probe. It does not control Gazebo or a vehicle. A valid RT0 run must use Sysplorer real-time simulation mode 2 and the companion probe client.</p></html>"),__MWORKS(version="26.3.0"));
end RT0RealtimeProbe;