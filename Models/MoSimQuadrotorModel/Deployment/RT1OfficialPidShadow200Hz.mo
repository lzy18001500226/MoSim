within MoSimQuadrotorModel.Deployment;
model RT1OfficialPidShadow200Hz
  "200 Hz Official PID MWORKS Live shadow controller"

  final parameter Real samplePeriod=0.005;
  parameter Real mass=MoSimQuadrotorModel.Parameters.sunray150_virtual_px4_classic_mass_kg;
  parameter Real gravity=MoSimQuadrotorModel.Parameters.sunray150_virtual_px4_classic_gravity_mps2;
  parameter Real hoverPercentage=
    MoSimQuadrotorModel.Parameters.sunray150_virtual_px4_classic_mworks_controller_hover_percentage;
  parameter Real kp[3]={11, 11, 4};
  parameter Real kv[3]={6.5, 6.5, 4};

  impure function exchangeOfficialPid
    input Real mass;
    input Real gravity;
    input Real hoverPercentage;
    input Real kpX;
    input Real kpY;
    input Real kpZ;
    input Real kvX;
    input Real kvY;
    input Real kvZ;
    output Integer processedFrames;
    output Integer sentFrames;
    output Integer lastStateSequence;
    output Real lastCollectiveThrustN;
    output Integer lastOutputValid;
    output Integer socketInitStatus;
    output Integer socketErrorCode;
    output Integer socketLocalPort;
    external "C" processedFrames = mosim_mworks_live_rt1_exchange_official_pid(
      mass, gravity, hoverPercentage, kpX, kpY, kpZ, kvX, kvY, kvZ,
      sentFrames, lastStateSequence, lastCollectiveThrustN,
      lastOutputValid, socketInitStatus, socketErrorCode, socketLocalPort) 
      annotation(
        Include="#include \"mosim_mworks_live_rt1_bridge.h\"",
        IncludeDirectory="modelica://MoSimQuadrotorModel/Deployment/Resources/Include",
        Library="Ws2_32");
  end exchangeOfficialPid;

  impure function requestHighResolutionTimer
    output Integer status;
    external "C" status = mosim_mworks_live_request_1ms_timer_resolution() 
      annotation(
        Include="#include \"mosim_mworks_live_rt0_timer_resolution.h\"",
        IncludeDirectory="modelica://MoSimQuadrotorModel/Deployment/Resources/Include",
        Library="Winmm");
  end requestHighResolutionTimer;

  discrete Integer timerResolutionStatus(start=0, fixed=true);
  discrete Integer processedFrames(start=0, fixed=true);
  discrete Integer processedThisTick(start=0, fixed=true);
  discrete Integer sentFrames(start=0, fixed=true);
  discrete Integer sentThisTick(start=0, fixed=true);
  discrete Integer coalescedFrames(start=0, fixed=true)
    "Stale queued state frames discarded by latest-state-wins processing";
  discrete Integer lastStateSequence(start=-1, fixed=true);
  discrete Real lastCollectiveThrustN(start=mass*gravity, fixed=true);
  discrete Integer lastOutputValid(start=0, fixed=true);
  discrete Integer socketInitStatus(start=0, fixed=true);
  discrete Integer socketErrorCode(start=0, fixed=true);
  discrete Integer socketLocalPort(start=0, fixed=true);

algorithm
  when initial() then
    timerResolutionStatus := requestHighResolutionTimer();
  end when;
  when sample(0, samplePeriod) then
    (processedThisTick, sentThisTick, lastStateSequence,
     lastCollectiveThrustN, lastOutputValid, socketInitStatus,
     socketErrorCode, socketLocalPort) := exchangeOfficialPid(
      mass, gravity, hoverPercentage,
      kp[1], kp[2], kp[3], kv[1], kv[2], kv[3]);
    processedFrames := pre(processedFrames) + max(processedThisTick, 0);
    sentFrames := pre(sentFrames) + max(sentThisTick, 0);
    coalescedFrames := pre(coalescedFrames) +
      max(processedThisTick - sentThisTick, 0);
  end when;

  annotation(
    experiment(StartTime=0, StopTime=900, Interval=0.005, Tolerance=1e-6),
    Documentation(info="<html><p>Runs the Official PID translational outer loop inside MWORKS at 200 Hz. In Sysplorer real-time mode the 5 ms experiment interval is part of the live scheduler and must remain aligned with the controller event. The receive bridge drains a bounded UDP backlog but computes only from the newest state, so a scheduler pause cannot replay historical control outputs; discarded queued states are counted in coalescedFrames. The 900 s default window includes runtime startup and a full 300 s shadow gate. The 200 Hz RT0 contract allows a measured 10 ms end-to-end deadline and reports command age above the 5 ms nominal period as a soft warning. Ground-only takeover and unique publisher gates remain mandatory.</p></html>"),__MWORKS(version="26.3.0"));
end RT1OfficialPidShadow200Hz;