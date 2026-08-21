within MoSimQuadrotorModel.Control.GeometricFlatness.DfbcBasic;
model DfbcBasicCore "dfbc_basic graphical control core"
  extends ModelWorkspace;
  import SysplorerEmbeddedCoder.Types.*;
  import BaseWorkspace.*;
  annotation(__MWORKS(version="26.3.0",modelType=Control,BlockSystem(blockKind=BlockKind.userModel,SampleTime(auto=true),OutputInterval=0.01),SysblockVersion="1.0"),experiment(Algorithm=Euler,Interval=0.01,IntegratorStep=0.01,StartTime=0,StopTime=0.2,StoreEventValue=0),Diagram(coordinateSystem(extent={{-560,-180},{560,180}},grid={2,2})));
  model ModelWorkspace
    annotation(__MWORKS(hide=true,BlockSystem(blockKind=BlockKind.modelWorkspace)));
  end ModelWorkspace;
  SysplorerEmbeddedCoder.Sources.Constant position_error_source(k=0.15) annotation(Placement(transformation(origin={-200,80},extent={{-20,-15},{20,15}})));
  SysplorerEmbeddedCoder.MathOperation.Gain position_feedback(k=1.5) annotation(Placement(transformation(origin={-80,80},extent={{-22,-16},{22,16}})));
  SysplorerEmbeddedCoder.Sources.Constant velocity_error_source(k=0.05) annotation(Placement(transformation(origin={-200,0},extent={{-20,-15},{20,15}})));
  SysplorerEmbeddedCoder.MathOperation.Gain velocity_feedback(k=2.0) annotation(Placement(transformation(origin={-80,0},extent={{-22,-16},{22,16}})));
  SysplorerEmbeddedCoder.Discrete.UnitDelay disturbance_state annotation(Placement(transformation(origin={-200,-80},extent={{-22,-16},{22,16}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap),SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.MathOperation.Gain disturbance_compensation(k=0.8) annotation(Placement(transformation(origin={-80,-80},extent={{-22,-16},{22,16}})));
  SysplorerEmbeddedCoder.MathOperation.Sum acceleration_sum(isSaturate=false,inputs="+++") annotation(Placement(transformation(origin={60,0},extent={{-22,-16},{22,16}})),__MWORKS(BlockSystem(Instance(u(u1(Type(ref="double"),Dimension=1),u2(Type(ref="double"),Dimension=1),u3(Type(ref="double"),Dimension=1)),y(Type(ref="double"),Dimension=1)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap),SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Discontinuities.Saturation command_limit(lowLimit=-4.0,upLimit=4.0) annotation(Placement(transformation(origin={190,0},extent={{-22,-16},{22,16}})));
  SysplorerEmbeddedCoder.Port.Outport command annotation(Placement(transformation(origin={280,20},extent={{-12,-10},{12,10}})));
equation
  connect(position_error_source.y, position_feedback.u) annotation(Line(points={{-180,80},{-102,80}},color={0,90,160},thickness=0.75));
  connect(velocity_error_source.y, velocity_feedback.u) annotation(Line(points={{-180,0},{-102,0}},color={0,90,160},thickness=0.75));
  connect(disturbance_state.y, disturbance_compensation.u) annotation(Line(points={{-178,-80},{-102,-80}},color={0,90,160},thickness=0.75));
  connect(position_feedback.y, acceleration_sum.u1) annotation(Line(points={{-58,80},{20,80},{20,8},{38,8}},color={0,90,160},thickness=0.75));
  connect(velocity_feedback.y, acceleration_sum.u2) annotation(Line(points={{-58,0},{38,0}},color={0,90,160},thickness=0.75));
  connect(disturbance_compensation.y, acceleration_sum.u3) annotation(Line(points={{-58,-80},{20,-80},{20,-8},{38,-8}},color={0,90,160},thickness=0.75));
  connect(acceleration_sum.y, command_limit.u) annotation(Line(points={{82,0},{168,0}},color={0,90,160},thickness=0.75));
  connect(command_limit.y, command) annotation(Line(points={{212,0},{240,0},{240,20},{268,20}},color={0,90,160},thickness=0.75));
end DfbcBasicCore;