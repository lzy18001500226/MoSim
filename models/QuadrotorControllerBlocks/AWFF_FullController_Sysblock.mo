model AWFF_FullController_Sysblock "MWORKS.Sysblock composed AWFF PID controller"
  extends ModelWorkspace;
  import SysplorerEmbeddedCoder.Types.*;
  import BaseWorkspace.*;
  annotation(__MWORKS(version="26.3.0",modelType=Control,PortArrangement(Left(x_error,y_error,z_error,z_ref_rate,roll_mea,pitch_mea,yaw_mea,yaw_ref), Right(y,y1,y2,y3)),BlockSystem(blockKind=BlockKind.userModel,SampleTime(auto=true,group="")=0.01,OutputInterval=0.01),SysblockVersion="1.0"),
    Icon(coordinateSystem(preserveAspectRatio=false)),
    experiment(DoublePrecision=false,Algorithm=Euler,IntegratorStep=0.01,Interval=0.01,StartTime=0,StopTime=1,StoreEventValue=0),
    Diagram(coordinateSystem(extent={{-320,-220},{280,220}},grid={2,2})));

  SysplorerEmbeddedCoder.Port.Inport x_error annotation(Placement(transformation(origin={-300,180},extent={{-10,-10},{10,10}}),iconTransformation(origin={-101.8,87.5},extent={{-1.8,-1.8},{1.8,1.8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport y_error annotation(Placement(transformation(origin={-300,130},extent={{-10,-10},{10,10}}),iconTransformation(origin={-101.8,62.5},extent={{-1.8,-1.8},{1.8,1.8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport z_error annotation(Placement(transformation(origin={-300,80},extent={{-10,-10},{10,10}}),iconTransformation(origin={-101.8,37.5},extent={{-1.8,-1.8},{1.8,1.8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport z_ref_rate annotation(Placement(transformation(origin={-300,30},extent={{-10,-10},{10,10}}),iconTransformation(origin={-101.8,12.5},extent={{-1.8,-1.8},{1.8,1.8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport roll_mea annotation(Placement(transformation(origin={-300,-30},extent={{-10,-10},{10,10}}),iconTransformation(origin={-101.8,-12.5},extent={{-1.8,-1.8},{1.8,1.8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport pitch_mea annotation(Placement(transformation(origin={-300,-80},extent={{-10,-10},{10,10}}),iconTransformation(origin={-101.8,-37.5},extent={{-1.8,-1.8},{1.8,1.8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport yaw_mea annotation(Placement(transformation(origin={-300,-130},extent={{-10,-10},{10,10}}),iconTransformation(origin={-101.8,-62.5},extent={{-1.8,-1.8},{1.8,1.8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport yaw_ref annotation(Placement(transformation(origin={-300,-180},extent={{-10,-10},{10,10}}),iconTransformation(origin={-101.8,-87.5},extent={{-1.8,-1.8},{1.8,1.8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));

  SysplorerEmbeddedCoder.Port.Outport y annotation(Placement(transformation(origin={250,150},extent={{-10,-10},{10,10}}),iconTransformation(origin={101.8,75},extent={{-1.8,-1.8},{1.8,1.8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport y1 annotation(Placement(transformation(origin={250,50},extent={{-10,-10},{10,10}}),iconTransformation(origin={101.8,25},extent={{-1.8,-1.8},{1.8,1.8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport y2 annotation(Placement(transformation(origin={250,-50},extent={{-10,-10},{10,10}}),iconTransformation(origin={101.8,-25},extent={{-1.8,-1.8},{1.8,1.8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport y3 annotation(Placement(transformation(origin={250,-150},extent={{-10,-10},{10,10}}),iconTransformation(origin={101.8,-75},extent={{-1.8,-1.8},{1.8,1.8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));

  AWFF_PositionOuterLoop_Sysblock position_loop annotation(Placement(transformation(origin={-140,90},extent={{-40,-40},{40,40}})));
  AWFF_AttitudeInnerLoop_Sysblock attitude_loop annotation(Placement(transformation(origin={10,10},extent={{-40,-40},{40,40}})));
  AWFF_MotorMixer_Sysblock motor_mixer annotation(Placement(transformation(origin={150,0},extent={{-40,-40},{40,40}})));

  model ModelWorkspace
    annotation(__MWORKS(hide = true,BlockSystem(blockKind=BlockKind.modelWorkspace)));
  end ModelWorkspace;

equation
  connect(x_error, position_loop.x_error)
    annotation(Line(origin={-220,155},points={{-70,25},{38,25},{38,-20}},color={0,0,0}));
  connect(y_error, position_loop.y_error)
    annotation(Line(origin={-220,120},points={{-70,10},{38,10},{38,-20}},color={0,0,0}));
  connect(z_error, position_loop.z_error)
    annotation(Line(origin={-220,85},points={{-70,-5},{38,-5},{38,-15}},color={0,0,0}));
  connect(z_ref_rate, position_loop.z_ref_rate)
    annotation(Line(origin={-220,50},points={{-70,-20},{38,-20},{38,0}},color={0,0,0}));

  connect(position_loop.roll_ref, attitude_loop.roll_ref)
    annotation(Line(origin={-65,80},points={{-33,10},{33,10},{33,-30}},color={0,0,0}));
  connect(position_loop.pitch_ref, attitude_loop.pitch_ref)
    annotation(Line(origin={-65,105},points={{-33,25},{45,25},{45,-55},{33,-55}},color={0,0,0}));
  connect(yaw_ref, attitude_loop.yaw_ref)
    annotation(Line(origin={-145,-90},points={{-145,-90},{105,-90},{105,60}},color={0,0,0}));
  connect(roll_mea, attitude_loop.roll_mea)
    annotation(Line(origin={-145,-30},points={{-145,0},{105,0},{105,0}},color={0,0,0}));
  connect(pitch_mea, attitude_loop.pitch_mea)
    annotation(Line(origin={-145,-60},points={{-145,-20},{105,-20},{105,20}},color={0,0,0}));
  connect(yaw_mea, attitude_loop.yaw_mea)
    annotation(Line(origin={-145,-85},points={{-145,-45},{105,-45},{105,35}},color={0,0,0}));

  connect(position_loop.thrust_ref, motor_mixer.thrust_ref)
    annotation(Line(origin={5,80},points={{-63,-30},{105,-30},{105,40}},color={0,0,0}));
  connect(attitude_loop.roll_cmd, motor_mixer.roll_cmd)
    annotation(Line(origin={80,35},points={{-28,15},{28,15},{28,5}},color={0,0,0}));
  connect(attitude_loop.pitch_cmd, motor_mixer.pitch_cmd)
    annotation(Line(origin={80,5},points={{-28,5},{28,5},{28,-25}},color={0,0,0}));
  connect(attitude_loop.yaw_cmd, motor_mixer.yaw_cmd)
    annotation(Line(origin={80,-25},points={{-28,-25},{28,-25},{28,-25}},color={0,0,0}));

  connect(motor_mixer.y, y)
    annotation(Line(origin={210,125},points={{-18,25},{30,25}},color={0,0,0}));
  connect(motor_mixer.y1, y1)
    annotation(Line(origin={210,45},points={{-18,-5},{30,5}},color={0,0,0}));
  connect(motor_mixer.y2, y2)
    annotation(Line(origin={210,-45},points={{-18,5},{30,-5}},color={0,0,0}));
  connect(motor_mixer.y3, y3)
    annotation(Line(origin={210,-125},points={{-18,-25},{30,-25}},color={0,0,0}));
end AWFF_FullController_Sysblock;