within MoSimQuadrotorModel.Controllers.Sysblocks;
model AWFF_FullController_Sysblock "MWORKS.Sysblock composed AWFF PID controller"
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

  AWFF_PositionOuterLoop_Sysblock position_loop annotation(Placement(transformation(origin={-145,85},extent={{-45,-45},{45,45}})));
  AWFF_AttitudeInnerLoop_Sysblock attitude_loop annotation(Placement(transformation(origin={5,-35},extent={{-45,-45},{45,45}})));
  AWFF_MotorMixer_Sysblock motor_mixer annotation(Placement(transformation(origin={155,-35},extent={{-45,-45},{45,45}})));

  model AWFF_PositionOuterLoop_Sysblock "MWORKS.Sysblock AWFF PID position outer-loop structure"
    extends ModelWorkspace;
    import SysplorerEmbeddedCoder.Types.*;
    import BaseWorkspace.*;
    annotation(__MWORKS(version="26.3.0",modelType=Control,PortArrangement(Left(x_error,y_error,z_error,z_ref_rate), Right(pitch_ref,roll_ref,thrust_ref)),BlockSystem(blockKind=BlockKind.userModel,SampleTime(auto=true,group="")=0.01,OutputInterval=0.01),SysblockVersion="1.0"),
      Icon(coordinateSystem(preserveAspectRatio=false), graphics={
        Rectangle(extent={{-100,-100},{100,100}},lineColor={45,85,130},fillColor={238,246,255},fillPattern=FillPattern.Solid,radius=8),
        Text(extent={{-90,30},{90,-6}},textString="Position",lineColor={20,45,75}),
        Text(extent={{-90,-12},{90,-48}},textString="Outer Loop",lineColor={20,45,75}),
        Text(extent={{-90,-54},{90,-82}},textString="x/y/z -> attitude + thrust",lineColor={85,105,125})}),
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
  model AWFF_AttitudeInnerLoop_Sysblock "MWORKS.Sysblock AWFF PID attitude inner-loop structure"
    extends ModelWorkspace;
    import SysplorerEmbeddedCoder.Types.*;
    import BaseWorkspace.*;
    annotation(__MWORKS(version="26.3.0",modelType=Control,PortArrangement(Left(roll_ref,pitch_ref,yaw_ref,roll_mea,pitch_mea,yaw_mea), Right(roll_cmd,pitch_cmd,yaw_cmd)),BlockSystem(blockKind=BlockKind.userModel,SampleTime(auto=true,group="")=0.01,OutputInterval=0.01),SysblockVersion="1.0"),
      Icon(coordinateSystem(preserveAspectRatio=false), graphics={
        Rectangle(extent={{-100,-100},{100,100}},lineColor={120,70,35},fillColor={255,244,232},fillPattern=FillPattern.Solid,radius=8),
        Text(extent={{-90,30},{90,-6}},textString="Attitude",lineColor={80,45,20}),
        Text(extent={{-90,-12},{90,-48}},textString="Inner Loop",lineColor={80,45,20}),
        Text(extent={{-90,-54},{90,-82}},textString="roll/pitch/yaw PID",lineColor={120,85,55})}),
      experiment(DoublePrecision=false,Algorithm=Euler,IntegratorStep=0.01,Interval=0.01,StartTime=0,StopTime=1,StoreEventValue=0),
      Diagram(coordinateSystem(extent={{-260,-150},{180,150}},grid={2,2})));

    SysplorerEmbeddedCoder.Port.Inport roll_ref annotation(Placement(transformation(origin={-240,110},extent={{-10,-10},{10,10}}),iconTransformation(origin={-101.8,80},extent={{-1.8,-1.8},{1.8,1.8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Inport pitch_ref annotation(Placement(transformation(origin={-240,60},extent={{-10,-10},{10,10}}),iconTransformation(origin={-101.8,48},extent={{-1.8,-1.8},{1.8,1.8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Inport yaw_ref annotation(Placement(transformation(origin={-240,10},extent={{-10,-10},{10,10}}),iconTransformation(origin={-101.8,16},extent={{-1.8,-1.8},{1.8,1.8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Inport roll_mea annotation(Placement(transformation(origin={-240,-40},extent={{-10,-10},{10,10}}),iconTransformation(origin={-101.8,-16},extent={{-1.8,-1.8},{1.8,1.8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Inport pitch_mea annotation(Placement(transformation(origin={-240,-90},extent={{-10,-10},{10,10}}),iconTransformation(origin={-101.8,-48},extent={{-1.8,-1.8},{1.8,1.8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Inport yaw_mea annotation(Placement(transformation(origin={-240,-130},extent={{-10,-10},{10,10}}),iconTransformation(origin={-101.8,-80},extent={{-1.8,-1.8},{1.8,1.8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));

    SysplorerEmbeddedCoder.Port.Outport roll_cmd annotation(Placement(transformation(origin={150,90},extent={{-10,-10},{10,10}}),iconTransformation(origin={101.8,60},extent={{-1.8,-1.8},{1.8,1.8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Outport pitch_cmd annotation(Placement(transformation(origin={150,10},extent={{-10,-10},{10,10}}),iconTransformation(origin={101.8,0},extent={{-1.8,-1.8},{1.8,1.8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Outport yaw_cmd annotation(Placement(transformation(origin={150,-90},extent={{-10,-10},{10,10}}),iconTransformation(origin={101.8,-60},extent={{-1.8,-1.8},{1.8,1.8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));

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
    connect(roll_ref, roll_error.u1)
      annotation(Line(origin={-205,95},points={{-25,15},{23,-15}},color={0,0,0}));
    connect(roll_mea, roll_error.u2)
      annotation(Line(origin={-205,20},points={{-25,-60},{23,60}},color={0,0,0}));
    connect(roll_error.y, roll_kp.u)
      annotation(Line(origin={-130,90},points={{-28,-10},{28,10}},color={0,0,0}),__MWORKS(BlockSystem(NamedSignal)));
    connect(roll_error.y, roll_kd.u)
      annotation(Line(origin={-130,70},points={{-28,10},{28,-10}},color={0,0,0}),__MWORKS(BlockSystem(NamedSignal)));
    connect(roll_kp.y, roll_sum.u1)
      annotation(Line(origin={-45,95},points={{-33,5},{33,-15}},color={0,0,0}));
    connect(roll_kd.y, roll_sum.u2)
      annotation(Line(origin={-45,65},points={{-33,-5},{33,15}},color={0,0,0}));
    connect(roll_sum.y, roll_cmd)
      annotation(Line(origin={75,85},points={{-63,-5},{65,5}},color={0,0,0}));

    connect(pitch_ref, pitch_error.u1)
      annotation(Line(origin={-205,30},points={{-25,30},{23,-30}},color={0,0,0}));
    connect(pitch_mea, pitch_error.u2)
      annotation(Line(origin={-205,-45},points={{-25,-45},{23,45}},color={0,0,0}));
    connect(pitch_error.y, pitch_kp.u)
      annotation(Line(origin={-130,10},points={{-28,-10},{28,10}},color={0,0,0}),__MWORKS(BlockSystem(NamedSignal)));
    connect(pitch_error.y, pitch_kd.u)
      annotation(Line(origin={-130,-10},points={{-28,10},{28,-10}},color={0,0,0}),__MWORKS(BlockSystem(NamedSignal)));
    connect(pitch_kp.y, pitch_sum.u1)
      annotation(Line(origin={-45,15},points={{-33,5},{33,-15}},color={0,0,0}));
    connect(pitch_kd.y, pitch_sum.u2)
      annotation(Line(origin={-45,-15},points={{-33,-5},{33,15}},color={0,0,0}));
    connect(pitch_sum.y, pitch_cmd)
      annotation(Line(origin={75,5},points={{-63,-5},{65,5}},color={0,0,0}));

    connect(yaw_ref, yaw_error.u1)
      annotation(Line(origin={-205,-40},points={{-25,50},{23,-50}},color={0,0,0}));
    connect(yaw_mea, yaw_error.u2)
      annotation(Line(origin={-205,-110},points={{-25,-20},{23,20}},color={0,0,0}));
    connect(yaw_error.y, yaw_kp.u)
      annotation(Line(origin={-120,-90},points={{-38,0},{38,0}},color={0,0,0}));
    connect(yaw_kp.y, yaw_cmd)
      annotation(Line(origin={45,-90},points={{-103,0},{95,0}},color={0,0,0}));
  end AWFF_AttitudeInnerLoop_Sysblock;
  model AWFF_MotorMixer_Sysblock "MWORKS.Sysblock quadrotor motor mixer structure"
    extends ModelWorkspace;
    import SysplorerEmbeddedCoder.Types.*;
    import BaseWorkspace.*;
    annotation(__MWORKS(version="26.3.0",modelType=Control,PortArrangement(Left(thrust_ref,roll_cmd,pitch_cmd,yaw_cmd), Right(y,y1,y2,y3)),BlockSystem(blockKind=BlockKind.userModel,SampleTime(auto=true,group="")=0.01,OutputInterval=0.01),SysblockVersion="1.0"),
      Icon(coordinateSystem(preserveAspectRatio=false), graphics={
        Rectangle(extent={{-100,-100},{100,100}},lineColor={60,110,80},fillColor={238,250,242},fillPattern=FillPattern.Solid,radius=8),
        Text(extent={{-90,30},{90,-6}},textString="Motor",lineColor={30,75,50}),
        Text(extent={{-90,-12},{90,-48}},textString="Mixer",lineColor={30,75,50}),
        Text(extent={{-90,-54},{90,-82}},textString="T/r/p/y -> u1..u4",lineColor={75,115,90})}),
      experiment(DoublePrecision=false,Algorithm=Euler,IntegratorStep=0.01,Interval=0.01,StartTime=0,StopTime=1,StoreEventValue=0),
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
end AWFF_FullController_Sysblock;