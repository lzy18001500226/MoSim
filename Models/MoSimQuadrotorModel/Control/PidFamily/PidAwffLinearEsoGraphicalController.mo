within MoSimQuadrotorModel.Control.PidFamily;
model PidAwffLinearEsoGraphicalController
  "AWFF PID with linear ESO - graphical block implementation"
  extends ModelWorkspace;
  import SysplorerEmbeddedCoder.Types.*;
  import BaseWorkspace.*;
  annotation(__MWORKS(version="26.3.0",modelType=Control,PortArrangement(Left(x_error,y_error,z_error,z_ref_rate,roll_mea,pitch_mea,yaw_mea,yaw_ref),
Right(y,y1,y2,y3)),BlockSystem(blockKind=BlockKind.userModel,SampleTime(auto=true,group="")=0.01,OutputInterval=0.01),SysblockVersion="1.0"),
    Icon(coordinateSystem(preserveAspectRatio=false)),
    experiment(DoublePrecision=false,Algorithm=Euler,IntegratorStep=0.01,
      Interval=0.01,StartTime=0,StopTime=1,StoreEventValue=0),
    Diagram(coordinateSystem(extent={{-760,-350},{1050,480}},grid={2,2})));

  SysplorerEmbeddedCoder.Port.Inport x_error annotation(Placement(transformation(origin={-740,400},extent={{-10,-10},{10,10}})),iconTransformation(origin={-101.8,87.5},extent={{-1.8,-1.8},{1.8,1.8}}),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport y_error annotation(Placement(transformation(origin={-740,300},extent={{-10,-10},{10,10}})),iconTransformation(origin={-101.8,62.5},extent={{-1.8,-1.8},{1.8,1.8}}),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport z_error annotation(Placement(transformation(origin={-740,200},extent={{-10,-10},{10,10}})),iconTransformation(origin={-101.8,37.5},extent={{-1.8,-1.8},{1.8,1.8}}),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport z_ref_rate annotation(Placement(transformation(origin={-740,100},extent={{-10,-10},{10,10}})),iconTransformation(origin={-101.8,12.5},extent={{-1.8,-1.8},{1.8,1.8}}),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport roll_mea annotation(Placement(transformation(origin={-740,0},extent={{-10,-10},{10,10}})),iconTransformation(origin={-101.8,-12.5},extent={{-1.8,-1.8},{1.8,1.8}}),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport pitch_mea annotation(Placement(transformation(origin={-740,-100},extent={{-10,-10},{10,10}})),iconTransformation(origin={-101.8,-37.5},extent={{-1.8,-1.8},{1.8,1.8}}),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport yaw_mea annotation(Placement(transformation(origin={-740,-200},extent={{-10,-10},{10,10}})),iconTransformation(origin={-101.8,-62.5},extent={{-1.8,-1.8},{1.8,1.8}}),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport yaw_ref annotation(Placement(transformation(origin={-740,-300},extent={{-10,-10},{10,10}})),iconTransformation(origin={-101.8,-87.5},extent={{-1.8,-1.8},{1.8,1.8}}),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));

  SysplorerEmbeddedCoder.Port.Outport y annotation(Placement(transformation(origin={1030,300},extent={{-10,-10},{10,10}})),iconTransformation(origin={101.8,75},extent={{-1.8,-1.8},{1.8,1.8}}),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport y1 annotation(Placement(transformation(origin={1030,200},extent={{-10,-10},{10,10}})),iconTransformation(origin={101.8,25},extent={{-1.8,-1.8},{1.8,1.8}}),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport y2 annotation(Placement(transformation(origin={1030,100},extent={{-10,-10},{10,10}})),iconTransformation(origin={101.8,-25},extent={{-1.8,-1.8},{1.8,1.8}}),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport y3 annotation(Placement(transformation(origin={1030,0},extent={{-10,-10},{10,10}})),iconTransformation(origin={101.8,-75},extent={{-1.8,-1.8},{1.8,1.8}}),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));

  SysplorerEmbeddedCoder.MathOperation.Gain kp_x(k=0.165) annotation(Placement(transformation(origin={-600,420},extent={{-15,-15},{15,15}})));
  SysplorerEmbeddedCoder.Discrete.UnitDelay x_prev(initCond=0.0) annotation(Placement(transformation(origin={-600,350},extent={{-15,-15},{15,15}})));
  SysplorerEmbeddedCoder.MathOperation.Sum x_delta(inputs="+-") annotation(Placement(transformation(origin={-520,350},extent={{-15,-15},{15,15}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain x_d_rate(k=100.0) annotation(Placement(transformation(origin={-440,350},extent={{-15,-15},{15,15}})));
  SysplorerEmbeddedCoder.MathOperation.Gain kd_x(k=0.1) annotation(Placement(transformation(origin={-360,350},extent={{-15,-15},{15,15}})));
  SysplorerEmbeddedCoder.MathOperation.Sum x_pd(inputs="++") annotation(Placement(transformation(origin={-280,400},extent={{-15,-15},{15,15}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));

  SysplorerEmbeddedCoder.MathOperation.Gain kp_y(k=0.165) annotation(Placement(transformation(origin={-600,320},extent={{-15,-15},{15,15}})));
  SysplorerEmbeddedCoder.Discrete.UnitDelay y_prev(initCond=0.0) annotation(Placement(transformation(origin={-600,250},extent={{-15,-15},{15,15}})));
  SysplorerEmbeddedCoder.MathOperation.Sum y_delta(inputs="+-") annotation(Placement(transformation(origin={-520,250},extent={{-15,-15},{15,15}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain y_d_rate(k=100.0) annotation(Placement(transformation(origin={-440,250},extent={{-15,-15},{15,15}})));
  SysplorerEmbeddedCoder.MathOperation.Gain kd_y(k=0.1) annotation(Placement(transformation(origin={-360,250},extent={{-15,-15},{15,15}})));
  SysplorerEmbeddedCoder.MathOperation.Sum y_pd(inputs="++") annotation(Placement(transformation(origin={-280,300},extent={{-15,-15},{15,15}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));

  SysplorerEmbeddedCoder.MathOperation.Gain kp_z(k=0.8) annotation(Placement(transformation(origin={-600,220},extent={{-15,-15},{15,15}})));
  SysplorerEmbeddedCoder.Discrete.UnitDelay z_prev(initCond=0.0) annotation(Placement(transformation(origin={-600,150},extent={{-15,-15},{15,15}})));
  SysplorerEmbeddedCoder.MathOperation.Sum z_delta(inputs="+-") annotation(Placement(transformation(origin={-520,150},extent={{-15,-15},{15,15}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain z_d_rate(k=12.5) annotation(Placement(transformation(origin={-440,150},extent={{-15,-15},{15,15}})));
  SysplorerEmbeddedCoder.MathOperation.Gain kd_z(k=0.4) annotation(Placement(transformation(origin={-360,150},extent={{-15,-15},{15,15}})));
  SysplorerEmbeddedCoder.Continuous.Integrator z_int(initCond=0.0) annotation(Placement(transformation(origin={-600,80},extent={{-15,-15},{15,15}})));
  SysplorerEmbeddedCoder.MathOperation.Gain ki_z(k=0.6) annotation(Placement(transformation(origin={-520,80},extent={{-15,-15},{15,15}})));
  SysplorerEmbeddedCoder.MathOperation.Gain kff_z(k=0.035) annotation(Placement(transformation(origin={-520,120},extent={{-15,-15},{15,15}})));
  SysplorerEmbeddedCoder.MathOperation.Sum z_pid(inputs="++++") annotation(Placement(transformation(origin={-280,180},extent={{-15,-15},{15,15}})),__MWORKS(BlockSystem(Instance(u(u1,u2,u3,u4)))));

  SysplorerEmbeddedCoder.Discontinuities.Saturation pitch_limit(lowLimit=-0.209,upLimit=0.209) annotation(Placement(transformation(origin={-180,400},extent={{-15,-15},{15,15}})));
  SysplorerEmbeddedCoder.Discontinuities.Saturation roll_limit(lowLimit=-0.209,upLimit=0.209) annotation(Placement(transformation(origin={-180,300},extent={{-15,-15},{15,15}})));
  SysplorerEmbeddedCoder.Discontinuities.Saturation thrust_limit(lowLimit=-20.0,upLimit=20.0) annotation(Placement(transformation(origin={-180,180},extent={{-15,-15},{15,15}})));

  SysplorerEmbeddedCoder.MathOperation.Sum pitch_err(inputs="+-") annotation(Placement(transformation(origin={-80,400},extent={{-15,-15},{15,15}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum roll_err(inputs="++") annotation(Placement(transformation(origin={-80,300},extent={{-15,-15},{15,15}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum yaw_err(inputs="+-") annotation(Placement(transformation(origin={-80,-200},extent={{-15,-15},{15,15}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));

  SysplorerEmbeddedCoder.Discrete.UnitDelay pitch_prev(initCond=0.0) annotation(Placement(transformation(origin={0,350},extent={{-15,-15},{15,15}})));
  SysplorerEmbeddedCoder.MathOperation.Sum pitch_delta(inputs="+-") annotation(Placement(transformation(origin={80,350},extent={{-15,-15},{15,15}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain pitch_d_rate(k=33.333) annotation(Placement(transformation(origin={160,350},extent={{-15,-15},{15,15}})));
  SysplorerEmbeddedCoder.MathOperation.Gain kd_pitch(k=0.17) annotation(Placement(transformation(origin={240,350},extent={{-15,-15},{15,15}})));
  SysplorerEmbeddedCoder.MathOperation.Gain kp_pitch(k=1.4142) annotation(Placement(transformation(origin={0,420},extent={{-15,-15},{15,15}})));
  SysplorerEmbeddedCoder.MathOperation.Sum pitch_pd(inputs="++") annotation(Placement(transformation(origin={320,400},extent={{-15,-15},{15,15}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));

  SysplorerEmbeddedCoder.Discrete.UnitDelay roll_prev(initCond=0.0) annotation(Placement(transformation(origin={0,250},extent={{-15,-15},{15,15}})));
  SysplorerEmbeddedCoder.MathOperation.Sum roll_delta(inputs="+-") annotation(Placement(transformation(origin={80,250},extent={{-15,-15},{15,15}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain roll_d_rate(k=33.333) annotation(Placement(transformation(origin={160,250},extent={{-15,-15},{15,15}})));
  SysplorerEmbeddedCoder.MathOperation.Gain kd_roll(k=0.17) annotation(Placement(transformation(origin={240,250},extent={{-15,-15},{15,15}})));
  SysplorerEmbeddedCoder.MathOperation.Gain kp_roll(k=1.4142) annotation(Placement(transformation(origin={0,320},extent={{-15,-15},{15,15}})));
  SysplorerEmbeddedCoder.MathOperation.Sum roll_pd(inputs="++") annotation(Placement(transformation(origin={320,300},extent={{-15,-15},{15,15}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));

  SysplorerEmbeddedCoder.MathOperation.Gain kp_yaw(k=0.5) annotation(Placement(transformation(origin={0,-200},extent={{-15,-15},{15,15}})));

  SysplorerEmbeddedCoder.Discontinuities.Saturation pitch_cmd_limit(lowLimit=-6.5,upLimit=6.5) annotation(Placement(transformation(origin={400,400},extent={{-15,-15},{15,15}})));
  SysplorerEmbeddedCoder.Discontinuities.Saturation roll_cmd_limit(lowLimit=-6.5,upLimit=6.5) annotation(Placement(transformation(origin={400,300},extent={{-15,-15},{15,15}})));
  SysplorerEmbeddedCoder.Discontinuities.Saturation yaw_cmd_limit(lowLimit=-6.5,upLimit=6.5) annotation(Placement(transformation(origin={80,-200},extent={{-15,-15},{15,15}})));

  SysplorerEmbeddedCoder.MathOperation.Gain yaw_mix_gain(k=0.707) annotation(Placement(transformation(origin={480,400},extent={{-15,-15},{15,15}})));
  SysplorerEmbeddedCoder.MathOperation.Gain pitch_mix_gain(k=0.707) annotation(Placement(transformation(origin={480,300},extent={{-15,-15},{15,15}})));
  SysplorerEmbeddedCoder.MathOperation.Gain roll_mix_gain(k=0.707) annotation(Placement(transformation(origin={480,200},extent={{-15,-15},{15,15}})));

  SysplorerEmbeddedCoder.MathOperation.Sum u1_sum(inputs="+---") annotation(Placement(transformation(origin={600,300},extent={{-15,-15},{15,15}})),__MWORKS(BlockSystem(Instance(u(u1,u2,u3,u4)))));
  SysplorerEmbeddedCoder.MathOperation.Sum u2_sum_inner(inputs="+-+") annotation(Placement(transformation(origin={560,200},extent={{-15,-15},{15,15}})),__MWORKS(BlockSystem(Instance(u(u1,u2,u3)))));
  SysplorerEmbeddedCoder.MathOperation.Gain u2_neg(k=-1.0) annotation(Placement(transformation(origin={640,200},extent={{-15,-15},{15,15}})));
  SysplorerEmbeddedCoder.MathOperation.Sum u3_sum(inputs="+-+-") annotation(Placement(transformation(origin={600,100},extent={{-15,-15},{15,15}})),__MWORKS(BlockSystem(Instance(u(u1,u2,u3,u4)))));
  SysplorerEmbeddedCoder.MathOperation.Sum u4_sum_inner(inputs="+++") annotation(Placement(transformation(origin={560,0},extent={{-15,-15},{15,15}})),__MWORKS(BlockSystem(Instance(u(u1,u2,u3)))));
  SysplorerEmbeddedCoder.MathOperation.Gain u4_neg(k=-1.0) annotation(Placement(transformation(origin={640,0},extent={{-15,-15},{15,15}})));

  SysplorerEmbeddedCoder.Discontinuities.Saturation u1_limit(lowLimit=-20.0,upLimit=20.0) annotation(Placement(transformation(origin={720,300},extent={{-15,-15},{15,15}})));
  SysplorerEmbeddedCoder.Discontinuities.Saturation u2_limit(lowLimit=-20.0,upLimit=20.0) annotation(Placement(transformation(origin={720,200},extent={{-15,-15},{15,15}})));
  SysplorerEmbeddedCoder.Discontinuities.Saturation u3_limit(lowLimit=-20.0,upLimit=20.0) annotation(Placement(transformation(origin={720,100},extent={{-15,-15},{15,15}})));
  SysplorerEmbeddedCoder.Discontinuities.Saturation u4_limit(lowLimit=-20.0,upLimit=20.0) annotation(Placement(transformation(origin={720,0},extent={{-15,-15},{15,15}})));

  model ModelWorkspace
    annotation(__MWORKS(hide = true,BlockSystem(blockKind=BlockKind.modelWorkspace)));
  end ModelWorkspace;

equation
  connect(x_error, kp_x.u) annotation(Line(points={{-740,400},{-615,420}}));
  connect(x_error, x_prev.u1) annotation(Line(points={{-740,400},{-650,400},{-650,350},{-615,350}}));
  connect(x_error, x_delta.u1) annotation(Line(points={{-740,400},{-680,400},{-680,357},{-535,357}}));
  connect(x_prev.y, x_delta.u2) annotation(Line(points={{-585,350},{-560,350},{-560,343},{-535,343}}));
  connect(x_delta.y, x_d_rate.u) annotation(Line(points={{-505,350},{-455,350}}));
  connect(x_d_rate.y, kd_x.u) annotation(Line(points={{-425,350},{-375,350}}));
  connect(kp_x.y, x_pd.u1) annotation(Line(points={{-585,420},{-400,420},{-400,407},{-295,407}}));
  connect(kd_x.y, x_pd.u2) annotation(Line(points={{-345,350},{-320,350},{-320,393},{-295,393}}));

  connect(y_error, kp_y.u) annotation(Line(points={{-740,300},{-615,320}}));
  connect(y_error, y_prev.u1) annotation(Line(points={{-740,300},{-650,300},{-650,250},{-615,250}}));
  connect(y_error, y_delta.u1) annotation(Line(points={{-740,300},{-680,300},{-680,257},{-535,257}}));
  connect(y_prev.y, y_delta.u2) annotation(Line(points={{-585,250},{-560,250},{-560,243},{-535,243}}));
  connect(y_delta.y, y_d_rate.u) annotation(Line(points={{-505,250},{-455,250}}));
  connect(y_d_rate.y, kd_y.u) annotation(Line(points={{-425,250},{-375,250}}));
  connect(kp_y.y, y_pd.u1) annotation(Line(points={{-585,320},{-400,320},{-400,307},{-295,307}}));
  connect(kd_y.y, y_pd.u2) annotation(Line(points={{-345,250},{-320,250},{-320,293},{-295,293}}));

  connect(z_error, kp_z.u) annotation(Line(points={{-740,200},{-615,220}}));
  connect(z_error, z_prev.u1) annotation(Line(points={{-740,200},{-650,200},{-650,150},{-615,150}}));
  connect(z_error, z_delta.u1) annotation(Line(points={{-740,200},{-680,200},{-680,157},{-535,157}}));
  connect(z_prev.y, z_delta.u2) annotation(Line(points={{-585,150},{-560,150},{-560,143},{-535,143}}));
  connect(z_delta.y, z_d_rate.u) annotation(Line(points={{-505,150},{-455,150}}));
  connect(z_d_rate.y, kd_z.u) annotation(Line(points={{-425,150},{-375,150}}));
  connect(z_error, z_int.u1) annotation(Line(points={{-740,200},{-660,200},{-660,80},{-615,80}}));
  connect(z_int.y, ki_z.u) annotation(Line(points={{-585,80},{-535,80}}));
  connect(z_ref_rate, kff_z.u) annotation(Line(points={{-740,100},{-620,100},{-620,120},{-535,120}}));
  connect(kp_z.y, z_pid.u1) annotation(Line(points={{-585,220},{-340,220},{-340,194},{-295,194}}));
  connect(kd_z.y, z_pid.u2) annotation(Line(points={{-345,150},{-330,150},{-330,186},{-295,186}}));
  connect(ki_z.y, z_pid.u3) annotation(Line(points={{-505,80},{-320,80},{-320,174},{-295,174}}));
  connect(kff_z.y, z_pid.u4) annotation(Line(points={{-505,120},{-310,120},{-310,166},{-295,166}}));

  connect(x_pd.y, pitch_limit.u) annotation(Line(points={{-265,400},{-195,400}}));
  connect(y_pd.y, roll_limit.u) annotation(Line(points={{-265,300},{-195,300}}));
  connect(z_pid.y, thrust_limit.u) annotation(Line(points={{-265,180},{-195,180}}));

  connect(pitch_limit.y, pitch_err.u1) annotation(Line(points={{-165,400},{-120,400},{-120,407},{-95,407}}));
  connect(pitch_mea, pitch_err.u2) annotation(Line(points={{-740,-100},{-120,-100},{-120,393},{-95,393}}));
  connect(roll_limit.y, roll_err.u1) annotation(Line(points={{-165,300},{-120,300},{-120,307},{-95,307}}));
  connect(roll_mea, roll_err.u2) annotation(Line(points={{-740,0},{-120,0},{-120,293},{-95,293}}));
  connect(yaw_ref, yaw_err.u1) annotation(Line(points={{-740,-300},{-120,-300},{-120,-193},{-95,-193}}));
  connect(yaw_mea, yaw_err.u2) annotation(Line(points={{-740,-200},{-400,-200},{-400,-207},{-95,-207}}));

  connect(pitch_err.y, pitch_prev.u1) annotation(Line(points={{-65,400},{-40,400},{-40,350},{-15,350}}));
  connect(pitch_err.y, pitch_delta.u1) annotation(Line(points={{-65,400},{-40,400},{-40,357},{65,357}}));
  connect(pitch_prev.y, pitch_delta.u2) annotation(Line(points={{15,350},{40,350},{40,343},{65,343}}));
  connect(pitch_delta.y, pitch_d_rate.u) annotation(Line(points={{95,350},{145,350}}));
  connect(pitch_d_rate.y, kd_pitch.u) annotation(Line(points={{175,350},{225,350}}));
  connect(pitch_err.y, kp_pitch.u) annotation(Line(points={{-65,400},{-40,400},{-40,420},{-15,420}}));
  connect(kp_pitch.y, pitch_pd.u1) annotation(Line(points={{15,420},{280,420},{280,407},{305,407}}));
  connect(kd_pitch.y, pitch_pd.u2) annotation(Line(points={{255,350},{280,350},{280,393},{305,393}}));

  connect(roll_err.y, roll_prev.u1) annotation(Line(points={{-65,300},{-40,300},{-40,250},{-15,250}}));
  connect(roll_err.y, roll_delta.u1) annotation(Line(points={{-65,300},{-40,300},{-40,257},{65,257}}));
  connect(roll_prev.y, roll_delta.u2) annotation(Line(points={{15,250},{40,250},{40,243},{65,243}}));
  connect(roll_delta.y, roll_d_rate.u) annotation(Line(points={{95,250},{145,250}}));
  connect(roll_d_rate.y, kd_roll.u) annotation(Line(points={{175,250},{225,250}}));
  connect(roll_err.y, kp_roll.u) annotation(Line(points={{-65,300},{-40,300},{-40,320},{-15,320}}));
  connect(kp_roll.y, roll_pd.u1) annotation(Line(points={{15,320},{280,320},{280,307},{305,307}}));
  connect(kd_roll.y, roll_pd.u2) annotation(Line(points={{255,250},{280,250},{280,293},{305,293}}));

  connect(yaw_err.y, kp_yaw.u) annotation(Line(points={{-65,-200},{-15,-200}}));

  connect(pitch_pd.y, pitch_cmd_limit.u) annotation(Line(points={{335,400},{385,400}}));
  connect(roll_pd.y, roll_cmd_limit.u) annotation(Line(points={{335,300},{385,300}}));
  connect(kp_yaw.y, yaw_cmd_limit.u) annotation(Line(points={{15,-200},{65,-200}}));

  connect(yaw_cmd_limit.y, yaw_mix_gain.u) annotation(Line(points={{95,-200},{440,-200},{440,400},{465,400}}));
  connect(pitch_cmd_limit.y, pitch_mix_gain.u) annotation(Line(points={{415,400},{440,400},{440,300},{465,300}}));
  connect(roll_cmd_limit.y, roll_mix_gain.u) annotation(Line(points={{415,300},{440,300},{440,200},{465,200}}));

  connect(thrust_limit.y, u1_sum.u1) annotation(Line(points={{-165,180},{540,180},{540,320},{585,320}}));
  connect(yaw_mix_gain.y, u1_sum.u2) annotation(Line(points={{495,400},{540,400},{540,313},{585,313}}));
  connect(pitch_mix_gain.y, u1_sum.u3) annotation(Line(points={{495,300},{540,300},{540,294},{585,294}}));
  connect(roll_mix_gain.y, u1_sum.u4) annotation(Line(points={{495,200},{540,200},{540,287},{585,287}}));

  connect(yaw_mix_gain.y, u2_sum_inner.u1) annotation(Line(points={{495,400},{520,400},{520,211},{545,211}}));
  connect(pitch_mix_gain.y, u2_sum_inner.u2) annotation(Line(points={{495,300},{520,300},{520,200},{545,200}}));
  connect(roll_mix_gain.y, u2_sum_inner.u3) annotation(Line(points={{495,200},{520,200},{520,189},{545,189}}));
  connect(thrust_limit.y, u2_neg.u) annotation(Line(points={{-165,180},{600,180},{600,200},{625,200}}));
  connect(u2_sum_inner.y, u2_neg.u) annotation(Line(points={{600,200}}));

  connect(thrust_limit.y, u3_sum.u1) annotation(Line(points={{-165,180},{540,180},{540,120},{585,120}}));
  connect(yaw_mix_gain.y, u3_sum.u2) annotation(Line(points={{495,400},{560,400},{560,113},{585,113}}));
  connect(pitch_mix_gain.y, u3_sum.u3) annotation(Line(points={{495,300},{560,300},{560,94},{585,94}}));
  connect(roll_mix_gain.y, u3_sum.u4) annotation(Line(points={{495,200},{560,200},{560,87},{585,87}}));

  connect(yaw_mix_gain.y, u4_sum_inner.u1) annotation(Line(points={{495,400},{520,400},{520,11},{545,11}}));
  connect(pitch_mix_gain.y, u4_sum_inner.u2) annotation(Line(points={{495,300},{520,300},{520,0},{545,0}}));
  connect(roll_mix_gain.y, u4_sum_inner.u3) annotation(Line(points={{495,200},{520,200},{520,-11},{545,-11}}));
  connect(thrust_limit.y, u4_neg.u) annotation(Line(points={{-165,180},{600,180},{600,0},{625,0}}));
  connect(u4_sum_inner.y, u4_neg.u) annotation(Line(points={{600,0}}));

  connect(u1_sum.y, u1_limit.u) annotation(Line(points={{615,300},{705,300}}));
  connect(u2_neg.y, u2_limit.u) annotation(Line(points={{655,200},{705,200}}));
  connect(u3_sum.y, u3_limit.u) annotation(Line(points={{615,100},{705,100}}));
  connect(u4_neg.y, u4_limit.u) annotation(Line(points={{655,0},{705,0}}));

  connect(u1_limit.y, y) annotation(Line(points={{735,300},{1030,300}}));
  connect(u2_limit.y, y1) annotation(Line(points={{735,200},{1030,200}}));
  connect(u3_limit.y, y2) annotation(Line(points={{735,100},{1030,100}}));
  connect(u4_limit.y, y3) annotation(Line(points={{735,0},{1030,0}}));
end PidAwffLinearEsoGraphicalController;