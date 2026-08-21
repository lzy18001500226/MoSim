within MoSimQuadrotorModel.Control.IntegratedChains.LinearMpcL1Indi;
model LinearMpcL1IndiAttitudeGraphical
  "INDI-like incremental attitude inner loop"
  extends ModelWorkspace;
  import SysplorerEmbeddedCoder.Types.*;
  import BaseWorkspace.*;
  model ModelWorkspace
    annotation(__MWORKS(hide=true,BlockSystem(blockKind=BlockKind.modelWorkspace),version="26.3.0"));
  end ModelWorkspace;
  annotation(__MWORKS(version="26.3.0",modelType=Control,PortArrangement(Left(roll_ref,pitch_ref,yaw_ref,roll_mea,pitch_mea,yaw_mea),Right(roll_cmd,pitch_cmd,yaw_cmd)),BlockSystem(blockKind=BlockKind.userModel,SampleTime(auto=true,group="")=0.01,OutputInterval=0.02),SysblockVersion="1.0"),
    Icon(coordinateSystem(preserveAspectRatio=false),graphics={
      Rectangle(extent={{-100,-100},{100,100}},lineColor={130,65,135},fillColor={250,238,255},fillPattern=FillPattern.Solid,radius=8),
      Text(extent={{-90,28},{90,-6}},textString="INDI",lineColor={85,40,95}),
      Text(extent={{-90,-12},{90,-46}},textString="Attitude",lineColor={85,40,95})}),
    Diagram(coordinateSystem(extent={{-220,-160},{220,160}},grid={2,2})));
  parameter Real kp_roll=14.142;
  parameter Real kd_roll=1.70;
  parameter Real kp_pitch=14.142;
  parameter Real kd_pitch=1.70;
  parameter Real kp_yaw=5.0;
  parameter Real attitude_cmd_limit=6.5;
  parameter Real yaw_cmd_limit=6.5;
  parameter Real attitude_rate_filter_T=0.035;
  parameter Real angular_accel_filter_T=0.08;
  parameter Real indi_roll_gain=0.015;
  parameter Real indi_pitch_gain=0.015;
  parameter Real indi_yaw_gain=0.005;
  parameter Real indi_increment_limit=0.15;
  parameter Real attitude_feedback_blend=1.00;
  SysplorerEmbeddedCoder.Port.Inport roll_ref annotation(Placement(transformation(origin={-200,120},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport pitch_ref annotation(Placement(transformation(origin={-200,70},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport yaw_ref annotation(Placement(transformation(origin={-200,20},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport roll_mea annotation(Placement(transformation(origin={-200,-40},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport pitch_mea annotation(Placement(transformation(origin={-200,-90},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport yaw_mea annotation(Placement(transformation(origin={-200,-140},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport roll_cmd annotation(Placement(transformation(origin={200,90},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport pitch_cmd annotation(Placement(transformation(origin={200,0},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport yaw_cmd annotation(Placement(transformation(origin={200,-90},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.MathOperation.Sum roll_error_sum(isSaturate=false,inputs="++") annotation(Placement(transformation(origin={-135,110},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(u1(Type(ref="double"),Dimension=1),u2(Type(ref="double"),Dimension=1)),y(Type(ref="double"),Dimension=1)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap),SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.MathOperation.Gain roll_kp_gain(k=kp_roll) annotation(Placement(transformation(origin={-70,130},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)),SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.MathOperation.Gain roll_kd_over_rate_gain(k=kd_roll / attitude_rate_filter_T) annotation(Placement(transformation(origin={-70,90},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)),SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.MathOperation.Sum roll_raw_sum(isSaturate=false,inputs="++") annotation(Placement(transformation(origin={-5,110},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(u1(Type(ref="double"),Dimension=1),u2(Type(ref="double"),Dimension=1)),y(Type(ref="double"),Dimension=1)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap),SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.MathOperation.Gain roll_feedback_gain(k=attitude_feedback_blend) annotation(Placement(transformation(origin={50,125},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)),SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.MathOperation.Gain roll_indi_gain_block(k=indi_roll_gain) annotation(Placement(transformation(origin={50,95},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)),SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.MathOperation.Sum roll_indi_sum(isSaturate=false,inputs="+++") annotation(Placement(transformation(origin={135,110},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(u1(Type(ref="double"),Dimension=1),u2(Type(ref="double"),Dimension=1),u3(Type(ref="double"),Dimension=1)),y(Type(ref="double"),Dimension=1)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap),SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Discrete.UnitDelay roll_cmd_delay(initCond=0) annotation(Placement(transformation(origin={88,70},extent={{-10,-10},{10,10}})));
  SysplorerEmbeddedCoder.Discontinuities.Saturation roll_cmd_sat(upLimit=attitude_cmd_limit,lowLimit=-attitude_cmd_limit) annotation(Placement(transformation(origin={165,110},extent={{-10,-10},{10,10}})));

  SysplorerEmbeddedCoder.MathOperation.Sum pitch_error_sum(isSaturate=false,inputs="+-") annotation(Placement(transformation(origin={-135,20},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(u1(Type(ref="double"),Dimension=1),u2(Type(ref="double"),Dimension=1)),y(Type(ref="double"),Dimension=1)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap),SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.MathOperation.Gain pitch_kp_gain(k=kp_pitch) annotation(Placement(transformation(origin={-70,40},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)),SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.MathOperation.Gain pitch_kd_over_rate_gain(k=kd_pitch / attitude_rate_filter_T) annotation(Placement(transformation(origin={-70,0},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)),SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.MathOperation.Sum pitch_raw_sum(isSaturate=false,inputs="++") annotation(Placement(transformation(origin={-5,20},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(u1(Type(ref="double"),Dimension=1),u2(Type(ref="double"),Dimension=1)),y(Type(ref="double"),Dimension=1)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap),SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.MathOperation.Gain pitch_feedback_gain(k=attitude_feedback_blend) annotation(Placement(transformation(origin={50,35},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)),SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.MathOperation.Gain pitch_indi_gain_block(k=indi_pitch_gain) annotation(Placement(transformation(origin={50,5},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)),SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.MathOperation.Sum pitch_indi_sum(isSaturate=false,inputs="+++") annotation(Placement(transformation(origin={135,20},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(u1(Type(ref="double"),Dimension=1),u2(Type(ref="double"),Dimension=1),u3(Type(ref="double"),Dimension=1)),y(Type(ref="double"),Dimension=1)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap),SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Discrete.UnitDelay pitch_cmd_delay(initCond=0) annotation(Placement(transformation(origin={88,-20},extent={{-10,-10},{10,10}})));
  SysplorerEmbeddedCoder.Discontinuities.Saturation pitch_cmd_sat(upLimit=attitude_cmd_limit,lowLimit=-attitude_cmd_limit) annotation(Placement(transformation(origin={165,20},extent={{-10,-10},{10,10}})));

  SysplorerEmbeddedCoder.MathOperation.Sum yaw_error_sum(isSaturate=false,inputs="+-") annotation(Placement(transformation(origin={-135,-100},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(u1(Type(ref="double"),Dimension=1),u2(Type(ref="double"),Dimension=1)),y(Type(ref="double"),Dimension=1)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap),SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.MathOperation.Gain yaw_kp_gain(k=kp_yaw) annotation(Placement(transformation(origin={-70,-100},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)),SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.MathOperation.Gain yaw_feedback_gain(k=attitude_feedback_blend) annotation(Placement(transformation(origin={5,-85},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)),SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.MathOperation.Gain yaw_indi_gain_block(k=indi_yaw_gain) annotation(Placement(transformation(origin={5,-115},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)),SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.MathOperation.Sum yaw_indi_sum(isSaturate=false,inputs="+++") annotation(Placement(transformation(origin={110,-100},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(u1(Type(ref="double"),Dimension=1),u2(Type(ref="double"),Dimension=1),u3(Type(ref="double"),Dimension=1)),y(Type(ref="double"),Dimension=1)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap),SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Discrete.UnitDelay yaw_cmd_delay(initCond=0) annotation(Placement(transformation(origin={62,-140},extent={{-10,-10},{10,10}})));
  SysplorerEmbeddedCoder.Discontinuities.Saturation yaw_cmd_sat(upLimit=yaw_cmd_limit,lowLimit=-yaw_cmd_limit) annotation(Placement(transformation(origin={145,-100},extent={{-10,-10},{10,10}})));
equation
  connect(roll_ref,roll_error_sum.u1) annotation(Line(points={{-190,120},{-160,120},{-160,116},{-147,116}},color={0,0,0}));
  connect(roll_mea,roll_error_sum.u2) annotation(Line(points={{-190,-40},{-170,-40},{-170,104},{-147,104}},color={0,0,0}));
  connect(roll_error_sum.y,roll_kp_gain.u) annotation(Line(points={{-123,110},{-100,110},{-100,130},{-82,130}},color={0,0,0}),__MWORKS(BlockSystem(NamedSignal)));
  connect(roll_error_sum.y,roll_kd_over_rate_gain.u) annotation(Line(points={{-123,110},{-100,110},{-100,90},{-82,90}},color={0,0,0}),__MWORKS(BlockSystem(NamedSignal)));
  connect(roll_kp_gain.y,roll_raw_sum.u1) annotation(Line(points={{-58,130},{-26,130},{-26,116},{-17,116}},color={0,0,0}));
  connect(roll_kd_over_rate_gain.y,roll_raw_sum.u2) annotation(Line(points={{-58,90},{-26,90},{-26,104},{-17,104}},color={0,0,0}));
  connect(roll_raw_sum.y,roll_feedback_gain.u) annotation(Line(points={{7,110},{24,110},{24,125},{38,125}},color={0,0,0}),__MWORKS(BlockSystem(NamedSignal)));
  connect(roll_raw_sum.y,roll_indi_gain_block.u) annotation(Line(points={{7,110},{24,110},{24,95},{38,95}},color={0,0,0}),__MWORKS(BlockSystem(NamedSignal)));
  connect(roll_feedback_gain.y,roll_indi_sum.u1) annotation(Line(points={{62,125},{116,125},{116,116},{123,116}},color={0,0,0}));
  connect(roll_indi_gain_block.y,roll_indi_sum.u2) annotation(Line(points={{62,95},{116,95},{116,104},{123,104}},color={0,0,0}));
  connect(roll_cmd_delay.y,roll_indi_sum.u3) annotation(Line(points={{100,70},{116,70},{116,104},{123,104}},color={0,0,0}));

  connect(pitch_ref,pitch_error_sum.u1) annotation(Line(points={{-190,70},{-160,70},{-160,26},{-147,26}},color={0,0,0}));
  connect(pitch_mea,pitch_error_sum.u2) annotation(Line(points={{-190,-90},{-170,-90},{-170,14},{-147,14}},color={0,0,0}));
  connect(pitch_error_sum.y,pitch_kp_gain.u) annotation(Line(points={{-123,20},{-100,20},{-100,40},{-82,40}},color={0,0,0}),__MWORKS(BlockSystem(NamedSignal)));
  connect(pitch_error_sum.y,pitch_kd_over_rate_gain.u) annotation(Line(points={{-123,20},{-100,20},{-100,0},{-82,0}},color={0,0,0}),__MWORKS(BlockSystem(NamedSignal)));
  connect(pitch_kp_gain.y,pitch_raw_sum.u1) annotation(Line(points={{-58,40},{-26,40},{-26,26},{-17,26}},color={0,0,0}));
  connect(pitch_kd_over_rate_gain.y,pitch_raw_sum.u2) annotation(Line(points={{-58,0},{-26,0},{-26,14},{-17,14}},color={0,0,0}));
  connect(pitch_raw_sum.y,pitch_feedback_gain.u) annotation(Line(points={{7,20},{24,20},{24,35},{38,35}},color={0,0,0}),__MWORKS(BlockSystem(NamedSignal)));
  connect(pitch_raw_sum.y,pitch_indi_gain_block.u) annotation(Line(points={{7,20},{24,20},{24,5},{38,5}},color={0,0,0}),__MWORKS(BlockSystem(NamedSignal)));
  connect(pitch_feedback_gain.y,pitch_indi_sum.u1) annotation(Line(points={{62,35},{116,35},{116,26},{123,26}},color={0,0,0}));
  connect(pitch_indi_gain_block.y,pitch_indi_sum.u2) annotation(Line(points={{62,5},{116,5},{116,14},{123,14}},color={0,0,0}));
  connect(pitch_cmd_delay.y,pitch_indi_sum.u3) annotation(Line(points={{100,-20},{116,-20},{116,14},{123,14}},color={0,0,0}));

  connect(yaw_ref,yaw_error_sum.u1) annotation(Line(points={{-190,20},{-160,20},{-160,-94},{-147,-94}},color={0,0,0}));
  connect(yaw_mea,yaw_error_sum.u2) annotation(Line(points={{-190,-140},{-170,-140},{-170,-106},{-147,-106}},color={0,0,0}));
  connect(yaw_error_sum.y,yaw_kp_gain.u) annotation(Line(points={{-123,-100},{-82,-100}},color={0,0,0}));
  connect(yaw_kp_gain.y,yaw_feedback_gain.u) annotation(Line(points={{-58,-100},{-30,-100},{-30,-85},{-7,-85}},color={0,0,0}),__MWORKS(BlockSystem(NamedSignal)));
  connect(yaw_kp_gain.y,yaw_indi_gain_block.u) annotation(Line(points={{-58,-100},{-30,-100},{-30,-115},{-7,-115}},color={0,0,0}),__MWORKS(BlockSystem(NamedSignal)));
  connect(yaw_feedback_gain.y,yaw_indi_sum.u1) annotation(Line(points={{17,-85},{86,-85},{86,-94},{98,-94}},color={0,0,0}));
  connect(yaw_indi_gain_block.y,yaw_indi_sum.u2) annotation(Line(points={{17,-115},{86,-115},{86,-106},{98,-106}},color={0,0,0}));
  connect(yaw_cmd_delay.y,yaw_indi_sum.u3) annotation(Line(points={{74,-140},{86,-140},{86,-106},{98,-106}},color={0,0,0}));
  connect(roll_indi_sum.y,roll_cmd_sat.u) annotation(Line(points={{147,110},{153,110}},color={0,0,0}));
  connect(pitch_indi_sum.y,pitch_cmd_sat.u) annotation(Line(points={{147,20},{153,20}},color={0,0,0}));
  connect(yaw_indi_sum.y,yaw_cmd_sat.u) annotation(Line(points={{122,-100},{133,-100}},color={0,0,0}));
  connect(roll_cmd_sat.y,roll_cmd) annotation(Line(points={{177,110},{180,110},{180,90},{190,90}},color={0,0,0}));
  connect(pitch_cmd_sat.y,pitch_cmd) annotation(Line(points={{177,20},{180,20},{180,0},{190,0}},color={0,0,0}));
  connect(yaw_cmd_sat.y,yaw_cmd) annotation(Line(points={{157,-100},{180,-100},{180,-90},{190,-90}},color={0,0,0}));
  connect(roll_cmd_sat.y,roll_cmd_delay.u1) annotation(Line(points={{177,110},{184,110},{184,70},{100,70}},color={0,0,0}));
  connect(pitch_cmd_sat.y,pitch_cmd_delay.u1) annotation(Line(points={{177,20},{184,20},{184,-20},{100,-20}},color={0,0,0}));
  connect(yaw_cmd_sat.y,yaw_cmd_delay.u1) annotation(Line(points={{157,-100},{170,-100},{170,-140},{74,-140}},color={0,0,0}));
end LinearMpcL1IndiAttitudeGraphical;