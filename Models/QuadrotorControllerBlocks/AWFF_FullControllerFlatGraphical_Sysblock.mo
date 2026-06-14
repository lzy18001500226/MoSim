model AWFF_FullControllerFlatGraphical_Sysblock
  "Single-layer graphical AWFF Sysblock controller for plant integration"
  extends ModelWorkspace;
  import SysplorerEmbeddedCoder.Types.*;
  import BaseWorkspace.*;
  annotation(__MWORKS(version="26.3.0",modelType=Control,PortArrangement(Left(x_error,y_error,z_error,z_ref_rate,roll_mea,pitch_mea,yaw_mea,yaw_ref), Right(y,y1,y2,y3)),BlockSystem(blockKind=BlockKind.userModel,SampleTime(auto=true,group="")=0.01,OutputInterval=0.01),SysblockVersion="1.0"),
    Icon(coordinateSystem(preserveAspectRatio=false)),
    experiment(DoublePrecision=false,Algorithm=Euler,IntegratorStep=0.01,Interval=0.01,StartTime=0,StopTime=1,StoreEventValue=0),
    Diagram(coordinateSystem(extent={{-420,-300},{360,300}},grid={2,2})));

  SysplorerEmbeddedCoder.Port.Inport x_error annotation(Placement(transformation(origin={-400,240},extent={{-10,-10},{10,10}}),iconTransformation(origin={-101.8,87.5},extent={{-1.8,-1.8},{1.8,1.8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport y_error annotation(Placement(transformation(origin={-400,180},extent={{-10,-10},{10,10}}),iconTransformation(origin={-101.8,62.5},extent={{-1.8,-1.8},{1.8,1.8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport z_error annotation(Placement(transformation(origin={-400,100},extent={{-10,-10},{10,10}}),iconTransformation(origin={-101.8,37.5},extent={{-1.8,-1.8},{1.8,1.8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport z_ref_rate annotation(Placement(transformation(origin={-400,40},extent={{-10,-10},{10,10}}),iconTransformation(origin={-101.8,12.5},extent={{-1.8,-1.8},{1.8,1.8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport roll_mea annotation(Placement(transformation(origin={-400,-40},extent={{-10,-10},{10,10}}),iconTransformation(origin={-101.8,-12.5},extent={{-1.8,-1.8},{1.8,1.8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport pitch_mea annotation(Placement(transformation(origin={-400,-100},extent={{-10,-10},{10,10}}),iconTransformation(origin={-101.8,-37.5},extent={{-1.8,-1.8},{1.8,1.8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport yaw_mea annotation(Placement(transformation(origin={-400,-180},extent={{-10,-10},{10,10}}),iconTransformation(origin={-101.8,-62.5},extent={{-1.8,-1.8},{1.8,1.8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport yaw_ref annotation(Placement(transformation(origin={-400,-240},extent={{-10,-10},{10,10}}),iconTransformation(origin={-101.8,-87.5},extent={{-1.8,-1.8},{1.8,1.8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));

  SysplorerEmbeddedCoder.Port.Outport y annotation(Placement(transformation(origin={330,180},extent={{-10,-10},{10,10}}),iconTransformation(origin={101.8,75},extent={{-1.8,-1.8},{1.8,1.8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport y1 annotation(Placement(transformation(origin={330,60},extent={{-10,-10},{10,10}}),iconTransformation(origin={101.8,25},extent={{-1.8,-1.8},{1.8,1.8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport y2 annotation(Placement(transformation(origin={330,-60},extent={{-10,-10},{10,10}}),iconTransformation(origin={101.8,-25},extent={{-1.8,-1.8},{1.8,1.8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport y3 annotation(Placement(transformation(origin={330,-180},extent={{-10,-10},{10,10}}),iconTransformation(origin={101.8,-75},extent={{-1.8,-1.8},{1.8,1.8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));

  SysplorerEmbeddedCoder.MathOperation.Gain x_kp(k=1.65) annotation(Placement(transformation(origin={-310,260},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)),SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.MathOperation.Gain x_kd(k=1.0) annotation(Placement(transformation(origin={-310,220},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)),SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.MathOperation.Sum x_sum(isSaturate=false,inputs="++") annotation(Placement(transformation(origin={-230,240},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(u1(Type(ref="double"),Dimension=1),u2(Type(ref="double"),Dimension=1)),y(Type(ref="double"),Dimension=1)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap),SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.MathOperation.Gain pitch_ref_scale(k=0.1) annotation(Placement(transformation(origin={-150,240},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)),SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Discontinuities.Saturation pitch_ref_sat(upLimit=12/57.3,lowLimit=-12/57.3) annotation(Placement(transformation(origin={-95,240},extent={{-10,-10},{10,10}})));

  SysplorerEmbeddedCoder.MathOperation.Gain y_kp(k=1.65) annotation(Placement(transformation(origin={-310,200},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)),SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.MathOperation.Gain y_kd(k=1.0) annotation(Placement(transformation(origin={-310,160},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)),SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.MathOperation.Sum y_sum(isSaturate=false,inputs="++") annotation(Placement(transformation(origin={-230,180},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(u1(Type(ref="double"),Dimension=1),u2(Type(ref="double"),Dimension=1)),y(Type(ref="double"),Dimension=1)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap),SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.MathOperation.Gain roll_ref_scale(k=0.1) annotation(Placement(transformation(origin={-150,180},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)),SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Discontinuities.Saturation roll_ref_sat(upLimit=12/57.3,lowLimit=-12/57.3) annotation(Placement(transformation(origin={-95,180},extent={{-10,-10},{10,10}})));

  SysplorerEmbeddedCoder.MathOperation.Gain z_kp(k=8.0) annotation(Placement(transformation(origin={-310,120},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)),SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Discrete.DiscreteTimeIntegrator z_ki(externalResetType=SysplorerEmbeddedCoder.Discrete.DiscreteTimeIntegrator.ExternalResetType.None,gain=6.0,initCond=0) annotation(Placement(transformation(origin={-310,80},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(SampleTime(auto=true,group="D1")=0.01,Instance(u1(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),gain(Type(ref="double"),Dimension=1),initCond(Type(ref="double"),Dimension=1))),PortLabels(labelType="CustomType",labels(label(text="",instance="u1"),label(text="",instance="u2"),label(text="x0",instance="u3")))));
  SysplorerEmbeddedCoder.MathOperation.Gain z_kd(k=4.0) annotation(Placement(transformation(origin={-310,40},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)),SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.MathOperation.Gain z_ff(k=0.35) annotation(Placement(transformation(origin={-310,0},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)),SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.MathOperation.Sum thrust_sum(isSaturate=false,inputs="++++") annotation(Placement(transformation(origin={-190,80},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(u1(Type(ref="double"),Dimension=1),u2(Type(ref="double"),Dimension=1),u3(Type(ref="double"),Dimension=1),u4(Type(ref="double"),Dimension=1)),y(Type(ref="double"),Dimension=1)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap),SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Discontinuities.Saturation thrust_sat(upLimit=20.0,lowLimit=-20.0) annotation(Placement(transformation(origin={-120,80},extent={{-10,-10},{10,10}})));

  SysplorerEmbeddedCoder.MathOperation.Sum roll_error(isSaturate=false,inputs="++") annotation(Placement(transformation(origin={-40,180},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(u1(Type(ref="double"),Dimension=1),u2(Type(ref="double"),Dimension=1)),y(Type(ref="double"),Dimension=1)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap),SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.MathOperation.Gain roll_kp(k=14.142) annotation(Placement(transformation(origin={40,200},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)),SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.MathOperation.Gain roll_kd(k=1.70) annotation(Placement(transformation(origin={40,160},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)),SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.MathOperation.Sum roll_cmd_sum(isSaturate=false,inputs="++") annotation(Placement(transformation(origin={120,180},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(u1(Type(ref="double"),Dimension=1),u2(Type(ref="double"),Dimension=1)),y(Type(ref="double"),Dimension=1)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap),SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.MathOperation.Gain roll_mix(k=0.707) annotation(Placement(transformation(origin={190,180},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)),SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.MathOperation.Gain neg_roll_mix(k=-0.707) annotation(Placement(transformation(origin={190,140},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)),SampleTime(group="D1")=0.01)));

  SysplorerEmbeddedCoder.MathOperation.Sum pitch_error(isSaturate=false,inputs="+-") annotation(Placement(transformation(origin={-40,80},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(u1(Type(ref="double"),Dimension=1),u2(Type(ref="double"),Dimension=1)),y(Type(ref="double"),Dimension=1)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap),SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.MathOperation.Gain pitch_kp(k=14.142) annotation(Placement(transformation(origin={40,100},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)),SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.MathOperation.Gain pitch_kd(k=1.70) annotation(Placement(transformation(origin={40,60},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)),SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.MathOperation.Sum pitch_cmd_sum(isSaturate=false,inputs="++") annotation(Placement(transformation(origin={120,80},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(u1(Type(ref="double"),Dimension=1),u2(Type(ref="double"),Dimension=1)),y(Type(ref="double"),Dimension=1)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap),SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.MathOperation.Gain pitch_mix(k=0.707) annotation(Placement(transformation(origin={190,80},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)),SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.MathOperation.Gain neg_pitch_mix(k=-0.707) annotation(Placement(transformation(origin={190,40},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)),SampleTime(group="D1")=0.01)));

  SysplorerEmbeddedCoder.MathOperation.Sum yaw_error(isSaturate=false,inputs="+-") annotation(Placement(transformation(origin={-40,-40},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(u1(Type(ref="double"),Dimension=1),u2(Type(ref="double"),Dimension=1)),y(Type(ref="double"),Dimension=1)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap),SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.MathOperation.Gain yaw_kp(k=5.0) annotation(Placement(transformation(origin={40,-40},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)),SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.MathOperation.Gain yaw_mix(k=0.707) annotation(Placement(transformation(origin={190,-20},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)),SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.MathOperation.Gain neg_yaw_mix(k=-0.707) annotation(Placement(transformation(origin={190,-60},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)),SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.MathOperation.Gain neg_thrust(k=-1) annotation(Placement(transformation(origin={190,-120},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)),SampleTime(group="D1")=0.01)));

  SysplorerEmbeddedCoder.MathOperation.Sum motor1_sum(isSaturate=false,inputs="++++") annotation(Placement(transformation(origin={260,180},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(u1(Type(ref="double"),Dimension=1),u2(Type(ref="double"),Dimension=1),u3(Type(ref="double"),Dimension=1),u4(Type(ref="double"),Dimension=1)),y(Type(ref="double"),Dimension=1)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap),SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.MathOperation.Sum motor2_sum(isSaturate=false,inputs="++++") annotation(Placement(transformation(origin={260,60},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(u1(Type(ref="double"),Dimension=1),u2(Type(ref="double"),Dimension=1),u3(Type(ref="double"),Dimension=1),u4(Type(ref="double"),Dimension=1)),y(Type(ref="double"),Dimension=1)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap),SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.MathOperation.Sum motor3_sum(isSaturate=false,inputs="++++") annotation(Placement(transformation(origin={260,-60},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(u1(Type(ref="double"),Dimension=1),u2(Type(ref="double"),Dimension=1),u3(Type(ref="double"),Dimension=1),u4(Type(ref="double"),Dimension=1)),y(Type(ref="double"),Dimension=1)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap),SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.MathOperation.Sum motor4_sum(isSaturate=false,inputs="++++") annotation(Placement(transformation(origin={260,-180},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(u1(Type(ref="double"),Dimension=1),u2(Type(ref="double"),Dimension=1),u3(Type(ref="double"),Dimension=1),u4(Type(ref="double"),Dimension=1)),y(Type(ref="double"),Dimension=1)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap),SampleTime(group="D1")=0.01)));

  model ModelWorkspace
    annotation(__MWORKS(hide = true,BlockSystem(blockKind=BlockKind.modelWorkspace)));
  end ModelWorkspace;

equation
  connect(x_error, x_kp.u) annotation(Line(origin={-355,250},points={{-35,-10},{33,10}},color={0,0,0}),__MWORKS(BlockSystem(NamedSignal)));
  connect(x_error, x_kd.u) annotation(Line(origin={-355,230},points={{-35,10},{33,-10}},color={0,0,0}),__MWORKS(BlockSystem(NamedSignal)));
  connect(x_kp.y, x_sum.u1) annotation(Line(origin={-270,250},points={{-28,10},{28,-10}},color={0,0,0}));
  connect(x_kd.y, x_sum.u2) annotation(Line(origin={-270,230},points={{-28,-10},{28,10}},color={0,0,0}));
  connect(x_sum.y, pitch_ref_scale.u) annotation(Line(origin={-190,240},points={{-28,0},{28,0}},color={0,0,0}));
  connect(pitch_ref_scale.y, pitch_ref_sat.u) annotation(Line(origin={-122,240},points={{-16,0},{15,0}},color={0,0,0}));

  connect(y_error, y_kp.u) annotation(Line(origin={-355,190},points={{-35,-10},{33,10}},color={0,0,0}),__MWORKS(BlockSystem(NamedSignal)));
  connect(y_error, y_kd.u) annotation(Line(origin={-355,170},points={{-35,10},{33,-10}},color={0,0,0}),__MWORKS(BlockSystem(NamedSignal)));
  connect(y_kp.y, y_sum.u1) annotation(Line(origin={-270,190},points={{-28,10},{28,-10}},color={0,0,0}));
  connect(y_kd.y, y_sum.u2) annotation(Line(origin={-270,170},points={{-28,-10},{28,10}},color={0,0,0}));
  connect(y_sum.y, roll_ref_scale.u) annotation(Line(origin={-190,180},points={{-28,0},{28,0}},color={0,0,0}));
  connect(roll_ref_scale.y, roll_ref_sat.u) annotation(Line(origin={-122,180},points={{-16,0},{15,0}},color={0,0,0}));

  connect(z_error, z_kp.u) annotation(Line(origin={-355,110},points={{-35,-10},{33,10}},color={0,0,0}),__MWORKS(BlockSystem(NamedSignal)));
  connect(z_error, z_ki.u1) annotation(Line(origin={-355,90},points={{-35,10},{33,-10}},color={0,0,0}),__MWORKS(BlockSystem(NamedSignal)));
  connect(z_error, z_kd.u) annotation(Line(origin={-355,60},points={{-35,40},{33,-20}},color={0,0,0}),__MWORKS(BlockSystem(NamedSignal)));
  connect(z_ref_rate, z_ff.u) annotation(Line(origin={-355,20},points={{-35,20},{33,-20}},color={0,0,0}));
  connect(z_kp.y, thrust_sum.u1) annotation(Line(origin={-250,115},points={{-48,5},{48,-38}},color={0,0,0}));
  connect(z_ki.y, thrust_sum.u2) annotation(Line(origin={-250,80},points={{-48,0},{48,0}},color={0,0,0}));
  connect(z_kd.y, thrust_sum.u3) annotation(Line(origin={-250,55},points={{-48,-15},{48,18}},color={0,0,0}));
  connect(z_ff.y, thrust_sum.u4) annotation(Line(origin={-250,30},points={{-48,-30},{48,45}},color={0,0,0}));
  connect(thrust_sum.y, thrust_sat.u) annotation(Line(origin={-155,80},points={{-23,0},{23,0}},color={0,0,0}),__MWORKS(BlockSystem(NamedSignal)));

  connect(roll_ref_sat.y, roll_error.u1) annotation(Line(origin={-72,180},points={{-11,0},{20,0}},color={0,0,0}));
  connect(roll_mea, roll_error.u2) annotation(Line(origin={-220,70},points={{-170,-110},{170,-110},{170,105},{168,105}},color={0,0,0}));
  connect(roll_error.y, roll_kp.u) annotation(Line(origin={0,190},points={{-28,-10},{28,10}},color={0,0,0}),__MWORKS(BlockSystem(NamedSignal)));
  connect(roll_error.y, roll_kd.u) annotation(Line(origin={0,170},points={{-28,10},{28,-10}},color={0,0,0}),__MWORKS(BlockSystem(NamedSignal)));
  connect(roll_kp.y, roll_cmd_sum.u1) annotation(Line(origin={80,190},points={{-28,10},{28,-10}},color={0,0,0}));
  connect(roll_kd.y, roll_cmd_sum.u2) annotation(Line(origin={80,170},points={{-28,-10},{28,10}},color={0,0,0}));
  connect(roll_cmd_sum.y, roll_mix.u) annotation(Line(origin={155,180},points={{-23,0},{23,0}},color={0,0,0}),__MWORKS(BlockSystem(NamedSignal)));
  connect(roll_cmd_sum.y, neg_roll_mix.u) annotation(Line(origin={155,160},points={{-23,20},{23,-20}},color={0,0,0}),__MWORKS(BlockSystem(NamedSignal)));

  connect(pitch_ref_sat.y, pitch_error.u1) annotation(Line(origin={-72,160},points={{-11,80},{20,-80}},color={0,0,0}));
  connect(pitch_mea, pitch_error.u2) annotation(Line(origin={-220,-10},points={{-170,-90},{170,-90},{170,85},{168,85}},color={0,0,0}));
  connect(pitch_error.y, pitch_kp.u) annotation(Line(origin={0,90},points={{-28,-10},{28,10}},color={0,0,0}),__MWORKS(BlockSystem(NamedSignal)));
  connect(pitch_error.y, pitch_kd.u) annotation(Line(origin={0,70},points={{-28,10},{28,-10}},color={0,0,0}),__MWORKS(BlockSystem(NamedSignal)));
  connect(pitch_kp.y, pitch_cmd_sum.u1) annotation(Line(origin={80,90},points={{-28,10},{28,-10}},color={0,0,0}));
  connect(pitch_kd.y, pitch_cmd_sum.u2) annotation(Line(origin={80,70},points={{-28,-10},{28,10}},color={0,0,0}));
  connect(pitch_cmd_sum.y, pitch_mix.u) annotation(Line(origin={155,80},points={{-23,0},{23,0}},color={0,0,0}),__MWORKS(BlockSystem(NamedSignal)));
  connect(pitch_cmd_sum.y, neg_pitch_mix.u) annotation(Line(origin={155,60},points={{-23,20},{23,-20}},color={0,0,0}),__MWORKS(BlockSystem(NamedSignal)));

  connect(yaw_ref, yaw_error.u1) annotation(Line(origin={-220,-140},points={{-170,-100},{168,100}},color={0,0,0}));
  connect(yaw_mea, yaw_error.u2) annotation(Line(origin={-220,-110},points={{-170,-70},{168,70}},color={0,0,0}));
  connect(yaw_error.y, yaw_kp.u) annotation(Line(origin={0,-40},points={{-28,0},{28,0}},color={0,0,0}));
  connect(yaw_kp.y, yaw_mix.u) annotation(Line(origin={115,-30},points={{-63,-10},{63,10}},color={0,0,0}),__MWORKS(BlockSystem(NamedSignal)));
  connect(yaw_kp.y, neg_yaw_mix.u) annotation(Line(origin={115,-50},points={{-63,10},{63,-10}},color={0,0,0}),__MWORKS(BlockSystem(NamedSignal)));
  connect(thrust_sat.y, neg_thrust.u) annotation(Line(origin={35,-20},points={{-143,100},{143,-100}},color={0,0,0}),__MWORKS(BlockSystem(NamedSignal)));

  connect(thrust_sat.y, motor1_sum.u1) annotation(Line(origin={70,130},points={{-178,-50},{178,50}},color={0,0,0}),__MWORKS(BlockSystem(NamedSignal)));
  connect(neg_yaw_mix.y, motor1_sum.u2) annotation(Line(origin={225,55},points={{-23,-115},{23,115}},color={0,0,0}));
  connect(neg_pitch_mix.y, motor1_sum.u3) annotation(Line(origin={225,110},points={{-23,-70},{23,65}},color={0,0,0}));
  connect(roll_mix.y, motor1_sum.u4) annotation(Line(origin={225,180},points={{-23,0},{23,-5}},color={0,0,0}));

  connect(neg_thrust.y, motor2_sum.u1) annotation(Line(origin={225,-30},points={{-23,-90},{23,90}},color={0,0,0}),__MWORKS(BlockSystem(NamedSignal)));
  connect(neg_yaw_mix.y, motor2_sum.u2) annotation(Line(origin={225,0},points={{-23,-60},{23,55}},color={0,0,0}));
  connect(pitch_mix.y, motor2_sum.u3) annotation(Line(origin={225,70},points={{-23,10},{23,-15}},color={0,0,0}));
  connect(roll_mix.y, motor2_sum.u4) annotation(Line(origin={225,120},points={{-23,60},{23,-65}},color={0,0,0}));

  connect(thrust_sat.y, motor3_sum.u1) annotation(Line(origin={70,10},points={{-178,70},{178,-70}},color={0,0,0}),__MWORKS(BlockSystem(NamedSignal)));
  connect(neg_yaw_mix.y, motor3_sum.u2) annotation(Line(origin={225,-60},points={{-23,0},{23,-5}},color={0,0,0}));
  connect(pitch_mix.y, motor3_sum.u3) annotation(Line(origin={225,10},points={{-23,70},{23,-75}},color={0,0,0}));
  connect(neg_roll_mix.y, motor3_sum.u4) annotation(Line(origin={225,40},points={{-23,100},{23,-105}},color={0,0,0}));

  connect(neg_thrust.y, motor4_sum.u1) annotation(Line(origin={225,-150},points={{-23,30},{23,-30}},color={0,0,0}),__MWORKS(BlockSystem(NamedSignal)));
  connect(neg_yaw_mix.y, motor4_sum.u2) annotation(Line(origin={225,-120},points={{-23,60},{23,-55}},color={0,0,0}));
  connect(neg_pitch_mix.y, motor4_sum.u3) annotation(Line(origin={225,-70},points={{-23,110},{23,-105}},color={0,0,0}));
  connect(neg_roll_mix.y, motor4_sum.u4) annotation(Line(origin={225,-20},points={{-23,160},{23,-155}},color={0,0,0}));

  connect(motor1_sum.y, y) annotation(Line(origin={300,180},points={{-28,0},{20,0}},color={0,0,0}));
  connect(motor2_sum.y, y1) annotation(Line(origin={300,60},points={{-28,0},{20,0}},color={0,0,0}));
  connect(motor3_sum.y, y2) annotation(Line(origin={300,-60},points={{-28,0},{20,0}},color={0,0,0}));
  connect(motor4_sum.y, y3) annotation(Line(origin={300,-180},points={{-28,0},{20,0}},color={0,0,0}));
end AWFF_FullControllerFlatGraphical_Sysblock;