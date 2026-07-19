model MoSim_G9_PID_INDI_GRAPHICAL_OVERVIEW "PID_INDI readable algorithm topology"
  extends ModelWorkspace;
  import SysplorerEmbeddedCoder.Types.*;
  import BaseWorkspace.*;
  annotation(__MWORKS(version="26.3.0",modelType=Control,BlockSystem(blockKind=BlockKind.userModel,SampleTime(auto=true),OutputInterval=0.01),SysblockVersion="1.0"),experiment(Algorithm=Euler,Interval=0.01,IntegratorStep=0.01,StartTime=0,StopTime=0.20,StoreEventValue=0),Diagram(coordinateSystem(extent={{-560,-180},{560,180}},grid={2,2})));
  SysplorerEmbeddedCoder.Sources.Constant position_error_source(k=0.15) annotation(Placement(transformation(origin={-480,100},extent={{-14,-11},{14,11}})));
  SysplorerEmbeddedCoder.Sources.Constant velocity_error_source(k=-0.03) annotation(Placement(transformation(origin={-480,0},extent={{-14,-11},{14,11}})));
  SysplorerEmbeddedCoder.Sources.Constant auxiliary_source(k=0.02) annotation(Placement(transformation(origin={-480,-100},extent={{-14,-11},{14,11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain pid_position(k=1.5) annotation(Placement(transformation(origin={-220,100},extent={{-22,-16},{22,16}})));
  SysplorerEmbeddedCoder.MathOperation.Gain pid_velocity(k=1.5) annotation(Placement(transformation(origin={-220,0},extent={{-22,-16},{22,16}})));
  SysplorerEmbeddedCoder.MathOperation.Sum pid_command(isSaturate=false,inputs="++") annotation(Placement(transformation(origin={-70,50},extent={{-22,-16},{22,16}})),__MWORKS(BlockSystem(Instance(u(u1(Type(ref="double"),Dimension=1),u2(Type(ref="double"),Dimension=1)),y(Type(ref="double"),Dimension=1)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap),SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.MathOperation.Sum acceleration_residual(isSaturate=false,inputs="+-") annotation(Placement(transformation(origin={70,-50},extent={{-22,-16},{22,16}})),__MWORKS(BlockSystem(Instance(u(u1(Type(ref="double"),Dimension=1),u2(Type(ref="double"),Dimension=1)),y(Type(ref="double"),Dimension=1)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap),SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.MathOperation.Gain indi_gain(k=0.12) annotation(Placement(transformation(origin={190,-50},extent={{-22,-16},{22,16}})));
  SysplorerEmbeddedCoder.Discontinuities.Saturation indi_increment_limit(lowLimit=-0.35,upLimit=0.35) annotation(Placement(transformation(origin={310,-50},extent={{-22,-16},{22,16}})));
  SysplorerEmbeddedCoder.MathOperation.Sum augmented_command(isSaturate=false,inputs="++") annotation(Placement(transformation(origin={430,20},extent={{-22,-16},{22,16}})),__MWORKS(BlockSystem(Instance(u(u1(Type(ref="double"),Dimension=1),u2(Type(ref="double"),Dimension=1)),y(Type(ref="double"),Dimension=1)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap),SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport command annotation(Placement(transformation(origin={520,20},extent={{-12,-10},{12,10}})));
  model ModelWorkspace
    annotation(__MWORKS(hide=true,BlockSystem(blockKind=BlockKind.modelWorkspace)));
  end ModelWorkspace;
equation
  connect(position_error_source.y, pid_position.u) annotation(Line(points={{-466,100},{-242,100}},color={0,90,160},thickness=0.75));
  connect(velocity_error_source.y, pid_velocity.u) annotation(Line(points={{-466,0},{-242,0}},color={0,90,160},thickness=0.75));
  connect(pid_position.y, pid_command.u1) annotation(Line(points={{-198,100},{-130,100},{-130,58},{-92,58}},color={0,90,160},thickness=0.75));
  connect(pid_velocity.y, pid_command.u2) annotation(Line(points={{-198,0},{-130,0},{-130,42},{-92,42}},color={0,90,160},thickness=0.75));
  connect(pid_command.y, acceleration_residual.u1) annotation(Line(points={{-48,50},{0,50},{0,-42},{48,-42}},color={0,90,160},thickness=0.75));
  connect(auxiliary_source.y, acceleration_residual.u2) annotation(Line(points={{-466,-100},{0,-100},{0,-58},{48,-58}},color={0,90,160},thickness=0.75));
  connect(acceleration_residual.y, indi_gain.u) annotation(Line(points={{92,-50},{168,-50}},color={0,90,160},thickness=0.75));
  connect(indi_gain.y, indi_increment_limit.u) annotation(Line(points={{212,-50},{288,-50}},color={0,90,160},thickness=0.75));
  connect(pid_command.y, augmented_command.u1) annotation(Line(points={{-48,50},{370,50},{370,28},{408,28}},color={0,90,160},thickness=0.75));
  connect(indi_increment_limit.y, augmented_command.u2) annotation(Line(points={{332,-50},{370,-50},{370,12},{408,12}},color={0,90,160},thickness=0.75));
  connect(augmented_command.y, command) annotation(Line(points={{452,20},{508,20}},color={0,90,160},thickness=0.75));
end MoSim_G9_PID_INDI_GRAPHICAL_OVERVIEW;