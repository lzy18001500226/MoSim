within MoSimQuadrotorModel.RealTime;
model MworksRt1Px4CtrlGraphicalShadow100Hz
  "RT1 transport wrapper for the graphical px4ctrl outer-loop core"

  final parameter Real samplePeriod(unit = "s") = 0.01;
  final parameter Integer transportPaceMs(min = 0) = 10
    "Wall-clock transport pace for the 100 Hz MWORKS shadow";
  parameter Real quaternionEpsilon = 1e-12;
  parameter MoSimQuadrotorModel.Parameters.Sunray150Parameters profile =
    MoSimQuadrotorModel.Parameters.Sunray150Parameters();
  parameter Real hoverCollectiveThrustN(unit = "N") = 4
    * profile.mworks_visual_thrust_coefficient
    * profile.mworks_hover_visual_rotor_speed_rad_s ^ 2;

  impure function exchange
    input Integer sendRequested;
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
    input Integer paceMs;
    output Integer processedFrames;
    output Integer exchangeCallCount;
    output Integer sendStatus;
    output Integer socketReady;
    output Integer socketInitStatus;
    output Integer socketErrorCode;
    output Integer socketLocalPort;
    output Integer receivedDatagramsThisTick;
    output Integer rejectedDatagramsThisTick;
    output Integer lastReceivedByteCount;
    output Integer receiveErrorCode;
    output Integer receivedStateSequence;
    output Real receivedSourceStampNs;
    output Real receivedAdapterReceiveMonotonicNs;
    output Integer receivedArmed;
    output Integer receivedFrameValid;
    output Real receivedValues[24];
    external "C" processedFrames = mosim_mworks_rt1_graphical_exchange(
      sendRequested, stateSequence, adapterReceiveMonotonicNs, qx, qy, qz,
      qw, collectiveThrustN, saturationMask, controllerStatus, outputValid,
      paceMs,
      exchangeCallCount, sendStatus, socketReady, socketInitStatus, socketErrorCode,
      socketLocalPort, receivedDatagramsThisTick, rejectedDatagramsThisTick,
      lastReceivedByteCount, receiveErrorCode, receivedStateSequence,
      receivedSourceStampNs,
      receivedAdapterReceiveMonotonicNs, receivedArmed, receivedFrameValid,
      receivedValues) 
      annotation(
        Include="#include \"mosim_mworks_rt1_graphical_exchange.h\"",
        IncludeDirectory="modelica://MoSimQuadrotorModel/RealTime/Resources/Include",
        Library="Ws2_32");
  end exchange;

  // The adapter is a Modelica integration layer; its nested outer_loop is the
  // actual graphical Sysblock. Marking this wrapper as SECInstance is invalid.
  MoSimQuadrotorModel.Control.Px4Ctrl.Px4CtrlAttitudeThrustSysblockAdapter 
    graphicalController(profile = profile);

  discrete Real stateValues[24](each start = 0, each fixed = true);
  discrete Integer lastStateSequence(start = -1, fixed = true);
  discrete Real lastSourceStampNs(start = 0, fixed = true);
  discrete Real lastAdapterReceiveMonotonicNs(start = 0, fixed = true);
  discrete Integer lastArmed(start = 0, fixed = true);
  discrete Integer lastFrameValid(start = 0, fixed = true);
  discrete Boolean pendingCommand(start = false, fixed = true);
  discrete Integer processedFrames(start = 0, fixed = true);
  discrete Integer sentFrames(start = 0, fixed = true);
  discrete Integer coalescedFrames(start = 0, fixed = true);
  discrete Integer sampleTicks(start = 0, fixed = true);
  discrete Integer graphicalStateTicks(start = 0, fixed = true);
  discrete Integer receivedDatagrams(start = 0, fixed = true);
  discrete Integer rejectedDatagrams(start = 0, fixed = true);
  discrete Integer processedThisTick(start = 0, fixed = true);
  discrete Integer exchangeCallCount(start = 0, fixed = true);
  discrete Integer sentThisTick(start = 0, fixed = true);
  discrete Integer receivedStateSequence(start = -1, fixed = true);
  discrete Real receivedSourceStampNs(start = 0, fixed = true);
  discrete Real receivedAdapterReceiveMonotonicNs(start = 0, fixed = true);
  discrete Integer receivedArmed(start = 0, fixed = true);
  discrete Integer receivedFrameValid(start = 0, fixed = true);
  discrete Real receivedValues[24](each start = 0, each fixed = true);
  discrete Integer sendStatus(start = 0, fixed = true);
  discrete Integer socketReady(start = 0, fixed = true);
  discrete Integer socketInitStatus(start = 0, fixed = true);
  discrete Integer socketErrorCode(start = 0, fixed = true);
  discrete Integer socketLocalPort(start = 0, fixed = true);
  discrete Integer receivedDatagramsThisTick(start = 0, fixed = true);
  discrete Integer rejectedDatagramsThisTick(start = 0, fixed = true);
  discrete Integer lastReceivedByteCount(start = 0, fixed = true);
  discrete Integer receiveErrorCode(start = 0, fixed = true);
  discrete Real queuedCommandQx(start = 0, fixed = true);
  discrete Real queuedCommandQy(start = 0, fixed = true);
  discrete Real queuedCommandQz(start = 0, fixed = true);
  discrete Real queuedCommandQw(start = 1, fixed = true);
  discrete Real queuedCollectiveThrustN(start = hoverCollectiveThrustN,
    fixed = true);

  Real rawStateQx;
  Real rawStateQy;
  Real rawStateQz;
  Real rawStateQw;
  Real stateQx;
  Real stateQy;
  Real stateQz;
  Real stateQw;
  Real stateQuaternionNorm;
  Real rollMeasured;
  Real pitchMeasured;
  Real yawMeasured;
  Real pitchArgument;
  Real commandRoll;
  Real commandPitch;
  Real commandYaw;
  Real rawCommandQx;
  Real rawCommandQy;
  Real rawCommandQz;
  Real rawCommandQw;
  Real commandQx;
  Real commandQy;
  Real commandQz;
  Real commandQw;
  Real commandQuaternionNorm;
  Real collectiveThrustN(unit = "N");
  discrete Integer saturationMask(start = 0, fixed = true);
  discrete Integer controllerStatus(start = 0, fixed = true);
  discrete Integer controllerOutputValid(start = 0, fixed = true);

