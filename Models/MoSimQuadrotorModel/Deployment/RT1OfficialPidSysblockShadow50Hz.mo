within MoSimQuadrotorModel.Deployment;
model RT1OfficialPidSysblockShadow50Hz
  "50 Hz RT1 shadow bridge driven by the native graphical Official PID Sysblock"

  final parameter Real samplePeriod = 0.02;
  parameter Real mass = MoSimQuadrotorModel.Parameters.sunray150_virtual_px4_classic_mass_kg;
  parameter Real gravity = MoSimQuadrotorModel.Parameters.sunray150_virtual_px4_classic_gravity_mps2;
  parameter Real hoverPercentage =
    MoSimQuadrotorModel.Parameters.sunray150_virtual_px4_classic_mworks_controller_hover_percentage;

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
        Include = "#include \"mosim_mworks_live_rt1_bridge.h\"",
        IncludeDirectory = "modelica://MoSimQuadrotorModel/Deployment/Resources/Include",
        Library = "Ws2_32");
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
        Include = "#include \"mosim_mworks_live_rt1_bridge.h\"",
        IncludeDirectory = "modelica://MoSimQuadrotorModel/Deployment/Resources/Include",
        Library = "Ws2_32");
  end sendCommand;

  MoSimQuadrotorModel.Control.Adapters.OfficialPidSysblockAttitudeThrustAdapter
    controller
    annotation(Placement(transformation(origin = {0, 0}, extent = {{-82, -90}, {82, 90}})));

  final parameter Real fullThrustN = mass * gravity / hoverPercentage;
  discrete Integer processedFrames(start = 0, fixed = true);
  discrete Integer processedThisTick(start = 0, fixed = true);
  discrete Integer sentFrames(start = 0, fixed = true);
  discrete Integer sendResult(start = 0, fixed = true);
  discrete Integer receivedStateSequence(start = -1, fixed = true);
  discrete Integer pendingStateSequence(start = -1, fixed = true);
  discrete Integer pendingFrameValid(start = 0, fixed = true);
  discrete Integer armed(start = 0, fixed = true);
  discrete Integer frameValid(start = 0, fixed = true);
  discrete Integer saturationMask(start = 0, fixed = true);
  discrete Integer lastOutputValid(start = 0, fixed = true);
  discrete Real sourceStampNs(start = 0, fixed = true);
  discrete Real adapterReceiveMonotonicNs(start = 0, fixed = true);
  discrete Real pendingReceiveMonotonicNs(start = 0, fixed = true);
  discrete Real values[24](each start = 0, each fixed = true);
  discrete Real positionReference[3](each start = 0, each fixed = true);
  discrete Real positionMeasurement[3](each start = 0, each fixed = true);
  discrete Real attitudeMeasurement[3](each start = 0, each fixed = true);
  discrete Real yawReference(start = 0, fixed = true);
  discrete Real stateQx(start = 0, fixed = true);
  discrete Real stateQy(start = 0, fixed = true);
  discrete Real stateQz(start = 0, fixed = true);
  discrete Real stateQw(start = 1, fixed = true);
  discrete Real stateQNorm(start = 1, fixed = true);
  discrete Real commandQx(start = 0, fixed = true);
  discrete Real commandQy(start = 0, fixed = true);
  discrete Real commandQz(start = 0, fixed = true);
  discrete Real commandQw(start = 1, fixed = true);
  discrete Real commandQNorm(start = 1, fixed = true);
  discrete Real commandCollectiveThrustN(start = mass * gravity, fixed = true);
  discrete Real rawCollectiveThrustN(start = mass * gravity, fixed = true);
  Real rollDesired;
  Real pitchDesired;
  Real yawDesired;
  Real thrustDeltaNewton;

equation
  controller.position_ref = positionReference;
  controller.velocity_ref = {0, 0, 0};
  controller.acceleration_ref = {0, 0, 0};
  controller.position_mea = positionMeasurement;
  controller.velocity_mea = {0, 0, 0};
  controller.attitude_mea = attitudeMeasurement;
  rollDesired = controller.attitude_ref[1];
  pitchDesired = controller.attitude_ref[2];
  // The native Sysblock owns the translational axes. RT1 carries the incoming
  // yaw reference because the historical core's graphical yaw source is fixed.
  yawDesired = yawReference;
  thrustDeltaNewton = controller.collective_thrust_delta;

