within MoSimQuadrotorModel.Control.PidFamily;
model AwffPidFullGraphicalController "MWORKS.Sysblock composed AWFF PID controller"
  extends ModelWorkspace;
  import SysplorerEmbeddedCoder.Types.*;
  import BaseWorkspace.*;
  annotation(__MWORKS(version="26.3.0",modelType=Control,PortArrangement(Left(x_error,y_error,z_error,z_ref_rate,roll_mea,pitch_mea,yaw_mea,yaw_ref), Right(y,y1,y2,y3)),BlockSystem(blockKind=BlockKind.userModel,SampleTime(auto=true,group="")=0.01,OutputInterval=0.01),SysblockVersion="1.0",CodeGeneration(Config = {"code_placement":{"mode":"Compact"},"code_replacement":{"standard_c_library":"C99"},"custom_code":{"code":{"function_declare":{"head":"","item_head":"","item_tail":"","tail":""},"function_define":{"head":"","item_head":"","item_tail":"","tail":""},"global_variable_declare":{"head":"","item_head":"","item_tail":"","tail":""},"global_variable_define":{"head":"","item_head":"","item_tail":"","tail":""},"include":{"head":"","item_head":"","item_tail":"","tail":""},"macro":{"head":"","item_head":"","item_tail":"","tail":""},"type":{"head":"","item_head":"","item_tail":"","tail":""}},"code_protection":{"integer_division_by_zero":false,"overflow":false}},"data_type":{"real_as_float":true},"experiment":{"task_and_sample":{"muti_task_mode":false,"whether_to_use_prefix":false}},"hardware_platform":{"largest_atomic_size":{"floating_point":"32","integer":"32"}},"identifier":{"max_length":32,"style":{"function":"camelCase","local_variable":"camelCase","macro":"camelCase","mem_var":"camelCase","type":"camelCase"}},"interface":{"function_name":{"initialize":"Init","step":"Step"}},"is_expand":{"is_expand":false},"optimization":{"array_loop_threshold":5,"logical_operator":"logical"}}, Sim_seting = {"sim_seting":{"output":"C:\\Users\\HP\\Desktop\\MoSim\\Results\\generated_mworks\\AWFF_FullController_Sysblock_20260620_032747"}})),
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

  AwffPidPositionOuterLoopGraphical position_loop annotation(Placement(transformation(origin={-145,85},extent={{-45,-45},{45,45}})));
  AwffPidAttitudeInnerLoopGraphical attitude_loop annotation(Placement(transformation(origin={5,-35},extent={{-45,-45},{45,45}})));
  AwffPidMotorMixerGraphical motor_mixer annotation(Placement(transformation(origin={155,-35},extent={{-45,-45},{45,45}})));

  model ModelWorkspace
    annotation(__MWORKS(hide = true,BlockSystem(blockKind=BlockKind.modelWorkspace)));
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
    annotation(Line(points={{202,-1},{225,-1},{225,150},{240,150}},color={0,0,0}));
  connect(motor_mixer.y1, y1) 
    annotation(Line(points={{202,-24},{220,-24},{220,50},{240,50}},color={0,0,0}));
  connect(motor_mixer.y2, y2) 
    annotation(Line(points={{202,-46},{220,-46},{220,-50},{240,-50}},color={0,0,0}));
  connect(motor_mixer.y3, y3) 
    annotation(Line(points={{202,-69},{225,-69},{225,-150},{240,-150}},color={0,0,0}));
end AwffPidFullGraphicalController;