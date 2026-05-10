model AWFF_MotorMixer_Sysblock "MWORKS.Sysblock quadrotor motor mixer structure"
  extends ModelWorkspace;
  import SysplorerEmbeddedCoder.Types.*;
  import BaseWorkspace.*;
  annotation(__MWORKS(version="2025a",modelType=Control,
    PortArrangement(Left(thrust_ref,roll_cmd,pitch_cmd,yaw_cmd), Right(y,y1,y2,y3)),
    BlockSystem(blockKind=BlockKind.userModel,SampleTime(auto=true,group="")=0.01),SysblockVersion="1.0"),
    Icon(coordinateSystem(preserveAspectRatio=false)),
    experiment(DoublePrecision=false,Algorithm=Euler,InlineIntegrator=false,InlineStepSize=false,IntegratorStep=0.01,Interval=0.01,StartTime=0,StopTime=1,Tolerance=0.0001),
    Diagram(coordinateSystem(extent={{-260,-160},{200,160}},grid={2,2})));

  SysplorerEmbeddedCoder.Port.Inport thrust_ref annotation(Placement(transformation(origin={-240,120},extent={{-10,-10},{10,10}}),iconTransformation(origin={-101.8,75},extent={{-1.8,-1.8},{1.8,1.8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport roll_cmd annotation(Placement(transformation(origin={-240,50},extent={{-10,-10},{10,10}}),iconTransformation(origin={-101.8,25},extent={{-1.8,-1.8},{1.8,1.8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport pitch_cmd annotation(Placement(transformation(origin={-240,-20},extent={{-10,-10},{10,10}}),iconTransformation(origin={-101.8,-25},extent={{-1.8,-1.8},{1.8,1.8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport yaw_cmd annotation(Placement(transformation(origin={-240,-90},extent={{-10,-10},{10,10}}),iconTransformation(origin={-101.8,-75},extent={{-1.8,-1.8},{1.8,1.8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));

  SysplorerEmbeddedCoder.Port.Outport y annotation(Placement(transformation(origin={170,120},extent={{-10,-10},{10,10}}),iconTransformation(origin={101.8,75},extent={{-1.8,-1.8},{1.8,1.8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport y1 annotation(Placement(transformation(origin={170,40},extent={{-10,-10},{10,10}}),iconTransformation(origin={101.8,25},extent={{-1.8,-1.8},{1.8,1.8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport y2 annotation(Placement(transformation(origin={170,-40},extent={{-10,-10},{10,10}}),iconTransformation(origin={101.8,-25},extent={{-1.8,-1.8},{1.8,1.8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport y3 annotation(Placement(transformation(origin={170,-120},extent={{-10,-10},{10,10}}),iconTransformation(origin={101.8,-75},extent={{-1.8,-1.8},{1.8,1.8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));

  SysplorerEmbeddedCoder.MathOperation.Gain neg_roll(k=-1) annotation(Placement(transformation(origin={-120,20},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)),SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.MathOperation.Gain neg_pitch(k=-1) annotation(Placement(transformation(origin={-120,-50},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)),SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.MathOperation.Gain neg_yaw(k=-1) annotation(Placement(transformation(origin={-120,-120},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)),SampleTime(group="D1")=0.01)));

  SysplorerEmbeddedCoder.MathOperation.Sum motor1_sum(isSaturate=false,inputs="++++") annotation(Placement(transformation(origin={50,120},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(u1(Type(ref="double"),Dimension=1),u2(Type(ref="double"),Dimension=1),u3(Type(ref="double"),Dimension=1),u4(Type(ref="double"),Dimension=1)),y(Type(ref="double"),Dimension=1)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap),SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.MathOperation.Sum motor2_sum(isSaturate=false,inputs="++++") annotation(Placement(transformation(origin={50,40},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(u1(Type(ref="double"),Dimension=1),u2(Type(ref="double"),Dimension=1),u3(Type(ref="double"),Dimension=1),u4(Type(ref="double"),Dimension=1)),y(Type(ref="double"),Dimension=1)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap),SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.MathOperation.Sum motor3_sum(isSaturate=false,inputs="++++") annotation(Placement(transformation(origin={50,-40},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(u1(Type(ref="double"),Dimension=1),u2(Type(ref="double"),Dimension=1),u3(Type(ref="double"),Dimension=1),u4(Type(ref="double"),Dimension=1)),y(Type(ref="double"),Dimension=1)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap),SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.MathOperation.Sum motor4_sum(isSaturate=false,inputs="++++") annotation(Placement(transformation(origin={50,-120},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(u1(Type(ref="double"),Dimension=1),u2(Type(ref="double"),Dimension=1),u3(Type(ref="double"),Dimension=1),u4(Type(ref="double"),Dimension=1)),y(Type(ref="double"),Dimension=1)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap),SampleTime(group="D1")=0.01)));

  model ModelWorkspace
    annotation(__MWORKS(hide = true,BlockSystem(blockKind=BlockKind.modelWorkspace)));
  end ModelWorkspace;

equation
  connect(roll_cmd, neg_roll.u) annotation(__MWORKS(BlockSystem(NamedSignal)));
  connect(pitch_cmd, neg_pitch.u) annotation(__MWORKS(BlockSystem(NamedSignal)));
  connect(yaw_cmd, neg_yaw.u) annotation(__MWORKS(BlockSystem(NamedSignal)));

  connect(thrust_ref, motor1_sum.u1) annotation(__MWORKS(BlockSystem(NamedSignal)));
  connect(roll_cmd, motor1_sum.u2) annotation(__MWORKS(BlockSystem(NamedSignal)));
  connect(neg_pitch.y, motor1_sum.u3);
  connect(neg_yaw.y, motor1_sum.u4);

  connect(thrust_ref, motor2_sum.u1) annotation(__MWORKS(BlockSystem(NamedSignal)));
  connect(neg_roll.y, motor2_sum.u2);
  connect(pitch_cmd, motor2_sum.u3) annotation(__MWORKS(BlockSystem(NamedSignal)));
  connect(neg_yaw.y, motor2_sum.u4);

  connect(thrust_ref, motor3_sum.u1) annotation(__MWORKS(BlockSystem(NamedSignal)));
  connect(neg_roll.y, motor3_sum.u2);
  connect(pitch_cmd, motor3_sum.u3) annotation(__MWORKS(BlockSystem(NamedSignal)));
  connect(yaw_cmd, motor3_sum.u4) annotation(__MWORKS(BlockSystem(NamedSignal)));

  connect(thrust_ref, motor4_sum.u1) annotation(__MWORKS(BlockSystem(NamedSignal)));
  connect(roll_cmd, motor4_sum.u2) annotation(__MWORKS(BlockSystem(NamedSignal)));
  connect(pitch_cmd, motor4_sum.u3) annotation(__MWORKS(BlockSystem(NamedSignal)));
  connect(yaw_cmd, motor4_sum.u4) annotation(__MWORKS(BlockSystem(NamedSignal)));

  connect(motor1_sum.y, y);
  connect(motor2_sum.y, y1);
  connect(motor3_sum.y, y2);
  connect(motor4_sum.y, y3);
end AWFF_MotorMixer_Sysblock;
