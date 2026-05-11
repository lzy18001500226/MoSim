model AWFF_MotorMixer_Sysblock "MWORKS.Sysblock quadrotor motor mixer structure"
  extends ModelWorkspace;
  import SysplorerEmbeddedCoder.Types.*;
  import BaseWorkspace.*;
  annotation(__MWORKS(version="26.3.0",modelType=Control,PortArrangement(Left(thrust_ref,roll_cmd,pitch_cmd,yaw_cmd), Right(y,y1,y2,y3)),BlockSystem(blockKind=BlockKind.userModel,SampleTime(auto=true,group="")=0.01,OutputInterval=0.01),SysblockVersion="1.0"),
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
  connect(roll_cmd, neg_roll.u)
    annotation(Line(origin={-180,35},points={{-50,15},{48,-15}},color={0,0,0}),__MWORKS(BlockSystem(NamedSignal)));
  connect(pitch_cmd, neg_pitch.u)
    annotation(Line(origin={-180,-35},points={{-50,15},{48,-15}},color={0,0,0}),__MWORKS(BlockSystem(NamedSignal)));
  connect(yaw_cmd, neg_yaw.u)
    annotation(Line(origin={-180,-105},points={{-50,15},{48,-15}},color={0,0,0}),__MWORKS(BlockSystem(NamedSignal)));

  connect(thrust_ref, motor1_sum.u1)
    annotation(Line(origin={-95,120},points={{-135,0},{133,0}},color={0,0,0}),__MWORKS(BlockSystem(NamedSignal)));
  connect(roll_cmd, motor1_sum.u2)
    annotation(Line(origin={-95,80},points={{-135,-30},{95,-30},{95,30},{133,30}},color={0,0,0}),__MWORKS(BlockSystem(NamedSignal)));
  connect(neg_pitch.y, motor1_sum.u3)
    annotation(Line(origin={-35,35},points={{-73,-85},{15,-85},{15,65},{73,65}},color={0,0,0}));
  connect(neg_yaw.y, motor1_sum.u4)
    annotation(Line(origin={-35,0},points={{-73,-120},{35,-120},{35,90},{73,90}},color={0,0,0}));

  connect(thrust_ref, motor2_sum.u1)
    annotation(Line(origin={-95,85},points={{-135,35},{80,35},{80,-35},{133,-35}},color={0,0,0}),__MWORKS(BlockSystem(NamedSignal)));
  connect(neg_roll.y, motor2_sum.u2)
    annotation(Line(origin={-35,30},points={{-73,-10},{35,-10},{35,0},{73,0}},color={0,0,0}));
  connect(pitch_cmd, motor2_sum.u3)
    annotation(Line(origin={-95,10},points={{-135,-30},{90,-30},{90,20},{133,20}},color={0,0,0}),__MWORKS(BlockSystem(NamedSignal)));
  connect(neg_yaw.y, motor2_sum.u4)
    annotation(Line(origin={-35,-40},points={{-73,-80},{20,-80},{20,70},{73,70}},color={0,0,0}));

  connect(thrust_ref, motor3_sum.u1)
    annotation(Line(origin={-95,45},points={{-135,75},{65,75},{65,-75},{133,-75}},color={0,0,0}),__MWORKS(BlockSystem(NamedSignal)));
  connect(neg_roll.y, motor3_sum.u2)
    annotation(Line(origin={-35,-10},points={{-73,30},{20,30},{20,-20},{73,-20}},color={0,0,0}));
  connect(pitch_cmd, motor3_sum.u3)
    annotation(Line(origin={-95,-30},points={{-135,10},{95,10},{95,-20},{133,-20}},color={0,0,0}),__MWORKS(BlockSystem(NamedSignal)));
  connect(yaw_cmd, motor3_sum.u4)
    annotation(Line(origin={-95,-65},points={{-135,-25},{90,-25},{90,35},{133,35}},color={0,0,0}),__MWORKS(BlockSystem(NamedSignal)));

  connect(thrust_ref, motor4_sum.u1)
    annotation(Line(origin={-95,0},points={{-135,120},{50,120},{50,-120},{133,-120}},color={0,0,0}),__MWORKS(BlockSystem(NamedSignal)));
  connect(roll_cmd, motor4_sum.u2)
    annotation(Line(origin={-95,-35},points={{-135,85},{65,85},{65,-75},{133,-75}},color={0,0,0}),__MWORKS(BlockSystem(NamedSignal)));
  connect(pitch_cmd, motor4_sum.u3)
    annotation(Line(origin={-95,-70},points={{-135,50},{80,50},{80,-40},{133,-40}},color={0,0,0}),__MWORKS(BlockSystem(NamedSignal)));
  connect(yaw_cmd, motor4_sum.u4)
    annotation(Line(origin={-95,-105},points={{-135,15},{95,15},{95,15},{133,15}},color={0,0,0}),__MWORKS(BlockSystem(NamedSignal)));

  connect(motor1_sum.y, y)
    annotation(Line(origin={110,120},points={{-48,0},{50,0}},color={0,0,0}));
  connect(motor2_sum.y, y1)
    annotation(Line(origin={110,40},points={{-48,0},{50,0}},color={0,0,0}));
  connect(motor3_sum.y, y2)
    annotation(Line(origin={110,-40},points={{-48,0},{50,0}},color={0,0,0}));
  connect(motor4_sum.y, y3)
    annotation(Line(origin={110,-120},points={{-48,0},{50,0}},color={0,0,0}));
end AWFF_MotorMixer_Sysblock;