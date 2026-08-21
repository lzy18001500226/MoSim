within MoSimQuadrotorModel.Control.IntegratedChains.AwffL1Indi;
model AwffL1IndiMotorMixerGraphical
  "Quadrotor motor mixer"
  extends ModelWorkspace;
  import SysplorerEmbeddedCoder.Types.*;
  import BaseWorkspace.*;
  model ModelWorkspace
    annotation(__MWORKS(hide=true,BlockSystem(blockKind=BlockKind.modelWorkspace),version="26.3.0"));
  end ModelWorkspace;
  annotation(__MWORKS(version="26.3.0",modelType=Control,PortArrangement(Left(thrust_ref,roll_cmd,pitch_cmd,yaw_cmd),Right(y,y1,y2,y3)),BlockSystem(blockKind=BlockKind.userModel,SampleTime(auto=true,group="")=0.01,OutputInterval=0.02),SysblockVersion="1.0"),
    Icon(coordinateSystem(preserveAspectRatio=false),graphics={
      Rectangle(extent={{-100,-100},{100,100}},lineColor={60,110,80},fillColor={238,250,242},fillPattern=FillPattern.Solid,radius=8),
      Text(extent={{-90,26},{90,-8}},textString="Motor",lineColor={30,75,50}),
      Text(extent={{-90,-12},{90,-46}},textString="Mixer",lineColor={30,75,50})}),
    Diagram(coordinateSystem(extent={{-220,-140},{220,140}},grid={2,2})));

  parameter Real output_limit=20.0;
  SysplorerEmbeddedCoder.Port.Inport thrust_ref annotation(Placement(transformation(origin={-200,90},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport roll_cmd annotation(Placement(transformation(origin={-200,30},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport pitch_cmd annotation(Placement(transformation(origin={-200,-30},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport yaw_cmd annotation(Placement(transformation(origin={-200,-90},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport y annotation(Placement(transformation(origin={200,90},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport y1 annotation(Placement(transformation(origin={200,30},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport y2 annotation(Placement(transformation(origin={200,-30},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport y3 annotation(Placement(transformation(origin={200,-90},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));

  SysplorerEmbeddedCoder.MathOperation.Gain roll_pos(k=0.707) annotation(Placement(transformation(origin={-130,65},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)),SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.MathOperation.Gain roll_neg(k=-0.707) annotation(Placement(transformation(origin={-130,40},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)),SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.MathOperation.Gain pitch_pos(k=0.707) annotation(Placement(transformation(origin={-130,-5},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)),SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.MathOperation.Gain pitch_neg(k=-0.707) annotation(Placement(transformation(origin={-130,-30},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)),SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.MathOperation.Gain yaw_pos(k=0.707) annotation(Placement(transformation(origin={-130,-75},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)),SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.MathOperation.Gain yaw_neg(k=-0.707) annotation(Placement(transformation(origin={-130,-100},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)),SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.MathOperation.Gain thrust_neg(k=-1.0) annotation(Placement(transformation(origin={-130,110},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)),SampleTime(group="D1")=0.01)));

  SysplorerEmbeddedCoder.MathOperation.Sum motor1_sum(isSaturate=false,inputs="++++") annotation(Placement(transformation(origin={20,90},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(u1(Type(ref="double"),Dimension=1),u2(Type(ref="double"),Dimension=1),u3(Type(ref="double"),Dimension=1),u4(Type(ref="double"),Dimension=1)),y(Type(ref="double"),Dimension=1)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap),SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.MathOperation.Sum motor2_sum(isSaturate=false,inputs="++++") annotation(Placement(transformation(origin={20,30},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(u1(Type(ref="double"),Dimension=1),u2(Type(ref="double"),Dimension=1),u3(Type(ref="double"),Dimension=1),u4(Type(ref="double"),Dimension=1)),y(Type(ref="double"),Dimension=1)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap),SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.MathOperation.Sum motor3_sum(isSaturate=false,inputs="++++") annotation(Placement(transformation(origin={20,-30},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(u1(Type(ref="double"),Dimension=1),u2(Type(ref="double"),Dimension=1),u3(Type(ref="double"),Dimension=1),u4(Type(ref="double"),Dimension=1)),y(Type(ref="double"),Dimension=1)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap),SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.MathOperation.Sum motor4_sum(isSaturate=false,inputs="++++") annotation(Placement(transformation(origin={20,-90},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(u1(Type(ref="double"),Dimension=1),u2(Type(ref="double"),Dimension=1),u3(Type(ref="double"),Dimension=1),u4(Type(ref="double"),Dimension=1)),y(Type(ref="double"),Dimension=1)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap),SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Discontinuities.Saturation motor1_sat(upLimit=output_limit,lowLimit=-output_limit) annotation(Placement(transformation(origin={95,90},extent={{-10,-10},{10,10}})));
  SysplorerEmbeddedCoder.Discontinuities.Saturation motor2_sat(upLimit=output_limit,lowLimit=-output_limit) annotation(Placement(transformation(origin={95,30},extent={{-10,-10},{10,10}})));
  SysplorerEmbeddedCoder.Discontinuities.Saturation motor3_sat(upLimit=output_limit,lowLimit=-output_limit) annotation(Placement(transformation(origin={95,-30},extent={{-10,-10},{10,10}})));
  SysplorerEmbeddedCoder.Discontinuities.Saturation motor4_sat(upLimit=output_limit,lowLimit=-output_limit) annotation(Placement(transformation(origin={95,-90},extent={{-10,-10},{10,10}})));
equation
  connect(thrust_ref,thrust_neg.u) annotation(Line(points={{-190,90},{-170,90},{-170,110},{-142,110}},color={0,0,0}),__MWORKS(BlockSystem(NamedSignal)));
  connect(roll_cmd,roll_pos.u) annotation(Line(points={{-190,30},{-164,30},{-164,65},{-142,65}},color={0,0,0}),__MWORKS(BlockSystem(NamedSignal)));
  connect(roll_cmd,roll_neg.u) annotation(Line(points={{-190,30},{-164,30},{-164,40},{-142,40}},color={0,0,0}),__MWORKS(BlockSystem(NamedSignal)));
  connect(pitch_cmd,pitch_pos.u) annotation(Line(points={{-190,-30},{-164,-30},{-164,-5},{-142,-5}},color={0,0,0}),__MWORKS(BlockSystem(NamedSignal)));
  connect(pitch_cmd,pitch_neg.u) annotation(Line(points={{-190,-30},{-142,-30}},color={0,0,0}),__MWORKS(BlockSystem(NamedSignal)));
  connect(yaw_cmd,yaw_pos.u) annotation(Line(points={{-190,-90},{-164,-90},{-164,-75},{-142,-75}},color={0,0,0}),__MWORKS(BlockSystem(NamedSignal)));
  connect(yaw_cmd,yaw_neg.u) annotation(Line(points={{-190,-90},{-164,-90},{-164,-100},{-142,-100}},color={0,0,0}),__MWORKS(BlockSystem(NamedSignal)));

  connect(thrust_ref,motor1_sum.u1) annotation(Line(points={{-190,90},{0,90},{0,99},{8,99}},color={0,0,0}),__MWORKS(BlockSystem(NamedSignal)));
  connect(roll_pos.y,motor1_sum.u2) annotation(Line(points={{-118,65},{-10,65},{-10,93},{8,93}},color={0,0,0}),__MWORKS(BlockSystem(NamedSignal)));
  connect(pitch_neg.y,motor1_sum.u3) annotation(Line(points={{-118,-30},{-4,-30},{-4,87},{8,87}},color={0,0,0}),__MWORKS(BlockSystem(NamedSignal)));
  connect(yaw_neg.y,motor1_sum.u4) annotation(Line(points={{-118,-100},{2,-100},{2,81},{8,81}},color={0,0,0}),__MWORKS(BlockSystem(NamedSignal)));

  connect(thrust_neg.y,motor2_sum.u1) annotation(Line(points={{-118,110},{-16,110},{-16,39},{8,39}},color={0,0,0}),__MWORKS(BlockSystem(NamedSignal)));
  connect(roll_pos.y,motor2_sum.u2) annotation(Line(points={{-118,65},{-8,65},{-8,33},{8,33}},color={0,0,0}),__MWORKS(BlockSystem(NamedSignal)));
  connect(pitch_pos.y,motor2_sum.u3) annotation(Line(points={{-118,-5},{-8,-5},{-8,27},{8,27}},color={0,0,0}),__MWORKS(BlockSystem(NamedSignal)));
  connect(yaw_neg.y,motor2_sum.u4) annotation(Line(points={{-118,-100},{0,-100},{0,21},{8,21}},color={0,0,0}),__MWORKS(BlockSystem(NamedSignal)));

  connect(thrust_ref,motor3_sum.u1) annotation(Line(points={{-190,90},{-22,90},{-22,-21},{8,-21}},color={0,0,0}),__MWORKS(BlockSystem(NamedSignal)));
  connect(roll_neg.y,motor3_sum.u2) annotation(Line(points={{-118,40},{-14,40},{-14,-27},{8,-27}},color={0,0,0}),__MWORKS(BlockSystem(NamedSignal)));
  connect(pitch_pos.y,motor3_sum.u3) annotation(Line(points={{-118,-5},{-10,-5},{-10,-33},{8,-33}},color={0,0,0}),__MWORKS(BlockSystem(NamedSignal)));
  connect(yaw_neg.y,motor3_sum.u4) annotation(Line(points={{-118,-100},{-4,-100},{-4,-39},{8,-39}},color={0,0,0}),__MWORKS(BlockSystem(NamedSignal)));

  connect(thrust_neg.y,motor4_sum.u1) annotation(Line(points={{-118,110},{-30,110},{-30,-81},{8,-81}},color={0,0,0}),__MWORKS(BlockSystem(NamedSignal)));
  connect(roll_neg.y,motor4_sum.u2) annotation(Line(points={{-118,40},{-22,40},{-22,-87},{8,-87}},color={0,0,0}),__MWORKS(BlockSystem(NamedSignal)));
  connect(pitch_neg.y,motor4_sum.u3) annotation(Line(points={{-118,-30},{-14,-30},{-14,-93},{8,-93}},color={0,0,0}),__MWORKS(BlockSystem(NamedSignal)));
  connect(yaw_neg.y,motor4_sum.u4) annotation(Line(points={{-118,-100},{8,-100},{8,-99}},color={0,0,0}),__MWORKS(BlockSystem(NamedSignal)));
  connect(motor1_sum.y,motor1_sat.u) annotation(Line(points={{32,90},{83,90}},color={0,0,0}));
  connect(motor2_sum.y,motor2_sat.u) annotation(Line(points={{32,30},{83,30}},color={0,0,0}));
  connect(motor3_sum.y,motor3_sat.u) annotation(Line(points={{32,-30},{83,-30}},color={0,0,0}));
  connect(motor4_sum.y,motor4_sat.u) annotation(Line(points={{32,-90},{83,-90}},color={0,0,0}));
  connect(motor1_sat.y,y) annotation(Line(points={{107,90},{190,90}},color={0,0,0}));
  connect(motor2_sat.y,y1) annotation(Line(points={{107,30},{190,30}},color={0,0,0}));
  connect(motor3_sat.y,y2) annotation(Line(points={{107,-30},{190,-30}},color={0,0,0}));
  connect(motor4_sat.y,y3) annotation(Line(points={{107,-90},{190,-90}},color={0,0,0}));
end AwffL1IndiMotorMixerGraphical;