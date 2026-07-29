within MoSimQuadrotorModel.Control.Implementations.Sysblocks;
model AWFF_InnovationGraphicalControllers
  "Openable overview for graphical L1, INDI, and rotor fault-isolation Sysblock controllers"
  import SysplorerEmbeddedCoder.Types.*;
  import BaseWorkspace.*;
  extends ModelWorkspace;
  annotation(__MWORKS(version="26.3.0",modelType=Control,BlockSystem(blockKind=BlockKind.userModel,SampleTime(auto=true,group="")=0.01,OutputInterval=0.01),SysblockVersion="1.0"),
    Icon(coordinateSystem(preserveAspectRatio=false),graphics={
      Rectangle(extent={{-100,-100},{100,100}},lineColor={45,80,120},fillColor={238,246,255},fillPattern=FillPattern.Solid,radius=8),
      Text(extent={{-90,34},{90,-2}},textString="AWFF",lineColor={20,45,75}),
      Text(extent={{-90,-10},{90,-44}},textString="Innovation",lineColor={20,45,75}),
      Text(extent={{-90,-52},{90,-82}},textString="L1 / INDI / MPC / Fault",lineColor={85,105,125})}),
    Diagram(coordinateSystem(extent={{-340,-520},{340,220}},grid={2,2})));

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
  end L1ResidualOuterLoopBlock;

  model PIDAttitudeInnerLoopBlock
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
  end PIDAttitudeInnerLoopBlock;

  model INDIAttitudeInnerLoopBlock
    "INDI-like incremental attitude inner loop"
    extends ModelWorkspace;
    annotation(__MWORKS(version="26.3.0",modelType=Control,PortArrangement(Left(roll_ref,pitch_ref,yaw_ref,roll_mea,pitch_mea,yaw_mea),Right(roll_cmd,pitch_cmd,yaw_cmd)),BlockSystem(blockKind=BlockKind.userModel,SampleTime(auto=true,group="")=0.01,OutputInterval=0.01),SysblockVersion="1.0"),
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
  end INDIAttitudeInnerLoopBlock;

  model MotorMixerBlock
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

  model KnownRotorFaultMixerBlock
    "Known rotor-1 efficiency allocation"
    extends ModelWorkspace;
    annotation(__MWORKS(version="26.3.0",modelType=Control,PortArrangement(Left(thrust_ref,roll_cmd,pitch_cmd,yaw_cmd),Right(y,y1,y2,y3)),BlockSystem(blockKind=BlockKind.userModel,SampleTime(auto=true,group="")=0.01,OutputInterval=0.01),SysblockVersion="1.0"),
      Icon(coordinateSystem(preserveAspectRatio=false),graphics={
        Rectangle(extent={{-100,-100},{100,100}},lineColor={135,95,45},fillColor={255,248,232},fillPattern=FillPattern.Solid,radius=8),
        Text(extent={{-90,26},{90,-8}},textString="Fault",lineColor={95,65,25}),
        Text(extent={{-90,-12},{90,-46}},textString="Allocation",lineColor={95,65,25})}),
      Diagram(coordinateSystem(extent={{-220,-140},{220,140}},grid={2,2})));
    parameter Real output_limit=20.0;
    parameter Real rotor1_efficiency=0.85;
    parameter Real min_rotor_efficiency=0.50;
    parameter Real rotor1_allocation_blend=0.52;
    SysplorerEmbeddedCoder.Port.Inport thrust_ref annotation(Placement(transformation(origin={-200,90},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Inport roll_cmd annotation(Placement(transformation(origin={-200,30},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Inport pitch_cmd annotation(Placement(transformation(origin={-200,-30},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Inport yaw_cmd annotation(Placement(transformation(origin={-200,-90},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Outport y annotation(Placement(transformation(origin={200,90},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Outport y1 annotation(Placement(transformation(origin={200,30},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Outport y2 annotation(Placement(transformation(origin={200,-30},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Outport y3 annotation(Placement(transformation(origin={200,-90},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    MotorMixerBlock raw_mixer(output_limit=1e9) annotation(Placement(transformation(origin={-40,0},extent={{-45,-50},{45,50}})));
    SysplorerEmbeddedCoder.MathOperation.Gain rotor1_comp_gain(k=1 + rotor1_allocation_blend * (1 / max(rotor1_efficiency,min_rotor_efficiency) - 1)) annotation(Placement(transformation(origin={70,80},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)),SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Discontinuities.Saturation rotor1_sat(upLimit=output_limit,lowLimit=-output_limit) annotation(Placement(transformation(origin={120,80},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Discontinuities.Saturation rotor2_sat(upLimit=output_limit,lowLimit=-output_limit) annotation(Placement(transformation(origin={120,25},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Discontinuities.Saturation rotor3_sat(upLimit=output_limit,lowLimit=-output_limit) annotation(Placement(transformation(origin={120,-25},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Discontinuities.Saturation rotor4_sat(upLimit=output_limit,lowLimit=-output_limit) annotation(Placement(transformation(origin={120,-80},extent={{-10,-10},{10,10}})));
  equation
    connect(thrust_ref,raw_mixer.thrust_ref) annotation(Line(points={{-190,90},{-120,90},{-120,32},{-86,32}},color={0,0,0}));
    connect(roll_cmd,raw_mixer.roll_cmd) annotation(Line(points={{-190,30},{-86,11}},color={0,0,0}));
    connect(pitch_cmd,raw_mixer.pitch_cmd) annotation(Line(points={{-190,-30},{-120,-30},{-120,-11},{-86,-11}},color={0,0,0}));
    connect(yaw_cmd,raw_mixer.yaw_cmd) annotation(Line(points={{-190,-90},{-120,-90},{-120,-32},{-86,-32}},color={0,0,0}));
    connect(raw_mixer.y,rotor1_comp_gain.u) annotation(Line(points={{6,32},{42,32},{42,80},{58,80}},color={0,0,0}));
    connect(rotor1_comp_gain.y,rotor1_sat.u) annotation(Line(points={{82,80},{108,80}},color={0,0,0}));
    connect(raw_mixer.y1,rotor2_sat.u) annotation(Line(points={{6,11},{90,11},{90,25},{108,25}},color={0,0,0}));
    connect(raw_mixer.y2,rotor3_sat.u) annotation(Line(points={{6,-11},{90,-11},{90,-25},{108,-25}},color={0,0,0}));
    connect(raw_mixer.y3,rotor4_sat.u) annotation(Line(points={{6,-32},{90,-32},{90,-80},{108,-80}},color={0,0,0}));
    connect(rotor1_sat.y,y) annotation(Line(points={{132,80},{160,80},{160,90},{190,90}},color={0,0,0}));
    connect(rotor2_sat.y,y1) annotation(Line(points={{132,25},{160,25},{160,30},{190,30}},color={0,0,0}));
    connect(rotor3_sat.y,y2) annotation(Line(points={{132,-25},{160,-25},{160,-30},{190,-30}},color={0,0,0}));
    connect(rotor4_sat.y,y3) annotation(Line(points={{132,-80},{160,-80},{160,-90},{190,-90}},color={0,0,0}));
  end KnownRotorFaultMixerBlock;

  model RotorFaultIsolationBlock
    "Online four-rotor fault isolation from lateral residual signature"
    extends ModelWorkspace;
    annotation(__MWORKS(version="26.3.0",modelType=Control,PortArrangement(Left(x_error,y_error),Right(eta_hat1,eta_hat2,eta_hat3,eta_hat4,fault_index)),BlockSystem(blockKind=BlockKind.userModel,SampleTime(auto=true,group="")=0.01,OutputInterval=0.01),SysblockVersion="1.0"),
      Icon(coordinateSystem(preserveAspectRatio=false),graphics={
        Rectangle(extent={{-100,-100},{100,100}},lineColor={145,55,55},fillColor={255,238,238},fillPattern=FillPattern.Solid,radius=8),
        Text(extent={{-90,26},{90,-8}},textString="Fault",lineColor={100,35,35}),
        Text(extent={{-90,-12},{90,-46}},textString="Isolation",lineColor={100,35,35})}),
      Diagram(coordinateSystem(extent={{-220,-160},{220,160}},grid={2,2})));

    parameter Real position_derivative_filter_T=0.05;
    parameter Real eta_min_est=0.50;
    parameter Real eta_max_est=1.00;
    parameter Real eta_est_filter_T=5.0;
    parameter Real eta_signature_deadband=0.015;
    parameter Real eta_signature_gain=2.65;
    parameter Real fault_lock_margin=0.012;

    SysplorerEmbeddedCoder.Port.Inport x_error annotation(Placement(transformation(origin={-200,50},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Inport y_error annotation(Placement(transformation(origin={-200,-50},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Outport eta_hat1 annotation(Placement(transformation(origin={200,100},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Outport eta_hat2 annotation(Placement(transformation(origin={200,50},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Outport eta_hat3 annotation(Placement(transformation(origin={200,0},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Outport eta_hat4 annotation(Placement(transformation(origin={200,-50},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Outport fault_index annotation(Placement(transformation(origin={200,-110},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.MathOperation.Gain neg_x_half(k=-0.5) annotation(Placement(transformation(origin={-120,85},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)),SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.MathOperation.Gain pos_x_half(k=0.5) annotation(Placement(transformation(origin={-120,25},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)),SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.MathOperation.Gain neg_y_half(k=-0.5) annotation(Placement(transformation(origin={-120,-35},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)),SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.MathOperation.Gain pos_y_half(k=0.5) annotation(Placement(transformation(origin={-120,-95},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)),SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.MathOperation.Sum sig1_sum(isSaturate=false,inputs="++") annotation(Placement(transformation(origin={-45,85},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(u1(Type(ref="double"),Dimension=1),u2(Type(ref="double"),Dimension=1)),y(Type(ref="double"),Dimension=1)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap),SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.MathOperation.Sum sig2_sum(isSaturate=false,inputs="++") annotation(Placement(transformation(origin={-45,35},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(u1(Type(ref="double"),Dimension=1),u2(Type(ref="double"),Dimension=1)),y(Type(ref="double"),Dimension=1)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap),SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.MathOperation.Sum sig3_sum(isSaturate=false,inputs="++") annotation(Placement(transformation(origin={-45,-15},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(u1(Type(ref="double"),Dimension=1),u2(Type(ref="double"),Dimension=1)),y(Type(ref="double"),Dimension=1)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap),SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.MathOperation.Sum sig4_sum(isSaturate=false,inputs="++") annotation(Placement(transformation(origin={-45,-65},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(u1(Type(ref="double"),Dimension=1),u2(Type(ref="double"),Dimension=1)),y(Type(ref="double"),Dimension=1)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap),SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.MathOperation.Gain eta1_gain(k=-eta_signature_gain) annotation(Placement(transformation(origin={35,85},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)),SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.MathOperation.Gain eta2_gain(k=-eta_signature_gain) annotation(Placement(transformation(origin={35,35},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)),SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.MathOperation.Gain eta3_gain(k=-eta_signature_gain) annotation(Placement(transformation(origin={35,-15},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)),SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.MathOperation.Gain eta4_gain(k=-eta_signature_gain) annotation(Placement(transformation(origin={35,-65},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)),SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Discontinuities.DeadZone sig1_deadzone(startOfZone=-eta_signature_deadband,endOfZone=eta_signature_deadband) annotation(Placement(transformation(origin={-5,85},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Discontinuities.DeadZone sig2_deadzone(startOfZone=-eta_signature_deadband,endOfZone=eta_signature_deadband) annotation(Placement(transformation(origin={-5,35},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Discontinuities.DeadZone sig3_deadzone(startOfZone=-eta_signature_deadband,endOfZone=eta_signature_deadband) annotation(Placement(transformation(origin={-5,-15},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Discontinuities.DeadZone sig4_deadzone(startOfZone=-eta_signature_deadband,endOfZone=eta_signature_deadband) annotation(Placement(transformation(origin={-5,-65},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Discrete.DiscreteTimeIntegrator eta1_filter(externalResetType=SysplorerEmbeddedCoder.Discrete.DiscreteTimeIntegrator.ExternalResetType.None,gain=0.01 / eta_est_filter_T,initCond=0) annotation(Placement(transformation(origin={62,85},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(SampleTime(auto=true,group="D1")=0.01,Instance(u1(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),gain(Type(ref="double"),Dimension=1),initCond(Type(ref="double"),Dimension=1))),PortLabels(labelType="CustomType",labels(label(text="",instance="u1"),label(text="",instance="u2"),label(text="x0",instance="u3")))));
    SysplorerEmbeddedCoder.Discrete.DiscreteTimeIntegrator eta2_filter(externalResetType=SysplorerEmbeddedCoder.Discrete.DiscreteTimeIntegrator.ExternalResetType.None,gain=0.01 / eta_est_filter_T,initCond=0) annotation(Placement(transformation(origin={62,35},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(SampleTime(auto=true,group="D1")=0.01,Instance(u1(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),gain(Type(ref="double"),Dimension=1),initCond(Type(ref="double"),Dimension=1))),PortLabels(labelType="CustomType",labels(label(text="",instance="u1"),label(text="",instance="u2"),label(text="x0",instance="u3")))));
    SysplorerEmbeddedCoder.Discrete.DiscreteTimeIntegrator eta3_filter(externalResetType=SysplorerEmbeddedCoder.Discrete.DiscreteTimeIntegrator.ExternalResetType.None,gain=0.01 / eta_est_filter_T,initCond=0) annotation(Placement(transformation(origin={62,-15},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(SampleTime(auto=true,group="D1")=0.01,Instance(u1(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),gain(Type(ref="double"),Dimension=1),initCond(Type(ref="double"),Dimension=1))),PortLabels(labelType="CustomType",labels(label(text="",instance="u1"),label(text="",instance="u2"),label(text="x0",instance="u3")))));
    SysplorerEmbeddedCoder.Discrete.DiscreteTimeIntegrator eta4_filter(externalResetType=SysplorerEmbeddedCoder.Discrete.DiscreteTimeIntegrator.ExternalResetType.None,gain=0.01 / eta_est_filter_T,initCond=0) annotation(Placement(transformation(origin={62,-65},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(SampleTime(auto=true,group="D1")=0.01,Instance(u1(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),gain(Type(ref="double"),Dimension=1),initCond(Type(ref="double"),Dimension=1))),PortLabels(labelType="CustomType",labels(label(text="",instance="u1"),label(text="",instance="u2"),label(text="x0",instance="u3")))));
    SysplorerEmbeddedCoder.Sources.Constant one_eta(k=1) annotation(Placement(transformation(origin={35,130},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(SampleTime(auto=true,group="D1")=0.01,Instance(y(Type(inherit=InheritType.constantValue,ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)))));
    SysplorerEmbeddedCoder.MathOperation.Sum eta1_raw_sum(isSaturate=false,inputs="++") annotation(Placement(transformation(origin={90,85},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(u1(Type(ref="double"),Dimension=1),u2(Type(ref="double"),Dimension=1)),y(Type(ref="double"),Dimension=1)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap),SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.MathOperation.Sum eta2_raw_sum(isSaturate=false,inputs="++") annotation(Placement(transformation(origin={90,35},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(u1(Type(ref="double"),Dimension=1),u2(Type(ref="double"),Dimension=1)),y(Type(ref="double"),Dimension=1)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap),SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.MathOperation.Sum eta3_raw_sum(isSaturate=false,inputs="++") annotation(Placement(transformation(origin={90,-15},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(u1(Type(ref="double"),Dimension=1),u2(Type(ref="double"),Dimension=1)),y(Type(ref="double"),Dimension=1)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap),SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.MathOperation.Sum eta4_raw_sum(isSaturate=false,inputs="++") annotation(Placement(transformation(origin={90,-65},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(u1(Type(ref="double"),Dimension=1),u2(Type(ref="double"),Dimension=1)),y(Type(ref="double"),Dimension=1)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap),SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Discontinuities.Saturation eta1_sat(upLimit=eta_max_est,lowLimit=eta_min_est) annotation(Placement(transformation(origin={135,85},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Discontinuities.Saturation eta2_sat(upLimit=eta_max_est,lowLimit=eta_min_est) annotation(Placement(transformation(origin={135,35},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Discontinuities.Saturation eta3_sat(upLimit=eta_max_est,lowLimit=eta_min_est) annotation(Placement(transformation(origin={135,-15},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Discontinuities.Saturation eta4_sat(upLimit=eta_max_est,lowLimit=eta_min_est) annotation(Placement(transformation(origin={135,-65},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Sources.Constant fault_zero(k=0) annotation(Placement(transformation(origin={90,-125},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(SampleTime(auto=true,group="D1")=0.01,Instance(y(Type(inherit=InheritType.constantValue,ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)))));
    SysplorerEmbeddedCoder.Sources.Constant fault_one(k=1) annotation(Placement(transformation(origin={45,-145},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(SampleTime(auto=true,group="D1")=0.01,Instance(y(Type(inherit=InheritType.constantValue,ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)))));
    SysplorerEmbeddedCoder.SignalRouting.Switch fault_switch(threshold=fault_lock_margin) annotation(Placement(transformation(origin={135,-125},extent={{-10,-10},{10,10}})));
  equation
    connect(x_error,neg_x_half.u) annotation(Line(points={{-190,50},{-160,50},{-160,85},{-132,85}},color={0,0,0}),__MWORKS(BlockSystem(NamedSignal)));
    connect(x_error,pos_x_half.u) annotation(Line(points={{-190,50},{-160,50},{-160,25},{-132,25}},color={0,0,0}),__MWORKS(BlockSystem(NamedSignal)));
    connect(y_error,neg_y_half.u) annotation(Line(points={{-190,-50},{-160,-50},{-160,-35},{-132,-35}},color={0,0,0}),__MWORKS(BlockSystem(NamedSignal)));
    connect(y_error,pos_y_half.u) annotation(Line(points={{-190,-50},{-160,-50},{-160,-95},{-132,-95}},color={0,0,0}),__MWORKS(BlockSystem(NamedSignal)));
    connect(neg_x_half.y,sig1_sum.u1) annotation(Line(points={{-108,85},{-57,85},{-57,91}},color={0,0,0}),__MWORKS(BlockSystem(NamedSignal)));
    connect(pos_y_half.y,sig1_sum.u2) annotation(Line(points={{-108,-95},{-70,-95},{-70,79},{-57,79}},color={0,0,0}),__MWORKS(BlockSystem(NamedSignal)));
    connect(neg_x_half.y,sig2_sum.u1) annotation(Line(points={{-108,85},{-75,85},{-75,41},{-57,41}},color={0,0,0}),__MWORKS(BlockSystem(NamedSignal)));
    connect(neg_y_half.y,sig2_sum.u2) annotation(Line(points={{-108,-35},{-75,-35},{-75,29},{-57,29}},color={0,0,0}),__MWORKS(BlockSystem(NamedSignal)));
    connect(pos_x_half.y,sig3_sum.u1) annotation(Line(points={{-108,25},{-75,25},{-75,-9},{-57,-9}},color={0,0,0}),__MWORKS(BlockSystem(NamedSignal)));
    connect(neg_y_half.y,sig3_sum.u2) annotation(Line(points={{-108,-35},{-75,-35},{-75,-21},{-57,-21}},color={0,0,0}),__MWORKS(BlockSystem(NamedSignal)));
    connect(pos_x_half.y,sig4_sum.u1) annotation(Line(points={{-108,25},{-70,25},{-70,-59},{-57,-59}},color={0,0,0}),__MWORKS(BlockSystem(NamedSignal)));
    connect(pos_y_half.y,sig4_sum.u2) annotation(Line(points={{-108,-95},{-70,-95},{-70,-71},{-57,-71}},color={0,0,0}),__MWORKS(BlockSystem(NamedSignal)));
    connect(sig1_sum.y,sig1_deadzone.u) annotation(Line(points={{-33,85},{-17,85}},color={0,0,0}));
    connect(sig2_sum.y,sig2_deadzone.u) annotation(Line(points={{-33,35},{-17,35}},color={0,0,0}));
    connect(sig3_sum.y,sig3_deadzone.u) annotation(Line(points={{-33,-15},{-17,-15}},color={0,0,0}));
    connect(sig4_sum.y,sig4_deadzone.u) annotation(Line(points={{-33,-65},{-17,-65}},color={0,0,0}));
    connect(sig1_deadzone.y,eta1_gain.u) annotation(Line(points={{7,85},{23,85}},color={0,0,0}));
    connect(sig2_deadzone.y,eta2_gain.u) annotation(Line(points={{7,35},{23,35}},color={0,0,0}));
    connect(sig3_deadzone.y,eta3_gain.u) annotation(Line(points={{7,-15},{23,-15}},color={0,0,0}));
    connect(sig4_deadzone.y,eta4_gain.u) annotation(Line(points={{7,-65},{23,-65}},color={0,0,0}));
    connect(one_eta.y,eta1_raw_sum.u1) annotation(Line(points={{47,130},{70,130},{70,91},{78,91}},color={0,0,0}),__MWORKS(BlockSystem(NamedSignal)));
    connect(one_eta.y,eta2_raw_sum.u1) annotation(Line(points={{47,130},{66,130},{66,41},{78,41}},color={0,0,0}),__MWORKS(BlockSystem(NamedSignal)));
    connect(one_eta.y,eta3_raw_sum.u1) annotation(Line(points={{47,130},{62,130},{62,-9},{78,-9}},color={0,0,0}),__MWORKS(BlockSystem(NamedSignal)));
    connect(one_eta.y,eta4_raw_sum.u1) annotation(Line(points={{47,130},{58,130},{58,-59},{78,-59}},color={0,0,0}),__MWORKS(BlockSystem(NamedSignal)));
    connect(eta1_gain.y,eta1_filter.u1) annotation(Line(points={{47,85},{50,85}},color={0,0,0}));
    connect(eta2_gain.y,eta2_filter.u1) annotation(Line(points={{47,35},{50,35}},color={0,0,0}));
    connect(eta3_gain.y,eta3_filter.u1) annotation(Line(points={{47,-15},{50,-15}},color={0,0,0}));
    connect(eta4_gain.y,eta4_filter.u1) annotation(Line(points={{47,-65},{50,-65}},color={0,0,0}));
    connect(eta1_filter.y,eta1_raw_sum.u2) annotation(Line(points={{74,85},{78,79}},color={0,0,0}));
    connect(eta2_filter.y,eta2_raw_sum.u2) annotation(Line(points={{74,35},{78,29}},color={0,0,0}));
    connect(eta3_filter.y,eta3_raw_sum.u2) annotation(Line(points={{74,-15},{78,-21}},color={0,0,0}));
    connect(eta4_filter.y,eta4_raw_sum.u2) annotation(Line(points={{74,-65},{78,-71}},color={0,0,0}));
    connect(eta1_raw_sum.y,eta1_sat.u) annotation(Line(points={{102,85},{123,85}},color={0,0,0}));
    connect(eta2_raw_sum.y,eta2_sat.u) annotation(Line(points={{102,35},{123,35}},color={0,0,0}));
    connect(eta3_raw_sum.y,eta3_sat.u) annotation(Line(points={{102,-15},{123,-15}},color={0,0,0}));
    connect(eta4_raw_sum.y,eta4_sat.u) annotation(Line(points={{102,-65},{123,-65}},color={0,0,0}));
    connect(eta1_sat.y,eta_hat1) annotation(Line(points={{147,85},{180,85},{180,100},{190,100}},color={0,0,0}));
    connect(eta2_sat.y,eta_hat2) annotation(Line(points={{147,35},{180,35},{180,50},{190,50}},color={0,0,0}));
    connect(eta3_sat.y,eta_hat3) annotation(Line(points={{147,-15},{180,-15},{180,0},{190,0}},color={0,0,0}));
    connect(eta4_sat.y,eta_hat4) annotation(Line(points={{147,-65},{180,-65},{180,-50},{190,-50}},color={0,0,0}));
    connect(fault_one.y,fault_switch.u1) annotation(Line(points={{57,-145},{115,-145},{115,-119},{123,-119}},color={0,0,0}));
    connect(sig1_deadzone.y,fault_switch.u2) annotation(Line(points={{7,85},{116,85},{116,-125},{123,-125}},color={0,0,0}));
    connect(fault_zero.y,fault_switch.u3) annotation(Line(points={{102,-125},{123,-131}},color={0,0,0}));
    connect(fault_switch.y,fault_index) annotation(Line(points={{147,-125},{180,-125},{180,-110},{190,-110}},color={0,0,0}));
  end RotorFaultIsolationBlock;

  model AdaptiveFaultMixerBlock
    "Motor mixer with online rotor-efficiency allocation"
    extends ModelWorkspace;
    annotation(__MWORKS(version="26.3.0",modelType=Control,PortArrangement(Left(thrust_ref,roll_cmd,pitch_cmd,yaw_cmd,eta_hat1,eta_hat2,eta_hat3,eta_hat4),Right(y,y1,y2,y3)),BlockSystem(blockKind=BlockKind.userModel,SampleTime(auto=true,group="")=0.01,OutputInterval=0.01),SysblockVersion="1.0"),
      Icon(coordinateSystem(preserveAspectRatio=false),graphics={
        Rectangle(extent={{-100,-100},{100,100}},lineColor={120,55,55},fillColor={255,240,236},fillPattern=FillPattern.Solid,radius=8),
        Text(extent={{-90,26},{90,-8}},textString="Adaptive",lineColor={95,35,35}),
        Text(extent={{-90,-12},{90,-46}},textString="Fault Mixer",lineColor={95,35,35})}),
      Diagram(coordinateSystem(extent={{-220,-240},{220,140}},grid={2,2})));

    parameter Real output_limit=20.0;
    parameter Real allocation_blend=0.52;
    parameter Real min_rotor_efficiency=0.50;
    SysplorerEmbeddedCoder.Port.Inport thrust_ref annotation(Placement(transformation(origin={-200,90},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Inport roll_cmd annotation(Placement(transformation(origin={-200,30},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Inport pitch_cmd annotation(Placement(transformation(origin={-200,-30},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Inport yaw_cmd annotation(Placement(transformation(origin={-200,-90},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Inport eta_hat1 annotation(Placement(transformation(origin={-200,-135},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Inport eta_hat2 annotation(Placement(transformation(origin={-200,-165},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Inport eta_hat3 annotation(Placement(transformation(origin={-200,-195},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Inport eta_hat4 annotation(Placement(transformation(origin={-200,-225},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Outport y annotation(Placement(transformation(origin={200,90},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Outport y1 annotation(Placement(transformation(origin={200,30},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Outport y2 annotation(Placement(transformation(origin={200,-30},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Outport y3 annotation(Placement(transformation(origin={200,-90},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    MotorMixerBlock raw_mixer(output_limit=1e9) annotation(Placement(transformation(origin={-35,0},extent={{-45,-50},{45,50}})));
    SysplorerEmbeddedCoder.MathOperation.Product rotor1_eta_product(isSaturate=false,inputs="*/") annotation(Placement(transformation(origin={75,80},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(u1(Type(ref="double"),Dimension=1),u2(Type(ref="double"),Dimension=1)),y(Type(ref="double"),Dimension=1)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap),SampleTime(group="D1")=0.01),PortLabels(labelType="CustomType",labels(label(text="*",instance="u1"),label(text="/",instance="u2")))));
    SysplorerEmbeddedCoder.MathOperation.Product rotor2_eta_product(isSaturate=false,inputs="*/") annotation(Placement(transformation(origin={75,25},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(u1(Type(ref="double"),Dimension=1),u2(Type(ref="double"),Dimension=1)),y(Type(ref="double"),Dimension=1)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap),SampleTime(group="D1")=0.01),PortLabels(labelType="CustomType",labels(label(text="*",instance="u1"),label(text="/",instance="u2")))));
    SysplorerEmbeddedCoder.MathOperation.Product rotor3_eta_product(isSaturate=false,inputs="*/") annotation(Placement(transformation(origin={75,-30},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(u1(Type(ref="double"),Dimension=1),u2(Type(ref="double"),Dimension=1)),y(Type(ref="double"),Dimension=1)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap),SampleTime(group="D1")=0.01),PortLabels(labelType="CustomType",labels(label(text="*",instance="u1"),label(text="/",instance="u2")))));
    SysplorerEmbeddedCoder.MathOperation.Product rotor4_eta_product(isSaturate=false,inputs="*/") annotation(Placement(transformation(origin={75,-85},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(u1(Type(ref="double"),Dimension=1),u2(Type(ref="double"),Dimension=1)),y(Type(ref="double"),Dimension=1)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap),SampleTime(group="D1")=0.01),PortLabels(labelType="CustomType",labels(label(text="*",instance="u1"),label(text="/",instance="u2")))));
    SysplorerEmbeddedCoder.Discontinuities.Saturation rotor1_sat(upLimit=output_limit,lowLimit=-output_limit) annotation(Placement(transformation(origin={125,80},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Discontinuities.Saturation rotor2_sat(upLimit=output_limit,lowLimit=-output_limit) annotation(Placement(transformation(origin={125,25},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Discontinuities.Saturation rotor3_sat(upLimit=output_limit,lowLimit=-output_limit) annotation(Placement(transformation(origin={125,-30},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Discontinuities.Saturation rotor4_sat(upLimit=output_limit,lowLimit=-output_limit) annotation(Placement(transformation(origin={125,-85},extent={{-10,-10},{10,10}})));
  equation
    connect(thrust_ref,raw_mixer.thrust_ref) annotation(Line(points={{-190,90},{-120,90},{-120,32},{-81,32}},color={0,0,0}));
    connect(roll_cmd,raw_mixer.roll_cmd) annotation(Line(points={{-190,30},{-81,11}},color={0,0,0}));
    connect(pitch_cmd,raw_mixer.pitch_cmd) annotation(Line(points={{-190,-30},{-120,-30},{-120,-11},{-81,-11}},color={0,0,0}));
    connect(yaw_cmd,raw_mixer.yaw_cmd) annotation(Line(points={{-190,-90},{-120,-90},{-120,-32},{-81,-32}},color={0,0,0}));
    connect(raw_mixer.y,rotor1_eta_product.u1) annotation(Line(points={{11,32},{40,32},{40,86},{63,86}},color={0,0,0}));
    connect(raw_mixer.y1,rotor2_eta_product.u1) annotation(Line(points={{11,11},{40,11},{40,31},{63,31}},color={0,0,0}));
    connect(raw_mixer.y2,rotor3_eta_product.u1) annotation(Line(points={{11,-11},{40,-11},{40,-24},{63,-24}},color={0,0,0}));
    connect(raw_mixer.y3,rotor4_eta_product.u1) annotation(Line(points={{11,-32},{40,-32},{40,-79},{63,-79}},color={0,0,0}));
    connect(eta_hat1,rotor1_eta_product.u2) annotation(Line(points={{-190,-135},{20,-135},{20,74},{63,74}},color={0,0,0}));
    connect(eta_hat2,rotor2_eta_product.u2) annotation(Line(points={{-190,-165},{28,-165},{28,19},{63,19}},color={0,0,0}));
    connect(eta_hat3,rotor3_eta_product.u2) annotation(Line(points={{-190,-195},{36,-195},{36,-36},{63,-36}},color={0,0,0}));
    connect(eta_hat4,rotor4_eta_product.u2) annotation(Line(points={{-190,-225},{44,-225},{44,-91},{63,-91}},color={0,0,0}));
    connect(rotor1_eta_product.y,rotor1_sat.u) annotation(Line(points={{87,80},{113,80}},color={0,0,0}));
    connect(rotor2_eta_product.y,rotor2_sat.u) annotation(Line(points={{87,25},{113,25}},color={0,0,0}));
    connect(rotor3_eta_product.y,rotor3_sat.u) annotation(Line(points={{87,-30},{113,-30}},color={0,0,0}));
    connect(rotor4_eta_product.y,rotor4_sat.u) annotation(Line(points={{87,-85},{113,-85}},color={0,0,0}));
    connect(rotor1_sat.y,y) annotation(Line(points={{137,80},{160,80},{160,90},{190,90}},color={0,0,0}));
    connect(rotor2_sat.y,y1) annotation(Line(points={{137,25},{160,25},{160,30},{190,30}},color={0,0,0}));
    connect(rotor3_sat.y,y2) annotation(Line(points={{137,-30},{190,-30}},color={0,0,0}));
    connect(rotor4_sat.y,y3) annotation(Line(points={{137,-85},{160,-85},{160,-90},{190,-90}},color={0,0,0}));
  end AdaptiveFaultMixerBlock;

  model AWFF_L1ResidualControllerGraphical_Sysblock
    "Graphical L1 residual AWFF controller"
    extends ModelWorkspace;
    annotation(__MWORKS(version="26.3.0",modelType=Control,PortArrangement(Left(x_error,y_error,z_error,z_ref_rate,roll_mea,pitch_mea,yaw_mea,yaw_ref),Right(y,y1,y2,y3)),BlockSystem(blockKind=BlockKind.userModel,SampleTime(auto=true,group="")=0.01,OutputInterval=0.02),SysblockVersion="1.0"),
      Icon(coordinateSystem(preserveAspectRatio=false)),Diagram(coordinateSystem(extent={{-340,-220},{320,220}},grid={2,2})));

    SysplorerEmbeddedCoder.Port.Inport x_error annotation(Placement(transformation(origin={-320,180},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Inport y_error annotation(Placement(transformation(origin={-320,130},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Inport z_error annotation(Placement(transformation(origin={-320,80},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Inport z_ref_rate annotation(Placement(transformation(origin={-320,30},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Inport roll_mea annotation(Placement(transformation(origin={-320,-30},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Inport pitch_mea annotation(Placement(transformation(origin={-320,-80},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Inport yaw_mea annotation(Placement(transformation(origin={-320,-130},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Inport yaw_ref annotation(Placement(transformation(origin={-320,-180},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Outport y annotation(Placement(transformation(origin={300,150},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Outport y1 annotation(Placement(transformation(origin={300,50},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Outport y2 annotation(Placement(transformation(origin={300,-50},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Outport y3 annotation(Placement(transformation(origin={300,-150},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));

    L1ResidualOuterLoopBlock l1_outer annotation(Placement(transformation(origin={-160,70},extent={{-50,-45},{50,45}})));
    PIDAttitudeInnerLoopBlock attitude_loop annotation(Placement(transformation(origin={0,-25},extent={{-50,-45},{50,45}})));
    MotorMixerBlock motor_mixer annotation(Placement(transformation(origin={165,-25},extent={{-50,-45},{50,45}})));
  equation
    connect(x_error,l1_outer.x_error) annotation(Line(points={{-310,180},{-240,180},{-240,111},{-211,111}},color={0,0,0}));
    connect(y_error,l1_outer.y_error) annotation(Line(points={{-310,130},{-230,130},{-230,84},{-211,84}},color={0,0,0}));
    connect(z_error,l1_outer.z_error) annotation(Line(points={{-310,80},{-230,80},{-230,56},{-211,56}},color={0,0,0}));
    connect(z_ref_rate,l1_outer.z_ref_rate) annotation(Line(points={{-310,30},{-230,30},{-230,29},{-211,29}},color={0,0,0}));
    connect(l1_outer.roll_ref,attitude_loop.roll_ref) annotation(Line(points={{-109,70},{-70,70},{-70,29},{-51,29}},color={0,0,0}));
    connect(l1_outer.pitch_ref,attitude_loop.pitch_ref) annotation(Line(points={{-109,102},{-58,102},{-58,6},{-51,6}},color={0,0,0}));
    connect(yaw_ref,attitude_loop.yaw_ref) annotation(Line(points={{-310,-180},{-78,-180},{-78,-16},{-51,-16}},color={0,0,0}));
    connect(roll_mea,attitude_loop.roll_mea) annotation(Line(points={{-310,-30},{-94,-30},{-94,-43},{-51,-43}},color={0,0,0}));
    connect(pitch_mea,attitude_loop.pitch_mea) annotation(Line(points={{-310,-80},{-102,-80},{-102,-66},{-51,-66}},color={0,0,0}));
    connect(yaw_mea,attitude_loop.yaw_mea) annotation(Line(points={{-310,-130},{-112,-130},{-112,-88},{-51,-88}},color={0,0,0}));
    connect(l1_outer.thrust_ref,motor_mixer.thrust_ref) annotation(Line(points={{-109,38},{92,38},{92,16},{114,16}},color={0,0,0}));
    connect(attitude_loop.roll_cmd,motor_mixer.roll_cmd) annotation(Line(points={{51,16},{92,16},{92,-12},{114,-12}},color={0,0,0}));
    connect(attitude_loop.pitch_cmd,motor_mixer.pitch_cmd) annotation(Line(points={{51,-25},{114,-25},{114,-39}},color={0,0,0}));
    connect(attitude_loop.yaw_cmd,motor_mixer.yaw_cmd) annotation(Line(points={{51,-66},{92,-66},{92,-66},{114,-66}},color={0,0,0}));
    connect(motor_mixer.y,y) annotation(Line(points={{216,16},{250,16},{250,150},{290,150}},color={0,0,0}));
    connect(motor_mixer.y1,y1) annotation(Line(points={{216,-12},{246,-12},{246,50},{290,50}},color={0,0,0}));
    connect(motor_mixer.y2,y2) annotation(Line(points={{216,-39},{246,-39},{246,-50},{290,-50}},color={0,0,0}));
    connect(motor_mixer.y3,y3) annotation(Line(points={{216,-66},{250,-66},{250,-150},{290,-150}},color={0,0,0}));
  end AWFF_L1ResidualControllerGraphical_Sysblock;

  model AWFF_INDIControllerGraphical_Sysblock
    "Graphical L1 residual plus INDI attitude controller"
    extends ModelWorkspace;
    annotation(__MWORKS(version="26.3.0",modelType=Control,PortArrangement(Left(x_error,y_error,z_error,z_ref_rate,roll_mea,pitch_mea,yaw_mea,yaw_ref),Right(y,y1,y2,y3)),BlockSystem(blockKind=BlockKind.userModel,SampleTime(auto=true,group="")=0.01,OutputInterval=0.02),SysblockVersion="1.0"),
      Icon(coordinateSystem(preserveAspectRatio=false)),Diagram(coordinateSystem(extent={{-340,-220},{320,220}},grid={2,2})));

    SysplorerEmbeddedCoder.Port.Inport x_error annotation(Placement(transformation(origin={-320,180},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Inport y_error annotation(Placement(transformation(origin={-320,130},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Inport z_error annotation(Placement(transformation(origin={-320,80},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Inport z_ref_rate annotation(Placement(transformation(origin={-320,30},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Inport roll_mea annotation(Placement(transformation(origin={-320,-30},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Inport pitch_mea annotation(Placement(transformation(origin={-320,-80},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Inport yaw_mea annotation(Placement(transformation(origin={-320,-130},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Inport yaw_ref annotation(Placement(transformation(origin={-320,-180},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Outport y annotation(Placement(transformation(origin={300,150},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Outport y1 annotation(Placement(transformation(origin={300,50},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Outport y2 annotation(Placement(transformation(origin={300,-50},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Outport y3 annotation(Placement(transformation(origin={300,-150},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));

    L1ResidualOuterLoopBlock l1_outer annotation(Placement(transformation(origin={-160,70},extent={{-50,-45},{50,45}})));
    INDIAttitudeInnerLoopBlock attitude_loop annotation(Placement(transformation(origin={0,-25},extent={{-50,-45},{50,45}})));
    MotorMixerBlock motor_mixer annotation(Placement(transformation(origin={165,-25},extent={{-50,-45},{50,45}})));
  equation
    connect(x_error,l1_outer.x_error) annotation(Line(points={{-310,180},{-240,180},{-240,111},{-211,111}},color={0,0,0}));
    connect(y_error,l1_outer.y_error) annotation(Line(points={{-310,130},{-230,130},{-230,84},{-211,84}},color={0,0,0}));
    connect(z_error,l1_outer.z_error) annotation(Line(points={{-310,80},{-230,80},{-230,56},{-211,56}},color={0,0,0}));
    connect(z_ref_rate,l1_outer.z_ref_rate) annotation(Line(points={{-310,30},{-230,30},{-230,29},{-211,29}},color={0,0,0}));
    connect(l1_outer.roll_ref,attitude_loop.roll_ref) annotation(Line(points={{-109,70},{-70,70},{-70,29},{-51,29}},color={0,0,0}));
    connect(l1_outer.pitch_ref,attitude_loop.pitch_ref) annotation(Line(points={{-109,102},{-58,102},{-58,6},{-51,6}},color={0,0,0}));
    connect(yaw_ref,attitude_loop.yaw_ref) annotation(Line(points={{-310,-180},{-78,-180},{-78,-16},{-51,-16}},color={0,0,0}));
    connect(roll_mea,attitude_loop.roll_mea) annotation(Line(points={{-310,-30},{-94,-30},{-94,-43},{-51,-43}},color={0,0,0}));
    connect(pitch_mea,attitude_loop.pitch_mea) annotation(Line(points={{-310,-80},{-102,-80},{-102,-66},{-51,-66}},color={0,0,0}));
    connect(yaw_mea,attitude_loop.yaw_mea) annotation(Line(points={{-310,-130},{-112,-130},{-112,-88},{-51,-88}},color={0,0,0}));
    connect(l1_outer.thrust_ref,motor_mixer.thrust_ref) annotation(Line(points={{-109,38},{92,38},{92,16},{114,16}},color={0,0,0}));
    connect(attitude_loop.roll_cmd,motor_mixer.roll_cmd) annotation(Line(points={{51,16},{92,16},{92,-12},{114,-12}},color={0,0,0}));
    connect(attitude_loop.pitch_cmd,motor_mixer.pitch_cmd) annotation(Line(points={{51,-25},{114,-25},{114,-39}},color={0,0,0}));
    connect(attitude_loop.yaw_cmd,motor_mixer.yaw_cmd) annotation(Line(points={{51,-66},{92,-66},{92,-66},{114,-66}},color={0,0,0}));
    connect(motor_mixer.y,y) annotation(Line(points={{216,16},{250,16},{250,150},{290,150}},color={0,0,0}));
    connect(motor_mixer.y1,y1) annotation(Line(points={{216,-12},{246,-12},{246,50},{290,50}},color={0,0,0}));
    connect(motor_mixer.y2,y2) annotation(Line(points={{216,-39},{246,-39},{246,-50},{290,-50}},color={0,0,0}));
    connect(motor_mixer.y3,y3) annotation(Line(points={{216,-66},{250,-66},{250,-150},{290,-150}},color={0,0,0}));
  end AWFF_INDIControllerGraphical_Sysblock;

  model AWFF_L1FaultAllocationControllerGraphical_Sysblock
    "Graphical L1 residual controller with known rotor-1 fault allocation"
    extends ModelWorkspace;
    annotation(__MWORKS(version="26.3.0",modelType=Control,PortArrangement(Left(x_error,y_error,z_error,z_ref_rate,roll_mea,pitch_mea,yaw_mea,yaw_ref),Right(y,y1,y2,y3)),BlockSystem(blockKind=BlockKind.userModel,SampleTime(auto=true,group="")=0.01,OutputInterval=0.02),SysblockVersion="1.0"),
      Icon(coordinateSystem(preserveAspectRatio=false)),Diagram(coordinateSystem(extent={{-340,-220},{320,220}},grid={2,2})));

    SysplorerEmbeddedCoder.Port.Inport x_error annotation(Placement(transformation(origin={-320,180},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Inport y_error annotation(Placement(transformation(origin={-320,130},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Inport z_error annotation(Placement(transformation(origin={-320,80},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Inport z_ref_rate annotation(Placement(transformation(origin={-320,30},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Inport roll_mea annotation(Placement(transformation(origin={-320,-30},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Inport pitch_mea annotation(Placement(transformation(origin={-320,-80},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Inport yaw_mea annotation(Placement(transformation(origin={-320,-130},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Inport yaw_ref annotation(Placement(transformation(origin={-320,-180},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Outport y annotation(Placement(transformation(origin={300,150},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Outport y1 annotation(Placement(transformation(origin={300,50},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Outport y2 annotation(Placement(transformation(origin={300,-50},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Outport y3 annotation(Placement(transformation(origin={300,-150},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));

    L1ResidualOuterLoopBlock l1_outer annotation(Placement(transformation(origin={-160,70},extent={{-50,-45},{50,45}})));
    PIDAttitudeInnerLoopBlock attitude_loop annotation(Placement(transformation(origin={0,-25},extent={{-50,-45},{50,45}})));
    KnownRotorFaultMixerBlock motor_mixer annotation(Placement(transformation(origin={165,-25},extent={{-50,-45},{50,45}})));
  equation
    connect(x_error,l1_outer.x_error) annotation(Line(points={{-310,180},{-240,180},{-240,111},{-211,111}},color={0,0,0}));
    connect(y_error,l1_outer.y_error) annotation(Line(points={{-310,130},{-230,130},{-230,84},{-211,84}},color={0,0,0}));
    connect(z_error,l1_outer.z_error) annotation(Line(points={{-310,80},{-230,80},{-230,56},{-211,56}},color={0,0,0}));
    connect(z_ref_rate,l1_outer.z_ref_rate) annotation(Line(points={{-310,30},{-230,30},{-230,29},{-211,29}},color={0,0,0}));
    connect(l1_outer.roll_ref,attitude_loop.roll_ref) annotation(Line(points={{-109,70},{-70,70},{-70,29},{-51,29}},color={0,0,0}));
    connect(l1_outer.pitch_ref,attitude_loop.pitch_ref) annotation(Line(points={{-109,102},{-58,102},{-58,6},{-51,6}},color={0,0,0}));
    connect(yaw_ref,attitude_loop.yaw_ref) annotation(Line(points={{-310,-180},{-78,-180},{-78,-16},{-51,-16}},color={0,0,0}));
    connect(roll_mea,attitude_loop.roll_mea) annotation(Line(points={{-310,-30},{-94,-30},{-94,-43},{-51,-43}},color={0,0,0}));
    connect(pitch_mea,attitude_loop.pitch_mea) annotation(Line(points={{-310,-80},{-102,-80},{-102,-66},{-51,-66}},color={0,0,0}));
    connect(yaw_mea,attitude_loop.yaw_mea) annotation(Line(points={{-310,-130},{-112,-130},{-112,-88},{-51,-88}},color={0,0,0}));
    connect(l1_outer.thrust_ref,motor_mixer.thrust_ref) annotation(Line(points={{-109,38},{92,38},{92,16},{114,16}},color={0,0,0}));
    connect(attitude_loop.roll_cmd,motor_mixer.roll_cmd) annotation(Line(points={{51,16},{92,16},{92,-12},{114,-12}},color={0,0,0}));
    connect(attitude_loop.pitch_cmd,motor_mixer.pitch_cmd) annotation(Line(points={{51,-25},{114,-25},{114,-39}},color={0,0,0}));
    connect(attitude_loop.yaw_cmd,motor_mixer.yaw_cmd) annotation(Line(points={{51,-66},{92,-66},{92,-66},{114,-66}},color={0,0,0}));
    connect(motor_mixer.y,y) annotation(Line(points={{216,16},{250,16},{250,150},{290,150}},color={0,0,0}));
    connect(motor_mixer.y1,y1) annotation(Line(points={{216,-12},{246,-12},{246,50},{290,50}},color={0,0,0}));
    connect(motor_mixer.y2,y2) annotation(Line(points={{216,-39},{246,-39},{246,-50},{290,-50}},color={0,0,0}));
    connect(motor_mixer.y3,y3) annotation(Line(points={{216,-66},{250,-66},{250,-150},{290,-150}},color={0,0,0}));
  end AWFF_L1FaultAllocationControllerGraphical_Sysblock;

  model AWFF_FaultCompensationControllerGraphical_Sysblock
    "Graphical AWFF controller with known rotor-1 fault compensation"
    extends ModelWorkspace;
    annotation(__MWORKS(version="26.3.0",modelType=Control,PortArrangement(Left(x_error,y_error,z_error,z_ref_rate,roll_mea,pitch_mea,yaw_mea,yaw_ref),Right(y,y1,y2,y3)),BlockSystem(blockKind=BlockKind.userModel,SampleTime(auto=true,group="")=0.01,OutputInterval=0.01),SysblockVersion="1.0"),
      Icon(coordinateSystem(preserveAspectRatio=false)),Diagram(coordinateSystem(extent={{-340,-220},{320,220}},grid={2,2})));

    SysplorerEmbeddedCoder.Port.Inport x_error annotation(Placement(transformation(origin={-320,180},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Inport y_error annotation(Placement(transformation(origin={-320,130},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Inport z_error annotation(Placement(transformation(origin={-320,80},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Inport z_ref_rate annotation(Placement(transformation(origin={-320,30},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Inport roll_mea annotation(Placement(transformation(origin={-320,-30},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Inport pitch_mea annotation(Placement(transformation(origin={-320,-80},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Inport yaw_mea annotation(Placement(transformation(origin={-320,-130},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Inport yaw_ref annotation(Placement(transformation(origin={-320,-180},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Outport y annotation(Placement(transformation(origin={300,150},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Outport y1 annotation(Placement(transformation(origin={300,50},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Outport y2 annotation(Placement(transformation(origin={300,-50},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Outport y3 annotation(Placement(transformation(origin={300,-150},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));

    L1ResidualOuterLoopBlock awff_outer(
      l1_gain_xy=0,
      l1_gain_z=0,
      l1_comp_limit_xy=0,
      l1_comp_limit_z=0) annotation(Placement(transformation(origin={-160,70},extent={{-50,-45},{50,45}})));
    PIDAttitudeInnerLoopBlock attitude_loop annotation(Placement(transformation(origin={0,-25},extent={{-50,-45},{50,45}})));
    KnownRotorFaultMixerBlock motor_mixer annotation(Placement(transformation(origin={165,-25},extent={{-50,-45},{50,45}})));
  equation
    connect(x_error,awff_outer.x_error) annotation(Line(points={{-310,180},{-240,180},{-240,111},{-211,111}},color={0,0,0}));
    connect(y_error,awff_outer.y_error) annotation(Line(points={{-310,130},{-230,130},{-230,84},{-211,84}},color={0,0,0}));
    connect(z_error,awff_outer.z_error) annotation(Line(points={{-310,80},{-230,80},{-230,56},{-211,56}},color={0,0,0}));
    connect(z_ref_rate,awff_outer.z_ref_rate) annotation(Line(points={{-310,30},{-230,30},{-230,29},{-211,29}},color={0,0,0}));
    connect(awff_outer.roll_ref,attitude_loop.roll_ref) annotation(Line(points={{-109,70},{-70,70},{-70,29},{-51,29}},color={0,0,0}));
    connect(awff_outer.pitch_ref,attitude_loop.pitch_ref) annotation(Line(points={{-109,102},{-58,102},{-58,6},{-51,6}},color={0,0,0}));
    connect(yaw_ref,attitude_loop.yaw_ref) annotation(Line(points={{-310,-180},{-78,-180},{-78,-16},{-51,-16}},color={0,0,0}));
    connect(roll_mea,attitude_loop.roll_mea) annotation(Line(points={{-310,-30},{-94,-30},{-94,-43},{-51,-43}},color={0,0,0}));
    connect(pitch_mea,attitude_loop.pitch_mea) annotation(Line(points={{-310,-80},{-102,-80},{-102,-66},{-51,-66}},color={0,0,0}));
    connect(yaw_mea,attitude_loop.yaw_mea) annotation(Line(points={{-310,-130},{-112,-130},{-112,-88},{-51,-88}},color={0,0,0}));
    connect(awff_outer.thrust_ref,motor_mixer.thrust_ref) annotation(Line(points={{-109,38},{92,38},{92,16},{114,16}},color={0,0,0}));
    connect(attitude_loop.roll_cmd,motor_mixer.roll_cmd) annotation(Line(points={{51,16},{92,16},{92,-12},{114,-12}},color={0,0,0}));
    connect(attitude_loop.pitch_cmd,motor_mixer.pitch_cmd) annotation(Line(points={{51,-25},{114,-25},{114,-39}},color={0,0,0}));
    connect(attitude_loop.yaw_cmd,motor_mixer.yaw_cmd) annotation(Line(points={{51,-66},{92,-66},{92,-66},{114,-66}},color={0,0,0}));
    connect(motor_mixer.y,y) annotation(Line(points={{216,16},{250,16},{250,150},{290,150}},color={0,0,0}));
    connect(motor_mixer.y1,y1) annotation(Line(points={{216,-12},{246,-12},{246,50},{290,50}},color={0,0,0}));
    connect(motor_mixer.y2,y2) annotation(Line(points={{216,-39},{246,-39},{246,-50},{290,-50}},color={0,0,0}));
    connect(motor_mixer.y3,y3) annotation(Line(points={{216,-66},{250,-66},{250,-150},{290,-150}},color={0,0,0}));
  end AWFF_FaultCompensationControllerGraphical_Sysblock;

  model AWFF_L1MultiFaultIsolationControllerGraphical_Sysblock
    "Graphical L1 residual controller with online four-rotor fault isolation"
    extends ModelWorkspace;
    annotation(__MWORKS(version="26.3.0",modelType=Control,PortArrangement(Left(x_error,y_error,z_error,z_ref_rate,roll_mea,pitch_mea,yaw_mea,yaw_ref),Right(y,y1,y2,y3,eta_hat1,eta_hat2,eta_hat3,eta_hat4,fault_index)),BlockSystem(blockKind=BlockKind.userModel,SampleTime(auto=true,group="")=0.01,OutputInterval=0.02),SysblockVersion="1.0"),
      Icon(coordinateSystem(preserveAspectRatio=false)),Diagram(coordinateSystem(extent={{-340,-360},{320,220}},grid={2,2})));

    SysplorerEmbeddedCoder.Port.Inport x_error annotation(Placement(transformation(origin={-320,180},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Inport y_error annotation(Placement(transformation(origin={-320,130},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Inport z_error annotation(Placement(transformation(origin={-320,80},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Inport z_ref_rate annotation(Placement(transformation(origin={-320,30},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Inport roll_mea annotation(Placement(transformation(origin={-320,-30},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Inport pitch_mea annotation(Placement(transformation(origin={-320,-80},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Inport yaw_mea annotation(Placement(transformation(origin={-320,-130},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Inport yaw_ref annotation(Placement(transformation(origin={-320,-180},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Outport y annotation(Placement(transformation(origin={300,150},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Outport y1 annotation(Placement(transformation(origin={300,50},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Outport y2 annotation(Placement(transformation(origin={300,-50},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Outport y3 annotation(Placement(transformation(origin={300,-150},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Outport eta_hat1 annotation(Placement(transformation(origin={300,-205},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Outport eta_hat2 annotation(Placement(transformation(origin={300,-235},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Outport eta_hat3 annotation(Placement(transformation(origin={300,-265},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Outport eta_hat4 annotation(Placement(transformation(origin={300,-295},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Outport fault_index annotation(Placement(transformation(origin={300,-330},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));

    L1ResidualOuterLoopBlock l1_outer annotation(Placement(transformation(origin={-160,70},extent={{-50,-45},{50,45}})));
    PIDAttitudeInnerLoopBlock attitude_loop annotation(Placement(transformation(origin={0,-25},extent={{-50,-45},{50,45}})));
    AdaptiveFaultMixerBlock motor_mixer annotation(Placement(transformation(origin={165,-25},extent={{-50,-45},{50,45}})));
    RotorFaultIsolationBlock fault_isolation annotation(Placement(transformation(origin={0,-165},extent={{-45,-35},{45,35}})));
  equation
    connect(x_error,l1_outer.x_error) annotation(Line(points={{-310,180},{-240,180},{-240,111},{-211,111}},color={0,0,0}));
    connect(y_error,l1_outer.y_error) annotation(Line(points={{-310,130},{-230,130},{-230,84},{-211,84}},color={0,0,0}));
    connect(z_error,l1_outer.z_error) annotation(Line(points={{-310,80},{-230,80},{-230,56},{-211,56}},color={0,0,0}));
    connect(z_ref_rate,l1_outer.z_ref_rate) annotation(Line(points={{-310,30},{-230,30},{-230,29},{-211,29}},color={0,0,0}));
    connect(l1_outer.roll_ref,attitude_loop.roll_ref) annotation(Line(points={{-109,70},{-70,70},{-70,29},{-51,29}},color={0,0,0}));
    connect(l1_outer.pitch_ref,attitude_loop.pitch_ref) annotation(Line(points={{-109,102},{-58,102},{-58,6},{-51,6}},color={0,0,0}));
    connect(yaw_ref,attitude_loop.yaw_ref) annotation(Line(points={{-310,-180},{-78,-180},{-78,-16},{-51,-16}},color={0,0,0}));
    connect(roll_mea,attitude_loop.roll_mea) annotation(Line(points={{-310,-30},{-94,-30},{-94,-43},{-51,-43}},color={0,0,0}));
    connect(pitch_mea,attitude_loop.pitch_mea) annotation(Line(points={{-310,-80},{-102,-80},{-102,-66},{-51,-66}},color={0,0,0}));
    connect(yaw_mea,attitude_loop.yaw_mea) annotation(Line(points={{-310,-130},{-112,-130},{-112,-88},{-51,-88}},color={0,0,0}));
    connect(l1_outer.thrust_ref,motor_mixer.thrust_ref) annotation(Line(points={{-109,38},{92,38},{92,16},{114,16}},color={0,0,0}));
    connect(attitude_loop.roll_cmd,motor_mixer.roll_cmd) annotation(Line(points={{51,16},{92,16},{92,-12},{114,-12}},color={0,0,0}));
    connect(attitude_loop.pitch_cmd,motor_mixer.pitch_cmd) annotation(Line(points={{51,-25},{114,-25},{114,-39}},color={0,0,0}));
    connect(attitude_loop.yaw_cmd,motor_mixer.yaw_cmd) annotation(Line(points={{51,-66},{92,-66},{92,-66},{114,-66}},color={0,0,0}));
    connect(motor_mixer.y,y) annotation(Line(points={{216,16},{250,16},{250,150},{290,150}},color={0,0,0}));
    connect(motor_mixer.y1,y1) annotation(Line(points={{216,-12},{246,-12},{246,50},{290,50}},color={0,0,0}));
    connect(motor_mixer.y2,y2) annotation(Line(points={{216,-39},{246,-39},{246,-50},{290,-50}},color={0,0,0}));
    connect(motor_mixer.y3,y3) annotation(Line(points={{216,-66},{250,-66},{250,-150},{290,-150}},color={0,0,0}));
    connect(x_error,fault_isolation.x_error) annotation(Line(points={{-310,180},{-250,180},{-250,-154},{-46,-154}},color={0,0,0}));
    connect(y_error,fault_isolation.y_error) annotation(Line(points={{-310,130},{-260,130},{-260,-176},{-46,-176}},color={0,0,0}));
    connect(fault_isolation.eta_hat1,motor_mixer.eta_hat1) annotation(Line(points={{46,-143},{88,-143},{88,-86},{114,-86}},color={0,0,0}));
    connect(fault_isolation.eta_hat2,motor_mixer.eta_hat2) annotation(Line(points={{46,-154},{96,-154},{96,-99},{114,-99}},color={0,0,0}));
    connect(fault_isolation.eta_hat3,motor_mixer.eta_hat3) annotation(Line(points={{46,-165},{104,-165},{104,-113},{114,-113}},color={0,0,0}));
    connect(fault_isolation.eta_hat4,motor_mixer.eta_hat4) annotation(Line(points={{46,-176},{112,-176},{112,-126},{114,-126}},color={0,0,0}));
    connect(fault_isolation.eta_hat1,eta_hat1) annotation(Line(points={{46,-143},{260,-143},{260,-205},{290,-205}},color={0,0,0}));
    connect(fault_isolation.eta_hat2,eta_hat2) annotation(Line(points={{46,-154},{252,-154},{252,-235},{290,-235}},color={0,0,0}));
    connect(fault_isolation.eta_hat3,eta_hat3) annotation(Line(points={{46,-165},{244,-165},{244,-265},{290,-265}},color={0,0,0}));
    connect(fault_isolation.eta_hat4,eta_hat4) annotation(Line(points={{46,-176},{236,-176},{236,-295},{290,-295}},color={0,0,0}));
    connect(fault_isolation.fault_index,fault_index) annotation(Line(points={{46,-189},{228,-189},{228,-330},{290,-330}},color={0,0,0}));
  end AWFF_L1MultiFaultIsolationControllerGraphical_Sysblock;

  model AWFF_L1OnlineFaultAllocationControllerGraphical_Sysblock
    "Graphical L1 residual controller with online rotor-1 efficiency allocation"
    extends ModelWorkspace;
    annotation(__MWORKS(version="26.3.0",modelType=Control,PortArrangement(Left(x_error,y_error,z_error,z_ref_rate,roll_mea,pitch_mea,yaw_mea,yaw_ref),Right(y,y1,y2,y3,eta_hat)),BlockSystem(blockKind=BlockKind.userModel,SampleTime(auto=true,group="")=0.01,OutputInterval=0.02),SysblockVersion="1.0"),
      Icon(coordinateSystem(preserveAspectRatio=false)),Diagram(coordinateSystem(extent={{-340,-300},{320,220}},grid={2,2})));

    SysplorerEmbeddedCoder.Port.Inport x_error annotation(Placement(transformation(origin={-320,180},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Inport y_error annotation(Placement(transformation(origin={-320,130},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Inport z_error annotation(Placement(transformation(origin={-320,80},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Inport z_ref_rate annotation(Placement(transformation(origin={-320,30},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Inport roll_mea annotation(Placement(transformation(origin={-320,-30},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Inport pitch_mea annotation(Placement(transformation(origin={-320,-80},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Inport yaw_mea annotation(Placement(transformation(origin={-320,-130},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Inport yaw_ref annotation(Placement(transformation(origin={-320,-180},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Outport y annotation(Placement(transformation(origin={300,150},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Outport y1 annotation(Placement(transformation(origin={300,50},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Outport y2 annotation(Placement(transformation(origin={300,-50},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Outport y3 annotation(Placement(transformation(origin={300,-150},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Outport eta_hat annotation(Placement(transformation(origin={300,-240},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));

    L1ResidualOuterLoopBlock l1_outer annotation(Placement(transformation(origin={-160,70},extent={{-50,-45},{50,45}})));
    PIDAttitudeInnerLoopBlock attitude_loop annotation(Placement(transformation(origin={0,-25},extent={{-50,-45},{50,45}})));
    AdaptiveFaultMixerBlock motor_mixer annotation(Placement(transformation(origin={165,-25},extent={{-50,-45},{50,45}})));
    Rotor1OnlineEfficiencyEstimatorBlock rotor1_eta_estimator annotation(Placement(transformation(origin={0,-185},extent={{-45,-35},{45,35}})));
    SysplorerEmbeddedCoder.Sources.Constant eta_one(k=1) annotation(Placement(transformation(origin={80,-245},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(SampleTime(auto=true,group="D1")=0.01,Instance(y(Type(inherit=InheritType.constantValue,ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)))));
  equation
    connect(x_error,l1_outer.x_error) annotation(Line(points={{-310,180},{-240,180},{-240,111},{-211,111}},color={0,0,0}));
    connect(y_error,l1_outer.y_error) annotation(Line(points={{-310,130},{-230,130},{-230,84},{-211,84}},color={0,0,0}));
    connect(z_error,l1_outer.z_error) annotation(Line(points={{-310,80},{-230,80},{-230,56},{-211,56}},color={0,0,0}));
    connect(z_ref_rate,l1_outer.z_ref_rate) annotation(Line(points={{-310,30},{-230,30},{-230,29},{-211,29}},color={0,0,0}));
    connect(l1_outer.roll_ref,attitude_loop.roll_ref) annotation(Line(points={{-109,70},{-70,70},{-70,29},{-51,29}},color={0,0,0}));
    connect(l1_outer.pitch_ref,attitude_loop.pitch_ref) annotation(Line(points={{-109,102},{-58,102},{-58,6},{-51,6}},color={0,0,0}));
    connect(yaw_ref,attitude_loop.yaw_ref) annotation(Line(points={{-310,-180},{-78,-180},{-78,-16},{-51,-16}},color={0,0,0}));
    connect(roll_mea,attitude_loop.roll_mea) annotation(Line(points={{-310,-30},{-94,-30},{-94,-43},{-51,-43}},color={0,0,0}));
    connect(pitch_mea,attitude_loop.pitch_mea) annotation(Line(points={{-310,-80},{-102,-80},{-102,-66},{-51,-66}},color={0,0,0}));
    connect(yaw_mea,attitude_loop.yaw_mea) annotation(Line(points={{-310,-130},{-112,-130},{-112,-88},{-51,-88}},color={0,0,0}));
    connect(l1_outer.thrust_ref,motor_mixer.thrust_ref) annotation(Line(points={{-109,38},{92,38},{92,16},{114,16}},color={0,0,0}));
    connect(attitude_loop.roll_cmd,motor_mixer.roll_cmd) annotation(Line(points={{51,16},{92,16},{92,-12},{114,-12}},color={0,0,0}));
    connect(attitude_loop.pitch_cmd,motor_mixer.pitch_cmd) annotation(Line(points={{51,-25},{114,-25},{114,-39}},color={0,0,0}));
    connect(attitude_loop.yaw_cmd,motor_mixer.yaw_cmd) annotation(Line(points={{51,-66},{92,-66},{92,-66},{114,-66}},color={0,0,0}));
    connect(x_error,rotor1_eta_estimator.x_error) annotation(Line(points={{-310,180},{-260,180},{-260,-164},{-46,-164}},color={0,0,0}));
    connect(y_error,rotor1_eta_estimator.y_error) annotation(Line(points={{-310,130},{-250,130},{-250,-199},{-46,-199}},color={0,0,0}));
    connect(rotor1_eta_estimator.eta_hat,motor_mixer.eta_hat1) annotation(Line(points={{46,-182},{98,-182},{98,-86},{114,-86}},color={0,0,0}));
    connect(eta_one.y,motor_mixer.eta_hat2) annotation(Line(points={{92,-245},{102,-245},{102,-99},{114,-99}},color={0,0,0}));
    connect(eta_one.y,motor_mixer.eta_hat3) annotation(Line(points={{92,-245},{106,-245},{106,-113},{114,-113}},color={0,0,0}));
    connect(eta_one.y,motor_mixer.eta_hat4) annotation(Line(points={{92,-245},{110,-245},{110,-126},{114,-126}},color={0,0,0}));
    connect(motor_mixer.y,y) annotation(Line(points={{216,16},{250,16},{250,150},{290,150}},color={0,0,0}));
    connect(motor_mixer.y1,y1) annotation(Line(points={{216,-12},{246,-12},{246,50},{290,50}},color={0,0,0}));
    connect(motor_mixer.y2,y2) annotation(Line(points={{216,-39},{246,-39},{246,-50},{290,-50}},color={0,0,0}));
    connect(motor_mixer.y3,y3) annotation(Line(points={{216,-66},{250,-66},{250,-150},{290,-150}},color={0,0,0}));
    connect(rotor1_eta_estimator.eta_hat,eta_hat) annotation(Line(points={{46,-182},{260,-182},{260,-240},{290,-240}},color={0,0,0}));
  end AWFF_L1OnlineFaultAllocationControllerGraphical_Sysblock;

  model LinearMPCOuterLoopBlock
    "Graphical finite-horizon linear MPC-style outer loop with L1 residual compensation"
    extends ModelWorkspace;
    annotation(__MWORKS(version="26.3.0",modelType=Control,PortArrangement(Left(x_error,y_error,z_error,z_ref_rate),Right(pitch_ref,roll_ref,thrust_ref)),BlockSystem(blockKind=BlockKind.userModel,SampleTime(auto=true,group="")=0.01,OutputInterval=0.01),SysblockVersion="1.0"),
      Icon(coordinateSystem(preserveAspectRatio=false),graphics={
        Rectangle(extent={{-100,-100},{100,100}},lineColor={35,95,145},fillColor={236,246,255},fillPattern=FillPattern.Solid,radius=8),
        Text(extent={{-90,28},{90,-6}},textString="Linear MPC",lineColor={20,55,95}),
        Text(extent={{-90,-12},{90,-46}},textString="Outer Loop",lineColor={20,55,95})}),
      Diagram(coordinateSystem(extent={{-320,-260},{320,240}},grid={2,2})));

    parameter Real mpc_dt=0.05;
    parameter Real mpc_horizon_steps=20;
    parameter Real mpc_kp_xy=1.65;
    parameter Real mpc_kd_xy=1.00;
    parameter Real mpc_terminal_gain_xy=0.04;
    parameter Real mpc_kp_z=8.0;
    parameter Real mpc_ki_z=6.0;
    parameter Real mpc_kd_z=4.0;
    parameter Real mpc_terminal_gain_z=0.03;
    parameter Real kff_z=0.35;
    parameter Real mpc_acc_limit_xy=2.5;
    parameter Real mpc_thrust_limit=20.0;
    parameter Real roll_pitch_cmd_limit=12/57.3;
    parameter Real position_derivative_filter_T=0.05;
    parameter Real altitude_derivative_filter_T=0.08;
    parameter Real l1_model_decay=1.25;
    parameter Real l1_filter_T=0.20;
    parameter Real l1_gain_xy=0.32;
    parameter Real l1_gain_z=0.35;
    parameter Real l1_comp_limit_xy=2.0;
    parameter Real l1_comp_limit_z=2.0;

    SysplorerEmbeddedCoder.Port.Inport x_error annotation(Placement(transformation(origin={-300,170},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Inport y_error annotation(Placement(transformation(origin={-300,60},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Inport z_error annotation(Placement(transformation(origin={-300,-70},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Inport z_ref_rate annotation(Placement(transformation(origin={-300,-210},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Outport pitch_ref annotation(Placement(transformation(origin={300,150},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Outport roll_ref annotation(Placement(transformation(origin={300,40},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Outport thrust_ref annotation(Placement(transformation(origin={300,-140},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));

    SysplorerEmbeddedCoder.Discrete.UnitDelay x_error_delay(initCond=0) annotation(Placement(transformation(origin={-238,195},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.MathOperation.Sum x_rate_sum(isSaturate=false,inputs="+-") annotation(Placement(transformation(origin={-198,178},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(u1(Type(ref="double"),Dimension=1),u2(Type(ref="double"),Dimension=1)),y(Type(ref="double"),Dimension=1)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap),SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.MathOperation.Gain x_rate_gain(k=1/position_derivative_filter_T) annotation(Placement(transformation(origin={-155,178},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)),SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.MathOperation.Gain x_horizon_gain(k=mpc_dt*mpc_horizon_steps) annotation(Placement(transformation(origin={-108,205},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)),SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.MathOperation.Sum x_terminal_sum(isSaturate=false,inputs="++") annotation(Placement(transformation(origin={-60,190},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(u1(Type(ref="double"),Dimension=1),u2(Type(ref="double"),Dimension=1)),y(Type(ref="double"),Dimension=1)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap),SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.MathOperation.Gain x_decay_gain(k=l1_model_decay) annotation(Placement(transformation(origin={-108,145},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)),SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.MathOperation.Sum x_residual_sum(isSaturate=false,inputs="++") annotation(Placement(transformation(origin={-60,155},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(u1(Type(ref="double"),Dimension=1),u2(Type(ref="double"),Dimension=1)),y(Type(ref="double"),Dimension=1)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap),SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.MathOperation.Gain x_l1_gain(k=l1_gain_xy) annotation(Placement(transformation(origin={-12,155},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)),SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Discrete.DiscreteTimeIntegrator x_l1_filter(externalResetType=SysplorerEmbeddedCoder.Discrete.DiscreteTimeIntegrator.ExternalResetType.None,gain=0.01/l1_filter_T,initCond=0) annotation(Placement(transformation(origin={34,155},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(SampleTime(auto=true,group="D1")=0.01,Instance(u1(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),gain(Type(ref="double"),Dimension=1),initCond(Type(ref="double"),Dimension=1)))));
    SysplorerEmbeddedCoder.Discontinuities.Saturation x_comp_sat(upLimit=l1_comp_limit_xy,lowLimit=-l1_comp_limit_xy) annotation(Placement(transformation(origin={80,155},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.MathOperation.Gain x_kp_gain(k=mpc_kp_xy) annotation(Placement(transformation(origin={-108,230},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)),SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.MathOperation.Gain x_kd_gain(k=mpc_kd_xy) annotation(Placement(transformation(origin={-108,178},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)),SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.MathOperation.Gain x_terminal_gain(k=mpc_terminal_gain_xy) annotation(Placement(transformation(origin={-12,190},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)),SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.MathOperation.Sum x_acc_sum(isSaturate=false,inputs="++++") annotation(Placement(transformation(origin={132,190},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(u1(Type(ref="double"),Dimension=1),u2(Type(ref="double"),Dimension=1),u3(Type(ref="double"),Dimension=1),u4(Type(ref="double"),Dimension=1)),y(Type(ref="double"),Dimension=1)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap),SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Discontinuities.Saturation x_acc_sat(upLimit=mpc_acc_limit_xy,lowLimit=-mpc_acc_limit_xy) annotation(Placement(transformation(origin={176,190},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.MathOperation.Gain pitch_scale(k=0.1) annotation(Placement(transformation(origin={220,190},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)),SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Discontinuities.Saturation pitch_ref_sat(upLimit=roll_pitch_cmd_limit,lowLimit=-roll_pitch_cmd_limit) annotation(Placement(transformation(origin={260,190},extent={{-10,-10},{10,10}})));

    SysplorerEmbeddedCoder.Discrete.UnitDelay y_error_delay(initCond=0) annotation(Placement(transformation(origin={-238,82},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.MathOperation.Sum y_rate_sum(isSaturate=false,inputs="+-") annotation(Placement(transformation(origin={-198,62},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(u1(Type(ref="double"),Dimension=1),u2(Type(ref="double"),Dimension=1)),y(Type(ref="double"),Dimension=1)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap),SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.MathOperation.Gain y_rate_gain(k=1/position_derivative_filter_T) annotation(Placement(transformation(origin={-155,62},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)),SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.MathOperation.Gain y_horizon_gain(k=mpc_dt*mpc_horizon_steps) annotation(Placement(transformation(origin={-108,90},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)),SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.MathOperation.Sum y_terminal_sum(isSaturate=false,inputs="++") annotation(Placement(transformation(origin={-60,78},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(u1(Type(ref="double"),Dimension=1),u2(Type(ref="double"),Dimension=1)),y(Type(ref="double"),Dimension=1)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap),SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.MathOperation.Gain y_decay_gain(k=l1_model_decay) annotation(Placement(transformation(origin={-108,30},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)),SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.MathOperation.Sum y_residual_sum(isSaturate=false,inputs="++") annotation(Placement(transformation(origin={-60,40},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(u1(Type(ref="double"),Dimension=1),u2(Type(ref="double"),Dimension=1)),y(Type(ref="double"),Dimension=1)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap),SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.MathOperation.Gain y_l1_gain(k=l1_gain_xy) annotation(Placement(transformation(origin={-12,40},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)),SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Discrete.DiscreteTimeIntegrator y_l1_filter(externalResetType=SysplorerEmbeddedCoder.Discrete.DiscreteTimeIntegrator.ExternalResetType.None,gain=0.01/l1_filter_T,initCond=0) annotation(Placement(transformation(origin={34,40},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(SampleTime(auto=true,group="D1")=0.01,Instance(u1(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),gain(Type(ref="double"),Dimension=1),initCond(Type(ref="double"),Dimension=1)))));
    SysplorerEmbeddedCoder.Discontinuities.Saturation y_comp_sat(upLimit=l1_comp_limit_xy,lowLimit=-l1_comp_limit_xy) annotation(Placement(transformation(origin={80,40},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.MathOperation.Gain y_kp_gain(k=mpc_kp_xy) annotation(Placement(transformation(origin={-108,118},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)),SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.MathOperation.Gain y_kd_gain(k=mpc_kd_xy) annotation(Placement(transformation(origin={-108,62},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)),SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.MathOperation.Gain y_terminal_gain(k=mpc_terminal_gain_xy) annotation(Placement(transformation(origin={-12,78},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)),SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.MathOperation.Sum y_acc_sum(isSaturate=false,inputs="++++") annotation(Placement(transformation(origin={132,78},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(u1(Type(ref="double"),Dimension=1),u2(Type(ref="double"),Dimension=1),u3(Type(ref="double"),Dimension=1),u4(Type(ref="double"),Dimension=1)),y(Type(ref="double"),Dimension=1)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap),SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Discontinuities.Saturation y_acc_sat(upLimit=mpc_acc_limit_xy,lowLimit=-mpc_acc_limit_xy) annotation(Placement(transformation(origin={176,78},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.MathOperation.Gain roll_scale(k=0.1) annotation(Placement(transformation(origin={220,78},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)),SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Discontinuities.Saturation roll_ref_sat(upLimit=roll_pitch_cmd_limit,lowLimit=-roll_pitch_cmd_limit) annotation(Placement(transformation(origin={260,78},extent={{-10,-10},{10,10}})));

    SysplorerEmbeddedCoder.Discrete.UnitDelay z_error_delay(initCond=0) annotation(Placement(transformation(origin={-238,-48},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.MathOperation.Sum z_rate_sum(isSaturate=false,inputs="+-") annotation(Placement(transformation(origin={-198,-68},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(u1(Type(ref="double"),Dimension=1),u2(Type(ref="double"),Dimension=1)),y(Type(ref="double"),Dimension=1)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap),SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.MathOperation.Gain z_rate_gain(k=1/altitude_derivative_filter_T) annotation(Placement(transformation(origin={-155,-68},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)),SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.MathOperation.Gain z_horizon_gain(k=mpc_dt*mpc_horizon_steps) annotation(Placement(transformation(origin={-108,-38},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)),SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.MathOperation.Sum z_terminal_sum(isSaturate=false,inputs="++") annotation(Placement(transformation(origin={-60,-52},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(u1(Type(ref="double"),Dimension=1),u2(Type(ref="double"),Dimension=1)),y(Type(ref="double"),Dimension=1)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap),SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.MathOperation.Gain z_decay_gain(k=l1_model_decay) annotation(Placement(transformation(origin={-108,-105},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)),SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.MathOperation.Sum z_residual_sum(isSaturate=false,inputs="++") annotation(Placement(transformation(origin={-60,-95},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(u1(Type(ref="double"),Dimension=1),u2(Type(ref="double"),Dimension=1)),y(Type(ref="double"),Dimension=1)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap),SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.MathOperation.Gain z_l1_gain(k=l1_gain_z) annotation(Placement(transformation(origin={-12,-95},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)),SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Discrete.DiscreteTimeIntegrator z_l1_filter_mpc(externalResetType=SysplorerEmbeddedCoder.Discrete.DiscreteTimeIntegrator.ExternalResetType.None,gain=0.01/l1_filter_T,initCond=0) annotation(Placement(transformation(origin={34,-95},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(SampleTime(auto=true,group="D1")=0.01,Instance(u1(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),gain(Type(ref="double"),Dimension=1),initCond(Type(ref="double"),Dimension=1)))));
    SysplorerEmbeddedCoder.Discontinuities.Saturation z_comp_sat(upLimit=l1_comp_limit_z,lowLimit=-l1_comp_limit_z) annotation(Placement(transformation(origin={80,-95},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Discrete.DiscreteTimeIntegrator z_integrator(externalResetType=SysplorerEmbeddedCoder.Discrete.DiscreteTimeIntegrator.ExternalResetType.None,gain=0.01,initCond=0) annotation(Placement(transformation(origin={-108,-150},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(SampleTime(auto=true,group="D1")=0.01,Instance(u1(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),gain(Type(ref="double"),Dimension=1),initCond(Type(ref="double"),Dimension=1)))));
    SysplorerEmbeddedCoder.MathOperation.Gain z_kp_gain(k=mpc_kp_z) annotation(Placement(transformation(origin={-12,-22},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)),SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.MathOperation.Gain z_ki_gain(k=mpc_ki_z) annotation(Placement(transformation(origin={-12,-150},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)),SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.MathOperation.Gain z_kd_gain(k=mpc_kd_z) annotation(Placement(transformation(origin={-12,-68},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)),SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.MathOperation.Gain z_terminal_gain(k=mpc_terminal_gain_z) annotation(Placement(transformation(origin={34,-52},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)),SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.MathOperation.Gain z_ff_gain(k=kff_z) annotation(Placement(transformation(origin={-12,-210},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)),SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.MathOperation.Sum thrust_sum(isSaturate=false,inputs="++++++") annotation(Placement(transformation(origin={140,-112},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(u1(Type(ref="double"),Dimension=1),u2(Type(ref="double"),Dimension=1),u3(Type(ref="double"),Dimension=1),u4(Type(ref="double"),Dimension=1),u5(Type(ref="double"),Dimension=1),u6(Type(ref="double"),Dimension=1)),y(Type(ref="double"),Dimension=1)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap),SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Discontinuities.Saturation thrust_sat(upLimit=mpc_thrust_limit,lowLimit=-mpc_thrust_limit) annotation(Placement(transformation(origin={220,-112},extent={{-10,-10},{10,10}})));
  equation
    connect(x_error,x_error_delay.u1) annotation(Line(points={{-290,170},{-268,170},{-268,195},{-250,195}},color={0,0,0}));
    connect(x_error,x_rate_sum.u1) annotation(Line(points={{-290,170},{-220,170},{-220,184},{-210,184}},color={0,0,0}),__MWORKS(BlockSystem(NamedSignal)));
    connect(x_error_delay.y,x_rate_sum.u2) annotation(Line(points={{-226,195},{-218,195},{-218,172},{-210,172}},color={0,0,0}));
    connect(x_rate_sum.y,x_rate_gain.u) annotation(Line(points={{-186,178},{-167,178}},color={0,0,0}));
    connect(x_rate_gain.y,x_horizon_gain.u) annotation(Line(points={{-143,178},{-132,178},{-132,205},{-120,205}},color={0,0,0}),__MWORKS(BlockSystem(NamedSignal)));
    connect(x_error,x_terminal_sum.u1) annotation(Line(points={{-290,170},{-82,170},{-82,196},{-72,196}},color={0,0,0}));
    connect(x_horizon_gain.y,x_terminal_sum.u2) annotation(Line(points={{-96,205},{-78,205},{-78,184},{-72,184}},color={0,0,0}));
    connect(x_error,x_decay_gain.u) annotation(Line(points={{-290,170},{-132,170},{-132,145},{-120,145}},color={0,0,0}));
    connect(x_rate_gain.y,x_residual_sum.u1) annotation(Line(points={{-143,178},{-88,178},{-88,161},{-72,161}},color={0,0,0}));
    connect(x_decay_gain.y,x_residual_sum.u2) annotation(Line(points={{-96,145},{-82,145},{-82,149},{-72,149}},color={0,0,0}));
    connect(x_residual_sum.y,x_l1_gain.u) annotation(Line(points={{-48,155},{-24,155}},color={0,0,0}));
    connect(x_l1_gain.y,x_l1_filter.u1) annotation(Line(points={{0,155},{22,155}},color={0,0,0}));
    connect(x_l1_filter.y,x_comp_sat.u) annotation(Line(points={{46,155},{68,155}},color={0,0,0}));
    connect(x_error,x_kp_gain.u) annotation(Line(points={{-290,170},{-138,170},{-138,230},{-120,230}},color={0,0,0}));
    connect(x_rate_gain.y,x_kd_gain.u) annotation(Line(points={{-143,178},{-120,178}},color={0,0,0}));
    connect(x_terminal_sum.y,x_terminal_gain.u) annotation(Line(points={{-48,190},{-24,190}},color={0,0,0}));
    connect(x_kp_gain.y,x_acc_sum.u1) annotation(Line(points={{-96,230},{112,230},{112,205},{120,205}},color={0,0,0}));
    connect(x_kd_gain.y,x_acc_sum.u2) annotation(Line(points={{-96,178},{112,178},{112,195},{120,195}},color={0,0,0}));
    connect(x_terminal_gain.y,x_acc_sum.u3) annotation(Line(points={{0,190},{120,190}},color={0,0,0}));
    connect(x_comp_sat.y,x_acc_sum.u4) annotation(Line(points={{92,155},{112,155},{112,176},{120,176}},color={0,0,0}));
    connect(x_acc_sum.y,x_acc_sat.u) annotation(Line(points={{144,190},{164,190}},color={0,0,0}));
    connect(x_acc_sat.y,pitch_scale.u) annotation(Line(points={{188,190},{208,190}},color={0,0,0}));
    connect(pitch_scale.y,pitch_ref_sat.u) annotation(Line(points={{232,190},{248,190}},color={0,0,0}));
    connect(pitch_ref_sat.y,pitch_ref) annotation(Line(points={{272,190},{286,190},{286,150},{290,150}},color={0,0,0}));

    connect(y_error,y_error_delay.u1) annotation(Line(points={{-290,60},{-268,60},{-268,82},{-250,82}},color={0,0,0}));
    connect(y_error,y_rate_sum.u1) annotation(Line(points={{-290,60},{-220,60},{-220,68},{-210,68}},color={0,0,0}),__MWORKS(BlockSystem(NamedSignal)));
    connect(y_error_delay.y,y_rate_sum.u2) annotation(Line(points={{-226,82},{-218,82},{-218,56},{-210,56}},color={0,0,0}));
    connect(y_rate_sum.y,y_rate_gain.u) annotation(Line(points={{-186,62},{-167,62}},color={0,0,0}));
    connect(y_rate_gain.y,y_horizon_gain.u) annotation(Line(points={{-143,62},{-132,62},{-132,90},{-120,90}},color={0,0,0}),__MWORKS(BlockSystem(NamedSignal)));
    connect(y_error,y_terminal_sum.u1) annotation(Line(points={{-290,60},{-84,60},{-84,84},{-72,84}},color={0,0,0}));
    connect(y_horizon_gain.y,y_terminal_sum.u2) annotation(Line(points={{-96,90},{-78,90},{-78,72},{-72,72}},color={0,0,0}));
    connect(y_error,y_decay_gain.u) annotation(Line(points={{-290,60},{-132,60},{-132,30},{-120,30}},color={0,0,0}));
    connect(y_rate_gain.y,y_residual_sum.u1) annotation(Line(points={{-143,62},{-88,62},{-88,46},{-72,46}},color={0,0,0}));
    connect(y_decay_gain.y,y_residual_sum.u2) annotation(Line(points={{-96,30},{-82,30},{-82,34},{-72,34}},color={0,0,0}));
    connect(y_residual_sum.y,y_l1_gain.u) annotation(Line(points={{-48,40},{-24,40}},color={0,0,0}));
    connect(y_l1_gain.y,y_l1_filter.u1) annotation(Line(points={{0,40},{22,40}},color={0,0,0}));
    connect(y_l1_filter.y,y_comp_sat.u) annotation(Line(points={{46,40},{68,40}},color={0,0,0}));
    connect(y_error,y_kp_gain.u) annotation(Line(points={{-290,60},{-138,60},{-138,118},{-120,118}},color={0,0,0}));
    connect(y_rate_gain.y,y_kd_gain.u) annotation(Line(points={{-143,62},{-120,62}},color={0,0,0}));
    connect(y_terminal_sum.y,y_terminal_gain.u) annotation(Line(points={{-48,78},{-24,78}},color={0,0,0}));
    connect(y_kp_gain.y,y_acc_sum.u1) annotation(Line(points={{-96,118},{112,118},{112,93},{120,93}},color={0,0,0}));
    connect(y_kd_gain.y,y_acc_sum.u2) annotation(Line(points={{-96,62},{112,62},{112,83},{120,83}},color={0,0,0}));
    connect(y_terminal_gain.y,y_acc_sum.u3) annotation(Line(points={{0,78},{120,78}},color={0,0,0}));
    connect(y_comp_sat.y,y_acc_sum.u4) annotation(Line(points={{92,40},{112,40},{112,64},{120,64}},color={0,0,0}));
    connect(y_acc_sum.y,y_acc_sat.u) annotation(Line(points={{144,78},{164,78}},color={0,0,0}));
    connect(y_acc_sat.y,roll_scale.u) annotation(Line(points={{188,78},{208,78}},color={0,0,0}));
    connect(roll_scale.y,roll_ref_sat.u) annotation(Line(points={{232,78},{248,78}},color={0,0,0}));
    connect(roll_ref_sat.y,roll_ref) annotation(Line(points={{272,78},{286,78},{286,40},{290,40}},color={0,0,0}));

    connect(z_error,z_error_delay.u1) annotation(Line(points={{-290,-70},{-268,-70},{-268,-48},{-250,-48}},color={0,0,0}));
    connect(z_error,z_rate_sum.u1) annotation(Line(points={{-290,-70},{-220,-70},{-220,-62},{-210,-62}},color={0,0,0}),__MWORKS(BlockSystem(NamedSignal)));
    connect(z_error_delay.y,z_rate_sum.u2) annotation(Line(points={{-226,-48},{-218,-48},{-218,-74},{-210,-74}},color={0,0,0}));
    connect(z_rate_sum.y,z_rate_gain.u) annotation(Line(points={{-186,-68},{-167,-68}},color={0,0,0}));
    connect(z_rate_gain.y,z_horizon_gain.u) annotation(Line(points={{-143,-68},{-132,-68},{-132,-38},{-120,-38}},color={0,0,0}),__MWORKS(BlockSystem(NamedSignal)));
    connect(z_error,z_terminal_sum.u1) annotation(Line(points={{-290,-70},{-82,-70},{-82,-46},{-72,-46}},color={0,0,0}));
    connect(z_horizon_gain.y,z_terminal_sum.u2) annotation(Line(points={{-96,-38},{-78,-38},{-78,-58},{-72,-58}},color={0,0,0}));
    connect(z_error,z_decay_gain.u) annotation(Line(points={{-290,-70},{-132,-70},{-132,-105},{-120,-105}},color={0,0,0}));
    connect(z_rate_gain.y,z_residual_sum.u1) annotation(Line(points={{-143,-68},{-88,-68},{-88,-89},{-72,-89}},color={0,0,0}));
    connect(z_decay_gain.y,z_residual_sum.u2) annotation(Line(points={{-96,-105},{-82,-105},{-82,-101},{-72,-101}},color={0,0,0}));
    connect(z_residual_sum.y,z_l1_gain.u) annotation(Line(points={{-48,-95},{-24,-95}},color={0,0,0}));
    connect(z_l1_gain.y,z_l1_filter_mpc.u1) annotation(Line(points={{0,-95},{22,-95}},color={0,0,0}));
    connect(z_l1_filter_mpc.y,z_comp_sat.u) annotation(Line(points={{46,-95},{68,-95}},color={0,0,0}));
    connect(z_error,z_integrator.u1) annotation(Line(points={{-290,-70},{-138,-70},{-138,-150},{-120,-150}},color={0,0,0}));
    connect(z_error,z_kp_gain.u) annotation(Line(points={{-290,-70},{-44,-70},{-44,-22},{-24,-22}},color={0,0,0}));
    connect(z_integrator.y,z_ki_gain.u) annotation(Line(points={{-96,-150},{-24,-150}},color={0,0,0}));
    connect(z_rate_gain.y,z_kd_gain.u) annotation(Line(points={{-143,-68},{-24,-68}},color={0,0,0}));
    connect(z_terminal_sum.y,z_terminal_gain.u) annotation(Line(points={{-48,-52},{22,-52}},color={0,0,0}));
    connect(z_ref_rate,z_ff_gain.u) annotation(Line(points={{-290,-210},{-24,-210}},color={0,0,0}));
    connect(z_kp_gain.y,thrust_sum.u1) annotation(Line(points={{0,-22},{112,-22},{112,-97},{128,-97}},color={0,0,0}));
    connect(z_ki_gain.y,thrust_sum.u2) annotation(Line(points={{0,-150},{112,-150},{112,-103},{128,-103}},color={0,0,0}));
    connect(z_kd_gain.y,thrust_sum.u3) annotation(Line(points={{0,-68},{108,-68},{108,-109},{128,-109}},color={0,0,0}));
    connect(z_terminal_gain.y,thrust_sum.u4) annotation(Line(points={{46,-52},{104,-52},{104,-115},{128,-115}},color={0,0,0}));
    connect(z_ff_gain.y,thrust_sum.u5) annotation(Line(points={{0,-210},{112,-210},{112,-121},{128,-121}},color={0,0,0}));
    connect(z_comp_sat.y,thrust_sum.u6) annotation(Line(points={{92,-95},{116,-95},{116,-127},{128,-127}},color={0,0,0}));
    connect(thrust_sum.y,thrust_sat.u) annotation(Line(points={{152,-112},{208,-112}},color={0,0,0}));
    connect(thrust_sat.y,thrust_ref) annotation(Line(points={{232,-112},{270,-112},{270,-140},{290,-140}},color={0,0,0}));
  end LinearMPCOuterLoopBlock;

  model Rotor1OnlineEfficiencyEstimatorBlock
    "Graphical rotor-1 online efficiency estimator used by LinearMPC fault allocation"
    extends ModelWorkspace;
    annotation(__MWORKS(version="26.3.0",modelType=Control,PortArrangement(Left(x_error,y_error),Right(eta_hat)),BlockSystem(blockKind=BlockKind.userModel,SampleTime(auto=true,group="")=0.01,OutputInterval=0.01),SysblockVersion="1.0"),
      Icon(coordinateSystem(preserveAspectRatio=false),graphics={
        Rectangle(extent={{-100,-100},{100,100}},lineColor={130,70,45},fillColor={255,244,236},fillPattern=FillPattern.Solid,radius=8),
        Text(extent={{-90,28},{90,-6}},textString="Rotor1 eta",lineColor={90,45,25}),
        Text(extent={{-90,-12},{90,-46}},textString="Estimator",lineColor={90,45,25})}),
      Diagram(coordinateSystem(extent={{-220,-120},{220,120}},grid={2,2})));

    parameter Real eta_min_est=0.50;
    parameter Real eta_max_est=1.00;
    parameter Real eta_est_filter_T=5.0;
    parameter Real eta_signature_deadband=0.015;
    parameter Real eta_signature_gain=2.65;

    SysplorerEmbeddedCoder.Port.Inport x_error annotation(Placement(transformation(origin={-200,60},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Inport y_error annotation(Placement(transformation(origin={-200,-40},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Outport eta_hat annotation(Placement(transformation(origin={200,10},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));

    SysplorerEmbeddedCoder.MathOperation.Gain neg_x_half(k=-0.5) annotation(Placement(transformation(origin={-130,60},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)),SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.MathOperation.Gain pos_y_half(k=0.5) annotation(Placement(transformation(origin={-130,-40},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)),SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.MathOperation.Sum eta_signature_sum(isSaturate=false,inputs="++") annotation(Placement(transformation(origin={-70,10},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(u1(Type(ref="double"),Dimension=1),u2(Type(ref="double"),Dimension=1)),y(Type(ref="double"),Dimension=1)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap),SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Discontinuities.DeadZone eta_signature_deadzone(startOfZone=-eta_signature_deadband,endOfZone=eta_signature_deadband) annotation(Placement(transformation(origin={-25,10},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.MathOperation.Gain eta_drop_gain(k=-eta_signature_gain) annotation(Placement(transformation(origin={20,10},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)),SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Discrete.DiscreteTimeIntegrator eta_drop_filter(externalResetType=SysplorerEmbeddedCoder.Discrete.DiscreteTimeIntegrator.ExternalResetType.None,gain=0.01/eta_est_filter_T,initCond=0) annotation(Placement(transformation(origin={65,10},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(SampleTime(auto=true,group="D1")=0.01,Instance(u1(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),gain(Type(ref="double"),Dimension=1),initCond(Type(ref="double"),Dimension=1)))));
    SysplorerEmbeddedCoder.Sources.Constant one_eta(k=1) annotation(Placement(transformation(origin={65,70},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(SampleTime(auto=true,group="D1")=0.01,Instance(y(Type(inherit=InheritType.constantValue,ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)))));
    SysplorerEmbeddedCoder.MathOperation.Sum eta_raw_sum(isSaturate=false,inputs="++") annotation(Placement(transformation(origin={112,30},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(u1(Type(ref="double"),Dimension=1),u2(Type(ref="double"),Dimension=1)),y(Type(ref="double"),Dimension=1)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap),SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Discontinuities.Saturation eta_sat(upLimit=eta_max_est,lowLimit=eta_min_est) annotation(Placement(transformation(origin={155,30},extent={{-10,-10},{10,10}})));
  equation
    connect(x_error,neg_x_half.u) annotation(Line(points={{-190,60},{-142,60}},color={0,0,0}));
    connect(y_error,pos_y_half.u) annotation(Line(points={{-190,-40},{-142,-40}},color={0,0,0}));
    connect(neg_x_half.y,eta_signature_sum.u1) annotation(Line(points={{-118,60},{-92,60},{-92,16},{-82,16}},color={0,0,0}));
    connect(pos_y_half.y,eta_signature_sum.u2) annotation(Line(points={{-118,-40},{-92,-40},{-92,4},{-82,4}},color={0,0,0}));
    connect(eta_signature_sum.y,eta_signature_deadzone.u) annotation(Line(points={{-58,10},{-37,10}},color={0,0,0}));
    connect(eta_signature_deadzone.y,eta_drop_gain.u) annotation(Line(points={{-13,10},{8,10}},color={0,0,0}));
    connect(eta_drop_gain.y,eta_drop_filter.u1) annotation(Line(points={{32,10},{53,10}},color={0,0,0}));
    connect(one_eta.y,eta_raw_sum.u1) annotation(Line(points={{77,70},{94,70},{94,36},{100,36}},color={0,0,0}));
    connect(eta_drop_filter.y,eta_raw_sum.u2) annotation(Line(points={{77,10},{94,10},{94,24},{100,24}},color={0,0,0}));
    connect(eta_raw_sum.y,eta_sat.u) annotation(Line(points={{124,30},{143,30}},color={0,0,0}));
    connect(eta_sat.y,eta_hat) annotation(Line(points={{167,30},{184,30},{184,10},{190,10}},color={0,0,0}));
  end Rotor1OnlineEfficiencyEstimatorBlock;

  model AWFF_LinearMPCControllerGraphical_Sysblock
    "Graphical LinearMPC-style outer loop plus INDI attitude controller"
    extends ModelWorkspace;
    annotation(__MWORKS(version="26.3.0",modelType=Control,PortArrangement(Left(x_error,y_error,z_error,z_ref_rate,roll_mea,pitch_mea,yaw_mea,yaw_ref),Right(y,y1,y2,y3)),BlockSystem(blockKind=BlockKind.userModel,SampleTime(auto=true,group="")=0.01,OutputInterval=0.02),SysblockVersion="1.0"),
      Icon(coordinateSystem(preserveAspectRatio=false)),Diagram(coordinateSystem(extent={{-340,-220},{320,220}},grid={2,2})));

    SysplorerEmbeddedCoder.Port.Inport x_error annotation(Placement(transformation(origin={-320,180},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Inport y_error annotation(Placement(transformation(origin={-320,130},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Inport z_error annotation(Placement(transformation(origin={-320,80},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Inport z_ref_rate annotation(Placement(transformation(origin={-320,30},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Inport roll_mea annotation(Placement(transformation(origin={-320,-30},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Inport pitch_mea annotation(Placement(transformation(origin={-320,-80},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Inport yaw_mea annotation(Placement(transformation(origin={-320,-130},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Inport yaw_ref annotation(Placement(transformation(origin={-320,-180},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Outport y annotation(Placement(transformation(origin={300,150},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Outport y1 annotation(Placement(transformation(origin={300,50},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Outport y2 annotation(Placement(transformation(origin={300,-50},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Outport y3 annotation(Placement(transformation(origin={300,-150},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));

    LinearMPCOuterLoopBlock mpc_outer annotation(Placement(transformation(origin={-160,70},extent={{-50,-45},{50,45}})));
    INDIAttitudeInnerLoopBlock attitude_loop annotation(Placement(transformation(origin={0,-25},extent={{-50,-45},{50,45}})));
    MotorMixerBlock motor_mixer annotation(Placement(transformation(origin={165,-25},extent={{-50,-45},{50,45}})));
  equation
    connect(x_error,mpc_outer.x_error) annotation(Line(points={{-310,180},{-240,180},{-240,101},{-211,101}},color={0,0,0}));
    connect(y_error,mpc_outer.y_error) annotation(Line(points={{-310,130},{-230,130},{-230,82},{-211,82}},color={0,0,0}));
    connect(z_error,mpc_outer.z_error) annotation(Line(points={{-310,80},{-230,80},{-230,59},{-211,59}},color={0,0,0}));
    connect(z_ref_rate,mpc_outer.z_ref_rate) annotation(Line(points={{-310,30},{-230,30},{-230,34},{-211,34}},color={0,0,0}));
    connect(mpc_outer.roll_ref,attitude_loop.roll_ref) annotation(Line(points={{-109,77},{-70,77},{-70,29},{-51,29}},color={0,0,0}));
    connect(mpc_outer.pitch_ref,attitude_loop.pitch_ref) annotation(Line(points={{-109,97},{-58,97},{-58,6},{-51,6}},color={0,0,0}));
    connect(yaw_ref,attitude_loop.yaw_ref) annotation(Line(points={{-310,-180},{-78,-180},{-78,-16},{-51,-16}},color={0,0,0}));
    connect(roll_mea,attitude_loop.roll_mea) annotation(Line(points={{-310,-30},{-94,-30},{-94,-43},{-51,-43}},color={0,0,0}));
    connect(pitch_mea,attitude_loop.pitch_mea) annotation(Line(points={{-310,-80},{-102,-80},{-102,-66},{-51,-66}},color={0,0,0}));
    connect(yaw_mea,attitude_loop.yaw_mea) annotation(Line(points={{-310,-130},{-112,-130},{-112,-88},{-51,-88}},color={0,0,0}));
    connect(mpc_outer.thrust_ref,motor_mixer.thrust_ref) annotation(Line(points={{-109,45},{92,45},{92,16},{114,16}},color={0,0,0}));
    connect(attitude_loop.roll_cmd,motor_mixer.roll_cmd) annotation(Line(points={{51,16},{92,16},{92,-12},{114,-12}},color={0,0,0}));
    connect(attitude_loop.pitch_cmd,motor_mixer.pitch_cmd) annotation(Line(points={{51,-25},{114,-25},{114,-39}},color={0,0,0}));
    connect(attitude_loop.yaw_cmd,motor_mixer.yaw_cmd) annotation(Line(points={{51,-66},{92,-66},{92,-66},{114,-66}},color={0,0,0}));
    connect(motor_mixer.y,y) annotation(Line(points={{216,16},{250,16},{250,150},{290,150}},color={0,0,0}));
    connect(motor_mixer.y1,y1) annotation(Line(points={{216,-12},{246,-12},{246,50},{290,50}},color={0,0,0}));
    connect(motor_mixer.y2,y2) annotation(Line(points={{216,-39},{246,-39},{246,-50},{290,-50}},color={0,0,0}));
    connect(motor_mixer.y3,y3) annotation(Line(points={{216,-66},{250,-66},{250,-150},{290,-150}},color={0,0,0}));
  end AWFF_LinearMPCControllerGraphical_Sysblock;

  model AWFF_LinearMPCOnlineFaultAllocationControllerGraphical_Sysblock
    "Graphical LinearMPC controller with online rotor-1 efficiency allocation"
    extends ModelWorkspace;
    annotation(__MWORKS(version="26.3.0",modelType=Control,PortArrangement(Left(x_error,y_error,z_error,z_ref_rate,roll_mea,pitch_mea,yaw_mea,yaw_ref),Right(y,y1,y2,y3,eta_hat)),BlockSystem(blockKind=BlockKind.userModel,SampleTime(auto=true,group="")=0.01,OutputInterval=0.01),SysblockVersion="1.0"),
      Icon(coordinateSystem(preserveAspectRatio=false)),Diagram(coordinateSystem(extent={{-340,-300},{320,220}},grid={2,2})));

    SysplorerEmbeddedCoder.Port.Inport x_error annotation(Placement(transformation(origin={-320,180},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Inport y_error annotation(Placement(transformation(origin={-320,130},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Inport z_error annotation(Placement(transformation(origin={-320,80},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Inport z_ref_rate annotation(Placement(transformation(origin={-320,30},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Inport roll_mea annotation(Placement(transformation(origin={-320,-30},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Inport pitch_mea annotation(Placement(transformation(origin={-320,-80},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Inport yaw_mea annotation(Placement(transformation(origin={-320,-130},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Inport yaw_ref annotation(Placement(transformation(origin={-320,-180},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Outport y annotation(Placement(transformation(origin={300,150},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Outport y1 annotation(Placement(transformation(origin={300,50},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Outport y2 annotation(Placement(transformation(origin={300,-50},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Outport y3 annotation(Placement(transformation(origin={300,-150},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Outport eta_hat annotation(Placement(transformation(origin={300,-240},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));

    LinearMPCOuterLoopBlock mpc_outer annotation(Placement(transformation(origin={-160,70},extent={{-50,-45},{50,45}})));
    INDIAttitudeInnerLoopBlock attitude_loop annotation(Placement(transformation(origin={0,-25},extent={{-50,-45},{50,45}})));
    AdaptiveFaultMixerBlock motor_mixer annotation(Placement(transformation(origin={165,-25},extent={{-50,-45},{50,45}})));
    Rotor1OnlineEfficiencyEstimatorBlock rotor1_eta_estimator annotation(Placement(transformation(origin={0,-185},extent={{-45,-35},{45,35}})));
    SysplorerEmbeddedCoder.Sources.Constant eta_one(k=1) annotation(Placement(transformation(origin={80,-245},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(SampleTime(auto=true,group="D1")=0.01,Instance(y(Type(inherit=InheritType.constantValue,ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)))));
  equation
    connect(x_error,mpc_outer.x_error) annotation(Line(points={{-310,180},{-240,180},{-240,101},{-211,101}},color={0,0,0}));
    connect(y_error,mpc_outer.y_error) annotation(Line(points={{-310,130},{-230,130},{-230,82},{-211,82}},color={0,0,0}));
    connect(z_error,mpc_outer.z_error) annotation(Line(points={{-310,80},{-230,80},{-230,59},{-211,59}},color={0,0,0}));
    connect(z_ref_rate,mpc_outer.z_ref_rate) annotation(Line(points={{-310,30},{-230,30},{-230,34},{-211,34}},color={0,0,0}));
    connect(mpc_outer.roll_ref,attitude_loop.roll_ref) annotation(Line(points={{-109,77},{-70,77},{-70,29},{-51,29}},color={0,0,0}));
    connect(mpc_outer.pitch_ref,attitude_loop.pitch_ref) annotation(Line(points={{-109,97},{-58,97},{-58,6},{-51,6}},color={0,0,0}));
    connect(yaw_ref,attitude_loop.yaw_ref) annotation(Line(points={{-310,-180},{-78,-180},{-78,-16},{-51,-16}},color={0,0,0}));
    connect(roll_mea,attitude_loop.roll_mea) annotation(Line(points={{-310,-30},{-94,-30},{-94,-43},{-51,-43}},color={0,0,0}));
    connect(pitch_mea,attitude_loop.pitch_mea) annotation(Line(points={{-310,-80},{-102,-80},{-102,-66},{-51,-66}},color={0,0,0}));
    connect(yaw_mea,attitude_loop.yaw_mea) annotation(Line(points={{-310,-130},{-112,-130},{-112,-88},{-51,-88}},color={0,0,0}));
    connect(mpc_outer.thrust_ref,motor_mixer.thrust_ref) annotation(Line(points={{-109,45},{92,45},{92,16},{114,16}},color={0,0,0}));
    connect(attitude_loop.roll_cmd,motor_mixer.roll_cmd) annotation(Line(points={{51,16},{92,16},{92,-12},{114,-12}},color={0,0,0}));
    connect(attitude_loop.pitch_cmd,motor_mixer.pitch_cmd) annotation(Line(points={{51,-25},{114,-25},{114,-39}},color={0,0,0}));
    connect(attitude_loop.yaw_cmd,motor_mixer.yaw_cmd) annotation(Line(points={{51,-66},{92,-66},{92,-66},{114,-66}},color={0,0,0}));
    connect(x_error,rotor1_eta_estimator.x_error) annotation(Line(points={{-310,180},{-260,180},{-260,-164},{-46,-164}},color={0,0,0}));
    connect(y_error,rotor1_eta_estimator.y_error) annotation(Line(points={{-310,130},{-250,130},{-250,-199},{-46,-199}},color={0,0,0}));
    connect(rotor1_eta_estimator.eta_hat,motor_mixer.eta_hat1) annotation(Line(points={{46,-182},{98,-182},{98,-86},{114,-86}},color={0,0,0}));
    connect(eta_one.y,motor_mixer.eta_hat2) annotation(Line(points={{92,-245},{102,-245},{102,-99},{114,-99}},color={0,0,0}));
    connect(eta_one.y,motor_mixer.eta_hat3) annotation(Line(points={{92,-245},{106,-245},{106,-113},{114,-113}},color={0,0,0}));
    connect(eta_one.y,motor_mixer.eta_hat4) annotation(Line(points={{92,-245},{110,-245},{110,-126},{114,-126}},color={0,0,0}));
    connect(motor_mixer.y,y) annotation(Line(points={{216,16},{250,16},{250,150},{290,150}},color={0,0,0}));
    connect(motor_mixer.y1,y1) annotation(Line(points={{216,-12},{246,-12},{246,50},{290,50}},color={0,0,0}));
    connect(motor_mixer.y2,y2) annotation(Line(points={{216,-39},{246,-39},{246,-50},{290,-50}},color={0,0,0}));
    connect(motor_mixer.y3,y3) annotation(Line(points={{216,-66},{250,-66},{250,-150},{290,-150}},color={0,0,0}));
    connect(rotor1_eta_estimator.eta_hat,eta_hat) annotation(Line(points={{46,-182},{260,-182},{260,-240},{290,-240}},color={0,0,0}));
  end AWFF_LinearMPCOnlineFaultAllocationControllerGraphical_Sysblock;

  AWFF_L1ResidualControllerGraphical_Sysblock l1_residual_overview annotation(Placement(transformation(origin={-170,80},extent={{-70,-45},{70,45}})));
  AWFF_INDIControllerGraphical_Sysblock l1_indi_overview annotation(Placement(transformation(origin={170,80},extent={{-70,-45},{70,45}})));
  AWFF_L1FaultAllocationControllerGraphical_Sysblock known_fault_allocation_overview annotation(Placement(transformation(origin={-170,-100},extent={{-70,-45},{70,45}})));
  AWFF_L1MultiFaultIsolationControllerGraphical_Sysblock online_fault_isolation_overview annotation(Placement(transformation(origin={170,-100},extent={{-70,-45},{70,45}})));
  AWFF_LinearMPCControllerGraphical_Sysblock linear_mpc_overview annotation(Placement(transformation(origin={-170,-280},extent={{-70,-45},{70,45}})));
  AWFF_LinearMPCOnlineFaultAllocationControllerGraphical_Sysblock linear_mpc_fault_allocation_overview annotation(Placement(transformation(origin={170,-280},extent={{-70,-45},{70,45}})));
  AWFF_L1OnlineFaultAllocationControllerGraphical_Sysblock l1_online_fault_allocation_overview annotation(Placement(transformation(origin={-110,-440},extent={{-70,-45},{70,45}})));
  AWFF_FaultCompensationControllerGraphical_Sysblock awff_fault_compensation_overview annotation(Placement(transformation(origin={130,-440},extent={{-70,-45},{70,45}})));
end AWFF_InnovationGraphicalControllers;