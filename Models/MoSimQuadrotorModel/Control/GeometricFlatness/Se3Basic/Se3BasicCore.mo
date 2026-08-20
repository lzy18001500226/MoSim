within MoSimQuadrotorModel.Control.GeometricFlatness.Se3Basic;
model Se3BasicCore "se3_basic graphical control core"
  extends ModelWorkspace;
  import SysplorerEmbeddedCoder.Types.*;
  import BaseWorkspace.*;
  annotation(__MWORKS(version="26.3.0",modelType=Control,BlockSystem(blockKind=BlockKind.userModel,SampleTime(auto=true),OutputInterval=0.01),SysblockVersion="1.0"),experiment(Algorithm=Euler,Interval=0.01,IntegratorStep=0.01,StartTime=0,StopTime=0.2,StoreEventValue=0),Diagram(coordinateSystem(extent={{-560,-180},{560,180}},grid={2,2})));
  model ModelWorkspace
    annotation(__MWORKS(hide=true,BlockSystem(blockKind=BlockKind.modelWorkspace)));
  end ModelWorkspace;
  SysplorerEmbeddedCoder.Sources.Constant position_error_source(k=0.15) annotation(Placement(transformation(origin={-220,100},extent={{-20,-15},{20,15}})));
  SysplorerEmbeddedCoder.MathOperation.Gain geometric_position_error(k=1.5) annotation(Placement(transformation(origin={-100,100},extent={{-22,-16},{22,16}})));
  SysplorerEmbeddedCoder.Sources.Constant velocity_error_source(k=0.05) annotation(Placement(transformation(origin={-220,20},extent={{-20,-15},{20,15}})));
  SysplorerEmbeddedCoder.MathOperation.Gain geometric_velocity_error(k=2.0) annotation(Placement(transformation(origin={-100,20},extent={{-22,-16},{22,16}})));
  SysplorerEmbeddedCoder.MathOperation.Sum attitude_desired(isSaturate=false,inputs="++") annotation(Placement(transformation(origin={20,60},extent={{-22,-16},{22,16}})),__MWORKS(BlockSystem(Instance(u(u1(Type(ref="double"),Dimension=1),u2(Type(ref="double"),Dimension=1)),y(Type(ref="double"),Dimension=1)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap),SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Discontinuities.Saturation tilt_limit(lowLimit=-0.5,upLimit=0.5) annotation(Placement(transformation(origin={140,60},extent={{-22,-16},{22,16}})));
  SysplorerEmbeddedCoder.MathOperation.Gain attitude_projection(k=1.2) annotation(Placement(transformation(origin={260,60},extent={{-22,-16},{22,16}})));
  SysplorerEmbeddedCoder.Discontinuities.Saturation thrust_limit(lowLimit=-3.0,upLimit=3.0) annotation(Placement(transformation(origin={380,60},extent={{-22,-16},{22,16}})));
  SysplorerEmbeddedCoder.Port.Outport command annotation(Placement(transformation(origin={470,80},extent={{-12,-10},{12,10}})));
equation
  connect(position_error_source.y, geometric_position_error.u) annotation(Line(points={{-200,100},{-122,100}},color={0,90,160},thickness=0.75));
  connect(velocity_error_source.y, geometric_velocity_error.u) annotation(Line(points={{-200,20},{-122,20}},color={0,90,160},thickness=0.75));
  connect(geometric_position_error.y, attitude_desired.u1) annotation(Line(points={{-78,100},{-20,100},{-20,68},{-2,68}},color={0,90,160},thickness=0.75));
  connect(geometric_velocity_error.y, attitude_desired.u2) annotation(Line(points={{-78,20},{-20,20},{-20,52},{-2,52}},color={0,90,160},thickness=0.75));
  connect(attitude_desired.y, tilt_limit.u) annotation(Line(points={{42,60},{118,60}},color={0,90,160},thickness=0.75));
  connect(tilt_limit.y, attitude_projection.u) annotation(Line(points={{162,60},{238,60}},color={0,90,160},thickness=0.75));
  connect(attitude_projection.y, thrust_limit.u) annotation(Line(points={{282,60},{358,60}},color={0,90,160},thickness=0.75));
  connect(thrust_limit.y, command) annotation(Line(points={{402,60},{430,60},{430,80},{458,80}},color={0,90,160},thickness=0.75));
end Se3BasicCore;