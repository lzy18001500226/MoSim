within MoSimQuadrotorModel.LiveIntegration;
model RT1OfficialPidShadow50Hz
  "50 Hz Official PID MWORKS Live shadow controller"

  parameter Real samplePeriod=0.02;
  parameter Real mass=0.67;
  parameter Real gravity=9.81;
  parameter Real hoverPercentage=0.294;
  parameter Real kp[3]={11, 11, 4};
  parameter Real kv[3]={6.5, 6.5, 4};

  impure function receiveFrame
    output Integer processedFrames;
    output Integer sequence;
    output Real sourceStampNs;
    output Real adapterReceiveMonotonicNs;
    output Integer armed;
    output Integer frameValid;
    output Real values[24];
    external "C" processedFrames = mosim_mworks_live_rt1_receive(
      sequence, sourceStampNs, adapterReceiveMonotonicNs, armed, frameValid,
      values)
      annotation(
        Include="#include \"mosim_mworks_live_rt1_bridge.h\"",
        IncludeDirectory="modelica://MoSimQuadrotorModel/LiveIntegration/Resources/Include",
        Library="Ws2_32");
  end receiveFrame;

  impure function sendCommand
    input Integer stateSequence;
    input Real adapterReceiveMonotonicNs;
    input Real qx;
    input Real qy;
    input Real qz;
    input Real qw;
    input Real collectiveThrustN;
    input Integer saturationMask;
    input Integer controllerStatus;
    input Integer outputValid;
    output Integer result;
    external "C" result = mosim_mworks_live_rt1_send(
      stateSequence, adapterReceiveMonotonicNs, qx, qy, qz, qw,
      collectiveThrustN, saturationMask, controllerStatus, outputValid)
      annotation(
        Include="#include \"mosim_mworks_live_rt1_bridge.h\"",
        IncludeDirectory="modelica://MoSimQuadrotorModel/LiveIntegration/Resources/Include",
        Library="Ws2_32");
  end sendCommand;

  discrete Integer processedFrames(start=0, fixed=true);
  discrete Integer processedThisTick(start=0, fixed=true);
  discrete Integer sentFrames(start=0, fixed=true);
  discrete Integer sendResult(start=0, fixed=true);
  discrete Integer stateSequence(start=-1, fixed=true);
  discrete Integer armed(start=0, fixed=true);
  discrete Integer frameValid(start=0, fixed=true);
  discrete Real sourceStampNs(start=0, fixed=true);
  discrete Real adapterReceiveMonotonicNs(start=0, fixed=true);
  discrete Real values[24](each start=0, each fixed=true);
  discrete Real desiredAcceleration[3](each start=0, each fixed=true);
  discrete Real rollDes(start=0, fixed=true);
  discrete Real pitchDes(start=0, fixed=true);
  discrete Real yawDes(start=0, fixed=true);
  discrete Real qx(start=0, fixed=true);
  discrete Real qy(start=0, fixed=true);
  discrete Real qz(start=0, fixed=true);
  discrete Real qw(start=1, fixed=true);
  discrete Real qNorm(start=1, fixed=true);
  discrete Real collectiveThrustN(start=mass*gravity, fixed=true);
  discrete Real fullThrustN(start=mass*gravity/hoverPercentage, fixed=true);
  discrete Integer saturationMask(start=0, fixed=true);

algorithm
  when sample(0, samplePeriod) then
    (processedThisTick, stateSequence, sourceStampNs,
     adapterReceiveMonotonicNs, armed, frameValid, values) := receiveFrame();
    processedFrames := pre(processedFrames) + max(processedThisTick, 0);
    fullThrustN := mass*gravity/hoverPercentage;
    if processedThisTick > 0 and frameValid == 1 then
      desiredAcceleration[1] := values[20] + kv[1]*(values[17] - values[4]) + kp[1]*(values[14] - values[1]);
      desiredAcceleration[2] := values[21] + kv[2]*(values[18] - values[5]) + kp[2]*(values[15] - values[2]);
      desiredAcceleration[3] := values[22] + kv[3]*(values[19] - values[6]) + kp[3]*(values[16] - values[3]) + gravity;
      yawDes := values[23];
      rollDes := (desiredAcceleration[1]*sin(yawDes) - desiredAcceleration[2]*cos(yawDes))/gravity;
      pitchDes := (desiredAcceleration[1]*cos(yawDes) + desiredAcceleration[2]*sin(yawDes))/gravity;
      qw := cos(yawDes/2)*cos(pitchDes/2)*cos(rollDes/2) + sin(yawDes/2)*sin(pitchDes/2)*sin(rollDes/2);
      qx := cos(yawDes/2)*cos(pitchDes/2)*sin(rollDes/2) - sin(yawDes/2)*sin(pitchDes/2)*cos(rollDes/2);
      qy := cos(yawDes/2)*sin(pitchDes/2)*cos(rollDes/2) + sin(yawDes/2)*cos(pitchDes/2)*sin(rollDes/2);
      qz := sin(yawDes/2)*cos(pitchDes/2)*cos(rollDes/2) - cos(yawDes/2)*sin(pitchDes/2)*sin(rollDes/2);
      qNorm := sqrt(qx*qx + qy*qy + qz*qz + qw*qw);
      qx := qx/max(qNorm, 1e-12);
      qy := qy/max(qNorm, 1e-12);
      qz := qz/max(qNorm, 1e-12);
      qw := qw/max(qNorm, 1e-12);
      collectiveThrustN := min(max(mass*desiredAcceleration[3], 0), fullThrustN);
      saturationMask := if mass*desiredAcceleration[3] <> collectiveThrustN then 1 else 0;
      sendResult := sendCommand(
        stateSequence, adapterReceiveMonotonicNs, qx, qy, qz, qw,
        collectiveThrustN, saturationMask, 1, 1);
      if sendResult > 0 then
        sentFrames := pre(sentFrames) + 1;
      end if;
    end if;
  end when;

  annotation(
    experiment(StartTime=0, StopTime=120, Interval=0.02, Tolerance=1e-6),
    Documentation(info="<html><p>Runs the Official PID translational outer loop inside MWORKS at 50 Hz. The default ROS adapter is shadow-only, so this model cannot own MAVROS output until a separate ground-only takeover gate passes.</p></html>"),__MWORKS(version="26.3.0"));
end RT1OfficialPidShadow50Hz;