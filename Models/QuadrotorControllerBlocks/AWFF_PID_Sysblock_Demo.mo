model AWFF_PID_Sysblock_Demo "MWORKS.Sysblock AWFF PID altitude-loop demo"
  extends ModelWorkspace;
  import SysplorerEmbeddedCoder.Types.*;
  import BaseWorkspace.*;
  annotation(__MWORKS(version="26.3.0",modelType=Control,PortArrangement(Left(z_error), Right(thrust_cmd)),BlockSystem(blockKind=BlockKind.userModel,SampleTime(auto=true,group="")=0.01,OutputInterval=0.01),SysblockVersion="1.0",CodeGeneration(Config = {"code_placement":{"mode":"Compact"},"code_replacement":{"standard_c_library":"C99"},"custom_code":{"code":{"function_declare":{"head":"","item_head":"","item_tail":"","tail":""},"function_define":{"head":"","item_head":"","item_tail":"","tail":""},"global_variable_declare":{"head":"","item_head":"","item_tail":"","tail":""},"global_variable_define":{"head":"","item_head":"","item_tail":"","tail":""},"include":{"head":"","item_head":"","item_tail":"","tail":""},"macro":{"head":"","item_head":"","item_tail":"","tail":""},"type":{"head":"","item_head":"","item_tail":"","tail":""}},"code_protection":{"integer_division_by_zero":false,"overflow":false}},"data_type":{"real_as_float":true},"experiment":{"task_and_sample":{"muti_task_mode":false,"whether_to_use_prefix":false}},"hardware_platform":{"largest_atomic_size":{"floating_point":"32","integer":"32"}},"identifier":{"max_length":32,"style":{"function":"camelCase","local_variable":"camelCase","macro":"camelCase","mem_var":"camelCase","type":"camelCase"}},"interface":{"function_name":{"initialize":"Init","step":"Step"}},"is_expand":{"is_expand":false},"optimization":{"array_loop_threshold":5,"logical_operator":"logical"}}, Sim_seting = {"sim_seting":{"output":"C:\\Users\\HP\\Desktop\\MoSim\\Results\\sunray_ros1\\px4ctrl_g6_codegen_20260622_001\\control_codegen_sanity_awff_pid"}})),Icon(coordinateSystem(preserveAspectRatio=false)),experiment(DoublePrecision=false,Algorithm=Euler,IntegratorStep=0.01,Interval=0.01,StartTime=0,StopTime=0.03,StoreEventValue=0),Diagram(coordinateSystem(extent={{-240,-100},{120,100}},grid={2,2})));

  SysplorerEmbeddedCoder.Discrete.DiscreteTimeIntegrator ki_integrator(externalResetType=SysplorerEmbeddedCoder.Discrete.DiscreteTimeIntegrator.ExternalResetType.None,gain=6.0,initCond=0) 
    annotation (Placement(transformation(origin={-72,34},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(SampleTime(auto=true,group="D1")=0.01,Instance(u1(Type(ref="double") ,Dimension=1) ,y(Type(ref="double") ,Dimension=1) ,gain(Type(ref="double") ,Dimension=1) ,initCond(Type(ref="double") ,Dimension=1))),PortLabels(labelType="CustomType",labels(label(text="",instance="u1"),label(text="",instance="u2"),label(text="x0",instance="u3")))));
  SysplorerEmbeddedCoder.MathOperation.Gain kp_gain(k=8.0) 
    annotation (Placement(transformation(origin={-72,70},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double") ,Dimension=1) ,y(Type(ref="double") ,Dimension=1) ,k(Type(ref="double") ,Dimension=1)),SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Discrete.Difference diff_error 
    annotation (Placement(transformation(origin={-72,-2},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double") ,Dimension=1) ,add(u(u1(Type(ref="double") ,Dimension=1) ,u2(Type(ref="double") ,Dimension=1)) ,y(Type(ref="double") ,Dimension=1)) ,unitDelay(u1(Type(ref="double") ,Dimension=1) ,y(Type(ref="double") ,Dimension=1) ,initCond(Type(ref="") ,Dimension=1)) ,y(Type(ref="double") ,Dimension=1) ,iCPrevInput(Type(ref="") ,Dimension=1)),SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.MathOperation.Gain kd_gain(k=4.0) 
    annotation (Placement(transformation(origin={-154,12},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double") ,Dimension=1) ,y(Type(ref="double") ,Dimension=1) ,k(Type(ref="double") ,Dimension=1)),SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Sources.Constant ts_const(k=0.01) 
    annotation (Placement(transformation(origin={-154,-22},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(SampleTime(auto=true,group="D1")=0.01,Instance(y(Type(inherit=InheritType.constantValue ,ref="double") ,Dimension=1) ,k(Type(ref="double") ,Dimension=1)))));
  SysplorerEmbeddedCoder.MathOperation.Product derivative_over_ts(isSaturate=false,inputs="*/") 
    annotation (Placement(transformation(origin={-109,-2},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(u1(Type(ref="double") ,Dimension=1) ,u2(Type(ref="double") ,Dimension=1)) ,y(Type(ref="double") ,Dimension=1)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap) ,SampleTime(group="D1")=0.01),PortLabels(labelType="CustomType",labels(label(text="*",instance="u1"),label(text="/",instance="u2")))));
  SysplorerEmbeddedCoder.MathOperation.Gain ff_gain(k=0.35) 
    annotation (Placement(transformation(origin={-72,-50},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double") ,Dimension=1) ,y(Type(ref="double") ,Dimension=1) ,k(Type(ref="double") ,Dimension=1)),SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.MathOperation.Sum cmd_sum(isSaturate=false,inputs="++++") 
    annotation (Placement(transformation(origin={0,34},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(u1(Type(ref="double") ,Dimension=1) ,u2(Type(ref="double") ,Dimension=1) ,u3(Type(ref="double") ,Dimension=1) ,u4(Type(ref="double") ,Dimension=1)) ,y(Type(ref="double") ,Dimension=1)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap) ,SampleTime(group="D1")=0.01),PortLabels(labelType="CustomType",labels(label(text="+",instance="u1"),label(text="+",instance="u2"),label(text="+",instance="u3"),label(text="+",instance="u4")))));
  SysplorerEmbeddedCoder.Port.Inport z_error 
    annotation (Placement(transformation(origin={-222,34},extent={{-10,-10},{10,10}}),iconTransformation(origin={-101.8,0},extent={{-1.8,-1.8},{1.8,1.8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport thrust_cmd 
    annotation (Placement(transformation(origin={72,34},extent={{-10,-10},{10,10}}),iconTransformation(origin={101.8,0},extent={{-1.8,-1.8},{1.8,1.8}})),__MWORKS(BlockSystem(Type(ref="double"),Dimension=1,SampleTime(group="D1")=0.01)));

  model ModelWorkspace
    annotation(__MWORKS(hide = true,BlockSystem(blockKind=BlockKind.modelWorkspace)));
  end ModelWorkspace;

  equation
  connect(z_error, ki_integrator.u1) 
  annotation(Line(origin={-148,34},points={{-62,0},{64.2,0}},color={0,0,0}));
  connect(kp_gain.y, cmd_sum.u1) 
  annotation(Line(origin={-34,55},points={{-26.2,15},{22,15},{22,-14.3333},{22.2,-14.3333}},color={0,0,0}));
  connect(ki_integrator.y, cmd_sum.u2) 
  annotation(Line(origin={-34,34},points={{-26.2,0},{22.2,0}},color={0,0,0}));
  connect(diff_error.y, cmd_sum.u3) 
  annotation(Line(origin={-34,13},points={{-26.2,-15},{22,-15},{22,14.3333},{22.2,14.3333}},color={0,0,0}));
  connect(cmd_sum.y, thrust_cmd) 
  annotation(Line(origin={37,34},points={{-25.2,0},{23,0}},color={0,0,0}));
  connect(kp_gain.u, z_error) 
  annotation(Line(origin={-148,52},points={{64.2,18},{-32,18},{-32,-18},{-62,-18}},color={0,0,0}),__MWORKS(BlockSystem(NamedSignal)));
  connect(kd_gain.u, z_error) 
  annotation(Line(origin={-189,23},points={{23.2,-11},{9,-11},{9,11},{-21,11}},color={0,0,0}),__MWORKS(BlockSystem(NamedSignal)));
  connect(kd_gain.y, derivative_over_ts.u1) 
  annotation(Line(origin={-131,8},points={{-11.2,4},{6.4,4},{6.4,-5},{10.2,-5}},color={0,0,0}));
  connect(ts_const.y, derivative_over_ts.u2) 
  annotation(Line(origin={-131,-14},points={{-11.2,-8},{6.4,-8},{6.4,7},{10.2,7}},color={0,0,0}));
  connect(derivative_over_ts.y, diff_error.u) 
  annotation(Line(origin={-90,-2},points={{-7.2,0},{6.2,0}},color={0,0,0}));
  connect(ff_gain.u, z_error) 
  annotation(Line(origin={-148,-8},points={{64.2,-42},{-32,-42},{-32,42},{-62,42}},color={0,0,0}),__MWORKS(BlockSystem(NamedSignal)));
  connect(ff_gain.y, cmd_sum.u4) 
  annotation(Line(origin={-34,-8},points={{-26.2,-42},{22,-42},{22,35},{22.2,35}},color={0,0,0}));
end AWFF_PID_Sysblock_Demo;