algorithm
  when sample(0, samplePeriod) then
    (processedThisTick, receivedStateSequence, sourceStampNs,
     adapterReceiveMonotonicNs, armed, frameValid, values) := receiveFrame();
    processedFrames := pre(processedFrames) + max(processedThisTick, 0);
    pendingFrameValid := 0;

    if processedThisTick > 0 and frameValid == 1 then
      stateQx := values[7];
      stateQy := values[8];
      stateQz := values[9];
      stateQw := values[10];
      stateQNorm := sqrt(stateQx * stateQx + stateQy * stateQy +
        stateQz * stateQz + stateQw * stateQw);
      if stateQNorm > 1e-12 then
        stateQx := stateQx / stateQNorm;
        stateQy := stateQy / stateQNorm;
        stateQz := stateQz / stateQNorm;
        stateQw := stateQw / stateQNorm;
        positionMeasurement := {values[1], values[2], values[3]};
        positionReference := {values[14], values[15], values[16]};
        attitudeMeasurement[1] := atan2(
          2 * (stateQw * stateQx + stateQy * stateQz),
          1 - 2 * (stateQx * stateQx + stateQy * stateQy));
        attitudeMeasurement[2] := asin(max(-1, min(1,
          2 * (stateQw * stateQy - stateQz * stateQx))));
        attitudeMeasurement[3] := atan2(
          2 * (stateQw * stateQz + stateQx * stateQy),
          1 - 2 * (stateQy * stateQy + stateQz * stateQz));
        yawReference := values[23];
        pendingStateSequence := receivedStateSequence;
        pendingReceiveMonotonicNs := adapterReceiveMonotonicNs;
        pendingFrameValid := 1;
      end if;
    end if;
  end when;

  // Offset from receive gives the graphical core one sample phase before emission.
  when sample(samplePeriod / 2, samplePeriod) then
    if pendingFrameValid == 1 then
      rawCollectiveThrustN := mass * gravity + thrustDeltaNewton;
      commandCollectiveThrustN := min(max(rawCollectiveThrustN, 0), fullThrustN);
      saturationMask := if rawCollectiveThrustN <> commandCollectiveThrustN then 1 else 0;
      commandQx := cos(yawDesired / 2) * cos(pitchDesired / 2) * sin(rollDesired / 2) -
        sin(yawDesired / 2) * sin(pitchDesired / 2) * cos(rollDesired / 2);
      commandQy := cos(yawDesired / 2) * sin(pitchDesired / 2) * cos(rollDesired / 2) +
        sin(yawDesired / 2) * cos(pitchDesired / 2) * sin(rollDesired / 2);
      commandQz := sin(yawDesired / 2) * cos(pitchDesired / 2) * cos(rollDesired / 2) -
        cos(yawDesired / 2) * sin(pitchDesired / 2) * sin(rollDesired / 2);
      commandQw := cos(yawDesired / 2) * cos(pitchDesired / 2) * cos(rollDesired / 2) +
        sin(yawDesired / 2) * sin(pitchDesired / 2) * sin(rollDesired / 2);
      commandQNorm := sqrt(commandQx * commandQx + commandQy * commandQy +
        commandQz * commandQz + commandQw * commandQw);
      commandQx := commandQx / max(commandQNorm, 1e-12);
      commandQy := commandQy / max(commandQNorm, 1e-12);
      commandQz := commandQz / max(commandQNorm, 1e-12);
      commandQw := commandQw / max(commandQNorm, 1e-12);
      if commandQx * pre(commandQx) + commandQy * pre(commandQy) +
          commandQz * pre(commandQz) + commandQw * pre(commandQw) < 0 then
        commandQx := -commandQx;
        commandQy := -commandQy;
        commandQz := -commandQz;
        commandQw := -commandQw;
      end if;
      sendResult := sendCommand(
        pendingStateSequence, pendingReceiveMonotonicNs,
        commandQx, commandQy, commandQz, commandQw,
        commandCollectiveThrustN, saturationMask, 1, 1);
      lastOutputValid := if sendResult > 0 then 1 else 0;
      if sendResult > 0 then
        sentFrames := pre(sentFrames) + 1;
      end if;
      pendingFrameValid := 0;
    end if;
  end when;

  annotation(
    experiment(StartTime = 0, StopTime = 120, Interval = 0.02, Tolerance = 1e-6),
    Documentation(info = "<html><p>RT1 shadow-only MWORKS bridge whose translational command originates from the native graphical <code>OfficialPidSysblockCore</code> through the formal <code>ATTITUDE_THRUST</code> adapter. The UDP C header only performs bounded receive/send transport; it does not calculate the PID law for this model.</p><p>The adapter uses the native graphical mapper's calibrated amplitude-to-Newton chain. RT1 carries yaw through separately because the historical graphical core has a fixed yaw source. This model is suitable for MWORKS-side wiring, protocol, and shadow evidence, but it does not pass RT0, enable a controller takeover, or prove Gazebo/PX4 flight.</p></html>"),
    __MWORKS(version = "26.3.0"));
end RT1OfficialPidSysblockShadow50Hz;
