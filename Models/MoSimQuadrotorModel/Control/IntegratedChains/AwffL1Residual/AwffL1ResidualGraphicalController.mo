within MoSimQuadrotorModel.Control.IntegratedChains.AwffL1Residual;
model AwffL1ResidualGraphicalController "AWFF L1 Residual controller - standalone graphical Sysblock"
  extends ModelWorkspace;
  import SysplorerEmbeddedCoder.Types.*;
  import BaseWorkspace.*;
  annotation(__MWORKS(version="26.3.0",modelType=Control,PortArrangement(Left(x_error,y_error,z_error,z_ref_rate,roll_mea,pitch_mea,yaw_mea,yaw_ref), Right(y,y1,y2,y3)),BlockSystem(blockKind=BlockKind.userModel,SampleTime(auto=true,group="")=0.01,OutputInterval=0.01),SysblockVersion="1.0"),
    Icon(coordinateSystem(preserveAspectRatio=false)),
    experiment(DoublePrecision=false,Algorithm=Euler,IntegratorStep=0.01,Interval=0.01,StartTime=0,StopTime=1,StoreEventValue=0),
    Diagram(coordinateSystem(extent={{-320,-220},{280,220}},grid={2,2})));


  SysplorerEmbeddedCoder.Port.Inport x_error annotation(Placement(transformation(origin={-300,180},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport y_error annotation(Placement(transformation(origin={-300,130},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport z_error annotation(Placement(transformation(origin={-300,80},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport z_ref_rate annotation(Placement(transformation(origin={-300,30},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport roll_mea annotation(Placement(transformation(origin={-300,-30},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport pitch_mea annotation(Placement(transformation(origin={-300,-80},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport yaw_mea annotation(Placement(transformation(origin={-300,-130},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport yaw_ref annotation(Placement(transformation(origin={-300,-180},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));

  SysplorerEmbeddedCoder.Port.Outport y annotation(Placement(transformation(origin={250,150},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport y1 annotation(Placement(transformation(origin={250,50},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport y2 annotation(Placement(transformation(origin={250,-50},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport y3 annotation(Placement(transformation(origin={250,-150},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));

  L1ResidualOuterLoopBlock position_loop annotation(Placement(transformation(origin={-145,85},extent={{-45,-45},{45,45}})));
  PIDAttitudeInnerLoopBlock attitude_loop annotation(Placement(transformation(origin={5,-35},extent={{-45,-45},{45,45}})));
  MotorMixerBlock motor_mixer annotation(Placement(transformation(origin={155,-35},extent={{-45,-45},{45,45}})));

  model ModelWorkspace
    annotation(__MWORKS(hide=true,BlockSystem(blockKind=BlockKind.modelWorkspace),version="26.3.0"));
  end ModelWorkspace;

  model L1ResidualOuterLoopBlock
    "L1-inspired residual compensated position outer loop"
    extends ModelWorkspace;
    annotation(__MWORKS(version="26.3.0",modelType=Control,PortArrangement(Left(x_error,y_error,z_error,z_ref_rate),Right(pitch_ref,roll_ref,thrust_ref)),BlockSystem(blockKind=BlockKind.userModel,SampleTime(auto=true,group="")=0.01,OutputInterval=0.01),SysblockVersion="1.0"),
      Icon(coordinateSystem(preserveAspectRatio=false),graphics={
        Rectangle(extent={{-100,-100},{100,100}},lineColor={45,85,130},fillColor={238,246,255},fillPattern=FillPattern.Solid,radius=8),
        Text(extent={{-90,30},{90,-4}},textString="L1 Residual",lineColor={20,45,75}),
        Text(extent={{-90,-12},{90,-46}},textString="Outer Loop",lineColor={20,45,75}),
        Text(extent={{-90,-54},{90,-82}},textString="e,r -> attitude,T",lineColor={85,105,125})}),
      Diagram(coordinateSystem(extent={{-220,-140},{220,140}},grid={2,2})));

    parameter Real kp_x=1.65;
    parameter Real kd_x=1.0;
    parameter Real kp_y=1.65;
    parameter Real kd_y=1.0;
    parameter Real kp_z=8.0;
    parameter Real ki_z=6.0;
    parameter Real kd_z=4.0;
    parameter Real kff_z=0.35;
    parameter Real roll_pitch_cmd_limit=12/57.3;
    parameter Real output_limit=20.0;
    parameter Real position_derivative_filter_T=0.05;
    parameter Real altitude_derivative_filter_T=0.08;
    parameter Real l1_model_decay=1.25;
    parameter Real l1_filter_T=0.20;
    parameter Real l1_gain_xy=0.32;
    parameter Real l1_gain_z=0.35;
    parameter Real l1_comp_limit_xy=2.0;
    parameter Real l1_comp_limit_z=2.0;

    SysplorerEmbeddedCoder.Port.Inport x_error annotation(Placement(transformation(origin={-200,90},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Inport y_error annotation(Placement(transformation(origin={-200,30},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Inport z_error annotation(Placement(transformation(origin={-200,-30},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Inport z_ref_rate annotation(Placement(transformation(origin={-200,-90},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Outport pitch_ref annotation(Placement(transformation(origin={200,70},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Outport roll_ref annotation(Placement(transformation(origin={200,0},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Outport thrust_ref annotation(Placement(transformation(origin={200,-70},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));

    SysplorerEmbeddedCoder.MathOperation.Gain x_rate_gain(k=l1_model_decay) annotation(Placement(transformation(origin={-145,105},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)),SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.MathOperation.Gain x_decay_gain(k=l1_model_decay) annotation(Placement(transformation(origin={-145,75},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)),SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.MathOperation.Sum x_l1_sum(isSaturate=false,inputs="++") annotation(Placement(transformation(origin={-95,90},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(u1(Type(ref="double"),Dimension=1),u2(Type(ref="double"),Dimension=1)),y(Type(ref="double"),Dimension=1)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap),SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.MathOperation.Gain x_l1_gain(k=l1_gain_xy) annotation(Placement(transformation(origin={-45,90},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)),SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.MathOperation.Gain x_kp_gain(k=kp_x) annotation(Placement(transformation(origin={-95,125},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)),SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.MathOperation.Gain x_kd_gain(k=kd_x) annotation(Placement(transformation(origin={-45,125},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)),SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.MathOperation.Sum pitch_raw_sum(isSaturate=false,inputs="+++") annotation(Placement(transformation(origin={55,110},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(u1(Type(ref="double"),Dimension=1),u2(Type(ref="double"),Dimension=1),u3(Type(ref="double"),Dimension=1)),y(Type(ref="double"),Dimension=1)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap),SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.MathOperation.Gain pitch_scale(k=0.1) annotation(Placement(transformation(origin={105,110},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)),SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Discontinuities.Saturation pitch_ref_sat(upLimit=roll_pitch_cmd_limit,lowLimit=-roll_pitch_cmd_limit) annotation(Placement(transformation(origin={150,110},extent={{-10,-10},{10,10}})));

    SysplorerEmbeddedCoder.MathOperation.Gain y_rate_gain(k=l1_model_decay) annotation(Placement(transformation(origin={-145,35},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)),SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.MathOperation.Gain y_decay_gain(k=l1_model_decay) annotation(Placement(transformation(origin={-145,5},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)),SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.MathOperation.Sum y_l1_sum(isSaturate=false,inputs="++") annotation(Placement(transformation(origin={-95,20},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(u1(Type(ref="double"),Dimension=1),u2(Type(ref="double"),Dimension=1)),y(Type(ref="double"),Dimension=1)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap),SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.MathOperation.Gain y_l1_gain(k=l1_gain_xy) annotation(Placement(transformation(origin={-45,20},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)),SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.MathOperation.Gain y_kp_gain(k=kp_y) annotation(Placement(transformation(origin={-95,55},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)),SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.MathOperation.Gain y_kd_gain(k=kd_y) annotation(Placement(transformation(origin={-45,55},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)),SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.MathOperation.Sum roll_raw_sum(isSaturate=false,inputs="+++") annotation(Placement(transformation(origin={55,40},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(u1(Type(ref="double"),Dimension=1),u2(Type(ref="double"),Dimension=1),u3(Type(ref="double"),Dimension=1)),y(Type(ref="double"),Dimension=1)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap),SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.MathOperation.Gain roll_scale(k=0.1) annotation(Placement(transformation(origin={105,40},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)),SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Discontinuities.Saturation roll_ref_sat(upLimit=roll_pitch_cmd_limit,lowLimit=-roll_pitch_cmd_limit) annotation(Placement(transformation(origin={150,40},extent={{-10,-10},{10,10}})));

    SysplorerEmbeddedCoder.MathOperation.Gain z_rate_gain(k=l1_model_decay) annotation(Placement(transformation(origin={-145,-40},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)),SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.MathOperation.Gain z_decay_gain(k=l1_model_decay) annotation(Placement(transformation(origin={-145,-70},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)),SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.MathOperation.Sum z_l1_sum(isSaturate=false,inputs="++") annotation(Placement(transformation(origin={-95,-55},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(u1(Type(ref="double"),Dimension=1),u2(Type(ref="double"),Dimension=1)),y(Type(ref="double"),Dimension=1)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap),SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.MathOperation.Gain z_l1_gain(k=l1_gain_z) annotation(Placement(transformation(origin={-45,-55},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)),SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.MathOperation.Gain z_kp_gain(k=kp_z) annotation(Placement(transformation(origin={-95,-105},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)),SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.MathOperation.Gain z_kd_gain(k=kd_z) annotation(Placement(transformation(origin={-45,-105},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)),SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.MathOperation.Gain z_ff_gain(k=kff_z) annotation(Placement(transformation(origin={-45,-130},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)),SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Sources.Constant z_integral_zero(k=0) annotation(Placement(transformation(origin={-45,-80},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(SampleTime(auto=true,group="D1")=0.01,Instance(y(Type(inherit=InheritType.constantValue,ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)))));
    SysplorerEmbeddedCoder.MathOperation.Sum thrust_pid_sum(isSaturate=false,inputs="++++") annotation(Placement(transformation(origin={35,-95},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(u1(Type(ref="double"),Dimension=1),u2(Type(ref="double"),Dimension=1),u3(Type(ref="double"),Dimension=1),u4(Type(ref="double"),Dimension=1)),y(Type(ref="double"),Dimension=1)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap),SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.MathOperation.Sum thrust_l1_sum(isSaturate=false,inputs="++") annotation(Placement(transformation(origin={90,-85},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(u1(Type(ref="double"),Dimension=1),u2(Type(ref="double"),Dimension=1)),y(Type(ref="double"),Dimension=1)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap),SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Discrete.DiscreteTimeIntegrator z_l1_filter(externalResetType=SysplorerEmbeddedCoder.Discrete.DiscreteTimeIntegrator.ExternalResetType.None,gain=0.01 / l1_filter_T,initCond=0) annotation(Placement(transformation(origin={35,-55},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(SampleTime(auto=true,group="D1")=0.01,Instance(u1(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),gain(Type(ref="double"),Dimension=1),initCond(Type(ref="double"),Dimension=1))),PortLabels(labelType="CustomType",labels(label(text="",instance="u1"),label(text="",instance="u2"),label(text="x0",instance="u3")))));
    SysplorerEmbeddedCoder.Discontinuities.Saturation thrust_sat(upLimit=output_limit,lowLimit=-output_limit) annotation(Placement(transformation(origin={140,-85},extent={{-10,-10},{10,10}})));

  equation
    connect(x_error,x_rate_gain.u) annotation(Line(points={{-190,90},{-175,90},{-175,105},{-157,105}},color={0,0,0}),__MWORKS(BlockSystem(NamedSignal)));
    connect(x_error,x_decay_gain.u) annotation(Line(points={{-190,90},{-175,90},{-175,75},{-157,75}},color={0,0,0}),__MWORKS(BlockSystem(NamedSignal)));
    connect(x_error,x_kp_gain.u) annotation(Line(points={{-190,90},{-128,90},{-128,125},{-107,125}},color={0,0,0}),__MWORKS(BlockSystem(NamedSignal)));
    connect(x_rate_gain.y,x_l1_sum.u1) annotation(Line(points={{-133,105},{-118,105},{-118,96},{-107,96}},color={0,0,0}));
    connect(x_decay_gain.y,x_l1_sum.u2) annotation(Line(points={{-133,75},{-118,75},{-118,84},{-107,84}},color={0,0,0}));
    connect(x_l1_sum.y,x_l1_gain.u) annotation(Line(points={{-83,90},{-57,90}},color={0,0,0}));
    connect(x_rate_gain.y,x_kd_gain.u) annotation(Line(points={{-133,105},{-118,105},{-118,125},{-57,125}},color={0,0,0}),__MWORKS(BlockSystem(NamedSignal)));
    connect(x_kp_gain.y,pitch_raw_sum.u1) annotation(Line(points={{-83,125},{34,125},{34,118},{43,118}},color={0,0,0}));
    connect(x_kd_gain.y,pitch_raw_sum.u2) annotation(Line(points={{-33,125},{30,125},{30,110},{43,110}},color={0,0,0}));
    connect(x_l1_gain.y,pitch_raw_sum.u3) annotation(Line(points={{-33,90},{34,90},{34,102},{43,102}},color={0,0,0}));
    connect(pitch_raw_sum.y,pitch_scale.u) annotation(Line(points={{67,110},{93,110}},color={0,0,0}));

    connect(y_error,y_rate_gain.u) annotation(Line(points={{-190,30},{-175,30},{-175,35},{-157,35}},color={0,0,0}),__MWORKS(BlockSystem(NamedSignal)));
    connect(y_error,y_decay_gain.u) annotation(Line(points={{-190,30},{-175,30},{-175,5},{-157,5}},color={0,0,0}),__MWORKS(BlockSystem(NamedSignal)));
    connect(y_error,y_kp_gain.u) annotation(Line(points={{-190,30},{-128,30},{-128,55},{-107,55}},color={0,0,0}),__MWORKS(BlockSystem(NamedSignal)));
    connect(y_rate_gain.y,y_l1_sum.u1) annotation(Line(points={{-133,35},{-118,35},{-118,26},{-107,26}},color={0,0,0}));
    connect(y_decay_gain.y,y_l1_sum.u2) annotation(Line(points={{-133,5},{-118,5},{-118,14},{-107,14}},color={0,0,0}));
    connect(y_l1_sum.y,y_l1_gain.u) annotation(Line(points={{-83,20},{-57,20}},color={0,0,0}));
    connect(y_rate_gain.y,y_kd_gain.u) annotation(Line(points={{-133,35},{-118,35},{-118,55},{-57,55}},color={0,0,0}),__MWORKS(BlockSystem(NamedSignal)));
    connect(y_kp_gain.y,roll_raw_sum.u1) annotation(Line(points={{-83,55},{34,55},{34,48},{43,48}},color={0,0,0}));
    connect(y_kd_gain.y,roll_raw_sum.u2) annotation(Line(points={{-33,55},{30,55},{30,40},{43,40}},color={0,0,0}));
    connect(y_l1_gain.y,roll_raw_sum.u3) annotation(Line(points={{-33,20},{34,20},{34,32},{43,32}},color={0,0,0}));
    connect(roll_raw_sum.y,roll_scale.u) annotation(Line(points={{67,40},{93,40}},color={0,0,0}));

    connect(z_error,z_rate_gain.u) annotation(Line(points={{-190,-30},{-175,-30},{-175,-40},{-157,-40}},color={0,0,0}),__MWORKS(BlockSystem(NamedSignal)));
    connect(z_error,z_decay_gain.u) annotation(Line(points={{-190,-30},{-175,-30},{-175,-70},{-157,-70}},color={0,0,0}),__MWORKS(BlockSystem(NamedSignal)));
    connect(z_error,z_kp_gain.u) annotation(Line(points={{-190,-30},{-128,-30},{-128,-105},{-107,-105}},color={0,0,0}),__MWORKS(BlockSystem(NamedSignal)));
    connect(z_rate_gain.y,z_l1_sum.u1) annotation(Line(points={{-133,-40},{-118,-40},{-118,-49},{-107,-49}},color={0,0,0}));
    connect(z_decay_gain.y,z_l1_sum.u2) annotation(Line(points={{-133,-70},{-118,-70},{-118,-61},{-107,-61}},color={0,0,0}));
    connect(z_l1_sum.y,z_l1_gain.u) annotation(Line(points={{-83,-55},{-57,-55}},color={0,0,0}));
    connect(z_rate_gain.y,z_kd_gain.u) annotation(Line(points={{-133,-40},{-120,-40},{-120,-105},{-57,-105}},color={0,0,0}),__MWORKS(BlockSystem(NamedSignal)));
    connect(z_ref_rate,z_ff_gain.u) annotation(Line(points={{-190,-90},{-82,-90},{-82,-130},{-57,-130}},color={0,0,0}));
    connect(z_kp_gain.y,thrust_pid_sum.u1) annotation(Line(points={{-83,-105},{14,-105},{14,-107},{23,-107}},color={0,0,0}));
    connect(z_integral_zero.y,thrust_pid_sum.u2) annotation(Line(points={{-33,-80},{14,-80},{14,-99},{23,-99}},color={0,0,0}));
    connect(z_kd_gain.y,thrust_pid_sum.u3) annotation(Line(points={{-33,-105},{10,-105},{10,-91},{23,-91}},color={0,0,0}));
    connect(z_ff_gain.y,thrust_pid_sum.u4) annotation(Line(points={{-33,-130},{14,-130},{14,-83},{23,-83}},color={0,0,0}));
    connect(thrust_pid_sum.y,thrust_l1_sum.u1) annotation(Line(points={{47,-95},{72,-95},{72,-91},{78,-91}},color={0,0,0}));
    connect(z_l1_gain.y,z_l1_filter.u1) annotation(Line(points={{-33,-55},{23,-55}},color={0,0,0}));
    connect(z_l1_filter.y,thrust_l1_sum.u2) annotation(Line(points={{47,-55},{70,-55},{70,-79},{78,-79}},color={0,0,0}));
    connect(pitch_scale.y,pitch_ref_sat.u) annotation(Line(points={{117,110},{138,110}},color={0,0,0}));
    connect(roll_scale.y,roll_ref_sat.u) annotation(Line(points={{117,40},{138,40}},color={0,0,0}));
    connect(thrust_l1_sum.y,thrust_sat.u) annotation(Line(points={{102,-85},{128,-85}},color={0,0,0}));
    connect(pitch_ref_sat.y,pitch_ref) annotation(Line(points={{162,110},{180,110},{180,70},{190,70}},color={0,0,0}));
    connect(roll_ref_sat.y,roll_ref) annotation(Line(points={{162,40},{180,40},{180,0},{190,0}},color={0,0,0}));
    connect(thrust_sat.y,thrust_ref) annotation(Line(points={{152,-85},{180,-85},{180,-70},{190,-70}},color={0,0,0}));
  end L1ResidualOuterLoopBlock;  model PIDAttitudeInnerLoopBlock
    "PID attitude inner loop"
    extends ModelWorkspace;
    annotation(__MWORKS(version="26.3.0",modelType=Control,PortArrangement(Left(roll_ref,pitch_ref,yaw_ref,roll_mea,pitch_mea,yaw_mea),Right(roll_cmd,pitch_cmd,yaw_cmd)),BlockSystem(blockKind=BlockKind.userModel,SampleTime(auto=true,group="")=0.01,OutputInterval=0.01),SysblockVersion="1.0"),
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
  end PIDAttitudeInnerLoopBlock;  model MotorMixerBlock
    "Quadrotor motor mixer"
    extends ModelWorkspace;
    annotation(__MWORKS(version="26.3.0",modelType=Control,PortArrangement(Left(thrust_ref,roll_cmd,pitch_cmd,yaw_cmd),Right(y,y1,y2,y3)),BlockSystem(blockKind=BlockKind.userModel,SampleTime(auto=true,group="")=0.01,OutputInterval=0.01),SysblockVersion="1.0"),
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
  end MotorMixerBlock;
equation
  connect(x_error, position_loop.x_error) 
    annotation(Line(points={{-290,180},{-230,180},{-230,119},{-191,119}},color={0,0,0}));
  connect(y_error, position_loop.y_error) 
    annotation(Line(points={{-290,130},{-220,130},{-220,96},{-191,96}},color={0,0,0}));
  connect(z_error, position_loop.z_error) 
    annotation(Line(points={{-290,80},{-218,80},{-218,74},{-191,74}},color={0,0,0}));
  connect(z_ref_rate, position_loop.z_ref_rate) 
    annotation(Line(points={{-290,30},{-220,30},{-220,51},{-191,51}},color={0,0,0}));

  connect(position_loop.roll_ref, attitude_loop.roll_ref) 
    annotation(Line(points={{-98,85},{-70,85},{-70,1},{-42,1}},color={0,0,0}));
  connect(position_loop.pitch_ref, attitude_loop.pitch_ref) 
    annotation(Line(points={{-98,112},{-58,112},{-58,-21},{-42,-21}},color={0,0,0}));
  connect(yaw_ref, attitude_loop.yaw_ref) 
    annotation(Line(points={{-290,-180},{-72,-180},{-72,-43},{-42,-43}},color={0,0,0}));
  connect(roll_mea, attitude_loop.roll_mea) 
    annotation(Line(points={{-290,-30},{-110,-30},{-110,-66},{-42,-66}},color={0,0,0}));
  connect(pitch_mea, attitude_loop.pitch_mea) 
    annotation(Line(points={{-290,-80},{-120,-80},{-120,-88},{-42,-88}},color={0,0,0}));
  connect(yaw_mea, attitude_loop.yaw_mea) 
    annotation(Line(points={{-290,-130},{-130,-130},{-130,-106},{-42,-106}},color={0,0,0}));

  connect(position_loop.thrust_ref, motor_mixer.thrust_ref) 
    annotation(Line(points={{-98,58},{86,58},{86,-1},{108,-1}},color={0,0,0}));
  connect(attitude_loop.roll_cmd, motor_mixer.roll_cmd) 
    annotation(Line(points={{52,-8},{86,-8},{86,-24},{108,-24}},color={0,0,0}));
  connect(attitude_loop.pitch_cmd, motor_mixer.pitch_cmd) 
    annotation(Line(points={{52,-35},{108,-35},{108,-46}},color={0,0,0}));
  connect(attitude_loop.yaw_cmd, motor_mixer.yaw_cmd) 
    annotation(Line(points={{52,-62},{86,-62},{86,-69},{108,-69}},color={0,0,0}));

  connect(motor_mixer.y, y) 
    annotation(Line(points={{202,-8},{230,-8},{230,150},{240,150}},color={0,0,0}));
  connect(motor_mixer.y1, y1) 
    annotation(Line(points={{202,-35},{230,-35},{230,50},{240,50}},color={0,0,0}));
  connect(motor_mixer.y2, y2) 
    annotation(Line(points={{202,-62},{230,-62},{230,-50},{240,-50}},color={0,0,0}));
  connect(motor_mixer.y3, y3) 
    annotation(Line(points={{202,-89},{230,-89},{230,-150},{240,-150}},color={0,0,0}));
end AwffL1ResidualGraphicalController;