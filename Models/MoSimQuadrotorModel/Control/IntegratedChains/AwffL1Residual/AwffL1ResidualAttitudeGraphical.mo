within MoSimQuadrotorModel.Control.IntegratedChains.AwffL1Residual;
model AwffL1ResidualAttitudeGraphical
  "PID attitude inner loop"
  extends ModelWorkspace;
  import SysplorerEmbeddedCoder.Types.*;
  import BaseWorkspace.*;
  model ModelWorkspace
    annotation(__MWORKS(hide=true,BlockSystem(blockKind=BlockKind.modelWorkspace),version="26.3.0"));
  end ModelWorkspace;
  annotation(__MWORKS(version="26.3.0",modelType=Control,PortArrangement(Left(roll_ref,pitch_ref,yaw_ref,roll_mea,pitch_mea,yaw_mea),Right(roll_cmd,pitch_cmd,yaw_cmd)),BlockSystem(blockKind=BlockKind.userModel,SampleTime(auto=true,group="")=0.01,OutputInterval=0.02),SysblockVersion="1.0"),
    Icon(coordinateSystem(preserveAspectRatio=false),graphics={
      Rectangle(extent={{-100,-100},{100,100}},lineColor={120,70,35},fillColor={255,244,232},fillPattern=FillPattern.Solid,radius=8),
      Text(extent={{-90,28},{90,-6}},textString="PID",lineColor={80,45,20}),
      Text(extent={{-90,-12},{90,-46}},textString="Attitude",lineColor={80,45,20})}),
    Diagram(coordinateSystem(extent={{-220,-160},{220,160}},grid={2,2})));

  parameter Real kp_roll=14.142;
  parameter Real kd_roll=1.70;
  parameter Real kp_pitch=14.142;
  parameter Real kd_pitch=1.70;
  parameter Real kp_yaw=5.0;
  parameter Real attitude_derivative_filter_T=0.03;
  parameter Real attitude_cmd_limit=6.5;
  parameter Real yaw_cmd_limit=6.5;

  SysplorerEmbeddedCoder.Port.Inport roll_ref annotation(Placement(transformation(origin={-200,120},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport pitch_ref annotation(Placement(transformation(origin={-200,70},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport yaw_ref annotation(Placement(transformation(origin={-200,20},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport roll_mea annotation(Placement(transformation(origin={-200,-40},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport pitch_mea annotation(Placement(transformation(origin={-200,-90},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport yaw_mea annotation(Placement(transformation(origin={-200,-140},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport roll_cmd annotation(Placement(transformation(origin={200,90},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport pitch_cmd annotation(Placement(transformation(origin={200,0},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport yaw_cmd annotation(Placement(transformation(origin={200,-90},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));

  SysplorerEmbeddedCoder.MathOperation.Sum roll_error_sum(isSaturate=false,inputs="++") annotation(Placement(transformation(origin={-135,105},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(u1(Type(ref="double"),Dimension=1),u2(Type(ref="double"),Dimension=1)),y(Type(ref="double"),Dimension=1)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap),SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.MathOperation.Gain roll_kp_gain(k=kp_roll) annotation(Placement(transformation(origin={-65,125},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)),SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.MathOperation.Gain roll_kd_over_filter_gain(k=kd_roll / attitude_derivative_filter_T) annotation(Placement(transformation(origin={-65,85},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)),SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.MathOperation.Sum roll_cmd_raw_sum(isSaturate=false,inputs="++") annotation(Placement(transformation(origin={10,105},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(u1(Type(ref="double"),Dimension=1),u2(Type(ref="double"),Dimension=1)),y(Type(ref="double"),Dimension=1)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap),SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Discontinuities.Saturation roll_cmd_sat(upLimit=attitude_cmd_limit,lowLimit=-attitude_cmd_limit) annotation(Placement(transformation(origin={95,105},extent={{-10,-10},{10,10}})));

  SysplorerEmbeddedCoder.MathOperation.Sum pitch_error_sum(isSaturate=false,inputs="+-") annotation(Placement(transformation(origin={-135,25},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(u1(Type(ref="double"),Dimension=1),u2(Type(ref="double"),Dimension=1)),y(Type(ref="double"),Dimension=1)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap),SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.MathOperation.Gain pitch_kp_gain(k=kp_pitch) annotation(Placement(transformation(origin={-65,45},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)),SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.MathOperation.Gain pitch_kd_over_filter_gain(k=kd_pitch / attitude_derivative_filter_T) annotation(Placement(transformation(origin={-65,5},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)),SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.MathOperation.Sum pitch_cmd_raw_sum(isSaturate=false,inputs="++") annotation(Placement(transformation(origin={10,25},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(u1(Type(ref="double"),Dimension=1),u2(Type(ref="double"),Dimension=1)),y(Type(ref="double"),Dimension=1)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap),SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Discontinuities.Saturation pitch_cmd_sat(upLimit=attitude_cmd_limit,lowLimit=-attitude_cmd_limit) annotation(Placement(transformation(origin={95,25},extent={{-10,-10},{10,10}})));

  SysplorerEmbeddedCoder.MathOperation.Sum yaw_error_sum(isSaturate=false,inputs="+-") annotation(Placement(transformation(origin={-135,-85},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(u1(Type(ref="double"),Dimension=1),u2(Type(ref="double"),Dimension=1)),y(Type(ref="double"),Dimension=1)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap),SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.MathOperation.Gain yaw_kp_gain(k=kp_yaw) annotation(Placement(transformation(origin={-45,-85},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)),SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Discontinuities.Saturation yaw_cmd_sat(upLimit=yaw_cmd_limit,lowLimit=-yaw_cmd_limit) annotation(Placement(transformation(origin={95,-85},extent={{-10,-10},{10,10}})));

equation
  connect(roll_ref,roll_error_sum.u1) annotation(Line(points={{-190,120},{-160,120},{-160,111},{-147,111}},color={0,0,0}));
  connect(roll_mea,roll_error_sum.u2) annotation(Line(points={{-190,-40},{-170,-40},{-170,99},{-147,99}},color={0,0,0}));
  connect(roll_error_sum.y,roll_kp_gain.u) annotation(Line(points={{-123,105},{-100,105},{-100,125},{-77,125}},color={0,0,0}),__MWORKS(BlockSystem(NamedSignal)));
  connect(roll_error_sum.y,roll_kd_over_filter_gain.u) annotation(Line(points={{-123,105},{-100,105},{-100,85},{-77,85}},color={0,0,0}),__MWORKS(BlockSystem(NamedSignal)));
  connect(roll_kp_gain.y,roll_cmd_raw_sum.u1) annotation(Line(points={{-53,125},{-14,125},{-14,111},{-2,111}},color={0,0,0}));
  connect(roll_kd_over_filter_gain.y,roll_cmd_raw_sum.u2) annotation(Line(points={{-53,85},{-14,85},{-14,99},{-2,99}},color={0,0,0}));

  connect(pitch_ref,pitch_error_sum.u1) annotation(Line(points={{-190,70},{-160,70},{-160,31},{-147,31}},color={0,0,0}));
  connect(pitch_mea,pitch_error_sum.u2) annotation(Line(points={{-190,-90},{-170,-90},{-170,19},{-147,19}},color={0,0,0}));
  connect(pitch_error_sum.y,pitch_kp_gain.u) annotation(Line(points={{-123,25},{-100,25},{-100,45},{-77,45}},color={0,0,0}),__MWORKS(BlockSystem(NamedSignal)));
  connect(pitch_error_sum.y,pitch_kd_over_filter_gain.u) annotation(Line(points={{-123,25},{-100,25},{-100,5},{-77,5}},color={0,0,0}),__MWORKS(BlockSystem(NamedSignal)));
  connect(pitch_kp_gain.y,pitch_cmd_raw_sum.u1) annotation(Line(points={{-53,45},{-14,45},{-14,31},{-2,31}},color={0,0,0}));
  connect(pitch_kd_over_filter_gain.y,pitch_cmd_raw_sum.u2) annotation(Line(points={{-53,5},{-14,5},{-14,19},{-2,19}},color={0,0,0}));

  connect(yaw_ref,yaw_error_sum.u1) annotation(Line(points={{-190,20},{-160,20},{-160,-79},{-147,-79}},color={0,0,0}));
  connect(yaw_mea,yaw_error_sum.u2) annotation(Line(points={{-190,-140},{-170,-140},{-170,-91},{-147,-91}},color={0,0,0}));
  connect(yaw_error_sum.y,yaw_kp_gain.u) annotation(Line(points={{-123,-85},{-57,-85}},color={0,0,0}));
  connect(roll_cmd_raw_sum.y,roll_cmd_sat.u) annotation(Line(points={{22,105},{83,105}},color={0,0,0}));
  connect(pitch_cmd_raw_sum.y,pitch_cmd_sat.u) annotation(Line(points={{22,25},{83,25}},color={0,0,0}));
  connect(yaw_kp_gain.y,yaw_cmd_sat.u) annotation(Line(points={{-33,-85},{83,-85}},color={0,0,0}));
  connect(roll_cmd_sat.y,roll_cmd) annotation(Line(points={{107,105},{160,105},{160,90},{190,90}},color={0,0,0}));
  connect(pitch_cmd_sat.y,pitch_cmd) annotation(Line(points={{107,25},{160,25},{160,0},{190,0}},color={0,0,0}));
  connect(yaw_cmd_sat.y,yaw_cmd) annotation(Line(points={{107,-85},{160,-85},{160,-90},{190,-90}},color={0,0,0}));
end AwffL1ResidualAttitudeGraphical;