equation
  // The state-vector ordering is the fixed RT1 frame ordering in rt1_contract.py.
  rawStateQx = stateValues[7];
  rawStateQy = stateValues[8];
  rawStateQz = stateValues[9];
  rawStateQw = stateValues[10];
  stateQuaternionNorm = max(quaternionEpsilon,
    sqrt(rawStateQx ^ 2 + rawStateQy ^ 2 + rawStateQz ^ 2 + rawStateQw ^ 2));
  stateQx = rawStateQx / stateQuaternionNorm;
  stateQy = rawStateQy / stateQuaternionNorm;
  stateQz = rawStateQz / stateQuaternionNorm;
  stateQw = rawStateQw / stateQuaternionNorm;
  rollMeasured = atan2(2 * (stateQw * stateQx + stateQy * stateQz),
    1 - 2 * (stateQx ^ 2 + stateQy ^ 2));
  pitchArgument = 2 * (stateQw * stateQy - stateQz * stateQx);
  pitchMeasured = if pitchArgument >= 1 then Modelica.Constants.pi / 2 
    else if pitchArgument <= -1 then -Modelica.Constants.pi / 2 
    else asin(pitchArgument);
  yawMeasured = atan2(2 * (stateQw * stateQz + stateQx * stateQy),
    1 - 2 * (stateQy ^ 2 + stateQz ^ 2));

  graphicalController.position_ref[1] = stateValues[14];
  graphicalController.position_ref[2] = stateValues[15];
  graphicalController.position_ref[3] = stateValues[16];
  graphicalController.velocity_ref[1] = stateValues[17];
  graphicalController.velocity_ref[2] = stateValues[18];
  graphicalController.velocity_ref[3] = stateValues[19];
  graphicalController.acceleration_ref[1] = stateValues[20];
  graphicalController.acceleration_ref[2] = stateValues[21];
  graphicalController.acceleration_ref[3] = stateValues[22];
  graphicalController.position_mea[1] = stateValues[1];
  graphicalController.position_mea[2] = stateValues[2];
  graphicalController.position_mea[3] = stateValues[3];
  graphicalController.velocity_mea[1] = stateValues[4];
  graphicalController.velocity_mea[2] = stateValues[5];
  graphicalController.velocity_mea[3] = stateValues[6];
  graphicalController.attitude_mea[1] = rollMeasured;
  graphicalController.attitude_mea[2] = pitchMeasured;
  graphicalController.attitude_mea[3] = yawMeasured;

  commandRoll = graphicalController.attitude_ref[1];
  commandPitch = graphicalController.attitude_ref[2];
  commandYaw = graphicalController.attitude_ref[3];
  rawCommandQw = cos(commandYaw / 2) * cos(commandPitch / 2) * cos(commandRoll / 2)
    + sin(commandYaw / 2) * sin(commandPitch / 2) * sin(commandRoll / 2);
  rawCommandQx = cos(commandYaw / 2) * cos(commandPitch / 2) * sin(commandRoll / 2)
    - sin(commandYaw / 2) * sin(commandPitch / 2) * cos(commandRoll / 2);
  rawCommandQy = cos(commandYaw / 2) * sin(commandPitch / 2) * cos(commandRoll / 2)
    + sin(commandYaw / 2) * cos(commandPitch / 2) * sin(commandRoll / 2);
  rawCommandQz = sin(commandYaw / 2) * cos(commandPitch / 2) * cos(commandRoll / 2)
    - cos(commandYaw / 2) * sin(commandPitch / 2) * sin(commandRoll / 2);
  commandQuaternionNorm = max(quaternionEpsilon,
    sqrt(rawCommandQx ^ 2 + rawCommandQy ^ 2 + rawCommandQz ^ 2 + rawCommandQw ^ 2));
  commandQx = rawCommandQx / commandQuaternionNorm;
  commandQy = rawCommandQy / commandQuaternionNorm;
  commandQz = rawCommandQz / commandQuaternionNorm;
  commandQw = rawCommandQw / commandQuaternionNorm;
  collectiveThrustN = hoverCollectiveThrustN
    + graphicalController.collective_thrust_delta;

