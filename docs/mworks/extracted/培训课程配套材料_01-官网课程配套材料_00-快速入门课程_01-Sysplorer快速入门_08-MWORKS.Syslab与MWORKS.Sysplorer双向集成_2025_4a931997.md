# JuliaFunctionDemo.mo

- Source: `培训课程配套材料/01-官网课程配套材料/00-快速入门课程/01-Sysplorer快速入门/08-MWORKS.Syslab与MWORKS.Sysplorer双向集成(2025b)/配套示例/4-Syslab Block/JuliaFunctionDemo.mo`
- Category: `sysplorer_modeling`
- Score: `132`
- Size: `0.01 MB`
- Extract mode: `text`

## Extracted Text

```text
model JuliaFunctionDemo
  extends ModelWorkspace;
  import SysplorerEmbeddedCoder.Types.*;
  import BaseWorkspace.*;
  annotation(__MWORKS(version="2025b",modelType=Control,PortArrangement,BlockSystem(blockKind=BlockKind.userModel,SampleTime(auto=true,group="")=0.2,OutputInterval=0.2),SysblockVersion="1.0"),Icon(coordinateSystem(preserveAspectRatio=false)),experiment(Algorithm=Euler,Interval=-1,InlineIntegrator=false,InlineStepSize=false,StoreEventValue=0,Tolerance=0.0001,StartTime=0,StopTime=10));
  block JuliaFunction "编辑和调用Julia脚本函数"
      annotation (defaultComponentName = "juliaFunction", __MWORKS(BlockSystem(blockKind=BlockKind.subSystem,bltBlockKind=BltBlockKind.juliaFunctionSystem,SubSystem(virtual=true,functionPack=FunctionPack.auto,functionName="",sourceFile=""),SampleTime(auto = true)),PortArrangement(Left(in_u1,in_u2),Right(out_y)),sourceModel=SysplorerEmbeddedCoder.Utilities.JuliaFunction,independentInstance=true,hide=true), Icon(coordinateSystem(extent={{-200,-100},{200,100}},
  grid={2,2}),graphics = {Rectangle(sizePolicy=SizePolicy.Expanding,
  rotationPolicy=RotationPolicy.Follow,
  origin={0,0},
  fillColor={255,255,255},
  fillPattern=FillPattern.Solid,
  lineThickness=3,
  extent={{-200,100},{200,-100}}), Text(origin={0,-75},
  lineColor={0,0,0},
  extent={{-200,20},{200,-20}},
  textString="%juliaFunctionName",
  fontSize=14,
  textStyle={TextStyle.None},
  textColor={0,0,0}), Text(origin={0,-120},
  lineColor={0,0,0},
  extent={{0,-20},{0,20}},
  textString="%name",
  fontSize=14,
  textStyle={TextStyle.None},
  textColor={0,0,0},
  verticalAlignment=TextAlignment.Top), Bitmap(origin={0,0},
  extent={{-40,-40},{40,40}},
  fileName="modelica://SysplorerEmbeddedCoder/Resources/Icons/JuliaFunction.svg")},sizePolicy=SizePolicy.Fixed,rotationPolicy=RotationPolicy.Ignore),Diagram(coordinateSystem(extent={{-100,-100},{100,100}},
  grid={2,2})),Protection(access=Access.packageDuplicate));

      block JuliaFunctionAtomic
          annotation (__MWORKS(BlockSystem(blockKind=Types.BlockKind.atomic,
              bltBlockKind=Types.BltBlockKind.juliaFunction), hide=true),Protection(access=Access.packageDuplicate));
        SysplorerEmbeddedCoder.Types.InputAuto in_u1 annotation(Placement(transformation(origin={ -240,30 },extent={ {-6.5,-6.5},{6.5,6.5} }),iconTransformation(origin={ -301.8,30 },extent={ {-1.8,-1.8},{1.8,1.8} })),__MWORKS(BlockSystem(SampleTime(auto=true)=-1,Dimension(dimensionType=DimensionType.auto),Type)));
        SysplorerEmbeddedCoder.Types.InputAuto in_u2 annotation(Placement(transformation(origin={ -240,-30 },extent={ {-6.5,-6.5},{6.5,6.5} }),iconTransformation(origin={ -301.8,-30 },extent={ {-1.8,-1.8},{1.8,1.8} })),__MWORKS(BlockSystem(SampleTime(auto=true)=-1,Dimension(dimensionType=DimensionType.auto),Type)));
        SysplorerEmbeddedCoder.Types.OutputAuto out_y annotation(Placement(transformation(origin={ -240,0 },extent={ {-6.5,-6.5},{6.5,6.5} }),iconTransformation(origin={ -301.8,0 },extent={ {-1.8,-1.8},{1.8,1.8} })),__MWORKS(BlockSystem(SampleTime(auto=true)=-1,Dimension(dimensionType=DimensionType.none)=1,Type(inherit=InheritType.none,ref="double"),funcReturn=true)));
        parameter String juliaScript = "function fcn(u1, u2)\r\n    y = u1 + u2\r\n    return y\r\nend" annotation (HideResult = true);
        parameter String juliaObjectName = "fcn" annotation (HideResult = true);
          end JuliaFunctionAtomic;

      JuliaFunctionAtomic juliaFunctionAtomic annotation(HideResult = true,__MWORKS(BlockSystem(Instance(in_u1(Type(ref="double"),Dimension=1),
in_u2(Type(ref="double"),Dimension=1)),SampleTime(group="D0")=0)));
    SysplorerEmbeddedCoder.Types.InputAuto in_u1 annotation(Placement(transformation(origin={ -240,30 },extent={ {-6.5,-6.5},{6.5,6.5} }),iconTransformation(origin={ -301.8,30 },extent={ {-1.8,-1.8},{1.8,1.8} })),__MWORKS(BlockSystem(SampleTime(auto=true,group="D0")=0,Dimension(dimensionType=DimensionType.auto)=1,Type(ref="double"))));
    SysplorerEmbeddedCoder.Types.InputAuto in_u2 annotation(Placement(transformation(origin={ -240,-30 },extent={ {-6.5,-6.5},{6.5,6.5} }),iconTransformation(origin={ -301.8,-30 },extent={ {-1.8,-1.8},{1.8,1.8} })),__MWORKS(BlockSystem(SampleTime(auto=true,group="D0")=0,Dimension(dimensionType=DimensionType.auto)=1,Type(ref="double"))));
    SysplorerEmbeddedCoder.Types.OutputAuto out_y annotation(Placement(transformation(origin={ -240,0 },extent={ {-6.5,-6.5},{6.5,6.5} }),iconTransformation(origin={ -301.8,0 },extent={ {-1.8,-1.8},{1.8,1.8} })),__MWORKS(BlockSystem(SampleTime(auto=true,group="D0")=0,Dimension(dimensionType=DimensionType.none)=1,Type(inherit=InheritType.none,ref="double"))));
    parameter String juliaFunctionName = "fcn" annotation(HideResult = true);
      equation
    connect(in_u1, juliaFunctionAtomic.in_u1);
    connect(in_u2, juliaFunctionAtomic.in_u2);
    connect(out_y, juliaFunctionAtomic.out_y);
        end JuliaFunction;
  model ModelWorkspace
    annotation(__MWORKS(hide = true,BlockSystem(blockKind=BlockKind.modelWorkspace)));
  end ModelWorkspace;
  JuliaFunction juliaFunction 
    annotation (Placement(transformation(origin={24,8},
extent={{-20,-10},{20,10}})),__MWORKS(BlockSystem(SampleTime=-1)));
  SysplorerEmbeddedCoder.Sources.Clock clock 
    annotation (Placement(transformation(origin = {-60, 30}, extent = {{-10, -10}, {10, 10}})),__MWORKS(BlockSystem(SampleTime(group="D0")=0)));
  SysplorerEmbeddedCoder.Sources.SineWave sineWave(amplitude=1,bias=0,frequency=2,phase=0,timeSource=SysplorerEmbeddedCoder.MathOperation.SineWaveFunction.TimeSourceType.simulationTime) 
    annotation (Placement(transformation(origin={-60,-16},
extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(SampleTime(auto=false)=0,Instance(y(Dimension=1),
amplitude(Dimension=1),
bias(Dimension=1),
frequency(Dimension=1),
phase(Dimension=1)))));
  Scope scope 
    annotation (Placement(transformation(origin={82,8},
extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u1(Type(ref="double"),Dimension=1)),SampleTime(group="D0")=0)));
  block Scope "显示仿真过程中生成的信号"

    parameter String displayFormat = "y(t)" annotation(HideResult = true);

    parameter String showOnSimulator = "false" annotation(HideResult = true);

    SysplorerEmbeddedCoder.Types.InputAuto u1 
       annotation (Placement(transformation(origin={-110,0},
      extent={{-10,-10},{10,10}}),
      iconTransformation(origin={-101.8,0},
      extent={{-1.8,-1.8},{1.8,1.8}})),
        __MWORKS(BlockSystem(AllowDimension(choices(choice=DimensionType.scalar,
       choice=DimensionType.array1D,
  choice=DimensionType.scalar,choice=DimensionType.rowVector2D,choice=DimensionType.columnVector2D,choice=DimensionType.array2D)),
        AllowType(choices(choice = "double", choice = "float", choice = "int8", choice = "uint8", choice = "int16", choice = "uint16", choice = "int32",
        choice = "uint32", choice = "int64", choice = "uint64", choice = "string", choice = "boolean", choice = "enum", choice = "bus")))));

    annotation(defaultComponentName = "scope", __MWORKS(BlockSystem(blockKind=Types.BlockKind.atomic, bltBlockKind=Types.BltBlockKind.scope),PortArrangement(Left(u1)),sourceModel=SysplorerEmbeddedCoder.Utilities.Scope,independentInstance=true,hide=true), Icon(coordinateSystem(extent={{-100,-100},{100,100}},
  grid={2,2}),graphics = {Rectangle(origin={0,0},
  fillColor={255,255,255},
  fillPattern=FillPattern.Solid,
  lineThickness=3,
  extent={{-100,100},{100,-100}},
  rotationPolicy=RotationPolicy.Follow), Rectangle(origin={1,54.5},
  fillColor={255,255,255},
  fillPattern=FillPattern.Solid,
  lineThickness=2,
  extent={{-79,24.5},{79,-24.5}},
  radius=10), Text(origin={0,-120},
  lineColor={0,0,0},
  extent={{0,-20},{0,20}},
  textString="%name",
  fontSize=14,
  textStyle={TextStyle.None},
  textColor={0,0,0},
  verticalAlignment=TextAlignment.Top)},rotationPolicy=RotationPolicy.Ignore),Protection(access=Access.packageDuplicate));

  end Scope;
equation
  connect(clock.y, juliaFunction.in_u1) 
  annotation(Line(origin={-23,22},
  points={{-25.2,8},{1,8},{1,-9},{25.2,-9}},
  color={0,0,0}));
  connect(sineWave.y, juliaFunction.in_u2) 
  annotation(Line(origin={-23,-6},
  points={{-25.2,-10},{1,-10},{1,9},{25.2,9}},
  color={0,0,0}));
  connect(juliaFunction.out_y, scope.u1) 
  annotation(Line(origin={58,8},
  points={{-12.2,0},{12.2,0}},
  color={0,0,0}));

end JuliaFunctionDemo;
```
