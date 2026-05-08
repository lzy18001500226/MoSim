model Subsys_1 "子系统示例1"
  extends ModelWorkspace;
  import SysplorerEmbeddedCoder.Types.*;
  import BaseWorkspace.*;
  annotation(__MWORKS(version="2025a",modelType=Control,PortArrangement(Right(outport)),BlockSystem(blockKind=BlockKind.userModel,SampleTime(auto=true,group="")=0.1),SysblockVersion="1.0"),Icon(coordinateSystem(preserveAspectRatio=false)),experiment(Algorithm=Euler,Interval=-1));
  block SubSystem "选择子系统模块的设置。 要启用涉及代码生成的相关参数, 请选择 '视为原子单元' 。"

    SysplorerEmbeddedCoder.Port.Inport u 
      annotation (Placement(transformation(origin={-310, 0}, extent={{-10, -10}, {10, 10}}), iconTransformation(extent={{-1.8, -1.8}, {1.8, 1.8}})),__MWORKS(BlockSystem(Type(ref="double"),Dimension=1,SampleTime(group="D1")=0.1)));
    SysplorerEmbeddedCoder.Port.Outport y 
      annotation (Placement(transformation(origin={-148,-5}, 
extent={{-10,-10},{10,10}}), 
iconTransformation(origin={301.8,0}, 
extent={{-1.8,-1.8},{1.8,1.8}})),__MWORKS(BlockSystem(Type(ref="double"),Dimension=1,SampleTime(group="D1")=0.1)));
    Trigger trigger 
      annotation (Placement(transformation(origin = {-190, 40}, extent = {{-6, -6}, {6, 6}})),__MWORKS(BlockSystem(Type(ref="double"),Dimension=1,SampleTime(group="D1")=0.1)));
    SysplorerEmbeddedCoder.Sources.Constant constant1 
      annotation (Placement(transformation(origin = {-270, -30}, extent = {{-10, -10}, {10, 10}})),__MWORKS(BlockSystem(Instance(y(Type(ref="double") ,Dimension=1) ,k(Type(ref="double") ,Dimension=1)),SampleTime(group="D1")=0.1)));
    SysplorerEmbeddedCoder.MathOperation.Sum sum1 
      annotation (Placement(transformation(origin={-201,-5}, 
extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(u1(Type(ref="double") ,Dimension=1) ,u2(Type(ref="double") ,Dimension=1)) ,y(Type(ref="double") ,Dimension=1)),SampleTime(group="D1")=0.1)));

    annotation (__MWORKS(PortArrangement(Left(u), Top(trigger), Right(y)),BlockSystem(blockKind=BlockKind.subSystem, SampleTime(auto=true), SubSystem(virtual=true, functionPack=FunctionPack.auto, functionName="", sourceFile="")),sourceModel=SysplorerEmbeddedCoder.SubSystems.SubSystem,independentInstance=true,hide=true), Icon(coordinateSystem(extent={{-300, -120}, {300, 120}}, grid={2, 2}), graphics={Rectangle(origin = {0, 0}, fillColor = {255, 255, 255}, fillPattern = FillPattern.Solid, lineThickness = 1, extent = {{-300, 120}, {300, -120}}), Text(origin = {6.217248937900877e-15, -142}, lineColor = {0, 0, 0}, extent = {{0, 20}, {0, -20}}, textString = "%name", fontSize = 14, textStyle = {TextStyle.None}, textColor = {0, 0, 0}, verticalAlignment = TextAlignment.Top)}),Protection(access=Access.packageDuplicate));
    connector Trigger = input Auto "将此模块放在子系统中或模型的根级，以创建一个触发或函数调用系统" 
      annotation(Placement(transformation(origin = {-70, 2.220446049250313e-16}, extent = {{-10, -10}, {10, 10}}), iconTransformation(origin = {-61.8, 0}, extent = {{-1.8, -1.8}, {1.8, 1.8}})), 
      __MWORKS(BlockSystem(blockKind = BlockKind.atomic,bltBlockKind = BltBlockKind.trigger,triggerType=TriggerType.functionCall,zeroCross=true,AllowType(choices(choice="double", choice="float", choice="int8", choice="uint8", choice="int16", choice="uint16", choice="int32", 
choice="uint32", choice="int64", choice="uint64", choice="boolean", choice="fixdt(1,16,0)", choice="fixdt(1,16,2^0,0)", choice="fixdt(1,16,1.0,0,0.0)")),InheritType(choices(choice = InheritType.auto)),Type(inherit = InheritType.auto, ref = "double")),sourceModel=SysplorerEmbeddedCoder.SubSystems.Trigger,independentInstance=true,hide=true,portFlag="%trigger_functionCall"), 
      Icon(coordinateSystem(extent = {{-60, -60}, {60, 60}}, 
      grid = {2, 2}), graphics = {Polygon(origin = {0, 0}, 
      fillColor = {255, 255, 255}, 
      fillPattern = FillPattern.Solid, 
      points = {{-60, 60}, {-60, -60}, {60, 0}})}), Diagram(coordinateSystem(extent={{-60,-60},{60,60}}, 
grid={2,2}),graphics = {Rectangle(origin={0,0}, 
fillColor={255,255,255}, 
fillPattern=FillPattern.Solid, 
extent={{-60,-60},{60,60}}), Text(origin={0,-120}, 
extent={{-150,20},{150,-20}}, 
textString="%name", 
fontSize=14, 
verticalAlignment=TextAlignment.Top), Text(origin={0,0}, 
extent={{-60,-60},{60,60}}, 
textString="f()", 
fontSize=14)}),Protection(access=Access.packageDuplicate));
  equation
    connect(u, sum1.u1) 
    annotation(Line(origin={-255,0}, 
    points={{-43,0},{42.2,2.22045e-16}}, 
    color={0,0,0}));
    connect(constant1.y, sum1.u2) 
    annotation(Line(origin={-235,-20}, 
    points={{-23.2,-10},{-3,-10},{-3,10},{22.2,10}}, 
    color={0,0,0}));
    connect(sum1.y, y) 
    annotation(Line(origin={-146,-2}, 
points={{-43.2,-3},{-14,-3}}, 
color={0,0,0}));
    end SubSystem;
  model ModelWorkspace
    annotation(__MWORKS(hide = true,BlockSystem(blockKind=BlockKind.modelWorkspace)));
  end ModelWorkspace;
  SubSystem subSystem 
    annotation (Placement(transformation(origin = {-90, 0}, extent = {{-30, -12}, {30, 12}})),__MWORKS(PortLabels(labelType="PortName"),BlockSystem(SampleTime(group="D1")=0.1)));
  SysplorerEmbeddedCoder.Sources.Clock clock 
    annotation (Placement(transformation(origin={-170,-2}, 
extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(SampleTime(group="D0")=0)));
  SysplorerEmbeddedCoder.Port.Outport outport 
    annotation (Placement(transformation(origin={-28,0}, 
extent={{-10,-10},{10,10}}), 
iconTransformation(origin={101.8,0}, 
extent={{-1.8,-1.8},{1.8,1.8}})),__MWORKS(BlockSystem(Type(ref="double"),Dimension=1,SampleTime(group="D1")=0.1)));
  SysplorerEmbeddedCoder.SubSystems.FunctionCallGenerator functionCallGenerator(iter_num=2,isShowEnable=false) 
    annotation (Placement(transformation(origin = {-140, 40}, extent = {{-10, -10}, {10, 10}})),__MWORKS(BlockSystem(SampleTime(auto=false)=0.1,Instance(y(Dimension=1)))));
equation
  connect(clock.y, subSystem.u) 
  annotation(Line(origin={-140,-1}, 
  points={{-18.2,-1},{14.4,-1},{14.4,1},{18.2,1}}, 
  color={0,0,0}));
  connect(subSystem.y, outport) 
  annotation(Line(origin={-49,0}, 
  points={{-9.2,2.22045e-16},{9,0}}, 
  color={0,0,0}));
  connect(functionCallGenerator.y, subSystem.trigger) 
  annotation(Line(origin={-109,27}, 
  points={{-19.2,13},{19,13},{19,-13.2}}, 
  color={0,0,0}));

end Subsys_1;