within MoSimQuadrotorModel.Deployment;
model RTTelemetryScope50Hz
  "Read-only 50 Hz ROS1 telemetry receiver for native MWORKS curves"

  parameter Real samplePeriod=0.02;

  impure function receiveTelemetry
    output Integer processedFrames;
    output Integer sequence;
    output Real sourceStampNs;
    output Real senderMonotonicNs;
    output Integer flags;
    output Integer frameValid;
    output Integer socketInitStatus;
    output Integer socketErrorCode;
    output Real values[32];
    external "C" processedFrames = mosim_mworks_live_telemetry_scope_receive(
      sequence, sourceStampNs, senderMonotonicNs, flags, frameValid,
      socketInitStatus, socketErrorCode, values)
      annotation(
        Include="#include \"mosim_mworks_live_telemetry_scope.h\"",
        IncludeDirectory="modelica://MoSimQuadrotorModel/Deployment/Resources/Include",
        Library="Ws2_32");
  end receiveTelemetry;

  discrete Integer processedFrames(start=0, fixed=true);
  discrete Integer processedThisTick(start=0, fixed=true);
  discrete Integer sequence(start=-1, fixed=true);
  discrete Integer previousSequence(start=-1, fixed=true);
  discrete Integer sequenceGaps(start=0, fixed=true);
  discrete Integer flags(start=0, fixed=true);
  discrete Integer frameValid(start=0, fixed=true);
  discrete Integer socketInitStatus(start=0, fixed=true);
  discrete Integer socketErrorCode(start=0, fixed=true);
  discrete Real sourceStampNs(start=0, fixed=true);
  discrete Real senderMonotonicNs(start=0, fixed=true);
  discrete Real values[32](each start=0, each fixed=true);

  discrete Real actualPosition[3](each start=0, each fixed=true);
  discrete Real actualVelocity[3](each start=0, each fixed=true);
  discrete Real attitudeQuaternion[4](start={0,0,0,1}, each fixed=true);
  discrete Real bodyRate[3](each start=0, each fixed=true);
  discrete Real referencePosition[3](each start=0, each fixed=true);
  discrete Real referenceVelocity[3](each start=0, each fixed=true);
  discrete Real referenceAcceleration[3](each start=0, each fixed=true);
  discrete Real referenceYaw(start=0, fixed=true);
  discrete Real targetThrust(start=0, fixed=true);
  discrete Real positionError[3](each start=0, each fixed=true);
  discrete Real positionErrorNorm(start=0, fixed=true);
  discrete Real attitudeErrorRad(start=0, fixed=true);
  discrete Real sourceAgeMs(start=-1, fixed=true);
  discrete Real roundTripMs(start=-1, fixed=true);
  discrete Real commandAgeMs(start=-1, fixed=true);
  discrete Real senderAckGaps(start=0, fixed=true);
  discrete Integer armed(start=0, fixed=true);
  discrete Integer stateValid(start=0, fixed=true);
  discrete Integer referenceValid(start=0, fixed=true);
  discrete Integer commandValid(start=0, fixed=true);

algorithm
  when sample(0, samplePeriod) then
    previousSequence := pre(sequence);
    (processedThisTick, sequence, sourceStampNs, senderMonotonicNs, flags,
     frameValid, socketInitStatus, socketErrorCode, values) := receiveTelemetry();
    processedFrames := pre(processedFrames) + max(processedThisTick, 0);
    if processedThisTick > 0 and frameValid == 1 then
      if previousSequence >= 0 and sequence > previousSequence + 1 then
        sequenceGaps := pre(sequenceGaps) + sequence - previousSequence - 1;
      end if;
      actualPosition := values[1:3];
      actualVelocity := values[4:6];
      attitudeQuaternion := values[7:10];
      bodyRate := values[11:13];
      referencePosition := values[14:16];
      referenceVelocity := values[17:19];
      referenceAcceleration := values[20:22];
      referenceYaw := values[23];
      targetThrust := values[24];
      positionError := values[25:27];
      positionErrorNorm := sqrt(
        positionError[1]^2 + positionError[2]^2 + positionError[3]^2);
      attitudeErrorRad := values[28];
      sourceAgeMs := values[29];
      roundTripMs := values[30];
      commandAgeMs := values[31];
      senderAckGaps := values[32];
      armed := mod(div(flags, 1), 2);
      stateValid := mod(div(flags, 2), 2);
      referenceValid := mod(div(flags, 4), 2);
      commandValid := mod(div(flags, 8), 2);
    end if;
  end when;

  annotation(
    experiment(StartTime=0, StopTime=300, Interval=0.02, Tolerance=1e-6),
    Documentation(info="<html><p>Read-only observer for same-run ROS1 flight telemetry on the existing allowed UDP port 49020. The model never publishes a control command and must not run concurrently with the RT1 control model that owns the same port. Select actualPosition/referencePosition, actualVelocity, targetThrust, positionErrorNorm, attitudeErrorRad, sourceAgeMs, commandAgeMs and roundTripMs in the native MWORKS Scope/result curve window.</p></html>"),__MWORKS(version="26.3.0"));
end RTTelemetryScope50Hz;