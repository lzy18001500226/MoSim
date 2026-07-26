within MoSimQuadrotorModel.Visualization.Diagnostics;
model FactoryTraceIso23PositionSampleHoldBridgeSmoke
  "Position bridge 23: sampled/held sensor position feeds display actual_position through inherited bridge"
  extends FactoryTraceIso21ControllerRateAliasSmoke(
    actual_position(y = display_position_hold.y));

  Modelica.Blocks.Discrete.Sampler display_position_sampler[3](
    each samplePeriod = 0.01,
    each startTime = 0.0);
  Modelica.Blocks.Discrete.ZeroOrderHold display_position_hold[3](
    each samplePeriod = 0.01,
    each startTime = 0.0);

  Real display_actual_x;
  Real display_actual_y;
  Real display_actual_z;
  Real display_reference_x;
  Real display_reference_y;
  Real display_reference_z;
  Real display_bridge_x;
  Real display_bridge_y;
  Real display_bridge_z;

equation
  connect(sensors1_1.PosMea, display_position_sampler.u);
  connect(display_position_sampler.y, display_position_hold.u);

  display_actual_x = sensors1_1.PosMea[1];
  display_actual_y = sensors1_1.PosMea[2];
  display_actual_z = sensors1_1.PosMea[3];
  display_reference_x = planningReference.position_command[1];
  display_reference_y = planningReference.position_command[2];
  display_reference_z = planningReference.position_command[3];
  display_bridge_x = display_position_hold[1].y;
  display_bridge_y = display_position_hold[2].y;
  display_bridge_z = display_position_hold[3].y;
  annotation(__MWORKS(hide=true,version="26.3.0"));
end FactoryTraceIso23PositionSampleHoldBridgeSmoke;