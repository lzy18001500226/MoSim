model AWFF_AttitudeInnerLoop_Sysblock "MWORKS.Sysblock AWFF PID attitude inner-loop structure"
  extends ModelWorkspace;
  import SysplorerEmbeddedCoder.Types.*;
  import BaseWorkspace.*;
  annotation(__MWORKS(version="2025a",modelType=Control,
    PortArrangement(Left(roll_ref,pitch_ref,yaw_ref,roll_mea,pitch_mea,yaw_mea), Right(roll_cmd,pitch_cmd,yaw_cmd)),
    BlockSystem(blockKind=BlockKind.userModel,SampleTime(auto=true,group="")=0.01),SysblockVersion="1.0"),
    Icon(coordinateSystem(preserveAspectRatio=false)),
    experiment(DoublePrecision=false,Algorithm=Euler,InlineIntegrator=false,InlineStepSize=false,IntegratorStep=0.01,Interval=0.01,StartTime=0,StopTime=1,Tolerance=0.0001),
    Diagram(coordinateSystem(extent={{-260,-150},{180,150}},grid={2,2})));

  SysplorerEmbeddedCoder.Port.Inport roll_ref annotation(Placement(transformation(origin={-240,110},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport pitch_ref annotation(Placement(transformation(origin={-240,60},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport yaw_ref annotation(Placement(transformation(origin={-240,10},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport roll_mea annotation(Placement(transformation(origin={-240,-40},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport pitch_mea annotation(Placement(transformation(origin={-240,-90},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport yaw_mea annotation(Placement(transformation(origin={-240,-130},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));

  SysplorerEmbeddedCoder.Port.Outport roll_cmd annotation(Placement(transformation(origin={150,90},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(ref="double"),Dimension=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport pitch_cmd annotation(Placement(transformation(origin={150,10},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(ref="double"),Dimension=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport yaw_cmd annotation(Placement(transformation(origin={150,-90},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(ref="double"),Dimension=1,SampleTime(group="D1")=0.01)));

  SysplorerEmbeddedCoder.MathOperation.Sum roll_error(isSaturate=false,inputs="+-") annotation(Placement(transformation(origin={-170,80},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(u1(Type(ref="double"),Dimension=1),u2(Type(ref="double"),Dimension=1)),y(Type(ref="double"),Dimension=1)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap),SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.MathOperation.Gain roll_kp(k=14.142) annotation(Placement(transformation(origin={-90,100},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)),SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.MathOperation.Gain roll_kd(k=1.70) annotation(Placement(transformation(origin={-90,60},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)),SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.MathOperation.Sum roll_sum(isSaturate=false,inputs="++") annotation(Placement(transformation(origin={0,80},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(u1(Type(ref="double"),Dimension=1),u2(Type(ref="double"),Dimension=1)),y(Type(ref="double"),Dimension=1)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap),SampleTime(group="D1")=0.01)));

  SysplorerEmbeddedCoder.MathOperation.Sum pitch_error(isSaturate=false,inputs="+-") annotation(Placement(transformation(origin={-170,0},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(u1(Type(ref="double"),Dimension=1),u2(Type(ref="double"),Dimension=1)),y(Type(ref="double"),Dimension=1)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap),SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.MathOperation.Gain pitch_kp(k=14.142) annotation(Placement(transformation(origin={-90,20},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)),SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.MathOperation.Gain pitch_kd(k=1.70) annotation(Placement(transformation(origin={-90,-20},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)),SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.MathOperation.Sum pitch_sum(isSaturate=false,inputs="++") annotation(Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(u1(Type(ref="double"),Dimension=1),u2(Type(ref="double"),Dimension=1)),y(Type(ref="double"),Dimension=1)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap),SampleTime(group="D1")=0.01)));

  SysplorerEmbeddedCoder.MathOperation.Sum yaw_error(isSaturate=false,inputs="+-") annotation(Placement(transformation(origin={-170,-90},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(u1(Type(ref="double"),Dimension=1),u2(Type(ref="double"),Dimension=1)),y(Type(ref="double"),Dimension=1)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap),SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.MathOperation.Gain yaw_kp(k=5.0) annotation(Placement(transformation(origin={-70,-90},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)),SampleTime(group="D1")=0.01)));

  model ModelWorkspace
    annotation(__MWORKS(hide = true,BlockSystem(blockKind=BlockKind.modelWorkspace)));
  end ModelWorkspace;

equation
  connect(roll_ref, roll_error.u1);
  connect(roll_mea, roll_error.u2);
  connect(roll_error.y, roll_kp.u) annotation(__MWORKS(BlockSystem(NamedSignal)));
  connect(roll_error.y, roll_kd.u) annotation(__MWORKS(BlockSystem(NamedSignal)));
  connect(roll_kp.y, roll_sum.u1);
  connect(roll_kd.y, roll_sum.u2);
  connect(roll_sum.y, roll_cmd);

  connect(pitch_ref, pitch_error.u1);
  connect(pitch_mea, pitch_error.u2);
  connect(pitch_error.y, pitch_kp.u) annotation(__MWORKS(BlockSystem(NamedSignal)));
  connect(pitch_error.y, pitch_kd.u) annotation(__MWORKS(BlockSystem(NamedSignal)));
  connect(pitch_kp.y, pitch_sum.u1);
  connect(pitch_kd.y, pitch_sum.u2);
  connect(pitch_sum.y, pitch_cmd);

  connect(yaw_ref, yaw_error.u1);
  connect(yaw_mea, yaw_error.u2);
  connect(yaw_error.y, yaw_kp.u);
  connect(yaw_kp.y, yaw_cmd);
end AWFF_AttitudeInnerLoop_Sysblock;
