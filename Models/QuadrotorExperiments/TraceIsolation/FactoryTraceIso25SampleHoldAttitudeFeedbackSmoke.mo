within QuadrotorExperiments.TraceIsolation;
model FactoryTraceIso25SampleHoldAttitudeFeedbackSmoke
  "Attitude feedback bridge 25: sampled/held AngleMea feedback while preserving Iso23 display bridge"
  extends FactoryTraceIso23PositionSampleHoldBridgeSmoke(
    roll_estimated(y = attitude_hold[1].y),
    pitch_estimated(y = attitude_hold[2].y),
    yaw_estimated(y = attitude_hold[3].y));

  Modelica.Blocks.Discrete.Sampler attitude_sampler[3](
    each samplePeriod = 0.01,
    each startTime = 0.0);
  Modelica.Blocks.Discrete.ZeroOrderHold attitude_hold[3](
    each samplePeriod = 0.01,
    each startTime = 0.0);

  Real attitude_bridge_roll;
  Real attitude_bridge_pitch;
  Real attitude_bridge_yaw;

equation
  connect(sensors1_1.AngleMea, attitude_sampler.u);
  connect(attitude_sampler.y, attitude_hold.u);

  attitude_bridge_roll = attitude_hold[1].y;
  attitude_bridge_pitch = attitude_hold[2].y;
  attitude_bridge_yaw = attitude_hold[3].y;
  annotation(__MWORKS(hide=true));
end FactoryTraceIso25SampleHoldAttitudeFeedbackSmoke;
