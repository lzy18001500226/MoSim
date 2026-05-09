model Subsys2 "子系统示例2"
  extends ModelWorkspace;
  import SysplorerEmbeddedCoder.Types.*;
  import BaseWorkspace.*;
  annotation(__MWORKS(version="2025a",modelType=Control,PortArrangement,BlockSystem(blockKind=BlockKind.userModel,SampleTime(auto=true,group="")=0.1),SysblockVersion="1.0"),Icon(coordinateSystem(preserveAspectRatio=false)),experiment(Algorithm=Euler,Interval=-1));
  block SubSystem1 "选择子系统模块的设置。 要启用涉及代码生成的相关参数, 请选择 '视为原子单元' 。"

    annotation (__MWORKS(PortArrangement(Top(trigger)),BlockSystem(blockKind=BlockKind.subSystem, SampleTime(auto=true), SubSystem(virtual=true, functionPack=FunctionPack.auto, functionName="", sourceFile="")),independentInstance=true,hide=true,sourceModel=SysplorerEmbeddedCoder.SubSystems.SubSystem), Icon(coordinateSystem(extent={{-300, -120}, {300, 120}}, grid={2, 2}), graphics={Rectangle(origin = {0, 0}, fillColor = {255, 255, 255}, fillPattern = FillPattern.Solid, lineThickness = 1, extent = {{-300, 120}, {300, -120}}), Text(origin = {6.217248937900877e-15, -142}, lineColor = {0, 0, 0}, extent = {{0, 20}, {0, -20}}, textString = "%name", fontSize = 14, textStyle = {TextStyle.None}, textColor = {0, 0, 0}, verticalAlignment = TextAlignment.Top)}),Protection(access=Access.packageDuplicate));
    SysplorerEmbeddedCoder.SignalRouting.DataStoreRead dataStoreRead 
      annotation (Placement(transformation(origin = {-140, 0}, extent = {{-10, -10}, {10, 10}})),__MWORKS(BlockSystem(Instance(y(Type(ref="double") ,Dimension=1)),SampleTime(group="D1")=0.1)));
    SysplorerEmbeddedCoder.MathOperation.Sum sum1 
      annotation (Placement(transformation(origin={-80,-5}, 
    extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(u1(Type(ref="double") ,Dimension=1) ,u2(Type(ref="double") ,Dimension=1)) ,y(Type(ref="double") ,Dimension=1)),SampleTime(group="D1")=0.1)));
    SysplorerEmbeddedCoder.Sources.Constant constant1 
      annotation (Placement(transformation(origin={-140,-46}, 
    extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(y(Type(ref="double") ,Dimension=1) ,k(Type(ref="double") ,Dimension=1)),SampleTime(group="D1")=0.1)));
    SysplorerEmbeddedCoder.SignalRouting.DataStoreWrite dataStoreWrite 
      annotation (Placement(transformation(origin={-20,-5}, 
    extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double") ,Dimension=1)),SampleTime(group="D1")=0.1)));
    Trigger trigger 
      annotation (Placement(transformation(origin = {-90, 40}, extent = {{-6, -6}, {6, 6}})),__MWORKS(BlockSystem(Type(ref="double"),Dimension=1,SampleTime(group="D1")=0.1)));
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
    connect(dataStoreRead.y, sum1.u1) 
    annotation(Line(origin={-110,0}, 
    points={{-19,0},{18.2,2.22045e-16}}, 
    color={0,0,0}));
    connect(sum1.y, dataStoreWrite.u) 
    annotation(Line(origin={-50,-2}, 
    points={{-18.2,-3},{18.2,-3}}, 
    color={0,0,0}));
    connect(constant1.y, sum1.u2) 
    annotation(Line(origin={-110,-28}, 
    points={{-18.2,-18},{10,-18},{10,18},{18.2,18}}, 
    color={0,0,0}));
    end SubSystem1;
  model ModelWorkspace
    annotation(__MWORKS(hide = true,BlockSystem(blockKind=BlockKind.modelWorkspace)));
  end ModelWorkspace;
  SubSystem1 subSystem1 annotation(Placement(transformation(origin = {-95,-14}, extent = {{-20,-10},{20,10}})),__MWORKS(BlockSystem(SampleTime(group="D1")=0.1)));
  inner SysplorerEmbeddedCoder.SignalRouting.DataStoreMemory X(start=0) 
    annotation (Placement(transformation(origin={-176,-22}, 
extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.1)));
  SysplorerEmbeddedCoder.SubSystems.FunctionCallGenerator functionCallGenerator(iter_num=1,isShowEnable=false) 
    annotation (Placement(transformation(origin = {-150, 30}, extent = {{-10, -10}, {10, 10}})),__MWORKS(BlockSystem(SampleTime(auto=false)=0.1 ,Instance(y(Dimension=1)))));
  equation
  connect(functionCallGenerator.y, subSystem1.trigger) 
  annotation(Line(origin={-117,14}, 
  points={{-21.2,16},{22,16},{22,-16.2}}, 
  color={0,0,0}));
  end Subsys2;