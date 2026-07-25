within MoSimQuadrotorModel.Controllers.GraphicalMIL.Optimization;
model MoSim_G9_NMPC_OUTER_GRAPHICAL_OVERVIEW "NMPC_OUTER readable algorithm topology"
  extends ModelWorkspace;
  import SysplorerEmbeddedCoder.Types.*;
  import BaseWorkspace.*;
  annotation(__MWORKS(version="26.3.0",modelType=Control,BlockSystem(blockKind=BlockKind.userModel,SampleTime(auto=true),OutputInterval=0.01),SysblockVersion="1.0"),experiment(Algorithm=Euler,Interval=0.01,IntegratorStep=0.01,StartTime=0,StopTime=0.2,StoreEventValue=0),Diagram(coordinateSystem(extent={{-560,-180},{560,180}},grid={2,2})));
  SysplorerEmbeddedCoder.Sources.Constant position_error_source(k=0.15) annotation(Placement(transformation(origin={-480,100},extent={{-14,-11},{14,11}})));
  SysplorerEmbeddedCoder.Sources.Constant velocity_error_source(k=-0.03) annotation(Placement(transformation(origin={-480,0},extent={{-14,-11},{14,11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain position_prediction(k=0.25) annotation(Placement(transformation(origin={-220,100},extent={{-22,-16},{22,16}})));
  SysplorerEmbeddedCoder.MathOperation.Gain velocity_prediction(k=0.25) annotation(Placement(transformation(origin={-220,0},extent={{-22,-16},{22,16}})));
  SysplorerEmbeddedCoder.MathOperation.Sum horizon_state(isSaturate=false,inputs="++") annotation(Placement(transformation(origin={-70,50},extent={{-22,-16},{22,16}})),__MWORKS(BlockSystem(Instance(u(u1(Type(ref="double"),Dimension=1),u2(Type(ref="double"),Dimension=1)),y(Type(ref="double"),Dimension=1)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap),SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.MathOperation.Gain quadratic_optimizer(k=3.2) annotation(Placement(transformation(origin={80,50},extent={{-22,-16},{22,16}})));
  SysplorerEmbeddedCoder.Discrete.UnitDelay previous_command(initCond=0.0) annotation(Placement(transformation(origin={80,-80},extent={{-22,-16},{22,16}})));
  SysplorerEmbeddedCoder.MathOperation.Sum command_increment(isSaturate=false,inputs="+-") annotation(Placement(transformation(origin={220,20},extent={{-22,-16},{22,16}})),__MWORKS(BlockSystem(Instance(u(u1(Type(ref="double"),Dimension=1),u2(Type(ref="double"),Dimension=1)),y(Type(ref="double"),Dimension=1)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap),SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Discontinuities.Saturation increment_limit(lowLimit=-1.2,upLimit=1.2) annotation(Placement(transformation(origin={340,20},extent={{-22,-16},{22,16}})));
  SysplorerEmbeddedCoder.Discontinuities.Saturation acceleration_limit(lowLimit=-4.0,upLimit=4.0) annotation(Placement(transformation(origin={460,20},extent={{-22,-16},{22,16}})));
  SysplorerEmbeddedCoder.Port.Outport command annotation(Placement(transformation(origin={520,20},extent={{-12,-10},{12,10}})));
  model ModelWorkspace
    annotation(__MWORKS(hide=true,BlockSystem(blockKind=BlockKind.modelWorkspace)));
  end ModelWorkspace;
equation
  connect(position_error_source.y, position_prediction.u) annotation(Line(points={{-466,100},{-242,100}},color={0,90,160},thickness=0.75));
  connect(velocity_error_source.y, velocity_prediction.u) annotation(Line(points={{-466,0},{-242,0}},color={0,90,160},thickness=0.75));
  connect(position_prediction.y, horizon_state.u1) annotation(Line(points={{-198,100},{-130,100},{-130,58},{-92,58}},color={0,90,160},thickness=0.75));
  connect(velocity_prediction.y, horizon_state.u2) annotation(Line(points={{-198,0},{-130,0},{-130,42},{-92,42}},color={0,90,160},thickness=0.75));
  connect(horizon_state.y, quadratic_optimizer.u) annotation(Line(points={{-48,50},{58,50}},color={0,90,160},thickness=0.75));
  connect(previous_command.y, command_increment.u2) annotation(Line(points={{102,-80},{160,-80},{160,12},{198,12}},color={0,90,160},thickness=0.75));
  connect(quadratic_optimizer.y, command_increment.u1) annotation(Line(points={{102,50},{160,50},{160,28},{198,28}},color={0,90,160},thickness=0.75));
  connect(command_increment.y, increment_limit.u) annotation(Line(points={{242,20},{318,20}},color={0,90,160},thickness=0.75));
  connect(increment_limit.y, previous_command.u1) annotation(Line(points={{362,20},{380,20},{380,-120},{40,-120},{40,-80},{58,-80}},color={0,90,160},thickness=0.75));
  connect(increment_limit.y, acceleration_limit.u) annotation(Line(points={{362,20},{438,20}},color={0,90,160},thickness=0.75));
  connect(acceleration_limit.y, command) annotation(Line(points={{482,20},{508,20}},color={0,90,160},thickness=0.75));
end MoSim_G9_NMPC_OUTER_GRAPHICAL_OVERVIEW;