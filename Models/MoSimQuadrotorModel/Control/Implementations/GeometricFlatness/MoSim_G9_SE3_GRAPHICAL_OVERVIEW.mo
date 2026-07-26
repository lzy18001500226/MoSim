within MoSimQuadrotorModel.Control.Implementations.GeometricFlatness;
model MoSim_G9_SE3_GRAPHICAL_OVERVIEW "SE3 readable algorithm topology"
  extends ModelWorkspace;
  import SysplorerEmbeddedCoder.Types.*;
  import BaseWorkspace.*;
  annotation(__MWORKS(version="26.3.0",modelType=Control,BlockSystem(blockKind=BlockKind.userModel,SampleTime(auto=true),OutputInterval=0.01),SysblockVersion="1.0"),experiment(Algorithm=Euler,Interval=0.01,IntegratorStep=0.01,StartTime=0,StopTime=0.2,StoreEventValue=0),Diagram(coordinateSystem(extent={{-560,-180},{560,180}},grid={2,2})));
  SysplorerEmbeddedCoder.Sources.Constant position_error_source(k=0.15) annotation(Placement(transformation(origin={-480,100},extent={{-14,-11},{14,11}})));
  SysplorerEmbeddedCoder.Sources.Constant velocity_error_source(k=-0.03) annotation(Placement(transformation(origin={-480,0},extent={{-14,-11},{14,11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain geometric_position_error(k=1.5) annotation(Placement(transformation(origin={-220,100},extent={{-22,-16},{22,16}})));
  SysplorerEmbeddedCoder.MathOperation.Gain geometric_velocity_error(k=1.5) annotation(Placement(transformation(origin={-220,0},extent={{-22,-16},{22,16}})));
  SysplorerEmbeddedCoder.MathOperation.Sum desired_force(isSaturate=false,inputs="++") annotation(Placement(transformation(origin={-70,50},extent={{-22,-16},{22,16}})),__MWORKS(BlockSystem(Instance(u(u1(Type(ref="double"),Dimension=1),u2(Type(ref="double"),Dimension=1)),y(Type(ref="double"),Dimension=1)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap),SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Discontinuities.Saturation tilt_limit(lowLimit=-0.5236,upLimit=0.5236) annotation(Placement(transformation(origin={80,50},extent={{-22,-16},{22,16}})));
  SysplorerEmbeddedCoder.MathOperation.Gain attitude_projection(k=1.0) annotation(Placement(transformation(origin={220,50},extent={{-22,-16},{22,16}})));
  SysplorerEmbeddedCoder.Discontinuities.Saturation thrust_limit(lowLimit=0.0,upLimit=1.0) annotation(Placement(transformation(origin={380,50},extent={{-22,-16},{22,16}})));
  SysplorerEmbeddedCoder.Port.Outport command annotation(Placement(transformation(origin={520,20},extent={{-12,-10},{12,10}})));
  model ModelWorkspace
    annotation(__MWORKS(hide=true,BlockSystem(blockKind=BlockKind.modelWorkspace)));
  end ModelWorkspace;
equation
  connect(position_error_source.y, geometric_position_error.u) annotation(Line(points={{-466,100},{-242,100}},color={0,90,160},thickness=0.75));
  connect(velocity_error_source.y, geometric_velocity_error.u) annotation(Line(points={{-466,0},{-242,0}},color={0,90,160},thickness=0.75));
  connect(geometric_position_error.y, desired_force.u1) annotation(Line(points={{-198,100},{-130,100},{-130,58},{-92,58}},color={0,90,160},thickness=0.75));
  connect(geometric_velocity_error.y, desired_force.u2) annotation(Line(points={{-198,0},{-130,0},{-130,42},{-92,42}},color={0,90,160},thickness=0.75));
  connect(desired_force.y, tilt_limit.u) annotation(Line(points={{-48,50},{58,50}},color={0,90,160},thickness=0.75));
  connect(tilt_limit.y, attitude_projection.u) annotation(Line(points={{102,50},{198,50}},color={0,90,160},thickness=0.75));
  connect(attitude_projection.y, thrust_limit.u) annotation(Line(points={{242,50},{358,50}},color={0,90,160},thickness=0.75));
  connect(thrust_limit.y, command) annotation(Line(points={{402,50},{470,50},{470,20},{508,20}},color={0,90,160},thickness=0.75));
end MoSim_G9_SE3_GRAPHICAL_OVERVIEW;
