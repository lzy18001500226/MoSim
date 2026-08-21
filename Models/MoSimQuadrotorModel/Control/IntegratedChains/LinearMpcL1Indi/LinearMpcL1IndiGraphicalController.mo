within MoSimQuadrotorModel.Control.IntegratedChains.LinearMpcL1Indi;
model LinearMpcL1IndiGraphicalController "AWFF Linear MPC INDI controller - standalone graphical Sysblock"
  extends ModelWorkspace;
  import SysplorerEmbeddedCoder.Types.*;
  import BaseWorkspace.*;
  annotation(__MWORKS(version="26.3.0",modelType=Control,PortArrangement(Left(x_error,y_error,z_error,z_ref_rate,roll_mea,pitch_mea,yaw_mea,yaw_ref), Right(y,y1,y2,y3)),BlockSystem(blockKind=BlockKind.userModel,SampleTime(auto=true,group="")=0.01,OutputInterval=0.01),SysblockVersion="1.0",CodeGeneration(Config = {"code_placement":{"mode":"Compact"}})),
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

  LinearMpcL1IndiOuterLoopGraphical position_loop annotation(Placement(transformation(origin={-145,85},extent={{-45,-45},{45,45}})));
  LinearMpcL1IndiAttitudeGraphical attitude_loop annotation(Placement(transformation(origin={5,-35},extent={{-45,-45},{45,45}})));
  LinearMpcL1IndiMotorMixerGraphical motor_mixer annotation(Placement(transformation(origin={155,-35},extent={{-45,-45},{45,45}})));

  model ModelWorkspace
    annotation(__MWORKS(hide=true,BlockSystem(blockKind=BlockKind.modelWorkspace),version="26.3.0"));
  end ModelWorkspace;

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
end LinearMpcL1IndiGraphicalController;