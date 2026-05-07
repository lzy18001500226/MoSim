model SimplePID "简单PID控制器"
  extends ModelWorkspace;
  import SysplorerEmbeddedCoder.Types.*;
  import BaseWorkspace.*;
  import SysblockExample.SimplePID.DataDic.*;
  annotation(__MWORKS(version="2025a",modelType=Control,PortArrangement(Left(inport), Right(outport)),BlockSystem(blockKind=BlockKind.userModel,SampleTime(auto=true,group="")=0.001),SysblockVersion="1.0",BindDataXml(XML="modelica://SysblockExample/SimplePID.modd"),CodeGeneration(Config = {"code_comments":{"blocks":false,"descriptions":false,"eliminated_objects":false,"enable":false,"nested_objects":false},"code_placement":{"mode":"Compact"},"code_replacement":{"fixed_point_library":"Fixed-TY","standard_c_library":"C99"},"custom_code":{"code":{"function_declare":{"head":"","item_head":"","item_tail":"","tail":""},"function_define":{"head":"","item_head":"","item_tail":"","tail":""},"global_variable_declare":{"head":"","item_head":"","item_tail":"","tail":""},"global_variable_define":{"head":"","item_head":"","item_tail":"","tail":""},"include":{"head":"","item_head":"","item_tail":"","tail":""},"macro":{"head":"","item_head":"","item_tail":"","tail":""},"type":{"head":"","item_head":"","item_tail":"","tail":""}},"code_protection":{"integer_division_by_zero":true,"overflow":false}},"data_type":{"real_as_float":false},"experiment":{"task_and_sample":{"muti_task_mode":false}},"hardware_platform":{"byte_ordering":"大端序","largest_atomic_size":{"floating_point":"32","integer":"32"},"number_of_bits":{"char":8,"double":32,"float":32,"int":32,"long":32,"long_long":0,"pointer":32,"ptrdiff_t":32,"size_t":32},"support_dynamic_memory_allocation":false,"support_float_point":true,"target":"get","type_platform":"ARM Cortex-M0","vendor":"中颖科技"},"identifier":{"format":{"function":"{{model_name}}{{name}}","global_variable":"{{model_name}}{{data_type}}{{prefix}}{{name}}","local_variable":"{{data_type}}{{prefix}}{{name}}","macro":"{{model_name}}{{name}}","mem_var":"{{model_name}}{{name}}","type":"{{model_name}}{{name}}"},"format_string":{"boolean":"b","input":"in","integer":"i","output":"out","parameter":"p","real":"r"},"max_length":32,"style":{"function":"camelCase","global_variable":"camelCase"
,"local_variable":"camelCase","macro":"camelCase","mem_var":"camelCase","type":"camelCase"}},"interface":{"function_name":{"initialize":"Init","step":"Step","terminate":""},"have_terminate":false},"optimization":{"Code":"size","array_loop_threshold":5,"logical_operator":"logical"}}, Sim_seting = {"sim_seting":{"output":""}})),Icon(coordinateSystem(preserveAspectRatio=false)),experiment(DoublePrecision=false,Algorithm=Euler,InlineIntegrator=false,InlineStepSize=false,IntegratorStep=0.001,Interval=0.001,StartTime=0,StopTime=1,Tolerance=0.0001),Diagram(coordinateSystem(extent={{-100,-100},{100,100}}, 
grid={2,2})));
  SysplorerEmbeddedCoder.Discrete.DiscreteTimeIntegrator discreteTimeIntegrator(externalResetType=SysplorerEmbeddedCoder.Discrete.DiscreteTimeIntegrator.ExternalResetType.None,gain=Ki,initCond=0) 
    annotation (Placement(transformation(origin={-66,34}, 
extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(SampleTime(auto=true,group="D1")=0.001,Instance(u1(Type(ref="double") ,Dimension=1) ,y(Type(ref="double") ,Dimension=1) ,gain(Type(ref="double") ,Dimension=1) ,initCond(Type(ref="double") ,Dimension=1))),PortLabels(labelType="CustomType",labels(label(text="",instance="u1"),label(text="",instance="u2"),label(text="x0",instance="u3")))));
  SysplorerEmbeddedCoder.MathOperation.Gain gain(k=Kp) 
    annotation (Placement(transformation(origin={-66,70}, 
extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double") ,Dimension=1) ,y(Type(ref="double") ,Dimension=1) ,k(Type(ref="double") ,Dimension=1)),SampleTime(group="D1")=0.001)));
  SysplorerEmbeddedCoder.Discrete.Difference difference 
    annotation (Placement(transformation(origin={-66,-2}, 
extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double") ,Dimension=1) ,add(u(u1(Type(ref="double") ,Dimension=1) ,u2(Type(ref="double") ,Dimension=1)) ,y(Type(ref="double") ,Dimension=1)) ,unitDelay(u1(Type(ref="double") ,Dimension=1) ,y(Type(ref="double") ,Dimension=1) ,initCond(Type(ref="") ,Dimension=1)) ,y(Type(ref="double") ,Dimension=1) ,iCPrevInput(Type(ref="") ,Dimension=1)),SampleTime(group="D1")=0.001)));
  SysplorerEmbeddedCoder.MathOperation.Gain gain1(k=Kd) 
    annotation (Placement(transformation(origin={-148,12}, 
extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double") ,Dimension=1) ,y(Type(ref="double") ,Dimension=1) ,k(Type(ref="double") ,Dimension=1)),SampleTime(group="D1")=0.001)));
  SysplorerEmbeddedCoder.Sources.Constant constant1(k=Ts) 
    annotation (Placement(transformation(origin={-148,-22}, 
extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(SampleTime(auto=true,group="D1")=0.001,Instance(y(Type(inherit=InheritType.constantValue ,ref="double") ,Dimension=1) ,k(Type(ref="double") ,Dimension=1)))));
  SysplorerEmbeddedCoder.MathOperation.Product product1(isSaturate=false,inputs="*/") 
    annotation (Placement(transformation(origin={-103,-2}, 
extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(u1(Type(ref="double") ,Dimension=1) ,u2(Type(ref="double") ,Dimension=1)) ,y(Type(ref="double") ,Dimension=1)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap) ,SampleTime(group="D1")=0.001),PortLabels(labelType="CustomType",labels(label(text="*",instance="u1"),label(text="/",instance="u2")))));
  SysplorerEmbeddedCoder.MathOperation.Sum sum1(isSaturate=false,inputs="+++") 
    annotation (Placement(transformation(origin={-12,34}, 
extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(u1(Type(ref="double") ,Dimension=1) ,u2(Type(ref="double") ,Dimension=1) ,u3(Type(ref="double") ,Dimension=1)) ,y(Type(ref="double") ,Dimension=1)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap) ,SampleTime(group="D1")=0.001),PortLabels(labelType="CustomType",labels(label(text="+",instance="u1"),label(text="+",instance="u2"),label(text="+",instance="u3")))));
  SysplorerEmbeddedCoder.Port.Inport inport 
    annotation (Placement(transformation(origin={-222,34}, 
extent={{-10,-10},{10,10}}), 
iconTransformation(origin={-101.8,0}, 
extent={{-1.8,-1.8},{1.8,1.8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.001)));
  SysplorerEmbeddedCoder.Port.Outport outport 
    annotation (Placement(transformation(origin={58,34}, 
extent={{-10,-10},{10,10}}), 
iconTransformation(origin={101.8,0}, 
extent={{-1.8,-1.8},{1.8,1.8}})),__MWORKS(BlockSystem(Type(ref="double"),Dimension=1,SampleTime(group="D1")=0.001)));
  model ModelWorkspace
    annotation(__MWORKS(hide = true,BlockSystem(blockKind=BlockKind.modelWorkspace)));
  end ModelWorkspace;
  package DataDic
    annotation(__MWORKS(hide=true,BlockSystem(blockKind=BlockKind.dataDictionary)));
    constant Auto Kp=100 annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,DataDictionary(dataKind = DataDictKind.parm, dataType = "double", storageType = "Auto"))));
    constant Auto Ki=0.1 annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,DataDictionary(dataKind = DataDictKind.parm, dataType = "double", storageType = "Auto"))));
    constant Auto Kd=0.1 annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,DataDictionary(dataKind = DataDictKind.parm, dataType = "double", storageType = "Auto"))));
    constant Auto Ts=0.01 annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,DataDictionary(dataKind = DataDictKind.parm, dataType = "double", storageType = "Auto"))));
  end DataDic;
  equation
  connect(inport, discreteTimeIntegrator.u1) 
  annotation(Line(origin={-144,34}, 
  points={{-66,0},{66.2,0}}, 
  color={0,0,0}));
  connect(gain.y, sum1.u1) 
  annotation(Line(origin={-39,55}, 
  points={{-15.2,15},{1,15},{1,-14.3333},{15.2,-14.3333}}, 
  color={0,0,0}));
  connect(discreteTimeIntegrator.y, sum1.u2) 
  annotation(Line(origin={-39,34}, 
  points={{-15.2,0},{15.2,0}}, 
  color={0,0,0}));
  connect(difference.y, sum1.u3) 
  annotation(Line(origin={-39,13}, 
  points={{-15.2,-15},{3,-15},{3,14.3333},{15.2,14.3333}}, 
  color={0,0,0}));
  connect(sum1.y, outport) 
  annotation(Line(origin={23,34}, 
  points={{-23.2,0},{23,0}}, 
  color={0,0,0}));
  connect(gain.u, inport) 
  annotation(Line(origin={-144,52}, 
  points={{66.2,18},{-36,18},{-36,-18},{-66,-18}}, 
  color={0,0,0}),__MWORKS(BlockSystem(NamedSignal)));
  connect(gain1.u, inport) 
  annotation(Line(origin={-185,23}, 
  points={{25.2,-11},{5,-11},{5,11},{-25,11}}, 
  color={0,0,0}),__MWORKS(BlockSystem(NamedSignal)));
  connect(gain1.y, product1.u1) 
  annotation(Line(origin={-125,8}, 
  points={{-11.2,4},{6.4,4},{6.4,-5},{10.2,-5}}, 
  color={0,0,0}));
  connect(constant1.y, product1.u2) 
  annotation(Line(origin={-125,-14}, 
  points={{-11.2,-8},{6.4,-8},{6.4,7},{10.2,7}}, 
  color={0,0,0}));
  connect(product1.y, difference.u) 
  annotation(Line(origin={-84,-2}, 
  points={{-7.2,2.22045e-16},{6.2,2.22045e-16}}, 
  color={0,0,0}));
  end SimplePID;