algorithm
  when sample(0, samplePeriod) then
    // Keep all transport state in one C translation unit.  The call sends the
    // queued graphical output from the preceding sample, then returns the
    // freshest bounded receive batch for this sample.
    (processedThisTick, exchangeCallCount, sendStatus, socketReady, socketInitStatus,
      socketErrorCode, socketLocalPort, receivedDatagramsThisTick,
      rejectedDatagramsThisTick, lastReceivedByteCount, receiveErrorCode,
      receivedStateSequence, receivedSourceStampNs,
      receivedAdapterReceiveMonotonicNs, receivedArmed, receivedFrameValid,
      receivedValues) := exchange(
      if pre(pendingCommand) then 1 else 0, pre(lastStateSequence),
      pre(lastAdapterReceiveMonotonicNs), pre(queuedCommandQx),
      pre(queuedCommandQy), pre(queuedCommandQz), pre(queuedCommandQw),
      pre(queuedCollectiveThrustN), pre(saturationMask),
      pre(controllerStatus), pre(controllerOutputValid), transportPaceMs);
    processedFrames := pre(processedFrames) + max(processedThisTick, 0);
    sentThisTick := if sendStatus > 0 then 1 else 0;
    sentFrames := pre(sentFrames) + sentThisTick;
    coalescedFrames := pre(coalescedFrames)
      + max(processedThisTick - (if processedThisTick > 0 then 1 else 0), 0);
    sampleTicks := pre(sampleTicks) + 1;
    receivedDatagrams := pre(receivedDatagrams)
      + max(receivedDatagramsThisTick, 0);
    rejectedDatagrams := pre(rejectedDatagrams)
      + max(rejectedDatagramsThisTick, 0);

    if processedThisTick > 0 and receivedArmed > 0 and receivedFrameValid > 0 then
      stateValues := receivedValues;
      lastStateSequence := receivedStateSequence;
      lastSourceStampNs := receivedSourceStampNs;
      lastAdapterReceiveMonotonicNs := receivedAdapterReceiveMonotonicNs;
      lastArmed := receivedArmed;
      lastFrameValid := receivedFrameValid;
      graphicalStateTicks := pre(graphicalStateTicks) + 1;
      queuedCommandQx := commandQx;
      queuedCommandQy := commandQy;
      queuedCommandQz := commandQz;
      queuedCommandQw := commandQw;
      queuedCollectiveThrustN := collectiveThrustN;
      // These are transport-gate values. The C exchange also rejects
      // non-finite or non-positive graphical thrust on the wire.
      saturationMask := 0;
      controllerStatus := 1;
      controllerOutputValid := 1;
      // The first accepted state primes the scheduled graphical Sysblock.
      // Sending begins after the next accepted state, so every outbound
      // command is generated by that Sysblock rather than an equation fallback.
      pendingCommand := pre(graphicalStateTicks) >= 1;
    else
      saturationMask := 0;
      controllerStatus := 0;
      controllerOutputValid := 0;
      pendingCommand := false;
    end if;
  end when;

  annotation(
    experiment(Algorithm = Euler, IntegratorStep = 0.01, Interval = 0.01,
      StartTime = 0, StopTime = 300, StoreEventValue = 0),
    Documentation(info = "<html><p>The C boundary receives and sends fixed-size RT1 frames only. The control calculation is delegated to the nested px4ctrl graphical Sysblock through its Modelica adapter. This model is a 100 Hz MWORKS shadow entry because the referenced graphical core currently declares a 10 ms sample time. The transport pace keeps a local loopback aligned with that sample period; live deadline acceptance remains separate from this structural bridge.</p></html>"),
    __MWORKS(version = "26.3.0"));
end MworksRt1Px4CtrlGraphicalShadow100Hz;