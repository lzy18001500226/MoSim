model AWFF_PositionOuterLoop_Sysblock "MWORKS.Sysblock AWFF PID position outer-loop structure"
  extends ModelWorkspace;
  import SysplorerEmbeddedCoder.Types.*;
  import BaseWorkspace.*;
  annotation(__MWORKS(version="26.3.0",modelType=Control,PortArrangement(Left(x_error,y_error,z_error,z_ref_rate), Right(pitch_ref,roll_ref,thrust_ref)),BlockSystem(blockKind=BlockKind.userModel,SampleTime(auto=true,group="")=0.01,OutputInterval=0.01),SysblockVersion="1.0"),
    Icon(coordinateSystem(preserveAspectRatio=false)),
    experiment(DoublePrecision=false,Algorithm=Euler,IntegratorStep=0.01,Interval=0.01,StartTime=0,StopTime=1,StoreEventValue=0),
    Diagram(coordinateSystem(extent={{-260,-160},{180,160}},grid={2,2})));

  SysplorerEmbeddedCoder.Port.Inport x_error annotation(Placement(transformation(origin={-240,110},extent={{-10,-10},{10,10}}),iconTransformation(origin={-101.8,75},extent={{-1.8,-1.8},{1.8,1.8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport y_error annotation(Placement(transformation(origin={-240,40},extent={{-10,-10},{10,10}}),iconTransformation(origin={-101.8,25},extent={{-1.8,-1.8},{1.8,1.8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport z_error annotation(Placement(transformation(origin={-240,-40},extent={{-10,-10},{10,10}}),iconTransformation(origin={-101.8,-25},extent={{-1.8,-1.8},{1.8,1.8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport z_ref_rate annotation(Placement(transformation(origin={-240,-120},extent={{-10,-10},{10,10}}),iconTransformation(origin={-101.8,-75},extent={{-1.8,-1.8},{1.8,1.8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));

  SysplorerEmbeddedCoder.Port.Outport pitch_ref annotation(Placement(transformation(origin={150,110},extent={{-10,-10},{10,10}}),iconTransformation(origin={101.8,60},extent={{-1.8,-1.8},{1.8,1.8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport roll_ref annotation(Placement(transformation(origin={150,40},extent={{-10,-10},{10,10}}),iconTransformation(origin={101.8,0},extent={{-1.8,-1.8},{1.8,1.8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport thrust_ref annotation(Placement(transformation(origin={150,-60},extent={{-10,-10},{10,10}}),iconTransformation(origin={101.8,-60},extent={{-1.8,-1.8},{1.8,1.8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));

  SysplorerEmbeddedCoder.MathOperation.Gain x_kp(k=1.65) annotation(Placement(transformation(origin={-170,130},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)),SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.MathOperation.Gain x_kd(k=1.0) annotation(Placement(transformation(origin={-170,90},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)),SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.MathOperation.Sum x_sum(isSaturate=false,inputs="++") annotation(Placement(transformation(origin={-100,110},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(u1(Type(ref="double"),Dimension=1),u2(Type(ref="double"),Dimension=1)),y(Type(ref="double"),Dimension=1)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap),SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.MathOperation.Gain x_scale(k=0.1) annotation(Placement(transformation(origin={-30,110},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)),SampleTime(group="D1")=0.01)));

  SysplorerEmbeddedCoder.MathOperation.Gain y_kp(k=1.65) annotation(Placement(transformation(origin={-170,60},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)),SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.MathOperation.Gain y_kd(k=1.0) annotation(Placement(transformation(origin={-170,20},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)),SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.MathOperation.Sum y_sum(isSaturate=false,inputs="++") annotation(Placement(transformation(origin={-100,40},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(u1(Type(ref="double"),Dimension=1),u2(Type(ref="double"),Dimension=1)),y(Type(ref="double"),Dimension=1)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap),SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.MathOperation.Gain y_scale(k=0.1) annotation(Placement(transformation(origin={-30,40},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)),SampleTime(group="D1")=0.01)));

  SysplorerEmbeddedCoder.MathOperation.Gain z_kp(k=8.0) annotation(Placement(transformation(origin={-170,-20},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)),SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Discrete.DiscreteTimeIntegrator z_ki(externalResetType=SysplorerEmbeddedCoder.Discrete.DiscreteTimeIntegrator.ExternalResetType.None,gain=6.0,initCond=0) annotation(Placement(transformation(origin={-170,-60},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(SampleTime(auto=true,group="D1")=0.01,Instance(u1(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),gain(Type(ref="double"),Dimension=1),initCond(Type(ref="double"),Dimension=1))),PortLabels(labelType="CustomType",labels(label(text="",instance="u1"),label(text="",instance="u2"),label(text="x0",instance="u3")))));
  SysplorerEmbeddedCoder.MathOperation.Gain z_kd(k=4.0) annotation(Placement(transformation(origin={-170,-100},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)),SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.MathOperation.Gain z_ff(k=0.35) annotation(Placement(transformation(origin={-170,-140},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)),SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.MathOperation.Sum z_sum(isSaturate=false,inputs="++++") annotation(Placement(transformation(origin={-80,-60},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(u1(Type(ref="double"),Dimension=1),u2(Type(ref="double"),Dimension=1),u3(Type(ref="double"),Dimension=1),u4(Type(ref="double"),Dimension=1)),y(Type(ref="double"),Dimension=1)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap),SampleTime(group="D1")=0.01)));

  model ModelWorkspace
    annotation(__MWORKS(hide = true,BlockSystem(blockKind=BlockKind.modelWorkspace)));
  end ModelWorkspace;

equation
  connect(x_error, x_kp.u)
    annotation(Line(origin={-205,120},points={{-25,-10},{23,10}},color={0,0,0}),__MWORKS(BlockSystem(NamedSignal)));
  connect(x_error, x_kd.u)
    annotation(Line(origin={-205,100},points={{-25,10},{23,-10}},color={0,0,0}),__MWORKS(BlockSystem(NamedSignal)));
  connect(x_kp.y, x_sum.u1)
    annotation(Line(origin={-135,120},points={{-23,10},{23,-10}},color={0,0,0}));
  connect(x_kd.y, x_sum.u2)
    annotation(Line(origin={-135,100},points={{-23,-10},{23,10}},color={0,0,0}));
  connect(x_sum.y, x_scale.u)
    annotation(Line(origin={-65,110},points={{-23,0},{23,0}},color={0,0,0}));
  connect(x_scale.y, pitch_ref)
    annotation(Line(origin={60,110},points={{-78,0},{80,0}},color={0,0,0}));

  connect(y_error, y_kp.u)
    annotation(Line(origin={-205,50},points={{-25,-10},{23,10}},color={0,0,0}),__MWORKS(BlockSystem(NamedSignal)));
  connect(y_error, y_kd.u)
    annotation(Line(origin={-205,30},points={{-25,10},{23,-10}},color={0,0,0}),__MWORKS(BlockSystem(NamedSignal)));
  connect(y_kp.y, y_sum.u1)
    annotation(Line(origin={-135,50},points={{-23,10},{23,-10}},color={0,0,0}));
  connect(y_kd.y, y_sum.u2)
    annotation(Line(origin={-135,30},points={{-23,-10},{23,10}},color={0,0,0}));
  connect(y_sum.y, y_scale.u)
    annotation(Line(origin={-65,40},points={{-23,0},{23,0}},color={0,0,0}));
  connect(y_scale.y, roll_ref)
    annotation(Line(origin={60,40},points={{-78,0},{80,0}},color={0,0,0}));

  connect(z_error, z_kp.u)
    annotation(Line(origin={-205,-30},points={{-25,-10},{23,10}},color={0,0,0}),__MWORKS(BlockSystem(NamedSignal)));
  connect(z_error, z_ki.u1)
    annotation(Line(origin={-205,-50},points={{-25,10},{23,-10}},color={0,0,0}),__MWORKS(BlockSystem(NamedSignal)));
  connect(z_error, z_kd.u)
    annotation(Line(origin={-205,-70},points={{-25,30},{23,-30}},color={0,0,0}),__MWORKS(BlockSystem(NamedSignal)));
  connect(z_ref_rate, z_ff.u)
    annotation(Line(origin={-205,-130},points={{-25,10},{23,-10}},color={0,0,0}));
  connect(z_kp.y, z_sum.u1)
    annotation(Line(origin={-125,-35},points={{-33,15},{33,-18}},color={0,0,0}));
  connect(z_ki.y, z_sum.u2)
    annotation(Line(origin={-125,-60},points={{-33,0},{33,0}},color={0,0,0}));
  connect(z_kd.y, z_sum.u3)
    annotation(Line(origin={-125,-85},points={{-33,-15},{33,18}},color={0,0,0}));
  connect(z_ff.y, z_sum.u4)
    annotation(Line(origin={-125,-110},points={{-33,-30},{33,45}},color={0,0,0}));
  connect(z_sum.y, thrust_ref)
    annotation(Line(origin={35,-60},points={{-103,0},{105,0}},color={0,0,0}));
end AWFF_PositionOuterLoop_Sysblock;